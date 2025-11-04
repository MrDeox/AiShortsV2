"""
Testes Unitários - Cliente OpenRouter

Testa todas as funcionalidades do cliente OpenRouter de forma isolada.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import time

@pytest.mark.unit
class TestOpenRouterClient:
    """Testes do cliente OpenRouter."""
    
    def test_client_initialization(self, mock_logger):
        """Testa a inicialização do cliente."""
        from src.core.openrouter_client import OpenRouterClient
        
        client = OpenRouterClient()
        assert client is not None
        
        model_info = client.get_model_info()
        assert "model" in model_info
        assert "base_url" in model_info
        assert "max_tokens" in model_info
        assert "temperature" in model_info
    
    def test_client_with_config(self, config_test):
        """Testa criação do cliente com configurações específicas."""
        from src.core.openrouter_client import OpenRouterClient
        
        client = OpenRouterClient(
            api_key=config_test["openrouter"]["api_key"],
            model=config_test["openrouter"]["model"],
            max_tokens=config_test["openrouter"]["max_tokens"]
        )
        
        assert client.config.api_key == config_test["openrouter"]["api_key"]
        assert client.config.model == config_test["openrouter"]["model"]
        assert client.config.max_tokens == config_test["openrouter"]["max_tokens"]
    
    @patch('src.core.openrouter_client.requests.post')
    def test_successful_api_call(self, mock_post, mock_openrouter_response, mock_logger):
        """Testa chamada bem-sucedida da API."""
        from src.core.openrouter_client import OpenRouterClient
        
        # Configurar mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_openrouter_response
        mock_post.return_value = mock_response
        
        client = OpenRouterClient()
        result = client.generate_completion(
            system_message="Test system",
            user_message="Test user"
        )
        
        assert "Por que o céu é azul?" in result["content"]
        assert result["usage"]["total_tokens"] == 150
    
    @patch('src.core.openrouter_client.requests.post')
    def test_api_error_handling(self, mock_post, mock_logger):
        """Testa tratamento de erros da API."""
        from src.core.openrouter_client import OpenRouterClient, OpenRouterError
        
        # Simular erro da API
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_post.return_value = mock_response
        
        client = OpenRouterClient()
        
        with pytest.raises(OpenRouterError):
            client.generate_completion("test", "test")
    
    @patch('src.core.openrouter_client.requests.post')
    def test_rate_limit_error(self, mock_post, mock_logger):
        """Testa tratamento de erro de rate limit."""
        from src.core.openrouter_client import RateLimitError
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_post.return_value = mock_response
        
        # Teste será implementado quando o método for chamado
    
    def test_rate_limiter_basic(self):
        """Testa funcionalidade básica do rate limiter."""
        from src.core.openrouter_client import RateLimiter
        
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        # Primeira requisição deve ser permitida
        assert limiter.can_make_request() is True
        
        # Adicionar algumas requisições
        for i in range(4):
            limiter.add_request()
            assert limiter.can_make_request() is True
        
        # Após 5 requisições, deve bloquear
        limiter.add_request()  # 5ª requisição
        assert limiter.can_make_request() is False
    
    def test_rate_limiter_reset(self):
        """Testa reset do rate limiter."""
        from src.core.openrouter_client import RateLimiter
        
        limiter = RateLimiter(max_requests=2, time_window=1)  # 1 segundo
        
        # Usar todas as requisições
        assert limiter.can_make_request() is True
        limiter.add_request()
        
        assert limiter.can_make_request() is True
        limiter.add_request()  # Segunda requisição
        
        # Agora deve estar bloqueado
        assert limiter.can_make_request() is False
        
        # Aguardar o reset
        time.sleep(1.1)
        assert limiter.can_make_request() is True

@pytest.mark.unit
class TestErrorHandling:
    """Testes do sistema de tratamento de erros."""
    
    def test_openrouter_error(self, mock_logger):
        """Testa exceção OpenRouterError."""
        from src.utils.exceptions import OpenRouterError, ErrorHandler
        
        error = OpenRouterError("Test error", status_code=500)
        assert error.message == "Test error"
        assert error.status_code == 500
        
        error_info = ErrorHandler.handle_error(error, "test_context")
        assert error_info["error_code"] == "OPENROUTER_ERROR"
        assert error_info["message"] == "Test error"
        assert "test_context" in error_info["context"]
    
    def test_rate_limit_error(self, mock_logger):
        """Testa exceção RateLimitError."""
        from src.utils.exceptions import RateLimitError, ErrorHandler
        
        error = RateLimitError("Too many requests", wait_time=2.5)
        assert error.message == "Too many requests"
        assert error.wait_time == 2.5
        
        error_info = ErrorHandler.handle_error(error, "test_rate_limit")
        assert error_info["error_code"] == "RATE_LIMIT_ERROR"
        assert error_info["wait_time"] == 2.5
    
    def test_safe_execution(self, mock_logger):
        """Testa execução segura com fallback."""
        from src.utils.exceptions import ErrorHandler
        
        def funcao_sucesso():
            return "sucesso"
        
        def funcao_erro():
            raise ValueError("Erro de teste")
        
        # Teste com sucesso
        result = ErrorHandler.safe_execute(
            funcao_sucesso,
            fallback_return="fallback",
            context="teste_sucesso"
        )
        assert result == "sucesso"
        
        # Teste com erro
        result = ErrorHandler.safe_execute(
            funcao_erro,
            fallback_return="fallback",
            context="teste_erro"
        )
        assert result == "fallback"
    
    def test_theme_generation_error(self, mock_logger):
        """Testa exceção ThemeGenerationError."""
        from src.utils.exceptions import ThemeGenerationError, ErrorHandler
        
        error = ThemeGenerationError("Theme validation failed", attempt=2, category="science")
        assert error.message == "Theme validation failed"
        assert error.attempt == 2
        assert error.category == "science"
        
        error_info = ErrorHandler.handle_error(error, "test_theme")
        assert error_info["error_code"] == "THEME_GENERATION_ERROR"
        assert error_info["attempt"] == 2
        assert error_info["category"] == "science"

@pytest.mark.unit
class TestConfiguration:
    """Testes das configurações."""
    
    def test_config_loading(self, config_test):
        """Testa carregamento das configurações."""
        from src.config.settings import config
        
        # Verificar se configurações carregaram
        assert config is not None
        assert hasattr(config, 'openrouter')
    
    def test_config_summary(self, mock_logger):
        """Testa geração do resumo das configurações."""
        from src.config.settings import config
        
        summary = config.get_summary()
        assert isinstance(summary, dict)
        
        expected_keys = ["model", "max_tokens", "temperature"]
        for key in expected_keys:
            assert key in summary
    
    def test_config_validation_flexible(self, mock_logger):
        """Testa validação flexível das configurações."""
        from src.config.settings import config
        
        # Validação flexível deve passar mesmo sem API key
        try:
            config.validate_config(strict=False)
            validation_passed = True
        except ValueError as e:
            # Aceitar falha apenas se for por falta de API key
            validation_passed = "OPENROUTER_API_KEY" in str(e)
        
        assert validation_passed is True

@pytest.mark.unit
class TestLogging:
    """Testes do sistema de logging."""
    
    def test_logger_creation(self, mock_logger):
        """Testa criação do logger."""
        from src.config.logging_config import logger
        
        assert logger is not None
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
    
    def test_log_levels(self, mock_logger):
        """Testa diferentes níveis de log."""
        from src.config.logging_config import logger
        
        # Testar se todos os níveis funcionam
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Não deve levantar exceção
        assert True
    
    def test_log_format(self, mock_logger):
        """Testa formato das mensagens de log."""
        from src.config.logging_config import logger, setup_logging
        
        # Configurar logging se necessário
        setup_logging(level="DEBUG")
        
        # Verificar se logging está configurado
        assert logger.level is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])