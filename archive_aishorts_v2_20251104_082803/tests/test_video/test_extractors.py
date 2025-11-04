# -*- coding: utf-8 -*-
"""
Testes para extractors de vídeo.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Importar módulos a serem testados
from src.video.extractors.youtube_extractor import YouTubeExtractor
from src.video.extractors.segment_processor import SegmentProcessor
from src.utils.exceptions import (
    YouTubeExtractionError,
    VideoUnavailableError,
    VideoTooShortError,
    VideoProcessingError,
    NetworkError
)


class TestYouTubeExtractor:
    """Testes para YouTubeExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Fixture para criar instância do extrator."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield YouTubeExtractor(temp_dir=temp_dir, output_dir=temp_dir)
    
    @pytest.fixture
    def mock_ydl_search_result(self):
        """Mock para resultado de busca do yt-dlp."""
        return {
            'entries': [
                {
                    'id': 'test_id_1',
                    'title': 'Vídeo de Teste 1',
                    'duration': 120,
                    'uploader': 'Canal Teste',
                    'view_count': 1000,
                    'url': 'https://www.youtube.com/watch?v=test_id_1',
                    'thumbnail': 'https://example.com/thumb1.jpg',
                    'webpage_url': 'https://www.youtube.com/watch?v=test_id_1'
                },
                {
                    'id': 'test_id_2',
                    'title': 'Vídeo de Teste 2',
                    'duration': 60,
                    'uploader': 'Canal Teste 2',
                    'view_count': 500,
                    'url': 'https://www.youtube.com/watch?v=test_id_2',
                    'thumbnail': 'https://example.com/thumb2.jpg',
                    'webpage_url': 'https://www.youtube.com/watch?v=test_id_2'
                }
            ]
        }
    
    @pytest.fixture
    def mock_ydl_info_result(self):
        """Mock para resultado de informações do vídeo."""
        return {
            'id': 'test_video_123',
            'title': 'Vídeo de Teste Completo',
            'description': 'Descrição do vídeo de teste',
            'duration': 300,
            'uploader': 'Canal de Teste',
            'upload_date': '20240101',
            'view_count': 5000,
            'like_count': 200,
            'comment_count': 50,
            'categories': ['Entertainment'],
            'tags': ['teste', 'video'],
            'webpage_url': 'https://www.youtube.com/watch?v=test_video_123',
            'thumbnail': 'https://example.com/thumbnail.jpg',
            'formats': [
                {
                    'format_id': '18',
                    'ext': 'mp4',
                    'height': 360,
                    'width': 640,
                    'fps': 30,
                    'vcodec': 'h264',
                    'acodec': 'aac',
                    'filesize': 1000000
                },
                {
                    'format_id': '22',
                    'ext': 'mp4',
                    'height': 720,
                    'width': 1280,
                    'fps': 30,
                    'vcodec': 'h264',
                    'acodec': 'aac',
                    'filesize': 2000000
                }
            ],
            'subtitles': {},
            'automatic_captions': {}
        }
    
    def test_initialization(self, extractor):
        """Testa inicialização do extrator."""
        assert extractor.temp_dir.exists()
        assert extractor.output_dir.exists()
        assert extractor.ydl_opts['format'] == 'best[height<=720]'
    
    @patch('yt_dlp.YoutubeDL')
    def test_search_videos_success(self, mock_ydl, extractor, mock_ydl_search_result):
        """Testa busca de vídeos com sucesso."""
        mock_ydl_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = mock_ydl_search_result
        
        results = extractor.search_videos("teste busca", max_results=5)
        
        assert len(results) == 2
        assert results[0]['id'] == 'test_id_1'
        assert results[0]['title'] == 'Vídeo de Teste 1'
        assert results[0]['duration'] == 120
        assert 'url' in results[0]
        assert 'thumbnail' in results[0]
    
    @patch('yt_dlp.YoutubeDL')
    def test_search_videos_empty_result(self, mock_ydl, extractor):
        """Testa busca sem resultados."""
        mock_ydl_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {'entries': []}
        
        results = extractor.search_videos("busca inexistente")
        
        assert len(results) == 0
    
    @patch('yt_dlp.YoutubeDL')
    def test_search_videos_no_entries(self, mock_ydl, extractor):
        """Testa busca com resultado sem entries."""
        mock_ydl_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {}
        
        results = extractor.search_videos("teste")
        
        assert len(results) == 0
    
    @patch('yt_dlp.YoutubeDL')
    def test_extract_video_info_success(self, mock_ydl, extractor, mock_ydl_info_result):
        """Testa extração de informações com sucesso."""
        mock_ydl_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = mock_ydl_info_result
        
        info = extractor.extract_video_info("https://www.youtube.com/watch?v=test_video_123")
        
        assert info['id'] == 'test_video_123'
        assert info['title'] == 'Vídeo de Teste Completo'
        assert info['duration'] == 300
        assert info['uploader'] == 'Canal de Teste'
        assert 'formats' in info
        assert len(info['formats']) == 2
    
    @patch('yt_dlp.YoutubeDL')
    def test_extract_video_info_too_short(self, mock_ydl, extractor):
        """Testa extração de vídeo muito curto."""
        mock_ydl_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        short_video_info = {
            'id': 'short_video',
            'duration': 3,  # Menor que 5 segundos
            'title': 'Vídeo Curto'
        }
        mock_ydl_instance.extract_info.return_value = short_video_info
        
        with pytest.raises(VideoTooShortError) as exc_info:
            extractor.extract_video_info("https://www.youtube.com/watch?v=short_video")
        
        assert "muito curto" in str(exc_info.value)
    
    @patch('yt_dlp.YoutubeDL')
    def test_extract_video_info_private(self, mock_ydl, extractor):
        """Testa extração de vídeo privado."""
        mock_ydl_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        # Simular erro de vídeo privado
        mock_ydl_instance.extract_info.side_effect = Exception(" vídeo é privado ")
        
        with pytest.raises(VideoUnavailableError) as exc_info:
            extractor.extract_video_info("https://www.youtube.com/watch?v=private_video")
        
        assert "privado" in str(exc_info.value).lower()
        assert exc_info.value.details['unavailable_reason'] == 'private'
    
    @patch('yt_dlp.YoutubeDL')
    def test_download_segment_success(self, mock_ydl, extractor):
        """Testa download de segmento com sucesso."""
        mock_ydl_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        # Mock do extract_info
        mock_ydl_instance.extract_info.return_value = {
            'id': 'test_video_123',
            'duration': 60
        }
        
        # Mock do glob para simular arquivo criado
        with patch('glob.glob', return_value=['/tmp/segment_file.mp4']):
            with patch('pathlib.Path.exists', return_value=True):
                segment_path = extractor.download_segment(
                    "https://www.youtube.com/watch?v=test_video_123", 
                    10, 
                    5
                )
                
                assert segment_path.endswith('.mp4')
                mock_ydl_instance.extract_info.assert_called_once()
    
    def test_download_segment_invalid_params(self, extractor):
        """Testa download com parâmetros inválidos."""
        # Tempo negativo
        with pytest.raises(ValueError):
            extractor.download_segment("https://example.com", -1, 5)
        
        # Duração zero
        with pytest.raises(ValueError):
            extractor.download_segment("https://example.com", 0, 0)
        
        # Duração muito longa
        with pytest.raises(ValueError):
            extractor.download_segment("https://example.com", 0, 400)  # > 300s
    
    def test_format_filtering(self, extractor):
        """Testa filtragem de formatos."""
        formats = [
            {'format_id': 'low', 'height': 240, 'width': 426},
            {'format_id': 'medium', 'height': 480, 'width': 854},
            {'format_id': 'high', 'height': 720, 'width': 1280},
            {'format_id': 'ultra', 'height': 1080, 'width': 1920},
            {'format_id': 'invalid', 'height': 0},  # Deve ser filtrado
        ]
        
        filtered = extractor._extract_format_info(formats)
        
        assert len(filtered) == 3  # Apenas 480p, 720p, 1080p
        assert all(fmt['height'] >= 360 for fmt in filtered)
        assert all(fmt['height'] <= 1080 for fmt in filtered)


class TestSegmentProcessor:
    """Testes para SegmentProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Fixture para criar instância do processador."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield SegmentProcessor(temp_dir=temp_dir)
    
    @pytest.fixture
    def mock_video_path(self):
        """Mock para caminho de vídeo."""
        return "/path/to/test_video.mp4"
    
    @pytest.fixture
    def mock_ffprobe_output(self):
        """Mock para saída do ffprobe."""
        return {
            "format": {
                "duration": "120.5",
                "bit_rate": "1000000",
                "format_name": "mp4",
                "format_long_name": "MP4 (MPEG-4 Part 14)"
            },
            "streams": [
                {
                    "index": 0,
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1280,
                    "height": 720,
                    "r_frame_rate": "30/1",
                    "duration": "120.5",
                    "bit_rate": "800000"
                },
                {
                    "index": 1,
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "sample_rate": "48000",
                    "channels": 2,
                    "duration": "120.5",
                    "bit_rate": "128000"
                }
            ]
        }
    
    def test_initialization(self, processor):
        """Testa inicialização do processador."""
        assert processor.temp_dir.exists()
    
    @patch('subprocess.run')
    def test_ffmpeg_check_success(self, mock_run, processor):
        """Testa verificação do FFmpeg com sucesso."""
        # Mock para simulação de verificação do FFmpeg
        mock_run.return_value = Mock(returncode=0, stdout="ffmpeg version 4.0.0\n")
        
        # Não deve raise exception
        processor._check_ffmpeg()
    
    @patch('subprocess.run')
    def test_ffmpeg_check_failure(self, mock_run, processor):
        """Testa verificação do FFmpeg com falha."""
        mock_run.side_effect = FileNotFoundError("ffmpeg not found")
        
        with pytest.raises(VideoProcessingError) as exc_info:
            processor._check_ffmpeg()
        
        assert "FFmpeg não está instalado" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_extract_segment_success(self, mock_exists, mock_run, processor, mock_video_path):
        """Testa extração de segmento com sucesso."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        # Criar arquivo de saída mock
        mock_output_path = Path(processor.temp_dir) / "segment_10_5s.mp4"
        mock_exists.side_effect = lambda: True  # Para o arquivo de saída também
        
        result = processor.extract_segment(mock_video_path, 10, 5)
        
        assert result.endswith('.mp4')
        mock_run.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_extract_segment_file_not_found(self, mock_exists, processor):
        """Testa extração com arquivo não encontrado."""
        mock_exists.return_value = False
        
        with pytest.raises(VideoProcessingError) as exc_info:
            processor.extract_segment("/nonexistent/video.mp4", 0, 5)
        
        assert "não encontrado" in str(exc_info.value)
    
    def test_extract_segment_invalid_params(self, processor):
        """Testa extração com parâmetros inválidos."""
        with pytest.raises(ValueError):
            processor.extract_segment("/test/video.mp4", -1, 5)  # Start negativo
        
        with pytest.raises(ValueError):
            processor.extract_segment("/test/video.mp4", 0, 0)  # Duração zero
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_normalize_video_success(self, mock_exists, mock_run, processor):
        """Testa normalização de vídeo com sucesso."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="")
        
        mock_input = "/test/input.mp4"
        mock_output = processor.temp_dir / "normalized_input.mp4"
        mock_exists.side_effect = lambda: True
        
        result = processor.normalize_video(mock_input, target_resolution="720p")
        
        assert result.endswith('.mp4')
        mock_run.assert_called_once()
    
    def test_normalize_video_unsupported_resolution(self, processor):
        """Testa normalização com resolução não suportada."""
        with pytest.raises(ValueError) as exc_info:
            processor.normalize_video("/test/video.mp4", target_resolution="4k")
        
        assert "Resolução não suportada" in str(exc_info.value)
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_get_video_info_success(self, mock_exists, mock_run, processor, mock_ffprobe_output):
        """Testa obtenção de informações com sucesso."""
        mock_exists.return_value = True
        
        # Mock do ffprobe
        import json
        mock_run.return_value = Mock(
            returncode=0, 
            stdout=json.dumps(mock_ffprobe_output)
        )
        
        info = processor.get_video_info("/test/video.mp4")
        
        assert 'general' in info
        assert 'video_stream' in info
        assert 'audio_stream' in info
        assert info['general']['duration'] == 120.5
        assert info['video_stream']['width'] == 1280
        assert info['video_stream']['height'] == 720
    
    @patch('subprocess.run')
    def test_get_video_info_ffprobe_error(self, mock_run, processor):
        """Testa obtenção de informações com erro do ffprobe."""
        mock_run.return_value = Mock(returncode=1, stderr="Error message")
        
        with pytest.raises(VideoProcessingError) as exc_info:
            processor.get_video_info("/test/video.mp4")
        
        assert "Erro no FFprobe" in str(exc_info.value)
    
    def test_get_video_duration(self, processor):
        """Testa obtenção rápida de duração."""
        with patch.object(processor, 'get_video_info') as mock_get_info:
            mock_get_info.return_value = {'general': {'duration': 90.5}}
            
            duration = processor.get_video_duration("/test/video.mp4")
            
            assert duration == 90.5
            mock_get_info.assert_called_once_with("/test/video.mp4")


class TestErrorHandling:
    """Testes para tratamento de erros."""
    
    def test_network_error_detection(self):
        """Testa detecção de erros de rede."""
        extractor = YouTubeExtractor(temp_dir="/tmp")
        
        # Teste de detecção de erro de rede
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl_instance = Mock()
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
            
            # Simular erro de rede
            mock_ydl_instance.extract_info.side_effect = Exception("conexão esgotada")
            
            with pytest.raises(NetworkError):
                extractor.extract_video_info("https://youtube.com/watch?v=test")
    
    def test_private_video_error(self):
        """Testa detecção de vídeo privado."""
        extractor = YouTubeExtractor(temp_dir="/tmp")
        
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl_instance = Mock()
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
            
            # Simular vídeo privado
            mock_ydl_instance.extract_info.side_effect = Exception("Private video")
            
            with pytest.raises(VideoUnavailableError) as exc_info:
                extractor.extract_video_info("https://youtube.com/watch?v=private")
            
            assert exc_info.value.details['unavailable_reason'] == 'private'


if __name__ == "__main__":
    # Executar testes se executado diretamente
    pytest.main([__file__, "-v"])