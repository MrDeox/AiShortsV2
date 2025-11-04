# 🎬 Sistema de Sincronização Áudio-Vídeo - AiShorts v2.0

## 📋 Visão Geral

Sistema avançado de sincronização entre narração TTS (Kokoro) e conteúdo visual para criação automática de vídeos engajantes para plataformas como TikTok, YouTube Shorts e Instagram Reels.

## 🚀 Funcionalidades Principais

### ✨ AudioVideoSynchronizer
- **Sincronização Precisa**: Alinha automaticamente áudio TTS com segmentos de vídeo
- **Detecção de Beats**: Identifica pontos de sincronização baseados em análise espectral
- **Timeline Combinado**: Cria timeline detalhado com áudio e vídeo sincronizados
- **Compensação Automática**: Corrige gaps e overlaps automaticamente

### 🎨 TimingOptimizer
- **Otimização de Transições**: Aplica efeitos suaves entre segmentos
- **Cálculo de Duração Ideal**: Determina duração perfeita baseada no conteúdo textual
- **Predição de Engajamento**: Analisa e otimiza para máximo engajamento
- **Análise de Qualidade**: Gera métricas de sincronização e qualidade

## 🛠️ Instalação

```bash
# Instalar dependências do sistema de sincronização
pip install -r requirements_sync.txt

# Ou instalar individualmente
pip install librosa moviepy soundfile scipy torch torchaudio
```

## 📖 Guia de Uso

### 1. Uso Básico - Sincronização Simples

```python
from src.video.sync import AudioVideoSynchronizer, TimingOptimizer
from src.tts.kokoro_tts import KokoroTTSClient

# Inicializar componentes
tts = KokoroTTSClient()
synchronizer = AudioVideoSynchronizer()
optimizer = TimingOptimizer()

# Gerar áudio TTS
script = create_your_script()  # Sua função de criação de script
audio_result = tts.script_to_audio(script, "narracao")

# Definir segmentos de vídeo
video_segments = [
    {
        'video_path': 'segment1.mp4',
        'start_time': 0.0,
        'duration': 10.0,
        'description': 'Primeiro segmento'
    },
    {
        'video_path': 'segment2.mp4',
        'start_time': 10.0,
        'duration': 12.0,
        'description': 'Segundo segmento'
    }
]

# Sincronizar áudio com vídeo
sync_result = synchronizer.sync_audio_with_video(
    audio_path=audio_result['full_audio']['audio_path'],
    video_segments=video_segments,
    script_timing=audio_result
)

print(f"Sincronização: {sync_result['success']}")
print(f"Duração final: {sync_result['total_duration']:.1f}s")
```

### 2. Detecção de Beats

```python
# Detectar pontos de sincronização no áudio
beat_points = synchronizer.detect_beat_points('audio_file.wav')

print(f"Pontos de beat detectados: {len(beat_points)}")
for beat in beat_points[:10]:
    print(f"Beat: {beat:.2f}s")
```

### 3. Otimização de Transições

```python
# Otimizar transições para engajamento máximo
optimization = optimizer.optimize_transitions(
    video_segments=video_segments,
    audio_timing=audio_result
)

# Aplicar efeitos de transição
effects = optimizer.add_transition_effects(video_segments)

print(f"Efeitos aplicados: {effects['total_effects']}")
print(f"Variedade: {effects['effect_statistics']['unique_effects']}")
```

### 4. Cálculo de Duração Ideal

```python
# Calcular duração ideal para um segmento
duration_opt = optimizer.calculate_optimal_duration(
    segment_text="Seu texto aqui...",
    video_length=60.0  # Duração total do vídeo
)

print(f"Duração ideal: {duration_opt['final_duration']:.1f}s")
print(f"Precisão: {duration_opt['sync_precision']:.2f}")
```

## 📊 Estruturas de Dados

### AudioSegment
```python
@dataclass
class AudioSegment:
    start_time: float
    end_time: float
    duration: float
    audio_path: str
    text_content: str
    section_type: str
    beat_points: List[float] = None
```

### VideoSegment
```python
@dataclass
class VideoSegment:
    start_time: float
    end_time: float
    duration: float
    video_path: str
    description: str
    transition_in: str = "fade"
    transition_out: str = "fade"
```

### TimelineEntry
```python
@dataclass
class TimelineEntry:
    timestamp: float
    audio_segment: Optional[AudioSegment]
    video_segment: Optional[VideoSegment]
    sync_point: bool = False
    transition_effect: Optional[str] = None
```

## 🎯 Características Avançadas

### Beat Detection com Librosa
- **Onset Detection**: Identifica início de eventos musicais/falados
- **Beat Tracking**: Detecta batidas regulares
- **Spectral Analysis**: Análise espectral para pontos de sincronização
- **Filtro Inteligente**: Remove pontos muito próximos (< 200ms)

### Otimização de Transições
- **Efeitos Disponíveis**:
  - `fade`: Fade in/out suave
  - `slide_left/right`: Deslizamento lateral
  - `slide_up/down`: Deslizamento vertical
  - `zoom_in/out`: Zoom in/out dinâmico
  - `cross_dissolve`: Dissolução cruzada

### Compensação Automática
- **Gap Detection**: Identifica intervalos muito grandes (> 0.5s)
- **Overlap Resolution**: Corrige sobreposições de vídeo
- **Timing Adjustment**: Ajusta timing automaticamente
- **Quality Assurance**: Mantém precisão de sincronização

## 📈 Métricas de Qualidade

### Smoothness Score
- **Cálculo**: Baseado na consistência das durações dos segmentos
- **Range**: 0.0 - 1.0 (1.0 = máxima suavidade)
- **Fatores**: Variância das durações, transições aplicadas

### Sync Accuracy
- **Cálculo**: Precisão do alinhamento áudio-vídeo
- **Range**: 0.0 - 1.0 (1.0 = sincronização perfeita)
- **Considera**: Beats detectados, timing de seções

### Engagement Prediction
- **Algoritmo**: Baseado em variedade, suavidade, duração otimizada
- **Range**: 0.0 - 1.0 (1.0 = engajamento máximo)
- **Plataformas**: Otimizado para TikTok/Shorts/Reels

## 🎬 Demo e Testes

### Executar Demo Completa
```bash
cd src/video/sync
python demo_sync.py
```

### Demo de Beat Detection
```python
from src.video.sync.demo_sync import AudioVideoSyncDemo

demo = AudioVideoSyncDemo()
beat_result = demo.demo_beat_detection()
```

## 📁 Estrutura de Arquivos

```
src/video/sync/
├── __init__.py                     # Exports do módulo
├── audio_video_synchronizer.py    # Classe principal de sincronização
├── timing_optimizer.py            # Otimizador de timing e transições
└── demo_sync.py                   # Demo e exemplos de uso
```

## 🔧 Configuração Avançada

### Parâmetros do AudioVideoSynchronizer
```python
synchronizer = AudioVideoSynchronizer(
    output_dir="outputs/video/sync"
)

# Ajustar parâmetros de sincronização
synchronizer.beat_detection_threshold = 0.7
synchronizer.max_gap_compensation = 0.5
synchronizer.optimal_transition_duration = 0.3
```

### Parâmetros do TimingOptimizer
```python
optimizer = TimingOptimizer(
    output_dir="outputs/video/optimization"
)

# Ajustar configurações de otimização
optimizer.min_transition_duration = 0.2
optimizer.max_transition_duration = 1.0
optimizer.optimal_segment_duration = 8.0
optimizer.sync_precision_threshold = 0.05
```

## 🎯 Integração com Sistema TTS

### Formato de Script Timing
O sistema espera um formato específico de timing do TTS:

```python
script_timing = {
    'sections_count': 4,
    'total_duration': 45.0,
    'section_audio': [
        {
            'section_type': 'hook',
            'audio_path': 'section_1.wav',
            'duration': 10.5,
            'text': 'Texto da seção...'
        },
        # ... mais seções
    ],
    'full_audio': {
        'audio_path': 'completo.wav',
        'duration': 45.0
    }
}
```

## 🚨 Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'librosa'"
```bash
pip install librosa soundfile
```

### Erro: "Could not find a suitable video codec"
```bash
# Instalar codecs de vídeo
pip install imageio-ffmpeg
```

### Vídeos muito longos ou curtos
- Verificar configuração `optimal_segment_duration`
- Ajustar `beat_detection_threshold` para mais/menos sensibilidade
- Usar `calculate_optimal_duration` para timing ideal

### Qualidade de sincronização baixa
- Verificar se áudio e vídeo têm qualidade adequada
- Ajustar parâmetros de beat detection
- Usar segmentos de vídeo com duração similar ao texto

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Verificar logs detalhados em `outputs/logs/`
- Executar `demo_sync.py` para exemplos práticos
- Consultar métricas de qualidade geradas

---

**Sistema desenvolvido para AiShorts v2.0**  
*Sincronização perfeita entre narração e visual para máximo engajamento* 🎬✨