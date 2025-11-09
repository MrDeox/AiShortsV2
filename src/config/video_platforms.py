"""
Configurações específicas para plataformas de vídeo (TikTok, YouTube Shorts, Instagram Reels)

Baseado na pesquisa de requisitos técnicos e melhores práticas visuais para 2025.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import os

class VideoFormat(Enum):
    """Formatos de vídeo suportados."""
    MP4 = "mp4"
    MOV = "mov"

class VideoCodec(Enum):
    """Codecs de vídeo suportados."""
    H264 = "h264"

class AudioCodec(Enum):
    """Codecs de áudio suportados."""
    AAC = "aac"
    MP3 = "mp3"

class Platform(Enum):
    """Plataformas suportadas."""
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"

@dataclass
class VideoSpecs:
    """Especificações técnicas de vídeo para uma plataforma."""
    name: str
    aspect_ratio: str
    resolution: Tuple[int, int]
    duration_min: int
    duration_max: int
    fps: int
    format: VideoFormat
    video_codec: VideoCodec
    audio_codec: AudioCodec
    file_size_max_mb: int
    bitrate_kbps: int = None
    thumbnail_required: bool = False
    has_safe_area: bool = True
    
    @property
    def resolution_str(self) -> str:
        """Retorna resolução como string."""
        return f"{self.resolution[0]}x{self.resolution[1]}"
    
    def validate_duration(self, duration_seconds: float) -> bool:
        """Valida se a duração está dentro dos limites da plataforma."""
        return self.duration_min <= duration_seconds <= self.duration_max

@dataclass
class QualityPreset:
    """Preset de qualidade de exportação."""
    name: str
    bitrate_kbps: int
    quality_level: str
    compression_ratio: float
    use_case: str

class VideoPlatformConfig:
    """Configurações para plataformas de vídeo."""
    
    def __init__(self):
        self.platforms = self._init_platform_configs()
        self.quality_presets = self._init_quality_presets()
        self.safe_zones = self._init_safe_zones()
    
    def _init_platform_configs(self) -> Dict[Platform, VideoSpecs]:
        """Inicializa configurações específicas para cada plataforma."""
        
        # TikTok
        tiktok = VideoSpecs(
            name="TikTok",
            aspect_ratio="9:16",
            resolution=(1080, 1920),
            duration_min=1,
            duration_max=600,  # 10 minutos
            fps=30,
            format=VideoFormat.MP4,
            video_codec=VideoCodec.H264,
            audio_codec=AudioCodec.AAC,
            file_size_max_mb=500,
            bitrate_kbps=3000,
            thumbnail_required=False,
            has_safe_area=True
        )
        
        # YouTube Shorts
        youtube_shorts = VideoSpecs(
            name="YouTube Shorts",
            aspect_ratio="9:16",
            resolution=(1080, 1920),
            duration_min=15,
            duration_max=60,
            fps=30,
            format=VideoFormat.MP4,
            video_codec=VideoCodec.H264,
            audio_codec=AudioCodec.AAC,
            file_size_max_mb=1000,  # Estimativa conservadora
            bitrate_kbps=2500,
            thumbnail_required=True,
            has_safe_area=True
        )
        
        # Instagram Reels
        instagram_reels = VideoSpecs(
            name="Instagram Reels",
            aspect_ratio="9:16",
            resolution=(1080, 1920),
            duration_min=1,
            duration_max=90,
            fps=30,
            format=VideoFormat.MP4,
            video_codec=VideoCodec.H264,
            audio_codec=AudioCodec.AAC,
            file_size_max_mb=4000,  # 4 GB
            bitrate_kbps=3500,
            thumbnail_required=True,
            has_safe_area=True
        )
        
        return {
            Platform.TIKTOK: tiktok,
            Platform.YOUTUBE_SHORTS: youtube_shorts,
            Platform.INSTAGRAM_REELS: instagram_reels
        }
    
    def _init_quality_presets(self) -> List[QualityPreset]:
        """Inicializa presets de qualidade."""
        return [
            QualityPreset(
                name="Baixa",
                bitrate_kbps=1500,
                quality_level="baixa",
                compression_ratio=0.6,
                use_case="Teste rápido, tamanho pequeno"
            ),
            QualityPreset(
                name="Média",
                bitrate_kbps=3000,
                quality_level="média",
                compression_ratio=0.8,
                use_case="Padrão para redes sociais"
            ),
            QualityPreset(
                name="Alta",
                bitrate_kbps=5000,
                quality_level="alta",
                compression_ratio=0.9,
                use_case="Máxima qualidade"
            ),
            QualityPreset(
                name="Otimizada",
                bitrate_kbps=2500,
                quality_level="otimizada",
                compression_ratio=0.7,
                use_case="Equilíbrio entre qualidade e tamanho"
            )
        ]
    
    def _init_safe_zones(self) -> Dict[Platform, Dict[str, Any]]:
        """Define zonas seguras para cada plataforma."""
        return {
            Platform.TIKTOK: {
                "top_margin_pct": 10,
                "bottom_margin_pct": 15,
                "side_margin_pct": 5,
                "avoid_ui_overlay": True,
                "recommended_text_position": "centro_superior"
            },
            Platform.YOUTUBE_SHORTS: {
                "top_margin_pct": 8,
                "bottom_margin_pct": 12,
                "side_margin_pct": 5,
                "avoid_ui_overlay": True,
                "recommended_text_position": "centro"
            },
            Platform.INSTAGRAM_REELS: {
                "top_margin_pct": 12,
                "bottom_margin_pct": 18,
                "side_margin_pct": 8,
                "avoid_ui_overlay": True,
                "recommended_text_position": "centro_inferior"
            }
        }
    
    def get_platform_specs(self, platform: Platform) -> VideoSpecs:
        """Obtém especificações de uma plataforma."""
        return self.platforms[platform]
    
    def get_quality_preset(self, quality_name: str) -> QualityPreset:
        """Obtém preset de qualidade."""
        for preset in self.quality_presets:
            if preset.name.lower() == quality_name.lower():
                return preset
        return self.quality_presets[1]  # Padrão "Média"
    
    def get_safe_zone(self, platform: Platform) -> Dict[str, Any]:
        """Obtém configurações de zona segura."""
        return self.safe_zones[platform]
    
    def get_platform_config(self, platform: Platform) -> Dict[str, Any]:
        """Obtém configuração completa de uma plataforma."""
        specs = self.get_platform_specs(platform)
        safe_zone = self.get_safe_zone(platform)
        
        return {
            "specifications": specs,
            "safe_zone": safe_zone,
            "export_settings": self._get_export_settings(platform, specs)
        }
    
    def _get_export_settings(self, platform: Platform, specs: VideoSpecs) -> Dict[str, Any]:
        """Gera configurações de exportação."""
        return {
            "container": specs.format.value,
            "video_codec": specs.video_codec.value,
            "audio_codec": specs.audio_codec.value,
            "resolution": specs.resolution_str,
            "fps": specs.fps,
            "bitrate": f"{specs.bitrate_kbps}k",
            "aspect_ratio": specs.aspect_ratio,
            "target_duration": specs.duration_max
        }
    
    def validate_video_for_platform(self, video_path: str, platform: Platform) -> Dict[str, Any]:
        """Valida se um vídeo atende aos requisitos da plataforma."""
        from pathlib import Path
        
        specs = self.get_platform_specs(platform)
        file_path = Path(video_path)
        
        # Verificações básicas
        checks = {
            "file_exists": file_path.exists(),
            "extension_supported": file_path.suffix.lower()[1:] in [f.value for f in VideoFormat],
            "file_size_ok": file_path.stat().st_size <= specs.file_size_max_mb * 1024 * 1024,
        }
        
        # Pontuação de validação
        total_checks = len(checks)
        passed_checks = sum(checks.values())
        score = (passed_checks / total_checks) * 100
        
        return {
            "valid": all(checks.values()),
            "score": score,
            "checks": checks,
            "recommendations": self._get_recommendations(platform, checks)
        }
    
    def _get_recommendations(self, platform: Platform, checks: Dict[str, bool]) -> List[str]:
        """Gera recomendações baseado nos checks."""
        recommendations = []
        
        if not checks.get("file_exists"):
            recommendations.append("Arquivo de vídeo não encontrado")
        
        if not checks.get("extension_supported"):
            recommendations.append("Formato de arquivo não suportado. Use MP4 ou MOV")
        
        if not checks.get("file_size_ok"):
            recommendations.append("Arquivo muito grande. Reduza a qualidade ou duração")
        
        if not recommendations:
            recommendations.append("Vídeo atende aos requisitos básicos da plataforma")
        
        return recommendations

# Instância global de configuração
video_config = VideoPlatformConfig()

# Configurações específicas por categoria de conteúdo
CONTENT_CATEGORY_CONFIGS = {
    "SPACE": {
        "transition_effects": ["fade", "slide", "zoom"],
        "text_overlay_style": "modern_sans",
        "color_palette": ["#000428", "#004e92", "#ffffff"],
        "timing_preset": "educational"
    },
    "ANIMALS": {
        "transition_effects": ["cut", "fade", "morph"],
        "text_overlay_style": "playful",
        "color_palette": ["#ff6b6b", "#4ecdc4", "#45b7d1"],
        "timing_preset": "storytelling"
    },
    "SCIENCE": {
        "transition_effects": ["dissolve", "wipe", "slide"],
        "text_overlay_style": "scientific",
        "color_palette": ["#2c3e50", "#3498db", "#ecf0f1"],
        "timing_preset": "informative"
    },
    "HISTORY": {
        "transition_effects": ["sepia", "fade", "slide"],
        "text_overlay_style": "elegant",
        "color_palette": ["#8B4513", "#D2B48C", "#F5F5DC"],
        "timing_preset": "narrative"
    },
    "NATURE": {
        "transition_effects": ["fade", "dissolve", "slide"],
        "text_overlay_style": "organic",
        "color_palette": ["#228B22", "#90EE90", "#98FB98"],
        "timing_preset": "relaxing"
    }
}

# Configurações de timing e transições
TIMING_PRESETS = {
    "educational": {
        "hook_duration": 3,
        "value_delivery_segments": [4, 5, 4],
        "conclusion_duration": 3,
        "transition_duration": 0.5
    },
    "storytelling": {
        "hook_duration": 4,
        "value_delivery_segments": [6, 8, 6],
        "conclusion_duration": 4,
        "transition_duration": 0.8
    },
    "informative": {
        "hook_duration": 2,
        "value_delivery_segments": [5, 5, 5],
        "conclusion_duration": 3,
        "transition_duration": 0.3
    },
    "narrative": {
        "hook_duration": 5,
        "value_delivery_segments": [7, 10, 8],
        "conclusion_duration": 5,
        "transition_duration": 1.0
    },
    "relaxing": {
        "hook_duration": 2,
        "value_delivery_segments": [8, 10, 8],
        "conclusion_duration": 3,
        "transition_duration": 1.2
    }
}

def get_category_config(category: str) -> Dict[str, Any]:
    """Obtém configuração para uma categoria de conteúdo."""
    return CONTENT_CATEGORY_CONFIGS.get(category.upper(), CONTENT_CATEGORY_CONFIGS["SPACE"])

def get_timing_preset(timing_name: str) -> Dict[str, int]:
    """Obtém preset de timing."""
    return TIMING_PRESETS.get(timing_name, TIMING_PRESETS["educational"])

if __name__ == "__main__":
    # Teste das configurações
print("=== Configurações de Plataforma de Vídeo ===")
print(f"Plataformas configuradas: {list(video_config.platforms.keys())}")
print(f"Presets de qualidade: {[p.name for p in video_config.quality_presets]}")
    
    # Teste de especificações do TikTok
    tiktok_specs = video_config.get_platform_specs(Platform.TIKTOK)
print(f"\nTikTok - Resolução: {tiktok_specs.resolution_str}")
print(f"TikTok - Duração: {tiktok_specs.duration_min}s - {tiktok_specs.duration_max}s")
print(f"TikTok - FPS: {tiktok_specs.fps}")
    
    # Teste de configurações de categoria
print(f"\nConfiguração SPACE: {get_category_config('SPACE')}")
print(f"Timing EDUCATIONAL: {get_timing_preset('educational')}")