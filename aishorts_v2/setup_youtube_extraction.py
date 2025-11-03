#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalação e configuração do sistema de extração do YouTube.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Verifica versão do Python."""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário. Versão atual:", 
              f"{version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_python_packages():
    """Instala pacotes Python necessários."""
    print("\n📦 Instalando pacotes Python...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Pacotes Python instalados com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação dos pacotes: {e}")
        return False


def check_ffmpeg():
    """Verifica se FFmpeg está instalado."""
    print("\n🎬 Verificando FFmpeg...")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            # Extrair versão
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg encontrado: {version_line}")
            return True
        else:
            print("❌ FFmpeg não está funcionando corretamente")
            return False
            
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        print("❌ FFmpeg não encontrado no sistema")
        return False


def install_ffmpeg_instructions():
    """Mostra instruções para instalar FFmpeg."""
    print("\n📋 INSTRUÇÕES PARA INSTALAR FFMPEG:")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("Windows:")
        print("1. Baixe FFmpeg de: https://ffmpeg.org/download.html")
        print("2. Extraia o arquivo em: C:\\ffmpeg")
        print("3. Adicione C:\\ffmpeg\\bin ao PATH do sistema")
        print("4. Reinicie o terminal/IDE")
        
    elif system == "darwin":  # macOS
        print("macOS (usando Homebrew):")
        print("brew install ffmpeg")
        print("\nOu baixe de: https://ffmpeg.org/download.html")
        
    else:  # Linux
        print("Ubuntu/Debian:")
        print("sudo apt update && sudo apt install ffmpeg")
        print("\nCentOS/RHEL/Fedora:")
        print("sudo dnf install ffmpeg")
        print("  ou")
        print("sudo yum install ffmpeg")
        
        print("\nOu baixe de: https://ffmpeg.org/download.html")
    
    print("\nDepois de instalar, execute este script novamente para verificar.")


def create_directories():
    """Cria diretórios necessários."""
    print("\n📁 Criando diretórios...")
    
    dirs_to_create = [
        "outputs/video",
        "data/temp",
        "logs"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")
    
    return True


def test_installation():
    """Testa a instalação."""
    print("\n🧪 Testando instalação...")
    
    try:
        # Teste de importação
        print("Testando importações...")
        
        import yt_dlp
        print("✅ yt-dlp importado com sucesso")
        
        import ffmpeg
        print("✅ ffmpeg-python importado com sucesso")
        
        # Teste dos módulos customizados
        sys.path.append('src')
        
        from video.extractors.youtube_extractor import YouTubeExtractor
        from video.extractors.segment_processor import SegmentProcessor
        print("✅ Módulos customizados importados com sucesso")
        
        # Teste de inicialização
        print("\nTestando inicialização dos componentes...")
        
        extractor = YouTubeExtractor()
        processor = SegmentProcessor()
        
        print("✅ YouTubeExtractor inicializado")
        print("✅ SegmentProcessor inicializado")
        
        print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\nVocê pode agora:")
        print("1. Executar: python demo_youtube_extraction.py")
        print("2. Executar testes: pytest tests/test_video/test_extractors.py -v")
        print("3. Importar no seu código:")
        print("   from src.video import YouTubeExtractor, SegmentProcessor")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        print("\nVerifique se todas as dependências foram instaladas corretamente.")
        return False


def run_tests():
    """Executa os testes."""
    print("\n🧪 Executando testes...")
    
    try:
        subprocess.check_call([
            "pytest", 
            "tests/test_video/test_extractors.py", 
            "-v"
        ])
        print("✅ Todos os testes passaram!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Alguns testes falharam: {e}")
        return False


def main():
    """Função principal de instalação."""
    print("🚀 INSTALAÇÃO DO SISTEMA DE EXTRAÇÃO DO YOUTUBE")
    print("=" * 55)
    
    # Verificações e instalação
    steps = [
        ("Verificando Python", check_python_version),
        ("Instalando pacotes Python", install_python_packages),
        ("Verificando FFmpeg", check_ffmpeg),
        ("Criando diretórios", create_directories),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            if step_name == "Verificando FFmpeg":
                install_ffmpeg_instructions()
            print(f"\n❌ Falha na etapa: {step_name}")
            print("Instale as dependências em falta e execute novamente.")
            sys.exit(1)
    
    # Teste final
    if test_installation():
        print("\n❓ Deseja executar os testes também? (y/n): ", end="")
        
        try:
            if input().lower().startswith('y'):
                run_tests()
        except (EOFError, KeyboardInterrupt):
            pass
        
        print("\n✅ Instalação finalizada!")
    else:
        print("\n❌ Instalação falhou!")
        sys.exit(1)


if __name__ == "__main__":
    main()