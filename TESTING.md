# Test Modules

Run these commands to test individual components:

## Test Text Analysis

```bash
python -c "from src.models.text_toxicity import TextAnalyzer; a = TextAnalyzer(); print(a.analyze_text('I love this product!'))"
```

## Test Image Analysis

```bash
# Requires an image file
python src/models/image_nsfw.py path/to/your/image.jpg
```

## Test Video Processing

```bash
# Requires a video file
python src/models/video_analysis.py path/to/your/video.mp4
```

## Test Audio Transcription

```bash
# Requires an audio/video file
python src/models/audio_analysis.py path/to/your/audio.wav
```

## Test Full Pipeline

```bash
# After scraping data with Scraper.py
python -m src.pipeline.run_full_pipeline
```

## Common Issues

### ModuleNotFoundError

```bash
# Make sure you're in the FYP directory
cd c:\Users\user\Desktop\FYP

# Run setup
python setup_project.py
```

### CUDA/GPU Errors

```bash
# Edit .env and set:
USE_GPU=false
```

### ffmpeg not found

Install ffmpeg:
- Windows: `choco install ffmpeg` or download from https://ffmpeg.org/
- Restart terminal after installation
