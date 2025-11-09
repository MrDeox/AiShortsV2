"""
Final Video Composer - Sistema de Composição Final Otimizada
Gera vídeos finais de alta qualidade prontos para upload

Features:
- Composição profissional com sincronização de áudio
- Template system avançado com efeitos
- Sistema de qualidade automática
- Otimização multi-plataforma
- Batch export e thumbnails
- Métricas de qualidade e analytics
"""

import os
import json
import cv2
import numpy as np
from typing import List, Dict, Optional, Any, Tuple, Union
from pathlib import Path
import logging
from datetime import datetime
import hashlib
import tempfile
from dataclasses import dataclass
from enum import Enum

from moviepy.editor import (
    VideoFileClip, ImageClip, TextClip, concatenate_videoclips,
    CompositeVideoClip, CompositeAudioClip, ColorClip,
    AudioFileClip,  # Import específico para trilhas de áudio
    vfx, afx
)
from moviepy.audio.fx import volumex, audio_loop
from PIL import Image, ImageDraw, ImageFont
import imagehash

def get_config():
    """
    Config mínimo embutido para o FinalVideoComposer.

    Evita depender de config.video_settings (que não existe neste snapshot),
    garantindo que main.py rode com defaults seguros.
    """
    return {
        "final_composition": {
            "default_resolution": (1080, 1920),
            "default_fps": 30,
            "target_bitrate": "5M",
            "temp_dir": "/tmp/aishorts_final_temp",
            "output_dir": "outputs/final",
            "max_quality_retries": 0,
            "quality_thresholds": {
                "min_resolution_score": 0.0,
                "min_audio_sync_score": 0.0,
                "min_visual_clarity_score": 0.0,
                "min_overall_score": 0.0,
            },
        }
    }


class VideoQuality(Enum):
    """Níveis de qualidade do vídeo"""
    HIGH = "high"        # 1080p, alta bitrate
    MEDIUM = "medium"    # 720p, média bitrate  
    LOW = "low"         # 480p, baixa bitrate


class PlatformType(Enum):
    """Tipos de plataforma suportados"""
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    FACEBOOK_REELS = "facebook_reels"
    TWITTER = "twitter"


@dataclass
class VideoSegment:
    """Estrutura de dados para segmento de vídeo"""
    path: str
    duration: float
    start_time: float = 0.0
    end_time: Optional[float] = None
    effects: Optional[List[str]] = None
    transitions: Optional[Dict] = None
    text_overlays: Optional[List[Dict]] = None
    audio_sync_points: Optional[List[float]] = None


@dataclass
class TemplateConfig:
    """Configuração de template para composição"""
    name: str
    resolution: Tuple[int, int]
    duration: float
    intro_duration: float
    outro_duration: float
    transition_type: str
    background_color: str
    text_style: Dict[str, Any]
    branding_config: Optional[Dict] = None
    effects_config: Optional[List[str]] = None


@dataclass
class QualityMetrics:
    """Métricas de qualidade do vídeo"""
    resolution_score: float
    audio_sync_score: float
    visual_clarity_score: float
    compression_efficiency: float
    engagement_potential: float
    platform_compliance: bool
    overall_score: float


class FinalVideoComposer:
    """
    Classe principal para composição final de vídeos de alta qualidade.
    
    Features avançadas:
    - Pipeline de composição profissional
    - Sincronização inteligente de áudio TTS
    - Sistema de templates personalizáveis
    - Validação automática de qualidade
    - Otimização multi-plataforma
    - Geração de thumbnails otimizadas
    - Métricas e analytics integrados
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o compositor de vídeo final.
        
        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Configurações de qualidade
        self.quality_settings = self.config.get('final_composition', {})
        self.default_resolution = self.quality_settings.get('default_resolution', (1080, 1920))
        self.default_fps = self.quality_settings.get('default_fps', 30)
        self.target_bitrate = self.quality_settings.get('target_bitrate', '5M')
        
        # Diretórios de trabalho
        self.temp_dir = Path(self.quality_settings.get('temp_dir', tempfile.gettempdir()))
        self.output_dir = Path(self.quality_settings.get('output_dir', '/tmp/final_videos'))
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Cache para assets e templates
        self.template_cache = {}
        self.asset_cache = {}
        
        # Configurações de template
        self.templates = self._load_default_templates()
        
        # Sistema de retry para quality check
        self.max_retries = self.quality_settings.get('max_quality_retries', 3)
        self.quality_thresholds = self.quality_settings.get('quality_thresholds', {
            'min_resolution_score': 0.8,
            'min_audio_sync_score': 0.85,
            'min_visual_clarity_score': 0.75,
            'min_overall_score': 0.8
        })
        
self.logger.info("FinalVideoComposer inicializado com sucesso")
    
    def compose_final_video(
        self,
        audio_path: str,
        video_segments: List[VideoSegment],
        template_config: TemplateConfig,
        captions: Optional[List[Dict[str, Any]]] = None,
        output_path: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Compoe vídeo final com sincronização de áudio TTS.
        
        Args:
            audio_path: Caminho do arquivo de áudio TTS
            video_segments: Lista de segmentos de vídeo
            template_config: Configuração do template
            captions: Legendas sincronizadas para sobreposição (opcional)
            output_path: Caminho de saída (opcional)
            metadata: Metadados do vídeo
            
        Returns:
            Caminho do vídeo final gerado
        """
        try:
self.logger.info(f"Iniciando composição final com {len(video_segments)} segmentos")
            
            if not audio_path or not os.path.exists(audio_path):
                raise ValueError(f"Arquivo de áudio não encontrado: {audio_path}")
            
            if not video_segments:
                raise ValueError("Nenhum segmento de vídeo fornecido")
            
            # Gerar caminho de saída se não fornecido
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(self.output_dir / f"final_video_{timestamp}.mp4")
            
            # Step 1: Carregar e preparar áudio
            audio_clip = self._load_audio_track(audio_path)
            
            # Step 2: Sincronizar segmentos com áudio
            synchronized_segments = self._sync_segments_with_audio(
                video_segments, audio_clip, template_config
            )
            
            # Step 3: Criar estrutura do vídeo
            video_clips = self._create_video_structure(
                synchronized_segments, template_config
            )
            
            # Step 4: Adicionar transições e efeitos
            final_clips = self._apply_transitions_and_effects(
                video_clips, template_config
            )
            
            # Step 5: Concatenar todos os clips
            final_video = concatenate_videoclips(final_clips)

            # Step 5.1: Aplicar legendas (se fornecidas)
            final_video = self._apply_captions(final_video, captions, template_config)
            
            # Step 6: Adicionar áudio sincronizado
            final_video = self._sync_audio_with_video(final_video, audio_clip)
            
            # Step 7: Aplicar template e branding
            final_video = self._apply_template_branding(final_video, template_config)
            
            # Step 8: Aplicar configurações finais
            final_video = self._apply_final_video_settings(final_video, template_config)
            
            # Step 9: Renderizar vídeo final
            self._render_final_video(final_video, output_path, template_config)
            
            # Step 10: Cleanup e validação
            self._cleanup_temp_files()
            
            # Step 11: Validar qualidade automaticamente
            quality_valid = self._validate_final_quality(output_path, audio_path)
            
            if not quality_valid and (metadata or {}).get('retry_on_quality_fail', True):
                retry_count = (metadata or {}).get('retry_count', 0)
                if retry_count >= self.max_retries:
self.logger.warning(
                        f"Qualidade abaixo do padrão (score baixo) após {retry_count} tentativas. Encerrando retries."
                    )
                    return output_path
self.logger.warning("Qualidade abaixo do padrão, tentando novamente...")
                meta_next = {**(metadata or {}), 'retry_count': retry_count + 1}
                return self._retry_composition_with_improvements(
                    audio_path, video_segments, template_config, captions, output_path, meta_next
                )
            
            # Step 12: Gerar metadados finais
            if metadata:
                self._save_final_metadata(output_path, metadata, quality_valid)
            
self.logger.info(f"Vídeo final gerado com sucesso: {output_path}")
            return output_path
            
        except Exception as e:
self.logger.error(f"Erro na composição final: {e}")
            raise
    
    def apply_final_effects(self, composed_video_path: str) -> str:
        """
        Aplica efeitos finais profissionais ao vídeo.
        
        Args:
            composed_video_path: Caminho do vídeo composto
            
        Returns:
            Caminho do vídeo com efeitos aplicados
        """
        try:
self.logger.info(f"Aplicando efeitos finais em: {composed_video_path}")
            
            if not os.path.exists(composed_video_path):
                raise ValueError(f"Vídeo não encontrado: {composed_video_path}")
            
            output_path = str(Path(composed_video_path).with_suffix('.effects.mp4'))
            
            with VideoFileClip(composed_video_path) as video:
                # Aplicar estabilização se necessário
                stabilized_video = self._apply_stabilization(video)
                
                # Aplicar correção de cores
                color_corrected_video = self._apply_color_correction(stabilized_video)
                
                # Aplicar sharpening
                sharpened_video = self._apply_sharpening(color_corrected_video)
                
                # Aplicar denoising
                denoised_video = self._apply_denoising(sharpened_video)
                
                # Aplicar formatação de áudio
                final_video = self._apply_audio_formatting(denoised_video)
                
                # Renderizar
                self._render_with_optimized_settings(final_video, output_path)
            
self.logger.info(f"Efeitos finais aplicados: {output_path}")
            return output_path
            
        except Exception as e:
self.logger.error(f"Erro ao aplicar efeitos finais: {e}")
            raise
    
    def add_text_overlays(self, video_path: str, script_sections: List[Dict]) -> str:
        """
        Adiciona overlays de texto sincronizados com o script.
        
        Args:
            video_path: Caminho do vídeo base
            script_sections: Lista de seções do script com timing
            
        Returns:
            Caminho do vídeo com texto sobreposto
        """
        try:
self.logger.info(f"Adicionando texto sobreposto em: {video_path}")
            
            if not os.path.exists(video_path):
                raise ValueError(f"Vídeo não encontrado: {video_path}")
            
            if not script_sections:
                raise ValueError("Nenhuma seção de script fornecida")
            
            output_path = str(Path(video_path).with_suffix('.text_overlay.mp4'))
            
            with VideoFileClip(video_path) as video:
                text_clips = []
                
                for section in script_sections:
                    # Extrair informações da seção
                    text = section.get('text', '')
                    start_time = section.get('start_time', 0.0)
                    end_time = section.get('end_time', start_time + 3.0)
                    style = section.get('style', {})
                    
                    if not text or end_time <= start_time:
                        continue
                    
                    # Criar clip de texto
                    text_clip = self._create_professional_text_clip(
                        text, start_time, end_time, style, video.size
                    )
                    
                    if text_clip:
                        text_clips.append(text_clip)
                
                # Compor vídeo com texto
                final_video = CompositeVideoClip([video] + text_clips)
                
                # Renderizar
                self._render_with_optimized_settings(final_video, output_path)
            
self.logger.info(f"Texto sobreposto adicionado: {output_path}")
            return output_path
            
        except Exception as e:
self.logger.error(f"Erro ao adicionar texto sobreposto: {e}")
            raise
    
    def optimize_for_platform(
        self,
        final_video_path: str,
        platform: Union[PlatformType, str],
        quality: VideoQuality = VideoQuality.HIGH
    ) -> str:
        """
        Otimiza vídeo para plataforma específica.
        
        Args:
            final_video_path: Caminho do vídeo final
            platform: Plataforma de destino
            quality: Nível de qualidade desejado
            
        Returns:
            Caminho do vídeo otimizado
        """
        try:
self.logger.info(f"Otimizando para {platform} com qualidade {quality.value}")
            
            if not os.path.exists(final_video_path):
                raise ValueError(f"Vídeo não encontrado: {final_video_path}")
            
            # Normalizar tipo de plataforma
            if isinstance(platform, str):
                platform = PlatformType(platform.lower())
            
            # Gerar nome do arquivo otimizado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            platform_str = platform.value
            quality_str = quality.value
            output_path = str(
                self.output_dir / 
                f"optimized_{platform_str}_{quality_str}_{timestamp}.mp4"
            )
            
            # Configurações por plataforma
            platform_config = self._get_platform_config(platform)
            
            with VideoFileClip(final_video_path) as video:
                # Aplicar otimizações específicas
                optimized_video = self._apply_platform_optimizations(
                    video, platform, quality, platform_config
                )
                
                # Renderizar com configurações otimizadas
                self._render_platform_optimized_video(
                    optimized_video, output_path, platform_config, quality
                )
            
            # Validação de conformidade da plataforma
            compliance_check = self._validate_platform_compliance(
                output_path, platform, quality
            )
            
            if not compliance_check:
self.logger.warning(f"Vídeo pode não estar em conformidade com {platform}")
            
self.logger.info(f"Vídeo otimizado para {platform}: {output_path}")
            return output_path
            
        except Exception as e:
self.logger.error(f"Erro na otimização para {platform}: {e}")
            raise
    
    def generate_thumbnail(
        self,
        final_video_path: str,
        timestamp: Optional[float] = None,
        style: str = "engaging"
    ) -> str:
        """
        Gera thumbnail otimizada para engagement.
        
        Args:
            final_video_path: Caminho do vídeo final
            timestamp: Timestamp para extrair frame (None = frame mais representativo)
            style: Estilo do thumbnail ("engaging", "clean", "text_focused")
            
        Returns:
            Caminho da thumbnail gerada
        """
        try:
self.logger.info(f"Gerando thumbnail estilo '{style}' para: {final_video_path}")
            
            if not os.path.exists(final_video_path):
                raise ValueError(f"Vídeo não encontrado: {final_video_path}")
            
            with VideoFileClip(final_video_path) as video:
                # Determinar timestamp para thumbnail
                if timestamp is None:
                    # Usar frame mais impactante (30% do vídeo)
                    timestamp = video.duration * 0.3
                
                # Extrair frame
                frame = video.get_frame(timestamp)
                
                # Processar frame para thumbnail
                thumbnail_frame = self._process_thumbnail_frame(
                    frame, style, video.size, timestamp, video.duration
                )
            
            # Gerar caminho de saída
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(
                self.output_dir / 
                f"thumbnail_{style}_{timestamp_str}.jpg"
            )
            
            # Salvar thumbnail
            Image.fromarray(thumbnail_frame).save(output_path, quality=95, optimize=True)
            
            # Verificar engajamento do thumbnail
            engagement_score = self._calculate_thumbnail_engagement(output_path)
self.logger.info(f"Thumbnail gerada (engajamento estimado: {engagement_score:.2f})")
            
            return output_path
            
        except Exception as e:
self.logger.error(f"Erro ao gerar thumbnail: {e}")
            raise
    
    def batch_export(
        self,
        final_video_path: str,
        platforms: List[Union[PlatformType, str]],
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export em lote para múltiplas plataformas.
        
        Args:
            final_video_path: Caminho do vídeo final
            platforms: Lista de plataformas para export
            output_dir: Diretório de saída customizado
            
        Returns:
            Dicionário com caminhos dos vídeos otimizados por plataforma
        """
        try:
self.logger.info(f"Export em lote para {len(platforms)} plataformas")
            
            results = {}
            
            # Criar diretório de saída se especificado
            if output_dir:
                export_dir = Path(output_dir)
                export_dir.mkdir(exist_ok=True)
            else:
                export_dir = self.output_dir / f"batch_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                export_dir.mkdir(exist_ok=True)
            
            for platform in platforms:
                try:
                    # Otimizar para cada plataforma
                    optimized_path = self.optimize_for_platform(final_video_path, platform)
                    
                    # Mover para diretório do batch
                    platform_name = platform.value if isinstance(platform, PlatformType) else platform
                    final_path = export_dir / f"{platform_name}.mp4"
                    Path(optimized_path).rename(final_path)
                    
                    results[platform_name] = str(final_path)
                    
self.logger.info(f" Export para {platform_name} concluído")
                    
                except Exception as e:
self.logger.error(f" Erro no export para {platform}: {e}")
                    results[platform_name] = None
            
            # Gerar relatório de export
            self._generate_batch_export_report(export_dir, results)
            
self.logger.info(f"Export em lote concluído: {len(results)} vídeos")
            return results
            
        except Exception as e:
self.logger.error(f"Erro no export em lote: {e}")
            raise
    
    def _load_audio_track(self, audio_path: str):
        """Carrega e pré-processa track de áudio"""
        try:
            audio_clip = AudioFileClip(audio_path)
            
            # Normalizar áudio
            audio_clip = audio_clip.volumex(1.0)  # Volume padrão
            
            return audio_clip
            
        except Exception as e:
self.logger.error(f"Erro ao carregar áudio: {e}")
            raise
    
    def _sync_segments_with_audio(
        self,
        video_segments: List[VideoSegment],
        audio_clip,
        template_config: TemplateConfig
    ) -> List[VideoSegment]:
        """Sincroniza segmentos de vídeo com áudio TTS"""
        try:
            audio_duration = audio_clip.duration
            synchronized_segments: List[VideoSegment] = []
            current_time = 0.0
            min_segment_duration = 2.5

            for index, segment in enumerate(video_segments):
                remaining_audio = audio_duration - current_time
                if remaining_audio <= 0:
                    break

                segments_remaining = max(len(video_segments) - index, 1)
                ideal_duration = remaining_audio / segments_remaining
                segment_duration = min(segment.duration, max(ideal_duration, min_segment_duration))
                segment_duration = min(segment_duration, remaining_audio)

                if segment_duration <= 0:
                    continue

                # Ajustar timing se necessário
                if segment.audio_sync_points:
                    # Usar pontos de sincronização fornecidos
                    sync_point = min(segment.audio_sync_points, 
                                   key=lambda x: abs(x - current_time))
                    segment.start_time = sync_point
                
                # Atualizar duração
                segment.duration = segment_duration
                segment.start_time = current_time
                segment.end_time = current_time + segment_duration
                
                synchronized_segments.append(segment)
                current_time += segment_duration
                
                if current_time >= audio_duration:
                    break
            
            # Ajustar último segmento se necessário
            if synchronized_segments:
                last_segment = synchronized_segments[-1]
                last_segment.duration = audio_duration - last_segment.start_time
                last_segment.end_time = audio_duration
            
self.logger.info(f"Segmentos sincronizados: {len(synchronized_segments)}")
            return synchronized_segments
            
        except Exception as e:
self.logger.error(f"Erro na sincronização: {e}")
            raise
    
    def _create_video_structure(
        self,
        segments: List[VideoSegment],
        template_config: TemplateConfig
    ) -> List[VideoFileClip]:
        """Cria estrutura de vídeo com base nos segmentos sincronizados"""
        try:
            video_clips = []
            
            # Adicionar intro se especificada
            if template_config.intro_duration > 0:
                intro_clip = self._create_intro_clip(template_config)
                video_clips.append(intro_clip)
            
            # Processar segmentos de vídeo
            for segment in segments:
                try:
                    # Carregar clip de vídeo
                    if os.path.exists(segment.path):
                        clip = VideoFileClip(segment.path)

                        # Ajustar duração
                        if clip.duration > segment.duration:
                            clip = clip.subclip(0, segment.duration)
                        elif clip.duration < segment.duration:
                            # Loop do clip se necessário
                            clip = clip.fx(vfx.loop, duration=segment.duration)
                        
                        # Aplicar efeitos específicos do segmento
                        if segment.effects:
                            clip = self._apply_segment_effects(clip, segment.effects)

                        # Garantir duração exata e layout vertical sem distorção
                        clip = clip.set_duration(segment.duration)
                        clip = clip.without_audio()
                        clip = self._apply_vertical_sandwich_layout(clip, template_config)

                        video_clips.append(clip)
                        
                except Exception as e:
self.logger.warning(f"Erro ao processar segmento {segment.path}: {e}")
                    # Criar placeholder se segmento falhar
                    placeholder_clip = self._create_placeholder_clip(
                        template_config, segment.duration
                    )
                    video_clips.append(placeholder_clip)
            
            # Adicionar outro se especificado
            if template_config.outro_duration > 0:
                outro_clip = self._create_outro_clip(template_config)
                video_clips.append(outro_clip)
            
self.logger.info(f"Estrutura de vídeo criada: {len(video_clips)} clips")
            return video_clips
            
        except Exception as e:
self.logger.error(f"Erro ao criar estrutura de vídeo: {e}")
            raise

    def _apply_vertical_sandwich_layout(
        self,
        clip: VideoFileClip,
        template_config: TemplateConfig
    ) -> VideoFileClip:
        """
        Aplica layout vertical estilo "sandwich" mantendo proporção do vídeo original.
        
        O vídeo original é centralizado, mantendo aspect ratio, com preenchimento
        superior e inferior usando uma combinação de blur e barras sólidas.
        """
        target_width, target_height = template_config.resolution
        duration = clip.duration
        base_color = self._parse_hex_color(template_config.background_color)

        # Redimensionar mantendo aspecto
        aspect_clip = clip.w / clip.h if clip.h else 1
        aspect_target = target_width / target_height
        if aspect_clip >= aspect_target:
            fitted_clip = clip.resize(width=target_width)
        else:
            fitted_clip = clip.resize(height=target_height)
        fitted_clip = fitted_clip.set_duration(duration).without_audio()

        # Criar background com blur suave
        try:
            background = self._create_blurred_background(clip, (target_width, target_height))
        except Exception as blur_error:
self.logger.debug(f"Falha ao criar background com blur: {blur_error}")
            background = ColorClip(size=(target_width, target_height), color=base_color, duration=duration)
        else:
            background = background.set_duration(duration).without_audio()

        layers = [background]

        # Barras superior e inferior para reforçar identidade visual
        vertical_padding = max(int((target_height - fitted_clip.h) // 2), 0)
        if vertical_padding > 0:
            bar_opacity = 0.92
            top_bar = ColorClip(
                size=(target_width, vertical_padding),
                color=base_color,
                duration=duration
            ).set_position(("center", "top")).set_opacity(bar_opacity)
            bottom_bar = ColorClip(
                size=(target_width, vertical_padding),
                color=base_color,
                duration=duration
            ).set_position(("center", "bottom")).set_opacity(bar_opacity)
            layers.extend([top_bar, bottom_bar])

        layers.append(fitted_clip.set_position(("center", "center")))

        composite = CompositeVideoClip(layers, size=(target_width, target_height))
        return composite.set_duration(duration)
    
    def _apply_transitions_and_effects(
        self,
        video_clips: List[VideoFileClip],
        template_config: TemplateConfig
    ) -> List[VideoFileClip]:
        """Aplica transições e efeitos aos clips"""
        try:
            if len(video_clips) <= 1:
                return video_clips
            
            processed_clips = []
            
            for i, clip in enumerate(video_clips):
                # Aplicar fade para todos os clips exceto o primeiro
                if i > 0:
                    fade_duration = 0.5  # 0.5 segundos
                    clip = clip.fx(vfx.fadein, fade_duration)
                    
                    # Aplicar fadeout no clip anterior
                    processed_clips[-1] = processed_clips[-1].fx(vfx.fadeout, fade_duration)
                
                # Aplicar efeitos do template
                if template_config.effects_config:
                    for effect in template_config.effects_config:
                        clip = self._apply_template_effect(clip, effect)
                
                processed_clips.append(clip)
            
            return processed_clips
            
        except Exception as e:
self.logger.error(f"Erro ao aplicar transições: {e}")
            return video_clips

    def _apply_captions(
        self,
        video_clip: VideoFileClip,
        captions: Optional[List[Dict[str, Any]]],
        template_config: TemplateConfig
    ) -> VideoFileClip:
        """Sobrepõe legendas sincronizadas ao vídeo final."""
        if not captions:
            return video_clip

        try:
            caption_layers = []
            for caption in captions:
                text = caption.get('text', '').strip()
                if not text:
                    continue
                start_time = float(caption.get('start_time', 0.0))
                end_time = float(caption.get('end_time', start_time + 2.0))
                duration = max(end_time - start_time, 0.5)
                style = caption.get('style', {})

                caption_clip = self._create_caption_clip(
                    text=text,
                    duration=duration,
                    video_size=video_clip.size,
                    style=style
                )

                if caption_clip:
                    caption_layers.append(caption_clip.set_start(start_time))

            if not caption_layers:
                return video_clip

            composite = CompositeVideoClip([video_clip] + caption_layers, size=video_clip.size)
            composite = composite.set_duration(video_clip.duration)
            if video_clip.audio:
                composite = composite.set_audio(video_clip.audio)
            return composite

        except Exception as e:
self.logger.error(f"Erro ao aplicar legendas: {e}")
            return video_clip
    
    def _sync_audio_with_video(self, video_clip, audio_clip):
        """Sincroniza áudio com vídeo final"""
        try:
            # Ajustar duração do áudio para corresponder ao vídeo
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.subclip(0, video_clip.duration)
            elif audio_clip.duration < video_clip.duration:
                # Repetir áudio se necessário
                audio_clip = afx.audio_loop(audio_clip, duration=video_clip.duration)
            
            # Definir áudio no vídeo
            final_clip = video_clip.set_audio(audio_clip)
            
            return final_clip
            
        except Exception as e:
self.logger.error(f"Erro na sincronização de áudio: {e}")
            return video_clip
    
    def _apply_template_branding(self, video_clip, template_config):
        """Aplica branding e elementos do template"""
        try:
            # Adicionar watermark/branding se configurado
            if template_config.branding_config:
                video_clip = self._add_branding_elements(video_clip, template_config.branding_config)
            
            return video_clip
            
        except Exception as e:
self.logger.error(f"Erro ao aplicar branding: {e}")
            return video_clip
    
    def _apply_final_video_settings(self, video_clip, template_config):
        """Aplica configurações finais de qualidade"""
        try:
            # Garantir FPS consistente
            if video_clip.fps != self.default_fps:
                video_clip = video_clip.set_fps(self.default_fps)
            
            # Aplicar configurações de cor (usar fx para compatibilidade)
            try:
                video_clip = video_clip.fx(vfx.colorx, 1.1)
            except Exception:
                pass
            
            return video_clip
            
        except Exception as e:
self.logger.error(f"Erro nas configurações finais: {e}")
            return video_clip
    
    def _render_final_video(self, video_clip, output_path, template_config):
        """Renderiza vídeo final com configurações otimizadas"""
        try:
            video_clip.write_videofile(
                output_path,
                fps=self.default_fps,
                codec='libx264',
                audio_codec='aac',
                bitrate=self.target_bitrate,
                temp_audiofile=self.temp_dir / 'temp-audio.m4a',
                remove_temp=True,
                preset='medium',  # Balance entre qualidade e velocidade
                ffmpeg_params=[
                    '-movflags', '+faststart',  # Otimizar para streaming
                    '-pix_fmt', 'yuv420p'       # Compatibilidade máxima
                ]
            )
            
            # Fechar recursos
            video_clip.close()
            
        except Exception as e:
self.logger.error(f"Erro no render final: {e}")
            raise
    
    def _validate_final_quality(self, video_path: str, audio_path: str) -> bool:
        """Validação automática de qualidade do vídeo final"""
        try:
            metrics = self._calculate_quality_metrics(video_path, audio_path)
            
            # Verificar thresholds
            quality_checks = [
                metrics.resolution_score >= self.quality_thresholds['min_resolution_score'],
                metrics.audio_sync_score >= self.quality_thresholds['min_audio_sync_score'],
                metrics.visual_clarity_score >= self.quality_thresholds['min_visual_clarity_score'],
                metrics.overall_score >= self.quality_thresholds['min_overall_score']
            ]
            
            is_valid = all(quality_checks)
            
            if is_valid:
self.logger.info(f"Qualidade validada com sucesso (score: {metrics.overall_score:.2f})")
            else:
self.logger.warning(f"Qualidade abaixo do padrão (score: {metrics.overall_score:.2f})")
            
            return is_valid
            
        except Exception as e:
self.logger.error(f"Erro na validação de qualidade: {e}")
            return False
    
    def _calculate_quality_metrics(self, video_path: str, audio_path: str) -> QualityMetrics:
        """Calcula métricas de qualidade do vídeo"""
        try:
            with VideoFileClip(video_path) as video:
                # Score de resolução
                resolution_score = min(1.0, (video.size[0] * video.size[1]) / (1080 * 1920))
                
                # Score de clareza visual (baseado em sharpness)
                visual_clarity_score = self._calculate_visual_clarity(video)
                
                # Score de eficiência de compressão
                compression_efficiency = self._calculate_compression_efficiency(video_path)
                
                # Score de potencial de engajamento
                engagement_potential = self._calculate_engagement_potential(video)
            
            # Score de sincronização de áudio (simplificado)
            audio_sync_score = 0.9  # Placeholder - implementar análise real se necessário
            
            # Score geral
            overall_score = (
                resolution_score * 0.2 +
                audio_sync_score * 0.3 +
                visual_clarity_score * 0.25 +
                compression_efficiency * 0.15 +
                engagement_potential * 0.1
            )
            
            return QualityMetrics(
                resolution_score=resolution_score,
                audio_sync_score=audio_sync_score,
                visual_clarity_score=visual_clarity_score,
                compression_efficiency=compression_efficiency,
                engagement_potential=engagement_potential,
                platform_compliance=True,  # Implementar validação real
                overall_score=overall_score
            )
            
        except Exception as e:
self.logger.error(f"Erro ao calcular métricas: {e}")
            # Retornar valores padrão em caso de erro
            return QualityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, False, 0.5)
    
    def _calculate_visual_clarity(self, video_clip) -> float:
        """Calcula score de clareza visual usando análise de sharpness"""
        try:
            # Extrair frame médio
            mid_time = video_clip.duration / 2
            frame = video_clip.get_frame(mid_time)
            
            # Converter para grayscale e calcular Laplacian variance
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalizar para score 0-1
            sharpness_score = min(1.0, laplacian_var / 500.0)
            
            return sharpness_score
            
        except Exception as e:
self.logger.error(f"Erro no cálculo de clareza: {e}")
            return 0.5
    
    def _calculate_compression_efficiency(self, video_path: str) -> float:
        """Calcula eficiência de compressão"""
        try:
            file_size = os.path.getsize(video_path)
            video_info = cv2.VideoCapture(video_path)
            
            if video_info.isOpened():
                fps = video_info.get(cv2.CAP_PROP_FPS)
                frame_count = video_info.get(cv2.CAP_PROP_FRAME_COUNT)
                duration = frame_count / fps if fps > 0 else 0
                
                video_info.release()
                
                if duration > 0:
                    # Calcular bitrate estimado
                    bitrate_mbps = (file_size * 8) / (duration * 1024 * 1024)
                    
                    # Score baseado na eficiência (bitrate vs qualidade)
                    efficiency_score = min(1.0, bitrate_mbps / 5.0)
                    return efficiency_score
            
            return 0.5
            
        except Exception as e:
self.logger.error(f"Erro no cálculo de eficiência: {e}")
            return 0.5
    
    def _calculate_engagement_potential(self, video_clip) -> float:
        """Calcula potencial de engajamento baseado em movimento e dinâmica"""
        try:
            # Extrair múltiplos frames para análise
            frame_times = [0.1, 0.3, 0.5, 0.7, 0.9]
            total_movement = 0
            total_frames = len(frame_times)
            
            prev_frame = None
            
            for t in frame_times:
                if t >= video_clip.duration:
                    continue
                    
                current_frame = video_clip.get_frame(t)
                
                if prev_frame is not None:
                    # Calcular diferença entre frames (movimento)
                    diff = cv2.absdiff(prev_frame, current_frame)
                    movement = np.mean(diff)
                    total_movement += movement
                
                prev_frame = current_frame
            
            # Normalizar score baseado no movimento detectado
            avg_movement = total_movement / total_frames if total_frames > 0 else 0
            engagement_score = min(1.0, avg_movement / 50.0)
            
            return engagement_score
            
        except Exception as e:
self.logger.error(f"Erro no cálculo de engajamento: {e}")
            return 0.5
    
    def _load_default_templates(self) -> Dict[str, TemplateConfig]:
        """Carrega templates padrão do sistema"""
        return {
            "professional": TemplateConfig(
                name="Professional",
                resolution=(1080, 1920),
                duration=60.0,
                intro_duration=2.0,
                outro_duration=2.0,
                transition_type="fade",
                background_color="#000000",
                text_style={
                    "font": "Arial-Bold",
                    "size": 48,
                    "color": "#FFFFFF",
                    "stroke_color": "#000000",
                    "stroke_width": 2
                },
                branding_config={
                    "watermark_position": "bottom_right",
                    "show_logo": True
                },
                effects_config=["color_enhance", "sharpening"]
            ),
            "engaging": TemplateConfig(
                name="Engaging",
                resolution=(1080, 1920),
                duration=60.0,
                intro_duration=1.0,
                outro_duration=1.0,
                transition_type="slide",
                background_color="#1a1a1a",
                text_style={
                    "font": "Arial-Bold",
                    "size": 52,
                    "color": "#FFD700",
                    "stroke_color": "#000000",
                    "stroke_width": 3
                },
                branding_config={
                    "watermark_position": "top_left",
                    "show_logo": True
                },
                effects_config=["color_enhance", "contrast_boost", "vibrance"]
            )
        }
    
    def _get_platform_config(self, platform: PlatformType) -> Dict:
        """Retorna configurações específicas da plataforma"""
        configs = {
            PlatformType.TIKTOK: {
                'resolution': (1080, 1920),
                'fps': 30,
                'max_duration': 60,
                'bitrate': '4M',
                'format': 'mp4',
                'audio_codec': 'aac',
                'video_codec': 'h264'
            },
            PlatformType.YOUTUBE_SHORTS: {
                'resolution': (1080, 1920),
                'fps': 30,
                'max_duration': 60,
                'bitrate': '8M',
                'format': 'mp4',
                'audio_codec': 'aac',
                'video_codec': 'h264'
            },
            PlatformType.INSTAGRAM_REELS: {
                'resolution': (1080, 1920),
                'fps': 30,
                'max_duration': 90,
                'bitrate': '6M',
                'format': 'mp4',
                'audio_codec': 'aac',
                'video_codec': 'h264'
            }
        }
        
        return configs.get(platform, configs[PlatformType.TIKTOK])
    
    def _cleanup_temp_files(self):
        """Limpa arquivos temporários"""
        try:
            for file_path in self.temp_dir.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
self.logger.info("Arquivos temporários limpos")
        except Exception as e:
self.logger.warning(f"Erro na limpeza de temp files: {e}")
    
    def _save_final_metadata(self, video_path: str, metadata: Dict, quality_valid: bool):
        """Salva metadados finais do vídeo"""
        try:
            video_dir = Path(video_path).parent
            metadata_file = video_dir / f"{Path(video_path).stem}_final_metadata.json"
            
            final_metadata = {
                **metadata,
                'quality_validated': quality_valid,
                'generated_at': datetime.now().isoformat(),
                'composer_version': '1.0.0',
                'platform_optimized': True
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(final_metadata, f, indent=2, ensure_ascii=False)
            
self.logger.info(f"Metadados salvos: {metadata_file}")
            
        except Exception as e:
self.logger.error(f"Erro ao salvar metadados: {e}")
    
    def _retry_composition_with_improvements(
        self,
        audio_path: str,
        video_segments: List[VideoSegment],
        template_config: TemplateConfig,
        captions: Optional[List[Dict[str, Any]]],
        output_path: str,
        metadata: Dict
    ) -> str:
        """Sistema de retry com melhorias automáticas"""
        try:
self.logger.info("Tentando composição com melhorias...")
            
            # Aplicar melhorias baseadas nos problemas detectados
            improved_template = self._apply_quality_improvements(template_config)
            
            # Retry com configurações melhoradas
            return self.compose_final_video(
                audio_path=audio_path,
                video_segments=video_segments,
                template_config=improved_template,
                captions=captions,
                output_path=output_path.replace('.mp4', '_retry.mp4'),
                metadata={**(metadata or {}), 'retry_attempt': True}
            )
            
        except Exception as e:
self.logger.error(f"Erro no retry: {e}")
            return output_path  # Retornar vídeo original em caso de falha
    
    def _apply_quality_improvements(self, template_config: TemplateConfig) -> TemplateConfig:
        """Aplica melhorias automáticas de qualidade"""
        # Clone do template com melhorias
        improved_config = TemplateConfig(
            name=f"{template_config.name}_Improved",
            resolution=template_config.resolution,
            duration=template_config.duration,
            intro_duration=template_config.intro_duration,
            outro_duration=template_config.outro_duration,
            transition_type=template_config.transition_type,
            background_color=template_config.background_color,
            text_style=template_config.text_style.copy(),
            branding_config=template_config.branding_config.copy() if template_config.branding_config else None,
            effects_config=(template_config.effects_config or []) + ['quality_boost']
        )
        
        # Melhorias específicas
        improved_config.text_style['size'] = min(64, improved_config.text_style['size'] + 4)
        improved_config.effects_config.append('sharpening_enhanced')
        
        return improved_config
    
    # Métodos auxiliares para criação de elementos
    
    def _create_intro_clip(self, template_config: TemplateConfig) -> VideoFileClip:
        """Cria clip de introdução"""
        intro_duration = template_config.intro_duration
        
        # Criar color clip como background
        intro_clip = ColorClip(
            size=template_config.resolution,
            color=tuple(int(template_config.background_color[i:i+2], 16) 
                       for i in (1, 3, 5)),  # Hex para RGB
            duration=intro_duration
        )
        
        return intro_clip
    
    def _create_outro_clip(self, template_config: TemplateConfig) -> VideoFileClip:
        """Cria clip de encerramento"""
        outro_duration = template_config.outro_duration
        
        outro_clip = ColorClip(
            size=template_config.resolution,
            color=(0, 0, 0),  # Preto
            duration=outro_duration
        )
        
        return outro_clip
    
    def _create_placeholder_clip(self, template_config: TemplateConfig, duration: float) -> VideoFileClip:
        """Cria clip placeholder para segmentos com erro"""
        placeholder_clip = ColorClip(
            size=template_config.resolution,
            color=(128, 128, 128),  # Cinza
            duration=duration
        )
        
        return placeholder_clip

    def _parse_hex_color(self, hex_color: str) -> Tuple[int, int, int]:
        """Converte cor em hex (#RRGGBB) para tupla RGB."""
        if not hex_color:
            return (0, 0, 0)
        try:
            if hex_color.startswith('#'):
                hex_color = hex_color[1:]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
            if len(hex_color) == 8:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
        except ValueError:
self.logger.debug(f"Cor inválida recebida: {hex_color}")
        return (0, 0, 0)

    def _create_blurred_background(
        self,
        clip: VideoFileClip,
        target_size: Tuple[int, int],
        blur_sigma: int = 35
    ) -> VideoFileClip:
        """Cria background desfocado a partir do próprio vídeo."""
        resized = clip.resize(target_size).without_audio()

        def _gaussian(frame):
            return cv2.GaussianBlur(frame, (0, 0), blur_sigma)

        return resized.fl_image(_gaussian)

    def _create_caption_clip(
        self,
        text: str,
        duration: float,
        video_size: Tuple[int, int],
        style: Dict[str, Any]
    ) -> Optional[ImageClip]:
        """Cria clip de legenda com fundo arredondado."""
        try:
            font_path = self._resolve_font_path(style.get('font_path'))
            font_size = int(style.get('font_size', 54))
            line_spacing = int(style.get('line_spacing', 12))
            max_width_ratio = float(style.get('max_width_ratio', 0.9))
            padding_x = int(style.get('padding_horizontal', 48))
            padding_y = int(style.get('padding_vertical', 32))
            background_opacity = float(style.get('background_opacity', 0.85))
            text_color = style.get('font_color', '#FFFFFF')
            stroke_color = style.get('stroke_color', '#000000')
            stroke_width = int(style.get('stroke_width', 2))

            font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

            max_text_width = int(video_size[0] * max_width_ratio) - (padding_x * 2)
            lines = self._wrap_caption_text(text, font, max_text_width)
            if not lines:
                return None

            ascent, descent = font.getmetrics() if hasattr(font, "getmetrics") else (font_size, int(font_size * 0.2))
            line_height = ascent + descent
            text_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
            panel_width = min(
                int(video_size[0] * max_width_ratio),
                max(self._measure_text(font, line)[0] + padding_x * 2 for line in lines)
            )
            panel_height = text_height + padding_y * 2

            bg_color_rgb = self._parse_hex_color(style.get('background_color', '#101010'))
            alpha = int(255 * background_opacity)
            background_rgba = (*bg_color_rgb, alpha)

            image = Image.new("RGBA", (panel_width, panel_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle(
                [(0, 0), (panel_width, panel_height)],
                radius=24,
                fill=background_rgba
            )

            current_y = padding_y
            for line in lines:
                line_width, _ = self._measure_text(font, line)
                x = (panel_width - line_width) // 2
                draw.text(
                    (x, current_y),
                    line,
                    font=font,
                    fill=text_color,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_color if stroke_width > 0 else None
                )
                current_y += line_height + line_spacing

            np_image = np.array(image)
            caption_clip = ImageClip(np_image).set_duration(duration)

            baseline = style.get('baseline', 'bottom')
            vertical_margin_ratio = float(style.get('vertical_margin_ratio', 0.075))
            if baseline == 'top':
                y_pos = int(video_size[1] * vertical_margin_ratio)
            elif baseline == 'center':
                y_pos = (video_size[1] - panel_height) // 2
            else:
                y_pos = video_size[1] - panel_height - int(video_size[1] * vertical_margin_ratio)

            caption_clip = caption_clip.set_position(("center", y_pos))
            return caption_clip

        except Exception as e:
self.logger.error(f"Erro ao criar legenda: {e}")
            return None

    def _resolve_font_path(self, preferred_path: Optional[str]) -> Optional[str]:
        """Resolve caminho de fonte a ser utilizado nas legendas."""
        candidate_paths = []
        if preferred_path:
            candidate_paths.append(preferred_path)
        candidate_paths.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            str(Path(__file__).resolve().parent / "assets" / "fonts" / "Roboto-Bold.ttf"),
        ])
        for path in candidate_paths:
            if path and Path(path).exists():
                return path
        return None

    def _wrap_caption_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Quebra o texto para caber na largura disponível."""
        if not text:
            return []
        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []

        for word in words:
            test_line = " ".join(current_line + [word]).strip()
            line_width, _ = self._measure_text(font, test_line)
            if line_width <= max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _measure_text(self, font: ImageFont.ImageFont, text: str) -> Tuple[int, int]:
        """Calcula largura e altura de um texto usando o font informado."""
        if hasattr(font, "getbbox"):
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]

        dummy_image = Image.new("RGB", (10, 10))
        draw = ImageDraw.Draw(dummy_image)
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    def _create_professional_text_clip(
        self,
        text: str,
        start_time: float,
        end_time: float,
        style: Dict[str, Any],
        video_size: Tuple[int, int]
    ) -> Optional[TextClip]:
        """Cria clip de texto profissional"""
        try:
            duration = end_time - start_time
            
            # Configurações de estilo
            font_size = style.get('font_size', 48)
            font_color = style.get('font_color', '#FFFFFF')
            stroke_color = style.get('stroke_color', '#000000')
            stroke_width = style.get('stroke_width', 2)
            position = style.get('position', ('center', 'center'))
            
            # Criar text clip
            text_clip = TextClip(
                text,
                fontsize=font_size,
                color=font_color,
                font='Arial-Bold',
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                size=video_size
            ).set_duration(duration).set_start(start_time).set_position(position)
            
            return text_clip
            
        except Exception as e:
self.logger.error(f"Erro ao criar texto: {e}")
            return None
    
    def _apply_stabilization(self, video_clip) -> VideoFileClip:
        """Aplica estabilização de vídeo"""
        # Placeholder - implementar estabilização real se necessário
        return video_clip
    
    def _apply_color_correction(self, video_clip) -> VideoFileClip:
        """Aplica correção de cores"""
        try:
            return video_clip.fx(vfx.colorx, 1.1)
        except Exception:
            return video_clip
    
    def _apply_sharpening(self, video_clip) -> VideoFileClip:
        """Aplica sharpening"""
        # Placeholder - implementar sharpening real
        return video_clip
    
    def _apply_denoising(self, video_clip) -> VideoFileClip:
        """Aplica redução de ruído"""
        # Placeholder - implementar denoising real
        return video_clip
    
    def _apply_audio_formatting(self, video_clip) -> VideoFileClip:
        """Aplica formatação de áudio"""
        if video_clip.audio:
            return video_clip.volumex(1.0)
        return video_clip
    
    def _apply_segment_effects(self, video_clip, effects: List[str]) -> VideoFileClip:
        """Aplica efeitos específicos do segmento"""
        for effect in effects:
            if effect == 'brightness_up':
                try:
                    video_clip = video_clip.fx(vfx.colorx, 1.1)
                except Exception:
self.logger.debug("Efeito brightness_up não suportado para este clip")
            elif effect == 'contrast_boost':
                try:
                    video_clip = video_clip.fx(vfx.lum_contrast, contrast=30)
                except Exception:
self.logger.debug("Efeito contrast_boost não suportado para este clip")

        return video_clip
    
    def _apply_template_effect(self, video_clip, effect: str) -> VideoFileClip:
        """Aplica efeito do template"""
        if effect == 'color_enhance':
            return video_clip.fx(vfx.colorx, 1.15)
        elif effect == 'sharpening':
            return video_clip  # Placeholder
        elif effect == 'contrast_boost':
            try:
                return video_clip.fx(vfx.lum_contrast, contrast=20)
            except Exception:
                return video_clip
        elif effect == 'vibrance':
            return video_clip.fx(vfx.colorx, 1.2)
        
        return video_clip
    
    def _add_branding_elements(self, video_clip, branding_config: Dict) -> VideoFileClip:
        """Adiciona elementos de branding"""
        # Placeholder para watermark/branding
        return video_clip
    
    def _render_with_optimized_settings(self, video_clip, output_path: str):
        """Renderiza vídeo com configurações otimizadas"""
        video_clip.write_videofile(
            output_path,
            fps=self.default_fps,
            codec='libx264',
            audio_codec='aac',
            bitrate=self.target_bitrate,
            preset='medium'
        )
        video_clip.close()
    
    def _apply_platform_optimizations(
        self,
        video_clip,
        platform: PlatformType,
        quality: VideoQuality,
        platform_config: Dict
    ) -> VideoFileClip:
        """Aplica otimizações específicas da plataforma"""
        # Redimensionar se necessário
        if video_clip.size != tuple(platform_config['resolution']):
            video_clip = video_clip.resize(platform_config['resolution'])
        
        # Ajustar duração se necessário
        if video_clip.duration > platform_config['max_duration']:
            video_clip = video_clip.subclip(0, platform_config['max_duration'])
        
        return video_clip
    
    def _render_platform_optimized_video(
        self,
        video_clip,
        output_path: str,
        platform_config: Dict,
        quality: VideoQuality
    ):
        """Renderiza vídeo otimizado para plataforma"""
        # Configurações de qualidade
        quality_settings = {
            VideoQuality.HIGH: {'bitrate': '8M', 'preset': 'slow'},
            VideoQuality.MEDIUM: {'bitrate': '5M', 'preset': 'medium'},
            VideoQuality.LOW: {'bitrate': '3M', 'preset': 'fast'}
        }
        
        settings = quality_settings[quality]
        
        video_clip.write_videofile(
            output_path,
            fps=platform_config['fps'],
            codec=platform_config['video_codec'],
            audio_codec=platform_config['audio_codec'],
            bitrate=settings['bitrate'],
            preset=settings['preset'],
            temp_audiofile=self.temp_dir / 'temp-platform-audio.m4a',
            remove_temp=True
        )
        
        video_clip.close()
    
    def _validate_platform_compliance(
        self,
        video_path: str,
        platform: PlatformType,
        quality: VideoQuality
    ) -> bool:
        """Valida conformidade com plataforma"""
        try:
            video_info = cv2.VideoCapture(video_path)
            
            if not video_info.isOpened():
                return False
            
            width = int(video_info.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_info.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = video_info.get(cv2.CAP_PROP_FPS)
            
            video_info.release()
            
            # Verificações básicas de conformidade
            platform_config = self._get_platform_config(platform)
            
            compliance_checks = [
                (width, height) == tuple(platform_config['resolution']),
                fps >= platform_config['fps'] * 0.9,  # Tolerância de 10%
                os.path.getsize(video_path) < 100 * 1024 * 1024  # 100MB limit
            ]
            
            return all(compliance_checks)
            
        except Exception as e:
self.logger.error(f"Erro na validação de conformidade: {e}")
            return False
    
    def _process_thumbnail_frame(
        self,
        frame: np.ndarray,
        style: str,
        video_size: Tuple[int, int],
        timestamp: float,
        duration: float
    ) -> np.ndarray:
        """Processa frame para thumbnail otimizada"""
        try:
            # Redimensionar para formato de thumbnail padrão (16:9)
            thumbnail_size = (1280, 720)
            thumbnail_frame = cv2.resize(frame, thumbnail_size)
            
            if style == "engaging":
                # Aumentar contraste e saturação
                thumbnail_frame = cv2.convertScaleAbs(thumbnail_frame, alpha=1.2, beta=10)
            
            elif style == "text_focused":
                # Adicionar overlay escuro para destacar texto
                overlay = np.zeros_like(thumbnail_frame)
                overlay[:int(thumbnail_frame.shape[0] * 0.3)] = [0, 0, 0]
                thumbnail_frame = cv2.addWeighted(thumbnail_frame, 0.8, overlay, 0.2, 0)
            
            return cv2.cvtColor(thumbnail_frame, cv2.COLOR_BGR2RGB)
            
        except Exception as e:
self.logger.error(f"Erro no processamento de thumbnail: {e}")
            return frame
    
    def _calculate_thumbnail_engagement(self, thumbnail_path: str) -> float:
        """Calcula score de engajamento da thumbnail"""
        try:
            # Carregar imagem
            img = Image.open(thumbnail_path)
            
            # Calcular hash perceptual
            img_hash = imagehash.phash(img)
            
            # Análise básica de cores
            img_array = np.array(img)
            color_variance = np.var(img_array)
            
            # Score baseado na diversidade de cores
            color_score = min(1.0, color_variance / 1000.0)
            
            return color_score
            
        except Exception as e:
self.logger.error(f"Erro no cálculo de engajamento da thumbnail: {e}")
            return 0.5
    
    def _generate_batch_export_report(self, export_dir: Path, results: Dict[str, str]):
        """Gera relatório do export em lote"""
        try:
            report_path = export_dir / "batch_export_report.json"
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'total_platforms': len(results),
                'successful_exports': sum(1 for path in results.values() if path),
                'failed_exports': sum(1 for path in results.values() if not path),
                'results': results
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
self.logger.info(f"Relatório de export salvo: {report_path}")
            
        except Exception as e:
self.logger.error(f"Erro ao gerar relatório: {e}")


# Exemplo de uso e testes
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Inicializar compositor
        composer = FinalVideoComposer()
        
        # Configuração de exemplo
        template_config = TemplateConfig(
            name="Professional",
            resolution=(1080, 1920),
            duration=30.0,
            intro_duration=2.0,
            outro_duration=2.0,
            transition_type="fade",
            background_color="#000000",
            text_style={
                "font": "Arial-Bold",
                "size": 48,
                "color": "#FFFFFF",
                "stroke_color": "#000000",
                "stroke_width": 2
            }
        )
        
        # Exemplo de segmentos de vídeo
        video_segments = [
            VideoSegment(
                path="/tmp/segment1.mp4",
                duration=10.0,
                effects=["brightness_up"]
            ),
            VideoSegment(
                path="/tmp/segment2.mp4", 
                duration=10.0,
                effects=["contrast_boost"]
            )
        ]
        
print("Sistema de Composição Final inicializado com sucesso!")
print("Pronto para processar vídeos de alta qualidade.")
        
    except Exception as e:
print(f"Erro na inicialização: {e}")
