"""
Sistema de Validação - AiShorts v2.0

Módulo responsável pela validação avançada de roteiros gerados,
incluindo checagem de estrutura, qualidade, requisitos de plataforma
e sugestões de melhorias.
"""

from .script_validator import (
    ScriptValidator,
    ValidationResult,
    ValidationReport,
    ScriptValidationError,
    PlatformRequirements,
    QualityMetrics
)

__all__ = [
    'ScriptValidator',
    'ValidationResult', 
    'ValidationReport',
    'ScriptValidationError',
    'PlatformRequirements',
    'QualityMetrics'
]
