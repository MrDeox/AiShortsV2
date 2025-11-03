"""
Testes para o sistema Kokoro TTS
Validação completa do módulo de narração
"""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import soundfile as sf

# Importar módulo a ser testado
import sys
sys.path.append('/workspace')
from src.tts.kokoro_tts import KokoroTTSClient


class TestKokoroTTSClient(unittest.TestCase):
    """Testes para KokoroTTSClient"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = KokoroTTSClient(
            output_dir=self.temp_dir,
            voice_name='af_diamond',
            speed=1.0
        )
    
    def test_initialization(self):
        """Testa inicialização do cliente"""
        self.assertEqual(self.client.lang_code, 'p')
        self.assertEqual(self.client.voice_name, 'af_diamond')
        self.assertEqual(self.client.speed, 1.0)
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_get_voice_list(self):
        """Testa listagem de vozes disponíveis"""
        voices = self.client.get_voice_list()
        
        self.assertIsInstance(voices, dict)
        self.assertIn('af_diamond', voices)
        self.assertIn('af_heart', voices)
        self.assertIn('am_oreo', voices)
        self.assertTrue(len(voices) > 0)
    
    def test_set_voice_valid(self):
        """Testa mudança de voz válida"""
        original_voice = self.client.voice_name
        
        self.client.set_voice('af_heart')
        self.assertEqual(self.client.voice_name, 'af_heart')
        
        self.client.set_voice(original_voice)  # Restaurar
    
    def test_set_voice_invalid(self):
        """Testa mudança de voz inválida"""
        with self.assertRaises(ValueError):
            self.client.set_voice('voce_inexistente')
    
    def test_set_speed_valid(self):
        """Testa configuração válida de velocidade"""
        self.client.set_speed(1.5)
        self.assertEqual(self.client.speed, 1.5)
        
        self.client.set_speed(0.8)
        self.assertEqual(self.client.speed, 0.8)
    
    def test_set_speed_invalid(self):
        """Testa configuração inválida de velocidade"""
        with self.assertRaises(ValueError):
            self.client.set_speed(0.1)  # Muito baixo
            
        with self.assertRaises(ValueError):
            self.client.set_speed(3.0)  # Muito alto
    
    @patch('src.tts.kokoro_tts.KPipeline')
    @patch('src.tts.kokoro_tts.sf')
    def test_text_to_speech_basic(self, mock_sf, mock_pipeline):
        """Testa conversão básica de texto para áudio"""
        # Mock do pipeline
        mock_gen = MagicMock()
        mock_gen.__iter__.return_value = [
            ('texto', 'fonemas', [1.0, 2.0, 3.0])  # Simular áudio
        ]
        mock_pipeline.return_value.return_value = mock_gen
        
        # Mock do soundfile
        mock_sf.write = MagicMock()
        
        # Teste
        result = self.client.text_to_speech("Texto de teste", "teste")
        
        self.assertTrue(result['success'])
        self.assertIn('audio_path', result)
        self.assertIn('duration', result)
        self.assertEqual(result['voice'], 'af_diamond')
        mock_sf.write.assert_called_once()
    
    def test_text_to_speech_empty_text(self):
        """Testa comportamento com texto vazio"""
        with self.assertRaises(ValueError):
            self.client.text_to_speech("")
        
        with self.assertRaises(ValueError):
            self.client.text_to_speech("   ")
    
    @patch('src.tts.kokoro_tts.KPipeline')
    @patch('src.tts.kokoro_tts.sf')
    def test_script_to_audio_mock(self, mock_sf, mock_pipeline):
        """Testa conversão de roteiro usando mocks"""
        from src.models.script_models import Script, GeneratedTheme, ScriptSection, ThemeCategory
        
        # Criar roteiro de teste
        theme = GeneratedTheme(
            main_title="Tema de teste",
            category=ThemeCategory.SCIENCE,
            keywords=["teste", "exemplo"],
            target_audience="geral"
        )
        
        sections = [
            ScriptSection(type="hook", content="Você sabia que..."),
            ScriptSection(type="development", content="Este é o desenvolvimento do tema."),
            ScriptSection(type="conclusion", content="Incrível, né?")
        ]
        
        script = Script(
            id="test_script",
            theme=theme,
            sections=sections
        )
        
        # Mock do pipeline
        mock_gen = MagicMock()
        mock_gen.__iter__.return_value = [
            ('texto', 'fonemas', [1.0, 2.0])
        ]
        mock_pipeline.return_value.return_value = mock_gen
        
        # Mock do soundfile
        mock_sf.write = MagicMock()
        
        # Teste
        result = self.client.script_to_audio(script, "teste_roteiro")
        
        self.assertEqual(result['script_id'], 'test_script')
        self.assertEqual(result['theme'], 'Tema de teste')
        self.assertEqual(result['sections_count'], 3)
        self.assertIn('total_duration', result)
        self.assertIn('voice_info', result)
    
    @patch('src.tts.kokoro_tts.sf')
    def test_optimize_for_platform(self, mock_sf):
        """Testa otimização para plataformas"""
        # Criar arquivo de teste
        test_audio = os.path.join(self.temp_dir, "test.wav")
        
        # Simular áudio de 50 segundos
        mock_sf.read.return_value = ([1.0] * 50 * 24000, 24000)
        
        result = self.client.optimize_for_platform(test_audio, "tiktok")
        
        self.assertEqual(result['platform'], 'tiktok')
        self.assertEqual(result['original_duration'], 50.0)
        self.assertEqual(result['platform_max_duration'], 60)
        self.assertTrue(result['is_compliant'])
        self.assertTrue(result['is_optimal'])
    
    def test_optimize_for_platform_reels(self):
        """Testa otimização específica para Instagram Reels"""
        test_audio = os.path.join(self.temp_dir, "reels_test.wav")
        
        # Simular áudio de 80 segundos
        with patch('src.tts.kokoro_tts.sf') as mock_sf:
            mock_sf.read.return_value = ([1.0] * 80 * 24000, 24000)
            
            result = self.client.optimize_for_platform(test_audio, "reels")
            
            self.assertEqual(result['platform'], 'reels')
            self.assertEqual(result['platform_max_duration'], 90)
            self.assertEqual(result['platform_recommended_duration'], 60)
            self.assertTrue(result['is_compliant'])  # 80s < 90s
    
    def tearDown(self):
        """Cleanup após cada teste"""
        # Remover arquivos temporários
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestTTSIntegration(unittest.TestCase):
    """Testes de integração do sistema TTS"""
    
    def test_pipeline_integration(self):
        """Testa integração com pipeline completo"""
        # Este teste verificaria a integração com:
        # Theme Generator -> Script Generator -> Validator -> TTS
        
        # Por enquanto, apenas verifica se os imports funcionam
        try:
            from src.tts.kokoro_tts import KokoroTTSClient
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Falha na importação: {e}")
    
    @unittest.skip("Requer instalação completa do Kokoro")
    def test_real_tts_generation(self):
        """Teste real de geração TTS (requer setup completo)"""
        client = KokoroTTSClient()
        
        test_text = "Este é um teste real do sistema de narração Kokoro."
        result = client.text_to_speech(test_text, "teste_real")
        
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['audio_path']))
        
        # Verificar duração razoável
        self.assertGreater(result['duration'], 0.5)
        self.assertLess(result['duration'], 10.0)


def run_performance_tests():
    """Executa testes de performance do sistema TTS"""
    print("\n🚀 Executando testes de performance TTS...")
    
    client = KokoroTTSClient(output_dir="/tmp/tts_performance")
    
    # Teste de velocidade
    import time
    
    # Texto de teste
    test_text = """
    Você sabia que os golfinhos têm nomes uns para os outros? 
    Cada golfinho desenvolve um assobio único que funciona como nome, 
    e outros golfinhos podem chamá-los usando esse som específico. 
    Isso foi descoberto em estudos que mostraram que golfinhos 
    respondem ao seu 'nome' mesmo quando chamado por outros indivíduos.
    """
    
    # Teste de performance
    start_time = time.time()
    
    with patch('src.tts.kokoro_tts.KPipeline') as mock_pipeline:
        # Mock rápido para teste de performance
        mock_gen = MagicMock()
        mock_gen.__iter__.return_value = [
            ('texto', 'fonemas', [1.0] * 1000)
        ]
        mock_pipeline.return_value.return_value = mock_gen
        
        with patch('src.tts.kokoro_tts.sf'):
            result = client.text_to_speech(test_text, "perf_test")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"⏱️ Tempo de processamento: {duration:.2f}s")
    print(f"📊 Resultado: {result['success']}")
    
    # Cleanup
    import shutil
    shutil.rmtree("/tmp/tts_performance", ignore_errors=True)


if __name__ == "__main__":
    print("🎙️ Testes do Sistema Kokoro TTS - AiShorts v2.0")
    print("=" * 60)
    
    # Executar testes unitários
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Executar testes de performance
    run_performance_tests()
    
    print("\n✅ Todos os testes concluídos!")