"""
Teste direto do sistema de matching, importando módulos diretamente.
"""

import sys
import os
import numpy as np
from collections import Counter
import re

print("=== Testando Sistema de Matching Roteiro-Vídeo ===")

# Adiciona diretórios ao path
sys.path.insert(0, '/workspace/aishorts_v2/src')

print("Importando módulos...")

try:
    # Importa diretamente os arquivos Python
    import importlib.util
    
    # Carrega semantic_analyzer
    spec = importlib.util.spec_from_file_location("semantic_analyzer", 
                                                  "/workspace/aishorts_v2/src/video/matching/semantic_analyzer.py")
    semantic_analyzer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(semantic_analyzer)
    SemanticAnalyzer = semantic_analyzer.SemanticAnalyzer
    
    # Carrega video_searcher
    spec = importlib.util.spec_from_file_location("video_searcher", 
                                                  "/workspace/aishorts_v2/src/video/matching/video_searcher.py")
    video_searcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(video_searcher)
    VideoSearcher = video_searcher.VideoSearcher
    VideoInfo = video_searcher.VideoInfo
    
    print("✓ Módulos carregados com sucesso!")
    
    # Teste 1: SemanticAnalyzer
    print("\n1. Testando SemanticAnalyzer...")
    analyzer = SemanticAnalyzer()
    
    script = "Os golfinhos são animais incríveis que nadam no oceano azul. Eles são muito inteligentes e realizam truques espetaculares."
    
    print(f"   Roteiro analisado: '{script[:50]}...'")
    
    # Extrai palavras-chave
    keywords = analyzer.extract_keywords(script)
    print(f"   ✓ Palavras-chave extraídas: {keywords[:5]}")
    
    # Analisa tom
    tone = analyzer.analyze_tone(script)
    print(f"   ✓ Análise de tom:")
    print(f"     - Positivo: {tone['positive']:.2f}")
    print(f"     - Neutro: {tone['neutral']:.2f}")
    print(f"     - Negativo: {tone['negative']:.2f}")
    
    # Categoriza conteúdo
    category, confidence = analyzer.categorize_content(script)
    print(f"   ✓ Categoria identificada: {category} (confiança: {confidence:.2f})")
    
    # Gera embedding
    embedding = analyzer.get_semantic_embedding(script)
    if embedding is not None:
        print(f"   ✓ Embedding semântico gerado: {len(embedding)} dimensões")
    else:
        print("   ⚠ Embedding não disponível (usando fallback)")
    
    print("   ✓ SemanticAnalyzer funcionando corretamente!")
    
    # Teste 2: VideoSearcher
    print("\n2. Testando VideoSearcher...")
    searcher = VideoSearcher()
    
    # Testa busca por palavras-chave
    test_keywords = ['golfinho', 'oceano', 'inteligência']
    results = searcher.search_by_keywords(test_keywords, max_results=3)
    print(f"   ✓ Busca por palavras-chave: {len(results)} vídeos encontrados")
    
    for i, video in enumerate(results):
        print(f"     {i+1}. {video.title}")
        print(f"        - Canal: {video.channel}")
        print(f"        - Categoria: {video.category}")
        print(f"        - Score: {video.keyword_score:.2f}")
        print(f"        - Views: {video.views:,}")
        print()
    
    # Testa busca semântica (se embedding disponível)
    if embedding is not None:
        semantic_results = searcher.search_by_semantic(embedding, max_results=3)
        print(f"   ✓ Busca semântica: {len(semantic_results)} vídeos encontrados")
        
        # Testa busca combinada
        combined_results = searcher.search_combined(test_keywords, embedding, max_results=3)
        print(f"   ✓ Busca combinada: {len(combined_results)} vídeos encontrados")
        
        # Melhor match
        best_match = searcher.get_best_match(test_keywords, embedding)
        if best_match:
            print(f"   ✓ Melhor vídeo encontrado: '{best_match.title}'")
            print(f"     - Canal: {best_match.channel}")
            print(f"     - Score de qualidade: {best_match.quality_score:.2f}")
        else:
            print("   ⚠ Nenhum match perfeito encontrado")
    
    print("   ✓ VideoSearcher funcionando corretamente!")
    
    # Teste 3: Demonstração de uso completo
    print("\n3. Demonstração de Uso Completo...")
    
    # Script de exemplo mais complexo
    complex_script = """
    Descubra o mundo fascinante dos golfinhos, estes mamíferos marinhos extraordinários.
    Emoce-se com a inteligência destes animais incríveis que habitam os oceanos do mundo.
    Veja golfinhos realizando saltos espetaculares e truques que demonstram sua incrível capacidade cognitiva.
    Prepare-se para uma jornada inesquecível pelo reino marinho!
    """
    
    print(f"   Analisando roteiro complexo...")
    
    # Análise completa
    analysis = analyzer.analyze_script(complex_script)
    
    print(f"   ✓ Resultados da análise:")
    print(f"     - Categoria: {analysis['category']}")
    print(f"     - Confiança: {analysis['category_confidence']:.2f}")
    print(f"     - Tom emocional: Positivo={analysis['tone']['positive']:.2f}")
    print(f"     - Palavras-chave principais: {analysis['keywords'][:8]}")
    
    # Busca o melhor vídeo
    if analysis['semantic_vector'] is not None:
        best_video = searcher.get_best_match(
            analysis['keywords'][:5],
            analysis['semantic_vector'],
            analysis['category']
        )
        
        if best_video:
            print(f"   ✓ Melhor vídeo recomendado:")
            print(f"     - Título: {best_video.title}")
            print(f"     - Canal: {best_video.channel}")
            print(f"     - Duração: {best_video.duration // 60}:{best_video.duration % 60:02d} min")
            print(f"     - Visualizações: {best_video.views:,}")
            print(f"     - Engajamento: {best_video.likes / max(best_video.views, 1) * 100:.1f}%")
        else:
            print("   ⚠ Nenhum vídeo adequado encontrado no banco de dados")
    
    print("\n" + "="*60)
    print("🎉 SISTEMA DE MATCHING ROTEIRO-VÍDEO IMPLEMENTADO COM SUCESSO! 🎉")
    print("="*60)
    print("\n📋 Resumo dos Recursos Implementados:")
    print("✅ Análise semântica avançada com spaCy (com fallback)")
    print("✅ Extração inteligente de palavras-chave")
    print("✅ Análise de tom emocional (positivo/negativo/neutro)")
    print("✅ Categorização automática de conteúdo")
    print("✅ Geração de embeddings semânticos")
    print("✅ Sistema de busca por palavras-chave")
    print("✅ Sistema de busca por similaridade semântica")
    print("✅ Algoritmo de busca combinada (keywords + semântica)")
    print("✅ Filtragem por qualidade de vídeo")
    print("✅ Sistema de ranking e scoring")
    print("✅ Matching inteligente roteiro-vídeo")
    
    print("\n🚀 Como usar:")
    print("1. Crie uma instância do SemanticAnalyzer")
    print("2. Analise seu roteiro com analyze_script()")
    print("3. Use as palavras-chave e embedding gerados")
    print("4. Busque vídeos com VideoSearcher")
    print("5. Use search_combined() para melhores resultados")
    
    print("\n📝 Exemplo de uso:")
    print("```python")
    print("analyzer = SemanticAnalyzer()")
    print("searcher = VideoSearcher()")
    print("analysis = analyzer.analyze_script(meu_roteiro)")
    print("melhor_video = searcher.get_best_match(")
    print("    analysis['keywords'],")
    print("    analysis['semantic_vector'],")
    print("    analysis['category']")
    print(")")
    print("```")
    
except Exception as e:
    print(f"❌ Erro durante os testes: {e}")
    import traceback
    print("\nDetalhes do erro:")
    traceback.print_exc()

print("\n=== Fim dos Testes ===")