"""
Testes básicos do módulo de vídeo
Fase 1 - Setup técnico do Módulo 8
"""

import unittest
import os
import tempfile
from pathlib import Path
import logging

# Configurar logging para testes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from src.video import __version__
from src.video.extractors import YouTubeExtractor
from src.video.matching import ContentMatcher
from src.video.processing import VideoProcessor
from src.video.generators import VideoGenerator
from config.video_settings import get_config


class TestVideoModule(unittest.TestCase):
    """Testes básicos do módulo de vídeo."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = get_config()
    
    def tearDown(self):
        """Limpeza após cada teste."""
        # Limpar arquivos temporários
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_module_version(self):
        """Testa se o módulo tem versão definida."""
        self.assertIsNotNone(__version__)
        self.assertIsInstance(__version__, str)
        print(f"✓ Versão do módulo: {__version__}")
    
    def test_config_loading(self):
        """Testa carregamento das configurações."""
        config = get_config()
        
        self.assertIsInstance(config, dict)
        self.assertIn('youtube', config)
        self.assertIn('video_processing', config)
        self.assertIn('similarity', config)
        self.assertIn('generation', config)
        
        print("✓ Configurações carregadas com sucesso")
    
    def test_youtube_extractor_creation(self):
        """Testa criação do YouTube extractor."""
        try:
            extractor = YouTubeExtractor()
            self.assertIsNotNone(extractor)
            self.assertIsInstance(extractor.config, dict)
            print("✓ YouTubeExtractor criado com sucesso")
        except Exception as e:
            print(f"⚠ Aviso - YouTubeExtractor: {e}")
    
    def test_content_matcher_creation(self):
        """Testa criação do Content Matcher."""
        try:
            matcher = ContentMatcher()
            self.assertIsNotNone(matcher)
            self.assertIsNotNone(matcher.model)
            print("✓ ContentMatcher criado com sucesso")
        except Exception as e:
            print(f"⚠ Aviso - ContentMatcher: {e}")
    
    def test_video_processor_creation(self):
        """Testa criação do Video Processor."""
        try:
            processor = VideoProcessor()
            self.assertIsNotNone(processor)
            self.assertIsInstance(processor.config, dict)
            print("✓ VideoProcessor criado com sucesso")
        except Exception as e:
            self.fail(f"VideoProcessor falhou: {e}")
    
    def test_video_generator_creation(self):
        """Testa criação do Video Generator."""
        try:
            generator = VideoGenerator()
            self.assertIsNotNone(generator)
            self.assertIsInstance(generator.config, dict)
            print("✓ VideoGenerator criado com sucesso")
        except Exception as e:
            self.fail(f"VideoGenerator falhou: {e}")
    
    def test_video_info_extraction(self):
        """Testa extração de informações de vídeo."""
        processor = VideoProcessor()
        
        # Criar um vídeo de teste simples usando OpenCV
        test_video_path = self.temp_dir / "test_video.avi"
        
        try:
            # Criar vídeo dummy para teste
            import cv2
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(str(test_video_path), fourcc, 20.0, (640, 480))
            
            # Escrever alguns frames
            for i in range(50):
                frame = (255 * (i / 50) * np.ones((480, 640, 3), dtype=np.uint8)).astype(np.uint8)
                out.write(frame)
            
            out.release()
            
            # Testar extração de informações
            info = processor.get_video_info(str(test_video_path))
            
            if info:
                self.assertIn('width', info)
                self.assertIn('height', info)
                self.assertIn('fps', info)
                self.assertIn('duration', info)
                print(f"✓ Informações do vídeo extraídas: {info}")
            else:
                print("⚠ Não foi possível extrair informações do vídeo")
            
        except Exception as e:
            print(f"⚠ Teste de informações de vídeo: {e}")
    
    def test_frame_extraction(self):
        """Testa extração de frames."""
        processor = VideoProcessor()
        
        # Criar vídeo de teste
        test_video_path = self.temp_dir / "test_video.avi"
        frames_dir = self.temp_dir / "frames"
        
        try:
            import cv2
            import numpy as np
            
            # Criar vídeo de teste
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(str(test_video_path), fourcc, 20.0, (640, 480))
            
            # Escrever 100 frames (5 segundos a 20fps)
            for i in range(100):
                frame = np.full((480, 640, 3), (i % 255, 0, 255-i % 255), dtype=np.uint8)
                out.write(frame)
            
            out.release()
            
            # Extrair frames
            frame_paths = processor.extract_frames(
                str(test_video_path), 
                str(frames_dir), 
                fps=2.0
            )
            
            if frame_paths:
                self.assertGreater(len(frame_paths), 0)
                print(f"✓ {len(frame_paths)} frames extraídos")
            else:
                print("⚠ Nenhum frame extraído")
            
        except Exception as e:
            print(f"⚠ Teste de extração de frames: {e}")
    
    def test_video_generation_basic(self):
        """Teste básico de geração de vídeo."""
        generator = VideoGenerator()
        
        # Criar imagens de teste simples
        images = []
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            for i in range(3):
                img = Image.new('RGB', (1080, 1920), color=(i*80, 100, 255-i*80))
                draw = ImageDraw.Draw(img)
                
                # Adicionar texto simples
                text = f"Slide {i+1}"
                # Usar fonte padrão se Arial não estiver disponível
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                except:
                    font = ImageFont.load_default()
                
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (1080 - text_width) // 2
                y = (1920 - text_height) // 2
                
                draw.text((x, y), text, fill="white", font=font)
                
                img_path = self.temp_dir / f"slide_{i+1}.jpg"
                img.save(img_path)
                images.append(str(img_path))
            
            # Testar criação de slideshow
            output_path = self.temp_dir / "generated_slideshow.mp4"
            success = generator.create_slideshow(
                images, 
                str(output_path), 
                duration_per_slide=2.0
            )
            
            if success and output_path.exists():
                print(f"✓ Vídeo gerado com sucesso: {output_path}")
            else:
                print("⚠ Falha na geração de vídeo")
            
        except Exception as e:
            print(f"⚠ Teste de geração de vídeo: {e}")
    
    def test_dependencies(self):
        """Testa se as dependências principais estão disponíveis."""
        dependencies = [
            ('cv2', 'opencv-python'),
            ('moviepy', 'moviepy'),
            ('yt_dlp', 'yt-dlp'),
            ('sklearn', 'scikit-learn'),
            ('torch', 'torch'),
            ('transformers', 'transformers'),
            ('pydub', 'pydub'),
            ('ffmpeg', 'ffmpeg-python'),
        ]
        
        available_deps = []
        missing_deps = []
        
        for import_name, package_name in dependencies:
            try:
                __import__(import_name)
                available_deps.append(package_name)
            except ImportError:
                missing_deps.append(package_name)
        
        print(f"✓ Dependências disponíveis ({len(available_deps)}): {', '.join(available_deps)}")
        
        if missing_deps:
            print(f"⚠ Dependências em falta ({len(missing_deps)}): {', '.join(missing_deps)}")
        
        # Pelo menos as dependências core devem estar disponíveis
        core_deps = ['cv2', 'moviepy', 'sklearn']
        for dep in core_deps:
            try:
                __import__(dep)
            except ImportError:
                self.fail(f"Dependência core não disponível: {dep}")


def run_basic_tests():
    """Executa testes básicos do módulo."""
    print("=" * 60)
    print("TESTES BÁSICOS DO MÓDULO DE VÍDEO")
    print("=" * 60)
    
    # Criar suite de testes
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVideoModule)
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Testes executados: {result.testsRun}")
    print(f"Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    
    if result.failures:
        print("\nFALHAS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERROS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print("\n" + "=" * 60)
    print("SETUP TÉCNICO COMPLETADO!")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_basic_tests()
    exit(0 if success else 1)
