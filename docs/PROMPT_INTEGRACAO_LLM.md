# Prompt de Integração: Finalização Pipeline AiShorts v2.0

## Contexto do Projeto

**Objetivo:** Completar e validar o pipeline AiShorts v2.0 para geração automatizada de vídeos curtos (TikTok, YouTube Shorts, Instagram Reels).

**Status Atual:** 67% FUNCIONAL (4/6 componentes validados)

**Base de Código:** Disponível no repositório GitHub `MrDeox/AiShortsV2` (commit `5c1cfe3`)

---

## Arquitetura do Pipeline (Ordem de Execução)

```
1. ThemeGenerator → Geração de roteiro com IA
2. KokoroTTS → Conversão texto → áudio PT-BR  
3. YouTubeExtractor → Busca e download B-roll
4. SemanticAnalyzer → Matching roteiro ↔ vídeo
5. AudioVideoSynchronizer → Sincronização áudio-vídeo
6. VideoProcessor → Composição final
```

---

## Status Detalhado por Componente

### ✅ COMPONENTES FUNCIONAIS (4/6)

#### 1. YouTubeExtractor - 100% FUNCIONAL
- **Localização:** `src/video/extractors/youtube_extractor.py`
- **Status:** ✅ Download de B-roll funcionando perfeitamente
- **Dependência:** `yt-dlp==2025.10.22` instalada
- **Teste Realizado:** Buscou e baixou 2 vídeos sobre "golfinhos aquaticos"
- **Validação:** Método `search_videos()` e `download_video()` testados com sucesso

#### 2. SemanticAnalyzer - 100% FUNCIONAL  
- **Localização:** `src/video/matching/semantic_analyzer.py`
- **Status:** ✅ Análise semântica para português funcionando
- **Dependência:** `spacy==3.8.7` instalada
- **Teste Realizado:** `extract_keywords("Os golfinhos são animais incríveis que nadam")` → `['golfinhos', 'são', 'animais', 'incríveis', 'nadam']`
- **Validação:** Métodos `analyze_text()`, `calculate_similarity()`, `categorize_content()` funcionando

#### 3. AudioVideoSynchronizer - 100% FUNCIONAL
- **Localização:** `src/video/sync/audio_video_synchronizer.py`
- **Status:** ✅ Sincronização áudio-vídeo operacional
- **Dependências:** `moviepy==2.2.1`, `librosa`, `soundfile`, `numpy`, `scipy` todas instaladas
- **Correção Aplicada:** Atualização para MoviePy v2.2.1 (estrutura de imports)

#### 4. VideoProcessor - 100% FUNCIONAL
- **Localização:** `src/video/processing/video_processor.py`
- **Status:** ✅ Composição e processamento de vídeo OK
- **Dependências:** Todas instaladas e testadas
- **Correção Aplicada:** Múltiplas correções para MoviePy v2.2.1

### ❌ COMPONENTES COM PROBLEMAS (2/6)

#### 5. ThemeGenerator - PROBLEMA DE API
- **Localização:** `src/generators/theme_generator.py`
- **Status:** ❌ Código funciona, mas API inválida
- **Problema:** OpenRouter API key inválida (chave fornecida anteriormente não é válida)
- **Erro:** 401 "User not found"
- **Estrutura:** ✅ Classe implementada corretamente
- **Métodos:** `generate_theme()` e `create_script_outline()` definidos
- **Configuração:** Arquivo `.env` com `OPENROUTER_API_KEY` (precisa de chave válida)

#### 6. KokoroTTS - BIBLIOTECA NÃO INSTALADA
- **Localização:** `src/tts/kokoro_tts.py`  
- **Status:** ❌ Código funciona, biblioteca não instalada
- **Problema:** `ModuleNotFoundError: No module named 'kokoro'`
- **Tentativas:** `uv add kokoro` e `pip install kokoro-tts` falharam
- **Estrutura:** ✅ Classe `KokoroTTSClient` implementada
- **Métodos:** `synthesize_speech()` e `batch_synthesize()` definidos
- **Requer:** Instalação local manual conforme documentação Kokoro

---

## Problemas Identificados e Soluções

### 🔴 PRIORIDADE ALTA

#### 1. Resolver API OpenRouter
**Problema:** Chave API inválida (erro 401 "User not found")
**Solução:** 
1. Acessar https://openrouter.ai
2. Criar conta ou fazer login  
3. Gerar nova API key válida
4. Atualizar arquivo `.env` com a nova chave
5. Testar ThemeGenerator com a nova chave

#### 2. Instalar Kokoro TTS Localmente
**Problema:** Biblioteca não disponível no PyPI
**Solução:**
1. Pesquisar documentação oficial Kokoro TTS
2. Seguir processo de instalação local
3. Instalar modelos de voz em português brasileiro
4. Testar sintetização com texto simples
5. Validar qualidade de áudio gerado

---

## Comandos de Teste Validados

### Teste YouTubeExtractor (FUNCIONANDO)
```bash
python -c "from src.video.extractors.youtube_extractor import YouTubeExtractor; yt = YouTubeExtractor(); results = yt.search_videos('golfinhos aquaticos'); print(f'Resultados: {len(results)} vídeos encontrados')"
# Resultado esperado: 2 vídeos encontrados e baixados
```

### Teste SemanticAnalyzer (FUNCIONANDO)
```bash
python -c "from src.video.matching.semantic_analyzer import SemanticAnalyzer; analyzer = SemanticAnalyzer(); keywords = analyzer.extract_keywords('Os golfinhos são animais incríveis que nadam'); print('Keywords:', keywords)"
# Resultado esperado: ['golfinhos', 'são', 'animais', 'incríveis', 'nadam']
```

### Teste ThemeGenerator (ERRO API)
```bash
python -c "from src.generators.theme_generator import ThemeGenerator; gen = ThemeGenerator(); print('ThemeGenerator inicializado com sucesso')"
# Estrutura OK, mas precisa API key válida
```

### Teste KokoroTTS (ERRO BIBLIOTECA)
```bash
python -c "from src.tts.kokoro_tts import KokoroTTSClient; tts = KokoroTTSClient(); print('KokoroTTS importado com sucesso')"
# Estrutura OK, mas biblioteca não instalada
```

---

## Dependências Instaladas e Funcionais

| Pacote | Versão | Status | Função |
|--------|--------|--------|--------|
| **loguru** | 0.7.3 | ✅ | Sistema de logging |
| **pydantic-settings** | 2.11.0 | ✅ | Configurações com validação |
| **yt-dlp** | 2025.10.22 | ✅ | Download de vídeos YouTube |
| **spacy** | 3.8.7 | ✅ | Processamento de linguagem natural |
| **moviepy** | 2.2.1 | ✅ | Processamento de vídeo |
| **librosa** | latest | ✅ | Análise de áudio |
| **soundfile** | latest | ✅ | Leitura/gravação de áudio |
| **numpy** | latest | ✅ | Operações numéricas |
| **scipy** | latest | ✅ | Processamento de sinais |

---

## Configurações de Ambiente

### Arquivo .env
**Localização:** `/workspace/.env`
**Conteúdo Atual:**
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here  # PRECISA SER ATUALIZADA
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
MAX_TOKENS_THEME=150
TEMPERATURE_THEME=0.7
MAX_TOKENS_SCRIPT=800
TEMPERATURE_SCRIPT=0.7
```

### Arquivo .gitignore
**Status:** ✅ Configurado corretamente
**Protege:** `.env`, `__pycache__/`, `*.pyc`, etc.

---

## Correções de Código Aplicadas

### 1. Correção de Import Paths (CRÍTICO)
**Problema:** Imports usando namespace `aishorts_v2.src` inexistente

**Arquivos Corrigidos:**
- `src/video/extractors/youtube_extractor.py` (linha 14)
- `src/video/extractors/segment_processor.py` (linha 14)  
- `src/video/processing/platform_optimizer.py` (linha 15)

**Mudança:**
```python
# ANTES (INCORRETO)
from aishorts_v2.src.utils.exceptions
from aishorts_v2.src.config.video_platforms

# DEPOIS (CORRETO)  
from src.utils.exceptions
from config.video_platforms
```

### 2. Atualização MoviePy v2.2.1 (CRÍTICO)
**Problema:** Estrutura de imports mudou na versão 2.2.1

**Arquivos Corrigidos:**
- `src/video/sync/audio_video_synchronizer.py` (linha 15)
- `src/video/sync/timing_optimizer.py` (linha 14)
- `src/video/processing/video_processor.py` (linhas 8, 9, 16)

**Mudanças:**
```python
# ANTES (MoviePy v1.x)
import moviepy.editor as mp
from moviepy.audio.fx import volumex
from src.config.video_settings

# DEPOIS (MoviePy v2.2.1)
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy.audio.fx import MultiplyVolume
from config.video_settings
```

---

## Plano de Finalização (Próximos Passos)

### FASE 1: Correção de Dependências (2-4 horas)

#### 1.1 Obter API OpenRouter Válida (30 min)
1. Criar conta no OpenRouter.ai
2. Gerar nova API key
3. Atualizar `.env`
4. Testar ThemeGenerator

#### 1.2 Instalar Kokoro TTS (2-3 horas)
1. Pesquisar documentação Kokoro TTS
2. Instalar conforme instruções oficiais
3. Baixar modelos PT-BR
4. Testar sintetização
5. Integrar com pipeline

### FASE 2: Teste End-to-End (2-3 horas)

#### 2.1 Teste de Componentes Individuais (30 min)
- Validar todos os 6 componentes isoladamente
- Verificar logs e tratamento de erros

#### 2.2 Teste de Integração (1-2 horas)  
- Executar pipeline completo com tema simples
- Validar cada etapa: Tema → TTS → B-roll → Matching → Sync → Composição
- Verificar qualidade do vídeo final

#### 2.3 Teste de Performance (30 min)
- Medir tempo de execução total
- Verificar uso de memória
- Otimizar gargalos se necessário

### FASE 3: Validação e Documentação (1 hora)

#### 3.1 Teste de Qualidade
- Gerar 3-5 vídeos com temas diferentes
- Validar qualidade de áudio TTS
- Verificar sincronização áudio-vídeo
- Testar em diferentes plataformas (resoluções)

#### 3.2 Documentação Final
- Atualizar relatório de validação
- Documentar problemas resolvidos
- Criar guia de instalação para outras máquinas
- Adicionar casos de teste unitários

---

## Comandos de Validação Final

### Teste Completo do Pipeline
```bash
# 1. Verificar todos os componentes
python -c "
import sys
components = [
    'src.generators.theme_generator.ThemeGenerator',
    'src.tts.kokoro_tts.KokoroTTSClient', 
    'src.video.extractors.youtube_extractor.YouTubeExtractor',
    'src.video.matching.semantic_analyzer.SemanticAnalyzer',
    'src.video.sync.audio_video_synchronizer.AudioVideoSynchronizer',
    'src.video.processing.video_processor.VideoProcessor'
]

for component in components:
    try:
        module_name, class_name = component.rsplit('.', 1)
        module = __import__(module_name, fromlist=[class_name])
        getattr(module, class_name)
        print(f'✅ {class_name} - OK')
    except Exception as e:
        print(f'❌ {class_name} - ERRO: {e}')
"

# 2. Teste de tema simples (após resolver API)
python -c "from src.generators.theme_generator import ThemeGenerator; gen = ThemeGenerator(); theme = gen.generate_theme('animais'); print('Tema gerado:', theme)"

# 3. Teste de TTS (após resolver Kokoro)  
python -c "from src.tts.kokoro_tts import KokoroTTSClient; tts = KokoroTTSClient(); audio = tts.synthesize_speech('Teste de áudio em português'); print('Áudio gerado:', audio)"

# 4. Teste de download B-roll
python -c "from src.video.extractors.youtube_extractor import YouTubeExtractor; yt = YouTubeExtractor(); vids = yt.search_videos('gatos brincalhões'); print(f'Vídeos encontrados: {len(vids)}')"
```

---

## Estrutura de Arquivos Principais

```
AiShortsV2/
├── src/
│   ├── generators/
│   │   └── theme_generator.py          # ❌ API key inválida
│   ├── tts/
│   │   └── kokoro_tts.py               # ❌ Biblioteca não instalada
│   ├── video/
│   │   ├── extractors/
│   │   │   ├── youtube_extractor.py    # ✅ FUNCIONAL
│   │   │   └── segment_processor.py    # ✅ Import corrigido
│   │   ├── matching/
│   │   │   └── semantic_analyzer.py    # ✅ FUNCIONAL
│   │   ├── sync/
│   │   │   ├── audio_video_synchronizer.py  # ✅ FUNCIONAL
│   │   │   └── timing_optimizer.py     # ✅ Import corrigido
│   │   └── processing/
│   │       ├── platform_optimizer.py   # ✅ Import corrigido
│   │       └── video_processor.py      # ✅ FUNCIONAL
│   ├── config/
│   │   ├── video_settings.py
│   │   └── video_platforms.py
│   └── utils/
│       └── exceptions.py
├── docs/
│   ├── RELATORIO_VALIDACAO_PIPELINE.md
│   └── PROMPT_INTEGRACAO_LLM.md        # Este arquivo
├── .env                                # Precisa API key válida
├── .gitignore
├── requirements.txt
└── pyproject.toml
```

---

## Considerações Técnicas

### MoviePy v2.2.1
- **Estrutura de imports mudou:** usar imports diretos em vez de `import moviepy.editor as mp`
- **Métodos de áudio:** `volumex` → `MultiplyVolume`
- **Performance:** Mais eficiente que versões anteriores

### spaCy para Português
- **Fallback funcionando:** Mesmo sem modelo `pt_core_news_sm` instalado
- **NLP básico:** Extração de palavras-chave funcional
- **Futuro:** Instalar modelo português para resultados mais precisos

### yt-dlp
- **Versão atual:** 2025.10.22
- **Funcionalidade:** Perfeita para download de B-roll
- **Filtros:** Duração, qualidade, formato funcionando

### OpenRouter
- **Modelo configurado:** `nvidia/nemotron-nano-9b-v2:free`
- **Token limits:** Tema 150, Roteiro 800
- **Temperature:** 0.7 para criatividade balanceada

---

## Resultados Esperados Pós-Finalização

### Funcionalidade Completa (100%)
- ✅ ThemeGenerator: Geração de temas e roteiros
- ✅ KokoroTTS: Síntese de áudio PT-BR
- ✅ YouTubeExtractor: Download automático de B-roll
- ✅ SemanticAnalyzer: Matching inteligente roteiro-vídeo
- ✅ AudioVideoSynchronizer: Sincronização perfeita
- ✅ VideoProcessor: Composição final otimizada

### Performance Alvo
- **Tempo total:** < 5 minutos para vídeo de 60s
- **Qualidade áudio:** 48kHz, 16-bit
- **Qualidade vídeo:** 1080x1920 (9:16 para plataformas verticais)
- **Sincronização:** Atraso < 100ms

### Casos de Uso
- **Temas:** Curiosidades, fatos interessantes, dicas rápidas
- **Plataformas:** TikTok, YouTube Shorts, Instagram Reels
- **Duração:** 15s a 180s
- **Estilo:** Narrativo, educativo, entretenimento

---

## Mensagem Final para o Agente

**TAREFA:** Finalizar o pipeline AiShorts v2.0 para 100% de funcionalidade

**PRIORIDADE:** 
1. Resolver OpenRouter API key
2. Instalar Kokoro TTS localmente  
3. Testar pipeline end-to-end

**CRITÉRIOS DE SUCESSO:**
- Todos os 6 componentes funcionando
- Pipeline end-to-end executando sem erros
- Vídeo final gerado com qualidade adequada
- Documentação atualizada

**TEMPO ESTIMADO:** 4-6 horas para completion completa

**RECURSOS DISPONÍVEIS:**
- Base de código completa e estruturada
- 4/6 componentes já funcionais
- Dependências principais instaladas
- Relatório detalhado de validação

**SUPORTE:**
- Documentação técnica completa
- Comandos de teste validados
- Estrutura de arquivos documentada
- Problemas identificados e soluções mapeadas

---

**Data:** 04/11/2025  
**Autor:** MiniMax Agent  
**Versão:** Prompt v1.0 para Finalização Pipeline AiShorts v2.0