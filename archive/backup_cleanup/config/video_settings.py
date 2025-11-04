"""
Configurações do módulo de vídeo - AI Shorts
Fase 1 - Setup técnico do Módulo 8
"""

import os
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).parent.parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "outputs" / "video"
CACHE_DIR = BASE_DIR / "cache" / "video"

# Criar diretórios se não existirem
for dir_path in [TEMP_DIR, OUTPUT_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Configurações de YouTube extraction
YOUTUBE_SETTINGS = {
    'quality': 'best[height<=720]',  # Limite de qualidade para videos
    'format': 'mp4',
    'extract_audio': True,
    'audio_format': 'mp3',
    'audio_quality': '192',
    'max_duration': 3600,  # 1 hora máximo
    'min_duration': 30,    # 30 segundos mínimo
    'writesubtitles': False,
    'writeautomaticsub': False,
}

# Configurações de processamento de vídeo
VIDEO_PROCESSING = {
    'output_resolution': (1920, 1080),  # Full HD padrão
    'output_fps': 30,
    'output_format': 'mp4',
    'codec': 'libx264',
    'audio_codec': 'aac',
    'video_bitrate': '2000k',
    'audio_bitrate': '128k',
    'temp_dir': str(TEMP_DIR),
    'max_workers': 4,  # Número de workers para processamento paralelo
}

# Configurações de extração de frames
FRAME_EXTRACTION = {
    'fps_target': 1,  # 1 frame por segundo
    'max_frames': 300,  # Máximo de 5 minutos de vídeo (300 frames)
    'min_frames': 10,   # Mínimo de 10 segundos de vídeo
    'quality': 'high',
}

# Configurações de similarity matching
SIMILARITY_MATCHING = {
    'similarity_threshold': 0.8,  # Threshold para considerar similar
    'max_matches': 5,             # Máximo de matches por query
    'model_name': 'clip-ViT-B-32',  # Modelo CLIP para comparação
    'similarity_metric': 'cosine',   # Métrica de similaridade
}

# Configurações de geração final
VIDEO_GENERATION = {
    'output_resolution': (1080, 1920),  # Vertical para shorts
    'target_duration': 60,               # Duração alvo em segundos
    'transitions': {
        'fade_duration': 0.5,           # Duração do fade entre clips
        'slide_duration': 0.3,          # Duração do slide
    },
    'text_overlay': {
        'font_size': 48,
        'font_color': 'white',
        'background_color': 'black',
        'opacity': 0.8,
    }
}

# Configurações de audio
AUDIO_PROCESSING = {
    'sample_rate': 44100,
    'channels': 2,
    'format': 'mp3',
    'bitrate': '192k',
    'noise_reduction': True,
    'normalize_audio': True,
}

# Configurações de cache
CACHE_SETTINGS = {
    'enabled': True,
    'ttl': 3600 * 24,  # 24 horas
    'cache_dir': str(CACHE_DIR),
    'max_cache_size': 1024 * 1024 * 1024,  # 1GB
}

# Configurações de logging
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': BASE_DIR / 'logs' / 'video_processing.log',
}

# URLs e endpoints importantes
API_ENDPOINTS = {
    'youtube_search': 'https://www.googleapis.com/youtube/v3/search',
    'clip_model_url': 'https://huggingface.co/openai/clip-vit-base-patch32',
}

# Limites e restrições
LIMITS = {
    'max_video_size': 500 * 1024 * 1024,  # 500MB
    'max_audio_size': 100 * 1024 * 1024,  # 100MB
    'max_concurrent_downloads': 3,
    'request_timeout': 300,  # 5 minutos
}

# Configurações de qualidade para diferentes tipos de conteúdo
QUALITY_PROFILES = {
    'high': {
        'video_bitrate': '4000k',
        'audio_bitrate': '192k',
        'resolution': (1920, 1080),
        'fps': 60,
    },
    'medium': {
        'video_bitrate': '2000k',
        'audio_bitrate': '128k',
        'resolution': (1280, 720),
        'fps': 30,
    },
    'low': {
        'video_bitrate': '1000k',
        'audio_bitrate': '96k',
        'resolution': (854, 480),
        'fps': 24,
    }
}

def get_config():
    """Retorna todas as configurações como um dicionário."""
    return {
        'youtube': YOUTUBE_SETTINGS,
        'video_processing': VIDEO_PROCESSING,
        'frame_extraction': FRAME_EXTRACTION,
        'similarity': SIMILARITY_MATCHING,
        'generation': VIDEO_GENERATION,
        'audio': AUDIO_PROCESSING,
        'cache': CACHE_SETTINGS,
        'logging': LOGGING,
        'api_endpoints': API_ENDPOINTS,
        'limits': LIMITS,
        'quality_profiles': QUALITY_PROFILES,
        'paths': {
            'base_dir': str(BASE_DIR),
            'temp_dir': str(TEMP_DIR),
            'output_dir': str(OUTPUT_DIR),
            'cache_dir': str(CACHE_DIR),
        }
    }

def get_quality_profile(quality='medium'):
    """Retorna o perfil de qualidade especificado."""
    return QUALITY_PROFILES.get(quality, QUALITY_PROFILES['medium'])

# Configurações de composição final otimizada
FINAL_COMPOSITION = {
    'default_resolution': (1080, 1920),
    'default_fps': 30,
    'target_bitrate': '5M',
    'temp_dir': str(TEMP_DIR / 'final_composition'),
    'output_dir': str(OUTPUT_DIR / 'final_videos'),
    'max_quality_retries': 3,
    'quality_thresholds': {
        'min_resolution_score': 0.8,
        'min_audio_sync_score': 0.85,
        'min_visual_clarity_score': 0.75,
        'min_overall_score': 0.8
    }
}

# Configurações de qualidade automática
AUTO_QUALITY = {
    'enabled': True,
    'checks': {
        'resolution_check': True,
        'audio_sync_check': True,
        'visual_clarity_check': True,
        'compression_check': True,
        'engagement_check': True
    },
    'thresholds': {
        'min_resolution': (720, 1280),
        'max_file_size_mb': 100,
        'min_engagement_score': 0.6,
        'max_audio_lag_ms': 100
    },
    'improvements': {
        'auto_enhance_colors': True,
        'auto_sharpen': True,
        'auto_normalize_audio': True,
        'auto_stabilize': False
    }
}

# Configurações multi-plataforma
MULTI_PLATFORM = {
    'batch_export': {
        'enabled': True,
        'parallel_processing': True,
        'max_concurrent': 3
    },
    'platforms': {
        'tiktok': {
            'resolution': (1080, 1920),
            'fps': 30,
            'max_duration': 60,
            'bitrate': '4M',
            'format': 'mp4'
        },
        'youtube_shorts': {
            'resolution': (1080, 1920),
            'fps': 30,
            'max_duration': 60,
            'bitrate': '8M',
            'format': 'mp4'
        },
        'instagram_reels': {
            'resolution': (1080, 1920),
            'fps': 30,
            'max_duration': 90,
            'bitrate': '6M',
            'format': 'mp4'
        },
        'facebook_reels': {
            'resolution': (1080, 1920),
            'fps': 30,
            'max_duration': 90,
            'bitrate': '5M',
            'format': 'mp4'
        },
        'twitter': {
            'resolution': (1080, 1920),
            'fps': 30,
            'max_duration': 140,
            'bitrate': '4M',
            'format': 'mp4'
        }
    }
}

def get_final_composition_config():
    """Retorna configurações específicas de composição final."""
    return FINAL_COMPOSITION

def get_platform_config(platform_name: str) -> dict:
    """Retorna configuração específica de uma plataforma."""
    return MULTI_PLATFORM['platforms'].get(platform_name, {})

def is_quality_auto_check_enabled() -> bool:
    """Verifica se verificação automática de qualidade está habilitada."""
    return AUTO_QUALITY['enabled']

def get_quality_thresholds() -> dict:
    """Retorna thresholds de qualidade."""
    return AUTO_QUALITY['thresholds']

# Atualizar get_config para incluir novas configurações
def get_config():
    """Retorna todas as configurações como um dicionário."""
    config = {
        'youtube': YOUTUBE_SETTINGS,
        'video_processing': VIDEO_PROCESSING,
        'frame_extraction': FRAME_EXTRACTION,
        'similarity': SIMILARITY_MATCHING,
        'generation': VIDEO_GENERATION,
        'audio': AUDIO_PROCESSING,
        'cache': CACHE_SETTINGS,
        'logging': LOGGING,
        'api_endpoints': API_ENDPOINTS,
        'limits': LIMITS,
        'quality_profiles': QUALITY_PROFILES,
        'final_composition': FINAL_COMPOSITION,
        'auto_quality': AUTO_QUALITY,
        'multi_platform': MULTI_PLATFORM,
        'paths': {
            'base_dir': str(BASE_DIR),
            'temp_dir': str(TEMP_DIR),
            'output_dir': str(OUTPUT_DIR),
            'cache_dir': str(CACHE_DIR),
        }
    }
    return config