"""
Kokoro TTS Client para AiShorts v2.0
Backend principal de TTS baseado em Kokoro, com suporte a múltiplos idiomas,
seleção de vozes configurável e integração com o pipeline de vídeo.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import soundfile as sf
from importlib import import_module

# Detecta Kokoro de forma mais flexível:
# - Primeiro tenta importar pacote "kokoro" (instalado via pip ou disponível no PYTHONPATH)
# - Se falhar, mantém _KOKORO_AVAILABLE=False, e o main/pipeline pode decidir usar mock/skip.
try:
    kokoro_module = import_module("kokoro")
    KPipeline = getattr(kokoro_module, "KPipeline")  # type: ignore[assignment]
    _KOKORO_AVAILABLE = True
except Exception:  # pragma: no cover - proteção ampla
    KPipeline = None  # type: ignore[assignment]
    _KOKORO_AVAILABLE = False

from src.models.script_models import Script

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Config / Mapping
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class KokoroTTSConfig:
    lang_code: str = "p"  # código interno Kokoro (ex: 'p' para pt-BR)
    default_voice: str = "af_diamond"
    speed: float = 1.0
    output_root: str = "outputs/audio"
    model_preset: Optional[str] = None
    device: Optional[str] = None


# Mapa simplificado de vozes por idioma (adaptar/expandir conforme VOICES.md)
VOICE_MAP: Dict[str, Dict[str, str]] = {
    "p": {
        "af_diamond": "PT-BR - Feminina",
        "af_heart": "PT-BR - Feminina",
        "af_breeze": "PT-BR - Feminina",
        "af_sol": "PT-BR - Feminina",
        "am_oreo": "PT-BR - Masculina",
        "am_glenn": "PT-BR - Masculina",
        "am_liam": "PT-BR - Masculina",
    },
    # Exemplos para outros idiomas (preencher conforme guia)
    "a": {},  # en-US
    "b": {},  # en-UK
    "e": {},  # es
    "f": {},  # fr
    "i": {},  # it
    "j": {},  # ja
    "z": {},  # zh
}


def _ensure_kokoro_available() -> None:
    """
    Garante que Kokoro esteja disponível.

    Ajuste para o seu setup:
    - Se você instalou via guia Asimov em outro projeto/venv, o import falha aqui.
    - Em vez de explodir o main, vamos:
        * emitir um warning quando não houver Kokoro;
        * permitir que o pipeline rode com TTS desabilitado (mock),
          até você alinhar o ambiente.
    """
    if not _KOKORO_AVAILABLE:
        import warnings

        warnings.warn(
            "Kokoro TTS não encontrado no ambiente atual. "
            "O pipeline continuará com TTS desabilitado (modo mock).",
            RuntimeWarning,
        )


def _resolve_output_dir(
    output_root: str,
    lang_code: str,
    voice: str,
) -> Path:
    """
    Aplica a convenção:
    outputs/audio/{lang_code}/{voice}/
    """
    out_dir = Path(output_root) / lang_code / voice
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


# --------------------------------------------------------------------------- #
# KokoroTTSClient - API pública usada pelo pipeline
# --------------------------------------------------------------------------- #


class KokoroTTSClient:
    """
    Serviço TTS baseado em Kokoro.

    Contrato público principal (usado pelo pipeline):
    - text_to_speech(text, output_basename, **kwargs) -> dict
      - deve retornar: {success, audio_path, duration, voice, lang_code, speed, sample_rate}
    - script_to_audio(script, base_name, **kwargs) -> dict (utilitário de alto nível)
    - get_voice_list(), set_voice(), set_speed(), set_lang(), optimize_for_platform()
    """

    def __init__(
        self,
        lang_code: str = "p",
        default_voice: str = "af_diamond",
        speed: float = 1.0,
        output_root: str = "outputs/audio",
        model_preset: Optional[str] = None,
        device: Optional[str] = None,
    ) -> None:
        _ensure_kokoro_available()

        config = KokoroTTSConfig(
            lang_code=lang_code,
            default_voice=default_voice,
            speed=speed,
            output_root=output_root,
            model_preset=model_preset,
            device=device,
        )

        self._config = config
        self.lang_code = config.lang_code
        self.voice_name = config.default_voice
        self.speed = config.speed
        self.output_root = config.output_root

        self._pipeline = self._init_pipeline()

logger.info(
            "KokoroTTSClient inicializado | lang=%s voice=%s speed=%.2f output_root=%s",
            self.lang_code,
            self.voice_name,
            self.speed,
            self.output_root,
        )

    # ------------------------------------------------------------------ #
    # Inicialização / helpers internos
    # ------------------------------------------------------------------ #

    def _init_pipeline(self) -> Any:
        """
        Inicializa o KPipeline com o lang_code atual.

        Se Kokoro não estiver disponível (_KOKORO_AVAILABLE=False ou KPipeline=None),
        retorna um pipeline mock que simula saída de áudio.
        Isso permite rodar o main.py e o pipeline completo sem Kokoro real.
        """
        if not _KOKORO_AVAILABLE or KPipeline is None:
logger.warning(
                "Kokoro TTS indisponível - usando pipeline TTS mock para desenvolvimento."
            )

            import numpy as np

            def _mock_pipeline(text: str, voice: str, speed: float, split_pattern: str = r"\n+"):
                # Gera áudio sintético silencioso/ruído leve apenas para manter fluxo.
                # 24000 Hz * 3s ~ 72000 amostras por trecho.
                duration_sec = max(1.0, min(5.0, len(text) / 40.0))  # 40 chars ~ 1s
                sr = 24000
                length = int(sr * duration_sec)
                audio = np.zeros(length, dtype=np.float32)

                # Interface compatível com o gerador esperado em _run_kokoro_pipeline
                # yield idx, (start, end, audio_array)
                yield 0, (0.0, duration_sec, audio)

            return _mock_pipeline

        # Kokoro real disponível
        try:
            if self._config.model_preset:
                pipeline = KPipeline(
                    lang_code=self.lang_code,
                    model_preset=self._config.model_preset,  # type: ignore[arg-type]
                )
            else:
                pipeline = KPipeline(lang_code=self.lang_code)
        except Exception as exc:  # pragma: no cover - falha de ambiente/modelo
logger.error("Erro ao inicializar KPipeline: %s", exc)
            # Fallback para mock se inicialização real falhar
            import numpy as np

            def _fallback_mock(text: str, voice: str, speed: float, split_pattern: str = r"\n+"):
                duration_sec = max(1.0, min(5.0, len(text) / 40.0))
                sr = 24000
                length = int(sr * duration_sec)
                audio = np.zeros(length, dtype=np.float32)
                yield 0, (0.0, duration_sec, audio)

logger.warning(
                "Falha ao inicializar Kokoro real. Usando pipeline TTS mock. Erro: %s", exc
            )
            return _fallback_mock

        return pipeline

    def _validate_voice(self, voice: str, lang_code: Optional[str] = None) -> str:
        lang = (lang_code or self.lang_code) or "p"
        voices = VOICE_MAP.get(lang, {})
        if voice not in voices:
            # Mantém o comportamento atual de erro explícito usado nos testes.
            raise ValueError(
                f"Voz '{voice}' não disponível para lang '{lang}'. "
                f"Disponíveis: {list(voices.keys())}"
            )
        return voice

    def _effective_params(
        self,
        lang_code: Optional[str],
        voice: Optional[str],
        speed: Optional[float],
    ) -> Dict[str, Any]:
        eff_lang = (lang_code or self.lang_code) or "p"
        if voice:
            eff_voice = self._validate_voice(voice, eff_lang)
        else:
            # Se default não pertence ao VOICE_MAP, aceita mesmo assim.
            if eff_lang in VOICE_MAP and VOICE_MAP[eff_lang]:
                eff_voice = (
                    self.voice_name
                    if self.voice_name in VOICE_MAP[eff_lang]
                    else list(VOICE_MAP[eff_lang].keys())[0]
                )
            else:
                eff_voice = self.voice_name
        eff_speed = speed if speed is not None else self.speed
        if eff_speed <= 0:
            raise ValueError("Velocidade deve ser positiva.")
        return {"lang_code": eff_lang, "voice": eff_voice, "speed": eff_speed}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def text_to_speech(
        self,
        text: str,
        output_basename: str,
        *,
        lang_code: Optional[str] = None,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        split_long_text: bool = True,
    ) -> Dict[str, Any]:
        """
        Converte texto em um único arquivo WAV, seguindo convenção de paths.

        Saída:
        - outputs/audio/{lang}/{voice}/{output_basename}.wav
        """
        if not text or not text.strip():
            raise ValueError("Texto vazio fornecido para TTS")

        text = text.strip()
        params = self._effective_params(lang_code, voice, speed)
        eff_lang = params["lang_code"]
        eff_voice = params["voice"]
        eff_speed = params["speed"]

        output_dir = _resolve_output_dir(self.output_root, eff_lang, eff_voice)
        base = output_basename.replace(".wav", "")
        target_path = output_dir / f"{base}.wav"

        try:
            if split_long_text and len(text) > 1000:
                # Delegar para helper de múltiplos segmentos.
                segments = self._synthesize_segments(
                    text=text,
                    eff_lang=eff_lang,
                    eff_voice=eff_voice,
                    eff_speed=eff_speed,
                    output_dir=output_dir,
                    base_name=base,
                )
                return self._combine_segments_to_single(
                    segments,
                    target_path=target_path,
                    lang_code=eff_lang,
                    voice=eff_voice,
                    speed=eff_speed,
                    metadata=metadata,
                )

            # Texto curto: gerar direto um único WAV
            audio = self._run_kokoro_pipeline(
                text=text,
                eff_lang=eff_lang,
                eff_voice=eff_voice,
                eff_speed=eff_speed,
            )
            sf.write(str(target_path), audio, 24000)
            duration = len(audio) / 24000.0

logger.info(
                "Áudio TTS gerado | path=%s dur=%.2fs lang=%s voice=%s",
                target_path,
                duration,
                eff_lang,
                eff_voice,
            )

            return {
                "success": True,
                "audio_path": str(target_path),
                "duration": duration,
                "text": text,
                "lang_code": eff_lang,
                "voice": eff_voice,
                "speed": eff_speed,
                "sample_rate": 24000,
                "metadata": metadata or {},
            }
        except Exception as exc:  # pragma: no cover - erros de runtime externo
logger.error("Erro na síntese Kokoro: %s", exc)
            return {
                "success": False,
                "error": str(exc),
                "audio_path": None,
                "duration": 0.0,
                "lang_code": eff_lang,
                "voice": eff_voice,
            }

    def script_to_audio(
        self,
        script: Script,
        *,
        base_name: str,
        lang_code: Optional[str] = None,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        per_section: bool = True,
    ) -> Dict[str, Any]:
        """
        Gera narração a partir de um Script estruturado.

        - Quando per_section=True:
          - Gera 1 WAV por seção
          - Gera também um WAV completo combinando todas as seções
        """
        params = self._effective_params(lang_code, voice, speed)
        eff_lang = params["lang_code"]
        eff_voice = params["voice"]
        eff_speed = params["speed"]

        output_dir = _resolve_output_dir(self.output_root, eff_lang, eff_voice)

        all_text_parts: List[str] = []
        section_audios: List[Dict[str, Any]] = []

        if per_section:
            for idx, section in enumerate(script.sections):
                if not section.content:
                    continue
                section_text = section.content.strip()
                if not section_text:
                    continue

                all_text_parts.append(section_text)

                sec_basename = f"{base_name}_section_{idx+1}_{section.type}"
                result = self.text_to_speech(
                    section_text,
                    sec_basename,
                    lang_code=eff_lang,
                    voice=eff_voice,
                    speed=eff_speed,
                    split_long_text=False,
                )
                if result.get("success"):
                    section_audios.append(
                        {
                            "section_type": section.type,
                            "index": idx,
                            "audio_path": result["audio_path"],
                            "duration": result["duration"],
                        }
                    )

        if not all_text_parts:
            # fallback: usa todo o conteúdo plano do script, se existir
            combined_text = "\n".join(
                [s.content for s in script.sections if s.content]
            ).strip()
        else:
            combined_text = "\n".join(all_text_parts).strip()

        full_basename = f"{base_name}_full"
        full_result = self.text_to_speech(
            combined_text,
            full_basename,
            lang_code=eff_lang,
            voice=eff_voice,
            speed=eff_speed,
            split_long_text=True,
        )

        total_duration = sum(s["duration"] for s in section_audios) or full_result.get(
            "duration", 0.0
        )

        return {
            "success": bool(full_result.get("success")),
            "script_id": script.id,
            "lang_code": eff_lang,
            "voice": eff_voice,
            "speed": eff_speed,
            "sections_count": len(script.sections),
            "total_text_length": len(combined_text),
            "total_duration": total_duration,
            "full_audio_path": full_result.get("audio_path"),
            "section_audios": section_audios,
        }

    def get_voice_list(self, lang_code: Optional[str] = None) -> Dict[str, str]:
        """
        Retorna vozes disponíveis para um idioma Kokoro (default: lang atual).
        Mantém compatibilidade com testes que esperam um dict.
        """
        lang = (lang_code or self.lang_code) or "p"
        return VOICE_MAP.get(lang, {}).copy()

    def set_speed(self, speed: float) -> None:
        """
        Atualiza velocidade default.
        Mantém validação compatível com testes (0.5–2.0).
        """
        if 0.5 <= speed <= 2.0:
            self.speed = speed
logger.info("Velocidade TTS ajustada para %.2fx", speed)
        else:
            raise ValueError("Velocidade deve estar entre 0.5 e 2.0")

    def set_voice(self, voice_name: str, lang_code: Optional[str] = None) -> None:
        """
        Atualiza voz default com validação.
        Compatível com testes existentes (raise em caso inválido).
        """
        lang = (lang_code or self.lang_code) or "p"
        voices = VOICE_MAP.get(lang, {})
        if voice_name not in voices:
            raise ValueError(
                f"Voz '{voice_name}' não disponível para lang '{lang}'. "
                f"Disponíveis: {list(voices.keys())}"
            )
        self.voice_name = voice_name
logger.info("Voz TTS ajustada para %s (lang=%s)", voice_name, lang)

    def set_lang(self, lang_code: str) -> None:
        """
        Atualiza idioma default; reinicializa pipeline para alinhar com Kokoro.
        """
        if not lang_code:
            raise ValueError("lang_code não pode ser vazio")
        self.lang_code = lang_code
        self._pipeline = self._init_pipeline()
logger.info("Idioma TTS ajustado para %s", lang_code)

    def optimize_for_platform(
        self,
        audio_path: str,
        platform: str,
        target_duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Analisa duração do áudio vs. limites de plataforma.
        Não altera o arquivo; apenas retorna metadados.
        """
        try:
            data, sr = sf.read(audio_path)
        except Exception as exc:  # pragma: no cover
            return {"success": False, "error": str(exc), "audio_path": audio_path}

        duration = float(len(data)) / float(sr or 24000)

        configs = {
            "tiktok": {"max": 60.0, "recommended": 45.0},
            "shorts": {"max": 60.0, "recommended": 45.0},
            "reels": {"max": 90.0, "recommended": 60.0},
        }
        cfg = configs.get(platform.lower(), configs["tiktok"])

        is_compliant = duration <= cfg["max"]
        is_optimal = duration <= cfg["recommended"]

        speed_factor = 1.0
        if target_duration and target_duration > 0 and duration > target_duration:
            speed_factor = duration / target_duration

        recommendations: List[str] = []
        if not is_compliant:
            recommendations.append(
                f"Áudio muito longo ({duration:.1f}s). Máximo {cfg['max']}s."
            )
        elif not is_optimal:
            recommendations.append(
                f"Duração pode ser otimizada (~{cfg['recommended']}s recomendado)."
            )
        else:
            recommendations.append("Duração adequada para a plataforma.")

        return {
            "success": True,
            "audio_path": audio_path,
            "platform": platform,
            "original_duration": duration,
            "target_duration": target_duration,
            "platform_max_duration": cfg["max"],
            "platform_recommended_duration": cfg["recommended"],
            "is_compliant": is_compliant,
            "is_optimal": is_optimal,
            "speed_factor": speed_factor,
            "recommendations": recommendations,
        }

    # ------------------------------------------------------------------ #
    # Implementação interna Kokoro
    # ------------------------------------------------------------------ #

    def _run_kokoro_pipeline(
        self,
        text: str,
        eff_lang: str,
        eff_voice: str,
        eff_speed: float,
    ):
        """
        Executa o KPipeline e retorna um único array de áudio (1D).
        Projetado para ser facilmente mockado nos testes.
        """
        generator = self._pipeline(
            text=text,
            voice=eff_voice,
            speed=eff_speed,
            split_pattern=r"\n+",
        )

        import numpy as np
 
        audio_chunks: List[Any] = []
        # Aceita múltiplos formatos de saída do pipeline (real ou mock):
        # - (idx, (start, end, audio))
        # - (idx, audio)
        # - audio direto
        for item in generator:
            if isinstance(item, tuple):
                if len(item) == 2:
                    idx, payload = item
                    if isinstance(payload, tuple) and len(payload) == 3:
                        _, _, audio = payload
                    else:
                        audio = payload
                elif len(item) == 3:
                    # (start, end, audio) ou similar
                    _, _, audio = item
                else:
                    # fallback: tenta último elemento como audio
                    audio = item[-1]
            else:
                audio = item
 
            audio_chunks.append(audio)

        if not audio_chunks:
            raise RuntimeError("Nenhum áudio gerado pelo Kokoro")

        if len(audio_chunks) == 1:
            return audio_chunks[0]

        return np.concatenate(audio_chunks)

    def _synthesize_segments(
        self,
        text: str,
        eff_lang: str,
        eff_voice: str,
        eff_speed: float,
        output_dir: Path,
        base_name: str,
    ) -> List[Path]:
        """
        Divide texto longo em segmentos e gera múltiplos arquivos WAV.
        Retorna lista de paths.
        """
        import re

        parts = [p.strip() for p in re.split(r"[.!?]+\s*", text) if p.strip()]
        segments: List[Path] = []

        for idx, part in enumerate(parts, start=1):
            seg_audio = self._run_kokoro_pipeline(
                text=part,
                eff_lang=eff_lang,
                eff_voice=eff_voice,
                eff_speed=eff_speed,
            )
            seg_path = output_dir / f"{base_name}_part_{idx}.wav"
            sf.write(str(seg_path), seg_audio, 24000)
            segments.append(seg_path)

        return segments

    def _combine_segments_to_single(
        self,
        segments: List[Path],
        target_path: Path,
        *,
        lang_code: str,
        voice: str,
        speed: float,
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Concatena segmentos WAV em um único arquivo target_path.
        """
        import numpy as np

        if not segments:
            raise RuntimeError("Nenhum segmento gerado para combinação")

        audio_all: List[Any] = []
        for seg in segments:
            if seg.exists():
                data, sr = sf.read(str(seg))
                if sr != 24000:
                    # Normalização simples (não reamostra aqui; assume alinhado nos testes).
logger.warning(
                        "Sample rate inesperado (%s) em %s; esperado 24000.",
                        sr,
                        seg,
                    )
                audio_all.append(data)

        if not audio_all:
            raise RuntimeError("Falha ao carregar segmentos para combinação")

        final_audio = np.concatenate(audio_all)
        sf.write(str(target_path), final_audio, 24000)
        duration = len(final_audio) / 24000.0

        return {
            "success": True,
            "audio_path": str(target_path),
            "duration": duration,
            "lang_code": lang_code,
            "voice": voice,
            "speed": speed,
            "sample_rate": 24000,
            "metadata": metadata or {},
        }


def main() -> None:
    """
    Execução manual simples de smoke-test (não usada em testes automatizados).
    """
    if not _KOKORO_AVAILABLE:
print("Kokoro não disponível; instale kokoro-tts para teste manual.")
        return

    client = KokoroTTSClient()
    text = "Olá! Este é um teste do sistema de narração Kokoro para AiShorts v2.0."
    result = client.text_to_speech(text, output_basename="teste_basico")
print(result)


if __name__ == "__main__":  # pragma: no cover
    main()
