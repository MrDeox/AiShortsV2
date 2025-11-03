"""
YouTube content extractor using yt-dlp
Extração de conteúdo do YouTube para o sistema AI Shorts
"""

import yt_dlp
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from config.video_settings import YOUTUBE_SETTINGS, get_config


class YouTubeExtractor:
    """
    Classe para extrair conteúdo de vídeos do YouTube.
    
    Features:
    - Extração de metadados
    - Download de vídeo e áudio
    - Extração de frames
    - Processamento de legendas
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o extrator de YouTube.
        
        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or get_config()['youtube']
        self.temp_dir = Path(tempfile.gettempdir()) / 'youtube_extractor'
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configurar yt-dlp
        self.ydl_opts = self._setup_ydl_options()
    
    def _setup_ydl_options(self) -> Dict:
        """
        Configura as opções do yt-dlp.
        
        Returns:
            Dicionário com as opções configuradas
        """
        opts = {
            'format': self.config.get('quality', 'best[height<=720]'),
            'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
            'writeinfojson': True,
            'writesubtitles': self.config.get('writesubtitles', False),
            'writeautomaticsub': self.config.get('writeautomaticsub', False),
            'ignoreerrors': True,
            'no_warnings': False,
        }
        
        if self.config.get('extract_audio', False):
            opts.update({
                'extractaudio': True,
                'audioformat': self.config.get('audio_format', 'mp3'),
                'audioquality': self.config.get('audio_quality', '192'),
            })
        
        return opts
    
    def extract_video_info(self, url: str) -> Optional[Dict]:
        """
        Extrai apenas as informações do vídeo sem fazer download.
        
        Args:
            url: URL do vídeo do YouTube
            
        Returns:
            Dicionário com as informações do vídeo ou None se falhar
        """
        info_opts = self.ydl_opts.copy()
        info_opts['quiet'] = True
        info_opts['no_warnings'] = True
        
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return self._process_video_info(info)
            except Exception as e:
                print(f"Erro ao extrair informações do vídeo: {e}")
                return None
    
    def download_video(self, url: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Faz download do vídeo.
        
        Args:
            url: URL do vídeo do YouTube
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do arquivo baixado ou None se falhar
        """
        if output_path:
            self.ydl_opts['outtmpl'] = output_path
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                return self._get_downloaded_file_path(info)
            except Exception as e:
                print(f"Erro ao fazer download do vídeo: {e}")
                return None
    
    def extract_frames(self, video_path: str, output_dir: str, fps: float = 1.0) -> List[str]:
        """
        Extrai frames do vídeo.
        
        Args:
            video_path: Caminho do vídeo
            output_dir: Diretório para salvar os frames
            fps: Frames por segundo para extração
            
        Returns:
            Lista de caminhos dos frames extraídos
        """
        # TODO: Implementar extração de frames usando OpenCV
        # Por enquanto, apenas cria o diretório
        os.makedirs(output_dir, exist_ok=True)
        print(f"Extraindo frames de {video_path} para {output_dir}")
        return []
    
    def _process_video_info(self, info: Dict) -> Dict:
        """
        Processa as informações do vídeo.
        
        Args:
            info: Informações brutas do yt-dlp
            
        Returns:
            Informações processadas
        """
        return {
            'title': info.get('title', ''),
            'description': info.get('description', ''),
            'duration': info.get('duration', 0),
            'view_count': info.get('view_count', 0),
            'uploader': info.get('uploader', ''),
            'upload_date': info.get('upload_date', ''),
            'tags': info.get('tags', []),
            'categories': info.get('categories', []),
            'thumbnail': info.get('thumbnail', ''),
            'formats': info.get('formats', []),
        }
    
    def _get_downloaded_file_path(self, info: Dict) -> Optional[str]:
        """
        Obtém o caminho do arquivo baixado.
        
        Args:
            info: Informações do download
            
        Returns:
            Caminho do arquivo ou None
        """
        if 'requested_downloads' in info and info['requested_downloads']:
            return info['requested_downloads'][0].get('filename')
        return info.get('filename')
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Busca vídeos no YouTube.
        
        Args:
            query: Termo de busca
            max_results: Máximo de resultados
            
        Returns:
            Lista de vídeos encontrados
        """
        # TODO: Implementar busca usando YouTube API ou yt-dlp
        print(f"Buscando por '{query}' (máximo {max_results} resultados)")
        return []
    
    def validate_url(self, url: str) -> bool:
        """
        Valida se a URL é do YouTube.
        
        Args:
            url: URL para validar
            
        Returns:
            True se for uma URL válida do YouTube
        """
        youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
        return any(domain in url for domain in youtube_domains)
    
    def get_video_duration(self, url: str) -> Optional[int]:
        """
        Obtém a duração do vídeo.
        
        Args:
            url: URL do vídeo
            
        Returns:
            Duração em segundos ou None se falhar
        """
        info = self.extract_video_info(url)
        return info.get('duration') if info else None
    
    def cleanup(self):
        """Limpa arquivos temporários."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("Arquivos temporários limpos")


# Exemplo de uso
if __name__ == "__main__":
    # Teste básico
    extractor = YouTubeExtractor()
    
    # URL de teste (você pode substituir por qualquer URL do YouTube)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    if extractor.validate_url(test_url):
        print(f"URL válida: {test_url}")
        
        # Extrair informações
        info = extractor.extract_video_info(test_url)
        if info:
            print(f"Título: {info['title']}")
            print(f"Duração: {info['duration']} segundos")
            print(f"Visualizações: {info['view_count']}")
    else:
        print(f"URL inválida: {test_url}")
