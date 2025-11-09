"""
Memory Monitor - Monitoramento de Memória para Pipeline Local
AiShorts v2.0 - Sistema de Monitoramento de Recursos

Monitoramento simples e local do consumo de memória para evitar
congelamento do sistema durante o processamento.
"""

import psutil
import os
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class MemoryStats:
    """Estatísticas de memória"""
    process_gb: float
    system_percent: float
    available_gb: float
    timestamp: float
    
    @property
    def is_critical(self) -> bool:
        """Verifica se uso está crítico (>85%)"""
        return self.system_percent > 85.0
    
    @property
    def is_warning(self) -> bool:
        """Verifica se uso está em nível de alerta (>70%)"""
        return 70.0 < self.system_percent <= 85.0
    
    @property
    def is_safe(self) -> bool:
        """Verifica se uso está seguro (<70%)"""
        return self.system_percent <= 70.0


class MemoryMonitor:
    """
    Monitor de memória simples para uso local.
    
    Features:
    - Monitoramento em tempo real
    - Alertas de consumo crítico
    - Context manager para testes
    - Logging detalhado
    """
    
    def __init__(self, 
                 max_memory_gb: float = 3.0,
                 warning_threshold: float = 70.0,
                 critical_threshold: float = 85.0):
        """
        Inicializa monitor de memória.
        
        Args:
            max_memory_gb: Limite máximo de memória para o processo
            warning_threshold: Percentual para alerta (default: 70%)
            critical_threshold: Percentual para crítico (default: 85%)
        """
        self.max_memory_gb = max_memory_gb
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        
        self.process = psutil.Process(os.getpid())
        self.logger = logging.getLogger(__name__)
        
        # Estatísticas - inicialização segura
        try:
            self.start_memory = self.get_current_stats()
            self.peak_memory = self.start_memory.process_gb
        except Exception:
            # Fallback para inicialização
            self.start_memory = MemoryStats(0.0, 0.0, 0.0, 0.0)
            self.peak_memory = 0.0
        self.checks_count = 0
        
    def get_current_stats(self) -> MemoryStats:
        """Obtém estatísticas atuais de memória"""
        try:
            memory_info = self.process.memory_info()
            virtual_memory = psutil.virtual_memory()
            
            stats = MemoryStats(
                process_gb=memory_info.rss / (1024**3),
                system_percent=virtual_memory.percent,
                available_gb=virtual_memory.available / (1024**3),
                timestamp=time.time()
            )
            
            # Atualizar pico se necessário
            if hasattr(self, 'peak_memory') and stats.process_gb > self.peak_memory:
                self.peak_memory = stats.process_gb
            
            if hasattr(self, 'checks_count'):
                self.checks_count += 1
            else:
                self.checks_count = 1
            return stats
            
        except Exception as e:
self.logger.error(f"Erro ao obter estatísticas de memória: {e}")
            return MemoryStats(0, 0, 0, time.time())
    
    def check_memory(self, context: str = "") -> bool:
        """
        Verifica memória atual e retorna True se está seguro.
        
        Args:
            context: Contexto da verificação (ex: "carregando CLIP")
            
        Returns:
            True se memória está OK, False se está crítica
        """
        stats = self.get_current_stats()
        
        # Log formatado
        context_str = f"[{context}] " if context else ""
self.logger.debug(
            f"{context_str}Memória: {stats.process_gb:.2f}GB "
            f"({stats.system_percent:.1f}% sistema, "
            f"{stats.available_gb:.1f}GB disponível)"
        )
        
        # Verificar limites
        if stats.is_critical:
self.logger.warning(
                f"⚠️ MEMÓRIA CRÍTICA {context_str}: "
                f"{stats.process_gb:.2f}GB ({stats.system_percent:.1f}%)"
            )
            return False
            
        elif stats.is_warning:
self.logger.warning(
                f"⚠️ Memória alta {context_str}: "
                f"{stats.process_gb:.2f}GB ({stats.system_percent:.1f}%)"
            )
            
        elif self.checks_count % 10 == 0:  # Log a cada 10 checks
self.logger.info(
                f"✅ Memória OK {context_str}: "
                f"{stats.process_gb:.2f}GB ({stats.system_percent:.1f}%)"
            )
        
        return True
    
    def suggest_cleanup(self) -> bool:
        """
        Sugere se deve fazer cleanup baseado no uso atual.
        
        Returns:
            True se recomenda cleanup de memória
        """
        stats = self.get_current_stats()
        
        # Recomendar cleanup se uso > 75% ou processo > 2GB
        if stats.system_percent > 75.0 or stats.process_gb > 2.0:
            return True
        
        return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo do monitoramento"""
        current = self.get_current_stats()
        
        return {
            "start_memory_gb": self.start_memory.process_gb if hasattr(self, 'start_memory') else 0.0,
            "current_memory_gb": current.process_gb,
            "peak_memory_gb": getattr(self, 'peak_memory', 0.0),
            "memory_increase_gb": current.process_gb - (self.start_memory.process_gb if hasattr(self, 'start_memory') else 0.0),
            "system_percent": current.system_percent,
            "available_gb": current.available_gb,
            "checks_count": getattr(self, 'checks_count', 0),
            "max_memory_gb": self.max_memory_gb,
            "status": "critical" if current.is_critical else "warning" if current.is_warning else "safe"
        }
    
    @contextmanager
    def monitor_context(self, context: str = ""):
        """
        Context manager para monitorar operação.
        
        Usage:
            with memory_monitor.monitor_context("carregando CLIP") as monitor:
                model = load_clip_model()
                # Monitor automaticamente durante a operação
        """
self.logger.info(f" Iniciando monitoramento: {context}")
        
        start_stats = self.get_current_stats()
        last_safe = True
        
        try:
            yield self
            
        except Exception as e:
self.logger.error(f" Erro durante {context}: {e}")
            raise
            
        finally:
            end_stats = self.get_current_stats()
            
            # Resumo da operação
            duration = end_stats.timestamp - start_stats.timestamp
            memory_delta = end_stats.process_gb - start_stats.process_gb
            
self.logger.info(
                f"✅ Monitoramento finalizado: {context} "
                f"(duração: {duration:.1f}s, memória: {memory_delta:+.2f}GB)"
            )
    
    def force_garbage_collection(self):
        """Força garbage collection para liberar memória"""
        try:
            import gc
            import torch
            
            # Python garbage collection
            collected = gc.collect()
            
            # Limpar cache CUDA se disponível
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            # Verificar memória após cleanup
            after_stats = self.get_current_stats()
            
self.logger.info(
                f"🧹 Cleanup executado: "
                f"{collected} objetos coletados, "
                f"memória atual: {after_stats.process_gb:.2f}GB"
            )
            
        except Exception as e:
self.logger.error(f"Erro no cleanup: {e}")


# Instância global para uso fácil
memory_monitor = MemoryMonitor()


def get_memory_monitor() -> MemoryMonitor:
    """Retorna instância global do monitor de memória"""
    return memory_monitor


@contextmanager
def memory_context(context: str, max_gb: Optional[float] = None):
    """
    Context manager simples para monitoramento de memória.
    
    Args:
        context: Descrição da operação
        max_gb: Limite máximo de memória (opcional)
    
    Usage:
        with memory_context("carregando CLIP", max_gb=2.0):
            model = load_model()
    """
    monitor = MemoryMonitor(max_memory_gb=max_gb or 3.0)
    
    try:
        with monitor.monitor_context(context):
            yield monitor
    finally:
        # Verificar se precisa de cleanup
        if monitor.suggest_cleanup():
            monitor.force_garbage_collection()