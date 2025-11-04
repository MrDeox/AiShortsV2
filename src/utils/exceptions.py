"""
Sistema de Tratamento de Exceções do AiShorts v2.0

Concentra todas as exceções customizadas e manejo de erros.
"""

from typing import Optional, Dict, Any
from loguru import logger

class AiShortsError(Exception):
    """Exceção base do AiShorts."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "AISHORTS_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a exceção para dicionário para logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }

class ConfigurationError(AiShortsError):
    """Erro de configuração do projeto."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "CONFIG_ERROR", {"config_key": config_key})

class OpenRouterError(AiShortsError):
    """Erro relacionado à integração OpenRouter."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message, "OPENROUTER_ERROR", {
            "status_code": status_code,
            "response_data": response_data
        })

class ThemeGenerationError(AiShortsError):
    """Erro na geração de temas."""
    
    def __init__(self, message: str, attempt: Optional[int] = None, category: Optional[str] = None):
        super().__init__(message, "THEME_GENERATION_ERROR", {
            "attempt": attempt,
            "category": category
        })

class ScriptGenerationError(AiShortsError):
    """Erro na geração de roteiros."""
    
    def __init__(self, message: str, theme_content: Optional[str] = None, platform: Optional[str] = None):
        super().__init__(message, "SCRIPT_GENERATION_ERROR", {
            "theme_content": theme_content,
            "platform": platform
        })

class RateLimitError(AiShortsError):
    """Erro de rate limiting."""
    
    def __init__(self, message: str, wait_time: Optional[float] = None, retry_after: Optional[int] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", {
            "wait_time": wait_time,
            "retry_after": retry_after
        })

class ValidationError(AiShortsError):
    """Erro de validação de dados."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message, "VALIDATION_ERROR", {
            "field": field,
            "value": value
        })

class YouTubeExtractionError(AiShortsError):
    """Erro na extração do YouTube."""
    
    def __init__(self, message: str, video_url: Optional[str] = None, youtube_error: Optional[str] = None):
        super().__init__(message, "YOUTUBE_EXTRACTION_ERROR", {
            "video_url": video_url,
            "youtube_error": youtube_error
        })

class VideoProcessingError(AiShortsError):
    """Erro no processamento de vídeo."""
    
    def __init__(self, message: str, video_path: Optional[str] = None, ffmpeg_error: Optional[str] = None):
        super().__init__(message, "VIDEO_PROCESSING_ERROR", {
            "video_path": video_path,
            "ffmpeg_error": ffmpeg_error
        })

class VideoUnavailableError(AiShortsError):
    """Erro quando vídeo não está disponível."""
    
    def __init__(self, message: str, video_url: Optional[str] = None, unavailable_reason: Optional[str] = None):
        super().__init__(message, "VIDEO_UNAVAILABLE_ERROR", {
            "video_url": video_url,
            "unavailable_reason": unavailable_reason
        })

class VideoTooShortError(AiShortsError):
    """Erro quando vídeo é muito curto."""
    
    def __init__(self, message: str, video_url: Optional[str] = None, duration: Optional[float] = None, requested_duration: Optional[float] = None):
        super().__init__(message, "VIDEO_TOO_SHORT_ERROR", {
            "video_url": video_url,
            "duration": duration,
            "requested_duration": requested_duration
        })

class NetworkError(AiShortsError):
    """Erro de conectividade de rede."""
    
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message, "NETWORK_ERROR", {
            "url": url,
            "status_code": status_code
        })

class ErrorHandler:
    """Handler centralizado para tratamento de erros."""
    
    @staticmethod
    def handle_error(error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Centraliza o tratamento de erros e logging.
        
        Args:
            error: Exceção capturada
            context: Contexto onde o erro ocorreu
            
        Returns:
            Dicionário com informações do erro
        """
        if isinstance(error, AiShortsError):
            error_info = error.to_dict()
        else:
            error_info = {
                "error_type": error.__class__.__name__,
                "message": str(error),
                "error_code": "UNKNOWN_ERROR",
                "details": {}
            }
        
        # Adicionar contexto se fornecido
        if context:
            error_info["context"] = context
        
        # Log do erro
        logger.error(f"Erro capturado: {error_info}")
        
        return error_info
    
    @staticmethod
    def safe_execute(func, *args, fallback_return=None, context: Optional[str] = None, **kwargs):
        """
        Executa função de forma segura, tratando erros.
        
        Args:
            func: Função a ser executada
            *args: Argumentos da função
            fallback_return: Valor de retorno em caso de erro
            context: Contexto da execução
            **kwargs: Argumentos keyword da função
            
        Returns:
            Resultado da função ou fallback_return em caso de erro
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, context)
            return fallback_return
    
    @staticmethod
    def retry_with_backoff(func, max_retries: int = 3, delay: float = 1.0, *args, **kwargs):
        """
        Executa função com retry e backoff exponencial.
        
        Args:
            func: Função a ser executada
            max_retries: Máximo de tentativas
            delay: Delay inicial entre tentativas
            *args: Argumentos da função
            **kwargs: Argumentos keyword da função
            
        Returns:
            Resultado da função após retry
            
        Raises:
            Última exceção se todas as tentativas falharem
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if attempt < max_retries:
                    wait_time = delay * (2 ** attempt)  # Backoff exponencial
                    logger.warning(f"Tentativa {attempt + 1} falhou, tentando novamente em {wait_time:.2f}s")
                    
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"Todas as {max_retries + 1} tentativas falharam")
                    ErrorHandler.handle_error(e, f"retry_with_backoff - max_retries: {max_retries}")
        
        # Se chegou aqui, todas as tentativas falharam
        raise last_error

if __name__ == "__main__":
    # Teste do sistema de exceções
    print("=== Teste do Sistema de Exceções ===")
    
    # Teste de exceção customizada
    try:
        raise ThemeGenerationError("Teste de erro de geração", attempt=1, category="science")
    except AiShortsError as e:
        error_info = ErrorHandler.handle_error(e, "teste_categoria")
        print(f"Erro processado: {error_info}")
    
    # Teste de execução segura
    def funcao_test():
        if True:  # Simula erro
            raise ValueError("Teste de erro")
        return "sucesso"
    
    result = ErrorHandler.safe_execute(funcao_test, fallback_return="fallback", context="teste_seguro")
    print(f"Resultado seguro: {result}")
    
    # Teste de retry
    try:
        def funcao_retry():
            if ErrorHandler.retry_with_backoff.__code__.co_argcount:  # Se não está na primeira tentativa
                raise OpenRouterError("Teste de retry", status_code=500)
            return "sucesso"
        
        # Teste sem erro simulado
        result = ErrorHandler.retry_with_backoff(lambda: "sucesso", max_retries=1, delay=0.1)
        print(f"Resultado retry: {result}")
    except Exception as e:
        print(f"Erro no retry: {e}")