#!/usr/bin/env python3
"""
Teste simples do pipeline AiShorts v2.0
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "aishorts_v2/src"))

def test_basic_imports():
    """Testar importações básicas"""
    try:
        from generators.theme_generator import ThemeGenerator
        return "ThemeGenerator: OK"
    except Exception as e:
        return f"ThemeGenerator: ERROR - {e}"

def test_youtube_extractor():
    """Testar YouTube extractor"""
    try:
        from video.extractors.youtube_extractor import YouTubeExtractor
        extractor = YouTubeExtractor()
        return "YouTubeExtractor: OK"
    except Exception as e:
        return f"YouTubeExtractor: ERROR - {e}"

def test_simple_demo():
    """Demo simples"""
    print("Iniciando teste simples...")
    
    # Testar imports
    results = []
    results.append(test_basic_imports())
    results.append(test_youtube_extractor())
    
    # Salvar resultados
    with open("test_results.txt", "w") as f:
        for result in results:
            f.write(result + "\n")
            print(result)
    
    print("Teste concluído. Resultados salvos em test_results.txt")

if __name__ == "__main__":
    test_simple_demo()