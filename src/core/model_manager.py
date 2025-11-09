"""
Model Manager - Centralização e Otimização de Modelos de IA
AiShorts v2.0 - Sistema de Gerenciamento de Memória

Implementa singleton pattern para evitar duplicação de modelos e
lazy loading para otimizar consumo de RAM.
"""

import gc
import logging
import psutil
import os
import threading
from typing import Dict, Any, Optional, Union
from pathlib import Path
import torch
from contextlib import contextmanager
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuração para um modelo local"""
    name: str
    model_class: str
    model_path: str
    device: str = "cpu"  # Foco em CPU para uso local
    lazy_load: bool = True
    memory_threshold_gb: float = 1.5  # Limite conservador para uso local


class ModelManager:
    """
    Singleton manager para centralizar carregamento e gerenciamento de modelos de IA.
    
    Features:
    - Singleton pattern para evitar duplicação
    - Lazy loading para economizar RAM  
    - Memory monitoring automático
    - Cleanup explícito e automático
    - Configurações de limites de memória
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger(__name__)
        
        # Armazenamento de modelos
        self._models: Dict[str, Any] = {}
        self._model_configs: Dict[str, ModelConfig] = {}
        
        # Configurações de memória (otimizado para uso local)
        self.max_memory_gb = 3.0  # Limite conservador para RAM local
        self.auto_cleanup = True
        self.memory_check_interval = 3  # Verificar com mais frequência
        self.force_cpu_mode = True  # Forçar CPU para estabilidade local
        
        # Estatísticas
        self._usage_counts = {}
        self._memory_usage = {}
        
        # Configurações padrão
        self._setup_default_configs()
        
        self._initialized = True
self.logger.info("ModelManager inicializado com lazy loading")
    
    def _setup_default_configs(self):
        """Configurações padrão para modelos conhecidos"""
        self._model_configs.update({
            # Modelo CLIP compartilhado (singleton para economizar RAM)
            "clip_shared": ModelConfig(
                name="CLIP Model (Shared)",
                model_class="transformers.CLIPModel", 
                model_path="openai/clip-vit-base-patch32",
                device="cpu",
                lazy_load=True,
                memory_threshold_gb=1.5
            ),
            "semantic_analyzer": ModelConfig(
                name="Semantic Analyzer",
                model_class="spacy",
                model_path="en_core_web_sm",
                device="cpu",
                lazy_load=True,
                memory_threshold_gb=0.5
            ),
            "kokoro_tts": ModelConfig(
                name="Kokoro TTS",
                model_class="kokoro.Kokoro",
                model_path="kokoro-models",
                device="cpu", 
                lazy_load=True,
                memory_threshold_gb=1.0
            )
        })
    
    def get_model(self, model_key: str, force_reload: bool = False) -> Optional[Any]:
        """
        Obtém um modelo de forma lazy com CLIP compartilhado.
        
        Args:
            model_key: Chave do modelo (clip_relevance_scorer, content_matcher, etc.)
            force_reload: Força recarregamento mesmo se já carregado
            
        Returns:
            Instância do modelo ou None se não encontrado/erro
        """
        # Mapear modelos para instância compartilhada CLIP
        if model_key in ["clip_relevance_scorer", "content_matcher"]:
            actual_key = "clip_shared"
        elif model_key in self._model_configs:
            actual_key = model_key
        else:
self.logger.error(f"Modelo '{model_key}' não configurado")
            return None
        
        # Retornar modelo se já carregado
        if not force_reload and actual_key in self._models:
            self._usage_counts[actual_key] = self._usage_counts.get(actual_key, 0) + 1
            self._check_memory_usage(actual_key)
            return self._models[actual_key]
        
        # Verificar memória disponível (crítico para uso local)
        if not self._check_memory_availability(actual_key):
self.logger.warning(f"Memória insuficiente para '{model_key}', fazendo cleanup...")
            self.cleanup_models(exclude_keys=[actual_key])
            
            if not self._check_memory_availability(actual_key):
self.logger.error(f"Memória crítica! Não é possível carregar '{model_key}'")
                return None
        
        # Carregar modelo
        model = self._load_model(actual_key)
        if model:
            self._models[actual_key] = model
            self._usage_counts[actual_key] = 1
            self._record_memory_usage(actual_key)
self.logger.info(f"Modelo '{model_key}' (como '{actual_key}') carregado com sucesso")
        
        return model
    
    def _load_model(self, model_key: str) -> Optional[Any]:
        """Carrega um modelo específico baseado na configuração"""
        config = self._model_configs[model_key]
        
        try:
            if model_key == "clip_relevance_scorer" or model_key == "content_matcher":
                return self._load_clip_model(config)
            elif model_key == "semantic_analyzer":
                return self._load_spacy_model(config)
            elif model_key == "kokoro_tts":
                return self._load_kokoro_model(config)
            else:
self.logger.error(f"Tipo de modelo não implementado: {model_key}")
                return None
                
        except Exception as e:
self.logger.error(f"Erro ao carregar modelo '{model_key}': {e}")
            return None
    
    def _load_clip_model(self, config: ModelConfig) -> Optional[Any]:
        """Carrega modelo CLIP otimizado para uso local"""
        try:
            from transformers import CLIPProcessor, CLIPModel
            
            # Forçar CPU para estabilidade local e economia de energia
            device = torch.device("cpu")
            
self.logger.info(f"Carregando CLIP model local: {config.model_path} (CPU mode)")
            
            # Carregar com otimizações de memória
            processor = CLIPProcessor.from_pretrained(config.model_path)
            
            # Carregar modelo com low memory optimization
            model = CLIPModel.from_pretrained(
                config.model_path,
                torch_dtype=torch.float32,  # Forçar float32 para compatibilidade
                low_cpu_mem_usage=True  # Otimização de memória
            )
            
            # Manter em CPU forçadamente
            model.to(device)
            model.eval()
            
            # Otimizações adicionais para CPU
            if hasattr(model, 'gradient_checkpointing'):
                model.gradient_checkpointing_enable()
            
            # Retornar estrutura otimizada
            return {
                'model': model,
                'processor': processor,
                'device': device,
                'model_name': config.model_path,
                'is_local_mode': True
            }
            
        except Exception as e:
self.logger.error(f"Erro ao carregar CLIP local: {e}")
            return None
    
    def _load_spacy_model(self, config: ModelConfig) -> Optional[Any]:
        """Carrega modelo spaCy"""
        try:
            import spacy
            
self.logger.info(f"Carregando spaCy model: {config.model_path}")
            model = spacy.load(config.model_path)
            return model
            
        except Exception as e:
self.logger.error(f"Erro ao carregar spaCy: {e}")
            return None
    
    def _load_kokoro_model(self, config: ModelConfig) -> Optional[Any]:
        """Carrega modelo Kokoro TTS"""
        try:
            from src.tts.kokoro_tts import KokoroTTSClient
            
self.logger.info(f"Carregando Kokoro TTS")
            model = KokoroTTSClient()
            return model
            
        except Exception as e:
self.logger.error(f"Erro ao carregar Kokoro TTS: {e}")
            return None
    
    def _setup_device(self, device_config: str) -> torch.device:
        """Configura o dispositivo para o modelo"""
        if device_config == "auto":
            if torch.cuda.is_available():
                device = torch.device("cuda")
self.logger.info("Usando CUDA para modelo")
            elif torch.backends.mps.is_available():
                device = torch.device("mps")
self.logger.info("Usando MPS (Apple Silicon) para modelo")
            else:
                device = torch.device("cpu")
self.logger.info("Usando CPU para modelo")
        else:
            device = torch.device(device_config)
        
        return device
    
    def _check_memory_availability(self, model_key: str) -> bool:
        """Verifica se há memória suficiente para carregar o modelo"""
        available_gb = psutil.virtual_memory().available / (1024**3)
        required_gb = self._model_configs[model_key].memory_threshold_gb
        
        # Margem de segurança de 1GB
        return (available_gb - required_gb) > 1.0
    
    def _check_memory_usage(self, model_key: str):
        """Verifica uso de memória e faz cleanup se necessário"""
        if self.auto_cleanup and self._usage_counts[model_key] % self.memory_check_interval == 0:
            current_memory = psutil.virtual_memory().percent
            
            if current_memory > 80:  # Se usar mais de 80% da RAM
self.logger.warning(f"Alto uso de memória ({current_memory:.1f}%), fazendo cleanup...")
                self.cleanup_models(exclude_keys=[model_key])
    
    def _record_memory_usage(self, model_key: str):
        """Registra uso de memória após carregar modelo"""
        process = psutil.Process(os.getpid())
        memory_gb = process.memory_info().rss / (1024**3)
        self._memory_usage[model_key] = memory_gb
    
    def cleanup_models(self, exclude_keys: Optional[list] = None):
        """Libera memória dos modelos carregados"""
        exclude_keys = exclude_keys or []
        
        for model_key in list(self._models.keys()):
            if model_key in exclude_keys:
                continue
            
            try:
                model_data = self._models[model_key]
                
                # Cleanup específico por tipo
                if model_key in ["clip_relevance_scorer", "content_matcher"]:
                    if isinstance(model_data, dict) and 'model' in model_data:
                        del model_data['model']
                        del model_data['processor']
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                
                del self._models[model_key]
self.logger.info(f"Modelo '{model_key}' liberado da memória")
                
            except Exception as e:
self.logger.error(f"Erro ao liberar modelo '{model_key}': {e}")
        
        # Garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    @contextmanager
    def model_context(self, model_key: str):
        """
        Context manager para uso temporário de modelo com cleanup automático.
        
        Usage:
            with model_manager.model_context("clip_relevance_scorer") as model:
                result = model.process(text, video_path)
            # Modelo automaticamente liberado após o contexto
        """
        model = self.get_model(model_key)
        try:
            yield model
        finally:
            # Cleanup apenas se não for modelo frequentemente usado
            if self._usage_counts.get(model_key, 0) < 3:
                self.cleanup_models(exclude_keys=[model_key])
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de memória dos modelos"""
        process = psutil.Process(os.getpid())
        
        return {
            "process_memory_gb": process.memory_info().rss / (1024**3),
            "system_memory_percent": psutil.virtual_memory().percent,
            "loaded_models": list(self._models.keys()),
            "model_usage_counts": self._usage_counts.copy(),
            "model_memory_usage": self._memory_usage.copy(),
            "available_memory_gb": psutil.virtual_memory().available / (1024**3)
        }
    
    def preload_model(self, model_key: str):
        """Força o carregamento prévio de um modelo"""
self.logger.info(f"Pré-carregando modelo: {model_key}")
        return self.get_model(model_key)
    
    def unload_model(self, model_key: str):
        """Força a liberação de um modelo específico"""
        if model_key in self._models:
            self.cleanup_models(exclude_keys=[model_key])
            if model_key in self._models:
                del self._models[model_key]
self.logger.info(f"Modelo '{model_key}' descarregado")


# Instância global do manager
model_manager = ModelManager()


def get_model_manager() -> ModelManager:
    """Retorna a instância singleton do ModelManager"""
    return model_manager