"""
Health Checker - Sistema de verificação de saúde dos componentes
Monitora o status de todos os serviços e dependências do pipeline
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import psutil
import json
from pathlib import Path

from loguru import logger


class HealthStatus(Enum):
    """Status de saúde dos componentes."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Resultado de um health check."""
    component: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "response_time": round(self.response_time, 3),
            "timestamp": self.timestamp.isoformat(),
            "details": self.details or {},
            "last_error": self.last_error
        }


class HealthChecker:
    """
    Verificador de saúde para componentes do pipeline.
    
    Features:
    - Checks assíncronos e síncronos
    - Métricas de performance
    - Histórico de saúde
    - Alertas automáticos
    - Relatórios detalhados
    """
    
    def __init__(self, check_interval: float = 60.0):
        """
        Inicializa o health checker.
        
        Args:
            check_interval: Intervalo entre checks em segundos
        """
        self.check_interval = check_interval
        self.checks: Dict[str, Callable] = {}
        self.history: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.is_running = False
        
logger.info(f"HealthChecker inicializado - Intervalo: {check_interval}s")
    
    def register_check(self, name: str, check_func: Callable):
        """
        Registra um health check.
        
        Args:
            name: Nome do componente
            check_func: Função de verificação
        """
        self.checks[name] = check_func
logger.info(f"Health check registrado: {name}")
    
    async def run_check_async(self, name: str) -> HealthCheck:
        """
        Executa um check assíncrono.
        
        Args:
            name: Nome do check
            
        Returns:
            HealthCheck result
        """
        if name not in self.checks:
            return HealthCheck(
                component=name,
                status=HealthStatus.UNKNOWN,
                message="Check not found",
                response_time=0.0,
                timestamp=datetime.now()
            )
        
        start_time = time.time()
        
        try:
            # Executar check
            result = await self.checks[name]()
            response_time = time.time() - start_time
            
            # Interpretar resultado
            if isinstance(result, dict):
                status = HealthStatus(result.get("status", "unknown"))
                message = result.get("message", "Check completed")
                details = result.get("details", {})
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Component is " + ("healthy" if result else "unhealthy")
                details = {}
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
                details = {"result": result}
            
            return HealthCheck(
                component=name,
                status=status,
                message=message,
                response_time=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = time.time() - start_time
logger.error(f"Health check failed for {name}: {str(e)}")
            
            return HealthCheck(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                response_time=response_time,
                timestamp=datetime.now(),
                last_error=str(e)
            )
    
    def run_check_sync(self, name: str) -> HealthCheck:
        """
        Executa um check síncrono.
        
        Args:
            name: Nome do check
            
        Returns:
            HealthCheck result
        """
        if name not in self.checks:
            return HealthCheck(
                component=name,
                status=HealthStatus.UNKNOWN,
                message="Check not found",
                response_time=0.0,
                timestamp=datetime.now()
            )
        
        start_time = time.time()
        
        try:
            # Executar check
            result = self.checks[name]()
            response_time = time.time() - start_time
            
            # Interpretar resultado
            if isinstance(result, dict):
                status = HealthStatus(result.get("status", "unknown"))
                message = result.get("message", "Check completed")
                details = result.get("details", {})
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Component is " + ("healthy" if result else "unhealthy")
                details = {}
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
                details = {"result": result}
            
            return HealthCheck(
                component=name,
                status=status,
                message=message,
                response_time=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = time.time() - start_time
logger.error(f"Health check failed for {name}: {str(e)}")
            
            return HealthCheck(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                response_time=response_time,
                timestamp=datetime.now(),
                last_error=str(e)
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """
        Executa todos os checks registrados.
        
        Returns:
            Dicionário com resultados de todos os checks
        """
        results = {}
        
        # Executar todos em paralelo
        tasks = [self.run_check_async(name) for name in self.checks.keys()]
        health_checks = await asyncio.gather(*tasks)
        
        # Mapear resultados
        for i, name in enumerate(self.checks.keys()):
            results[name] = health_checks[i]
        
        # Adicionar ao histórico
        self._add_to_history(results)
        
        # Verificar alertas
        self._check_alerts(results)
        
        return results
    
    def _add_to_history(self, results: Dict[str, HealthCheck]):
        """Adiciona resultados ao histórico."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(results),
            "healthy": len([r for r in results.values() if r.status == HealthStatus.HEALTHY]),
            "degraded": len([r for r in results.values() if r.status == HealthStatus.DEGRADED]),
            "unhealthy": len([r for r in results.values() if r.status == HealthStatus.UNHEALTHY]),
            "checks": {name: check.to_dict() for name, check in results.items()}
        }
        
        self.history.append(snapshot)
        
        # Manter apenas últimas 1000 entradas
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def _check_alerts(self, results: Dict[str, HealthCheck]):
        """Verifica se há alertas para emitir."""
        for name, check in results.items():
            # Alerta para componentes unhealthy
            if check.status == HealthStatus.UNHEALTHY:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "level": "critical",
                    "component": name,
                    "message": f"Component {name} is unhealthy: {check.message}",
                    "details": check.to_dict()
                }
                
                # Verificar se é um novo problema
                recent_alerts = [
                    a for a in self.alerts[-10:]
                    if a["component"] == name and a["level"] == "critical"
                ]
                
                if not recent_alerts or (datetime.now() - datetime.fromisoformat(recent_alerts[-1]["timestamp"])) > timedelta(minutes=5):
                    self.alerts.append(alert)
logger.critical(f"HEALTH ALERT: {alert['message']}")
            
            # Alerta para componentes degradados
            elif check.status == HealthStatus.DEGRADED:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "level": "warning",
                    "component": name,
                    "message": f"Component {name} is degraded: {check.message}",
                    "details": check.to_dict()
                }
                
                # Verificar se é um novo problema
                recent_alerts = [
                    a for a in self.alerts[-10:]
                    if a["component"] == name and a["level"] == "warning"
                ]
                
                if not recent_alerts or (datetime.now() - datetime.fromisoformat(recent_alerts[-1]["timestamp"])) > timedelta(minutes=15):
                    self.alerts.append(alert)
logger.warning(f"HEALTH WARNING: {alert['message']}")
    
    def get_last_results(self) -> Dict[str, HealthCheck]:
        """Retorna os últimos resultados dos health checks."""
        return self._last_results.copy()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo da saúde do sistema.
        
        Returns:
            Resumo com status geral
        """
        if not self.history:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health checks performed yet",
                "timestamp": datetime.now().isoformat()
            }
        
        latest = self.history[-1]
        
        # Determinar status geral
        if latest["unhealthy"] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif latest["degraded"] > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return {
            "status": overall_status.value,
            "message": f"{latest['healthy']}/{latest['total_checks']} components healthy",
            "timestamp": latest["timestamp"],
            "details": latest["checks"]
        }
    
    def get_component_health(self, component: str) -> Optional[HealthCheck]:
        """
        Obtém o status de saúde de um componente específico.
        
        Args:
            component: Nome do componente
            
        Returns:
            Health check mais recente ou None
        """
        if not self.history:
            return None
        
        latest = self.history[-1]
        if component in latest["checks"]:
            check_data = latest["checks"][component]
            return HealthCheck(
                component=check_data["component"],
                status=HealthStatus(check_data["status"]),
                message=check_data["message"],
                response_time=check_data["response_time"],
                timestamp=datetime.fromisoformat(check_data["timestamp"]),
                details=check_data.get("details"),
                last_error=check_data.get("last_error")
            )
        
        return None
    
    def save_report(self, filepath: Optional[str] = None) -> str:
        """
        Salva relatório de saúde em arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo (gera automaticamente se None)
            
        Returns:
            Caminho do arquivo salvo
        """
        if filepath is None:
            filepath = f"reports/health_report_{int(time.time())}.json"
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_health_summary(),
            "recent_history": self.history[-10:],  # Últimos 10 snapshots
            "recent_alerts": self.alerts[-50:],  # Últimos 50 alertas
            "registered_checks": list(self.checks.keys())
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
logger.info(f"Health report saved to: {filepath}")
        return filepath
    
    async def start_monitoring(self):
        """Inicia monitoramento contínuo."""
        self.is_running = True
logger.info("Starting continuous health monitoring...")
        
        while self.is_running:
            try:
                results = await self.run_all_checks()
                
                # Log resumo
                healthy = len([r for r in results.values() if r.status == HealthStatus.HEALTHY])
                total = len(results)
                
                if healthy == total:
logger.debug(f" All {total} components healthy")
                else:
logger.warning(f" Health: {healthy}/{total} components healthy")
                
                # Esperar próximo check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Para o monitoramento contínuo."""
        self.is_running = False
logger.info("Health monitoring stopped")


# Health checks específicos
async def check_openrouter_api() -> Dict[str, Any]:
    """Verifica saúde da API OpenRouter."""
    try:
        import httpx
        
        # Testar API key
        import os
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return {
                "status": "unhealthy",
                "message": "API key not configured"
            }
        
        # Fazer request de teste
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "API responding normally",
                    "details": {
                        "models_available": len(response.json().get("data", [])),
                        "response_code": response.status_code
                    }
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"API returned status {response.status_code}",
                    "details": {"response_code": response.status_code}
                }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)}"
        }


async def check_tts_service() -> Dict[str, Any]:
    """Verifica saúde do serviço TTS."""
    try:
        from src.tts.kokoro_tts import KokoroTTSClient
        
        client = KokoroTTSClient()
        
        # Testar síntese simples
        result = client.text_to_speech(
            "Test",
            output_basename="health_check",
            timeout=5.0
        )
        
        if result.get("success"):
            return {
                "status": "healthy",
                "message": "TTS service operational",
                "details": {
                    "voice": result.get("voice"),
                    "duration": result.get("duration")
                }
            }
        else:
            return {
                "status": "unhealthy",
                "message": f"TTS failed: {result.get('error')}"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"TTS service unavailable: {str(e)}"
        }


async def check_youtube_extractor() -> Dict[str, Any]:
    """Verifica saúde do extrator YouTube."""
    try:
        from src.video.extractors.youtube_extractor import YouTubeExtractor
        
        extractor = YouTubeExtractor()
        
        # Testar busca simples
        results = extractor.search_videos("test", max_results=1)
        
        if results:
            return {
                "status": "healthy",
                "message": "YouTube extractor working",
                "details": {
                    "results_found": len(results)
                }
            }
        else:
            return {
                "status": "degraded",
                "message": "No results returned (may be temporary)"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"YouTube extractor failed: {str(e)}"
        }


def check_system_resources() -> Dict[str, Any]:
    """Verifica recursos do sistema."""
    try:
        # Memória
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Disco
        disk = psutil.disk_usage("/")
        disk_usage = (disk.used / disk.total) * 100
        
        # Determinar status
        if memory_usage > 90 or cpu_usage > 90 or disk_usage > 90:
            status = "unhealthy"
        elif memory_usage > 70 or cpu_usage > 70 or disk_usage > 80:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "message": f"System resources - CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%, Disk: {disk_usage:.1f}%",
            "details": {
                "cpu_percent": cpu_usage,
                "memory_percent": memory_usage,
                "disk_percent": disk_usage,
                "memory_available_gb": memory.available / (1024**3)
            }
        }
        
    except Exception as e:
        return {
            "status": "unknown",
            "message": f"Could not check resources: {str(e)}"
        }


# Instância global
health_checker = HealthChecker(check_interval=60.0)


def get_health_checker() -> HealthChecker:
    """Retorna instância global do health checker."""
    return health_checker


def setup_default_health_checks():
    """Configura health checks padrão."""
    checker = get_health_checker()
    
    # Registrar checks
    checker.register_check("openrouter_api", check_openrouter_api)
    checker.register_check("tts_service", check_tts_service)
    checker.register_check("youtube_extractor", check_youtube_extractor)
    checker.register_check("system_resources", check_system_resources)
    
logger.info("Default health checks configured")


if __name__ == "__main__":
    # Teste do health checker
    import asyncio
    
    async def main():
print(" Testing Health Checker System")
print("=" * 50)
        
        # Configurar checks
        setup_default_health_checks()
        
        # Executar todos os checks
        results = await health_checker.run_all_checks()
        
        # Exibir resultados
print("\n Health Check Results:")
        for name, check in results.items():
            icon = "✅" if check.status == HealthStatus.HEALTHY else "⚠️" if check.status == HealthStatus.DEGRADED else "❌"
print(f"   {icon} {name}: {check.message} ({check.response_time:.3f}s)")
        
        # Resumo
        summary = health_checker.get_health_summary()
print(f"\n Overall Status: {summary['status'].upper()}")
print(f"   {summary['message']}")
        
        # Salvar relatório
        filepath = health_checker.save_report()
print(f"\n Report saved: {filepath}")
    
    asyncio.run(main())