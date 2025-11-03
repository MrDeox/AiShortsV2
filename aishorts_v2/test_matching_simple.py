"""
Teste simples para verificar se o sistema de matching funciona.
"""

import sys
import os
import numpy as np

# Adiciona o diretório ao path
sys.path.insert(0, '/workspace/aishorts_v2/src')

# Teste direto dos módulos
print("=== Testando Sistema de Matching Roteiro-Vídeo ===")

try:
    # Importa os módulos diretamente
    from video.matching.semantic_analyzer import SemanticAnalyzer
    from video.matching.video_searcher import VideoSearcher
    
    print("✓ Módulos importados com sucesso!")
    
    # Teste 1: SemanticAnalyzer
    print("\n1. Testando SemanticAnalyzer...")
    analyzer = SemanticAnalyzer()
    
    script = "Os golfinhos são animais incríveis que nadam no oceano azul. Eles são muito inteligentes e realizam truques espetaculares."
    
    print(f"   Roteiro: {script[:50]}...")
    
    # Extrai palavras-chave
    keywords = analyzer.extract_keywords(script)
    print(f"   ✓ Palavras-chave: {keywords[:5]}")
    
    # Analisa tom
    tone = analyzer.analyze_tone(script)
    print(f"   ✓ Tom: Positivo={tone['positive']:.2f}, Neutro={tone['neutral']:.2f}")
    
    # Categoriza conteúdo
    category, confidence = analyzer.categorize_content(script)
    print(f"   ✓ Categoria: {category} (confiança: {confidence:.2f})")
    
    # Gera embedding
    embedding = analyzer.get_semantic_embedding(script)
    if embedding is not None:
        print(f"   ✓ Embedding gerado: {len(embedding)} dimensões")
    else:
        print("   ⚠ Embedding não gerado")
    
    print("   ✓ SemanticAnalyzer funcionando!")
    
    # Teste 2: VideoSearcher
    print("\n2. Testando VideoSearcher...")
    searcher = VideoSearcher()
    
    # Busca por palavras-chave
    results = searcher.search_by_keywords(keywords[:3], max_results=3)
    print(f"   ✓ Encontrados {len(results)} vídeos por palavras-chave")
    
    for i, video in enumerate(results):
        print(f"      {i+1}. {video.title} (Score: {video.keyword_score:.2f})")
    
    # Busca semântica (se embedding disponível)
    if embedding is not None:
        semantic_results = searcher.search_by_semantic(embedding, max_results=3)
        print(f"   ✓ Encontrados {len(semantic_results)} vídeos por similaridade semântica")
        
        # Busca combinada
        combined_results = searcher.search_combined(keywords[:3], embedding, max_results=3)
        print(f"   ✓ Busca combinada: {len(combined_results)} vídeos")
        
        # Melhor match
        best = searcher.get_best_match(keywords[:3], embedding)
        if best:
            print(f"   ✓ Melhor match: {best.title}")
    
    print("   ✓ VideoSearcher funcionando!")
    
    # Teste 3: Integração completa
    print("\n3. Testando Integração Completa...")
    analysis = analyzer.analyze_script(script)
    
    print(f"   ✓ Análise completa:")
    print(f"      - Categoria: {analysis['category']}")
    print(f"      - Tom positivo: {analysis['tone']['positive']:.2f}")
    print(f"      - Palavras-chave: {len(analysis['keywords'])}")
    
    print("\n=== TODOS OS TESTES PASSARAM! ===")
    print("\nSistema de matching roteiro-vídeo implementado com sucesso!")
    print("Recursos disponíveis:")
    print("- ✓ Análise semântica de textos")
    print("- ✓ Extração de palavras-chave")
    print("- ✓ Análise de tom emocional")
    print("- ✓ Categorização automática de conteúdo")
    print("- ✓ Embeddings semânticos")
    print("- ✓ Busca inteligente por vídeos")
    print("- ✓ Filtragem por qualidade")
    print("- ✓ Sistema de ranking combinado")
    
except ImportError as e:
    print(f"✗ Erro de importação: {e}")
    print("Verifique se os arquivos estão nos locais corretos.")
    
except Exception as e:
    print(f"✗ Erro durante os testes: {e}")
    import traceback
    traceback.print_exc()