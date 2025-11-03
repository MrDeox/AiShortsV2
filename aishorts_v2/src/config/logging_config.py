"""
Configurações de Logging do AiShorts v2.0

Sistema de logging robusto para análise de qualidade e debugging.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

# Configuração do diretório de logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configuração do arquivo de log principal
LOG_FILE = LOG_DIR / f"aishorts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Remover o logger padrão do sistema
logger.remove()

# Adicionar logger para console (stderr)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="INFO",
    colorize=True
)

# Adicionar logger para arquivo (json format)
logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,  # Thread-safe
    serialize=True  # JSON format para análise posterior
)

# Configuração para logs de erro específicos
ERROR_LOG_FILE = LOG_DIR / "errors.log"
logger.add(
    ERROR_LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | ERROR | {file}:{function}:{line} | {message}",
    level="ERROR",
    rotation="5 MB",
    retention="7 days",
    filter=lambda record: record["level"].name in ["ERROR", "CRITICAL"]
)

# Função para configurar level baseado em ambiente
def setup_logging(level: str = "INFO", environment: str = "development"):
    """Configura o level de logging baseado no ambiente."""
    if environment == "development":
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", colorize=True)
        logger.add(LOG_FILE, level="DEBUG", serialize=True)
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO", colorize=False)
        logger.add(LOG_FILE, level="INFO", serialize=True)

if __name__ == "__main__":
    # Teste de configuração de logging
    logger.info("Sistema de logging do AiShorts v2.0 inicializado")
    logger.debug("Teste de debug - apenas em desenvolvimento")
    logger.warning("Teste de warning")
    logger.error("Teste de error")