"""
Graceful Degradation - Sistema de degradação graciosa
Permite que o pipeline continue operando mesmo com falhas parciais
"""

import time
import random
import asyncio
from typing import Callable, Any, Optional, List, Dict, Union
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class FallbackStrategy(Enum):
    """Estratégias de fallback disponíveis."""
    SKIP = "skip"  # Pular a etapa
    RETRY = "retry"  # Tentar novamente
    USE_CACHE = "use_cache"  # Usar cache se disponível
    USE_DEFAULT = "use_default"  # Usar valor padrão
    USE_ALTERNATIVE = "use_alternative"  # Usar método alternativo
    DEGRADE = "degrade"  # Degradar para versão mais simples


@dataclass
class RetryConfig:
    """Configuração de retry."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retry_on: Optional[List[type]] = None
    
    def __post_init__(self):
        if self.retry_on is None:
            # Tipos de erro que fazem sentido retry
            self.retry_on = [
                Exception  # Retry em tudo por padrão
            ]


@dataclass
class FallbackConfig:
    """Configuração de fallback."""
    strategy: FallbackStrategy
    fallback_value: Optional[Any] = None
    alternative_method: Optional[Callable] = None
    max_degradation_steps: int = 3
    timeout_seconds: Optional[float] = None


class CircuitBreaker:
    """
    Circuit Breaker para evitar chamadas a serviços que estão falhando.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """
        Inicializa o circuit breaker.
        
        Args:
            failure_threshold: Número de falhas para abrir o circuito
            recovery_timeout: Tempo para tentar recuperação
            expected_exception: Tipo de exceção esperada
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def __call__(self, func):
        """Decorador para aplicar circuit breaker."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception(f"Circuit breaker OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuito."""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Ação em caso de sucesso."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Ação em caso de falha."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")


class GracefulDegradationManager:
    """
    Gerenciador de degradação graciosa para componentes do pipeline.
    """
    
    def __init__(self):
        self.degradation_history: List[Dict[str, Any]] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
    def retry_with_exponential_backoff(
        self,
        config: Optional[RetryConfig] = None
    ) -> Callable:
        """
        Decorador para retry com exponential backoff.
        
        Args:
            config: Configuração de retry
        """
        if config is None:
            config = RetryConfig()
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self._retry_sync(func, config, *args, **kwargs)
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._retry_async(func, config, *args, **kwargs)
            
            # Detectar se é async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def _retry_sync(self, func: Callable, config: RetryConfig, *args, **kwargs) -> Any:
        """Implementação síncrona do retry."""
        last_error = None
        
        for attempt in range(config.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                # Verificar se deve retry
                if not self._should_retry(e, config, attempt):
                    break
                
                # Calcular delay
                delay = self._calculate_delay(attempt, config)
                
logger.warning(
                    f"Retry {attempt + 1}/{config.max_attempts} for {func.__name__} "
                    f"after {delay:.2f}s: {str(e)[:100]}"
                )
                
                time.sleep(delay)
        
        # Se chegou aqui, todas as tentativas falharam
        self._log_degradation(func.__name__, attempt + 1, str(last_error))
        raise last_error
    
    async def _retry_async(self, func: Callable, config: RetryConfig, *args, **kwargs) -> Any:
        """Implementação assíncrona do retry."""
        last_error = None
        
        for attempt in range(config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                # Verificar se deve retry
                if not self._should_retry(e, config, attempt):
                    break
                
                # Calcular delay
                delay = self._calculate_delay(attempt, config)
                
logger.warning(
                    f"Retry {attempt + 1}/{config.max_attempts} for {func.__name__} "
                    f"after {delay:.2f}s: {str(e)[:100]}"
                )
                
                await asyncio.sleep(delay)
        
        # Se chegou aqui, todas as tentativas falharam
        self._log_degradation(func.__name__, attempt + 1, str(last_error))
        raise last_error
    
    def _should_retry(self, error: Exception, config: RetryConfig, attempt: int) -> bool:
        """Verifica se deve retry baseado no erro e tentativa atual."""
        if attempt >= config.max_attempts - 1:
            return False
        
        # Verificar se o tipo de erro está na lista de retry
        for error_type in config.retry_on:
            if isinstance(error, error_type):
                return True
        
        return False
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calcula delay com exponential backoff e jitter."""
        delay = config.initial_delay * (config.backoff_factor ** attempt)
        delay = min(delay, config.max_delay)
        
        if config.jitter:
            # Adicionar jitter de ±25%
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def fallback_on_error(self, config: FallbackConfig) -> Callable:
        """
        Decorador para aplicar fallback em caso de erro.
        
        Args:
            config: Configuração de fallback
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
logger.error(f"Error in {func.__name__}: {str(e)[:100]}")
                    return self._apply_fallback(func, config, e, *args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def _apply_fallback(
        self,
        func: Callable,
        config: FallbackConfig,
        error: Exception,
        *args,
        **kwargs
    ) -> Any:
        """Aplica a estratégia de fallback configurada."""
        self._log_degradation(func.__name__, 0, str(error))
        
        if config.strategy == FallbackStrategy.SKIP:
logger.warning(f"Skipping {func.__name__} due to error")
            return None
        
        elif config.strategy == FallbackStrategy.USE_DEFAULT:
logger.warning(f"Using default value for {func.__name__}")
            return config.fallback_value
        
        elif config.strategy == FallbackStrategy.USE_ALTERNATIVE and config.alternative_method:
logger.warning(f"Using alternative method for {func.__name__}")
            try:
                return config.alternative_method(*args, **kwargs)
            except Exception as e:
logger.error(f"Alternative method also failed: {str(e)}")
                return config.fallback_value
        
        elif config.strategy == FallbackStrategy.DEGRADE:
            return self._degrade_function(func, config, *args, **kwargs)
        
        else:
            raise error
    
    def _degrade_function(
        self,
        func: Callable,
        config: FallbackConfig,
        *args,
        **kwargs
    ) -> Any:
        """
        Degrada a função para uma versão mais simples.
        """
logger.warning(f"Degrading {func.__name__}")
        
        # Implementar degradação específica por função
        func_name = func.__name__
        
        if "theme" in func_name.lower():
            # Degradar para tema genérico
            return "Fascinating science fact that will blow your mind"
        
        elif "script" in func_name.lower():
            # Degradar para script simples
            return {
                "hook": "Did you know this amazing fact?",
                "body": "It's something incredible that changes how we see the world.",
                "conclusion": "Nature never ceases to amaze us with its wonders.",
                "estimated_duration": 60
            }
        
        elif "broll" in func_name.lower():
            # Degradar para query genérica
            return ["documentary footage", "stock video", "nature video"]
        
        elif "tts" in func_name.lower():
            # Degradar para áudio silencioso ou fallback
            return None
        
        else:
            # Degradar genérico
            return config.fallback_value
    
    def get_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """
        Obtém ou cria um circuit breaker para um componente.
        
        Args:
            name: Nome do componente
            **kwargs: Argumentos para o CircuitBreaker
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(**kwargs)
        return self.circuit_breakers[name]
    
    def _log_degradation(self, component: str, attempts: int, error: str):
        """Registra degradação para análise posterior."""
        self.degradation_history.append({
            "timestamp": time.time(),
            "component": component,
            "attempts": attempts,
            "error": error[:200]
        })
        
        # Manter apenas últimas 1000 degradações
        if len(self.degradation_history) > 1000:
            self.degradation_history = self.degradation_history[-1000:]
    
    def get_degradation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de degradação."""
        if not self.degradation_history:
            return {"total_degradations": 0}
        
        recent = [d for d in self.degradation_history 
                 if time.time() - d["timestamp"] < 3600]  # Última hora
        
        component_counts = {}
        for d in recent:
            component = d["component"]
            component_counts[component] = component_counts.get(component, 0) + 1
        
        return {
            "total_degradations": len(self.degradation_history),
            "recent_degradations": len(recent),
            "components_with_issues": len(component_counts),
            "top_failing_components": sorted(
                component_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


# Instância global
degradation_manager = GracefulDegradationManager()


def get_degradation_manager() -> GracefulDegradationManager:
    """Retorna instância global do gerenciador de degradação."""
    return degradation_manager


# Decoradores de conveniência
def retry(config: Optional[RetryConfig] = None):
    """Decorador de retry com configuração padrão."""
    return degradation_manager.retry_with_exponential_backoff(config)


def fallback(strategy: FallbackStrategy, **kwargs):
    """Decorador de fallback com estratégia específica."""
    config = FallbackConfig(strategy=strategy, **kwargs)
    return degradation_manager.fallback_on_error(config)


@contextmanager
def timeout_context(seconds: float):
    """
    Context manager para timeout de operações.
    
    Args:
        seconds: Tempo limite em segundos
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    import signal
    
    # Configurar handler de timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(seconds))
    
    try:
        yield
    finally:
        # Limpar
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


# Exemplos de uso:
if __name__ == "__main__":
    # Exemplo 1: Retry com exponential backoff
    @retry(RetryConfig(max_attempts=3, initial_delay=0.5))
    def unreliable_function():
        import random
        if random.random() < 0.7:  # 70% chance de falha
            raise Exception("Simulated network error")
        return "Success!"
    
    # Exemplo 2: Fallback com valor padrão
    @fallback(FallbackStrategy.USE_DEFAULT, fallback_value="Default value")
    def might_fail():
        raise Exception("Simulated error")
    
    # Exemplo 3: Fallback com método alternativo
    def alternative_method():
        return "Alternative result"
    
    @fallback(FallbackStrategy.USE_ALTERNATIVE, alternative_method=alternative_method)
    def primary_method():
        raise Exception("Primary method failed")
    
    # Testes
print("Testando retry:")
    try:
        result = unreliable_function()
print(f"Resultado: {result}")
    except Exception as e:
print(f"Falha final: {e}")
    
print("\nTestando fallback com padrão:")
    result = might_fail()
print(f"Resultado: {result}")
    
print("\nTestando fallback com alternativo:")
    result = primary_method()
print(f"Resultado: {result}")
    
print("\nEstatísticas de degradação:")
    stats = degradation_manager.get_degradation_stats()
print(f"Stats: {stats}")