#!/usr/bin/env python3
"""
Demo do Gerador de Tema - AiShorts v2.0

Exemplo prático demonstrando o funcionamento completo do gerador de tema.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("=" * 70)
    print("🚀 AiShorts v2.0 - Demo do Gerador de Tema")
    print("=" * 70)
    
    try:
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        # 1. Verificar configuração
        print("📋 Configuração Atual:")
        model_info = theme_generator.openrouter.get_model_info()
        print(f"   Modelo: {model_info['model']}")
        print(f"   Max Tokens: {model_info['max_tokens']}")
        print(f"   Temperatura: {model_info['temperature']}")
        print(f"   Categorias: {len(theme_generator.config.categories)}")
        
        # 2. Teste de geração única
        print("\n🎯 DEMO 1: Geração de Tema Único")
        print("-" * 50)
        
        print("Gerando tema sobre CIÊNCIA...")
        theme = theme_generator.generate_single_theme(ThemeCategory.SCIENCE)
        
        print(f"📝 Tema: {theme.content}")
        print(f"⭐ Qualidade: {theme.quality_score:.2f}/1.0")
        print(f"⏱️ Tempo: {theme.response_time:.2f}s")
        print(f"🗂️ Categoria: {theme.category.value}")
        
        if theme.usage:
            print(f"🔢 Tokens: {theme.usage}")
        
        # 3. Teste de geração múltipla (sem API real para não gastar créditos)
        print("\n🎲 DEMO 2: Preparação para Geração Múltipla")
        print("-" * 50)
        
        print("Demonstrando lógica de geração múltipla...")
        print("(Sem fazer chamadas reais à API para preservar créditos)")
        
        # Simular processo de geração múltipla
        categories_demo = [ThemeCategory.SCIENCE, ThemeCategory.HISTORY, ThemeCategory.NATURE]
        
        print(f"📊 Estratégia:")
        print(f"   - Categorias: {[c.value for c in categories_demo]}")
        print(f"   - Quantidade alvo: 5 temas")
        print(f"   - Score mínimo: {theme_generator.min_quality_score}")
        print(f"   - Máx tentativas: {theme_generator.max_attempts}")
        
        # 4. Demonstração de análise
        print("\n📈 DEMO 3: Sistema de Análise")
        print("-" * 50)
        
        # Criar temas de exemplo para análise
        from datetime import datetime
        from src.generators.theme_generator import GeneratedTheme
        
        sample_themes = [
            GeneratedTheme(
                content="Por que o céu muda de cor ao entardecer?",
                category=ThemeCategory.SCIENCE,
                quality_score=0.85,
                response_time=1.2,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Como funcionava a navegação sem GPS no século XV?",
                category=ThemeCategory.HISTORY,
                quality_score=0.90,
                response_time=1.5,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Por que os flamingos são rosa?",
                category=ThemeCategory.NATURE,
                quality_score=0.75,
                response_time=1.0,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Como os golfinhos se comunicam debaixo d'água?",
                category=ThemeCategory.ANIMALS,
                quality_score=0.88,
                response_time=1.3,
                timestamp=datetime.now()
            )
        ]
        
        # Analisar temas
        analysis = theme_generator.analyze_themes(sample_themes)
        
        print("📊 Análise dos Temas:")
        print(f"   Total analisados: {analysis['total_themes']}")
        print(f"   Qualidade média: {analysis['quality_stats']['avg_quality']:.2f}")
        print(f"   Tempo médio: {analysis['performance_stats']['avg_time']:.2f}s")
        
        print("\n🏆 Melhores Temas:")
        for i, best_theme in enumerate(analysis['best_themes'], 1):
            print(f"   {i}. {best_theme['content'][:50]}...")
            print(f"      Score: {best_theme['quality_score']:.2f} | Categoria: {best_theme['category']}")
        
        print("\n📂 Categorias Representadas:")
        for category, data in analysis['categories'].items():
            print(f"   {category}: {data['count']} temas (qualidade média: {data['avg_quality']:.2f})")
        
        # 5. Demonstração de salvamento
        print("\n💾 DEMO 4: Sistema de Salvamento")
        print("-" * 50)
        
        from src.generators.theme_generator import ThemeGenerationResult
        
        # Simular resultado de geração
        demo_result = ThemeGenerationResult(
            themes=sample_themes,
            best_theme=max(sample_themes, key=lambda t: t.quality_score),
            total_time=5.8,
            generation_stats={
                "total_attempts": 6,
                "successful_generations": 4,
                "failed_generations": 2,
                "categories_used": [c.value for c in [ThemeCategory.SCIENCE, ThemeCategory.HISTORY, ThemeCategory.NATURE, ThemeCategory.ANIMALS]],
                "avg_quality_score": 0.845
            }
        )
        
        # Salvar resultado
        filepath = theme_generator.save_generation_result(demo_result, "demo_theme_generation.json")
        print(f"✅ Resultado salvo em: {filepath}")
        
        # Carregar e verificar
        loaded_result = ThemeGenerationResult.load_from_file(filepath)
        print(f"✅ Resultado carregado: {len(loaded_result.themes)} temas")
        
        # 6. Exemplo de uso prático
        print("\n🎯 DEMO 5: Exemplos de Uso Prático")
        print("-" * 50)
        
        print("💡 Como usar o gerador em produção:")
        print("""
# Importar o gerador
from src.generators.theme_generator import theme_generator

# Gerar um tema específico
theme = theme_generator.generate_single_theme(ThemeCategory.SCIENCE)
print(f"Tema: {theme.content}")

# Gerar múltiplos temas
result = theme_generator.generate_multiple_themes(count=5)
print(f"Melhor tema: {result.best_theme.content}")

# Salvar resultados
theme_generator.save_generation_result(result, "temas_hoje.json")

# Analisar qualidade
analysis = theme_generator.analyze_themes(result.themes)
print(f"Qualidade média: {analysis['quality_stats']['avg_quality']:.2f}")
""")
        
        print("\n" + "=" * 70)
        print("🎉 DEMO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        
        print("📋 Resumo do que foi demonstrado:")
        print("✅ Geração de tema único")
        print("✅ Sistema de prompt engineering")
        print("✅ Validação e métricas de qualidade")
        print("✅ Análise de múltiplos temas")
        print("✅ Sistema de salvamento/carregamento")
        print("✅ Exemplos de uso prático")
        
        print(f"\n🔧 Próximo passo: Sistema de Testes e Validação")
        print(f"📁 Resultados salvos em: {filepath}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)