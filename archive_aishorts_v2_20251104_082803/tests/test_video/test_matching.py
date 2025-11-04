"""
Testes para o sistema de matching entre roteiro e vídeo.
Testa análise semântica e busca inteligente de vídeos.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

import sys
import os

# Adiciona o diretório src ao path de forma segura
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, src_path)

# Importa diretamente os módulos para evitar problemas com o módulo video
from video.matching.semantic_analyzer import SemanticAnalyzer
from video.matching.video_searcher import VideoSearcher, VideoInfo


class TestSemanticAnalyzer:
    """Testes para o SemanticAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Cria instância do analisador para testes."""
        return SemanticAnalyzer()
    
    def test_extract_keywords_basic(self, analyzer):
        """Testa extração básica de palavras-chave."""
        text = "Os golfinhos são animais incríveis que vivem no oceano."
        keywords = analyzer.extract_keywords(text, max_keywords=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        assert 'golfinho' in keywords or 'animal' in keywords
        assert 'são' not in keywords  # Stop word
    
    def test_extract_keywords_with_spacy(self):
        """Testa extração de palavras-chave com spaCy."""
        with patch('video.matching.semantic_analyzer.spacy.load') as mock_load:
            # Mock do modelo spaCy
            mock_nlp = MagicMock()
            mock_token = MagicMock()
            mock_token.text = 'golfinhos'
            mock_token.lemma_ = 'golfinho'
            mock_token.is_stop = False
            mock_token.is_punct = False
            mock_token.is_space = False
            mock_token.pos_ = 'NOUN'
            mock_token.has_vector = True
            mock_token.vector = np.array([0.1] * 300)
            
            mock_doc = MagicMock()
            mock_doc.__iter__ = lambda self: iter([mock_token])
            mock_doc.has_vector = True
            mock_doc.vector = np.array([0.1] * 300)
            
            mock_nlp.return_value = mock_doc
            
            analyzer = SemanticAnalyzer()
            analyzer.use_spacy = True
            analyzer.nlp = mock_nlp
            
            text = "golfinhos incrível oceano"
            keywords = analyzer.extract_keywords(text)
            
            assert isinstance(keywords, list)
            assert len(keywords) > 0
    
    def test_analyze_tone_positive(self, analyzer):
        """Testa análise de tom positivo."""
        text = "Este é um vídeo incrível e fantásticos que me deixa muito feliz!"
        tone = analyzer.analyze_tone(text)
        
        assert isinstance(tone, dict)
        assert 'positive' in tone
        assert 'negative' in tone
        assert 'neutral' in tone
        assert tone['positive'] > tone['negative']
        assert abs(sum(tone.values()) - 1.0) < 0.01  # Soma deve ser aproximadamente 1
    
    def test_analyze_tone_negative(self, analyzer):
        """Testa análise de tom negativo."""
        text = "Este vídeo é terrível e me deixa muito triste."
        tone = analyzer.analyze_tone(text)
        
        assert tone['negative'] > tone['positive']
        assert tone['negative'] > 0.5
    
    def test_categorize_content_animals(self, analyzer):
        """Testa categorização de conteúdo sobre animais."""
        text = "Os golfinhos são mamíferos marinhos muito inteligentes que nadam no oceano."
        category, confidence = analyzer.categorize_content(text)
        
        assert isinstance(category, str)
        assert isinstance(confidence, float)
        assert category == 'ANIMALS'
        assert confidence > 0.5
    
    def test_categorize_content_space(self, analyzer):
        """Testa categorização de conteúdo sobre espaço."""
        text = "O universo é cheio de galáxias distantes e planetas incríveis."
        category, confidence = analyzer.categorize_content(text)
        
        assert category == 'SPACE'
        assert confidence > 0.3
    
    def test_get_semantic_embedding(self, analyzer):
        """Testa geração de embedding semântico."""
        text = "Golfinhos nadando no oceano azul."
        embedding = analyzer.get_semantic_embedding(text)
        
        if analyzer.use_spacy:
            assert embedding is not None
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) > 0
        else:
            # Testa fallback
            assert embedding is not None
            assert isinstance(embedding, np.ndarray)
    
    def test_calculate_similarity(self, analyzer):
        """Testa cálculo de similaridade semântica."""
        text1 = "Golfinhos são animais marinhos incríveis."
        text2 = "Delfins nadam nos oceanos azuis."
        
        similarity = analyzer.calculate_similarity(text1, text2)
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        
        # Textos similares devem ter alta similaridade
        if analyzer.use_spacy:
            assert similarity > 0.1  # Valor mínimo para textos relacionados
    
    def test_analyze_script_complete(self, analyzer):
        """Testa análise completa de um roteiro."""
        script = """
        Este vídeo incrível mostra golfinhos nadando em oceanos cristalinos.
        Você vai ficar impressionado com a inteligência destes mamíferos marinhos.
        Os golfinhos realizam truques espetaculares e demonstram amor pelos humanos.
        """
        
        result = analyzer.analyze_script(script)
        
        assert isinstance(result, dict)
        assert 'keywords' in result
        assert 'tone' in result
        assert 'category' in result
        assert 'category_confidence' in result
        assert 'semantic_vector' in result
        
        assert result['category'] == 'ANIMALS'
        assert result['tone']['positive'] > 0.5
        assert isinstance(result['keywords'], list)
        assert len(result['keywords']) > 0


class TestVideoSearcher:
    """Testes para o VideoSearcher."""
    
    @pytest.fixture
    def searcher(self):
        """Cria instância do buscador para testes."""
        return VideoSearcher()
    
    def test_search_by_keywords(self, searcher):
        """Testa busca por palavras-chave."""
        keywords = ['golfinho', 'oceano', 'inteligência']
        results = searcher.search_by_keywords(keywords, max_results=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        assert all(isinstance(video, VideoInfo) for video in results)
        
        # Deve encontrar pelo menos um vídeo sobre golfinhos
        found_dolphin = any('golfinho' in video.title.lower() or 
                           'delfim' in video.title.lower() for video in results)
        assert found_dolphin
    
    def test_search_by_semantic(self, searcher):
        """Testa busca por similaridade semântica."""
        # Cria embedding de exemplo
        query_embedding = np.array([0.1] * 300)
        
        results = searcher.search_by_semantic(query_embedding, max_results=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        assert all(isinstance(video, VideoInfo) for video in results)
        
        # Verifica se videos têm scores semânticos
        if results:
            assert all(hasattr(video, 'semantic_score') for video in results)
    
    def test_filter_by_quality(self, searcher):
        """Testa filtragem por qualidade."""
        # Cria vídeos de exemplo com diferentes métricas
        videos = [
            VideoInfo(
                id="video1", title="Vídeo 1", description="Descrição 1",
                duration=300, views=50000, likes=1000, upload_date="2024-01-01",
                channel="Canal 1", category="ANIMALS", tags=["test"]
            ),
            VideoInfo(
                id="video2", title="Vídeo 2", description="Descrição 2",
                duration=300, views=5000, likes=100, upload_date="2024-01-01",
                channel="Canal 2", category="ANIMALS", tags=["test"]
            )
        ]
        
        filtered = searcher.filter_by_quality(videos, min_views=10000)
        
        assert isinstance(filtered, list)
        assert len(filtered) == 1  # Apenas o vídeo com mais de 10k views
        
    def test_calculate_quality_score(self, searcher):
        """Testa cálculo de score de qualidade."""
        video = VideoInfo(
            id="video1", title="Vídeo Teste", description="Descrição teste",
            duration=300, views=100000, likes=5000, upload_date="2024-01-01",
            channel="Canal Teste", category="ANIMALS", tags=["test"]
        )
        
        score = searcher.calculate_quality_score(video)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Vídeo com muitas views e bom engajamento deve ter score alto
        assert score > 0.5
    
    def test_search_combined(self, searcher):
        """Testa busca combinada."""
        keywords = ['golfinho', 'oceano']
        embedding = np.array([0.1] * 300)
        
        results = searcher.search_combined(keywords, embedding, max_results=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        assert all(isinstance(video, VideoInfo) for video in results)
        
        # Verifica se vídeos têm scores
        if results:
            assert all(hasattr(video, 'quality_score') for video in results)
            assert all(hasattr(video, 'keyword_score') for video in results)
            assert all(hasattr(video, 'semantic_score') for video in results)
    
    def test_get_best_match(self, searcher):
        """Testa busca do melhor vídeo."""
        keywords = ['golfinho']
        embedding = np.array([0.1] * 300)
        
        best_match = searcher.get_best_match(keywords, embedding)
        
        if best_match:
            assert isinstance(best_match, VideoInfo)
            assert 'golfinho' in best_match.title.lower() or 'delfim' in best_match.title.lower()
        else:
            # Se não encontrar match, deve retornar None
            assert best_match is None


class TestIntegration:
    """Testes de integração entre SemanticAnalyzer e VideoSearcher."""
    
    def test_script_to_video_matching(self):
        """Testa matching completo de roteiro para vídeo."""
        analyzer = SemanticAnalyzer()
        searcher = VideoSearcher()
        
        # Roteiro de exemplo
        script = """
        Neste vídeo você vai conhecer os incríveis golfinhos.
        Estes mamíferos marinhos são conhecidos por sua inteligência excepcional.
        Você verá golfinhos realizando truques espetaculares no oceano.
        Prepare-se para se impressionar com estas criaturas magníficas!
        """
        
        # Analisa o roteiro
        analysis = analyzer.analyze_script(script)
        
        # Busca vídeos
        keywords = analysis['keywords'][:5]  # Top 5 keywords
        embedding = analysis['semantic_vector']
        
        if embedding is not None:
            results = searcher.search_combined(
                keywords, 
                embedding, 
                category=analysis['category'],
                max_results=3
            )
            
            assert isinstance(results, list)
            
            # Verifica se encontrou vídeos relacionados a golfinhos
            if results:
                animal_videos = [v for v in results if v.category == 'ANIMALS']
                assert len(animal_videos) > 0
        
        print("✓ Teste de integração concluído com sucesso!")


if __name__ == "__main__":
    # Executa testes básicos sem pytest
    print("=== Executando Testes do Sistema de Matching ===")
    
    # Teste básico do SemanticAnalyzer
    print("\n1. Testando SemanticAnalyzer...")
    try:
        analyzer = SemanticAnalyzer()
        
        # Teste de palavras-chave
        text = "Os golfinhos são animais incríveis que nadam no oceano azul."
        keywords = analyzer.extract_keywords(text)
        print(f"   ✓ Palavras-chave extraídas: {keywords[:5]}")
        
        # Teste de tom
        tone = analyzer.analyze_tone(text)
        print(f"   ✓ Tom analisado: {tone}")
        
        # Teste de categorização
        category, confidence = analyzer.categorize_content(text)
        print(f"   ✓ Categoria: {category} (confiança: {confidence:.2f})")
        
        # Teste de embedding
        embedding = analyzer.get_semantic_embedding(text)
        if embedding is not None:
            print(f"   ✓ Embedding gerado: {len(embedding)} dimensões")
        
        print("   ✓ SemanticAnalyzer funcionando!")
        
    except Exception as e:
        print(f"   ✗ Erro no SemanticAnalyzer: {e}")
    
    # Teste básico do VideoSearcher
    print("\n2. Testando VideoSearcher...")
    try:
        searcher = VideoSearcher()
        
        # Teste de busca por palavras-chave
        keywords = ['golfinho', 'oceano', 'inteligência']
        results = searcher.search_by_keywords(keywords, max_results=3)
        print(f"   ✓ Encontrados {len(results)} vídeos por palavras-chave")
        
        # Teste de busca semântica
        if embedding is not None:
            semantic_results = searcher.search_by_semantic(embedding, max_results=3)
            print(f"   ✓ Encontrados {len(semantic_results)} vídeos por semântica")
        
        # Teste de busca combinada
        if embedding is not None:
            combined_results = searcher.search_combined(keywords, embedding, max_results=3)
            print(f"   ✓ Encontrados {len(combined_results)} vídeos na busca combinada")
            
            if combined_results:
                best = searcher.get_best_match(keywords, embedding)
                print(f"   ✓ Melhor match: {best.title if best else 'Nenhum'}")
        
        print("   ✓ VideoSearcher funcionando!")
        
    except Exception as e:
        print(f"   ✗ Erro no VideoSearcher: {e}")
    
    print("\n=== Testes Concluídos ===")