"""
Content Cache - Sistema de cache inteligente para respostas LLM
Reduz chamadas API e melhora performance do pipeline
"""

import hashlib
import json
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import threading

from loguru import logger


@dataclass
class CacheEntry:
    """Entrada de cache com metadados."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_hours: int
    size_bytes: int
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou."""
        expiry_time = self.created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry_time
    
    def touch(self):
        """Atualiza timestamp de último acesso."""
        self.last_accessed = datetime.now()
        self.access_count += 1


class ContentCache:
    """
    Cache thread-safe para conteúdo LLM com persistência opcional.
    
    Features:
    - TTL por entrada
    - Controle de tamanho máximo
    - Persistência em disco
    - Estatísticas de uso
    - Evicção LRU (Least Recently Used)
    """
    
    def __init__(
        self,
        max_size_mb: int = 100,
        default_ttl_hours: int = 24,
        persist_to_disk: bool = True,
        cache_dir: Optional[Path] = None
    ):
        """
        Inicializa o cache.
        
        Args:
            max_size_mb: Tamanho máximo em MB
            default_ttl_hours: TTL padrão em horas
            persist_to_disk: Se deve persistir em disco
            cache_dir: Diretório para cache em disco
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl_hours = default_ttl_hours
        self.persist_to_disk = persist_to_disk
        
        # Cache em memória
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Estatísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0,
            "current_size_bytes": 0,
            "current_entries": 0
        }
        
        # Diretório de cache
        if persist_to_disk:
            self.cache_dir = cache_dir or Path("data/cache/llm_content")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
        
logger.info(f"ContentCache inicializado - Max: {max_size_mb}MB, TTL: {default_ttl_hours}h")
    
    def _generate_key(
        self,
        method: str,
        params: Dict[str, Any],
        content_hash: Optional[str] = None
    ) -> str:
        """
        Gera chave única para cache.
        
        Args:
            method: Nome do método LLM
            params: Parâmetros da chamada
            content_hash: Hash opcional do conteúdo
            
        Returns:
            Chave do cache
        """
        # Criar representação normalizada dos parâmetros
        normalized = {
            "method": method,
            "params": self._normalize_params(params)
        }
        
        # Adicionar hash do conteúdo se fornecido
        if content_hash:
            normalized["content_hash"] = content_hash
        
        # Gerar hash SHA-256
        key_str = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(key_str.encode('utf-8')).hexdigest()[:32]
    
    def _normalize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza parâmetros para geração de chave consistente."""
        normalized = {}
        
        for key, value in params.items():
            # Ignorar parâmetros que não afetam o resultado
            if key in ["request_id", "timeout"]:
                continue
            
            # Tratar listas de forma consistente
            if isinstance(value, list):
                normalized[key] = sorted(value) if all(isinstance(x, str) for x in value) else value
            # Tratar dicionários
            elif isinstance(value, dict):
                normalized[key] = self._normalize_params(value)
            else:
                normalized[key] = value
        
        return normalized
    
    def get(self, method: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        Obtém valor do cache.
        
        Args:
            method: Nome do método LLM
            params: Parâmetros da chamada
            
        Returns:
            Valor em cache ou None
        """
        key = self._generate_key(method, params)
        
        with self._lock:
            self.stats["total_requests"] += 1
            
            if key not in self._cache:
                self.stats["misses"] += 1
                return None
            
            entry = self._cache[key]
            
            # Verificar expiração
            if entry.is_expired():
                del self._cache[key]
                self._update_size()
                self.stats["misses"] += 1
logger.debug(f"Cache entry expired: {key}")
                return None
            
            # Atualizar acesso
            entry.touch()
            self.stats["hits"] += 1
            
logger.debug(f"Cache hit: {method} - {key}")
            return entry.value
    
    def set(
        self,
        method: str,
        params: Dict[str, Any],
        value: Any,
        ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Armazena valor no cache.
        
        Args:
            method: Nome do método LLM
            params: Parâmetros da chamada
            value: Valor a ser armazenado
            ttl_hours: TTL específico (usa padrão se None)
            
        Returns:
            True se armazenado com sucesso
        """
        key = self._generate_key(method, params)
        ttl = ttl_hours or self.default_ttl_hours
        
        # Serializar valor para calcular tamanho
        try:
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value, ensure_ascii=False)
            else:
                serialized = str(value)
            size_bytes = len(serialized.encode('utf-8'))
        except Exception as e:
logger.error(f"Erro ao serializar valor para cache: {e}")
            return False
        
        with self._lock:
            # Verificar se precisa evictar
            while (self._get_current_size() + size_bytes > self.max_size_bytes and 
                   self._cache):
                self._evict_lru()
            
            # Criar entrada
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl_hours=ttl,
                size_bytes=size_bytes
            )
            
            # Armazenar
            self._cache[key] = entry
            self._update_size()
            
            # Persistir se necessário
            if self.persist_to_disk:
                self._save_to_disk_async()
            
logger.debug(f"Cache set: {method} - {key} ({size_bytes} bytes)")
            return True
    
    def _evict_lru(self):
        """Remove entrada menos recentemente usada."""
        if not self._cache:
            return
        
        # Encontrar LRU
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].last_accessed)
        
        del self._cache[lru_key]
        self.stats["evictions"] += 1
logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def _get_current_size(self) -> int:
        """Calcula tamanho atual do cache em bytes."""
        return sum(entry.size_bytes for entry in self._cache.values())
    
    def _update_size(self):
        """Atualiza estatísticas de tamanho."""
        self.stats["current_size_bytes"] = self._get_current_size()
        self.stats["current_entries"] = len(self._cache)
    
    def clear(self, pattern: Optional[str] = None):
        """
        Limpa cache.
        
        Args:
            pattern: Padrão para limpar seletivo (ex: "theme_*")
        """
        with self._lock:
            if pattern:
                # Limpar apenas entradas que combinam com o padrão
                keys_to_remove = [k for k in self._cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self._cache[key]
logger.info(f"Cache cleared for pattern: {pattern} ({len(keys_to_remove)} entries)")
            else:
                # Limpar tudo
                self._cache.clear()
logger.info("Cache cleared completely")
            
            self._update_size()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        with self._lock:
            hit_rate = (
                self.stats["hits"] / max(self.stats["total_requests"], 1) * 100
            )
            
            return {
                **self.stats,
                "hit_rate_percent": round(hit_rate, 2),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "current_size_mb": self.stats["current_size_bytes"] / (1024 * 1024)
            }
    
    def _load_from_disk(self):
        """Carrega cache do disco."""
        cache_file = self.cache_dir / "content_cache.json"
        
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            now = datetime.now()
            loaded = 0
            
            for entry_data in data.get("entries", []):
                # Reconstruir datetime
                created_at = datetime.fromisoformat(entry_data["created_at"])
                last_accessed = datetime.fromisoformat(entry_data["last_accessed"])
                
                # Verificar expiração
                ttl_hours = entry_data["ttl_hours"]
                if now > created_at + timedelta(hours=ttl_hours):
                    continue
                
                # Reconstruir entrada
                entry = CacheEntry(
                    key=entry_data["key"],
                    value=entry_data["value"],
                    created_at=created_at,
                    last_accessed=last_accessed,
                    access_count=entry_data["access_count"],
                    ttl_hours=ttl_hours,
                    size_bytes=entry_data["size_bytes"]
                )
                
                self._cache[entry.key] = entry
                loaded += 1
            
            self._update_size()
logger.info(f"Loaded {loaded} entries from disk cache")
            
        except Exception as e:
logger.error(f"Error loading cache from disk: {e}")
    
    def _save_to_disk_async(self):
        """Salva cache em disco de forma assíncrona."""
        def save():
            self._save_to_disk()
        
        # Executar em thread separada para não bloquear
        thread = threading.Thread(target=save, daemon=True)
        thread.start()
    
    def _save_to_disk(self):
        """Salva cache em disco."""
        if not self.persist_to_disk:
            return
        
        cache_file = self.cache_dir / "content_cache.json"
        temp_file = cache_file.with_suffix(".tmp")
        
        try:
            with self._lock:
                # Preparar dados
                entries = []
                for entry in self._cache.values():
                    entry_dict = asdict(entry)
                    # Converter datetime para ISO
                    entry_dict["created_at"] = entry.created_at.isoformat()
                    entry_dict["last_accessed"] = entry.last_accessed.isoformat()
                    entries.append(entry_dict)
                
                data = {
                    "version": "1.0",
                    "saved_at": datetime.now().isoformat(),
                    "entries": entries
                }
            
            # Escrever em arquivo temporário primeiro
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Renomear para atomizar
            temp_file.rename(cache_file)
logger.debug(f"Saved {len(entries)} entries to disk cache")
            
        except Exception as e:
logger.error(f"Error saving cache to disk: {e}")
            if temp_file.exists():
                temp_file.unlink()
    
    def cleanup_expired(self):
        """Remove entradas expiradas do cache."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                self._update_size()
logger.info(f"Cleaned up {len(expired_keys)} expired entries")
    
    def get_top_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna entradas mais acessadas."""
        with self._lock:
            sorted_entries = sorted(
                self._cache.values(),
                key=lambda e: e.access_count,
                reverse=True
            )[:limit]
            
            return [
                {
                    "key": entry.key[:16] + "...",
                    "access_count": entry.access_count,
                    "created_at": entry.created_at.isoformat(),
                    "size_bytes": entry.size_bytes,
                    "age_hours": (datetime.now() - entry.created_at).total_seconds() / 3600
                }
                for entry in sorted_entries
            ]


# Instância global do cache
_content_cache: Optional[ContentCache] = None


def get_content_cache() -> ContentCache:
    """Retorna instância global do cache."""
    global _content_cache
    if _content_cache is None:
        from src.config.settings import config
        _content_cache = ContentCache(
            max_size_mb=50,  # 50MB padrão
            default_ttl_hours=config.llm_integration.cache_ttl_hours,
            persist_to_disk=config.llm_integration.enable_content_cache,
            cache_dir=config.storage.cache_dir / "llm_content"
        )
    return _content_cache


# Decorador para cache automático
def cached_response(ttl_hours: Optional[int] = None):
    """
    Decorador para cachear automaticamente respostas de métodos LLM.
    
    Args:
        ttl_hours: TTL específico para este método
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Obter nome do método
            method_name = func.__name__
            
            # Construir parâmetros para cache
            cache_params = {
                "args": args[1:],  # Pular self
                "kwargs": kwargs
            }
            
            # Tentar obter do cache
            cache = get_content_cache()
            cached_result = cache.get(method_name, cache_params)
            
            if cached_result is not None:
logger.debug(f"Cache hit for {method_name}")
                return cached_result
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Armazenar no cache
            cache.set(method_name, cache_params, result, ttl_hours)
logger.debug(f"Cached result for {method_name}")
            
            return result
        
        return wrapper
    return decorator