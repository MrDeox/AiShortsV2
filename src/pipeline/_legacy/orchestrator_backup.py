import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.generators.prompt_engineering import ThemeCategory
from src.models.unified_models import (
    PipelineResult,
    TranslationResult,
    TTSAudioResult,
    BrollMatchResult,
    VideoSyncPlan
)
from src.pipeline.services.content_generation_service import ContentGenerationService
from src.pipeline.services.media_acquisition_service import MediaAcquisitionService
from src.pipeline.services.video_assembly_service import VideoAssemblyService
from src.core.graceful_degradation import graceful_degradation_manager

# Importar otimizações de memória local
try:
    from src.core.model_manager import get_model_manager
    from src.core.memory_monitor import get_memory_monitor
    MEMORY_OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    MEMORY_OPTIMIZATIONS_AVAILABLE = False


class AiShortsOrchestrator:
    """Responsável por executar o pipeline end-to-end do AiShorts.
    
    Versão refatorada que delega responsabilidades para serviços especializados:
    - ContentGenerationService: geração de tema, script e TTS
    - MediaAcquisitionService: busca e análise de B-roll
    - VideoAssemblyService: sincronização e composição final
    """

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
        video_composer_factory: Optional[Any] = None,
        script_validator: Optional[Any] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Inicializar serviços especializados
        self.content_service = ContentGenerationService(
            theme_generator=theme_generator,
            script_generator=script_generator,
            translator=translator,
            tts_client=tts_client,
            script_validator=script_validator,
            logger=self.logger
        )
        
        self.media_service = MediaAcquisitionService(
            youtube_extractor=youtube_extractor,
            semantic_analyzer=semantic_analyzer,
            broll_query_service=broll_query_service,
            logger=self.logger
        )
        
        self.video_service = VideoAssemblyService(
            video_processor=video_processor,
            caption_service=caption_service,
            video_composer_factory=video_composer_factory,
            logger=self.logger
        )

        # Sistema de graceful degradation
        self.graceful_degradation = graceful_degradation_manager
        self._setup_graceful_degradation()

        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Otimizações de memória local
        if MEMORY_OPTIMIZATIONS_AVAILABLE:
            self.model_manager = get_model_manager()
            self.memory_monitor = get_memory_monitor()
self.logger.info(" Otimizações de memória local ativadas")
        else:
            self.model_manager = None
            self.memory_monitor = None
self.logger.warning(" Otimizações de memória não disponíveis")
        
        self._setup_directories()
    
    def _setup_graceful_degradation(self):
        """Configura sistema de graceful degradation"""
        try:
            # Configurar fallbacks padrão se ainda não foram configurados
            from src.core.graceful_degradation import setup_default_fallbacks
            setup_default_fallbacks()
            
            # Registrar dependências principais para monitoramento
            dependencies_to_monitor = [
                ("openrouter", lambda: bool(self.openrouter.client and hasattr(self.openrouter, 'api_key'))),
                ("tts", lambda: self.tts_client is not None),
                ("youtube", lambda: self.youtube_extractor is not None),
                ("memory", lambda: not (self.memory_monitor and self.memory_monitor.suggest_cleanup())),
                ("clip", lambda: self.clip_relevance_scorer is not None)
            ]
            
            for dep_name, health_check in dependencies_to_monitor:
                try:
                    self.graceful_degradation.register_dependency(dep_name, health_check)
                except Exception as e:
self.logger.warning(f" Falha ao registrar dependência '{dep_name}': {e}")
            
            # Gerar relatório inicial
            health_report = self.graceful_degradation.get_system_health_report()
            available = health_report["summary"]["available"]
            total = health_report["summary"]["total_dependencies"]
            
self.logger.info(f"Graceful degradation configurado: {available}/{total} dependências disponíveis")
            
        except Exception as e:
self.logger.error(f" Erro na configuração do graceful degradation: {e}")
    
    def _execute_with_fallback(self, dependency_name: str, operation: callable, *args, **kwargs):
        """
        Executa operação com fallback automático usando graceful degradation.
        
        Args:
            dependency_name: Nome da dependência
            operation: Operação a ser executada
            *args, **kwargs: Argumentos da operação
            
        Returns:
            Resultado da operação (principal ou fallback)
        """
        try:
            return self.graceful_degradation.execute_with_fallback(
                dependency_name=dependency_name,
                primary_operation=operation,
                *args,
                **kwargs
            )
        except Exception as e:
self.logger.error(f" Falha completa em '{dependency_name}' com fallback: {e}")
            # Tentar resposta padrão de emergência
            return self._emergency_fallback(dependency_name, e)
    
    def _emergency_fallback(self, dependency_name: str, original_error: Exception) -> Any:
        """
        Fallback de emergência quando todos os outros falharam.
        
        Args:
            dependency_name: Nome da dependência que falhou
            original_error: Erro original
            
        Returns:
            Resposta de emergência
        """
self.logger.warning(f" Emergency fallback para '{dependency_name}' devido a: {original_error}")
        
        if dependency_name == "tts":
            # Áudio silencioso de emergência
            return {
                "success": True,
                "audio_path": "assets/silence.wav",
                "duration": 60.0,
                "voice": "emergency_silence"
            }
        
        elif dependency_name == "youtube":
            # Vídeos locais de emergência
            return []
        
        elif dependency_name == "openrouter":
            # Conteúdo de emergência
            return {
                "content": "Contúdo gerado com recursos limitados. Tema: Natureza e Curiosidades.",
                "success": True,
                "fallback": "emergency"
            }
        
        # Para outros, retornar None
        return None

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def run(self, theme_category: ThemeCategory = ThemeCategory.ANIMALS) -> Dict[str, Any]:
        """Executa o pipeline completo usando serviços especializados."""
self.logger.info("=" * 70)
self.logger.info(" INICIANDO PIPELINE AISHORTS V2.0 - GERAÇÃO DE VÍDEO")
self.logger.info("=" * 70)

        # Verificar memória inicial
        initial_stats = None
        if self.memory_monitor:
            initial_stats = self.memory_monitor.get_current_stats()
self.logger.info(
                f"💾 Memória inicial: {initial_stats.process_gb:.2f}GB "
                f"({initial_stats.system_percent:.1f}% sistema)"
            )

        start_time = time.time()
        pipeline_result = PipelineResult(
            status="success",
            theme={},
            script={}
        )

        try:
            # 1) Gerar tema e script
            theme_obj, theme_result = self.content_service.generate_theme(theme_category)
            pipeline_result.theme = theme_result
            
            script_obj, script_result = self.content_service.generate_script(theme_obj)
            pipeline_result.script = script_result
            
            # 2) Gerar queries de B-roll
            broll_queries = self.media_service.broll_query_service.generate_queries(
                script_result["content_en"]["plain_text"]
            )
            pipeline_result.script["broll_queries"] = broll_queries
            if broll_queries:
self.logger.info(" Queries de B-roll sugeridas: %s", broll_queries)
            else:
self.logger.warning(" Falha ao gerar queries específicas de B-roll; usando fallback semântico")
            
            # 3) Traduzir script
            translation_result = self.content_service.translate_script(
                script_result["content_en"]["plain_text"]
            )
            pipeline_result.script["content_pt"] = translation_result.translated_text
            pipeline_result.script["translation"] = translation_result.to_dict()
            
            # 4) Sintetizar áudio
            audio_result = self.content_service.synthesize_audio(translation_result.translated_text)
            pipeline_result.audio = audio_result
            
            # 5) Gerar legendas
            captions = self.video_service.caption_service.build_captions(
                translation_result.translated_text, 
                audio_result.duration
            )
            pipeline_result.captions = captions
            if captions:
self.logger.info(" Legendas geradas: %d segmentos", len(captions))
                for preview in captions[:3]:
self.logger.info(
                        "   [%.2fs - %.2fs] %s",
                        preview["start_time"],
                        preview["end_time"],
                        preview["text"],
                    )
            else:
self.logger.warning(" Não foi possível gerar legendas sincronizadas")
            
            # 6) Extrair e analisar B-roll
            broll_result = self.media_service.extract_broll(
                theme_result["content_en"],
                search_queries=broll_queries,
            )
            pipeline_result.broll = broll_result
self.logger.info(
                "🎬 B-roll buscado com queries: %s",
                broll_result.queries_used,
            )
            
            # Verificar memória antes da análise (ponto crítico)
            if self.memory_monitor:
                self.memory_monitor.check_memory("antes_analise_semantica")
            
            analysis_result = self.media_service.analyze_content(theme_result["content_en"])
            pipeline_result.analysis = analysis_result
            
            # Verificar memória após carregar modelos
            if self.memory_monitor:
                if not self.memory_monitor.check_memory("apos_analise_semantica"):
self.logger.warning(" Memória alta após análise, tentando cleanup...")
                    self.model_manager.cleanup_models()
                    self.memory_monitor.force_garbage_collection()
            
            # 7) Sincronizar áudio e vídeo
            sync_result = self.video_service.sync_audio_video(
                audio_result.audio_path, 
                broll_result.videos
            )
            pipeline_result.sync = sync_result
            
            # 8) Compor vídeo final
            final_video_path = self.video_service.compose_final_video(
                video_paths=broll_result.videos,
                audio_path=audio_result.audio_path,
                captions=captions,
                sync_result=sync_result
            )
            
            final_video_exists = bool(final_video_path and Path(final_video_path).exists())
            
            pipeline_result.final = {
                "video_path": final_video_path,
                "video_count": len(broll_result.videos),
                "success": final_video_exists,
                "captions": len(captions),
            }
            
            if not final_video_exists:
self.logger.error(" Falha na composição final do vídeo. Arquivo não encontrado.")
                return self._create_failed_result(pipeline_result, start_time, "Final video was not generated")
            
            # Finalizar
            total_time = time.time() - start_time
            pipeline_result.total_time = total_time
            
            self._log_summary(
                theme_result, 
                script_result, 
                audio_result.to_dict(), 
                broll_result.to_dict(), 
                analysis_result, 
                final_video_path, 
                total_time
            )
            
            # Cleanup de memória
            self._cleanup_memory(initial_stats)
            
            # Salvar relatório
            self._save_report(pipeline_result.to_dict())
            
            return pipeline_result.to_dict()
            
        except Exception as error:
self.logger.error(" Pipeline falhou: %s", error)
            
            # Cleanup em caso de erro
            if self.model_manager:
                self.model_manager.cleanup_models()
            
            return self._create_failed_result(pipeline_result, start_time, str(error))

    # --------------------------------------------------------------------- #
    # Métodos de apoio (simplificados)
    # --------------------------------------------------------------------- #

    def _generate_script(self, theme_obj):
self.logger.info(" ETAPA 2: Geração de roteiro em inglês com validação robusta...")
        custom_requirements = None
        max_attempts = 4
        last_error = None
        validation_threshold = 70.0  # Score mínimo para aprovação

        for attempt in range(1, max_attempts + 1):
            try:
                script = self.script_generator.generate_single_script(
                    theme=theme_obj,
                    custom_requirements=custom_requirements,
                    target_platform="tiktok",
                )

                # Validar roteiro usando ScriptValidator integrado
self.logger.info(" Validando qualidade do roteiro gerado...")
                validation_report = self.script_validator.validate_script(script, PlatformType.TIKTOK)
                
                # Log detalhado da validação
self.logger.info(
                    "📊 Validação - Score geral: %.2f, Nível: %s, Aprovado: %s",
                    validation_report.overall_score,
                    validation_report.quality_level.value,
                    "✅" if validation_report.is_approved else "❌"
                )
                
                # Log de issues críticos
                critical_issues = validation_report.get_critical_issues()
                if critical_issues:
self.logger.warning(" Issues críticos encontrados (%d):", len(critical_issues))
                    for issue in critical_issues[:3]:  # Mostrar apenas os 3 primeiros
self.logger.warning("   • %s: %s", issue.code, issue.message)
                
                # Log de sugestões principais
                if validation_report.suggestions:
self.logger.info(" Sugestões de melhoria:")
                    for suggestion in validation_report.suggestions[:3]:  # Mostrar apenas 3 sugestões
self.logger.info("   • %s", suggestion)

                # Extrair texto do script para resultado
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

                # Verificar se o roteiro atende aos critérios
                duration_ok = script.total_duration >= 45.0
                validation_ok = validation_report.overall_score >= validation_threshold
                no_critical_errors = len(critical_issues) == 0

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
                    # Adicionar informações da validação
                    "validation": {
                        "overall_score": validation_report.overall_score,
                        "quality_level": validation_report.quality_level.value,
                        "is_approved": validation_report.is_approved,
                        "critical_issues": len(critical_issues),
                        "total_issues": len(validation_report.all_issues),
                        "suggestions": validation_report.suggestions[:5]  # Manter apenas 5 sugestões principais
                    }
                }
                if estimated_duration_from_text:
                    result["estimated_duration_from_text"] = estimated_duration_from_text

self.logger.info(
                    "📝 Roteiro gerado (EN) - Score: %.2f, Validação: %.2f, Duração: %.1fs",
                    script.quality_score,
                    validation_report.overall_score,
                    script.total_duration,
                )
self.logger.info("   HOOK (EN): %s", hook_text)
self.logger.info("   BODY (EN): %s", body_text[:100] + "..." if len(body_text) > 100 else body_text)
self.logger.info("   CONCLUSION (EN): %s", conclusion_text)

                # Verificar critérios de aprovação
                if duration_ok and validation_ok and no_critical_errors:
self.logger.info(" Roteiro aprovado pela validação robusta!")
                    return script, result
                
                # Se não aprovou, preparar para tentar novamente
self.logger.warning(
                    "⚠️ Roteiro não atendeu aos critérios (tentativa %d):",
                    attempt,
                )
                if not duration_ok:
self.logger.warning("   • Duração muito curta: %.1fs", script.total_duration)
                if not validation_ok:
self.logger.warning("   • Score de validação baixo: %.2f (mín: %.1f)",
                                      validation_report.overall_score, validation_threshold)
                if critical_issues:
self.logger.warning("   • %d erros críticos encontrados", len(critical_issues))
                
                # Refinar requisitos com base nas falhas da validação
                custom_requirements = self._generate_refined_requirements(validation_report, attempt)
                last_error = "validation_failed"

            except Exception as error:
                last_error = str(error)
self.logger.error(" Erro na geração do roteiro (tentativa %d): %s", attempt, error)
                custom_requirements = [
                    "Use three paragraphs: HOOK, BODY (6 sentences, 140-160 words), CONCLUSION (≥25 words)",
                    "Return the ESTIMATED_DURATION on its own line",
                ]

        raise ScriptGenerationError(
            f"Falha ao gerar roteiro consistente após {max_attempts} tentativas: {last_error}",
            theme_content=theme_obj.content,
            platform="tiktok",
        )

    def _generate_refined_requirements(self, validation_report, attempt: int) -> List[str]:
        """Gera requisitos refinados com base nas falhas da validação."""
        requirements = []
        
        # Requisitos base sempre presentes
        base_requirements = [
            "Ensure the script follows the structure: HOOK, BODY (6+ sentences), CONCLUSION",
            "Return ESTIMATED_DURATION on its own line as ESTIMATED_DURATION: <seconds>",
            "Overall narration should take 55-60 seconds when spoken"
        ]
        requirements.extend(base_requirements)
        
        # Analisar falhas específicas da validação
        critical_issues = validation_report.get_critical_issues()
        
        # Se há problemas de estrutura
        structure_issues = [i for i in critical_issues if i.code.startswith("STRUCTURE_")]
        if structure_issues:
            requirements.append("FIX STRUCTURE: Ensure all three sections (HOOK, BODY, CONCLUSION) are clearly labeled and complete")
        
        # Se há problemas com o hook
        hook_issues = [i for i in validation_report.all_issues if i.section == "hook"]
        if hook_issues:
            hook_codes = [i.code for i in hook_issues]
            if "HOOK_LOW_ENGAGEMENT" in hook_codes:
                requirements.append("IMPROVE HOOK: Start with a question, surprising fact, or emotional statement")
            if "HOOK_TOO_SHORT" in hook_codes:
                requirements.append("LENGTHEN HOOK: Make hook at least 50 characters with impact")
        
        # Se há problemas com o desenvolvimento
        dev_issues = [i for i in validation_report.all_issues if i.section == "development"]
        if dev_issues:
            dev_codes = [i.code for i in dev_issues]
            if "DEVELOPMENT_NO_FACTS" in dev_codes:
                requirements.append("ADD FACTS: Include specific numbers, statistics, or research findings")
            if "DEVELOPMENT_REPETITIVE" in dev_codes:
                requirements.append("REDUCE REPETITION: Use varied vocabulary and sentence structures")
        
        # Se há problemas com a conclusão
        conclusion_issues = [i for i in validation_report.all_issues if i.section == "conclusion"]
        if conclusion_issues:
            conclusion_codes = [i.code for i in conclusion_issues]
            if "CONCLUSION_NO_CTA" in conclusion_codes:
                requirements.append("ADD CTA: Include call-to-action (like, share, follow, comment)")
            if "CONCLUSION_TOO_LONG" in conclusion_codes:
                requirements.append("SHORTEN CONCLUSION: Keep conclusion under 200 characters")
        
        # Se há problemas de duração
        duration_issues = [i for i in validation_report.all_issues if "DURATION" in i.code]
        if duration_issues:
            requirements.append("ADJUST DURATION: Target 55-60 seconds total speaking time")
            requirements.append("Balance sections: Hook ~15%, Body ~70%, Conclusion ~15% of total time")
        
        # Se há problemas de conteúdo
        content_issues = [i for i in critical_issues if i.code.startswith("CONTENT_")]
        if content_issues:
            requirements.append("IMPROVE CONTENT: Ensure appropriate language and thematic coherence")
        
        # Adicionar incentivos específicos baseados no número de tentativas
        if attempt >= 2:
            requirements.append("FOCUS ON QUALITY: This retry must show significant improvement")
            requirements.append("BE MORE SPECIFIC: Use concrete examples and vivid descriptions")
        
        if attempt >= 3:
            requirements.append("URGENT: Previous attempts failed validation. Address ALL identified issues")
            requirements.append("MAXIMUM ENGAGEMENT: Use questions, emotional words, and storytelling techniques")
        
        # Limitar a quantidade de requisitos para não sobrecarregar o prompt
        return requirements[:8]  # Máximo de 8 requisitos focados

    def _translate_script(self, script_result: Dict[str, Any]):
        plain_script_en = script_result["content_en"]["plain_text"]
        translation_result = self.translator.translate(plain_script_en)

        if translation_result.success:
            script_text_pt = translation_result.translated_text or plain_script_en
self.logger.info(" Roteiro traduzido (PT-BR): %s", script_text_pt)
self.logger.info(" Roteiro traduzido para PT-BR com sucesso")
        else:
            script_text_pt = plain_script_en
self.logger.warning(" Tradução falhou, utilizando roteiro em inglês para TTS")
            if translation_result.error:
self.logger.warning("Motivo da falha de tradução: %s", translation_result.error)

        return {
            "success": translation_result.success,
            "response_time": translation_result.response_time,
            "usage": translation_result.usage,
            "error": translation_result.error,
        }, script_text_pt

    def _synthesize_audio(self, script_text_pt: str) -> Dict[str, Any]:
        """
        Gera narração TTS a partir do texto final do script.

        Contrato com o cliente TTS (ex: KokoroTTSClient):
        - text_to_speech(text, output_basename=...) -> {
              success: bool,
              audio_path: str,
              duration: float,
              voice: str,
              lang_code: str,
              ...
          }
        """
self.logger.info(" ETAPA 2: Síntese de Áudio TTS...")

        output_basename = f"narracao_{datetime.now().strftime('%H%M%S')}"
        result = self.tts_client.text_to_speech(
            script_text_pt,
            output_basename=output_basename,
        )

        if not result.get("success"):
            raise RuntimeError(f"Falha na síntese de áudio: {result.get('error')}")

        audio_path = result.get("audio_path")
        duration = float(result.get("duration", 0.0))
        voice = result.get("voice")

self.logger.info(" Áudio gerado: %s", audio_path)
self.logger.info("⏱ Duração: %.2fs", duration)
        if voice:
self.logger.info(" Voz: %s", voice)

        return {
            "success": True,
            "file_path": audio_path,
            "duration": duration,
            "voice": voice,
        }

    def _extract_broll(self, theme_content: str, *, search_queries: Optional[List[str]] = None):
self.logger.info(" ETAPA 3: Extração de B-roll com Semantic Matching Avançado...")

        # Estratégia priorizada com semantic matching:
        # 1) Queries explícitas (BrollQueryService)
        # 2) LLM especializado (SemanticAnalyzer) 
        # 3) Fallback heurístico local
        # 4) Semantic matching avançado para melhorar seleção

        queries: List[str] = []

        # 1) Queries explícitas (já geradas em etapa anterior, se houver)
        if search_queries:
            queries.extend([q for q in search_queries if q])

        # 2) Tentar LLM interno do SemanticAnalyzer para gerar queries otimizadas
        if not queries and theme_content:
            try:
                llm_queries = self.semantic_analyzer.generate_broll_keywords_via_llm(
                    script_text=theme_content,
                    max_queries=6,
                    max_keywords_per_query=4,
                )
                if llm_queries:
                    queries.extend(llm_queries)
self.logger.info(
                        "🔍 Queries de B-roll via LLM (SemanticAnalyzer): %s",
                        llm_queries,
                    )
            except Exception as exc:
self.logger.warning(
                    "⚠️ Falha ao gerar queries de B-roll via LLM (usando fallback local): %s",
                    exc,
                )

        # 3) Fallback heurístico local se nada foi gerado
        if not queries and theme_content:
            keywords = self.semantic_analyzer.extract_keywords(theme_content) or []
            if keywords:
                fallback_query = " ".join(keywords[:4]).strip()
                if fallback_query:
                    queries.append(fallback_query)
            if not queries:
                queries.append(theme_content[:60])

self.logger.info(" Estratégia de busca inicial: %s", queries)

        # Fase 1: Busca inicial no YouTube (mais candidatos que o necessário)
        all_candidates = []
        queries_used = []
        
        for query in queries[:3]:  # Limitar a 3 queries para não sobrecarregar
            try:
                candidates = self.youtube_extractor.search_videos(query, max_results=5)
                if candidates:
                    all_candidates.extend(candidates)
                    queries_used.append(query)
self.logger.info(" Query '%s': %d candidatos encontrados", query, len(candidates))
                else:
self.logger.warning(" Nenhum resultado para query '%s'", query)
            except Exception as error:
self.logger.warning(" Erro na busca por '%s': %s", query, error)

        if not all_candidates:
            raise RuntimeError("Nenhum candidato encontrado em nenhuma busca")

self.logger.info(" Total de candidatos brutos: %d", len(all_candidates))
        
        # Fase 2: Aplicar filtros básicos e pré-validação com CLIP
        filtered_candidates = []
        for candidate in all_candidates:
            # Remover duplicados
            video_id = candidate.get("id")
            if video_id and any(c.get("id") == video_id for c in filtered_candidates):
                continue
                
            # Filtrar duração muito longa
            duration = candidate.get("duration")
            if duration and duration > 180:
self.logger.debug("⏭ Ignorando vídeo muito longo (%.1fs): %s",
                                 duration, candidate.get("title", "sem título"))
                continue
                
            filtered_candidates.append(candidate)
        
self.logger.info(" Candidatos após filtros básicos: %d", len(filtered_candidates))
        
        # Fase 2.5: Pré-validação com ClipVideoPreValidator
        pre_validated_candidates = []
        pre_validation_performed = False
        
        if filtered_candidates and theme_content:
            try:
self.logger.info(" Iniciando pré-validação com ClipVideoPreValidator...")
                pre_validation_performed = True
                
                # Converter candidatos para o formato esperado pelo ClipVideoPreValidator
                video_candidates = []
                for candidate in filtered_candidates[:15]:  # Limitar para performance
                    video_candidate = {
                        "id": candidate.get("id", ""),
                        "title": candidate.get("title", ""),
                        "description": candidate.get("description", ""),
                        "thumbnail_url": candidate.get("thumbnail", ""),
                        "video_url": candidate.get("url", candidate.get("webpage_url", "")),
                        "duration": int(candidate.get("duration", 0)),
                        "view_count": candidate.get("view_count", 0),
                        "upload_date": candidate.get("upload_date", "")
                    }
                    
                    # Criar objeto VideoCandidate
                    from src.video.validation.clip_pre_validator import VideoCandidate
                    video_candidate_obj = VideoCandidate(**video_candidate)
                    video_candidates.append(video_candidate_obj)
                
                # Realizar pré-validação
                validated_candidates = self.clip_pre_validator.validate_candidates(
                    candidates=video_candidates,
                    query=queries_used[0] if queries_used else theme_content[:50],
                    max_results=10
                )
                
                # Converter de volta para formato original
                for validated_candidate in validated_candidates:
                    # Encontrar candidato original correspondente
                    original_candidate = next(
                        (c for c in filtered_candidates 
                         if c.get("id") == validated_candidate.id), 
                        None
                    )
                    
                    if original_candidate:
                        # Adicionar score de relevância ao original
                        original_candidate["pre_validation_score"] = validated_candidate.relevance_score
                        original_candidate["pre_validation_method"] = "clip" if self.clip_pre_validator.clip_scorer else "fallback"
                        pre_validated_candidates.append(original_candidate)
                
self.logger.info(" Pré-validação concluída: %d candidatos válidos", len(pre_validated_candidates))
                
                # Log dos top candidatos pré-validados
                if pre_validated_candidates:
self.logger.info(" Top 5 candidatos pré-validados:")
                    for i, candidate in enumerate(pre_validated_candidates[:5]):
                        score = candidate.get("pre_validation_score", 0)
                        title = candidate.get("title", "sem título")[:50]
                        method = candidate.get("pre_validation_method", "unknown")
self.logger.info("   %d. Score: %.3f (%s) - %s", i+1, score, method, title)
                
            except Exception as error:
self.logger.warning(" Pré-validação falhou, usando candidatos originais: %s", error)
                pre_validation_performed = False
                pre_validated_candidates = filtered_candidates
        
        if not pre_validation_performed:
            pre_validated_candidates = filtered_candidates
self.logger.info(" Pulando pré-validação, usando candidatos filtrados")
        
        # Usar candidatos pré-validados para próxima fase
        filtered_candidates = pre_validated_candidates
        
        # Fase 3: Semantic Matching Avançado se temos conteúdo temático
        scored_candidates = []
        semantic_analysis_performed = False
        
        if theme_content and len(filtered_candidates) > 3:
            try:
self.logger.info("🧠 Iniciando semantic matching avançado...")
                semantic_analysis_performed = True
                
                # Preparar texto de referência para matching
                reference_text = theme_content[:500]  # Limitar para performance
                
                for candidate in filtered_candidates[:10]:  # Limitar a 10 para performance
                    try:
                        score = self.clip_relevance_scorer.calculate_relevance_score(
                            text=reference_text,
                            video_url=candidate.get("url", ""),
                            video_title=candidate.get("title", ""),
                            video_description=candidate.get("description", "")
                        )
                        
                        candidate["relevance_score"] = score
                        scored_candidates.append(candidate)
                        
                    except Exception as error:
self.logger.debug(" Erro no scoring semântico: %s", error)
                        # Atribuir score neutro e continuar
                        candidate["relevance_score"] = 0.5
                        scored_candidates.append(candidate)
                
                # Ordenar por relevância semântica
                scored_candidates.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                # Log dos top candidatos
self.logger.info(" Top 5 candidatos por relevância semântica:")
                for i, candidate in enumerate(scored_candidates[:5]):
                    score = candidate.get("relevance_score", 0)
                    title = candidate.get("title", "sem título")[:50]
self.logger.info("   %d. Score: %.3f - %s", i+1, score, title)
                
            except Exception as error:
self.logger.warning(" Semantic matching falhou, usando ordenação por views: %s", error)
                semantic_analysis_performed = False
                scored_candidates = filtered_candidates
        
        if not semantic_analysis_performed:
            # Fallback: ordenar por número de views
            scored_candidates = filtered_candidates
            scored_candidates.sort(key=lambda x: x.get("view_count", 0), reverse=True)
self.logger.info(" Usando ordenação por views (fallback)")
        
        # Fase 4: Download dos melhores candidatos
        downloaded_videos: List[str] = []
        visited_ids: set[str] = set()
        output_dir = Path("outputs/video")
        
        for candidate in scored_candidates[:5]:  # Tentar baixar até 5 candidatos
            if len(downloaded_videos) >= 3:
                break
                
            video_id = candidate.get("id")
            if video_id and video_id in visited_ids:
                continue

            try:
                real_path = self.youtube_extractor.download_video(candidate["url"], str(output_dir))
                downloaded_videos.append(real_path)
                if video_id:
                    visited_ids.add(video_id)
                
                score = candidate.get("relevance_score", "N/A")
                title = candidate.get("title", "sem título")[:40]
self.logger.info(
                    "📥 Vídeo baixado (%d/3): %s [Score: %s]",
                    len(downloaded_videos),
                    title + "...",
                    f"{score:.3f}" if isinstance(score, float) else score
                )
                
            except Exception as error:
self.logger.warning(
                    "⚠️ Erro ao baixar '%s': %s",
                    candidate.get("title", "sem título"),
                    error,
                )

        if not downloaded_videos:
            raise RuntimeError("Nenhum vídeo foi baixado com sucesso após semantic matching")

        # Preparar resultado
        keywords = self.semantic_analyzer.extract_keywords(theme_content) or []
        
        return {
            "success": True,
            "videos": downloaded_videos,
            "queries": queries_used,
            "keywords": keywords,
            "used_queries": queries_used,
            "validation_pipeline": {
                "pre_validation": {
                    "performed": pre_validation_performed,
                    "method": "clip" if pre_validation_performed and self.clip_pre_validator.clip_scorer else "fallback",
                    "candidates_validated": len(pre_validated_candidates) if pre_validation_performed else 0,
                    "top_pre_validation_score": max([c.get("pre_validation_score", 0) for c in pre_validated_candidates]) if pre_validated_candidates else None
                },
                "semantic_analysis": {
                    "performed": semantic_analysis_performed,
                    "total_candidates": len(all_candidates),
                    "filtered_candidates": len(pre_validated_candidates),
                    "scored_candidates": len(scored_candidates),
                    "top_relevance_score": scored_candidates[0].get("relevance_score") if scored_candidates else None,
                    "average_relevance_score": sum(c.get("relevance_score", 0) for c in scored_candidates[:5]) / min(len(scored_candidates), 5) if scored_candidates else None
                }
            }
        }

    def _analyze_content(self, theme_content: str) -> Dict[str, Any]:
self.logger.info("🧠 ETAPA 4: Análise Semântica...")
        keywords = self.semantic_analyzer.extract_keywords(theme_content)
        category = self.semantic_analyzer.categorize_content(theme_content)

self.logger.info(" Keywords extraídas: %s", keywords)
self.logger.info(" Categoria: %s (%.2f)", category[0], category[1])

        return {
            "keywords": keywords,
            "category": category[0],
            "confidence": category[1],
        }

    def _sync_audio_video(self, audio_path: str, video_paths: List[str]) -> Dict[str, Any]:
self.logger.info(" ETAPA 5: Sincronização Avançada Áudio-Vídeo...")
        
        try:
            # Converter video_paths para segmentos se necessário
            video_segments = []
            for i, video_path in enumerate(video_paths):
                # Obter duração real se possível
                duration = 5.0  # fallback
                if self.video_processor:
                    video_info = self.video_processor.get_video_info(video_path)
                    if video_info and video_info.get("duration"):
                        duration = float(video_info["duration"])
                
                segment = {
                    "path": video_path,
                    "duration": duration,
                    "description": f"B-roll segment {i+1}",
                    "start_time": 0.0,
                    "end_time": duration
                }
                video_segments.append(segment)
            
            # Criar timing do script baseado nas legendas se disponíveis
            script_timing = {
                "audio_path": audio_path,
                "total_duration": 0.0,
                "sections": [],
                "beat_points": []
            }
            
            # Tentar obter duração real do áudio
            try:
                with contextlib.closing(wave.open(audio_path, "rb")) as wav_file:
                    frames = wav_file.getnframes()
                    framerate = wav_file.getframerate()
                    if framerate:
                        script_timing["total_duration"] = frames / float(framerate)
            except Exception:
self.logger.warning(" Não foi possível obter duração exata do áudio, usando fallback")
                script_timing["total_duration"] = 60.0  # fallback
            
            # 1) Otimizar timing das transições
self.logger.info(" Otimizando transições entre segmentos...")
            timing_result = self.timing_optimizer.optimize_transitions(
                video_segments=video_segments,
                audio_timing=script_timing
            )
            
            if timing_result.get("success"):
self.logger.info(" Timing otimizado com %d transições",
                               len(timing_result.get("optimized_segments", [])))
                script_timing["optimized_segments"] = timing_result.get("optimized_segments", [])
                script_timing["transition_effects"] = timing_result.get("transition_effects", [])
            else:
self.logger.warning(" Otimização de timing falhou, usando sincronização básica")
                script_timing["optimized_segments"] = video_segments
            
            # 2) Sincronização avançada áudio-vídeo
self.logger.info(" Realizando sincronização precisa áudio-vídeo...")
            sync_result = self.audio_video_synchronizer.sync_audio_with_video(
                audio_path=audio_path,
                video_segments=script_timing["optimized_segments"],
                script_timing=script_timing
            )
            
            if sync_result.get("success"):
self.logger.info(" Sincronização avançada concluída com sucesso!")
                
                # Extrair informações do resultado
                timeline = sync_result.get("timeline", [])
                sync_points = sync_result.get("sync_points", [])
                total_segments = len(timeline)
                
self.logger.info("   • Timeline sincronizado: %d segmentos", total_segments)
self.logger.info("   • Pontos de sincronia: %d", len(sync_points))
self.logger.info("   • Precisão: %.2fms", sync_result.get("sync_precision", 0) * 1000)
                
                return {
                    "success": True,
                    "audio_path": audio_path,
                    "video_paths": video_paths,
                    "sync_method": "advanced",
                    "timeline": timeline,
                    "sync_points": sync_points,
                    "sync_precision": sync_result.get("sync_precision", 0),
                    "optimized_segments": script_timing["optimized_segments"],
                    "transition_effects": script_timing.get("transition_effects", []),
                    "total_synced_duration": sync_result.get("total_duration", script_timing["total_duration"])
                }
            else:
self.logger.warning(" Sincronização avançada falhou, usando método básico")
                return {
                    "success": True,
                    "audio_path": audio_path,
                    "video_paths": video_paths,
                    "sync_method": "basic_fallback",
                    "error": sync_result.get("error", "Advanced sync failed")
                }
                
        except Exception as error:
self.logger.error(" Erro na sincronização avançada: %s", error)
self.logger.info(" Usando sincronização básica como fallback")
            return {
                "success": True,
                "audio_path": audio_path,
                "video_paths": video_paths,
                "sync_method": "error_fallback",
                "error": str(error)
            }

    def _process_final_video(
        self,
        video_paths: List[str],
        audio_path: str,
        *,
        captions: Optional[List[Dict[str, Any]]] = None,
        sync_result: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
self.logger.info(" ETAPA 6: Processamento Final com FinalVideoComposer...")

        # Verificar método de sincronização usado
        sync_method = "basic"
        if sync_result:
            sync_method = sync_result.get("sync_method", "basic")
self.logger.info(" Método de sincronização: %s", sync_method)
            
            if sync_method == "advanced":
self.logger.info(" Usando timing otimizado da sincronização avançada")
self.logger.info("   • Pontos de sincronia: %d", len(sync_result.get("sync_points", [])))
self.logger.info("   • Precisão: %.2fms", sync_result.get("sync_precision", 0) * 1000)

        if not audio_path or not Path(audio_path).exists():
self.logger.error(" Áudio inexistente para composição: %s", audio_path)
            return None
        if not video_paths:
self.logger.error(" Nenhum vídeo B-roll disponível para composição final")
            return None

        segments: List[VideoSegment] = []
        
        # Se temos sincronização avançada, usar segmentos otimizados
        if sync_result and sync_method == "advanced" and sync_result.get("optimized_segments"):
            optimized_segments = sync_result["optimized_segments"]
            
            for opt_segment in optimized_segments:
                path_obj = Path(opt_segment["path"])
                if not path_obj.exists():
self.logger.warning(" Vídeo otimizado ausente ignorado: %s", opt_segment["path"])
                    continue
                
                # Usar duração otimizada da sincronização
                duration = opt_segment.get("duration", 5.0)
                
                segment = VideoSegment(
                    path=str(path_obj), 
                    duration=duration,
                    transition_in=opt_segment.get("transition_in", "fade"),
                    transition_out=opt_segment.get("transition_out", "fade")
                )
                segments.append(segment)
self.logger.debug("   • Segmento otimizado: %s (%.2fs)", path_obj.name, duration)
        else:
            # Fallback para método básico
            for path in video_paths:
                path_obj = Path(path)
                if not path_obj.exists():
self.logger.warning(" Vídeo ausente ignorado: %s", path)
                    continue

                video_info = self.video_processor.get_video_info(path)
                if video_info and video_info.get("duration"):
                    duration = float(video_info["duration"])
                else:
self.logger.warning(" Duração desconhecida para %s, usando fallback de 5s", path)
                    duration = 5.0

                segments.append(VideoSegment(path=str(path_obj), duration=duration))

        if not segments:
self.logger.error(" Nenhum segmento de vídeo válido após validação")
            return None

        composer = self._composer_factory()
        template_config: Optional[TemplateConfig] = composer.templates.get("professional")
        if not template_config and composer.templates:
            template_config = next(iter(composer.templates.values()))
        if not template_config:
self.logger.error(" FinalVideoComposer não disponibilizou templates para composição")
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
            "sync_method": sync_method,
        }
        
        # Adicionar informações avançadas de sincronização se disponíveis
        if sync_result and sync_method == "advanced":
            metadata.update({
                "sync_precision_ms": sync_result.get("sync_precision", 0) * 1000,
                "sync_points_count": len(sync_result.get("sync_points", [])),
                "transition_effects": sync_result.get("transition_effects", []),
                "optimized_timing": True
            })

        try:
            final_video_path = composer.compose_final_video(
                audio_path=audio_path,
                video_segments=segments,
                template_config=template_config,
                captions=captions,
                output_path="outputs/final/video_final_aishorts.mp4",
                metadata=metadata,
            )
self.logger.info(" Vídeo final gerado: %s", final_video_path)
            return final_video_path
        except Exception as error:
self.logger.error(" ERRO NA COMPOSIÇÃO FINAL: %s", error)
print(f" ERRO NA COMPOSIÇÃO FINAL: {error}")
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
self.logger.warning(" Não foi possível ler duração do áudio %s", audio_path)
        return None

    def _log_summary(self, theme_result, script_result, audio_result, broll_result, analysis_result, final_video_path, total_time):
self.logger.info("=" * 70)
self.logger.info(" PIPELINE CONCLUÍDO COM SUCESSO!")
self.logger.info("=" * 70)
self.logger.info("⏱ Tempo total: %.2fs", total_time)
self.logger.info(" Tema (qualidade): %.2f", theme_result["quality"])
self.logger.info(
            "📝 Roteiro (EN) - Duração estimada: %.1fs, Qualidade: %.2f",
            script_result["total_duration"],
            script_result["quality_score"],
        )
self.logger.info(" Áudio (PT-BR): %.2fs", audio_result["duration"])
self.logger.info(" B-roll: %d vídeos", len(broll_result["videos"]))
self.logger.info("🧠 Análise: %s", analysis_result["keywords"])
self.logger.info(" Saída: %s", final_video_path)

    def _save_report(self, results: Dict[str, Any]):
        report_path = f"outputs/pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as file_handle:
            json.dump(results, file_handle, indent=2, ensure_ascii=False)
self.logger.info(" Relatório salvo: %s", report_path)

    def _fail_results(self, results: Dict[str, Any], start_time: float, error: str) -> Dict[str, Any]:
        results["status"] = "failed"
        results["error"] = error
        results["total_time"] = time.time() - start_time
        return results
