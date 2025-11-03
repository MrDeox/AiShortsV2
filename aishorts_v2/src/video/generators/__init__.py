"""
Módulo de geração de templates visuais para vídeo curto.

Contém templates organizados por categoria (SPACE, ANIMALS, SCIENCE, etc.)
com sobreposições de texto e efeitos de transição.
"""

from .visual_templates import (
    VisualTemplate, VisualTemplateGenerator, TextOverlay, TemplateType, TextStyle,
    template_generator, get_template, generate_text_overlay
)

__all__ = [
    "VisualTemplate",
    "VisualTemplateGenerator", 
    "TextOverlay",
    "TemplateType",
    "TextStyle",
    "template_generator",
    "get_template",
    "generate_text_overlay"
]