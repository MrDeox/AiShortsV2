"""
Configurações principais do AiShorts v2.0

Centraliza todas as configurações do projeto em um sistema robusto.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Carregar variáveis de ambiente explicitamente
from pathlib import Path
load_dotenv(dotenv_path=Path(".env").absolute())

class OpenRouterSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    """Configurações da integração OpenRouter."""
    
    api_key: str = Field(default="", env="OPENROUTER_API_KEY")
    base_url: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    model: str = Field(default="qwen/qwen3-235b-a22b:free", env="OPENROUTER_MODEL")
    max_tokens_theme: int = Field(default=2048, env="MAX_TOKENS_THEME")
    temperature_theme: float = Field(default=0.7, env="TEMPERATURE_THEME")
    max_tokens_script: int = Field(default=4096, env="MAX_TOKENS_SCRIPT")
    temperature_script: float = Field(default=0.7, env="TEMPERATURE_SCRIPT")

class LoggingSettings(BaseSettings):
    """Configurações do sistema de logging."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    log_file: str = Field(default="logs/aishorts.log", env="LOG_FILE")
    max_size: str = Field(default="10MB", env="LOG_MAX_SIZE")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

class ThemeGeneratorSettings(BaseSettings):
    """Configurações do gerador de temas."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    categories: List[str] = Field(
        default=["science", "history", "nature", "technology", "culture", 
                "space", "animals", "psychology", "geography", "food"],
        env="THEME_CATEGORIES"
    )
    max_attempts: int = Field(default=3, env="MAX_ATTEMPTS_THEME")
    
    @field_validator('categories', mode='before')
    @classmethod
    def parse_categories(cls, v):
        """Converte string separada por vírgulas em lista."""
        if isinstance(v, str):
            return [cat.strip() for cat in v.split(',')]
        return v

class ScriptGeneratorSettings(BaseSettings):
    """Configurações do gerador de roteiro."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    target_duration: int = Field(default=60, env="SCRIPT_TARGET_DURATION")
    min_quality_score: float = Field(default=0.7, env="SCRIPT_MIN_QUALITY_SCORE")
    max_attempts: int = Field(default=3, env="MAX_ATTEMPTS_SCRIPT")
    platforms: List[str] = Field(
        default=["tiktok", "shorts", "reels"],
        env="SCRIPT_PLATFORMS"
    )
    
    @field_validator('platforms', mode='before')
    @classmethod
    def parse_platforms(cls, v):
        """Converte string separada por vírgulas em lista."""
        if isinstance(v, str):
            return [plat.strip() for plat in v.split(',')]
        return v

class RetrySettings(BaseSettings):
    """Configurações de retry e rate limiting."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
    rate_limit_per_minute: int = Field(default=20, env="RATE_LIMIT_PER_MINUTE")

class StorageSettings(BaseSettings):
    """Configurações de armazenamento."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    output_dir: Path = Field(default=Path("data/output"), env="OUTPUT_DIR")
    temp_dir: Path = Field(default=Path("data/temp"), env="TEMP_DIR")
    cache_dir: Path = Field(default=Path("data/cache"), env="CACHE_DIR")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Criar diretórios se não existirem
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

class ProjectSettings(BaseSettings):
    """Configurações gerais do projeto."""
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
    environment: str = Field(default="development", env="PROJECT_ENV")
    version: str = Field(default="2.0.0", env="PROJECT_VERSION")
    debug: bool = Field(default=False)
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment deve ser um de: {valid_envs}")
        return v

class AiShortsConfig:
    """Configuração principal consolidada do AiShorts."""
    
    def __init__(self):
        self.project = ProjectSettings()
        self.openrouter = OpenRouterSettings()
        self.logging = LoggingSettings()
        self.theme_gen = ThemeGeneratorSettings()
        self.script_gen = ScriptGeneratorSettings()
        self.retry = RetrySettings()
        self.storage = StorageSettings()
        
        # Configurar debug baseado no ambiente
        self.project.debug = self.project.environment == "development"
    
    def validate_config(self, strict: bool = True) -> bool:
        """
        Valida se todas as configurações estão corretas.
        
        Args:
            strict: Se True, requer API key válida. Se False, permite testes sem API key.
        """
        try:
            # Verificar se a API key está configurada (apenas se strict=True)
            if strict:
                if not self.openrouter.api_key or self.openrouter.api_key in ["your_openrouter_api_key_here", "sk-test-key-for-testing"]:
                    raise ValueError("OPENROUTER_API_KEY não está configurada ou é inválida")
            
            # Verificar se o modelo é válido
            if "qwen3-235b-a22b" not in self.openrouter.model:
                raise ValueError("Modelo OpenRouter deve ser qwen/qwen3-235b-a22b:free")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Erro na configuração: {e}")
    
    def get_summary(self) -> dict:
        """Retorna resumo das configurações."""
        return {
            "environment": self.project.environment,
            "version": self.project.version,
            "openrouter_model": self.openrouter.model,
            "theme_categories": self.theme_gen.categories,
            "script_target_duration": self.script_gen.target_duration,
            "script_platforms": self.script_gen.platforms,
            "max_retries": self.retry.max_retries,
            "rate_limit_per_minute": self.retry.rate_limit_per_minute,
            "directories": {
                "output": str(self.storage.output_dir),
                "temp": str(self.storage.temp_dir),
                "cache": str(self.storage.cache_dir)
            }
        }

# Instância global de configuração
config = AiShortsConfig()

if __name__ == "__main__":
    # Teste de configuração
    print("=== AiShorts v2.0 - Configuração ===")
    print(config.get_summary())
    
    # Teste de validação
    try:
        config.validate_config()
        print("✅ Configuração válida!")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
