"""
Testes para o sistema de análise semântica e busca de vídeos.
AiShorts v2.0 - Módulo de Matching
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from video.matching.semantic_analyzer import SemanticAnalyzer
from video.matching.video_searcher import VideoSearcher
from models.script_models import Script, ScriptSection, GeneratedTheme, ThemeCategory


class TestSemanticAnalyzer:
    """Testes para SemanticAnalyzer."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.analyzer = SemanticAnalyzer()
        
        # Texto de exemplo
        self.sample_text = """
        O universo é cheio de mistérios fascinantes. As estrelas brilhantes 
        no céu noturno nos fazem pensar sobre nossa existência. A lua é um 
        satélite natural da Terra que influencia as marés dos oceanos.
        """
    
    def test_initialization(self):
        """Testa inicialização do analisador."""
        assert self.analyzer is not None
        assert self.analyzer.stop_words is not None
        assert len(self.analyzer.category_keywords) > 0
        assert len(self.analyzer.emotion_keywords) > 0
    
    def test_extract_keywords(self):
        """Testa extração de palavras-chave."""
        keywords = self.analyzer.extract_keywords(self.sample_text, max_keywords=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        assert all(isinstance(kw, str) for kw in keywords)
        
        # Deve conter palavras relevantes
        text_lower = self.sample_text.lower()
        found_relevant = any(kw in text_lower for kw in keywords if len(kw) > 3)
        assert found_relevant
    
    def test_extract_keywords_empty_text(self):
        """Testa extração com texto vazio."""
        keywords = self.analyzer.extract_keywords("")
        assert keywords == []
        
        keywords = self.analyzer.extract_keywords(None)
        assert keywords == []
    
    def test_extract_keywords_with_punctuation(self):
        """Testa extração com pontuação."""
        text_with_punct = "Hello, world! How are you? I'm fine."
        keywords = self.analyzer.extract_keywords(text_with_punct)
        
        # Não deve conter pontuação
        assert all(not any(p in kw for p in '.,!?') for kw in keywords)
    
    def test_analyze_tone(self):
        """Testa análise de tom emocional."""
        tone = self.analyzer.analyze_tone(self.sample_text)
        
        assert isinstance(tone, dict)
        assert 'positive' in tone
        assert 'negative' in tone
        assert 'neutral' in tone
        
        # Scores devem estar entre 0 e 1
        for score in tone.values():
            assert 0 <= score <= 1
        
        # Soma deve ser aproximadamente 1
        total = sum(tone.values())
        assert 0.9 <= total <= 1.1  # Allow small floating point error
    
    def test_analyze_tone_positive_text(self):
        """Testa análise com texto positivo."""
        positive_text = "Estou muito feliz e animado com essa descoberta incrível!"
        tone = self.analyzer.analyze_tone(positive_text)
        
        assert tone['positive'] >= tone['negative']
        assert tone['positive'] > 0
    
    def test_analyze_tone_negative_text(self):
        """Testa análise com texto negativo."""
        negative_text = "Isso é terrível e me deixa muito triste e preocupado."
        tone = self.analyzer.analyze_tone(negative_text)
        
        assert tone['negative'] >= tone['positive']
        assert tone['negative'] > 0
    
    def test_analyze_tone_empty_text(self):
        """Testa análise com texto vazio."""
        tone = self.analyzer.analyze_tone("")
        assert tone == {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def test_categorize_content(self):
        """Testa categorização de conteúdo."""
        categories = self.analyzer.categorize_content(self.sample_text)
        
        assert isinstance(categories, dict)
        assert len(categories) > 0
        
        # Deve ter SPACE como categoria principal
        space_score = categories.get('SPACE', 0)
        assert space_score > 0
        
        # Scores devem estar entre 0 e 1
        for score in categories.values():
            assert 0 <= score <= 1
    
    def test_categorize_content_space(self):
        """Testa categorização com conteúdo sobre espaço."""
        space_text = "Os astronautas viajaram para Marte em uma espaçonave futurística."
        categories = self.analyzer.categorize_content(space_text)
        
        space_score = categories.get('SPACE', 0)
        assert space_score > 0.1  # Deve ter score significativo
    
    def test_categorize_content_animals(self):
        """Testa categorização com conteúdo sobre animais."""
        animals_text = "O leão é um felino majestoso que vive na savana africana."
        categories = self.analyzer.categorize_content(animals_text)
        
        animals_score = categories.get('ANIMALS', 0)
        assert animals_score > 0.1
    
    def test_categorize_content_unknown(self):
        """Testa categorização com conteúdo genérico."""
        generic_text = "Isto é um texto muito genérico sem conteúdo específico."
        categories = self.analyzer.categorize_content(generic_text)
        
        # Deve retornar UNKNOWN se não houver matches significativos
        if 'UNKNOWN' in categories:
            assert categories['UNKNOWN'] >= 0.5
    
    def test_get_semantic_embedding(self):
        """Testa geração de embedding semântico."""
        embedding = self.analyzer.get_semantic_embedding(self.sample_text)
        
        if embedding is not None:
            assert isinstance(embedding, np.ndarray)
            assert len(embedding.shape) == 1  # Deve ser vetor 1D
            assert len(embedding) > 0
            
            # Deve estar normalizado
            norm = np.linalg.norm(embedding)
            assert abs(norm - 1.0) < 0.01  # Allow small floating point error
    
    def test_get_semantic_embedding_empty_text(self):
        """Testa embedding com texto vazio."""
        embedding = self.analyzer.get_semantic_embedding("")
        assert embedding is None
    
    def test_process_script_full_object(self):
        """Testa processamento de objeto Script completo."""
        # Criar objeto Script simulado
        theme = GeneratedTheme(
            main_title="Explorando o Universo",
            category=ThemeCategory.SPACE,
            keywords=["estrela", "universo", "planeta"],
            target_audience="jovens"
        )
        
        sections = [
            ScriptSection(
                type="hook",
                content="Você já se perguntou sobre as estrelas?"
            ),
            ScriptSection(
                type="development", 
                content="O universo é cheio de segredos fascinantes."
            )
        ]
        
        script = Script(
            id="test_script_1",
            theme=theme,
            sections=sections
        )
        
        analysis = self.analyzer.process_script(script)
        
        # Verificar estrutura do resultado
        assert 'script_id' in analysis
        assert 'keywords' in analysis
        assert 'tone' in analysis
        assert 'categories' in analysis
        assert 'embedding' in analysis
        assert 'sections' in analysis
        assert 'theme_title' in analysis
        
        assert analysis['script_id'] == "test_script_1"
        assert analysis['theme_title'] == "Explorando o Universo"
        assert isinstance(analysis['sections'], list)
        assert len(analysis['sections']) == 2
    
    def test_process_script_dict_object(self):
        """Testa processamento com objeto tipo dict."""
        # Simular script como dict
        script_dict = {
            'id': 'test_script_dict',
            'sections': [
                {'type': 'hook', 'content': 'Texto do hook'},
                {'type': 'development', 'content': 'Texto do development'}
            ]
        }
        
        analysis = self.analyzer.process_script(script_dict)
        
        assert analysis['script_id'] == 'test_script_dict'
        assert 'sections' in analysis
        assert isinstance(analysis['sections'], list)


class TestVideoSearcher:
    """Testes para VideoSearcher."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.searcher = VideoSearcher()
        
        # Vídeos de exemplo
        self.sample_videos = [
            {
                'id': 'video_1',
                'title': 'Explorando o Espaço - As Estrelas',
                'description': 'Um vídeo fascinante sobre as estrelas e o universo',
                'category': 'space',
                'keywords': ['estrela', 'universo', 'espaço'],
                'views': 50000,
                'likes': 2500,
                'comments': 150,
                'duration': 300
            },
            {
                'id': 'video_2',
                'title': 'Animais Selvagens - Leões da África', 
                'description': 'Documentário sobre leões africanos',
                'category': 'animals',
                'keywords': ['leão', 'África', 'selvagem'],
                'views': 75000,
                'likes': 4000,
                'comments': 200,
                'duration': 450
            }
        ]
        
        self.searcher.add_video_database(self.sample_videos)
    
    def test_initialization(self):
        """Testa inicialização do buscador."""
        assert self.searcher is not None
        assert self.searcher.video_database is not None
        assert len(self.searcher.embedding_cache) == 0
    
    def test_add_video_database(self):
        """Testa adição de vídeos ao banco."""
        initial_size = len(self.searcher.video_database)
        
        new_videos = [
            {
                'id': 'video_3',
                'title': 'Test Video',
                'category': 'science'
            }
        ]
        
        self.searcher.add_video_database(new_videos)
        assert len(self.searcher.video_database) == initial_size + 1
    
    def test_search_by_keywords(self):
        """Testa busca por palavras-chave."""
        results = self.searcher.search_by_keywords(['estrela', 'universo'])
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Deve encontrar o vídeo sobre espaço
        space_video = next((v for v in results if v.get('category') == 'space'), None)
        assert space_video is not None
        
        # Deve ter score de relevância
        assert 'relevance_score' in space_video
        assert space_video['relevance_score'] > 0
    
    def test_search_by_keywords_empty(self):
        """Testa busca com lista vazia de keywords."""
        results = self.searcher.search_by_keywords([])
        assert results == []
    
    def test_search_by_keywords_with_category(self):
        """Testa busca com filtro de categoria."""
        results = self.searcher.search_by_keywords(['estrela'], category='space')
        
        # Deve retornar apenas vídeos da categoria space
        for result in results:
            assert result.get('category') == 'space'
    
    def test_search_by_semantic(self):
        """Testa busca semântica."""
        # Embedding para conteúdo sobre espaço
        query_embedding = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0] + [0.8, 0.3, 0.1, 0.05] + [0] * 6)
        
        results = self.searcher.search_by_semantic(query_embedding)
        
        assert isinstance(results, list)
        # Pode retornar resultados vazios se o threshold for muito alto
        assert all('similarity_score' in r for r in results)
        assert all(r['similarity_score'] >= self.searcher.similarity_threshold for r in results)
    
    def test_filter_by_quality(self):
        """Testa filtro de qualidade."""
        # Usar vídeos do banco existente
        videos = self.searcher.video_database[:]
        
        results = self.searcher.filter_by_quality(videos, min_quality_score=1.0)
        
        assert isinstance(results, list)
        
        # Todos os resultados devem ter score mínimo
        for result in results:
            assert 'quality_score' in result
            assert result['quality_score'] >= 1.0
    
    def test_search_by_script(self):
        """Testa busca baseada em análise de roteiro."""
        # Simular análise de roteiro
        script_analysis = {
            'keywords': ['estrela', 'universo'],
            'embedding': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0] + [0.8, 0.3, 0.1, 0.05] + [0] * 6,
            'categories': {'SPACE': 0.8, 'ANIMALS': 0.1}
        }
        
        results = self.searcher.search_by_script(script_analysis)
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Deve ter método de busca definido
        for result in results:
            assert 'search_method' in result
            assert result['search_method'] in ['keywords', 'semantic']
    
    def test_calculate_keyword_score(self):
        """Testa cálculo de score de palavras-chave."""
        video = self.sample_videos[0]
        keywords = ['estrela', 'universo']
        
        score = self.searcher._calculate_keyword_score(video, keywords)
        
        assert isinstance(score, float)
        assert score >= 0
        
        # Deve dar score positivo para matches
        assert score > 0
    
    def test_generate_basic_embedding(self):
        """Testa geração de embedding básico."""
        video = {
            'id': 'test_video',
            'category': 'space',
            'keywords': ['estrela'],
            'quality_score': 0.8,
            'views': 50000
        }
        
        embedding = self.searcher._generate_basic_embedding(video)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1
        assert len(embedding) == 20  # Conforme implementação
        
        # Deve estar normalizado
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01
    
    def test_calculate_semantic_similarity(self):
        """Testa cálculo de similaridade semântica."""
        embedding1 = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        embedding2 = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        
        similarity = self.searcher._calculate_semantic_similarity(embedding1, embedding2)
        
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
        
        # Embeddings idênticos devem ter similaridade 1
        assert abs(similarity - 1.0) < 0.01
    
    def test_get_search_stats(self):
        """Testa estatísticas do sistema."""
        stats = self.searcher.get_search_stats()
        
        assert isinstance(stats, dict)
        assert 'database_size' in stats
        assert 'cache_size' in stats
        assert 'similarity_threshold' in stats
        assert 'max_results' in stats
        
        assert stats['database_size'] == 2
        assert stats['cache_size'] == 0  # Cache vazio inicialmente


class TestIntegration:
    """Testes de integração entre SemanticAnalyzer e VideoSearcher."""
    
    def setup_method(self):
        """Setup para integração."""
        self.analyzer = SemanticAnalyzer()
        self.searcher = VideoSearcher()
        
        # Adicionar vídeos
        self.searcher.add_video_database([
            {
                'id': 'integration_video_1',
                'title': 'Mistérios do Universo',
                'description': 'Descubra os segredos das estrelas e galáxias',
                'category': 'space',
                'keywords': ['estrela', 'galáxia', 'universo'],
                'views': 100000,
                'likes': 5000,
                'duration': 420
            },
            {
                'id': 'integration_video_2',
                'title': 'A Vida dos Golfinhos',
                'description': 'Conheça a inteligência e beleza dos golfinhos',
                'category': 'animals',
                'keywords': ['golfinho', 'mar', 'inteligência'],
                'views': 80000,
                'likes': 4000,
                'duration': 360
            }
        ])
    
    def test_full_integration_workflow(self):
        """Testa workflow completo de análise e busca."""
        # 1. Criar roteiro simulado
        theme = GeneratedTheme(
            main_title="As Estrelas e o Universo",
            category=ThemeCategory.SPACE,
            keywords=["estrela", "universo", "galáxia"],
            target_audience="geral"
        )
        
        sections = [
            ScriptSection(
                type="hook",
                content="Você já olhou para o céu e se perguntou sobre as estrelas?"
            ),
            ScriptSection(
                type="development",
                content="O universo é infinito e cheio de segredos. As estrelas são sóis distantes."
            )
        ]
        
        script = Script(
            id="integration_script",
            theme=theme,
            sections=sections
        )
        
        # 2. Analisar roteiro
        analysis = self.analyzer.process_script(script)
        
        assert 'keywords' in analysis
        assert 'categories' in analysis
        assert len(analysis['keywords']) > 0
        
        # 3. Buscar vídeos
        results = self.searcher.search_by_script(analysis)
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # 4. Verificar se encontrou vídeo relevante
        space_videos = [v for v in results if v.get('category') == 'space']
        assert len(space_videos) > 0
        
        # 5. Verificar scores
        for result in results:
            assert 'final_score' in result
            assert result['final_score'] > 0
    
    def test_script_processing_and_search_consistency(self):
        """Testa consistência entre processamento e busca."""
        script_text = """
        Os golfinhos são mamíferos marinhos extremamente inteligentes. 
        Eles vivem em grupos chamados cardumes e comunicam-se através de sons.
        """
        
        # Análise direta do texto
        keywords = self.analyzer.extract_keywords(script_text)
        categories = self.analyzer.categorize_content(script_text)
        
        # Busca com palavras-chave
        keyword_results = self.searcher.search_by_keywords(keywords)
        
        # Busca com categorias
        main_category = max(categories.keys(), key=lambda k: categories[k])
        category_results = self.searcher.search_by_keywords([], category=main_category)
        
        # Ambos devem encontrar vídeos de animals
        keyword_has_animals = any(v.get('category') == 'animals' for v in keyword_results)
        category_has_animals = any(v.get('category') == 'animals' for v in category_results)
        
        assert keyword_has_animals or category_has_animals


if __name__ == "__main__":
    # Executar testes se chamado diretamente
    pytest.main([__file__, "-v"])