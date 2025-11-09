#!/usr/bin/env python3
"""
Teste das integrações LLM implementadas no ContentGenerationService
"""

import sys
import asyncio
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
from src.config.settings import config
from src.pipeline.services.content_generation_service import ContentGenerationService
from src.generators.theme_generator import ThemeGenerator
from src.generators.script_generator import ScriptGenerator
from src.utils.translator import Translator
from src.tts.kokoro_tts import KokoroTTSClient
from src.validators.script_validator import ScriptValidator

# Configurar logging
init_logging(level="INFO", log_file=f"logs/llm_test_{int(Path(__file__).stat().st_mtime)}.log")
logger = get_logger(__name__)


async def test_llm_theme_strategy():
    """Testa o LLM Theme Strategy Engine."""
    logger.info("\n" + "="*70)
    logger.info("🧠 TESTANDO LLM THEME STRATEGY ENGINE")
    logger.info("="*70)
    
    # Verificar configuração
    logger.info(f"✅ Feature flag LLM Theme Strategy: {config.llm_integration.use_llm_theme_strategy}")
    
    # Criar ContentGenerationService
    theme_generator = ThemeGenerator()
    script_generator = ScriptGenerator()
    translator = Translator(api_key="", source_lang='EN', target_lang='PT', service="openrouter")
    tts_client = KokoroTTSClient()
    script_validator = ScriptValidator()
    
    content_service = ContentGenerationService(
        theme_generator=theme_generator,
        script_generator=script_generator,
        translator=translator,
        tts_client=tts_client,
        script_validator=script_validator,
        logger=logger
    )
    
    # Testar geração de tema com LLM
    with LogPerformance(logger, "Geração de tema com LLM"):
        try:
            theme, result = await content_service.generate_theme(ThemeCategory.TECHNOLOGY)
            
            logger.info(f"✅ Tema gerado: {theme.content}")
            logger.info(f"📊 Qualidade: {theme.quality_score:.2f}")
            
            if theme.metadata:
                logger.info(f"🎯 Angle: {theme.metadata.get('angle', 'N/A')}")
                logger.info(f"📈 Uniqueness: {theme.metadata.get('uniqueness_score', 'N/A')}")
                logger.info(f"🔥 Virality: {theme.metadata.get('virality_potential', 'N/A')}")
                logger.info(f"🤖 Gerado por: {theme.metadata.get('generated_by', 'N/A')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar LLM Theme Strategy: {e}")
            return False


async def test_llm_script_refiner():
    """Testa o LLM Script Refiner."""
    logger.info("\n" + "="*70)
    logger.info("🧠 TESTANDO LLM SCRIPT REFINER")
    logger.info("="*70)
    
    # Verificar configuração
    logger.info(f"✅ Feature flag LLM Script Refiner: {config.llm_integration.use_llm_script_refiner}")
    
    # Criar ContentGenerationService
    theme_generator = ThemeGenerator()
    script_generator = ScriptGenerator()
    translator = Translator(api_key="", source_lang='EN', target_lang='PT', service="openrouter")
    tts_client = KokoroTTSClient()
    script_validator = ScriptValidator()
    
    content_service = ContentGenerationService(
        theme_generator=theme_generator,
        script_generator=script_generator,
        translator=translator,
        tts_client=tts_client,
        script_validator=script_validator,
        logger=logger
    )
    
    # Gerar tema primeiro
    logger.info("🎯 Gerando tema para teste...")
    theme, _ = await content_service.generate_theme(ThemeCategory.SCIENCE)
    
    # Testar geração de script com LLM Refiner
    with LogPerformance(logger, "Geração de script com LLM Refiner"):
        try:
            script, result = await content_service.generate_script(
                theme=theme,
                target_platform="tiktok",
                max_attempts=2,  # Reduzir para forçar refinamento
                validation_threshold=80.0  # Aumentar threshold para forçar refinamento
            )
            
            logger.info(f"✅ Script gerado e validado!")
            logger.info(f"📊 Score: {script.quality_score:.2f}")
            logger.info(f"⏱️ Duração: {script.total_duration:.1f}s")
            
            if script.metadata:
                logger.info(f"🔧 Refinado via LLM: {script.metadata.get('llm_refined', False)}")
                if script.metadata.get('llm_refined'):
                    logger.info(f"🔄 Contagem de refinamentos: {script.metadata.get('refinement_count', 0)}")
                    logger.info(f"📝 Notas: {script.metadata.get('refinement_notes', [])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar LLM Script Refiner: {e}")
            return False


async def main():
    """Função principal de teste."""
    logger.info("=" * 70)
    logger.info("🧪 AISHORTS V2.0 - TESTE DE INTEGRAÇÕES LLM")
    logger.info("=" * 70)
    
    # Verificar configurações
    logger.info("\n📋 Configurações das integrações LLM:")
    logger.info(f"   • Theme Strategy: {config.llm_integration.use_llm_theme_strategy}")
    logger.info(f"   • Script Refiner: {config.llm_integration.use_llm_script_refiner}")
    logger.info(f"   • B-roll Planner: {config.llm_integration.use_llm_broll_planner}")
    logger.info(f"   • Reranker: {config.llm_integration.use_llm_reranker}")
    logger.info(f"   • Co-reviewer: {config.llm_integration.use_llm_co_reviewer}")
    logger.info(f"   • Caption Validator: {config.llm_integration.use_llm_caption_validator}")
    logger.info(f"   • Content Cache: {config.llm_integration.enable_content_cache}")
    logger.info(f"   • Cache TTL: {config.llm_integration.cache_ttl_hours}h")
    
    # Verificar API key
    import os
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        logger.info(f"✅ API Key OpenRouter configurada: {api_key[:15]}...")
    else:
        logger.error("❌ OPENROUTER_API_KEY não configurada!")
        return
    
    # Testar integrações
    results = []
    
    # Testar Theme Strategy
    theme_result = await test_llm_theme_strategy()
    results.append(("Theme Strategy Engine", theme_result))
    
    # Testar Script Refiner
    script_result = await test_llm_script_refiner()
    results.append(("Script Refiner", script_result))
    
    # Resumo dos testes
    logger.info("\n" + "="*70)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("="*70)
    
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"   {name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        logger.info("\n🎉 TODAS AS INTEGRAÇÕES LLM PASSARAM NOS TESTES!")
        logger.info("\n🚀 Para executar o pipeline completo com LLM:")
        logger.info("   python main.py")
        logger.info("   python cli_refactored.py technology")
    else:
        logger.error("\n❌ ALGUMAS INTEGRAÇÕES FALHARAM. VERIFIQUE OS LOGS.")


if __name__ == "__main__":
    asyncio.run(main())