import contextlib
import json
import logging
import time
import wave
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.generators.prompt_engineering import ThemeCategory
from src.video.generators.final_video_composer import (
    FinalVideoComposer,
    TemplateConfig,
    VideoSegment,
)
from src.utils.exceptions import ScriptGenerationError


class AiShortsOrchestrator:
    """Responsável por executar o pipeline end-to-end do AiShorts."""

    def __init__(
        self,
        *,
        theme_generator,
        script_generator,
        translator,
        tts_client,
        youtube_extractor,
        semantic_analyzer,
        audio_video_sync,
        video_processor,
        broll_query_service,
        caption_service,
        video_composer_factory: Optional[Callable[[], FinalVideoComposer]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.theme_generator = theme_generator
        self.script_generator = script_generator
        self.translator = translator
        self.tts_client = tts_client
        self.youtube_extractor = youtube_extractor
        self.semantic_analyzer = semantic_analyzer
        self.audio_video_sync = audio_video_sync
        self.video_processor = video_processor
        self.broll_query_service = broll_query_service
        self.caption_service = caption_service
        self._composer_factory = video_composer_factory or (lambda: FinalVideoComposer())

        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._setup_directories()

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def run(self, theme_category: ThemeCategory = ThemeCategory.ANIMALS) -> Dict[str, Any]:
        """Executa o pipeline completo e retorna os resultados das etapas."""
        self.logger.info("=" * 70)
        self.logger.info("🎬 INICIANDO PIPELINE AISHORTS V2.0 - GERAÇÃO DE VÍDEO")
        self.logger.info("=" * 70)

        start_time = time.time()
        results: Dict[str, Any] = {}

        try:
            theme_obj, theme_result = self._generate_theme(theme_category)
            results["theme"] = theme_result

            script_obj, script_result = self._generate_script(theme_obj)
            results["script"] = script_result

            broll_queries = self.broll_query_service.generate_queries(
                script_result["content_en"]["plain_text"]
            )
            results["script"]["broll_queries"] = broll_queries
            if broll_queries:
                self.logger.info("🎯 Queries de B-roll sugeridas: %s", broll_queries)
            else:
                self.logger.warning("⚠️ Falha ao gerar queries específicas de B-roll; usando fallback semântico")

            translation_result, script_text_pt = self._translate_script(script_result)
            results["script"]["content_pt"] = script_text_pt if translation_result["success"] else None
            results["script"]["translation"] = translation_result

            audio_result = self._synthesize_audio(script_text_pt)
            results["audio"] = audio_result

            captions = self.caption_service.build_captions(script_text_pt, audio_result["duration"])
            results["captions"] = captions
            if captions:
                self.logger.info("💬 Legendas geradas: %d segmentos", len(captions))
                for preview in captions[:3]:
                    self.logger.info(
                        "   [%.2fs - %.2fs] %s",
                        preview["start_time"],
                        preview["end_time"],
                        preview["text"],
                    )
            else:
                self.logger.warning("⚠️ Não foi possível gerar legendas sincronizadas")

            broll_result = self._extract_broll(
                theme_result["content_en"],
                search_queries=broll_queries,
            )
            results["broll"] = broll_result
            self.logger.info(
                "🎬 B-roll buscado com queries: %s",
                broll_result.get("used_queries") or broll_result.get("queries"),
            )

            analysis_result = self._analyze_content(theme_result["content_en"])
            results["analysis"] = analysis_result

            sync_result = self._sync_audio_video(audio_result["file_path"], broll_result["videos"])
            results["sync"] = sync_result

            final_video_path = self._process_final_video(
                broll_result["videos"],
                audio_result["file_path"],
                captions=captions,
            )
            final_video_exists = bool(final_video_path and Path(final_video_path).exists())

            results["final"] = {
                "video_path": final_video_path,
                "video_count": len(broll_result["videos"]),
                "success": final_video_exists,
                "captions": len(captions),
            }

            if not final_video_exists:
                self.logger.error("❌ Falha na composição final do vídeo. Arquivo não encontrado.")
                return self._fail_results(results, start_time, "Final video was not generated")

            total_time = time.time() - start_time
            results["total_time"] = total_time
            results["status"] = "success"

            self._log_summary(theme_result, script_result, audio_result, broll_result, analysis_result, final_video_path, total_time)
            self._save_report(results)

            return results

        except Exception as error:
            self.logger.error("❌ Pipeline falhou: %s", error)
            return self._fail_results(results, start_time, str(error))

    # --------------------------------------------------------------------- #
    # Internals
    # --------------------------------------------------------------------- #
    def _generate_theme(self, category: ThemeCategory):
        self.logger.info("🎯 ETAPA 1: Geração de Tema com IA...")
        theme = self.theme_generator.generate_single_theme(category)

        self.logger.info("✅ Tema gerado (EN): %s...", theme.content[:100])
        self.logger.info("📊 Qualidade: %.2f", theme.quality_score)
        self.logger.info("⏱️ Tempo: %.2fs", theme.response_time)
        self.logger.info("📄 Tema completo (EN): %s", theme.content)
        self.logger.info("✏️ Comprimento do tema: %d palavras", len(theme.content.split()))

        result = {
            "content_en": theme.content,
            "category": theme.category.value,
            "quality": theme.quality_score,
            "response_time": theme.response_time,
        }
        return theme, result

    def _generate_script(self, theme_obj):
        self.logger.info("📝 ETAPA 2: Geração de roteiro em inglês...")
        custom_requirements = None
        max_attempts = 4
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                script = self.script_generator.generate_single_script(
                    theme=theme_obj,
                    custom_requirements=custom_requirements,
                    target_platform="tiktok",
                )

                hook_text = script.hook.content if script.hook else ""
                body_text = script.development.content if script.development else ""
                conclusion_text = script.conclusion.content if script.conclusion else ""

                estimated_duration_from_text = None
                if conclusion_text and "ESTIMATED_DURATION" in conclusion_text:
                    parts = conclusion_text.split("ESTIMATED_DURATION")
                    conclusion_text = parts[0].strip()
                    try:
                        estimated_duration_from_text = float(parts[1].split(":")[-1].strip(" `"))
                    except Exception:
                        estimated_duration_from_text = None

                if body_text.endswith("```"):
                    body_text = body_text.rstrip("`").rstrip()
                if conclusion_text.endswith("```"):
                    conclusion_text = conclusion_text.rstrip("`").rstrip()

                structured_text = "\n".join(
                    filter(
                        None,
                        [
                            f"HOOK: {hook_text}" if hook_text else "",
                            f"BODY: {body_text}" if body_text else "",
                            f"CONCLUSION: {conclusion_text}" if conclusion_text else "",
                        ],
                    )
                ).strip()

                plain_text = "\n".join(
                    [line for line in [hook_text, body_text, conclusion_text] if line]
                ).strip()

                result = {
                    "title": script.title,
                    "total_duration": script.total_duration,
                    "quality_score": script.quality_score,
                    "engagement_score": script.engagement_score,
                    "retention_score": script.retention_score,
                    "generated_at": script.timestamp.isoformat(),
                    "content_en": {
                        "hook": hook_text,
                        "body": body_text,
                        "conclusion": conclusion_text,
                        "structured_text": structured_text,
                        "plain_text": plain_text,
                    },
                }
                if estimated_duration_from_text:
                    result["estimated_duration_from_text"] = estimated_duration_from_text

                self.logger.info(
                    "📝 Roteiro gerado (EN) - Score: %.2f, Duração estimada: %.1fs",
                    script.quality_score,
                    script.total_duration,
                )
                self.logger.info("   HOOK (EN): %s", hook_text)
                self.logger.info("   BODY (EN): %s", body_text)
                self.logger.info("   CONCLUSION (EN): %s", conclusion_text)
                self.logger.info("📜 Script completo (EN):\n%s", structured_text)

                if script.total_duration >= 45.0:
                    return script, result

                self.logger.warning(
                    "⚠️ Roteiro curto (%.1fs) na tentativa %d. Refinando instruções e tentando novamente.",
                    script.total_duration,
                    attempt,
                )
                custom_requirements = [
                    "Ensure the BODY contains at least 6 sentences totaling 140-160 words",
                    "Keep HOOK under 12 words but make it punchy",
                    "CONCLUSION must include a CTA with at least 25 words",
                    "Return ESTIMATED_DURATION on its own line as ESTIMATED_DURATION: <seconds>",
                    "Overall narration should take around 55-60 seconds when spoken",
                ]
                last_error = "script_too_short"

            except Exception as error:
                last_error = str(error)
                self.logger.error("❌ Erro na geração do roteiro (tentativa %d): %s", attempt, error)
                custom_requirements = [
                    "Use three paragraphs: HOOK, BODY (6 sentences, 140-160 words), CONCLUSION (≥25 words)",
                    "Return the ESTIMATED_DURATION on its own line",
                ]

        raise ScriptGenerationError(
            f"Falha ao gerar roteiro consistente: {last_error}",
            theme_content=theme_obj.content,
            platform="tiktok",
        )

    def _translate_script(self, script_result: Dict[str, Any]):
        plain_script_en = script_result["content_en"]["plain_text"]
        translation_result = self.translator.translate(plain_script_en)

        if translation_result.success:
            script_text_pt = translation_result.translated_text or plain_script_en
            self.logger.info("📝 Roteiro traduzido (PT-BR): %s", script_text_pt)
            self.logger.info("✅ Roteiro traduzido para PT-BR com sucesso")
        else:
            script_text_pt = plain_script_en
            self.logger.warning("⚠️ Tradução falhou, utilizando roteiro em inglês para TTS")
            if translation_result.error:
                self.logger.warning("Motivo da falha de tradução: %s", translation_result.error)

        return {
            "success": translation_result.success,
            "response_time": translation_result.response_time,
            "usage": translation_result.usage,
            "error": translation_result.error,
        }, script_text_pt

    def _synthesize_audio(self, script_text_pt: str) -> Dict[str, Any]:
        self.logger.info("🔊 ETAPA 2: Síntese de Áudio TTS...")
        result = self.tts_client.text_to_speech(
            script_text_pt,
            f"narracao_{datetime.now().strftime('%H%M%S')}.wav",
        )
        if not result.get("success"):
            raise RuntimeError(f"Falha na síntese de áudio: {result.get('error')}")

        self.logger.info("✅ Áudio gerado: %s", result["audio_path"])
        self.logger.info("⏱️ Duração: %.2fs", result["duration"])
        self.logger.info("🎤 Voz: %s", result["voice"])

        return {
            "success": True,
            "file_path": result["audio_path"],
            "duration": result["duration"],
            "voice": result["voice"],
        }

    def _extract_broll(self, theme_content: str, *, search_queries: Optional[List[str]] = None):
        self.logger.info("🎬 ETAPA 3: Extração de B-roll do YouTube...")

        keywords = self.semantic_analyzer.extract_keywords(theme_content) if theme_content else []
        queries: List[str] = []
        if search_queries:
            queries.extend([q for q in search_queries if q])
        fallback_query = " ".join(keywords[:3]).strip()
        if fallback_query and fallback_query not in queries:
            queries.append(fallback_query)
        if not queries and theme_content:
            queries.append(theme_content[:60])

        self.logger.info("🔍 Estratégia de busca para B-roll: %s", queries)

        downloaded_videos: List[str] = []
        used_queries: List[str] = []
        visited_ids: set[str] = set()
        output_dir = Path("outputs/video")

        for query in queries:
            if len(downloaded_videos) >= 3:
                break

            candidates = self.youtube_extractor.search_videos(query, max_results=3)
            if not candidates:
                self.logger.warning("⚠️ Nenhum resultado para query '%s'", query)
                continue

            used_queries.append(query)

            for video in candidates:
                if len(downloaded_videos) >= 3:
                    break

                video_id = video.get("id")
                if video_id and video_id in visited_ids:
                    continue

                duration = video.get("duration")
                if duration and duration > 180:
                    self.logger.info(
                        "⏭️ Ignorando vídeo muito longo (%.1fs): %s",
                        duration,
                        video.get("title", "sem título"),
                    )
                    continue

                try:
                    real_path = self.youtube_extractor.download_video(video["url"], str(output_dir))
                    downloaded_videos.append(real_path)
                    if video_id:
                        visited_ids.add(video_id)
                    self.logger.info(
                        "📥 Vídeo baixado (%d/3): %s",
                        len(downloaded_videos),
                        real_path,
                    )
                except Exception as error:
                    self.logger.warning(
                        "⚠️ Erro ao baixar '%s': %s",
                        video.get("title", "sem título"),
                        error,
                    )

            if len(downloaded_videos) >= 3:
                break

        if not downloaded_videos:
            raise RuntimeError("Nenhum vídeo encontrado ou baixado com as queries fornecidas")

        return {
            "success": True,
            "videos": downloaded_videos,
            "queries": queries,
            "keywords": keywords,
            "used_queries": used_queries,
        }

    def _analyze_content(self, theme_content: str) -> Dict[str, Any]:
        self.logger.info("🧠 ETAPA 4: Análise Semântica...")
        keywords = self.semantic_analyzer.extract_keywords(theme_content)
        category = self.semantic_analyzer.categorize_content(theme_content)

        self.logger.info("✅ Keywords extraídas: %s", keywords)
        self.logger.info("🏷️ Categoria: %s (%.2f)", category[0], category[1])

        return {
            "keywords": keywords,
            "category": category[0],
            "confidence": category[1],
        }

    def _sync_audio_video(self, audio_path: str, video_paths: List[str]) -> Dict[str, Any]:
        self.logger.info("🎵 ETAPA 5: Sincronização Áudio-Vídeo...")
        self.logger.info("✅ Configuração de sincronização concluída")
        self.logger.info("🎵 Áudio: %s", audio_path)
        self.logger.info("🎬 Vídeos: %d arquivos", len(video_paths))
        return {
            "success": True,
            "audio_path": audio_path,
            "video_paths": video_paths,
        }

    def _process_final_video(
        self,
        video_paths: List[str],
        audio_path: str,
        *,
        captions: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        self.logger.info("🎞️ ETAPA 6: Processamento Final com FinalVideoComposer...")

        if not audio_path or not Path(audio_path).exists():
            self.logger.error("❌ Áudio inexistente para composição: %s", audio_path)
            return None
        if not video_paths:
            self.logger.error("❌ Nenhum vídeo B-roll disponível para composição final")
            return None

        segments: List[VideoSegment] = []
        for path in video_paths:
            path_obj = Path(path)
            if not path_obj.exists():
                self.logger.warning("⚠️ Vídeo ausente ignorado: %s", path)
                continue

            video_info = self.video_processor.get_video_info(path)
            if video_info and video_info.get("duration"):
                duration = float(video_info["duration"])
            else:
                self.logger.warning("⚠️ Duração desconhecida para %s, usando fallback de 5s", path)
                duration = 5.0

            segments.append(VideoSegment(path=str(path_obj), duration=duration))

        if not segments:
            self.logger.error("❌ Nenhum segmento de vídeo válido após validação")
            return None

        composer = self._composer_factory()
        template_config: Optional[TemplateConfig] = composer.templates.get("professional")
        if not template_config and composer.templates:
            template_config = next(iter(composer.templates.values()))
        if not template_config:
            self.logger.error("❌ FinalVideoComposer não disponibilizou templates para composição")
            return None

        audio_duration = self._get_audio_duration(audio_path)
        if audio_duration:
            template_config = replace(template_config, duration=audio_duration)

        metadata = {
            "pipeline": "AiShortsOrchestrator",
            "generated_at": datetime.now().isoformat(),
            "video_segments": [segment.path for segment in segments],
            "audio_path": audio_path,
            "captions_count": len(captions or []),
        }

        try:
            final_video_path = composer.compose_final_video(
                audio_path=audio_path,
                video_segments=segments,
                template_config=template_config,
                captions=captions,
                output_path="outputs/final/video_final_aishorts.mp4",
                metadata=metadata,
            )
            self.logger.info("✅ Vídeo final gerado: %s", final_video_path)
            return final_video_path
        except Exception as error:
            self.logger.error("❌ ERRO NA COMPOSIÇÃO FINAL: %s", error)
            print(f"❌ ERRO NA COMPOSIÇÃO FINAL: {error}")
            return None

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #
    def _setup_directories(self):
        for dir_path in ["outputs/video", "outputs/audio", "outputs/final", "temp"]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def _get_audio_duration(self, audio_path: str) -> Optional[float]:
        try:
            with contextlib.closing(wave.open(audio_path, "rb")) as wav_file:
                frames = wav_file.getnframes()
                framerate = wav_file.getframerate()
                if framerate:
                    return frames / float(framerate)
        except (wave.Error, FileNotFoundError):
            self.logger.warning("⚠️ Não foi possível ler duração do áudio %s", audio_path)
        return None

    def _log_summary(self, theme_result, script_result, audio_result, broll_result, analysis_result, final_video_path, total_time):
        self.logger.info("=" * 70)
        self.logger.info("🏆 PIPELINE CONCLUÍDO COM SUCESSO!")
        self.logger.info("=" * 70)
        self.logger.info("⏱️ Tempo total: %.2fs", total_time)
        self.logger.info("📊 Tema (qualidade): %.2f", theme_result["quality"])
        self.logger.info(
            "📝 Roteiro (EN) - Duração estimada: %.1fs, Qualidade: %.2f",
            script_result["total_duration"],
            script_result["quality_score"],
        )
        self.logger.info("🎵 Áudio (PT-BR): %.2fs", audio_result["duration"])
        self.logger.info("🎬 B-roll: %d vídeos", len(broll_result["videos"]))
        self.logger.info("🧠 Análise: %s", analysis_result["keywords"])
        self.logger.info("📁 Saída: %s", final_video_path)

    def _save_report(self, results: Dict[str, Any]):
        report_path = f"outputs/pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as file_handle:
            json.dump(results, file_handle, indent=2, ensure_ascii=False)
        self.logger.info("📄 Relatório salvo: %s", report_path)

    def _fail_results(self, results: Dict[str, Any], start_time: float, error: str) -> Dict[str, Any]:
        results["status"] = "failed"
        results["error"] = error
        results["total_time"] = time.time() - start_time
        return results
