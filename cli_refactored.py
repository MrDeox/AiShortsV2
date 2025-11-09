#!/usr/bin/env python3
"""
CLI para o AiShorts v2.0 - Versão Refatorada
Interface de linha de comando simplificada para testar o pipeline refatorado.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

# Adicionar src ao path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(1, str(SRC_DIR))

from src.generators.prompt_engineering import ThemeCategory
from src.pipeline.orchestrator import AiShortsOrchestrator
from src.utils.logging_config import init_logging, get_logger
from src.config.settings import OpenRouterSettings, LoggingSettings


def create_orchestrator_for_cli(logger):
    """Cria instância do AiShortsOrchestrator para CLI."""
    from src.generators.theme_generator import ThemeGenerator
    from src.generators.script_generator import ScriptGenerator
    from src.core.openrouter_client import OpenRouterClient
    from src.utils.translator import DeepLTranslator
    from src.tts.kokoro_tts import KokoroTTSClient
    from src.video.extractors.youtube_extractor import YouTubeExtractor
    from src.video.matching.semantic_analyzer import SemanticAnalyzer
    from src.video.sync.audio_video_synchronizer import AudioVideoSynchronizer
    from src.video.processing.video_processor import VideoProcessor
    from src.pipeline.services.broll_query_service import BrollQueryService
    from src.pipeline.services.caption_service import CaptionService
    from src.video.generators.final_video_composer import FinalVideoComposer
    from src.validators.script_validator import ScriptValidator
    
    # Carregar configurações
    openrouter_settings = OpenRouterSettings()
    
    # Verificar se API key está configurada
    if not openrouter_settings.api_key:
        logger.error("❌ OPENROUTER_API_KEY não configurada no .env")
        logger.error("   Configure a chave e tente novamente")
        return None
    
    try:
        # Inicializar componentes
        openrouter_client = OpenRouterClient(
            api_key=openrouter_settings.api_key,
            model=openrouter_settings.model,
            base_url=openrouter_settings.base_url
        )
        
        theme_generator = ThemeGenerator(
            client=openrouter_client,
            cache_enabled=True
        )
        
        script_generator = ScriptGenerator(
            client=openrouter_client,
            target_duration=60.0
        )
        
        translator = DeepLTranslator(
            api_key=getattr(settings, 'deepl_api_key', ''),
            source_lang='EN',
            target_lang='PT'
        )
        
        tts_client = KokoroTTSClient()
        
        youtube_extractor = YouTubeExtractor()
        semantic_analyzer = SemanticAnalyzer()
        audio_video_sync = AudioVideoSynchronizer()
        video_processor = VideoProcessor()
        
        # Serviços
        broll_query_service = BrollQueryService(client=openrouter_client)
        caption_service = CaptionService()
        
        video_composer_factory = lambda: FinalVideoComposer()
        script_validator = ScriptValidator()
        
        # Criar orchestrator
        orchestrator = AiShortsOrchestrator(
            theme_generator=theme_generator,
            script_generator=script_generator,
            translator=translator,
            tts_client=tts_client,
            youtube_extractor=youtube_extractor,
            semantic_analyzer=semantic_analyzer,
            audio_video_sync=audio_video_sync,
            video_processor=video_processor,
            broll_query_service=broll_query_service,
            caption_service=caption_service,
            video_composer_factory=video_composer_factory,
            script_validator=script_validator,
            logger=logger
        )
        
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar componentes: {str(e)}")
        return None


def run_pipeline(category: ThemeCategory, test_mode: bool = False):
    """Executa o pipeline refatorado."""
    logger = get_logger(__name__)
    logger.info("=" * 70)
    logger.info("🎬 AISHORTS V2.0 - PIPELINE REFACTORADO")
    logger.info("=" * 70)
    
    if test_mode:
        logger.info("🧪 MODO TESTE ATIVADO")
        logger.info("   • Usando mocks para componentes externos")
        logger.info("   • Geração limitada para validação")
        logger.info("")
        
        # Criar orchestrator com mocks
        from unittest.mock import Mock, MagicMock
        mock_dependencies = {
            'theme_generator': Mock(),
            'script_generator': Mock(),
            'translator': Mock(),
            'tts_client': Mock(),
            'youtube_extractor': Mock(),
            'semantic_analyzer': Mock(),
            'audio_video_sync': Mock(),
            'video_processor': Mock(),
            'broll_query_service': Mock(),
            'caption_service': Mock(),
            'video_composer_factory': Mock(),
            'script_validator': Mock()
        }
        
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        # Mockar retornos básicos
        from src.models.unified_models import (
            GeneratedTheme, GeneratedScript, ScriptSection,
            TTSAudioResult, BrollMatchResult, VideoSyncPlan
        )
        
        mock_theme = GeneratedTheme(
            content=f"Teste de tema para categoria {category.value}",
            category=category,
            quality_score=0.85
        )
        mock_script = GeneratedScript(
            title="Teste de Script",
            theme=mock_theme,
            sections=[
                ScriptSection(name="hook", content="Hook de teste", duration_seconds=10),
                ScriptSection(name="body", content="Body de teste", duration_seconds=40),
                ScriptSection(name="conclusion", content="Conclusion de teste", duration_seconds=10)
            ],
            total_duration=60.0
        )
        
        # Mockar métodos
        orchestrator.content_service.generate_theme = Mock(return_value=(mock_theme, {
            "content_en": mock_theme.content,
            "category": mock_theme.category.value,
            "quality": mock_theme.quality_score
        }))
        orchestrator.content_service.generate_script = Mock(return_value=(mock_script, {
            "title": mock_script.title,
            "total_duration": mock_script.total_duration,
            "content_en": {
                "hook": "Hook de teste",
                "body": "Body de teste",
                "conclusion": "Conclusion de teste",
                "plain_text": "Hook de teste Body de teste Conclusion de teste"
            }
        }))
        orchestrator.content_service.translate_script = Mock(return_value=Mock(translated_text="Texto traduzido para teste", to_dict={"success": True}))
        orchestrator.content_service.synthesize_audio = Mock(return_value=TTSAudioResult(success=True, audio_path="/tmp/test.wav", duration=60.0))
        orchestrator.media_service.broll_query_service.generate_queries = Mock(return_value=["query1", "query2"])
        orchestrator.media_service.extract_broll = Mock(return_value=BrollMatchResult(
            success=True,
            videos=["/tmp/video1.mp4"],
            queries_used=["query1"],
            keywords=[],
            validation_pipeline={"semantic_analysis": {"performed": True}}
        ))
        orchestrator.media_service.analyze_content = Mock(return_value={"keywords": ["keyword1", "keyword2"]})
        orchestrator.video_service.sync_audio_video = Mock(return_value=VideoSyncPlan(
            success=True,
            audio_path="/tmp/test.wav",
            video_paths=["/tmp/video1.mp4"],
            sync_method="basic"
        ))
        orchestrator.video_service.caption_service.build_captions = Mock(return_value=[])
        orchestrator.video_service.compose_final_video = Mock(return_value="/tmp/final_test.mp4")
        
        logger.info(f"🎯 Categoria: {category.value}")
        
    else:
        logger.info("🚀 MODO PRODUÇÃO ATIVADO")
        logger.info(f"🎯 Categoria: {category.value}")
        logger.info("")
        
        # Criar orchestrator real
        orchestrator = create_orchestrator_for_cli(logger)
        if not orchestrator:
            logger.error("❌ Não foi possível inicializar o pipeline")
            return False
    
    # Executar pipeline
    try:
        results = orchestrator.run(theme_category=category)
        
        if results.get("status") == "success":
            logger.info("")
            logger.info("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
            logger.info(f"⏱️ Tempo total: {results.get('total_time', 0):.2f}s")
            
            if results.get("final", {}).get("success"):
                video_path = results["final"].get("video_path")
                logger.info(f"📁 Vídeo final: {video_path}")
            
            return True
        else:
            logger.error("")
            logger.error("❌ PIPELINE FALHOU!")
            if results.get("error"):
                logger.error(f"Erro: {results['error']}")
            return False
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Pipeline interrompido pelo usuário")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        return False


def main():
    """Função principal da CLI."""
    parser = argparse.ArgumentParser(
        description="AiShorts v2.0 - Pipeline Refatorado",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "category",
        nargs="?",
        choices=[cat.value.lower() for cat in ThemeCategory],
        default="animals",
        help="Categoria do tema (default: animals)"
    )
    
    parser.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="Executar em modo teste (usando mocks)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Logs detalhados (debug)"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    level = "DEBUG" if args.verbose else "INFO"
    init_logging(level=level, log_file=f"logs/cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger = get_logger(__name__)
    
    # Converter categoria
    try:
        # Encontrar a categoria correspondente (case insensitive)
        category_map = {cat.value.lower(): cat for cat in ThemeCategory}
        category = category_map[args.category.lower()]
    except KeyError:
        logger.error(f"❌ Categoria inválida: {args.category}")
        logger.info(f"   Categorias disponíveis: {', '.join(sorted([cat.value for cat in ThemeCategory]))}")
        sys.exit(1)
    
    # Executar pipeline
    success = run_pipeline(category, test_mode=args.test)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()