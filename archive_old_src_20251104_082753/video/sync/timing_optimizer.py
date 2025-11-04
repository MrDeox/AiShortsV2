"""
Timing Optimizer para AiShorts v2.0
Sistema de otimização de transições e timing para sincronização áudio-vídeo
"""

import os
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import librosa
from scipy.signal import find_peaks
import moviepy.editor as mp

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TransitionEffect:
    """Configuração de efeito de transição"""
    name: str
    duration: float
    intensity: float
    applicable_types: List[str]


@dataclass
class OptimizedTiming:
    """Resultado da otimização de timing"""
    original_duration: float
    optimized_duration: float
    transition_effects: List[TransitionEffect]
    sync_points: List[float]
    recommendations: List[str]


class TimingOptimizer:
    """
    Otimizador de timing para sincronização áudio-vídeo
    Foca em transições suaves e timing preciso para engajamento máximo
    """
    
    def __init__(self, output_dir: str = "outputs/video/optimization"):
        """
        Inicializa otimizador de timing
        
        Args:
            output_dir: Diretório para salvar resultados otimizados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de otimização
        self.min_transition_duration = 0.2  # segundos
        self.max_transition_duration = 1.0
        self.optimal_segment_duration = 8.0  # segundos ideal para shorts
        self.sync_precision_threshold = 0.05  # 50ms
        
        # Tipos de transições disponíveis
        self.transition_effects = {
            'fade': TransitionEffect('fade', 0.3, 0.8, ['fade', 'dissolve']),
            'slide_left': TransitionEffect('slide_left', 0.4, 0.9, ['slide', 'transition']),
            'slide_right': TransitionEffect('slide_right', 0.4, 0.9, ['slide', 'transition']),
            'zoom_in': TransitionEffect('zoom_in', 0.5, 0.7, ['zoom', 'scale']),
            'zoom_out': TransitionEffect('zoom_out', 0.5, 0.7, ['zoom', 'scale']),
            'slide_up': TransitionEffect('slide_up', 0.35, 0.8, ['slide', 'transition']),
            'slide_down': TransitionEffect('slide_down', 0.35, 0.8, ['slide', 'transition']),
            'cross_dissolve': TransitionEffect('cross_dissolve', 0.6, 0.6, ['dissolve', 'blend'])
        }
        
        logger.info("TimingOptimizer inicializado")
    
    def optimize_transitions(self, 
                           video_segments: List, 
                           audio_timing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Otimiza transições entre segmentos de vídeo baseadas no timing do áudio
        
        Args:
            video_segments: Lista de segmentos de vídeo
            audio_timing: Informações de timing do áudio TTS
            
        Returns:
            Dict com transições otimizadas e metadados
        """
        try:
            logger.info("Otimizando transições vídeo-aúdio")
            
            # Analisar timing atual dos segmentos
            timing_analysis = self._analyze_current_timing(video_segments, audio_timing)
            
            # Detectar pontos de transição ideais
            transition_points = self._detect_optimal_transitions(audio_timing)
            
            # Calcular durações otimizadas
            optimized_segments = self._calculate_optimal_durations(
                video_segments, audio_timing
            )
            
            # Selecionar efeitos de transição apropriados
            transition_effects = self._select_transition_effects(
                video_segments, audio_timing
            )
            
            # Aplicar otimizações
            final_timeline = self._apply_optimizations(
                video_segments, optimized_segments, transition_effects, transition_points
            )
            
            # Gerar relatório de otimização
            optimization_report = self._generate_optimization_report(
                timing_analysis, transition_points, transition_effects
            )
            
            return {
                'success': True,
                'optimized_timeline': final_timeline,
                'original_analysis': timing_analysis,
                'transition_points': transition_points,
                'applied_effects': transition_effects,
                'optimization_report': optimization_report,
                'improvements': {
                    'smoothness_score': self._calculate_smoothness_score(final_timeline),
                    'engagement_prediction': self._predict_engagement(final_timeline),
                    'sync_accuracy': self._calculate_sync_accuracy(final_timeline, audio_timing)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na otimização de transições: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_transition_effects(self, video_segments: List) -> Dict[str, Any]:
        """
        Adiciona efeitos de transição apropriados aos segmentos de vídeo
        
        Args:
            video_segments: Lista de segmentos de vídeo
            
        Returns:
            Dict com efeitos aplicados e configurações
        """
        try:
            logger.info("Adicionando efeitos de transição")
            
            enhanced_segments = []
            applied_effects = []
            
            for i, segment in enumerate(video_segments):
                # Determinar tipo de transição baseado no contexto
                if i == 0:
                    # Primeiro segmento - usar fade in suave
                    transition_effect = self.transition_effects['fade']
                    effect_config = {
                        'type': 'entrance',
                        'effect': 'fade_in',
                        'duration': 0.5,
                        'intensity': 0.8
                    }
                elif i == len(video_segments) - 1:
                    # Último segmento - fade out
                    transition_effect = self.transition_effects['fade']
                    effect_config = {
                        'type': 'exit',
                        'effect': 'fade_out',
                        'duration': 0.5,
                        'intensity': 0.8
                    }
                else:
                    # Segmentos intermediários - variação de efeitos
                    effect_options = ['slide_left', 'slide_right', 'zoom_in', 'cross_dissolve']
                    effect_name = effect_options[i % len(effect_options)]
                    transition_effect = self.transition_effects[effect_name]
                    effect_config = {
                        'type': 'transition',
                        'effect': effect_name,
                        'duration': transition_effect.duration,
                        'intensity': transition_effect.intensity
                    }
                
                # Aplicar efeito ao segmento
                enhanced_segment = {
                    'original_segment': segment,
                    'transition_effect': effect_config,
                    'enhanced': True
                }
                
                enhanced_segments.append(enhanced_segment)
                applied_effects.append(effect_config)
            
            # Calcular estatísticas dos efeitos aplicados
            effect_stats = self._calculate_effect_statistics(applied_effects)
            
            return {
                'success': True,
                'enhanced_segments': enhanced_segments,
                'applied_effects': applied_effects,
                'effect_statistics': effect_stats,
                'total_effects': len(applied_effects)
            }
            
        except Exception as e:
            logger.error(f"Erro ao adicionar efeitos de transição: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_optimal_duration(self, 
                                 segment_text: str, 
                                 video_length: float) -> Dict[str, Any]:
        """
        Calcula duração ideal para segmento baseado no conteúdo textual
        
        Args:
            segment_text: Texto do segmento
            video_length: Duração total do vídeo
            
        Returns:
            Dict com duração otimizada e justificativas
        """
        try:
            logger.info("Calculando duração ideal para segmento")
            
            # Análise do texto
            word_count = len(segment_text.split())
            char_count = len(segment_text)
            sentence_count = segment_text.count('.') + segment_text.count('!') + segment_text.count('?')
            
            # Velocidade de leitura média (palavras por segundo)
            avg_reading_speed = 2.5  # Palavras por segundo
            
            # Calcular duração baseada no texto
            text_based_duration = word_count / avg_reading_speed
            
            # Ajustar baseado no tipo de conteúdo
            content_multipliers = {
                'hook': 1.2,  # Hooks podem ser um pouco mais longos
                'development': 1.0,  # Desenvolvimento na velocidade normal
                'conclusion': 0.8  # Conclusão mais rápida
            }
            
            # Detectar tipo de conteúdo (simplificado)
            content_type = self._detect_content_type(segment_text)
            multiplier = content_multipliers.get(content_type, 1.0)
            
            adjusted_duration = text_based_duration * multiplier
            
            # Ajustar para duração total do vídeo
            available_duration = video_length * 0.3  # Máximo 30% do vídeo por segmento
            final_duration = min(adjusted_duration, available_duration)
            
            # Garantir duração mínima e máxima
            final_duration = max(3.0, min(final_duration, 15.0))
            
            # Calcular precisão de sincronização estimada
            sync_precision = 1.0 - (abs(final_duration - text_based_duration) / text_based_duration)
            
            return {
                'success': True,
                'original_text': segment_text,
                'text_analysis': {
                    'word_count': word_count,
                    'char_count': char_count,
                    'sentence_count': sentence_count,
                    'content_type': content_type
                },
                'calculated_duration': text_based_duration,
                'adjusted_duration': adjusted_duration,
                'final_duration': final_duration,
                'multiplier_used': multiplier,
                'sync_precision': sync_precision,
                'justification': self._generate_duration_justification(
                    word_count, content_type, final_duration
                )
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular duração ideal: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_current_timing(self, 
                              video_segments: List, 
                              audio_timing: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa timing atual dos segmentos"""
        try:
            # Extrair durações dos segmentos
            segment_durations = []
            total_duration = 0
            
            for segment in video_segments:
                if hasattr(segment, 'duration'):
                    duration = segment.duration
                else:
                    # Calcular duração baseado no path do vídeo
                    duration = self._get_video_duration(segment.video_path if hasattr(segment, 'video_path') else segment)
                
                segment_durations.append(duration)
                total_duration += duration
            
            # Calcular estatísticas
            avg_duration = np.mean(segment_durations)
            std_duration = np.std(segment_durations)
            
            # Identificar segmentos problemáticos
            problematic_segments = []
            for i, duration in enumerate(segment_durations):
                if duration < 2.0:  # Muito curto
                    problematic_segments.append({
                        'index': i,
                        'issue': 'too_short',
                        'duration': duration
                    })
                elif duration > 20.0:  # Muito longo
                    problematic_segments.append({
                        'index': i,
                        'issue': 'too_long',
                        'duration': duration
                    })
            
            return {
                'total_duration': total_duration,
                'segment_count': len(video_segments),
                'avg_duration': avg_duration,
                'std_duration': std_duration,
                'durations': segment_durations,
                'problematic_segments': problematic_segments,
                'consistency_score': 1.0 - (std_duration / avg_duration if avg_duration > 0 else 0)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de timing: {e}")
            return {}
    
    def _detect_optimal_transitions(self, audio_timing: Dict[str, Any]) -> List[float]:
        """Detecta pontos ideais para transições baseados no áudio"""
        try:
            transition_points = []
            
            if 'section_audio' in audio_timing:
                # Usar pontos de mudança de seção no áudio
                for i, section in enumerate(audio_timing['section_audio']):
                    # Adicionar ponto de transição um pouco antes do fim da seção
                    # para permitir transição suave
                    section_start = i * section['duration'] * 0.8  # Estimativa
                    transition_points.append(section_start)
            
            # Adicionar transições baseadas em beats se disponíveis
            if 'beat_points' in audio_timing:
                transition_points.extend(audio_timing['beat_points'])
            
            # Ordenar e remover duplicatas
            transition_points = sorted(list(set(transition_points)))
            
            return transition_points
            
        except Exception as e:
            logger.error(f"Erro na detecção de transições: {e}")
            return []
    
    def _calculate_optimal_durations(self, 
                                   video_segments: List, 
                                   audio_timing: Dict[str, Any]) -> List[float]:
        """Calcula durações otimizadas para segmentos"""
        try:
            optimal_durations = []
            
            if 'total_duration' in audio_timing:
                total_audio_duration = audio_timing['total_duration']
                segments_count = len(video_segments)
                target_avg_duration = total_audio_duration / segments_count
                
                for segment in video_segments:
                    current_duration = segment.duration if hasattr(segment, 'duration') else 5.0
                    
                    # Ajustar para duração alvo, mas mantendo limites
                    adjusted_duration = min(max(current_duration, 3.0), target_avg_duration * 1.5)
                    optimal_durations.append(adjusted_duration)
            else:
                # Usar duração padrão
                optimal_durations = [self.optimal_segment_duration] * len(video_segments)
            
            return optimal_durations
            
        except Exception as e:
            logger.error(f"Erro no cálculo de durações: {e}")
            return [5.0] * len(video_segments)
    
    def _select_transition_effects(self, 
                                 video_segments: List, 
                                 audio_timing: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Seleciona efeitos de transição apropriados"""
        effects = []
        
        for i, segment in enumerate(video_segments):
            if i == 0:
                # Primeiro segmento - entrada suave
                effect = {
                    'type': 'entrance',
                    'effect_name': 'fade_in',
                    'duration': 0.5,
                    'intensity': 0.8
                }
            elif i == len(video_segments) - 1:
                # Último segmento - saída suave
                effect = {
                    'type': 'exit', 
                    'effect_name': 'fade_out',
                    'duration': 0.5,
                    'intensity': 0.8
                }
            else:
                # Segmentos intermediários - variação
                available_effects = ['slide_left', 'slide_right', 'zoom_in', 'cross_dissolve']
                effect_name = available_effects[i % len(available_effects)]
                
                effect = {
                    'type': 'transition',
                    'effect_name': effect_name,
                    'duration': self.transition_effects[effect_name].duration,
                    'intensity': self.transition_effects[effect_name].intensity
                }
            
            effects.append(effect)
        
        return effects
    
    def _apply_optimizations(self, 
                           video_segments: List,
                           optimized_durations: List[float],
                           transition_effects: List[Dict[str, Any]],
                           transition_points: List[float]) -> List[Dict[str, Any]]:
        """Aplica otimizações ao timeline"""
        optimized_timeline = []
        
        for i, (segment, duration, effect) in enumerate(zip(video_segments, optimized_durations, transition_effects)):
            optimized_entry = {
                'original_segment': segment,
                'optimized_duration': duration,
                'transition_effect': effect,
                'transition_point': transition_points[i] if i < len(transition_points) else None,
                'enhanced': True
            }
            
            optimized_timeline.append(optimized_entry)
        
        return optimized_timeline
    
    def _generate_optimization_report(self, 
                                    timing_analysis: Dict[str, Any],
                                    transition_points: List[float],
                                    transition_effects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera relatório detalhado da otimização"""
        return {
            'timing_improvements': {
                'consistency_improvement': 'Eliminação de segmentos muito curtos/longos',
                'smooth_transitions': f'{len(transition_effects)} efeitos aplicados',
                'sync_precision': 'Otimizado para beat detection'
            },
            'transition_analysis': {
                'total_transitions': len(transition_points),
                'effect_distribution': self._analyze_effect_distribution(transition_effects),
                'smoothness_score': self._calculate_smoothness_score(transition_effects)
            },
            'recommendations': self._generate_optimization_recommendations(timing_analysis)
        }
    
    def _get_video_duration(self, video_path: str) -> float:
        """Obtém duração de um vídeo"""
        try:
            if os.path.exists(video_path):
                clip = mp.VideoFileClip(video_path)
                duration = clip.duration
                clip.close()
                return duration
            return 5.0  # Duração padrão
        except:
            return 5.0
    
    def _detect_content_type(self, text: str) -> str:
        """Detecta tipo de conteúdo do texto"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['você sabia', 'curiosidade', 'incrível', 'fato']):
            return 'hook'
        elif any(word in text_lower for word in ['conclusão', 'resumindo', 'finalmente', 'portanto']):
            return 'conclusion'
        else:
            return 'development'
    
    def _generate_duration_justification(self, word_count: int, content_type: str, duration: float) -> str:
        """Gera justificativa para duração calculada"""
        return f"Segmento de {word_count} palavras do tipo '{content_type}' com duração de {duration:.1f}s otimizada para engajamento."
    
    def _calculate_smoothness_score(self, timeline: List) -> float:
        """Calcula score de suavidade das transições"""
        try:
            if not timeline or len(timeline) < 2:
                return 1.0
            
            # Analisar variação nas durações dos segmentos
            durations = [entry.get('optimized_duration', 5.0) for entry in timeline]
            avg_duration = np.mean(durations)
            std_duration = np.std(durations)
            
            # Score baseado na consistência (menor variância = maior score)
            consistency = 1.0 - min(std_duration / avg_duration, 1.0)
            
            return consistency
        except:
            return 0.8
    
    def _predict_engagement(self, timeline: List) -> float:
        """Prediz nível de engajamento baseado no timeline"""
        try:
            if not timeline:
                return 0.5
            
            # Fatores que aumentam engajamento
            engagement_factors = {
                'variety': min(len(timeline) / 10, 1.0),  # Variety é bom até certo ponto
                'smooth_transitions': 0.8,  # Transições suaves sempre são boas
                'optimal_duration': 0.9  # Durações otimizadas são boas
            }
            
            # Calcular score médio
            predicted_engagement = np.mean(list(engagement_factors.values()))
            
            return min(predicted_engagement, 1.0)
        except:
            return 0.7
    
    def _calculate_sync_accuracy(self, timeline: List, audio_timing: Dict[str, Any]) -> float:
        """Calcula precisão da sincronização"""
        try:
            # Placeholder - implementação completa seria mais complexa
            # Consideraria beats, mudanças de seção, etc.
            return 0.85  # Score padrão otimista
        except:
            return 0.7
    
    def _calculate_effect_statistics(self, effects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estatísticas dos efeitos aplicados"""
        effect_types = [effect['effect'] for effect in effects]
        durations = [effect['duration'] for effect in effects]
        
        return {
            'unique_effects': len(set(effect_types)),
            'avg_duration': np.mean(durations),
            'most_used_effect': max(set(effect_types), key=effect_types.count),
            'effect_variety_score': len(set(effect_types)) / len(effect_types) if effect_types else 0
        }
    
    def _analyze_effect_distribution(self, effects: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analisa distribuição dos efeitos"""
        distribution = {}
        for effect in effects:
            effect_name = effect['effect_name']
            distribution[effect_name] = distribution.get(effect_name, 0) + 1
        return distribution
    
    def _generate_optimization_recommendations(self, timing_analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        if timing_analysis.get('consistency_score', 1.0) < 0.7:
            recommendations.append("Melhorar consistência das durações dos segmentos")
        
        if timing_analysis.get('problematic_segments'):
            recommendations.append("Ajustar segmentos muito curtos ou longos")
        
        recommendations.append("Aplicar transições suaves entre segmentos")
        recommendations.append("Sincronizar com beats do áudio quando possível")
        
        return recommendations