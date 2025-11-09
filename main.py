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
import asyncio
import sys
from src.core.performance_orchestrator import run_optimized_pipeline, run_enhanced_pipeline  # noqa: E402
from src.generators.prompt_engineering import ThemeCategory  # noqa: E402
from src.core.memory_monitor import get_memory_monitor  # noqa: E402


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    """Ponto de entrada principal com pipeline otimizado."""
    print("🎬 AiShorts v2.0 - Pipeline Super Otimizado")
    print("=" * 55)

    # Verificar se deve usar enhanced mode
    use_enhanced = "--enhanced" in sys.argv or "-e" in sys.argv
    
    if use_enhanced:
        print("✨ MODO ENHANCED ATIVADO - Usando otimizações LLM avançadas")
        print("   • Previsão de viralidade com IA")
        print("   • Análise de qualidade visual")
        print("   • B-roll enhancement inteligente")
    else:
        print("🚀 MODO PADRÃO - Pipeline otimizado básico")
        print("   • Use --enhanced ou -e para ativar todas as otimizações")
    
    print()

    # Iniciar monitoramento de memória
    memory_monitor = get_memory_monitor()
    initial_stats = memory_monitor.get_current_stats()
    
    print(f"💾 Memória inicial: {initial_stats.process_gb:.2f}GB ({initial_stats.system_percent:.1f}% sistema)")
    logger.info("✅ Otimizações de memória local ativadas")

    print("\n" + "=" * 73)
    print("🎬 INICIANDO PIPELINE AISHORTS V2.0 - GERAÇÃO DE VÍDEO")
    print("=" * 73)

    # Executar pipeline de forma assíncrona
    try:
        if use_enhanced:
            print("🔮 Executando Enhanced Pipeline com IA avançada...")
            results = asyncio.run(run_enhanced_pipeline(theme_category="animals"))
        else:
            print("⚡ Executando Pipeline Otimizado padrão...")
            results = asyncio.run(run_optimized_pipeline(theme_category="animals", enhanced_mode=False))
        
        if results.get("success"):
            print("\n🎉 SUCESSO! Pipeline concluído com brilhantismo.")
            
            # Exibir tipo de pipeline
            pipeline_type = results.get('pipeline_type', 'unknown')
            print(f"📊 Pipeline executado: {pipeline_type.replace('_', ' ').title()}")
            
            # Exibir métricas de performance
            perf_metrics = results.get('performance_metrics', {})
            overall_metrics = perf_metrics.get('overall', {})
            enhanced_metrics = results.get('enhanced_metrics', {})
            
            print(f"⏱️ Tempo total: {results.get('total_time', 0):.2f}s")
            print(f"🚀 Tempo economizado: {overall_metrics.get('total_time_saved_seconds', 0):.2f}s")
            print(f"💾 Cache hit rate: {overall_metrics.get('cache_hit_rate', '0%')}")
            
            # Métricas enhanced se disponíveis
            if enhanced_metrics:
                print(f"\n✨ Métricas Enhanced:")
                content_insights = enhanced_metrics.get('content_insights', {})
                print(f"   🔮 Nível viralidade: {content_insights.get('virality_level', 'N/A')}")
                print(f"   🎬 Score qualidade: {content_insights.get('average_quality_score', 0):.1f}/100")
                print(f"   🔍 Queries enhanced: {content_insights.get('enhanced_queries_count', 0)}")
                
                perf_improvements = enhanced_metrics.get('performance_improvements', {})
                print(f"   🤖 Otimizações IA ativas: {perf_improvements.get('llm_enhancements_active', 0)}")
                print(f"   📡 Requests LLM totais: {perf_improvements.get('total_llm_requests', 0)}")
            
            print("\n📁 Resultados:")
            theme = results.get('theme', 'N/A')
            script = results.get('script', 'N/A')
            video_count = len(results.get('video_paths', []))
            
            if theme != 'N/A':
                print(f"   • Tema: {theme[:60]}...")
            if script != 'N/A':
                print(f"   • Script: {script[:60]}...")
            print(f"   • Vídeos baixados: {video_count}")
            
            # Análises especiais se disponíveis
            if results.get('virality_analysis'):
                virality = results['virality_analysis']
                virality_scores = virality.get('virality_scores', {})
                print(f"   🔮 Score viralidade: {virality_scores.get('overall_score', 0):.1f}/100")
                
            if results.get('quality_analyses'):
                quality_scores = [qa.get('overall_score', 0) for qa in results['quality_analyses']]
                avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
                print(f"   🎬 Qualidade média vídeos: {avg_quality:.1f}/100")
            
            # Exibir estatísticas finais de memória
            final_stats = memory_monitor.get_current_stats()
            print(f"\n💾 Memória final: {final_stats.process_gb:.2f}GB ({final_stats.system_percent:.1f}% sistema)")
            
        else:
            error = results.get('error', 'Erro desconhecido')
            print(f"\n❌ FALHA: {error}")
            logger.error(f"Pipeline falhou: {error}")

        return results

    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrompido pelo usuário.")
        return {"success": False, "error": "Interrupção do usuário"}
    
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        logger.error(f"Erro crítico no pipeline: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    main()
