"""
Cliente OpenRouter para AiShorts v2.0

Implementação robusta da integração com o modelo nvidia/nemotron-nano-9b-v2:free.
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
        
        logger.info(f"OpenRouterClient inicializado - Modelo: {self.config.model}")
    
    def _make_request(self, 
                     messages: List[Dict[str, str]], 
                     max_tokens: Optional[int] = None,
                     temperature: Optional[float] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Faz uma requisição à API OpenRouter.
        
        Args:
            messages: Lista de mensagens no formato OpenAI
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura do modelo
            **kwargs: Parâmetros adicionais
        
        Returns:
            Resposta da API
            
        Raises:
            OpenRouterError: Erro na API
            RateLimitError: Rate limit excedido
        """
        # Preparar payload
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens_theme,
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
            with httpx.Client(timeout=30.0) as client:
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
                        status_code=429,
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
            print("✅ Conexão estabelecida com sucesso!")
        else:
            print("❌ Falha na conexão")
        
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
        
        print(f"📝 Tema gerado: {response.content}")
        print(f"⏱️ Tempo: {response.response_time:.2f}s")
        
        if response.usage:
            print(f"🔢 Tokens usados: {response.usage}")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")