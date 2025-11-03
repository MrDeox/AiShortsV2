"""
Exemplo de integração do sistema de matching roteiro-vídeo com AI Shorts.
Demonstra como usar o sistema em um fluxo completo de criação de conteúdo.
"""

import sys
import os

# Adiciona diretório ao path
sys.path.insert(0, '/workspace/aishorts_v2/src')

# Importa o sistema de matching
from video.matching.semantic_analyzer import SemanticAnalyzer
from video.matching.video_searcher import VideoSearcher


def exemplo_completo_ai_shorts():
    """
    Exemplo completo de uso do sistema de matching em um pipeline de criação.
    """
    print("🎬 EXEMPLO DE INTEGRAÇÃO COM AI SHORTS")
    print("=" * 50)
    
    # Inicialização
    analyzer = SemanticAnalyzer()
    searcher = VideoSearcher()
    
    # Simula um roteiro gerado pelo AI Shorts
    roteiro_gerado = """
    HOOK: Você sabia que os golfinhos são capazes de reconhecer-se no espelho?
    
    DEVELOPMENT: Estes incríveis mamíferos marinhos possuem uma inteligência 
    extraordinária que nos surpreende a cada nova descoberta. No oceano Pacífico, 
    pesquisadores observaram golfinhos desenvolvendo técnicas únicas de caça, 
    usando conchas como ferramentas para capturar peixes.
    
    Os golfinhos também demonstram comportamentos sociais complexos, criando 
    laços que duram décadas. Eles se comunicam através de cliques, assobios 
    e linguagem corporal, construindo uma rica cultura marinha.
    
    CONCLUSION: A próxima vez que você ver um golfinho, lembre-se de que está 
    diante de uma das mentes mais brilhantes dos oceanos. Estos seres extraordinários 
    nos ensinam sobre inteligência, comunidad e a importância de proteger nossos mares.
    """
    
    print("📝 ETAPA 1: Análise do Roteiro Gerado")
    print("-" * 40)
    
    # Análise semântica completa
    analise = analyzer.analyze_script(roteiro_gerado)
    
    print(f"✅ Categoria identificada: {analise['category']}")
    print(f"✅ Confiança da categorização: {analise['category_confidence']:.2f}")
    print(f"✅ Tom emocional: Positivo={analise['tone']['positive']:.2f}, "
          f"Neutro={analise['tone']['neutral']:.2f}")
    print(f"✅ Top palavras-chave: {analise['keywords'][:8]}")
    
    print("\n🎯 ETAPA 2: Busca de Vídeos Complementares")
    print("-" * 40)
    
    # Busca o melhor vídeo para o roteiro
    if analise['semantic_vector'] is not None:
        melhor_video = searcher.get_best_match(
            analise['keywords'][:5],
            analise['semantic_vector'],
            analise['category']
        )
        
        if melhor_video:
            print(f"🎬 Vídeo recomendado: '{melhor_video.title}'")
            print(f"📺 Canal: {melhor_video.channel}")
            print(f"⏱️ Duração: {melhor_video.duration // 60}:{melhor_video.duration % 60:02d}")
            print(f"👀 Visualizações: {melhor_video.views:,}")
            print(f"👍 Engajamento: {melhor_video.likes / melhor_video.views * 100:.1f}%")
            print(f"⭐ Score de qualidade: {melhor_video.quality_score:.2f}")
            
            # Mostra sugestões de como usar
            print(f"\n💡 Sugestões de uso:")
            print(f"   - Use como referência visual para imagens de golfinhos")
            print(f"   - Extraia clipes curtos para o HOOK e DEVELOPMENT")
            print(f"   - Use como B-roll footage para Transições")
        else:
            print("❌ Nenhum vídeo adequado encontrado")
    
    print("\n🔍 ETAPA 3: Análise de Múltiplas Opções")
    print("-" * 40)
    
    # Busca múltiplos vídeos
    opcoes = searcher.search_combined(
        analise['keywords'][:5],
        analise['semantic_vector'],
        analise['category'],
        max_results=3
    )
    
    print(f"✅ Encontradas {len(opcoes)} opções de vídeo:")
    for i, video in enumerate(opcoes, 1):
        print(f"\n{i}. {video.title}")
        print(f"   📺 {video.channel} | ⭐ {video.quality_score:.2f}")
        print(f"   🎯 Categoria: {video.category} | 👀 {video.views:,} views")
    
    print("\n📊 ETAPA 4: Relatório de Análise")
    print("-" * 40)
    
    # Gera relatório completo
    print("📈 MÉTRICAS DO ROTEIRO:")
    print(f"   • Complexidade semântica: {len(analise['keywords'])} palavras-chave")
    print(f"   • Tom emocional: {'Positivo' if analise['tone']['positive'] > 0.6 else 'Neutro'}")
    print(f"   • Foco temático: {analise['category']} (confiança: {analise['category_confidence']:.2f})")
    
    print("\n🎬 MÉTRICAS DOS VÍDEOS ENCONTRADOS:")
    if opcoes:
        avg_quality = sum(v.quality_score for v in opcoes) / len(opcoes)
        total_views = sum(v.views for v in opcoes)
        print(f"   • Qualidade média: {avg_quality:.2f}/1.0")
        print(f"   • Visualizações totais: {total_views:,}")
        print(f"   • Melhor canal: {opcoes[0].channel}")
    
    print("\n🚀 ETAPA 5: Recomendações para Produção")
    print("-" * 40)
    
    print("💡 RECOMENDAÇÕES ESTRATÉGICAS:")
    
    if analise['category'] == 'ANIMALS':
        print("   • Foque em imagens de alta qualidade dos animais")
        print("   • Use transições suaves entre cenas")
        print("   • Adicione fatos interessantes em overlays")
    
    if analise['tone']['positive'] > 0.7:
        print("   • Tom positivo detectado - use música energética")
        print("   • Cores vibrantes nas sobreposições de texto")
    
    if opcoes and opcoes[0].duration > 300:
        print("   • Vídeo de referência longo - foque nos melhores momentos")
        print("   • Extraia clips de 15-30 segundos para melhor impacto")
    
    print(f"\n   • Use {analise['keywords'][0]} como palavra-chave principal")
    print(f"   • Otimize para categoria: {analise['category']}")
    
    return analise, opcoes


def exemplo_otimizacao_seo():
    """
    Exemplo de como usar o sistema para otimização SEO.
    """
    print("\n\n🔍 EXEMPLO: OTIMIZAÇÃO SEO")
    print("=" * 50)
    
    analyzer = SemanticAnalyzer()
    
    # Texto com potencial SEO baixo
    texto_original = "Este vídeo fala sobre coisas legais."
    
    # Analisa o texto original
    analise_original = analyzer.analyze_script(texto_original)
    print(f"📝 Texto original: '{texto_original}'")
    print(f"🔑 Keywords extraídas: {analise_original['keywords']}")
    
    # Texto otimizado
    texto_otimizado = """
    Descubra os golfinhos, estes incríveis mamíferos marinhos que habitam 
    os oceanos do mundo. Saiba tudo sobre a inteligência excepcional dos 
    delfins e como eles se comunicam através de cliques e assobios. 
    Este vídeo educativo mostra comportamentos fascinantes dos golfinhos 
    em seu habitat natural, incluindo técnicas de caça e interações sociais.
    """
    
    # Analisa o texto otimizado
    analise_otimizada = analyzer.analyze_script(texto_otimizado)
    
    print(f"\n✅ Texto otimizado:")
    print(f"🔑 Keywords melhoradas: {analise_otimizada['keywords'][:8]}")
    print(f"📊 Categoria: {analise_otimizada['category']}")
    print(f"🎯 Tom: Positivo={analise_otimizada['tone']['positive']:.2f}")
    
    # Compara melhoras
    print(f"\n📈 MELHORIAS CONSEGUIDAS:")
    print(f"   • Mais palavras-chave relevantes: {len(analise_otimizada['keywords'])} vs {len(analise_original['keywords'])}")
    print(f"   • Categoria mais específica: {analise_otimizada['category']}")
    print(f"   • Tom mais positivo: {analise_otimizada['tone']['positive']:.2f}")
    
    return analise_otimizada


def exemplo_analise_competitiva():
    """
    Exemplo de análise competitiva de conteúdo.
    """
    print("\n\n🏆 EXEMPLO: ANÁLISE COMPETITIVA")
    print("=" * 50)
    
    analyzer = SemanticAnalyzer()
    searcher = VideoSearcher()
    
    # Simula análise de concorrentes
    videos_competidores = [
        "Os segredos dos golfinhos que você não sabia",
        "Inteligência animal: delfins são mais espertos que cães",
        "Golfinhos do mundo: aventura nos oceanos"
    ]
    
    print("🔍 Analisando vídeos de concorrentes...")
    
    for i, titulo in enumerate(videos_competidores, 1):
        analise = analyzer.analyze_script(titulo)
        print(f"\n{i}. {titulo}")
        print(f"   🎯 Categoria: {analise['category']}")
        print(f"   🔑 Keywords: {analise['keywords'][:5]}")
        
        # Simula busca de vídeo similar
        if analise['semantic_vector'] is not None:
            similar = searcher.get_best_match(
                analise['keywords'][:3],
                analise['semantic_vector'],
                analise['category']
            )
            if similar:
                print(f"   📺 Vídeo referência: {similar.title}")
    
    print(f"\n💡 ESTRATÉGIAS DE DIFERENCIAÇÃO:")
    print(f"   • Foque em um ângulo único (ex: conservation)")
    print(f"   • Use palavras-chave menos competitivas")
    print(f"   • Adicione dados científicos exclusivos")
    print(f"   • Crie tom mais educativo/científico")


if __name__ == "__main__":
    try:
        # Exemplo principal
        analise, opcoes = exemplo_completo_ai_shorts()
        
        # Exemplos adicionais
        exemplo_otimizacao_seo()
        exemplo_analise_competitiva()
        
        print("\n\n🎉 EXEMPLO CONCLUÍDO COM SUCESSO!")
        print("=" * 50)
        print("O sistema de matching roteiro-vídeo está pronto para integração")
        print("com o pipeline completo de criação de conteúdo do AI Shorts!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()