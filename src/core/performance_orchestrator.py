"""
Performance Orchestrator - Orquestrador de Performance
AiShorts v2.0 - Integração de Todas as Otimizações

Orquestrador que integra todas as otimizações de performance:
- Downloads paralelos do YouTube
- Cache inteligente de conteúdo
- CLIP pré-validação
- Requests assíncronos OpenRouter
- Max tokens automático
- Memory monitoring
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from src.core.async_openrouter_client import AsyncOpenRouterClient, AsyncRequest, get_async_openrouter_client
from src.core.content_cache import get_content_cache
from src.core.memory_monitor import get_memory_monitor, memory_context
from src.video.extractors.youtube_extractor import YouTubeExtractor
from src.video.validation.clip_pre_validator import get_video_pre_validator, VideoCandidate
from src.core.model_manager import get_model_manager
from src.core.video_quality_optimizer import get_video_quality_optimizer
from src.core.content_virality_predictor import get_content_virality_predictor

logger = logging.getLogger(__name__)


class PerformanceOrchestrator:
    """
    Orquestrador de performance que integra todas as otimizações.
    
    Features:
    - Geração paralela de tema + script
    - Busca e download paralelo de vídeos
    - Cache inteligente de conteúdo
    - CLIP pré-validação de vídeos
    - Memory monitoring contínuo
    - Async/await throughout
    """
    
    def __init__(self):
        """Inicializa o orquestrador de performance"""
        # Cliente OpenRouter assíncrono
        self.async_client = get_async_openrouter_client()
        
        # Cache de conteúdo
        self.content_cache = get_content_cache()
        
        # Memory monitor
        self.memory_monitor = get_memory_monitor()
        
        # YouTube extractor com otimizações
        self.youtube_extractor = YouTubeExtractor()
        
        # Validador CLIP
        self.clip_validator = get_video_pre_validator()
        
        # Model manager
        self.model_manager = get_model_manager()
        
        # Novos módulos de otimização com LLM
        self.quality_optimizer = get_video_quality_optimizer(self.async_client)
        self.virality_predictor = get_content_virality_predictor(self.async_client)
        
        # Estatísticas de performance
        self.performance_stats = {
            'total_pipeline_runs': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'parallel_downloads_saved_seconds': 0,
            'async_requests_saved_seconds': 0,
            'clip_validations_performed': 0,
            'memory_peaks_gb': 0.0,
            'average_pipeline_time': 0.0,
            'quality_analyses_performed': 0,
            'virality_predictions_made': 0,
            'enhanced_queries_generated': 0
        }
        
        self.logger = logging.getLogger(__name__)
self.logger.info(" PerformanceOrchestrator inicializado com todas as otimizações")
    
    async def generate_theme_and_script_async(self, 
                                            theme_category: str,
                                            theme_requirements: List[str] = None,
                                            script_requirements: List[str] = None) -> Tuple[str, str, Dict[str, Any]]:
        """
        Gera tema e script em paralelo com cache e max_tokens automático.
        
        Args:
            theme_category: Categoria do tema
            theme_requirements: Requisitos específicos do tema
            script_requirements: Requisitos específicos do script
            
        Returns:
            Tuple com (theme, script, performance_metrics)
        """
        with memory_context("generate_theme_and_script"):
            start_time = time.time()
            
            # Gerar cache keys
            theme_cache_key = f"theme_{theme_category}_{hash(str(theme_requirements))}"
            script_cache_key = f"script_{theme_category}_{hash(str(script_requirements))}"
            
            # Tentar obter do cache
            cached_theme = self.content_cache.get(theme_cache_key, "theme")
            cached_script = self.content_cache.get(script_cache_key, "script")
            
            cache_hits = 0
            if cached_theme:
self.logger.info(" Tema obtido do cache")
                self.performance_stats['cache_hits'] += 1
                cache_hits += 1
                theme = cached_theme
            else:
                self.performance_stats['cache_misses'] += 1
                theme = None
            
            if cached_script:
self.logger.info(" Script obtido do cache")
                self.performance_stats['cache_hits'] += 1
                cache_hits += 1
                script = cached_script
            else:
                self.performance_stats['cache_misses'] += 1
                script = None
            
            # Se ambos em cache, retornar imediatamente
            if theme and script:
                total_time = time.time() - start_time
self.logger.info(f" Tudo do cache! Tempo: {total_time:.2f}s")
                
                return theme, script, {
                    'cache_hits': 2,
                    'async_time_saved': 0,
                    'total_time': total_time,
                    'source': 'cache'
                }
            
            # Gerar prompts (simplificado para exemplo)
            theme_prompt = f"Crie um tema viral sobre {theme_category}"
            script_prompt = f"Crie um script curto sobre: {theme or 'o tema acima'}"
            
            # Criar requests assíncronos
            theme_req = AsyncRequest(
                prompt=theme_prompt,
                task_type="theme",
                temperature=0.8
            ) if not theme else None
            
            script_req = AsyncRequest(
                prompt=script_prompt,
                task_type="script",
                temperature=0.6
            ) if not script else None
            
            # Preparar tasks
            tasks = []
            if theme_req:
                tasks.append(('theme', self.async_client._make_single_request(theme_req)))
            if script_req:
                tasks.append(('script', self.async_client._make_single_request(script_req)))
            
            # Executar em paralelo
            results = {}
            if tasks:
                task_names, coroutines = zip(*tasks)
                task_results = await asyncio.gather(*coroutines, return_exceptions=True)
                
                for name, result in zip(task_names, task_results):
                    if isinstance(result, Exception):
self.logger.error(f" Erro no {name}: {result}")
                        # Em caso de falha, usar fallback ou retry
                        if name == 'theme':
                            theme = self._fallback_theme(theme_category)
                        elif name == 'script':
                            script = self._fallback_script(theme or theme_category)
                    else:
                        results[name] = result.content
                        
                        # Salvar no cache
                        if name == 'theme':
                            theme = result.content
                            self.content_cache.set(theme_cache_key, theme, "theme", ttl_hours=48.0)
                        elif name == 'script':
                            script = result.content
                            self.content_cache.set(script_cache_key, script, "script", ttl_hours=24.0)
            
            total_time = time.time() - start_time
            estimated_sequential_time = total_time * len(tasks)  # Tempo estimado se fosse sequencial
            time_saved = max(0, estimated_sequential_time - total_time)
            
            self.performance_stats['async_requests_saved_seconds'] += time_saved
            self.performance_stats['average_pipeline_time'] = (
                (self.performance_stats['average_pipeline_time'] * (self.performance_stats['total_pipeline_runs']) + total_time) /
                (self.performance_stats['total_pipeline_runs'] + 1)
            )
            self.performance_stats['total_pipeline_runs'] += 1
            
            performance_metrics = {
                'cache_hits': cache_hits,
                'async_time_saved': time_saved,
                'total_time': total_time,
                'parallel_tasks': len(tasks),
                'source': 'mixed' if cache_hits > 0 else 'generated'
            }
            
self.logger.info(f" Tema e script gerados: {total_time:.2f}s (economizados: {time_saved:.2f}s)")
            
            return results.get('theme', theme), results.get('script', script), performance_metrics
    
    async def find_and_download_videos_optimized(self, 
                                               queries: List[str],
                                               max_videos: int = 3,
                                               use_clip_validation: bool = True) -> Tuple[List[str], Dict[str, Any]]:
        """
        Busca e baixa vídeos com todas as otimizações.
        
        Args:
            queries: Lista de queries de busca
            max_videos: Máximo de vídeos para baixar
            use_clip_validation: Se deve usar validação CLIP
            
        Returns:
            Tuple com (video_paths, performance_metrics)
        """
        with memory_context("find_and_download_videos"):
            start_time = time.time()
            
            # Fase 1: Busca paralela de vídeos
self.logger.info(f" Buscando vídeos para {len(queries)} queries")
            
            # Buscar vídeos para cada query em paralelo
            search_tasks = []
            for query in queries:
                # Usar o método search do youtube extractor
                search_tasks.append(self._search_videos_async(query))
            
            # Aguardar todas as buscas
            all_candidates = []
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            for result in search_results:
                if isinstance(result, Exception):
self.logger.warning(f" Erro na busca: {result}")
                else:
                    all_candidates.extend(result)
            
self.logger.info(f" Encontrados {len(all_candidates)} candidatos totais")
            
            # Fase 2: Pré-validação CLIP se disponível
            if use_clip_validation and self.clip_validator and all_candidates:
self.logger.info(" Validando candidatos com CLIP...")
                
                # Converter para VideoCandidate objects
                video_candidates = []
                for video in all_candidates:
                    candidate = VideoCandidate(
                        id=video['id'],
                        title=video.get('title', ''),
                        description=video.get('description', ''),
                        thumbnail_url=video.get('thumbnail', ''),
                        video_url=video.get('url', video.get('webpage_url', f"https://www.youtube.com/watch?v={video['id']}")),
                        duration=video.get('duration', 0),
                        view_count=video.get('view_count', 0),
                        upload_date=video.get('upload_date', '')
                    )
                    video_candidates.append(candidate)
                
                # Validação CLIP assíncrona
                validated_candidates = await self.clip_validator.validate_candidates_async(
                    video_candidates, 
                    queries[0],  # Usar primeira query como referência
                    max_videos * 2  # Validar o dobro para ter opções
                )
                
self.logger.info(f" {len(validated_candidates)} candidatos validados")
                all_candidates = [
                    {
                        'id': c.id,
                        'title': c.title,
                        'description': c.description,
                        'webpage_url': c.video_url,
                        'duration': c.duration,
                        'view_count': c.view_count,
                        'upload_date': c.upload_date,
                        'relevance_score': c.relevance_score
                    }
                    for c in validated_candidates
                ]
                
                self.performance_stats['clip_validations_performed'] += len(video_candidates)
            
            # Fase 3: Download paralelo dos melhores vídeos
            if all_candidates:
                # Ordenar por relevância e pegar os melhores
                if all_candidates[0].get('relevance_score'):
                    all_candidates.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                else:
                    # Fallback para ordenação por views
                    all_candidates.sort(key=lambda x: x.get('view_count', 0), reverse=True)
                
                # Selecionar top N
                selected_videos = all_candidates[:max_videos]
                video_urls = [v['webpage_url'] for v in selected_videos]
                
self.logger.info(f" Iniciando download paralelo de {len(video_urls)} vídeos")
                
                # Download paralelo usando método otimizado
                downloaded_paths = self.youtube_extractor.download_videos_parallel(
                    video_urls,
                    max_workers=3
                )
                
                # Calcular tempo economizado
                download_time = time.time() - start_time
                estimated_sequential_time = len(video_urls) * 15  # Estimativa: 15s por download sequencial
                time_saved = max(0, estimated_sequential_time - download_time)
                
                self.performance_stats['parallel_downloads_saved_seconds'] += time_saved
                
                performance_metrics = {
                    'total_candidates': len(all_candidates),
                    'validated_candidates': len([c for c in all_candidates if c.get('relevance_score')]),
                    'downloaded_videos': len(downloaded_paths),
                    'parallel_time_saved': time_saved,
                    'total_time': download_time,
                    'clip_validation_used': use_clip_validation
                }
                
self.logger.info(f" Download concluído: {len(downloaded_paths)} vídeos em {download_time:.2f}s")
                
                return downloaded_paths, performance_metrics
            
            return [], {'total_time': time.time() - start_time, 'downloaded_videos': 0}
    
    async def _search_videos_async(self, query: str, max_results: int = 10) -> List[Dict]:
        """Wrapper assíncrono para busca de vídeos"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.youtube_extractor.search_videos, query, max_results)
    
    def _fallback_theme(self, category: str) -> str:
        """Fallback para tema em caso de falha"""
        return f"Descubra {category} fatos fascinantes que vão te surpreender"
    
    def _fallback_script(self, theme: str) -> str:
        """Fallback para script em caso de falha"""
        return f"""
Hook: Você não vai acreditar no que descobri sobre {theme}.

Body: Prepare-se para uma jornada incrível através de fatos surpreendentes que vão mudar sua perspectiva sobre {theme}. Cada revelação mais fascinante que a anterior.

Conclusion: O mundo de {theme} é muito mais extraordinário do que imaginamos.
"""
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas comprehensivas de performance"""
        # Estatísticas individuais
        cache_stats = self.content_cache.get_stats()
        memory_stats = self.memory_monitor.get_current_stats()
        model_stats = self.model_manager.get_memory_stats()
        client_stats = self.async_client.get_stats()
        
        # Combinar tudo
        comprehensive_stats = {
            'performance_orchestrator': self.performance_stats,
            'content_cache': cache_stats,
            'memory_monitor': {
                'current_gb': memory_stats.process_gb,
                'system_percent': memory_stats.system_percent,
                'status': 'critical' if memory_stats.is_critical else ('warning' if memory_stats.is_warning else 'normal'),
                'available_gb': memory_stats.available_gb
            },
            'model_manager': {
                'loaded_models': model_stats['loaded_models'],
                'process_memory_gb': model_stats['process_memory_gb'],
                'cache_size': len(model_stats['model_usage_counts'])
            },
            'async_openrouter': client_stats,
            'optimization_summary': {
                'total_time_saved_seconds': (
                    self.performance_stats['async_requests_saved_seconds'] +
                    self.performance_stats['parallel_downloads_saved_seconds']
                ),
                'cache_hit_rate': cache_stats.get('hit_rate', '0%'),
                'average_pipeline_time': self.performance_stats['average_pipeline_time'],
                'memory_efficiency': 'Optimized' if memory_stats.process_gb < 2.0 else 'High'
            }
        }
        
        return comprehensive_stats
    
    async def cleanup(self):
        """Limpa todos os recursos e caches"""
self.logger.info("🧹 Iniciando cleanup do PerformanceOrchestrator...")
        
        # Limpar caches se necessário
        if self.memory_monitor.suggest_cleanup():
            self.memory_monitor.force_garbage_collection()
            self.model_manager.cleanup_models()
        
        # Fechar cliente HTTP
        await self.async_client.close()
        
self.logger.info(" Cleanup concluído")
    
    async def run_enhanced_pipeline(self, 
                                  theme_category: str = "animals",
                                  enable_quality_analysis: bool = True,
                                  enable_virality_prediction: bool = True,
                                  enable_enhanced_broll: bool = True) -> Dict[str, Any]:
        """
        Pipeline completo avançado com todas as otimizações LLM.
        
        Args:
            theme_category: Categoria para geração
            enable_quality_analysis: Se deve analisar qualidade dos vídeos
            enable_virality_prediction: Se deve prever viralidade do conteúdo
            enable_enhanced_broll: Se deve usar B-roll enhancement
            
        Returns:
            Resultados completos do pipeline avançado
        """
        with memory_context("enhanced_pipeline"):
            start_time = time.time()
            
self.logger.info(" Iniciando Enhanced Pipeline com otimizações LLM avançadas")
            
            # ETAPA 1: Geração de tema e script paralela
            theme, script, gen_metrics = await self.generate_theme_and_script_async(
                theme_category=theme_category
            )
            
            enhanced_results = {
                'theme': theme,
                'script': script,
                'generation_metrics': gen_metrics
            }
            
            # ETAPA 2: Previsão de viralidade (se habilitado)
            virality_analysis = None
            if enable_virality_prediction and theme and script:
self.logger.info(" Analisando potencial viral...")
                virality_analysis = self.virality_predictor.predict_virality(
                    theme=theme,
                    script=script,
                    category=theme_category,
                    target_platform="tiktok"
                )
                self.performance_stats['virality_predictions_made'] += 1
                enhanced_results['virality_analysis'] = virality_analysis
            
            # ETAPA 3: Enhanced B-roll queries (se habilitado)
            enhanced_queries = None
            if enable_enhanced_broll and theme:
self.logger.info(" Gerando enhanced B-roll queries...")
                from src.pipeline.services.broll_query_service import BrollQueryService
                broll_service = BrollQueryService(self.async_client)
                
                enhanced_queries = broll_service.enhance_queries_with_scene_detection(
                    script_text=script,
                    video_metadata={'category': theme_category, 'virality_score': virality_analysis.get('virality_scores', {}).get('overall_score', 50) if virality_analysis else 50}
                )
                self.performance_stats['enhanced_queries_generated'] += 1
                enhanced_results['enhanced_queries'] = enhanced_queries
            
            # ETAPA 4: Busca e download de vídeos otimizado
            # Usar queries enhanced se disponíveis, senão usar keywords do tema
            search_queries = enhanced_queries if enhanced_queries else [theme_category] + theme.split()[:3]
            
            video_paths, video_metrics = await self.find_and_download_videos_optimized(
                queries=search_queries,
                max_videos=3
            )
            enhanced_results['video_paths'] = video_paths
            enhanced_results['video_metrics'] = video_metrics
            
            # ETAPA 5: Análise de qualidade dos vídeos (se habilitado)
            quality_analyses = []
            if enable_quality_analysis and video_paths:
self.logger.info(" Analisando qualidade dos vídeos...")
                
                for video_path in video_paths:
                    try:
                        quality_analysis = self.quality_optimizer.analyze_video_quality(
                            video_path=video_path,
                            target_platform="tiktok",
                            detailed_analysis=True
                        )
                        quality_analyses.append(quality_analysis)
                        self.performance_stats['quality_analyses_performed'] += 1
                        
                    except Exception as e:
self.logger.warning(f" Falha na análise de qualidade de {video_path}: {e}")
                
                enhanced_results['quality_analyses'] = quality_analyses
            
            # ETAPA 6: Estatísticas finais avançadas
            final_stats = await self.get_comprehensive_stats()
            
            # Métricas específicas do enhanced pipeline
            enhanced_metrics = {
                'enhanced_pipeline_duration': time.time() - start_time,
                'optimizations_applied': {
                    'quality_analysis': enable_quality_analysis,
                    'virality_prediction': enable_virality_prediction,
                    'enhanced_broll': enable_enhanced_broll
                },
                'content_insights': {
                    'virality_level': virality_analysis.get('virality_scores', {}).get('virality_level', 'unknown') if virality_analysis else 'not_analyzed',
                    'average_quality_score': sum([qa.get('overall_score', 0) for qa in quality_analyses]) / len(quality_analyses) if quality_analyses else 0,
                    'enhanced_queries_count': len(enhanced_queries) if enhanced_queries else 0
                },
                'performance_improvements': {
                    'llm_enhancements_active': sum([enable_quality_analysis, enable_virality_prediction, enable_enhanced_broll]),
                    'total_llm_requests': self.performance_stats['virality_predictions_made'] + 
                                        self.performance_stats['enhanced_queries_generated'],
                    'quality_analyses_performed': self.performance_stats['quality_analyses_performed']
                }
            }
            
            # Resultado final
            final_result = {
                **enhanced_results,
                'enhanced_metrics': enhanced_metrics,
                'comprehensive_stats': final_stats,
                'success': True,
                'pipeline_type': 'enhanced_llm_optimized'
            }
            
            total_time = time.time() - start_time
self.logger.info(f" Enhanced Pipeline concluído em {total_time:.2f}s")
self.logger.info(f" Otimizações LLM aplicadas: {enhanced_metrics['performance_improvements']['llm_enhancements_active']}")
            
            return final_result


# Instância global
performance_orchestrator = None


def get_performance_orchestrator() -> PerformanceOrchestrator:
    """Retorna instância global do orquestrador de performance"""
    global performance_orchestrator
    if performance_orchestrator is None:
        performance_orchestrator = PerformanceOrchestrator()
    return performance_orchestrator


# Função de conveniência principal
async def run_optimized_pipeline(theme_category: str = "technology", 
                                enhanced_mode: bool = False) -> Dict[str, Any]:
    """
    Executa pipeline completo com todas as otimizações.
    
    Args:
        theme_category: Categoria para geração
        enhanced_mode: Se deve usar o pipeline enhanced com LLM avançado
        
    Returns:
        Resultados completos do pipeline com métricas
    """
    orchestrator = get_performance_orchestrator()
    
    try:
        if enhanced_mode:
            # Usar Enhanced Pipeline com todas as otimizações LLM
            return await orchestrator.run_enhanced_pipeline(
                theme_category=theme_category,
                enable_quality_analysis=True,
                enable_virality_prediction=True,
                enable_enhanced_broll=True
            )
        
        # Pipeline padrão otimizado (legado)
        # Etapa 1: Gerar tema e script em paralelo
        theme, script, gen_metrics = await orchestrator.generate_theme_and_script_async(
            theme_category=theme_category
        )
        
        # Etapa 2: Buscar e baixar vídeos otimizado
        # Extrair keywords do tema/cript para busca
        keywords = [theme_category] + theme.split()[:3]  # Simplificado
        
        video_paths, video_metrics = await orchestrator.find_and_download_videos_optimized(
            queries=keywords,
            max_videos=3
        )
        
        # Etapa 3: Obter estatísticas finais
        final_stats = await orchestrator.get_comprehensive_stats()
        
        results = {
            'theme': theme,
            'script': script,
            'video_paths': video_paths,
            'performance_metrics': {
                'generation': gen_metrics,
                'videos': video_metrics,
                'overall': final_stats['optimization_summary']
            },
            'success': True,
            'total_time': gen_metrics['total_time'] + video_metrics['total_time'],
            'pipeline_type': 'standard_optimized'
        }
        
orchestrator.logger.info(f" Pipeline otimizado concluído em {results['total_time']:.2f}s")
        return results
        
    except Exception as e:
orchestrator.logger.error(f" Erro no pipeline otimizado: {e}")
        return {
            'success': False,
            'error': str(e),
            'theme': None,
            'script': None,
            'video_paths': [],
            'performance_metrics': {}
        }
    
    finally:
        await orchestrator.cleanup()


async def run_enhanced_pipeline(theme_category: str = "animals") -> Dict[str, Any]:
    """
    Função de conveniência para o Enhanced Pipeline com todas as otimizações LLM.
    
    Args:
        theme_category: Categoria para geração
        
    Returns:
        Resultados completos do enhanced pipeline
    """
    return await run_optimized_pipeline(theme_category=theme_category, enhanced_mode=True)