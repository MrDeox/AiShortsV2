"""
Models para AiShorts v2.0 - Compatibilidade com Módulo TTS
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class ThemeCategory(Enum):
    """Categorias de temas disponíveis."""
    SCIENCE = "science"
    HISTORY = "history" 
    NATURE = "nature"
    TECHNOLOGY = "technology"
    CULTURE = "culture"
    SPACE = "space"
    ANIMALS = "animals"
    PSYCHOLOGY = "psychology"
    GEOGRAPHY = "geography"
    FOOD = "food"


@dataclass
class GeneratedTheme:
    """Representa um tema gerado com metadados."""
    main_title: str  # Mudança para compatibilidade com TTS
    category: ThemeCategory
    keywords: List[str]
    target_audience: str
    quality_score: float = 0.0
    response_time: float = 0.0
    timestamp: Optional[datetime] = None
    usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return {
            "main_title": self.main_title,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "keywords": self.keywords,
            "target_audience": self.target_audience,
            "quality_score": self.quality_score,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "usage": self.usage,
            "metrics": self.metrics
        }


@dataclass  
class ScriptSection:
    """Representa uma seção do roteiro."""
    type: str  # 'hook', 'development', 'conclusion'
    content: str
    duration_seconds: float = 0.0
    purpose: str = ""
    key_elements: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "type": self.type,
            "content": self.content,
            "duration_seconds": self.duration_seconds,
            "purpose": self.purpose,
            "key_elements": self.key_elements or []
        }


@dataclass
class Script:
    """Representa um roteiro completo gerado."""
    id: str
    theme: GeneratedTheme
    sections: List[ScriptSection]
    total_duration: float = 0.0
    quality_score: float = 0.0
    platform: str = "tiktok"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "theme": self.theme.to_dict() if self.theme else None,
            "sections": [section.to_dict() for section in self.sections],
            "total_duration": self.total_duration,
            "quality_score": self.quality_score,
            "platform": self.platform
        }
    
    def get_full_text(self) -> str:
        """Retorna o texto completo do roteiro."""
        return " ".join(section.content for section in self.sections if section.content)
    
    def get_section_by_type(self, section_type: str) -> Optional[ScriptSection]:
        """Retorna seção por tipo."""
        for section in self.sections:
            if section.type == section_type:
                return section
        return None