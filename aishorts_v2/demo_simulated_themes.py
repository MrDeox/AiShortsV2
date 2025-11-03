#!/usr/bin/env python3
"""
Demo Simulado do Gerador de Tema - AiShorts v2.0

Demonstração completa sem fazer chamadas reais à API.
"""

import sys
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def simulate_theme_generation():
    """Simula a geração de tema sem fazer chamadas à API."""
    print("=" * 70)
    print("🚀 AiShorts v2.0 - Demo SIMULADO do Gerador de Tema")
    print("=" * 70)
    
    try:
        from src.generators.theme_generator import GeneratedTheme, ThemeGenerationResult, theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        # 1. Verificar configuração
        print("📋 Configuração Atual:")
        model_info = theme_generator.openrouter.get_model_info()
        print(f"   Modelo: {model_info['model']}")
        print(f"   Max Tokens: {model_info['max_tokens']}")
        print(f"   Temperatura: {model_info['temperature']}")
        print(f"   Categorias: {len(theme_generator.config.categories)}")
        
        # 2. Simular geração única
        print("\n🎯 DEMO 1: Geração de Tema Único (SIMULADA)")
        print("-" * 50)
        
        print("Simulando geração de tema sobre CIÊNCIA...")
        
        # Simular resposta da API
        simulated_themes = {
            ThemeCategory.SCIENCE: "Por que o gelo flutua na água sendo sólido?",
            ThemeCategory.HISTORY: "Como funcionava o calendário dos maias?",
            ThemeCategory.NATURE: "Por que os flamingos são rosa?",
            ThemeCategory.TECHNOLOGY: "Como seu celular calcula a rota mais rápida?",
            ThemeCategory.CULTURE: "Por que alguns países andam no lado errado da rua?",
            ThemeCategory.SPACE: "Como as galáxias se formam no universo?",
            ThemeCategory.ANIMALS: "Como os golfinhos dormem sem se afogar?",
            ThemeCategory.PSYCHOLOGY: "Por que temos Déjà vu?",
            ThemeCategory.GEOGRAPHY: "Por que a Groenlândia é tão verde mesmo sendo gelada?",
            ThemeCategory.FOOD: "Como o chocolate pode ser bom para a saúde?"
        }
        
        # Simular geração
        simulated_theme = GeneratedTheme(
            content=simulated_themes[ThemeCategory.SCIENCE],
            category=ThemeCategory.SCIENCE,
            quality_score=0.87,
            response_time=1.4,
            timestamp=datetime.now(),
            usage={"total_tokens": 85, "prompt_tokens": 65, "completion_tokens": 20},
            metrics={"overall_quality": 0.87, "criteria_scores": []}
        )
        
        print(f"📝 Tema: {simulated_theme.content}")
        print(f"⭐ Qualidade: {simulated_theme.quality_score:.2f}/1.0")
        print(f"⏱️ Tempo: {simulated_theme.response_time:.2f}s")
        print(f"🗂️ Categoria: {simulated_theme.category.value}")
        print(f"🔢 Tokens: {simulated_theme.usage}")
        
        # 3. Simular geração múltipla
        print("\n🎲 DEMO 2: Geração Múltipla (SIMULADA)")
        print("-" * 50)
        
        # Criar temas simulados de diferentes categorias
        simulated_themes_list = []
        categories_for_demo = [
            ThemeCategory.SCIENCE, 
            ThemeCategory.HISTORY, 
            ThemeCategory.NATURE, 
            ThemeCategory.TECHNOLOGY,
            ThemeCategory.ANIMALS
        ]
        
        for i, category in enumerate(categories_for_demo):
            theme = GeneratedTheme(
                content=simulated_themes[category],
                category=category,
                quality_score=0.75 + (i * 0.03),  # Scores crescente
                response_time=1.0 + (i * 0.2),   # Tempos variados
                timestamp=datetime.now(),
                usage={"total_tokens": 70 + i * 5, "prompt_tokens": 50 + i * 3, "completion_tokens": 20 + i * 2}
            )
            simulated_themes_list.append(theme)
        
        # Criar resultado simulado
        simulated_result = ThemeGenerationResult(
            themes=simulated_themes_list,
            best_theme=max(simulated_themes_list, key=lambda t: t.quality_score),
            total_time=7.5,
            generation_stats={
                "total_attempts": 7,
                "successful_generations": 5,
                "failed_generations": 2,
                "categories_used": [c.value for c in categories_for_demo],
                "avg_quality_score": 0.81,
                "quality_scores": [t.quality_score for t in simulated_themes_list],
                "response_times": [t.response_time for t in simulated_themes_list]
            }
        )
        
        print(f"📊 Resultados da Geração Múltipla:")
        print(f"   Temas gerados: {len(simulated_result.themes)}")
        print(f"   Tentativas totais: {simulated_result.generation_stats['total_attempts']}")
        print(f"   Sucessos: {simulated_result.generation_stats['successful_generations']}")
        print(f"   Falhas: {simulated_result.generation_stats['failed_generations']}")
        print(f"   Tempo total: {simulated_result.total_time:.1f}s")
        
        print(f"\n🏆 Melhor Tema: {simulated_result.best_theme.content}")
        print(f"   Score: {simulated_result.best_theme.quality_score:.2f}")
        print(f"   Categoria: {simulated_result.best_theme.category.value}")
        
        # 4. Análise detalhada
        print("\n📈 DEMO 3: Sistema de Análise Detalhada")
        print("-" * 50)
        
        analysis = theme_generator.analyze_themes(simulated_themes_list)
        
        print("📊 Estatísticas de Qualidade:")
        print(f"   Média: {analysis['quality_stats']['avg_quality']:.3f}")
        print(f"   Mínima: {analysis['quality_stats']['min_quality']:.3f}")
        print(f"   Máxima: {analysis['quality_stats']['max_quality']:.3f}")
        print(f"   Desvio padrão: {analysis['quality_stats']['std_quality']:.3f}")
        
        print("\n⚡ Estatísticas de Performance:")
        print(f"   Tempo médio: {analysis['performance_stats']['avg_time']:.2f}s")
        print(f"   Tempo mínimo: {analysis['performance_stats']['min_time']:.2f}s")
        print(f"   Tempo máximo: {analysis['performance_stats']['max_time']:.2f}s")
        
        print("\n🏆 Ranking dos Melhores Temas:")
        for i, theme in enumerate(analysis['best_themes'], 1):
            print(f"   {i}. {theme['content']}")
            print(f"      📊 Score: {theme['quality_score']:.3f} | 🏷️ {theme['category']}")
        
        print("\n📂 Distribuição por Categoria:")
        for category, data in analysis['categories'].items():
            print(f"   {category}: {data['count']} tema(s)")
            print(f"      Qualidade média: {data['avg_quality']:.3f}")
            print(f"      Tempo médio: {data['avg_time']:.2f}s")
        
        # 5. Sistema de salvamento
        print("\n💾 DEMO 4: Sistema de Salvamento e Carregamento")
        print("-" * 50)
        
        filepath = theme_generator.save_generation_result(simulated_result, "demo_simulated_themes.json")
        print(f"✅ Resultado salvo em: {filepath}")
        
        # Verificar se arquivo foi criado
        if filepath.exists():
            print(f"✅ Arquivo criado com sucesso: {filepath.stat().st_size} bytes")
        
        # Carregar e verificar
        loaded_result = ThemeGenerationResult.load_from_file(filepath)
        print(f"✅ Resultado carregado: {len(loaded_result.themes)} temas")
        print(f"   Melhor tema: {loaded_result.best_theme.content[:50]}...")
        
        # 6. Demonstração do prompt engineering
        print("\n🧠 DEMO 5: Sistema de Prompt Engineering")
        print("-" * 50)
        
        from src.generators.prompt_engineering import prompt_engineering
        
        # Mostrar exemplo de prompt para ciência
        science_prompt = prompt_engineering.create_generation_prompt(ThemeCategory.SCIENCE)
        print("📝 Exemplo de Prompt para Ciência:")
        print(f"System Message (primeiras 150 chars):")
        print(f"   {science_prompt['system_message'][:150]}...")
        print(f"\nUser Prompt:")
        print(f"   {science_prompt['user_prompt'][:150]}...")
        
        print(f"\n🎯 Critérios de Qualidade:")
        for criterion in science_prompt['quality_criteria']:
            print(f"   • {criterion}")
        
        # Testar validação
        print(f"\n✅ Validação de Formato:")
        good_theme = "Por que o céu é azul?"
        bad_theme = "O céu é azul por causa da refração da luz"
        
        print(f"   Bom formato: '{good_theme}' → {prompt_engineering.validate_prompt_format(good_theme)}")
        print(f"   Formato ruim: '{bad_theme}' → {prompt_engineering.validate_prompt_format(bad_theme)}")
        
        # 7. Resumo final
        print("\n" + "=" * 70)
        print("🎉 DEMO SIMULADO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        
        print("📋 Resumo das Funcionalidades Demonstradas:")
        print("✅ Sistema de prompt engineering especializado")
        print("✅ Geração de tema único com qualidade")
        print("✅ Geração múltipla com seleção inteligente")
        print("✅ Sistema de análise e métricas detalhadas")
        print("✅ Sistema de salvamento/carregamento")
        print("✅ Validação de formato e qualidade")
        print("✅ Rate limiting e error handling")
        print("✅ Logging estruturado")
        
        print(f"\n🔧 Arquivos Gerados:")
        print(f"   • {filepath}")
        
        print(f"\n🎯 Próximo Passo:")
        print("   Sistema de Testes e Validação Completa")
        print("   • Testes unitários abrangentes")
        print("   • Benchmark de performance")
        print("   • Testes de integração")
        
        print(f"\n💡 Status Atual:")
        print("   🟢 Base sólida implementada")
        print("   🟢 Prompt engineering funcional")
        print("   🟢 Validação de qualidade ativa")
        print("   🟡 Pronto para uso com API key real")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no demo simulado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_theme_generation()
    sys.exit(0 if success else 1)