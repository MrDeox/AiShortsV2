"""
Testes unitários para ContentGenerationService
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from src.generators.prompt_engineering import ThemeCategory
from src.models.unified_models import GeneratedTheme, GeneratedScript
from src.pipeline.services.content_generation_service import ContentGenerationService
from src.validators.script_validator import ValidationReport, QualityLevel
from src.validators.script_validator import Issue, IssueSeverity
from src.utils.exceptions import ScriptGenerationError, TTSError


class TestContentGenerationService:
    """Testes para ContentGenerationService."""
    
    @pytest.fixture
    def mock_theme_generator(self):
        """Mock do ThemeGenerator."""
        generator = Mock()
        theme = GeneratedTheme(
            content="Test theme content",
            category=ThemeCategory.TECHNOLOGY,
            quality_score=0.8,
            response_time=1.5
        )
        generator.generate_single_theme.return_value = theme
        return generator
    
    @pytest.fixture
    def mock_script_generator(self):
        """Mock do ScriptGenerator."""
        generator = Mock()
        
        # Criar seções mock
        mock_hook = Mock()
        mock_hook.content = "Test hook content"
        
        mock_development = Mock()
        mock_development.content = "Test body content"
        mock_development.duration = 30.0
        
        mock_conclusion = Mock()
        mock_conclusion.content = "Test conclusion content"
        mock_conclusion.duration = 15.0
        
        script = GeneratedScript(
            hook=mock_hook,
            development=mock_development,
            conclusion=mock_conclusion,
            quality_score=0.8,
            total_duration=45.0
        )
        script.metadata = {}
        
        generator.generate_single_script.return_value = script
        return generator
    
    @pytest.fixture
    def mock_translator(self):
        """Mock do Translator."""
        translator = Mock()
        translator.translate.return_value = (
            "Conteúdo traduzido",
            {"success": True, "translations": 1}
        )
        return translator
    
    @pytest.fixture
    def mock_tts_client(self):
        """Mock do TTS Client."""
        tts = AsyncMock()
        tts.synthesize_speech.return_value = (
            "/path/to/audio.mp3",
            {"duration": 45.0, "success": True}
        )
        return tts
    
    @pytest.fixture
    def mock_script_validator(self):
        """Mock do ScriptValidator."""
        validator = Mock()
        
        # Relatório de validação aprovado
        report = ValidationReport(
            overall_score=85.0,
            quality_level=QualityLevel.EXCELLENT,
            issues=[],
            is_approved=True,
            suggestions=[]
        )
        validator.validate_script.return_value = report
        return validator
    
    @pytest.fixture
    def content_service(
        self,
        mock_theme_generator,
        mock_script_generator,
        mock_translator,
        mock_tts_client,
        mock_script_validator
    ):
        """Instância do ContentGenerationService com mocks."""
        return ContentGenerationService(
            theme_generator=mock_theme_generator,
            script_generator=mock_script_generator,
            translator=mock_translator,
            tts_client=mock_tts_client,
            script_validator=mock_script_validator
        )
    
    @pytest.mark.asyncio
    async def test_generate_theme_traditional_method(self, content_service, mock_theme_generator):
        """Testa geração de tema pelo método tradicional."""
        # Execute
        theme, result = await content_service.generate_theme(ThemeCategory.SCIENCE)
        
        # Verify
        assert isinstance(theme, GeneratedTheme)
        assert theme.content == "Test theme content"
        assert theme.category == ThemeCategory.TECHNOLOGY
        
        assert result["content_en"] == "Test theme content"
        assert result["category"] == "technology"
        assert result["quality"] == 0.8
        
        # Verifica se o generator foi chamado
        mock_theme_generator.generate_single_theme.assert_called_once_with(ThemeCategory.SCIENCE)
    
    @pytest.mark.asyncio
    async def test_generate_theme_with_llm_success(self, content_service, mock_theme_generator):
        """Testa geração de tema com LLM Theme Strategy."""
        # Setup LLM helpers mock
        mock_llm = AsyncMock()
        mock_theme_strategy = Mock()
        mock_theme_strategy.topic = "AI breakthrough in medicine"
        mock_theme_strategy.angle = "Shows how AI is revolutionizing drug discovery"
        mock_theme_strategy.safety_flags = []
        mock_theme_strategy.uniqueness_score = 0.92
        mock_theme_strategy.virality_potential = 0.88
        
        mock_llm.generate_theme_strategy.return_value = mock_theme_strategy
        content_service.llm_helpers = mock_llm
        
        # Execute
        theme, result = await content_service.generate_theme(ThemeCategory.TECHNOLOGY)
        
        # Verify
        assert isinstance(theme, GeneratedTheme)
        assert theme.content == "AI breakthrough in medicine"
        assert theme.metadata["generated_by"] == "llm_theme_strategy"
        assert theme.metadata["angle"] == "Shows how AI is revolutionizing drug discovery"
        assert theme.metadata["uniqueness_score"] == 0.92
        assert theme.metadata["virality_potential"] == 0.88
        
        # Verifica se adicionou aos temas recentes
        assert theme.content in content_service._recent_themes
    
    @pytest.mark.asyncio
    async def test_generate_theme_with_llm_fallback(self, content_service, mock_theme_generator):
        """Testa fallback para método tradicional quando LLM falha."""
        # Setup LLM helpers mock que lança erro
        mock_llm = AsyncMock()
        mock_llm.generate_theme_strategy.side_effect = Exception("LLM API Error")
        content_service.llm_helpers = mock_llm
        
        # Execute
        theme, result = await content_service.generate_theme(ThemeCategory.HISTORY)
        
        # Verify - deve usar método tradicional
        assert isinstance(theme, GeneratedTheme)
        assert theme.content == "Test theme content"
        
        # Verifica se o generator tradicional foi chamado (fallback)
        mock_theme_generator.generate_single_theme.assert_called_once_with(ThemeCategory.HISTORY)
    
    @pytest.mark.asyncio
    async def test_generate_script_approved_first_attempt(self, content_service, mock_script_generator):
        """Testa geração de script aprovado na primeira tentativa."""
        # Setup theme
        theme = GeneratedTheme(
            content="Test theme",
            category=ThemeCategory.SCIENCE,
            quality_score=0.8
        )
        
        # Execute
        script, result = await content_service.generate_script(theme, target_platform="tiktok")
        
        # Verify
        assert isinstance(script, GeneratedScript)
        assert script.quality_score == 0.8
        assert script.total_duration == 45.0
        
        # Verifica resultado
        assert result["validation"]["is_approved"] is True
        assert result["validation"]["overall_score"] == 85.0
        
        # Verifica se o generator foi chamado
        mock_script_generator.generate_single_script.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_script_with_llm_refiner(self, content_service, mock_script_generator, mock_script_validator):
        """Testa refino de script com LLM quando falha validação."""
        # Setup theme
        theme = GeneratedTheme(
            content="Space exploration",
            category=ThemeCategory.SPACE,
            quality_score=0.8
        )
        
        # Setup validação para falhar na primeira tentativa
        critical_issue = Issue(
            code="TOO_SHORT",
            message="Script is too short",
            severity=IssueSeverity.CRITICAL
        )
        failing_report = ValidationReport(
            overall_score=45.0,
            quality_level=QualityLevel.POOR,
            issues=[critical_issue],
            is_approved=False,
            suggestions=["Add more content"]
        )
        
        # Configurar mock para falhar depois passar
        mock_script_validator.validate_script.side_effect = [
            failing_report,  # Primeira chamada falha
            ValidationReport(  # Segunda chamada passa
                overall_score=85.0,
                quality_level=QualityLevel.EXCELLENT,
                issues=[],
                is_approved=True,
                suggestions=[]
            )
        ]
        
        # Setup LLM refiner mock
        mock_llm = AsyncMock()
        mock_refined_script = Mock()
        mock_refined_script.hook = "Refined hook content"
        mock_refined_script.body = "Refined body content"
        mock_refined_script.conclusion = "Refined conclusion content"
        mock_refined_script.estimated_duration = 60
        mock_refined_script.refinement_notes = ["Added more detail", "Improved pacing"]
        
        mock_llm.refine_script.return_value = mock_refined_script
        content_service.llm_helpers = mock_llm
        
        # Execute
        script, result = await content_service.generate_script(
            theme, 
            target_platform="tiktok",
            max_attempts=2
        )
        
        # Verify
        assert isinstance(script, GeneratedScript)
        assert script.metadata.get("llm_refined") is True
        assert script.metadata.get("refinement_count") == 1
        assert "Added more detail" in script.metadata.get("refinement_notes", [])
        
        # Verifica se o LLM refiner foi chamado
        mock_llm.refine_script.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_script_max_attempts_reached(self, content_service, mock_script_generator, mock_script_validator):
        """Testa quando máximo de tentativas é alcançado."""
        # Setup theme
        theme = GeneratedTheme(
            content="Complex topic",
            category=ThemeCategory.PSYCHOLOGY,
            quality_score=0.8
        )
        
        # Setup validação para sempre falhar
        mock_script_validator.validate_script.return_value = ValidationReport(
            overall_score=30.0,
            quality_level=QualityLevel.POOR,
            issues=[Issue("CRITICAL_ERROR", "Always fails", IssueSeverity.CRITICAL)],
            is_approved=False,
            suggestions=[]
        )
        
        # Execute & Verify
        with pytest.raises(ScriptGenerationError, match="Failed after 4 attempts"):
            await content_service.generate_script(
                theme, 
                target_platform="tiktok",
                max_attempts=4
            )
    
    def test_translate_text(self, content_service, mock_translator):
        """Testa tradução de texto."""
        # Execute
        translated, result = content_service.translate_text("Hello world")
        
        # Verify
        assert translated == "Conteúdo traduzido"
        assert result["success"] is True
        mock_translator.translate.assert_called_once_with("Hello world")
    
    def test_translate_text_error(self, content_service, mock_translator):
        """Testa erro na tradução."""
        # Setup
        mock_translator.translate.side_effect = Exception("Translation API Error")
        
        # Execute
        translated, result = content_service.translate_text("Hello world")
        
        # Verify - fallback para texto original
        assert translated == "Hello world"
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_generate_audio_success(self, content_service, mock_tts_client):
        """Testa geração de áudio com sucesso."""
        # Setup
        text = "Text for TTS"
        
        # Execute
        audio_path, result = await content_service.generate_audio(text)
        
        # Verify
        assert audio_path == "/path/to/audio.mp3"
        assert result["success"] is True
        assert result["duration"] == 45.0
        
        mock_tts_client.synthesize_speech.assert_called_once_with(
            text=text,
            voice=None,
            rate=1.0,
            pitch=0,
            volume=1.0,
            output_path=None
        )
    
    @pytest.mark.asyncio
    async def test_generate_audio_error(self, content_service, mock_tts_client):
        """Testa erro na geração de áudio."""
        # Setup
        mock_tts_client.synthesize_speech.side_effect = Exception("TTS Error")
        
        # Execute & Verify
        with pytest.raises(TTSError, match="TTS Error"):
            await content_service.generate_audio("Test text")
    
    def test_generate_refined_requirements(self, content_service):
        """Testa geração de requisitos refinados."""
        # Setup validation report
        issues = [
            Issue("TOO_SHORT", "Content too short", IssueSeverity.CRITICAL),
            Issue("NO_HOOK", "Missing hook", IssueSeverity.MAJOR)
        ]
        report = ValidationReport(
            overall_score=40.0,
            quality_level=QualityLevel.POOR,
            issues=issues,
            is_approved=False,
            suggestions=["Add hook", "Extend content"]
        )
        
        # Execute
        requirements = content_service._generate_refined_requirements(report, attempt=2)
        
        # Verify
        assert isinstance(requirements, str)
        assert "hook" in requirements.lower()
        assert "longer" in requirements.lower()
        assert "60" in requirements  # target duration
    
    def test_generate_refined_requirements_no_issues(self, content_service):
        """Testa geração de requisitos quando não há issues."""
        # Setup
        report = ValidationReport(
            overall_score=80.0,
            quality_level=QualityLevel.GOOD,
            issues=[],
            is_approved=True,
            suggestions=[]
        )
        
        # Execute
        requirements = content_service._generate_refined_requirements(report, attempt=1)
        
        # Verify - deve ser None quando não há issues
        assert requirements is None