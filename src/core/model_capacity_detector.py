"""
Model Capacity Detector - Detector Automático de Capacidades de Modelos
AiShorts v2.0 - Sistema de Auto-Configuração de Tokens via API

Detecta automaticamente o limite máximo de tokens para cada modelo OpenRouter
via API e ajusta os parâmetros para evitar truncamento de respostas.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)

@dataclass
class ModelLimits:
    """Limites de um modelo específico"""
    max_context_tokens: int  # Limite total do contexto
    max_output_tokens: int   # Limite da resposta
    recommended_input: int   # Input recomendado para segurança
    safe_output: int        # Output seguro (80% do limite)
    model_info: Dict[str, Any]  # Informações completas do modelo


class ModelCapacityDetector:
    """
    Detector automático de capacidades de modelos com cache.
    
    Features:
    - Base de dados de modelos conhecidos
    - Detecção automática via API OpenRouter
    - Cache de capacidades detectadas
    - Fallbacks seguros
    """
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Configuração da API OpenRouter
        self.api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Cache de capacidades detectadas (persistente entre execuções)
        self.detected_cache = {}
        
        # Cache em memória durante execução
        self.memory_cache = {}
        
        # Estatísticas de detecção
        self.stats = {
            'api_requests': 0,
            'cache_hits': 0,
            'detections': 0,
            'fallbacks': 0
        }
        
        # Headers para API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aishorts.v2",
            "X-Title": "AiShorts v2.0 - Model Capacity Detector"
        }
        
    def get_model_limits(self, model_name: str) -> ModelLimits:
        """
        Obtém os limites de um modelo exclusivamente via API OpenRouter.
        
        Args:
            model_name: Nome do modelo (ex: "openrouter/polaris-alpha")
            
        Returns:
            ModelLimits com as capacidades do modelo
            
        Raises:
            RuntimeError: Se não for possível detectar os limites
        """
        # Extrair nome base do modelo
        base_name = self._extract_model_base_name(model_name)
        
        # Verificar cache em memória primeiro
        if base_name in self.memory_cache:
self.logger.debug(f" Limites do cache: {base_name}")
            self.stats['cache_hits'] += 1
            return self.memory_cache[base_name]
        
        # Tentar obter da API OpenRouter
        api_limits = self._detect_from_openrouter_api(model_name)
        if api_limits:
self.logger.info(f" Detectado via API para {model_name}: {api_limits.max_output_tokens} tokens output")
            self.stats['detections'] += 1
            self.memory_cache[base_name] = api_limits
            return api_limits
        
        # Se a API falhar, não usar fallback - lançar erro
        raise RuntimeError(
            f"Não foi possível detectar limites para o modelo '{model_name}'. "
            f"Verifique se o modelo existe na API OpenRouter ou se a API key está correta."
        )
    
    def _detect_from_openrouter_api(self, model_name: str) -> Optional[ModelLimits]:
        """
        Detecta limites do modelo via API OpenRouter usando a lista de modelos.
        
        Args:
            model_name: Nome completo do modelo
            
        Returns:
            ModelLimits detectado ou None
        """
        if not self.api_key:
self.logger.warning(" API key não configurada, pulando detecção via API")
            return None
        
        try:
            with httpx.Client(timeout=15.0) as client:
self.logger.debug(f" Consultando lista de modelos OpenRouter para: {model_name}")
                self.stats['api_requests'] += 1
                
                # Buscar todos os modelos e encontrar o nosso modelo
                response = client.get(f"{self.base_url}/models", headers=self.headers)
                
                if response.status_code == 200:
                    models_data = response.json()
                    all_models = models_data.get('data', [])
                    
                    # Encontrar o modelo específico
                    target_model = next(
                        (model for model in all_models if model.get('id') == model_name),
                        None
                    )
                    
                    if target_model:
self.logger.debug(f" Modelo {model_name} encontrado na lista")
                        return self._parse_openrouter_model_info(target_model)
                    else:
self.logger.warning(f" Modelo {model_name} não encontrado na lista de {len(all_models)} modelos")
                        return None
                else:
self.logger.error(f" Erro na listagem de modelos: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
self.logger.error(f" Erro na consulta API OpenRouter para {model_name}: {e}")
            return None
    
    def _parse_openrouter_model_info(self, model_data: Dict[str, Any]) -> ModelLimits:
        """
        Parseia informações do modelo da API OpenRouter.
        
        Args:
            model_data: Dados do modelo retornados pela API
            
        Returns:
            ModelLimits processado
        """
        # Extrair informações de contexto e tokens
        context_length = model_data.get('context_length', 4096)
        max_tokens = model_data.get('top_provider', {}).get('max_completion_tokens', None)
        
        # Se max_tokens não disponível, inferir do context_length
        if max_tokens is None:
            max_tokens = min(context_length // 4, 8192)  # Regra geral: 25% do contexto
        
        # Calcular valores seguros
        recommended_input = int(context_length * 0.8)  # 80% do contexto para input
        safe_output = int(max_tokens * 0.8)  # 80% do máximo para segurança
        
self.logger.debug(f" Parsing modelo: context={context_length}, max_tokens={max_tokens}")
        
        return ModelLimits(
            max_context_tokens=context_length,
            max_output_tokens=max_tokens,
            recommended_input=recommended_input,
            safe_output=safe_output,
            model_info={
                'name': model_data.get('name', 'Unknown'),
                'id': model_data.get('id', 'unknown'),
                'description': model_data.get('description', ''),
                'pricing': model_data.get('pricing', {}),
                'architecture': model_data.get('architecture', {}),
                'source': 'openrouter_api'
            }
        )
    
    async def _detect_from_openrouter_api_async(self, model_name: str) -> Optional[ModelLimits]:
        """Versão assíncrona da detecção via API"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models/{model_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    model_data = response.json()
                    return self._parse_openrouter_model_info(model_data)
                else:
                    return None
                    
        except Exception as e:
self.logger.error(f" Erro na API assíncrona para {model_name}: {e}")
            return None
    
    def _extract_model_base_name(self, model_name: str) -> str:
        """Extrai o nome base do modelo"""
        # Remover provider (ex: "openrouter/" prefixo)
        if "/" in model_name:
            parts = model_name.split("/")
            if len(parts) > 1:
                model_name = "/".join(parts[1:])  # Manter provider se houver múltiplos /
        
        # Remover sufixos como ":free", ":latest", etc.
        if ":" in model_name:
            model_name = model_name.split(":")[0]
        
        return model_name.lower()
    
        
    def calculate_optimal_max_tokens(self, 
                                   model_name: str, 
                                   input_tokens_estimate: int = 0,
                                   task_type: str = "general") -> int:
        """
        Calcula o max_tokens ideal para uma tarefa específica.
        
        Args:
            model_name: Nome do modelo
            input_tokens_estimate: Estimativa de tokens de entrada
            task_type: Tipo de tarefa (theme, script, general)
            
        Returns:
            Número ideal de max_tokens
        """
        limits = self.get_model_limits(model_name)
        
        # Calcular espaço disponível para output
        available_context = limits.max_context_tokens - input_tokens_estimate - 100  # 100 tokens de buffer
        
        # Ajustar baseado no tipo de tarefa
        if task_type == "theme":
            # Temas geralmente curtos
            optimal = min(limits.safe_output, 500, available_context)
        elif task_type == "script":
            # Scripts podem ser longos
            optimal = min(limits.safe_output, 2000, available_context)
        else:
            # General purpose
            optimal = min(limits.safe_output, available_context)
        
        # Garantir mínimo razoável
        optimal = max(optimal, 200)
        
self.logger.debug(f" Tokens ótimos para {model_name} ({task_type}): {optimal} (input: {input_tokens_estimate})")
        
        return int(optimal)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "cached_models": len(self.memory_cache),
            "cached_list": list(self.memory_cache.keys()),
            "stats": self.stats
        }


# Instância global
model_detector = None


def get_model_detector() -> ModelCapacityDetector:
    """Retorna a instância global do detector de modelos"""
    global model_detector
    if model_detector is None:
        # Tentar obter API key do ambiente
        import os
        from src.config.settings import config
        
        api_key = config.openrouter.api_key or os.getenv("OPENROUTER_API_KEY")
        model_detector = ModelCapacityDetector(openrouter_api_key=api_key)
        
        if api_key:
model_detector.logger.info(" ModelCapacityDetector inicializado com API OpenRouter")
        else:
model_detector.logger.warning(" ModelCapacityDetector sem API key (modo fallback)")
    
    return model_detector


def initialize_model_detector(api_key: str) -> ModelCapacityDetector:
    """Inicializa o detector com API key específica"""
    global model_detector
    model_detector = ModelCapacityDetector(openrouter_api_key=api_key)
    return model_detector