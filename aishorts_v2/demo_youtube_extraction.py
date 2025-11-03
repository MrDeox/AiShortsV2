# -*- coding: utf-8 -*-
"""
Exemplo de uso do sistema de extração do YouTube.
"""

import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos
from src.video import YouTubeExtractor, SegmentProcessor
from src.utils.exceptions import ErrorHandler


def exemplo_busca_videos():
    """Exemplo de busca de vídeos."""
    print("=== Exemplo: Busca de Vídeos ===")
    
    # Criar extrator
    extractor = YouTubeExtractor()
    
    try:
        # Buscar vídeos
        resultados = extractor.search_videos("gatos engraçados", max_results=5)
        
        print(f"Encontrados {len(resultados)} vídeos:")
        for i, video in enumerate(resultados, 1):
            print(f"{i}. {video['title']}")
            print(f"   Duração: {video['duration']}s")
            print(f"   Canal: {video['uploader']}")
            print(f"   Views: {video['view_count']:,}")
            print(f"   URL: {video['url']}")
            print()
        
        return resultados
        
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        ErrorHandler.handle_error(e, "exemplo_busca_videos")
        return []


def exemplo_extracao_info(resultados):
    """Exemplo de extração de informações detalhadas."""
    if not resultados:
        print("Nenhum vídeo disponível para extração de informações")
        return
    
    print("=== Exemplo: Extração de Informações ===")
    
    extractor = YouTubeExtractor()
    
    # Pegar o primeiro vídeo
    primeiro_video = resultados[0]
    
    try:
        info = extractor.extract_video_info(primeiro_video['url'])
        
        print(f"Título: {info['title']}")
        print(f"Descrição: {info['description'][:100]}...")
        print(f"Duração: {info['duration']} segundos")
        print(f"Uploader: {info['uploader']}")
        print(f"Data de upload: {info['upload_date']}")
        print(f"Views: {info['view_count']:,}")
        print(f"Likes: {info['like_count']:,}")
        print(f"Categorias: {info['categories']}")
        print(f"Tags: {', '.join(info['tags'][:5])}...")
        
        # Mostrar formatos disponíveis
        if info['formats']:
            print("\nFormatos disponíveis:")
            for fmt in info['formats'][:3]:
                print(f"  - {fmt['height']}p ({fmt['ext']})")
        
        return info
        
    except Exception as e:
        logger.error(f"Erro na extração de informações: {e}")
        ErrorHandler.handle_error(e, "exemplo_extracao_info")
        return None


def exemplo_processamento_segmento(video_url):
    """Exemplo de processamento de segmento de vídeo."""
    print("=== Exemplo: Processamento de Segmento ===")
    
    extractor = YouTubeExtractor()
    processor = SegmentProcessor()
    
    try:
        # Extrair segmento (primeiros 3 segundos)
        print("Baixando segmento de 3 segundos...")
        segmento_path = extractor.download_segment(video_url, 0, 3)
        print(f"Segmento baixado: {segmento_path}")
        
        # Obter informações do segmento
        print("\nAnalisando segmento...")
        info_segmento = processor.get_video_info(segmento_path)
        
        print(f"Duração: {info_segmento['general']['duration']:.1f}s")
        print(f"Tamanho do arquivo: {info_segmento['file_size']:,} bytes")
        
        if info_segmento.get('video_stream'):
            vs = info_segmento['video_stream']
            print(f"Resolução: {vs['width']}x{vs['height']}")
            print(f"FPS: {vs['fps']:.1f}")
            print(f"Codec: {vs['codec']}")
        
        if info_segmento.get('audio_stream'):
            audio = info_segmento['audio_stream']
            print(f"Codec de áudio: {audio['codec']}")
            print(f"Canais: {audio['channels']}")
        
        # Normalizar vídeo
        print("\nNormalizando vídeo...")
        video_normalizado = processor.normalize_video(
            segmento_path, 
            target_resolution="720p",
            target_fps=30
        )
        print(f"Vídeo normalizado: {video_normalizado}")
        
        return segmento_path, video_normalizado
        
    except Exception as e:
        logger.error(f"Erro no processamento de segmento: {e}")
        ErrorHandler.handle_error(e, "exemplo_processamento_segmento")
        return None, None


def exemplo_fluxo_completo():
    """Exemplo do fluxo completo: busca → extração → processamento."""
    print("=== Exemplo: Fluxo Completo ===")
    
    # 1. Busca
    print("1. Buscando vídeos...")
    resultados = exemplo_busca_videos()
    
    if not resultados:
        print("Nenhum vídeo encontrado. Encerrando.")
        return
    
    # 2. Extração de informações
    print("\n2. Extraindo informações detalhadas...")
    info = exemplo_extracao_info(resultados)
    
    if not info:
        print("Falha na extração de informações. Encerrando.")
        return
    
    # 3. Processamento de segmento
    print("\n3. Processando segmento...")
    try:
        # Verificar se vídeo é longo o suficiente
        if info['duration'] < 10:
            print(f"Vídeo muito curto ({info['duration']}s). Tentando com vídeo diferente...")
            # Tentar com outro vídeo da lista
            for video in resultados[1:]:
                if video['duration'] >= 10:
                    info_alt = extractor.extract_video_info(video['url'])
                    if info_alt['duration'] >= 10:
                        exemplo_processamento_segmento(video['url'])
                        break
        else:
            exemplo_processamento_segmento(info['url'])
            
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        ErrorHandler.handle_error(e, "exemplo_fluxo_completo")
    
    # 4. Limpeza
    print("\n4. Limpando arquivos temporários...")
    try:
        extractor.cleanup_temp_files(keep_output=True)
        processor = SegmentProcessor()
        processor.cleanup_temp_files()
        print("Limpeza concluída.")
    except Exception as e:
        logger.warning(f"Erro na limpeza: {e}")


def demonstracao_erros():
    """Demonstração de tratamento de erros."""
    print("=== Demonstração: Tratamento de Erros ===")
    
    extractor = YouTubeExtractor()
    processor = SegmentProcessor()
    
    # Teste 1: URL inválida
    print("\n1. Testando URL inválida...")
    try:
        extractor.extract_video_info("https://youtube.com/watch?v=INVALID")
    except Exception as e:
        print(f"Erro capturado: {type(e).__name__}: {e}")
    
    # Teste 2: Vídeo muito curto
    print("\n2. Testando vídeo muito curto...")
    try:
        # Simular vídeo de 2 segundos (muito curto)
        with patch.object(extractor, 'extract_video_info') as mock_extract:
            mock_extract.side_effect = Exception("Vídeo muito curto")
            extractor.extract_video_info("https://youtube.com/watch?v=short")
    except Exception as e:
        print(f"Erro capturado: {type(e).__name__}: {e}")
    
    # Teste 3: Arquivo inexistente
    print("\n3. Testando arquivo inexistente...")
    try:
        processor.get_video_info("/caminho/inexistente.mp4")
    except Exception as e:
        print(f"Erro capturado: {type(e).__name__}: {e}")


def main():
    """Função principal de demonstração."""
    print("SISTEMA DE EXTRAÇÃO DO YOUTUBE - DEMONSTRAÇÃO")
    print("=" * 50)
    
    try:
        # Demonstrar funcionalidades básicas
        exemplo_fluxo_completo()
        
        print("\n" + "=" * 50)
        print("Demonstração concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\nDemonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro geral na demonstração: {e}")
        ErrorHandler.handle_error(e, "main_demo")
    
    finally:
        print("\nLimpeza final...")
        try:
            extractor = YouTubeExtractor()
            extractor.cleanup_temp_files(keep_output=False)
        except:
            pass


if __name__ == "__main__":
    # Executar demonstração
    main()