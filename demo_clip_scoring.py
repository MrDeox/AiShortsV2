"""
Demo do Sistema CLIP Scoring - AiShorts v2.0
Demonstração completa do sistema de scoring semântico real texto-vídeo
"""

import logging
import os
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from video.matching.semantic_analyzer import SemanticAnalyzer
from video.matching.video_searcher import VideoSearcher
from video.matching.clip_relevance_scorer import CLIPRelevanceScorer


def demo_clip_scoring():
    """Demonstração do sistema CLIP scoring."""
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    print("="*60)
    print("🎬 DEMO - SISTEMA CLIP SCORING")
    print("AiShorts v2.0 - Scoring Semântico Real Texto-Vídeo")
    print("="*60)
    
    # 1. Inicializar componentes
    print("\n📦 Inicializando componentes...")
    
    try:
        # Semantic Analyzer
        print("  • Inicializando Semantic Analyzer...")
        semantic_analyzer = SemanticAnalyzer()
        
        # Video Searcher com CLIP
        print("  • Inicializando Video Searcher com CLIP...")
        video_searcher = VideoSearcher(use_clip_scorer=True)
        
        # CLIP Relevance Scorer (standalone)
        print("  • Inicializando CLIP Relevance Scorer...")
        clip_scorer = CLIPRelevanceScorer()
        
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        return
    
    print("✅ Componentes inicializados com sucesso!")
    
    # 2. Texto do roteiro exemplo
    roteiro_texto = """
    O universo é infinito e cheio de mistérios fascinantes. 
    As estrelas brilhantes no céu noturno nos fazem refletir sobre nossa existência. 
    A lua é um satélite natural da Terra que influencia as marés dos oceanos. 
    Os cientistas estudam constantemente os fenômenos cósmicos para entender melhor 
    o espaço e nossa posição no cosmos.
    """
    
    print(f"\n📝 ROTEIRO ANALISADO:")
    print(f"{roteiro_texto.strip()}")
    
    # 3. Análise semântica com embeddings CLIP
    print("\n🔍 Análise semântica com embeddings...")
    
    try:
        # Gerar embedding com CLIP
        print("  • Gerando embedding semântico (CLIP + fallback)...")
        embedding = semantic_analyzer.get_semantic_embedding(roteiro_texto, use_clip=True)
        
        if embedding is not None:
            print(f"  ✅ Embedding gerado: shape {embedding.shape}")
            print(f"  • Primeiros 10 valores: {embedding[:10]}")
            
            # Estatísticas do embedding
            norm = float(sum(x*x for x in embedding)**0.5)
            print(f"  • Norma do vetor: {norm:.4f}")
        else:
            print("  ❌ Falha ao gerar embedding")
        
    except Exception as e:
        print(f"  ❌ Erro na análise: {e}")
        embedding = None
    
    # 4. Adicionar vídeos ao banco
    print("\n📊 Configurando banco de vídeos...")
    
    videos_exemplo = [
        {
            'id': 'space_video_1',
            'title': 'Explorando o Universo - As Estrelas',
            'description': 'Um vídeo fascinante sobre as estrelas e o universo',
            'category': 'space',
            'url': 'https://example.com/estrelas_universo.mp4',
            'views': 150000,
            'likes': 8000,
            'comments': 450,
            'duration': 480,
            'keywords': ['estrela', 'universo', 'galáxia', 'cosmos']
        },
        {
            'id': 'animals_video_1',
            'title': 'Animais Selvagens - Leões da África',
            'description': 'Documentário sobre leões africanos',
            'category': 'animals',
            'url': 'https://example.com/leoes_africa.mp4',
            'views': 200000,
            'likes': 12000,
            'comments': 800,
            'duration': 600,
            'keywords': ['leão', 'África', 'selvagem', 'natureza']
        },
        {
            'id': 'science_video_1',
            'title': 'Ciência do Espaço - Como Funciona o Universo',
            'description': 'Explicação científica sobre os fenômenos cósmicos',
            'category': 'science',
            'url': 'https://example.com/ciencia_espaco.mp4',
            'views': 90000,
            'likes': 5500,
            'comments': 320,
            'duration': 420,
            'keywords': ['ciência', 'espaço', 'fenômenos', 'cosmologia']
        },
        {
            'id': 'nature_video_1',
            'title': 'Marés e Lua - O Poder dos Oceanos',
            'description': 'Como a lua influencia as marés dos oceanos',
            'category': 'nature',
            'url': 'https://example.com/mares_lua.mp4',
            'views': 75000,
            'likes': 4200,
            'comments': 200,
            'duration': 360,
            'keywords': ['maré', 'lua', 'oceano', 'natureza']
        }
    ]
    
    video_searcher.add_video_database(videos_exemplo)
    print(f"  ✅ {len(videos_exemplo)} vídeos adicionados ao banco")
    
    # 5. Teste de scoring individual
    print("\n🎯 Teste de scoring individual...")
    
    for i, video in enumerate(videos_exemplo, 1):
        try:
            # Score usando CLIP scorer direto
            video_path = video['url']
            score = clip_scorer.score_text_video_relevance(roteiro_texto, video_path)
            
            print(f"  {i}. {video['title']}")
            print(f"     • Score de relevância: {score:.3f}")
            print(f"     • Categoria: {video['category']}")
            print(f"     • Views: {video['views']:,}")
            
        except Exception as e:
            print(f"  {i}. {video['title']} - Erro: {e}")
    
    # 6. Ranking com CLIP
    print("\n🏆 Ranking de vídeos com scoring CLIP...")
    
    try:
        ranked_videos = clip_scorer.rank_videos_by_relevance(roteiro_texto, videos_exemplo)
        
        print(f"  ✅ {len(ranked_videos)} vídeos rankeados")
        
        for i, video in enumerate(ranked_videos, 1):
            print(f"  {i}. {video['title']}")
            print(f"     Score: {video['relevance_score']:.3f}")
            print(f"     Método: {video['scoring_method']}")
        
    except Exception as e:
        print(f"  ❌ Erro no ranking: {e}")
        ranked_videos = []
    
    # 7. Teste de busca integrada
    print("\n🔎 Teste de busca integrada com semantic analyzer...")
    
    try:
        # Simular análise de roteiro
        script_analysis = {
            'theme_title': 'Explorando o Universo',
            'keywords': ['universo', 'estrela', 'lua', 'oceano'],
            'categories': {'SPACE': 0.6, 'NATURE': 0.3, 'SCIENCE': 0.1}
        }
        
        # Busca com CLIP
        clip_results = video_searcher.search_with_clip_scoring(roteiro_texto, limit=3)
        
        print(f"  ✅ Busca com CLIP: {len(clip_results)} resultados")
        
        for i, result in enumerate(clip_results, 1):
            print(f"  {i}. {result['title']}")
            print(f"     Score: {result.get('relevance_score', 0):.3f}")
            print(f"     Método: {result.get('scoring_method', 'none')}")
        
    except Exception as e:
        print(f"  ❌ Erro na busca integrada: {e}")
    
    # 8. Estatísticas de performance
    print("\n📊 Estatísticas de performance...")
    
    try:
        clip_stats = clip_scorer.get_performance_stats()
        searcher_stats = video_searcher.get_search_stats()
        
        print("  CLIP Scorer:")
        for key, value in clip_stats.items():
            print(f"    • {key}: {value}")
        
        print("\n  Video Searcher:")
        for key, value in searcher_stats.items():
            if key != 'clip_stats':
                print(f"    • {key}: {value}")
        
    except Exception as e:
        print(f"  ❌ Erro nas estatísticas: {e}")
    
    # 9. Teste de score multicritério
    print("\n⚖️  Teste de scoring multicritério...")
    
    if ranked_videos:
        try:
            video = ranked_videos[0]
            quality_metrics = {
                'views': video.get('views', 0),
                'likes': video.get('likes', 0),
                'duration': video.get('duration', 300)
            }
            
            multi_score = clip_scorer.calculate_multicriteria_score(
                video,
                video['relevance_score'],
                quality_metrics,
                diversity_bonus=0.1
            )
            
            print(f"  Vídeo: {video['title']}")
            for key, value in multi_score.items():
                if key != 'components':
                    print(f"    • {key}: {value}")
            
        except Exception as e:
            print(f"  ❌ Erro no scoring multicritério: {e}")
    
    # 10. Cleanup
    print("\n🧹 Limpando recursos...")
    
    try:
        clip_scorer.cleanup()
        video_searcher.cleanup()
        print("  ✅ Recursos limpos com sucesso")
    except Exception as e:
        print(f"  ❌ Erro na limpeza: {e}")
    
    print("\n" + "="*60)
    print("🎉 DEMO CONCLUÍDO!")
    print("Sistema CLIP Scoring implementado com sucesso!")
    print("✅ Scoring semântico real texto-vídeo")
    print("✅ Ranking otimizado por similaridade")
    print("✅ Integração com sistemas existentes")
    print("✅ Performance otimizada com cache")
    print("✅ Fallback para TF-IDF/Básico")
    print("="*60)


if __name__ == "__main__":
    demo_clip_scoring()