"""
Configuração centralizada de logging para o AiShorts v2.0.
Garante uso consistente de logging em toda a aplicação, sem prints.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class AiShortsLogger:
    """
    Wrapper para logging com formatação personalizada e métodos convenientes.
    """
    
    # Níveis de log personalizados com emojis
    LOG_EMOJIS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨"
    }
    
    # Formato personalizado para os logs
    DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def setup_logging(
        cls,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        format_string: Optional[str] = None,
        enable_console: bool = True
    ) -> None:
        """
        Configura o sistema de logging da aplicação.
        
        Args:
            level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Arquivo para salvar logs (opcional)
            format_string: Formato personalizado para logs
            enable_console: Se deve habilitar logs no console
        """
        # Limpar configurações existentes
        root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.setLevel(level)
        
        # Formato
        fmt = format_string or cls.DEFAULT_FORMAT
        
        # Handler para console
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_formatter = cls._ColorFormatter(fmt, cls.DATE_FORMAT)
            console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)
        
        # Handler para arquivo
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(fmt, cls.DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)
        
        # Desabilitar logs de bibliotecas externas muito verbosas
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("moviepy").setLevel(logging.WARNING)
        logging.getLogger("yt_dlp").setLevel(logging.WARNING)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Obtém um logger configurado para o módulo especificado.
        
        Args:
            name: Nome do módulo/logger
            
        Returns:
            Logger configurado
        """
        return logging.getLogger(name)
    
    @classmethod
    def log_emoji(cls, logger: logging.Logger, level: int, message: str, *args, **kwargs):
        """
        Registra log com emoji baseado no nível.
        
        Args:
            logger: Instância do logger
            level: Nível do log
            message: Mensagem com placeholder para emoji
        """
        emoji = cls.LOG_EMOJIS.get(level, "")
        formatted_message = f"{emoji} {message}"
logger.log(level, formatted_message, *args, **kwargs)
    
    @classmethod
    def log_pipeline_start(cls, logger: logging.Logger, pipeline_name: str):
        """Log de início de pipeline."""
logger.info("=" * 70)
logger.info(f" INICIANDO {pipeline_name.upper()}")
logger.info("=" * 70)
    
    @classmethod
    def log_pipeline_success(cls, logger: logging.Logger, pipeline_name: str, duration: float):
        """Log de sucesso de pipeline."""
logger.info("=" * 70)
logger.info(f" {pipeline_name.upper()} CONCLUÍDO COM SUCESSO!")
logger.info(f"⏱ Tempo total: {duration:.2f}s")
logger.info("=" * 70)
    
    @classmethod
    def log_pipeline_failure(cls, logger: logging.Logger, pipeline_name: str, error: str):
        """Log de falha de pipeline."""
logger.error("=" * 70)
logger.error(f" {pipeline_name.upper()} FALHOU!")
logger.error(f" Erro: {error}")
logger.error("=" * 70)
    
    @classmethod
    def log_memory_usage(cls, logger: logging.Logger, usage_gb: float, system_percent: float, label: str = ""):
        """Log de uso de memória."""
        if label:
logger.info(f" {label}: {usage_gb:.2f}GB ({system_percent:.1f}% sistema)")
        else:
logger.info(f" Memória: {usage_gb:.2f}GB ({system_percent:.1f}% sistema)")
    
    @classmethod
    def log_progress(cls, logger: logging.Logger, current: int, total: int, description: str):
        """Log de progresso."""
        percent = (current / total) * 100
logger.info(f" Progresso: {description} - {current}/{total} ({percent:.1f}%)")
    
    @classmethod
    def log_step(cls, logger: logging.Logger, step_num: int, description: str):
        """Log de etapa do pipeline."""
logger.info(f" ETAPA {step_num}: {description}...")
    
    @classmethod
    def save_execution_report(cls, report: Dict[str, Any], output_dir: str = "outputs"):
        """
        Salva relatório de execução em formato JSON.
        
        Args:
            report: Dicionário com dados do relatório
            output_dir: Diretório para salvar o relatório
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"execution_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger = cls.get_logger(__name__)
logger.info(f" Relatório de execução salvo: {report_file}")
    
    class _ColorFormatter(logging.Formatter):
        """Formatter com cores para logs no console."""
        
        # Códigos de cor ANSI
        COLORS = {
            'DEBUG': '\033[36m',      # Ciano
            'INFO': '\033[32m',       # Verde
            'WARNING': '\033[33m',    # Amarelo
            'ERROR': '\033[31m',      # Vermelho
            'CRITICAL': '\033[35m',   # Magenta
            'RESET': '\033[0m'        # Reset
        }
        
        def format(self, record):
            # Adicionar cor baseada no nível
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = (
                    f"{self.COLORS[levelname]}{levelname}"
                    f"{self.COLORS['RESET']}"
                )
            
            # Formatar mensagem
            formatted = super().format(record)
            
            # Remover cores se não estiver em terminal
            if not sys.stdout.isatty():
                for color in self.COLORS.values():
                    formatted = formatted.replace(color, '')
            
            return formatted


# Função de conveniência para obter logger
def get_logger(name: str) -> logging.Logger:
    """Obtém um logger configurado."""
    return AiShortsLogger.get_logger(name)


# Inicialização padrão ao importar o módulo
def init_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_file_rotation: bool = True
) -> None:
    """
    Inicializa o logging com configurações padrão.
    
    Args:
        level: Nível de log como string ('DEBUG', 'INFO', etc.)
        log_file: Arquivo de log (opcional)
        enable_file_rotation: Se deve habilitar rotação de arquivos
    """
    # Converter string para nível
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Nome de arquivo padrão se não fornecido
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"logs/aishorts_{timestamp}.log"
    
    # Configurar logging
    AiShortsLogger.setup_logging(
        level=numeric_level,
        log_file=log_file if enable_file_rotation else None,
        enable_console=True
    )
    
    # Log de inicialização
    logger = get_logger(__name__)
logger.info("System de logging inicializado")
logger.info(f" Nível: {level.upper()}")
    if log_file:
logger.info(f" Arquivo: {log_file}")


# Decorador para capturar e logar exceções
def log_exceptions(logger: Optional[logging.Logger] = None):
    """
    Decorador para automaticamente logar exceções.
    
    Args:
        logger: Logger personalizado (opcional)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
logger.error(f" Exceção em {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


# Context manager para log de performance
class LogPerformance:
    """
    Context manager para medir e logar performance de operações.
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        operation_name: str,
        level: int = logging.INFO
    ):
        self.logger = logger
        self.operation_name = operation_name
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
self.logger.log(self.level, f"⏱ Iniciando: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
self.logger.log(
                self.level,
                f"✅ Concluído: {self.operation_name} ({duration:.2f}s)"
            )
        else:
self.logger.error(
                f"❌ Falhou: {self.operation_name} ({duration:.2f}s) - {exc_val}"
            )
    
    def elapsed(self) -> float:
        """Retorna tempo decorrido em segundos."""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0


if __name__ == "__main__":
    # Teste do sistema de logging
    init_logging(level="DEBUG")
    
    logger = get_logger("test")
    
    # Teste dos diferentes tipos de log
    AiShortsLogger.log_pipeline_start(logger, "Test Pipeline")
    
    with LogPerformance(logger, "Operação de Teste"):
        AiShortsLogger.log_step(logger, 1, "Processamento de dados")
        AiShortsLogger.log_progress(logger, 50, 100, "Processando arquivos")
        AiShortsLogger.log_memory_usage(logger, 2.5, 45.2, "Memória atual")
    
logger.info(" Sistema de logging configurado com sucesso!")
logger.warning(" Este é um aviso de teste")
logger.error(" Este é um erro de teste")
logger.debug(" Este é um debug de teste")
    
    AiShortsLogger.log_pipeline_success(logger, "Test Pipeline", 1.23)