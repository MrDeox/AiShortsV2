"""
MediaAcquisitionService - Responsável pela busca, extração e análise de mídias (B-roll).
Extrai a lógica de mídia do AiShortsOrchestrator para melhor separação de responsabilidades.
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.models.unified_models import BrollMatchResult
from src.video.matching.content_matcher import ContentMatcher
from src.video.matching.clip_relevance_scorer import CLIPRelevanceScorer
from src.video.validation.clip_pre_validator import ClipVideoPreValidator
from src.config.settings import config

# Importar helpers LLM se disponíveis
try:
    from src.core.llm_helpers import LLMHelpers
    LLM_HELPERS_AVAILABLE = True
except ImportError:
    LLM_HELPERS_AVAILABLE = False


class MediaAcquisitionService:
    """Serviço responsável por adquirir e analisar mídias para o vídeo."""
    
    def __init__(
        self,
        youtube_extractor,
        semantic_analyzer,
        broll_query_service,
        clip_relevance_scorer: Optional[CLIPRelevanceScorer] = None,
        clip_pre_validator: Optional[ClipVideoPreValidator] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.youtube_extractor = youtube_extractor
        self.semantic_analyzer = semantic_analyzer
        self.broll_query_service = broll_query_service
        self.clip_relevance_scorer = clip_relevance_scorer or CLIPRelevanceScorer()
        self.clip_pre_validator = clip_pre_validator or ClipVideoPreValidator(
            clip_scorer=self.clip_relevance_scorer,
            min_relevance_score=0.3,
            max_concurrent_validations=5
        )
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # Inicializar helpers LLM se disponível e ativado
        self.llm_helpers = None
        if LLM_HELPERS_AVAILABLE and config.llm_integration.use_llm_broll_planner:
            self.llm_helpers = LLMHelpers()
self.logger.info("🧠 LLM B-roll Planner ativado")
        elif not config.llm_integration.use_llm_broll_planner:
self.logger.info(" LLM B-roll Planner desativado via configuração")
    
    async def extract_broll(
        self,
        theme_content: str,
        search_queries: Optional[List[str]] = None
    ) -> BrollMatchResult:
        """
        Extrai vídeos B-roll com base no conteúdo temático.
        
        Returns:
            BrollMatchResult: Resultado da extração e matching de B-roll
        """
self.logger.info(" ETAPA 3: Extração de B-roll com Semantic Matching Avançado...")
        
        try:
            # Gerar queries
            queries = await self._generate_search_queries(theme_content, search_queries)
            
            # Buscar vídeos no YouTube
            all_candidates = self._search_videos(queries)
            
            # Filtrar candidatos
            filtered_candidates = self._filter_candidates(all_candidates)
            
            # Pré-validação com CLIP
            pre_validated_candidates = self._pre_validate_candidates(
                filtered_candidates, 
                theme_content,
                queries
            )
            
            # Semantic matching avançado
            scored_candidates = self._perform_semantic_matching(
                pre_validated_candidates,
                theme_content
            )
            
            # Baixar melhores vídeos
            downloaded_videos = self._download_videos(scored_candidates)
            
            # Preparar resultado
            keywords = self.semantic_analyzer.extract_keywords(theme_content) or []
            
            return BrollMatchResult(
                success=True,
                videos=downloaded_videos,
                queries_used=queries,
                keywords=keywords,
                validation_pipeline={
                    "pre_validation": {
                        "performed": len(pre_validated_candidates) > 0,
                        "method": "clip" if self.clip_pre_validator.clip_scorer else "fallback",
                        "candidates_validated": len(pre_validated_candidates),
                        "top_pre_validation_score": max(
                            [c.get("pre_validation_score", 0) for c in pre_validated_candidates]
                        ) if pre_validated_candidates else None
                    },
                    "semantic_analysis": {
                        "performed": len(scored_candidates) > 0,
                        "total_candidates": len(all_candidates),
                        "filtered_candidates": len(pre_validated_candidates),
                        "scored_candidates": len(scored_candidates),
                        "top_relevance_score": scored_candidates[0].get("relevance_score") if scored_candidates else None,
                        "average_relevance_score": (
                            sum(c.get("relevance_score", 0) for c in scored_candidates[:5]) / 
                            min(len(scored_candidates), 5)
                        ) if scored_candidates else None
                    }
                },
                total_candidates=len(all_candidates),
                download_count=len(downloaded_videos)
            )
            
        except Exception as error:
self.logger.error(" Erro na extração de B-roll: %s", error)
            return BrollMatchResult(
                success=False,
                videos=[],
                queries_used=[],
                keywords=[],
                validation_pipeline={},
                error=str(error)
            )
    
    def analyze_content(self, theme_content: str) -> Dict[str, Any]:
        """
        Analisa o conteúdo temático para extração de keywords e categorização.
        
        Returns:
            Dict: Resultado da análise semântica
        """
self.logger.info("🧠 ETAPA 4: Análise Semântica...")
        
        keywords = self.semantic_analyzer.extract_keywords(theme_content)
        category = self.semantic_analyzer.categorize_content(theme_content)
        
self.logger.info(" Keywords extraídas: %s", keywords)
self.logger.info(" Categoria: %s (%.2f)", category[0], category[1])
        
        return {
            "keywords": keywords,
            "category": category[0],
            "confidence": category[1],
        }
    
    async def _generate_search_queries(
        self, 
        theme_content: str, 
        explicit_queries: Optional[List[str]] = None
    ) -> List[str]:
        """Gera queries de busca usando múltiplas estratégias incluindo LLM B-roll Planner."""
        queries: List[str] = []
        
        # 1) Queries explícitas (se fornecidas)
        if explicit_queries:
            queries.extend([q for q in explicit_queries if q])
        
        # 2) Usar LLM B-roll Planner se disponível
        if self.llm_helpers and not queries:
            try:
self.logger.info("🧠 Usando LLM B-roll Planner...")
                
                broll_plan = await self.llm_helpers.plan_broll_queries(
                    script_text=theme_content,
                    max_queries=config.llm_integration.max_broll_queries,
                    visual_roles=[
                        "establishing_shot",
                        "subject_closeup", 
                        "dynamic_motion",
                        "emotional_reaction"
                    ]
                )
                
                # Extrair queries do planejamento
                if broll_plan.queries:
                    # Ordenar por prioridade e extrair texto
                    sorted_queries = sorted(broll_plan.queries, key=lambda x: x.priority, reverse=True)
                    queries = [q.text for q in sorted_queries]
                    
self.logger.info(f" {len(queries)} queries planejadas via LLM:")
                    for i, q in enumerate(queries[:3]):
                        role = sorted_queries[i].role if i < len(sorted_queries) else "general"
self.logger.info(f"   {i+1}. [{role}] {q}")
                
            except Exception as e:
self.logger.error(f" Erro no LLM B-roll Planner: {e}")
self.logger.info(" Fazendo fallback para SemanticAnalyzer...")
        
        # 3) Queries via LLM do SemanticAnalyzer (fallback)
        if not queries and theme_content:
            try:
                llm_queries = self.semantic_analyzer.generate_broll_keywords_via_llm(
                    script_text=theme_content,
                    max_queries=6,
                    max_keywords_per_query=4,
                )
                if llm_queries:
                    queries.extend(llm_queries)
self.logger.info(
                        "🔍 Queries de B-roll via LLM (SemanticAnalyzer): %s",
                        llm_queries,
                    )
            except Exception as exc:
self.logger.warning(
                    "⚠️ Falha ao gerar queries de B-roll via LLM (usando fallback local): %s",
                    exc,
                )
        
        # 4) Fallback heurístico
        if not queries and theme_content:
            keywords = self.semantic_analyzer.extract_keywords(theme_content) or []
            if keywords:
                fallback_query = " ".join(keywords[:4]).strip()
                if fallback_query:
                    queries.append(fallback_query)
            if not queries:
                queries.append(theme_content[:60])
        
self.logger.info(" Estratégia de busca final: %s", queries)
        return queries
    
    def _search_videos(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Busca vídeos no YouTube usando as queries."""
        all_candidates = []
        queries_used = []
        
        for query in queries[:3]:  # Limitar a 3 queries
            try:
                candidates = self.youtube_extractor.search_videos(query, max_results=5)
                if candidates:
                    all_candidates.extend(candidates)
                    queries_used.append(query)
self.logger.info(" Query '%s': %d candidatos encontrados", query, len(candidates))
                else:
self.logger.warning(" Nenhum resultado para query '%s'", query)
            except Exception as error:
self.logger.warning(" Erro na busca por '%s': %s", query, error)
        
        if not all_candidates:
            raise RuntimeError("Nenhum candidato encontrado em nenhuma busca")
        
self.logger.info(" Total de candidatos brutos: %d", len(all_candidates))
        return all_candidates
    
    def _filter_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplica filtros básicos nos candidatos."""
        filtered_candidates = []
        
        for candidate in candidates:
            # Remover duplicados
            video_id = candidate.get("id")
            if video_id and any(c.get("id") == video_id for c in filtered_candidates):
                continue
            
            # Filtrar duração muito longa
            duration = candidate.get("duration")
            if duration and duration > 180:
self.logger.debug(
                    "⏭️ Ignorando vídeo muito longo (%.1fs): %s", 
                    duration, 
                    candidate.get("title", "sem título")
                )
                continue
            
            filtered_candidates.append(candidate)
        
self.logger.info(" Candidatos após filtros básicos: %d", len(filtered_candidates))
        return filtered_candidates
    
    def _pre_validate_candidates(
        self,
        candidates: List[Dict[str, Any]],
        theme_content: str,
        queries: List[str]
    ) -> List[Dict[str, Any]]:
        """Realiza pré-validação com ClipVideoPreValidator."""
        if not candidates or not theme_content:
            return candidates
        
        try:
self.logger.info(" Iniciando pré-validação com ClipVideoPreValidator...")
            
            # Converter para formato VideoCandidate
            video_candidates = []
            for candidate in candidates[:15]:  # Limitar para performance
                video_candidate = {
                    "id": candidate.get("id", ""),
                    "title": candidate.get("title", ""),
                    "description": candidate.get("description", ""),
                    "thumbnail_url": candidate.get("thumbnail", ""),
                    "video_url": candidate.get("url", candidate.get("webpage_url", "")),
                    "duration": int(candidate.get("duration", 0)),
                    "view_count": candidate.get("view_count", 0),
                    "upload_date": candidate.get("upload_date", "")
                }
                
                from src.video.validation.clip_pre_validator import VideoCandidate
                video_candidate_obj = VideoCandidate(**video_candidate)
                video_candidates.append(video_candidate_obj)
            
            # Realizar pré-validação
            validated_candidates = self.clip_pre_validator.validate_candidates(
                candidates=video_candidates,
                query=queries[0] if queries else theme_content[:50],
                max_results=10
            )
            
            # Converter de volta para formato original
            pre_validated = []
            for validated_candidate in validated_candidates:
                original_candidate = next(
                    (c for c in candidates if c.get("id") == validated_candidate.id),
                    None
                )
                
                if original_candidate:
                    original_candidate["pre_validation_score"] = validated_candidate.relevance_score
                    original_candidate["pre_validation_method"] = (
                        "clip" if self.clip_pre_validator.clip_scorer else "fallback"
                    )
                    pre_validated.append(original_candidate)
            
self.logger.info(" Pré-validação concluída: %d candidatos válidos", len(pre_validated))
            
            # Log dos top candidatos
            if pre_validated:
self.logger.info(" Top 5 candidatos pré-validados:")
                for i, candidate in enumerate(pre_validated[:5]):
                    score = candidate.get("pre_validation_score", 0)
                    title = candidate.get("title", "sem título")[:50]
                    method = candidate.get("pre_validation_method", "unknown")
self.logger.info("   %d. Score: %.3f (%s) - %s", i+1, score, method, title)
            
            return pre_validated
            
        except Exception as error:
self.logger.warning(" Pré-validação falhou, usando candidatos originais: %s", error)
            return candidates
    
    def _perform_semantic_matching(
        self,
        candidates: List[Dict[str, Any]],
        theme_content: str
    ) -> List[Dict[str, Any]]:
        """Realiza semantic matching avançado usando CLIP."""
        if not theme_content or len(candidates) <= 3:
            # Fallback: ordenar por views
            candidates.sort(key=lambda x: x.get("view_count", 0), reverse=True)
self.logger.info(" Usando ordenação por views (fallback)")
            return candidates
        
        try:
self.logger.info("🧠 Iniciando semantic matching avançado...")
            
            reference_text = theme_content[:500]  # Limitar para performance
            scored_candidates = []
            
            for candidate in candidates[:10]:  # Limitar a 10 para performance
                try:
                    score = self.clip_relevance_scorer.calculate_relevance_score(
                        text=reference_text,
                        video_url=candidate.get("url", ""),
                        video_title=candidate.get("title", ""),
                        video_description=candidate.get("description", "")
                    )
                    
                    candidate["relevance_score"] = score
                    scored_candidates.append(candidate)
                    
                except Exception as error:
self.logger.debug(" Erro no scoring semântico: %s", error)
                    candidate["relevance_score"] = 0.5
                    scored_candidates.append(candidate)
            
            # Ordenar por relevância
            scored_candidates.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Log dos top candidatos
self.logger.info(" Top 5 candidatos por relevância semântica:")
            for i, candidate in enumerate(scored_candidates[:5]):
                score = candidate.get("relevance_score", 0)
                title = candidate.get("title", "sem título")[:50]
self.logger.info("   %d. Score: %.3f - %s", i+1, score, title)
            
            return scored_candidates
            
        except Exception as error:
self.logger.warning(" Semantic matching falhou, usando ordenação por views: %s", error)
            candidates.sort(key=lambda x: x.get("view_count", 0), reverse=True)
            return candidates
    
    def _download_videos(self, scored_candidates: List[Dict[str, Any]]) -> List[str]:
        """Baixa os melhores candidatos."""
        downloaded_videos: List[str] = []
        visited_ids: set[str] = set()
        output_dir = Path("outputs/video")
        
        for candidate in scored_candidates[:5]:  # Tentar baixar até 5
            if len(downloaded_videos) >= 3:
                break
            
            video_id = candidate.get("id")
            if video_id and video_id in visited_ids:
                continue
            
            try:
                real_path = self.youtube_extractor.download_video(
                    candidate["url"], 
                    str(output_dir)
                )
                downloaded_videos.append(real_path)
                if video_id:
                    visited_ids.add(video_id)
                
                score = candidate.get("relevance_score", "N/A")
                title = candidate.get("title", "sem título")[:40]
self.logger.info(
                    "📥 Vídeo baixado (%d/3): %s [Score: %s]",
                    len(downloaded_videos),
                    title + "...",
                    f"{score:.3f}" if isinstance(score, float) else score
                )
                
            except Exception as error:
self.logger.warning(
                    "⚠️ Erro ao baixar '%s': %s",
                    candidate.get("title", "sem título"),
                    error,
                )
        
        if not downloaded_videos:
            raise RuntimeError("Nenhum vídeo foi baixado com sucesso após semantic matching")
        
        return downloaded_videos