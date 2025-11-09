"""
Content matcher using CLIP model for visual similarity
Sistema de matching de conteúdo visual usando CLIP
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import cv2
from pathlib import Path
import logging
# Configurações locais enquanto não temos video_settings
SIMILARITY_MATCHING = {
    "threshold": 0.3,
    "model_name": "openai/clip-vit-base-patch32",
    "max_frames": 10
}

def get_config():
    return SIMILARITY_MATCHING

# Importar ModelManager para otimização de memória
try:
    from src.core.model_manager import get_model_manager
    MODEL_MANAGER_AVAILABLE = True
except ImportError:
    MODEL_MANAGER_AVAILABLE = False
    logging.warning("ModelManager não disponível, usando carregamento tradicional")


class ContentMatcher:
    """
    Classe para matching de conteúdo visual usando CLIP.
    
    Features:
    - Extração de features visuais usando CLIP
    - Cálculo de similaridade entre imagens/vídeos
    - Matching de conteúdo baseado em texto e imagem
    - Ranking de relevância
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o content matcher com lazy loading.
        
        Args:
            config: Configurações customizadas (opcional)
        """
        self.config = config or get_config()['similarity']
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Lazy loading - não carregar modelo imediatamente
        self.model_name = self.config.get('model_name', 'openai/clip-vit-base-patch32')
        self.model = None
        self.processor = None
        
        # ModelManager para otimização
        self._model_manager = get_model_manager() if MODEL_MANAGER_AVAILABLE else None
        self._use_model_manager = MODEL_MANAGER_AVAILABLE and self._model_manager is not None
        
        # Cache para embeddings
        self.embedding_cache = {}
        self.similarity_threshold = self.config.get('similarity_threshold', 0.8)
        self.max_matches = self.config.get('max_matches', 5)
        
        if self._use_model_manager:
self.logger.info("ContentMatcher inicializado com ModelManager otimizado")
        else:
self.logger.info("ContentMatcher inicializado com lazy loading tradicional")
    
    def _load_clip_model(self):
        """Carrega o modelo CLIP."""
        try:
self.logger.info(f"Carregando modelo CLIP: {self.model_name}")
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
self.logger.info("Modelo CLIP carregado com sucesso")
        except Exception as e:
self.logger.error(f"Erro ao carregar modelo CLIP: {e}")
            raise
    
    def extract_image_features(self, image_path: str) -> Optional[np.ndarray]:
        """
        Extrai features visuais de uma imagem.
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Array numpy com as features ou None se falhar
        """
        try:
            # Verificar cache
            if image_path in self.embedding_cache:
                return self.embedding_cache[image_path]
            
            # Carregar imagem
            image = Image.open(image_path).convert('RGB')
            
            # Processar com CLIP
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extrair features
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                # Normalizar
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Converter para numpy
            features = image_features.cpu().numpy().flatten()
            
            # Salvar no cache
            self.embedding_cache[image_path] = features
            
            return features
            
        except Exception as e:
self.logger.error(f"Erro ao extrair features de {image_path}: {e}")
            return None
    
    def extract_text_features(self, text: str) -> Optional[np.ndarray]:
        """
        Extrai features textuais de um texto.
        
        Args:
            text: Texto para processar
            
        Returns:
            Array numpy com as features ou None se falhar
        """
        try:
            # Verificar cache
            cache_key = f"text:{text}"
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
            
            # Processar texto com CLIP
            inputs = self.processor(text=[text], return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extrair features
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
                # Normalizar
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Converter para numpy
            features = text_features.cpu().numpy().flatten()
            
            # Salvar no cache
            self.embedding_cache[cache_key] = features
            
            return features
            
        except Exception as e:
self.logger.error(f"Erro ao extrair features de texto: {e}")
            return None
    
    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
        Calcula similaridade entre dois vetores de features.
        
        Args:
            features1: Primeiro vetor de features
            features2: Segundo vetor de features
            
        Returns:
            Similaridade (0-1)
        """
        try:
            # Usar similaridade cosseno
            similarity = cosine_similarity([features1], [features2])[0][0]
            return float(similarity)
        except Exception as e:
self.logger.error(f"Erro ao calcular similaridade: {e}")
            return 0.0
    
    def find_similar_images(self, query_image: str, image_database: List[str]) -> List[Dict]:
        """
        Encontra imagens similares no banco de dados.
        
        Args:
            query_image: Caminho da imagem de consulta
            image_database: Lista de caminhos de imagens para comparar
            
        Returns:
            Lista de dicionários com resultados ordenados por similaridade
        """
        # Extrair features da imagem de consulta
        query_features = self.extract_image_features(query_image)
        if query_features is None:
            return []
        
        results = []
        
        for img_path in image_database:
            # Extrair features da imagem do banco
            db_features = self.extract_image_features(img_path)
            if db_features is None:
                continue
            
            # Calcular similaridade
            similarity = self.calculate_similarity(query_features, db_features)
            
            # Adicionar à lista de resultados
            results.append({
                'image_path': img_path,
                'similarity': similarity,
                'match_quality': self._get_match_quality(similarity)
            })
        
        # Ordenar por similaridade (maior primeiro)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Aplicar threshold e limite
        filtered_results = [
            r for r in results 
            if r['similarity'] >= self.similarity_threshold
        ][:self.max_matches]
        
        return filtered_results
    
    def find_content_by_text(self, text_query: str, image_database: List[str]) -> List[Dict]:
        """
        Encontra conteúdo visual que corresponde ao texto de consulta.
        
        Args:
            text_query: Texto para buscar
            image_database: Lista de caminhos de imagens
            
        Returns:
            Lista de resultados ordenados por relevância
        """
        # Extrair features do texto
        text_features = self.extract_text_features(text_query)
        if text_features is None:
            return []
        
        results = []
        
        for img_path in image_database:
            # Extrair features da imagem
            img_features = self.extract_image_features(img_path)
            if img_features is None:
                continue
            
            # Calcular similaridade
            similarity = self.calculate_similarity(text_features, img_features)
            
            # Adicionar à lista de resultados
            results.append({
                'image_path': img_path,
                'text_query': text_query,
                'similarity': similarity,
                'match_quality': self._get_match_quality(similarity)
            })
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Aplicar filtros
        filtered_results = [
            r for r in results 
            if r['similarity'] >= self.similarity_threshold
        ][:self.max_matches]
        
        return filtered_results
    
    def batch_process_frames(self, frame_paths: List[str]) -> Dict[str, Optional[np.ndarray]]:
        """
        Processa múltiplos frames em lote.
        
        Args:
            frame_paths: Lista de caminhos dos frames
            
        Returns:
            Dicionário com path -> features
        """
        features_dict = {}
        
        for frame_path in frame_paths:
            features = self.extract_image_features(frame_path)
            features_dict[frame_path] = features
        
        return features_dict
    
    def _get_match_quality(self, similarity: float) -> str:
        """
        Determina a qualidade do match baseado na similaridade.
        
        Args:
            similarity: Valor de similaridade (0-1)
            
        Returns:
            String indicando a qualidade do match
        """
        if similarity >= 0.9:
            return "excelente"
        elif similarity >= 0.8:
            return "muito_boa"
        elif similarity >= 0.7:
            return "boa"
        elif similarity >= 0.6:
            return "razoavel"
        else:
            return "baixa"
    
    def clear_cache(self):
        """Limpa o cache de embeddings."""
        self.embedding_cache.clear()
self.logger.info("Cache de embeddings limpo")
    
    def get_cache_stats(self) -> Dict:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'cache_size': len(self.embedding_cache),
            'cached_items': list(self.embedding_cache.keys())[:10],  # Primeiros 10
        }


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar matcher
    matcher = ContentMatcher()
    
    # Teste com imagem dummy (criar uma imagem simples)
    test_image = "/tmp/test_image.jpg"
    
    try:
        # Extrair features
        features = matcher.extract_image_features(test_image)
        if features is not None:
print(f"Features extraídas com sucesso: shape {features.shape}")
        
        # Buscar conteúdo por texto
        results = matcher.find_content_by_text("uma paisagem bonita", [test_image])
print(f"Resultados da busca: {len(results)} encontrados")
        
        # Estatísticas do cache
        stats = matcher.get_cache_stats()
print(f"Estatísticas do cache: {stats}")
        
    except Exception as e:
print(f"Erro durante o teste: {e}")
