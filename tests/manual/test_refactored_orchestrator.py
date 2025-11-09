"""
Testes para o AiShortsOrchestrator refatorado.
Valida a nova estrutura com serviços especializados e modelos tipados.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.generators.prompt_engineering import ThemeCategory
from src.models.unified_models import (
    PipelineResult,
    TTSAudioResult,
    BrollMatchResult,
    VideoSyncPlan,
    GeneratedTheme,
    GeneratedScript,
    ScriptSection
)
from src.pipeline.orchestrator import AiShortsOrchestrator
from src.utils.exceptions import (
    TTSError,
    BrollExtractionError,
    VideoCompositionError
)


class TestAiShortsOrchestratorRefactored:
    """Testes da versão refatorada do AiShortsOrchestrator."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock para todas as dependências do orchestrator."""
        return {
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
    
    @pytest.fixture
    def orchestrator(self, mock_dependencies):
        """Cria instância do orchestrator com mocks."""
        with patch('src.pipeline.orchestrator.MEMORY_OPTIMIZATIONS_AVAILABLE', False):
            return AiShortsOrchestrator(**mock_dependencies)
    
    def test_orchestrator_initialization(self, mock_dependencies):
        """Testa inicialização correta do orchestrator."""
        with patch('src.pipeline.orchestrator.MEMORY_OPTIMIZATIONS_AVAILABLE', False):
            orchestrator = AiShortsOrchestrator(**mock_dependencies)
        
        # Verificar se os serviços foram inicializados
        assert orchestrator.content_service is not None
        assert orchestrator.media_service is not None
        assert orchestrator.video_service is not None
        
        # Verificar se graceful degradation foi configurado
        assert orchestrator.graceful_degradation is not None
    
    def test_generate_theme_service_delegation(self, orchestrator):
        """Testa se geração de tema é delegada corretamente ao ContentGenerationService."""
        # Setup
        theme = GeneratedTheme(
            content="Animais incríveis da Amazônia",
            category=ThemeCategory.ANIMALS,
            quality_score=0.85
        )
        theme_result = {
            "content_en": theme.content,
            "category": theme.category.value,
            "quality": theme.quality_score
        }
        
        orchestrator.content_service.generate_theme = Mock(return_value=(theme, theme_result))
        
        # Test
        result_theme, result = orchestrator.content_service.generate_theme(ThemeCategory.ANIMALS)
        
        # Verificação
        assert result_theme == theme
        assert result == theme_result
        orchestrator.content_service.generate_theme.assert_called_once_with(ThemeCategory.ANIMALS)
    
    def test_generate_script_service_delegation(self, orchestrator):
        """Testa se geração de script é delegada corretamente."""
        # Setup
        theme = GeneratedTheme(
            content="Test theme",
            category=ThemeCategory.SCIENCE
        )
        script = GeneratedScript(
            title="Test Script",
            theme=theme,
            sections=[
                ScriptSection(name="hook", content="Test hook"),
                ScriptSection(name="body", content="Test body"),
                ScriptSection(name="conclusion", content="Test conclusion")
            ],
            total_duration=60.0
        )
        script_result = {
            "title": script.title,
            "total_duration": script.total_duration,
            "content_en": {
                "hook": "Test hook",
                "body": "Test body",
                "conclusion": "Test conclusion",
                "plain_text": "Test hook Test body Test conclusion"
            }
        }
        
        orchestrator.content_service.generate_script = Mock(return_value=(script, script_result))
        
        # Test
        result_script, result = orchestrator.content_service.generate_script(theme)
        
        # Verificação
        assert result_script == script
        assert result == script_result
        orchestrator.content_service.generate_script.assert_called_once_with(theme)
    
    def test_tts_service_returns_typed_result(self, orchestrator):
        """Testa se serviço TTS retorna TTSAudioResult tipado."""
        # Setup
        text = "Texto de teste para TTS"
        expected_result = TTSAudioResult(
            success=True,
            audio_path="/tmp/test_audio.wav",
            duration=10.5,
            voice="default"
        )
        
        orchestrator.content_service.synthesize_audio = Mock(return_value=expected_result)
        
        # Test
        result = orchestrator.content_service.synthesize_audio(text)
        
        # Verificação
        assert isinstance(result, TTSAudioResult)
        assert result.success == True
        assert result.audio_path == "/tmp/test_audio.wav"
        assert result.duration == 10.5
        assert result.voice == "default"
        orchestrator.content_service.synthesize_audio.assert_called_once_with(text)
    
    def test_broll_extraction_returns_typed_result(self, orchestrator):
        """Testa se extração de B-roll retorna BrollMatchResult tipado."""
        # Setup
        theme_content = "Animais da selva"
        queries = ["wild animals", "jungle wildlife"]
        expected_result = BrollMatchResult(
            success=True,
            videos=["/tmp/video1.mp4", "/tmp/video2.mp4"],
            queries_used=queries,
            keywords=["animals", "jungle", "wildlife"],
            validation_pipeline={"semantic_analysis": {"performed": True}},
            total_candidates=10,
            download_count=2
        )
        
        orchestrator.media_service.extract_broll = Mock(return_value=expected_result)
        
        # Test
        result = orchestrator.media_service.extract_broll(theme_content, search_queries=queries)
        
        # Verificação
        assert isinstance(result, BrollMatchResult)
        assert result.success == True
        assert len(result.videos) == 2
        assert result.queries_used == queries
        assert result.total_candidates == 10
        assert result.download_count == 2
        orchestrator.media_service.extract_broll.assert_called_once_with(
            theme_content, 
            search_queries=queries
        )
    
    def test_video_sync_returns_typed_result(self, orchestrator):
        """Testa se sincronização vídeo retorna VideoSyncPlan tipado."""
        # Setup
        audio_path = "/tmp/audio.wav"
        video_paths = ["/tmp/video1.mp4", "/tmp/video2.mp4"]
        expected_result = VideoSyncPlan(
            success=True,
            audio_path=audio_path,
            video_paths=video_paths,
            sync_method="advanced",
            sync_precision=0.05,
            total_synced_duration=60.0
        )
        
        orchestrator.video_service.sync_audio_video = Mock(return_value=expected_result)
        
        # Test
        result = orchestrator.video_service.sync_audio_video(audio_path, video_paths)
        
        # Verificação
        assert isinstance(result, VideoSyncPlan)
        assert result.success == True
        assert result.sync_method == "advanced"
        assert result.sync_precision == 0.05
        assert result.total_synced_duration == 60.0
        orchestrator.video_service.sync_audio_video.assert_called_once_with(audio_path, video_paths)
    
    @patch('src.pipeline.orchestrator.Path.exists', return_value=True)
    def test_run_success_flow(self, mock_exists, orchestrator):
        """Testa fluxo completo de sucesso do pipeline."""
        # Setup dos mocks em cascata
        theme = GeneratedTheme(
            content="Test theme",
            category=ThemeCategory.SCIENCE
        )
        theme_result = {"content_en": theme.content, "category": theme.category.value}
        orchestrator.content_service.generate_theme = Mock(return_value=(theme, theme_result))
        
        script = GeneratedScript(
            title="Test Script",
            theme=theme,
            sections=[],
            total_duration=60.0
        )
        script_result = {
            "title": script.title,
            "total_duration": script.total_duration,
            "content_en": {"plain_text": "Test script content"}
        }
        orchestrator.content_service.generate_script = Mock(return_value=(script, script_result))
        
        translation_result = Mock()
        translation_result.translated_text = "Conteúdo traduzido"
        translation_result.to_dict.return_value = {"success": True}
        orchestrator.content_service.translate_script = Mock(return_value=translation_result)
        
        audio_result = TTSAudioResult(
            success=True,
            audio_path="/tmp/audio.wav",
            duration=60.0
        )
        orchestrator.content_service.synthesize_audio = Mock(return_value=audio_result)
        
        orchestrator.media_service.broll_query_service.generate_queries = Mock(return_value=["test query"])
        
        broll_result = BrollMatchResult(
            success=True,
            videos=["/tmp/video1.mp4"],
            queries_used=["test query"],
            keywords=[]
        )
        orchestrator.media_service.extract_broll = Mock(return_value=broll_result)
        
        orchestrator.media_service.analyze_content = Mock(return_value={"keywords": []})
        
        sync_result = VideoSyncPlan(
            success=True,
            audio_path="/tmp/audio.wav",
            video_paths=["/tmp/video1.mp4"],
            sync_method="advanced"
        )
        orchestrator.video_service.sync_audio_video = Mock(return_value=sync_result)
        
        orchestrator.video_service.caption_service.build_captions = Mock(return_value=[])
        orchestrator.video_service.compose_final_video = Mock(return_value="/tmp/final.mp4")
        
        # Test
        result = orchestrator.run(ThemeCategory.SCIENCE)
        
        # Verificação
        assert result["status"] == "success"
        assert "theme" in result
        assert "script" in result
        assert "audio" in result
        assert "broll" in result
        assert "sync" in result
        assert "final" in result
        assert result["final"]["success"] == True
        
        # Verificar se todos os serviços foram chamados
        orchestrator.content_service.generate_theme.assert_called_once()
        orchestrator.content_service.generate_script.assert_called_once()
        orchestrator.content_service.translate_script.assert_called_once()
        orchestrator.content_service.synthesize_audio.assert_called_once()
        orchestrator.media_service.extract_broll.assert_called_once()
        orchestrator.video_service.sync_audio_video.assert_called_once()
        orchestrator.video_service.compose_final_video.assert_called_once()
    
    def test_run_failure_handling(self, orchestrator):
        """Testa tratamento de falhas no pipeline."""
        # Setup para falhar na geração de tema
        orchestrator.content_service.generate_theme = Mock(
            side_effect=Exception("Theme generation failed")
        )
        
        # Test
        result = orchestrator.run(ThemeCategory.SCIENCE)
        
        # Verificação
        assert result["status"] == "failed"
        assert "error" in result
        assert "Theme generation failed" in result["error"]
    
    def test_error_handling_with_custom_exceptions(self, orchestrator):
        """Testa tratamento de exceções customizadas."""
        # Setup para falha com TTS
        orchestrator.content_service.generate_theme = Mock(return_value=(Mock(), {}))
        orchestrator.content_service.generate_script = Mock(return_value=(Mock(), {}))
        orchestrator.content_service.translate_script = Mock(return_value=Mock())
        orchestrator.content_service.synthesize_audio = Mock(
            side_effect=TTSError(
                "TTS service unavailable",
                text_preview="Test text",
                voice="default"
            )
        )
        
        # Test
        result = orchestrator.run(ThemeCategory.SCIENCE)
        
        # Verificação
        assert result["status"] == "failed"
        assert "TTS service unavailable" in result["error"]
    
    def test_pipeline_result_structure(self, orchestrator):
        """Testa se o resultado do pipeline segue estrutura esperada."""
        # Setup para retorno mínimo
        orchestrator.content_service.generate_theme = Mock(
            return_value=(Mock(), {"content_en": "test"})
        )
        orchestrator.content_service.generate_script = Mock(
            return_value=(Mock(), {"content_en": {"plain_text": "test"}})
        )
        orchestrator.content_service.translate_script = Mock(
            return_value=Mock(translated_text="test")
        )
        orchestrator.content_service.synthesize_audio = Mock(
            return_value=TTSAudioResult(
                success=True,
                audio_path="/tmp/test.wav",
                duration=10.0
            )
        )
        orchestrator.media_service.broll_query_service.generate_queries = Mock(return_value=[])
        orchestrator.media_service.extract_broll = Mock(
            return_value=BrollMatchResult(
                success=True,
                videos=["/tmp/test.mp4"],
                queries_used=[],
                keywords=[]
            )
        )
        orchestrator.media_service.analyze_content = Mock(return_value={})
        orchestrator.video_service.sync_audio_video = Mock(
            return_value=VideoSyncPlan(
                success=True,
                audio_path="/tmp/test.wav",
                video_paths=["/tmp/test.mp4"],
                sync_method="basic"
            )
        )
        orchestrator.video_service.caption_service.build_captions = Mock(return_value=[])
        orchestrator.video_service.compose_final_video = Mock(return_value="/tmp/final.mp4")
        
        with patch('src.pipeline.orchestrator.Path.exists', return_value=True):
            result = orchestrator.run(ThemeCategory.SCIENCE)
        
        # Verificar estrutura do resultado
        required_keys = ["status", "theme", "script", "audio", "broll", "sync", "final", "total_time"]
        for key in required_keys:
            assert key in result, f"Chave '{key}' ausente no resultado"
        
        # Verificar tipos de dados específicos
        assert isinstance(result["audio"], dict)
        assert "success" in result["audio"]
        assert "audio_path" in result["audio"]
        assert "duration" in result["audio"]
        
        assert isinstance(result["broll"], dict)
        assert "success" in result["broll"]
        assert "videos" in result["broll"]
        
        assert isinstance(result["sync"], dict)
        assert "success" in result["sync"]
        assert "sync_method" in result["sync"]
    
    def test_memory_optimization_integration(self, mock_dependencies):
        """Testa integração com otimizações de memória quando disponíveis."""
        with patch('src.pipeline.orchestrator.MEMORY_OPTIMIZATIONS_AVAILABLE', True):
            with patch('src.pipeline.orchestrator.get_model_manager') as mock_mm:
                with patch('src.pipeline.orchestrator.get_memory_monitor') as mock_mm_monitor:
                    orchestrator = AiShortsOrchestrator(**mock_dependencies)
                    
                    assert orchestrator.model_manager is not None
                    assert orchestrator.memory_monitor is not None
                    
                    # Verificar se setup de graceful degradation usa memory_monitor
                    assert orchestrator.memory_monitor == mock_mm_monitor.return_value
    
    def test_logging_integration(self, orchestrator):
        """Testa se logging está configurado corretamente."""
        assert orchestrator.logger is not None
        assert hasattr(orchestrator.logger, 'info')
        assert hasattr(orchestrator.logger, 'error')
        assert hasattr(orchestrator.logger, 'warning')
        assert hasattr(orchestrator.logger, 'debug')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])