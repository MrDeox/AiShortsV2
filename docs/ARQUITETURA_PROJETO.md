# Arquitetura do Projeto AiShorts v2.0

**Projeto:** Pipeline Automatizado para Criação de Vídeos Curtos  
**Versão:** 2.0.0  
**Marca:** Aithur  
**Data:** 2025-11-04

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura de Diretórios](#estrutura-de-diretórios)
3. [Módulos Principais](#módulos-principais)
4. [Fluxo de Execução](#fluxo-de-execução)
5. [Componentes-Chave](#componentes-chave)
6. [Padrões Arquiteturais](#padrões-arquiteturais)
7. [Pipeline de Processamento](#pipeline-de-processamento)

---

## 🎯 Visão Geral

O AiShorts v2.0 é um sistema modular completo para geração automatizada de vídeos curtos virais, desde a concepção do tema até o vídeo final otimizado para múltiplas plataformas (TikTok, YouTube Shorts, Instagram Reels).

### Objetivo Principal
Automatizar completamente o processo de criação de conteúdo de vídeos curtos usando IA, eliminando trabalho manual e maximizando engajamento.

### Tecnologias Core
- **Python 3.9+** - Linguagem principal
- **OpenRouter API** - Geração de conteúdo via IA (nvidia/nemotron-nano-9b-v2)
- **MoviePy** - Edição de vídeo
- **CLIP Model** - Matching de conteúdo visual
- **Kokoro TTS** - Text-to-Speech
- **Pydantic** - Validação de dados
- **Loguru** - Sistema de logging

---

## 📁 Estrutura de Diretórios

```
aishorts-v2/
│
├── 📂 src/                           # Código fonte principal
│   ├── 📂 core/                      # Infraestrutura central
│   │   ├── __init__.py
│   │   └── openrouter_client.py      # Cliente OpenRouter com rate limiting
│   │
│   ├── 📂 generators/                # Geradores de conteúdo
│   │   ├── __init__.py
│   │   ├── theme_generator.py        # Geração de temas de curiosidades
│   │   ├── script_generator.py       # Geração de roteiros virais
│   │   └── prompt_engineering.py     # Engenharia de prompts
│   │
│   ├── 📂 video/                     # Pipeline completo de vídeo
│   │   ├── __init__.py
│   │   │
│   │   ├── 📂 extractors/            # Extração de conteúdo
│   │   │   ├── __init__.py
│   │   │   ├── youtube_extractor.py  # Extração de vídeos do YouTube
│   │   │   └── segment_processor.py  # Processamento de segmentos
│   │   │
│   │   ├── 📂 matching/              # Matching de conteúdo visual
│   │   │   ├── __init__.py
│   │   │   ├── content_matcher.py    # CLIP-based visual matching
│   │   │   ├── semantic_analyzer.py  # Análise semântica de conteúdo
│   │   │   ├── clip_relevance_scorer.py  # Scoring de relevância
│   │   │   └── video_searcher.py     # Busca de vídeos relevantes
│   │   │
│   │   ├── 📂 processing/            # Processamento de vídeo
│   │   │   ├── __init__.py
│   │   │   ├── automatic_video_processor.py  # Processamento automático
│   │   │   ├── video_processor.py    # Processamento base
│   │   │   ├── platform_optimizer.py # Otimização para plataformas
│   │   │   └── video_quality_analyzer.py  # Análise de qualidade
│   │   │
│   │   ├── 📂 sync/                  # Sincronização áudio-vídeo
│   │   │   ├── __init__.py
│   │   │   ├── audio_video_synchronizer.py  # Sincronização principal
│   │   │   └── timing_optimizer.py   # Otimização de timing
│   │   │
│   │   └── 📂 generators/            # Geração de vídeo final
│   │       ├── __init__.py
│   │       ├── final_video_composer.py  # Compositor final
│   │       ├── premium_template_engine.py  # Engine de templates
│   │       ├── visual_templates.py   # Templates visuais
│   │       └── video_generator.py    # Gerador base
│   │
│   ├── 📂 tts/                       # Text-to-Speech
│   │   └── kokoro_tts.py             # Integração Kokoro TTS
│   │
│   ├── 📂 config/                    # Configurações
│   │   ├── __init__.py
│   │   ├── settings.py               # Configurações principais (Pydantic)
│   │   ├── logging_config.py         # Sistema de logging
│   │   └── video_platforms.py        # Configurações de plataformas
│   │
│   ├── 📂 models/                    # Modelos de dados
│   │   ├── __init__.py
│   │   └── script_models.py          # Modelos para roteiros
│   │
│   ├── 📂 validators/                # Validadores
│   │   ├── __init__.py
│   │   └── script_validator.py       # Validação de roteiros
│   │
│   ├── 📂 utils/                     # Utilitários
│   │   ├── __init__.py
│   │   └── exceptions.py             # Sistema de exceções customizadas
│   │
│   └── __init__.py
│
├── 📂 scripts/                       # Scripts de demonstração e testes
│   ├── demo_completo_fase1.py        # Demo completo Fase 1
│   ├── demo_completo_fase2.py        # Demo completo Fase 2
│   ├── demo_pipeline_simples.py      # Demo pipeline simplificado
│   ├── demo_final_composer.py        # Demo compositor final
│   └── ...
│
├── 📂 tests/                         # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py                   # Configuração pytest
│   ├── test_basic.py                 # Testes básicos
│   ├── test_integration.py           # Testes de integração
│   ├── test_script_generator.py      # Testes de gerador de roteiro
│   ├── test_kokoro_tts.py            # Testes TTS
│   └── 📂 test_video/                # Testes de vídeo
│       ├── test_extractors.py
│       ├── test_matching.py
│       ├── test_platforms.py
│       └── ...
│
├── 📂 docs/                          # Documentação
│   ├── ARQUITETURA_PROJETO.md        # Este arquivo
│   ├── RESUMO_EXECUTIVO_FASE1.md
│   ├── content_matching_strategies.md
│   ├── youtube_extraction_guide.md
│   └── ...
│
├── 📂 outputs/                       # Saídas geradas
│   ├── 📂 audio/                     # Arquivos de áudio (TTS)
│   ├── 📂 video/                     # Vídeos processados
│   │   ├── 📂 final_videos/          # Vídeos finais
│   │   ├── 📂 optimization/          # Vídeos otimizados
│   │   └── 📂 sync/                  # Vídeos sincronizados
│   └── 📂 demo_fase2/                # Outputs de demos
│
├── 📂 config/                        # Configurações globais
│   ├── __init__.py
│   └── video_settings.py             # Configurações de vídeo
│
├── 📂 data/                          # Dados do projeto
│   └── 📂 output/                    # Saídas gerais
│
├── 📂 browser/                       # Automação de browser
│   ├── global_browser.py
│   └── 📂 browser_extension/         # Extensão para captura de erros
│
├── 📂 backups/                       # Backups do workspace
├── 📂 archive/                       # Arquivos arquivados
│
├── requirements.txt                  # Dependências Python
├── setup.py                          # Setup do projeto
├── README.md                         # Documentação principal
└── .env.example                      # Template de variáveis de ambiente
```

---

## 🧩 Módulos Principais

### 1. **Core (`src/core/`)**

#### `openrouter_client.py`
**Propósito:** Cliente robusto para integração com OpenRouter API

**Responsabilidades:**
- Gerenciamento de requisições HTTP à API OpenRouter
- Rate limiting inteligente (20 req/min)
- Sistema de retry com backoff exponencial
- Validação e parsing de respostas
- Métricas de uso (tokens, tempo de resposta)

**Classes principais:**
- `OpenRouterClient`: Cliente principal
- `RateLimiter`: Controle de rate limit
- `OpenRouterResponse`: Estrutura de resposta

---

### 2. **Generators (`src/generators/`)**

#### `theme_generator.py`
**Propósito:** Geração de temas de curiosidades usando IA

**Responsabilidades:**
- Geração de temas virais em categorias específicas
- Validação de qualidade de temas
- Sistema de categorização (science, history, nature, etc.)
- Métricas de viralidade

**Classes principais:**
- `ThemeGenerator`: Gerador principal
- `GeneratedTheme`: Modelo de tema gerado
- `ThemeCategory`: Enum de categorias

#### `script_generator.py`
**Propósito:** Transformação de temas em roteiros otimizados para vídeos curtos

**Responsabilidades:**
- Geração de roteiros estruturados (Hook, Desenvolvimento, Conclusão)
- Otimização para plataformas específicas (TikTok, Shorts, Reels)
- Cálculo de métricas de qualidade, engajamento e retenção
- Validação de duração e estrutura

**Classes principais:**
- `ScriptGenerator`: Gerador de roteiros
- `GeneratedScript`: Roteiro completo
- `ScriptSection`: Seção individual do roteiro (Hook/Dev/Conclusion)
- `ScriptGenerationResult`: Resultado com múltiplos roteiros

**Estrutura de Roteiro:**
```
HOOK (3-5s)        → Prender atenção imediatamente
DESENVOLVIMENTO    → Explicação envolvente (40-50s)
CONCLUSÃO/CTA      → Call-to-action sutil (5-10s)
```

#### `prompt_engineering.py`
**Propósito:** Engenharia de prompts otimizados para cada tipo de geração

---

### 3. **Video Pipeline (`src/video/`)**

Este é o módulo mais complexo, dividido em 4 sub-módulos:

#### 3.1 **Extractors (`src/video/extractors/`)**

##### `youtube_extractor.py`
**Propósito:** Extração de vídeos do YouTube para uso como B-roll

**Responsabilidades:**
- Download de vídeos do YouTube (yt-dlp)
- Extração de segmentos específicos
- Conversão para formato otimizado
- Cache de vídeos baixados

##### `segment_processor.py`
**Propósito:** Processamento de segmentos de vídeo

**Responsabilidades:**
- Corte de segmentos em duração específica
- Análise de qualidade de segmentos
- Detecção de cenas

---

#### 3.2 **Matching (`src/video/matching/`)**

##### `content_matcher.py`
**Propósito:** Matching de conteúdo visual usando modelo CLIP

**Responsabilidades:**
- Extração de features visuais com CLIP
- Cálculo de similaridade entre imagens/vídeos
- Ranking de relevância de conteúdo
- Cache de embeddings

**Algoritmo:**
1. Extrai features visuais com CLIP (ViT-B-32)
2. Compara embeddings usando cosine similarity
3. Rankeia matches por relevância
4. Filtra por threshold de similaridade

##### `semantic_analyzer.py`
**Propósito:** Análise semântica de texto e vídeo

**Responsabilidades:**
- Análise de contexto do roteiro
- Matching entre texto e conteúdo visual
- Extração de keywords relevantes

##### `clip_relevance_scorer.py`
**Propósito:** Sistema de scoring de relevância CLIP-based

##### `video_searcher.py`
**Propósito:** Busca de vídeos relevantes para matching

---

#### 3.3 **Processing (`src/video/processing/`)**

##### `automatic_video_processor.py`
**Propósito:** Processamento automático de vídeos para qualidade profissional

**Responsabilidades:**
- Conversão para formato vertical (1080x1920)
- Aplicação de filtros de qualidade (sharpening, denoising, color correction)
- Batch processing de múltiplos vídeos
- Sistema de cache inteligente
- Otimização para diferentes plataformas

**Perfil Vertical:**
- Resolução: 1080x1920 (9:16)
- FPS: 30
- Video Bitrate: 4000k
- Audio Bitrate: 192k

##### `platform_optimizer.py`
**Propósito:** Otimização específica para cada plataforma social

**Responsabilidades:**
- TikTok: Vertical 9:16, 15-60s, max 287MB
- YouTube Shorts: Vertical 9:16, até 60s
- Instagram Reels: Vertical 9:16, até 90s
- Ajustes de bitrate, codec, metadata

##### `video_quality_analyzer.py`
**Propósito:** Análise automática de qualidade de vídeo

**Responsabilidades:**
- Análise de resolução e sharpness
- Detecção de artefatos de compressão
- Métricas de qualidade visual
- Validação de compliance com plataformas

---

#### 3.4 **Sync (`src/video/sync/`)**

##### `audio_video_synchronizer.py`
**Propósito:** Sincronização precisa de áudio e vídeo

**Responsabilidades:**
- Sincronização de narração TTS com vídeo
- Alinhamento temporal de segmentos
- Ajuste de velocidade de vídeo para match com áudio
- Transições suaves entre segmentos

**Algoritmo:**
1. Analisa duração do áudio (TTS)
2. Calcula duração necessária de vídeo para cada seção
3. Ajusta velocidade de clips (0.8x - 1.2x)
4. Aplica crossfade entre segmentos
5. Valida sincronização final

##### `timing_optimizer.py`
**Propósito:** Otimização de timing e pacing do vídeo

---

#### 3.5 **Generators (`src/video/generators/`)**

##### `final_video_composer.py`
**Propósito:** Composição final de vídeos de alta qualidade

**Responsabilidades:**
- Pipeline de composição profissional
- Sistema de templates avançado
- Aplicação de efeitos visuais
- Geração de thumbnails
- Export otimizado para múltiplas plataformas
- Métricas de qualidade e analytics

**Classes principais:**
- `FinalVideoComposer`: Compositor principal
- `VideoQuality`: Enum de níveis de qualidade (HIGH/MEDIUM/LOW)
- `PlatformType`: Enum de plataformas suportadas
- `TemplateConfig`: Configuração de templates
- `QualityMetrics`: Métricas de qualidade

##### `premium_template_engine.py`
**Propósito:** Engine de templates premium para vídeos

**Responsabilidades:**
- Templates customizáveis
- Branding automático
- Efeitos de transição profissionais

##### `visual_templates.py`
**Propósito:** Biblioteca de templates visuais

##### `video_generator.py`
**Propósito:** Gerador base de vídeo

---

### 4. **TTS (`src/tts/`)**

#### `kokoro_tts.py`
**Propósito:** Integração com Kokoro TTS para narração

**Responsabilidades:**
- Conversão de texto para fala
- Ajuste de prosódia e emoção
- Geração de áudio para cada seção do roteiro
- Export em formato otimizado

---

### 5. **Config (`src/config/`)**

#### `settings.py`
**Propósito:** Sistema centralizado de configurações usando Pydantic

**Classes de configuração:**
- `OpenRouterSettings`: API key, model, tokens, temperature
- `LoggingSettings`: Níveis de log, formato, rotação
- `ThemeGeneratorSettings`: Categorias, max attempts
- `ScriptGeneratorSettings`: Duração alvo, plataformas, qualidade mínima
- `RetrySettings`: Max retries, delay, rate limiting
- `StorageSettings`: Diretórios de output/temp/cache
- `ProjectSettings`: Environment, version, debug

**Instância global:**
```python
config = AiShortsConfig()
```

#### `logging_config.py`
**Propósito:** Configuração do sistema de logging estruturado (Loguru)

#### `video_platforms.py`
**Propósito:** Configurações específicas de cada plataforma

---

### 6. **Models (`src/models/`)**

#### `script_models.py`
**Propósito:** Modelos de dados para roteiros (Pydantic)

---

### 7. **Validators (`src/validators/`)**

#### `script_validator.py`
**Propósito:** Validação de roteiros gerados

**Validações:**
- Estrutura completa (Hook, Dev, Conclusion)
- Duração dentro dos limites
- Qualidade mínima de conteúdo
- Compliance com plataforma

---

### 8. **Utils (`src/utils/`)**

#### `exceptions.py`
**Propósito:** Sistema de exceções customizadas

**Classes:**
- `OpenRouterError`: Erros da API OpenRouter
- `RateLimitError`: Rate limit excedido
- `ScriptGenerationError`: Erros na geração de roteiro
- `ValidationError`: Erros de validação
- `ErrorHandler`: Handler centralizado com retry

---

## 🔄 Fluxo de Execução

### Pipeline Completo (Fase 1 + Fase 2)

```
┌─────────────────────────────────────────────────────────────────┐
│                     PIPELINE AISHORTS v2.0                       │
└─────────────────────────────────────────────────────────────────┘

1. GERAÇÃO DE CONTEÚDO
   ┌──────────────┐
   │ Tema (IA)    │ → ThemeGenerator
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Roteiro (IA) │ → ScriptGenerator
   └──────┬───────┘   - Hook (3-5s)
          │           - Development (40-50s)
          │           - Conclusion (5-10s)
          │
          ▼
2. GERAÇÃO DE ÁUDIO
   ┌──────────────┐
   │ TTS (Kokoro) │ → Narração para cada seção
   └──────┬───────┘
          │
          ▼
3. AQUISIÇÃO DE VÍDEO B-ROLL
   ┌──────────────────┐
   │ YouTube Extractor│ → Download de vídeos relevantes
   └──────┬───────────┘
          │
          ▼
4. MATCHING DE CONTEÚDO
   ┌──────────────────┐
   │ Content Matcher  │ → CLIP-based visual matching
   │ (CLIP Model)     │   - Análise semântica
   └──────┬───────────┘   - Ranking de relevância
          │
          ▼
5. PROCESSAMENTO DE VÍDEO
   ┌─────────────────────┐
   │ Automatic Processor │ → Conversão vertical 1080x1920
   │                     │   - Filtros de qualidade
   └──────┬──────────────┘   - Batch processing
          │
          ▼
6. SINCRONIZAÇÃO
   ┌─────────────────────┐
   │ Audio-Video Sync    │ → Sincronização precisa
   │                     │   - Timing optimization
   └──────┬──────────────┘   - Transições
          │
          ▼
7. COMPOSIÇÃO FINAL
   ┌─────────────────────┐
   │ Final Composer      │ → Templates premium
   │                     │   - Efeitos visuais
   └──────┬──────────────┘   - Branding
          │
          ▼
8. OTIMIZAÇÃO MULTI-PLATAFORMA
   ┌─────────────────────┐
   │ Platform Optimizer  │ → TikTok
   │                     │   YouTube Shorts
   └──────┬──────────────┘   Instagram Reels
          │
          ▼
   ┌─────────────────────┐
   │  VÍDEO FINAL PRONTO │
   │  PARA UPLOAD        │
   └─────────────────────┘
```

### Fluxo Detalhado por Fase

#### **Fase 1: Geração de Conteúdo**
```
ThemeGenerator.generate_single_theme()
    ↓
ScriptGenerator.generate_single_script(theme)
    ↓
KokoroTTS.generate_audio(script.sections)
    ↓
Output: Roteiro estruturado + Áudios por seção
```

#### **Fase 2: Geração de Vídeo**
```
YouTubeExtractor.download_video(query)
    ↓
ContentMatcher.match_content(script, videos)
    ↓
AutomaticVideoProcessor.process_batch(videos)
    ↓
AudioVideoSynchronizer.sync(audio, video_clips)
    ↓
FinalVideoComposer.compose(synced_video, template)
    ↓
PlatformOptimizer.optimize_for_platform(video, platform)
    ↓
Output: Vídeo final otimizado para cada plataforma
```

---

## 🔑 Componentes-Chave

### 1. OpenRouterClient
**Localização:** `src/core/openrouter_client.py`

**Função:** Hub de integração com IA para geração de conteúdo

**Features:**
- Rate limiting automático (20 req/min)
- Retry com backoff exponencial
- Métricas de uso (tokens, tempo)
- Validação de respostas

**Uso:**
```python
from src.core.openrouter_client import openrouter_client

response = openrouter_client.generate_content(
    prompt="Crie um tema sobre ciência",
    system_message="Você é um especialista em curiosidades",
    max_tokens=150,
    temperature=0.7
)
```

---

### 2. ScriptGenerator
**Localização:** `src/generators/script_generator.py`

**Função:** Transformar temas em roteiros virais estruturados

**Algoritmo de Qualidade:**
```
overall_quality = (structure_score * 0.4 + 
                  engagement_score * 0.3 + 
                  retention_score * 0.3)
```

**Métricas:**
- Structure Score: Validação de hook, desenvolvimento, conclusão
- Engagement Score: Análise do hook (palavras-chave, perguntas)
- Retention Score: Duração ideal (45-75s), distribuição de tempo

---

### 3. ContentMatcher (CLIP)
**Localização:** `src/video/matching/content_matcher.py`

**Função:** Matching inteligente de conteúdo visual usando IA

**Modelo:** CLIP ViT-B-32

**Pipeline:**
1. Extração de features visuais (512-dim embeddings)
2. Cálculo de similaridade cosine
3. Ranking por relevância
4. Filtragem por threshold (default: 0.8)

**Cache:** Embeddings são cached para otimização

---

### 4. AutomaticVideoProcessor
**Localização:** `src/video/processing/automatic_video_processor.py`

**Função:** Processamento profissional de vídeo em lote

**Features:**
- Conversão para vertical 1080x1920 (9:16)
- Filtros: sharpening, denoising, color correction
- Batch processing paralelo
- Cache TTL 24h
- Thread-safe

**Profile Vertical:**
```python
{
    'width': 1080,
    'height': 1920,
    'fps': 30,
    'video_bitrate': '4000k',
    'audio_bitrate': '192k'
}
```

---

### 5. FinalVideoComposer
**Localização:** `src/video/generators/final_video_composer.py`

**Função:** Compositor final de vídeos de alta qualidade

**Features:**
- Templates premium customizáveis
- Efeitos de transição profissionais
- Sistema de branding automático
- Geração de thumbnails
- Export multi-formato
- Métricas de qualidade

**Quality Levels:**
- HIGH: 1080p, alta bitrate
- MEDIUM: 720p, média bitrate
- LOW: 480p, baixa bitrate

---

### 6. AudioVideoSynchronizer
**Localização:** `src/video/sync/audio_video_synchronizer.py`

**Função:** Sincronização precisa de áudio e vídeo

**Algoritmo:**
1. Analisa duração do áudio TTS
2. Mapeia segmentos de vídeo para seções de roteiro
3. Ajusta velocidade de vídeo (0.8x - 1.2x) para match
4. Aplica crossfade entre clips (0.5s)
5. Valida sincronização (tolerance: 0.1s)

**Validações:**
- Duração total match com áudio
- Sem gaps ou overlaps
- Transições suaves

---

## 🏗️ Padrões Arquiteturais

### 1. **Modularidade**
Cada componente é independente e pode ser testado isoladamente.

```
Generators ──┐
Processors ──┼── Independentes, comunicação via interfaces
Matchers  ──┘
```

### 2. **Separation of Concerns**
```
Config        → Configurações centralizadas
Core          → Infraestrutura (API clients)
Generators    → Lógica de negócio (geração)
Video         → Pipeline de vídeo
Utils         → Utilitários compartilhados
```

### 3. **Error Handling Robusto**
```python
try:
    # Operação
except SpecificError:
    # Tratamento específico
    logger.error()
    raise CustomException()
```

Sistema de retry automático:
```python
ErrorHandler.retry_with_backoff(
    operation,
    max_retries=3,
    delay=1.0
)
```

### 4. **Logging Estruturado**
```python
from loguru import logger

logger.info("Operação iniciada", extra={
    "module": "script_generator",
    "theme": theme.content,
    "quality": quality_score
})
```

### 5. **Validação com Pydantic**
```python
class OpenRouterSettings(BaseSettings):
    api_key: Optional[str] = Field(default=None)
    model: str = Field(default="nvidia/nemotron-nano-9b-v2:free")
    temperature: float = Field(default=0.7)
```

### 6. **Dependency Injection**
```python
class ScriptGenerator:
    def __init__(self):
        self.config = config.script_gen
        self.openrouter = openrouter_client  # Injected
```

### 7. **Factory Pattern**
Usado em generators para criar objetos complexos:
```python
ScriptGenerator.generate_single_script(theme) → GeneratedScript
```

### 8. **Strategy Pattern**
PlatformOptimizer usa diferentes estratégias por plataforma:
```python
optimizer.optimize_for_platform(video, "tiktok")
optimizer.optimize_for_platform(video, "shorts")
```

---

## 🎬 Pipeline de Processamento

### Entry Points

#### 1. **Demo Completo Fase 1**
**Script:** `scripts/demo_completo_fase1.py`

**Fluxo:**
```
ThemeGenerator → ScriptGenerator → KokoroTTS → Output (roteiro + áudios)
```

#### 2. **Demo Completo Fase 2**
**Script:** `scripts/demo_completo_fase2.py`

**Fluxo:**
```
Load Roteiro → YouTubeExtractor → ContentMatcher → 
AutomaticProcessor → Synchronizer → FinalComposer → 
PlatformOptimizer → Output (vídeos finais)
```

#### 3. **Demo Pipeline Simples**
**Script:** `scripts/demo_pipeline_simples.py`

**Fluxo:** Pipeline end-to-end simplificado

---

### Data Flow

```
┌─────────────┐
│  User Input │ (categoria de tema)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ GeneratedTheme  │ {content, category, quality_score}
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ GeneratedScript  │ {sections[], quality_score, engagement}
└──────┬───────────┘
       │
       ▼
┌──────────────┐
│ TTS Audio    │ {section_1.wav, section_2.wav, ...}
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│ Video B-rolls   │ [video1.mp4, video2.mp4, ...]
└──────┬──────────┘
       │
       ▼
┌─────────────────────┐
│ Matched Segments    │ {video_clip → script_section}
└──────┬──────────────┘
       │
       ▼
┌──────────────────────┐
│ Processed Videos     │ 1080x1920, filtered, optimized
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Synchronized Video   │ audio + video perfeitamente sincronizados
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Final Composition    │ templates, efeitos, branding
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Platform Exports     │ tiktok.mp4, shorts.mp4, reels.mp4
└──────────────────────┘
```

---

### State Management

**Arquivos intermediários salvos em:**
- `outputs/audio/` - Áudios TTS gerados
- `outputs/video/sync/` - Vídeos sincronizados
- `outputs/video/optimization/` - Vídeos otimizados
- `outputs/video/final_videos/` - Vídeos finais

**Metadata:**
Cada etapa salva JSON com metadados:
```json
{
  "timestamp": "2025-11-04T09:00:00",
  "theme": "...",
  "quality_score": 0.85,
  "processing_time": 45.2,
  "metrics": {...}
}
```

---

## 📊 Métricas e Qualidade

### Script Quality Metrics
```python
{
    "structure_score": 0.9,      # Validação estrutural
    "engagement_score": 0.85,    # Potencial de engajamento
    "retention_score": 0.88,     # Potencial de retenção
    "overall_quality": 0.87      # Score geral ponderado
}
```

### Video Quality Metrics
```python
{
    "resolution_score": 1.0,          # 1080x1920 = perfeito
    "audio_sync_score": 0.95,         # Precisão de sync
    "visual_clarity_score": 0.88,     # Qualidade visual
    "compression_efficiency": 0.92,    # Otimização de tamanho
    "engagement_potential": 0.86,      # Potencial viral
    "platform_compliance": True,       # Compliance com plataforma
    "overall_score": 0.91             # Score geral
}
```

---

## 🔐 Segurança e Performance

### Rate Limiting
- OpenRouter: 20 requests/minuto
- Retry automático com backoff

### Caching
- Embeddings CLIP cached
- Vídeos processados cached (TTL: 24h)
- Themes e scripts salvos em JSON

### Parallelization
- Batch processing de vídeos (ThreadPoolExecutor)
- Max workers configurável (default: 4)

### Error Recovery
- Retry automático em erros transientes
- Fallback para parse simples se estrutura não for detectada
- Validação flexível em modo teste

---

## 🚀 Próximas Melhorias

1. **Cache Distribuído:** Redis para embeddings compartilhados
2. **Queue System:** Celery para processamento assíncrono
3. **API REST:** Expor pipeline como serviço
4. **Dashboard:** Monitoramento de métricas em tempo real
5. **A/B Testing:** Testar diferentes templates e estratégias
6. **Auto-Posting:** Integração com APIs de plataformas para upload automático

---

## 📝 Conclusão

O AiShorts v2.0 é uma arquitetura modular, escalável e robusta que automatiza completamente o processo de criação de vídeos curtos virais. Cada componente é independente, testável e otimizado para performance.

**Princípios fundamentais:**
✅ Modularidade  
✅ Separation of Concerns  
✅ Error Handling robusto  
✅ Logging estruturado  
✅ Validação em todas as camadas  
✅ Otimização de performance  
✅ Cache inteligente  
✅ Métricas de qualidade

---

**Documentação gerada em:** 2025-11-04  
**Versão do Projeto:** 2.0.0  
**Status:** ✅ Produção
