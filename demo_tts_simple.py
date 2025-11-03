"""
Demonstração Simplificada do Sistema Kokoro TTS
Teste básico de narração em português brasileiro
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append('/workspace')

from src.tts.kokoro_tts import KokoroTTSClient
from src.models.script_models import GeneratedTheme, ScriptSection, Script, ThemeCategory


def demo_basic_tts():
    """Demonstração básica do sistema TTS"""
    print("🎙️ DEMONSTRAÇÃO SISTEMA KOKORO TTS")
    print("=" * 50)
    
    # Inicializar cliente TTS
    print("1️⃣ Inicializando cliente TTS...")
    tts = KokoroTTSClient(
        lang_code='p',  # Português brasileiro
        voice_name='af_heart',  # Voz feminina - coração
        speed=1.0,
        output_dir='outputs/tts_demo'
    )
    print("   ✅ Cliente TTS inicializado!")
    
    # Listar vozes disponíveis
    print("\n2️⃣ Listando vozes disponíveis...")
    voices = tts.get_voice_list()
    for voice_id, description in voices.items():
        print(f"   🎤 {voice_id}: {description}")
    
    # Teste 1: Texto curto
    print("\n3️⃣ Teste 1 - Texto curto...")
    short_text = "Você sabia que os golfinhos têm nomes? Cientistas descobriram que cada golfinho desenvolve um assobio único."
    
    try:
        result1 = tts.text_to_speech(short_text, "teste_curto")
        if result1['success']:
            print(f"   ✅ Áudio gerado: {result1['audio_path']}")
            print(f"   ⏱️ Duração: {result1['duration']:.1f} segundos")
        else:
            print(f"   ❌ Erro: {result1.get('error')}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Teste 2: Roteiro simples
    print("\n4️⃣ Teste 2 - Roteiro completo...")
    
    # Criar roteiro de exemplo
    theme = GeneratedTheme(
        main_title="Curiosidade sobre golfinhos",
        category=ThemeCategory.ANIMALS,
        keywords=["golfinhos", "comunicação", "nomes"],
        target_audience="geral"
    )
    
    sections = [
        ScriptSection(
            type="hook",
            content="Você sabia que os golfinhos têm nomes uns para os outros?"
        ),
        ScriptSection(
            type="development", 
            content="Cada golfinho desenvolve um assobio único que funciona como nome, e outros golfinhos podem chamá-los usando esse som específico."
        ),
        ScriptSection(
            type="conclusion",
            content="Isso mostra como a comunicação animal é complexa e fascinante!"
        )
    ]
    
    script = Script(
        id="demo_script",
        theme=theme,
        sections=sections,
        platform="tiktok"
    )
    
    try:
        script_result = tts.script_to_audio(script, "demo_golfinhos")
        if script_result.get('full_audio', {}).get('success'):
            print(f"   ✅ Roteiro narrado com sucesso!")
            print(f"   📊 Estatísticas:")
            print(f"      • Tema: {script_result['theme']}")
            print(f"      • Seções: {script_result['sections_count']}")
            print(f"      • Duração total: {script_result['total_duration']:.1f}s")
            print(f"      • Voz: {script_result['voice_info']['description']}")
            print(f"      • Arquivo principal: {script_result['full_audio']['audio_path']}")
        else:
            print(f"   ❌ Erro na narração: {script_result.get('full_audio', {}).get('error')}")
    except Exception as e:
        print(f"   ❌ Exceção: {e}")
    
    # Teste 3: Otimização de plataforma
    print("\n5️⃣ Teste 3 - Otimização para plataformas...")
    
    if 'script_result' in locals() and script_result.get('full_audio', {}).get('success'):
        audio_file = script_result['full_audio']['audio_path']
        
        platforms = ['tiktok', 'shorts', 'reels']
        for platform in platforms:
            try:
                opt = tts.optimize_for_platform(audio_file, platform)
                print(f"   📱 {platform.upper()}:")
                print(f"      • Duração: {opt['original_duration']:.1f}s")
                print(f"      • Conforme: {'✅' if opt['is_compliant'] else '❌'}")
                print(f"      • Ótimo: {'✅' if opt['is_optimal'] else '❌'}")
                if opt['recommendations']:
                    print(f"      • Sugestões: {opt['recommendations'][0]}")
            except Exception as e:
                print(f"   ❌ Erro em {platform}: {e}")
    
    print(f"\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print(f"📁 Arquivos salvos em: outputs/tts_demo/")


def test_voice_compatibility():
    """Testa compatibilidade das vozes"""
    print("\n🔍 Testando compatibilidade de vozes...")
    
    # Lista de vozes para testar
    test_voices = ['af_heart', 'af_diamond', 'af_breeze', 'am_oreo', 'am_glenn']
    
    for voice in test_voices:
        try:
            print(f"\n🎤 Testando voz: {voice}")
            tts = KokoroTTSClient(
                lang_code='p',
                voice_name=voice,
                output_dir=f'outputs/voice_test_{voice}'
            )
            
            # Teste rápido
            test_text = "Teste de voz Kokoro."
            result = tts.text_to_speech(test_text, f"voice_test_{voice}")
            
            if result['success']:
                print(f"   ✅ Voz {voice} funciona!")
            else:
                print(f"   ❌ Voz {voice} falhou: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Erro com voz {voice}: {e}")


if __name__ == "__main__":
    # Criar diretório de saída
    Path('outputs').mkdir(exist_ok=True)
    Path('outputs/tts_demo').mkdir(exist_ok=True)
    
    # Executar demonstração básica
    demo_basic_tts()
    
    # Testar compatibilidade de vozes (opcional)
    # test_voice_compatibility()