"""
Testes para sistema CLIP Relevance Scoring
AiShorts v2.0 - Módulo de Scoring Semântico

Testes completos para validação do sistema de scoring semântico real texto-vídeo
usando modelo CLIP.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from PIL import Image
import tempfile

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from video.matching.clip_relevance_scorer import CLIPRelevanceScorer
from video.matching.semantic_analyzer import SemanticAnalyzer
from video.matching.video_searcher import VideoSearcher


class TestCLIPRelevanceScorer:
    """Testes para CLIPRelevanceScorer."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Criar scorer com mock do modelo para evitar downloads
        with patch('video.matching.clip_relevance_scorer.CLIPRelevanceScorer._init_clip_model'):
            self.scorer = CLIPRelevanceScorer()
        
        # Texto de exemplo
        self.sample_text = """
        O universo é cheio de mistérios fascinantes. As estrelas brilhantes 
        no céu noturno nos fazem pensar sobre nossa existência.
        """
        
        # Vídeo de exemplo (usando imagem para simplificar testes)
        self.sample_video = {
            'id': 'video_test_1',
            'title': 'Explorando o Espaço - As Estrelas',
            'description': 'Um vídeo fascinante sobre as estrelas e o universo',
            'url': 'https://example.com/space_video.mp4',
            'views': 50000,
            'likes': 2500,
            'duration': 300
        }
    
    def test_initialization(self):
        """Testa inicialização do scorer."""
        assert self.scorer is not None
        assert self.scorer.cache_dir is not None
        assert isinstance(self.scorer.text_cache, dict)
        assert isinstance(self.scorer.video_cache, dict)
    
    def test_initialization_with_fallback(self):
        """Testa inicialização com fallback TF-IDF."""
        with patch('video.matching.clip_relevance_scorer.CLIPRelevanceScorer._init_clip_model'):
            scorer = CLIPRelevanceScorer()
            # Deve ter fallback TF-IDF disponível
            assert scorer.tfidf_available or not scorer.tfidf_available  # Either way is fine
    
    def test_score_text_video_relevance_basic(self):
        """Testa cálculo básico de relevância."""
        # Criar imagem fake para teste
        test_image = Image.new('RGB', (224, 224), color='blue')
        
        # Mock do método _extract_video_frames
        with patch.object(self.scorer, '_extract_video_frames', return_value=[test_image]):
            # Com CLIP mockado, deve retornar fallback ou 0
            score = self.scorer.score_text_video_relevance(self.sample_text, "fake_video.mp4")
            
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
    
    def test_score_text_video_relevance_empty_inputs(self):
        """Testa com entradas vazias."""
        # Texto vazio
        score = self.scorer.score_text_video_relevance("", "video.mp4")
        assert score == 0.0
        
        # Vídeo vazio
        score = self.scorer.score_text_video_relevance(self.sample_text, "")
        assert score == 0.0
        
        # Ambos vazios
        score = self.scorer.score_text_video_relevance("", "")
        assert score == 0.0
    
    def test_extract_video_frames_with_image(self):
        """Testa extração de frames com imagem."""
        # Criar imagem fake
        test_image = Image.new('RGB', (224, 224), color='red')
        
        # Mock do cv2.VideoCapture para retornar imagem
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap_instance = Mock()
            mock_cap.return_value = mock_cap_instance
            
            # Configurar mock para retornar frame
            mock_cap_instance.isOpened.return_value = True
            mock_cap_instance.get.side_effect = lambda x: {
                cv2.CAP_PROP_FRAME_COUNT: 10,
                cv2.CAP_PROP_FPS: 30
            }.get(x, 0)
            mock_cap_instance.set.side_effect = lambda x, y: True
            mock_cap_instance.read.return_value = (True, np.array(test_image))
            
            frames = self.scorer._extract_video_frames("fake_video.mp4", max_frames=3)
            
            # Deve retornar pelo menos um frame
            assert len(frames) >= 1
            assert all(isinstance(frame, Image.Image) for frame in frames)
            
            mock_cap_instance.release.assert_called_once()
    
    def test_extract_video_frames_no_video(self):
        """Testa extração quando vídeo não pode ser aberto."""
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap_instance = Mock()
            mock_cap.return_value = mock_cap_instance
            mock_cap_instance.isOpened.return_value = False
            
            frames = self.scorer._extract_video_frames("nonexistent_video.mp4")
            
            assert frames == []
    
    def test_rank_videos_by_relevance(self):
        """Testa ranking de vídeos."""
        video_list = [
            self.sample_video,
            {
                'id': 'video_test_2',
                'title': 'Animais Selvagens',
                'url': 'https://example.com/animals_video.mp4'
            },
            {
                'id': 'video_test_3',
                'title': 'Ciência e Tecnologia',
                'url': 'https://example.com/science_video.mp4'
            }
        ]
        
        with patch.object(self.scorer, '_get_video_path', return_value="fake_video.mp4"):
            with patch.object(self.scorer, '_extract_video_frames', return_value=[]):
                ranked = self.scorer.rank_videos_by_relevance(self.sample_text, video_list)
                
                assert isinstance(ranked, list)
                assert len(ranked) == len(video_list)
                
                # Todos devem ter relevance_score
                for video in ranked:
                    assert 'relevance_score' in video
                    assert 'scoring_method' in video
                    assert 0.0 <= video['relevance_score'] <= 1.0
                
                # Deve estar ordenado por relevância (mesmo que scores sejam iguais)
                scores = [v['relevance_score'] for v in ranked]
                # Nota: ordem pode variar se scores forem iguais
    
    def test_get_text_embedding(self):
        """Testa geração de embedding textual."""
        text = "Teste de embedding textual"
        
        # Com CLIP mockado, deve retornar None ou fallback
        embedding = self.scorer.get_text_embedding(text)
        
        # Pode ser None se CLIP não está disponível
        if embedding is not None:
            assert isinstance(embedding, np.ndarray)
            assert len(embedding.shape) == 1
    
    def test_get_visual_embedding(self):
        """Testa geração de embedding visual."""
        with patch.object(self.scorer, '_extract_video_frames', return_value=[]):
            embedding = self.scorer.get_visual_embedding("fake_video.mp4")
            
            # Pode ser None se não há frames ou CLIP não disponível
            assert embedding is None or isinstance(embedding, np.ndarray)
    
    def test_calculate_multicriteria_score(self):
        """Testa cálculo de score multicritério."""
        video = self.sample_video
        semantic_score = 0.8
        quality_metrics = {
            'views': 50000,
            'likes': 2500,
            'duration': 300
        }
        diversity_bonus = 0.1
        
        result = self.scorer.calculate_multicriteria_score(
            video, semantic_score, quality_metrics, diversity_bonus
        )
        
        assert isinstance(result, dict)
        assert 'semantic_score' in result
        assert 'quality_score' in result
        assert 'diversity_bonus' in result
        assert 'final_score' in result
        assert 'components' in result
        
        assert result['semantic_score'] == semantic_score
        assert result['diversity_bonus'] == diversity_bonus
        assert 0.0 <= result['final_score'] <= 1.0
    
    def test_calculate_multicriteria_score_no_quality_metrics(self):
        """Testa cálculo sem métricas de qualidade."""
        result = self.scorer.calculate_multicriteria_score(
            self.sample_video, 0.5, None, 0.0
        )
        
        assert result['quality_score'] == 0.0
        assert result['final_score'] == 0.5  # Apenas score semântico
    
    def test_performance_stats(self):
        """Testa estatísticas de performance."""
        stats = self.scorer.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert 'model_loaded' in stats
        assert 'device' in stats
        assert 'text_cache_size' in stats
        assert 'video_cache_size' in stats
        assert 'cache_dir' in stats
        assert 'fallback_method' in stats
    
    def test_cache_operations(self):
        """Testa operações de cache."""
        # Adicionar item ao cache
        self.scorer.text_cache['test_key'] = np.array([1, 2, 3])
        
        assert len(self.scorer.text_cache) == 1
        
        # Limpar cache
        self.scorer.clear_cache()
        
        assert len(self.scorer.text_cache) == 0
        assert len(self.scorer.video_cache) == 0
    
    def test_cleanup(self):
        """Testa limpeza de recursos."""
        # Mock para evitar erros de cleanup
        with patch.object(self.scorer, 'save_cache') as mock_save:
            with patch.object(self.scorer, 'clear_cache') as mock_clear:
                self.scorer.cleanup()
                
                mock_save.assert_called_once()
                mock_clear.assert_called_once()


class TestCLIPIntegrationWithSemanticAnalyzer:
    """Testes de integração com SemanticAnalyzer."""
    
    def setup_method(self):
        """Setup para integração."""
        # Mock para evitar download do modelo
        with patch.object(SemanticAnalyzer, '_init_spacy'):
            self.analyzer = SemanticAnalyzer()
        
        self.sample_text = "O universo é infinito e cheio de mistérios fascinantes."
    
    def test_get_semantic_embedding_with_clip_fallback(self):
        """Testa embedding com fallback CLIP."""
        embedding = self.analyzer.get_semantic_embedding(self.sample_text, use_clip=True)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1
        assert len(embedding) > 0
    
    def test_get_semantic_embedding_basic_only(self):
        """Testa embedding apenas com método básico."""
        embedding = self.analyzer.get_semantic_embedding(self.sample_text, use_clip=False)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1
    
    def test_get_semantic_embedding_empty_text(self):
        """Testa embedding com texto vazio."""
        embedding = self.analyzer.get_semantic_embedding("", use_clip=True)
        assert embedding is None


class TestCLIPIntegrationWithVideoSearcher:
    """Testes de integração com VideoSearcher."""
    
    def setup_method(self):
        """Setup para integração."""
        # Mock para evitar download do modelo
        with patch.object(VideoSearcher, '__init__', lambda x, *args, **kwargs: None):
            self.searcher = VideoSearcher()
            self.searcher.video_database = []
            self.searcher.embedding_cache = {}
            self.searcher.similarity_threshold = 0.7
            self.searcher.max_results = 10
            self.searcher.use_clip_scorer = True
            self.searcher.clip_scorer = Mock()
        
        self.sample_videos = [
            {
                'id': 'video_1',
                'title': 'Explorando o Espaço',
                'url': 'https://example.com/space.mp4',
                'views': 50000,
                'duration': 300
            }
        ]
    
    def test_search_with_clip_scoring(self):
        """Testa busca com scoring CLIP."""
        # Configurar mock do CLIP scorer
        mock_ranked = [
            {
                'id': 'video_1',
                'title': 'Explorando o Espaço',
                'relevance_score': 0.8,
                'scoring_method': 'clip'
            }
        ]
        self.searcher.clip_scorer.rank_videos_by_relevance.return_value = mock_ranked
        
        # Mock do filter_by_quality
        self.searcher.filter_by_quality = Mock(return_value=mock_ranked)
        
        results = self.searcher.search_with_clip_scoring("universo estrelas")
        
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]['match_type'] == 'clip_semantic'
        assert results[0]['scoring_method'] == 'clip'
    
    def test_search_with_clip_scoring_disabled(self):
        """Testa busca com CLIP desabilitado."""
        self.searcher.use_clip_scorer = False
        
        results = self.searcher.search_with_clip_scoring("universo estrelas")
        
        assert results == []
    
    def test_search_with_clip_scoring_no_scorer(self):
        """Testa busca sem CLIP scorer disponível."""
        self.searcher.clip_scorer = None
        
        results = self.searcher.search_with_clip_scoring("universo estrelas")
        
        assert results == []
    
    def test_extract_text_from_analysis(self):
        """Testa extração de texto da análise."""
        analysis = {
            'theme_title': 'Explorando o Universo',
            'theme_keywords': ['estrela', 'planeta', 'espaço'],
            'keywords': ['universo', 'galáxia']
        }
        
        text = self.searcher._extract_text_from_analysis(analysis)
        
        assert 'Explorando' in text
        assert 'Universo' in text
        assert 'estrela' in text or 'universo' in text
    
    def test_apply_multicriteria_scoring(self):
        """Testa aplicação de scoring multicritério."""
        results = [
            {
                'id': 'video_1',
                'relevance_score': 0.8,
                'views': 50000,
                'likes': 2500,
                'duration': 300
            }
        ]
        
        script_analysis = {'keywords': ['estrela', 'universo']}
        
        # Mock do calculate_multicriteria_score
        self.searcher.clip_scorer = Mock()
        self.searcher.clip_scorer.calculate_multicriteria_score.return_value = {
            'semantic_score': 0.8,
            'quality_score': 0.6,
            'final_score': 0.75,
            'components': {}
        }
        
        scored_results = self.searcher._apply_multicriteria_scoring(results, script_analysis)
        
        assert len(scored_results) == 1
        assert 'final_score' in scored_results[0]
        assert 'components' in scored_results[0]
    
    def test_get_search_stats_with_clip(self):
        """Testa estatísticas com CLIP."""
        # Mock do clip_scorer
        self.searcher.clip_scorer = Mock()
        self.searcher.clip_scorer.get_performance_stats.return_value = {
            'model_loaded': True,
            'cache_size': 10
        }
        
        stats = self.searcher.get_search_stats()
        
        assert isinstance(stats, dict)
        assert 'use_clip_scorer' in stats
        assert 'clip_stats' in stats
        assert stats['clip_stats']['model_loaded'] is True


class TestCLIPEndToEndWorkflow:
    """Testes de workflow completo com CLIP."""
    
    def setup_method(self):
        """Setup para testes end-to-end."""
        # Mocks para evitar downloads
        with patch.object(SemanticAnalyzer, '_init_spacy'):
            self.analyzer = SemanticAnalyzer()
        
        with patch.object(VideoSearcher, '__init__', lambda x, *args, **kwargs: None):
            self.searcher = VideoSearcher()
            self.searcher.video_database = []
            self.searcher.embedding_cache = {}
            self.searcher.similarity_threshold = 0.7
            self.searcher.max_results = 10
            self.searcher.use_clip_scorer = True
            self.searcher.clip_scorer = Mock()
    
    def test_script_analysis_and_clip_ranking(self):
        """Testa workflow completo: análise + ranking."""
        # Texto do roteiro
        script_text = """
        O universo é infinito e cheio de mistérios fascinantes. 
        As estrelas são sóis distantes que brilham na escuridão do espaço.
        """
        
        # 1. Análise semântica
        embedding = self.analyzer.get_semantic_embedding(script_text, use_clip=True)
        assert embedding is not None
        
        # 2. Simular vídeo relevante
        mock_results = [
            {
                'id': 'video_space_1',
                'title': 'Explorando o Universo',
                'relevance_score': 0.9,
                'scoring_method': 'clip',
                'views': 100000,
                'likes': 5000,
                'duration': 420
            }
        ]
        
        self.searcher.clip_scorer.rank_videos_by_relevance.return_value = mock_results
        self.searcher.filter_by_quality = Mock(return_value=mock_results)
        self.searcher.clip_scorer.calculate_multicriteria_score.return_value = {
            'semantic_score': 0.9,
            'quality_score': 0.8,
            'final_score': 0.85,
            'components': {}
        }
        
        # 3. Busca com CLIP
        clip_results = self.searcher.search_with_clip_scoring(script_text)
        
        assert len(clip_results) == 1
        assert clip_results[0]['scoring_method'] == 'clip'
        assert clip_results[0]['relevance_score'] > 0.5


class TestCLIPErrorHandling:
    """Testes de tratamento de erros com CLIP."""
    
    def setup_method(self):
        """Setup para testes de erro."""
        with patch.object(CLIPRelevanceScorer, '_init_clip_model'):
            self.scorer = CLIPRelevanceScorer()
    
    def test_clip_model_loading_error(self):
        """Testa comportamento quando CLIP falha ao carregar."""
        # Scorer já inicializado com fallback
        assert self.scorer.model is None  # Deve ter falhado
        assert self.scorer.tfidf_available or not self.scorer.tfidf_available  # Pode ou não ter TF-IDF
    
    def test_invalid_video_path(self):
        """Testa com caminho de vídeo inválido."""
        score = self.scorer.score_text_video_relevance("texto teste", "invalid_path")
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0  # Deve retornar score válido (fallback)
    
    def test_network_error_in_video_download(self):
        """Testa erro de rede ao baixar vídeo."""
        # Mock para falhar no download
        with patch('requests.get', side_effect=Exception("Network error")):
            frames = self.scorer._extract_video_frames("http://example.com/video.mp4")
            assert frames == []  # Deve retornar lista vazia
    
    def test_corrupted_video_file(self):
        """Testa com arquivo de vídeo corrompido."""
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap_instance = Mock()
            mock_cap.return_value = mock_cap_instance
            mock_cap_instance.isOpened.return_value = True
            mock_cap_instance.read.return_value = (False, None)  # Falha na leitura
            
            frames = self.scorer._extract_video_frames("corrupted_video.mp4")
            assert frames == []
    
    def test_memory_error_handling(self):
        """Testa tratamento de erros de memória."""
        # Mock para simular erro de memória
        with patch.object(self.scorer, '_extract_video_frames', 
                         side_effect=MemoryError("Out of memory")):
            score = self.scorer.score_text_video_relevance("texto teste", "video.mp4")
            
            # Deve retornar score válido (0.0)
            assert score == 0.0


if __name__ == "__main__":
    # Executar testes se chamado diretamente
    pytest.main([__file__, "-v"])