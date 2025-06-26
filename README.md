# di_auto

Professional US academic transcript extraction using GPT Vision with high accuracy data validation.

## Features

- Multi-page PDF processing with GPT Vision
- Comprehensive transcript schema (student info, GPA, courses, degrees, honors)
- Smart course deduplication (preserves retakes, eliminates duplicates)
- Academic integrity validation and verification metrics

## Installation

**Prerequisites:** Install poppler-utils for PDF processing
```bash
# Ubuntu/Debian: sudo apt-get install poppler-utils
# macOS: brew install poppler
```

**Setup:**
```bash
# Using uv (recommended)
uv sync
uv sync --extra jupyter  # for notebooks

# Using pip
pip install -r requirements.txt
```

## Usage

1. Set OpenAI API key: `export OPENAI_API_KEY="your-key"`
2. Open `extraction.ipynb` in Jupyter
3. Run: `test_transcript_extraction('path/to/transcript.pdf')`

**Quick example:**
```python
from controllers import TranscriptProcessor, PDFToImageConverter, GPTVisionExtractor
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
pdf_converter = PDFToImageConverter()
gpt_extractor = GPTVisionExtractor(client=client)
processor = TranscriptProcessor(pdf_converter, gpt_extractor)

result = processor.process_transcript('transcript.pdf')
```

## Requirements

- Python 3.12+
- OpenAI API key (GPT-4o access)
- Cost: ~$0.30-0.60 per page
- Time: ~30-60 seconds per page
