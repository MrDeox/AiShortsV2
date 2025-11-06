"""
Video processing utilities using OpenCV and MoviePy
Utilitários de processamento de vídeo usando OpenCV e MoviePy
"""

import cv2
import numpy as np
try:
    from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoFileClip, ImageClip, concatenate_videoclips  # type: ignore
import os
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import tempfile
from PIL import Image
import logging
# Configurações inline para evitar dependências externas
VIDEO_PROCESSING = {
    'output_resolution': (1920, 1080),
    'output_fps': 30,
    'output_format': 'mp4',
    'codec': 'libx264',
    'audio_codec': 'aac',
    'video_bitrate': '2000k',
    'audio_bitrate': '128k',
    'temp_dir': '/tmp/aishorts',
    'max_workers': 4,
}

def get_config():
    """Retorna configurações como um dicionário."""
    return {
        'video_processing': VIDEO_PROCESSING,
        'paths': {
            'temp_dir': VIDEO_PROCESSING['temp_dir'],
            'output_dir': 'outputs/video'
        }
    }


class VideoProcessor:
    """
    Classe para processamento de vídeo usando OpenCV e MoviePy.
    
    Features:
    - Extração de frames
    - Redimensionamento e cortes
    - Aplicação de filtros
    - Concatenação de vídeos
    - Ajuste de qualidade
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o processador de vídeo.
        
        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or get_config()['video_processing']
        self.logger = logging.getLogger(__name__)
        
        # Configurações padrão
        self.output_resolution = self.config.get('output_resolution', (1920, 1080))
        self.output_fps = self.config.get('output_fps', 30)
        self.temp_dir = Path(self.config.get('temp_dir', tempfile.gettempdir()))
        self.temp_dir.mkdir(exist_ok=True)
    
    def extract_frames(self, video_path: str, output_dir: str, fps: float = 1.0) -> List[str]:
        """
        Extrai frames de um vídeo.
        
        Args:
            video_path: Caminho do vídeo
            output_dir: Diretório para salvar os frames
            fps: Frames por segundo para extração
            
        Returns:
            Lista de caminhos dos frames extraídos
        """
        try:
            # Abrir vídeo com OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
            
            # Obter propriedades do vídeo
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calcular frames a extrair
            frame_interval = int(original_fps / fps)
            
            # Criar diretório de saída
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            frame_paths = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extrair frame no intervalo correto
                if frame_count % frame_interval == 0:
                    # Salvar frame
                    frame_filename = f"frame_{extracted_count:06d}.jpg"
                    frame_path = output_path / frame_filename
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(str(frame_path))
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            
            self.logger.info(f"Extraídos {extracted_count} frames de {video_path}")
            return frame_paths
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair frames: {e}")
            return []
    
    def resize_video(self, input_path: str, output_path: str, resolution: Optional[Tuple[int, int]] = None) -> bool:
        """
        Redimensiona um vídeo.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho do vídeo de saída
            resolution: Resolução de destino (largura, altura)
            
        Returns:
            True se redimensionado com sucesso
        """
        try:
            # Usar resolução padrão se não especificada
            target_resolution = resolution or self.output_resolution
            
            # Carregar vídeo com MoviePy
            with VideoFileClip(input_path) as clip:
                # Redimensionar
                resized_clip = clip.resize(target_resolution)
                
                # Salvar
                resized_clip.write_videofile(
                    output_path,
                    fps=self.output_fps,
                    codec=self.config.get('codec', 'libx264'),
                    audio_codec=self.config.get('audio_codec', 'aac'),
                    temp_audiofile=self.temp_dir / 'temp-audio.m4a',
                    remove_temp=True
                )
            
            self.logger.info(f"Vídeo redimensionado: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao redimensionar vídeo: {e}")
            return False
    
    def crop_video(self, input_path: str, output_path: str, x: int, y: int, width: int, height: int) -> bool:
        """
        Recorta um vídeo.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho do vídeo de saída
            x, y: Posição inicial do recorte
            width, height: Dimensões do recorte
            
        Returns:
            True se recortado com sucesso
        """
        try:
            with VideoFileClip(input_path) as clip:
                # Recortar
                cropped_clip = clip.crop(x1=x, y1=y, x2=x+width, y2=y+height)
                
                # Salvar
                cropped_clip.write_videofile(
                    output_path,
                    fps=self.output_fps,
                    codec=self.config.get('codec', 'libx264'),
                    audio_codec=self.config.get('audio_codec', 'aac')
                )
            
            self.logger.info(f"Vídeo recortado: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao recortar vídeo: {e}")
            return False
    
    def apply_filters(self, video_path: str, output_path: str, filters: Dict[str, Any]) -> bool:
        """
        Aplica filtros ao vídeo.
        
        Args:
            video_path: Caminho do vídeo de entrada
            output_path: Caminho do vídeo de saída
            filters: Dicionário com filtros a aplicar
            
        Returns:
            True se filtrado com sucesso
        """
        try:
            with VideoFileClip(video_path) as clip:
                filtered_clip = clip
                
                # Aplicar brilho
                if 'brightness' in filters:
                    brightness = filters['brightness']
                    filtered_clip = filtered_clip.fx(lambda clip: clip.brightness(brightness))
                
                # Aplicar contraste
                if 'contrast' in filters:
                    contrast = filters['contrast']
                    filtered_clip = filtered_clip.fx(lambda clip: clip.contrast(contrast))
                
                # Aplicar saturação
                if 'saturation' in filters:
                    saturation = filters['saturation']
                    filtered_clip = filtered_clip.fx(lambda clip: clip.colorx(saturation))
                
                # Aplicar desfoque
                if 'blur' in filters:
                    blur_amount = filters['blur']
                    # Aplicar desfoque usando OpenCV
                    def apply_blur(get_frame, t):
                        frame = get_frame(t)
                        if len(frame.shape) == 3:
                            blurred = cv2.GaussianBlur(frame, (blur_amount*2+1, blur_amount*2+1), 0)
                            return blurred
                        return frame
                    
                    filtered_clip = filtered_clip.fl(apply_blur)
                
                # Salvar
                filtered_clip.write_videofile(
                    output_path,
                    fps=self.output_fps,
                    codec=self.config.get('codec', 'libx264'),
                    audio_codec=self.config.get('audio_codec', 'aac')
                )
            
            self.logger.info(f"Filtros aplicados: {video_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar filtros: {e}")
            return False
    
    def concatenate_videos(self, video_paths: List[str], output_path: str) -> bool:
        """
        Concatena múltiplos vídeos.
        
        Args:
            video_paths: Lista de caminhos dos vídeos
            output_path: Caminho do vídeo de saída
            
        Returns:
            True se concatenado com sucesso
        """
        try:
            clips = []
            
            # Carregar todos os clips
            for video_path in video_paths:
                if os.path.exists(video_path):
                    clip = VideoFileClip(video_path)
                    clips.append(clip)
                else:
                    self.logger.warning(f"Vídeo não encontrado: {video_path}")
            
            if not clips:
                raise ValueError("Nenhum vídeo válido encontrado para concatenação")
            
            # Concatenar
            final_clip = concatenate_videoclips(clips)
            
            # Salvar
            final_clip.write_videofile(
                output_path,
                fps=self.output_fps,
                codec=self.config.get('codec', 'libx264'),
                audio_codec=self.config.get('audio_codec', 'aac')
            )
            
            # Liberar memória
            for clip in clips:
                clip.close()
            final_clip.close()
            
            self.logger.info(f"Vídeos concatenados: {len(clips)} clips -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao concatenar vídeos: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """
        Obtém informações do vídeo.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Dicionário com informações do vídeo
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
                'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
            }
            
            cap.release()
            return info
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações do vídeo: {e}")
            return None
    
    def create_video_from_images(self, image_paths: List[str], output_path: str, duration_per_image: float = 3.0) -> bool:
        """
        Cria vídeo a partir de uma lista de imagens.
        
        Args:
            image_paths: Lista de caminhos das imagens
            output_path: Caminho do vídeo de saída
            duration_per_image: Duração de cada imagem em segundos
            
        Returns:
            True se criado com sucesso
        """
        try:
            clips = []
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    # Criar clip da imagem
                    clip = ImageClip(img_path, duration=duration_per_image)
                    
                    # Redimensionar para manter proporção
                    clip = clip.resize(self.output_resolution)
                    
                    clips.append(clip)
                else:
                    self.logger.warning(f"Imagem não encontrada: {img_path}")
            
            if not clips:
                raise ValueError("Nenhuma imagem válida encontrada")
            
            # Concatenar clips
            final_clip = concatenate_videoclips(clips)
            
            # Salvar
            final_clip.write_videofile(
                output_path,
                fps=self.output_fps,
                codec=self.config.get('codec', 'libx264'),
                audio_codec=self.config.get('audio_codec', 'aac')
            )
            
            # Liberar memória
            for clip in clips:
                clip.close()
            final_clip.close()
            
            self.logger.info(f"Vídeo criado a partir de {len(clips)} imagens")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar vídeo a partir de imagens: {e}")
            return False
    
    def add_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Adiciona áudio a um vídeo.
        
        Args:
            video_path: Caminho do vídeo
            audio_path: Caminho do áudio
            output_path: Caminho do vídeo de saída
            
        Returns:
            True se áudio adicionado com sucesso
        """
        try:
            from moviepy.audio.io.AudioArrayClip import AudioArrayClip
            
            with VideoFileClip(video_path) as video_clip:
                # Carregar áudio
                audio_clip = VideoFileClip(audio_path).audio
                
                # Ajustar duração do áudio para corresponder ao vídeo
                if audio_clip.duration > video_clip.duration:
                    audio_clip = audio_clip.subclip(0, video_clip.duration)
                elif audio_clip.duration < video_clip.duration:
                    # Repetir áudio se necessário
                    repeats = int(video_clip.duration / audio_clip.duration) + 1
                    audio_clip = concatenate_videoclips([audio_clip] * repeats).subclip(0, video_clip.duration)
                
                # Combinar vídeo e áudio
                final_clip = video_clip.set_audio(audio_clip)
                
                # Salvar
                final_clip.write_videofile(
                    output_path,
                    fps=self.output_fps,
                    codec=self.config.get('codec', 'libx264'),
                    audio_codec=self.config.get('audio_codec', 'aac')
                )
            
            self.logger.info(f"Áudio adicionado: {video_path} + {audio_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar áudio: {e}")
            return False


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar processador
    processor = VideoProcessor()
    
    # Teste com vídeo dummy (criar vídeo simples)
    test_video = "/tmp/test_video.mp4"
    
    try:
        # Obter informações do vídeo
        info = processor.get_video_info(test_video)
        if info:
            print(f"Informações do vídeo: {info}")
        
        # Extrair frames
        frames = processor.extract_frames(test_video, "/tmp/frames", fps=0.5)
        print(f"Frames extraídos: {len(frames)}")
        
        # Teste de redimensionamento
        resized_video = "/tmp/resized_video.mp4"
        success = processor.resize_video(test_video, resized_video, (1280, 720))
        print(f"Redimensionamento: {'Sucesso' if success else 'Falha'}")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
