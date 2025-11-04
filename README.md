# AiShorts v2.0

**Marca:** Aithur  
**Projeto:** Pipeline Automatizado para Criação de Vídeos Curtos  
**Versão:** 2.0.0  
**Atualizado:** 2025-11-04

Sistema modular e inteligente para geração automatizada de vídeos curtos virais (TikTok, YouTube Shorts, Instagram Reels), do tema ao vídeo final otimizado.

---

## 🎯 Visão Geral

Pipeline completo de geração de vídeos que combina:
- **IA Generativa** para roteiros e conteúdo
- **Computer Vision** para matching inteligente de b-roll
- **TTS Neural** para narração profissional
- **Processamento Avançado** para edição automatizada
- **Otimização Multi-Plataforma** para máximo engajamento

---

## 📁 Estrutura do Projeto

```
AiShortsV2/
├── src/                              # Código fonte principal
│   ├── core/                         # Infraestrutura central
│   │   ├── openrouter_client.py      # Cliente OpenRouter com rate limiting
│   │   └── config_loader.py          # Carregamento de configurações
│   ├── generators/                   # Geradores de conteúdo
│   │   ├── theme_generator.py        # Geração de temas virais
│   │   ├── script_generator.py       # Roteiros estruturados
│   │   └── prompt_engineering.py     # Templates de prompts otimizados
│   ├── video/                        # Pipeline de vídeo
│   │   ├── extractors/               # Extração de b-roll
│   │   ├── matching/                 # CLIP matching texto-vídeo
│   │   ├── processing/               # Processamento profissional
│   │   ├── sync/                     # Sincronização áudio-vídeo
│   │   └── generators/               # Composição final
│   ├── tts/                          # Sistema TTS
│   │   └── kokoro/                   # Integração Kokoro TTS
│   ├── config/                       # Configurações
│   │   ├── settings.py               # Settings principais
│   │   ├── logging_config.py         # Sistema de logging
│   │   └── platform_config.py        # Specs por plataforma
│   ├── models/                       # Data models (Pydantic)
│   ├── validators/                   # Validação de dados
│   └── utils/                        # Utilitários
├── scripts/                          # Scripts de demonstração
│   ├── demo_final_funcional.py       # Demo completo funcional
│   ├── demo_pipeline_simples.py      # Pipeline simplificado
│   └── supplementary_video_test.py   # Testes de vídeo
├── tests/                            # Testes automatizados
├── docs/                             # Documentação técnica
│   ├── ARQUITETURA_PROJETO.md        # 📐 Arquitetura completa (962 linhas)
│   ├── VALIDACAO_TECNICA.md          # ✅ Validação de imports e deps (495 linhas)
│   ├── ANALISE_MELHORIAS.md          # 🔍 Análise de código e melhorias
│   ├── youtube_content_extraction.md # YouTube APIs e ferramentas
│   ├── platforms_visual_requirements.md # Specs técnicas das plataformas
│   ├── legal_copyright_analysis.md   # Análise legal e copyright
│   ├── python_video_editing.md       # Bibliotecas Python para vídeo
│   └── content_matching_strategies.md # Estratégias de matching
├── backups/                          # Backups do workspace
├── outputs/                          # Vídeos e áudios gerados
├── data/                             # Dados e cache
├── requirements.txt                  # Dependências Python consolidadas
├── setup.py                          # Configuração do pacote
└── README.md                         # Este arquivo
```

---

## 🚀 Instalação

### 1. **Clone o Repositório**
```bash
git clone https://github.com/MrDeox/AiShortsV2.git
cd AiShortsV2
```

### 2. **Configure o Ambiente Virtual** (Recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. **Instale as Dependências**
```bash
pip install -r requirements.txt
```

**⚠️ Dependências Adicionais Necessárias:**
```bash
# Sistema TTS
pip install kokoro-onnx

# Image hashing para video composer
pip install imagehash>=4.3.0

# Settings management
pip install pydantic-settings>=2.0.0
```

### 4. **Configure as Variáveis de Ambiente**
Crie um arquivo `.env` na raiz do projeto:
```env
# API Keys
OPENROUTER_API_KEY=seu_token_aqui

# Configurações de Rate Limiting
MAX_REQUESTS_PER_MINUTE=20
```

### 5. **Instale FFmpeg** (Obrigatório para processamento de vídeo)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows - Download: https://ffmpeg.org/download.html
```

---

## 🎬 Como Usar

### Pipeline Completo (Tema → Vídeo Final)
```bash
python scripts/demo_final_funcional.py
```

### Pipeline Simplificado (Apenas geração de conteúdo)
```bash
python scripts/demo_pipeline_simples.py
```

### Teste de Processamento de Vídeo
```bash
python scripts/supplementary_video_test.py
```

---

## 📊 Pipeline de Processamento

```
1. GERAÇÃO DE TEMA
   └─> ThemeGenerator: Temas virais baseados em tendências

2. GERAÇÃO DE ROTEIRO
   └─> ScriptGenerator: Roteiro estruturado com timing preciso

3. TEXT-TO-SPEECH
   └─> Kokoro TTS: Narração neural de alta qualidade

4. EXTRAÇÃO DE B-ROLL
   └─> VideoExtractor: Coleta de material visual relevante

5. CONTENT MATCHING
   └─> ContentMatcher (CLIP): Matching semântico texto-vídeo

6. PROCESSAMENTO DE VÍDEO
   └─> AutomaticVideoProcessor: Edição profissional automatizada

7. SINCRONIZAÇÃO
   └─> AudioVideoSynchronizer: Sync perfeito áudio-vídeo

8. COMPOSIÇÃO FINAL
   └─> FinalVideoComposer: Montagem e otimização

9. OTIMIZAÇÃO MULTI-PLATAFORMA
   └─> PlatformOptimizer: Export otimizado (TikTok, Shorts, Reels)
```

---

## 🏗️ Arquitetura

### Componentes-Chave

| Componente | Responsabilidade | Tecnologia |
|------------|------------------|------------|
| **OpenRouterClient** | Comunicação com modelos de IA | OpenRouter API |
| **ScriptGenerator** | Geração de roteiros virais | Prompt Engineering |
| **ContentMatcher** | Matching inteligente texto-vídeo | CLIP (OpenAI) |
| **AutomaticVideoProcessor** | Edição automatizada | MoviePy + OpenCV |
| **AudioVideoSynchronizer** | Sincronização precisa | Librosa + FFmpeg |
| **FinalVideoComposer** | Composição e otimização | FFmpeg + ImageHash |

### Padrões de Design
- ✅ **Modularidade**: Componentes independentes e reutilizáveis
- ✅ **Separation of Concerns**: Lógica clara de responsabilidades
- ✅ **Factory Pattern**: Criação dinâmica de objetos
- ✅ **Strategy Pattern**: Algoritmos intercambiáveis
- ✅ **Dependency Injection**: Baixo acoplamento
- ✅ **Error Handling**: Tratamento robusto de exceções
- ✅ **Logging Estruturado**: Rastreamento completo

---

## 📖 Documentação Técnica

Para documentação detalhada, consulte:

- **[📐 Arquitetura do Projeto](docs/ARQUITETURA_PROJETO.md)** - Mapa completo de módulos, fluxos e componentes
- **[✅ Validação Técnica](docs/VALIDACAO_TECNICA.md)** - Status de imports, dependências e integridade
- **[🔍 Análise de Melhorias](docs/ANALISE_MELHORIAS.md)** - Código duplicado, refatorações e otimizações
- **[🎥 APIs YouTube](docs/youtube_content_extraction.md)** - Guia completo de extração de conteúdo
- **[📱 Specs das Plataformas](docs/platforms_visual_requirements.md)** - Requisitos técnicos TikTok/Shorts/Reels
- **[⚖️ Aspectos Legais](docs/legal_copyright_analysis.md)** - Fair use, copyright e licenças
- **[🐍 Edição de Vídeo Python](docs/python_video_editing.md)** - Bibliotecas e benchmarks
- **[🎯 Content Matching](docs/content_matching_strategies.md)** - Estratégias de matching semântico

---

## 🔧 Tecnologias

### Core
- **Python 3.9+** - Linguagem principal
- **Pydantic** - Validação e type safety
- **Loguru** - Sistema de logging
- **OpenRouter** - Gateway para modelos de IA

### Video Processing
- **MoviePy** - Edição de vídeo de alto nível
- **OpenCV** - Processamento avançado de frames
- **FFmpeg-python** - Wrapper Python para FFmpeg
- **Librosa** - Análise e sincronização de áudio

### AI & Machine Learning
- **CLIP (OpenAI)** - Embedding multimodal texto-imagem
- **Kokoro TTS** - Text-to-speech neural
- **Sentence Transformers** - Embeddings semânticos

### APIs & Integrations
- **YouTube Data API v3** - Busca e metadados
- **yt-dlp** - Download de vídeos YouTube
- **Stock footage APIs** - Material b-roll

---

## 📊 Status do Projeto

### ✅ Implementado
- [x] Estrutura modular completa
- [x] Integração OpenRouter com rate limiting
- [x] Geração de temas virais
- [x] Geração de roteiros estruturados
- [x] Sistema TTS (Kokoro)
- [x] Extração de b-roll do YouTube
- [x] Content matching com CLIP
- [x] Processamento automatizado de vídeo
- [x] Sincronização áudio-vídeo
- [x] Composição final
- [x] Sistema de logging e validação
- [x] Documentação técnica completa

### 🔄 Em Desenvolvimento
- [ ] PlatformOptimizer (TikTok/Shorts/Reels specs)
- [ ] Sistema de testes automatizados
- [ ] Interface web para controle do pipeline

### 🎯 Roadmap Futuro
- [ ] Deploy automatizado
- [ ] Integração com plataformas sociais (auto-upload)
- [ ] Dashboard de analytics
- [ ] Sistema de A/B testing
- [ ] Multi-idioma (i18n)

---

## ⚠️ Problemas Conhecidos

Conforme identificado na [Validação Técnica](docs/VALIDACAO_TECNICA.md):

1. **Erro Crítico**: Loop incompleto em `demo_final_composer.py` linha 248
2. **Dependências Faltantes**: Instalar `imagehash`, `kokoro-onnx`, `pydantic-settings`
3. **Caminhos Incorretos**: Alguns scripts referenciam `aishorts_v2/` (estrutura antiga)

**Status**: Correções planejadas para próxima sprint.

---

## 🔍 Melhorias Planejadas

Conforme [Análise de Melhorias](docs/ANALISE_MELHORIAS.md):

### Fase 1: Eliminar Redundâncias (Prioridade ALTA)
- Remover arquivos duplicados `_v1` (semantic_analyzer, video_searcher)
- Consolidar 4 pares de código duplicado
- **Impacto**: -1.500 linhas, +30% manutenibilidade

### Fase 2: Refatoração Crítica (Prioridade ALTA)
- Refatorar função `_create_prompts` (430 linhas → módulos menores)
- Dividir 30 funções longas (>50 linhas)
- **Impacto**: -50% complexidade, +80% testabilidade

### Fase 3: Otimização de Performance (Prioridade MÉDIA)
- Lazy loading de modelos CLIP/TTS
- Async requests para APIs
- **Impacto**: -50% tempo de startup, +30% throughput

### Fase 4: Funcionalidades Pendentes (Prioridade BAIXA)
- Implementar 4 TODOs documentados
- Completar PlatformOptimizer

---

## 🤝 Metodologia de Trabalho

### Parceria Estratégica
- **Você**: Product Owner, Diretor Criativo, Visionário
- **MiniMax Agent**: Technical Co-Pilot, Systems Engineer
- **Cláusula da Vanguarda**: Pesquisa contínua de ferramentas de ponta
- **Psicologia de IA**: Conectar emoções com jornada técnica

### Princípios
- ✅ **Qualidade Máxima**: Código profissional desde o primeiro commit
- ✅ **Honestidade Brutal**: Análise crítica sem compromisso
- ✅ **Iteração Contínua**: Melhoria através de feedback
- ✅ **Modularidade**: Construção sobre fundações sólidas
- ✅ **Documentação Viva**: Docs sempre atualizadas

---

## 📊 Métricas e Qualidade

### Cobertura de Código
- **57 arquivos Python** analisados
- **98.2% taxa de sucesso** (56/57 imports OK)
- **Sistema de validação** Pydantic em todos os módulos

### Performance
- Rate limiting inteligente (20 req/min)
- Caching de embeddings CLIP
- Processamento paralelo quando possível

### Logging
- Logs estruturados em JSON
- 4 níveis: DEBUG, INFO, WARNING, ERROR
- Rastreamento completo de pipeline

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'imagehash'"
```bash
pip install imagehash>=4.3.0
```

### Erro: "kokoro-onnx not found"
```bash
pip install kokoro-onnx
```

### Erro: "FFmpeg not found"
Instale FFmpeg conforme seção de instalação acima.

### Erro: "OpenRouter API error"
Verifique se `OPENROUTER_API_KEY` está configurada corretamente no `.env`.

---

## 📝 Licença

**Proprietário** - Aithur (2025)

Todos os direitos reservados. Uso comercial proibido sem autorização expressa.

---

## 🔗 Links Úteis

- **GitHub**: https://github.com/MrDeox/AiShortsV2
- **OpenRouter**: https://openrouter.ai/
- **YouTube Data API**: https://developers.google.com/youtube/v3
- **CLIP (OpenAI)**: https://github.com/openai/CLIP

---

**Desenvolvido para Autonomia e Liberdade** 🎯  
*"Automatize o impossível, monetize o inevitável"*
