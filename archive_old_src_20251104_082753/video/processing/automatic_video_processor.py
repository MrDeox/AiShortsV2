"""
Processador automático de vídeos para qualidade profissional
Automatic Video Processor for Professional Quality

Sistema completo de processamento que:
- Converte vídeos para formato vertical 1080x1920
- Aplica filtros de melhoria de qualidade
- Processa múltiplos vídeos em lote
- Sistema de cache para otimização
"""

import cv2
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip
import os
import json
import hashlib
import time
from typing import List, Dict, Tuple, Optional, Any, Union
from pathlib import Path
import tempfile
from PIL import Image, ImageEnhance
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime, timedelta
import shutil

from .video_processor import VideoProcessor
from config.video_settings import VIDEO_PROCESSING, get_config


class AutomaticVideoProcessor:
    """
    Processador automático de vídeos com foco em qualidade profissional.
    
    Funcionalidades:
    - Conversão para formato vertical 1080x1920
    - Filtros de melhoria (sharpening, denoising, color correction)
    - Batch processing para múltiplos vídeos
    - Sistema de cache inteligente
    - Otimização para diferentes plataformas
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o processador automático.
        
        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or get_config()
        self.base_processor = VideoProcessor(config)
        self.logger = logging.getLogger(__name__)
        
        # Configurações específicas para processamento automático
        self.target_resolution = (1080, 1920)  # Formato vertical
        self.vertical_profile = {
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'video_bitrate': '4000k',
            'audio_bitrate': '192k'
        }
        
        # Sistema de cache
        self.cache_dir = Path(self.config['paths']['cache_dir']) / "processed_videos"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = self.config['cache']['ttl']  # 24 horas
        
        # Thread pool para processamento paralelo
        self.max_workers = self.config['video_processing'].get('max_workers', 4)
        
        # Lock para thread safety
        self._lock = threading.Lock()
        
        # Estatísticas de processamento
        self.stats = {
            'processed_videos': 0,
            'cached_videos': 0,
            'total_processing_time': 0,
            'average_processing_time': 0
        }
    
    def _generate_cache_key(self, video_path: str, process_type: str, params: Dict) -> str:
        """
        Gera uma chave única para cache baseada no arquivo e parâmetros.
        
        Args:
            video_path: Caminho do vídeo
            process_type: Tipo de processamento
            params: Parâmetros do processamento
            
        Returns:
            Chave única para cache
        """
        # Criar hash do arquivo
        file_stat = os.stat(video_path)
        file_info = f"{video_path}_{file_stat.st_mtime}_{file_stat.st_size}"
        
        # Criar hash dos parâmetros
        params_str = json.dumps(params, sort_keys=True)
        content = f"{file_info}_{process_type}_{params_str}"
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """
        Verifica se o cache ainda é válido.
        
        Args:
            cache_path: Caminho do arquivo em cache
            
        Returns:
            True se cache é válido
        """
        if not cache_path.exists():
            return False
        
        # Verificar TTL
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - file_time < timedelta(seconds=self.cache_ttl)
    
    def _save_processing_result(self, cache_key: str, result: Dict) -> None:
        """
        Salva resultado do processamento em cache.
        
        Args:
            cache_key: Chave do cache
            result: Resultado a ser salvo
        """
        cache_path = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def _load_processing_result(self, cache_key: str) -> Optional[Dict]:
        """
        Carrega resultado do cache se disponível.
        
        Args:
            cache_key: Chave do cache
            
        Returns:
            Resultado em cache ou None
        """
        cache_path = self.cache_dir / f"{cache_key}.json"
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                self.logger.info(f"Cache hit para {cache_key}")
                return result
            except Exception as e:
                self.logger.warning(f"Erro ao carregar cache {cache_key}: {e}")
        
        return None
    
    def process_video_segment(self, video_path: str, target_duration: float, start_time: float = 0) -> Optional[str]:
        """
        Processa um segmento específico do vídeo com qualidade profissional.
        
        Args:
            video_path: Caminho do vídeo original
            target_duration: Duração alvo em segundos
            start_time: Tempo inicial do segmento
            
        Returns:
            Caminho do vídeo processado ou None
        """
        start_processing = time.time()
        
        # Parâmetros para cache
        cache_params = {
            'target_duration': target_duration,
            'start_time': start_time,
            'target_resolution': self.target_resolution
        }
        
        cache_key = self._generate_cache_key(video_path, 'segment', cache_params)
        
        # Verificar cache
        cached_result = self._load_processing_result(cache_key)
        if cached_result:
            with self._lock:
                self.stats['cached_videos'] += 1
            return cached_result.get('output_path')
        
        try:
            # Carregar vídeo
            with VideoFileClip(video_path) as clip:
                # Extrair segmento
                end_time = min(start_time + target_duration, clip.duration)
                segment = clip.subclip(start_time, end_time)
                
                # Processar segmento
                processed_segment = self._apply_professional_filters(segment)
                
                # Salvar em arquivo temporário
                temp_output = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_output_path = temp_output.name
                temp_output.close()
                
                # Renderizar
                processed_segment.write_videofile(
                    temp_output_path,
                    fps=self.vertical_profile['fps'],
                    codec='libx264',
                    audio_codec='aac',
                    video_bitrate=self.vertical_profile['video_bitrate'],
                    audio_bitrate=self.vertical_profile['audio_bitrate'],
                    temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                    remove_temp=True
                )
                
                # Limpar
                segment.close()
            
            # Salvar em cache
            result = {
                'output_path': temp_output_path,
                'processing_time': time.time() - start_processing,
                'metadata': {
                    'duration': end_time - start_time,
                    'resolution': self.target_resolution,
                    'processed_at': datetime.now().isoformat()
                }
            }
            
            self._save_processing_result(cache_key, result)
            
            # Atualizar estatísticas
            processing_time = time.time() - start_processing
            with self._lock:
                self.stats['processed_videos'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['average_processing_time'] = (
                    self.stats['total_processing_time'] / self.stats['processed_videos']
                )
            
            self.logger.info(f"Segmento processado: {temp_output_path} em {processing_time:.2f}s")
            return temp_output_path
            
        except Exception as e:
            self.logger.error(f"Erro ao processar segmento: {e}")
            return None
    
    def normalize_to_vertical(self, video_path: str) -> Optional[str]:
        """
        Converte vídeo para formato vertical 1080x1920.
        
        Args:
            video_path: Caminho do vídeo original
            
        Returns:
            Caminho do vídeo convertido ou None
        """
        start_processing = time.time()
        
        # Parâmetros para cache
        cache_params = {
            'target_resolution': self.target_resolution,
            'output_quality': 'professional'
        }
        
        cache_key = self._generate_cache_key(video_path, 'vertical', cache_params)
        
        # Verificar cache
        cached_result = self._load_processing_result(cache_key)
        if cached_result:
            with self._lock:
                self.stats['cached_videos'] += 1
            return cached_result.get('output_path')
        
        try:
            with VideoFileClip(video_path) as clip:
                original_width, original_height = clip.size
                
                # Converter para vertical mantendo proporção
                if original_width > original_height:
                    # Vídeo horizontal - criar vídeo vertical
                    new_width = self.vertical_profile['width']
                    new_height = self.vertical_profile['height']
                    
                    # Calcular escala e posição
                    scale = min(new_width / original_width, new_height / original_height)
                    scaled_width = int(original_width * scale)
                    scaled_height = int(original_height * scale)
                    
                    # Redimensionar
                    resized_clip = clip.resize((scaled_width, scaled_height))
                    
                    # Centrar em fundo preto
                    background = resized_clip.on_color(
                        size=(new_width, new_height),
                        color=(0, 0, 0),
                        pos=('center', 'center')
                    )
                    
                    processed_clip = background
                    
                else:
                    # Vídeo vertical ou quadrado
                    processed_clip = clip.resize(self.target_resolution)
                
                # Aplicar filtros profissionais
                processed_clip = self._apply_professional_filters(processed_clip)
                
                # Salvar
                temp_output = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_output_path = temp_output.name
                temp_output.close()
                
                processed_clip.write_videofile(
                    temp_output_path,
                    fps=self.vertical_profile['fps'],
                    codec='libx264',
                    audio_codec='aac',
                    video_bitrate=self.vertical_profile['video_bitrate'],
                    audio_bitrate=self.vertical_profile['audio_bitrate'],
                    temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                    remove_temp=True
                )
                
                processed_clip.close()
            
            # Salvar em cache
            result = {
                'output_path': temp_output_path,
                'processing_time': time.time() - start_processing,
                'original_size': (original_width, original_height),
                'new_size': self.target_resolution,
                'processed_at': datetime.now().isoformat()
            }
            
            self._save_processing_result(cache_key, result)
            
            # Atualizar estatísticas
            processing_time = time.time() - start_processing
            with self._lock:
                self.stats['processed_videos'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['average_processing_time'] = (
                    self.stats['total_processing_time'] / self.stats['processed_videos']
                )
            
            self.logger.info(f"Vídeo convertido para vertical: {temp_output_path}")
            return temp_output_path
            
        except Exception as e:
            self.logger.error(f"Erro ao converter para vertical: {e}")
            return None
    
    def enhance_quality(self, video_path: str) -> Optional[str]:
        """
        Aplica filtros de melhoria para qualidade profissional.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Caminho do vídeo melhorado ou None
        """
        start_processing = time.time()
        
        # Parâmetros para cache
        cache_params = {
            'enhancement_type': 'professional',
            'target_quality': 'high'
        }
        
        cache_key = self._generate_cache_key(video_path, 'enhancement', cache_params)
        
        # Verificar cache
        cached_result = self._load_processing_result(cache_key)
        if cached_result:
            with self._lock:
                self.stats['cached_videos'] += 1
            return cached_result.get('output_path')
        
        try:
            with VideoFileClip(video_path) as clip:
                # Aplicar filtros de melhoria
                enhanced_clip = self._apply_professional_filters(clip)
                
                # Salvar
                temp_output = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_output_path = temp_output.name
                temp_output.close()
                
                enhanced_clip.write_videofile(
                    temp_output_path,
                    fps=self.vertical_profile['fps'],
                    codec='libx264',
                    audio_codec='aac',
                    video_bitrate=self.vertical_profile['video_bitrate'],
                    audio_bitrate=self.vertical_profile['audio_bitrate'],
                    temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                    remove_temp=True
                )
                
                enhanced_clip.close()
            
            # Salvar em cache
            result = {
                'output_path': temp_output_path,
                'processing_time': time.time() - start_processing,
                'enhancement_applied': True,
                'processed_at': datetime.now().isoformat()
            }
            
            self._save_processing_result(cache_key, result)
            
            # Atualizar estatísticas
            processing_time = time.time() - start_processing
            with self._lock:
                self.stats['processed_videos'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['average_processing_time'] = (
                    self.stats['total_processing_time'] / self.stats['processed_videos']
                )
            
            self.logger.info(f"Qualidade melhorada: {temp_output_path}")
            return temp_output_path
            
        except Exception as e:
            self.logger.error(f"Erro ao melhorar qualidade: {e}")
            return None
    
    def _apply_professional_filters(self, clip: VideoFileClip) -> VideoFileClip:
        """
        Aplica filtros profissionais ao clip.
        
        Args:
            clip: Clip do MoviePy
            
        Returns:
            Clip com filtros aplicados
        """
        try:
            # Função para aplicar filtros frame a frame
            def apply_filters(get_frame, t):
                frame = get_frame(t)
                
                if len(frame.shape) == 3:
                    # Converter para OpenCV format (BGR)
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # 1. Redução de ruído
                    denoised = cv2.fastNlMeansDenoisingColored(frame_bgr, None, 10, 10, 7, 21)
                    
                    # 2. Sharpening
                    kernel_sharpen = np.array([[-1,-1,-1],
                                              [-1, 9,-1],
                                              [-1,-1,-1]])
                    sharpened = cv2.filter2D(denoised, -1, kernel_sharpen)
                    
                    # 3. Melhorar contraste e brilho
                    alpha = 1.1  # Contraste
                    beta = 10    # Brilho
                    enhanced = cv2.convertScaleAbs(sharpened, alpha=alpha, beta=beta)
                    
                    # Converter de volta para RGB
                    frame_processed = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
                    return frame_processed
                
                return frame
            
            # Aplicar filtros
            filtered_clip = clip.fl(apply_filters)
            
            return filtered_clip
            
        except Exception as e:
            self.logger.warning(f"Erro ao aplicar filtros profissionais: {e}")
            return clip
    
    def extract_frames_for_analysis(self, video_path: str, num_frames: int = 5) -> List[str]:
        """
        Extrai frames para análise de qualidade.
        
        Args:
            video_path: Caminho do vídeo
            num_frames: Número de frames a extrair
            
        Returns:
            Lista de caminhos dos frames extraídos
        """
        try:
            with VideoFileClip(video_path) as clip:
                duration = clip.duration
                
                # Calcular intervalos para extração uniforme
                if num_frames <= 1:
                    times = [duration / 2]  # Frame do meio
                else:
                    interval = duration / (num_frames + 1)
                    times = [interval * (i + 1) for i in range(num_frames)]
                
                frame_paths = []
                
                for i, time_in_clip in enumerate(times):
                    # Extrair frame
                    frame = clip.get_frame(time_in_clip)
                    
                    # Converter para PIL Image e salvar
                    frame_pil = Image.fromarray(frame)
                    
                    # Melhorar qualidade do frame
                    enhancer = ImageEnhance.Sharpness(frame_pil)
                    frame_pil = enhancer.enhance(1.2)
                    
                    # Salvar frame
                    frame_filename = f"analysis_frame_{i:02d}_{int(time_in_clip*1000)}ms.jpg"
                    frame_path = self.cache_dir / frame_filename
                    
                    frame_pil.save(frame_path, quality=95, optimize=True)
                    frame_paths.append(str(frame_path))
                
                self.logger.info(f"Extraídos {len(frame_paths)} frames para análise")
                return frame_paths
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair frames: {e}")
            return []
    
    def batch_process_videos(self, video_list: List[str], operations: List[str] = None) -> Dict[str, str]:
        """
        Processa múltiplos vídeos em lote.
        
        Args:
            video_list: Lista de caminhos dos vídeos
            operations: Lista de operações a realizar
            
        Returns:
            Dicionário com resultados: {video_path: processed_path}
        """
        if operations is None:
            operations = ['normalize_to_vertical', 'enhance_quality']
        
        results = {}
        total_videos = len(video_list)
        
        self.logger.info(f"Iniciando batch process de {total_videos} vídeos")
        
        def process_single_video(video_path):
            """Processa um único vídeo."""
            try:
                output_path = video_path
                
                for operation in operations:
                    if operation == 'normalize_to_vertical':
                        output_path = self.normalize_to_vertical(output_path)
                    elif operation == 'enhance_quality':
                        output_path = self.enhance_quality(output_path)
                    elif operation == 'extract_frames':
                        frames = self.extract_frames_for_analysis(output_path)
                        # Manter o caminho do vídeo mesmo extraindo frames
                    
                    if not output_path:
                        raise Exception(f"Falha na operação {operation}")
                
                return video_path, output_path
                
            except Exception as e:
                self.logger.error(f"Erro ao processar {video_path}: {e}")
                return video_path, None
        
        # Processar em paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video = {
                executor.submit(process_single_video, video_path): video_path 
                for video_path in video_list
            }
            
            for future in as_completed(future_to_video):
                video_path, processed_path = future.result()
                results[video_path] = processed_path
        
        # Estatísticas do batch
        successful = sum(1 for path in results.values() if path is not None)
        self.logger.info(f"Batch concluído: {successful}/{total_videos} vídeos processados com sucesso")
        
        return results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do processamento.
        
        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            return {
                **self.stats,
                'cache_hit_rate': (
                    self.stats['cached_videos'] / max(1, self.stats['processed_videos']) * 100
                ),
                'processing_rate_videos_per_hour': (
                    3600 / max(1, self.stats['average_processing_time'])
                ) if self.stats['average_processing_time'] > 0 else 0
            }
    
    def clear_cache(self, older_than_days: int = 1) -> int:
        """
        Limpa arquivos de cache antigos.
        
        Args:
            older_than_days: Remover arquivos com mais de N dias
            
        Returns:
            Número de arquivos removidos
        """
        removed_count = 0
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cache_file.unlink()
                    removed_count += 1
            
            self.logger.info(f"Cache limpo: {removed_count} arquivos removidos")
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {e}")
        
        return removed_count


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar processador
    processor = AutomaticVideoProcessor()
    
    # Exemplo de uso
    test_videos = [
        "/path/to/video1.mp4",
        "/path/to/video2.mp4"
    ]
    
    try:
        # Processar um segmento específico
        result = processor.process_video_segment(
            test_videos[0], 
            target_duration=30.0, 
            start_time=10.0
        )
        print(f"Segmento processado: {result}")
        
        # Converter para formato vertical
        vertical_result = processor.normalize_to_vertical(test_videos[0])
        print(f"Formato vertical: {vertical_result}")
        
        # Melhorar qualidade
        enhanced_result = processor.enhance_quality(test_videos[0])
        print(f"Qualidade melhorada: {enhanced_result}")
        
        # Extrair frames para análise
        frames = processor.extract_frames_for_analysis(test_videos[0], num_frames=5)
        print(f"Frames extraídos: {frames}")
        
        # Processamento em lote
        batch_results = processor.batch_process_videos(test_videos)
        print(f"Resultados batch: {batch_results}")
        
        # Estatísticas
        stats = processor.get_processing_stats()
        print(f"Estatísticas: {stats}")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")