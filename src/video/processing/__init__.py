"""
Processamento de vídeo
Módulo completo de processamento automático e análise de qualidade
"""

from .video_processor import VideoProcessor
from .automatic_video_processor import AutomaticVideoProcessor
from .video_quality_analyzer import VideoQualityAnalyzer, QualityMetrics, PlatformRequirements

__all__ = [
    "VideoProcessor",
    "AutomaticVideoProcessor", 
    "VideoQualityAnalyzer",
    "QualityMetrics",
    "PlatformRequirements"
]