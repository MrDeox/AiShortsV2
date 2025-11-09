"""
AiShortsOrchestrator - Versão refatorada com serviços especializados.
Este arquivo substitui o orchestrator.py original, delegando responsabilidades
para serviços específicos e reduzindo complexidade.
"""

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
from src.core.graceful_degradation import get_degradation_manager
from src.core.health_checker import get_health_checker, setup_default_health_checks

# Importar otimizações de memória local
try:
    from src.core.model_manager import get_model_manager
    from src.core.memory_monitor import get_memory_monitor
    MEMORY_OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    MEMORY_OPTIMIZATIONS_AVAILABLE = False


class AiShortsOrchestrator:
    """
    Responsável por executar o pipeline end-to-end do AiShorts.
    
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
        self.graceful_degradation = get_degradation_manager()
        self._setup_graceful_degradation()

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
        
        # Sistema de health checks
        self.health_checker = get_health_checker()
        self._setup_health_checks()
    
    def _setup_health_checks(self):
        """Configura health checks para os serviços."""
        try:
            # Setup checks padrão
            setup_default_health_checks()
            
            # Adicionar checks específicos do orchestrator
            self.health_checker.register_check(
                "content_service",
                self._check_content_service
            )
            
            self.health_checker.register_check(
                "media_service", 
                self._check_media_service
            )
            
            self.health_checker.register_check(
                "video_service",
                self._check_video_service
            )
            
self.logger.info(" Health checks configurados")
            
        except Exception as e:
self.logger.error(f" Erro ao configurar health checks: {e}")
    
    def _check_content_service(self) -> Dict[str, Any]:
        """Verifica saúde do ContentGenerationService."""
        try:
            # Verificar se componentes estão inicializados
            if not all([
                self.content_service.theme_generator,
                self.content_service.script_generator,
                self.content_service.translator,
                self.content_service.tts_client,
                self.content_service.script_validator
            ]):
                return {
                    "status": "unhealthy",
                    "message": "Missing dependencies"
                }
            
            # Verificar LLM helpers se disponível
            if self.content_service.llm_helpers:
                try:
                    # Testar conexão com cliente
                    client = self.content_service.llm_helpers.client
                    if not client:
                        return {
                            "status": "degraded",
                            "message": "LLM client not available"
                        }
                except Exception:
                    pass
            
            return {
                "status": "healthy",
                "message": "Content service operational",
                "details": {
                    "llm_enabled": self.content_service.llm_helpers is not None,
                    "recent_themes_count": len(self.content_service._recent_themes)
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Content service error: {str(e)}"
            }
    
    def _check_media_service(self) -> Dict[str, Any]:
        """Verifica saúde do MediaAcquisitionService."""
        try:
            if not all([
                self.media_service.youtube_extractor,
                self.media_service.semantic_analyzer,
                self.media_service.broll_query_service,
                self.media_service.clip_relevance_scorer
            ]):
                return {
                    "status": "unhealthy",
                    "message": "Missing dependencies"
                }
            
            return {
                "status": "healthy",
                "message": "Media service operational",
                "details": {
                    "llm_broll_planner": self.media_service.llm_helpers is not None
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Media service error: {str(e)}"
            }
    
    def _check_video_service(self) -> Dict[str, Any]:
        """Verifica saúde do VideoAssemblyService."""
        try:
            if not all([
                self.video_service.video_processor,
                self.video_service.caption_service
            ]):
                return {
                    "status": "unhealthy",
                    "message": "Missing dependencies"
                }
            
            # Verificar se o composer factory funciona
            try:
                composer = self.video_service.video_composer_factory()
                if not composer:
                    return {
                        "status": "degraded",
                        "message": "Video composer factory failed"
                    }
            except Exception:
                pass
            
            return {
                "status": "healthy",
                "message": "Video service operational"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Video service error: {str(e)}"
            }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """
        Verifica saúde completa do sistema.
        
        Returns:
            Relatório de saúde com status de todos os componentes
        """
self.logger.info(" Verificando saúde do sistema...")
        
        # Executar todos os checks
        results = await self.health_checker.run_all_checks()
        
        # Adicionar informações específicas do orchestrator
        orchestrator_info = {
            "services": {
                "content_service": self.content_service is not None,
                "media_service": self.media_service is not None,
                "video_service": self.video_service is not None
            },
            "optimizations": {
                "memory_optimization": MEMORY_OPTIMIZATIONS_AVAILABLE,
                "graceful_degradation": self.graceful_degradation is not None
            }
        }
        
        # Construir relatório completo
        report = {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_info": orchestrator_info,
            "health_checks": {name: check.to_dict() for name, check in results.items()},
            "summary": self.health_checker.get_health_summary()
        }
        
        # Log do resumo
        summary = report["summary"]
        icon = "✅" if summary["status"] == "healthy" else "⚠️" if summary["status"] == "degraded" else "❌"
self.logger.info(f"{icon} Sistema {summary['status'].upper()}: {summary['message']}")
        
        return report

    def _setup_graceful_degradation(self):
        """Configura sistema de graceful degradation."""
        try:
            # Configurar fallbacks padrão
            from src.core.graceful_degradation import setup_default_fallbacks
            setup_default_fallbacks()
            
            # Registrar dependências principais para monitoramento
            dependencies_to_monitor = [
                ("openrouter", lambda: bool(hasattr(self, 'openrouter') and self.openrouter.client and hasattr(self.openrouter, 'api_key'))),
                ("tts", lambda: self.content_service.tts_client is not None),
                ("youtube", lambda: self.media_service.youtube_extractor is not None),
                ("memory", lambda: not (self.memory_monitor and self.memory_monitor.suggest_cleanup())),
                ("clip", lambda: self.media_service.clip_relevance_scorer is not None)
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

    def run(self, theme_category: ThemeCategory = ThemeCategory.ANIMALS) -> Dict[str, Any]:
        """
        Executa o pipeline completo usando serviços especializados.
        
        Returns:
            Dict[str, Any]: Resultado completo do pipeline em formato de dicionário
        """
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

    def _create_failed_result(self, pipeline_result: PipelineResult, start_time: float, error: str) -> Dict[str, Any]:
        """Cria resultado de falha do pipeline."""
        pipeline_result.status = "failed"
        pipeline_result.error = error
        pipeline_result.total_time = time.time() - start_time
        return pipeline_result.to_dict()
    
    def _cleanup_memory(self, initial_stats):
        """Realiza cleanup de memória."""
        # Cleanup de memória ao final
        if self.model_manager:
self.logger.info("🧹 Fazendo cleanup final de modelos...")
            self.model_manager.cleanup_models()
        
        if self.memory_monitor and initial_stats:
            final_stats = self.memory_monitor.get_current_stats()
            memory_delta = final_stats.process_gb - initial_stats.process_gb
self.logger.info(
                f"💾 Memória final: {final_stats.process_gb:.2f}GB "
                f"(Δ{memory_delta:+.2f}GB, {final_stats.system_percent:.1f}% sistema)"
            )
            
            # Sugerir garbage collection se necessário
            if self.memory_monitor.suggest_cleanup():
                self.memory_monitor.force_garbage_collection()

    def _setup_directories(self):
        """Cria diretórios necessários para o pipeline."""
        for dir_path in ["outputs/video", "outputs/audio", "outputs/final", "temp"]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def _log_summary(self, theme_result, script_result, audio_result, broll_result, analysis_result, final_video_path, total_time):
        """Registra resumo do pipeline executado com sucesso."""
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
        """Salva relatório detalhado da execução do pipeline."""
        report_path = f"outputs/pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as file_handle:
            json.dump(results, file_handle, indent=2, ensure_ascii=False)
self.logger.info(" Relatório salvo: %s", report_path)