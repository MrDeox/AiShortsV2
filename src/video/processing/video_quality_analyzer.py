"""
Analisador de qualidade de vídeo
Video Quality Analyzer

Sistema de análise que:
- Analisa qualidade (brilho, nitidez, movimento)
- Verifica compatibilidade com plataformas
- Sugere melhorias baseadas na análise
- Gera relatórios de qualidade
"""

import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import os
import json
from typing import List, Dict, Tuple, Optional, Any, Union
from pathlib import Path
import tempfile
from PIL import Image, ImageStat
import logging
from dataclasses import dataclass
from datetime import datetime
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from .automatic_video_processor import AutomaticVideoProcessor

def get_config():
    """Config fallback para video_quality_analyzer."""
    return {
        "quality_analysis": {
            "enable_brightness_check": True,
            "enable_sharpness_check": True,
            "enable_motion_analysis": True,
            "min_brightness": 0.2,
            "max_brightness": 0.8,
            "min_sharpness": 0.3,
            "max_motion_level": 0.7
        }
    }


@dataclass
class QualityMetrics:
    """Métricas de qualidade do vídeo."""
    brightness: float
    sharpness: float
    motion_level: float
    contrast: float
    color_saturation: float
    noise_level: float
    overall_score: float
    
    def to_dict(self) -> Dict[str, float]:
        """Converte métricas para dicionário."""
        return {
            'brightness': self.brightness,
            'sharpness': self.sharpness,
            'motion_level': self.motion_level,
            'contrast': self.contrast,
            'color_saturation': self.color_saturation,
            'noise_level': self.noise_level,
            'overall_score': self.overall_score
        }


@dataclass
class PlatformRequirements:
    """Requisitos para diferentes plataformas."""
    name: str
    min_resolution: Tuple[int, int]
    max_resolution: Tuple[int, int]
    min_fps: int
    max_fps: int
    max_duration: float
    aspect_ratios: List[str]
    max_file_size: int


class VideoQualityAnalyzer:
    """
    Analisador de qualidade de vídeo com foco em otimização para plataformas.
    
    Funcionalidades:
    - Análise completa de qualidade (brilho, nitidez, movimento)
    - Verificação de compatibilidade com plataformas
    - Sugestões automáticas de melhoria
    - Relatórios detalhados de qualidade
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o analisador de qualidade.
        
        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Requisitos das plataformas
        self.platform_requirements = {
            'tiktok': PlatformRequirements(
                name='TikTok',
                min_resolution=(720, 1280),
                max_resolution=(1080, 1920),
                min_fps=24,
                max_fps=60,
                max_duration=600.0,  # 10 minutos
                aspect_ratios=['9:16', '1:1'],
                max_file_size=287 * 1024 * 1024  # 287MB
            ),
            'instagram_reels': PlatformRequirements(
                name='Instagram Reels',
                min_resolution=(720, 1280),
                max_resolution=(1080, 1920),
                min_fps=24,
                max_fps=60,
                max_duration=90.0,  # 90 segundos
                aspect_ratios=['9:16', '1:1'],
                max_file_size=4 * 1024 * 1024 * 1024  # 4GB
            ),
            'youtube_shorts': PlatformRequirements(
                name='YouTube Shorts',
                min_resolution=(720, 1280),
                max_resolution=(1080, 1920),
                min_fps=24,
                max_fps=60,
                max_duration=60.0,  # 60 segundos
                aspect_ratios=['9:16', '1:1', '16:9'],
                max_file_size=256 * 1024 * 1024  # 256MB
            ),
            'facebook_reels': PlatformRequirements(
                name='Facebook Reels',
                min_resolution=(720, 1280),
                max_resolution=(1080, 1920),
                min_fps=24,
                max_fps=60,
                max_duration=60.0,  # 60 segundos
                aspect_ratios=['9:16', '1:1'],
                max_file_size=4 * 1024 * 1024 * 1024  # 4GB
            )
        }
        
        # Pesos para cálculo da pontuação geral
        self.quality_weights = {
            'brightness': 0.15,
            'sharpness': 0.25,
            'motion_level': 0.20,
            'contrast': 0.15,
            'color_saturation': 0.15,
            'noise_level': 0.10
        }
    
    def analyze_video_quality(self, video_path: str) -> QualityMetrics:
        """
        Analisa a qualidade completa do vídeo.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Métricas de qualidade
        """
        try:
            # Abrir vídeo com OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
            
            # Obter propriedades do vídeo
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Analisar amostra de frames
            sample_size = min(30, total_frames)  # Máximo 30 frames
            frame_indices = np.linspace(0, total_frames - 1, sample_size, dtype=int)
            
            brightness_values = []
            sharpness_values = []
            motion_values = []
            contrast_values = []
            saturation_values = []
            noise_values = []
            
            prev_frame = None
            
            for frame_idx in frame_indices:
                # Posicionar no frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Converter para escala de cinza para algumas análises
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 1. Brilho (média dos pixels)
                brightness = np.mean(gray)
                brightness_values.append(brightness)
                
                # 2. Nitidez (variância do Laplaciano)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_values.append(laplacian_var)
                
                # 3. Contraste (desvio padrão)
                contrast = np.std(gray)
                contrast_values.append(contrast)
                
                # 4. Saturação de cor
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                saturation = np.mean(hsv[:, :, 1])
                saturation_values.append(saturation)
                
                # 5. Nível de ruído (detecção de bordas)
                edges = cv2.Canny(gray, 50, 150)
                noise_ratio = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                noise_values.append(noise_ratio)
                
                # 6. Movimento (diferença entre frames)
                if prev_frame is not None:
                    # Redimensionar para análise mais rápida
                    scale_factor = 0.25
                    h, w = gray.shape
                    small_h, small_w = int(h * scale_factor), int(w * scale_factor)
                    small_prev = cv2.resize(prev_frame, (small_w, small_h))
                    small_curr = cv2.resize(gray, (small_w, small_h))
                    
                    # Calcular diferença
                    diff = cv2.absdiff(small_prev, small_curr)
                    motion = np.mean(diff)
                    motion_values.append(motion)
                
                prev_frame = gray.copy()
            
            cap.release()
            
            # Calcular médias
            avg_brightness = np.mean(brightness_values) / 255.0  # Normalizar 0-1
            avg_sharpness = np.mean(sharpness_values) / 1000.0  # Normalizar
            avg_motion = np.mean(motion_values) / 128.0 if motion_values else 0  # Normalizar
            avg_contrast = np.mean(contrast_values) / 128.0  # Normalizar
            avg_saturation = np.mean(saturation_values) / 255.0  # Normalizar 0-1
            avg_noise = np.mean(noise_values)
            
            # Calcular pontuação geral
            quality_score = (
                avg_brightness * self.quality_weights['brightness'] +
                avg_sharpness * self.quality_weights['sharpness'] +
                avg_motion * self.quality_weights['motion_level'] +
                avg_contrast * self.quality_weights['contrast'] +
                avg_saturation * self.quality_weights['color_saturation'] +
                (1 - avg_noise) * self.quality_weights['noise_level']
            ) * 100
            
            metrics = QualityMetrics(
                brightness=avg_brightness,
                sharpness=avg_sharpness,
                motion_level=avg_motion,
                contrast=avg_contrast,
                color_saturation=avg_saturation,
                noise_level=avg_noise,
                overall_score=quality_score
            )
            
self.logger.info(f"Análise de qualidade concluída: {quality_score:.2f}/100")
            return metrics
            
        except Exception as e:
self.logger.error(f"Erro ao analisar qualidade do vídeo: {e}")
            # Retornar métricas padrão em caso de erro
            return QualityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 50.0)
    
    def check_platform_compatibility(self, video_path: str, platform: str) -> Dict[str, Any]:
        """
        Verifica compatibilidade do vídeo com uma plataforma específica.
        
        Args:
            video_path: Caminho do vídeo
            platform: Nome da plataforma (tiktok, instagram_reels, etc.)
            
        Returns:
            Dicionário com resultados da verificação
        """
        if platform not in self.platform_requirements:
            raise ValueError(f"Plataforma não suportada: {platform}")
        
        requirements = self.platform_requirements[platform]
        
        try:
            # Obter informações do vídeo
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
            
            video_info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            }
            
            cap.release()
            
            # Verificações de compatibilidade
            compatibility_checks = {
                'resolution_ok': self._check_resolution(video_info, requirements),
                'fps_ok': self._check_fps(video_info, requirements),
                'duration_ok': self._check_duration(video_info, requirements),
                'aspect_ratio_ok': self._check_aspect_ratio(video_info, requirements),
                'file_size_ok': self._check_file_size(video_path, requirements)
            }
            
            # Calcular compatibilidade geral
            overall_compatibility = sum(compatibility_checks.values()) / len(compatibility_checks) * 100
            
            # Obter análise de qualidade
            quality_metrics = self.analyze_video_quality(video_path)
            
            result = {
                'platform': platform,
                'video_info': video_info,
                'requirements': {
                    'min_resolution': requirements.min_resolution,
                    'max_resolution': requirements.max_resolution,
                    'min_fps': requirements.min_fps,
                    'max_fps': requirements.max_fps,
                    'max_duration': requirements.max_duration,
                    'aspect_ratios': requirements.aspect_ratios,
                    'max_file_size': requirements.max_file_size
                },
                'compatibility_checks': compatibility_checks,
                'overall_compatibility': overall_compatibility,
                'quality_metrics': quality_metrics.to_dict(),
                'recommendations': self._generate_platform_recommendations(
                    video_info, compatibility_checks, quality_metrics, platform
                ),
                'analyzed_at': datetime.now().isoformat()
            }
            
self.logger.info(f"Verificação de compatibilidade concluída para {platform}: {overall_compatibility:.1f}%")
            return result
            
        except Exception as e:
self.logger.error(f"Erro ao verificar compatibilidade: {e}")
            return {
                'platform': platform,
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _check_resolution(self, video_info: Dict, requirements: PlatformRequirements) -> bool:
        """Verifica se a resolução é adequada."""
        width, height = video_info['width'], video_info['height']
        min_w, min_h = requirements.min_resolution
        max_w, max_h = requirements.max_resolution
        
        return (min_w <= width <= max_w) and (min_h <= height <= max_h)
    
    def _check_fps(self, video_info: Dict, requirements: PlatformRequirements) -> bool:
        """Verifica se o FPS é adequado."""
        fps = video_info['fps']
        return requirements.min_fps <= fps <= requirements.max_fps
    
    def _check_duration(self, video_info: Dict, requirements: PlatformRequirements) -> bool:
        """Verifica se a duração é adequada."""
        duration = video_info['duration']
        return duration <= requirements.max_duration
    
    def _check_aspect_ratio(self, video_info: Dict, requirements: PlatformRequirements) -> bool:
        """Verifica se o aspect ratio é adequado."""
        width, height = video_info['width'], video_info['height']
        ratio = width / height
        
        # Verificar se a proporção está em uma das aceitáveis
        for aspect_str in requirements.aspect_ratios:
            w_ratio, h_ratio = map(int, aspect_str.split(':'))
            expected_ratio = w_ratio / h_ratio
            if abs(ratio - expected_ratio) < 0.1:  # Tolerância de 10%
                return True
        
        return False
    
    def _check_file_size(self, video_path: str, requirements: PlatformRequirements) -> bool:
        """Verifica se o tamanho do arquivo é adequado."""
        file_size = os.path.getsize(video_path)
        return file_size <= requirements.max_file_size
    
    def suggest_improvements(self, video_path: str) -> Dict[str, Any]:
        """
        Analisa o vídeo e sugere melhorias específicas.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Dicionário com sugestões de melhoria
        """
        try:
            # Análise completa
            quality_metrics = self.analyze_video_quality(video_path)
            
            # Verificar compatibilidade com plataformas
            platform_compatibility = {}
            for platform in self.platform_requirements.keys():
                platform_compatibility[platform] = self.check_platform_compatibility(video_path, platform)
            
            # Gerar sugestões baseadas na análise
            suggestions = {
                'quality_improvements': self._generate_quality_suggestions(quality_metrics),
                'technical_improvements': self._generate_technical_suggestions(video_path, platform_compatibility),
                'platform_optimizations': self._generate_platform_optimizations(platform_compatibility),
                'priority_actions': self._get_priority_actions(quality_metrics, platform_compatibility)
            }
            
            result = {
                'video_path': video_path,
                'current_quality': quality_metrics.to_dict(),
                'platform_compatibility': platform_compatibility,
                'suggestions': suggestions,
                'estimated_improvement': self._estimate_improvement(suggestions),
                'generated_at': datetime.now().isoformat()
            }
            
self.logger.info(f"Sugestões de melhoria geradas para {video_path}")
            return result
            
        except Exception as e:
self.logger.error(f"Erro ao gerar sugestões: {e}")
            return {
                'video_path': video_path,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def _generate_quality_suggestions(self, metrics: QualityMetrics) -> List[Dict[str, str]]:
        """Gera sugestões baseadas nas métricas de qualidade."""
        suggestions = []
        
        # Brilho
        if metrics.brightness < 0.3:
            suggestions.append({
                'type': 'brightness',
                'issue': 'Vídeo muito escuro',
                'suggestion': 'Aumentar brilho em 20-30%',
                'impact': 'medium',
                'method': 'adjust_brightness'
            })
        elif metrics.brightness > 0.8:
            suggestions.append({
                'type': 'brightness',
                'issue': 'Vídeo muito claro',
                'suggestion': 'Reduzir brilho em 15-20%',
                'impact': 'medium',
                'method': 'adjust_brightness'
            })
        
        # Nitidez
        if metrics.sharpness < 0.4:
            suggestions.append({
                'type': 'sharpness',
                'issue': 'Vídeo sem nitidez',
                'suggestion': 'Aplicar filtro de sharpening',
                'impact': 'high',
                'method': 'sharpen_filter'
            })
        
        # Contraste
        if metrics.contrast < 0.4:
            suggestions.append({
                'type': 'contrast',
                'issue': 'Baixo contraste',
                'suggestion': 'Aumentar contraste em 15-25%',
                'impact': 'medium',
                'method': 'adjust_contrast'
            })
        
        # Saturação
        if metrics.color_saturation < 0.4:
            suggestions.append({
                'type': 'saturation',
                'issue': 'Cores desbotadas',
                'suggestion': 'Aumentar saturação em 20%',
                'impact': 'medium',
                'method': 'adjust_saturation'
            })
        elif metrics.color_saturation > 0.9:
            suggestions.append({
                'type': 'saturation',
                'issue': 'Cores muito saturadas',
                'suggestion': 'Reduzir saturação em 15%',
                'impact': 'low',
                'method': 'adjust_saturation'
            })
        
        # Ruído
        if metrics.noise_level > 0.3:
            suggestions.append({
                'type': 'noise',
                'issue': 'Alto nível de ruído',
                'suggestion': 'Aplicar filtro de redução de ruído',
                'impact': 'high',
                'method': 'denoise_filter'
            })
        
        return suggestions
    
    def _generate_technical_suggestions(self, video_path: str, compatibility: Dict) -> List[Dict[str, str]]:
        """Gera sugestões técnicas baseadas na compatibilidade."""
        suggestions = []
        
        for platform, comp_data in compatibility.items():
            if not comp_data.get('compatibility_checks', {}).get('resolution_ok', True):
                suggestions.append({
                    'type': 'resolution',
                    'platform': platform,
                    'issue': f'Resolução inadequada para {platform}',
                    'suggestion': 'Converter para 1080x1920 (vertical)',
                    'impact': 'high',
                    'method': 'convert_resolution'
                })
            
            if not comp_data.get('compatibility_checks', {}).get('fps_ok', True):
                suggestions.append({
                    'type': 'fps',
                    'platform': platform,
                    'issue': f'FPS inadequado para {platform}',
                    'suggestion': 'Ajustar FPS para 30fps',
                    'impact': 'medium',
                    'method': 'adjust_fps'
                })
            
            if not comp_data.get('compatibility_checks', {}).get('duration_ok', True):
                suggestions.append({
                    'type': 'duration',
                    'platform': platform,
                    'issue': f'Duração muito longa para {platform}',
                    'suggestion': 'Recortar vídeo para duração adequada',
                    'impact': 'high',
                    'method': 'trim_video'
                })
        
        return suggestions
    
    def _generate_platform_optimizations(self, compatibility: Dict) -> Dict[str, List[str]]:
        """Gera otimizações específicas por plataforma."""
        optimizations = {}
        
        for platform, comp_data in compatibility.items():
            platform_suggestions = []
            
            if comp_data.get('overall_compatibility', 0) < 50:
                platform_suggestions.append("Processamento completo necessário")
            elif comp_data.get('overall_compatibility', 0) < 80:
                platform_suggestions.append("Pequenos ajustes recomendados")
            else:
                platform_suggestions.append("Vídeo já otimizado para esta plataforma")
            
            # Adicionar sugestões específicas baseadas na qualidade
            quality_metrics = comp_data.get('quality_metrics', {})
            if quality_metrics.get('overall_score', 0) < 60:
                platform_suggestions.append("Melhorar qualidade geral do vídeo")
            
            optimizations[platform] = platform_suggestions
        
        return optimizations
    
    def _get_priority_actions(self, quality_metrics: QualityMetrics, compatibility: Dict) -> List[Dict[str, Any]]:
        """Determina ações prioritárias baseadas na análise."""
        priority_actions = []
        
        # Prioridade 1: Problemas críticos de compatibilidade
        for platform, comp_data in compatibility.items():
            checks = comp_data.get('compatibility_checks', {})
            if not checks.get('resolution_ok', True) or not checks.get('duration_ok', True):
                priority_actions.append({
                    'priority': 1,
                    'action': 'resolve_compatibility_issues',
                    'details': f'Resolver problemas de compatibilidade com {platform}',
                    'estimated_time': '5-10 minutos'
                })
        
        # Prioridade 2: Problemas de qualidade severa
        if quality_metrics.overall_score < 40:
            priority_actions.append({
                'priority': 2,
                'action': 'improve_video_quality',
                'details': 'Melhorar qualidade geral do vídeo',
                'estimated_time': '10-15 minutos'
            })
        
        # Prioridade 3: Melhorias de qualidade
        if quality_metrics.sharpness < 0.5 or quality_metrics.noise_level > 0.3:
            priority_actions.append({
                'priority': 3,
                'action': 'apply_quality_filters',
                'details': 'Aplicar filtros de melhoria de qualidade',
                'estimated_time': '5-8 minutos'
            })
        
        # Prioridade 4: Otimizações para plataformas
        if quality_metrics.overall_score > 60:
            priority_actions.append({
                'priority': 4,
                'action': 'optimize_for_platforms',
                'details': 'Otimizar vídeo para todas as plataformas',
                'estimated_time': '3-5 minutos'
            })
        
        return sorted(priority_actions, key=lambda x: x['priority'])
    
    def _estimate_improvement(self, suggestions: Dict) -> Dict[str, float]:
        """Estima melhoria esperada com as sugestões."""
        # Calcular melhoria baseada no impacto das sugestões
        quality_suggestions = suggestions.get('quality_improvements', [])
        technical_suggestions = suggestions.get('technical_improvements', [])
        
        quality_score = 0
        for suggestion in quality_suggestions:
            if suggestion['impact'] == 'high':
                quality_score += 25
            elif suggestion['impact'] == 'medium':
                quality_score += 15
            else:
                quality_score += 5
        
        technical_score = len(technical_suggestions) * 10
        
        total_improvement = min(quality_score + technical_score, 100)
        
        return {
            'quality_improvement': min(quality_score, 50),
            'compatibility_improvement': min(technical_score, 50),
            'overall_improvement': total_improvement
        }
    
    def batch_analyze_quality(self, video_list: List[str]) -> Dict[str, Any]:
        """
        Analisa qualidade de múltiplos vídeos em lote.
        
        Args:
            video_list: Lista de caminhos dos vídeos
            
        Returns:
            Dicionário com resultados da análise em lote
        """
        results = {}
        total_videos = len(video_list)
        
self.logger.info(f"Iniciando análise em lote de {total_videos} vídeos")
        
        def analyze_single_video(video_path):
            """Analisa um único vídeo."""
            try:
                quality_metrics = self.analyze_video_quality(video_path)
                return video_path, {
                    'quality_metrics': quality_metrics.to_dict(),
                    'suggestions': self.suggest_improvements(video_path),
                    'status': 'success'
                }
            except Exception as e:
                return video_path, {
                    'error': str(e),
                    'status': 'failed'
                }
        
        # Processar em paralelo
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_video = {
                executor.submit(analyze_single_video, video_path): video_path 
                for video_path in video_list
            }
            
            for future in as_completed(future_to_video):
                video_path, result = future.result()
                results[video_path] = result
        
        # Calcular estatísticas gerais
        successful_analyses = [r for r in results.values() if r.get('status') == 'success']
        
        overall_stats = {
            'total_videos': total_videos,
            'successful_analyses': len(successful_analyses),
            'failed_analyses': total_videos - len(successful_analyses),
            'average_quality_score': 0,
            'common_issues': [],
            'improvement_potential': 0
        }
        
        if successful_analyses:
            quality_scores = [
                r['quality_metrics']['overall_score'] 
                for r in successful_analyses
            ]
            overall_stats['average_quality_score'] = statistics.mean(quality_scores)
            overall_stats['improvement_potential'] = max(0, 100 - overall_stats['average_quality_score'])
        
        result_summary = {
            'individual_results': results,
            'overall_statistics': overall_stats,
            'analyzed_at': datetime.now().isoformat()
        }
        
self.logger.info(f"Análise em lote concluída: {len(successful_analyses)}/{total_videos} sucessos")
        return result_summary
    
    def generate_quality_report(self, video_path: str, output_path: str) -> bool:
        """
        Gera relatório completo de qualidade em formato JSON.
        
        Args:
            video_path: Caminho do vídeo
            output_path: Caminho do arquivo de saída
            
        Returns:
            True se relatório gerado com sucesso
        """
        try:
            # Análise completa
            quality_metrics = self.analyze_video_quality(video_path)
            suggestions = self.suggest_improvements(video_path)
            
            # Verificar compatibilidade com todas as plataformas
            platform_compatibility = {}
            for platform in self.platform_requirements.keys():
                platform_compatibility[platform] = self.check_platform_compatibility(video_path, platform)
            
            # Compilar relatório
            report = {
                'video_info': {
                    'path': video_path,
                    'file_size': os.path.getsize(video_path),
                    'analyzed_at': datetime.now().isoformat()
                },
                'quality_analysis': {
                    'metrics': quality_metrics.to_dict(),
                    'grade': self._get_quality_grade(quality_metrics.overall_score),
                    'summary': self._generate_quality_summary(quality_metrics)
                },
                'platform_compatibility': platform_compatibility,
                'improvement_suggestions': suggestions,
                'recommended_actions': self._get_recommended_actions(quality_metrics, platform_compatibility)
            }
            
            # Salvar relatório
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
self.logger.info(f"Relatório de qualidade gerado: {output_path}")
            return True
            
        except Exception as e:
self.logger.error(f"Erro ao gerar relatório: {e}")
            return False
    
    def _get_quality_grade(self, score: float) -> str:
        """Converte pontuação em nota."""
        if score >= 90:
            return 'A+ (Excelente)'
        elif score >= 80:
            return 'A (Muito Bom)'
        elif score >= 70:
            return 'B (Bom)'
        elif score >= 60:
            return 'C (Regular)'
        elif score >= 50:
            return 'D (Ruim)'
        else:
            return 'F (Muito Ruim)'
    
    def _generate_quality_summary(self, metrics: QualityMetrics) -> str:
        """Gera resumo textual da qualidade."""
        if metrics.overall_score >= 80:
            return "Vídeo com excelente qualidade técnica e visual."
        elif metrics.overall_score >= 60:
            return "Vídeo com qualidade boa, mas pode se beneficiar de pequenos ajustes."
        else:
            return "Vídeo necessita de melhorias significativas na qualidade."
    
    def _get_recommended_actions(self, quality_metrics: QualityMetrics, compatibility: Dict) -> List[Dict[str, str]]:
        """Obtém ações recomendadas prioritárias."""
        actions = []
        
        # Verificar problemas críticos
        if quality_metrics.overall_score < 60:
            actions.append({
                'priority': 'Alta',
                'action': 'Aplicar filtros de melhoria de qualidade',
                'description': 'Sharpening, redução de ruído, ajuste de brilho/contraste'
            })
        
        # Verificar problemas de compatibilidade
        incompatible_platforms = [
            platform for platform, data in compatibility.items()
            if data.get('overall_compatibility', 100) < 70
        ]
        
        if incompatible_platforms:
            actions.append({
                'priority': 'Alta',
                'action': 'Resolver problemas de compatibilidade',
                'description': f'Ajustar resolução, duração ou FPS para: {", ".join(incompatible_platforms)}'
            })
        
        if not actions:
            actions.append({
                'priority': 'Baixa',
                'action': 'Otimizar para plataformas específicas',
                'description': 'Ajustes menores para maximizar compatibilidade'
            })
        
        return actions


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar analisador
    analyzer = VideoQualityAnalyzer()
    
    # Exemplo de uso
    test_video = "/path/to/test_video.mp4"
    
    try:
        # Análise de qualidade
        metrics = analyzer.analyze_video_quality(test_video)
print(f"Métricas de qualidade: {metrics}")
        
        # Verificar compatibilidade com TikTok
        tiktok_compat = analyzer.check_platform_compatibility(test_video, 'tiktok')
print(f"Compatibilidade TikTok: {tiktok_compat}")
        
        # Gerar sugestões de melhoria
        suggestions = analyzer.suggest_improvements(test_video)
print(f"Sugestões: {suggestions}")
        
        # Gerar relatório completo
        report_path = "/tmp/quality_report.json"
        success = analyzer.generate_quality_report(test_video, report_path)
print(f"Relatório gerado: {success}")
        
    except Exception as e:
print(f"Erro durante o teste: {e}")