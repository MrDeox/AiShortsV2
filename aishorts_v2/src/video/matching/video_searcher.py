"""
Sistema de busca inteligente de vídeos para matching com roteiros.
Implementa diferentes estratégias de busca e filtragem por qualidade.
"""

from typing import List, Dict, Tuple, Optional
import re
from dataclasses import dataclass
import numpy as np


@dataclass
class VideoInfo:
    """Estrutura de dados para informações de vídeo."""
    id: str
    title: str
    description: str
    duration: int  # duração em segundos
    views: int
    likes: int
    upload_date: str
    channel: str
    category: str
    tags: List[str]
    quality_score: float = 0.0
    semantic_score: float = 0.0
    keyword_score: float = 0.0


class VideoSearcher:
    """
    Classe para busca inteligente de vídeos baseada em análise semântica.
    """
    
    def __init__(self):
        """Inicializa o buscador de vídeos."""
        # Banco de dados de exemplo de vídeos (em produção, seria uma API real)
        self.video_database = self._initialize_sample_database()
    
    def _initialize_sample_database(self) -> List[VideoInfo]:
        """Inicializa banco de dados de exemplo com vídeos."""
        return [
            VideoInfo(
                id="video_001",
                title="Espaço: Uma Jornada Incrível pelo Universo",
                description="Explore as maravilhas do espaço com imagens espetaculares de galáxias e planetas distantes.",
                duration=300,
                views=1000000,
                likes=50000,
                upload_date="2024-01-15",
                channel="Ciência Espacial",
                category="SPACE",
                tags=["espaço", "universo", "galáxias", "estrelas", "astronomia"]
            ),
            VideoInfo(
                id="video_002",
                title="Delfins em Ação: A Inteligência dos Mamíferos Marinhos",
                description="Descubra a incrível inteligência e agilidade dos golfinhos em seu habitat natural.",
                duration=450,
                views=750000,
                likes=35000,
                upload_date="2024-02-20",
                channel="Vida Selvagem",
                category="ANIMALS",
                tags=["delfins", "golfinhos", "mamíferos", "marinhos", "inteligência"]
            ),
            VideoInfo(
                id="video_003",
                title="Floresta Amazônica: O Pulmão Verde do Mundo",
                description="Uma viagem pela biodiversidade única da maior floresta tropical do planeta.",
                duration=600,
                views=1200000,
                likes=60000,
                upload_date="2024-01-10",
                channel="Natureza Brasil",
                category="NATURE",
                tags=["amazônia", "floresta", "biodiversidade", "brasil", "tropical"]
            ),
            VideoInfo(
                id="video_004",
                title="Inteligência Artificial: O Futuro da Tecnologia",
                description="Explore como a IA está revolucionando diversos setores da sociedade moderna.",
                duration=480,
                views=800000,
                likes=40000,
                upload_date="2024-03-05",
                channel="Tech Future",
                category="TECHNOLOGY",
                tags=["IA", "inteligência artificial", "tecnologia", "futuro", "inovação"]
            ),
            VideoInfo(
                id="video_005",
                title="Golfinhos Brilhantes:.show de Inteligência Marina",
                description="Veja golfinhos realizando truques incríveis e demonstrando sua incrível inteligência.",
                duration=360,
                views=950000,
                likes=48000,
                upload_date="2024-02-14",
                channel="Oceanos Incríveis",
                category="ANIMALS",
                tags=["golfinhos", "inteligência", "trucos", "marinhos", "show"]
            )
        ]
    
    def search_by_keywords(self, keywords: List[str], category: Optional[str] = None, 
                          max_results: int = 10) -> List[VideoInfo]:
        """
        Busca vídeos baseados em palavras-chave.
        
        Args:
            keywords (List[str]): Lista de palavras-chave
            category (Optional[str]): Categoria do vídeo (opcional)
            max_results (int): Número máximo de resultados
            
        Returns:
            List[VideoInfo]: Lista de vídeos encontrados
        """
        matching_videos = []
        
        for video in self.video_database:
            score = 0
            video_text = f"{video.title} {video.description} {' '.join(video.tags)}".lower()
            
            # Pontua por correspondência de palavras-chave
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in video_text:
                    score += 2  # Pontuação maior para correspondência exata
                
                # Pontua por palavras similares ou parciais
                for word in video_text.split():
                    if keyword_lower in word or word in keyword_lower:
                        score += 0.5
                        break
            
            # Bonus por categoria
            if category and video.category == category:
                score += 3
            
            if score > 0:
                video.keyword_score = score
                matching_videos.append(video)
        
        # Ordena por score e retorna os melhores
        matching_videos.sort(key=lambda v: v.keyword_score, reverse=True)
        return matching_videos[:max_results]
    
    def search_by_semantic(self, embedding: np.ndarray, max_results: int = 10) -> List[VideoInfo]:
        """
        Busca vídeos usando similaridade semântica.
        
        Args:
            embedding (np.ndarray): Vetor de embedding do roteiro
            max_results (int): Número máximo de resultados
            
        Returns:
            List[VideoInfo]: Lista de vídeos ordenados por similaridade semântica
        """
        # Em produção, cada vídeo teria seu próprio embedding pré-calculado
        # Por enquanto, simulamos usando títulos e descrições
        
        semantic_scores = []
        
        for video in self.video_database:
            video_text = f"{video.title} {video.description}"
            video_embedding = self._simulate_embedding(video_text)
            
            if video_embedding is not None:
                similarity = self._cosine_similarity(embedding, video_embedding)
                video.semantic_score = similarity
                semantic_scores.append(video)
        
        # Ordena por similaridade semântica
        semantic_scores.sort(key=lambda v: v.semantic_score, reverse=True)
        return semantic_scores[:max_results]
    
    def _simulate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Simula embedding para fins de demonstração.
        Em produção, usaria o mesmo método do SemanticAnalyzer.
        """
        # Simulação simples: hash de palavras para vetor
        words = text.lower().split()
        vector = np.zeros(300)  # Tamanho típico de embedding spaCy
        
        for i, word in enumerate(words[:300]):  # Limita a 300 palavras
            hash_val = hash(word) % 300
            vector[hash_val] += 1 / (i + 1)  # Palavras mais próximas têm peso maior
        
        return vector if np.any(vector) else None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similaridade cosseno entre dois vetores."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def filter_by_quality(self, videos: List[VideoInfo], 
                         min_views: int = 10000,
                         min_likes_ratio: float = 0.02,
                         min_quality_score: float = 0.0) -> List[VideoInfo]:
        """
        Filtra vídeos por critérios de qualidade.
        
        Args:
            videos (List[VideoInfo]): Lista de vídeos para filtrar
            min_views (int): Número mínimo de visualizações
            min_likes_ratio (float): Razão mínima likes/views
            min_quality_score (float): Score mínimo de qualidade
            
        Returns:
            List[VideoInfo]: Lista filtrada de vídeos
        """
        filtered_videos = []
        
        for video in videos:
            # Critério 1: Visualizações mínimas
            if video.views < min_views:
                continue
            
            # Critério 2: Razão likes/views
            if video.views > 0:
                likes_ratio = video.likes / video.views
                if likes_ratio < min_likes_ratio:
                    continue
            
            # Critério 3: Score de qualidade
            if video.quality_score < min_quality_score:
                continue
            
            filtered_videos.append(video)
        
        return filtered_videos
    
    def calculate_quality_score(self, video: VideoInfo) -> float:
        """
        Calcula score de qualidade baseado em métricas do vídeo.
        
        Args:
            video (VideoInfo): Informações do vídeo
            
        Returns:
            float: Score de qualidade (0-1)
        """
        # Componentes do score
        views_score = min(video.views / 1000000, 1.0)  # Normaliza por 1M views
        
        if video.views > 0:
            engagement_score = min(video.likes / video.views * 10, 1.0)  # Normaliza engajamento
        else:
            engagement_score = 0.0
        
        # Bonus por duração adequada (entre 3-10 minutos)
        duration_score = 1.0
        if video.duration < 180:  # Menos de 3 minutos
            duration_score = 0.5
        elif video.duration > 600:  # Mais de 10 minutos
            duration_score = 0.7
        
        # Peso dos componentes
        total_score = (views_score * 0.4 + 
                      engagement_score * 0.4 + 
                      duration_score * 0.2)
        
        return min(total_score, 1.0)
    
    def search_combined(self, keywords: List[str], semantic_embedding: np.ndarray,
                       category: Optional[str] = None, max_results: int = 10) -> List[VideoInfo]:
        """
        Busca combinada usando palavras-chave e análise semântica.
        
        Args:
            keywords (List[str]): Palavras-chave do roteiro
            semantic_embedding (np.ndarray): Embedding semântico do roteiro
            category (Optional[str]): Categoria preferida
            max_results (int): Número máximo de resultados
            
        Returns:
            List[VideoInfo]: Lista de vídeos rankeados
        """
        # Busca por palavras-chave
        keyword_results = self.search_by_keywords(keywords, category)
        
        # Busca por similaridade semântica
        semantic_results = self.search_by_semantic(semantic_embedding)
        
        # Combina resultados
        video_scores = {}
        
        for video in keyword_results:
            if video.id not in video_scores:
                video_scores[video.id] = {
                    'video': video,
                    'combined_score': 0.0,
                    'keyword_score': 0.0,
                    'semantic_score': 0.0
                }
            
            video_scores[video.id]['keyword_score'] = video.keyword_score
            video_scores[video.id]['combined_score'] += video.keyword_score * 0.6
        
        for video in semantic_results:
            if video.id not in video_scores:
                video_scores[video.id] = {
                    'video': video,
                    'combined_score': 0.0,
                    'keyword_score': 0.0,
                    'semantic_score': 0.0
                }
            
            video_scores[video.id]['semantic_score'] = video.semantic_score
            video_scores[video.id]['combined_score'] += video.semantic_score * 0.4
        
        # Calcula score de qualidade para todos
        for video_id, data in video_scores.items():
            data['video'].quality_score = self.calculate_quality_score(data['video'])
            
            # Adiciona bonus de qualidade ao score combinado
            data['combined_score'] += data['video'].quality_score * 0.2
        
        # Ordena por score combinado
        ranked_videos = sorted(
            video_scores.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        # Retorna apenas os vídeos
        return [item['video'] for item in ranked_videos[:max_results]]
    
    def get_best_match(self, keywords: List[str], semantic_embedding: np.ndarray,
                      category: Optional[str] = None) -> Optional[VideoInfo]:
        """
        Retorna o melhor vídeo para o roteiro.
        
        Args:
            keywords (List[str]): Palavras-chave do roteiro
            semantic_embedding (np.ndarray): Embedding semântico do roteiro
            category (Optional[str]): Categoria preferida
            
        Returns:
            Optional[VideoInfo]: Melhor vídeo encontrado ou None
        """
        results = self.search_combined(keywords, semantic_embedding, category, max_results=1)
        return results[0] if results else None