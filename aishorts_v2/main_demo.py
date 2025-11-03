#!/usr/bin/env python3
"""
AiShorts v2.0 - Demo Principal do Gerador de Tema

Demo principal demonstrando o funcionamento completo do sistema.
Este demo usa a API OpenRouter real para gerar temas de qualidade.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("=" * 70)
    print("🚀 AiShorts v2.0 - Demo Principal do Gerador de Tema")
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
        
        # 3. Teste de geração múltipla real
        print("\n🎲 DEMO 2: Geração Múltipla")
        print("-" * 50)
        
        print("Gerando múltiplos temas...")
        result = theme_generator.generate_multiple_themes(count=3, min_quality_score=0.6)
        
        print(f"📊 Resultado da Geração Múltipla:")
        print(f"   Total tentado: {result.generation_stats['total_attempts']}")
        print(f"   Sucessos: {result.generation_stats['successful_generations']}")
        print(f"   Qualidade média: {result.generation_stats['avg_quality_score']:.2f}")
        
        if result.best_theme:
            print(f"\n🏆 Melhor tema gerado:")
            print(f"   Tema: {result.best_theme.content}")
            print(f"   Qualidade: {result.best_theme.quality_score:.2f}")
            print(f"   Categoria: {result.best_theme.category.value}")
        
        # 4. Salvar resultado
        print("\n💾 DEMO 3: Sistema de Salvamento")
        print("-" * 50)
        
        filepath = theme_generator.save_generation_result(result, "main_demo_result.json")
        print(f"✅ Resultado salvo em: {filepath}")
        
        # 5. Analisar temas gerados
        print("\n📈 DEMO 4: Sistema de Análise")
        print("-" * 50)
        
        analysis = theme_generator.analyze_themes(result.themes)
        print("📊 Análise dos Temas Gerados:")
        print(f"   Total analisados: {analysis['total_themes']}")
        print(f"   Qualidade média: {analysis['quality_stats']['avg_quality']:.2f}")
        print(f"   Tempo médio: {analysis['performance_stats']['avg_time']:.2f}s")
        
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
        print("✅ Geração de tema único com API real")
        print("✅ Geração múltipla com seleção inteligente")
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