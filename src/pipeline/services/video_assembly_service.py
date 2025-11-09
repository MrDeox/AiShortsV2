"""
VideoAssemblyService - Responsável pela sincronização áudio-vídeo e composição final.
Extrai a lógica de montagem de vídeo do AiShortsOrchestrator para melhor separação de responsabilidades.
"""

import contextlib
import logging
import wave
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable

from src.models.unified_models import VideoSyncPlan
from src.video.generators.final_video_composer import (
    FinalVideoComposer,
    TemplateConfig,
    VideoSegment,
)
from src.video.sync.audio_video_synchronizer import AudioVideoSynchronizer
from src.video.sync.timing_optimizer import TimingOptimizer


class VideoAssemblyService:
    """Serviço responsável por montar o vídeo final (sincronização e composição)."""
    
    def __init__(
        self,
        video_processor,
        caption_service,
        video_composer_factory: Optional[Callable[[], FinalVideoComposer]] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.video_processor = video_processor
        self.caption_service = caption_service
        self._composer_factory = video_composer_factory or (lambda: FinalVideoComposer())
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Componentes avançados
        self.audio_video_synchronizer = AudioVideoSynchronizer()
        self.timing_optimizer = TimingOptimizer()
    
    def sync_audio_video(self, audio_path: str, video_paths: List[str]) -> VideoSyncPlan:
        """
        Sincroniza áudio com os vídeos B-roll usando métodos avançados.
        
        Returns:
            VideoSyncPlan: Plano de sincronização áudio-vídeo
        """
self.logger.info(" ETAPA 5: Sincronização Avançada Áudio-Vídeo...")
        
        try:
            # Preparar segmentos de vídeo
            video_segments = self._prepare_video_segments(video_paths)
            
            # Obter timing do áudio
            audio_timing = self._get_audio_timing(audio_path)
            
            # 1) Otimizar transições
self.logger.info(" Otimizando transições entre segmentos...")
            timing_result = self.timing_optimizer.optimize_transitions(
                video_segments=video_segments,
                audio_timing=audio_timing
            )
            
            if timing_result.get("success"):
self.logger.info(
                    "✅ Timing otimizado com %d transições", 
                    len(timing_result.get("optimized_segments", []))
                )
                audio_timing["optimized_segments"] = timing_result.get("optimized_segments", [])
                audio_timing["transition_effects"] = timing_result.get("transition_effects", [])
            else:
self.logger.warning(" Otimização de timing falhou, usando sincronização básica")
                audio_timing["optimized_segments"] = video_segments
            
            # 2) Sincronização avançada
self.logger.info(" Realizando sincronização precisa áudio-vídeo...")
            sync_result = self.audio_video_synchronizer.sync_audio_with_video(
                audio_path=audio_path,
                video_segments=audio_timing["optimized_segments"],
                script_timing=audio_timing
            )
            
            if sync_result.get("success"):
self.logger.info(" Sincronização avançada concluída com sucesso!")
                
                timeline = sync_result.get("timeline", [])
                sync_points = sync_result.get("sync_points", [])
                
self.logger.info("   • Timeline sincronizado: %d segmentos", len(timeline))
self.logger.info("   • Pontos de sincronia: %d", len(sync_points))
self.logger.info("   • Precisão: %.2fms", sync_result.get("sync_precision", 0) * 1000)
                
                return VideoSyncPlan(
                    success=True,
                    audio_path=audio_path,
                    video_paths=video_paths,
                    sync_method="advanced",
                    timeline=timeline,
                    sync_points=sync_points,
                    sync_precision=sync_result.get("sync_precision", 0),
                    optimized_segments=audio_timing["optimized_segments"],
                    transition_effects=audio_timing.get("transition_effects", []),
                    total_synced_duration=sync_result.get("total_duration", audio_timing["total_duration"])
                )
            else:
self.logger.warning(" Sincronização avançada falhou, usando método básico")
                return VideoSyncPlan(
                    success=True,
                    audio_path=audio_path,
                    video_paths=video_paths,
                    sync_method="basic_fallback",
                    error=sync_result.get("error", "Advanced sync failed")
                )
                
        except Exception as error:
self.logger.error(" Erro na sincronização avançada: %s", error)
self.logger.info(" Usando sincronização básica como fallback")
            return VideoSyncPlan(
                success=True,
                audio_path=audio_path,
                video_paths=video_paths,
                sync_method="error_fallback",
                error=str(error)
            )
    
    def compose_final_video(
        self,
        video_paths: List[str],
        audio_path: str,
        captions: Optional[List[Dict[str, Any]]] = None,
        sync_result: Optional[VideoSyncPlan] = None
    ) -> Optional[str]:
        """
        Compõe o vídeo final com áudio, B-roll e legendas.
        
        Returns:
            Optional[str]: Caminho do vídeo final gerado
        """
self.logger.info(" ETAPA 6: Processamento Final com FinalVideoComposer...")
        
        # Verificar método de sincronização
        sync_method = "basic"
        if sync_result:
            sync_method = sync_result.sync_method
self.logger.info(" Método de sincronização: %s", sync_method)
            
            if sync_method == "advanced":
self.logger.info(" Usando timing otimizado da sincronização avançada")
self.logger.info("   • Pontos de sincronia: %d", len(sync_result.sync_points))
self.logger.info("   • Precisão: %.2fms", sync_result.sync_precision * 1000)
        
        # Validações básicas
        if not audio_path or not Path(audio_path).exists():
self.logger.error(" Áudio inexistente para composição: %s", audio_path)
            return None
        
        if not video_paths:
self.logger.error(" Nenhum vídeo B-roll disponível para composição final")
            return None
        
        # Preparar segmentos de vídeo
        segments = self._prepare_video_segments_for_composition(
            video_paths, 
            sync_result, 
            sync_method
        )
        
        if not segments:
self.logger.error(" Nenhum segmento de vídeo válido após validação")
            return None
        
        # Obter template e configurar duração
        composer = self._composer_factory()
        template_config = self._get_template_config(composer, audio_path)
        
        if not template_config:
self.logger.error(" FinalVideoComposer não disponibilizou templates para composição")
            return None
        
        # Preparar metadados
        metadata = self._prepare_metadata(segments, audio_path, captions, sync_result, sync_method)
        
        # Compor vídeo final
        try:
            final_video_path = composer.compose_final_video(
                audio_path=audio_path,
                video_segments=segments,
                template_config=template_config,
                captions=captions,
                output_path="outputs/final/video_final_aishorts.mp4",
                metadata=metadata,
            )
self.logger.info(" Vídeo final gerado: %s", final_video_path)
            return final_video_path
            
        except Exception as error:
self.logger.error(" ERRO NA COMPOSIÇÃO FINAL: %s", error)
            return None
    
    def _prepare_video_segments(self, video_paths: List[str]) -> List[Dict[str, Any]]:
        """Prepara segmentos de vídeo com informações de duração."""
        segments = []
        
        for i, video_path in enumerate(video_paths):
            # Obter duração real se possível
            duration = 5.0  # fallback
            if self.video_processor:
                video_info = self.video_processor.get_video_info(video_path)
                if video_info and video_info.get("duration"):
                    duration = float(video_info["duration"])
            
            segment = {
                "path": video_path,
                "duration": duration,
                "description": f"B-roll segment {i+1}",
                "start_time": 0.0,
                "end_time": duration
            }
            segments.append(segment)
        
        return segments
    
    def _get_audio_timing(self, audio_path: str) -> Dict[str, Any]:
        """Obtém informações de timing do áudio."""
        script_timing = {
            "audio_path": audio_path,
            "total_duration": 0.0,
            "sections": [],
            "beat_points": []
        }
        
        # Tentar obter duração real do áudio
        try:
            with contextlib.closing(wave.open(audio_path, "rb")) as wav_file:
                frames = wav_file.getnframes()
                framerate = wav_file.getframerate()
                if framerate:
                    script_timing["total_duration"] = frames / float(framerate)
        except Exception:
self.logger.warning(" Não foi possível obter duração exata do áudio, usando fallback")
            script_timing["total_duration"] = 60.0  # fallback
        
        return script_timing
    
    def _prepare_video_segments_for_composition(
        self,
        video_paths: List[str],
        sync_result: Optional[VideoSyncPlan],
        sync_method: str
    ) -> List[VideoSegment]:
        """Prepara segmentos de vídeo para composição."""
        segments: List[VideoSegment] = []
        
        # Se temos sincronização avançada, usar segmentos otimizados
        if sync_result and sync_method == "advanced" and sync_result.optimized_segments:
            optimized_segments = sync_result.optimized_segments
            
            for opt_segment in optimized_segments:
                path_obj = Path(opt_segment["path"])
                if not path_obj.exists():
self.logger.warning(" Vídeo otimizado ausente ignorado: %s", opt_segment["path"])
                    continue
                
                duration = opt_segment.get("duration", 5.0)
                
                segment = VideoSegment(
                    path=str(path_obj),
                    duration=duration,
                    transition_in=opt_segment.get("transition_in", "fade"),
                    transition_out=opt_segment.get("transition_out", "fade")
                )
                segments.append(segment)
self.logger.debug("   • Segmento otimizado: %s (%.2fs)", path_obj.name, duration)
        else:
            # Fallback para método básico
            for path in video_paths:
                path_obj = Path(path)
                if not path_obj.exists():
self.logger.warning(" Vídeo ausente ignorado: %s", path)
                    continue
                
                video_info = self.video_processor.get_video_info(path)
                if video_info and video_info.get("duration"):
                    duration = float(video_info["duration"])
                else:
self.logger.warning(" Duração desconhecida para %s, usando fallback de 5s", path)
                    duration = 5.0
                
                segments.append(VideoSegment(path=str(path_obj), duration=duration))
        
        return segments
    
    def _get_template_config(self, composer: FinalVideoComposer, audio_path: str) -> Optional[TemplateConfig]:
        """Obtém e configura o template para composição."""
        template_config: Optional[TemplateConfig] = composer.templates.get("professional")
        
        if not template_config and composer.templates:
            template_config = next(iter(composer.templates.values()))
        
        if template_config:
            # Ajustar duração do template para corresponder ao áudio
            audio_duration = self._get_audio_duration(audio_path)
            if audio_duration:
                template_config = replace(template_config, duration=audio_duration)
        
        return template_config
    
    def _prepare_metadata(
        self,
        segments: List[VideoSegment],
        audio_path: str,
        captions: Optional[List[Dict[str, Any]]],
        sync_result: Optional[VideoSyncPlan],
        sync_method: str
    ) -> Dict[str, Any]:
        """Prepara metadados para o vídeo final."""
        metadata = {
            "pipeline": "AiShortsOrchestrator",
            "generated_at": datetime.now().isoformat(),
            "video_segments": [segment.path for segment in segments],
            "audio_path": audio_path,
            "captions_count": len(captions or []),
            "sync_method": sync_method,
        }
        
        # Adicionar informações avançadas de sincronização
        if sync_result and sync_method == "advanced":
            metadata.update({
                "sync_precision_ms": sync_result.sync_precision * 1000,
                "sync_points_count": len(sync_result.sync_points),
                "transition_effects": sync_result.transition_effects,
                "optimized_timing": True
            })
        
        return metadata
    
    def _get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Obtém a duração do arquivo de áudio."""
        try:
            with contextlib.closing(wave.open(audio_path, "rb")) as wav_file:
                frames = wav_file.getnframes()
                framerate = wav_file.getframerate()
                if framerate:
                    return frames / float(framerate)
        except (wave.Error, FileNotFoundError):
self.logger.warning(" Não foi possível ler duração do áudio %s", audio_path)
        return None