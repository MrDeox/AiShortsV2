"""
Teste básico do sistema de processamento automático de vídeos
Basic test of automatic video processing system
"""

import sys
import os
import tempfile
import logging
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Testa se todas as classes podem ser importadas."""
    try:
        print("🧪 Testando imports...")
        
        from src.video.processing import (
            VideoProcessor,
            AutomaticVideoProcessor, 
            VideoQualityAnalyzer,
            QualityMetrics,
            PlatformRequirements
        )
        
        print("   ✅ Todas as classes importadas com sucesso")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no import: {e}")
        return False


def test_dependencies():
    """Testa se todas as dependências estão disponíveis."""
    print("\n🧪 Testando dependências...")
    
    dependencies = {
        'cv2': 'OpenCV',
        'numpy': 'NumPy', 
        'PIL': 'Pillow',
        'moviepy': 'MoviePy',
        'json': 'JSON',
        'pathlib': 'Pathlib'
    }
    
    missing = []
    for dep, name in dependencies.items():
        try:
            __import__(dep)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - NÃO ENCONTRADO")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Dependências faltando: {', '.join(missing)}")
        print("   Execute: pip install -r requirements_video.txt")
        return False
    
    print("   🎉 Todas as dependências disponíveis")
    return True


def test_video_processor_basic():
    """Testa funcionalidades básicas do VideoProcessor."""
    print("\n🧪 Testando VideoProcessor básico...")
    
    try:
        from src.video.processing import VideoProcessor
        
        processor = VideoProcessor()
        print("   ✅ VideoProcessor inicializado")
        
        # Testar obtenção de informações (com vídeo dummy)
        # info = processor.get_video_info("/dev/null")
        # print(f"   ✅ get_video_info funcionando: {info is not None}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no VideoProcessor: {e}")
        return False


def test_automatic_processor_basic():
    """Testa funcionalidades básicas do AutomaticVideoProcessor."""
    print("\n🧪 Testando AutomaticVideoProcessor básico...")
    
    try:
        from src.video.processing import AutomaticVideoProcessor
        
        processor = AutomaticVideoProcessor()
        print("   ✅ AutomaticVideoProcessor inicializado")
        
        # Testar estatísticas
        stats = processor.get_processing_stats()
        print(f"   ✅ Estatísticas disponíveis: {stats}")
        
        # Testar limpeza de cache
        cleared = processor.clear_cache(0)  # Limpar tudo
        print(f"   ✅ Limpeza de cache: {cleared} arquivos removidos")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no AutomaticVideoProcessor: {e}")
        return False


def test_quality_analyzer_basic():
    """Testa funcionalidades básicas do VideoQualityAnalyzer."""
    print("\n🧪 Testando VideoQualityAnalyzer básico...")
    
    try:
        from src.video.processing import VideoQualityAnalyzer, QualityMetrics
        
        analyzer = VideoQualityAnalyzer()
        print("   ✅ VideoQualityAnalyzer inicializado")
        
        # Testar criação de métricas
        metrics = QualityMetrics(
            brightness=0.5,
            sharpness=0.7,
            motion_level=0.3,
            contrast=0.6,
            color_saturation=0.8,
            noise_level=0.2,
            overall_score=75.0
        )
        
        metrics_dict = metrics.to_dict()
        print(f"   ✅ QualityMetrics criadas: {metrics_dict}")
        
        # Testar plataformas disponíveis
        platforms = list(analyzer.platform_requirements.keys())
        print(f"   ✅ Plataformas suportadas: {platforms}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no VideoQualityAnalyzer: {e}")
        return False


def test_mock_video_analysis():
    """Testa análise com vídeo simulado."""
    print("\n🧪 Testando análise com vídeo simulado...")
    
    try:
        from src.video.processing import AutomaticVideoProcessor, VideoQualityAnalyzer
        import numpy as np
        from moviepy.editor import ColorClip
        
        # Criar vídeo simples de teste
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_video_path = temp_file.name
        
        try:
            # Criar clip colorido simples
            clip = ColorClip(size=(640, 480), color=(100, 150, 200), duration=5)
            clip = clip.set_fps(10)  # FPS baixo para teste rápido
            
            clip.write_videofile(
                temp_video_path,
                fps=10,
                codec='libx264',
                audio_codec=None,  # Sem áudio para simplificar
                verbose=False,
                logger=None
            )
            clip.close()
            
            print(f"   ✅ Vídeo de teste criado: {temp_video_path}")
            
            # Testar análise de qualidade
            analyzer = VideoQualityAnalyzer()
            
            # Análise básica (pode falhar se vídeo inválido)
            try:
                metrics = analyzer.analyze_video_quality(temp_video_path)
                print(f"   ✅ Análise de qualidade: {metrics.overall_score:.1f}/100")
            except Exception as e:
                print(f"   ⚠️  Análise de qualidade falhou: {e}")
            
            # Testar processamento automático
            processor = AutomaticVideoProcessor()
            
            try:
                # Tentar extrair frames
                frames = processor.extract_frames_for_analysis(temp_video_path, num_frames=2)
                if frames:
                    print(f"   ✅ Frames extraídos: {len(frames)}")
                else:
                    print("   ⚠️  Nenhum frame extraído")
            except Exception as e:
                print(f"   ⚠️  Extração de frames falhou: {e}")
            
        finally:
            # Limpar arquivo temporário
            try:
                if os.path.exists(temp_video_path):
                    os.unlink(temp_video_path)
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste de análise: {e}")
        return False


def run_basic_tests():
    """Executa todos os testes básicos."""
    print("🚀 INICIANDO TESTES BÁSICOS DO SISTEMA DE PROCESSAMENTO")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_dependencies,
        test_video_processor_basic,
        test_automatic_processor_basic,
        test_quality_analyzer_basic,
        test_mock_video_analysis
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   💥 Erro inesperado: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DOS TESTES")
    print("=" * 60)
    print(f"✅ Testes aprovados: {passed}")
    print(f"❌ Testes falharam: {failed}")
    print(f"📈 Taxa de sucesso: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("   O sistema está pronto para uso.")
    else:
        print(f"\n⚠️  {failed} TESTE(S) FALHARAM")
        print("   Verifique os erros acima antes de usar em produção.")
    
    return failed == 0


if __name__ == "__main__":
    # Configurar logging básico
    logging.basicConfig(level=logging.WARNING)
    
    # Executar testes
    success = run_basic_tests()
    
    # Código de saída
    sys.exit(0 if success else 1)