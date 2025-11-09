"""
Final video generator for AI Shorts
Gerador final de vídeos para AI Shorts
"""

import os
import json
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import logging
from datetime import datetime

from moviepy.editor import (
    VideoFileClip, ImageClip, TextClip, concatenate_videoclips,
    CompositeVideoClip, CompositeAudioClip
)
from moviepy.audio.fx import volumex

from ..matching.content_matcher import ContentMatcher
from config.video_settings import VIDEO_GENERATION, get_config


class VideoGenerator:
    """
    Classe para geração final de vídeos do AI Shorts.
    
    Features:
    - Geração de vídeos a partir de conteúdo selecionado
    - Aplicação de transições e efeitos
    - Adição de texto e overlays
    - Otimização para diferentes plataformas
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o gerador de vídeo.
        
        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or get_config()['generation']
        self.logger = logging.getLogger(__name__)
        
        # Inicializar processador de vídeo
        # Importação local para evitar problemas de dependência circular
        from ..processing.video_processor import VideoProcessor
        self.video_processor = VideoProcessor()
        
        # Inicializar content matcher para automação
        self.content_matcher = ContentMatcher()
        
        # Configurações padrão
        self.target_resolution = self.config.get('output_resolution', (1080, 1920))  # Vertical para shorts
        self.target_duration = self.config.get('target_duration', 60)  # 1 minuto
        self.transitions = self.config.get('transitions', {})
        
        # Diretórios de trabalho
        self.work_dir = Path("/tmp/video_generation")
        self.work_dir.mkdir(exist_ok=True)
        
        # Cache para assets
        self.asset_cache = {}
    
    def generate_short_video(
        self, 
        content_sequence: List[Dict], 
        audio_path: Optional[str] = None,
        output_path: str = "output_short.mp4",
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Gera um vídeo short a partir de uma sequência de conteúdo.
        
        Args:
            content_sequence: Lista de dicionários com conteúdo (imagem/video + duração)
            audio_path: Caminho do arquivo de áudio (opcional)
            output_path: Caminho do vídeo de saída
            metadata: Metadados do vídeo
            
        Returns:
            True se gerado com sucesso
        """
        try:
self.logger.info(f"Iniciando geração de vídeo: {output_path}")
            
            # Validar sequência de conteúdo
            if not content_sequence:
                raise ValueError("Sequência de conteúdo vazia")
            
            # Criar clips de vídeo a partir do conteúdo
            video_clips = []
            
            for i, content_item in enumerate(content_sequence):
                clip = self._create_content_clip(content_item, i)
                if clip:
                    video_clips.append(clip)
            
            if not video_clips:
                raise ValueError("Nenhum clip de vídeo criado")
            
            # Aplicar transições entre clips
            final_clips = self._apply_transitions(video_clips)
            
            # Concatenar clips
            final_video = concatenate_videoclips(final_clips)
            
            # Redimensionar para formato short (vertical)
            final_video = final_video.resize(self.target_resolution)
            
            # Ajustar duração se necessário
            if final_video.duration > self.target_duration:
                final_video = final_video.subclip(0, self.target_duration)
            
            # Adicionar áudio se fornecido
            if audio_path and os.path.exists(audio_path):
                final_video = self._add_audio_track(final_video, audio_path)
            
            # Aplicar configurações finais
            final_video = self._apply_final_settings(final_video)
            
            # Salvar vídeo
            final_video.write_videofile(
                output_path,
                fps=30,  # FPS padrão para shorts
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=self.work_dir / 'temp-audio.m4a',
                remove_temp=True
            )
            
            # Fechar clips para liberar memória
            for clip in final_clips:
                clip.close()
            final_video.close()
            
            # Salvar metadados se fornecidos
            if metadata:
                self._save_metadata(output_path, metadata)
            
self.logger.info(f"Vídeo gerado com sucesso: {output_path}")
            return True
            
        except Exception as e:
self.logger.error(f"Erro ao gerar vídeo: {e}")
            return False
    
    def _create_content_clip(self, content_item: Dict, index: int) -> Optional[VideoFileClip]:
        """
        Cria um clip de vídeo a partir de um item de conteúdo.
        
        Args:
            content_item: Dicionário com informações do conteúdo
            index: Índice do item na sequência
            
        Returns:
            Clip de vídeo ou None se falhar
        """
        try:
            content_type = content_item.get('type', 'image')  # 'image' ou 'video'
            source_path = content_item.get('path')
            duration = content_item.get('duration', 3.0)
            
            if not source_path or not os.path.exists(source_path):
self.logger.warning(f"Arquivo não encontrado: {source_path}")
                return None
            
            if content_type == 'image':
                # Criar clip de imagem
                clip = ImageClip(source_path, duration=duration)
            elif content_type == 'video':
                # Carregar clip de vídeo
                clip = VideoFileClip(source_path)
                if clip.duration > duration:
                    clip = clip.subclip(0, duration)
                elif clip.duration < duration:
                    # Estender clip se necessário
                    clip = clip.loop(duration=duration)
            else:
                raise ValueError(f"Tipo de conteúdo não suportado: {content_type}")
            
            # Redimensionar para resolução alvo
            clip = clip.resize(self.target_resolution)
            
            # Adicionar texto se especificado
            if 'text' in content_item:
                text_clip = self._create_text_clip(content_item['text'], duration)
                if text_clip:
                    clip = CompositeVideoClip([clip, text_clip])
            
            return clip
            
        except Exception as e:
self.logger.error(f"Erro ao criar clip de conteúdo: {e}")
            return None
    
    def _create_text_clip(self, text_config: Dict, duration: float) -> Optional[TextClip]:
        """
        Cria um clip de texto.
        
        Args:
            text_config: Configurações do texto
            duration: Duração do texto
            
        Returns:
            Clip de texto ou None se falhar
        """
        try:
            text = text_config.get('content', '')
            if not text:
                return None
            
            # Configurações padrão do texto
            fontsize = text_config.get('font_size', self.config['text_overlay']['font_size'])
            fontcolor = text_config.get('font_color', self.config['text_overlay']['font_color'])
            bgcolor = text_config.get('background_color', self.config['text_overlay']['background_color'])
            
            # Posição
            position = text_config.get('position', ('center', 'center'))
            
            # Criar clip de texto
            text_clip = TextClip(
                text,
                fontsize=fontsize,
                color=fontcolor,
                font='Arial-Bold',
                size=self.target_resolution
            ).set_duration(duration).set_position(position)
            
            # Adicionar fundo semi-transparente se especificado
            if bgcolor:
                # Criar retângulo de fundo
                bg_clip = TextClip(
                    ' ' * len(text),
                    fontsize=fontsize,
                    color=bgcolor,
                    font='Arial-Bold'
                ).set_duration(duration).set_position(position)
                
                # Combinar texto e fundo
                text_clip = CompositeVideoClip([bg_clip, text_clip])
            
            return text_clip
            
        except Exception as e:
self.logger.error(f"Erro ao criar clip de texto: {e}")
            return None
    
    def _apply_transitions(self, clips: List[VideoFileClip]) -> List[VideoFileClip]:
        """
        Aplica transições entre clips.
        
        Args:
            clips: Lista de clips
            
        Returns:
            Lista de clips com transições aplicadas
        """
        if len(clips) <= 1:
            return clips
        
        try:
            # Implementar transições simples por enquanto
            # TODO: Implementar transições mais complexas
            
            fade_duration = self.transitions.get('fade_duration', 0.5)
            slide_duration = self.transitions.get('slide_duration', 0.3)
            
            processed_clips = [clips[0]]  # Primeiro clip sem transição
            
            for i in range(1, len(clips)):
                current_clip = clips[i]
                previous_clip = processed_clips[-1]
                
                # Aplicar fade in/out
                if fade_duration > 0:
                    current_clip = current_clip.fadein(fade_duration)
                    previous_clip = previous_clip.fadeout(fade_duration)
                
                processed_clips.append(current_clip)
            
            return processed_clips
            
        except Exception as e:
self.logger.error(f"Erro ao aplicar transições: {e}")
            return clips
    
    def _add_audio_track(self, video_clip: VideoFileClip, audio_path: str) -> VideoFileClip:
        """
        Adiciona faixa de áudio ao vídeo.
        
        Args:
            video_clip: Clip de vídeo
            audio_path: Caminho do áudio
            
        Returns:
            Clip de vídeo com áudio
        """
        try:
            audio_clip = VideoFileClip(audio_path).audio
            
            # Ajustar duração do áudio
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.subclip(0, video_clip.duration)
            elif audio_clip.duration < video_clip.duration:
                # Ajustar volume e repetir se necessário
                audio_clip = audio_clip.volumex(0.5)  # Reduzir volume
                repeats = int(video_clip.duration / audio_clip.duration) + 1
                audio_clips = [audio_clip] * repeats
                audio_clip = concatenate_videoclips(audio_clips).subclip(0, video_clip.duration)
            
            # Definir áudio no vídeo
            final_clip = video_clip.set_audio(audio_clip)
            
            # Fechar clip de áudio
            audio_clip.close()
            
            return final_clip
            
        except Exception as e:
self.logger.error(f"Erro ao adicionar áudio: {e}")
            return video_clip
    
    def _apply_final_settings(self, video_clip: VideoFileClip) -> VideoFileClip:
        """
        Aplica configurações finais ao vídeo.
        
        Args:
            video_clip: Clip de vídeo
            
        Returns:
            Clip com configurações aplicadas
        """
        try:
            # Ajustar FPS se necessário
            target_fps = 30
            if video_clip.fps != target_fps:
                video_clip = video_clip.set_fps(target_fps)
            
            # Otimizar para diferentes plataformas
            # TODO: Adicionar configurações específicas por plataforma
            
            return video_clip
            
        except Exception as e:
self.logger.error(f"Erro ao aplicar configurações finais: {e}")
            return video_clip
    
    def _save_metadata(self, video_path: str, metadata: Dict):
        """
        Salva metadados do vídeo em arquivo JSON.
        
        Args:
            video_path: Caminho do vídeo
            metadata: Metadados a salvar
        """
        try:
            video_dir = Path(video_path).parent
            metadata_file = video_dir / f"{Path(video_path).stem}_metadata.json"
            
            # Adicionar informações técnicas
            tech_info = {
                'generated_at': datetime.now().isoformat(),
                'target_resolution': self.target_resolution,
                'target_duration': self.target_duration,
                'generator_version': '1.0.0'
            }
            
            final_metadata = {**metadata, 'technical_info': tech_info}
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(final_metadata, f, indent=2, ensure_ascii=False)
            
self.logger.info(f"Metadados salvos: {metadata_file}")
            
        except Exception as e:
self.logger.error(f"Erro ao salvar metadados: {e}")
    
    def optimize_for_platform(self, video_path: str, platform: str, output_path: str) -> bool:
        """
        Otimiza vídeo para uma plataforma específica.
        
        Args:
            video_path: Caminho do vídeo original
            platform: Plataforma alvo ('youtube', 'tiktok', 'instagram', etc.)
            output_path: Caminho do vídeo otimizado
            
        Returns:
            True se otimizado com sucesso
        """
        try:
            # Configurações por plataforma
            platform_configs = {
                'youtube': {
                    'resolution': (1920, 1080),
                    'fps': 30,
                    'duration_limit': 600,  # 10 minutos
                },
                'tiktok': {
                    'resolution': (1080, 1920),
                    'fps': 30,
                    'duration_limit': 60,  # 1 minuto
                },
                'instagram': {
                    'resolution': (1080, 1920),
                    'fps': 30,
                    'duration_limit': 60,  # 1 minuto
                }
            }
            
            if platform not in platform_configs:
                raise ValueError(f"Plataforma não suportada: {platform}")
            
            config = platform_configs[platform]
            
            with VideoFileClip(video_path) as clip:
                # Redimensionar se necessário
                if clip.size != config['resolution']:
                    clip = clip.resize(config['resolution'])
                
                # Ajustar duração se necessário
                if clip.duration > config['duration_limit']:
                    clip = clip.subclip(0, config['duration_limit'])
                
                # Salvar vídeo otimizado
                clip.write_videofile(
                    output_path,
                    fps=config['fps'],
                    codec='libx264',
                    audio_codec='aac'
                )
            
self.logger.info(f"Vídeo otimizado para {platform}: {output_path}")
            return True
            
        except Exception as e:
self.logger.error(f"Erro ao otimizar para {platform}: {e}")
            return False
    
    def create_slideshow(self, images: List[str], output_path: str, duration_per_slide: float = 3.0) -> bool:
        """
        Cria um vídeo slideshow a partir de imagens.
        
        Args:
            images: Lista de caminhos das imagens
            output_path: Caminho do vídeo de saída
            duration_per_slide: Duração de cada slide
            
        Returns:
            True se criado com sucesso
        """
        try:
            return self.video_processor.create_video_from_images(
                images, output_path, duration_per_slide
            )
        except Exception as e:
self.logger.error(f"Erro ao criar slideshow: {e}")
            return False


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar gerador
    generator = VideoGenerator()
    
    # Teste com conteúdo dummy
    test_content = [
        {
            'type': 'image',
            'path': '/tmp/test_image1.jpg',
            'duration': 3.0,
            'text': {'content': 'Slide 1', 'position': ('center', 'bottom')}
        },
        {
            'type': 'image',
            'path': '/tmp/test_image2.jpg',
            'duration': 3.0,
            'text': {'content': 'Slide 2', 'position': ('center', 'bottom')}
        }
    ]
    
    try:
        # Gerar vídeo
        success = generator.generate_short_video(
            content_sequence=test_content,
            output_path="/tmp/generated_short.mp4",
            metadata={'title': 'Teste AI Shorts', 'category': 'demo'}
        )
        
print(f"Geração de vídeo: {'Sucesso' if success else 'Falha'}")
        
        # Otimizar para TikTok
        if success:
            optimized_path = "/tmp/tiktok_optimized.mp4"
            optimized = generator.optimize_for_platform(
                "/tmp/generated_short.mp4", 
                "tiktok", 
                optimized_path
            )
print(f"Otimização para TikTok: {'Sucesso' if optimized else 'Falha'}")
        
    except Exception as e:
print(f"Erro durante o teste: {e}")
