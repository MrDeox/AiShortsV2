#!/usr/bin/env python3
"""
Teste do pipeline refatorado com componentes reais
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Adicionar src ao path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(1, str(SRC_DIR))

# Carregar .env
load_dotenv(BASE_DIR / ".env")

from src.generators.prompt_engineering import ThemeCategory
from src.pipeline.orchestrator import AiShortsOrchestrator
from src.utils.logging_config import init_logging, get_logger, LogPerformance
from src.config.settings import OpenRouterSettings
from src.generators.theme_generator import ThemeGenerator
from src.generators.script_generator import ScriptGenerator
from src.core.openrouter_client import OpenRouterClient
from src.utils.translator import Translator
from src.tts.kokoro_tts import KokoroTTSClient
from src.video.extractors.youtube_extractor import YouTubeExtractor
from src.video.matching.semantic_analyzer import SemanticAnalyzer
from src.video.sync.audio_video_synchronizer import AudioVideoSynchronizer
from src.video.processing.video_processor import VideoProcessor
from src.pipeline.services.broll_query_service import BrollQueryService
from src.pipeline.services.caption_service import CaptionService
from src.video.generators.final_video_composer import FinalVideoComposer
from src.validators.script_validator import ScriptValidator
from src.utils.exceptions import AiShortsError

# Configurar logging
init_logging(level="INFO", log_file=f"logs/real_test_{int(Path(__file__).stat().st_mtime)}.log")
logger = get_logger(__name__)


def create_real_orchestrator():
    """Cria orchestrator com componentes reais."""
    logger.info("🔧 Inicializando componentes reais...")
    
    # Configurações
    import os
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY não encontrada no .env")
    
    # Verificar se a API key está no formato correto
    if not api_key.startswith('sk-or'):
        logger.warning(f"⚠️ API key com formato incomum: {api_key[:10]}...")
    
    logger.info(f"✅ API Key configurada: {api_key[:15]}...")
    
    # Inicializar componentes
    openrouter_client = OpenRouterClient()
    
    logger.info("✅ OpenRouterClient inicializado")
    
    theme_generator = ThemeGenerator()
    logger.info("✅ ThemeGenerator inicializado")
    
    script_generator = ScriptGenerator()
    logger.info("✅ ScriptGenerator inicializado")
    
    translator = Translator(
        api_key="",
        source_lang='EN',
        target_lang='PT',
        service="openrouter"  # Usar OpenRouter para tradução
    )
    logger.info("✅ Translator inicializado (modo fallback)")
    
    tts_client = KokoroTTSClient()
    logger.info("✅ TTS Client inicializado")
    
    youtube_extractor = YouTubeExtractor()
    logger.info("✅ YouTubeExtractor inicializado")
    
    semantic_analyzer = SemanticAnalyzer()
    logger.info("✅ SemanticAnalyzer inicializado")
    
    audio_video_sync = AudioVideoSynchronizer()
    logger.info("✅ AudioVideoSynchronizer inicializado")
    
    video_processor = VideoProcessor()
    logger.info("✅ VideoProcessor inicializado")
    
    broll_query_service = BrollQueryService(client=openrouter_client)
    logger.info("✅ BrollQueryService inicializado")
    
    caption_service = CaptionService()
    logger.info("✅ CaptionService inicializado")
    
    video_composer_factory = lambda: FinalVideoComposer()
    logger.info("✅ VideoComposer factory criado")
    
    script_validator = ScriptValidator()
    logger.info("✅ ScriptValidator inicializado")
    
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
    
    logger.info("✅ AiShortsOrchestrator criado com componentes reais")
    return orchestrator


def test_individual_components(orchestrator):
    """Testa componentes individualmente."""
    logger.info("\n🧪 Testando componentes individualmente...")
    
    with LogPerformance(logger, "Teste de geração de tema"):
        try:
            theme, theme_result = orchestrator.content_service.generate_theme(ThemeCategory.ANIMALS)
            logger.info(f"✅ Tema gerado: {theme.content[:50]}...")
            logger.info(f"   Score: {theme.quality_score:.2f}")
        except Exception as e:
            logger.error(f"❌ Falha na geração de tema: {e}")
            raise
    
    return theme, theme_result


def main():
    """Função principal."""
    logger.info("=" * 70)
    logger.info("🎬 AISHORTS V2.0 - TESTE COM COMPONENTES REAIS")
    logger.info("=" * 70)
    
    try:
        # Criar orchestrator
        orchestrator = create_real_orchestrator()
        
        # Testar componentes
        theme, theme_result = test_individual_components(orchestrator)
        
        logger.info("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("\n📋 Componentes validados:")
        logger.info("   ✅ OpenRouter API conectada")
        logger.info("   ✅ Geração de tema funcional")
        logger.info("   ✅ Serviços inicializados")
        logger.info("   ✅ Pipeline estruturado")
        
        logger.info("\n🚀 Para executar o pipeline completo:")
        logger.info("   python test_real_pipeline.py --full")
        logger.info("   python cli_refactored.py animals")
        
    except AiShortsError as e:
        logger.error(f"❌ Erro do AiShorts: {e}")
        if e.details:
            logger.error(f"Detalhes: {e.details}")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}", exc_info=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste do pipeline com componentes reais")
    parser.add_argument("--full", action="store_true", help="Executar pipeline completo")
    
    args = parser.parse_args()
    
    if args.full:
        logger.info("🚀 Executando pipeline completo...")
        # Criar orchestrator e executar
        try:
            orchestrator = create_real_orchestrator()
            with LogPerformance(logger, "Pipeline completo"):
                results = orchestrator.run(ThemeCategory.ANIMALS)
                
                if results.get("status") == "success":
                    logger.info("\n✅ PIPELINE CONCLUÍDO!")
                    logger.info(f"⏱️ Tempo total: {results.get('total_time', 0):.2f}s")
                    if results.get("final", {}).get("video_path"):
                        logger.info(f"📁 Vídeo: {results['final']['video_path']}")
                else:
                    logger.error(f"❌ Falha no pipeline: {results.get('error')}")
        except Exception as e:
            logger.error(f"❌ Erro: {e}", exc_info=True)
    else:
        main()