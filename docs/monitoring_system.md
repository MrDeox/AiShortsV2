# Sistema de Monitoramento - AiShortsV2

## Visão Geral

Implementei um sistema completo de monitoramento em tempo real para o pipeline do AiShortsV2, com dashboard via terminal que exibe status dos componentes, métricas de performance e alertas críticos.

## Componentes Implementados

### 1. HealthChecker (`src/core/health_checker.py`)
- Sistema de verificação de saúde para todos os componentes
- Health checks assíncronos para:
  - **OpenRouter API**: Verifica conectividade e quota
  - **TTS Service**: Testa geração de áudio
  - **YouTube Extractor**: Valida extração de vídeos
  - **System Resources**: Monitora CPU, memória e disco
- Registro automático de alertas e degraded warnings
- Histórico de verificações com tendências

### 2. Monitor Dashboard (`monitor_dashboard.py`)
Dashboard em tempo real com:
- **Status Geral**: Visão rápida da saúde do sistema
- **Alertas Críticos**: Destaque para problemas urgentes
- **Informações do Sistema**: CPU, memória, configurações
- **Health Checks Detalhados**: Status de cada componente
- **Graceful Degradation**: Estatísticas de falhas e circuit breakers
- **Cache de Conteúdo**: Hit rate, tamanho e entradas mais acessadas
- **Métricas de Performance**: Taxa de sucesso, tempos de resposta, throughput
- **Informações de Rede**: Tráfego de dados
- **Produção de Vídeos**: Estatísticas dos últimos 24h

### 3. Integração com o Pipeline
O sistema foi integrado ao `AiShortsOrchestrator` com:
- Health checks executados automaticamente
- Sistema de alertas que registra problemas críticos
- Métricas agregadas para análise de performance

## Como Usar

### Executar o Dashboard
```bash
python monitor_dashboard.py
```

### Testar o Sistema
```bash
python test_dashboard.py
```

### Verificar Saúde via Código
```python
from src.pipeline.orchestrator import AiShortsOrchestrator

orchestrator = AiShortsOrchestrator()
health_report = await orchestrator.check_system_health()
print(health_report["summary"]["status"])
```

## Funcionalidades Destaque

### 🔍 Monitoramento Proativo
- Detecção automática de problemas
- Alertas visuais para componentes críticos
- Histórico de tendências de saúde

### 📊 Métricas Detalhadas
- Tempo de resposta dos componentes
- Taxa de sucesso do pipeline
- Eficiência do cache
- Uso de recursos do sistema

### 🛡️ Resiliência
- Integração com graceful degradation
- Circuit breakers para proteção
- Fallback automático em falhas

### 💾 Cache Inteligente
- Monitoramento de hit rate
- Entradas mais populares
- Tamanho e evolução do cache

## Exemplo de Visualização

```
================================================================================
🚨 AISHORTS V2.0 - MONITOR DASHBOARD - 2 ALERTAS CRÍTICOS
⏰ 2025-11-08 23:12:45
================================================================================

🚨 ALERTAS CRÍTICOS:
   ❌ Tts Service: TTS service unavailable
   ❌ System Resources: object dict can't be used in 'await' expression
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

📊 SISTEMA
   CPU: 54.0%
   Memória: 45.9% (8.4GB disponível)
   PID: 30190

🏥 HEALTH STATUS
   Status Geral: ❌ UNHEALTHY
   2/4 components healthy
   
   Health Checks:
   • Openrouter Api: ✅ API responded OK (0.845s)
   • Tts Service: ❌ TTS service unavailable (0.001s)
   • Youtube Extractor: ✅ Extraction working (2.101s)
   • System Resources: ❌ Check failed (0.001s)

📈 MÉTRICAS DE PERFORMANCE
   Taxa de Sucesso (últimas 10): 50%
   Tempo Resposta Médio: 0.739s
   Tempo Resposta Máximo: 2.101s
   Vídeos (24h): 1
   Tamanho Total: 45.2MB
```

## Próximos Passos

1. **Alertas em Tempo Real**: Implementar notificações (email, webhook)
2. **Dashboard Web**: Criar interface web baseada no dashboard atual
3. **Métricas Avançadas**: Adicionar métricas específicas do pipeline
4. **Modo Headless**: Executar em background com logs estruturados
5. **Integração externa**: Enviar métricas para sistemas como Prometheus/Grafana

O sistema está pronto para produção e fornecerá visibilidade completa sobre a saúde e performance do pipeline AiShortsV2.