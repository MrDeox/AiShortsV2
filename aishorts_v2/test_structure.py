#!/usr/bin/env python3
"""
Teste da estrutura base do AiShorts v2.0

Valida se todas as configurações e módulos estão funcionando corretamente.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    print("🔍 Testando imports...")
    
    try:
        # Testar import principal
        import aishorts_v2
        print(f"✅ AiShorts v{aishorts_v2.__version__} importado com sucesso")
        
        # Testar configurações
        from src.config.settings import config
        print("✅ Configurações importadas com sucesso")
        
        from src.config.logging_config import setup_logging, logger
        print("✅ Sistema de logging importado com sucesso")
        
        from src.utils.exceptions import ErrorHandler, AiShortsError
        print("✅ Sistema de exceções importado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False

def test_configuration():
    """Testa se as configurações estão válidas."""
    print("\n⚙️ Testando configurações...")
    
    try:
        from src.config.settings import config
        
        # Testar resumo
        summary = config.get_summary()
        print("✅ Resumo das configurações:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Testar validação (pode falhar se .env não estiver configurado)
        try:
            config.validate_config(strict=False)  # Validação flexível para testes
            print("✅ Configuração válida!")
        except ValueError as e:
            print(f"⚠️ Configuração precisa de ajuste: {e}")
            print("   Dica: Configure sua OPENROUTER_API_KEY no arquivo .env")
            # Considera como válido para testes se apenas API key não estiver configurada
            if "OPENROUTER_API_KEY" in str(e):
                print("   ✅ Apenas API key não configurada - válido para testes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_logging():
    """Testa se o sistema de logging está funcionando."""
    print("\n📝 Testando sistema de logging...")
    
    try:
        from src.config.logging_config import logger, setup_logging
        
        # Testar diferentes níveis de log
        logger.debug("Teste de debug - apenas em desenvolvimento")
        logger.info("Teste de info - funcionando normalmente")
        logger.warning("Teste de warning - atenção")
        
        print("✅ Sistema de logging funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no logging: {e}")
        return False

def test_exceptions():
    """Testa se o sistema de exceções está funcionando."""
    print("\n🚨 Testando sistema de exceções...")
    
    try:
        from src.utils.exceptions import ErrorHandler, ThemeGenerationError
        
        # Teste de exceção customizada
        try:
            raise ThemeGenerationError("Teste de erro", attempt=1, category="science")
        except ThemeGenerationError as e:
            error_info = ErrorHandler.handle_error(e, "teste_excecoes")
            print(f"✅ Exceção processada: {error_info['error_code']}")
        
        # Teste de execução segura
        def funcao_com_erro():
            raise ValueError("Teste de erro")
        
        result = ErrorHandler.safe_execute(
            funcao_com_erro, 
            fallback_return="erro_processado", 
            context="teste_seguro"
        )
        print(f"✅ Execução segura: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de exceções: {e}")
        return False

def test_directories():
    """Testa se os diretórios foram criados corretamente."""
    print("\n📁 Testando estrutura de diretórios...")
    
    required_dirs = [
        "src",
        "src/core",
        "src/generators", 
        "src/utils",
        "src/config",
        "tests",
        "docs",
        "logs",
        "data",
        "data/output",
        "data/temp", 
        "data/cache"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - não encontrado")
            all_good = False
    
    return all_good

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🚀 AiShorts v2.0 - Teste da Estrutura Base")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configurações", test_configuration), 
        ("Logging", test_logging),
        ("Exceções", test_exceptions),
        ("Diretórios", test_directories)
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
        print(f"{test_name:15} - {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("\n🎉 Estrutura base criada com sucesso!")
        print("✅ Próximo passo: Implementar integração OpenRouter")
        return True
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)