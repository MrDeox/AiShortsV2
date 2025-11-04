"""
Módulo de processamento de vídeo para otimização por plataforma.

Contém ferramentas para ajustar vídeos para TikTok, YouTube Shorts e Instagram Reels.
"""

from .platform_optimizer import PlatformOptimizer, VideoProcessingError

__all__ = ["PlatformOptimizer", "VideoProcessingError"]