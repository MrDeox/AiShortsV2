"""
Testes unitários para LLMHelpers
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pydantic import ValidationError

from src.core.llm_helpers import (
    LLMHelpers,
    ThemeStrategyResult,
    ScriptRefinerResult,
    BrollPlannerResult,
    BrollQueryItem,
    RerankResult,
    RerankScore
)


class TestLLMHelpers:
    """Testes para a classe LLMHelpers."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock do AsyncOpenRouterClient."""
        client = AsyncMock()
        return client
    
    @pytest.fixture
    def llm_helpers(self, mock_client):
        """Instância do LLMHelpers com client mockado."""
        with patch('src.core.llm_helpers.get_async_openrouter_client', return_value=mock_client):
            return LLMHelpers()
    
    @pytest.mark.asyncio
    async def test_generate_theme_strategy_success(self, llm_helpers, mock_client):
        """Testa geração de tema com sucesso."""
        # Setup
        mock_response = {
            "topic": "The surprising intelligence of crows",
            "angle": "Shows how crows solve complex problems",
            "safety_flags": [],
            "uniqueness_score": 0.85,
            "virality_potential": 0.78
        }
        mock_client.generate_json.return_value = mock_response
        
        # Execute
        result = await llm_helpers.generate_theme_strategy(
            category="animals",
            recent_themes=["dogs", "cats"],
            constraints={"max_words": 40}
        )
        
        # Verify
        assert isinstance(result, ThemeStrategyResult)
        assert result.topic == "The surprising intelligence of crows"
        assert result.angle == "Shows how crows solve complex problems"
        assert result.uniqueness_score == 0.85
        assert result.virality_potential == 0.78
        assert len(result.safety_flags) == 0
        
        # Verifica se generate_json foi chamado corretamente
        mock_client.generate_json.assert_called_once()
        call_args = mock_client.generate_json.call_args
        assert "animals" in str(call_args)
        assert "dogs" in str(call_args)  # recent_themes
    
    @pytest.mark.asyncio
    async def test_generate_theme_strategy_error(self, llm_helpers, mock_client):
        """Testa fallback quando LLM falha."""
        # Setup
        mock_client.generate_json.side_effect = Exception("API Error")
        
        # Execute & Verify
        with pytest.raises(Exception, match="API Error"):
            await llm_helpers.generate_theme_strategy(
                category="technology",
                recent_themes=[],
                constraints={}
            )
    
    @pytest.mark.asyncio
    async def test_refine_script_success(self, llm_helpers, mock_client):
        """Testa refino de script com sucesso."""
        # Setup
        mock_response = {
            "hook": "Did you know octopuses have three hearts?",
            "body": "These incredible creatures evolved with one heart for each gill and a central heart...",
            "conclusion": "Nature never ceases to amaze with its ingenious designs",
            "estimated_duration": 62,
            "refinement_notes": ["Added hook question", "Adjusted pacing"]
        }
        mock_client.generate_json.return_value = mock_response
        
        # Execute
        result = await llm_helpers.refine_script(
            platform="tiktok",
            theme="octopus biology",
            previous_script={"hook": "Octopuses", "body": "They have hearts", "conclusion": "Amazing"},
            validation_summary={"overall_score": 60, "critical_issues": []},
            constraints={"target_duration": [50, 65]}
        )
        
        # Verify
        assert isinstance(result, ScriptRefinerResult)
        assert result.hook == "Did you know octopuses have three hearts?"
        assert result.estimated_duration == 62
        assert len(result.refinement_notes) == 2
    
    @pytest.mark.asyncio
    async def test_refine_script_text_response(self, llm_helpers, mock_client):
        """Testa refino quando resposta é texto em vez de JSON."""
        # Setup
        mock_response = """HOOK: What if I told you sharks existed before trees?
BODY: Sharks have been swimming in our oceans for over 400 million years...
CONCLUSION: These ancient predators are true survivors of time
ESTIMATED_DURATION: 58"""
        mock_client.generate_json.return_value = mock_response
        
        # Execute
        result = await llm_helpers.refine_script(
            platform="shorts",
            theme="shark evolution",
            previous_script={},
            validation_summary={},
            constraints={}
        )
        
        # Verify
        assert isinstance(result, ScriptRefinerResult)
        assert "What if I told you sharks existed before trees?" in result.hook
        assert result.estimated_duration == 58
    
    @pytest.mark.asyncio
    async def test_plan_broll_queries_success(self, llm_helpers, mock_client):
        """Testa planejamento de queries B-roll com sucesso."""
        # Setup
        mock_response = {
            "queries": [
                {
                    "text": "shark swimming underwater slow motion",
                    "role": "establishing_shot",
                    "priority": 0.9
                },
                {
                    "text": "shark teeth closeup macro",
                    "role": "subject_closeup",
                    "priority": 0.8
                },
                {
                    "text": "shark hunting seal",
                    "role": "dynamic_motion",
                    "priority": 0.85
                }
            ]
        }
        mock_client.generate_json.return_value = mock_response
        
        # Execute
        result = await llm_helpers.plan_broll_queries(
            script_text="Sharks are ancient predators that rule the oceans",
            max_queries=6,
            visual_roles=["establishing_shot", "subject_closeup"]
        )
        
        # Verify
        assert isinstance(result, BrollPlannerResult)
        assert len(result.queries) == 3
        assert result.queries[0].text == "shark swimming underwater slow motion"
        assert result.queries[0].role == "establishing_shot"
        assert result.queries[0].priority == 0.9
    
    @pytest.mark.asyncio
    async def test_plan_broll_queries_fallback(self, llm_helpers, mock_client):
        """Testa fallback quando LLM B-roll Planner está desativado."""
        # Setup
        with patch('src.core.llm_helpers.USE_LLM_BROLL_PLANNER', False):
            llm_helpers_disabled = LLMHelpers()
        
        # Execute
        result = await llm_helpers_disabled.plan_broll_queries(
            script_text="Space exploration and the future of humanity",
            max_queries=6
        )
        
        # Verify - deve retornar fallback do SemanticAnalyzer
        assert isinstance(result, BrollPlannerResult)
        assert len(result.queries) == 1
        assert result.queries[0].role == "general"
        assert result.queries[0].priority == 0.5
    
    @pytest.mark.asyncio
    async def test_rerank_candidates_success(self, llm_helpers, mock_client):
        """Testa reranking de candidatos com sucesso."""
        # Setup
        mock_response = {
            "scores": [
                {"id": "vid1", "llm_relevance": 0.92, "reason": "Perfect match"},
                {"id": "vid2", "llm_relevance": 0.75, "reason": "Good visual match"},
                {"id": "vid3", "llm_relevance": 0.30, "reason": "Poor relevance"}
            ]
        }
        mock_client.generate_json.return_value = mock_response
        
        candidates = [
            {"id": "vid1", "title": "Shark Documentary", "clip_score": 0.85},
            {"id": "vid2", "title": "Ocean Life", "clip_score": 0.70},
            {"id": "vid3", "title": "Cat Video", "clip_score": 0.20}
        ]
        
        # Execute
        result = await llm_helpers.rerank_candidates(
            script_summary="Documentary about sharks in the ocean",
            candidates=candidates,
            weights={"clip": 0.6, "llm": 0.4}
        )
        
        # Verify
        assert isinstance(result, RerankResult)
        assert len(result.scores) == 3
        
        # Verificar cálculo do score final
        # vid1: 0.85 * 0.6 + 0.92 * 0.4 = 0.878
        assert result.scores[0].id == "vid1"
        assert result.scores[0].llm_relevance == 0.92
        assert result.scores[0].final_score == pytest.approx(0.878, rel=1e-2)
    
    @pytest.mark.asyncio
    async def test_rerank_candidates_disabled(self, llm_helpers, mock_client):
        """Testa reranking quando feature está desativada."""
        # Setup
        with patch('src.core.llm_helpers.USE_LLM_RERANKER', False):
            llm_helpers_disabled = LLMHelpers()
        
        candidates = [
            {"id": "vid1", "clip_score": 0.85, "relevance_score": 0.85},
            {"id": "vid2", "clip_score": 0.70, "relevance_score": 0.70}
        ]
        
        # Execute
        result = await llm_helpers_disabled.rerank_candidates(
            script_summary="Any script",
            candidates=candidates
        )
        
        # Verify - deve retornar scores CLIP originais
        assert isinstance(result, RerankResult)
        assert len(result.scores) == 2
        assert result.scores[0].llm_relevance == 0.85
        assert result.scores[0].reason == "CLIP score"
    
    @pytest.mark.asyncio
    async def test_validate_script_with_llm_disabled(self, llm_helpers, mock_client):
        """Testa validação de script quando LLM co-reviewer está desativado."""
        # Setup
        with patch('src.core.llm_helpers.USE_LLM_CO_REVIEWER', False):
            llm_helpers_disabled = LLMHelpers()
        
        script = {"hook": "Test", "body": "Test body", "conclusion": "Test end"}
        
        # Execute
        result = await llm_helpers_disabled.validate_script_with_llm(
            script=script,
            platform="tiktok",
            theme="test theme"
        )
        
        # Verify - deve retornar dict vazio
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_validate_captions_disabled(self, llm_helpers, mock_client):
        """Testa validação de legendas quando está desativado."""
        # Setup
        with patch('src.core.llm_helpers.USE_LLM_CAPTION_VALIDATOR', False):
            llm_helpers_disabled = LLMHelpers()
        
        # Execute
        result = await llm_helpers_disabled.validate_captions(
            script_text="Test script",
            captions=[{"text": "Test", "start": 0, "end": 1}]
        )
        
        # Verify - deve retornar aceitável por padrão
        assert result["is_acceptable"] is True


class TestLLMHelpersModels:
    """Testes para os modelos Pydantic do LLMHelpers."""
    
    def test_theme_strategy_result_valid(self):
        """Testa criação válida de ThemeStrategyResult."""
        result = ThemeStrategyResult(
            topic="Test topic",
            angle="Test angle",
            uniqueness_score=0.8,
            virality_potential=0.7
        )
        assert result.topic == "Test topic"
        assert result.uniqueness_score == 0.8
    
    def test_theme_strategy_result_invalid_score(self):
        """Testa validação de score inválido."""
        with pytest.raises(ValidationError):
            ThemeStrategyResult(
                topic="Test",
                angle="Test",
                uniqueness_score=1.5,  > 1.0
                virality_potential=0.5
            )
    
    def test_broll_query_item_valid(self):
        """Testa criação válida de BrollQueryItem."""
        query = BrollQueryItem(
            text="shark documentary",
            role="establishing_shot",
            priority=0.9
        )
        assert query.text == "shark documentary"
        assert query.role == "establishing_shot"
        assert query.priority == 0.9
    
    def test_rerank_score_optional_fields(self):
        """Testa campos opcionais de RerankScore."""
        score = RerankScore(
            id="test",
            llm_relevance=0.8,
            reason="Good match"
        )
        assert score.final_score is None  # Campo opcional