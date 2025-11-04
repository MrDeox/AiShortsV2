"""
Testes Unitários - Gerador de Tema

Testa todas as funcionalidades do gerador de temas de forma isolada.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

@pytest.mark.unit
class TestPromptEngineering:
    """Testes do sistema de prompt engineering."""
    
    def test_get_all_categories(self, mock_logger):
        """Testa obtenção de todas as categorias."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        categories = prompt_engineering.get_all_categories()
        
        assert len(categories) == 10  # Todas as 10 categorias
        assert ThemeCategory.SCIENCE in categories
        assert ThemeCategory.HISTORY in categories
        assert ThemeCategory.NATURE in categories
        assert ThemeCategory.TECHNOLOGY in categories
        assert ThemeCategory.CULTURE in categories
        assert ThemeCategory.SPACE in categories
        assert ThemeCategory.ANIMALS in categories
        assert ThemeCategory.PSYCHOLOGY in categories
        assert ThemeCategory.GEOGRAPHY in categories
        assert ThemeCategory.FOOD in categories
    
    def test_create_generation_prompt_science(self, mock_logger):
        """Testa criação de prompt para categoria Science."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        prompt = prompt_engineering.create_generation_prompt(ThemeCategory.SCIENCE)
        
        assert "system_message" in prompt
        assert "user_prompt" in prompt
        assert isinstance(prompt["system_message"], str)
        assert isinstance(prompt["user_prompt"], str)
        assert len(prompt["system_message"]) > 0
        assert len(prompt["user_prompt"]) > 0
        
        # Verificar se menciona ciência
        assert "ciência" in prompt["system_message"].lower() or "science" in prompt["system_message"].lower()
    
    def test_create_generation_prompt_space(self, mock_logger):
        """Testa criação de prompt para categoria Space."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        prompt = prompt_engineering.create_generation_prompt(ThemeCategory.SPACE)
        
        assert "system_message" in prompt
        assert "user_prompt" in prompt
        assert "espaço" in prompt["system_message"].lower() or "space" in prompt["system_message"].lower()
    
    def test_create_generation_prompt_animals(self, mock_logger):
        """Testa criação de prompt para categoria Animals."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        prompt = prompt_engineering.create_generation_prompt(ThemeCategory.ANIMALS)
        
        assert "system_message" in prompt
        assert "user_prompt" in prompt
        assert "animal" in prompt["system_message"].lower() or "bicho" in prompt["system_message"].lower()
    
    def test_validate_prompt_format_good(self, mock_logger):
        """Testa validação de formato com tema bom."""
        from src.generators.prompt_engineering import prompt_engineering
        
        good_themes = [
            "Por que o céu é azul?",
            "Como funciona o sistema solar?",
            "Qual a origem dos dinossauros?",
            "Por que as plantas precisam de luz solar?",
            "Como os pássaros navigam?"
        ]
        
        for theme in good_themes:
            result = prompt_engineering.validate_prompt_format(theme)
            assert result is True, f"Tema '{theme}' deveria ser válido"
    
    def test_validate_prompt_format_bad(self, mock_logger):
        """Testa validação de formato com tema ruim."""
        from src.generators.prompt_engineering import prompt_engineering
        
        bad_themes = [
            "",  # Vazio
            "   ",  # Apenas espaços
            "O céu é azul",  # Declaração sem pergunta
            "Azul",  # Muito curto
            "O sistema solar é um conjunto de planetas que orbitam o sol"  # Resposta direta
        ]
        
        for theme in bad_themes:
            result = prompt_engineering.validate_prompt_format(theme)
            assert result is False, f"Tema '{theme}' deveria ser inválido"
    
    def test_get_quality_metrics(self, test_utils, mock_logger):
        """Testa cálculo de métricas de qualidade."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        good_theme = "Por que o céu é azul?"
        metrics = prompt_engineering.get_quality_metrics(good_theme, ThemeCategory.SCIENCE)
        
        # Verificar estrutura das métricas
        test_utils.assert_quality_metrics(metrics)
        
        # Verificar se o tema bom tem qualidade razoável
        assert metrics["overall_quality"] > 0.5
        assert metrics["curiosity_factor"] > 0.5
        assert metrics["educational_value"] > 0.5
    
    def test_quality_metrics_bad_theme(self, test_utils, mock_logger):
        """Testa métricas para tema de baixa qualidade."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        bad_theme = "Azul"
        metrics = prompt_engineering.get_quality_metrics(bad_theme, ThemeCategory.SCIENCE)
        
        test_utils.assert_quality_metrics(metrics)
        
        # Tema ruim deve ter baixa qualidade
        assert metrics["overall_quality"] < 0.7
        assert metrics["curiosity_factor"] < 0.7
        assert metrics["educational_value"] < 0.7
    
    def test_all_categories_have_prompts(self, mock_logger):
        """Testa se todas as categorias têm prompts configurados."""
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        categories_with_prompts = []
        categories_without_prompts = []
        
        for category in ThemeCategory:
            try:
                prompt = prompt_engineering.create_generation_prompt(category)
                if prompt["system_message"] and prompt["user_prompt"]:
                    categories_with_prompts.append(category)
                else:
                    categories_without_prompts.append(category)
            except Exception:
                categories_without_prompts.append(category)
        
        # Todas as 10 categorias devem ter prompts
        assert len(categories_with_prompts) == 10, f"Categorias sem prompt: {[c.value for c in categories_without_prompts]}"
        assert len(categories_without_prompts) == 0, "Algumas categorias não têm prompts configurados"

@pytest.mark.unit
class TestThemeDataStructures:
    """Testes das estruturas de dados de temas."""
    
    def test_generated_theme_creation(self, test_utils, mock_logger):
        """Testa criação de GeneratedTheme."""
        from src.generators.theme_generator import GeneratedTheme
        from src.generators.prompt_engineering import ThemeCategory
        
        theme = GeneratedTheme(
            content="Por que o céu é azul?",
            category=ThemeCategory.SCIENCE,
            quality_score=0.8,
            response_time=1.5,
            timestamp=datetime.now()
        )
        
        assert theme.content == "Por que o céu é azul?"
        assert theme.category == ThemeCategory.SCIENCE
        assert theme.quality_score == 0.8
        assert theme.response_time == 1.5
        assert theme.timestamp is not None
    
    def test_generated_theme_to_dict(self, test_utils, mock_logger):
        """Testa conversão GeneratedTheme para dict."""
        from src.generators.theme_generator import GeneratedTheme
        from src.generators.prompt_engineering import ThemeCategory
        
        theme = GeneratedTheme(
            content="Test theme",
            category=ThemeCategory.NATURE,
            quality_score=0.9,
            response_time=2.0,
            timestamp=datetime(2025, 11, 3, 23, 23, 28)
        )
        
        theme_dict = theme.to_dict()
        
        assert isinstance(theme_dict, dict)
        assert theme_dict["content"] == "Test theme"
        assert theme_dict["category"] == "nature"
        assert theme_dict["quality_score"] == 0.9
        assert theme_dict["response_time"] == 2.0
        assert "timestamp" in theme_dict
    
    def test_generated_theme_from_dict(self, test_utils, mock_logger):
        """Testa criação de GeneratedTheme a partir de dict."""
        from src.generators.theme_generator import GeneratedTheme
        from src.generators.prompt_engineering import ThemeCategory
        
        theme_dict = {
            "content": "Test theme from dict",
            "category": "technology",
            "quality_score": 0.75,
            "response_time": 1.8,
            "timestamp": "2025-11-03T23:23:28"
        }
        
        theme = GeneratedTheme.from_dict(theme_dict)
        
        assert theme.content == "Test theme from dict"
        assert theme.category == ThemeCategory.TECHNOLOGY
        assert theme.quality_score == 0.75
        assert theme.response_time == 1.8
    
    def test_theme_generation_result(self, test_utils, mock_logger):
        """Testa criação de ThemeGenerationResult."""
        from src.generators.theme_generator import GeneratedTheme, ThemeGenerationResult, ThemeCategory
        
        themes = [
            GeneratedTheme(
                content="Theme 1",
                category=ThemeCategory.SCIENCE,
                quality_score=0.8,
                response_time=1.0,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Theme 2", 
                category=ThemeCategory.HISTORY,
                quality_score=0.9,
                response_time=1.2,
                timestamp=datetime.now()
            )
        ]
        
        best_theme = themes[1]  # O de maior score
        
        result = ThemeGenerationResult(
            themes=themes,
            best_theme=best_theme,
            total_time=5.0,
            generation_stats={"categories_tested": 2, "total_attempts": 4}
        )
        
        assert len(result.themes) == 2
        assert result.best_theme == best_theme
        assert result.total_time == 5.0
        assert result.generation_stats["categories_tested"] == 2
        assert result.generation_stats["total_attempts"] == 4
    
    def test_theme_generation_result_to_dict(self, test_utils, mock_logger):
        """Testa conversão ThemeGenerationResult para dict."""
        from src.generators.theme_generator import GeneratedTheme, ThemeGenerationResult, ThemeCategory
        
        theme = GeneratedTheme(
            content="Test result theme",
            category=ThemeCategory.CULTURE,
            quality_score=0.85,
            response_time=1.5,
            timestamp=datetime.now()
        )
        
        result = ThemeGenerationResult(
            themes=[theme],
            best_theme=theme,
            total_time=3.0,
            generation_stats={"test": True}
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert len(result_dict["themes"]) == 1
        assert result_dict["total_time"] == 3.0
        assert result_dict["generation_stats"]["test"] is True

@pytest.mark.unit
class TestValidationLogic:
    """Testes da lógica de validação."""
    
    def test_clean_response(self, mock_logger):
        """Testa limpeza de resposta."""
        from src.generators.theme_generator import theme_generator
        
        messy_responses = [
            "   Por que o céu é azul?   \n\n",
            "\n\n\nComo funciona o sistema solar?\n\n\n",
            "  \t Por que as plantas são verdes? \t  ",
            "Tema: Por que o oceano é salgado?\n\nMais texto desnecessário"
        ]
        
        for messy in messy_responses:
            clean = theme_generator._clean_response(messy)
            assert clean.strip() == clean  # Não deve ter espaços nas bordas
            assert "\n\n" not in clean  # Não deve ter múltiplas quebras de linha
            assert len(clean) > 0  # Não deve estar vazio
    
    def test_validate_theme_response_valid(self, mock_logger):
        """Testa validação de resposta válida."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        valid_responses = [
            "Por que o céu é azul?",
            "Como funcionava o calendário egípcio?",
            "Por que os flamingos são rosa?",
            "Qual a origem do Carnaval brasileiro?"
        ]
        
        for response in valid_responses:
            # Não deve levantar exceção
            theme_generator._validate_theme_response(response, ThemeCategory.SCIENCE)
    
    def test_validate_theme_response_invalid(self, mock_logger):
        """Testa validação de resposta inválida."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        from src.utils.exceptions import ThemeGenerationError
        
        invalid_responses = [
            "",  # Vazio
            "   ",  # Apenas espaços
            "Resposta direta sem pergunta",  # Não é pergunta
            "Azul",  # Muito curto
            "O céu é azul porque散散散散散散散散散散散散散"  # Com caracteres estranhos
        ]
        
        for response in invalid_responses:
            with pytest.raises(ThemeGenerationError):
                theme_generator._validate_theme_response(response, ThemeCategory.SCIENCE)
    
    def test_choose_random_category(self, mock_logger):
        """Testa escolha de categoria aleatória."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        # Chamar múltiplas vezes para verificar se sempre retorna categoria válida
        for _ in range(10):
            category = theme_generator._choose_random_category()
            assert isinstance(category, ThemeCategory)
            assert category in list(ThemeCategory)
    
    def test_is_valid_theme_quality(self, mock_logger):
        """Testa verificação de qualidade do tema."""
        from src.generators.theme_generator import theme_generator
        
        # Tema com qualidade alta deve ser válido
        high_quality = "Por que o céu é azul? Uma questão fascinante sobre óptica."
        assert theme_generator._is_valid_theme_quality(high_quality, 0.8) is True
        
        # Tema com qualidade baixa deve ser inválido
        low_quality = "Azul"
        assert theme_generator._is_valid_theme_quality(low_quality, 0.3) is False

@pytest.mark.unit
class TestAnalysisFunctionality:
    """Testes da funcionalidade de análise."""
    
    def test_analyze_themes(self, test_utils, mock_logger):
        """Testa análise de temas."""
        from src.generators.theme_generator import theme_generator, GeneratedTheme
        from src.generators.prompt_engineering import ThemeCategory
        
        # Criar temas de teste
        themes = [
            GeneratedTheme(
                content="Por que o céu é azul?",
                category=ThemeCategory.SCIENCE,
                quality_score=0.8,
                response_time=1.0,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Como funcionava o calendário egípcio?",
                category=ThemeCategory.HISTORY,
                quality_score=0.9,
                response_time=1.2,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Por que os flamingos são rosa?",
                category=ThemeCategory.NATURE,
                quality_score=0.7,
                response_time=0.8,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Como funciona o GPS?",
                category=ThemeCategory.TECHNOLOGY,
                quality_score=0.85,
                response_time=1.1,
                timestamp=datetime.now()
            )
        ]
        
        analysis = theme_generator.analyze_themes(themes)
        
        # Verificar estrutura da análise
        assert "total_themes" in analysis
        assert "quality_stats" in analysis
        assert "categories" in analysis
        assert "best_themes" in analysis
        
        # Verificar dados da análise
        assert analysis["total_themes"] == 4
        assert analysis["quality_stats"]["avg_quality"] > 0
        assert analysis["quality_stats"]["min_quality"] >= 0
        assert analysis["quality_stats"]["max_quality"] <= 1
        
        # Verificar categorias
        categories_found = list(analysis["categories"].keys())
        assert len(categories_found) == 4
        assert "science" in categories_found
        assert "history" in categories_found
        assert "nature" in categories_found
        assert "technology" in categories_found
        
        # Verificar melhores temas
        assert len(analysis["best_themes"]) == 4
        # O primeiro deve ser o de maior qualidade
        assert analysis["best_themes"][0]["quality_score"] >= analysis["best_themes"][1]["quality_score"]
    
    def test_analyze_themes_empty(self, mock_logger):
        """Testa análise com lista vazia."""
        from src.generators.theme_generator import theme_generator
        
        analysis = theme_generator.analyze_themes([])
        
        assert analysis["total_themes"] == 0
        assert analysis["quality_stats"]["avg_quality"] == 0
        assert analysis["categories"] == {}
        assert analysis["best_themes"] == []
    
    def test_analyze_themes_single(self, test_utils, mock_logger):
        """Testa análise com apenas um tema."""
        from src.generators.theme_generator import theme_generator, GeneratedTheme
        from src.generators.prompt_engineering import ThemeCategory
        
        theme = GeneratedTheme(
            content="Tema único",
            category=ThemeCategory.CULTURE,
            quality_score=0.9,
            response_time=1.5,
            timestamp=datetime.now()
        )
        
        analysis = theme_generator.analyze_themes([theme])
        
        assert analysis["total_themes"] == 1
        assert analysis["quality_stats"]["avg_quality"] == 0.9
        assert list(analysis["categories"].keys()) == ["culture"]
        assert len(analysis["best_themes"]) == 1
        assert analysis["best_themes"][0]["content"] == "Tema único"

@pytest.mark.unit
class TestThemeGeneratorInitialization:
    """Testes da inicialização do gerador de tema."""
    
    def test_generator_initialization(self, mock_logger):
        """Testa inicialização do gerador."""
        from src.generators.theme_generator import theme_generator
        
        assert theme_generator is not None
        assert hasattr(theme_generator, 'config')
        assert hasattr(theme_generator, 'openrouter')
        assert hasattr(theme_generator, 'prompt_engineering')
    
    def test_generator_config(self, mock_logger):
        """Testa configurações do gerador."""
        from src.generators.theme_generator import theme_generator
        
        config = theme_generator.config
        assert hasattr(config, 'categories')
        assert hasattr(config, 'theme_generator')
        
        theme_config = config.theme_generator
        assert hasattr(theme_config, 'min_quality_score')
        assert hasattr(theme_config, 'max_attempts')
    
    def test_generator_quality_settings(self, mock_logger):
        """Testa configurações de qualidade."""
        from src.generators.theme_generator import theme_generator
        
        assert theme_generator.min_quality_score > 0
        assert theme_generator.min_quality_score <= 1
        assert theme_generator.max_attempts > 0
    
    def test_generator_dependencies(self, mock_logger):
        """Testa dependências do gerador."""
        from src.generators.theme_generator import theme_generator
        
        # Verificar se OpenRouter está configurado
        assert theme_generator.openrouter is not None
        assert hasattr(theme_generator.openrouter, 'generate_completion')
        
        # Verificar se prompt engineering está configurado
        assert theme_generator.prompt_engineering is not None
        assert hasattr(theme_generator.prompt_engineering, 'create_generation_prompt')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])