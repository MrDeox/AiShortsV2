"""
Script para baixar e verificar modelos do spaCy.
"""

import subprocess
import sys
import os


def download_spacy_model():
    """Baixa o modelo português do spaCy."""
    try:
        print("Tentando baixar modelo português do spaCy...")
        result = subprocess.run([
            sys.executable, "-m", "spacy", "download", "pt_core_news_sm"
        ], capture_output=True, text=True, check=True)
        
        print("✓ Modelo spaCy pt_core_news_sm baixado com sucesso!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao baixar modelo spaCy: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        
        print("\nAlternativa: Execute manualmente:")
        print("python -m spacy download pt_core_news_sm")
        return False
    
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        return False


def check_spacy_model():
    """Verifica se o modelo está disponível."""
    try:
        import spacy
        nlp = spacy.load("pt_core_news_sm")
        print("✓ Modelo spaCy pt_core_news_sm está disponível!")
        return True
        
    except OSError:
        print("✗ Modelo spaCy pt_core_news_sm não encontrado.")
        return False
    
    except ImportError:
        print("✗ spaCy não está instalado.")
        return False
    
    except Exception as e:
        print(f"✗ Erro ao verificar modelo: {e}")
        return False


if __name__ == "__main__":
    print("=== Verificação e Download do Modelo spaCy ===")
    
    # Verifica se o modelo já está disponível
    if check_spacy_model():
        print("✓ Sistema pronto para uso!")
    else:
        print("\nTentando baixar o modelo...")
        if download_spacy_model():
            print("\nVerificando novamente...")
            check_spacy_model()
        else:
            print("\n⚠️  Para usar o sistema de análise semântica, é necessário:")
            print("1. Instalar o spaCy: pip install spacy")
            print("2. Baixar o modelo: python -m spacy download pt_core_news_sm")
            print("3. Ou implementar uma alternativa usando NLTK ou outra biblioteca NLP")