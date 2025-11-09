"""
Video Pre-validator - Sistema de Pré-validação com CLIP
AiShorts v2.0 - Validação de Relevância Antes do Download

Usa CLIP para pré-validar a relevância dos vídeos antes do download,
economizando banda e tempo evitando baixar conteúdo irrelevante.
"""

import asyncio
import logging
import aiohttp
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import requests
import tempfile

logger = logging.getLogger(__name__)

@dataclass
class VideoCandidate:
    """Candidato de vídeo para validação"""
    id: str
    title: str
    description: str
    thumbnail_url: str
    video_url: str
    duration: int
    view_count: int
    upload_date: str
    
    @property
    def relevance_score(self) -> Optional[float]:
        """Score de relevância calculado"""
        return getattr(self, '_relevance_score', None)
    
    @relevance_score.setter
    def relevance_score(self, score: float):
        self._relevance_score = score


class ClipVideoPreValidator:
    """
    Pré-validador de vídeos usando CLIP antes do download.
    
    Features:
    - Scoring de relevância baseado em thumbnail e texto
    - Validação assíncrona paralela
    - Filtros de qualidade e duração
    - Cache de validações
    - Thresholds configuráveis
    """
    
    def __init__(self, 
                 clip_scorer=None,
                 max_concurrent_validations: int = 5,
                 min_relevance_score: float = 0.3,
                 min_duration_seconds: int = 30,
                 max_duration_seconds: int = 300):
        """
        Inicializa o pré-validador.
        
        Args:
            clip_scorer: Instância do CLIP scorer
            max_concurrent_validations: Máximo de validações paralelas
            min_relevance_score: Score mínimo de relevância
            min_duration_seconds: Duração mínima em segundos
            max_duration_seconds: Duração máxima em segundos
        """
        self.clip_scorer = clip_scorer
        self.max_concurrent_validations = max_concurrent_validations
        self.min_relevance_score = min_relevance_score
        self.min_duration_seconds = min_duration_seconds
        self.max_duration_seconds = max_duration_seconds
        
        # Cache de validações (evitar revalidar)
        self.validation_cache = {}
        
        # ThreadPool para processamento CLIP
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        self.logger = logging.getLogger(__name__)
        
        if self.clip_scorer:
self.logger.info(" ClipVideoPreValidator inicializado com CLIP scoring")
        else:
self.logger.warning(" ClipVideoPreValidator inicializado sem CLIP (fallback)")
    
    def _generate_validation_key(self, candidate: VideoCandidate, query: str) -> str:
        """Gera chave única para cache de validação"""
        import hashlib
        content = f"{candidate.id}_{query}_{candidate.duration}_{candidate.view_count}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _filter_by_basic_criteria(self, candidate: VideoCandidate) -> bool:
        """Filtra candidatos por critérios básicos (duração, views, etc.)"""
        
        # Verificar duração
        if candidate.duration < self.min_duration_seconds:
self.logger.debug(f"⏰ Vídeo muito curto: {candidate.duration}s < {self.min_duration_seconds}s")
            return False
        
        if candidate.duration > self.max_duration_seconds:
self.logger.debug(f"⏰ Vídeo muito longo: {candidate.duration}s > {self.max_duration_seconds}s")
            return False
        
        # Verificar conteúdo básico
        if not candidate.title or len(candidate.title.strip()) < 5:
self.logger.debug(" Título muito curto ou vazio")
            return False
        
        # Verificar se não é live ou playlist
        forbidden_keywords = ['live', 'stream', 'playlist', '#shorts', '#short']
        title_lower = candidate.title.lower()
        
        for keyword in forbidden_keywords:
            if keyword in title_lower:
self.logger.debug(f" Conteúdo não permitido: '{keyword}' no título")
                return False
        
        return True
    
    def _download_thumbnail_sync(self, thumbnail_url: str) -> Optional[np.ndarray]:
        """Download síncrono de thumbnail (compatibilidade)"""
        try:
            response = requests.get(thumbnail_url, timeout=10)
            response.raise_for_status()
            
            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            # Carregar como imagem
            image = Image.open(tmp_path).convert('RGB')
            
            # Redimensionar para CLIP (224x224)
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            
            # Converter para numpy
            return np.array(image)
            
        except Exception as e:
self.logger.warning(f" Erro no download do thumbnail: {e}")
            return None
        finally:
            # Limpar arquivo temporário
            try:
                import os
                if 'tmp_path' in locals():
                    os.unlink(tmp_path)
            except:
                pass
    
    def _validate_candidate_sync(self, candidate: VideoCandidate, query: str) -> float:
        """
        Validação síncrona de um candidato usando CLIP.
        
        Args:
            candidate: Candidato de vídeo
            query: Query de busca
            
        Returns:
            Score de relevância (0.0 - 1.0)
        """
        if not self.clip_scorer:
            # Fallback simples baseado em keywords
            return self._fallback_scoring(candidate, query)
        
        try:
            # Download do thumbnail
            thumbnail = self._download_thumbnail_sync(candidate.thumbnail_url)
            if thumbnail is None:
self.logger.warning(f" Falha no download do thumbnail para {candidate.id}")
                return 0.0
            
            # Preparar texto para CLIP (título + descrição)
            text_content = f"{candidate.title}. {candidate.description or ''}"
            
            # Calcular score usando CLIP
            score = self.clip_scorer._score_with_clip(text_content, thumbnail)
            
self.logger.debug(f" CLIP score para {candidate.id}: {score:.3f}")
            return float(score)
            
        except Exception as e:
self.logger.error(f" Erro na validação CLIP de {candidate.id}: {e}")
            return self._fallback_scoring(candidate, query)
    
    def _fallback_scoring(self, candidate: VideoCandidate, query: str) -> float:
        """
        Scoring de fallback baseado em keywords quando CLIP não disponível.
        
        Args:
            candidate: Candidato de vídeo
            query: Query de busca
            
        Returns:
            Score de relevância (0.0 - 1.0)
        """
        query_words = set(query.lower().split())
        title_words = set(candidate.title.lower().split())
        desc_words = set(candidate.description.lower().split()) if candidate.description else set()
        
        # Calcular Jaccard similarity
        title_intersection = len(query_words & title_words)
        title_union = len(query_words | title_words)
        title_score = title_intersection / title_union if title_union > 0 else 0
        
        desc_intersection = len(query_words & desc_words)
        desc_union = len(query_words | desc_words)
        desc_score = desc_intersection / desc_union if desc_union > 0 else 0
        
        # Combinar scores (título mais importante)
        combined_score = (title_score * 0.7 + desc_score * 0.3)
        
        # Ajustar baseado em views (popularidade)
        view_boost = min(candidate.view_count / 1000000, 0.2)  # Max 0.2 boost
        
        final_score = min(combined_score + view_boost, 1.0)
        
self.logger.debug(f" Fallback score para {candidate.id}: {final_score:.3f}")
        return final_score
    
    def validate_candidates(self, 
                          candidates: List[VideoCandidate], 
                          query: str,
                          max_results: int = 5) -> List[VideoCandidate]:
        """
        Valida múltiplos candidatos e retorna os mais relevantes.
        
        Args:
            candidates: Lista de candidatos
            query: Query de busca original
            max_results: Máximo de resultados a retornar
            
        Returns:
            Lista de candidatos validados e ordenados por relevância
        """
self.logger.info(f" Validando {len(candidates)} candidatos para query: '{query}'")
        
        # Filtrar por critérios básicos
        filtered_candidates = []
        for candidate in candidates:
            if self._filter_by_basic_criteria(candidate):
                # Verificar cache
                cache_key = self._generate_validation_key(candidate, query)
                if cache_key in self.validation_cache:
                    candidate.relevance_score = self.validation_cache[cache_key]
self.logger.debug(f" Score do cache: {candidate.relevance_score:.3f}")
                else:
                    # Validar usando CLIP
                    score = self._validate_candidate_sync(candidate, query)
                    candidate.relevance_score = score
                    self.validation_cache[cache_key] = score
                
                filtered_candidates.append(candidate)
        
self.logger.info(f" {len(filtered_candidates)} candidatos passaram filtros básicos")
        
        # Filtrar por relevância mínima
        relevant_candidates = [
            c for c in filtered_candidates 
            if c.relevance_score and c.relevance_score >= self.min_relevance_score
        ]
        
self.logger.info(f" {len(relevant_candidates)} candidatos com relevância >= {self.min_relevance_score}")
        
        # Ordenar por relevância e retornar top N
        sorted_candidates = sorted(
            relevant_candidates,
            key=lambda x: x.relevance_score or 0,
            reverse=True
        )[:max_results]
        
self.logger.info(f" Retornando {len(sorted_candidates)} candidatos mais relevantes")
        
        for i, candidate in enumerate(sorted_candidates, 1):
self.logger.info(f"   {i}. {candidate.title[:60]}... (score: {candidate.relevance_score:.3f})")
        
        return sorted_candidates
    
    async def validate_candidates_async(self, 
                                     candidates: List[VideoCandidate], 
                                     query: str,
                                     max_results: int = 5) -> List[VideoCandidate]:
        """
        Validação assíncrona de candidatos para melhor performance.
        
        Args:
            candidates: Lista de candidatos
            query: Query de busca
            max_results: Máximo de resultados
            
        Returns:
            Lista de candidatos validados
        """
self.logger.info(f" Iniciando validação assíncrona de {len(candidates)} candidatos")
        
        # Filtro básico síncrono (rápido)
        filtered_candidates = [
            c for c in candidates 
            if self._filter_by_basic_criteria(c)
        ]
        
        if not self.clip_scorer:
            # Sem CLIP, usar método síncrono
            return self.validate_candidates(candidates, query, max_results)
        
        # Validação CLIP assíncrona
        async def validate_single(candidate: VideoCandidate) -> VideoCandidate:
            loop = asyncio.get_event_loop()
            
            # Verificar cache
            cache_key = self._generate_validation_key(candidate, query)
            if cache_key in self.validation_cache:
                candidate.relevance_score = self.validation_cache[cache_key]
                return candidate
            
            # Validar em thread separada
            score = await loop.run_in_executor(
                self.executor, 
                self._validate_candidate_sync, 
                candidate, 
                query
            )
            
            candidate.relevance_score = score
            self.validation_cache[cache_key] = score
            return candidate
        
        # Processar em lote (limitar concorrência)
        semaphore = asyncio.Semaphore(self.max_concurrent_validations)
        
        async def validate_with_semaphore(candidate):
            async with semaphore:
                return await validate_single(candidate)
        
        # Executar validações em paralelo
        validated_candidates = await asyncio.gather(
            *[validate_with_semaphore(c) for c in filtered_candidates],
            return_exceptions=True
        )
        
        # Filtrar exceções e candidatos válidos
        valid_candidates = []
        for result in validated_candidates:
            if isinstance(result, Exception):
self.logger.warning(f" Erro na validação assíncrona: {result}")
                continue
            
            if result.relevance_score and result.relevance_score >= self.min_relevance_score:
                valid_candidates.append(result)
        
        # Ordenar e retornar top N
        sorted_candidates = sorted(
            valid_candidates,
            key=lambda x: x.relevance_score or 0,
            reverse=True
        )[:max_results]
        
self.logger.info(f" Validação assíncrona concluída: {len(sorted_candidates)} válidos")
        
        return sorted_candidates
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de validação"""
        return {
            'cache_size': len(self.validation_cache),
            'min_relevance_score': self.min_relevance_score,
            'clip_available': self.clip_scorer is not None,
            'duration_limits': {
                'min_seconds': self.min_duration_seconds,
                'max_seconds': self.max_duration_seconds
            },
            'concurrent_validations': self.max_concurrent_validations
        }
    
    def clear_cache(self):
        """Limpa cache de validações"""
        cache_size = len(self.validation_cache)
        self.validation_cache.clear()
self.logger.info(f" Cache de validações limpo: {cache_size} entradas removidas")
    
    def update_settings(self, 
                        min_relevance_score: Optional[float] = None,
                        min_duration_seconds: Optional[int] = None,
                        max_duration_seconds: Optional[int] = None):
        """Atualiza configurações de validação"""
        if min_relevance_score is not None:
            self.min_relevance_score = min_relevance_score
self.logger.info(f" Min relevance score atualizado: {min_relevance_score}")
        
        if min_duration_seconds is not None:
            self.min_duration_seconds = min_duration_seconds
self.logger.info(f" Min duration atualizado: {min_duration_seconds}s")
        
        if max_duration_seconds is not None:
            self.max_duration_seconds = max_duration_seconds
self.logger.info(f" Max duration atualizado: {max_duration_seconds}s")


# Instância global
video_pre_validator = None


def get_video_pre_validator(clip_scorer=None) -> ClipVideoPreValidator:
    """Retorna instância global do pré-validador"""
    global video_pre_validator
    if video_pre_validator is None:
        video_pre_validator = ClipVideoPreValidator(clip_scorer=clip_scorer)
    return video_pre_validator