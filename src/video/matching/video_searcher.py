"""
Buscador inteligente de vídeos - AiShorts v2.0
Sistema de busca por palavras-chave e similaridade semântica
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class VideoSearcher:
    """
    Sistema de busca inteligente de vídeos baseado em análise semântica.
    
    Features:
    - Busca por palavras-chave
    - Busca por similaridade semântica
    - Filtros de qualidade
    - Ranking de relevância
    - Cache de resultados
    """
    
    def __init__(self, video_database: Optional[List[Dict]] = None):
        """
        Inicializa o buscador de vídeos.
        
        Args:
            video_database: Banco de dados de vídeos com metadados
        """
        self.logger = logging.getLogger(__name__)
        
        # Banco de dados de vídeos (seria substituído por DB real)
        self.video_database = video_database or []
        
        # Cache para embeddings
        self.embedding_cache = {}
        
        # Configurações
        self.similarity_threshold = 0.7
        self.max_results = 10
        
        self.logger.info("VideoSearcher inicializado com sucesso")
    
    def add_video_database(self, videos: List[Dict]):
        """
        Adiciona vídeos ao banco de dados.
        
        Args:
            videos: Lista de vídeos com metadados
        """
        self.video_database.extend(videos)
        self.logger.info(f"Banco de dados atualizado: {len(self.video_database)} vídeos")
    
    def search_by_keywords(self, keywords: List[str], category: Optional[str] = None, 
                          limit: int = None) -> List[Dict]:
        """
        Busca vídeos por palavras-chave.
        
        Args:
            keywords: Lista de palavras-chave
            category: Categoria opcional para filtro
            limit: Limite de resultados
            
        Returns:
            Lista de vídeos ordenados por relevância
        """
        if not keywords:
            return []
        
        limit = limit or self.max_results
        
        try:
            scored_videos = []
            
            for video in self.video_database:
                score = self._calculate_keyword_score(video, keywords, category)
                
                if score > 0:
                    video_info = video.copy()
                    video_info['relevance_score'] = score
                    video_info['match_type'] = 'keyword'
                    scored_videos.append(video_info)
            
            # Ordenar por relevância
            scored_videos.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Aplicar limite
            results = scored_videos[:limit]
            
            self.logger.info(f"Busca por keywords: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca por keywords: {e}")
            return []
    
    def search_by_semantic(self, query_embedding: np.ndarray, limit: int = None) -> List[Dict]:
        """
        Busca vídeos por similaridade semântica.
        
        Args:
            query_embedding: Embedding da consulta
            limit: Limite de resultados
            
        Returns:
            Lista de vídeos ordenados por similaridade
        """
        if query_embedding is None or len(query_embedding) == 0:
            return []
        
        limit = limit or self.max_results
        
        try:
            scored_videos = []
            
            for video in self.video_database:
                video_embedding = self._get_video_embedding(video)
                
                if video_embedding is not None:
                    similarity = self._calculate_semantic_similarity(query_embedding, video_embedding)
                    
                    if similarity >= self.similarity_threshold:
                        video_info = video.copy()
                        video_info['similarity_score'] = similarity
                        video_info['match_type'] = 'semantic'
                        scored_videos.append(video_info)
            
            # Ordenar por similaridade
            scored_videos.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Aplicar limite
            results = scored_videos[:limit]
            
            self.logger.info(f"Busca semântica: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca semântica: {e}")
            return []
    
    def filter_by_quality(self, video_info_list: List[Dict], 
                         min_quality_score: float = 0.5,
                         prefer_recent: bool = True) -> List[Dict]:
        """
        Filtra vídeos por qualidade.
        
        Args:
            video_info_list: Lista de vídeos para filtrar
            min_quality_score: Score mínimo de qualidade
            prefer_recent: Preferir vídeos mais recentes
            
        Returns:
            Lista de vídeos filtrados por qualidade
        """
        try:
            filtered_videos = []
            
            for video in video_info_list:
                quality_score = self._calculate_quality_score(video)
                
                if quality_score >= min_quality_score:
                    video_info = video.copy()
                    video_info['quality_score'] = quality_score
                    filtered_videos.append(video_info)
            
            # Ordenar por qualidade (e recência se preferido)
            if prefer_recent:
                filtered_videos.sort(
                    key=lambda x: (x['quality_score'], x.get('publication_date', '')),
                    reverse=True
                )
            else:
                filtered_videos.sort(key=lambda x: x['quality_score'], reverse=True)
            
            self.logger.info(f"Filtro de qualidade: {len(filtered_videos)} vídeos aprovados")
            return filtered_videos
            
        except Exception as e:
            self.logger.error(f"Erro no filtro de qualidade: {e}")
            return video_info_list
    
    def search_by_script(self, script_analysis: Dict[str, Any], 
                        prefer_semantic: bool = True,
                        include_categories: List[str] = None) -> List[Dict]:
        """
        Busca vídeos baseada na análise completa de um roteiro.
        
        Args:
            script_analysis: Análise semântica do roteiro
            prefer_semantic: Preferir busca semântica
            include_categories: Categorias para incluir na busca
            
        Returns:
            Lista de vídeos ordenados por relevância
        """
        try:
            all_results = []
            
            # 1. Busca por palavras-chave
            keywords = script_analysis.get('keywords', [])
            if keywords:
                keyword_results = self.search_by_keywords(keywords)
                for result in keyword_results:
                    result['search_method'] = 'keywords'
                all_results.extend(keyword_results)
            
            # 2. Busca semântica se disponível
            if prefer_semantic and 'embedding' in script_analysis:
                embedding = script_analysis['embedding']
                if embedding is not None:
                    semantic_results = self.search_by_semantic(np.array(embedding))
                    for result in semantic_results:
                        result['search_method'] = 'semantic'
                    all_results.extend(semantic_results)
            
            # 3. Filtrar por categorias específicas se fornecidas
            if include_categories:
                all_results = self._filter_by_categories(all_results, include_categories)
            
            # 4. Combinar e remover duplicatas
            combined_results = self._combine_results(all_results)
            
            # 5. Filtrar por qualidade
            quality_results = self.filter_by_quality(combined_results)
            
            # 6. Ordenar final
            final_results = self._rank_final_results(quality_results, script_analysis)
            
            self.logger.info(f"Busca por roteiro: {len(final_results)} vídeos selecionados")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Erro na busca por roteiro: {e}")
            return []
    
    def _calculate_keyword_score(self, video: Dict, keywords: List[str], 
                                category: Optional[str] = None) -> float:
        """Calcula score de relevância baseado em palavras-chave."""
        score = 0.0
        
        # Palavras-chave do vídeo
        video_keywords = set()
        if 'keywords' in video and video['keywords']:
            video_keywords.update(video['keywords'])
        
        # Título do vídeo
        if 'title' in video:
            video_text = video['title'].lower()
            for keyword in keywords:
                if keyword.lower() in video_text:
                    score += 2.0  # Título tem peso maior
        
        # Descrição
        if 'description' in video:
            video_text = video['description'].lower()
            for keyword in keywords:
                if keyword.lower() in video_text:
                    score += 1.0
        
        # Tags
        if 'tags' in video and video['tags']:
            for tag in video['tags']:
                if tag.lower() in [k.lower() for k in keywords]:
                    score += 1.5
        
        # Categoria
        if category and 'category' in video:
            if video['category'].lower() == category.lower():
                score += 3.0
        
        # Normalizar pelo número de palavras-chave
        if keywords:
            score = score / len(keywords)
        
        return min(score, 10.0)  # Limite máximo de 10
    
    def _get_video_embedding(self, video: Dict) -> Optional[np.ndarray]:
        """Extrai embedding de um vídeo."""
        cache_key = f"video_{video.get('id', 'unknown')}"
        
        # Verificar cache
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Tentar usar embedding pré-computado
        if 'embedding' in video and video['embedding'] is not None:
            embedding = np.array(video['embedding'])
            self.embedding_cache[cache_key] = embedding
            return embedding
        
        # Gerar embedding básico baseado em metadados
        try:
            embedding = self._generate_basic_embedding(video)
            self.embedding_cache[cache_key] = embedding
            return embedding
        except:
            return None
    
    def _generate_basic_embedding(self, video: Dict) -> np.ndarray:
        """Gera embedding básico baseado em metadados do vídeo."""
        # Mapeamento de categorias para vetores
        category_map = {
            'space': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'animals': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            'science': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            'nature': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            'history': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            'technology': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            'culture': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            'psychology': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            'geography': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            'food': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        }
        
        # Iniciar com vetor base
        embedding = np.zeros(20)  # 10 categorias + 10 características extras
        
        # Categoria
        category = video.get('category', '').lower()
        category_embedding = category_map.get(category, [0] * 10)
        embedding[:10] = category_embedding
        
        # Características extras (qualidade, duração, etc.)
        quality_score = video.get('quality_score', 0.5)
        duration = video.get('duration', 300)  # 5 minutos padrão
        
        embedding[10] = quality_score
        embedding[11] = min(duration / 3600, 1.0)  # Duração normalizada
        embedding[12] = video.get('views', 0) / 1000000  # Views normalizado
        embedding[13] = video.get('likes', 0) / 10000  # Likes normalizado
        
        # Palavras-chave do vídeo
        video_keywords = video.get('keywords', [])
        for i, keyword in enumerate(video_keywords[:6]):  # Máximo 6 palavras-chave
            if i < 6:
                embedding[14 + i] = 1.0
        
        # Normalizar
        if np.linalg.norm(embedding) > 0:
            embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def _calculate_semantic_similarity(self, embedding1: np.ndarray, 
                                     embedding2: np.ndarray) -> float:
        """Calcula similaridade semântica entre embeddings."""
        try:
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def _calculate_quality_score(self, video: Dict) -> float:
        """Calcula score de qualidade do vídeo."""
        score = 0.0
        
        # Qualidade baseada em métricas
        views = video.get('views', 0)
        likes = video.get('likes', 0)
        comments = video.get('comments', 0)
        duration = video.get('duration', 300)
        
        # Score de engajamento
        if views > 0:
            engagement = (likes + comments) / views
            score += min(engagement * 10, 5.0)  # Máximo 5 pontos
        
        # Score de popularidade
        if views > 10000:
            score += 2.0
        elif views > 1000:
            score += 1.0
        
        # Score de duração ideal (30s a 10min)
        if 30 <= duration <= 600:
            score += 1.5
        elif 15 <= duration <= 900:
            score += 1.0
        
        # Score de qualidade técnica (se disponível)
        if 'resolution' in video:
            resolution = video['resolution']
            if '1080' in resolution:
                score += 1.0
            elif '720' in resolution:
                score += 0.5
        
        # Score de autor/confiabilidade
        if 'channel_subscribers' in video:
            subscribers = video['channel_subscribers']
            if subscribers > 100000:
                score += 1.0
            elif subscribers > 10000:
                score += 0.5
        
        return min(score, 10.0)  # Limite máximo de 10
    
    def _filter_by_categories(self, videos: List[Dict], 
                            include_categories: List[str]) -> List[Dict]:
        """Filtra vídeos por categorias específicas."""
        if not include_categories:
            return videos
        
        filtered = []
        for video in videos:
            video_category = video.get('category', '').lower()
            if video_category in [cat.lower() for cat in include_categories]:
                filtered.append(video)
        
        return filtered
    
    def _combine_results(self, results: List[Dict]) -> List[Dict]:
        """Combina resultados removendo duplicatas."""
        seen_ids = set()
        combined = []
        
        for result in results:
            video_id = result.get('id', result.get('url', ''))
            if video_id not in seen_ids:
                seen_ids.add(video_id)
                combined.append(result)
        
        return combined
    
    def _rank_final_results(self, results: List[Dict], 
                          script_analysis: Dict[str, Any]) -> List[Dict]:
        """Rankeamento final dos resultados."""
        # Combinar diferentes scores
        for result in results:
            relevance = result.get('relevance_score', 0)
            similarity = result.get('similarity_score', 0)
            quality = result.get('quality_score', 0)
            
            # Score combinado com pesos
            combined_score = (relevance * 0.4 + similarity * 0.4 + quality * 0.2)
            result['final_score'] = combined_score
        
        # Ordenar por score final
        results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return results
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de busca."""
        return {
            'database_size': len(self.video_database),
            'cache_size': len(self.embedding_cache),
            'similarity_threshold': self.similarity_threshold,
            'max_results': self.max_results
        }


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar buscador
    searcher = VideoSearcher()
    
    # Adicionar vídeos de exemplo
    sample_videos = [
        {
            'id': 'video_1',
            'title': 'Explorando o Espaço - As Estrelas',
            'description': 'Um vídeo fascinante sobre as estrelas e o universo',
            'category': 'space',
            'keywords': ['estrela', 'universo', 'espaço'],
            'views': 50000,
            'likes': 2500,
            'comments': 150,
            'duration': 300,
            'url': 'https://example.com/video1'
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
            'duration': 450,
            'url': 'https://example.com/video2'
        }
    ]
    
    searcher.add_video_database(sample_videos)
    
    print("=== Teste do VideoSearcher ===")
    
    # Teste 1: Busca por keywords
    print("\n1. Busca por palavras-chave:")
    keywords_results = searcher.search_by_keywords(['estrela', 'universo'])
    for video in keywords_results:
        print(f"  - {video['title']} (score: {video.get('relevance_score', 0):.2f})")
    
    # Teste 2: Busca semântica
    print("\n2. Busca semântica:")
    query_embedding = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.8, 0.3, 0.1, 0.05, 0, 0, 0, 0, 0, 0])
    semantic_results = searcher.search_by_semantic(query_embedding)
    for video in semantic_results:
        print(f"  - {video['title']} (similarity: {video.get('similarity_score', 0):.2f})")
    
    # Teste 3: Filtro de qualidade
    print("\n3. Filtro de qualidade:")
    quality_results = searcher.filter_by_quality(keywords_results + semantic_results)
    for video in quality_results:
        print(f"  - {video['title']} (quality: {video.get('quality_score', 0):.2f})")
    
    # Estatísticas
    print("\n4. Estatísticas:")
    stats = searcher.get_search_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    print("\n=== Teste concluído ===")