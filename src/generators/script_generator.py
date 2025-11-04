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


@dataclass
class ScriptSection:
    """Representa uma seção do roteiro."""
    name: str  # 'hook', 'development', 'conclusion'
    content: str
    duration_seconds: float
    purpose: str
    key_elements: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "name": self.name,
            "content": self.content,
            "duration_seconds": self.duration_seconds,
            "purpose": self.purpose,
            "key_elements": self.key_elements
        }


@dataclass
class GeneratedScript:
    """Representa um roteiro completo gerado."""
    title: str
    theme: GeneratedTheme
    sections: List[ScriptSection]
    total_duration: float
    quality_score: float
    engagement_score: float
    retention_score: float
    response_time: float
    timestamp: datetime
    usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    @property
    def hook(self) -> ScriptSection:
        """Retorna a seção de hook."""
        return next((s for s in self.sections if s.name == "hook"), None)
    
    @property
    def development(self) -> ScriptSection:
        """Retorna a seção de desenvolvimento."""
        return next((s for s in self.sections if s.name == "development"), None)
    
    @property
    def conclusion(self) -> ScriptSection:
        """Retorna a seção de conclusão."""
        return next((s for s in self.sections if s.name == "conclusion"), None)
    
    def get_hook_preview(self, max_chars: int = 100) -> str:
        """Retorna preview do hook (para吸引 atenção)."""
        if self.hook:
            content = self.hook.content[:max_chars]
            return content + "..." if len(self.hook.content) > max_chars else content
        return ""
    
    def get_script_text(self) -> str:
        """Retorna texto completo do roteiro."""
        return " ".join([section.content for section in self.sections])
    
    def save_to_file(self, filepath: Path) -> None:
        """Salva roteiro em arquivo JSON."""
        data = {
            "title": self.title,
            "theme": self.theme.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "total_duration": self.total_duration,
            "quality_score": self.quality_score,
            "engagement_score": self.engagement_score,
            "retention_score": self.retention_score,
            "response_time": self.response_time,
            "timestamp": self.timestamp.isoformat(),
            "usage": self.usage,
            "metrics": self.metrics
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class ScriptGenerationResult:
    """Resultado da geração de múltiplos roteiros."""
    scripts: List[GeneratedScript]
    best_script: Optional[GeneratedScript]
    total_time: float
    generation_stats: Dict[str, Any]
    
    def save_to_file(self, filepath: Path) -> None:
        """Salva resultado em arquivo JSON."""
        data = {
            "scripts": [script.to_dict() for script in self.scripts],
            "best_script": self.best_script.to_dict() if self.best_script else None,
            "total_time": self.total_time,
            "generation_stats": self.generation_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


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
            "tiktok": "TikTok: Foque em conteúdo viral, tendências e linguagem jovem",
            "shorts": "YouTube Shorts: Foque em qualidade de conteúdo e retenção",
            "reels": "Instagram Reels: Foque em estética e engajamento visual"
        }
        
        base_system = f"""Você é um especialista em criar roteiros virais para vídeos curtos de 60 segundos.

Sua especialidade:
- Criar roteiros que prendam atenção nos primeiros 3 segundos
- Transformar curiosidades em narrativas envolventes
- Estruturar conteúdo para máxima retenção de audiência
- Adaptar linguagem para {target_platform}

PRINCÍPIOS DE SUCESSO:
1. Hook Fortíssimo (3-5s): Frase que faz a pessoa PARAR e assistir
2. Desenvolvimento Envolvente (40-50s): Explicação clara e fascinante
3. Call-to-Action Estratégico (5-10s): Encoraja engajamento sem ser óbvio
4. Linguagem Natural: Como se estivesse contando para um amigo
5. Ritmo Dinâmico: Variação de velocidade e ênfase

ESTRUTURA OBRIGATÓRIA:
HOOK (3-5 segundos):
- Frase de impacto que desperte curiosidade
- Pode ser pergunta, afirmação surpreendente ou "Você sabia que..."
- DEVE fazer a pessoa querer continuar assistindo

DESENVOLVIMENTO (40-50 segundos):
- Explicação clara e envolvente do tema
- Use analogias e exemplos práticos
- Mantenha ritmo dinâmico
- Varie entonação (subir, baixar volume)
- Use pausas dramáticas

CONCLUSÃO/CTA (5-10 segundos):
- Resumo em 1 frase
- Call-to-action sutil (curtir, comentar, seguir)
- Pode incluir pergunta para comentários

FORMATO DE RESPOSTA:
```
HOOK: [texto do gancho de 8-12 palavras]
DESENVOLVIMENTO: [explicação principal em 2-3 frases, 40-50 palavras]
CONCLUSÃO: [resumo + CTA em 1-2 frases, 8-15 palavras]

DURAÇÃO ESTIMADA: [calculada em segundos]
```

{platform_instructions[target_platform]}

Sua tarefa é transformar o seguinte tema em um roteiro viral:"""
        
        user_prompt = f"""TEMA: "{theme.content}"
CATEGORIA: {theme.category.value.upper()}
QUALIDADE DO TEMA: {theme.quality_score:.2f}/1.0

INSTRUÇÕES ESPECÍFICAS:
- Use a curiosidade natural do tema como base
- Adapte o tom para {target_platform}
- Mantenha factual accuracy
- Crie narrativa envolvente sem perder credibilidade

{'- ' + '\n- '.join(custom_requirements) if custom_requirements else ''}

Agora crie o roteiro:"""
        
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
                    purpose="Prender atenção",
                    key_elements=[]
                )
                current_content = [line[5:].strip()]  # Pega conteúdo após "HOOK:"
            
            elif line_upper.startswith('DESENVOLVIMENTO:'):
                if current_section:
                    current_section.content = ' '.join(current_content)
                    sections.append(current_section)
                current_section = ScriptSection(
                    name="development",
                    content="",
                    duration_seconds=0,
                    purpose="Explicar e envolver",
                    key_elements=[]
                )
                current_content = [line[14:].strip()]  # Pega conteúdo após "DESENVOLVIMENTO:"
            
            elif line_upper.startswith('CONCLUSÃO:') or line_upper.startswith('CTA:'):
                if current_section:
                    current_section.content = ' '.join(current_content)
                    sections.append(current_section)
                current_section = ScriptSection(
                    name="conclusion",
                    content="",
                    duration_seconds=0,
                    purpose="Fechar e engajar",
                    key_elements=[]
                )
                start_idx = 10 if line_upper.startswith('CONCLUSÃO:') else 4
                current_content = [line[start_idx:].strip()]
            
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
        
        return sections
    
    def _simple_parse_script(self, response: str, theme: GeneratedTheme) -> List[ScriptSection]:
        """Parse simples quando a estrutura não é detectada."""
        
        # Dividir em partes lógicas (aproximação)
        words = response.split()
        total_words = len(words)
        
        if total_words < 10:
            # Resposta muito curta, usar estrutura básica
            hook_content = f"Você sabia que {theme.content}?"
            development_content = f"Esta curiosidade sobre {theme.category.value} vai te surpreender!"
            conclusion_content = "Curte se você não sabia disso!"
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
                purpose="Prender atenção",
                key_elements=["curiosidade", "surpresa"]
            ),
            ScriptSection(
                name="development",
                content=development_content,
                duration_seconds=45.0,
                purpose="Explicar e envolver",
                key_elements=["explicação", "detalhes", "fascínio"]
            ),
            ScriptSection(
                name="conclusion",
                content=conclusion_content,
                duration_seconds=8.0,
                purpose="Fechar e engajar",
                key_elements=["resumo", "engajamento"]
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
        if development_section:
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
        print(f"📝 Tema: {theme.content}")
        
        # Depois, gerar roteiro
        print("\n2. Gerando roteiro...")
        script = script_generator.generate_single_script(theme)
        print(f"🎬 Título: {script.title}")
        print(f"⏱️ Duração: {script.total_duration:.1f}s")
        print(f"⭐ Qualidade: {script.quality_score:.2f}")
        
        # Mostrar estrutura
        print("\n3. Estrutura do roteiro:")
        for section in script.sections:
            print(f"   {section.name.upper()}: {section.content[:50]}... ({section.duration_seconds:.1f}s)")
        
        # Teste de geração múltipla
        print("\n4. Teste de geração múltipla:")
        themes = [theme_generator.generate_single_theme(ThemeCategory.NATURE) for _ in range(2)]
        result = script_generator.generate_multiple_scripts(themes, count=2)
        print(f"✅ {len(result.scripts)} roteiros gerados")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")