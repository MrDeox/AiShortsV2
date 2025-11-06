# GEMINI.md

## Project Overview

This project, AiShortsV2, is a Python-based pipeline for automatically generating short, viral videos for platforms like TikTok, YouTube Shorts, and Instagram Reels. It leverages a modular architecture that combines generative AI for scriptwriting, computer vision for B-roll matching, neural TTS for narration, and advanced video processing for automated editing. The goal is to create a system that can take a theme and produce a fully optimized video with minimal human intervention.

**Key Technologies:**

*   **Core:** Python 3.9+, Pydantic, Loguru, OpenRouter
*   **Video Processing:** MoviePy, OpenCV, FFmpeg, Librosa
*   **AI & Machine Learning:** CLIP (OpenAI), Kokoro TTS, Sentence Transformers, PyTorch
*   **APIs & Integrations:** YouTube Data API v3, yt-dlp

## Building and Running

### 1. **Prerequisites**

*   Python 3.9+
*   FFmpeg

### 2. **Installation**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MrDeox/AiShortsV2.git
    cd AiShortsV2
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/macOS
    # or
    venv\Scripts\activate  # For Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    **Note:** The `README.md` also suggests installing `kokoro-onnx`, `imagehash>=4.3.0`, and `pydantic-settings>=2.0.0` separately.

4.  **Set up environment variables:**
    Create a `.env` file in the project root and add the following:
    ```env
    # API Keys
    OPENROUTER_API_KEY=your_token_here

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE=20
    ```

### 3. **Running the Demos**

*   **Full Pipeline (Theme to Final Video):**
    ```bash
    python scripts/demo_final_funcional.py
    ```

*   **Simplified Pipeline (Content Generation Only):**
    ```bash
    python scripts/demo_pipeline_simples.py
    ```

*   **Video Processing Test:**
    ```bash
    python scripts/supplementary_video_test.py
    ```

## Development Conventions

*   **Modular Architecture:** The project is structured into independent, reusable components with clear responsibilities.
*   **Design Patterns:** The codebase utilizes patterns like Factory, Strategy, and Dependency Injection to promote low coupling and high cohesion.
*   **Type Hinting and Validation:** Pydantic is used for data validation and to enforce type safety.
*   **Logging:** A structured logging system is in place for comprehensive tracking and debugging.
*   **Testing:** The project includes a `tests` directory, indicating a commitment to automated testing.
*   **Documentation:** The `docs` directory contains extensive technical documentation, including architectural diagrams, validation reports, and analyses.

## Project Structure

The project is organized into the following key directories:

*   `src/`: Contains the main source code, organized by feature (core, generators, video, tts, etc.).
*   `scripts/`: Includes demonstration scripts for running different parts of the pipeline.
*   `tests/`: Contains automated tests.
*   `docs/`: Holds detailed technical documentation.
*   `outputs/`: The destination for generated videos and audio.
*   `data/`: Used for data and caching.
*   `requirements.txt`: Lists the project's Python dependencies.
*   `setup.py`: The setup script for the project.
*   `README.md`: Provides a comprehensive overview of the project.
