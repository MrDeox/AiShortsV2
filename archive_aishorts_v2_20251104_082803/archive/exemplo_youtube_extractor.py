# -*- coding: utf-8 -*-
"""
Exemplo prático de uso do sistema de extração do YouTube.
Cria segmentos de 3-5 segundos para shorts.
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from video import YouTubeExtractor, SegmentProcessor
from utils.exceptions import ErrorHandler


def criar_segmento_youtube(video_url, start_time=0, duration=5, output_name=None):
    """
    Cria um segmento de vídeo do YouTube otimizado para shorts.
    
    Args:
        video_url: URL do vídeo do YouTube
        start_time: Tempo de início em segundos
        duration: Duração do segmento (3-5 segundos recomendado)
        output_name: Nome do arquivo de saída (opcional)
    
    Returns:
        Caminho do arquivo criado ou None se houver erro
    """
    
    print(f"🎬 Criando segmento de {duration}s do vídeo...")
    print(f"📍 URL: {video_url}")
    print(f"⏰ Início: {start_time}s")
    
    # Inicializar componentes
    extractor = YouTubeExtractor()
    processor = SegmentProcessor()
    
    try:
        # 1. Verificar disponibilidade e duração do vídeo
        print("\n🔍 Verificando vídeo...")
        video_info = extractor.extract_video_info(video_url)
        
        print(f"📺 Título: {video_info['title']}")
        print(f"⏱️ Duração total: {video_info['duration']}s")
        print(f"👤 Canal: {video_info['uploader']}")
        
        # Validar se vídeo é longo o suficiente
        if video_info['duration'] < start_time + duration:
            print(f"❌ Vídeo muito curto! Necessário: {start_time + duration}s, Disponível: {video_info['duration']}s")
            return None
        
        # 2. Baixar segmento específico
        print(f"\n⬇️ Baixando segmento...")
        segmento_path = extractor.download_segment(video_url, start_time, duration)
        print(f"✅ Segmento baixado: {segmento_path}")
        
        # 3. Normalizar para formato padrão
        print(f"\n🔧 Normalizando vídeo...")
        
        if output_name:
            if not output_name.endswith('.mp4'):
                output_name += '.mp4'
            output_path = f"outputs/video/{output_name}"
        else:
            # Nome automático baseado no vídeo e timestamp
            safe_title = "".join(c for c in video_info['title'][:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_path = f"outputs/video/{safe_title}_{start_time}s_{duration}s.mp4"
        
        video_final = processor.normalize_video(
            segmento_path,
            target_resolution="720p",
            target_fps=30,
            output_path=output_path
        )
        
        print(f"✅ Vídeo normalizado: {video_final}")
        
        # 4. Mostrar informações do resultado
        info_final = processor.get_video_info(video_final)
        print(f"\n📊 Informações do vídeo final:")
        print(f"   📏 Duração: {info_final['general']['duration']:.1f}s")
        print(f"   🎥 Resolução: {info_final['video_stream']['width']}x{info_final['video_stream']['height']}")
        print(f"   🎞️ FPS: {info_final['video_stream']['fps']:.1f}")
        print(f"   💾 Tamanho: {info_final['file_size'] / 1024 / 1024:.1f} MB")
        
        return video_final
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        ErrorHandler.handle_error(e, "criar_segmento_youtube")
        return None
    
    finally:
        # Limpeza
        print("\n🧹 Limpando arquivos temporários...")
        extractor.cleanup_temp_files()
        processor.cleanup_temp_files()


def demo_busca_e_selecao():
    """
    Demonstra busca de vídeos e seleção manual.
    """
    print("🔍 DEMO: Busca e Seleção de Vídeos")
    print("=" * 50)
    
    extractor = YouTubeExtractor()
    
    # Buscar vídeos
    termo = input("Digite o termo de busca (ex: 'gatos engraçados'): ") or "gatos engraçados"
    
    try:
        resultados = extractor.search_videos(termo, max_results=5)
        
        if not resultados:
            print("Nenhum vídeo encontrado.")
            return None
        
        print(f"\n📋 Resultados da busca por '{termo}':")
        print("-" * 50)
        
        for i, video in enumerate(resultados, 1):
            print(f"{i}. {video['title']}")
            print(f"   ⏱️ Duração: {video['duration']}s")
            print(f"   👤 Canal: {video['uploader']}")
            print(f"   👀 Views: {video['view_count']:,}")
            print()
        
        # Seleção
        while True:
            try:
                choice = int(input("Escolha um vídeo (1-5): ")) - 1
                if 0 <= choice < len(resultados):
                    return resultados[choice]['url']
                else:
                    print("Escolha inválida!")
            except ValueError:
                print("Digite um número válido!")
    
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        ErrorHandler.handle_error(e, "demo_busca_e_selecao")
        return None


def main():
    """Função principal de demonstração."""
    print("🎯 SISTEMA DE EXTRAÇÃO YOUTUBE - EXEMPLO PRÁTICO")
    print("=" * 60)
    
    # Opções do demo
    print("\nEscolha uma opção:")
    print("1. Usar URL específica")
    print("2. Buscar e selecionar vídeo")
    print("3. Demo completo (URL pré-definida)")
    
    try:
        opcao = input("\nOpção (1-3): ").strip()
        
        if opcao == "1":
            # URL específica
            url = input("Digite a URL do YouTube: ").strip()
            if not url:
                print("URL não pode estar vazia!")
                return
            
            # Configurações do segmento
            try:
                start = float(input("Tempo de início (segundos) [0]: ") or "0")
                duration = float(input("Duração do segmento (segundos) [5]: ") or "5")
                duration = min(max(duration, 1), 10)  # Limite entre 1-10s
            except ValueError:
                start, duration = 0, 5
            
            criar_segmento_youtube(url, start, duration)
        
        elif opcao == "2":
            # Busca e seleção
            url = demo_busca_e_selecao()
            if url:
                try:
                    start = float(input("Tempo de início (segundos) [0]: ") or "0")
                    duration = float(input("Duração do segmento (segundos) [5]: ") or "5")
                    duration = min(max(duration, 1), 10)
                except ValueError:
                    start, duration = 0, 5
                
                criar_segmento_youtube(url, start, duration)
        
        elif opcao == "3":
            # Demo com URL pré-definida (vídeo de teste)
            demo_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll para teste
            print(f"\n🎮 Executando demo com vídeo de teste...")
            print(f"⚠️ Este é um vídeo de exemplo para demonstração.")
            
            criar_segmento_youtube(demo_url, 0, 5, "demo_segmento")
        
        else:
            print("Opção inválida!")
    
    except KeyboardInterrupt:
        print("\n\n👋 Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        ErrorHandler.handle_error(e, "main")


if __name__ == "__main__":
    main()