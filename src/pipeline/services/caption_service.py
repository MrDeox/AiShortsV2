import logging
import re
from typing import Any, Dict, List, Optional


class CaptionService:
    """Serviço responsável por construir legendas alinhadas ao tempo do áudio."""

    def __init__(
        self,
        *,
        min_segment_duration: float = 1.8,
        final_segment_min_duration: float = 0.5,
    ):
        self._min_segment_duration = min_segment_duration
        self._final_segment_min_duration = final_segment_min_duration
        self._logger = logging.getLogger(self.__class__.__name__)

    def build_captions(self, text: Optional[str], audio_duration: float) -> List[Dict[str, Any]]:
        """Gera legendas aproximadas distribuindo a duração proporcionalmente às palavras."""
        if not text or audio_duration <= 0:
            self._logger.debug("Legenda não gerada: texto vazio ou áudio inválido.")
            return []

        sentences = self._split_into_sentences(text)
        if not sentences:
            sentences = [text.strip()]

        total_words = sum(len(sentence.split()) for sentence in sentences) or len(sentences)
        captions: List[Dict[str, Any]] = []
        start_time = 0.0

        for index, sentence in enumerate(sentences):
            words = max(len(sentence.split()), 1)
            remaining_audio = max(audio_duration - start_time, 0.0)
            remaining_segments = len(sentences) - index

            if remaining_audio <= 0:
                break

            proportional_duration = (words / total_words) * audio_duration
            min_remaining_for_tail = max((remaining_segments - 1) * self._min_segment_duration, 0.0)

            segment_duration = max(self._min_segment_duration, proportional_duration)
            if remaining_segments > 1:
                segment_duration = min(segment_duration, remaining_audio - min_remaining_for_tail)
                segment_duration = max(self._min_segment_duration, segment_duration)
            else:
                segment_duration = max(self._final_segment_min_duration, remaining_audio)

            end_time = min(audio_duration, start_time + segment_duration)

            captions.append({
                "text": sentence,
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "style": self._default_style(),
            })

            start_time = end_time

        self._logger.info("Legendas geradas: %d segmentos", len(captions))
        return captions

    def _split_into_sentences(self, text: str) -> List[str]:
        paragraphs = [
            chunk.strip()
            for chunk in re.split(r"\n+", text)
            if chunk.strip()
        ]
        sentences: List[str] = []
        for chunk in paragraphs:
            sentences.extend([
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", chunk)
                if sentence.strip()
            ])
        return sentences

    def _default_style(self) -> Dict[str, Any]:
        return {
            "position": "center",
            "baseline": "bottom",
            "font_size": 58,
            "line_spacing": 12,
            "font_color": "#FFFFFF",
            "stroke_color": "#000000",
            "stroke_width": 3,
            "background_color": "#101010",
            "background_opacity": 0.88,
            "padding_horizontal": 48,
            "padding_vertical": 28,
            "max_width_ratio": 0.92,
            "vertical_margin_ratio": 0.08,
        }
