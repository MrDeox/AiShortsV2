#!/usr/bin/env python3
"""
Verificação simples da correção do YouTubeExtractor.
"""

import sys
from pathlib import Path

def check_youtube_extractor_fix():
    """Verifica se a correção foi aplicada."""
    
    print("🔍 VERIFICANDO CORREÇÃO DO YOUTUBEEXTRACTOR")
    print("=" * 50)
    
    # Ler o arquivo do YouTubeExtractor
    file_path = Path(__file__).parent / "src" / "video" / "extractors" / "youtube_extractor.py"
    
    if not file_path.exists():
        print("❌ Arquivo não encontrado!")
        return False
    
    content = file_path.read_text()
    
    # Verificar se a correção foi aplicada
    checks = [
        ("def download_segment(self, video_url: str, start_time: float, duration: float, output_dir: Optional[str] = None)", 
         "Método aceita output_dir como parâmetro"),
        ("output_dir_path = Path(output_dir) if output_dir else self.output_dir", 
         "Lógica de output_dir implementada"),
        ("str(output_dir_path / f\"{video_id}_segment.*\")", 
         "Busca de arquivos usa output_dir correto")
    ]
    
    all_passed = True
    
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_passed = False
    
    # Verificar também se os scripts ainda chamam o método incorretamente
    print("\n🔍 VERIFICANDO SCRIPTS DE CHAMADA")
    
    scripts_to_check = [
        "scripts/demo_end_to_end_real.py",
        "scripts/demo_integracao.py"
    ]
    
    for script_path in scripts_to_check:
        full_path = Path(__file__).parent / script_path
        if full_path.exists():
            script_content = full_path.read_text()
            if "output_dir=str(self.output_dir" in script_content:
                print(f"✅ {script_path}: Chamada está correta")
            else:
                print(f"⚠️  {script_path}: Pode precisar de verificação")
    
    return all_passed

if __name__ == "__main__":
    success = check_youtube_extractor_fix()
    
    if success:
        print("\n🎉 CORREÇÃO APLICADA COM SUCESSO!")
        print("   O YouTubeExtractor.download_segment() agora aceita output_dir")
        print("   Os scripts devem funcionar corretamente agora")
    else:
        print("\n❌ CORREÇÃO INCOMPLETA!")
        print("   Alguns elementos não foram encontrados")
    
    sys.exit(0 if success else 1)