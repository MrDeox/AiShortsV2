#!/usr/bin/env python3
"""
🎬 DEMO FINAL FUNCIONAL - AiShorts v2.0
=====================================

Demo end-to-end REAL que resolve os problemas identificados na análise:
1. Geração de tema e roteiro
2. TTS narração funcional 
3. Busca YouTube real
4. Download e processamento
5. Vídeo final FUNCIONAL para TikTok

CORRIGE: Arquivos de vídeo com 0 bytes, problemas de imports
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

def setup_environment():
    """Configurar ambiente para o demo"""
    print("🔧 Configurando ambiente...")
    
    # Configurar path corretamente
    base_path = Path(__file__).parent.parent
    src_path = base_path / "src"
    
    if src_path.exists():
        sys.path.insert(0, str(base_path))
        print(f"✅ Path configurado: {src_path}")
        return True
    else:
        print(f"❌ Diretório src não encontrado em {base_path}")
        return False

def test_theme_generator():
    """Testar geração de tema"""
    print("🎯 Testando Theme Generator...")
    
    try:
        # Importar com path correto
        from src.generators.theme_generator import theme_generator, ThemeCategory

        # Gerar tema real
        theme = theme_generator.generate_single_theme(ThemeCategory.ANIMALS)
        
        print(f"✅ Tema gerado: {theme.content}")
        print(f"📊 Qualidade: {theme.quality_score}")
        
        return theme
        
    except Exception as e:
        print(f"❌ Erro no Theme Generator: {e}")
        return None

def test_tts_generation(script_text):
    """Testar geração de TTS"""
    print("🎙️ Testando TTS Generation...")
    
    try:
        from src.tts.kokoro_tts import KokoroTTSClient
        
        tts = KokoroTTSClient()
        output_dir = Path("final_demo_audio")
        output_dir.mkdir(exist_ok=True)
        
        # Gerar áudio para texto simples
        audio_file = tts.text_to_speech(
            text=script_text[:200],  # Primeiros 200 chars
            output_filename="demo_audio.wav",
            voice="af_heart",
        )
        
        if audio_file and audio_file.get('success'):
            print(f"✅ TTS gerado: {audio_file.get('audio_path')}")
            return [Path(audio_file.get('audio_path'))]
        else:
            print(f"❌ Falha na geração de TTS: {audio_file.get('error')}")
            return []
        
    except Exception as e:
        print(f"❌ Erro no TTS: {e}")
        return []

def test_youtube_search(theme):
    """Testar busca no YouTube"""
    print("🔍 Testando busca no YouTube...")
    
    try:
        from src.video.extractors.youtube_extractor import YouTubeExtractor
        
        extractor = YouTubeExtractor()
        
        # Buscar vídeos relacionados ao tema
        query = f"{theme.content} curiosity"
        videos = extractor.search_videos(query, max_results=5)
        
        print(f"✅ Vídeos encontrados: {len(videos)}")
        for i, video in enumerate(videos[:3]):
            print(f"   {i+1}. {video.get('title', 'N/A')[:50]}...")
        
        return videos
        
    except Exception as e:
        print(f"❌ Erro na busca YouTube: {e}")
        return []

def test_youtube_download(videos):
    """Testar download de vídeo do YouTube"""
    print("📥 Testando download de vídeo do YouTube...")
    
    try:
        from src.video.extractors.youtube_extractor import YouTubeExtractor
        
        extractor = YouTubeExtractor()
        
        if not videos:
            print("❌ Nenhum vídeo para baixar.")
            return None
            
        # Tentar baixar o primeiro vídeo
        video_to_download = videos[0]
        print(f"📥 Baixando: {video_to_download.get('title', 'N/A')[:50]}...")
        
        # Baixar um segmento de 5 segundos
        downloaded_file = extractor.download_segment(
            video_to_download['url'],
            start_time=0,
            duration=5
        )
        
        if downloaded_file and Path(downloaded_file).exists():
            print(f"✅ Vídeo baixado: {downloaded_file}")
            return downloaded_file
        else:
            print("❌ Falha no download do vídeo.")
            return None
            
    except Exception as e:
        print(f"❌ Erro no download do YouTube: {e}")
        return None

def create_video_from_segment(audio_files, video_segment):
    """Criar vídeo a partir de um segmento de vídeo e áudio"""
    print("🎬 Criando vídeo a partir do segmento...")
    
    try:
        output_video = Path("final_demo_video.mp4")
        audio_file = audio_files[0] if audio_files else None

        if not video_segment or not Path(video_segment).exists():
            print("❌ Segmento de vídeo não encontrado.")
            return None

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_segment),
        ]

        if audio_file and audio_file.exists():
            cmd.extend(["-i", str(audio_file)])

        cmd.extend([
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            str(output_video)
        ])
        
        print(f"🎬 Executando: {' '.join(cmd[:5])}...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and output_video.exists():
            file_size = output_video.stat().st_size
            print(f"✅ Vídeo criado: {output_video}")
            print(f"📊 Tamanho: {file_size / (1024*1024):.1f} MB")
            
            if file_size > 1000:
                return output_video
            else:
                print(f"❌ Vídeo muito pequeno: {file_size} bytes")
                return None
        else:
            print(f"❌ Erro FFmpeg: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na criação do vídeo: {e}")
        return None

def generate_final_report(results):
    """Gerar relatório final"""
    print("📊 Gerando relatório final...")
    
    total_time = time.time() - results.get('start_time', time.time())
    
    report = {
        "demo_info": {
            "name": "Demo Final Funcional - AiShorts v2.0",
            "timestamp": datetime.now().isoformat(),
            "purpose": "Validação end-to-end com vídeo real",
            "status": "completed" if results.get('video_created') else "partial"
        },
        "pipeline_steps": {
            "theme_generation": results.get('theme') is not None,
            "tts_generation": len(results.get('audio_files', [])) > 0,
            "youtube_search": len(results.get('videos', [])) > 0,
            "video_creation": results.get('video_created') is not None
        },
        "output_files": {
            "theme": str(results.get('theme_file', 'N/A')),
            "audio_files": [str(f) for f in results.get('audio_files', [])],
            "youtube_videos": len(results.get('videos', [])),
            "final_video": str(results.get('video_created', 'N/A'))
        },
        "quality_metrics": {
            "pipeline_completion": sum(results.get('pipeline_steps', {}).values()),
            "total_steps": 4,
            "success_rate": sum(results.get('pipeline_steps', {}).values()) / 4 * 100,
            "execution_time": total_time
        }
    }
    
    # Salvar relatório
    report_file = Path("final_demo_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Relatório salvo: {report_file}")
    
    return report

def main():
    """Função principal do demo"""
    print("🚀 DEMO FINAL FUNCIONAL - AiShorts v2.0")
    print("=" * 50)
    
    start_time = time.time()
    results = {'start_time': start_time}
    
    try:
        # 1. Setup ambiente
        if not setup_environment():
            print("❌ Falha no setup. Encerrando.")
            return
        
        # 2. Testar Theme Generator
        theme = test_theme_generator()
        if theme:
            results['theme'] = theme
            results['pipeline_steps'] = {'theme_generation': True}
        
        # 3. Testar TTS
        script_text = theme.content if theme else 'Tema sobre animais curiosos'
        audio_files = test_tts_generation(script_text)
        if audio_files:
            results['audio_files'] = audio_files
            results['pipeline_steps']['tts_generation'] = True
        
        # 4. Testar YouTube Search
        videos = test_youtube_search(theme) if theme else []
        if videos:
            results['videos'] = videos
            results['pipeline_steps']['youtube_search'] = True
        
        # 5. Testar YouTube Download
        video_segment = test_youtube_download(videos)
        if video_segment:
            results['video_segment'] = video_segment
            results['pipeline_steps']['youtube_download'] = True

        # 6. Criar vídeo final
        video_file = create_video_from_segment(audio_files, video_segment)
        if video_file:
            results['video_created'] = video_file
            results['pipeline_steps']['video_creation'] = True
        
        # 7. Gerar relatório
        report = generate_final_report(results)
        
        # 8. Status final
        print("\n" + "=" * 50)
        print("🎉 DEMO FINAL CONCLUÍDO!")
        print("=" * 50)
        
        completed_steps = sum(report['pipeline_steps'].values())
        total_steps = len(report['pipeline_steps'])
        success_rate = (completed_steps / total_steps) * 100
        
        print(f"✅ Pipeline Steps: {completed_steps}/{total_steps} ({success_rate:.0f}%)")
        print(f"⏱️ Tempo Total: {report['quality_metrics']['execution_time']:.1f}s")
        print(f"🎬 Vídeo Final: {'✅ GERADO' if results.get('video_created') else '❌ NÃO GERADO'}")
        print(f"📁 Arquivos Output: {len([f for f in results.get('audio_files', []) if f.exists()])} áudios")
        
        if results.get('video_created'):
            size_mb = results['video_created'].stat().st_size / (1024*1024)
            print(f"📊 Vídeo: {size_mb:.1f} MB - {results['video_created']}")
        
        print("=" * 50)
        
        return report
        
    except Exception as e:
        print(f"❌ ERRO FATAL: {e}")
        return None

if __name__ == "__main__":
    main()