"""
Script Validator - AiShorts v2.0

Sistema avançado de validação de roteiros com:
- Validação de estrutura e formato
- Checagem de qualidade de conteúdo
- Verificação de requisitos por plataforma
- Sistema de pontuação e feedback automático
- Sugestões de melhorias
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from loguru import logger

from src.config.settings import config
from src.generators.script_generator import GeneratedScript, ScriptSection
from src.utils.exceptions import ValidationError


class PlatformType(Enum):
    """Plataformas suportadas."""
    TIKTOK = "tiktok"
    SHORTS = "shorts"
    REELS = "reels"


class ValidationSeverity(Enum):
    """Níveis de severidade das validações."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class QualityLevel(Enum):
    """Níveis de qualidade."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class ValidationIssue:
    """Representa um problema encontrado na validação."""
    code: str
    message: str
    severity: ValidationSeverity
    section: Optional[str] = None
    field: Optional[str] = None
    suggestion: Optional[str] = None
    position: Optional[int] = None  # Posição no texto
    details: Optional[Dict[str, Any]] = None


@dataclass
class QualityMetrics:
    """Métricas de qualidade do roteiro."""
    clarity_score: float = 0.0
    engagement_score: float = 0.0
    retention_score: float = 0.0
    clarity_issues: List[ValidationIssue] = field(default_factory=list)
    engagement_issues: List[ValidationIssue] = field(default_factory=list)
    retention_issues: List[ValidationIssue] = field(default_factory=list)


@dataclass
class PlatformRequirements:
    """Requisitos específicos por plataforma."""
    max_duration: int  # em segundos
    min_duration: int
    max_characters: int
    min_characters: int
    hook_duration_percent: float  # Hook deve representar X% do total
    development_duration_percent: float
    conclusion_duration_percent: float
    banned_words: Set[str] = field(default_factory=set)
    required_engagement_phrases: Set[str] = field(default_factory=set)
    recommended_hashtags: Set[str] = field(default_factory=set)


@dataclass
class ValidationResult:
    """Resultado da validação de uma seção."""
    section_name: str
    is_valid: bool
    score: float
    issues: List[ValidationIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Relatório completo de validação do roteiro."""
    script: GeneratedScript
    platform: PlatformType
    overall_score: float
    quality_level: QualityLevel
    is_approved: bool
    structure_validation: ValidationResult
    content_validation: ValidationResult
    platform_validation: ValidationResult
    quality_metrics: QualityMetrics
    all_issues: List[ValidationIssue] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Retorna issues por severidade."""
        return [issue for issue in self.all_issues if issue.severity == severity]
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Retorna apenas problemas críticos."""
        return self.get_issues_by_severity(ValidationSeverity.ERROR)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo da validação."""
        return {
            "platform": self.platform.value,
            "overall_score": round(self.overall_score, 3),
            "quality_level": self.quality_level.value,
            "is_approved": self.is_approved,
            "total_issues": len(self.all_issues),
            "critical_issues": len(self.get_critical_issues()),
            "total_suggestions": len(self.suggestions),
            "structure_score": self.structure_validation.score,
            "content_score": self.content_validation.score,
            "platform_score": self.platform_validation.score
        }


class ScriptValidationError(Exception):
    """Exceção específica para erros de validação de roteiro."""
    pass


class ScriptValidator:
    """Validador principal para roteiros."""
    
    # Requisitos por plataforma
    PLATFORM_REQUIREMENTS = {
        PlatformType.TIKTOK: PlatformRequirements(
            max_duration=60,
            min_duration=15,
            max_characters=2200,
            min_characters=150,
            hook_duration_percent=0.15,  # 15%
            development_duration_percent=0.70,  # 70%
            conclusion_duration_percent=0.15,  # 15%
            banned_words={"spam", "fake", "false", "fraud"},
            required_engagement_phrases={"Você sabia que", "Incrível", "Vamos descobrir", "Surpreendente"},
            recommended_hashtags={"#curiosidade", "#fatos", "#interessante"}
        ),
        PlatformType.SHORTS: PlatformRequirements(
            max_duration=60,
            min_duration=15,
            max_characters=5000,
            min_characters=200,
            hook_duration_percent=0.20,  # 20%
            development_duration_percent=0.65,  # 65%
            conclusion_duration_percent=0.15,  # 15%
            banned_words={"spam", "propaganda", "venda"},
            required_engagement_phrases={"Você sabia que", "Vamos explorar", "Descubra", "Incrível"},
            recommended_hashtags={"#shorts", "#curiosidades", "#fatos"}
        ),
        PlatformType.REELS: PlatformRequirements(
            max_duration=90,
            min_duration=15,
            max_characters=2200,
            min_characters=150,
            hook_duration_percent=0.20,  # 20%
            development_duration_percent=0.65,  # 65%
            conclusion_duration_percent=0.15,  # 15%
            banned_words={"spam", "promoção", "desconto"},
            required_engagement_phrases={"Você não vai acreditar", "Incrível", "Espetacular", "Surpreendente"},
            recommended_hashtags={"#reels", "#viral", "#interessante"}
        )
    }
    
    # Padrões para análise de conteúdo
    ENGAGEMENT_PATTERNS = {
        "questions": [r"\?", r"\b(você|vocês|we)\b.*\?"],
        "emotional": [r"incrível",r"fantástico",r"surpreendente",r"espetacular",r"extraordinário"],
        "storytelling": [r"uma vez",r"há muito tempo",r"imagina só",r"se você"],
        "facts": [r"\d+%?", r"estudos mostram",r"pesquisadores",r"cientistas"]
    }
    
    RETENTION_PATTERNS = {
        "cliffhangers": [r"mas espera",r"você não vai acreditar",r"o próximo",r"e então"],
        "structure": [r"primeiro",r"segundo",r"finalmente",r"por último"],
        "anticipation": [r"mais adiante",r"continue assistindo",r"o resultado vai"]
    }

    def __init__(self):
        """Inicializa o validador."""
        self.platform_requirements = self.PLATFORM_REQUIREMENTS
        logger.info("ScriptValidator inicializado com sucesso")

    def validate_script(self, script: GeneratedScript, platform: PlatformType = PlatformType.TIKTOK) -> ValidationReport:
        """
        Valida um roteiro completo.
        
        Args:
            script: Roteiro para validar
            platform: Plataforma alvo
            
        Returns:
            Relatório completo de validação
        """
        logger.info(f"Iniciando validação do roteiro '{script.title}' para {platform.value}")
        
        start_time = datetime.now()
        
        # Validações específicas
        structure_result = self._validate_structure(script)
        content_result = self._validate_content(script)
        platform_result = self._validate_platform_requirements(script, platform)
        quality_metrics = self._analyze_quality_metrics(script)
        
        # Coleta todos os issues
        all_issues = []
        all_issues.extend(structure_result.issues)
        all_issues.extend(content_result.issues)
        all_issues.extend(platform_result.issues)
        
        # Calcula score geral
        overall_score = self._calculate_overall_score(
            structure_result, content_result, platform_result, quality_metrics
        )
        
        # Determina nível de qualidade
        quality_level = self._determine_quality_level(overall_score)
        
        # Verifica se foi aprovado
        is_approved = self._check_approval_criteria(all_issues, overall_score)
        
        # Gera sugestões
        suggestions = self._generate_suggestions(all_issues, structure_result, content_result, platform_result)
        
        report = ValidationReport(
            script=script,
            platform=platform,
            overall_score=overall_score,
            quality_level=quality_level,
            is_approved=is_approved,
            structure_validation=structure_result,
            content_validation=content_result,
            platform_validation=platform_result,
            quality_metrics=quality_metrics,
            all_issues=all_issues,
            suggestions=suggestions
        )
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Validação concluída em {elapsed_time:.2f}s - Score: {overall_score:.3f}")
        
        return report

    def _validate_structure(self, script: GeneratedScript) -> ValidationResult:
        """Valida estrutura do roteiro."""
        issues: List[ValidationIssue] = []
        suggestions: List[str] = []
        
        # Verifica seções obrigatórias
        required_sections = {"hook", "development", "conclusion"}
        found_sections = {section.name for section in script.sections}
        
        missing_sections = required_sections - found_sections
        if missing_sections:
            for missing in missing_sections:
                issues.append(ValidationIssue(
                    code="STRUCTURE_MISSING_SECTION",
                    message=f"Seção obrigatória '{missing}' não encontrada",
                    severity=ValidationSeverity.ERROR,
                    section=missing,
                    suggestion=f"Adicione uma seção '{missing}' ao roteiro"
                ))
        
        # Verifica ordem das seções
        section_order = [section.name for section in script.sections]
        if section_order != ["hook", "development", "conclusion"]:
            suggestions.append("Reorganize as seções na ordem: Hook → Desenvolvimento → Conclusão")
        
        # Valida conteúdo de cada seção
        for section in script.sections:
            section_issues = self._validate_section_structure(section)
            issues.extend(section_issues)
        
        # Calcula score
        max_score = 100
        error_penalty = len([i for i in issues if i.severity == ValidationSeverity.ERROR]) * 20
        warning_penalty = len([i for i in issues if i.severity == ValidationSeverity.WARNING]) * 10
        score = max(0, max_score - error_penalty - warning_penalty)
        
        return ValidationResult(
            section_name="structure",
            is_valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
            score=score,
            issues=issues,
            suggestions=suggestions
        )

    def _validate_section_structure(self, section: ScriptSection) -> List[ValidationIssue]:
        """Valida estrutura de uma seção específica."""
        issues: List[ValidationIssue] = []
        
        # Verifica conteúdo vazio
        if not section.content or len(section.content.strip()) == 0:
            issues.append(ValidationIssue(
                code="SECTION_EMPTY",
                message=f"Seção '{section.name}' está vazia",
                severity=ValidationSeverity.ERROR,
                section=section.name,
                suggestion=f"Adicione conteúdo à seção '{section.name}'"
            ))
            return issues
        
        # Verifica duração adequada
        if section.duration_seconds <= 0:
            issues.append(ValidationIssue(
                code="SECTION_ZERO_DURATION",
                message=f"Seção '{section.name}' tem duração inválida",
                severity=ValidationSeverity.ERROR,
                section=section.name,
                suggestion="Defina uma duração válida para a seção"
            ))
        
        # Validações específicas por seção
        if section.name == "hook":
            hook_issues = self._validate_hook_section(section)
            issues.extend(hook_issues)
        elif section.name == "development":
            dev_issues = self._validate_development_section(section)
            issues.extend(dev_issues)
        elif section.name == "conclusion":
            conclusion_issues = self._validate_conclusion_section(section)
            issues.extend(conclusion_issues)
        
        return issues

    def _validate_hook_section(self, section: ScriptSection) -> List[ValidationIssue]:
        """Valida seção de hook especificamente."""
        issues: List[ValidationIssue] = []
        
        content = section.content.lower()
        
        # Verifica se tem elementos de engajamento
        has_question = bool(re.search(r'\?', content))
        has_emotional_words = bool(re.search(r'|'.join(self.ENGAGEMENT_PATTERNS["emotional"]), content))
        has_storytelling = bool(re.search(r'|'.join(self.ENGAGEMENT_PATTERNS["storytelling"]), content))
        
        if not (has_question or has_emotional_words or has_storytelling):
            issues.append(ValidationIssue(
                code="HOOK_LOW_ENGAGEMENT",
                message="Hook não tem elementos suficientes de engajamento",
                severity=ValidationSeverity.WARNING,
                section="hook",
                suggestion="Adicione perguntas, palavras emocionais ou storytelling ao hook"
            ))
        
        # Verifica tamanho do hook
        if len(section.content) < 50:
            issues.append(ValidationIssue(
                code="HOOK_TOO_SHORT",
                message="Hook é muito curto (menos de 50 caracteres)",
                severity=ValidationSeverity.WARNING,
                section="hook",
                suggestion="Torne o hook mais detalhado e envolvente"
            ))
        
        return issues

    def _validate_development_section(self, section: ScriptSection) -> List[ValidationIssue]:
        """Valida seção de desenvolvimento."""
        issues: List[ValidationIssue] = []
        
        content = section.content
        
        # Verifica se tem informações factuais
        has_numbers = bool(re.search(r'\d+', content))
        has_facts = bool(re.search(r'|'.join(self.ENGAGEMENT_PATTERNS["facts"]), content))
        
        if not (has_numbers or has_facts):
            issues.append(ValidationIssue(
                code="DEVELOPMENT_NO_FACTS",
                message="Seção de desenvolvimento carece de fatos ou dados",
                severity=ValidationSeverity.WARNING,
                section="development",
                suggestion="Adicione números, estatísticas ou fatos relevantes"
            ))
        
        # Verifica se é muito repetitivo
        words = content.lower().split()
        unique_words = set(words)
        if len(words) > 0 and len(unique_words) / len(words) < 0.5:
            issues.append(ValidationIssue(
                code="DEVELOPMENT_REPETITIVE",
                message="Seção de desenvolvimento é muito repetitiva",
                severity=ValidationSeverity.WARNING,
                section="development",
                suggestion="Varie o vocabulário e evite repetições"
            ))
        
        return issues

    def _validate_conclusion_section(self, section: ScriptSection) -> List[ValidationIssue]:
        """Valida seção de conclusão."""
        issues: List[ValidationIssue] = []
        
        content = section.content.lower()
        
        # Verifica se tem call-to-action
        cta_patterns = [r"curtir", r"compartilhar", r"seguir", r"inscrever", r"comente", r"achei"]
        has_cta = bool(re.search('|'.join(cta_patterns), content))
        
        if not has_cta:
            issues.append(ValidationIssue(
                code="CONCLUSION_NO_CTA",
                message="Conclusão não contém call-to-action",
                severity=ValidationSeverity.WARNING,
                section="conclusion",
                suggestion="Adicione um call-to-action (curtir, compartilhar, seguir)"
            ))
        
        # Verifica se é muito longa
        if len(section.content) > 200:
            issues.append(ValidationIssue(
                code="CONCLUSION_TOO_LONG",
                message="Conclusão é muito longa (mais de 200 caracteres)",
                severity=ValidationSeverity.WARNING,
                section="conclusion",
                suggestion="Torne a conclusão mais concisa e impactante"
            ))
        
        return issues

    def _validate_content(self, script: GeneratedScript) -> ValidationResult:
        """Valida qualidade do conteúdo."""
        issues: List[ValidationIssue] = []
        suggestions: List[str] = []
        
        # Análise de linguagem
        script_text = script.get_script_text()
        
        # Verifica linguagem adequada
        inappropriate_words = {"merda", "porra", "caralho", "bosta", "putinha"}
        found_inappropriate = [word for word in inappropriate_words if word in script_text.lower()]
        
        if found_inappropriate:
            issues.append(ValidationIssue(
                code="CONTENT_INAPPROPRIATE",
                message=f"Conteúdo contém palavras inadequadas: {', '.join(found_inappropriate)}",
                severity=ValidationSeverity.ERROR,
                suggestion="Remova palavras inadequadas para manter conteúdo apropriado"
            ))
        
        # Verifica repetição excessiva
        words = script_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignora palavras muito pequenas
                word_freq[word] = word_freq.get(word, 0) + 1
        
        repeated_words = [word for word, freq in word_freq.items() if freq > 3]
        if repeated_words:
            issues.append(ValidationIssue(
                code="CONTENT_REPETITIVE",
                message=f"Palavras muito repetidas: {', '.join(repeated_words[:5])}",
                severity=ValidationSeverity.WARNING,
                suggestion="Varie o vocabulário para evitar repetições"
            ))
        
        # Verifica Coerência temática
        if script.theme and script.theme.category:
            if not any(section.content.lower().find(script.theme.category.value.lower()) != -1 
                      for section in script.sections if section.content):
                issues.append(ValidationIssue(
                    code="CONTENT_THEME_MISMATCH",
                    message="Conteúdo não reflete claramente o tema/categoria",
                    severity=ValidationSeverity.WARNING,
                    suggestion=f"Garanta que o conteúdo esteja alinhado com a categoria '{script.theme.category}'"
                ))
        
        # Calcula score
        max_score = 100
        error_penalty = len([i for i in issues if i.severity == ValidationSeverity.ERROR]) * 25
        warning_penalty = len([i for i in issues if i.severity == ValidationSeverity.WARNING]) * 15
        score = max(0, max_score - error_penalty - warning_penalty)
        
        return ValidationResult(
            section_name="content",
            is_valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
            score=score,
            issues=issues,
            suggestions=suggestions
        )

    def _validate_platform_requirements(self, script: GeneratedScript, platform: PlatformType) -> ValidationResult:
        """Valida requisitos específicos da plataforma."""
        issues: List[ValidationIssue] = []
        suggestions: List[str] = []
        
        requirements = self.platform_requirements[platform]
        
        # Verifica duração total
        if script.total_duration > requirements.max_duration:
            issues.append(ValidationIssue(
                code="PLATFORM_DURATION_TOO_LONG",
                message=f"Duração {script.total_duration}s excede limite {requirements.max_duration}s para {platform.value}",
                severity=ValidationSeverity.ERROR,
                suggestion="Reduza a duração do roteiro"
            ))
        elif script.total_duration < requirements.min_duration:
            issues.append(ValidationIssue(
                code="PLATFORM_DURATION_TOO_SHORT",
                message=f"Duração {script.total_duration}s é muito curta (min: {requirements.min_duration}s) para {platform.value}",
                severity=ValidationSeverity.WARNING,
                suggestion="Aumente a duração do roteiro"
            ))
        
        # Verifica caracteres totais
        total_chars = len(script.get_script_text())
        if total_chars > requirements.max_characters:
            issues.append(ValidationIssue(
                code="PLATFORM_CHARS_TOO_LONG",
                message=f"Texto muito longo ({total_chars} chars) para {platform.value} (max: {requirements.max_characters})",
                severity=ValidationSeverity.ERROR,
                suggestion="Reduza o texto do roteiro"
            ))
        elif total_chars < requirements.min_characters:
            issues.append(ValidationIssue(
                code="PLATFORM_CHARS_TOO_SHORT",
                message=f"Texto muito curto ({total_chars} chars) para {platform.value} (min: {requirements.min_characters})",
                severity=ValidationSeverity.WARNING,
                suggestion="Expanda o conteúdo do roteiro"
            ))
        
        # Verifica palavras proibidas
        script_text = script.get_script_text().lower()
        found_banned = [word for word in requirements.banned_words if word in script_text]
        if found_banned:
            issues.append(ValidationIssue(
                code="PLATFORM_BANNED_WORDS",
                message=f"Palavras proibidas encontradas: {', '.join(found_banned)}",
                severity=ValidationSeverity.ERROR,
                section="all",
                suggestion="Remova palavras proibidas para a plataforma"
            ))
        
        # Verifica distribuição de duração por seção
        self._validate_section_distribution(script, requirements, issues)
        
        # Verifica elementos de engajamento específicos da plataforma
        self._validate_platform_engagement(script, platform, requirements, issues)
        
        # Calcula score
        max_score = 100
        error_penalty = len([i for i in issues if i.severity == ValidationSeverity.ERROR]) * 30
        warning_penalty = len([i for i in issues if i.severity == ValidationSeverity.WARNING]) * 20
        score = max(0, max_score - error_penalty - warning_penalty)
        
        return ValidationResult(
            section_name="platform",
            is_valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
            score=score,
            issues=issues,
            suggestions=suggestions
        )

    def _validate_section_distribution(self, script: GeneratedScript, requirements: PlatformRequirements, issues: List[ValidationIssue]):
        """Valida distribuição de duração por seção."""
        total_duration = script.total_duration
        
        for section in script.sections:
            section_percent = (section.duration_seconds / total_duration * 100) if total_duration > 0 else 0
            
            if section.name == "hook":
                expected_percent = requirements.hook_duration_percent * 100
                if abs(section_percent - expected_percent) > 10:  # Tolerância de 10%
                    issues.append(ValidationIssue(
                        code="PLATFORM_HOOK_DURATION_MISMATCH",
                        message=f"Hook representa {section_percent:.1f}% (esperado: {expected_percent:.1f}%)",
                        severity=ValidationSeverity.WARNING,
                        section="hook",
                        suggestion="Ajuste a duração do hook para melhor engajamento"
                    ))
            
            elif section.name == "development":
                expected_percent = requirements.development_duration_percent * 100
                if abs(section_percent - expected_percent) > 15:  # Tolerância de 15%
                    issues.append(ValidationIssue(
                        code="PLATFORM_DEVELOPMENT_DURATION_MISMATCH",
                        message=f"Desenvolvimento representa {section_percent:.1f}% (esperado: {expected_percent:.1f}%)",
                        severity=ValidationSeverity.WARNING,
                        section="development",
                        suggestion="Ajuste a duração do desenvolvimento"
                    ))
            
            elif section.name == "conclusion":
                expected_percent = requirements.conclusion_duration_percent * 100
                if abs(section_percent - expected_percent) > 10:  # Tolerância de 10%
                    issues.append(ValidationIssue(
                        code="PLATFORM_CONCLUSION_DURATION_MISMATCH",
                        message=f"Conclusão representa {section_percent:.1f}% (esperado: {expected_percent:.1f}%)",
                        severity=ValidationSeverity.WARNING,
                        section="conclusion",
                        suggestion="Ajuste a duração da conclusão"
                    ))

    def _validate_platform_engagement(self, script: GeneratedScript, platform: PlatformType, requirements: PlatformRequirements, issues: List[ValidationIssue]):
        """Valida elementos de engajamento específicos da plataforma."""
        script_text = script.get_script_text().lower()
        
        # Verifica frases de engajamento recomendadas
        found_engagement = [phrase for phrase in requirements.required_engagement_phrases 
                           if phrase.lower() in script_text]
        
        if not found_engagement:
            issues.append(ValidationIssue(
                code="PLATFORM_MISSING_ENGAGEMENT",
                message=f"Faltam frases de engajamento recomendadas para {platform.value}",
                severity=ValidationSeverity.WARNING,
                suggestion=f"Adicione frases como: {', '.join(list(requirements.required_engagement_phrases)[:3])}"
            ))

    def _analyze_quality_metrics(self, script: GeneratedScript) -> QualityMetrics:
        """Analisa métricas de qualidade detalhadas."""
        metrics = QualityMetrics()
        
        script_text = script.get_script_text()
        
        # Score de clareza
        clarity_issues = []
        
        # Verifica complexidade de sentenças
        sentences = re.split(r'[.!?]+', script_text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        
        if avg_sentence_length > 25:
            clarity_issues.append(ValidationIssue(
                code="CLARITY_COMPLEX_SENTENCES",
                message=f"Sentenças muito complexas (média: {avg_sentence_length:.1f} palavras)",
                severity=ValidationSeverity.WARNING,
                suggestion="Simplifique as sentenças para melhor compreensão"
            ))
        
        # Verifica jargões técnicos
        technical_terms = re.findall(r'\b[A-Z]{2,}\b|\b\w+ção\b|\b\w+ismo\b', script_text)
        if len(technical_terms) > 3:
            clarity_issues.append(ValidationIssue(
                code="CLARITY_TECHNICAL_JARGON",
                message=f"Muitos termos técnicos: {', '.join(technical_terms[:5])}",
                severity=ValidationSeverity.WARNING,
                suggestion="Explique termos técnicos ou use linguagem mais simples"
            ))
        
        metrics.clarity_score = max(0, 1.0 - len(clarity_issues) * 0.2)
        metrics.clarity_issues = clarity_issues
        
        # Score de engajamento
        engagement_issues = []
        
        # Conta padrões de engajamento
        engagement_count = 0
        for pattern_group in self.ENGAGEMENT_PATTERNS.values():
            for pattern in pattern_group:
                engagement_count += len(re.findall(pattern, script_text, re.IGNORECASE))
        
        if engagement_count < 3:
            engagement_issues.append(ValidationIssue(
                code="ENGAGEMENT_LOW_PATTERNS",
                message=f"Poucos elementos de engajamento (encontrados: {engagement_count})",
                severity=ValidationSeverity.WARNING,
                suggestion="Adicione mais perguntas, elementos emocionais e storytelling"
            ))
        
        metrics.engagement_score = min(1.0, engagement_count / 10.0)
        metrics.engagement_issues = engagement_issues
        
        # Score de retenção
        retention_issues = []
        
        # Conta padrões de retenção
        retention_count = 0
        for pattern_group in self.RETENTION_PATTERNS.values():
            for pattern in pattern_group:
                retention_count += len(re.findall(pattern, script_text, re.IGNORECASE))
        
        if retention_count < 2:
            retention_issues.append(ValidationIssue(
                code="RETENTION_LOW_PATTERNS",
                message=f"Poucos elementos de retenção (encontrados: {retention_count})",
                severity=ValidationSeverity.WARNING,
                suggestion="Adicione cliffhangers, estruturação clara e elementos de antecipação"
            ))
        
        metrics.retention_score = min(1.0, retention_count / 8.0)
        metrics.retention_issues = retention_issues
        
        return metrics

    def _calculate_overall_score(self, structure_result: ValidationResult, content_result: ValidationResult, 
                                platform_result: ValidationResult, quality_metrics: QualityMetrics) -> float:
        """Calcula score geral do roteiro."""
        # Pesos diferentes para cada aspecto
        weights = {
            "structure": 0.25,
            "content": 0.25,
            "platform": 0.25,
            "quality": 0.25
        }
        
        quality_avg = (quality_metrics.clarity_score + quality_metrics.engagement_score + quality_metrics.retention_score) / 3
        
        overall_score = (
            structure_result.score / 100 * weights["structure"] +
            content_result.score / 100 * weights["content"] +
            platform_result.score / 100 * weights["platform"] +
            quality_avg * weights["quality"]
        ) * 100
        
        return round(overall_score, 3)

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determina nível de qualidade baseado no score."""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR

    def _check_approval_criteria(self, issues: List[ValidationIssue], score: float) -> bool:
        """Verifica se o roteiro atende aos critérios de aprovação."""
        # Não pode ter erros críticos
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR]
        if critical_issues:
            return False
        
        # Score mínimo
        if score < 60:
            return False
        
        return True

    def _generate_suggestions(self, issues: List[ValidationIssue], structure_result: ValidationResult, 
                             content_result: ValidationResult, platform_result: ValidationResult) -> List[str]:
        """Gera sugestões de melhoria baseadas nos problemas encontrados."""
        suggestions = []
        
        # Coleta sugestões de issues
        for issue in issues:
            if issue.suggestion:
                suggestions.append(issue.suggestion)
        
        # Adiciona sugestões gerais baseadas nos scores
        if structure_result.score < 70:
            suggestions.append("Revise a estrutura do roteiro, garantindo que todas as seções estejam presentes e bem organizadas")
        
        if content_result.score < 70:
            suggestions.append("Melhore a qualidade do conteúdo, adicionando mais fatos, diminuindo repetições e tornando o texto mais envolvente")
        
        if platform_result.score < 70:
            suggestions.append("Ajuste o roteiro para atender melhor aos requisitos da plataforma (duração, formato, elementos específicos)")
        
        # Remove duplicatas e retorna
        return list(set(suggestions))

    def validate_multiple_platforms(self, script: GeneratedScript) -> Dict[PlatformType, ValidationReport]:
        """Valida roteiro para múltiplas plataformas."""
        reports = {}
        
        for platform in PlatformType:
            try:
                report = self.validate_script(script, platform)
                reports[platform] = report
            except Exception as e:
                logger.error(f"Erro ao validar para {platform.value}: {e}")
                continue
        
        return reports

    def save_validation_report(self, report: ValidationReport, filepath: Path) -> None:
        """Salva relatório de validação em arquivo."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "timestamp": report.timestamp.isoformat(),
            "script_title": report.script.title,
            "platform": report.platform.value,
            "overall_score": report.overall_score,
            "quality_level": report.quality_level.value,
            "is_approved": report.is_approved,
            "structure_validation": {
                "score": report.structure_validation.score,
                "is_valid": report.structure_validation.is_valid,
                "issues": [self._issue_to_dict(issue) for issue in report.structure_validation.issues]
            },
            "content_validation": {
                "score": report.content_validation.score,
                "is_valid": report.content_validation.is_valid,
                "issues": [self._issue_to_dict(issue) for issue in report.content_validation.issues]
            },
            "platform_validation": {
                "score": report.platform_validation.score,
                "is_valid": report.platform_validation.is_valid,
                "issues": [self._issue_to_dict(issue) for issue in report.platform_validation.issues]
            },
            "quality_metrics": {
                "clarity_score": report.quality_metrics.clarity_score,
                "engagement_score": report.quality_metrics.engagement_score,
                "retention_score": report.quality_metrics.retention_score
            },
            "all_issues": [self._issue_to_dict(issue) for issue in report.all_issues],
            "suggestions": report.suggestions,
            "summary": report.get_summary()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Relatório de validação salvo em: {filepath}")

    def _issue_to_dict(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Converte ValidationIssue para dicionário."""
        return {
            "code": issue.code,
            "message": issue.message,
            "severity": issue.severity.value,
            "section": issue.section,
            "field": issue.field,
            "suggestion": issue.suggestion,
            "position": issue.position,
            "details": issue.details
        }
