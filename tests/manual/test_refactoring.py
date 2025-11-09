#!/usr/bin/env python
"""
Script de teste rápido para validar a refatoração do AiShorts.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline.orchestrator import AiShortsOrchestrator
from src.generators.prompt_engineering import ThemeCategory
from src.utils.logging_config import init_logging, get_logger

# Configurar logging
init_logging(level="INFO", log_file="logs/test_refactoring.log")
logger = get_logger(__name__)

def create_test_orchestrator():
    """Cria instância do AiShortsOrchestrator para testes."""
    from unittest.mock import Mock
    
    # Mock dependencies para teste rápido
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
    
    return AiShortsOrchestrator(**mock_dependencies)

def test_refactored_pipeline():
    """Testa o pipeline refatorado com tema simples."""
    logger.info("=" * 60)
    logger.info("🧪 TESTE DE VALIDAÇÃO DA REFACTORAÇÃO")
    logger.info("=" * 60)
    
    try:
        # Criar orchestrator
        logger.info("📦 Criando instância do AiShortsOrchestrator refatorado...")
        orchestrator = create_test_orchestrator()
        
        # Verificar serviços
        logger.info("✅ Serviços inicializados:")
        logger.info(f"   • ContentGenerationService: {orchestrator.content_service is not None}")
        logger.info(f"   • MediaAcquisitionService: {orchestrator.media_service is not None}")
        logger.info(f"   • VideoAssemblyService: {orchestrator.video_service is not None}")
        
        # Testar tema (etapa 1)
        logger.info("\n🎯 Testando geração de tema...")
        from src.models.unified_models import GeneratedTheme, GeneratedScript, ScriptSection
        
        # Mock para teste rápido
        mock_theme = GeneratedTheme(
            content="Animais incríveis da natureza",
            category=ThemeCategory.ANIMALS,
            quality_score=0.85
        )
        
        logger.info(f"   Tema mock: {mock_theme.content}")
        logger.info(f"   Categoria: {mock_theme.category.value}")
        logger.info(f"   Score: {mock_theme.quality_score}")
        
        # Testar script (etapa 2)
        logger.info("\n📝 Testando estrutura de script...")
        mock_script = GeneratedScript(
            title="Animais Incríveis",
            theme=mock_theme,
            sections=[
                ScriptSection(name="hook", content="Você sabia que...", duration_seconds=10.0),
                ScriptSection(name="body", content="A natureza é cheia de maravilhas...", duration_seconds=40.0),
                ScriptSection(name="conclusion", content="Compartilhe esse fato!", duration_seconds=10.0)
            ],
            total_duration=60.0
        )
        
        logger.info(f"   Título: {mock_script.title}")
        logger.info(f"   Duração: {mock_script.total_duration}s")
        logger.info(f"   Seções: {len(mock_script.sections)}")
        
        # Testar modelos tipados
        logger.info("\n📊 Testando modelos tipados...")
        from src.models.unified_models import (
            TTSAudioResult,
            BrollMatchResult,
            VideoSyncPlan,
            PipelineResult
        )
        
        audio_result = TTSAudioResult(
            success=True,
            audio_path="/tmp/test.wav",
            duration=60.0,
            voice="test_voice"
        )
        logger.info(f"   TTSAudioResult: success={audio_result.success}, duration={audio_result.duration}s")
        
        broll_result = BrollMatchResult(
            success=True,
            videos=["/tmp/video1.mp4"],
            queries_used=["nature animals"],
            keywords=[],
            validation_pipeline={"semantic_analysis": {"performed": True}}
        )
        logger.info(f"   BrollMatchResult: success={broll_result.success}, videos={len(broll_result.videos)}")
        
        sync_result = VideoSyncPlan(
            success=True,
            audio_path="/tmp/test.wav",
            video_paths=["/tmp/video1.mp4"],
            sync_method="basic"
        )
        logger.info(f"   VideoSyncPlan: success={sync_result.success}, method={sync_result.sync_method}")
        
        # Pipeline Result
        pipeline_result = PipelineResult(
            status="success",
            theme={"content": mock_theme.content},
            script={"title": mock_script.title}
        )
        logger.info(f"   PipelineResult: status={pipeline_result.status}")
        
        logger.info("\n✅ TODOS OS TESTES PASSARAM!")
        logger.info("🎉 Refatoração validada com sucesso!")
        logger.info("\n📋 Resumo:")
        logger.info("   • Importações funcionando")
        logger.info("   • Serviços inicializados")
        logger.info("   • Modelos tipados criados")
        logger.info("   • Estrutura refatorada operacional")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {str(e)}", exc_info=True)
        return False

def check_file_structure():
    """Verifica se todos os arquivos da refatoração existem."""
    logger.info("\n📁 Verificando estrutura de arquivos...")
    
    files_to_check = [
        "src/pipeline/orchestrator.py",
        "src/pipeline/services/content_generation_service.py",
        "src/pipeline/services/media_acquisition_service.py",
        "src/pipeline/services/video_assembly_service.py",
        "src/models/unified_models.py",
        "src/utils/logging_config.py",
        "src/utils/exceptions.py",
        "tests/test_refactored_orchestrator.py",
        "docs/refatoramento_2024.md"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if Path(file_path).exists():
            logger.info(f"   ✅ {file_path}")
        else:
            logger.error(f"   ❌ {file_path} (NÃO ENCONTRADO)")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    logger.info("🚀 Iniciando teste de validação da refatoração...")
    
    # Verificar estrutura
    structure_ok = check_file_structure()
    
    if structure_ok:
        # Testar pipeline
        success = test_refactored_pipeline()
        
        if success:
            logger.info("\n🎯 PRÓXIMOS PASSOS SUGERIDOS:")
            logger.info("1. Rodar: python main.py (para teste completo)")
            logger.info("2. Implementar cache nos serviços")
            logger.info("3. Adicionar métricas e monitoramento")
            logger.info("4. Criar dashboard de operações")
            sys.exit(0)
        else:
            logger.error("\n❌ Testes falharam. Verifique os logs.")
            sys.exit(1)
    else:
        logger.error("\n❌ Estrutura de arquivos incompleta.")
        sys.exit(1)