#!/usr/bin/env python3
"""
Test Runner - Executa todos os testes do AiShortsV2
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """Executa um comando e retorna o resultado."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print("⚠️ ERROS:")
        print(result.stderr)
    
    return result.returncode == 0


def main():
    """Função principal."""
    print("=" * 70)
    print("🎬 AISHORTS V2.0 - TEST RUNNER")
    print("=" * 70)
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mudar para diretório raiz
    root_dir = Path(__file__).parent
    import os
    os.chdir(root_dir)
    
    results = []
    
    # 1. Testes unitários dos helpers LLM
    results.append((
        run_command(
            "python -m pytest tests/unit/test_llm_helpers.py -v",
            "Testes Unitários - LLMHelpers"
        ),
        "LLMHelpers"
    ))
    
    # 2. Testes unitários do ContentGenerationService
    results.append((
        run_command(
            "python -m pytest tests/unit/test_content_generation_service.py -v",
            "Testes Unitários - ContentGenerationService"
        ),
        "ContentGenerationService"
    ))
    
    # 3. Testes unitários do MediaAcquisitionService
    results.append((
        run_command(
            "python -m pytest tests/unit/test_media_acquisition_service.py -v",
            "Testes Unitários - MediaAcquisitionService"
        ),
        "MediaAcquisitionService"
    ))
    
    # 4. Testes de integração das LLMs
    results.append((
        run_command(
            "python test_llm_integrations.py",
            "Testes de Integração - LLM"
        ),
        "Integrações LLM"
    ))
    
    # 5. Testes existentes do TTS
    results.append((
        run_command(
            "python -m pytest tests/test_kokoro_tts.py -v",
            "Testes - TTS Kokoro"
        ),
        "TTS Kokoro"
    ))
    
    # 6. Testes de vídeo
    results.append((
        run_command(
            "python -m pytest tests/test_video/ -v",
            "Testes - Módulo de Vídeo"
        ),
        "Módulo de Vídeo"
    ))
    
    # Resumo dos resultados
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    
    passed = sum(1 for success, _ in results if success)
    total = len(results)
    
    for success, name in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"   {status:<10} {name}")
    
    print(f"\n📈 Total: {passed}/{total} testes passaram")
    
    # Estatísticas detalhadas
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ Pipeline validado e pronto para uso")
        print("\n🚀 Para executar o pipeline completo:")
        print("   python main.py")
        print("   python cli_refactored.py technology")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam. Verifique os erros acima.")
        
        # Sugerir próximos passos
        print("\n🔧 Sugestões:")
        print("   1. Verifique se as dependências estão instaladas")
        print("   2. Configure as variáveis de ambiente no .env")
        print("   3. Execute os testes individualmente para debugar")
        print("   4. Verifique se os arquivos de teste estão corretos")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())