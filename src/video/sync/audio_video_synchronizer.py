"""
Audio Video Synchronizer para AiShorts v2.0
Sistema avançado de sincronização entre narração TTS e vídeos
"""

import os
import librosa
import numpy as np
import soundfile as sf
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from scipy.signal import find_peaks
import moviepy as mp

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AudioSegment:
    """Segmento de áudio com informações de timing"""
    start_time: float
    end_time: float
    duration: float
    audio_path: str
    text_content: str
    section_type: str
    beat_points: List[float] = None


@dataclass
class VideoSegment:
    """Segmento de vídeo com informações de timing"""
    start_time: float
    end_time: float
    duration: float
    video_path: str
    description: str
    transition_in: str = "fade"
    transition_out: str = "fade"
    beat_sync_points: List[float] = None


@dataclass
class TimelineEntry:
    """Entrada no timeline combinado"""
    timestamp: float
    audio_segment: Optional[AudioSegment]
    video_segment: Optional[VideoSegment]
    sync_point: bool = False
    transition_effect: Optional[str] = None


class AudioVideoSynchronizer:
    """
    Sincronizador avançado áudio-vídeo para AiShorts v2.0
    Integra com sistema TTS Kokoro para sincronização precisa
    """
    
    def __init__(self, output_dir: str = "outputs/video/sync"):
        """
        Inicializa sincronizador
        
        Args:
            output_dir: Diretório para salvar resultados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parâmetros de sincronização
        self.beat_detection_threshold = 0.7
        self.max_gap_compensation = 0.5  # segundos
        self.optimal_transition_duration = 0.3
        
        logger.info("AudioVideoSynchronizer inicializado")
    
    def sync_audio_with_video(self, 
                             audio_path: str, 
                             video_segments: List[VideoSegment], 
                             script_timing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sincroniza áudio principal com segmentos de vídeo
        
        Args:
            audio_path: Caminho do arquivo de áudio TTS
            video_segments: Lista de segmentos de vídeo
            script_timing: Informações de timing do script TTS
            
        Returns:
            Dict com timeline sincronizado e metadados
        """
        try:
            logger.info("Iniciando sincronização áudio-vídeo")
            
            # Carregar e analisar áudio principal
            audio_info = self._load_and_analyze_audio(audio_path)
            if not audio_info['success']:
                return audio_info
            
            # Criar segmentos de áudio baseados no script timing
            audio_segments = self._create_audio_segments(script_timing, audio_info)
            
            # Detectar pontos de beat no áudio
            beat_points = self.detect_beat_points(audio_path)
            
            # Alinhar segmentos de áudio e vídeo
            aligned_segments = self.align_segments(audio_segments, video_segments)
            
            # Criar timeline combinado
            timeline = self.create_timeline(audio_path, video_segments)
            
            # Compensar gaps e overlaps automaticamente
            compensated_timeline = self._compensate_gaps_overlaps(timeline)
            
            # Gerar vídeo sincronizado
            synchronized_video = self._generate_synchronized_video(
                compensated_timeline, audio_path
            )
            
            return {
                'success': True,
                'audio_info': audio_info,
                'timeline': timeline,
                'aligned_segments': aligned_segments,
                'beat_points': beat_points,
                'synchronized_video': synchronized_video,
                'total_duration': compensated_timeline[-1].timestamp if compensated_timeline else 0,
                'segments_count': len(aligned_segments)
            }
            
        except Exception as e:
            logger.error(f"Erro na sincronização áudio-vídeo: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_timeline(self, 
                       audio_path: str, 
                       video_segments: List[VideoSegment]) -> List[TimelineEntry]:
        """
        Cria timeline combinado áudio-vídeo
        
        Args:
            audio_path: Caminho do áudio principal
            video_segments: Lista de segmentos de vídeo
            
        Returns:
            Lista de entradas do timeline
        """
        logger.info("Criando timeline combinado")
        
        try:
            # Carregar duração do áudio
            audio_duration = librosa.get_duration(filename=audio_path)
            
            timeline = []
            current_time = 0.0
            
            # Criar entradas para cada segmento de vídeo
            for video_seg in video_segments:
                # Criar entrada do timeline
                timeline_entry = TimelineEntry(
                    timestamp=current_time,
                    audio_segment=None,  # Será preenchido durante alinhamento
                    video_segment=video_seg,
                    sync_point=False,
                    transition_effect=video_seg.transition_in
                )
                
                timeline.append(timeline_entry)
                current_time += video_seg.duration
            
            # Ajustar duração do timeline para duração do áudio
            if current_time < audio_duration:
                # Adicionar segment final se necessário
                timeline.append(TimelineEntry(
                    timestamp=current_time,
                    audio_segment=None,
                    video_segment=None,
                    sync_point=False
                ))
            
            logger.info(f"Timeline criado com {len(timeline)} entradas")
            return timeline
            
        except Exception as e:
            logger.error(f"Erro ao criar timeline: {e}")
            return []
    
    def detect_beat_points(self, audio_path: str) -> List[float]:
        """
        Detecta pontos de beat no áudio usando análise espectral
        
        Args:
            audio_path: Caminho do arquivo de áudio
            
        Returns:
            Lista de timestamps dos beats detectados
        """
        try:
            logger.info("Detectando pontos de beat no áudio")
            
            # Carregar áudio
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Detectar onset (início de eventos musicais/falados)
            onset_frames = librosa.onset.onset_detect(
                y=y, 
                sr=sr,
                units='time',
                hop_length=512
            )
            
            # Detectar beats usando Espectrograma de Cromas
            tempo, beat_frames = librosa.beat.beat_track(
                y=y, 
                sr=sr,
                hop_length=512
            )
            
            # Converter frames para timestamps
            beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)
            
            # Combinar onsets e beats para pontos de sincronização
            sync_points = list(onset_frames) + list(beat_times)
            sync_points.sort()
            
            # Filtrar pontos muito próximos (menos de 0.2s)
            filtered_points = []
            for point in sync_points:
                if not filtered_points or point - filtered_points[-1] > 0.2:
                    filtered_points.append(point)
            
            logger.info(f"Detectados {len(filtered_points)} pontos de sincronização")
            return filtered_points
            
        except Exception as e:
            logger.error(f"Erro na detecção de beats: {e}")
            return []
    
    def align_segments(self, 
                      audio_segments: List[AudioSegment], 
                      video_segments: List[VideoSegment]) -> Dict[str, Any]:
        """
        Alinha segmentos de áudio e vídeo com base em beats e timing
        
        Args:
            audio_segments: Lista de segmentos de áudio
            video_segments: Lista de segmentos de vídeo
            
        Returns:
            Dict com alinhamentos e metadados
        """
        try:
            logger.info("Alinhando segmentos áudio-vídeo")
            
            alignments = []
            total_audio_duration = sum(seg.duration for seg in audio_segments)
            total_video_duration = sum(seg.duration for seg in video_segments)
            
            # Calcular duração total de áudio vs vídeo
            duration_ratio = total_video_duration / total_audio_duration if total_audio_duration > 0 else 1.0
            
            # Ajustar velocidades se necessário
            if abs(duration_ratio - 1.0) > 0.1:  # Diferença de mais de 10%
                logger.warning(f"Razão de duração diferente: {duration_ratio:.2f}")
            
            # Alinhar cada segmento
            current_audio_time = 0.0
            current_video_time = 0.0
            
            for i, (audio_seg, video_seg) in enumerate(zip(audio_segments, video_segments)):
                # Ajustar timing do vídeo para corresponder ao áudio
                video_duration = audio_seg.duration * duration_ratio
                
                alignment = {
                    'segment_index': i,
                    'audio_segment': audio_seg,
                    'video_segment': video_seg,
                    'audio_start_time': current_audio_time,
                    'audio_end_time': current_audio_time + audio_seg.duration,
                    'video_start_time': current_video_time,
                    'video_end_time': current_video_time + video_duration,
                    'sync_accuracy': 0.95,  # Placeholder para cálculo real
                    'needs_transition': i > 0
                }
                
                alignments.append(alignment)
                
                current_audio_time += audio_seg.duration
                current_video_time += video_duration
            
            # Calcular estatísticas de alinhamento
            avg_sync_accuracy = np.mean([a['sync_accuracy'] for a in alignments])
            
            result = {
                'success': True,
                'alignments': alignments,
                'total_duration': max(current_audio_time, current_video_time),
                'avg_sync_accuracy': avg_sync_accuracy,
                'duration_ratio': duration_ratio,
                'segments_count': len(alignments)
            }
            
            logger.info(f"Alinhamento concluído: {len(alignments)} segmentos")
            return result
            
        except Exception as e:
            logger.error(f"Erro no alinhamento de segmentos: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_and_analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """Carrega e analisa arquivo de áudio"""
        try:
            if not os.path.exists(audio_path):
                return {'success': False, 'error': f'Arquivo não encontrado: {audio_path}'}
            
            # Carregar áudio com librosa
            y, sr = librosa.load(audio_path, sr=22050)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Análise espectral
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            rms_energy = librosa.feature.rms(y=y)
            
            # Análise de pitch (melody)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Detectar silêncio
            intervals = librosa.effects.split(y, top_db=20)
            
            return {
                'success': True,
                'audio_path': audio_path,
                'duration': duration,
                'sample_rate': sr,
                'spectral_centroids': np.mean(spectral_centroids),
                'rms_energy': np.mean(rms_energy),
                'silence_intervals': intervals,
                'beats_count': len(self.detect_beat_points(audio_path))
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar áudio: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_audio_segments(self, 
                              script_timing: Dict[str, Any], 
                              audio_info: Dict[str, Any]) -> List[AudioSegment]:
        """Cria segmentos de áudio baseados no timing do script"""
        segments = []
        
        if 'section_audio' in script_timing:
            for i, section in enumerate(script_timing['section_audio']):
                segment = AudioSegment(
                    start_time=i * 10,  # Placeholder - seria calculado baseado no offset real
                    end_time=i * 10 + section['duration'],
                    duration=section['duration'],
                    audio_path=section['audio_path'],
                    text_content=section['text'],
                    section_type=section['section_type']
                )
                segments.append(segment)
        
        return segments
    
    def _compensate_gaps_overlaps(self, timeline: List[TimelineEntry]) -> List[TimelineEntry]:
        """Compensa automaticamente gaps e overlaps no timeline"""
        try:
            logger.info("Compensando gaps e overlaps")
            
            if not timeline:
                return timeline
            
            compensated_timeline = timeline.copy()
            
            # Verificar e corrigir gaps/overlaps consecutivos
            for i in range(len(compensated_timeline) - 1):
                current = compensated_timeline[i]
                next_entry = compensated_timeline[i + 1]
                
                # Calcular gap ou overlap
                time_diff = next_entry.timestamp - current.timestamp
                
                # Compensar gaps muito grandes
                if time_diff > self.max_gap_compensation:
                    # Adicionar transição de fade ou manter pausa
                    current.transition_effect = "pause"
                    next_entry.transition_effect = "fade_in"
                
                # Compensar overlaps (vídeo mais longo que espaço disponível)
                elif time_diff < -0.1:  # Overlap de mais de 100ms
                    # Ajustar timing do próximo segmento
                    next_entry.timestamp = current.timestamp + 0.1
            
            return compensated_timeline
            
        except Exception as e:
            logger.error(f"Erro na compensação: {e}")
            return timeline
    
    def _generate_synchronized_video(self, 
                                   timeline: List[TimelineEntry], 
                                   audio_path: str) -> Dict[str, Any]:
        """Gera vídeo sincronizado final"""
        try:
            logger.info("Gerando vídeo sincronizado")
            
            if not timeline:
                return {'success': False, 'error': 'Timeline vazio'}
            
            # Criar clipes de vídeo baseados no timeline
            video_clips = []
            
            for entry in timeline:
                if entry.video_segment and os.path.exists(entry.video_segment.video_path):
                    # Carregar vídeo
                    video_clip = mp.VideoFileClip(entry.video_segment.video_path)
                    
                    # Ajustar timing
                    start_time = entry.timestamp
                    duration = entry.video_segment.duration
                    
                    video_clip = video_clip.subclip(0, min(duration, video_clip.duration))
                    
                    # Aplicar transições se necessário
                    if entry.transition_effect == "fade_in":
                        video_clip = video_clip.fadein(self.optimal_transition_duration)
                    elif entry.transition_effect == "fade_out":
                        video_clip = video_clip.fadeout(self.optimal_transition_duration)
                    
                    video_clips.append(video_clip)
            
            if not video_clips:
                return {'success': False, 'error': 'Nenhum vídeo válido para sincronizar'}
            
            # Concatenar vídeos
            final_video = mp.concatenate_videoclips(video_clips, method="compose")
            
            # Adicionar áudio
            if os.path.exists(audio_path):
                audio_clip = mp.AudioFileClip(audio_path)
                final_video = final_video.set_audio(audio_clip)
            
            # Salvar resultado
            output_path = self.output_dir / "video_sincronizado_final.mp4"
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Limpar memória
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            return {
                'success': True,
                'output_path': str(output_path),
                'duration': final_video.duration,
                'clips_count': len(video_clips)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar vídeo sincronizado: {e}")
            return {'success': False, 'error': str(e)}