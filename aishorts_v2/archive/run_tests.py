#!/usr/bin/env python3
"""
Executador Principal de Testes - AiShorts v2.0

Este script executa todos os testes do sistema de forma organizada:
- Testes unitários (rápidos)
- Testes de integração (API key necessária)
- Benchmarks de performance
- Validação de qualidade

Uso:
    python run_tests.py --unit          # Apenas testes unitários
    python run_tests.py --integration   # Apenas testes de integração  
    python run_tests.py --benchmark     # Apenas benchmarks
    python run_tests.py --quality       # Apenas validação de qualidade
    python run_tests.py --all           # Todos os testes
    python run_tests.py --help          # Mostrar ajuda
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Adicionar diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """Executor principal de testes."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_dir = self.project_root / "tests"
        self.results_dir = self.project_root / "data" / "test_results"
        self.results_dir.mkdir(exist_ok=True)
    
    def run_command(self, command, description):
        """Executa comando e retorna resultado."""
        print(f"\n{'='*60}")
        print(f"🔄 {description}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            # Exibir saída
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            success = result.returncode == 0
            status = "✅ SUCESSO" if success else "❌ FALHOU"
            print(f"\n{status} - {description}")
            
            return success, result
            
        except subprocess.TimeoutExpired:
            print(f"\n⏰ TIMEOUT - {description}")
            return False, None
        except Exception as e:
            print(f"\n💥 ERRO - {description}: {e}")
            return False, None
    
    def run_unit_tests(self):
        """Executa testes unitários."""
        print("\n🧪 EXECUTANDO TESTES UNITÁRIOS")
        print("Estes testes são rápidos e não requerem API key")
        
        command = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-v",
            "-m", "unit",
            "--tb=short"
        ]
        
        return self.run_command(command, "Testes Unitários")
    
    def run_integration_tests(self):
        """Executa testes de integração."""
        print("\n🔗 EXECUTANDO TESTES DE INTEGRAÇÃO")
        print("Estes testes requerem OPENROUTER_API_KEY configurada")
        
        # Verificar se API key está configurada
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("⚠️  OPENROUTER_API_KEY não encontrada!")
            print("   Configure a variável de ambiente ou arquivo .env")
            print("   Pulando testes de integração...")
            return True  # Não falhar por isso
        
        command = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_integration.py"),
            "-v",
            "-m", "integration",
            "--tb=short"
        ]
        
        return self.run_command(command, "Testes de Integração")
    
    def run_benchmark_tests(self):
        """Executa testes de benchmark."""
        print("\n📊 EXECUTANDO BENCHMARKS DE PERFORMANCE")
        print("Estes testes medem performance e podem ser mais lentos")
        
        command = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_benchmarks.py"),
            "-v",
            "-m", "benchmark",
            "--tb=short"
        ]
        
        return self.run_command(command, "Benchmarks de Performance")
    
    def run_quality_tests(self):
        """Executa testes de validação de qualidade."""
        print("\n⭐ EXECUTANDO VALIDAÇÃO DE QUALIDADE")
        print("Estes testes avaliam a qualidade dos temas gerados")
        
        command = [
            "python", "-m", "pytest",
            str(self.test_dir / "test_quality_validation.py"),
            "-v",
            "-m", "quality",
            "--tb=short"
        ]
        
        return self.run_command(command, "Validação de Qualidade")
    
    def run_all_tests(self):
        """Executa todos os testes."""
        print("\n🚀 EXECUTANDO TODOS OS TESTES")
        print("Esto pode levar alguns minutos...")
        
        # Executar testes na ordem de velocidade
        results = {}
        
        # 1. Testes unitários (sempre)
        results['unit'] = self.run_unit_tests()
        
        # 2. Testes de qualidade (sempre)
        results['quality'] = self.run_quality_tests()
        
        # 3. Benchmarks (opcional, se não demorar muito)
        print("\n💡 Executando benchmarks básicos...")
        results['benchmark'] = self.run_benchmark_tests()
        
        # 4. Testes de integração (opcional, se API key disponível)
        print("\n💡 Verificando API key para testes de integração...")
        results['integration'] = self.run_integration_tests()
        
        return results
    
    def generate_report(self, results):
        """Gera relatório dos resultados."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"test_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE TESTES - AiShorts v2.0\n")
            f.write("=" * 80 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Diretório: {self.project_root}\n\n")
            
            f.write("RESUMO DOS RESULTADOS:\n")
            f.write("-" * 40 + "\n")
            
            total_passed = 0
            total_tests = 0
            
            for test_name, (success, _) in results.items():
                status = "✅ PASSOU" if success else "❌ FALHOU"
                f.write(f"{test_name:15} - {status}\n")
                total_tests += 1
                if success:
                    total_passed += 1
            
            f.write(f"\nRESULTADO GERAL: {total_passed}/{total_tests} grupos passaram\n")
            
            if total_passed == total_tests:
                f.write("\n🎉 TODOS OS TESTES PASSARAM!\n")
                f.write("Sistema pronto para produção.\n")
            else:
                f.write(f"\n⚠️  {total_tests - total_passed} grupo(s) de teste falharam.\n")
                f.write("Revisar erros antes de prosseguir.\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"\n📊 Relatório salvo em: {report_file}")
        return report_file
    
    def check_dependencies(self):
        """Verifica dependências dos testes."""
        print("🔍 Verificando dependências...")
        
        # Verificar pytest
        try:
            import pytest
            print("✅ pytest disponível")
        except ImportError:
            print("❌ pytest não encontrado. Execute: pip install pytest")
            return False
        
        # Verificar psutil (para benchmarks)
        try:
            import psutil
            print("✅ psutil disponível (para benchmarks)")
        except ImportError:
            print("⚠️  psutil não encontrado. Execute: pip install psutil")
        
        # Verificar estrutura de arquivos
        required_files = [
            "src/core/openrouter_client.py",
            "src/generators/theme_generator.py",
            "src/generators/prompt_engineering.py",
            "tests/test_openrouter.py",
            "tests/test_theme_generator.py"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - arquivo não encontrado")
                return False
        
        return True
    
    def show_help(self):
        """Mostra ajuda."""
        help_text = """
🔬 AiShorts v2.0 - Sistema de Testes

Este sistema executa testes abrangentes para validar o funcionamento
e qualidade do sistema AiShorts v2.0.

CATEGORIAS DE TESTE:

📦 Testes Unitários (-m unit)
   - Validam componentes isoladamente
   - Rápidos (segundos)
   - Não requerem API key
   
🔗 Testes de Integração (-m integration)  
   - Testam componentes working together
   - Requerem OPENROUTER_API_KEY
   - Levam alguns minutos
   
📊 Benchmarks (-m benchmark)
   - Medem performance do sistema
   - Testam tempos de resposta
   - Verificam uso de memória
   
⭐ Validação de Qualidade (-m quality)
   - Avaliam qualidade dos temas gerados
   - Testam métricas de curiosidade/educação
   - Verificam consistência

OPÇÕES:

--unit          Executa apenas testes unitários
--integration   Executa apenas testes de integração  
--benchmark     Executa apenas benchmarks
--quality       Executa apenas validação de qualidade
--all           Executa todos os testes (padrão)
--help          Mostra esta ajuda

EXEMPLOS:

python run_tests.py --unit                    # Testes rápidos
python run_tests.py --all                     # Todos os testes
python run_tests.py --integration --benchmark # Integração + performance

CONFIGURAÇÃO:

Para testes de integração, configure:
export OPENROUTER_API_KEY="sua_chave_aqui"

Ou crie arquivo .env com:
OPENROUTER_API_KEY=sua_chave_aqui

RELATÓRIOS:

Resultados são salvos em: data/test_results/
Arquivo: test_report_YYYYMMDD_HHMMSS.txt
        """
        print(help_text)

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Executor de Testes AiShorts v2.0")
    parser.add_argument("--unit", action="store_true", help="Executar apenas testes unitários")
    parser.add_argument("--integration", action="store_true", help="Executar apenas testes de integração")
    parser.add_argument("--benchmark", action="store_true", help="Executar apenas benchmarks")
    parser.add_argument("--quality", action="store_true", help="Executar apenas validação de qualidade")
    parser.add_argument("--all", action="store_true", help="Executar todos os testes (padrão)")
    parser.add_argument("--help-extended", action="store_true", help="Mostrar ajuda estendida")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Mostrar ajuda estendida se solicitado
    if args.help_extended:
        runner.show_help()
        return
    
    # Verificar dependências
    if not runner.check_dependencies():
        print("\n❌ Dependências não atendidas. Corrija os problemas acima.")
        sys.exit(1)
    
    # Determinar quais testes executar
    if not any([args.unit, args.integration, args.benchmark, args.quality]):
        args.all = True  # Padrão: executar todos
    
    print("🚀 INICIANDO SISTEMA DE TESTES AiShorts v2.0")
    print(f"📁 Diretório do projeto: {runner.project_root}")
    print(f"📁 Diretório de testes: {runner.test_dir}")
    
    results = {}
    
    # Executar testes selecionados
    if args.all:
        results = runner.run_all_tests()
    else:
        if args.unit:
            results['unit'] = runner.run_unit_tests()
        if args.integration:
            results['integration'] = runner.run_integration_tests()
        if args.benchmark:
            results['benchmark'] = runner.run_benchmark_tests()
        if args.quality:
            results['quality'] = runner.run_quality_tests()
    
    # Gerar relatório
    report_file = runner.generate_report(results)
    
    # Resumo final
    total_passed = sum(1 for success, _ in results.values() if success)
    total_tests = len(results)
    
    print(f"\n{'='*60}")
    print("🏁 EXECUÇÃO DE TESTES CONCLUÍDA")
    print(f"{'='*60}")
    print(f"📊 Resultados: {total_passed}/{total_tests} grupos passaram")
    
    if total_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema AiShorts v2.0 está funcionando corretamente")
    else:
        failed_groups = [name for name, (success, _) in results.items() if not success]
        print(f"❌ Testes falharam: {', '.join(failed_groups)}")
        print("🔧 Revise os erros acima antes de prosseguir")
    
    print(f"📄 Relatório completo: {report_file}")
    
    # Exit code baseado no sucesso
    sys.exit(0 if total_passed == total_tests else 1)

if __name__ == "__main__":
    main()