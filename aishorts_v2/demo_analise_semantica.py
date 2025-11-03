"""
Integração do Sistema de Análise Semântica com AiShorts v2.0
Demo de uso completo do sistema de matching de vídeos
"""

import sys
import os
import logging
from typing import List, Dict, Any

# Adicionar paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from video.matching.semantic_analyzer import SemanticAnalyzer
from video.matching.video_searcher import VideoSearcher
from src.models.script_models import Script, ScriptSection, GeneratedTheme, ThemeCategory


class AiShortsMatchingSystem:
    """
    Sistema integrado de análise semântica e busca de vídeos para AiShorts v2.0.
    
    Combina:
    - Análise semântica de roteiros
    - Busca inteligente de vídeos
    - Integração com pipeline de geração
    """
    
    def __init__(self, video_database: List[Dict] = None):
        """
        Inicializa o sistema integrado.
        
        Args:
            video_database: Banco de dados de vídeos com metadados
        """
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.analyzer = SemanticAnalyzer()
        self.searcher = VideoSearcher(video_database)
        
        # Configurar logging
        self.logger.info("AiShortsMatchingSystem inicializado")
    
    def analyze_script_and_find_videos(self, script: Script, 
                                     max_videos: int = 5,
                                     prefer_semantic: bool = True) -> Dict[str, Any]:
        """
        Analisa um roteiro e encontra vídeos relevantes.
        
        Args:
            script: Objeto Script do AiShorts v2.0
            max_videos: Número máximo de vídeos para retornar
            prefer_semantic: Preferir busca semântica
            
        Returns:
            Dicionário com análise completa e vídeos encontrados
        """
        try:
            self.logger.info(f"Iniciando análise do roteiro: {script.id}")
            
            # 1. Análise semântica completa
            analysis = self.analyzer.process_script(script)
            self.logger.info(f"Análise semântica concluída: {len(analysis.get('keywords', []))} keywords")
            
            # 2. Busca de vídeos
            videos = self.searcher.search_by_script(
                analysis, 
                prefer_semantic=prefer_semantic,
                limit=max_videos
            )
            self.logger.info(f"Busca concluída: {len(videos)} vídeos encontrados")
            
            # 3. Filtrar por qualidade
            quality_videos = self.searcher.filter_by_quality(videos)
            
            # 4. Preparar resultado final
            result = {
                'script_analysis': analysis,
                'found_videos': quality_videos,
                'search_summary': {
                    'total_found': len(videos),
                    'quality_filtered': len(quality_videos),
                    'primary_category': self._get_primary_category(analysis),
                    'primary_keywords': analysis.get('keywords', [])[:5],
                    'dominant_tone': self._get_dominant_tone(analysis.get('tone', {})),
                    'search_methods_used': list(set(v.get('search_method', 'unknown') for v in videos))
                },
                'recommendations': self._generate_recommendations(analysis, quality_videos)
            }
            
            self.logger.info(f"Sistema completo finalizado para roteiro {script.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na análise completa: {e}")
            return {
                'script_analysis': {'error': str(e)},
                'found_videos': [],
                'search_summary': {'error': str(e)},
                'recommendations': []
            }
    
    def batch_analyze_scripts(self, scripts: List[Script]) -> List[Dict[str, Any]]:
        """
        Analisa múltiplos roteiros em lote.
        
        Args:
            scripts: Lista de objetos Script
            
        Returns:
            Lista de resultados de análise
        """
        results = []
        
        for script in scripts:
            result = self.analyze_script_and_find_videos(script)
            results.append(result)
        
        return results
    
    def update_video_database(self, new_videos: List[Dict]):
        """
        Atualiza o banco de dados de vídeos.
        
        Args:
            new_videos: Lista de novos vídeos para adicionar
        """
        self.searcher.add_video_database(new_videos)
        self.logger.info(f"Banco de dados atualizado: {len(new_videos)} novos vídeos")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema."""
        searcher_stats = self.searcher.get_search_stats()
        
        return {
            'analyzer_ready': True,
            'searcher_stats': searcher_stats,
            'total_videos': len(self.searcher.video_database),
            'cache_entries': len(self.searcher.embedding_cache)
        }
    
    def _get_primary_category(self, analysis: Dict[str, Any]) -> str:
        """Extrai a categoria principal da análise."""
        categories = analysis.get('categories', {})
        if not categories:
            return 'UNKNOWN'
        
        return max(categories.keys(), key=lambda k: categories[k])
    
    def _get_dominant_tone(self, tone_scores: Dict[str, float]) -> str:
        """Extrai o tom dominante."""
        if not tone_scores:
            return 'neutral'
        
        return max(tone_scores.keys(), key=lambda k: tone_scores[k])
    
    def _generate_recommendations(self, analysis: Dict[str, Any], 
                                videos: List[Dict]) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []
        
        # Recomendações baseadas em keywords
        keywords = analysis.get('keywords', [])
        if len(keywords) < 3:
            recommendations.append("Considere adicionar mais palavras-chave específicas ao roteiro")
        
        # Recomendações baseadas em tom
        tone = analysis.get('tone', {})
        if tone.get('neutral', 0) > 0.7:
            recommendations.append("Considere adicionar mais emoção ao roteiro para engajamento")
        
        # Recomendações baseadas em vídeos encontrados
        if len(videos) < 3:
            recommendations.append("Poucos vídeos encontrados - considere expandir o banco de dados")
        elif len(videos) > 10:
            recommendations.append("Muitos vídeos encontrados - use filtros mais específicos")
        
        # Recomendações baseadas em categoria
        primary_category = self._get_primary_category(analysis)
        if primary_category == 'UNKNOWN':
            recommendations.append("Considere tornar o conteúdo mais específico para facilitar a busca")
        
        return recommendations


def create_sample_video_database() -> List[Dict]:
    """Cria banco de dados de exemplo."""
    return [
        {
            'id': 'space_001',
            'title': 'Mistérios do Universo',
            'description': 'Descubra os segredos das estrelas, galáxias e buracos negros',
            'category': 'space',
            'keywords': ['estrela', 'galáxia', 'universo', 'buraco negro'],
            'tags': ['astronomia', 'ciência', 'espaço'],
            'views': 150000,
            'likes': 7500,
            'comments': 300,
            'duration': 480,
            'resolution': '1080p',
            'channel_subscribers': 50000,
            'url': 'https://youtube.com/watch?v=space001',
            'thumbnail': 'https://example.com/thumb_space001.jpg'
        },
        {
            'id': 'animals_001',
            'title': 'A Vida Inteligente dos Golfinhos',
            'description': 'Conheça a fascinante inteligência e comportamento dos golfinhos',
            'category': 'animals',
            'keywords': ['golfinho', 'mar', 'inteligência', 'mamífero'],
            'tags': ['natureza', 'mar', 'animais'],
            'views': 120000,
            'likes': 6000,
            'comments': 250,
            'duration': 420,
            'resolution': '1080p',
            'channel_subscribers': 30000,
            'url': 'https://youtube.com/watch?v=animals001',
            'thumbnail': 'https://example.com/thumb_animals001.jpg'
        },
        {
            'id': 'science_001',
            'title': 'Experimentos Científicos Incríveis',
            'description': 'Experimentos que demonstram princípios científicos fascinantes',
            'category': 'science',
            'keywords': ['experimento', 'ciência', 'laboratório'],
            'tags': ['educação', 'experimento'],
            'views': 200000,
            'likes': 12000,
            'comments': 500,
            'duration': 600,
            'resolution': '1080p',
            'channel_subscribers': 100000,
            'url': 'https://youtube.com/watch?v=science001',
            'thumbnail': 'https://example.com/thumb_science001.jpg'
        },
        {
            'id': 'nature_001',
            'title': 'Florestas Tropicais: O Pulmão do Mundo',
            'description': 'Explore a biodiversidade das florestas tropicais',
            'category': 'nature',
            'keywords': ['floresta', 'biodiversidade', 'tropical'],
            'tags': ['meio ambiente', 'natureza'],
            'views': 90000,
            'likes': 4500,
            'comments': 180,
            'duration': 540,
            'resolution': '720p',
            'channel_subscribers': 25000,
            'url': 'https://youtube.com/watch?v=nature001',
            'thumbnail': 'https://example.com/thumb_nature001.jpg'
        }
    ]


def create_sample_script() -> Script:
    """Cria roteiro de exemplo."""
    theme = GeneratedTheme(
        main_title="As Estrelas: Portais para o Infinito",
        category=ThemeCategory.SPACE,
        keywords=["estrela", "universo", "galáxia", "astronomia"],
        target_audience="curiosos e estudantes",
        quality_score=8.5
    )
    
    sections = [
        ScriptSection(
            type="hook",
            content="Já imaginou tocar uma estrela? Embora seja impossível, podemos explorá-las através da ciência!",
            duration_seconds=5.0,
            purpose="capturar atenção"
        ),
        ScriptSection(
            type="development",
            content="As estrelas são esferas gigantes de plasma que produzem luz através da fusão nuclear. Nossa galáxia, a Via Láctea, abriga mais de 100 bilhões de estrelas como o nosso Sol. Cada uma é um possível portal para descobertas incríveis sobre o universo.",
            duration_seconds=25.0,
            purpose="educar e informar"
        ),
        ScriptSection(
            type="conclusion",
            content="Da próxima vez que olhar para o céu estrelado, lembre-se: cada ponto de luz é um mundo de possibilidades esperando para ser explorado!",
            duration_seconds=8.0,
            purpose="finalizar com inspiração"
        )
    ]
    
    script = Script(
        id="demo_script_space",
        theme=theme,
        sections=sections,
        total_duration=38.0,
        quality_score=8.5
    )
    
    return script


def main():
    """Demonstração do sistema completo."""
    print("=== AiShorts v2.0 - Sistema de Análise Semântica e Busca de Vídeos ===")
    print()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 1. Criar sistema
    print("1. Inicializando sistema...")
    video_db = create_sample_video_database()
    matching_system = AiShortsMatchingSystem(video_database=video_db)
    
    # 2. Criar roteiro de exemplo
    print("2. Criando roteiro de exemplo...")
    script = create_sample_script()
    print(f"   - Título: {script.theme.main_title}")
    print(f"   - Categoria: {script.theme.category.value}")
    print(f"   - Duração: {script.total_duration}s")
    print()
    
    # 3. Analisar roteiro e buscar vídeos
    print("3. Analisando roteiro e buscando vídeos...")
    result = matching_system.analyze_script_and_find_videos(script, max_videos=3)
    
    # 4. Exibir resultados
    print("=== RESULTADOS DA ANÁLISE ===")
    print()
    
    print("Resumo da Análise:")
    summary = result['search_summary']
    for key, value in summary.items():
        print(f"  - {key}: {value}")
    print()
    
    print("Palavras-chave extraídas:")
    keywords = result['script_analysis'].get('keywords', [])
    for i, keyword in enumerate(keywords[:10], 1):
        print(f"  {i}. {keyword}")
    print()
    
    print("Categorias detectadas:")
    categories = result['script_analysis'].get('categories', {})
    for category, score in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {score:.3f}")
    print()
    
    print("Tom emocional:")
    tone = result['script_analysis'].get('tone', {})
    for emotion, score in tone.items():
        print(f"  - {emotion}: {score:.3f}")
    print()
    
    print("Vídeos encontrados:")
    videos = result['found_videos']
    for i, video in enumerate(videos, 1):
        print(f"  {i}. {video['title']}")
        print(f"     Categoria: {video['category']}")
        print(f"     Score: {video.get('final_score', 0):.2f}")
        print(f"     Método: {video.get('search_method', 'unknown')}")
        print()
    
    print("Recomendações:")
    recommendations = result['recommendations']
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    print()
    
    # 5. Estatísticas do sistema
    print("Estatísticas do Sistema:")
    stats = matching_system.get_system_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    print()
    
    # 6. Teste de busca direta por keywords
    print("=== TESTE DE BUSCA DIRETA ===")
    search_results = matching_system.searcher.search_by_keywords(
        ['estrela', 'universo'], 
        category='space'
    )
    print(f"Busca direta por 'estrela' e 'universo': {len(search_results)} resultados")
    for video in search_results[:2]:
        print(f"  - {video['title']} (score: {video.get('relevance_score', 0):.2f})")
    print()
    
    print("=== DEMONSTRAÇÃO CONCLUÍDA ===")


if __name__ == "__main__":
    main()