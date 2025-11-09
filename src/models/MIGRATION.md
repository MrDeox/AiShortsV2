# Migração de Modelos - AiShorts v2.0

## Resumo da Consolidação

Foi realizada uma migração para consolidar os modelos de dados duplicados que existiam em múltiplos arquivos:

### Arquivos Antigos (Deprecados)
- `src/models/script_models.py` - Modelos alternativos para compatibilidade TTS
- `src/generators/script_generator.py` - Definições de modelos (linhas 23-125)
- `src/generators/theme_generator.py` - Definições de modelos (linhas 30-47)

### Novo Arquivo Unificado
- `src/models/unified_models.py` - Contém todos os modelos consolidados

### Arquivo de Imports Central
- `src/models/__init__.py` - Ponto centralizado para imports de modelos

## Modelos Unificados

### 1. GeneratedTheme
```python
@dataclass
class GeneratedTheme:
    content: str                    # Nome principal do conteúdo
    category: ThemeCategory
    quality_score: float = 0.0
    response_time: float = 0.0
    timestamp: Optional[datetime] = None
    usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    # Campos adicionais para compatibilidade
    keywords: List[str] = field(default_factory=list)
    target_audience: str = "general"
    
    @property
    def main_title(self) -> str:    # Alias para compatibilidade TTS
        return self.content
```

### 2. ScriptSection
```python
@dataclass
class ScriptSection:
    name: str                      # 'hook', 'development', 'conclusion'
    content: str
    duration_seconds: float = 0.0
    purpose: str = ""
    key_elements: List[str] = field(default_factory=list)
    
    @property
    def type(self) -> str:          # Alias para compatibilidade
        return self.name
```

### 3. GeneratedScript
```python
@dataclass
class GeneratedScript:
    title: str
    theme: GeneratedTheme
    sections: List[ScriptSection]
    total_duration: float = 0.0
    quality_score: float = 0.0
    engagement_score: float = 0.0
    retention_score: float = 0.0
    response_time: float = 0.0
    timestamp: Optional[datetime] = None
    usage: Optional[Dict[str, int]] = None
    metrics: Optional[Dict[str, Any]] = None
    platform: str = "tiktok"
```

## Compatibilidade Mantida

### Aliases
- `Script = GeneratedScript` (para compatibilidade com script_models)
- `main_title ↔ content` (compatibilidade TTS)
- `type ↔ name` (compatibilidade script_models)

### Funções de Compatibilidade
```python
def get_script_section_by_type(script: GeneratedScript, section_type: str) -> ScriptSection
def get_script_full_text(script: GeneratedScript) -> str
```

## Como Usar

### Import Recomendado
```python
# Importar do models package
from src.models import (
    ThemeCategory,
    GeneratedTheme,
    ScriptSection,
    GeneratedScript,
    ScriptGenerationResult
)
```

### Migração de Código Antigo
```python
# Antigo (ainda funciona via aliases)
from src.models.script_models import Script
from src.generators.script_generator import GeneratedScript as OldGeneratedScript

# Novo (recomendado)
from src.models import GeneratedScript, ScriptSection, ThemeCategory
```

## Funções de Migração

### Migrar Dados Existentes
```python
from src.models import migrate_from_script_models, migrate_from_script_generator

# Migrar tema do formato antigo
old_theme_data = {"main_title": "Título", "category": "animals", ...}
new_theme = migrate_from_script_models(old_theme_data)

# Migrar script do formato antigo  
old_script_data = {"title": "Título", "sections": [...], ...}
new_script = migrate_from_script_generator(old_script_data)
```

### Validação de Modelos
```python
from src.models import validate_model_consistency

validation = validate_model_consistency()
print(validation['status'])  # 'valid'
```

## Benefícios da Migração

1. **Eliminação de Duplicação**: Um único local para todas as definições de modelos
2. **Compatibilidade Total**: Código existente continua funcionando sem mudanças
3. **Melhor Manutenibilidade**: Mudanças feitas em um único lugar
4. **Validação Centralizada**: Verificação automática de consistência
5. **Migração Gradual**: Suporte a múltiplos formatos durante transição

## Arquivos Deprecados

Os seguintes arquivos estão marcados como deprecados:
- `src/models/script_models.py` - pode ser removido após migração completa
- Definições de modelos em `src/generators/script_generator.py` 
- Definições de modelos em `src/generators/theme_generator.py`

Eles podem ser removidos após verificar que todo o código foi migrado para usar os modelos unificados.

## Testes

Para testar a migração:

```python
# Testar modelos unificados
python src/models/unified_models.py

# Verificar informações da migração
from src.models import get_migration_info
print(get_migration_info())
```

A migração foi projetada para ser **sem breaking changes**, garantindo que o código existente continue funcionando enquanto beneficia os novos modelos unificados.