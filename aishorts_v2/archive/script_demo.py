#!/usr/bin/env python3
"""
Demonstração do Sistema de Roteiro - AiShorts v2.0

Este script demonstra o pipeline completo:
1. Gerar tema de curiosidade
2. Transformar tema em roteiro para TikTok/Shorts
3. Analisar qualidade do roteiro
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.generators.theme_generator import theme_generator, ThemeCategory
from src.generators.script_generator import script_generator
from src.config.settings import config


def main():
    """Demonstração principal do sistema de roteiro."""
    
    print("🎬" + "="*50 + "🎬")
    print("    AiShorts v2.0 - Sistema de Roteiro")
    print("🎬" + "="*50 + "🎬\n")
    
    # Configurar logger para demonstração
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    
    try:
        # =========================
        # 1. DEMONSTRAÇÃO BÁSICA
        # =========================
        print("📝 ETAPA 1: Gerando tema de curiosidade...\n")
        
        # Gerar tema base
        theme = theme_generator.generate_single_theme(ThemeCategory.SCIENCE)
        print(f"✅ Tema gerado: {theme.content}")
        print(f"⭐ Qualidade: {theme.quality_score:.2f}")
        print(f"📂 Categoria: {theme.category.value}")
        print(f"⏱️ Tempo: {theme.response_time:.2f}s\n")
        
        # =========================
        # 2. GERAÇÃO DE ROTEIRO
        # =========================
        print("🎬 ETAPA 2: Transformando tema em roteiro...\n")
        
        # Gerar roteiro para TikTok
        script = script_generator.generate_single_script(
            theme=theme,
            target_platform="tiktok"
        )
        
        print(f"✅ Roteiro gerado com sucesso!")
        print(f"🎯 Título: {script.title}")
        print(f"⏱️ Duração total: {script.total_duration:.1f} segundos")
        print(f"⭐ Qualidade: {script.quality_score:.2f}")
        print(f"🔥 Engajamento: {script.engagement_score:.2f}")
        print(f"👁️ Retenção: {script.retention_score:.2f}\n")
        
        # Mostrar estrutura detalhada
        print("📋 ESTRUTURA DO ROTEIRO:")
        print("-" * 40)
        for section in script.sections:
            print(f"\n🔸 {section.name.upper()}")
            print(f"   Conteúdo: {section.content}")
            print(f"   Duração: {section.duration_seconds:.1f}s")
            print(f"   Objetivo: {section.purpose}")
        
        print("\n" + "="*60)
        
        # =========================
        # 3. DEMONSTRAÇÃO AVANÇADA
        # =========================
        print("🚀 ETAPA 3: Geração múltipla e análise...\n")
        
        # Gerar múltiplos temas para diferentes categorias
        categories_demo = [ThemeCategory.NATURE, ThemeCategory.HISTORY]
        themes_multi = []
        
        for cat in categories_demo:
            theme_demo = theme_generator.generate_single_theme(cat)
            themes_multi.append(theme_demo)
            print(f"📝 Tema {cat.value}: {theme_demo.content[:60]}...")
        
        # Gerar múltiplos roteiros
        print(f"\n🎬 Gerando {len(themes_multi)} roteiros...")
        result = script_generator.generate_multiple_scripts(themes_multi, count=len(themes_multi))
        
        print(f"✅ {len(result.scripts)} roteiros gerados")
        print(f"🏆 Melhor roteiro: {result.best_script.title if result.best_script else 'Nenhum'}")
        
        # =========================
        # 4. ANÁLISE DETALHADA
        # =========================
        print(f"\n📊 ETAPA 4: Análise detalhada dos roteiros...\n")
        
        analysis = script_generator.analyze_scripts(result.scripts)
        
        print("📈 ESTATÍSTICAS DE DURAÇÃO:")
        duration_stats = analysis["duration_stats"]
        print(f"   • Média: {duration_stats['avg_duration']:.1f}s")
        print(f"   • Mínima: {duration_stats['min_duration']:.1f}s")
        print(f"   • Máxima: {duration_stats['max_duration']:.1f}s")
        
        print("\n⭐ ESTATÍSTICAS DE QUALIDADE:")
        quality_stats = analysis["quality_stats"]
        print(f"   • Média: {quality_stats['avg_quality']:.2f}")
        print(f"   • Melhor: {quality_stats['max_quality']:.2f}")
        
        print("\n🔥 ESTATÍSTICAS DE ENGAJAMENTO:")
        engagement_stats = analysis["engagement_stats"]
        print(f"   • Média: {engagement_stats['avg_engagement']:.2f}")
        print(f"   • Melhor: {engagement_stats['max_engagement']:.2f}")
        
        # =========================
        # 5. MELHOR ROTEIRO DETALHADO
        # =========================
        if result.best_script:
            print(f"\n🎯 MELHOR ROTEIRO - ANÁLISE DETALHADA:")
            print("-" * 50)
            best_script = result.best_script
            
            print(f"🎬 Título: {best_script.title}")
            print(f"📝 Tema base: {best_script.theme.content}")
            print(f"⏱️ Duração: {best_script.total_duration:.1f}s")
            print(f"⭐ Scores:")
            print(f"   • Qualidade: {best_script.quality_score:.2f}")
            print(f"   • Engajamento: {best_script.engagement_score:.2f}")
            print(f"   • Retenção: {best_script.retention_score:.2f}")
            
            print(f"\n🎭 ESTRUTURA COMPLETA:")
            for section in best_script.sections:
                print(f"\n   {section.name.upper()} ({section.duration_seconds:.1f}s):")
                print(f"   {section.content}")
        
        # =========================
        # 6. SALVAR RESULTADOS
        # =========================
        print(f"\n💾 ETAPA 5: Salvando resultados...\n")
        
        # Salvar resultado da geração múltipla
        script_file = script_generator.save_script_result(result)
        print(f"✅ Resultados salvos em: {script_file}")
        
        # Salvar roteiro individual
        individual_file = Path(config.storage.output_dir) / f"individual_script_{int(time.time())}.json"
        best_script.save_to_file(individual_file)
        print(f"✅ Melhor roteiro salvo em: {individual_file}")
        
        print(f"\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("📋 RESUMO:")
        print(f"   • {len(themes_multi)} temas gerados")
        print(f"   • {len(result.scripts)} roteiros criados")
        print(f"   • Duração média: {duration_stats['avg_duration']:.1f}s")
        print(f"   • Qualidade média: {quality_stats['avg_quality']:.2f}")
        print(f"   • Melhor engajamento: {engagement_stats['max_engagement']:.2f}")
        print("\n🚀 Sistema pronto para produção!")
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração: {e}")
        print(f"\n💥 Erro durante a execução: {e}")
        raise


if __name__ == "__main__":
    main()