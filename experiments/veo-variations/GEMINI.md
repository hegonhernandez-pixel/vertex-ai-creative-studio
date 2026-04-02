# Veo Variations Experiment Guide

This application generates creative variations of a video concept and evaluates them technically.

## Project Structure

- **`api/main.py`**: FastAPI backend that orchestrates the workflow.
- **`core/`**: Core logic for generation and analysis.
  - **`generator.py`**: Veo video generation using the GenAI SDK.
  - **`variations.py`**: Prompt variation generation using Gemini.
  - **`metrics.py`**: Technical quality evaluation (NIQE) using `pyiqa`.
  - **`c2pa.py`**: C2PA manifest extraction and summarization.
- **`ui/`**: Lit-based frontend (TypeScript).

## Development Workflow

### Backend

1. **Install dependencies:**
   ```bash
   uv sync
   ```
2. **Setup environment:**
   Create a `.env` file from `.env.template`.
3. **Start the API:**
   ```bash
   python api/main.py
   ```

### Frontend

1. **Install dependencies:**
   ```bash
   cd ui && npm install
   ```
2. **Start development server:**
   ```bash
   npm run dev
   ```
3. **Build for production:**
   ```bash
   npm run build
   ```

## Key Features

- **Concurrent Generation:** Generates multiple video variations in parallel.
- **Technical Analysis:** Automatically calculates NIQE scores for generated videos.
- **C2PA Integration:** Verifies and summarizes content credentials.
