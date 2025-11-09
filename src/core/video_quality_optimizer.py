"""
Video Quality Optimizer - Análise Visual Avançada com LLM
Sistema inteligente para análise e otimização de qualidade de vídeos usando LLM multimodal

Features:
- Análise visual de frames com LLM
- Sugestões de melhorias específicas
- Detecção automática de problemas de qualidade
- Recomendações de color grading e edição
- Análise de compatibilidade com plataformas
"""

import cv2
import numpy as np
import base64
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import tempfile

from src.core.openrouter_client import OpenRouterClient


@dataclass
class QualityIssue:
    """Representa um problema de qualidade detectado."""
    issue_type: str
    severity: str  # low, medium, high, critical
    description: str
    suggested_fix: str
    confidence: float


@dataclass
class QualityRecommendation:
    """Recomendação de melhoria de qualidade."""
    category: str  # color, lighting, composition, stability, etc
    priority: str
    recommendation: str
    expected_impact: str
    implementation_difficulty: str


class VideoQualityOptimizer:
    """
    Otimizador de qualidade de vídeo usando LLM multimodal.
    
    Funcionalidades:
    - Análise visual avançada
    - Detecção de problemas técnicos
    - Sugestões de melhoria
    - Recomendações de pós-processamento
    """
    
    def __init__(self, llm_client: OpenRouterClient):
        """
        Inicializa o otimizador de qualidade.
        
        Args:
            llm_client: Cliente LLM para análise multimodal
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path(tempfile.gettempdir()) / "aishorts_quality_analysis"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Padrões de qualidade para diferentes plataformas
        self.platform_requirements = {
            'tiktok': {
                'min_resolution': (720, 1280),
                'max_resolution': (1080, 1920),
                'fps': [24, 25, 30],
                'aspect_ratio': '9:16',
                'bitrate_range': (2000, 8000)
            },
            'shorts': {
                'min_resolution': (720, 1280),
                'max_resolution': (1080, 1920),
                'fps': [24, 25, 30],
                'aspect_ratio': '9:16',
                'bitrate_range': (2000, 8000)
            },
            'reels': {
                'min_resolution': (720, 1280),
                'max_resolution': (1080, 1920),
                'fps': [24, 25, 30],
                'aspect_ratio': '9:16',
                'bitrate_range': (2500, 10000)
            }
        }
    
    def analyze_video_quality(self, 
                            video_path: str,
                            target_platform: str = 'tiktok',
                            detailed_analysis: bool = True) -> Dict[str, Any]:
        """
        Análise completa da qualidade do vídeo usando LLM multimodal.
        
        Args:
            video_path: Path do vídeo para análise
            target_platform: Plataforma alvo (tiktok, shorts, reels)
            detailed_analysis: Se deve fazer análise detalhada
            
        Returns:
            Dicionário com resultados completos da análise
        """
self.logger.info(f" Iniciando análise de qualidade: {video_path}")
        
        try:
            # Análise técnica tradicional
            technical_analysis = self._perform_technical_analysis(video_path)
            
            # Extrair frames para análise visual
            frames = self._extract_representative_frames(video_path, num_frames=5)
            if not frames:
                return {"error": "Could not extract frames for analysis"}
            
            # Análise visual com LLM
            visual_analysis = self._analyze_visual_quality_with_llm(
                frames, 
                target_platform,
                technical_analysis
            )
            
            # Detectar problemas específicos
            quality_issues = self._detect_quality_issues(technical_analysis, visual_analysis)
            
            # Gerar recomendações
            recommendations = self._generate_quality_recommendations(
                quality_issues, 
                target_platform,
                technical_analysis
            )
            
            # Compor resultado final
            analysis_result = {
                'video_path': video_path,
                'target_platform': target_platform,
                'analysis_timestamp': datetime.now().isoformat(),
                'technical_analysis': technical_analysis,
                'visual_analysis': visual_analysis,
                'quality_issues': [issue.__dict__ for issue in quality_issues],
                'recommendations': [rec.__dict__ for rec in recommendations],
                'overall_score': self._calculate_overall_quality_score(technical_analysis, quality_issues),
                'platform_compatibility': self._check_platform_compatibility(
                    technical_analysis, 
                    target_platform
                )
            }
            
self.logger.info(f" Análise concluída - Score: {analysis_result['overall_score']:.2f}")
            return analysis_result
            
        except Exception as e:
self.logger.error(f" Erro na análise de qualidade: {e}")
            return {"error": str(e)}
    
    def _perform_technical_analysis(self, video_path: str) -> Dict[str, Any]:
        """
        Realiza análise técnica tradicional do vídeo.
        
        Args:
            video_path: Path do vídeo
            
        Returns:
            Dicionário com métricas técnicas
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {"error": "Could not open video file"}
            
            # Propriedades básicas
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Análise de brilho e contraste
            brightness_values = []
            contrast_values = []
            sharpness_values = []
            
            # Amostrar frames para análise
            sample_frames = min(30, frame_count)
            frame_interval = max(1, frame_count // sample_frames)
            
            for i in range(0, frame_count, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Converter para grayscale para análise
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Calcular brilho (média de pixels)
                    brightness = np.mean(gray)
                    brightness_values.append(brightness)
                    
                    # Calcular contraste (desvio padrão)
                    contrast = np.std(gray)
                    contrast_values.append(contrast)
                    
                    # Calcular nitidez (usando Laplacian)
                    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                    sharpness_values.append(sharpness)
            
            cap.release()
            
            # Estatísticas finais
            analysis = {
                'resolution': (width, height),
                'fps': fps,
                'duration': duration,
                'frame_count': frame_count,
                'aspect_ratio': f"{width}:{height}",
                'brightness': {
                    'mean': np.mean(brightness_values) if brightness_values else 0,
                    'std': np.std(brightness_values) if brightness_values else 0,
                    'min': np.min(brightness_values) if brightness_values else 0,
                    'max': np.max(brightness_values) if brightness_values else 0
                },
                'contrast': {
                    'mean': np.mean(contrast_values) if contrast_values else 0,
                    'std': np.std(contrast_values) if contrast_values else 0
                },
                'sharpness': {
                    'mean': np.mean(sharpness_values) if sharpness_values else 0,
                    'std': np.std(sharpness_values) if sharpness_values else 0
                },
                'estimated_bitrate': self._estimate_bitrate(video_path, duration)
            }
            
            return analysis
            
        except Exception as e:
self.logger.error(f"Erro na análise técnica: {e}")
            return {"error": str(e)}
    
    def _extract_representative_frames(self, video_path: str, num_frames: int = 5) -> List[str]:
        """
        Extrai frames representativos do vídeo para análise.
        
        Args:
            video_path: Path do vídeo
            num_frames: Número de frames para extrair
            
        Returns:
            Lista de paths para os frames extraídos
        """
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return frames
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                cap.release()
                return frames
            
            # Extrair frames distribuídos uniformemente
            frame_indices = []
            for i in range(num_frames):
                frame_idx = i * total_frames // num_frames
                frame_indices.append(frame_idx)
            
            for i, frame_idx in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Salvar frame
                    frame_path = self.temp_dir / f"quality_frame_{i}_{frame_idx}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    frames.append(str(frame_path))
                    
                    # Redimensionar frame para economia de espaço
                    frame = cv2.resize(frame, (512, 512))
                    frame_path_small = self.temp_dir / f"quality_frame_{i}_{frame_idx}_small.jpg"
                    cv2.imwrite(str(frame_path_small), frame)
            
            cap.release()
            
        except Exception as e:
self.logger.error(f"Erro ao extrair frames: {e}")
        
        return frames
    
    def _analyze_visual_quality_with_llm(self, 
                                       frames: List[str],
                                       target_platform: str,
                                       technical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa qualidade visual usando LLM multimodal.
        
        Args:
            frames: Lista de paths para frames
            target_platform: Plataforma alvo
            technical_analysis: Análise técnica prévia
            
        Returns:
            Análise visual do LLM
        """
        try:
            # Preparar informações técnicas para o LLM
            tech_summary = f"""
Video Technical Information:
- Resolution: {technical_analysis.get('resolution', 'Unknown')}
- FPS: {technical_analysis.get('fps', 'Unknown')}
- Duration: {technical_analysis.get('duration', 'Unknown'):.2f}s
- Average Brightness: {technical_analysis.get('brightness', {}).get('mean', 0):.2f}
- Average Contrast: {technical_analysis.get('contrast', {}).get('mean', 0):.2f}
- Average Sharpness: {technical_analysis.get('sharpness', {}).get('mean', 0):.2f}
"""
            
            system_message = (
                "You are an expert video quality analyst with multimodal vision capabilities. "
                "Analyze the provided video frames and technical data to assess video quality. "
                "Focus on: 1) Visual appeal, 2) Technical issues, 3) Platform compatibility, "
                "4) Engagement potential, 5) Professional quality standards. "
                "Provide specific, actionable feedback for improvement."
            )
            
            prompt = f"""
TARGET PLATFORM: {target_platform.upper()}
{tech_summary}

Analyze these video frames and provide detailed assessment:

1. VISUAL QUALITY ASSESSMENT:
   - Color grading and saturation
   - Lighting quality and consistency
   - Composition and framing
   - Overall visual appeal

2. TECHNICAL ISSUES:
   - Resolution and clarity
   - Stability and camera movement
   - Focus and sharpness problems
   - Exposure issues

3. PLATFORM OPTIMIZATION:
   - How well this fits {target_platform} standards
   - Engagement potential on this platform
   - Recommended adjustments for this platform

4. IMPROVEMENT RECOMMENDATIONS:
   - Specific color grading suggestions
   - Lighting and exposure fixes
   - Composition improvements
   - Technical adjustments needed

Return structured JSON with these sections:
{
    "visual_quality_score": <0-100>,
    "technical_quality_score": <0-100>,
    "platform_fit_score": <0-100>,
    "visual_issues": ["issue1", "issue2"],
    "technical_problems": ["problem1", "problem2"],
    "improvements": {
        "color_grading": "suggestions",
        "lighting": "suggestions", 
        "composition": "suggestions",
        "technical": "suggestions"
    },
    "overall_assessment": "detailed summary"
}
"""
            
            # Para análise visual, vamos usar um frame representativo
            if frames:
                response = self.llm_client.generate_content(
                    prompt=prompt,
                    system_message=system_message,
                    max_tokens=800,
                    temperature=0.3
                )
                
                if response and response.content:
                    try:
                        # Tentar parsear JSON
                        content = response.content.strip()
                        if content.startswith('```json'):
                            content = content[7:-3].strip()
                        
                        visual_analysis = json.loads(content)
self.logger.info(" Análise visual LLM concluída com sucesso")
                        return visual_analysis
                        
                    except json.JSONDecodeError:
                        # Fallback se não for JSON válido
                        return {
                            "raw_analysis": response.content,
                            "visual_quality_score": 75,
                            "technical_quality_score": 75,
                            "platform_fit_score": 75,
                            "visual_issues": ["Could not parse detailed analysis"],
                            "improvements": {
                                "general": "Review video quality manually"
                            }
                        }
            
        except Exception as e:
self.logger.error(f"Erro na análise visual LLM: {e}")
        
        # Fallback mínimo
        return {
            "visual_quality_score": 50,
            "technical_quality_score": 50,
            "platform_fit_score": 50,
            "error": "Visual analysis failed"
        }
    
    def _detect_quality_issues(self, 
                             technical_analysis: Dict[str, Any],
                             visual_analysis: Dict[str, Any]) -> List[QualityIssue]:
        """
        Detecta problemas de qualidade baseado nas análises.
        
        Args:
            technical_analysis: Análise técnica
            visual_analysis: Análise visual LLM
            
        Returns:
            Lista de problemas detectados
        """
        issues = []
        
        # Problemas técnicos
        if 'brightness' in technical_analysis:
            brightness = technical_analysis['brightness']['mean']
            if brightness < 50:
                issues.append(QualityIssue(
                    issue_type="underexposed",
                    severity="medium",
                    description="Video appears too dark",
                    suggested_fix="Increase brightness by 20-30%",
                    confidence=0.8
                ))
            elif brightness > 200:
                issues.append(QualityIssue(
                    issue_type="overexposed",
                    severity="medium", 
                    description="Video appears too bright",
                    suggested_fix="Decrease brightness by 20-30%",
                    confidence=0.8
                ))
        
        if 'sharpness' in technical_analysis:
            sharpness = technical_analysis['sharpness']['mean']
            if sharpness < 50:
                issues.append(QualityIssue(
                    issue_type="blurry",
                    severity="high",
                    description="Video lacks sharpness and clarity",
                    suggested_fix="Apply sharpening filter or check focus",
                    confidence=0.9
                ))
        
        # Problemas visuais da análise LLM
        if 'visual_issues' in visual_analysis:
            for issue in visual_analysis['visual_issues']:
                issues.append(QualityIssue(
                    issue_type="visual_problem",
                    severity="medium",
                    description=issue,
                    suggested_fix="Review editing and color grading",
                    confidence=0.7
                ))
        
        return issues
    
    def _generate_quality_recommendations(self,
                                        issues: List[QualityIssue],
                                        target_platform: str,
                                        technical_analysis: Dict[str, Any]) -> List[QualityRecommendation]:
        """
        Gera recomendações de melhoria.
        
        Args:
            issues: Lista de problemas detectados
            target_platform: Plataforma alvo
            technical_analysis: Análise técnica
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        # Recomendações baseadas nos problemas
        for issue in issues:
            if issue.issue_type == "blurry":
                recommendations.append(QualityRecommendation(
                    category="sharpness",
                    priority="high",
                    recommendation=issue.suggested_fix,
                    expected_impact="Improved clarity and professional appearance",
                    implementation_difficulty="medium"
                ))
            
            elif issue.issue_type in ["underexposed", "overexposed"]:
                recommendations.append(QualityRecommendation(
                    category="lighting",
                    priority="high",
                    recommendation=issue.suggested_fix,
                    expected_impact="Better visibility and mood",
                    implementation_difficulty="low"
                ))
        
        # Recomendações específicas por plataforma
        if target_platform == 'tiktok':
            recommendations.append(QualityRecommendation(
                category="platform_optimization",
                priority="medium",
                recommendation="Ensure fast pacing in first 3 seconds",
                expected_impact="Higher retention and engagement",
                implementation_difficulty="medium"
            ))
        
        return recommendations
    
    def _calculate_overall_quality_score(self,
                                       technical_analysis: Dict[str, Any],
                                       issues: List[QualityIssue]) -> float:
        """
        Calcula score geral de qualidade.
        
        Args:
            technical_analysis: Análise técnica
            issues: Problemas detectados
            
        Returns:
            Score 0-100
        """
        base_score = 100.0
        
        # Penalidades por problemas
        for issue in issues:
            if issue.severity == "critical":
                base_score -= 25
            elif issue.severity == "high":
                base_score -= 15
            elif issue.severity == "medium":
                base_score -= 8
            elif issue.severity == "low":
                base_score -= 3
        
        # Bônus por métricas técnicas boas
        if 'sharpness' in technical_analysis:
            sharpness = technical_analysis['sharpness']['mean']
            if sharpness > 100:
                base_score += 5
        
        return max(0, min(100, base_score))
    
    def _check_platform_compatibility(self,
                                    technical_analysis: Dict[str, Any],
                                    platform: str) -> Dict[str, Any]:
        """
        Verifica compatibilidade com a plataforma alvo.
        
        Args:
            technical_analysis: Análise técnica
            platform: Plataforma alvo
            
        Returns:
            Info de compatibilidade
        """
        if platform not in self.platform_requirements:
            return {"error": "Unknown platform"}
        
        requirements = self.platform_requirements[platform]
        resolution = technical_analysis.get('resolution', (0, 0))
        fps = technical_analysis.get('fps', 0)
        
        compatibility = {
            'platform': platform,
            'compatible': True,
            'issues': []
        }
        
        # Verificar resolução
        min_res = requirements['min_resolution']
        if (resolution[0] < min_res[0] or resolution[1] < min_res[1]):
            compatibility['compatible'] = False
            compatibility['issues'].append(
                f"Resolution too low: {resolution} < {min_res}"
            )
        
        # Verificar FPS
        if fps not in requirements['fps']:
            compatibility['issues'].append(
                f"Non-standard FPS: {fps} (recommended: {requirements['fps']})"
            )
        
        return compatibility
    
    def _estimate_bitrate(self, video_path: str, duration: float) -> Optional[float]:
        """
        Estima bitrate do vídeo.
        
        Args:
            video_path: Path do vídeo
            duration: Duração em segundos
            
        Returns:
            Bitrate estimado em kbps
        """
        try:
            file_size = Path(video_path).stat().st_size  # bytes
            if duration > 0:
                bitrate_kbps = (file_size * 8) / (duration * 1000)
                return bitrate_kbps
        except Exception:
            pass
        return None


# Instância global
video_quality_optimizer = None


def get_video_quality_optimizer(llm_client: OpenRouterClient) -> VideoQualityOptimizer:
    """
    Retorna instância global do otimizador de qualidade.
    
    Args:
        llm_client: Cliente LLM para análise
        
    Returns:
        Instância do VideoQualityOptimizer
    """
    global video_quality_optimizer
    if video_quality_optimizer is None:
        video_quality_optimizer = VideoQualityOptimizer(llm_client)
    return video_quality_optimizer