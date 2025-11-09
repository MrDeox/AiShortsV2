#!/usr/bin/env python3
"""
Script para limpar emojis e logs excessivos dos módulos core.
Mantém logs técnicos essenciais apenas.
"""

import re
import sys
from pathlib import Path

# Mapeamento de substituições de logs com emojis para logs técnicos
LOG_REPLACEMENTS = [
    # OpenRouter
    (r'🧠 OpenRouterClient inicializado', 'OpenRouterClient initialized'),
    (r'📊 Limites detectados via API', 'Rate limits detected via API'),
    (r'📋 Fonte: openrouter_api', 'Source: openrouter_api'),
    (r'✅ Max tokens automático ativado', 'Auto max tokens enabled'),
    (r'🔄 Usando modelo via API', 'Using model via API'),
    (r'🚨 Erro da API OpenRouter', 'OpenRouter API error'),
    
    # Health Checker
    (r'🏥 HEALTH CHECKER', 'HEALTH CHECKER'),
    (r'🚨 HEALTH ALERT', 'HEALTH ALERT'),
    (r'⚠️ HEALTH WARNING', 'HEALTH WARNING'),
    
    # Content Cache
    (r'💾 Cache', 'Cache'),
    (r'✅ Cache hit', 'Cache hit'),
    (r'❌ Cache miss', 'Cache miss'),
    
    # Graceful Degradation
    (r'🛡️ Graceful degradation', 'Graceful degradation'),
    (r'🔄 Retry', 'Retry'),
    (r'⚡ Fallback', 'Fallback'),
    
    # Geradores
    (r'🎬 Gerando tema', 'Generating theme'),
    (r'📝 Gerando script', 'Generating script'),
    (r'🔊 Gerando áudio', 'Generating audio'),
    (r'🎥 Processando vídeo', 'Processing video'),
    
    # Sistema
    (r'🔧 Sistema', 'System'),
    (r'📊 Estatísticas', 'Statistics'),
    (r'⚙️ Configurações', 'Configuration'),
]

def clean_file(file_path: Path) -> int:
    """Limpa emojis de um arquivo e retorna número de substituições."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar substituições
        for pattern, replacement in LOG_REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # Remover emojis isolados
        # Lista de emojis a remover
        emoji_pattern = re.compile(
            '['
            '\U0001F600-\U0001F64F'  # Emoticons
            '\U0001F300-\U0001F5FF'  # Símbolos & pictogramas
            '\U0001F680-\U0001F6FF'  # Transporte & símbolos de mapa
            '\U0001F1E0-\U0001F1FF'  # Bandeiras
            '\U00002702-\U000027B0'  # Dings
            '\U000024C2-\U0001F251'  # Símbolos diversos
            ']+',
            flags=re.UNICODE
        )
        
        # Remover apenas emojis em logs (não em strings)
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Se for uma linha de log
            if 'logger.' in line or 'print(' in line:
                # Remover emojis mas manter o texto
                cleaned_line = emoji_pattern.sub('', line).strip()
                # Corrigir aspas duplas
                cleaned_line = cleaned_line.replace('""', '"')
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Salvar se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return 1
        return 0
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return 0

def main():
    """Função principal."""
    print("🧹 Limpando emojis dos logs em módulos core...")
    
    # Diretórios para limpar
    core_dirs = [
        'src/core',
        'src/config',
        'src/models',
        'src/pipeline',
        'src/generators',
        'src/tts',
        'src/video',
        'src/utils',
        'src/validators'
    ]
    
    total_files = 0
    modified_files = 0
    
    for dir_name in core_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue
        
        print(f"\n📁 Processando {dir_name}/")
        
        for py_file in dir_path.rglob('*.py'):
            total_files += 1
            if clean_file(py_file):
                modified_files += 1
                print(f"  ✅ {py_file}")
    
    print(f"\n📊 Resumo:")
    print(f"   Total de arquivos: {total_files}")
    print(f"   Arquivos modificados: {modified_files}")
    print(f"   Arquivos sem mudanças: {total_files - modified_files}")
    
    if modified_files > 0:
        print(f"\n✨ Limpeza concluída! {modified_files} arquivos atualizados.")
    else:
        print(f"\n✨ Nenhum arquivo precisou de limpeza.")

if __name__ == "__main__":
    main()