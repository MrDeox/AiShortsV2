"""
Async OpenRouter Client - Cliente Assíncrono OpenRouter
AiShorts v2.0 - Requests Paralelos para Melhor Performance

Cliente OpenRouter com suporte a requests assíncronos paralelos
para reduzir tempo total de geração de conteúdo.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Coroutine
from dataclasses import dataclass

import httpx
from loguru import logger

from src.config.settings import config
from src.utils.exceptions import OpenRouterError, RateLimitError, ErrorHandler
from src.core.openrouter_client import OpenRouterResponse, RateLimiter

# Importar detector de capacidades
try:
    from src.core.model_capacity_detector import get_model_detector
    MODEL_DETECTOR_AVAILABLE = True
except ImportError:
    MODEL_DETECTOR_AVAILABLE = False

@dataclass
class AsyncRequest:
    """Request assíncrono para OpenRouter"""
    prompt: str
    system_message: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    task_type: str = "general"
    request_id: Optional[str] = None
    timeout: float = 30.0


class AsyncOpenRouterClient:
    """
    Cliente OpenRouter com suporte a requests assíncronos.
    
    Features:
    - Requests paralelos para múltiplas tarefas
    - Rate limiting assíncrono
    - Timeout por request individual
    - Batch processing
    - Callbacks para progress tracking
    """
    
    def __init__(self):
        """Inicializa o cliente assíncrono"""
        # Herdar configurações do cliente síncrono
        self.config = config.openrouter
        self.retry_config = config.retry
        
        # Cliente HTTP assíncrono
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Rate limiter compartilhado
        self.rate_limiter = RateLimiter(
            max_requests=self.retry_config.rate_limit_per_minute,
            time_window=60
        )
        
        # Detector de capacidades
        self.model_detector = get_model_detector() if MODEL_DETECTOR_AVAILABLE else None
        
        # Estatísticas
        self.stats = {
            'total_requests': 0,
            'parallel_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'average_response_time': 0.0
        }
        
        # CORREÇÃO BUG: Usar variáveis de ambiente diretamente
        import os
        api_key = os.getenv('OPENROUTER_API_KEY', self.config.api_key)
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY não está configurada")
        
        # Headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aishorts.v2",
            "X-Title": "AiShorts v2.0 (Async)"
        }
        
logger.info(" AsyncOpenRouterClient inicializado")
    
    async def _acquire_rate_limit(self) -> bool:
        """Adquire permissão do rate limiter de forma assíncrona"""
        while not self.rate_limiter.can_make_request():
            await asyncio.sleep(0.1)  # Pequeno delay para não bloquear
        
        self.rate_limiter.add_request()
        return True
    
    async def _make_single_request(self, request: AsyncRequest) -> OpenRouterResponse:
        """
        Faz um único request assíncrono.
        
        Args:
            request: Objeto AsyncRequest
            
        Returns:
            OpenRouterResponse
            
        Raises:
            OpenRouterError: Se houver erro
        """
        start_time = time.time()
        
        # Aguardar rate limit
        await self._acquire_rate_limit()
        
        # Calcular max_tokens automático se necessário
        if request.max_tokens is None and self.model_detector:
            input_text = f"{request.system_message or ''} {request.prompt}"
            input_tokens_estimate = len(input_text.split()) * 1.3
            
            request.max_tokens = self.model_detector.calculate_optimal_max_tokens(
                self.config.model,
                int(input_tokens_estimate),
                request.task_type
            )
        
        # Preparar payload
        messages = []
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": request.max_tokens or self.config.max_tokens_theme,
            "temperature": request.temperature or self.config.temperature_theme,
        }
        
        try:
            response = await self.client.post(
                f"{self.config.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=request.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            # Atualizar estatísticas
            response_time = time.time() - start_time
            self.stats['total_requests'] += 1
            self.stats['successful_requests'] += 1
            
            # Atualizar média de tempo
            total_time = self.stats['average_response_time'] * (self.stats['total_requests'] - 1)
            self.stats['average_response_time'] = (total_time + response_time) / self.stats['total_requests']
            
logger.debug(f" Request {request.request_id} concluído em {response_time:.2f}s")
            
            return OpenRouterResponse(
                content=content,
                model=self.config.model,
                usage=usage,
                response_time=response_time,
                timestamp=datetime.now()
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"Erro HTTP {e.response.status_code}: {e.response.text}"
logger.error(f" Request {request.request_id} falhou: {error_msg}")
            self.stats['failed_requests'] += 1
            
            if e.response.status_code == 429:
                raise RateLimitError("Rate limit excedido")
            else:
                raise OpenRouterError(error_msg, request.request_id)
                
        except Exception as e:
            error_msg = f"Erro no request {request.request_id}: {str(e)}"
logger.error(f" {error_msg}")
            self.stats['failed_requests'] += 1
            raise OpenRouterError(error_msg, request.request_id)
    
    async def generate_multiple_content(self, 
                                     requests: List[AsyncRequest],
                                     progress_callback: Optional[callable] = None) -> List[OpenRouterResponse]:
        """
        Gera múltiplos conteúdos em paralelo.
        
        Args:
            requests: Lista de AsyncRequest objects
            progress_callback: Callback opcional para progresso
            
        Returns:
            Lista de OpenRouterResponse
        """
logger.info(f" Iniciando {len(requests)} requests em paralelo")
        self.stats['parallel_requests'] += len(requests)
        
        # Adicionar request IDs se não fornecidos
        for i, req in enumerate(requests):
            if req.request_id is None:
                req.request_id = f"req_{i+1}_{int(time.time())}"
        
        # Função wrapper para callback de progresso
        async def request_with_callback(request: AsyncRequest) -> OpenRouterResponse:
            try:
                response = await self._make_single_request(request)
                if progress_callback:
                    progress_callback(len(requests), 1, request.request_id, True)
                return response
            except Exception as e:
                if progress_callback:
                    progress_callback(len(requests), 1, request.request_id, False, str(e))
                raise
        
        # Executar requests em paralelo com controle de concorrência
        max_concurrent = min(len(requests), 5)  # Máximo 5 simultâneos
        
        responses = []
        failed_count = 0
        
        # Processar em lotes para controlar concorrência
        for i in range(0, len(requests), max_concurrent):
            batch = requests[i:i + max_concurrent]
            
            try:
                # Executar lote em paralelo
                batch_results = await asyncio.gather(
                    *[request_with_callback(req) for req in batch],
                    return_exceptions=True
                )
                
                # Processar resultados do lote
                for result in batch_results:
                    if isinstance(result, Exception):
logger.error(f" Request falhou: {result}")
                        failed_count += 1
                    else:
                        responses.append(result)
                        
            except Exception as e:
logger.error(f" Erro no lote {i//max_concurrent + 1}: {e}")
                failed_count += len(batch)
        
        success_count = len(responses)
        total_count = len(requests)
        
logger.info(
            f"📊 Requests paralelos concluídos: "
            f"{success_count}/{total_count} bem-sucedidos, {failed_count} falhas"
        )
        
        return responses
    
    async def generate_theme_and_script_parallel(self, 
                                                theme_request: AsyncRequest,
                                                script_request: AsyncRequest) -> tuple[OpenRouterResponse, OpenRouterResponse]:
        """
        Gera tema e script em paralelo (caso de uso comum).
        
        Args:
            theme_request: Request para tema
            script_request: Request para script
            
        Returns:
            Tuple com (theme_response, script_response)
        """
logger.info(" Gerando tema e script em paralelo...")
        
        # Configurar requests corretamente
        theme_request.task_type = "theme"
        theme_request.temperature = 0.8  # Mais criativo
        
        script_request.task_type = "script"
        script_request.temperature = 0.6  # Mais estruturado
        
        # Adicionar IDs
        if theme_request.request_id is None:
            theme_request.request_id = "theme_req"
        if script_request.request_id is None:
            script_request.request_id = "script_req"
        
        # Executar em paralelo
        try:
            theme_response, script_response = await asyncio.gather(
                self._make_single_request(theme_request),
                self._make_single_request(script_request),
                return_exceptions=True
            )
            
            # Verificar erros
            if isinstance(theme_response, Exception):
                raise OpenRouterError(f"Erro no tema: {theme_response}")
            if isinstance(script_response, Exception):
                raise OpenRouterError(f"Erro no script: {script_response}")
            
            total_time = max(theme_response.response_time, script_response.response_time)
logger.info(f" Tema e script gerados em paralelo ({total_time:.2f}s)")
            
            return theme_response, script_response
            
        except Exception as e:
logger.error(f" Falha na geração paralela: {e}")
            raise
    
    async def generate_json(self,
                           system_message: str,
                           user_message: str,
                           temperature: Optional[float] = None,
                           max_tokens: Optional[int] = None,
                           **kwargs) -> Dict[str, Any]:
        """
        Gera resposta em formato JSON estruturado.
        
        Args:
            system_message: Mensagem do sistema
            user_message: Mensagem do usuário
            temperature: Temperatura para geração
            max_tokens: Tokens máximos
            **kwargs: Argumentos adicionais
            
        Returns:
            Dict com resposta JSON
        """
        request = AsyncRequest(
            prompt=user_message,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            task_type="json"
        )
        
        response = await self._make_single_request(request)
        
        # Tentar fazer parse do JSON
        try:
            import json
            # Limpar o conteúdo para garantir JSON válido
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Fazer parse
            parsed = json.loads(content)
logger.debug(f" JSON gerado com sucesso: {len(parsed)} campos")
            return parsed
            
        except json.JSONDecodeError as e:
logger.error(f" Erro ao fazer parse do JSON: {e}")
logger.debug(f"Conteúdo bruto: {response.content[:200]}...")
            # Retornar conteúdo bruto se não for JSON válido
            return {"raw_content": response.content, "parse_error": str(e)}
    
    async def close(self):
        """Fecha o cliente HTTP e limpa recursos"""
        await self.client.aclose()
logger.info(" AsyncOpenRouterClient fechado")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cliente"""
        return {
            **self.stats,
            'success_rate': self.stats['successful_requests'] / max(self.stats['total_requests'], 1),
            'rate_limit_per_minute': self.retry_config.rate_limit_per_minute,
            'model': self.config.model,
            'base_url': self.config.base_url
        }


# Instância global
async_openrouter_client = None


def get_async_openrouter_client() -> AsyncOpenRouterClient:
    """Retorna instância global do cliente assíncrono"""
    global async_openrouter_client
    if async_openrouter_client is None:
        async_openrouter_client = AsyncOpenRouterClient()
    return async_openrouter_client


async def generate_theme_and_script_async(theme_prompt: str, 
                                         script_prompt: str,
                                         system_message: str = None) -> tuple[str, str]:
    """
    Função de conveniência para gerar tema e script em paralelo.
    
    Args:
        theme_prompt: Prompt para tema
        script_prompt: Prompt para script  
        system_message: Mensagem de sistema
        
    Returns:
        Tuple com (tema_gerado, script_gerado)
    """
    client = get_async_openrouter_client()
    
    # Criar requests
    theme_req = AsyncRequest(
        prompt=theme_prompt,
        system_message=system_message,
        task_type="theme"
    )
    
    script_req = AsyncRequest(
        prompt=script_prompt,
        system_message=system_message,
        task_type="script"
    )
    
    # Gerar em paralelo
    theme_response, script_response = await client.generate_theme_and_script_parallel(
        theme_req, script_req
    )
    
    return theme_response.content, script_response.content