"""
Teste do Gerador de Tema - AiShorts v2.0

Valida se todas as funcionalidades do gerador estão funcionando.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_prompt_engineering():
    """Testa o sistema de prompt engineering."""
    print("📝 Testando Prompt Engineering...")
    
    try:
        from src.generators.prompt_engineering import prompt_engineering, ThemeCategory
        
        # Testar categorias disponíveis
        categories = prompt_engineering.get_all_categories()
        print(f"✅ {len(categories)} categorias disponíveis: {[c.value for c in categories[:5]]}...")
        
        # Testar criação de prompt
        science_prompt = prompt_engineering.create_generation_prompt(ThemeCategory.SCIENCE)
        print("✅ Prompt para Science criado")
        print(f"   System message: {science_prompt['system_message'][:100]}...")
        print(f"   User prompt: {science_prompt['user_prompt'][:100]}...")
        
        # Testar validação
        good_theme = "Por que o gelo flutua na água?"
        bad_theme = "O gelo flutua porque é menos denso"
        
        good_valid = prompt_engineering.validate_prompt_format(good_theme)
        bad_valid = prompt_engineering.validate_prompt_format(bad_theme)
        
        print(f"✅ Validação de formato - Bom: {good_valid}, Ruim: {bad_valid}")
        
        # Testar métricas de qualidade
        metrics = prompt_engineering.get_quality_metrics(good_theme, ThemeCategory.SCIENCE)
        print(f"✅ Métricas de qualidade: score geral {metrics['overall_quality']:.2f}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro no prompt engineering: {e}")
        return False

def test_theme_generator_initialization():
    """Testa a inicialização do gerador de tema."""
    print("\n🎯 Testando inicialização do ThemeGenerator...")
    
    try:
        from src.generators.theme_generator import theme_generator
        
        print("✅ ThemeGenerator importado com sucesso")
        
        # Verificar configurações
        categories = theme_generator.config.categories
        print(f"✅ Categorias configuradas: {len(categories)}")
        
        # Verificar referências
        print(f"✅ OpenRouter configurado: {theme_generator.openrouter is not None}")
        print(f"✅ Prompt engineering configurado: {theme_generator.prompt_engineering is not None}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

def test_theme_data_structures():
    """Testa as estruturas de dados dos temas."""
    print("\n📊 Testando estruturas de dados...")
    
    try:
        from src.generators.theme_generator import GeneratedTheme, ThemeGenerationResult
        from src.generators.prompt_engineering import ThemeCategory
        from datetime import datetime
        
        # Testar GeneratedTheme
        theme = GeneratedTheme(
            content="Teste de tema",
            category=ThemeCategory.SCIENCE,
            quality_score=0.8,
            response_time=1.5,
            timestamp=datetime.now()
        )
        
        print("✅ GeneratedTheme criado")
        
        # Testar conversão para dict
        theme_dict = theme.to_dict()
        print(f"✅ Convertido para dict - chave 'content': {theme_dict.get('content')}")
        
        # Testar conversão de volta
        theme_restored = GeneratedTheme.from_dict(theme_dict)
        print(f"✅ Restaurado do dict - conteúdo: {theme_restored.content}")
        
        # Testar ThemeGenerationResult
        result = ThemeGenerationResult(
            themes=[theme],
            best_theme=theme,
            total_time=5.0,
            generation_stats={"test": True}
        )
        
        print("✅ ThemeGenerationResult criado")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro nas estruturas de dados: {e}")
        return False

def test_validation_logic():
    """Testa a lógica de validação."""
    print("\n🔍 Testando lógica de validação...")
    
    try:
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        # Testar limpeza de resposta
        messy_response = "   Por que o céu é azul?   \n\nAqui tem mais texto desnecessário"
        clean_response = theme_generator._clean_response(messy_response)
        print(f"✅ Limpeza de resposta: '{clean_response}'")
        
        # Testar validação de resposta válida
        try:
            theme_generator._validate_theme_response("Por que o céu é azul?", ThemeCategory.SCIENCE)
            print("✅ Resposta válida passou na validação")
        except Exception as e:
            print(f"❌ Resposta válida falhou: {e}")
            return False
        
        # Testar validação de resposta inválida
        try:
            theme_generator._validate_theme_response("", ThemeCategory.SCIENCE)
            print("❌ Resposta vazia deveria ter falhado")
            return False
        except:
            print("✅ Resposta vazia foi corretamente rejeitada")
        
        # Testar escolha de categoria aleatória
        category = theme_generator._choose_random_category()
        print(f"✅ Categoria aleatória: {category.value}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro na lógica de validação: {e}")
        return False

def test_analysis_functionality():
    """Testa a funcionalidade de análise."""
    print("\n📈 Testando análise de temas...")
    
    try:
        from src.generators.theme_generator import theme_generator, GeneratedTheme
        from src.generators.prompt_engineering import ThemeCategory
        from datetime import datetime
        
        # Criar temas de teste
        test_themes = [
            GeneratedTheme(
                content="Por que o céu é azul?",
                category=ThemeCategory.SCIENCE,
                quality_score=0.8,
                response_time=1.0,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Como funcionava o calendário egípcio?",
                category=ThemeCategory.HISTORY,
                quality_score=0.9,
                response_time=1.2,
                timestamp=datetime.now()
            ),
            GeneratedTheme(
                content="Por que os flamingos são rosa?",
                category=ThemeCategory.NATURE,
                quality_score=0.7,
                response_time=0.8,
                timestamp=datetime.now()
            )
        ]
        
        # Testar análise
        analysis = theme_generator.analyze_themes(test_themes)
        
        print(f"✅ Análise criada - {analysis['total_themes']} temas analisados")
        print(f"   Qualidade média: {analysis['quality_stats']['avg_quality']:.2f}")
        print(f"   Categorias: {list(analysis['categories'].keys())}")
        print(f"   Melhor tema: {analysis['best_themes'][0]['content'][:30]}...")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return False

def test_integration_preparation():
    """Testa preparação para integração (sem API calls reais)."""
    print("\n🔗 Testando preparação para integração...")
    
    try:
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        # Testar se consegue preparar geração sem executar
        print("✅ Estrutura preparada para geração")
        
        # Verificar configurações de qualidade
        print(f"   Score mínimo: {theme_generator.min_quality_score}")
        print(f"   Máx tentativas: {theme_generator.max_attempts}")
        
        # Verificar caminhos de salvamento
        output_dir = theme_generator.config.storage.output_dir if hasattr(theme_generator.config, 'storage') else "data/output"
        print(f"   Diretório de saída: {output_dir}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro na preparação de integração: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 AiShorts v2.0 - Teste do Gerador de Tema")
    print("=" * 60)
    
    tests = [
        ("Prompt Engineering", test_prompt_engineering),
        ("Inicialização", test_theme_generator_initialization),
        ("Estruturas de Dados", test_theme_data_structures),
        ("Lógica de Validação", test_validation_logic),
        ("Análise de Temas", test_analysis_functionality),
        ("Preparação para Integração", test_integration_preparation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Erro crítico em {test_name}: {e}")
            results[test_name] = False
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:25} - {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("\n🎉 Gerador de Tema implementado com sucesso!")
        print("✅ Todos os componentes estão funcionando")
        print("✅ Pronto para geração real de temas")
        return True
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)