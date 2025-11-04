# -*- coding: utf-8 -*-
"""
Processador de segmentos de vídeo usando FFmpeg.
"""

import os
import subprocess
import tempfile
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from loguru import logger

from aishorts_v2.src.utils.exceptions import (
    VideoProcessingError,
    VideoUnavailableError,
    ErrorHandler
)


class SegmentProcessor:
    """
    Processador de segmentos de vídeo usando FFmpeg.
    
    Capabilities:
    - Extração de segmentos de vídeo
    - Normalização de formato de vídeo
    - Obtenção de informações de vídeo
    - Conversão de codecs e resoluções
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Inicializa o processador.
        
        Args:
            temp_dir: Diretório temporário para processamento
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "aishorts_processor"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Verificar se FFmpeg está disponível
        self._check_ffmpeg()
        
        logger.info(f"SegmentProcessor inicializado - Temp: {self.temp_dir}")
    
    def _check_ffmpeg(self):
        """Verifica se FFmpeg está instalado e disponível."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                raise VideoProcessingError("FFmpeg não está funcionando corretamente")
            
            # Extrair versão do FFmpeg
            version_line = result.stdout.split('\n')[0]
            logger.info(f"FFmpeg encontrado: {version_line}")
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            raise VideoProcessingError(
                "FFmpeg não está instalado ou não está no PATH do sistema",
                ffmpeg_error=str(e)
            )
    
    def extract_segment(self, video_path: str, start: float, duration: float, 
                       output_path: Optional[str] = None) -> str:
        """
        Extrai um segmento de vídeo.
        
        Args:
            video_path: Caminho para o vídeo de origem
            start: Tempo de início em segundos
            duration: Duração do segmento em segundos
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho para o arquivo de segmento gerado
            
        Raises:
            VideoProcessingError: Se houver erro no processamento
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise VideoProcessingError(f"Vídeo não encontrado: {video_path}")
        
        if not output_path:
            output_path = self.temp_dir / f"segment_{start}_{duration}s.mp4"
        else:
            output_path = Path(output_path)
        
        logger.info(f"Extraindo segmento: {video_path} ({start}s, {duration}s)")
        
        # Validar parâmetros
        if start < 0:
            raise ValueError(f"Tempo de início deve ser positivo: {start}")
        if duration <= 0:
            raise ValueError(f"Duração deve ser positiva: {duration}")
        
        # Comando FFmpeg para extração de segmento
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-ss', str(start),           # Start time
            '-t', str(duration),         # Duration
            '-c:v', 'libx264',          # Video codec
            '-c:a', 'aac',              # Audio codec
            '-preset', 'fast',          # Encoding preset
            '-crf', '23',               # Quality (lower = better)
            '-movflags', '+faststart',  # Optimize for streaming
            '-y',                       # Overwrite output
            str(output_path)
        ]
        
        def _extract():
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode != 0:
                error_msg = f"FFmpeg error: {result.stderr}"
                logger.error(error_msg)
                raise VideoProcessingError(
                    f"Erro na extração do segmento: {error_msg}",
                    video_path=str(video_path),
                    ffmpeg_error=result.stderr
                )
            
            if not output_path.exists():
                raise VideoProcessingError(
                    f"Arquivo de saída não foi criado: {output_path}"
                )
            
            return str(output_path)
        
        try:
            output_file = ErrorHandler.retry_with_backoff(
                _extract,
                max_retries=2,
                delay=1.0,
                context=f"extract_segment: {video_path} ({start}s, {duration}s)"
            )
            
            logger.info(f"Segmento extraído com sucesso: {output_file}")
            return output_file
            
        except Exception as e:
            error_msg = f"Erro na extração do segmento: {str(e)}"
            logger.error(error_msg)
            raise VideoProcessingError(error_msg, video_path=str(video_path))
    
    def normalize_video(self, segment_path: str, target_format: str = "mp4",
                       target_resolution: str = "720p", target_fps: int = 30,
                       output_path: Optional[str] = None) -> str:
        """
        Normaliza formato, resolução e FPS do vídeo.
        
        Args:
            segment_path: Caminho para o segmento
            target_format: Formato de saída (mp4, mov, avi)
            target_resolution: Resolução alvo (720p, 1080p, 480p)
            target_fps: FPS alvo
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho para o vídeo normalizado
            
        Raises:
            VideoProcessingError: Se houver erro no processamento
        """
        segment_path = Path(segment_path)
        if not segment_path.exists():
            raise VideoProcessingError(f"Segmento não encontrado: {segment_path}")
        
        if not output_path:
            output_path = self.temp_dir / f"normalized_{segment_path.stem}.{target_format}"
        else:
            output_path = Path(output_path)
        
        logger.info(f"Normalizando vídeo: {segment_path}")
        
        # Mapear resolução para dimensões
        resolution_map = {
            "480p": {"width": 854, "height": 480},
            "720p": {"width": 1280, "height": 720},
            "1080p": {"width": 1920, "height": 1080},
        }
        
        if target_resolution not in resolution_map:
            raise ValueError(f"Resolução não suportada: {target_resolution}. Use: {list(resolution_map.keys())}")
        
        dimensions = resolution_map[target_resolution]
        
        # Comando FFmpeg para normalização
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', str(segment_path),
            '-vf', f'scale={dimensions["width"]}:{dimensions["height"]}:force_original_aspect_ratio=decrease,'
                   f'pad={dimensions["width"]}:{dimensions["height"]}:(ow-iw)/2:(oh-ih)/2:black',
            '-r', str(target_fps),              # Frame rate
            '-c:v', 'libx264',                 # Video codec
            '-preset', 'fast',                 # Encoding preset
            '-crf', '23',                      # Quality
            '-c:a', 'aac',                     # Audio codec
            '-b:a', '128k',                    # Audio bitrate
            '-movflags', '+faststart',         # Optimize for streaming
            '-y',                              # Overwrite output
            str(output_path)
        ]
        
        def _normalize():
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode != 0:
                error_msg = f"FFmpeg error: {result.stderr}"
                logger.error(error_msg)
                raise VideoProcessingError(
                    f"Erro na normalização: {error_msg}",
                    video_path=str(segment_path),
                    ffmpeg_error=result.stderr
                )
            
            if not output_path.exists():
                raise VideoProcessingError(
                    f"Arquivo normalizado não foi criado: {output_path}"
                )
            
            return str(output_path)
        
        try:
            output_file = ErrorHandler.retry_with_backoff(
                _normalize,
                max_retries=2,
                delay=1.0,
                context=f"normalize_video: {segment_path}"
            )
            
            logger.info(f"Vídeo normalizado com sucesso: {output_file}")
            return output_file
            
        except Exception as e:
            error_msg = f"Erro na normalização: {str(e)}"
            logger.error(error_msg)
            raise VideoProcessingError(error_msg, video_path=str(segment_path))
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas do vídeo.
        
        Args:
            video_path: Caminho para o vídeo
            
        Returns:
            Dicionário com informações do vídeo
            
        Raises:
            VideoProcessingError: Se houver erro na análise
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise VideoProcessingError(f"Vídeo não encontrado: {video_path}")
        
        logger.info(f"Analisando vídeo: {video_path}")
        
        # Comando FFprobe para obter informações
        ffprobe_cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        
        try:
            result = subprocess.run(
                ffprobe_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise VideoProcessingError(f"Erro no FFprobe: {result.stderr}")
            
            import json
            probe_data = json.loads(result.stdout)
            
            # Extrair informações relevantes
            video_info = {
                'file_path': str(video_path),
                'file_size': video_path.stat().st_size,
                'format': probe_data.get('format', {}),
                'streams': probe_data.get('streams', []),
            }
            
            # Encontrar stream de vídeo
            video_stream = None
            audio_stream = None
            
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            # Informações específicas do vídeo
            if video_stream:
                video_info['video_stream'] = {
                    'codec': video_stream.get('codec_name'),
                    'width': video_stream.get('width'),
                    'height': video_stream.get('height'),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),  # Parse fraction
                    'duration': video_stream.get('duration'),
                    'bit_rate': video_stream.get('bit_rate'),
                }
            
            # Informações específicas do áudio
            if audio_stream:
                video_info['audio_stream'] = {
                    'codec': audio_stream.get('codec_name'),
                    'sample_rate': audio_stream.get('sample_rate'),
                    'channels': audio_stream.get('channels'),
                    'duration': audio_stream.get('duration'),
                    'bit_rate': audio_stream.get('bit_rate'),
                }
            
            # Informações gerais
            format_info = probe_data.get('format', {})
            video_info['general'] = {
                'duration': float(format_info.get('duration', 0)),
                'bit_rate': format_info.get('bit_rate'),
                'format_name': format_info.get('format_name'),
                'format_long_name': format_info.get('format_long_name'),
            }
            
            logger.info(f"Análise concluída: {video_info['general']['duration']:.1f}s, "
                       f"{video_info['video_stream']['width']}x{video_info['video_stream']['height']}")
            
            return video_info
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            error_msg = f"Erro na análise do vídeo: {str(e)}"
            logger.error(error_msg)
            raise VideoProcessingError(error_msg, video_path=str(video_path))
        except json.JSONDecodeError as e:
            error_msg = f"Erro ao parsear JSON do FFprobe: {str(e)}"
            raise VideoProcessingError(error_msg, video_path=str(video_path))
    
    def get_video_duration(self, video_path: str) -> float:
        """
        Obtém apenas a duração do vídeo (método rápido).
        
        Args:
            video_path: Caminho para o vídeo
            
        Returns:
            Duração em segundos
        """
        try:
            info = self.get_video_info(video_path)
            return info['general']['duration']
        except Exception as e:
            logger.warning(f"Erro ao obter duração de {video_path}: {e}")
            return 0.0
    
    def cleanup_temp_files(self):
        """Limpa arquivos temporários."""
        try:
            temp_files = list(self.temp_dir.glob("*"))
            cleaned = 0
            
            for file_path in temp_files:
                if file_path.is_file():
                    file_path.unlink()
                    cleaned += 1
            
            logger.info(f"Limpeza concluída: {cleaned} arquivos removidos")
            
        except Exception as e:
            logger.warning(f"Erro durante limpeza: {str(e)}")


if __name__ == "__main__":
    # Teste básico do processador
    print("=== Teste do SegmentProcessor ===")
    
    processor = SegmentProcessor()
    
    try:
        # Teste de obtenção de informações (se houver um vídeo de teste)
        test_video = "./test_video.mp4"
        
        if Path(test_video).exists():
            print(f"\n1. Testando análise de vídeo: {test_video}")
            info = processor.get_video_info(test_video)
            print(f"Duração: {info['general']['duration']:.1f}s")
            if info.get('video_stream'):
                print(f"Resolução: {info['video_stream']['width']}x{info['video_stream']['height']}")
                print(f"FPS: {info['video_stream']['fps']:.1f}")
        else:
            print(f"\nVídeo de teste não encontrado: {test_video}")
        
        print("\n=== Teste concluído ===")
        
    except Exception as e:
        print(f"Erro durante teste: {e}")
        ErrorHandler.handle_error(e, "teste_segment_processor")
    
    finally:
        # Limpeza
        processor.cleanup_temp_files()