"""
Models Import Hub - AiShorts v2.0
Ponto centralizado para imports de modelos consolidados.

Este arquivo substitui os múltiplos arquivos de models e fornece
uma interface unificada para toda a aplicação.
"""

# Importar todos os modelos unificados
from .unified_models import (
    # Enums
    ThemeCategory,
    
    # Classes de modelo
    GeneratedTheme,
    ScriptSection, 
    GeneratedScript,
    ScriptGenerationResult,
    
    # Funções de utilidade
    migrate_from_script_models,
    migrate_from_script_generator,
    validate_model_consistency
)

# Re-exportar tudo que era disponibilizado nos arquivos antigos
__all__ = [
    # Enums (compatível com prompt_engineering)
    'ThemeCategory',
    
    # Models (compatível com script_models e script_generator)
    'GeneratedTheme',
    'ScriptSection',
    'GeneratedScript', 
    'ScriptGenerationResult',
    
    # Utilidades
    'migrate_from_script_models',
    'migrate_from_script_generator',
    'validate_model_consistency'
]

# Alias para compatibilidade total
# Estes permitem que o código existente continue funcionando sem mudanças

# Compatibilidade com script_models.py
Script = GeneratedScript  # Alias para compatibilidade

# Compatibilidade com diferentes convenções de nome
def get_script_section_by_type(script: GeneratedScript, section_type: str) -> ScriptSection:
    """Função de compatibilidade para buscar seção por tipo."""
    return script.get_section_by_type(section_type)

def get_script_full_text(script: GeneratedScript) -> str:
    """Função de compatibilidade para obter texto completo."""
    return script.get_script_text()

# Metadados da migração
MIGRATION_INFO = {
    "migrated_at": "2025-01-08",
    "source_files": ["script_models.py", "script_generator.py"],
    "target_file": "unified_models.py", 
    "compatibility_level": "full",
    "breaking_changes": False,
    "deprecated_files": [
        "src/models/script_models.py",
        "src/generators/script_generator.py (model definitions only)"
    ]
}

def get_migration_info() -> dict:
    """Retorna informações sobre a migração realizada."""
    return MIGRATION_INFO.copy()