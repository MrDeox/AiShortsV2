"""
Teste Básico do Sistema de Sincronização Áudio-Vídeo
Valida funcionalidades essenciais sem dependências externas complexas
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
print("🧪 Testando imports dos módulos...")
    
    try:
        from src.video.sync import AudioVideoSynchronizer, TimingOptimizer
print(" Imports principais: OK")
        
        # Testar se classes podem ser instanciadas
        sync = AudioVideoSynchronizer()
        opt = TimingOptimizer()
print(" Instanciação de classes: OK")
        
        return True
    except ImportError as e:
print(f" Erro de import: {e}")
        return False
    except Exception as e:
print(f" Erro geral: {e}")
        return False


def test_basic_functionality():
    """Testa funcionalidades básicas sem arquivos reais"""
print("\n Testando funcionalidades básicas...")
    
    try:
        from src.video.sync import AudioVideoSynchronizer, TimingOptimizer
        from src.video.sync.audio_video_synchronizer import AudioSegment, VideoSegment, TimelineEntry
        from src.video.sync.timing_optimizer import TransitionEffect
        
        # Testar AudioVideoSynchronizer
        sync = AudioVideoSynchronizer()
        
        # Criar segmento de teste
        audio_seg = AudioSegment(
            start_time=0.0,
            end_time=10.0,
            duration=10.0,
            audio_path="test.wav",
            text_content="Teste de áudio",
            section_type="hook"
        )
        
        video_seg = VideoSegment(
            start_time=0.0,
            end_time=10.0,
            duration=10.0,
            video_path="test.mp4",
            description="Teste de vídeo"
        )
        
        timeline_entry = TimelineEntry(
            timestamp=0.0,
            audio_segment=audio_seg,
            video_segment=video_seg,
            sync_point=True,
            transition_effect="fade"
        )
        
print(" Criação de estruturas de dados: OK")
        
        # Testar TimingOptimizer
        opt = TimingOptimizer()
        
        # Testar efeito de transição
        effect = TransitionEffect(
            name="fade",
            duration=0.5,
            intensity=0.8,
            applicable_types=["fade", "dissolve"]
        )
        
print(" Criação de efeitos de transição: OK")
        
        # Testar método de cálculo de duração
        duration_result = opt.calculate_optimal_duration(
            segment_text="Este é um teste de texto para calcular duração.",
            video_length=60.0
        )
        
print(" Cálculo de duração: OK")
print(f"   Duração calculada: {duration_result.get('final_duration', 0):.1f}s")
        
        return True
        
    except Exception as e:
print(f" Erro nas funcionalidades básicas: {e}")
        return False


def test_timeline_creation():
    """Testa criação de timeline combinado"""
print("\n Testando criação de timeline...")
    
    try:
        from src.video.sync import AudioVideoSynchronizer
        from src.video.sync.audio_video_synchronizer import VideoSegment
        
        sync = AudioVideoSynchronizer()
        
        # Criar segmentos de vídeo de teste
        video_segments = [
            VideoSegment(
                start_time=0.0,
                end_time=10.0,
                duration=10.0,
                video_path="segment1.mp4",
                description="Primeiro segmento"
            ),
            VideoSegment(
                start_time=10.0,
                end_time=22.0,
                duration=12.0,
                video_path="segment2.mp4",
                description="Segundo segmento"
            )
        ]
        
        # Criar timeline (simulado - não precisa de arquivo de áudio real)
        timeline = sync.create_timeline("dummy_audio.wav", video_segments)
        
print(f" Timeline criado com {len(timeline)} entradas")
        
        # Verificar estrutura do timeline
        for i, entry in enumerate(timeline):
            if hasattr(entry, 'timestamp') and hasattr(entry, 'video_segment'):
print(f"   Entrada {i+1}: {entry.timestamp:.1f}s - {entry.video_segment.description}")
        
        return True
        
    except Exception as e:
print(f" Erro na criação de timeline: {e}")
        return False


def test_transition_effects():
    """Testa sistema de efeitos de transição"""
print("\n Testando efeitos de transição...")
    
    try:
        from src.video.sync import TimingOptimizer
        
        opt = TimingOptimizer()
        
        # Verificar se efeitos estão disponíveis
        effects = opt.transition_effects
        
print(f" Efeitos disponíveis: {len(effects)}")
        for name, effect in effects.items():
print(f"   - {name}: {effect.duration}s, intensidade {effect.intensity}")
        
        # Testar seleção de efeitos
        video_segments = [
            {'video_path': 'seg1.mp4', 'duration': 10.0},
            {'video_path': 'seg2.mp4', 'duration': 12.0}
        ]
        
        effects_result = opt.add_transition_effects(video_segments)
        
print(f" Efeitos aplicados: {effects_result.get('total_effects', 0)}")
        
        return True
        
    except Exception as e:
print(f" Erro nos efeitos de transição: {e}")
        return False


def test_integration_points():
    """Testa pontos de integração com sistema TTS"""
print("\n Testando integração com TTS...")
    
    try:
        # Testar import do sistema TTS
        from src.tts.kokoro_tts import KokoroTTSClient
print(" Import do sistema TTS: OK")
        
        # Verificar se podemos instanciar cliente TTS
        tts = KokoroTTSClient()
print(" Instanciação do cliente TTS: OK")
        
        # Verificar vozes disponíveis
        voices = tts.get_voice_list()
print(f" Vozes disponíveis: {len(voices)}")
        
        return True
        
    except Exception as e:
print(f" Erro na integração TTS: {e}")
        return False


def main():
    """Executa todos os testes"""
print("🧪 INICIANDO TESTES DO SISTEMA DE SINCRONIZAÇÃO ÁUDIO-VÍDEO")
print("=" * 65)
    
    tests = [
        ("Imports", test_imports),
        ("Funcionalidades Básicas", test_basic_functionality),
        ("Criação de Timeline", test_timeline_creation),
        ("Efeitos de Transição", test_transition_effects),
        ("Integração TTS", test_integration_points)
    ]
    
    results = []
    
    for test_name, test_func in tests:
print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
print(f" Erro crítico em {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
print(f"\n{'='*65}")
print(" RELATÓRIO FINAL DOS TESTES")
print(f"{'='*65}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
print(f"\nResultado: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
print(" TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
print("\nPara usar o sistema:")
print("1. Instale dependências: pip install -r requirements_sync.txt")
print("2. Execute demo: python src/video/sync/demo_sync.py")
    else:
print(" Alguns testes falharam. Verifique as dependências:")
print("- pip install -r requirements_sync.txt")
print("- Verifique se Python >= 3.7")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)