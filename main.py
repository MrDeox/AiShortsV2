#!/usr/bin/env python3
"""
AiShorts v2.0 - Pipeline Orquestrado

Este módulo inicializa as dependências principais e aciona o orquestrador que
executa todo o fluxo de geração de vídeos curtos, mantendo a lógica de negócio
isolada em módulos separados dentro de `src/pipeline`.
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Ajuste de caminho para permitir imports relativos ao projeto
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(1, str(SRC_DIR))

# --------------------------------------------------------------------------- #
# Configurações de ambiente e logging
# --------------------------------------------------------------------------- #
env_path = Path(".env").absolute()
load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("outputs/pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("AiShortsMain")

# --------------------------------------------------------------------------- #
# Imports das camadas de domínio
# --------------------------------------------------------------------------- #
from src.core.openrouter_client import openrouter_client  # noqa: E402
from src.generators.prompt_engineering import ThemeCategory  # noqa: E402
from src.generators.script_generator import ScriptGenerator  # noqa: E402
from src.generators.theme_generator import ThemeGenerator  # noqa: E402
from src.pipeline.orchestrator import AiShortsOrchestrator  # noqa: E402
from src.pipeline.services.broll_query_service import BrollQueryService  # noqa: E402
from src.pipeline.services.caption_service import CaptionService  # noqa: E402
from src.tts.kokoro_tts import KokoroTTSClient  # noqa: E402
from src.utils.translator import translator  # noqa: E402
from src.video.extractors.youtube_extractor import YouTubeExtractor  # noqa: E402
from src.video.matching.semantic_analyzer import SemanticAnalyzer  # noqa: E402
from src.video.processing.video_processor import VideoProcessor  # noqa: E402
from src.video.sync.audio_video_synchronizer import AudioVideoSynchronizer  # noqa: E402


# --------------------------------------------------------------------------- #
# Fábrica do orquestrador
# --------------------------------------------------------------------------- #
def create_orchestrator() -> AiShortsOrchestrator:
    """Instancia e configura todas as dependências do pipeline."""
    logger.info("🚀 Inicializando dependências do pipeline AiShorts v2.0...")

    theme_generator = ThemeGenerator()
    script_generator = ScriptGenerator()
    tts_client = KokoroTTSClient()
    youtube_extractor = YouTubeExtractor()
    semantic_analyzer = SemanticAnalyzer()
    audio_video_sync = AudioVideoSynchronizer()
    video_processor = VideoProcessor()
    broll_query_service = BrollQueryService(openrouter_client)
    caption_service = CaptionService()

    logger.info("✅ Dependências inicializadas com sucesso!")

    return AiShortsOrchestrator(
        theme_generator=theme_generator,
        script_generator=script_generator,
        translator=translator,
        tts_client=tts_client,
        youtube_extractor=youtube_extractor,
        semantic_analyzer=semantic_analyzer,
        audio_video_sync=audio_video_sync,
        video_processor=video_processor,
        broll_query_service=broll_query_service,
        caption_service=caption_service,
        logger=logging.getLogger("AiShortsOrchestrator"),
    )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    """Ponto de entrada principal."""
    print("🎬 AiShorts v2.0 - Geração de Vídeo Curto")
    print("=" * 50)

    orchestrator = create_orchestrator()

    print("\n🚀 Executando pipeline completo...")
    results = orchestrator.run(theme_category=ThemeCategory.ANIMALS)

    if results.get("status") == "success":
        print("\n🎉 SUCESSO! Vídeo gerado com todas as etapas.")
        print(f"⏱️ Tempo total: {results['total_time']:.2f}s")
        print("📁 Arquivos gerados:")

        script_hook = results["script"]["content_en"].get("hook") or ""
        if script_hook:
            print(f"   • Roteiro (EN) - Hook: {script_hook[:60]}...")

        if results["script"].get("content_pt"):
            preview_pt = results["script"]["content_pt"].split("\n")[0]
            print(f"   • Roteiro (PT-BR): {preview_pt[:60]}...")

        llm_queries = results["script"].get("broll_queries") or []
        if llm_queries:
            print(f"   • Queries B-roll (LLM): {', '.join(llm_queries)}")

        print(f"   • Áudio: {results['audio']['file_path']}")
        print(f"   • Vídeos B-roll: {len(results['broll']['videos'])}")

        captions_count = len(results.get("captions") or [])
        if captions_count:
            print(f"   • Legendas sincronizadas: {captions_count}")

        print(f"   • Vídeo Final: {results['final']['video_path']}")
        print("   • Relatório: outputs/pipeline_report_*.json")
    else:
        print(f"\n❌ FALHA: {results.get('error', 'Erro desconhecido')}")

    return results


if __name__ == "__main__":
    main()
