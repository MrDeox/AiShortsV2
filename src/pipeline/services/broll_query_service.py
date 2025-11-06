import json
import logging
from typing import List, Optional


class BrollQueryService:
    """Responsável por gerar queries de B-roll usando modelos LLM."""

    def __init__(self, llm_client, max_tokens: int = 200, temperature: float = 0.3):
        self._llm_client = llm_client
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._logger = logging.getLogger(self.__class__.__name__)

    def generate_queries(self, script_text: Optional[str]) -> List[str]:
        """Gera queries curtas e acionáveis para busca de B-roll."""
        if not script_text:
            self._logger.debug("Texto do script vazio; sem queries de B-roll para gerar.")
            return []

        system_message = (
            "You are a video content assistant. Your job is to read the provided short-form script "
            "and output concise YouTube search queries (in English) to find matching b-roll footage. "
            "Return 3 to 5 queries, 3-5 words each, focused on nouns and visual actions. "
            "Output them as a JSON array of strings with no explanations."
        )
        prompt = (
            "Script:\n"
            f"{script_text}\n\n"
            "Return JSON array with search queries."
        )

        try:
            response = self._llm_client.generate_content(
                prompt=prompt,
                system_message=system_message,
                max_tokens=self._max_tokens,
                temperature=self._temperature
            )
        except Exception as error:
            self._logger.warning("Falha na chamada LLM para queries de B-roll: %s", error)
            return []

        raw_content = (response.content or "").strip()
        if not raw_content:
            self._logger.info("LLM retornou resposta vazia para queries de B-roll.")
            return []

        queries: List[str] = []
        try:
            parsed = json.loads(raw_content)
            if isinstance(parsed, list):
                queries = [str(item).strip() for item in parsed if str(item).strip()]
            else:
                raise ValueError("Resposta não era um array JSON.")
        except Exception:
            queries = [
                line.strip("-• ").strip()
                for line in raw_content.splitlines()
                if line.strip()
            ]

        deduped = []
        for query in queries:
            if query and query not in deduped:
                deduped.append(query)

        final_queries = deduped[:5]
        self._logger.info("Queries de B-roll geradas: %s", final_queries)
        return final_queries
