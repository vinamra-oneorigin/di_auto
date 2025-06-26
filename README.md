# di_auto

A Python project for automated document intelligence using GPT Vision API for image analysis and data extraction.

## Features

- Document image processing with GPT Vision
- Jupyter notebook support for research and development
- uv package management for fast, reliable dependency handling

## Setup

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. For Jupyter notebook support:
   ```bash
   uv add jupyter
   ```

## Usage

- Run Jupyter notebooks: `uv run jupyter lab`
- Execute main module: `uv run python -m di_auto`
- Add dependencies: `uv add <package>`

## Project Structure

- `src/di_auto/` - Main package source code
- `extraction.ipynb` - Document extraction research notebook
- `research_process.md` - Research findings and decision log
- `pyproject.toml` - Project configuration and dependencies

## Requirements

Dependencies are managed through `pyproject.toml`. Key packages to add as needed:

```bash
# Vision/AI packages
uv add openai pillow

# Data processing
uv add pandas numpy

# Jupyter environment
uv add jupyter ipykernel

# Additional packages as required
```
