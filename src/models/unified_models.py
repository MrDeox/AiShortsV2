"""
Unified Models para AiShorts v2.0 - Modelo Centralizado
Este arquivo consolida e unifica todos os modelos de dados duplicados.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


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
    """Representa um tema gerado com metadados - Modelo Unificado."""
    content: str  # Nome principal do conteúdo
    category: ThemeCategory
    quality_score: float = 0.0
    response_time: float = 0.0
    timestamp: Optional[datetime] = None
    usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    # Campos adicionais do script_models para compatibilidade
    keywords: List[str] = field(default_factory=list)
    target_audience: str = "general"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    # Compatibilidade com ambos os sistemas
    @property
    def main_title(self) -> str:
        """Alias para compatibilidade com TTS."""
        return self.content
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return {
            "content": self.content,
            "main_title": self.content,  # Compatibilidade
            "category": self.category.value,
            "quality_score": self.quality_score,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "usage": self.usage,
            "metrics": self.metrics,
            "keywords": self.keywords,
            "target_audience": self.target_audience
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedTheme':
        """Cria instância a partir de dicionário."""
        # Suporte a ambos os formatos: content e main_title
        content = data.get("content") or data.get("main_title", "")
        
        return cls(
            content=content,
            category=ThemeCategory(data["category"]),
            quality_score=data.get("quality_score", 0.0),
            response_time=data.get("response_time", 0.0),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            usage=data.get("usage"),
            metrics=data.get("metrics"),
            keywords=data.get("keywords", []),
            target_audience=data.get("target_audience", "general")
        )


@dataclass
class ScriptSection:
    """Representa uma seção do roteiro - Modelo Unificado."""
    # Unificar campos: name e type
    name: str  # 'hook', 'development', 'conclusion'
    content: str
    duration_seconds: float = 0.0
    purpose: str = ""
    key_elements: List[str] = field(default_factory=list)
    
    # Compatibilidade com script_models (usava 'type')
    @property
    def type(self) -> str:
        """Alias para compatibilidade com script_models."""
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "name": self.name,
            "type": self.name,  # Compatibilidade
            "content": self.content,
            "duration_seconds": self.duration_seconds,
            "purpose": self.purpose,
            "key_elements": self.key_elements
        }


@dataclass
class GeneratedScript:
    """Representa um roteiro completo gerado - Modelo Unificado."""
    title: str
    theme: GeneratedTheme
    sections: List[ScriptSection]
    total_duration: float = 0.0
    quality_score: float = 0.0
    engagement_score: float = 0.0
    retention_score: float = 0.0
    response_time: float = 0.0
    timestamp: Optional[datetime] = None
    usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    # Campo adicional do script_models para compatibilidade
    platform: str = "tiktok"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    # Métodos de conveniência para acesso às seções
    @property
    def hook(self) -> Optional[ScriptSection]:
        """Retorna a seção de hook."""
        return next((s for s in self.sections if s.name == "hook"), None)
    
    @property
    def development(self) -> Optional[ScriptSection]:
        """Retorna a seção de desenvolvimento."""
        return next((s for s in self.sections if s.name == "development"), None)
    
    @property
    def conclusion(self) -> Optional[ScriptSection]:
        """Retorna a seção de conclusão."""
        return next((s for s in self.sections if s.name == "conclusion"), None)
    
    # Métodos utilitários
    def get_hook_preview(self, max_chars: int = 100) -> str:
        """Retorna preview do hook."""
        if self.hook and self.hook.content:
            content = self.hook.content[:max_chars]
            return content + "..." if len(self.hook.content) > max_chars else content
        return ""
    
    def get_script_text(self) -> str:
        """Retorna texto completo do roteiro."""
        return " ".join([section.content for section in self.sections if section.content])
    
    def get_full_text(self) -> str:
        """Alias para compatibilidade."""
        return self.get_script_text()
    
    def get_section_by_type(self, section_type: str) -> Optional[ScriptSection]:
        """Retorna seção por tipo."""
        for section in self.sections:
            if section.name == section_type or section.type == section_type:
                return section
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "title": self.title,
            "theme": self.theme.to_dict() if self.theme else None,
            "sections": [section.to_dict() for section in self.sections],
            "total_duration": self.total_duration,
            "quality_score": self.quality_score,
            "engagement_score": self.engagement_score,
            "retention_score": self.retention_score,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "usage": self.usage,
            "metrics": self.metrics,
            "platform": self.platform
        }
    
    def save_to_file(self, filepath: Path) -> None:
        """Salva roteiro em arquivo JSON."""
        data = self.to_dict()
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedScript':
        """Cria instância a partir de dicionário."""
        theme_data = data.get("theme")
        theme = GeneratedTheme.from_dict(theme_data) if theme_data else None
        
        sections = []
        for section_data in data.get("sections", []):
            sections.append(ScriptSection(
                name=section_data.get("name") or section_data.get("type", ""),
                content=section_data.get("content", ""),
                duration_seconds=section_data.get("duration_seconds", 0.0),
                purpose=section_data.get("purpose", ""),
                key_elements=section_data.get("key_elements", [])
            ))
        
        return cls(
            title=data.get("title", ""),
            theme=theme,
            sections=sections,
            total_duration=data.get("total_duration", 0.0),
            quality_score=data.get("quality_score", 0.0),
            engagement_score=data.get("engagement_score", 0.0),
            retention_score=data.get("retention_score", 0.0),
            response_time=data.get("response_time", 0.0),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            usage=data.get("usage"),
            metrics=data.get("metrics"),
            platform=data.get("platform", "tiktok")
        )


@dataclass
class ScriptGenerationResult:
    """Resultado da geração de múltiplos roteiros."""
    scripts: List[GeneratedScript]
    best_script: Optional[GeneratedScript] = None
    total_time: float = 0.0
    generation_stats: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "scripts": [script.to_dict() for script in self.scripts],
            "best_script": self.best_script.to_dict() if self.best_script else None,
            "total_time": self.total_time,
            "generation_stats": self.generation_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_to_file(self, filepath: Path) -> None:
        """Salva resultado em arquivo JSON."""
        data = self.to_dict()
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# Funções de migração para compatibilidade
def migrate_from_script_models(old_theme_data: Dict[str, Any]) -> GeneratedTheme:
    """Migra dados do formato script_models para o formato unificado."""
    return GeneratedTheme.from_dict(old_theme_data)


def migrate_from_script_generator(old_script_data: Dict[str, Any]) -> GeneratedScript:
    """Migra dados do formato script_generator para o formato unificado."""
    return GeneratedScript.from_dict(old_script_data)


# Verificação de integridade dos modelos
def validate_model_consistency() -> Dict[str, Any]:
    """Valida se todos os modelos estão consistentes."""
    return {
        "status": "valid",
        "models": ["GeneratedTheme", "ScriptSection", "GeneratedScript", "ScriptGenerationResult"],
        "unified_at": datetime.now().isoformat(),
        "compatibility_layers": ["main_title <=> content", "type <=> name"]
    }


# Modelos para resultados do pipeline
@dataclass
class TTSAudioResult:
    """Resultado da síntese de áudio TTS."""
    success: bool
    audio_path: str
    duration: float
    voice: Optional[str] = None
    lang_code: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "audio_path": self.audio_path,
            "duration": self.duration,
            "voice": self.voice,
            "lang_code": self.lang_code,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class BrollMatchResult:
    """Resultado da busca e matching de B-roll."""
    success: bool
    videos: List[str]
    queries_used: List[str]
    keywords: List[str]
    validation_pipeline: Dict[str, Any]
    total_candidates: int = 0
    download_count: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "videos": self.videos,
            "queries_used": self.queries_used,
            "keywords": self.keywords,
            "validation_pipeline": self.validation_pipeline,
            "total_candidates": self.total_candidates,
            "download_count": self.download_count,
            "error": self.error
        }


@dataclass
class VideoSyncPlan:
    """Plano de sincronização áudio-vídeo."""
    success: bool
    audio_path: str
    video_paths: List[str]
    sync_method: str
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    sync_points: List[Dict[str, Any]] = field(default_factory=list)
    optimized_segments: List[Dict[str, Any]] = field(default_factory=list)
    transition_effects: List[Dict[str, Any]] = field(default_factory=list)
    sync_precision: float = 0.0
    total_synced_duration: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "audio_path": self.audio_path,
            "video_paths": self.video_paths,
            "sync_method": self.sync_method,
            "timeline": self.timeline,
            "sync_points": self.sync_points,
            "optimized_segments": self.optimized_segments,
            "transition_effects": self.transition_effects,
            "sync_precision": self.sync_precision,
            "total_synced_duration": self.total_synced_duration,
            "error": self.error
        }


@dataclass
class PipelineResult:
    """Resultado completo do pipeline."""
    status: str  # 'success' ou 'failed'
    theme: Dict[str, Any]
    script: Dict[str, Any]
    audio: Optional[TTSAudioResult] = None
    captions: List[Dict[str, Any]] = field(default_factory=list)
    broll: Optional[BrollMatchResult] = None
    analysis: Optional[Dict[str, Any]] = None
    sync: Optional[VideoSyncPlan] = None
    final: Optional[Dict[str, Any]] = None
    total_time: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "status": self.status,
            "theme": self.theme,
            "script": self.script,
            "captions": self.captions,
            "total_time": self.total_time
        }
        
        if self.audio:
            result["audio"] = self.audio.to_dict()
        if self.broll:
            result["broll"] = self.broll.to_dict()
        if self.sync:
            result["sync"] = self.sync.to_dict()
        if self.analysis:
            result["analysis"] = self.analysis
        if self.final:
            result["final"] = self.final
        if self.error:
            result["error"] = self.error
            
        return result


@dataclass
class TranslationResult:
    """Resultado da tradução do script."""
    success: bool
    translated_text: str
    response_time: float = 0.0
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "translated_text": self.translated_text,
            "response_time": self.response_time,
            "usage": self.usage,
            "error": self.error
        }


if __name__ == "__main__":
    # Teste dos modelos unificados
print("=== Teste dos Modelos Unificados ===")
    
    # Criar tema de exemplo
    theme = GeneratedTheme(
        content="Animais incríveis da Amazônia",
        category=ThemeCategory.ANIMALS,
        quality_score=0.85,
        keywords=["animais", "amazônia", "biodiversidade"],
        target_audience="geral"
    )
    
print(f"Tema: {theme.content}")
print(f"Main Title (alias): {theme.main_title}")
print(f"Categoria: {theme.category.value}")
    
    # Criar seções
    sections = [
        ScriptSection(
            name="hook",
            content="Você sabia que a Amazônia abriga 10% de todas as espécies do planeta?",
            duration_seconds=5.0,
            purpose="capturar atenção"
        ),
        ScriptSection(
            name="development", 
            content="A floresta amazônica é o lar de mais de 40.000 espécies de plantas, 3.000 espécies de peixes e 1.300 espécies de aves.",
            duration_seconds=45.0,
            purpose="informar"
        ),
        ScriptSection(
            name="conclusion",
            content="Proteger a Amazônia é proteger a maior reserva de biodiversidade do mundo. Compartilhe esse fato!",
            duration_seconds=10.0,
            purpose="chamada à ação"
        )
    ]
    
    # Criar script completo
    script = GeneratedScript(
        title="Animais Incríveis da Amazônia",
        theme=theme,
        sections=sections,
        total_duration=60.0,
        quality_score=0.88,
        engagement_score=0.75,
        retention_score=0.82
    )
    
print(f"\nScript: {script.title}")
print(f"Duração: {script.total_duration}s")
print(f"Hook: {script.hook.content if script.hook else 'N/A'}")
print(f"Texto completo: {script.get_script_text()[:100]}...")
    
    # Testar serialização
    script_dict = script.to_dict()
print(f"\nSerialização bem-sucedida: {len(script_dict)} campos")
    
    # Testar desserialização
    script_restored = GeneratedScript.from_dict(script_dict)
print(f"Desserialização bem-sucedida: {script_restored.title}")
    
    # Validação de consistência
    validation = validate_model_consistency()
print(f"\nValidação: {validation['status']}")
print(f"Modelos disponíveis: {', '.join(validation['models'])}")
    
print("\n Todos os modelos unificados funcionando corretamente!")