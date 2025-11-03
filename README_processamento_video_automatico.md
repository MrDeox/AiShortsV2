# Sistema de Processamento Automático de Vídeos

## Visão Geral

Sistema completo de processamento automático de vídeos para qualidade profissional, com foco na conversão para formato vertical 1080x1920 e otimização para plataformas de mídia social.

## Características Principais

### ✨ Funcionalidades Implementadas

1. **Processador Automático (AutomaticVideoProcessor)**
   - Conversão automática para formato vertical 1080x1920
   - Aplicação de filtros profissionais (sharpening, denoising, color correction)
   - Processamento em lote (batch processing)
   - Sistema de cache inteligente
   - Extração de frames para análise

2. **Analisador de Qualidade (VideoQualityAnalyzer)**
   - Análise completa de qualidade (brilho, nitidez, movimento, contraste, saturação)
   - Verificação de compatibilidade com plataformas (TikTok, Instagram Reels, YouTube Shorts, Facebook Reels)
   - Sugestões automáticas de melhoria
   - Relatórios detalhados de qualidade
   - Processamento em lote de análises

3. **Integração Avançada**
   - MoviePy para manipulação de vídeos
   - OpenCV para processamento de imagem
   - Threading para processamento paralelo
   - Sistema de cache com TTL
   - Logging detalhado

## Estrutura de Arquivos

```
src/video/processing/
├── __init__.py                     # Exports das classes principais
├── video_processor.py             # Classe base VideoProcessor
├── automatic_video_processor.py   # AutomaticVideoProcessor (NOVO)
└── video_quality_analyzer.py      # VideoQualityAnalyzer (NOVO)

demo_processamento_video_automatico.py  # Demonstração completa
```

## Classes Principais

### AutomaticVideoProcessor

```python
from src.video.processing import AutomaticVideoProcessor

processor = AutomaticVideoProcessor()

# Converter para formato vertical
vertical_video = processor.normalize_to_vertical("input.mp4")

# Melhorar qualidade
enhanced_video = processor.enhance_quality(vertical_video)

# Processar segmento específico
segment = processor.process_video_segment(
    enhanced_video, 
    target_duration=30.0, 
    start_time=10.0
)

# Processar múltiplos vídeos em lote
batch_results = processor.batch_process_videos(
    ["video1.mp4", "video2.mp4"], 
    operations=['normalize_to_vertical', 'enhance_quality']
)

# Extrair frames para análise
frames = processor.extract_frames_for_analysis("video.mp4", num_frames=5)

# Obter estatísticas
stats = processor.get_processing_stats()
```

### VideoQualityAnalyzer

```python
from src.video.processing import VideoQualityAnalyzer

analyzer = VideoQualityAnalyzer()

# Analisar qualidade
metrics = analyzer.analyze_video_quality("video.mp4")
print(f"Qualidade: {metrics.overall_score}/100")

# Verificar compatibilidade com plataforma
compatibility = analyzer.check_platform_compatibility("video.mp4", "tiktok")
print(f"Compatibilidade TikTok: {compatibility['overall_compatibility']:.1f}%")

# Gerar sugestões de melhoria
suggestions = analyzer.suggest_improvements("video.mp4")

# Gerar relatório completo
analyzer.generate_quality_report("video.mp4", "report.json")

# Análise em lote
batch_analysis = analyzer.batch_analyze_quality(["video1.mp4", "video2.mp4"])
```

## Filtros de Qualidade Implementados

### 1. Redução de Ruído (Denoising)
- **Algoritmo**: `cv2.fastNlMeansDenoisingColored`
- **Benefício**: Remove ruído mantendo detalhes importantes
- **Impacto**: Alto - melhora significativamente a qualidade visual

### 2. Sharpening
- **Kernel**: Matriz de convolução personalizada para realce de bordas
- **Benefício**: Aumenta nitidez e definição
- **Impacto**: Alto - essencial para vídeos profissionais

### 3. Ajuste de Contraste e Brilho
- **Contraste**: Multiplicador alpha = 1.1
- **Bilho**: Adição beta = 10
- **Benefício**: Melhora a visibilidade e impacto visual
- **Impacto**: Médio - ajusta exposição

### 4. Melhoria de Cor
- **Conversão**: RGB ↔ BGR para processamento
- **Benefício**: Cores mais vibrantes e naturais
- **Impacto**: Médio - melhora o apelo visual

## Requisitos por Plataforma

### TikTok
- **Resolução**: 720x1280 a 1080x1920
- **FPS**: 24-60
- **Duração máxima**: 10 minutos
- **Tamanho máximo**: 287MB
- **Aspect Ratios**: 9:16, 1:1

### Instagram Reels
- **Resolução**: 720x1280 a 1080x1920
- **FPS**: 24-60
- **Duração máxima**: 90 segundos
- **Tamanho máximo**: 4GB
- **Aspect Ratios**: 9:16, 1:1

### YouTube Shorts
- **Resolução**: 720x1280 a 1080x1920
- **FPS**: 24-60
- **Duração máxima**: 60 segundos
- **Tamanho máximo**: 256MB
- **Aspect Ratios**: 9:16, 1:1, 16:9

### Facebook Reels
- **Resolução**: 720x1280 a 1080x1920
- **FPS**: 24-60
- **Duração máxima**: 60 segundos
- **Tamanho máximo**: 4GB
- **Aspect Ratios**: 9:16, 1:1

## Sistema de Cache

### Características
- **Localização**: `cache/processed_videos/`
- **TTL**: 24 horas (configurável)
- **Chave**: Hash MD5 do arquivo + parâmetros
- **Formato**: JSON com metadados

### Benefícios
- Evita reprocessamento desnecessário
- Acelera workflows repetitivos
- Reduz uso de CPU/GPU
- Gerenciamento automático de limpeza

## Métricas de Qualidade

### Brilho (Brightness)
- **Faixa**: 0.0 - 1.0
- **Ideal**: 0.3 - 0.8
- **Método**: Média dos pixels normalizada

### Nitidez (Sharpness)
- **Faixa**: 0.0 - 1.0+
- **Ideal**: > 0.6
- **Método**: Variância do Laplaciano

### Movimento (Motion Level)
- **Faixa**: 0.0 - 1.0+
- **Ideal**: Variável por conteúdo
- **Método**: Diferença entre frames consecutivos

### Contraste (Contrast)
- **Faixa**: 0.0 - 1.0+
- **Ideal**: 0.4 - 0.8
- **Método**: Desvio padrão dos pixels

### Saturação (Color Saturation)
- **Faixa**: 0.0 - 1.0
- **Ideal**: 0.4 - 0.9
- **Método**: Média do canal S em HSV

### Ruído (Noise Level)
- **Faixa**: 0.0 - 1.0
- **Ideal**: < 0.3
- **Método**: Densidade de bordas detectadas

## Como Executar a Demonstração

```bash
# Executar demonstração completa
python demo_processamento_video_automatico.py

# A demonstração inclui:
# 1. Processamento automático completo
# 2. Análise de qualidade
# 3. Verificação de compatibilidade com plataformas
# 4. Processamento em lote
# 5. Geração de relatórios
# 6. Estatísticas de performance
```

## Configuração

### Arquivo `config/video_settings.py`

```python
# Configurações de processamento automático
VIDEO_PROCESSING = {
    'output_resolution': (1920, 1080),
    'output_fps': 30,
    'codec': 'libx264',
    'audio_codec': 'aac',
    'max_workers': 4,
}

# Cache settings
CACHE_SETTINGS = {
    'enabled': True,
    'ttl': 3600 * 24,  # 24 horas
    'max_cache_size': 1024 * 1024 * 1024,  # 1GB
}
```

## Performance

### Benchmarks Esperados
- **Processamento por vídeo**: 10-30 segundos
- **Taxa de cache hit**: 70-90% (após primeiro uso)
- **Throughput**: 120-360 vídeos/hora
- **Uso de memória**: ~200-500MB por vídeo processado

### Otimizações Implementadas
- Processamento paralelo com ThreadPoolExecutor
- Cache inteligente com validação TTL
- Liberação automática de recursos
- Compressão otimizada de saída

## Tratamento de Erros

### Estratégias
- **Fallback graceful**: Continua processamento mesmo com falhas parciais
- **Logging detalhado**: Rastreamento completo de erros
- **Validação de entrada**: Verificação prévia de arquivos
- **Recuperação automática**: Retry para operações falhas

### Casos Tratados
- Arquivos de vídeo corrompidos ou inválidos
- Falhas de codec ou formato incompatível
- Problemas de memória ou disco
- Interrupções de rede (para downloads)

## Extensibilidade

### Adicionando Novas Plataformas
```python
# No VideoQualityAnalyzer.__init__()
self.platform_requirements['nova_plataforma'] = PlatformRequirements(
    name='Nova Plataforma',
    min_resolution=(720, 1280),
    max_resolution=(1080, 1920),
    min_fps=24,
    max_fps=60,
    max_duration=60.0,
    aspect_ratios=['9:16'],
    max_file_size=256 * 1024 * 1024
)
```

### Adicionando Novos Filtros
```python
# No AutomaticVideoProcessor._apply_professional_filters()
def apply_novo_filtro(frame):
    # Implementar filtro personalizado
    return frame_processed
```

## Requisitos do Sistema

### Bibliotecas Python
- `opencv-python>=4.5.0`
- `moviepy>=1.0.3`
- `Pillow>=8.0.0`
- `numpy>=1.20.0`

### Recursos de Sistema
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **CPU**: Multi-core recomendado para batch processing
- **Disco**: Espaço para cache (até 1GB configurável)
- **GPU**: Opcional, acelera processamento com CUDA

## Conclusão

O sistema implementado fornece uma solução completa e profissional para processamento automático de vídeos, com foco em:

1. **Qualidade**: Filtros avançados para qualidade broadcast
2. **Eficiência**: Cache inteligente e processamento paralelo
3. **Compatibilidade**: Otimização para todas as principais plataformas
4. **Automação**: Processamento em lote sem intervenção manual
5. **Análise**: Métricas detalhadas e sugestões de melhoria

O sistema está pronto para uso em produção e pode ser facilmente extensível para novas plataformas e funcionalidades.