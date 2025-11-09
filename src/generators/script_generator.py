"""
Gerador de Roteiro - AiShorts v2.0

Módulo principal para geração de roteiros de vídeos curtos usando IA.
Otimizado para TikTok/YouTube Shorts com foco em engajamento e retenção.
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from src.config.settings import config
from src.core.openrouter_client import openrouter_client
from src.generators.theme_generator import GeneratedTheme
from src.utils.exceptions import ScriptGenerationError, ValidationError, ErrorHandler

# Importar modelos unificados
from src.models import GeneratedScript as GeneratedScriptBase, ScriptSection as ScriptSectionBase, ScriptGenerationResult as ScriptGenerationResultBase


# Usar modelos unificados diretamente (herança para compatibilidade)
GeneratedScript = GeneratedScriptBase
ScriptSection = ScriptSectionBase  
ScriptGenerationResult = ScriptGenerationResultBase


class ScriptGenerator:
    """Gerador principal de roteiros para vídeos curtos."""
    
    def __init__(self):
        self.config = config.script_gen if hasattr(config, 'script_gen') else type('ScriptConfig', (), {
            'max_attempts': 3,
            'min_quality_score': 0.7,
            'target_duration': 60
        })()
        
        self.openrouter = openrouter_client
        self.target_duration = self.config.target_duration
        
        # Configurações de qualidade
        self.min_quality_score = self.config.min_quality_score
        self.max_attempts = self.config.max_attempts
        
        # Modo de teste (para validações mais flexíveis)
        self._test_mode = False
        
logger.info(f"ScriptGenerator inicializado - Duração alvo: {self.target_duration}s")
    
    def generate_single_script(self, 
                             theme: GeneratedTheme,
                             custom_requirements: List[str] = None,
                             target_platform: str = "tiktok") -> GeneratedScript:
        """
        Gera um único roteiro de alta qualidade a partir de um tema.
        
        Args:
            theme: Tema para transformar em roteiro
            custom_requirements: Requisitos específicos para o roteiro
            target_platform: Plataforma alvo (tiktok, shorts, reels)
            
        Returns:
            GeneratedScript com roteiro otimizado
        """
        if target_platform not in ["tiktok", "shorts", "reels"]:
            raise ValueError("Plataforma deve ser: tiktok, shorts, ou reels")
        
        try:
            # Criar prompt baseado no tema
            prompt_data = self._create_script_prompt(theme, custom_requirements, target_platform)
            
            # Log do início da geração
logger.info(f"Iniciando geração de roteiro - Tema: {theme.content[:50]}...")
            
            # Gerar roteiro usando OpenRouter
            start_time = time.time()
            
            response = self.openrouter.generate_content(
                prompt=prompt_data["user_prompt"],
                system_message=prompt_data["system_message"],
                max_tokens=config.openrouter.max_tokens_script if hasattr(config.openrouter, 'max_tokens_script') else 1000,
                temperature=0.7  # Equilibrio entre criatividade e estrutura
            )
            
            generation_time = time.time() - start_time
            
            # Processar e estruturar roteiro
            script_sections = self._parse_script_response(response.content, theme)
            
            # Validar roteiro
            self._validate_script_sections(script_sections, theme)
            
            # Calcular métricas de qualidade
            quality_metrics = self._calculate_script_quality(script_sections, theme)
            
            # Calcular duração total
            total_duration = sum(section.duration_seconds for section in script_sections)
            
            # Criar roteiro gerado
            script = GeneratedScript(
                title=self._generate_title(theme),
                theme=theme,
                sections=script_sections,
                total_duration=total_duration,
                quality_score=quality_metrics["overall_quality"],
                engagement_score=quality_metrics["engagement_score"],
                retention_score=quality_metrics["retention_score"],
                response_time=generation_time,
                timestamp=datetime.now(),
                usage=response.usage,
                metrics=quality_metrics
            )
            
            # Log do resultado
logger.info(
                f"Roteiro gerado - Duração: {total_duration:.1f}s, "
                f"Qualidade: {quality_metrics['overall_quality']:.2f}, "
                f"Engajamento: {quality_metrics['engagement_score']:.2f}, "
                f"Tempo: {generation_time:.2f}s"
            )
            
            return script
        
        except Exception as e:
logger.error(f"Erro na geração de roteiro - Tema: {theme.content[:50]}..., Erro: {e}")
            raise ScriptGenerationError(f"Falha na geração: {str(e)}", theme_content=theme.content)
    
    def generate_multiple_scripts(self, 
                                themes: List[GeneratedTheme],
                                count: int = 3,
                                min_quality_score: float = None) -> ScriptGenerationResult:
        """
        Gera múltiplos roteiros e seleciona os melhores.
        
        Args:
            themes: Temas para transformar em roteiros
            count: Quantidade de roteiros a gerar
            min_quality_score: Score mínimo de qualidade
            
        Returns:
            ScriptGenerationResult com melhores roteiros
        """
        if min_quality_score is None:
            min_quality_score = self.min_quality_score
        
        start_time = time.time()
        scripts = []
        generation_stats = {
            "total_attempts": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "themes_used": [],
            "quality_scores": [],
            "engagement_scores": [],
            "retention_scores": [],
            "response_times": []
        }
        
logger.info(f"Iniciando geração de {count} roteiros de {len(themes)} temas")
        
        for attempt in range(min(count * 2, len(themes) * 2)):
            if len(scripts) >= count:
                break
            
            generation_stats["total_attempts"] += 1
            
            # Escolher tema (round-robin ou aleatório)
            theme = themes[attempt % len(themes)]
            generation_stats["themes_used"].append(theme.content[:50] + "...")
            
            try:
                # Gerar roteiro
                script = self.generate_single_script(theme)
                
                # Verificar qualidade mínima
                if script.quality_score >= min_quality_score:
                    scripts.append(script)
                    generation_stats["successful_generations"] += 1
                    generation_stats["quality_scores"].append(script.quality_score)
                    generation_stats["engagement_scores"].append(script.engagement_score)
                    generation_stats["retention_scores"].append(script.retention_score)
                    generation_stats["response_times"].append(script.response_time)
                    
logger.info(f"Roteiro aceito - Score: {script.quality_score:.2f}, Duração: {script.total_duration:.1f}s")
                else:
logger.warning(f"Roteiro rejeitado - Score baixo: {script.quality_score:.2f}")
                    generation_stats["failed_generations"] += 1
                
            except Exception as e:
logger.error(f"Falha na tentativa {attempt + 1}: {e}")
                generation_stats["failed_generations"] += 1
        
        total_time = time.time() - start_time
        
        # Encontrar melhor roteiro
        best_script = None
        if scripts:
            # Melhor roteiro é o que tem maior score combinado (qualidade + engajamento + retenção)
            best_script = max(scripts, key=lambda s: s.quality_score * 0.4 + s.engagement_score * 0.3 + s.retention_score * 0.3)
        
        # Finalizar estatísticas
        if generation_stats["quality_scores"]:
            generation_stats["avg_quality_score"] = sum(generation_stats["quality_scores"]) / len(generation_stats["quality_scores"])
            generation_stats["avg_engagement_score"] = sum(generation_stats["engagement_scores"]) / len(generation_stats["engagement_scores"])
            generation_stats["avg_retention_score"] = sum(generation_stats["retention_scores"]) / len(generation_stats["retention_scores"])
        
        if generation_stats["response_times"]:
            generation_stats["avg_response_time"] = sum(generation_stats["response_times"]) / len(generation_stats["response_times"])
        
        result = ScriptGenerationResult(
            scripts=scripts,
            best_script=best_script,
            total_time=total_time,
            generation_stats=generation_stats
        )
        
logger.info(
            f"Geração concluída - {len(scripts)}/{count} roteiros aceitos, "
            f"Melhor score: {(best_script.quality_score if best_script else 0.0):.2f}, "
            f"Tempo total: {total_time:.2f}s"
        )
        
        return result
    
    def _create_script_prompt(self, 
                             theme: GeneratedTheme, 
                             custom_requirements: List[str],
                             target_platform: str) -> Dict[str, str]:
        """
        Cria prompt específico para geração de roteiro.
        
        Args:
            theme: Tema base
            custom_requirements: Requisitos adicionais
            target_platform: Plataforma alvo
            
        Returns:
            Dicionário com system_message e user_prompt
        """
        
        # System message baseado na plataforma
        platform_instructions = {
            "tiktok": "TikTok: lean into fast pacing, bold hooks, and conversational slang.",
            "shorts": "YouTube Shorts: balance storytelling with clarity and high retention cues.",
            "reels": "Instagram Reels: emphasize visual moments, aesthetic beats, and shareable lines."
        }
        
        base_system = f"""You are a senior short-form scriptwriter who crafts viral 60-second videos in English.

Your superpowers:
- Write hooks that stop the scroll within three seconds
- Turn curiosity-packed facts into binge-worthy micro stories
- Structure every beat for maximum retention and rewatchability
- Adapt tone, pacing, and wording for {target_platform}

SUCCESS PRINCIPLES:
1. Magnetic Hook (3-5s): deliver a shocking fact or question immediately.
2. Engaging Body (~50s): explain with clarity, analogies, and dynamic pacing.
3. Strategic Close (5-10s): wrap up with a punchy summary and subtle CTA.
4. Natural Voice: sound like a passionate friend sharing the coolest fact.
5. Dynamic Rhythm: vary sentence length, energy, and pauses.

MANDATORY STRUCTURE:
- HOOK (3-5 seconds): Start with a jaw-dropping fact, bold claim, or question. Keep it under 12 words.
- BODY (~50 seconds): 6 sentences, 140-160 words total. Use imagery, comparisons, or mini-scenes to keep attention high and maintain momentum.
- CONCLUSION (5-10 seconds): 2 sentences, at least 25 words total, delivering payoff + subtle CTA.
- ESTIMATED_DURATION: A single line formatted exactly as ESTIMATED_DURATION: <seconds>

RESPONSE FORMAT (use exactly this layout, no extra markdown or backticks):
HOOK: [8-12 words]
BODY: [6 sentences, 140-160 words total]
CONCLUSION: [2 sentences, ≥25 words with CTA]
ESTIMATED_DURATION: [seconds]

EXAMPLES (copy the structure and tone, no markdown fences):
HOOK: This fish defeats sharks with instant, suffocating slime.
BODY: Meet the hagfish—the ocean’s weirdest survivor. When threatened, it ejects threads of mucus that expand like foam, clogging a predator’s gills in seconds. Scientists measured enough slime to fill a bathtub from one fish, turning an attack into a choking retreat. Divers filmed this in Alaska, proving even sharks back off the “slime torpedo.”
CONCLUSION: Nature’s grossest defense might be the smartest. Would you touch it? Tag someone who would!
ESTIMATED_DURATION: 58

HOOK: This tree whispers secrets through an underground internet.
BODY: Forests aren’t silent—fungi link roots into a “wood-wide web,” letting trees trade nutrients and send distress signals. A shaded sapling can literally receive carbon “transfers” from older trees, keeping it alive until it reaches sunlight—an ecosystem built on hidden generosity. Researchers tracked this network in Canada, proving forests behave like families. Imagine the tallest tree feeding a sapling through hidden fibers while the forest “hears” chainsaws miles away. That’s not myth—it’s chemistry and teamwork.
CONCLUSION: Still think trees don’t talk? The forest says otherwise—share if that blew your mind. Tag someone who needs proof that nature is running a covert comms network under our feet.
ESTIMATED_DURATION: 60

{platform_instructions[target_platform]}

Write the full script in English using the structure above. Do NOT include any extra commentary, explanations, or markdown fences."""
        
        user_prompt = f"""THEME: "{theme.content}"
CATEGORY: {theme.category.value.upper()}
THEME QUALITY: {theme.quality_score:.2f}/1.0

SPECIFIC INSTRUCTIONS:
- Let the core curiosity drive the narrative.
- Match the tone, pacing, and slang to {target_platform}.
- Keep every statement factual and sourceable.
- Make the story feel cinematic without losing credibility.

{'- ' + '\n- '.join(custom_requirements) if custom_requirements else ''}

Now craft the script:"""
        
        return {
            "system_message": base_system,
            "user_prompt": user_prompt
        }
    
    def _parse_script_response(self, response: str, theme: GeneratedTheme) -> List[ScriptSection]:
        """
        Parseia a resposta do modelo em seções estruturadas.
        
        Args:
            response: Resposta do modelo
            theme: Tema original
            
        Returns:
            Lista de seções do roteiro
        """
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        sections = []
        current_section = None
        current_content = []
        
        # Debug: Log da resposta para análise
logger.debug(f"Parseando resposta: {response[:200]}...")
        
        for line in lines:
            line_upper = line.upper()
            
            if line_upper.startswith('HOOK:'):
                if current_section:
                    current_section.content = ' '.join(current_content)
                    sections.append(current_section)
                current_section = ScriptSection(
                    name="hook",
                    content="",
                    duration_seconds=0,
                    purpose="Grab attention instantly",
                    key_elements=[]
                )
                current_content = [line[5:].strip()]  # Pega conteúdo após "HOOK:"
            
            elif line_upper.startswith('DESENVOLVIMENTO:') or line_upper.startswith('BODY:'):
                if current_section:
                    current_section.content = ' '.join(current_content)
                    sections.append(current_section)
                current_section = ScriptSection(
                    name="development",
                    content="",
                    duration_seconds=0,
                    purpose="Explain and sustain engagement",
                    key_elements=[]
                )
                content_start = line.split(':', 1)[1].strip()
                current_content = [content_start]
            
            elif line_upper.startswith('CONCLUSÃO:') or line_upper.startswith('CONCLUSION:') or line_upper.startswith('CTA:'):
                if current_section:
                    current_section.content = ' '.join(current_content)
                    sections.append(current_section)
                current_section = ScriptSection(
                    name="conclusion",
                    content="",
                    duration_seconds=0,
                    purpose="Deliver payoff and invite engagement",
                    key_elements=[]
                )
                if ':' in line:
                    content_start = line.split(':', 1)[1].strip()
                else:
                    start_idx = 10 if line_upper.startswith('CONCLUSÃO:') else 4
                    content_start = line[start_idx:].strip()
                current_content = [content_start]
            
            elif line_upper.startswith('DURAÇÃO'):
                # Calcular duração e fechar seção atual
                duration_str = line.split(':')[-1].strip()
                try:
                    duration = float(duration_str.split()[0])
                except:
                    duration = self._estimate_section_duration(current_content)
                
                if current_section:
                    current_section.content = ' '.join(current_content)
                    current_section.duration_seconds = duration
                    sections.append(current_section)
                break
            
            else:
                # Se não é um header, adiciona ao conteúdo atual
                if current_section:
                    current_content.append(line)
        
        # Se não encontrou a estrutura esperada, usar abordagem simples
        if not sections:
logger.warning("Estrutura de roteiro não encontrada, usando parse simples")
            sections = self._simple_parse_script(response, theme)
        elif current_section and current_content:
            # Fechar última seção se ainda não foi fechada
            current_section.content = ' '.join(current_content)
            sections.append(current_section)
        
        # Garantir que cada seção tenha duração estimada (>0)
        for s in sections:
            if s.duration_seconds is None or s.duration_seconds <= 0:
                s.duration_seconds = self._estimate_section_duration([s.content])
        
        return sections
    
    def _simple_parse_script(self, response: str, theme: GeneratedTheme) -> List[ScriptSection]:
        """Parse simples quando a estrutura não é detectada."""
        
        # Dividir em partes lógicas (aproximação)
        words = response.split()
        total_words = len(words)
        
        if total_words < 10:
            # Very short response; craft a minimal English structure
            hook_content = f"Did you know that {theme.content}?"
            development_content = f"This {theme.category.value} fact is wilder than it sounds."  # noqa: E501
            conclusion_content = "Follow for more mind-bending curiosities!"
        else:
            # Dividir texto em 3 partes
            third = total_words // 3
            hook_content = ' '.join(words[:third//2])
            development_content = ' '.join(words[third//2:third + third//2])
            conclusion_content = ' '.join(words[third + third//2:])
        
        return [
            ScriptSection(
                name="hook",
                content=hook_content,
                duration_seconds=4.0,
                purpose="Grab attention instantly",
                key_elements=["curiosity", "surprise"]
            ),
            ScriptSection(
                name="development",
                content=development_content,
                duration_seconds=45.0,
                purpose="Explain and keep viewers engaged",
                key_elements=["explanation", "detail", "wonder"]
            ),
            ScriptSection(
                name="conclusion",
                content=conclusion_content,
                duration_seconds=8.0,
                purpose="Deliver payoff and invite engagement",
                key_elements=["summary", "engagement"]
            )
        ]
    
    def _estimate_section_duration(self, content_lines: List[str]) -> float:
        """Estima duração de uma seção baseada no conteúdo."""
        total_words = len(' '.join(content_lines).split())
        
        # Estimar 150-200 palavras por minuto = 2.5-3.3 palavras por segundo
        words_per_second = 2.8
        return min(total_words / words_per_second, 60.0)  # Máximo 60 segundos
    
    def _validate_script_sections(self, sections: List[ScriptSection], theme: GeneratedTheme) -> None:
        """Valida se as seções do roteiro estão corretas."""
        
logger.debug(f"Validando roteiro com {len(sections)} seções")
        
        if len(sections) < 2:
            raise ValidationError("Roteiro deve ter pelo menos hook e desenvolvimento", field="sections", value=len(sections))
        
        # Verificar se tem hook
        hook_section = next((s for s in sections if s.name == "hook"), None)
        if not hook_section:
            raise ValidationError("Roteiro deve ter seção HOOK", field="hook", value="missing")
        
        # Verificar duração total
        total_duration = sum(section.duration_seconds for section in sections)
        if total_duration > 90:  # Muito longo
logger.warning(f"Roteiro muito longo: {total_duration:.1f}s, pode ser truncado")
        elif total_duration < 30:  # Muito curto
logger.warning(f"Roteiro muito curto: {total_duration:.1f}s, pode precisar de mais conteúdo")
        
        # Verificar conteúdo básico
        for section in sections:
            if len(section.content) < 5:
logger.warning(f"Seção {section.name} muito curta: {len(section.content)} chars")
                # Em ambiente de teste, continuar em vez de falhar
                if hasattr(self, '_test_mode') and self._test_mode:
                    continue
                raise ValidationError(f"Seção {section.name} muito curta", field=section.name, value=len(section.content))
        
logger.debug(f"Validação OK - Duração total: {total_duration:.1f}s")
    
    def _calculate_script_quality(self, sections: List[ScriptSection], theme: GeneratedTheme) -> Dict[str, float]:
        """Calcula métricas de qualidade do roteiro."""
        
        # Métricas básicas
        total_duration = sum(section.duration_seconds for section in sections)
        total_words = len(self.get_script_text_from_sections(sections).split())
        
        # Score de qualidade estrutural
        structure_score = self._evaluate_structure(sections)
        
        # Score de engajamento (baseado no hook)
        engagement_score = self._evaluate_engagement(sections)
        
        # Score de retenção (baseado na duração e fluxo)
        retention_score = self._evaluate_retention(sections, total_duration)
        
        # Score geral
        overall_quality = (structure_score * 0.4 + engagement_score * 0.3 + retention_score * 0.3)
        
        return {
            "structure_score": structure_score,
            "engagement_score": engagement_score,
            "retention_score": retention_score,
            "overall_quality": overall_quality,
            "total_duration": total_duration,
            "total_words": total_words,
            "theme_quality": theme.quality_score
        }
    
    def _evaluate_structure(self, sections: List[ScriptSection]) -> float:
        """Avalia a qualidade estrutural do roteiro."""
        score = 0.0
        
        # Tem hook?
        hook_section = next((s for s in sections if s.name == "hook"), None)
        if hook_section:
            score += 0.3
        
        # Tem desenvolvimento?
        development_section = next((s for s in sections if s.name == "development"), None)
        if development_section and len(development_section.content) > 20:
            score += 0.4
        
        # Tem conclusão/CTA?
        conclusion_section = next((s for s in sections if s.name == "conclusion"), None)
        if conclusion_section:
            score += 0.3
        
        return min(score, 1.0)
    
    def _evaluate_engagement(self, sections: List[ScriptSection]) -> float:
        """Avalia potencial de engajamento baseado no hook."""
        hook_section = next((s for s in sections if s.name == "hook"), None)
        if not hook_section:
            return 0.0
        
        hook_content = hook_section.content.lower()
        score = 0.5  # Base score
        
        # Palavras que aumentam engajamento
        engagement_words = ['sabia', 'você', 'que', '?', 'inacreditável', 'surpreendente', 'louco']
        for word in engagement_words:
            if word in hook_content:
                score += 0.1
        
        # Questões prendem mais atenção
        if '?' in hook_content:
            score += 0.2
        
        # Frases diretas funcionam melhor
        if len(hook_content.split()) <= 15:
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_retention(self, sections: List[ScriptSection], total_duration: float) -> float:
        """Avalia potencial de retenção baseado na duração e estrutura."""
        score = 0.5  # Base score
        
        # Duração ideal: 45-75 segundos
        if 45 <= total_duration <= 75:
            score += 0.3
        elif 30 <= total_duration <= 90:
            score += 0.1
        
        # Desenvolvimento deve ser a maior parte
        development_section = next((s for s in sections if s.name == "development"), None)
        if development_section and total_duration > 0:
            development_ratio = development_section.duration_seconds / total_duration
            if 0.6 <= development_ratio <= 0.8:
                score += 0.2
        
        return min(score, 1.0)
    
    def _generate_title(self, theme: GeneratedTheme) -> str:
        """Gera título atrativo para o roteiro baseado no tema."""
        theme_words = theme.content.split()[:4]  # Primeiras 4 palavras
        return f"Curiosidade: {' '.join(theme_words)}..."
    
    def get_script_text_from_sections(self, sections: List[ScriptSection]) -> str:
        """Retorna texto completo das seções."""
        return " ".join([section.content for section in sections])
    
    def save_script_result(self, result: ScriptGenerationResult, filename: str = None) -> Path:
        """Salva resultado da geração em arquivo."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"script_generation_{timestamp}.json"
        
        filepath = config.storage.output_dir / filename
        result.save_to_file(filepath)
        
logger.info(f"Resultado salvo em: {filepath}")
        return filepath
    
    def analyze_scripts(self, scripts: List[GeneratedScript]) -> Dict[str, Any]:
        """Analisa uma lista de roteiros gerados."""
        if not scripts:
            return {"error": "Nenhum roteiro para analisar"}
        
        analysis = {
            "total_scripts": len(scripts),
            "duration_stats": {},
            "quality_stats": {},
            "engagement_stats": {},
            "retention_stats": {},
            "best_scripts": [],
            "patterns": []
        }
        
        # Estatísticas de duração
        durations = [script.total_duration for script in scripts]
        analysis["duration_stats"] = {
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations)
        }
        
        # Estatísticas de qualidade
        quality_scores = [script.quality_score for script in scripts]
        analysis["quality_stats"] = {
            "avg_quality": sum(quality_scores) / len(quality_scores),
            "min_quality": min(quality_scores),
            "max_quality": max(quality_scores)
        }
        
        # Estatísticas de engajamento
        engagement_scores = [script.engagement_score for script in scripts]
        analysis["engagement_stats"] = {
            "avg_engagement": sum(engagement_scores) / len(engagement_scores),
            "min_engagement": min(engagement_scores),
            "max_engagement": max(engagement_scores)
        }
        
        # Estatísticas de retenção
        retention_scores = [script.retention_score for script in scripts]
        analysis["retention_stats"] = {
            "avg_retention": sum(retention_scores) / len(retention_scores),
            "min_retention": min(retention_scores),
            "max_retention": max(retention_scores)
        }
        
        # Melhores roteiros
        sorted_scripts = sorted(scripts, key=lambda s: s.quality_score, reverse=True)
        analysis["best_scripts"] = [
            {
                "title": script.title,
                "quality_score": script.quality_score,
                "engagement_score": script.engagement_score,
                "retention_score": script.retention_score,
                "duration": script.total_duration,
                "theme": script.theme.content[:50] + "..."
            }
            for script in sorted_scripts[:5]
        ]
        
        return analysis


# Instância global do gerador
script_generator = ScriptGenerator()

if __name__ == "__main__":
    # Teste do gerador de roteiro
print("=== Teste do Gerador de Roteiro ===")
    
    try:
        # Importar e usar o gerador de temas
        from src.generators.theme_generator import theme_generator, ThemeCategory
        
        # Primeiro, gerar um tema
print("1. Gerando tema base...")
        theme = theme_generator.generate_single_theme(ThemeCategory.SCIENCE)
print(f" Tema: {theme.content}")
        
        # Depois, gerar roteiro
print("\n2. Gerando roteiro...")
        script = script_generator.generate_single_script(theme)
print(f" Título: {script.title}")
print(f"⏱ Duração: {script.total_duration:.1f}s")
print(f" Qualidade: {script.quality_score:.2f}")
        
        # Mostrar estrutura
print("\n3. Estrutura do roteiro:")
        for section in script.sections:
print(f"   {section.name.upper()}: {section.content[:50]}... ({section.duration_seconds:.1f}s)")
        
        # Teste de geração múltipla
print("\n4. Teste de geração múltipla:")
        themes = [theme_generator.generate_single_theme(ThemeCategory.NATURE) for _ in range(2)]
        result = script_generator.generate_multiple_scripts(themes, count=2)
print(f" {len(result.scripts)} roteiros gerados")
        
    except Exception as e:
print(f" Erro no teste: {e}")
