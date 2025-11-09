"""
Cliente OpenRouter para AiShorts v2.0

Integração centralizada com o modelo qwen/qwen3-235b-a22b:free via OpenRouter.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import httpx
from loguru import logger

from src.config.settings import config
from src.utils.exceptions import OpenRouterError, RateLimitError, ErrorHandler

# Importar detector de capacidades de modelos
try:
    from src.core.model_capacity_detector import get_model_detector
    MODEL_DETECTOR_AVAILABLE = True
except ImportError:
    MODEL_DETECTOR_AVAILABLE = False
logger.warning("ModelCapacityDetector não disponível, usando max_tokens fixo")


@dataclass
class OpenRouterResponse:
    """Resposta da API OpenRouter."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    response_time: Optional[float] = None
    timestamp: Optional[datetime] = None


class RateLimiter:
    """Rate limiter para controlar chamadas à API."""
    
    def __init__(self, max_requests: int = 20, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Verifica se pode fazer uma nova requisição."""
        now = datetime.now()
        
        # Remove requisições antigas fora da janela de tempo
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        
        # Verifica se ainda pode fazer requisições
        return len(self.requests) < self.max_requests
    
    def add_request(self):
        """Adiciona uma nova requisição."""
        self.requests.append(datetime.now())
    
    def get_wait_time(self) -> float:
        """Calcula quanto tempo deve esperar."""
        if self.can_make_request():
            return 0.0
        
        # Tempo até a requisição mais antiga sair da janela
        oldest_request = min(self.requests)
        wait_until = oldest_request + timedelta(seconds=self.time_window)
        wait_seconds = (wait_until - datetime.now()).total_seconds()
        
        return max(0.0, wait_seconds)


class OpenRouterClient:
    """Cliente robusto para integração com OpenRouter."""
    
    def __init__(self):
        self.config = config.openrouter
        self.retry_config = config.retry
        
        # CORREÇÃO BUG: Usar variáveis de ambiente diretamente
        import os
        api_key = os.getenv('OPENROUTER_API_KEY', self.config.api_key)
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY não está configurada")
        
        # Headers padrão
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aishorts.v2",
            "X-Title": "AiShorts v2.0"
        }
        
        # Rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=self.retry_config.rate_limit_per_minute,
            time_window=60
        )
        
        # Detector automático de capacidades (inicializado automaticamente)
        if MODEL_DETECTOR_AVAILABLE:
            self.model_detector = get_model_detector()
            # Se o detector ainda não tiver API key, inicializar com a nossa
            if self.model_detector and not self.model_detector.api_key:
                self.model_detector = ModelCapacityDetector(openrouter_api_key=self.config.api_key)
        else:
            self.model_detector = None
        
        if self.model_detector:
            try:
                limits = self.model_detector.get_model_limits(self.config.model)
logger.info(f"OpenRouterClient initialized - Modelo: {self.config.model}")
logger.info(f"Rate limits detected via API: {limits.max_output_tokens:,} tokens output, {limits.max_context_tokens:,} contexto")
logger.info(f" Fonte: {limits.model_info.get('source', 'unknown')}")
logger.info(f"Auto max tokens enabled (seguro: {limits.safe_output:,} tokens)")
            except RuntimeError as e:
logger.error(f" Erro ao detectar limites via API: {e}")
logger.warning(" Usando max_tokens fixo como fallback")
                self.model_detector = None  # Desativar detector em caso de erro
        else:
logger.info(f"OpenRouterClient inicializado - Modelo: {self.config.model}")
logger.warning(" Detector de capacidades não disponível, usando max_tokens fixo")
        
logger.info(
            "OpenRouterClient usando base_url=%s; configure OPENROUTER_MODEL/OPENROUTER_BASE_URL no .env para mudar o provider/modelo.",
            self.config.base_url,
        )
    
    def _make_request(self, 
                     messages: List[Dict[str, str]], 
                     max_tokens: Optional[int] = None,
                     temperature: Optional[float] = None,
                     task_type: str = "general",
                     **kwargs) -> Dict[str, Any]:
        """
        Faz uma requisição à API OpenRouter com max_tokens automático.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            max_tokens: Máximo de tokens na resposta (opcional, auto-detected se None)
            temperature: Temperatura do modelo
            task_type: Tipo de tarefa para otimizar tokens (theme, script, general)
            **kwargs: Parâmetros adicionais
        
        Returns:
            Resposta da API
            
        Raises:
            OpenRouterError: Erro na API
            RateLimitError: Rate limit excedido
        """
        # Calcular max_tokens automático se não fornecido
        if max_tokens is None and self.model_detector:
            # Estimar tokens de entrada
            input_text = " ".join([msg.get("content", "") for msg in messages])
            input_tokens_estimate = len(input_text.split()) * 1.3  # Estimativa粗糙
            
            # Calcular max_tokens ótimo para o modelo e tarefa
            max_tokens = self.model_detector.calculate_optimal_max_tokens(
                self.config.model, 
                int(input_tokens_estimate), 
                task_type
            )
            
logger.debug(f" Max tokens auto-ajustado: {max_tokens} para {task_type}")
        
        # Fallback para configuração fixa se detector não disponível
        if max_tokens is None:
            max_tokens = self.config.max_tokens_theme
        
        # Preparar payload
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature or self.config.temperature_theme,
            **kwargs
        }
        
        # Verificar rate limit
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.get_wait_time()
            raise RateLimitError(
                f"Rate limit excedido. Aguarde {wait_time:.2f} segundos.",
                wait_time=wait_time
            )
        
        try:
            # Aumentar timeout para respostas longas (tokens altos)
            with httpx.Client(timeout=120.0) as client:
                start_time = time.time()
                
                response = client.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                response_time = time.time() - start_time
                self.rate_limiter.add_request()
                
                # Log da requisição
logger.debug(f"OpenRouter request - Tempo: {response_time:.2f}s, Status: {response.status_code}")
                
                # Verificar resposta
                if response.status_code == 200:
                    return {
                        "content": response.json(),
                        "response_time": response_time,
                        "timestamp": datetime.now()
                    }
                
                elif response.status_code == 429:
                    # Rate limit
                    wait_time = self.rate_limiter.get_wait_time()
                    raise RateLimitError(
                        f"Rate limit HTTP 429 - Aguarde {wait_time:.2f}s",
                        wait_time=wait_time
                    )
                
                elif response.status_code >= 400:
                    # Erro na API
                    error_data = response.json() if response.content else {}
                    raise OpenRouterError(
                        f"Erro HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        response_data=error_data
                    )
                
                else:
                    # Outros erros
                    raise OpenRouterError(
                        f"Erro inesperado HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code
                    )
        
        except httpx.TimeoutException:
            raise OpenRouterError("Timeout na requisição OpenRouter (30s)")
        
        except httpx.RequestError as e:
            raise OpenRouterError(f"Erro de rede: {str(e)}")
    
    def generate_content(self, 
                        prompt: str, 
                        context: Optional[str] = None,
                        system_message: Optional[str] = None,
                        **kwargs) -> OpenRouterResponse:
        """
        Gera conteúdo usando o modelo OpenRouter.
        
        Args:
            prompt: Prompt principal
            context: Contexto adicional
            system_message: Mensagem do sistema
            **kwargs: Parâmetros adicionais para a API
        
        Returns:
            OpenRouterResponse com conteúdo gerado
        """
        try:
            # Construir mensagens
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            if context:
                messages.append({"role": "system", "content": context})
            
            messages.append({"role": "user", "content": prompt})
            
            # Fazer requisição com retry
            def _make_request():
                return self._make_request(messages, **kwargs)
            
            result = ErrorHandler.retry_with_backoff(
                _make_request,
                max_retries=self.retry_config.max_retries,
                delay=self.retry_config.retry_delay
            )
            
            # Processar resposta
            response_data = result["content"]
            response_time = result["response_time"]
            timestamp = result["timestamp"]
            
            # Extrair conteúdo da resposta
            content = response_data["choices"][0]["message"]["content"]
            
            # Extrair informações de uso se disponíveis
            usage = response_data.get("usage", {})
            
logger.info(f"Conteúdo gerado - Tempo: {response_time:.2f}s, Tokens: {usage.get('total_tokens', 'N/A')}")
            
            return OpenRouterResponse(
                content=content,
                model=self.config.model,
                usage=usage,
                response_time=response_time,
                timestamp=timestamp
            )
        
        except RateLimitError:
            # Re-raise rate limit errors
            raise
        
        except Exception as e:
            # Tratar outros erros
            if isinstance(e, OpenRouterError):
                raise
            else:
                raise OpenRouterError(f"Erro inesperado na geração: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com a API OpenRouter.
        
        Returns:
            True se a conexão for bem-sucedida
        """
        try:
            response = self.generate_content(
                prompt="Responda apenas 'Teste bem-sucedido'.",
                max_tokens=10,
                temperature=0.1
            )
            
logger.info(f"Conexão OpenRouter testada: {response.content[:50]}...")
            return True
        
        except Exception as e:
logger.error(f"Erro no teste de conexão OpenRouter: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o modelo configurado.
        
        Returns:
            Informações do modelo
        """
        return {
            "model": self.config.model,
            "base_url": self.config.base_url,
            "max_tokens": self.config.max_tokens_theme,
            "temperature": self.config.temperature_theme,
            "rate_limit_per_minute": self.retry_config.rate_limit_per_minute,
            "max_retries": self.retry_config.max_retries
        }


# Instância global do cliente
openrouter_client = OpenRouterClient()

if __name__ == "__main__":
    # Teste do cliente OpenRouter
print("=== Teste do OpenRouter Client ===")
    
    try:
        # Teste de conexão
print("1. Testando conexão...")
        if openrouter_client.test_connection():
print(" Conexão estabelecida com sucesso!")
        else:
print(" Falha na conexão")
        
        # Informações do modelo
print("\n2. Informações do modelo:")
        model_info = openrouter_client.get_model_info()
        for key, value in model_info.items():
print(f"   {key}: {value}")
        
        # Teste de geração
print("\n3. Teste de geração de conteúdo:")
        response = openrouter_client.generate_content(
            prompt="Sugira um tema interessante sobre ciência para um vídeo curto.",
            system_message="Você é um especialista em criação de conteúdo viral."
        )
        
print(f" Tema gerado: {response.content}")
print(f"⏱ Tempo: {response.response_time:.2f}s")
        
        if response.usage:
print(f" Tokens usados: {response.usage}")
    
    except Exception as e:
print(f" Erro no teste: {e}")
