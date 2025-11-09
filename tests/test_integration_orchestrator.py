"""
Testes de Integração para AiShortsOrchestrator
Testa o fluxo completo com todos os componentes avançados integrados
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import json

# Import dos componentes a serem testados
from src.pipeline.orchestrator import AiShortsOrchestrator
from src.generators.theme_generator import ThemeGenerator, GeneratedTheme
from src.generators.script_generator import ScriptGenerator
from src.models import GeneratedScript, ScriptSection, ThemeCategory
from src.validators.script_validator import ScriptValidator, PlatformType
from src.video.sync.audio_video_synchronizer import AudioVideoSynchronizer
from src.video.sync.timing_optimizer import TimingOptimizer
from src.video.matching.content_matcher import ContentMatcher
from src.video.matching.clip_relevance_scorer import CLIPRelevanceScorer
from src.video.validation.clip_pre_validator import ClipVideoPreValidator, VideoCandidate


class TestAiShortsOrchestratorIntegration:
    """Testes de integração completa para o AiShortsOrchestrator"""
    
    @pytest.fixture
    def temp_dir(self):
        """Diretório temporário para os testes"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock de todas as dependências do orquestrador"""
        
        # Mock ThemeGenerator
        mock_theme_generator = Mock()
        mock_theme = GeneratedTheme(
            content="Animais incríveis da Amazônia",
            category=ThemeCategory.ANIMALS,
            quality_score=0.85,
            response_time=1.2
        )
        mock_theme_generator.generate_single_theme.return_value = mock_theme
        
        # Mock ScriptGenerator
        mock_script_generator = Mock()
        mock_script = GeneratedScript(
            title="Animais Incríveis da Amazônia",
            theme=mock_theme,
            sections=[
                ScriptSection(
                    name="hook",
                    content="Você sabia que a Amazônia abriga 10% de todas as espécies do planeta?",
                    duration_seconds=5.0,
                    purpose="capturar atenção"
                ),
                ScriptSection(
                    name="development",
                    content="A floresta amazônica abriga mais de 40.000 espécies de plantas e milhares de animais únicos.",
                    duration_seconds=45.0,
                    purpose="informar"
                ),
                ScriptSection(
                    name="conclusion",
                    content="Proteger a Amazônia é essencial para preservar a biodiversidade do nosso planeta.",
                    duration_seconds=10.0,
                    purpose="chamada à ação"
                )
            ],
            total_duration=60.0,
            quality_score=0.88
        )
        mock_script_generator.generate_single_script.return_value = mock_script
        
        # Mock Translator
        mock_translator = Mock()
        mock_translator.translate.return_value = Mock(
            success=True,
            translated_text="Você sabia que a Amazônia abriga 10% de todas as espécies do planeta? A floresta amazônica abriga mais de 40.000 espécies de plantas e milhares de animais únicos. Proteger a Amazônia é essencial para preservar a biodiversidade do nosso planeta.",
            response_time=0.8
        )
        
        # Mock TTS Client
        mock_tts_client = Mock()
        mock_tts_result = {
            "success": True,
            "audio_path": "test_audio.wav",
            "duration": 58.5,
            "voice": "default"
        }
        mock_tts_client.text_to_speech.return_value = mock_tts_result
        
        # Mock YouTube Extractor
        mock_youtube_extractor = Mock()
        mock_candidates = [
            {
                "id": "video1",
                "title": "The Amazing Amazon Rainforest",
                "description": "Incredible wildlife in the Amazon",
                "url": "http://youtube.com/watch?v=video1",
                "duration": 120,
                "view_count": 1000000,
                "thumbnail": "http://youtube.com/thumb1.jpg"
            },
            {
                "id": "video2", 
                "title": "Amazon Animals Documentary",
                "description": "Rare species of the Amazon",
                "url": "http://youtube.com/watch?v=video2",
                "duration": 90,
                "view_count": 500000,
                "thumbnail": "http://youtube.com/thumb2.jpg"
            }
        ]
        mock_youtube_extractor.search_videos.return_value = mock_candidates
        
        def mock_download_video(url, output_dir):
            # Criar arquivo de vídeo falso
            output_path = Path(output_dir) / "test_video.mp4"
            output_path.write_text("fake video content")
            return str(output_path)
        
        mock_youtube_extractor.download_video.side_effect = mock_download_video
        
        # Mock SemanticAnalyzer
        mock_semantic_analyzer = Mock()
        mock_semantic_analyzer.generate_broll_keywords_via_llm.return_value = ["amazon rainforest", "wildlife animals"]
        mock_semantic_analyzer.extract_keywords.return_value = ["amazon", "rainforest", "animals", "wildlife"]
        mock_semantic_analyzer.categorize_content.return_value = ["nature", 0.95]
        
        # Mock AudioVideoSynchronizer
        mock_sync = Mock()
        mock_sync_result = {
            "success": True,
            "timeline": [{"timestamp": 0.0, "video": "test_video.mp4"}],
            "sync_points": [0.0, 15.0, 45.0],
            "sync_precision": 0.02,
            "total_duration": 58.5
        }
        mock_sync.sync_audio_with_video.return_value = mock_sync_result
        
        # Mock TimingOptimizer
        mock_timing_optimizer = Mock()
        mock_timing_result = {
            "success": True,
            "optimized_segments": [
                {"path": "test_video.mp4", "duration": 20.0, "transition_in": "fade"}
            ],
            "transition_effects": [{"name": "fade", "duration": 0.3}]
        }
        mock_timing_optimizer.optimize_transitions.return_value = mock_timing_result
        
        # Mock ContentMatcher
        mock_content_matcher = Mock()
        
        # Mock CLIPRelevanceScorer
        mock_clip_scorer = Mock()
        mock_clip_scorer.calculate_relevance_score.return_value = 0.85
        
        # Mock ClipPreValidator
        mock_clip_validator = Mock()
        
        # Mock VideoProcessor
        mock_video_processor = Mock()
        mock_video_processor.get_video_info.return_value = {"duration": 20.0}
        
        # Mock BrollQueryService
        mock_broll_service = Mock()
        mock_broll_service.generate_queries.return_value = ["amazon wildlife documentary"]
        
        # Mock CaptionService
        mock_caption_service = Mock()
        mock_caption_service.build_captions.return_value = [
            {"text": "Você sabia que a Amazônia...", "start_time": 0.0, "end_time": 3.0}
        ]
        
        # Mock ScriptValidator
        mock_script_validator = Mock()
        mock_validation_report = Mock()
        mock_validation_report.overall_score = 85.0
        mock_validation_report.quality_level.value = "good"
        mock_validation_report.is_approved = True
        mock_validation_report.get_critical_issues.return_value = []
        mock_validation_report.all_issues = []
        mock_validation_report.suggestions = ["Ótimo script!"]
        mock_script_validator.validate_script.return_value = mock_validation_report
        
        return {
            "theme_generator": mock_theme_generator,
            "script_generator": mock_script_generator,
            "translator": mock_translator,
            "tts_client": mock_tts_client,
            "youtube_extractor": mock_youtube_extractor,
            "semantic_analyzer": mock_semantic_analyzer,
            "audio_video_sync": mock_sync,
            "timing_optimizer": mock_timing_optimizer,
            "content_matcher": mock_content_matcher,
            "clip_relevance_scorer": mock_clip_scorer,
            "clip_pre_validator": mock_clip_validator,
            "video_processor": mock_video_processor,
            "broll_query_service": mock_broll_service,
            "caption_service": mock_caption_service,
            "script_validator": mock_script_validator
        }
    
    def test_orchestrator_initialization(self, mock_dependencies):
        """Testa inicialização do orquestrador com todos os componentes"""
        
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        # Verificar se todos os componentes foram injetados
        assert orchestrator.theme_generator is not None
        assert orchestrator.script_generator is not None
        assert orchestrator.script_validator is not None
        assert orchestrator.audio_video_synchronizer is not None
        assert orchestrator.timing_optimizer is not None
        assert orchestrator.content_matcher is not None
        assert orchestrator.clip_relevance_scorer is not None
        assert orchestrator.clip_pre_validator is not None
        
        print("✅ Orquestrator inicializado com todos os componentes avançados")
    
    @patch('src.pipeline.orchestrator.Path')
    def test_orchestrator_complete_flow(self, mock_path, mock_dependencies):
        """Testa o fluxo completo do orquestrator"""
        
        # Mock Path.exists()
        mock_path.return_value.exists.return_value = True
        
        # Criar orquestrator
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        # Executar pipeline completo
        results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)
        
        # Verificar sucesso
        assert results["status"] == "success"
        assert "theme" in results
        assert "script" in results
        assert "audio" in results
        assert "broll" in results
        assert "sync" in results
        assert "final" in results
        
        # Verificar se a validação foi aplicada
        assert "validation" in results["script"]
        assert results["script"]["validation"]["overall_score"] == 85.0
        assert results["script"]["validation"]["is_approved"] == True
        
        # Verificar se sincronização avançada foi usada
        assert results["sync"]["sync_method"] == "advanced"
        assert "sync_points" in results["sync"]
        assert "sync_precision" in results["sync"]
        
        # Verificar se validação de B-roll foi aplicada
        assert "validation_pipeline" in results["broll"]
        assert results["broll"]["validation_pipeline"]["pre_validation"]["performed"] == True
        
        print("✅ Fluxo completo executado com sucesso")
        print(f"   • Score validação: {results['script']['validation']['overall_score']}")
        print(f"   • Método sincronização: {results['sync']['sync_method']}")
        print(f"   • Pré-validação B-roll: {results['broll']['validation_pipeline']['pre_validation']['performed']}")
    
    def test_script_validation_integration(self, mock_dependencies):
        """Testa integração da validação de script com o pipeline"""
        
        # Configurar mock para rejeitar script na primeira tentativa
        def mock_validate_side_effect(script, platform):
            # Simular score baixo na primeira chamada
            if not hasattr(mock_validate_side_effect, 'call_count'):
                mock_validate_side_effect.call_count = 0
            mock_validate_side_effect.call_count += 1
            
            if mock_validate_side_effect.call_count == 1:
                # Primeira tentativa - score baixo
                mock_validation_report = Mock()
                mock_validation_report.overall_score = 45.0
                mock_validation_report.quality_level.value = "poor"
                mock_validation_report.is_approved = False
                mock_validation_report.get_critical_issues.return_value = [
                    Mock(code="SCRIPT_TOO_SHORT", message="Script muito curto")
                ]
                mock_validation_report.all_issues = mock_validation_report.get_critical_issues.return_value
                mock_validation_report.suggestions = ["Adicionar mais conteúdo"]
                return mock_validation_report
            else:
                # Segunda tentativa - score bom
                mock_validation_report = Mock()
                mock_validation_report.overall_score = 85.0
                mock_validation_report.quality_level.value = "good"
                mock_validation_report.is_approved = True
                mock_validation_report.get_critical_issues.return_value = []
                mock_validation_report.all_issues = []
                mock_validation_report.suggestions = []
                return mock_validation_report
        
        mock_dependencies["script_validator"].validate_script.side_effect = mock_validate_side_effect
        
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        with patch('src.pipeline.orchestrator.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)
        
        # Verificar que o script foi validado (chamado pelo menos 1 vez)
        assert mock_dependencies["script_validator"].validate_script.call_count >= 1
        
        # Verificar que o pipeline completou com sucesso
        assert results["status"] == "success"
        assert results["script"]["validation"]["overall_score"] > 70.0
        
        print("✅ Validação de script integrada funcionando")
        print(f"   • Validações realizadas: {mock_dependencies['script_validator'].validate_script.call_count}")
        print(f"   • Score final: {results['script']['validation']['overall_score']}")
    
    def test_advanced_sync_integration(self, mock_dependencies):
        """Testa integração da sincronização avançada"""
        
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        with patch('src.pipeline.orchestrator.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)
        
        # Verificar que os componentes foram chamados
        mock_dependencies["timing_optimizer"].optimize_transitions.assert_called_once()
        mock_dependencies["audio_video_sync"].sync_audio_with_video.assert_called_once()
        
        # Verificar resultados da sincronização
        assert results["sync"]["sync_method"] == "advanced"
        assert "timeline" in results["sync"]
        assert "sync_points" in results["sync"]
        assert "sync_precision" in results["sync"]
        assert "transition_effects" in results["sync"]
        
        print("✅ Sincronização avançada integrada funcionando")
        print(f"   • Método: {results['sync']['sync_method']}")
        print(f"   • Precisão: {results['sync']['sync_precision']}")
        print(f"   • Pontos de sincronia: {len(results['sync']['sync_points'])}")
    
    def test_semantic_matching_integration(self, mock_dependencies):
        """Testa integração do semantic matching"""
        
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        with patch('src.pipeline.orchestrator.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)
        
        # Verificar que o CLIP scorer foi chamado
        mock_dependencies["clip_relevance_scorer"].calculate_relevance_score.assert_called()
        
        # Verificar resultados do semantic matching
        assert results["broll"]["validation_pipeline"]["semantic_analysis"]["performed"] == True
        assert "top_relevance_score" in results["broll"]["validation_pipeline"]["semantic_analysis"]
        
        print("✅ Semantic matching integrado funcionando")
        print(f"   • Análise semântica realizada: {results['broll']['validation_pipeline']['semantic_analysis']['performed']}")
        print(f"   • Score de relevância: {results['broll']['validation_pipeline']['semantic_analysis']['top_relevance_score']}")
    
    def test_pre_validation_integration(self, mock_dependencies):
        """Testa integração da pré-validação de vídeos"""
        
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        with patch('src.pipeline.orchestrator.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)
        
        # Verificar que a pré-validação foi realizada
        assert results["broll"]["validation_pipeline"]["pre_validation"]["performed"] == True
        assert "candidates_validated" in results["broll"]["validation_pipeline"]["pre_validation"]
        assert "top_pre_validation_score" in results["broll"]["validation_pipeline"]["pre_validation"]
        
        print("✅ Pré-validação de vídeos integrada funcionando")
        print(f"   • Pré-validação realizada: {results['broll']['validation_pipeline']['pre_validation']['performed']}")
        print(f"   • Candidatos validados: {results['broll']['validation_pipeline']['pre_validation']['candidates_validated']}")
    
    def test_models_consistency(self, mock_dependencies):
        """Testa consistência dos modelos unificados"""
        
        # Importar modelos unificados
        from src.models import validate_model_consistency, get_migration_info
        
        # Validar modelos
        validation = validate_model_consistency()
        assert validation["status"] == "valid"
        
        # Verificar migração
        migration_info = get_migration_info()
        assert migration_info["compatibility_level"] == "full"
        assert not migration_info["breaking_changes"]
        
        print("✅ Consistência de modelos verificada")
        print(f"   • Status: {validation['status']}")
        print(f"   • Modelos: {', '.join(validation['models'])}")
        print(f"   • Compatibilidade: {migration_info['compatibility_level']}")
    
    def test_error_handling_and_recovery(self, mock_dependencies):
        """Testa tratamento de erros e recuperação"""
        
        # Configurar mock para falhar em validação CLIP
        mock_dependencies["clip_relevance_scorer"].calculate_relevance_score.side_effect = Exception("CLIP error")
        
        orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        with patch('src.pipeline.orchestrator.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)
        
        # Pipeline deve continuar mesmo com falha no CLIP
        assert results["status"] == "success"
        assert results["broll"]["validation_pipeline"]["pre_validation"]["method"] == "fallback"
        
        print("✅ Tratamento de erros funcionando")
        print(f"   • Status final: {results['status']}")
        print(f"   • Método fallback: {results['broll']['validation_pipeline']['pre_validation']['method']}")
    
    def test_memory_optimization_integration(self, mock_dependencies):
        """Testa integração de otimizações de memória"""
        
        # Mock MemoryMonitor
        mock_memory_monitor = Mock()
        mock_memory_monitor.get_current_stats.return_value = Mock(
            process_gb=1.2, system_percent=45.0
        )
        mock_memory_monitor.check_memory.return_value = True
        mock_memory_monitor.suggest_cleanup.return_value = False
        
        # Mock ModelManager
        mock_model_manager = Mock()
        
        with patch('src.pipeline.orchestrator.get_memory_monitor', return_value=mock_memory_monitor), \
             patch('src.pipeline.orchestrator.get_model_manager', return_value=mock_model_manager):
            
            orchestrator = AiShortsOrchestrator(**mock_dependencies)
            
            with patch('src.pipeline.orchestrator.Path') as mock_path:
                mock_path.return_value.exists.return_value = True
                results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)
        
        # Verificar que as otimizações foram ativadas
        assert orchestrator.memory_monitor is not None
        assert orchestrator.model_manager is not None
        
        print("✅ Otimizações de memória integradas")
        print(f"   • Memory monitor disponível: {orchestrator.memory_monitor is not None}")
        print(f"   • Model manager disponível: {orchestrator.model_manager is not None}")


def run_integration_tests():
    """Executa todos os testes de integração"""
    print("🧪 Executando Testes de Integração do AiShortsOrchestrator")
    print("=" * 60)
    
    # Criar instância dos testes
    test_instance = TestAiShortsOrchestratorIntegration()
    
    # Mock de dependências
    mock_deps = test_instance.mock_dependencies()
    
    tests = [
        ("Inicialização", lambda: test_instance.test_orchestrator_initialization(mock_deps)),
        ("Fluxo Completo", lambda: test_instance.test_orchestrator_complete_flow(mock_deps)),
        ("Validação de Script", lambda: test_instance.test_script_validation_integration(mock_deps)),
        ("Sincronização Avançada", lambda: test_instance.test_advanced_sync_integration(mock_deps)),
        ("Semantic Matching", lambda: test_instance.test_semantic_matching_integration(mock_deps)),
        ("Pré-validação de Vídeos", lambda: test_instance.test_pre_validation_integration(mock_deps)),
        ("Consistência de Modelos", lambda: test_instance.test_models_consistency(mock_deps)),
        ("Tratamento de Erros", lambda: test_instance.test_error_handling_and_recovery(mock_deps)),
        ("Otimizações de Memória", lambda: test_instance.test_memory_optimization_integration(mock_deps))
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Testando: {test_name}")
            test_func()
            print(f"✅ {test_name}: PASS")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAIL - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resumo dos Testes: {passed} passaram, {failed} falharam")
    
    if failed == 0:
        print("🎉 Todos os testes de integração passaram com sucesso!")
        print("✅ AiShortsOrchestrator está pronto para produção")
    else:
        print("⚠️ Alguns testes falharam. Verifique a implementação.")
    
    return failed == 0


if __name__ == "__main__":
    run_integration_tests()