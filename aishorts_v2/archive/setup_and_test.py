#!/usr/bin/env python3
"""
Setup e Execução de Testes - AiShorts v2.0

Este script instala dependências de teste e executa o sistema completo
de testes para validar o funcionamento do AiShorts v2.0.

Uso:
    python setup_and_test.py    # Instala dependências e executa testes
    python setup_and_test.py --unit-only    # Apenas testes unitários
"""

import sys
import subprocess
import argparse
from pathlib import Path

def install_dependencies():
    """Instala dependências necessárias para testes."""
    print("📦 Instalando dependências de teste...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt não encontrado!")
        return False
    
    try:
        # Instalar dependências
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso!")
            return True
        else:
            print("❌ Erro na instalação:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar pip: {e}")
        return False

def run_tests(test_type="all"):
    """Executa os testes."""
    print(f"🧪 Executando testes ({test_type})...")
    
    script_path = Path(__file__).parent / "run_tests.py"
    
    if not script_path.exists():
        print("❌ run_tests.py não encontrado!")
        return False
    
    # Construir comando
    command = [sys.executable, str(script_path)]
    
    if test_type == "unit":
        command.append("--unit")
    elif test_type == "integration":
        command.append("--integration")
    elif test_type == "benchmark":
        command.append("--benchmark")
    elif test_type == "quality":
        command.append("--quality")
    else:  # all
        command.append("--all")
    
    try:
        # Executar testes
        result = subprocess.run(command)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def check_environment():
    """Verifica se o ambiente está pronto."""
    print("🔍 Verificando ambiente...")
    
    # Verificar se está no diretório correto
    current_dir = Path.cwd()
    project_file = current_dir / "aishorts_v2" / "__init__.py"
    
    if not project_file.exists():
        print("❌ Execute este script no diretório raiz do projeto AiShorts v2.0")
        return False
    
    print("✅ Diretório do projeto correto")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python 3.8+ necessário, atual: {python_version.major}.{python_version.minor}")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar pip
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pip disponível")
        else:
            print("❌ pip não disponível")
            return False
    except:
        print("❌ pip não disponível")
        return False
    
    return True

def show_summary():
    """Mostra resumo do sistema de testes."""
    print("""
🎯 SISTEMA DE TESTES AiShorts v2.0 - RESUMO
═══════════════════════════════════════════════════════════════

Este sistema executa testes abrangentes para validar:

📦 TESTES UNITÁRIOS (--unit)
   ✓ Cliente OpenRouter
   ✓ Gerador de temas
   ✓ Prompt engineering
   ✓ Estruturas de dados
   ✓ Sistema de configurações
   ✓ Tratamento de erros
   → Rápidos (segundos), sem API key necessária

🔗 TESTES DE INTEGRAÇÃO (--integration)
   ✓ Geração completa de temas
   ✓ Integração com API OpenRouter
   ✓ Workflow end-to-end
   ✓ Recuperação de erros
   → Requerem OPENROUTER_API_KEY configurada

📊 BENCHMARKS (--benchmark)
   ✓ Tempo de geração de temas
   ✓ Performance da API
   ✓ Uso de memória
   ✓ Testes de concorrência
   → Medem performance do sistema

⭐ VALIDAÇÃO DE QUALIDADE (--quality)
   ✓ Medição de curiosidade
   ✓ Valor educacional
   ✓ Consistência de métricas
   ✓ Thresholds de qualidade
   → Avaliam qualidade dos temas gerados

🚀 EXECUÇÃO COMPLETA (--all)
   Executa todos os testes na ordem otimizada

📄 RELATÓRIOS
   Resultados salvos em: data/test_results/
   Arquivo: test_report_YYYYMMDD_HHMMSS.txt

⚙️ CONFIGURAÇÃO NECESSÁRIA
   Para testes de integração:
   export OPENROUTER_API_KEY="sua_chave_aqui"
   
   Ou arquivo .env:
   OPENROUTER_API_KEY=sua_chave_aqui

═══════════════════════════════════════════════════════════════
""")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Setup e Testes AiShorts v2.0")
    parser.add_argument("--unit-only", action="store_true", 
                       help="Apenas testes unitários (rápido)")
    parser.add_argument("--skip-install", action="store_true",
                       help="Pular instalação de dependências")
    parser.add_argument("--help-summary", action="store_true",
                       help="Mostrar resumo do sistema de testes")
    
    args = parser.parse_args()
    
    if args.help_summary:
        show_summary()
        return
    
    print("🚀 AiShorts v2.0 - Setup e Sistema de Testes")
    print("=" * 60)
    
    # Verificar ambiente
    if not check_environment():
        sys.exit(1)
    
    # Instalar dependências
    if not args.skip_install:
        if not install_dependencies():
            print("❌ Falha na instalação. Corrija os erros e tente novamente.")
            sys.exit(1)
    
    # Determinar tipo de teste
    test_type = "all"
    if args.unit_only:
        test_type = "unit"
    
    # Executar testes
    print(f"\n🎯 Iniciando execução: {test_type.upper()}")
    success = run_tests(test_type)
    
    if success:
        print("\n🎉 Execução concluída com sucesso!")
        print("✅ Sistema AiShorts v2.0 validado")
    else:
        print("\n❌ Execução falhou!")
        print("🔧 Revise os erros acima")
        sys.exit(1)

if __name__ == "__main__":
    main()