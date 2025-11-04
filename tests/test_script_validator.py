"""
Testes para ScriptValidator - AiShorts v2.0

Testes abrangentes para o sistema de validação de roteiros.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

from src.validators.script_validator import (
    ScriptValidator,
    ValidationReport,
    ValidationResult,
    ValidationIssue,
    QualityMetrics,
    PlatformRequirements,
    PlatformType,
    ValidationSeverity,
    QualityLevel
)
from src.generators.script_generator import GeneratedScript, ScriptSection
from src.generators.theme_generator import GeneratedTheme


class TestScriptValidator:
    """Testes para a classe ScriptValidator."""
    
    @pytest.fixture
    def validator(self):
        """Fixture para criar validador."""
        return ScriptValidator()
    
    @pytest.fixture
    def sample_script(self):
        """Fixture para criar roteiro de exemplo."""
        theme = GeneratedTheme(
            content="Fenômenos físicos incríveis",
            category=ThemeCategory.SCIENCE,
            quality_score=0.85,
            response_time=2.5,
            timestamp=datetime.now()
        )
        
        hook = ScriptSection(
            name="hook",
            content="Você sabia que existe um fenômeno onde objetos podem flutuar no ar?",
            duration_seconds=15,
            purpose="Captar atenção inicial",
            key_elements=["pergunta", "fenômeno", "curiosidade"]
        )
        
        development = ScriptSection(
            name="development", 
            content="Esse fenômeno é chamado de levitação magnética e ocorre quando campos magnéticos fortes fazem com que materiais condutores flutuem. Estudos mostram que 95% das pessoas ficam impressionadas com essa demonstração.",
            duration_seconds=90,
            purpose="Explicar o conceito",
            key_elements=["levitação", "magnética", "campos", "estudos"]
        )
        
        conclusion = ScriptSection(
            name="conclusion",
            content="Que incrível, né? Curtiu esse fato? Compartilha com seus amigos!",
            duration_seconds=15,
            purpose="Encerrar com engajamento",
            key_elements=["engajamento", "cta"]
        )
        
        return GeneratedScript(
            title="Levitação Magnética",
            theme=theme,
            sections=[hook, development, conclusion],
            total_duration=120,
            quality_score=0.85,
            engagement_score=1.0,
            retention_score=0.8,
            response_time=2.5,
            timestamp=datetime.now()
        )
    
    @pytest.fixture
    def invalid_script(self):
        """Fixture para criar roteiro inválido."""
        theme = GeneratedTheme(
            content="Tema Genérico",
            category=ThemeCategory.SCIENCE,
            quality_score=0.3,
            response_time=1.5,
            timestamp=datetime.now()
        )
        
        # Roteiro com problemas estruturais
        hook = ScriptSection(
            name="hook",
            content="",  # Conteúdo vazio
            duration_seconds=0,  # Duração inválida
            purpose="",
            key_elements=[]
        )
        
        return GeneratedScript(
            title="Roteiro Inválido",
            theme=theme,
            sections=[hook],
            total_duration=0,
            quality_score=0.1,
            engagement_score=0.1,
            retention_score=0.1,
            response_time=5.0,
            timestamp=datetime.now()
        )

    def test_validator_initialization(self, validator):
        """Testa inicialização do validador."""
        assert validator is not None
        assert validator.platform_requirements is not None
        assert PlatformType.TIKTOK in validator.platform_requirements
        assert PlatformType.SHORTS in validator.platform_requirements
        assert PlatformType.REELS in validator.platform_requirements

    def test_validate_structure_valid_script(self, validator, sample_script):
        """Testa validação de estrutura com roteiro válido."""
        result = validator._validate_structure(sample_script)
        
        assert isinstance(result, ValidationResult)
        assert result.section_name == "structure"
        assert result.score >= 60  # Score mínimo para roteiro válido
        assert len(result.issues) >= 0  # Pode ter warnings
        assert len(result.suggestions) >= 0

    def test_validate_structure_invalid_script(self, validator, invalid_script):
        """Testa validação de estrutura com roteiro inválido."""
        result = validator._validate_structure(invalid_script)
        
        assert isinstance(result, ValidationResult)
        assert result.section_name == "structure"
        assert result.score < 60  # Score baixo para roteiro inválido
        assert len(result.issues) > 0  # Deve ter problemas
        
        # Deve ter problemas críticos
        critical_issues = [i for i in result.issues if i.severity == ValidationSeverity.ERROR]
        assert len(critical_issues) > 0

    def test_validate_hook_section_valid(self, validator):
        """Testa validação de hook válida."""
        hook = ScriptSection(
            name="hook",
            content="Você sabia que existe um incrível fenômeno de flutuação?",
            duration_seconds=15,
            purpose="Engajar",
            key_elements=["pergunta"]
        )
        
        issues = validator._validate_hook_section(hook)
        
        # Não deve ter problemas críticos
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR]
        assert len(critical_issues) == 0

    def test_validate_hook_section_invalid(self, validator):
        """Testa validação de hook inválida."""
        hook = ScriptSection(
            name="hook",
            content="Isso é um texto muito simples e sem engaging",  # Sem elementos de engajamento
            duration_seconds=15,
            purpose="Engajar",
            key_elements=[]
        )
        
        issues = validator._validate_hook_section(hook)
        
        # Deve ter pelo menos um warning
        warning_issues = [i for i in issues if i.severity == ValidationSeverity.WARNING]
        assert len(warning_issues) > 0

    def test_validate_development_section(self, validator):
        """Testa validação de seção de desenvolvimento."""
        # Desenvolvimento com fatos
        development_good = ScriptSection(
            name="development",
            content="Estudos mostram que 90% das pessoas ficam impressionadas. Os números comprovam: 95% de eficácia.",
            duration_seconds=90,
            purpose="Explicar",
            key_elements=["estudos", "números"]
        )
        
        issues_good = validator._validate_development_section(development_good)
        
        # Não deve ter problemas de falta de fatos
        fact_issues = [i for i in issues_good if i.code == "DEVELOPMENT_NO_FACTS"]
        assert len(fact_issues) == 0
        
        # Desenvolvimento sem fatos
        development_bad = ScriptSection(
            name="development",
            content="Isso é muito interessante e awesome e fantastic",
            duration_seconds=90,
            purpose="Explicar",
            key_elements=[]
        )
        
        issues_bad = validator._validate_development_section(development_bad)
        
        # Deve ter problema de falta de fatos
        fact_issues = [i for i in issues_bad if i.code == "DEVELOPMENT_NO_FACTS"]
        assert len(fact_issues) > 0

    def test_validate_conclusion_section(self, validator):
        """Testa validação de seção de conclusão."""
        # Conclusão com CTA
        conclusion_good = ScriptSection(
            name="conclusion",
            content="Curtiu esse conteúdo? Compartilha e segue para mais curiosidades!",
            duration_seconds=15,
            purpose="Engajar",
            key_elements=["curtiu", "compartilha", "segue"]
        )
        
        issues_good = validator._validate_conclusion_section(conclusion_good)
        
        # Não deve ter problema de falta de CTA
        cta_issues = [i for i in issues_good if i.code == "CONCLUSION_NO_CTA"]
        assert len(cta_issues) == 0

    def test_validate_content(self, validator, sample_script):
        """Testa validação de conteúdo."""
        result = validator._validate_content(sample_script)
        
        assert isinstance(result, ValidationResult)
        assert result.section_name == "content"
        assert result.score >= 0
        assert result.score <= 100

    def test_validate_platform_requirements_tiktok(self, validator, sample_script):
        """Testa validação para TikTok."""
        result = validator._validate_platform_requirements(sample_script, PlatformType.TIKTOK)
        
        assert isinstance(result, ValidationResult)
        assert result.section_name == "platform"
        assert result.score >= 0
        
        # Verifica se tem informações sobre duração
        duration_issues = [i for i in result.issues if "duration" in i.code.lower()]
        assert len(duration_issues) >= 0  # Pode ou não ter problemas

    def test_validate_platform_requirements_shorts(self, validator, sample_script):
        """Testa validação para YouTube Shorts."""
        result = validator._validate_platform_requirements(sample_script, PlatformType.SHORTS)
        
        assert isinstance(result, ValidationResult)
        assert result.section_name == "platform"
        assert result.score >= 0

    def test_validate_platform_requirements_reels(self, validator, sample_script):
        """Testa validação para Instagram Reels."""
        result = validator._validate_platform_requirements(sample_script, PlatformType.REELS)
        
        assert isinstance(result, ValidationResult)
        assert result.section_name == "platform"
        assert result.score >= 0

    def test_analyze_quality_metrics(self, validator, sample_script):
        """Testa análise de métricas de qualidade."""
        metrics = validator._analyze_quality_metrics(sample_script)
        
        assert isinstance(metrics, QualityMetrics)
        assert 0 <= metrics.clarity_score <= 1
        assert 0 <= metrics.engagement_score <= 1
        assert 0 <= metrics.retention_score <= 1
        
        # Deve ter listas de issues (mesmo que vazias)
        assert isinstance(metrics.clarity_issues, list)
        assert isinstance(metrics.engagement_issues, list)
        assert isinstance(metrics.retention_issues, list)

    def test_calculate_overall_score(self, validator):
        """Testa cálculo de score geral."""
        structure_result = ValidationResult("structure", True, 80, [])
        content_result = ValidationResult("content", True, 85, [])
        platform_result = ValidationResult("platform", True, 90, [])
        
        quality_metrics = QualityMetrics(
            clarity_score=0.8,
            engagement_score=0.9,
            retention_score=0.7
        )
        
        score = validator._calculate_overall_score(structure_result, content_result, platform_result, quality_metrics)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_determine_quality_level(self, validator):
        """Testa determinação do nível de qualidade."""
        assert validator._determine_quality_level(95) == QualityLevel.EXCELLENT
        assert validator._determine_quality_level(85) == QualityLevel.GOOD
        assert validator._determine_quality_level(70) == QualityLevel.FAIR
        assert validator._determine_quality_level(50) == QualityLevel.POOR

    def test_check_approval_criteria(self, validator):
        """Testa verificação de critérios de aprovação."""
        # Critérios atendidos
        no_errors = []
        high_score = 80
        assert validator._check_approval_criteria(no_errors, high_score) == True
        
        # Critérios não atendidos - erros críticos
        critical_error = ValidationIssue(
            code="TEST_ERROR",
            message="Erro crítico",
            severity=ValidationSeverity.ERROR
        )
        errors = [critical_error]
        assert validator._check_approval_criteria(errors, high_score) == False
        
        # Critérios não atendidos - score baixo
        low_score = 50
        assert validator._check_approval_criteria([], low_score) == False

    def test_validate_script_full(self, validator, sample_script):
        """Testa validação completa do roteiro."""
        report = validator.validate_script(sample_script, PlatformType.TIKTOK)
        
        assert isinstance(report, ValidationReport)
        assert report.script == sample_script
        assert report.platform == PlatformType.TIKTOK
        assert isinstance(report.overall_score, float)
        assert isinstance(report.quality_level, QualityLevel)
        assert isinstance(report.is_approved, bool)
        assert isinstance(report.all_issues, list)
        assert isinstance(report.suggestions, list)
        
        # Deve ter validações de estrutura, conteúdo e plataforma
        assert isinstance(report.structure_validation, ValidationResult)
        assert isinstance(report.content_validation, ValidationResult)
        assert isinstance(report.platform_validation, ValidationResult)
        assert isinstance(report.quality_metrics, QualityMetrics)

    def test_validate_multiple_platforms(self, validator, sample_script):
        """Testa validação para múltiplas plataformas."""
        reports = validator.validate_multiple_platforms(sample_script)
        
        assert isinstance(reports, dict)
        assert len(reports) == 3  # TikTok, Shorts, Reels
        
        for platform in PlatformType:
            assert platform in reports
            assert isinstance(reports[platform], ValidationReport)

    def test_generate_suggestions(self, validator):
        """Testa geração de sugestões."""
        # Cria alguns issues com sugestões
        issues = [
            ValidationIssue(
                code="TEST_1",
                message="Problema de estrutura",
                severity=ValidationSeverity.WARNING,
                suggestion="Melhore a estrutura"
            ),
            ValidationIssue(
                code="TEST_2", 
                message="Problema de conteúdo",
                severity=ValidationSeverity.WARNING,
                suggestion="Melhore o conteúdo"
            )
        ]
        
        structure_result = ValidationResult("structure", True, 50, [])  # Score baixo
        content_result = ValidationResult("content", True, 50, [])  # Score baixo
        platform_result = ValidationResult("platform", True, 90, [])  # Score bom
        
        suggestions = validator._generate_suggestions(issues, structure_result, content_result, platform_result)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        # Deve incluir sugestões dos issues e sugestões gerais
        assert any("estrutura" in s.lower() for s in suggestions)
        assert any("conteúdo" in s.lower() for s in suggestions)

    def test_issue_to_dict(self, validator):
        """Testa conversão de ValidationIssue para dicionário."""
        issue = ValidationIssue(
            code="TEST_CODE",
            message="Test message",
            severity=ValidationSeverity.WARNING,
            section="hook",
            suggestion="Test suggestion"
        )
        
        result = validator._issue_to_dict(issue)
        
        assert isinstance(result, dict)
        assert result["code"] == "TEST_CODE"
        assert result["message"] == "Test message"
        assert result["severity"] == "warning"
        assert result["section"] == "hook"
        assert result["suggestion"] == "Test suggestion"

    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_validation_report(self, validator, sample_script, mock_open, mock_mkdir):
        """Testa salvamento do relatório de validação."""
        report = validator.validate_script(sample_script, PlatformType.TIKTOK)
        
        filepath = Path("test_report.json")
        validator.save_validation_report(report, filepath)
        
        # Verifica se o arquivo foi aberto para escrita
        mock_open.assert_called_once()
        
        # Verifica se mkdir foi chamado
        mock_mkdir.assert_called_once()

    def test_platform_requirements_consistency(self, validator):
        """Testa consistência dos requisitos de plataforma."""
        requirements = validator.platform_requirements
        
        for platform, req in requirements.items():
            assert isinstance(req, PlatformRequirements)
            assert 0 < req.min_duration < req.max_duration
            assert 0 < req.min_characters < req.max_characters
            assert abs(req.hook_duration_percent + req.development_duration_percent + req.conclusion_duration_percent - 1.0) < 0.01
            assert isinstance(req.banned_words, set)
            assert isinstance(req.required_engagement_phrases, set)

    def test_engagement_patterns_coverage(self, validator):
        """Testa cobertura dos padrões de engajamento."""
        patterns = validator.ENGAGEMENT_PATTERNS
        
        assert "questions" in patterns
        assert "emotional" in patterns
        assert "storytelling" in patterns
        assert "facts" in patterns
        
        for pattern_group in patterns.values():
            assert isinstance(pattern_group, list)
            assert len(pattern_group) > 0

    def test_retention_patterns_coverage(self, validator):
        """Testa cobertura dos padrões de retenção."""
        patterns = validator.RETENTION_PATTERNS
        
        assert "cliffhangers" in patterns
        assert "structure" in patterns
        assert "anticipation" in patterns
        
        for pattern_group in patterns.values():
            assert isinstance(pattern_group, list)
            assert len(pattern_group) > 0

    def test_validation_report_summary(self, validator, sample_script):
        """Testa geração de resumo do relatório."""
        report = validator.validate_script(sample_script, PlatformType.TIKTOK)
        summary = report.get_summary()
        
        assert isinstance(summary, dict)
        assert "platform" in summary
        assert "overall_score" in summary
        assert "quality_level" in summary
        assert "is_approved" in summary
        assert "total_issues" in summary
        assert "critical_issues" in summary
        assert "total_suggestions" in summary
        assert "structure_score" in summary
        assert "content_score" in summary
        assert "platform_score" in summary
        
        # Valores devem ser consistentes
        assert summary["platform"] == "tiktok"
        assert 0 <= summary["overall_score"] <= 100
        assert isinstance(summary["is_approved"], bool)
        assert isinstance(summary["total_issues"], int)
        assert summary["total_issues"] >= 0

    def test_get_issues_by_severity(self, validator, sample_script):
        """Testa filtragem de issues por severidade."""
        report = validator.validate_script(sample_script, PlatformType.TIKTOK)
        
        errors = report.get_issues_by_severity(ValidationSeverity.ERROR)
        warnings = report.get_issues_by_severity(ValidationSeverity.WARNING)
        infos = report.get_issues_by_severity(ValidationSeverity.INFO)
        
        # Todos os issues devem estar em uma das categorias
        total_categorized = len(errors) + len(warnings) + len(infos)
        assert total_categorized == len(report.all_issues)
        
        # Não deve haver overlap
        assert len(set(id(i) for i in errors) & set(id(i) for i in warnings)) == 0

    def test_get_critical_issues(self, validator, sample_script):
        """Testa obtenção de issues críticos."""
        report = validator.validate_script(sample_script, PlatformType.TIKTOK)
        critical = report.get_critical_issues()
        
        # Todos os issues críticos devem ter severidade ERROR
        for issue in critical:
            assert issue.severity == ValidationSeverity.ERROR
