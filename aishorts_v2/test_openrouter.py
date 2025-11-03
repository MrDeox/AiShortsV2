"""
Teste do Cliente OpenRouter - AiShorts v2.0

Valida se todas as funcionalidades do cliente estão funcionando.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_client_initialization():
    """Testa a inicialização do cliente."""
    print("🔍 Testando inicialização do cliente...")
    
    try:
        from src.core.openrouter_client import openrouter_client, OpenRouterClient
        
        print("✅ Cliente importado com sucesso")
        
        # Verificar configuração
        model_info = openrouter_client.get_model_info()
        print(f"✅ Modelo configurado: {model_info['model']}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

def test_rate_limiter():
    """Testa o sistema de rate limiting."""
    print("\n⏱️ Testando rate limiter...")
    
    try:
        from src.core.openrouter_client import RateLimiter
        
        # Teste básico
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        # Primeira requisição deve ser permitida
        if not limiter.can_make_request():
            print("❌ Rate limiter bloqueou primeira requisição")
            return False
        
        print("✅ Rate limiter permite primeira requisição")
        
        # Adicionar algumas requisições
        for i in range(3):
            limiter.add_request()
            if i < 4 and not limiter.can_make_request():
                print(f"❌ Rate limiter bloqueou requisição {i+1}")
                return False
        
        print("✅ Rate limiter permite múltiplas requisições")
        
        # Testar bloqueamento
        for i in range(2):
            limiter.add_request()  # Agora deve ter 5
        
        if limiter.can_make_request():
            print("❌ Rate limiter não bloqueou após limite atingido")
            return False
        
        print("✅ Rate limiter bloqueia após limite atingido")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro no teste do rate limiter: {e}")
        return False

def test_error_handling():
    """Testa o sistema de tratamento de erros."""
    print("\n🚨 Testando tratamento de erros...")
    
    try:
        from src.utils.exceptions import OpenRouterError, RateLimitError, ErrorHandler
        
        # Teste de exceção customizada
        try:
            raise OpenRouterError("Teste de erro", status_code=500)
        except OpenRouterError as e:
            error_info = ErrorHandler.handle_error(e, "teste_openrouter")
            if error_info["error_code"] != "OPENROUTER_ERROR":
                print("❌ Exceção OpenRouter não processada corretamente")
                return False
        
        print("✅ Exceções OpenRouter processadas corretamente")
        
        # Teste de rate limit
        try:
            raise RateLimitError("Teste de rate limit", wait_time=2.5)
        except RateLimitError as e:
            error_info = ErrorHandler.handle_error(e, "teste_rate_limit")
            if error_info["error_code"] != "RATE_LIMIT_ERROR":
                print("❌ Exceção RateLimit não processada corretamente")
                return False
        
        print("✅ Exceções RateLimit processadas corretamente")
        
        # Teste de execução segura
        def funcao_com_erro():
            raise ValueError("Teste")
        
        result = ErrorHandler.safe_execute(
            funcao_com_erro,
            fallback_return="tratado",
            context="teste_seguranca"
        )
        
        if result != "tratado":
            print("❌ Execução segura não funcionou")
            return False
        
        print("✅ Execução segura funcionando")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro no teste de erros: {e}")
        return False

def test_api_structure():
    """Testa a estrutura da API (sem fazer requisições reais)."""
    print("\n🔧 Testando estrutura da API...")
    
    try:
        from src.core.openrouter_client import OpenRouterClient
        
        # Testar criação de instância
        client = OpenRouterClient()
        print("✅ Cliente pode ser instanciado")
        
        # Testar informações do modelo
        model_info = client.get_model_info()
        required_fields = ["model", "base_url", "max_tokens", "temperature"]
        
        for field in required_fields:
            if field not in model_info:
                print(f"❌ Campo {field} ausente nas informações do modelo")
                return False
        
        print("✅ Informações do modelo completas")
        
        # Verificar configuração
        from src.config.settings import config
        
        if client.config.model != config.openrouter.model:
            print("❌ Configuração do cliente não coincide com settings")
            return False
        
        print("✅ Configurações sincronizadas")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro no teste da API: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🔬 AiShorts v2.0 - Teste do Cliente OpenRouter")
    print("=" * 60)
    
    tests = [
        ("Inicialização", test_client_initialization),
        ("Rate Limiter", test_rate_limiter),
        ("Tratamento de Erros", test_error_handling),
        ("Estrutura da API", test_api_structure)
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
        print(f"{test_name:20} - {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("\n🎉 Cliente OpenRouter implementado com sucesso!")
        print("✅ Próximo passo: Desenvolver Gerador de Tema")
        return True
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)