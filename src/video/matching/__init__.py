"""
Módulo de matching entre roteiro e vídeo.
Implementa análise semântica e busca inteligente de conteúdo.
"""

from .semantic_analyzer import SemanticAnalyzer
from .video_searcher import VideoSearcher, VideoInfo

__all__ = [
    'SemanticAnalyzer',
    'VideoSearcher', 
    'VideoInfo'
]