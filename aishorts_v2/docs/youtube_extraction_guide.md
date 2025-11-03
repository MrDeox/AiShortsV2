# Sistema de Extração do YouTube

Sistema completo para extração e processamento de vídeos do YouTube, incluindo busca, download de segmentos e normalização de conteúdo para criação de shorts.

## 🚀 Funcionalidades

### YouTubeExtractor
- **Busca de Vídeos**: Pesquisa vídeos por termo usando yt-dlp
- **Extração de Metadados**: Obtém informações detalhadas dos vídeos
- **Download de Segmentos**: Extrai partes específicas dos vídeos (3-5 segundos)
- **Tratamento de Erros**: Robust error handling para vídeos indisponíveis, problemas de rede, etc.

### SegmentProcessor
- **Extração de Segmentos**: Usa FFmpeg para extrair partes específicas de vídeos
- **Normalização**: Converte vídeos para formatos padronizados (MP4, 720p, 30fps)
- **Análise de Vídeo**: Extrai metadados técnicos usando FFprobe
- **Conversão de Codecs**: Padroniza codecs de vídeo e áudio

## 📋 Pré-requisitos

### Software Necessário
- Python 3.8+
- FFmpeg (instalado e no PATH)
- FFprobe (incluído com FFmpeg)

### Pacotes Python
```bash
pip install yt-dlp>=2024.1.1 ffmpeg-python>=0.2.0
```

## 🛠️ Instalação

Execute o script de instalação automática:

```bash
python setup_youtube_extraction.py
```

O script irá:
1. Verificar a versão do Python
2. Instalar dependências Python
3. Verificar se FFmpeg está instalado
4. Criar diretórios necessários
5. Testar a instalação

### Instalação Manual do FFmpeg

#### Windows
1. Baixe de [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extraia em `C:\ffmpeg`
3. Adicione `C:\ffmpeg\bin` ao PATH

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install ffmpeg
```

## 📖 Uso Básico

### Exemplo 1: Busca de Vídeos

```python
from src.video import YouTubeExtractor

# Criar extrator
extractor = YouTubeExtractor()

# Buscar vídeos
resultados = extractor.search_videos("gatos engraçados", max_results=10)

for video in resultados:
    print(f"{video['title']} - {video['duration']}s")
    print(f"URL: {video['url']}")
```

### Exemplo 2: Extração de Metadados

```python
# Obter informações detalhadas de um vídeo
info = extractor.extract_video_info("https://www.youtube.com/watch?v=VIDEO_ID")

print(f"Título: {info['title']}")
print(f"Duração: {info['duration']} segundos")
print(f"Uploader: {info['uploader']}")
print(f"Views: {info['view_count']:,}")
print(f"Tags: {', '.join(info['tags'])}")
```

### Exemplo 3: Download de Segmentos

```python
# Baixar primeiros 5 segundos de um vídeo
segmento_path = extractor.download_segment(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    start_time=10,    # Início em segundos
    duration=5        # Duração em segundos
)

print(f"Segmento salvo em: {segmento_path}")
```

### Exemplo 4: Processamento de Vídeo

```python
from src.video import SegmentProcessor

# Criar processador
processor = SegmentProcessor()

# Extrair segmento com FFmpeg
segmento = processor.extract_segment(
    "video_original.mp4",
    start=15,
    duration=3,
    output_path="meu_segmento.mp4"
)

# Normalizar para formato padrão
video_normalizado = processor.normalize_video(
    segmento,
    target_resolution="720p",
    target_fps=30,
    target_format="mp4"
)

# Obter informações do vídeo
info = processor.get_video_info(video_normalizado)
print(f"Duração: {info['general']['duration']}s")
print(f"Resolução: {info['video_stream']['width']}x{info['video_stream']['height']}")
```

### Exemplo 5: Fluxo Completo

```python
def criar_segmento_para_shorts(video_url, start_time=0, duration=5):
    \"\"\"Fluxo completo para criar segmento otimizado para shorts.\"\"\"
    
    extractor = YouTubeExtractor()
    processor = SegmentProcessor()
    
    try:
        # 1. Verificar se vídeo está disponível e é longo o suficiente
        info = extractor.extract_video_info(video_url)
        
        if info['duration'] < start_time + duration:
            raise ValueError("Vídeo muito curto para o segmento solicitado")
        
        # 2. Baixar segmento específico
        segmento_path = extractor.download_segment(video_url, start_time, duration)
        
        # 3. Normalizar para padrão de shorts
        shorts_video = processor.normalize_video(
            segmento_path,
            target_resolution="720p",
            target_fps=30,
            output_path=f"shorts_{start_time}s_{duration}s.mp4"
        )
        
        return shorts_video
        
    except Exception as e:
        print(f"Erro: {e}")
        return None
    
    finally:
        # Limpeza
        extractor.cleanup_temp_files()
        processor.cleanup_temp_files()

# Uso
video_final = criar_segmento_para_shorts(
    "https://www.youtube.com/watch?v=EXEMPLO",
    start_time=30,
    duration=5
)
```

## 🧪 Testes

Execute os testes unitários:

```bash
pytest tests/test_video/test_extractors.py -v
```

Ou execute o demo completo:

```bash
python demo_youtube_extraction.py
```

## ⚠️ Tratamento de Erros

O sistema inclui tratamento robusto para vários cenários de erro:

### Vídeos Indisponíveis
```python
try:
    info = extractor.extract_video_info("URL_DO_VIDEO")
except VideoUnavailableError as e:
    print(f"Vídeo indisponível: {e.details['unavailable_reason']}")
```

### Vídeos Muito Curtos
```python
try:
    info = extractor.extract_video_info("URL_DO_VIDEO")
except VideoTooShortError as e:
    print(f"Vídeo muito curto ({e.details['duration']}s)")
```

### Problemas de Conectividade
```python
try:
    resultados = extractor.search_videos("termo")
except NetworkError as e:
    print(f"Erro de rede: {e}")
```

### Erros de Processamento
```python
try:
    segmento = processor.extract_segment("video.mp4", 0, 5)
except VideoProcessingError as e:
    print(f"Erro no processamento: {e.details['ffmpeg_error']}")
```

## 📁 Estrutura de Arquivos

```
src/
├── video/
│   ├── __init__.py
│   └── extractors/
│       ├── __init__.py
│       ├── youtube_extractor.py    # Extração do YouTube
│       └── segment_processor.py    # Processamento com FFmpeg
tests/
└── test_video/
    └── test_extractors.py           # Testes unitários
```

## 🔧 Configuração Avançada

### Personalização do YouTubeExtractor

```python
extractor = YouTubeExtractor(
    temp_dir="/caminho/temp",    # Diretório temporário
    output_dir="/caminho/output" # Diretório de saída
)

# Configurações personalizadas do yt-dlp
extractor.ydl_opts['format'] = 'best[height<=1080]'  # Qualidade maior
extractor.ydl_opts['outtmpl'] = 'videos/%(title)s.%(ext)s'
```

### Configuração do SegmentProcessor

```python
processor = SegmentProcessor(
    temp_dir="/caminho/processamento"
)

# Normalização personalizada
video = processor.normalize_video(
    "input.mp4",
    target_resolution="1080p",
    target_fps=60,  # FPS maior
    output_path="output_hq.mp4"
)
```

## 📊 Especificações Técnicas

### Formatos Suportados
- **Entrada**: YouTube URLs (qualquer vídeo público)
- **Saída**: MP4 (padrão), MOV, AVI
- **Resoluções**: 480p, 720p, 1080p
- **Codecs**: H.264 vídeo, AAC áudio

### Limitações
- Vídeos privados e não listados não são suportados
- Segmentos máximos de 5 minutos
- Respeita rate limiting do YouTube
- Requer FFmpeg para processamento

### Performance
- Downloads otimizados para segmentos curtos (3-5s)
- Timeout configurável para operações de rede
- Cache inteligente para evitar downloads duplicados
- Limpeza automática de arquivos temporários

## 🤝 Contribuição

Para contribuir com o projeto:

1. Siga os padrões de código existentes
2. Adicione testes para novas funcionalidades
3. Documente APIs e mudanças
4. Teste com diferentes tipos de vídeo

## 📄 Licença

Este projeto faz parte do AiShorts v2.0. Consulte a licença principal do projeto.

---

**Desenvolvido para criação eficiente de conteúdo de shorts usando extração e processamento automatizado de vídeos do YouTube.**