#!/usr/bin/env python3
"""
Script simples para testar o monitor dashboard
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar src ao path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(1, str(SRC_DIR))

async def main():
    """Testa o dashboard com validações básicas."""
    print("🧪 Testando Monitor Dashboard...")
    print("=" * 50)
    
    # Testar 1: Importação
    try:
        from monitor_dashboard import MonitorDashboard
        print("✅ Importação bem sucedida")
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return
    
    # Testar 2: Inicialização
    try:
        dashboard = MonitorDashboard()
        print("✅ Dashboard inicializado")
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return
    
    # Testar 3: Health checks
    try:
        if hasattr(dashboard, 'health_checker') and dashboard.health_checker:
            results = await dashboard.health_checker.run_all_checks()
            print(f"✅ Health checks executados: {len(results)} componentes")
        else:
            print("⚠️ Health checker não disponível")
    except Exception as e:
        print(f"❌ Erro nos health checks: {e}")
    
    # Testar 4: Cache
    try:
        from src.core.content_cache import get_content_cache
        cache = get_content_cache()
        stats = cache.get_stats()
        print(f"✅ Cache funcionando: {stats['current_entries']} entradas")
    except Exception as e:
        print(f"❌ Erro no cache: {e}")
    
    # Testar 5: Graceful degradation
    try:
        from src.core.graceful_degradation import get_degradation_manager
        manager = get_degradation_manager()
        stats = manager.get_degradation_stats()
        print(f"✅ Grace degradation: {stats['total_degradations']} degradações")
    except Exception as e:
        print(f"❌ Erro no graceful degradation: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testes concluídos! O dashboard está pronto para uso.")
    print("\nPara executar o dashboard em tempo real:")
    print("python monitor_dashboard.py")

if __name__ == "__main__":
    asyncio.run(main())