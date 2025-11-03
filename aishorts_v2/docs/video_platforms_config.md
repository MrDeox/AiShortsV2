# Configurações de Plataforma de Vídeo - AiShorts v2.0

## Visão Geral

Este documento descreve as configurações específicas implementadas para otimização de vídeos em múltiplas plataformas (TikTok, YouTube Shorts, Instagram Reels), incluindo templates visuais e ferramentas de processamento.

## 📁 Estrutura de Arquivos Criados

```
aishorts_v2/
├── src/
│   ├── config/
│   │   └── video_platforms.py          # Configurações das plataformas
│   └── video/
│       ├── processing/
│       │   └── platform_optimizer.py    # Otimizador de vídeo
│       └── generators/
│           └── visual_templates.py      # Templates visuais
├── tests/
│   └── test_video/
│       └── test_platforms.py           # Testes das plataformas
└── docs/
    └── video_platforms_config.md        # Esta documentação
```

## 🎯 Funcionalidades Implementadas

### 1. Configurações de Plataforma (`src/config/video_platforms.py`)

#### Especificações Técnicas

**TikTok:**
- Resolução: 1080x1920 (9:16)
- Duração: 1s - 600s (10 minutos)
- FPS: 30 (60 para movimento intenso)
- Formato: MP4/MOV
- Codec: H.264/AAC
- Tamanho máximo: 500MB

**YouTube Shorts:**
- Resolução: 1080x1920 (9:16)
- Duração: 15s - 60s
- FPS: 24-60
- Formato: MP4/MOV
- Codec: H.264/AAC
- Bitrate: 1-6 Mbps

**Instagram Reels:**
- Resolução: 1080x1920 (9:16)
- Duração: 1s - 90s
- FPS: 30+
- Formato: MP4/MOV
- Codec: H.264/AAC
- Tamanho máximo: 4GB

#### Presets de Qualidade
- **Baixa**: 1500kbps (teste rápido)
- **Média**: 3000kbps (padrão social)
- **Alta**: 5000kbps (máxima qualidade)
- **Otimizada**: 2500kbps (equilíbrio)

#### Zonas Seguras
Configuradas para evitar sobreposições da interface:
- TikTok: 10% top, 15% bottom, 5% sides
- YouTube Shorts: 8% top, 12% bottom, 5% sides
- Instagram Reels: 12% top, 18% bottom, 8% sides

### 2. Otimizador de Plataforma (`src/video/processing/platform_optimizer.py`)

#### Classe `PlatformOptimizer`

**Métodos Principais:**

```python
# Otimiza vídeo para uma plataforma específica
optimize_for_platform(video_path, platform, category="SPACE", quality="Média")

# Ajusta timing e transições
adjust_timing(video_path, platform, category="SPACE")

# Aplica configurações de plataforma
apply_platform_settings(video_path, platform)
```

**Funcionalidades:**
- Validação de vídeo de entrada
- Ajuste de resolução e aspect ratio
- Configuração de codec e bitrate
- Otimização de timing baseada na categoria
- Geração de relatórios de validação

### 3. Templates Visuais (`src/video/generators/visual_templates.py`)

#### Categorias de Template

**SPACE:**
- Cor: Azul escuro (#000428, #004e92)
- Estilo: Modern sans-serif
- Transições: fade, slide, zoom
- Timing: Educational (3s hook, 4+5+4s entrega, 3s conclusão)

**ANIMALS:**
- Cor: Vibrante (#ff6b6b, #4ecdc4)
- Estilo: Playful round
- Transições: cut, fade, morph
- Timing: Storytelling (4s hook, 6+8+6s entrega, 4s conclusão)

**SCIENCE:**
- Cor: Técnico (#2c3e50, #3498db)
- Estilo: Scientific bold
- Transições: dissolve, wipe, slide
- Timing: Informative (2s hook, 5+5+5s entrega, 3s conclusão)

**HISTORY:**
- Cor: Vintage (#8B4513, #D2B48C)
- Estilo: Elegant serif
- Transições: sepia, fade, slide
- Timing: Narrative (5s hook, 7+10+8s entrega, 5s conclusão)

**NATURE:**
- Cor: Verde (#228B22, #90EE90)
- Estilo: Organic sans
- Transições: fade, dissolve, slide
- Timing: Relaxing (2s hook, 8+10+8s entrega, 3s conclusão)

#### Tipos de Template
- **Title Slide**: Títulos principais
- **Content Slide**: Conteúdo educativo
- **Transition**: Transições entre seções
- **End Card**: Chamadas para ação
- **Background**: Fundos personalizáveis

### 4. Configurações de Timing

#### Presets de Timing

| Categoria | Hook | Entrega | Conclusão | Transição |
|-----------|------|---------|-----------|-----------|
| Educational | 3s | 4+5+4s | 3s | 0.5s |
| Storytelling | 4s | 6+8+6s | 4s | 0.8s |
| Informative | 2s | 5+5+5s | 3s | 0.3s |
| Narrative | 5s | 7+10+8s | 5s | 1.0s |
| Relaxing | 2s | 8+10+8s | 3s | 1.2s |

## 🧪 Testes Implementados

### Arquivo: `tests/test_video/test_platforms.py`

**Testes Incluídos:**

1. **TestVideoPlatformConfig:**
   - Inicialização de configurações
   - Obtenção de especificações
   - Validação de presets de qualidade
   - Configurações de zona segura

2. **TestPlatformOptimizer:**
   - Inicialização do otimizador
   - Ajuste de timing
   - Aplicação de configurações
   - Tratamento de erros

3. **TestVisualTemplateGenerator:**
   - Inicialização de templates
   - Obtenção por categoria/tipo
   - Geração de texto personalizado
   - Paletas de cores

4. **TestIntegration:**
   - Completude de configurações
   - Consistência entre templates
   - Validação de timing

## 🚀 Uso Básico

### 1. Carregar Configurações

```python
from aishorts_v2.src.config.video_platforms import Platform, video_config

# Obter especificações da plataforma
specs = video_config.get_platform_specs(Platform.TIKTOK)
print(f"Resolução: {specs.resolution_str}")
```

### 2. Otimizar Vídeo

```python
from aishorts_v2.src.video.processing.platform_optimizer import PlatformOptimizer

optimizer = PlatformOptimizer()
result = optimizer.optimize_for_platform(
    "video.mp4", 
    Platform.TIKTOK, 
    category="SPACE",
    quality="Otimizada"
)
```

### 3. Usar Templates

```python
from aishorts_v2.src.video.generators.visual_templates import (
    get_template, TemplateType, generate_text_overlay
)

# Obter template
template = get_template("SPACE", TemplateType.TITLE_SLIDE)

# Gerar texto personalizado
overlay = generate_text_overlay("Meu Título", "SPACE", "center")
```

### 4. Sequência Completa

```python
from aishorts_v2.src.config.video_platforms import get_category_config
from aishorts_v2.src.video.generators.visual_templates import template_generator

# Configurar categoria
config = get_category_config("SPACE")

# Criar sequência de templates
content = ["Título", "Fato 1", "Fato 2", "Conclusão"]
sequence = template_generator.create_sequence_template("SPACE", content)

# Otimizar para plataforma
optimizer = PlatformOptimizer()
for template in sequence:
    # Aplicar template e otimizar
    result = optimizer.optimize_for_platform("input.mp4", Platform.TIKTOK)
```

## 📊 Configurações Exportadas

Cada plataforma gera configurações específicas para FFmpeg:

```bash
# TikTok
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -r 30 -c:v libx264 -preset medium -crf 25 -b:v 3000k \
  -c:a aac -b:a 128k -movflags +faststart \
  output_tiktok.mp4

# YouTube Shorts
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920" \
  -r 30 -c:v libx264 -b:v 2500k \
  -c:a aac -b:a 128k \
  output_shorts.mp4

# Instagram Reels
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920" \
  -r 30 -c:v libx264 -b:v 3500k \
  -c:a aac -b:a 128k \
  output_reels.mp4
```

## 🔧 Extensibilidade

### Adicionar Nova Plataforma

1. **Editar `video_platforms.py`:**
```python
# Adicionar nova plataforma
new_platform = VideoSpecs(
    name="Nova Plataforma",
    aspect_ratio="9:16",
    resolution=(1080, 1920),
    # ... outras configurações
)

config.platforms[Platform.NOVA_PLATAFORMA] = new_platform
```

2. **Adicionar zona segura:**
```python
safe_zones[Platform.NOVA_PLATAFORMA] = {
    "top_margin_pct": 10,
    "bottom_margin_pct": 15,
    "side_margin_pct": 5
}
```

### Adicionar Nova Categoria

1. **Em `video_platforms.py`:**
```python
CONTENT_CATEGORY_CONFIGS["NOVA_CATEGORIA"] = {
    "transition_effects": ["fade", "slide"],
    "text_overlay_style": "modern_sans",
    "color_palette": ["#color1", "#color2"],
    "timing_preset": "educational"
}
```

2. **Em `visual_templates.py`:**
```python
# Adicionar templates para a nova categoria
nova_categoria_title = VisualTemplate(
    name="nova_categoria_title",
    category="NOVA_CATEGORIA",
    template_type=TemplateType.TITLE_SLIDE,
    # ... configurações
)
```

## 📝 Logs e Monitoramento

O sistema gera logs detalhados para:
- Validação de vídeos
- Processo de otimização
- Aplicação de configurações
- Geração de templates

Exemplo de log:
```
INFO: Otimizando video.mp4 para tiktok
INFO: Aplicando configurações de resolução 1080x1920
INFO: Ajustando timing para categoria SPACE
SUCCESS: Vídeo otimizado em output_tiktok_space.mp4
```

## 🔄 Próximos Passos

1. **Implementação de FFmpeg:** Integrar processamento real de vídeo
2. **Interface Gráfica:** Criar UI para configuração visual
3. **Templates Avançados:** Adicionar animações mais complexas
4. **Integração com APIs:** Conectar com ferramentas de edição
5. **Otimização Automática:** IA para seleção automática de configurações

## 📚 Referências

- [TikTok Video Specifications](https://ads.tiktok.com/help/article/creative-best-practices)
- [YouTube Shorts Guidelines](https://blog.hootsuite.com/youtube-shorts/)
- [Instagram Reels Requirements](https://help.instagram.com/1038071743007909)
- [Research: Platforms Visual Requirements](../platforms_visual_requirements.md)

---

**Criado em:** 2025-11-04  
**Versão:** 1.0  
**Status:** Implementado e Testado