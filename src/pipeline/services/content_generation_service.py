"""
ContentGenerationService - Responsável pela geração de tema, script e tradução.
Extrai a lógica de geração de conteúdo do AiShortsOrchestrator para melhor separação de responsabilidades.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from src.generators.prompt_engineering import ThemeCategory
from src.models.unified_models import (
    GeneratedTheme,
    GeneratedScript,
    TranslationResult,
    TTSAudioResult
)
from src.validators.script_validator import ScriptValidator, PlatformType
from src.utils.exceptions import ScriptGenerationError, ThemeGenerationError, TTSError, TranslationError
from src.config.settings import config
from src.core.graceful_degradation import retry, fallback, FallbackStrategy, RetryConfig

# Importar helpers LLM se disponíveis
try:
    from src.core.llm_helpers import LLMHelpers
    LLM_HELPERS_AVAILABLE = True
except ImportError:
    LLM_HELPERS_AVAILABLE = False


class ContentGenerationService:
    """Serviço responsável por gerar temas, scripts e traduções."""
    
    def __init__(
        self,
        theme_generator,
        script_generator,
        translator,
        tts_client,
        script_validator: Optional[ScriptValidator] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.theme_generator = theme_generator
        self.script_generator = script_generator
        self.translator = translator
        self.tts_client = tts_client
        self.script_validator = script_validator or ScriptValidator()
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Inicializar helpers LLM se disponível e ativado
        self.llm_helpers = None
        if LLM_HELPERS_AVAILABLE and config.llm_integration.use_llm_theme_strategy:
            self.llm_helpers = LLMHelpers()
self.logger.info("🧠 LLM Theme Strategy Engine ativado")
        elif not config.llm_integration.use_llm_theme_strategy:
self.logger.info(" LLM Theme Strategy Engine desativado via configuração")
        
        # Cache de temas recentes para evitar repetições
        self._recent_themes: List[str] = []
    
    @retry(RetryConfig(max_attempts=3, initial_delay=1.0))
    @fallback(FallbackStrategy.DEGRADE, fallback_value="Default science theme")
    async def generate_theme(self, category: ThemeCategory) -> Tuple[GeneratedTheme, Dict[str, Any]]:
        """
        Gera um tema para a categoria especificada usando LLM Strategy Engine se disponível.
        
        Returns:
            Tuple[GeneratedTheme, Dict]: Tema gerado e resultado para compatibilidade
        """
self.logger.info(" ETAPA 1: Geração de Tema com IA...")
        
        # Usar LLM Theme Strategy Engine se disponível
        if self.llm_helpers:
            try:
self.logger.info("🧠 Usando LLM Theme Strategy Engine...")
                
                # Gerar tema estratégico via LLM
                theme_strategy = await self.llm_helpers.generate_theme_strategy(
                    category=category.value,
                    recent_themes=self._recent_themes,
                    constraints={
                        "max_words": 40,
                        "must_be_fact_based": True,
                        "avoid_overlap_with_recent": True,
                        "avoid_generic": True
                    }
                )
                
                # Criar GeneratedTheme a partir do resultado LLM
                theme = GeneratedTheme(
                    content=theme_strategy.topic,
                    category=category,
                    quality_score=(theme_strategy.uniqueness_score + theme_strategy.virality_potential) / 2,
                    response_time=0.0,  # Não medido aqui
                    metadata={
                        "angle": theme_strategy.angle,
                        "safety_flags": theme_strategy.safety_flags,
                        "uniqueness_score": theme_strategy.uniqueness_score,
                        "virality_potential": theme_strategy.virality_potential,
                        "generated_by": "llm_theme_strategy"
                    }
                )
                
                # Adicionar aos temas recentes
                self._recent_themes.append(theme.content)
                if len(self._recent_themes) > 20:  # Manter apenas últimos 20
                    self._recent_themes.pop(0)
                
self.logger.info(" Tema LLM gerado: %s...", theme.content[:100])
self.logger.info(" Uniqueness: %.2f, Virality: %.2f",
                               theme_strategy.uniqueness_score, 
                               theme_strategy.virality_potential)
self.logger.info(" Angle: %s", theme_strategy.angle)
                
            except Exception as e:
self.logger.error(f" Erro no LLM Theme Strategy Engine: {e}")
self.logger.info(" Fazendo fallback para método tradicional...")
                
                # Fallback para método tradicional
                theme = self.theme_generator.generate_single_theme(category)
        else:
            # Método tradicional
            theme = self.theme_generator.generate_single_theme(category)
        
        # Log comum
self.logger.info(" Tema completo (EN): %s", theme.content)
self.logger.info(" Comprimento do tema: %d palavras", len(theme.content.split()))
        
        result = {
            "content_en": theme.content,
            "category": theme.category.value,
            "quality": theme.quality_score,
            "response_time": theme.response_time,
            "metadata": theme.metadata or {}
        }
        return theme, result
    
    @retry(RetryConfig(max_attempts=2, initial_delay=0.5))
    async def generate_script(
        self,
        theme: GeneratedTheme,
        target_platform: str = "tiktok",
        max_attempts: int = 4,
        validation_threshold: float = 70.0
    ) -> Tuple[GeneratedScript, Dict[str, Any]]:
        """
        Gera um roteiro validado para o tema especificado com suporte a LLM Script Refiner.
        
        Returns:
            Tuple[GeneratedScript, Dict]: Script gerado e resultado para compatibilidade
        """
self.logger.info(" ETAPA 2: Geração de roteiro em inglês com validação robusta...")
        
        custom_requirements = None
        last_error = None
        script_refinements = 0
        
        for attempt in range(1, max_attempts + 1):
            try:
                script = self.script_generator.generate_single_script(
                    theme=theme,
                    custom_requirements=custom_requirements,
                    target_platform=target_platform,
                )
                
                # Validar roteiro
self.logger.info(" Validando qualidade do roteiro gerado...")
                validation_report = self.script_validator.validate_script(
                    script, 
                    PlatformType.TIKTOK if target_platform == "tiktok" else PlatformType.YOUTUBE_SHORTS
                )
                
                # Log detalhado da validação
self.logger.info(
                    "📊 Validação - Score geral: %.2f, Nível: %s, Aprovado: %s",
                    validation_report.overall_score,
                    validation_report.quality_level.value,
                    "✅" if validation_report.is_approved else "❌"
                )
                
                # Log de issues críticos
                critical_issues = validation_report.get_critical_issues()
                if critical_issues:
self.logger.warning(" Issues críticos encontrados (%d):", len(critical_issues))
                    for issue in critical_issues[:3]:
self.logger.warning("   • %s: %s", issue.code, issue.message)
                
                # Log de sugestões
                if validation_report.suggestions:
self.logger.info(" Sugestões de melhoria:")
                    for suggestion in validation_report.suggestions[:3]:
self.logger.info("   • %s", suggestion)
                
                # Extrair texto do script
                hook_text = script.hook.content if script.hook else ""
                body_text = script.development.content if script.development else ""
                conclusion_text = script.conclusion.content if script.conclusion else ""
                
                # Processar duração estimada se presente
                estimated_duration_from_text = None
                if conclusion_text and "ESTIMATED_DURATION" in conclusion_text:
                    parts = conclusion_text.split("ESTIMATED_DURATION")
                    conclusion_text = parts[0].strip()
                    try:
                        estimated_duration_from_text = float(parts[1].split(":")[-1].strip(" `"))
                    except Exception:
                        estimated_duration_from_text = None
                
                # Limpar formatação
                if body_text.endswith("```"):
                    body_text = body_text.rstrip("`").rstrip()
                if conclusion_text.endswith("```"):
                    conclusion_text = conclusion_text.rstrip("`").rstrip()
                
                # Construir textos estruturado e plano
                structured_text = "\n".join(
                    filter(None, [
                        f"HOOK: {hook_text}" if hook_text else "",
                        f"BODY: {body_text}" if body_text else "",
                        f"CONCLUSION: {conclusion_text}" if conclusion_text else "",
                    ])
                ).strip()
                
                plain_text = "\n".join(
                    [line for line in [hook_text, body_text, conclusion_text] if line]
                ).strip()
                
                # Verificar critérios de aprovação
                duration_ok = script.total_duration >= 45.0
                validation_ok = validation_report.overall_score >= validation_threshold
                no_critical_errors = len(critical_issues) == 0
                
                # Construir resultado
                result = {
                    "title": script.title,
                    "total_duration": script.total_duration,
                    "quality_score": script.quality_score,
                    "engagement_score": script.engagement_score,
                    "retention_score": script.retention_score,
                    "generated_at": script.timestamp.isoformat(),
                    "content_en": {
                        "hook": hook_text,
                        "body": body_text,
                        "conclusion": conclusion_text,
                        "structured_text": structured_text,
                        "plain_text": plain_text,
                    },
                    "validation": {
                        "overall_score": validation_report.overall_score,
                        "quality_level": validation_report.quality_level.value,
                        "is_approved": validation_report.is_approved,
                        "critical_issues": len(critical_issues),
                        "total_issues": len(validation_report.all_issues),
                        "suggestions": validation_report.suggestions[:5]
                    }
                }
                
                if estimated_duration_from_text:
                    result["estimated_duration_from_text"] = estimated_duration_from_text
                
self.logger.info(
                    "📝 Roteiro gerado (EN) - Score: %.2f, Validação: %.2f, Duração: %.1fs",
                    script.quality_score,
                    validation_report.overall_score,
                    script.total_duration,
                )
self.logger.info("   HOOK (EN): %s", hook_text)
self.logger.info("   BODY (EN): %s", body_text[:100] + "..." if len(body_text) > 100 else body_text)
self.logger.info("   CONCLUSION (EN): %s", conclusion_text)
                
                # Verificar aprovação
                if duration_ok and validation_ok and no_critical_errors:
self.logger.info(" Roteiro aprovado pela validação robusta!")
                    return script, result
                
                # Preparar para retry
self.logger.warning(
                    "⚠️ Roteiro não atendeu aos critérios (tentativa %d):",
                    attempt,
                )
                if not duration_ok:
self.logger.warning("   • Duração muito curta: %.1fs", script.total_duration)
                if not validation_ok:
self.logger.warning(
                        "   • Score de validação baixo: %.2f (mín: %.1f)", 
                        validation_report.overall_score, 
                        validation_threshold
                    )
                if critical_issues:
self.logger.warning("   • %d erros críticos encontrados", len(critical_issues))
                
                # Usar LLM Script Refiner se disponível e ainda não excedeu o limite
                if (self.llm_helpers and 
                    config.llm_integration.use_llm_script_refiner and
                    script_refinements < config.llm_integration.max_script_refinements):
                    
                    try:
self.logger.info("🧠 Usando LLM Script Refiner...")
                        
                        # Preparar script atual em formato de dict
                        script_dict = {
                            "hook": hook_text,
                            "body": body_text,
                            "conclusion": conclusion_text
                        }
                        
                        # Preparar resumo da validação
                        validation_summary = {
                            "overall_score": validation_report.overall_score,
                            "critical_issues": [
                                {"code": issue.code, "message": issue.message}
                                for issue in critical_issues[:5]
                            ],
                            "suggestions": validation_report.suggestions[:3]
                        }
                        
                        # Refinar script via LLM
                        refined_script = await self.llm_helpers.refine_script(
                            platform=target_platform,
                            theme=theme.content,
                            previous_script=script_dict,
                            validation_summary=validation_summary,
                            constraints={
                                "target_duration": [50, 65],
                                "language": "pt-BR",
                                "safe_for_ads": True
                            }
                        )
                        
                        # Atualizar script com refinamento
                        script.hook.content = refined_script.hook
                        script.development.content = refined_script.body
                        script.conclusion.content = refined_script.conclusion
                        
                        # Adicionar nota de refinamento
                        if not hasattr(script, 'metadata'):
                            script.metadata = {}
                        script.metadata['llm_refined'] = True
                        script.metadata['refinement_count'] = script_refinements + 1
                        script.metadata['refinement_notes'] = refined_script.refinement_notes
                        
                        script_refinements += 1
self.logger.info(" Script refinado via LLM (refinamento #%d)", script_refinements)
                        
                        # Continuar para próxima iteração com script refinado
                        custom_requirements = None  # Não precisa de custom requirements
                        last_error = "validation_failed"
                        continue
                        
                    except Exception as e:
self.logger.error(f" Erro no LLM Script Refiner: {e}")
self.logger.info(" Continuando com método tradicional...")
                
                custom_requirements = self._generate_refined_requirements(validation_report, attempt)
                last_error = "validation_failed"
                
            except Exception as error:
                last_error = str(error)
self.logger.error(" Erro na geração do roteiro (tentativa %d): %s", attempt, error)
                custom_requirements = [
                    "Use three paragraphs: HOOK, BODY (6 sentences, 140-160 words), CONCLUSION (≥25 words)",
                    "Return the ESTIMATED_DURATION on its own line",
                ]
        
        raise ScriptGenerationError(
            f"Falha ao gerar roteiro consistente após {max_attempts} tentativas: {last_error}",
            theme_content=theme.content,
            platform=target_platform,
        )
    
    @retry(RetryConfig(max_attempts=3, initial_delay=0.5))
    @fallback(FallbackStrategy.USE_DEFAULT, fallback_value="")
    def translate_script(self, script_plain_text: str) -> TranslationResult:
        """
        Traduz o script para português.
        
        Returns:
            TranslationResult: Resultado da tradução
        """
        translation_result = self.translator.translate(script_plain_text)
        
        if translation_result.success:
            script_text_pt = translation_result.translated_text or script_plain_text
self.logger.info(" Roteiro traduzido (PT-BR): %s", script_text_pt)
self.logger.info(" Roteiro traduzido para PT-BR com sucesso")
        else:
            script_text_pt = script_plain_text
self.logger.warning(" Tradução falhou, utilizando roteiro em inglês para TTS")
            if translation_result.error:
self.logger.warning("Motivo da falha de tradução: %s", translation_result.error)
        
        return TranslationResult(
            success=translation_result.success,
            translated_text=script_text_pt,
            response_time=translation_result.response_time,
            usage=translation_result.usage,
            error=translation_result.error
        )
    
    @retry(RetryConfig(max_attempts=2, initial_delay=1.0))
    @fallback(FallbackStrategy.SKIP)
    def synthesize_audio(self, script_text_pt: str) -> TTSAudioResult:
        """
        Sintetiza áudio a partir do texto em português.
        
        Returns:
            TTSAudioResult: Resultado da síntese TTS
        """
self.logger.info(" ETAPA 3: Síntese de Áudio TTS...")
        
        output_basename = f"narracao_{datetime.now().strftime('%H%M%S')}"
        result = self.tts_client.text_to_speech(
            script_text_pt,
            output_basename=output_basename,
        )
        
        if not result.get("success"):
            return TTSAudioResult(
                success=False,
                audio_path="",
                duration=0.0,
                error=result.get("error", "Unknown TTS error")
            )
        
        audio_path = result.get("audio_path")
        duration = float(result.get("duration", 0.0))
        voice = result.get("voice")
        
self.logger.info(" Áudio gerado: %s", audio_path)
self.logger.info("⏱ Duração: %.2fs", duration)
        if voice:
self.logger.info(" Voz: %s", voice)
        
        return TTSAudioResult(
            success=True,
            audio_path=audio_path,
            duration=duration,
            voice=voice,
            lang_code=result.get("lang_code"),
            metadata=result
        )
    
    def _generate_refined_requirements(self, validation_report, attempt: int) -> List[str]:
        """Gera requisitos refinados com base nas falhas da validação."""
        requirements = []
        
        # Requisitos base
        base_requirements = [
            "Ensure the script follows the structure: HOOK, BODY (6+ sentences), CONCLUSION",
            "Return ESTIMATED_DURATION on its own line as ESTIMATED_DURATION: <seconds>",
            "Overall narration should take 55-60 seconds when spoken"
        ]
        requirements.extend(base_requirements)
        
        # Analisar falhas específicas
        critical_issues = validation_report.get_critical_issues()
        
        # Problemas de estrutura
        structure_issues = [i for i in critical_issues if i.code.startswith("STRUCTURE_")]
        if structure_issues:
            requirements.append(
                "FIX STRUCTURE: Ensure all three sections (HOOK, BODY, CONCLUSION) are clearly labeled and complete"
            )
        
        # Problemas com hook
        hook_issues = [i for i in validation_report.all_issues if i.section == "hook"]
        if hook_issues:
            hook_codes = [i.code for i in hook_issues]
            if "HOOK_LOW_ENGAGEMENT" in hook_codes:
                requirements.append(
                    "IMPROVE HOOK: Start with a question, surprising fact, or emotional statement"
                )
            if "HOOK_TOO_SHORT" in hook_codes:
                requirements.append("LENGTHEN HOOK: Make hook at least 50 characters with impact")
        
        # Problemas com desenvolvimento
        dev_issues = [i for i in validation_report.all_issues if i.section == "development"]
        if dev_issues:
            dev_codes = [i.code for i in dev_issues]
            if "DEVELOPMENT_NO_FACTS" in dev_codes:
                requirements.append(
                    "ADD FACTS: Include specific numbers, statistics, or research findings"
                )
            if "DEVELOPMENT_REPETITIVE" in dev_codes:
                requirements.append(
                    "REDUCE REPETITION: Use varied vocabulary and sentence structures"
                )
        
        # Problemas com conclusão
        conclusion_issues = [i for i in validation_report.all_issues if i.section == "conclusion"]
        if conclusion_issues:
            conclusion_codes = [i.code for i in conclusion_issues]
            if "CONCLUSION_NO_CTA" in conclusion_codes:
                requirements.append(
                    "ADD CTA: Include call-to-action (like, share, follow, comment)"
                )
            if "CONCLUSION_TOO_LONG" in conclusion_codes:
                requirements.append("SHORTEN CONCLUSION: Keep conclusion under 200 characters")
        
        # Problemas de duração
        duration_issues = [i for i in validation_report.all_issues if "DURATION" in i.code]
        if duration_issues:
            requirements.append("ADJUST DURATION: Target 55-60 seconds total speaking time")
            requirements.append(
                "Balance sections: Hook ~15%, Body ~70%, Conclusion ~15% of total time"
            )
        
        # Problemas de conteúdo
        content_issues = [i for i in critical_issues if i.code.startswith("CONTENT_")]
        if content_issues:
            requirements.append(
                "IMPROVE CONTENT: Ensure appropriate language and thematic coherence"
            )
        
        # Incentivos baseados no número de tentativas
        if attempt >= 2:
            requirements.append("FOCUS ON QUALITY: This retry must show significant improvement")
            requirements.append("BE MORE SPECIFIC: Use concrete examples and vivid descriptions")
        
        if attempt >= 3:
            requirements.append(
                "URGENT: Previous attempts failed validation. Address ALL identified issues"
            )
            requirements.append(
                "MAXIMUM ENGAGEMENT: Use questions, emotional words, and storytelling techniques"
            )
        
        return requirements[:8]  # Máximo de 8 requisitos focados