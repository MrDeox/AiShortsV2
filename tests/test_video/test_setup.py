"""
Teste simplificado do setup técnico do módulo de vídeo
Fase 1 - Setup técnico do Módulo 8
"""

import os
import sys
import tempfile
from pathlib import Path

# Adicionar diretórios ao path
sys.path.insert(0, '/workspace/src')
sys.path.insert(0, '/workspace')

def test_basic_setup():
    """Testa o setup básico do módulo."""
    print("=" * 60)
    print("TESTE DE SETUP TÉCNICO - MÓDULO DE VÍDEO")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Teste 1: Estrutura de pastas
    total_tests += 1
    print("\n1. Verificando estrutura de pastas...")
    
    expected_dirs = [
        "/workspace/src/video",
        "/workspace/src/video/extractors",
        "/workspace/src/video/matching", 
        "/workspace/src/video/processing",
        "/workspace/src/video/generators",
        "/workspace/tests/test_video",
        "/workspace/config"
    ]
    
    dirs_ok = True
    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            print(f"   ✓ {dir_path}")
        else:
            print(f"   ✗ {dir_path} - NÃO ENCONTRADO")
            dirs_ok = False
    
    if dirs_ok:
        success_count += 1
        print("   ✓ Estrutura de pastas OK")
    else:
        print("   ✗ Estrutura de pastas com problemas")
    
    # Teste 2: Arquivos Python criados
    total_tests += 1
    print("\n2. Verificando arquivos Python...")
    
    expected_files = [
        "/workspace/src/video/__init__.py",
        "/workspace/src/video/extractors/__init__.py",
        "/workspace/src/video/extractors/youtube_extractor.py",
        "/workspace/src/video/matching/__init__.py",
        "/workspace/src/video/matching/content_matcher.py",
        "/workspace/src/video/processing/__init__.py",
        "/workspace/src/video/processing/video_processor.py",
        "/workspace/src/video/generators/__init__.py",
        "/workspace/src/video/generators/video_generator.py",
        "/workspace/tests/test_video/__init__.py",
        "/workspace/config/__init__.py",
        "/workspace/config/video_settings.py",
        "/workspace/requirements_video.txt"
    ]
    
    files_ok = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"   ✓ {Path(file_path).name}")
        else:
            print(f"   ✗ {Path(file_path).name} - NÃO ENCONTRADO")
            files_ok = False
    
    if files_ok:
        success_count += 1
        print("   ✓ Arquivos Python criados OK")
    else:
        print("   ✗ Arquivos Python com problemas")
    
    # Teste 3: Importações básicas
    total_tests += 1
    print("\n3. Testando importações básicas...")
    
    import_tests = [
        ("cv2", "opencv-python"),
        ("numpy", "numpy"),
        ("sklearn", "scikit-learn"),
        ("yt_dlp", "yt-dlp"),
        ("torch", "torch"),
        ("transformers", "transformers"),
        ("pydub", "pydub"),
    ]
    
    import_results = []
    for module_name, package_name in import_tests:
        try:
            __import__(module_name)
            print(f"   ✓ {package_name}")
            import_results.append(True)
        except ImportError as e:
            print(f"   ✗ {package_name} - {e}")
            import_results.append(False)
    
    if all(import_results):
        success_count += 1
        print("   ✓ Importações básicas OK")
    else:
        print("   ⚠ Algumas importações falharam")
    
    # Teste 4: Configurações
    total_tests += 1
    print("\n4. Testando configurações...")
    
    try:
        from config.video_settings import get_config
        config = get_config()
        
        required_keys = ['youtube', 'video_processing', 'similarity', 'generation']
        config_ok = all(key in config for key in required_keys)
        
        if config_ok:
            print("   ✓ Configurações carregadas corretamente")
            print(f"   ✓ {len(config)} seções de configuração encontradas")
            success_count += 1
        else:
            print("   ✗ Configurações incompletas")
            
    except Exception as e:
        print(f"   ✗ Erro ao carregar configurações: {e}")
    
    # Teste 5: Dependências MoviePy (importação específica)
    total_tests += 1
    print("\n5. Testando MoviePy...")
    
    try:
        import moviepy
        print(f"   ✓ MoviePy versão {moviepy.__version__}")
        
        # Testar importações específicas do MoviePy
        try:
            from moviepy.editor import VideoFileClip
            print("   ✓ MoviePy editor disponível")
            success_count += 1
        except ImportError as e:
            print(f"   ⚠ MoviePy editor: {e}")
            
    except ImportError as e:
        print(f"   ✗ MoviePy não disponível: {e}")
    
    # Teste 6: Teste básico de OpenCV
    total_tests += 1
    print("\n6. Testando funcionalidades básicas de vídeo...")
    
    try:
        import cv2
        import numpy as np
        
        # Criar vídeo de teste simples
        temp_dir = Path(tempfile.mkdtemp())
        test_video = temp_dir / "test.avi"
        
        # Criar vídeo simples
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(str(test_video), fourcc, 20.0, (640, 480))
        
        # Escrever alguns frames
        for i in range(20):
            frame = np.full((480, 640, 3), (i*12, 100, 255-i*12), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        
        # Ler informações do vídeo
        cap = cv2.VideoCapture(str(test_video))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        if width == 640 and height == 480:
            print(f"   ✓ Vídeo criado e lido: {width}x{height} @ {fps}fps")
            success_count += 1
        else:
            print(f"   ✗ Problemas na criação/leitura do vídeo")
        
        # Limpar
        import shutil
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"   ✗ Erro no teste de vídeo: {e}")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DO TESTE DE SETUP")
    print("=" * 60)
    print(f"Testes executados: {total_tests}")
    print(f"Testes bem-sucedidos: {success_count}")
    print(f"Taxa de sucesso: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 SETUP TÉCNICO COMPLETO COM SUCESSO!")
        print("   ✓ Estrutura de pastas criada")
        print("   ✓ Arquivos Python gerados")
        print("   ✓ Dependências principais instaladas")
        print("   ✓ Configurações funcionais")
        print("   ✓ Módulo de vídeo operacional")
        return True
    elif success_count >= total_tests * 0.8:
        print("\n⚠ SETUP TÉCNICO PARCIALMENTE COMPLETO")
        print("   O módulo está funcional com alguns warnings")
        return True
    else:
        print("\n❌ SETUP TÉCNICO COM PROBLEMAS")
        print("   Verifique os erros acima antes de continuar")
        return False

if __name__ == "__main__":
    success = test_basic_setup()
    
    if success:
        print("\n" + "=" * 60)
        print("PRÓXIMOS PASSOS:")
        print("=" * 60)
        print("1. Implementar funcionalidades específicas dos módulos")
        print("2. Criar testes mais específicos para cada componente")
        print("3. Integrar com o sistema principal do AI Shorts")
        print("4. Testar extração de conteúdo do YouTube")
        print("5. Validar geração de vídeos para diferentes plataformas")
        print("=" * 60)
    
    exit(0 if success else 1)
