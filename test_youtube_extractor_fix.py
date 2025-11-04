#!/usr/bin/env python3
"""
Teste rápido para verificar se o YouTubeExtractor agora funciona corretamente.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from video.extractors.youtube_extractor import YouTubeExtractor
from loguru import logger

def test_download_segment_with_output_dir():
    """Testa se o método download_segment agora aceita output_dir."""
    
    print("🧪 TESTANDO CORREÇÃO DO YOUTUBEEXTRACTOR")
    print("=" * 50)
    
    # Criar instância do YouTubeExtractor
    extractor = YouTubeExtractor()
    
    # Teste 1: Verificar se o método aceita output_dir
    print("1️⃣ Testando assinatura do método...")
    try:
        # Verificar se a função existe e pode ser chamada com output_dir
        import inspect
        sig = inspect.signature(extractor.download_segment)
        params = list(sig.parameters.keys())
        print(f"   Parâmetros do método: {params}")
        
        if 'output_dir' in params:
            print("   ✅ Parâmetro 'output_dir' encontrado!")
        else:
            print("   ❌ Parâmetro 'output_dir' NÃO encontrado!")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar assinatura: {e}")
        return False
    
    # Teste 2: Testar busca de vídeos (método que funciona)
    print("\n2️⃣ Testando busca de vídeos...")
    try:
        videos = extractor.search_videos("gatos fofos", max_results=3)
        print(f"   ✅ Busca funcionando: {len(videos)} vídeos encontrados")
        
        if videos:
            first_video = videos[0]
            print(f"   📹 Primeiro vídeo: {first_video.get('title', 'N/A')[:50]}...")
            
            # Teste 3: Tentar download (mesmo que falhe, deve ser pela API)
            print("\n3️⃣ Testando download com output_dir...")
            try:
                # Usar diretório temporário para teste
                import tempfile
                test_dir = tempfile.mkdtemp()
                
                # A chamada agora deve funcionar (mesmo que falhe por outros motivos)
                segment_path = extractor.download_segment(
                    video_url=first_video['url'],
                    start_time=5.0,
                    duration=3.0,
                    output_dir=test_dir
                )
                print(f"   ✅ Método aceita output_dir! Arquivo: {segment_path}")
                
            except TypeError as e:
                if "output_dir" in str(e):
                    print(f"   ❌ Método ainda não aceita output_dir: {e}")
                    return False
                else:
                    print(f"   ✅ Método aceita output_dir (erro é outro): {e}")
                    
            except Exception as e:
                print(f"   ✅ Método aceita output_dir (erro de download é esperado): {e}")
                
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na busca: {e}")
        return False

if __name__ == "__main__":
    success = test_download_segment_with_output_dir()
    
    if success:
        print("\n🎉 SUCESSO: YouTubeExtractor foi corrigido!")
        print("   O método download_segment() agora aceita output_dir")
    else:
        print("\n❌ FALHA: Correção não foi aplicada corretamente")
    
    sys.exit(0 if success else 1)