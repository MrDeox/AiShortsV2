# -*- coding: utf-8 -*-
"""
Módulo de extratores de vídeo.
"""

from .youtube_extractor import YouTubeExtractor
from .segment_processor import SegmentProcessor

__all__ = ["YouTubeExtractor", "SegmentProcessor"]