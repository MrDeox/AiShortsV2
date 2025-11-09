# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AiShorts v2.0 is an automated pipeline for generating short viral videos (TikTok, YouTube Shorts, Instagram Reels) from theme to final optimized video. The system combines AI generation, computer vision, neural TTS, and advanced video processing.

## Development Commands

### Running the Application
```bash
# Main pipeline entry point
python main.py

# Pipeline with different theme categories
python -c "from main import create_orchestrator; from src.generators.prompt_engineering import ThemeCategory; orchestrator = create_orchestrator(); orchestrator.run(theme_category=ThemeCategory.TECHNOLOGY)"
```

### Testing
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_kokoro_tts.py
pytest tests/test_video/test_video_module.py
pytest tests/test_integration.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run single test
pytest tests/test_kokoro_tts.py::test_kokoro_tts_basic_synthesis
```

### Code Quality
```bash
# Type checking
mypy src/

# Code formatting (if black is configured)
black src/

# Linting (if flake8 is configured)
flake8 src/
```

### Dependencies Management
```bash
# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for TTS
pip install kokoro-onnx imagehash>=4.3.0

# Development dependencies (from requirements.txt)
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

## Architecture Overview

### Core Pipeline Flow
The main pipeline is orchestrated by `AiShortsOrchestrator` in `src/pipeline/orchestrator.py`:

1. **Theme Generation** (`ThemeGenerator`) - Generates viral themes using AI
2. **Script Generation** (`ScriptGenerator`) - Creates structured scripts with timing
3. **Translation** (`translator`) - Translates scripts to Portuguese for TTS
4. **TTS Synthesis** (`KokoroTTSClient`) - Neural text-to-speech
5. **B-roll Extraction** (`YouTubeExtractor`) - Sources relevant video content
6. **Semantic Analysis** (`SemanticAnalyzer`) - Content matching and analysis
7. **Audio-Video Sync** (`AudioVideoSynchronizer`) - Synchronizes timing
8. **Final Composition** (`FinalVideoComposer`) - Creates optimized output

### Key Components

#### Configuration System
- **Centralized Settings**: `src/config/settings.py` uses Pydantic for type-safe configuration
- **Environment Variables**: All settings configurable via `.env` file
- **Required Environment Variables**:
  - `OPENROUTER_API_KEY`: API access for AI generation
  - `OPENROUTER_MODEL` or `LLM_MODEL`: AI model to use

#### AI Integration
- **OpenRouter Client**: `src/core/openrouter_client.py` handles AI API calls with rate limiting
- **Prompt Engineering**: `src/generators/prompt_engineering.py` contains optimized templates
- **Rate Limiting**: Built-in rate limiting (20 req/min by default)

#### Video Processing Pipeline
- **Multi-stage Processing**: Extract → Match → Sync → Compose
- **CLIP-based Matching**: `src/video/matching/semantic_analyzer.py` for content relevance
- **Platform Optimization**: Support for TikTok, Shorts, Reels specifications
- **Professional Templates**: `src/video/generators/visual_templates.py`

#### Audio Processing
- **Neural TTS**: Primary backend is Kokoro TTS (`src/tts/kokoro_tts.py`)
- **Audio Analysis**: Uses librosa for timing and synchronization
- **Caption Generation**: `src/pipeline/services/caption_service.py` creates timed captions

### Data Models
All data structures use Pydantic models defined in `src/models/` for type safety and validation.

### Service Layer
- **B-roll Query Service**: `src/pipeline/services/broll_query_service.py` generates optimized search queries
- **Caption Service**: Automatic caption generation with timing
- **Modular Design**: Services are injected into the orchestrator

## Development Guidelines

### Code Organization Principles
- **Modular Architecture**: Each component has a single responsibility
- **Dependency Injection**: Components receive dependencies via constructors
- **Type Safety**: All public interfaces use Python type hints
- **Error Handling**: Structured exception handling with custom exceptions in `src/utils/exceptions.py`

### File Structure Conventions
- **Generators**: `src/generators/` - Content creation components
- **Video Processing**: `src/video/` - All video-related functionality
- **Pipeline**: `src/pipeline/` - Orchestration and services
- **Models**: `src/models/` - Pydantic data models
- **Config**: `src/config/` - Configuration management
- **Utils**: `src/utils/` - Shared utilities

### Testing Strategy
- **Unit Tests**: Each module has corresponding test files
- **Integration Tests**: `tests/test_integration.py` tests pipeline flow
- **Fixtures**: `tests/conftest.py` provides test data and mocks
- **Async Testing**: Uses pytest-asyncio for TTS and API testing

### Portuguese Development Notes
- **Content Language**: Generated content is primarily in English, then translated to Portuguese for TTS
- **User-facing**: All user messages and logs should be in Portuguese when appropriate
- **Code Comments**: Maintain Portuguese comments in alignment with project style

## Troubleshooting Common Issues

### Dependencies
- **Missing TTS**: Install `kokoro-onnx` separately from PyPI
- **Image Processing**: Ensure `imagehash>=4.3.0` is installed
- **FFmpeg**: Required system dependency for video processing

### API Configuration
- **OpenRouter Key**: Must be set in `.env` file
- **Rate Limits**: Adjust `RATE_LIMIT_PER_MINUTE` if hitting API limits
- **Model Selection**: Use `OPENROUTER_MODEL` or `LLM_MODEL` to specify AI model

### Pipeline Failures
- **Script Generation**: Check AI model availability and API quota
- **Video Downloads**: YouTube extraction may fail due to video availability
- **Audio Sync**: Ensure audio files exist before video composition

## Environment Setup

1. **Python Version**: Requires Python 3.9+ (specified as 3.12.5 in pyproject.toml)
2. **Virtual Environment**: Strongly recommended
3. **System Dependencies**: FFmpeg must be installed system-wide
4. **Configuration**: Copy `.env.example` to `.env` and configure API keys

## Key File Locations

- **Main Entry Point**: `main.py`
- **Pipeline Orchestrator**: `src/pipeline/orchestrator.py`
- **Configuration**: `src/config/settings.py`
- **AI Client**: `src/core/openrouter_client.py`
- **TTS Engine**: `src/tts/kokoro_tts.py`
- **Video Composer**: `src/video/generators/final_video_composer.py`
- **Test Suite**: `tests/` directory

## Output Structure

Generated content is organized in `outputs/`:
- `outputs/audio/` - TTS-generated narration files
- `outputs/video/` - Downloaded b-roll content
- `outputs/final/` - Final composed videos
- `outputs/pipeline_report_*.json` - Detailed execution reports

The pipeline maintains comprehensive logging and generates detailed JSON reports for each execution.