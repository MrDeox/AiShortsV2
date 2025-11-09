#!/usr/bin/env python3
"""
Monitor Dashboard - Dashboard de monitoramento do AiShortsV2
Exibe status dos serviços em tempo real via terminal
"""

import asyncio
import sys
import json
import time
import os
from datetime import datetime
from typing import Any, Dict, List
from pathlib import Path
from dotenv import load_dotenv

# Adicionar src ao path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(1, str(SRC_DIR))

# Carregar .env
load_dotenv(BASE_DIR / ".env")

from src.generators.prompt_engineering import ThemeCategory
from src.utils.logging_config import init_logging, get_logger
from src.config.settings import config

# Configurar logging
init_logging(level="INFO")
logger = get_logger(__name__)


class MonitorDashboard:
    """Dashboard de monitoramento em tempo real."""
    
    def __init__(self):
        self.orchestrator = None
        self.is_running = False
        self.last_update = None
        self.health_history = []
        
    async def start(self):
        """Inicia o dashboard."""
        logger.info("🖥️ Iniciando monitor dashboard...")
        
        # Criar orchestrator de forma simplificada
        try:
            # Usar apenas o health checker diretamente
            from src.core.health_checker import get_health_checker, setup_default_health_checks
            self.health_checker = get_health_checker()
            setup_default_health_checks()
            self.orchestrator = None  # Não vamos inicializar o orchestrator completo
            logger.info("✅ Health checker inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar health checker: {e}")
            return
        
        self.is_running = True
        
        # Limpar tela
        self.clear_screen()
        
        # Loop de monitoramento
        while self.is_running:
            try:
                await self.update_dashboard()
                await asyncio.sleep(5.0)  # Atualizar a cada 5 segundos
            except KeyboardInterrupt:
                logger.info("👋 Dashboard interrompido pelo usuário")
                self.is_running = False
            except Exception as e:
                logger.error(f"❌ Erro no dashboard: {e}")
                await asyncio.sleep(5.0)
    
    def clear_screen(self):
        """Limpa a tela."""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
    
    async def update_dashboard(self):
        """Atualiza o dashboard com informações atuais."""
        self.clear_screen()
        
        # Cabeçalho com alertas críticos
        critical_alerts = self.get_critical_alerts()
        
        print("=" * 80)
        if critical_alerts:
            print(f"🚨 AISHORTS V2.0 - MONITOR DASHBOARD - {len(critical_alerts)} ALERTAS CRÍTICOS")
        else:
            print(f"🎬 AISHORTS V2.0 - MONITOR DASHBOARD")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Exibir alertas críticos primeiro
        if critical_alerts:
            print("\n🚨 ALERTAS CRÍTICOS:")
            for alert in critical_alerts[:3]:  # Limitar a 3 alertas
                print(f"   ❌ {alert['component']}: {alert['message']}")
            if len(critical_alerts) > 3:
                print(f"   ... e mais {len(critical_alerts) - 3} alertas")
            print("\n" + "!" * 80)
        
        # Informações do sistema
        self.print_system_info()
        
        print("\n" + "-" * 80)
        
        # Health checks
        await self.print_health_status()
        
        print("\n" + "-" * 80)
        
        # Métricas degradadas
        self.print_degradation_metrics()
        
        print("\n" + "-" * 80)
        
        # Estatísticas do cache
        self.print_cache_stats()
        
        print("\n" + "-" * 80)
        
        # Métricas de performance
        self.print_performance_metrics()
        
        print("\n" + "-" * 80)
        
        # Comandos disponíveis
        self.print_commands()
        
        self.last_update = datetime.now()
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Obtém alertas críticos do sistema."""
        alerts = []
        
        # Verificar health checks
        if hasattr(self, 'health_checker') and self.health_checker:
            try:
                # Obter resultados dos checks sem esperar (usar cache se disponível)
                last_results = self.health_checker.get_last_results()
                for name, check in last_results.items():
                    if check.status == "unhealthy":
                        alerts.append({
                            "component": name.replace("_", " ").title(),
                            "message": check.message,
                            "severity": "critical",
                            "timestamp": check.timestamp
                        })
            except Exception:
                pass
        
        # Verificar degradações recentes
        try:
            from src.core.graceful_degradation import get_degradation_manager
            manager = get_degradation_manager()
            stats = manager.get_degradation_stats()
            
            if stats.get("recent_degradations", 0) > 5:  # Muitas degradações na última hora
                alerts.append({
                    "component": "Sistema",
                    "message": f"Alta taxa de degradações: {stats['recent_degradations']} na última hora",
                    "severity": "warning"
                })
        except Exception:
            pass
        
        # Verificar uso de recursos
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            
            if cpu > 90:
                alerts.append({
                    "component": "CPU",
                    "message": f"Uso crítico: {cpu:.1f}%",
                    "severity": "critical"
                })
            
            if memory > 90:
                alerts.append({
                    "component": "Memória",
                    "message": f"Uso crítico: {memory:.1f}%",
                    "severity": "critical"
                })
        except Exception:
            pass
        
        return alerts
    
    def print_system_info(self):
        """Exibe informações do sistema."""
        import psutil
        
        # CPU e Memória
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        print("📊 SISTEMA")
        print(f"   CPU: {cpu_percent:.1f}%")
        print(f"   Memória: {memory.percent:.1f}% ({memory.available / (1024**3):.1f}GB disponível)")
        print(f"   PID: {os.getpid()}")
        
        # Configurações
        print(f"\n⚙️ CONFIGURAÇÕES")
        print(f"   OpenRouter: {config.openrouter.model}")
        print(f"   Environment: {config.project.environment}")
        print(f"   Log Level: {config.logging.level}")
        
        # Feature flags LLM
        print(f"\n🧠 INTEGRAÇÕES LLM")
        llm_config = config.llm_integration
        print(f"   Theme Strategy: {'✅' if llm_config.use_llm_theme_strategy else '❌'}")
        print(f"   Script Refiner: {'✅' if llm_config.use_llm_script_refiner else '❌'}")
        print(f"   B-roll Planner: {'✅' if llm_config.use_llm_broll_planner else '❌'}")
        print(f"   Content Cache: {'✅' if llm_config.enable_content_cache else '❌'}")
    
    async def print_health_status(self):
        """Exibe status de saúde dos componentes."""
        if not self.health_checker:
            print("❌ Health checker não inicializado")
            return
        
        print("🏥 HEALTH STATUS")
        
        try:
            # Executar health checks
            results = await self.health_checker.run_all_checks()
            summary = self.health_checker.get_health_summary()
            
            # Status geral
            status_icon = "✅" if summary["status"] == "healthy" else "⚠️" if summary["status"] == "degraded" else "❌"
            print(f"   Status Geral: {status_icon} {summary['status'].upper()}")
            print(f"   {summary['message']}")
            
            # Health checks detalhados
            print("\n   Health Checks:")
            for name, check in results.items():
                icon = "✅" if check.status == "healthy" else "⚠️" if check.status == "degraded" else "❌"
                print(f"   • {name}: {icon} {check.message} ({check.response_time:.3f}s)")
            
            # Salvar no histórico
            self.health_history.append({
                "timestamp": datetime.now().isoformat(),
                "status": summary["status"],
                "healthy_count": summary.get("healthy", 0),
                "total_count": summary.get("total_dependencies", 0)
            })
            
            # Manter apenas últimas 100 entradas
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
        except Exception as e:
            print(f"❌ Erro ao obter status: {e}")
    
    def print_degradation_metrics(self):
        """Exibe métricas de degradação."""
        try:
            from src.core.graceful_degradation import get_degradation_manager
            
            manager = get_degradation_manager()
            stats = manager.get_degradation_stats()
            
            print("🛡️ GRACEFUL DEGRADATION")
            
            if stats["total_degradations"] == 0:
                print("   ✅ Nenhuma degradação registrada")
            else:
                print(f"   Total de Degradações: {stats['total_degradations']}")
                print(f"   Última Hora: {stats['recent_degradations']}")
                
                if stats["top_failing_components"]:
                    print("\n   Componentes com Problemas:")
                    for component, count in stats["top_failing_components"]:
                        print(f"   • {component}: {count} falhas")
                
                # Circuit breakers
                if manager.circuit_breakers:
                    print(f"\n   Circuit Breakers:")
                    for name, cb in manager.circuit_breakers.items():
                        state_icon = "🔓" if cb.state == "CLOSED" else "🔴" if cb.state == "OPEN" else "🟡"
                        print(f"   • {name}: {state_icon} {cb.state} ({cb.failure_count} falhas)")
            
        except Exception as e:
            print(f"❌ Erro ao obter métricas: {e}")
    
    def print_cache_stats(self):
        """Exibe estatísticas do cache."""
        try:
            from src.core.content_cache import get_content_cache
            
            cache = get_content_cache()
            stats = cache.get_stats()
            
            print("💾 CACHE DE CONTEÚDO")
            print(f"   Hit Rate: {stats['hit_rate_percent']:.1f}%")
            print(f"   Total Requests: {stats['total_requests']}")
            print(f"   Hits: {stats['hits']}")
            print(f"   Misses: {stats['misses']}")
            print(f"   Entradas Ativas: {stats['current_entries']}")
            print(f"   Tamanho: {stats['current_size_mb']:.2f}MB / {stats['max_size_mb']:.0f}MB")
            
            # Top entries
            top_entries = cache.get_top_entries(5)
            if top_entries:
                print(f"\n   Mais Acessados:")
                for entry in top_entries:
                    print(f"   • {entry['key']}: {entry['access_count']}x acessos")
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
    
    def print_performance_metrics(self):
        """Exibe métricas de performance do pipeline."""
        print("📈 MÉTRICAS DE PERFORMANCE")
        
        # Taxa de sucesso do pipeline
        if self.health_history:
            recent_checks = self.health_history[-10:]  # Últimas 10 verificações
            healthy_count = sum(1 for h in recent_checks if h["status"] == "healthy")
            success_rate = (healthy_count / len(recent_checks)) * 100
            print(f"   Taxa de Sucesso (últimas 10): {success_rate:.0f}%")
        
        # Tempo de resposta dos health checks
        if hasattr(self, 'health_checker') and self.health_checker:
            try:
                response_times = []
                for check in self.health_checker._last_results.values():
                    if hasattr(check, 'response_time'):
                        response_times.append(check.response_time)
                
                if response_times:
                    avg_response = sum(response_times) / len(response_times)
                    max_response = max(response_times)
                    print(f"   Tempo Resposta Médio: {avg_response:.3f}s")
                    print(f"   Tempo Resposta Máximo: {max_response:.3f}s")
            except Exception:
                pass
        
        # Throughput do cache
        try:
            from src.core.content_cache import get_content_cache
            cache = get_content_cache()
            stats = cache.get_stats()
            
            if stats["total_requests"] > 0:
                print(f"   Cache Throughput: {stats['total_requests']} requisições")
                if stats["hit_rate_percent"] > 0:
                    print(f"   Eficiência do Cache: {stats['hit_rate_percent']:.1f}%")
        except Exception:
            pass
        
        # Uso de rede (estimado)
        try:
            import psutil
            network = psutil.net_io_counters()
            if network:
                mb_sent = network.bytes_sent / (1024 * 1024)
                mb_recv = network.bytes_recv / (1024 * 1024)
                print(f"   Rede Enviada: {mb_sent:.1f}MB")
                print(f"   Rede Recebida: {mb_recv:.1f}MB")
        except Exception:
            pass
        
        # Processamento de vídeos
        outputs_dir = Path("outputs/final")
        if outputs_dir.exists():
            videos = list(outputs_dir.glob("*.mp4"))
            if videos:
                # Vídeos das últimas 24h
                import time
                now = time.time()
                recent_videos = [v for v in videos if now - v.stat().st_mtime < 86400]
                print(f"   Vídeos (24h): {len(recent_videos)}")
                
                if recent_videos:
                    # Tamanho total dos vídeos recentes
                    total_size = sum(v.stat().st_size for v in recent_videos) / (1024 * 1024)
                    print(f"   Tamanho Total: {total_size:.1f}MB")
    
    def print_commands(self):
        """Exibe comandos disponíveis."""
        print("⌨️ COMANDOS")
        print("   Ctrl+C: Sair do dashboard")
        print("   python run_tests.py: Executar todos os testes")
        print("   python test_llm_integrations.py: Testar integrações LLM")
        print(f"   📄 Relatórios salvos em: outputs/")
        
        # Verificar se há vídeos gerados recentemente
        outputs_dir = Path("outputs/final")
        if outputs_dir.exists():
            videos = list(outputs_dir.glob("*.mp4"))
            if videos:
                videos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                latest = videos[0]
                age = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime))
                print(f"\n   📹 Vídeo mais recente: {latest.name} (há {age.total_seconds() // 60} min)")
    
    def print_status_bar(self):
        """Exibe barra de status."""
        if self.last_update:
            elapsed = (datetime.now() - self.last_update).total_seconds()
            print(f"\n🔄 Última atualização: {elapsed:.1f}s atrás", end="", flush=True)


async def main():
    """Função principal."""
    print("🖥️ AISHORTS V2.0 - Monitor Dashboard")
    print("=" * 50)
    print("Monitoramento em tempo real do pipeline...")
    
    dashboard = MonitorDashboard()
    await dashboard.start()


if __name__ == "__main__":
    asyncio.run(main())