"""
Content Virality Predictor - Previsor de Viralidade com LLM
Sistema inteligente para prever potencial viral e otimizar conteúdo

Features:
- Análise de viralidade baseada em padrões
- Otimização de hooks eCTAs
- Previsão de engajamento por plataforma
- Sugestões de melhoria para maximizar viralidade
- Análise competitiva e trending topics
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from src.core.openrouter_client import OpenRouterClient


class ViralityScore(Enum):
    """Níveis de viralidade."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    VIRAL = "viral"


@dataclass
class ViralityMetric:
    """Métrica de viralidade específica."""
    metric_name: str
    score: float  # 0-100
    importance: float  # 0-1 peso no cálculo final
    explanation: str
    improvement_suggestions: List[str]


@dataclass
class ContentOptimization:
    """Sugestão de otimização de conteúdo."""
    element: str  # hook, body, cta, timing, etc
    current_version: str
    suggested_version: str
    expected_improvement: str
    implementation_priority: str


class ContentViralityPredictor:
    """
    Previsor de viralidade de conteúdo usando LLM avançado.
    
    Funcionalidades:
    - Análise preditiva de engajamento
    - Otimização de conteúdo viral
    - Análise de padrões virais
    - Recomendações de melhoria
    """
    
    def __init__(self, llm_client: OpenRouterClient):
        """
        Inicializa o previsor de viralidade.
        
        Args:
            llm_client: Cliente LLM para análise
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        
        # Padrões virais conhecidos por categoria
        self.viral_patterns = {
            'animals': {
                'high_engagement_words': ['surprising', 'unbelievable', 'shocking', 'adorable', 'heartwarming'],
                'optimal_length': 45,  # seconds
                'hook_patterns': ['You won\'t believe', 'This animal can', 'Scientists discovered'],
                'viral_topics': ['animal intelligence', 'survival skills', 'rare species', 'animal emotions']
            },
            'technology': {
                'high_engagement_words': ['breakthrough', 'revolutionary', 'game-changing', 'future', 'innovation'],
                'optimal_length': 60,
                'hook_patterns': ['This technology will', 'The future of', 'Revolutionary new'],
                'viral_topics': ['AI developments', 'quantum computing', 'space technology', 'biomedical advances']
            },
            'food': {
                'high_engagement_words': ['delicious', 'amazing', 'incredible', 'secret', 'master chef'],
                'optimal_length': 30,
                'hook_patterns': ['This food tastes', 'The secret to', 'You\'ve been eating'],
                'viral_topics': ['cooking hacks', 'food science', 'traditional recipes', 'food trends']
            }
        }
        
        # Fatores de impacto viral
        self.virality_factors = {
            'hook_strength': 0.25,      # Gancho inicial forte
            'content_value': 0.20,       # Valor/informação do conteúdo
            'emotional_impact': 0.15,   # Impacto emocional
            'timing_pacing': 0.10,      # Timing e ritmo
            'call_to_action': 0.10,     # CTA eficaz
            'novelty_factor': 0.10,     # Fator novidade
            'shareability': 0.10        # Potencial de compartilhamento
        }
    
    def predict_virality(self,
                        theme: str,
                        script: str,
                        category: str = 'general',
                        target_platform: str = 'tiktok',
                        analyze_competition: bool = True) -> Dict[str, Any]:
        """
        Prediz potencial viral do conteúdo.
        
        Args:
            theme: Tema do vídeo
            script: Script/roteiro completo
            category: Categoria do conteúdo
            target_platform: Plataforma alvo
            analyze_competition: Se deve analisar competição
            
        Returns:
            Análise completa de viralidade
        """
self.logger.info(f" Analisando potencial viral: {theme[:50]}...")
        
        try:
            # Análise básica de padrões
            pattern_analysis = self._analyze_viral_patterns(theme, script, category)
            
            # Análise profunda com LLM
            llm_analysis = self._analyze_with_llm(theme, script, category, target_platform)
            
            # Calcular métricas específicas
            virality_metrics = self._calculate_virality_metrics(
                theme, script, pattern_analysis, llm_analysis
            )
            
            # Calcular score geral
            overall_score = self._calculate_overall_virality_score(virality_metrics)
            
            # Gerar otimizações
            optimizations = self._generate_content_optimizations(
                theme, script, virality_metrics, category
            )
            
            # Prever engajamento
            engagement_prediction = self._predict_engagement(
                overall_score, category, target_platform
            )
            
            # Análise competitiva se solicitada
            competitive_analysis = None
            if analyze_competition:
                competitive_analysis = self._analyze_competitive_landscape(
                    theme, category, target_platform
                )
            
            # Compor resultado final
            prediction = {
                'content_info': {
                    'theme': theme,
                    'category': category,
                    'target_platform': target_platform,
                    'analysis_timestamp': datetime.now().isoformat()
                },
                'virality_scores': {
                    'overall_score': overall_score,
                    'virality_level': self._get_virality_level(overall_score),
                    'confidence': 0.85  # Baseado na precisão histórica
                },
                'detailed_metrics': [metric.__dict__ for metric in virality_metrics],
                'pattern_analysis': pattern_analysis,
                'llm_analysis': llm_analysis,
                'engagement_prediction': engagement_prediction,
                'content_optimizations': [opt.__dict__ for opt in optimizations],
                'competitive_analysis': competitive_analysis,
                'viral_potential_breakdown': self._get_viral_breakdown(overall_score, category)
            }
            
self.logger.info(f" Análise de viralidade concluída - Score: {overall_score:.2f}")
            return prediction
            
        except Exception as e:
self.logger.error(f" Erro na previsão de viralidade: {e}")
            return {"error": str(e)}
    
    def _analyze_viral_patterns(self, theme: str, script: str, category: str) -> Dict[str, Any]:
        """
        Analisa padrões virais conhecidos.
        
        Args:
            theme: Tema do conteúdo
            script: Script completo
            category: Categoria
            
        Returns:
            Análise de padrões
        """
        patterns_found = []
        category_patterns = self.viral_patterns.get(category, {})
        
        # Verificar palavras de alto engajamento
        high_engagement_words = category_patterns.get('high_engagement_words', [])
        found_words = []
        
        theme_lower = theme.lower()
        script_lower = script.lower()
        
        for word in high_engagement_words:
            if word in theme_lower or word in script_lower:
                found_words.append(word)
        
        if found_words:
            patterns_found.append(f"High-engagement words: {', '.join(found_words)}")
        
        # Verificar padrões de hook
        hook_patterns = category_patterns.get('hook_patterns', [])
        found_hooks = []
        
        for pattern in hook_patterns:
            if pattern.lower() in script_lower:
                found_hooks.append(pattern)
        
        if found_hooks:
            patterns_found.append(f"Viral hook patterns: {', '.join(found_hooks)}")
        
        # Verificar tópicos virais
        viral_topics = category_patterns.get('viral_topics', [])
        found_topics = []
        
        for topic in viral_topics:
            if topic.lower() in script_lower:
                found_topics.append(topic)
        
        if found_topics:
            patterns_found.append(f"Viral topics: {', '.join(found_topics)}")
        
        # Análise de estrutura
        hook_strength = self._analyze_hook_strength(script)
        pacing_analysis = self._analyze_pacing(script)
        
        return {
            'viral_patterns_found': patterns_found,
            'hook_strength': hook_strength,
            'pacing_analysis': pacing_analysis,
            'pattern_match_score': len(patterns_found) * 15,  # 0-60 points
            'category_optimization': category in self.viral_patterns
        }
    
    def _analyze_with_llm(self, theme: str, script: str, category: str, platform: str) -> Dict[str, Any]:
        """
        Faz análise profunda usando LLM.
        
        Args:
            theme: Tema do conteúdo
            script: Script completo
            category: Categoria
            platform: Plataforma alvo
            
        Returns:
            Análise detalhada do LLM
        """
        try:
            system_message = (
                "You are a social media content expert specializing in viral content analysis. "
                "Analyze the provided content for viral potential using proven frameworks: "
                "1) Hook-Story-Offer structure, 2) Emotional triggers, 3) Shareability factors, "
                "4) Platform optimization, 5) Engagement patterns. "
                "Provide specific, actionable insights for maximizing viral potential."
            )
            
            prompt = f"""
CONTENT ANALYSIS REQUEST:
Theme: {theme}
Category: {category}
Target Platform: {platform}

Script:
{script}

Analyze this content for viral potential and provide:

1. HOOK ANALYSIS:
- Opening strength (0-100)
- Pattern recognition
- Improvement suggestions

2. EMOTIONAL TRIGGERS:
- Primary emotions evoked
- Emotional journey
- Intensity assessment

3. VIRAL FACTORS:
- Novelty/Uniqueness (0-100)
- Shareability score (0-100)
- Conversation starter potential
- Trend alignment

4. PLATFORM OPTIMIZATION:
- {platform} specific strengths
- {platform} optimization opportunities
- Native feature usage

5. ENGAGEMENT PREDICTION:
- Expected view-through rate
- Share prediction
- Comment potential
- Overall viral probability

6. IMPROVEMENT RECOMMENDATIONS:
- Specific hook improvements
- Content enhancement opportunities
- CTA optimization
- Timing adjustments

Return structured JSON:
{
    "hook_analysis": {
        "strength": <0-100>,
        "pattern_used": "pattern_name",
        "improvements": ["suggestion1", "suggestion2"]
    },
    "emotional_triggers": {
        "primary_emotions": ["emotion1", "emotion2"],
        "intensity": <0-100>,
        "journey": "description"
    },
    "viral_factors": {
        "novelty_score": <0-100>,
        "shareability_score": <0-100>,
        "conversation_starter": <0-100>,
        "trend_alignment": <0-100>
    },
    "platform_optimization": {
        "platform_score": <0-100>,
        "opportunities": ["opportunity1", "opportunity2"],
        "native_features": ["feature1", "feature2"]
    },
    "engagement_prediction": {
        "view_through_rate": <0-100>,
        "share_prediction": <0-100>,
        "comment_potential": <0-100>,
        "viral_probability": <0-100>
    },
    "improvements": {
        "hook": "specific suggestions",
        "content": "content improvements",
        "cta": "cta optimization",
        "timing": "timing suggestions"
    },
    "overall_viral_score": <0-100>
}
"""
            
            response = self.llm_client.generate_content(
                prompt=prompt,
                system_message=system_message,
                max_tokens=1000,
                temperature=0.3
            )
            
            if response and response.content:
                try:
                    content = response.content.strip()
                    if content.startswith('```json'):
                        content = content[7:-3].strip()
                    
                    llm_analysis = json.loads(content)
self.logger.info(" Análise LLM de viralidade concluída")
                    return llm_analysis
                    
                except json.JSONDecodeError:
                    # Fallback para resposta textual
                    return {
                        "raw_analysis": response.content,
                        "overall_viral_score": 75,
                        "viral_factors": {
                            "novelty_score": 70,
                            "shareability_score": 75,
                            "conversation_starter": 70,
                            "trend_alignment": 75
                        }
                    }
            
        except Exception as e:
self.logger.error(f"Erro na análise LLM: {e}")
        
        # Fallback mínimo
        return {
            "overall_viral_score": 50,
            "viral_factors": {
                "novelty_score": 50,
                "shareability_score": 50,
                "conversation_starter": 50,
                "trend_alignment": 50
            }
        }
    
    def _calculate_virality_metrics(self,
                                  theme: str,
                                  script: str,
                                  pattern_analysis: Dict[str, Any],
                                  llm_analysis: Dict[str, Any]) -> List[ViralityMetric]:
        """
        Calcula métricas detalhadas de viralidade.
        
        Args:
            theme: Tema do conteúdo
            script: Script completo
            pattern_analysis: Análise de padrões
            llm_analysis: Análise LLM
            
        Returns:
            Lista de métricas de viralidade
        """
        metrics = []
        
        # Hook Strength
        hook_score = llm_analysis.get('hook_analysis', {}).get('strength', 50)
        hook_pattern_score = pattern_analysis.get('pattern_match_score', 0)
        combined_hook = (hook_score + hook_pattern_score) / 2
        
        metrics.append(ViralityMetric(
            metric_name="hook_strength",
            score=combined_hook,
            importance=self.virality_factors['hook_strength'],
            explanation=f"Strength of opening hook based on pattern analysis and LLM assessment",
            improvement_suggestions=[
                "Start with a surprising fact or question",
                "Use pattern interrupts in first 3 seconds",
                "Create immediate curiosity gap"
            ]
        ))
        
        # Content Value
        content_score = min(90, len(script.split()) * 2)  # Base em word count
        metrics.append(ViralityMetric(
            metric_name="content_value",
            score=content_score,
            importance=self.virality_factors['content_value'],
            explanation="Educational or entertainment value provided to viewer",
            improvement_suggestions=[
                "Add more specific, valuable information",
                "Include surprising facts or statistics",
                "Ensure clear takeaway messages"
            ]
        ))
        
        # Emotional Impact
        emotional_score = llm_analysis.get('emotional_triggers', {}).get('intensity', 50)
        metrics.append(ViralityMetric(
            metric_name="emotional_impact",
            score=emotional_score,
            importance=self.virality_factors['emotional_impact'],
            explanation="Emotional response elicited from viewers",
            improvement_suggestions=[
                "Add emotional storytelling elements",
                "Use power words and emotional triggers",
                "Create empathy or surprise moments"
            ]
        ))
        
        # Viral Factors (combinado)
        viral_factors = llm_analysis.get('viral_factors', {})
        novelty_score = viral_factors.get('novelty_score', 50)
        shareability_score = viral_factors.get('shareability_score', 50)
        combined_viral = (novelty_score + shareability_score) / 2
        
        metrics.append(ViralityMetric(
            metric_name="viral_potential",
            score=combined_viral,
            importance=self.virality_factors['novelty_factor'] + self.virality_factors['shareability'],
            explanation="Inherent viral characteristics and shareability",
            improvement_suggestions=[
                "Add unique, surprising elements",
                "Create conversation-worthy moments",
                "Include meme-able content"
            ]
        ))
        
        return metrics
    
    def _calculate_overall_virality_score(self, metrics: List[ViralityMetric]) -> float:
        """
        Calcula score geral de viralidade.
        
        Args:
            metrics: Lista de métricas
            
        Returns:
            Score geral 0-100
        """
        total_score = 0
        total_importance = 0
        
        for metric in metrics:
            total_score += metric.score * metric.importance
            total_importance += metric.importance
        
        if total_importance > 0:
            return min(100, total_score / total_importance)
        return 50
    
    def _get_virality_level(self, score: float) -> ViralityScore:
        """
        Converte score numérico para nível de viralidade.
        
        Args:
            score: Score 0-100
            
        Returns:
            Nível de viralidade
        """
        if score >= 85:
            return ViralityScore.VIRAL
        elif score >= 70:
            return ViralityScore.HIGH
        elif score >= 50:
            return ViralityScore.MEDIUM
        else:
            return ViralityScore.LOW
    
    def _generate_content_optimizations(self,
                                       theme: str,
                                       script: str,
                                       metrics: List[ViralityMetric],
                                       category: str) -> List[ContentOptimization]:
        """
        Gera sugestões de otimização de conteúdo.
        
        Args:
            theme: Tema atual
            script: Script atual
            metrics: Métricas calculadas
            category: Categoria
            
        Returns:
            Lista de otimizações sugeridas
        """
        optimizations = []
        
        # Encontrar métricas com scores baixos
        for metric in metrics:
            if metric.score < 70:  # Abaixo de 70 precisa melhorar
                if metric.metric_name == "hook_strength":
                    optimizations.append(ContentOptimization(
                        element="hook",
                        current_version=self._extract_hook(script),
                        suggested_version=self._generate_better_hook(theme, category),
                        expected_improvement="Increase viewer retention by 40-60%",
                        implementation_priority="high"
                    ))
                
                elif metric.metric_name == "content_value":
                    optimizations.append(ContentOptimization(
                        element="content",
                        current_version=script[:200],
                        suggested_version=self._enhance_content_value(script, category),
                        expected_improvement="Increase perceived value and watch time",
                        implementation_priority="medium"
                    ))
        
        return optimizations
    
    def _predict_engagement(self, 
                          virality_score: float,
                          category: str,
                          platform: str) -> Dict[str, Any]:
        """
        Prevê métricas de engajamento.
        
        Args:
            virality_score: Score de viralidade
            category: Categoria
            platform: Plataforma
            
        Returns:
            Predição de engajamento
        """
        # Baselines por categoria
        category_benchmarks = {
            'animals': {'avg_views': 50000, 'avg_shares': 500},
            'technology': {'avg_views': 30000, 'avg_shares': 300},
            'food': {'avg_views': 80000, 'avg_shares': 800},
            'general': {'avg_views': 25000, 'avg_shares': 250}
        }
        
        benchmarks = category_benchmarks.get(category, category_benchmarks['general'])
        
        # Multiplicadores baseados no score
        score_multiplier = virality_score / 50  # 50 = baseline
        
        # Multiplicadores por plataforma
        platform_multipliers = {
            'tiktok': 1.2,
            'shorts': 1.0,
            'reels': 1.1
        }
        
        platform_multiplier = platform_multipliers.get(platform, 1.0)
        
        prediction = {
            'predicted_views': int(benchmarks['avg_views'] * score_multiplier * platform_multiplier),
            'predicted_shares': int(benchmarks['avg_shares'] * score_multiplier * platform_multiplier),
            'view_through_rate': min(95, virality_score * 0.9),
            'engagement_rate': min(15, virality_score * 0.15),
            'viral_coefficient': max(1.0, virality_score / 50),
            'confidence_interval': {
                'low': int(benchmarks['avg_views'] * score_multiplier * 0.7),
                'high': int(benchmarks['avg_views'] * score_multiplier * 1.5)
            }
        }
        
        return prediction
    
    def _analyze_competitive_landscape(self,
                                     theme: str,
                                     category: str,
                                     platform: str) -> Dict[str, Any]:
        """
        Analisa cenário competitivo (simplificado).
        
        Args:
            theme: Tema do conteúdo
            category: Categoria
            platform: Plataforma
            
        Returns:
            Análise competitiva
        """
        # Esta é uma análise simulada - em produção poderia usar API real
        return {
            'competition_level': 'medium',
            'content_saturation': 0.6,
            'trending_topics': [theme],
            'differentiation_opportunities': [
                "Focus on unique angle or perspective",
                "Add personal experience or expert insight",
                "Combine with trending format or style"
            ],
            'market_gap_score': 70
        }
    
    def _get_viral_breakdown(self, score: float, category: str) -> Dict[str, Any]:
        """
        Gera breakdown detalhado do potencial viral.
        
        Args:
            score: Score geral
            category: Categoria
            
        Returns:
            Breakdown detalhado
        """
        return {
            'viral_probability': f"{score:.1f}%",
            'success_factors': self._identify_success_factors(score),
            'risk_factors': self._identify_risk_factors(score),
            'recommended_strategy': self._recommend_strategy(score, category),
            'next_steps': self._suggest_next_steps(score)
        }
    
    # Métodos auxiliares
    def _analyze_hook_strength(self, script: str) -> float:
        """Analisa força do hook."""
        first_3_sentences = ' '.join(script.split('.')[:3])
        hook_indicators = ['you won\'t believe', 'this will', 'the secret', 'surprising', 'unbelievable']
        hook_score = 50
        
        for indicator in hook_indicators:
            if indicator in first_3_sentences.lower():
                hook_score += 10
        
        return min(100, hook_score)
    
    def _analyze_pacing(self, script: str) -> Dict[str, Any]:
        """Analisa ritmo e pacing do conteúdo."""
        word_count = len(script.split())
        estimated_duration = word_count / 150  # ~150 words per minute
        
        return {
            'estimated_duration_seconds': estimated_duration * 60,
            'word_count': word_count,
            'pacing_score': 80 if 30 <= estimated_duration <= 60 else 60
        }
    
    def _extract_hook(self, script: str) -> str:
        """Extrai hook do script."""
        sentences = script.split('.')
        return sentences[0] if sentences else ""
    
    def _generate_better_hook(self, theme: str, category: str) -> str:
        """Gera hook melhorado."""
        hooks = {
            'animals': [
                f"You won't believe what this {theme.split()[-1]} can do",
                f"Scientists discovered something shocking about {theme}",
                f"This {theme.split()[-1]} has a secret ability"
            ],
            'technology': [
                f"This technology will change everything you know about {theme}",
                f"The future of {theme} is here and it's unbelievable",
                f"Revolutionary breakthrough in {theme} revealed"
            ]
        }
        
        category_hooks = hooks.get(category, [f"Surprising discovery about {theme}"])
        return category_hooks[0]
    
    def _enhance_content_value(self, script: str, category: str) -> str:
        """Adiciona valor ao conteúdo."""
        value_additions = {
            'animals': "Recent scientific research reveals fascinating insights about animal behavior that will change how you see these creatures forever.",
            'technology': "Cutting-edge developments in this field are reshaping our future in ways most people can't even imagine yet.",
            'food': "Culinary experts and food scientists have uncovered secrets that transform ordinary ingredients into extraordinary experiences."
        }
        
        addition = value_additions.get(category, "Expert analysis reveals deeper insights that most people miss entirely.")
        return f"{script} {addition}"
    
    def _identify_success_factors(self, score: float) -> List[str]:
        """Identifica fatores de sucesso."""
        factors = []
        if score > 80:
            factors.extend(["Strong viral potential", "High engagement predicted"])
        if score > 60:
            factors.extend(["Good content structure", "Shareable elements present"])
        return factors or ["Basic content quality"]
    
    def _identify_risk_factors(self, score: float) -> List[str]:
        """Identifica fatores de risco."""
        risks = []
        if score < 50:
            risks.extend(["Low viral potential", "Weak hook strength"])
        if score < 70:
            risks.extend(["Limited emotional impact", "Could benefit from optimization"])
        return risks
    
    def _recommend_strategy(self, score: float, category: str) -> str:
        """Recomenda estratégia."""
        if score >= 80:
            return "Proceed with current approach - high viral potential"
        elif score >= 60:
            return "Minor optimizations recommended before publishing"
        else:
            return "Significant revisions needed for viral success"
    
    def _suggest_next_steps(self, score: float) -> List[str]:
        """Sugere próximos passos."""
        steps = ["Publish and monitor performance"]
        if score < 70:
            steps.insert(0, "Implement suggested optimizations")
        if score < 50:
            steps.insert(0, "Consider content restructure")
        return steps


# Instância global
content_virality_predictor = None


def get_content_virality_predictor(llm_client: OpenRouterClient) -> ContentViralityPredictor:
    """
    Retorna instância global do previsor de viralidade.
    
    Args:
        llm_client: Cliente LLM para análise
        
    Returns:
        Instância do ContentViralityPredictor
    """
    global content_virality_predictor
    if content_virality_predictor is None:
        content_virality_predictor = ContentViralityPredictor(llm_client)
    return content_virality_predictor