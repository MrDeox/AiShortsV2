"""
Testes unitários para MediaAcquisitionService
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from src.models.unified_models import BrollMatchResult
from src.pipeline.services.media_acquisition_service import MediaAcquisitionService
from src.video.matching.clip_relevance_scorer import CLIPRelevanceScorer
from src.video.validation.clip_pre_validator import ClipVideoPreValidator


class TestMediaAcquisitionService:
    """Testes para MediaAcquisitionService."""
    
    @pytest.fixture
    def mock_youtube_extractor(self):
        """Mock do YouTubeExtractor."""
        extractor = Mock()
        extractor.search_videos.return_value = [
            {
                "id": "vid1",
                "title": "Shark Documentary",
                "description": "Amazing shark footage",
                "duration": 120,
                "view_count": 1000000,
                "thumbnail": "http://example.com/thumb1.jpg"
            },
            {
                "id": "vid2", 
                "title": "Ocean Life",
                "description": "Underwater documentary",
                "duration": 180,
                "view_count": 500000,
                "thumbnail": "http://example.com/thumb2.jpg"
            }
        ]
        return extractor
    
    @pytest.fixture
    def mock_semantic_analyzer(self):
        """Mock do SemanticAnalyzer."""
        analyzer = Mock()
        analyzer.extract_keywords.return_value = ["shark", "ocean", "predator"]
        analyzer.generate_broll_keywords_via_llm.return_value = [
            "shark underwater",
            "ocean documentary",
            "predator hunting"
        ]
        return analyzer
    
    @pytest.fixture
    def mock_broll_query_service(self):
        """Mock do BrollQueryService."""
        service = Mock()
        return service
    
    @pytest.fixture
    def media_service(
        self,
        mock_youtube_extractor,
        mock_semantic_analyzer,
        mock_broll_query_service
    ):
        """Instância do MediaAcquisitionService com mocks."""
        return MediaAcquisitionService(
            youtube_extractor=mock_youtube_extractor,
            semantic_analyzer=mock_semantic_analyzer,
            broll_query_service=mock_broll_query_service
        )
    
    @pytest.mark.asyncio
    async def test_generate_search_queries_explicit(self, media_service):
        """Testa geração de queries com lista explícita."""
        # Execute
        queries = await media_service._generate_search_queries(
            theme_content="Sharks are predators",
            explicit_queries=["shark documentary", "ocean life"]
        )
        
        # Verify
        assert len(queries) == 2
        assert "shark documentary" in queries
        assert "ocean life" in queries
    
    @pytest.mark.asyncio
    async def test_generate_search_queries_with_llm_broll_planner(self, media_service):
        """Testa geração de queries com LLM B-roll Planner."""
        # Setup LLM helpers mock
        mock_llm = AsyncMock()
        mock_broll_plan = Mock()
        mock_query1 = Mock()
        mock_query1.text = "shark hunting seal"
        mock_query1.role = "dynamic_motion"
        mock_query1.priority = 0.9
        mock_query2 = Mock()
        mock_query2.text = "shark closeup underwater"
        mock_query2.role = "subject_closeup"
        mock_query2.priority = 0.85
        mock_broll_plan.queries = [mock_query1, mock_query2]
        
        mock_llm.plan_broll_queries.return_value = mock_broll_plan
        media_service.llm_helpers = mock_llm
        
        # Execute
        queries = await media_service._generate_search_queries(
            theme_content="Sharks are amazing predators",
            explicit_queries=None
        )
        
        # Verify
        assert len(queries) == 2
        assert "shark hunting seal" in queries
        assert "shark closeup underwater" in queries
        
        # Verifica se o LLM foi chamado
        mock_llm.plan_broll_queries.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_search_queries_fallback_semantic_analyzer(self, media_service):
        """Testa fallback para SemanticAnalyzer quando LLM não disponível."""
        # Execute (sem LLM helpers)
        queries = await media_service._generate_search_queries(
            theme_content="Amazing shark behavior",
            explicit_queries=None
        )
        
        # Verify - deve usar SemanticAnalyzer
        assert len(queries) == 3
        assert "shark underwater" in queries
        assert "ocean documentary" in queries
        assert "predator hunting" in queries
        
        # Verifica se SemanticAnalyzer foi chamado
        media_service.semantic_analyzer.generate_broll_keywords_via_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_search_queries_fallback_keywords(self, media_service):
        """Testa fallback para extração de keywords."""
        # Setup SemanticAnalyzer para falhar
        media_service.semantic_analyzer.generate_broll_keywords_via_llm.side_effect = Exception("LLM Error")
        
        # Execute
        queries = await media_service._generate_search_queries(
            theme_content="The ocean is vast",
            explicit_queries=None
        )
        
        # Verify - deve usar keywords
        assert len(queries) == 1
        assert "shark ocean predator" in queries
    
    @pytest.mark.asyncio
    async def test_generate_search_queries_fallback_truncate(self, media_service):
        """Testa fallback truncando conteúdo do tema."""
        # Setup SemanticAnalyzer para retornar vazio
        media_service.semantic_analyzer.extract_keywords.return_value = []
        media_service.semantic_analyzer.generate_broll_keywords_via_llm.return_value = []
        
        # Execute
        queries = await media_service._generate_search_queries(
            theme_content="This is a very long theme content that should be truncated because it exceeds the normal limit for fallback queries",
            explicit_queries=None
        )
        
        # Verify - deve truncar o conteúdo
        assert len(queries) == 1
        assert len(queries[0]) <= 60
    
    @pytest.mark.asyncio
    async def test_generate_search_queries_llm_error_fallback(self, media_service):
        """Testa fallback quando LLM B-roll Planner lança erro."""
        # Setup LLM helpers mock que falha
        mock_llm = AsyncMock()
        mock_llm.plan_broll_queries.side_effect = Exception("LLM API Error")
        media_service.llm_helpers = mock_llm
        
        # Execute
        queries = await media_service._generate_search_queries(
            theme_content="Test content",
            explicit_queries=None
        )
        
        # Verify - deve fazer fallback para SemanticAnalyzer
        assert len(queries) == 3  # Do SemanticAnalyzer
        
        # Verifica se ambos foram tentados
        mock_llm.plan_broll_queries.assert_called_once()
        media_service.semantic_analyzer.generate_broll_keywords_via_llm.assert_called_once()
    
    def test_search_videos(self, media_service, mock_youtube_extractor):
        """Testa busca de vídeos no YouTube."""
        # Setup
        queries = ["shark documentary", "ocean life"]
        
        # Execute
        candidates = media_service._search_videos(queries)
        
        # Verify
        assert len(candidates) == 2  # 1 vídeo por query
        
        # Verifica se buscou para cada query
        assert mock_youtube_extractor.search_videos.call_count == 2
    
    def test_filter_candidates(self, media_service):
        """Testa filtragem de candidatos."""
        # Setup
        candidates = [
            {
                "id": "vid1",
                "title": "Good Video",
                "duration": 120,
                "view_count": 10000
            },
            {
                "id": "vid2",
                "title": "Bad Video",
                "duration": 5,  # Muito curto
                "view_count": 100
            },
            {
                "id": "vid3",
                "title": "Another Bad",
                "duration": 7200,  # Muito longo
                "view_count": 50
            }
        ]
        
        # Execute
        filtered = media_service._filter_candidates(candidates)
        
        # Verify - deve filtrar apenas vídeos válidos
        assert len(filtered) == 1
        assert filtered[0]["id"] == "vid1"
    
    def test_pre_validate_candidates(self, media_service):
        """Testa pré-validação de candidatos."""
        # Setup
        candidates = [
            {"id": "vid1", "title": "Test Video 1"},
            {"id": "vid2", "title": "Test Video 2"}
        ]
        
        # Mock do pre-validator
        media_service.clip_pre_validator.validate_candidates = AsyncMock()
        media_service.clip_pre_validator.validate_candidates.return_value = candidates
        
        # Execute
        loop = asyncio.get_event_loop()
        validated = loop.run_until_complete(
            media_service._pre_validate_candidates(
                candidates,
                "sharks are predators",
                ["shark documentary"]
            )
        )
        
        # Verify
        assert len(validated) == 2
        media_service.clip_pre_validator.validate_candidates.assert_called_once()
    
    def test_perform_semantic_matching(self, media_service):
        """Testa matching semântico."""
        # Setup
        candidates = [
            {"id": "vid1", "title": "Shark Attack"},
            {"id": "vid2", "title": "Cat Video"}
        ]
        
        # Mock do scorer
        media_service.clip_relevance_scorer.score_and_rank = Mock()
        media_service.clip_relevance_scorer.score_and_rank.return_value = candidates
        
        # Execute
        scored = media_service._perform_semantic_matching(
            candidates,
            "Documentary about sharks"
        )
        
        # Verify
        assert len(scored) == 2
        media_service.clip_relevance_scorer.score_and_rank.assert_called_once()
    
    def test_download_videos(self, media_service, mock_youtube_extractor):
        """Testa download de vídeos."""
        # Setup
        scored_candidates = [
            {"id": "vid1", "title": "Video 1", "relevance_score": 0.9},
            {"id": "vid2", "title": "Video 2", "relevance_score": 0.8},
            {"id": "vid3", "title": "Video 3", "relevance_score": 0.7}
        ]
        
        # Mock do download
        mock_youtube_extractor.download_video.return_value = "/path/to/video.mp4"
        
        # Execute
        downloaded = media_service._download_videos(scored_candidates)
        
        # Verify - deve baixar apenas os melhores (limit=3)
        assert len(downloaded) == 3
        assert all("path" in video for video in downloaded)
        
        # Verifica se fez download
        assert mock_youtube_extractor.download_video.call_count == 3
    
    def test_download_videos_with_limit(self, media_service, mock_youtube_extractor):
        """Testa download com limite de vídeos."""
        # Setup
        scored_candidates = [{"id": f"vid{i}", "title": f"Video {i}"} for i in range(10)]
        mock_youtube_extractor.download_video.return_value = f"/path/video.mp4"
        
        # Execute
        downloaded = media_service._download_videos(scored_candidates, max_videos=5)
        
        # Verify - deve respeitar o limite
        assert len(downloaded) == 5
        assert mock_youtube_extractor.download_video.call_count == 5
    
    @pytest.mark.asyncio
    async def test_extract_broll_full_flow(self, media_service, mock_youtube_extractor):
        """Teste completo do fluxo de extração de B-roll."""
        # Setup mocks adicionais
        media_service.clip_pre_validator.validate_candidates = AsyncMock()
        media_service.clip_pre_validator.validate_candidates.return_value = [
            {"id": "vid1", "title": "Shark Documentary"}
        ]
        
        media_service.clip_relevance_scorer.score_and_rank.return_value = [
            {"id": "vid1", "title": "Shark Documentary", "relevance_score": 0.9}
        ]
        
        mock_youtube_extractor.download_video.return_value = "/path/to/video.mp4"
        
        # Execute
        result = await media_service.extract_broll(
            theme_content="Amazing shark behavior in the ocean",
            search_queries=["shark documentary"]
        )
        
        # Verify
        assert isinstance(result, BrollMatchResult)
        assert result.success is True
        assert len(result.candidates) == 1
        assert result.candidates[0]["id"] == "vid1"
        assert len(result.downloaded_videos) == 1
        assert result.downloaded_videos[0]["path"] == "/path/to/video.mp3"