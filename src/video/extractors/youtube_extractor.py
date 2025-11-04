# -*- coding: utf-8 -*-
"""
Extrator de vídeos do YouTube usando yt-dlp.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path

import yt_dlp
from loguru import logger

from src.utils.exceptions import (
    YouTubeExtractionError, 
    VideoUnavailableError, 
    VideoTooShortError,
    NetworkError,
    ErrorHandler
)


class YouTubeExtractor:
    """
    Extrator de vídeos do YouTube usando yt-dlp.
    
    Capabilities:
    - Search de vídeos por query
    - Extração de informações de vídeos
    - Download de segmentos específicos
    - Tratamento robusto de erros
    """
    
    def __init__(self, temp_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Inicializa o extrator.
        
        Args:
            temp_dir: Diretório temporário para arquivos de download
            output_dir: Diretório de saída para vídeos processados
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "aishorts"
        self.output_dir = Path(output_dir) if output_dir else Path("./outputs/video")
        
        # Criar diretórios se não existirem
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações do yt-dlp
        self.ydl_opts = {
            'format': 'best[height<=720]',  # Resolução máxima 720p
            'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
            'no_warnings': False,
            'extract_flat': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        logger.info(f"YouTubeExtractor inicializado - Temp: {self.temp_dir}, Output: {self.output_dir}")
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Pesquisa vídeos no YouTube por query.
        
        Args:
            query: Query de busca
            max_results: Máximo de resultados (padrão: 10)
            
        Returns:
            Lista de vídeos encontrados com informações básicas
            
        Raises:
            YouTubeExtractionError: Se houver erro na busca
        """
        logger.info(f"Pesquisando vídeos para: '{query}' (max_results: {max_results})")
        
        def _search():
            search_opts = {
                'playlist_items': f'1:{max_results}',
                'noplaylist': False,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL({**self.ydl_opts, **search_opts}) as ydl:
                return ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        
        try:
            result = ErrorHandler.retry_with_backoff(
                _search, 
                max_retries=3, 
                delay=1.0
            )
            
            if not result or 'entries' not in result:
                logger.warning(f"Nenhum vídeo encontrado para query: {query}")
                return []
            
            videos = []
            for entry in result['entries']:
                if entry:  # Skip entries vazios
                    video_info = {
                        'id': entry.get('id'),
                        'title': entry.get('title', 'Sem título'),
                        'duration': entry.get('duration'),
                        'uploader': entry.get('uploader'),
                        'view_count': entry.get('view_count'),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'thumbnail': entry.get('thumbnail'),
                        'webpage_url': entry.get('webpage_url'),
                    }
                    videos.append(video_info)
            
            logger.info(f"Encontrados {len(videos)} vídeos para '{query}'")
            return videos
            
        except Exception as e:
            error_msg = f"Erro na busca de vídeos para '{query}': {str(e)}"
            logger.error(error_msg)
            raise YouTubeExtractionError(error_msg, youtube_error=str(e))
    
    def extract_video_info(self, video_url: str) -> Dict[str, Any]:
        """
        Extrai informações detalhadas de um vídeo.
        
        Args:
            video_url: URL do vídeo
            
        Returns:
            Dicionário com informações do vídeo
            
        Raises:
            VideoUnavailableError: Se vídeo não estiver disponível
            NetworkError: Se houver problema de conectividade
            YouTubeExtractionError: Outros erros de extração
        """
        logger.info(f"Extraindo informações do vídeo: {video_url}")
        
        def _extract_info():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(video_url, download=False)
        
        try:
            info = ErrorHandler.retry_with_backoff(
                _extract_info,
                max_retries=2,
                delay=2.0
            )
            
            if not info:
                raise VideoUnavailableError(
                    f"Vídeo indisponível ou não encontrado: {video_url}",
                    video_url=video_url
                )
            
            # Verificar se o vídeo tem duração adequada
            duration = info.get('duration', 0)
            if duration and duration < 5:  # Mínimo 5 segundos
                raise VideoTooShortError(
                    f"Vídeo muito curto ({duration}s): {video_url}",
                    video_url=video_url,
                    duration=duration,
                    requested_duration=5
                )
            
            # Extrair informações relevantes
            video_info = {
                'id': info.get('id'),
                'title': info.get('title'),
                'description': info.get('description'),
                'duration': duration,
                'uploader': info.get('uploader'),
                'upload_date': info.get('upload_date'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'comment_count': info.get('comment_count'),
                'categories': info.get('categories'),
                'tags': info.get('tags'),
                'url': video_url,
                'webpage_url': info.get('webpage_url'),
                'thumbnail': info.get('thumbnail'),
                'formats': self._extract_format_info(info.get('formats', [])),
                'available_subtitles': info.get('subtitles', {}),
                'automatic_captions': info.get('automatic_captions', {}),
            }
            
            logger.info(f"Informações extraídas com sucesso para: {video_info['title']}")
            return video_info
            
        except VideoUnavailableError:
            raise
        except VideoTooShortError:
            raise
        except Exception as e:
            error_msg = f"Erro na extração de informações de {video_url}: {str(e)}"
            
            # Verificar erros específicos
            if " vídeo é privado" in str(e).lower() or "private" in str(e).lower():
                raise VideoUnavailableError(
                    f"Vídeo privado ou indisponível: {video_url}",
                    video_url=video_url,
                    unavailable_reason="private"
                )
            elif "não encontrado" in str(e).lower() or "not found" in str(e).lower():
                raise VideoUnavailableError(
                    f"Vídeo não encontrado: {video_url}",
                    video_url=video_url,
                    unavailable_reason="not_found"
                )
            elif "conexão" in str(e).lower() or "network" in str(e).lower() or "timeout" in str(e).lower():
                raise NetworkError(
                    f"Erro de conectividade para {video_url}: {str(e)}",
                    url=video_url
                )
            
            raise YouTubeExtractionError(error_msg, video_url=video_url, youtube_error=str(e))
    
    def download_segment(self, video_url: str, start_time: float, duration: float, output_dir: Optional[str] = None) -> str:
        """
        Baixa um segmento específico de um vídeo.
        
        Args:
            video_url: URL do vídeo
            start_time: Tempo de início em segundos
            duration: Duração do segmento em segundos
            output_dir: Diretório de saída (opcional)
            
        Returns:
            Caminho para o arquivo baixado
            
        Raises:
            VideoUnavailableError: Se vídeo não estiver disponível
            YouTubeExtractionError: Se houver erro no download
        """
        logger.info(f"Baixando segmento: {start_time}s por {duration}s de {video_url}")
        
        # Validar parâmetros
        if start_time < 0:
            raise ValueError(f"Tempo de início deve ser positivo: {start_time}")
        if duration <= 0:
            raise ValueError(f"Duração deve ser positiva: {duration}")
        if duration > 300:  # Máximo 5 minutos
            raise ValueError(f"Duração muito longa (máximo 300s): {duration}")
        
        try:
            # Verificar duração do vídeo primeiro
            video_info = self.extract_video_info(video_url)
            video_duration = video_info.get('duration', 0)
            
            if video_duration and start_time + duration > video_duration:
                raise ValueError(
                    f"Segmento excede duração do vídeo. "
                    f"Vídeo: {video_duration}s, Solicitado: {start_time}s + {duration}s"
                )
            
            # Definir diretório de saída
            output_dir_path = Path(output_dir) if output_dir else self.output_dir
            output_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Configurar opções para download do segmento
            download_opts = {
                **self.ydl_opts,
                'format': 'best[height<=720]',  # Resolução adequada para shorts
                'outtmpl': str(output_dir_path / '%(id)s_segment.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',  # Convert to MP4 for consistency
                }],
                'postprocessor_args': [
                    '-ss', str(start_time),  # Start time
                    '-t', str(duration),     # Duration
                ],
                'keepvideo': True,
            }
            
            def _download():
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    
                    # O arquivo é salvo com o template, encontramos o arquivo real
                    video_id = info.get('id')
                    pattern = str(output_dir_path / f"{video_id}_segment.*")
                    
                    import glob
                    downloaded_files = glob.glob(pattern)
                    if not downloaded_files:
                        raise YouTubeExtractionError(
                            f"Arquivo não encontrado após download: {video_url}"
                        )
                    
                    return downloaded_files[0]
            
            file_path = ErrorHandler.retry_with_backoff(
                _download,
                max_retries=2,
                delay=3.0
            )
            
            logger.info(f"Segmento baixado com sucesso: {file_path}")
            return file_path
            
        except (VideoUnavailableError, VideoTooShortError):
            raise
        except Exception as e:
            error_msg = f"Erro no download do segmento de {video_url}: {str(e)}"
            logger.error(error_msg)
            raise YouTubeExtractionError(error_msg, video_url=video_url, youtube_error=str(e))
    
    def _extract_format_info(self, formats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrai informações relevantes dos formatos disponíveis.
        
        Args:
            formats: Lista de formatos do yt-dlp
            
        Returns:
            Lista de formatos filtrados e processados
        """
        filtered_formats = []
        
        for fmt in formats:
            if not fmt or not fmt.get('format_id'):
                continue
            
            # Filtrar apenas formatos de vídeo com qualidade aceitável
            height = fmt.get('height', 0)
            if height and height >= 360 and height <= 1080:  # Entre 360p e 1080p
                format_info = {
                    'format_id': fmt['format_id'],
                    'ext': fmt.get('ext'),
                    'height': height,
                    'width': fmt.get('width'),
                    'fps': fmt.get('fps'),
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                    'filesize': fmt.get('filesize'),
                    'url': fmt.get('url'),
                }
                filtered_formats.append(format_info)
        
        # Ordenar por resolução (maior primeiro)
        filtered_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
        
        return filtered_formats[:10]  # Máximo 10 formatos
    
    def cleanup_temp_files(self, keep_output: bool = True):
        """
        Limpa arquivos temporários.
        
        Args:
            keep_output: Se True, mantém arquivos de saída
        """
        try:
            temp_files = list(self.temp_dir.glob("*"))
            cleaned = 0
            
            for file_path in temp_files:
                if file_path.is_file():
                    if keep_output and file_path.suffix == '.mp4':
                        continue  # Manter vídeos finais
                    
                    file_path.unlink()
                    cleaned += 1
            
            logger.info(f"Limpeza concluída: {cleaned} arquivos removidos")
            
        except Exception as e:
            logger.warning(f"Erro durante limpeza: {str(e)}")


if __name__ == "__main__":
    # Teste básico do extrator
    print("=== Teste do YouTubeExtractor ===")
    
    extractor = YouTubeExtractor()
    
    try:
        # Teste de busca
        print("\n1. Testando busca de vídeos...")
        results = extractor.search_videos("gatos engraçados", max_results=3)
        print(f"Encontrados: {len(results)} vídeos")
        for video in results:
            print(f"  - {video['title']} ({video['duration']}s)")
        
        # Teste de extração de informações (se houver resultados)
        if results:
            print("\n2. Testando extração de informações...")
            first_video = results[0]
            info = extractor.extract_video_info(first_video['url'])
            print(f"Título: {info['title']}")
            print(f"Duração: {info['duration']}s")
            print(f"Uploader: {info['uploader']}")
        
        # Teste de download de segmento (opcional, pode ser lento)
        if results and info['duration'] > 10:
            print("\n3. Testando download de segmento (primeiros 3s)...")
            segment_path = extractor.download_segment(first_video['url'], 0, 3)
            print(f"Segmento salvo em: {segment_path}")
        
        print("\n=== Teste concluído com sucesso ===")
        
    except Exception as e:
        print(f"Erro durante teste: {e}")
        ErrorHandler.handle_error(e, "teste_youtube_extractor")
    
    finally:
        # Limpeza
        extractor.cleanup_temp_files()