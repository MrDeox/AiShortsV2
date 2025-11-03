"""
Integração Simples com AiShorts v2.0 - Módulo de Matching
Arquivo para integração direta no pipeline principal
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Paths para import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from video.matching.semantic_analyzer import SemanticAnalyzer
from video.matching.video_searcher import VideoSearcher


class AiShortsMatchingIntegration:
    """
    Interface simplificada para integração com AiShorts v2.0.
    
    Funcionalidades:
    - Análise automática de roteiros
    - Busca inteligente de vídeos
    - Integração seamless com pipeline existente
    """
    
    def __init__(self, video_database: Optional[List[Dict]] = None):
        """
        Inicializa a integração.
        
        Args:
            video_database: Banco de dados de vídeos (opcional)
        """
        self.analyzer = SemanticAnalyzer()
        self.searcher = VideoSearcher(video_database or [])
        
        print("✅ AiShortsMatchingIntegration inicializada")
    
    def analyze_script(self, script, max_videos: int = 5) -> Dict[str, Any]:
        """
        Analisa um roteiro e encontra vídeos relacionados.
        
        Args:
            script: Objeto Script ou dict do AiShorts v2.0
            max_videos: Número máximo de vídeos para retornar
            
        Returns:
            Dicionário com análise completa e vídeos encontrados
        """
        try:
            # Análise semântica completa
            analysis = self.analyzer.process_script(script)
            
            # Busca de vídeos
            videos = self.searcher.search_by_script(analysis, limit=max_videos)
            
            # Filtro de qualidade
            quality_videos = self.searcher.filter_by_quality(videos)
            
            return {
                'success': True,
                'analysis': analysis,
                'videos_found': len(quality_videos),
                'videos': quality_videos,
                'summary': {
                    'primary_keywords': analysis.get('keywords', [])[:5],
                    'main_category': self._get_main_category(analysis),
                    'dominant_tone': self._get_dominant_tone(analysis.get('tone', {})),
                    'total_videos_in_db': len(self.searcher.video_database)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis': None,
                'videos_found': 0,
                'videos': []
            }
    
    def add_videos_to_database(self, videos: List[Dict]):
        """Adiciona vídeos ao banco de dados."""
        self.searcher.add_video_database(videos)
        print(f"✅ {len(videos)} vídeos adicionados ao banco de dados")
    
    def get_recommended_videos_for_theme(self, theme_category: str, keywords: List[str], 
                                       max_videos: int = 3) -> List[Dict]:
        """
        Busca vídeos recomendados para um tema específico.
        
        Args:
            theme_category: Categoria do tema (space, animals, etc.)
            keywords: Palavras-chave do tema
            max_videos: Número máximo de vídeos
            
        Returns:
            Lista de vídeos recomendados
        """
        results = self.searcher.search_by_keywords(
            keywords=keywords, 
            category=theme_category.lower(), 
            limit=max_videos
        )
        return self.searcher.filter_by_quality(results)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema."""
        return self.searcher.get_search_stats()
    
    def _get_main_category(self, analysis: Dict[str, Any]) -> str:
        """Extrai a categoria principal."""
        categories = analysis.get('categories', {})
        if not categories:
            return 'UNKNOWN'
        return max(categories.keys(), key=lambda k: categories[k])
    
    def _get_dominant_tone(self, tone_scores: Dict[str, float]) -> str:
        """Extrai o tom dominante."""
        if not tone_scores:
            return 'neutral'
        return max(tone_scores.keys(), key=lambda k: tone_scores[k])


# Funções utilitárias para uso direto
def quick_script_analysis(script) -> Dict[str, Any]:
    """
    Análise rápida de um roteiro.
    
    Args:
        script: Objeto Script
        
    Returns:
        Resultado da análise
    """
    matcher = AiShortsMatchingIntegration()
    return matcher.analyze_script(script)


def quick_video_search(theme_category: str, keywords: List[str], 
                      max_videos: int = 5) -> List[Dict]:
    """
    Busca rápida de vídeos por tema.
    
    Args:
        theme_category: Categoria do tema
        keywords: Palavras-chave
        max_videos: Número máximo de vídeos
        
    Returns:
        Lista de vídeos encontrados
    """
    matcher = AiShortsMatchingIntegration()
    return matcher.get_recommended_videos_for_theme(
        theme_category, keywords, max_videos
    )


# Exemplo de uso no pipeline AiShorts v2.0
if __name__ == "__main__":
    print("=== Integração AiShorts v2.0 - Exemplo de Uso ===")
    
    # 1. Inicializar sistema
    matcher = AiShortsMatchingIntegration()
    
    # 2. Exemplo com objeto Script (simulado)
    print("\n1. Análise de roteiro:")
    script_example = {
        'id': 'script_example',
        'sections': [
            {'type': 'hook', 'content': 'Você conhece os mistérios do espaço?'},
            {'type': 'development', 'content': 'As estrelas são sóis distantes que brilham no universo.'}
        ]
    }
    
    result = matcher.analyze_script(script_example)
    if result['success']:
        print(f"   ✅ {result['videos_found']} vídeos encontrados")
        print(f"   📝 Keywords: {result['summary']['primary_keywords']}")
        print(f"   🏷️  Categoria: {result['summary']['main_category']}")
        print(f"   🎭 Tom: {result['summary']['dominant_tone']}")
    
    # 3. Busca direta por tema
    print("\n2. Busca por tema:")
    space_videos = matcher.get_recommended_videos_for_theme(
        'space', ['estrela', 'universo', 'galáxia'], 3
    )
    print(f"   ✅ {len(space_videos)} vídeos de espaço encontrados")
    
    # 4. Estatísticas
    print("\n3. Estatísticas do sistema:")
    stats = matcher.get_system_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n✅ Sistema de integração funcionando!")
    print("   Use: from ai_shorts_matching import AiShortsMatchingIntegration")