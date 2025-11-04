# -*- coding: utf-8 -*-
"""
Módulo de processamento e geração de vídeo para AiShorts v2.0

Contém ferramentas para:
- Extração e processamento de vídeos do YouTube
- Otimização de vídeo por plataforma 
- Geração de templates visuais
"""

# Sistema de extração do YouTube
from .extractors.youtube_extractor import YouTubeExtractor
from .extractors.segment_processor import SegmentProcessor

# Imports existentes (mantém compatibilidade)
try:
    from . import matching
except ImportError:
    matching = None

try:
    from .processing.platform_optimizer import PlatformOptimizer, VideoProcessingError
except ImportError:
    PlatformOptimizer = None
    VideoProcessingError = None

try:
    from .generators.visual_templates import (
        VisualTemplate, VisualTemplateGenerator, TextOverlay, TemplateType, TextStyle,
        template_generator
    )
except ImportError:
    VisualTemplate = None
    VisualTemplateGenerator = None
    TextOverlay = None
    TemplateType = None
    TextStyle = None
    template_generator = None

__all__ = [
    # Sistema de extração YouTube
    "YouTubeExtractor", 
    "SegmentProcessor",
    
    # Imports existentes (se disponíveis)
    "matching",
    "PlatformOptimizer",
    "VideoProcessingError", 
    "VisualTemplate",
    "VisualTemplateGenerator",
    "TextOverlay",
    "TemplateType",
    "TextStyle",
    "template_generator"
]