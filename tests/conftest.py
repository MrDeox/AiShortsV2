"""
Configuração Global de Testes - AiShorts v2.0

Define fixtures, configurações e utilitários compartilhados
para todos os testes do sistema.
"""

import sys
from pathlib import Path
import pytest
import tempfile
import json
from unittest.mock import Mock, patch

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def project_root_path():
    """Retorna o diretório raiz do projeto."""
    return project_root

@pytest.fixture
def temp_dir():
    """Cria diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_openrouter_response():
    """Mock de resposta da API OpenRouter."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Por que o céu é azul? Esta é uma pergunta interessante sobre física óptica que explora como a luz solar interage com a atmosfera terrestre."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

@pytest.fixture
def sample_themes():
    """Temas de exemplo para testes."""
    return {
        "science": "Por que o céu é azul?",
        "history": "Como funcionava o calendário egípcio?",
        "nature": "Por que os flamingos são rosa?",
        "technology": "Como funciona o GPS?",
        "culture": "Qual a origem do Carnaval brasileiro?"
    }

@pytest.fixture
def mock_logger():
    """Mock do logger para testes."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger

@pytest.fixture
def config_test():
    """Configuração específica para testes."""
    test_config = {
        "openrouter": {
            "api_key": "test_key_123",
            "model": "nvidia/nemotron-nano-9b-v2:free",
            "max_tokens": 200,
            "temperature": 0.7,
            "max_requests_per_minute": 5
        },
        "theme_generator": {
            "min_quality_score": 0.6,
            "max_attempts": 3,
            "themes_per_category": 2
        },
        "logging": {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    return test_config

@pytest.fixture
def test_data_file(temp_dir):
    """Arquivo de dados temporário para testes."""
    test_data = {
        "themes": [
            {"content": "Test theme 1", "category": "science", "score": 0.8},
            {"content": "Test theme 2", "category": "history", "score": 0.9}
        ],
        "metadata": {"created": "2025-11-03", "version": "2.0"}
    }
    
    file_path = temp_dir / "test_data.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    return file_path

# Utilitários para testes
class TestUtils:
    """Utilitários compartilhados para testes."""
    
    @staticmethod
    def assert_theme_format(theme_content: str):
        """Verifica se um tema segue o formato esperado."""
        assert isinstance(theme_content, str)
        assert len(theme_content.strip()) > 0
        assert "?" in theme_content or "qual" in theme_content.lower()
    
    @staticmethod
    def assert_quality_metrics(metrics: dict):
        """Verifica se as métricas de qualidade estão corretas."""
        required_fields = ["overall_quality", "curiosity_factor", "educational_value"]
        for field in required_fields:
            assert field in metrics
            assert 0 <= metrics[field] <= 1
    
    @staticmethod
    def create_mock_theme(category: str, score: float = 0.8):
        """Cria um tema mock para testes."""
        return {
            "content": f"Test theme for {category}",
            "category": category,
            "quality_score": score,
            "response_time": 1.5,
            "timestamp": "2025-11-03T23:23:28"
        }

@pytest.fixture
def test_utils():
    """Disponibiliza utilitários de teste."""
    return TestUtils()

# Marcar testes por categoria
pytestmark = pytest.mark.asyncio

def pytest_configure(config):
    """Configuração global do pytest."""
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "benchmark: marca testes de performance"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )

def pytest_collection_modifyitems(config, items):
    """Modifica collection de testes para adicionar marcadores."""
    for item in items:
        # Adicionar marcador unit para testes que não são integração
        if "integration" not in item.nodeid and "benchmark" not in item.nodeid:
            item.add_marker(pytest.mark.unit)
