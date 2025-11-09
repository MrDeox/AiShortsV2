"""
CLIP Relevance Scorer - AiShorts v2.0
Sistema de scoring semântico real texto-vídeo usando modelo CLIP

Este módulo implementa scoring semântico avançado usando o modelo CLIP para:
- Avaliar relevância real entre texto do roteiro e conteúdo de vídeos
- Gerar embeddings visuais e textuais para matching preciso
- Ranking inteligente de vídeos baseado em similaridade semântica
- Cache de embeddings para performance otimizada
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import pickle
from datetime import datetime
import cv2
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel
import requests
import tempfile

# Importar ModelManager para otimização de memória
try:
    from src.core.model_manager import get_model_manager
    MODEL_MANAGER_AVAILABLE = True
except ImportError:
    MODEL_MANAGER_AVAILABLE = False
    logging.warning("ModelManager não disponível, usando carregamento tradicional")

logger = logging.getLogger(__name__)


class CLIPRelevanceScorer:
    """
    Sistema de scoring semântico usando modelo CLIP para análise texto-vídeo.
    
    Features:
    - Score de relevância real texto-vídeo usando CLIP
    - Geração de embeddings visuais e textuais
    - Ranking otimizado por similaridade semântica
    - Sistema de cache para performance
    - Fallback para TF-IDF quando CLIP não disponível
    """
    
    def __init__(self, cache_dir: Optional[str] = None, device: str = "auto"):
        """
        Inicializa o CLIP Relevance Scorer com lazy loading.
        
        Args:
            cache_dir: Diretório para cache de embeddings
            device: Dispositivo para inferência ('auto', 'cpu', 'cuda')
        """
        self.logger = logging.getLogger(__name__)
        
        # Configurar cache
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache/clip_embeddings")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache em memória
        self.text_cache = {}
        self.video_cache = {}
        
        # Configurar dispositivo
        self.device = self._setup_device(device)
        
        # Lazy loading - não carregar modelo imediatamente
        self.model = None
        self.processor = None
        self.model_name = "openai/clip-vit-base-patch32"
        
        # ModelManager para otimização
        self._model_manager = get_model_manager() if MODEL_MANAGER_AVAILABLE else None
        self._use_model_manager = MODEL_MANAGER_AVAILABLE and self._model_manager is not None
        
        # Inicializar com fallback TF-IDF
        self.tfidf_scorer = None
        self._init_fallback_scorer()
        
        # NÃO carregar modelo CLIP imediatamente (lazy loading)
        if not self._use_model_manager:
self.logger.info("CLIPRelevanceScorer inicializado com lazy loading tradicional")
        else:
self.logger.info("CLIPRelevanceScorer inicializado com ModelManager otimizado")
    
    def _setup_device(self, device: str) -> torch.device:
        """Configura o dispositivo para inferência."""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif torch.backends.mps.is_available():  # Apple Silicon
                return torch.device("mps")
            else:
                return torch.device("cpu")
        else:
            return torch.device(device)
    
    @property
    def clip_model_loaded(self) -> bool:
        """Verifica se o modelo CLIP está carregado"""
        if self._use_model_manager:
            model_data = self._model_manager.get_model("clip_relevance_scorer")
            return model_data is not None
        else:
            return self.model is not None and self.processor is not None
    
    def _ensure_clip_model_loaded(self):
        """Garante que o modelo CLIP está carregado (lazy loading)"""
        if self.clip_model_loaded:
            return
        
        if self._use_model_manager:
            # Usar ModelManager
self.logger.info("Carregando CLIP model via ModelManager...")
            model_data = self._model_manager.get_model("clip_relevance_scorer")
            if model_data:
                self.model = model_data['model']
                self.processor = model_data['processor']
                self.device = model_data['device']
                self.model_name = model_data['model_name']
self.logger.info("CLIP model carregado via ModelManager")
            else:
self.logger.error("Falha ao carregar CLIP model via ModelManager")
        else:
            # Carregamento tradicional
            self._init_clip_model_traditional()
    
    def _init_clip_model_traditional(self):
        """Inicializa modelo CLIP de forma tradicional (backup)"""
        try:
self.logger.info(f"Carregando modelo CLIP tradicional: {self.model_name}")
            
            # Baixar modelo
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model = CLIPModel.from_pretrained(self.model_name)
            
            # Mover para dispositivo
            self.model.to(self.device)
            self.model.eval()
            
            # Testar inferência
            with torch.no_grad():
                test_inputs = self.processor(
                    text=["test"],
                    images=[Image.new('RGB', (224, 224), color='red')],
                    return_tensors="pt",
                    padding=True
                ).to(self.device)
                
                outputs = self.model(**test_inputs)
                test_similarity = outputs.logits_per_image.item()
                
self.logger.info(f"Modelo CLIP carregado com sucesso. Teste: {test_similarity:.3f}")
            
        except Exception as e:
self.logger.error(f"Erro ao carregar modelo CLIP: {e}")
self.logger.info("Usando fallback TF-IDF para scoring")
            self.model = None
            self.processor = None
    
    def _init_fallback_scorer(self):
        """Inicializa scorer TF-IDF como fallback."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.tfidf_available = True
            
        except ImportError:
self.logger.warning("sklearn não disponível, usando similarity básica")
            self.tfidf_vectorizer = None
            self.tfidf_available = False
    
    def score_text_video_relevance(self, text: str, video_path: str) -> float:
        """
        Calcula score de relevância real entre texto e vídeo usando CLIP.
        
        Args:
            text: Texto do roteiro
            video_path: Caminho para o vídeo
            
        Returns:
            Score de relevância (0.0 a 1.0)
        """
        if not text or not video_path:
            return 0.0
        
        try:
            # Usar CLIP se disponível
            if self.model is not None:
                return self._score_with_clip(text, video_path)
            else:
                return self._score_with_fallback(text, video_path)
                
        except Exception as e:
self.logger.error(f"Erro ao calcular relevância: {e}")
            return 0.0
    
    def _score_with_clip(self, text: str, video_path: str) -> float:
        """Calcula score usando modelo CLIP com lazy loading."""
        try:
            # Garante que o modelo está carregado (lazy loading)
            self._ensure_clip_model_loaded()
            
            if not self.clip_model_loaded:
self.logger.warning("Modelo CLIP não disponível, usando fallback")
                return self._score_with_fallback(text, video_path)
            
            # Extrair frames do vídeo
            video_frames = self._extract_video_frames(video_path)
            if not video_frames:
                return 0.0
            
            # Processar texto
            text_inputs = self.processor(
                text=[text],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77  # CLIP text limit
            ).to(self.device)
            
            # Processar imagens (usar frame médio)
            representative_frame = video_frames[len(video_frames) // 2]
            image_inputs = self.processor(
                images=[representative_frame],
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Calcular similaridade
            with torch.no_grad():
                outputs = self.model(**image_inputs, **text_inputs)
                similarity = outputs.logits_per_image.item()
                
                # Normalizar para [0, 1]
                normalized_score = (similarity + 1) / 2  # CLIP outputs [-1, 1]
                return max(0.0, min(1.0, normalized_score))
                
        except Exception as e:
self.logger.error(f"Erro no scoring CLIP: {e}")
            return self._score_with_fallback(text, video_path)
    
    def _score_with_fallback(self, text: str, video_path: str) -> float:
        """Calcula score usando fallback (TF-IDF ou básico)."""
        try:
            # Extrair informações do vídeo (título, descrição se disponível)
            video_text = self._extract_video_text_info(video_path)
            
            # Usar TF-IDF se disponível
            if self.tfidf_available:
                return self._score_with_tfidf(text, video_text)
            else:
                return self._score_with_basic_similarity(text, video_text)
                
        except Exception as e:
self.logger.error(f"Erro no fallback scoring: {e}")
            return 0.0
    
    def _score_with_tfidf(self, text1: str, text2: str) -> float:
        """Calcula similaridade usando TF-IDF."""
        try:
            # Preparar textos
            texts = [text1, text2]
            
            # Ajustar corpus se necessário
            if not hasattr(self, '_tfidf_fitted') or not self._tfidf_fitted:
                # Primeiro uso ou corpus mudou
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
                self._tfidf_fitted = True
            else:
                # Corpus existente, apenas adicionar novo texto
                self.tfidf_matrix = self.tfidf_vectorizer.transform(texts)
            
            # Calcular similaridade
            similarity = cosine_similarity(self.tfidf_matrix[0:1], self.tfidf_matrix[1:2])[0][0]
            return float(max(0.0, similarity))
            
        except Exception as e:
self.logger.error(f"Erro TF-IDF: {e}")
            return self._score_with_basic_similarity(text1, text2)
    
    def _score_with_basic_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade básica baseada em palavras."""
        try:
            # Tokenizar e limpar
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            # Calcular Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
self.logger.error(f"Erro similarity básica: {e}")
            return 0.0
    
    def _extract_video_frames(self, video_path: str, max_frames: int = 5) -> List[Image.Image]:
        """Extrai frames representativos do vídeo."""
        try:
            # Verificar se é URL ou arquivo local
            if video_path.startswith(('http://', 'https://')):
                # Baixar vídeo temporário
                temp_video = self._download_video_temp(video_path)
                if temp_video:
                    video_path = temp_video
                else:
                    return []
            
            # Abrir vídeo
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []
            
            # Obter propriedades do vídeo
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            if total_frames <= 0:
                cap.release()
                return []
            
            # Calcular frames para amostragem
            frame_indices = np.linspace(0, total_frames - 1, min(max_frames, total_frames), dtype=int)
            
            frames = []
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Converter BGR para RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Redimensionar para CLIP (224x224)
                    pil_image = Image.fromarray(frame_rgb)
                    pil_image = pil_image.resize((224, 224), Image.Resampling.LANCZOS)
                    frames.append(pil_image)
            
            cap.release()
            
            # Limpar arquivo temporário se foi criado
            if video_path.startswith(self.temp_dir.name if hasattr(self, 'temp_dir') else ""):
                try:
                    os.unlink(video_path)
                except:
                    pass
            
            return frames
            
        except Exception as e:
self.logger.error(f"Erro ao extrair frames: {e}")
            return []
    
    def _download_video_temp(self, url: str) -> Optional[str]:
        """Baixa vídeo para arquivo temporário."""
        try:
            # Criar diretório temporário
            if not hasattr(self, 'temp_dir'):
                self.temp_dir = tempfile.TemporaryDirectory()
            
            # Nome do arquivo
            filename = f"temp_video_{int(datetime.now().timestamp())}.mp4"
            temp_path = os.path.join(self.temp_dir.name, filename)
            
            # Baixar
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path
            
        except Exception as e:
self.logger.error(f"Erro ao baixar vídeo: {e}")
            return None
    
    def _extract_video_text_info(self, video_path: str) -> str:
        """Extrai informações textuais do vídeo (título, descrição, etc.)."""
        # Por simplicidade, extrair do nome do arquivo
        # Em implementação real, usaria metadata do vídeo
        filename = os.path.basename(video_path)
        return filename.replace('_', ' ').replace('-', ' ')
    
    def rank_videos_by_relevance(self, text: str, video_list: List[Dict]) -> List[Dict]:
        """
        Rankeia lista de vídeos por relevância semântica usando CLIP.
        
        Args:
            text: Texto do roteiro
            video_list: Lista de vídeos com metadados
            
        Returns:
            Lista de vídeos ordenados por relevância com scores
        """
        if not text or not video_list:
            return []
        
        try:
            scored_videos = []
            
            for video in video_list:
                # Extrair caminho do vídeo
                video_path = self._get_video_path(video)
                
                if video_path:
                    # Calcular score de relevância
                    relevance_score = self.score_text_video_relevance(text, video_path)
                    
                    # Adicionar informações de score
                    video_info = video.copy()
                    video_info['relevance_score'] = relevance_score
                    video_info['scoring_method'] = 'clip' if self.model else 'fallback'
                    
                    scored_videos.append(video_info)
                else:
                    # Vídeo sem caminho válido
                    video_info = video.copy()
                    video_info['relevance_score'] = 0.0
                    video_info['scoring_method'] = 'none'
                    scored_videos.append(video_info)
            
            # Ordenar por relevância
            scored_videos.sort(key=lambda x: x['relevance_score'], reverse=True)
            
self.logger.info(f"Rankeados {len(scored_videos)} vídeos por relevância")
            return scored_videos
            
        except Exception as e:
self.logger.error(f"Erro no ranking: {e}")
            return video_list  # Retornar lista original em caso de erro
    
    def get_visual_embedding(self, video_path: str) -> Optional[np.ndarray]:
        """
        Gera embedding visual de um vídeo usando CLIP.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Array numpy com embedding visual ou None se falhar
        """
        if not video_path:
            return None
        
        # Verificar cache
        cache_key = f"visual_{hash(video_path)}"
        if cache_key in self.video_cache:
            return self.video_cache[cache_key]
        
        try:
            if self.model is not None:
                # Extrair frames
                frames = self._extract_video_frames(video_path, max_frames=1)
                if not frames:
                    return None
                
                # Processar frame
                inputs = self.processor(
                    images=frames,
                    return_tensors="pt",
                    padding=True
                ).to(self.device)
                
                # Gerar embedding
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                    embedding = image_features.cpu().numpy()[0]
                    
                    # Normalizar
                    embedding = embedding / np.linalg.norm(embedding)
                    
                    # Cache
                    self.video_cache[cache_key] = embedding
                    
                    return embedding
            else:
                return None
                
        except Exception as e:
self.logger.error(f"Erro ao gerar visual embedding: {e}")
            return None
    
    def get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Gera embedding textual usando CLIP.
        
        Args:
            text: Texto para processar
            
        Returns:
            Array numpy com embedding textual ou None se falhar
        """
        if not text:
            return None
        
        # Verificar cache
        cache_key = f"text_{hash(text)}"
        if cache_key in self.text_cache:
            return self.text_cache[cache_key]
        
        try:
            if self.model is not None:
                # Processar texto
                inputs = self.processor(
                    text=[text],
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=77
                ).to(self.device)
                
                # Gerar embedding
                with torch.no_grad():
                    text_features = self.model.get_text_features(**inputs)
                    embedding = text_features.cpu().numpy()[0]
                    
                    # Normalizar
                    embedding = embedding / np.linalg.norm(embedding)
                    
                    # Cache
                    self.text_cache[cache_key] = embedding
                    
                    return embedding
            else:
                return None
                
        except Exception as e:
self.logger.error(f"Erro ao gerar text embedding: {e}")
            return None
    
    def _get_video_path(self, video: Dict) -> Optional[str]:
        """Extrai caminho do vídeo do metadados."""
        # Tentar diferentes campos
        for field in ['url', 'file_path', 'path', 'video_path', 'source']:
            if field in video and video[field]:
                return video[field]
        return None
    
    def calculate_multicriteria_score(self, video: Dict, 
                                    semantic_score: float,
                                    quality_metrics: Dict[str, float] = None,
                                    diversity_bonus: float = 0.0) -> Dict[str, float]:
        """
        Calcula score multicritério combinando relevância semântica e qualidade.
        
        Args:
            video: Metadados do vídeo
            semantic_score: Score de relevância semântica
            quality_metrics: Métricas de qualidade do vídeo
            diversity_bonus: Bônus de diversidade
            
        Returns:
            Dicionário com scores detalhados
        """
        try:
            # Score base semântico
            semantic_weight = 0.6
            base_score = semantic_score * semantic_weight
            
            # Score de qualidade
            quality_weight = 0.3
            quality_score = 0.0
            
            if quality_metrics:
                # Combinar métricas de qualidade
                views_score = min(quality_metrics.get('views', 0) / 100000, 1.0)
                likes_score = min(quality_metrics.get('likes', 0) / 10000, 1.0)
                duration_score = self._evaluate_duration_quality(
                    quality_metrics.get('duration', 300)
                )
                
                quality_score = (views_score * 0.4 + likes_score * 0.4 + duration_score * 0.2)
            
            weighted_quality = quality_score * quality_weight
            
            # Bônus de diversidade
            diversity_weight = 0.1
            weighted_diversity = diversity_bonus * diversity_weight
            
            # Score final
            final_score = base_score + weighted_quality + weighted_diversity
            
            return {
                'semantic_score': semantic_score,
                'quality_score': quality_score,
                'diversity_bonus': diversity_bonus,
                'final_score': min(final_score, 1.0),
                'components': {
                    'semantic_component': base_score,
                    'quality_component': weighted_quality,
                    'diversity_component': weighted_diversity
                }
            }
            
        except Exception as e:
self.logger.error(f"Erro no cálculo multicritério: {e}")
            return {
                'semantic_score': semantic_score,
                'quality_score': 0.0,
                'diversity_bonus': diversity_bonus,
                'final_score': semantic_score,
                'components': {}
            }
    
    def _evaluate_duration_quality(self, duration: float) -> float:
        """Avalia qualidade baseada na duração do vídeo."""
        # Duração ideal para vídeos educativos: 30s - 10min
        if 30 <= duration <= 600:
            return 1.0
        elif 15 <= duration <= 900:
            return 0.8
        elif 5 <= duration <= 1200:
            return 0.6
        else:
            return 0.3
    
    def save_cache(self, cache_file: Optional[str] = None):
        """Salva cache para arquivo."""
        try:
            cache_file = cache_file or str(self.cache_dir / "embeddings_cache.pkl")
            
            cache_data = {
                'text_cache': self.text_cache,
                'video_cache': self.video_cache,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
self.logger.info(f"Cache salvo: {cache_file}")
            
        except Exception as e:
self.logger.error(f"Erro ao salvar cache: {e}")
    
    def load_cache(self, cache_file: Optional[str] = None):
        """Carrega cache de arquivo."""
        try:
            cache_file = cache_file or str(self.cache_dir / "embeddings_cache.pkl")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                self.text_cache = cache_data.get('text_cache', {})
                self.video_cache = cache_data.get('video_cache', {})
                
self.logger.info(f"Cache carregado: {len(self.text_cache)} textos, {len(self.video_cache)} vídeos")
            else:
self.logger.info("Arquivo de cache não encontrado, iniciando com cache vazio")
                
        except Exception as e:
self.logger.error(f"Erro ao carregar cache: {e}")
    
    def clear_cache(self):
        """Limpa caches em memória."""
        self.text_cache.clear()
        self.video_cache.clear()
self.logger.info("Cache limpo")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance."""
        return {
            'model_loaded': self.model is not None,
            'device': str(self.device),
            'text_cache_size': len(self.text_cache),
            'video_cache_size': len(self.video_cache),
            'cache_dir': str(self.cache_dir),
            'fallback_method': 'tfidf' if self.tfidf_available else 'basic'
        }
    
    def cleanup(self):
        """Limpeza de recursos com otimização ModelManager."""
        # Salvar cache antes de limpar
        self.save_cache()
        
        # Limpar caches
        self.clear_cache()
        
        # Limpar diretório temporário
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()
        
        # Cleanup com ModelManager ou tradicional
        if self._use_model_manager and self._model_manager:
            # Usar ModelManager para cleanup otimizado
            self._model_manager.unload_model("clip_relevance_scorer")
        else:
            # Cleanup tradicional
            if self.model:
                del self.model
                del self.processor
                self.model = None
                self.processor = None
        
        # Limpar memória GPU se disponível
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Garbage collection
        import gc
        gc.collect()
        
self.logger.info("CLIPRelevanceScorer finalizado com cleanup otimizado")


# Exemplo de uso
if __name__ == "__main__":
    import tempfile
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar scorer
    scorer = CLIPRelevanceScorer()
    
    # Texto de exemplo
    texto_roteiro = """
    O universo é infinito e cheio de mistérios fascinantes. 
    As estrelas brilhantes no céu nos fazem refletir sobre nossa existência. 
    A lua é um satélite natural da Terra que influencia as marés dos oceanos.
    """
    
print("=== Teste CLIP Relevance Scorer ===")
print(f"Texto: {texto_roteiro.strip()}")
print()
    
    # Estatísticas de performance
    stats = scorer.get_performance_stats()
print("Estatísticas:")
    for key, value in stats.items():
print(f"  - {key}: {value}")
print()
    
    # Teste de embedding textual
    text_embedding = scorer.get_text_embedding(texto_roteiro)
    if text_embedding is not None:
print(f"Embedding textual: shape {text_embedding.shape}")
print(f"Embedding (primeiros 5 valores): {text_embedding[:5]}")
    else:
print("Embedding textual: None (modelo não disponível)")
print()
    
    # Teste com vídeo de exemplo (se disponível)
    sample_videos = [
        {
            'id': 'video_1',
            'title': 'Explorando o Espaço - As Estrelas',
            'description': 'Um vídeo fascinante sobre as estrelas e o universo',
            'url': 'https://example.com/space_video.mp4',
            'duration': 300,
            'views': 50000,
            'likes': 2500
        },
        {
            'id': 'video_2',
            'title': 'Animais Selvagens - Leões da África',
            'description': 'Documentário sobre leões africanos',
            'url': 'https://example.com/lions_video.mp4',
            'duration': 450,
            'views': 75000,
            'likes': 4000
        }
    ]
    
print("Ranking de vídeos:")
    ranked_videos = scorer.rank_videos_by_relevance(texto_roteiro, sample_videos)
    
    for i, video in enumerate(ranked_videos, 1):
print(f"{i}. {video['title']}")
print(f"   Score: {video.get('relevance_score', 0):.3f}")
print(f"   Método: {video.get('scoring_method', 'none')}")
print()
    
    # Teste de score multicritério
    if ranked_videos:
        video = ranked_videos[0]
        multi_score = scorer.calculate_multicriteria_score(
            video,
            video['relevance_score'],
            quality_metrics={
                'views': video.get('views', 0),
                'likes': video.get('likes', 0),
                'duration': video.get('duration', 300)
            },
            diversity_bonus=0.1
        )
        
print("Score multicritério (primeiro vídeo):")
        for key, value in multi_score.items():
            if key != 'components':
print(f"  - {key}: {value}")
print()
    
    # Cleanup
    scorer.cleanup()
    
print("=== Teste concluído ===")