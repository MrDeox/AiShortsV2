"""
Translation utilities for AiShorts v2.0.

Provides a thin wrapper around the OpenRouter client to translate content
between languages while preserving structure and tone.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

from src.core.openrouter_client import openrouter_client
from src.utils.exceptions import RateLimitError, OpenRouterError

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Resultado da tradução."""
    success: bool
    translated_text: Optional[str] = None
    response_time: Optional[float] = None
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class Translator:
    """Wrapper para tradução usando o cliente OpenRouter."""

    def __init__(
        self,
        target_language: str = "pt-BR",
        client=None,
        max_retries: int = 4,
        base_delay: float = 2.0,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ):
        self.default_target_language = target_language
        self.client = client or openrouter_client
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.default_max_tokens = max_tokens
        self.default_temperature = temperature

    def translate(
        self,
        text: str,
        target_language: Optional[str] = None,
        system_message: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.2,
    ) -> TranslationResult:
        if not text or not text.strip():
logger.warning("Texto vazio recebido para tradução")
            return TranslationResult(success=False, error="empty_text")

        target = target_language or self.default_target_language
logger.info(f" Iniciando tradução para {target} (tokens máx: {max_tokens})")

        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        target = target_language or self.default_target_language

        effective_system_message = system_message or (
            "You are a professional literary translator working from English into "
            f"{target}. Rewrite the given content in natural language, preserving meaning, tone, "
            "stylistic devices, and any structural markers (HEADERS, bullet points, timing, etc.). "
            "Return only the translated text without additional commentary."
        )

        prompt = (
            f"Translate the following text into {target}. Keep the original structure, headers, "
            "and formatting. Return only the translated text.\n\n"
            f"{text}"
        )

        delay = self.base_delay

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.generate_content(
                    prompt=prompt,
                    system_message=effective_system_message,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                translated = response.content.strip()
                if not translated:
logger.warning(
                        f"⚠️ Tradução retornou conteúdo vazio (tentativa {attempt}/{self.max_retries})."
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue

logger.info(" Tradução concluída com sucesso")
                return TranslationResult(
                    success=True,
                    translated_text=translated,
                    response_time=response.response_time,
                    usage=response.usage,
                )

            except RateLimitError as rl_err:
                wait = rl_err.details.get('wait_time') if isinstance(rl_err.details, dict) else None
                wait = wait or delay
logger.warning(
                    f"⚠️ Tradução atingiu rate limit (tentativa {attempt}/{self.max_retries}). "
                    f"Aguardando {wait:.1f}s antes de tentar novamente."
                )
                time.sleep(wait)
                delay *= 2
                continue

            except OpenRouterError as api_err:
logger.error(f" Falha na tradução (OpenRouter): {api_err}")
                return TranslationResult(success=False, error=str(api_err))

            except Exception as exc:
logger.error(f" Falha inesperada na tradução: {exc}")
                return TranslationResult(success=False, error=str(exc))

logger.error(" Tradução falhou após múltiplas tentativas")
        return TranslationResult(success=False, error="translation_rate_limit_exceeded")


# Instância padrão reutilizável
translator = Translator()
