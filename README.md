<<<<<<< HEAD
# CloutCheck AI – Influencer Reputation Analysis Pipeline

Multi-modal AI pipeline for analyzing Instagram influencer content using text toxicity detection, image NSFW analysis, video processing, and audio transcription. Generates comprehensive reputation scores and brand-influencer fit analysis.

**📚 Documentation:**
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Space efficiency & optimization details
- [Walkthrough](WALKTHROUGH.md) - Detailed guide on what was built
- [Task List](TASKS.md) - Development progress log
- [Testing Guide](TESTING.md) - How to test components

## 🚀 Quick Start

### 1. Setup

```bash
# One-click setup (installs dependencies and downloads models)
python setup_project.py

# Or manual install
pip install -r requirements.txt

# Create .env file and add your Apify token
# cp .env.example .env (Linux/Mac)
# copy .env.example .env (Windows)
# Edit .env and set APIFY_API_TOKEN=your_token_here
```

### 2. Scrape Instagram Data

```bash
python Scraper.py
# Enter username when prompted
# Output: username_posts.json
```

### 3. Run Full Pipeline

```bash
python -m src.pipeline.run_full_pipeline
```

This will:
- Preprocess scraped JSON
- Download media (images/videos)
- Analyze text (toxicity, sentiment, spam)
- Analyze images (NSFW detection)
- Calculate reputation score (0-100)
- Generate detailed report
- Clean up temporary files

## 📊 Features

### Multi-Modal AI Analysis

| Modality | Model | Purpose |
|----------|-------|---------|
| **Text** | `unitary/unbiased-toxic-roberta` | Toxicity, sentiment, insults (via Transformers) |
| **Image** | `Falconsai/nsfw_image_detection` | NSFW detection (ViT via Transformers) |
| **Video** | Frame extraction | Video content visual safety |
| **Audio** | OpenAI Whisper (`tiny`) | Speech-to-text → text analysis |

### Brand-Influencer Fit Analysis

Analyze compatibility between influencers and brands based on:
- Semantic similarity (brand voice vs. content)
- Category alignment (fitness, tech, fashion, etc.)
- Value alignment (safety scores, authenticity)
- Audience fit (engagement, demographics)

**Score:** 0-100 with detailed breakdown

### Reputation Scoring

Comprehensive 0-100 score based on:
- **Text Safety** (30%): Low toxicity, no spam
- **Content Safety** (30%): NSFW/inappropriate content
- **Engagement** (20%): Likes, comments, authenticity
- **Sentiment** (20%): Positive vs. negative content

## 🏗️ Architecture

```
┌─────────────┐
│  Scraper.py │  Instagram data via Apify
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Converter.py       │  Download images/videos
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Pipeline (src/pipeline/run_full_pipeline)  │
└──────┬──────────────────────────────────────┘
       │
       ├──▶ Text Analysis (Detoxify + Sentiment)
       ├──▶ Image Analysis (NudeNet)
       ├──▶ Video Analysis (Frames + Audio)
       ├──▶ Scoring & Fusion
       └──▶ Report Generation
```

## 📁 Project Structure

```
FYP/
├── src/
│   ├── config.py              # Configuration management
│   ├── data_prep/
│   │   ├── preprocess_apify_json.py   # JSON preprocessing
│   │   └── video_processor.py         # Video frame/audio extraction
│   ├── models/
│   │   ├── text_toxicity.py   # Text analysis
│   │   ├── image_nsfw.py      # Image analysis
│   │   ├── audio_analysis.py  # Audio transcription
│   │   ├── video_analysis.py  # Video processing
│   ├── scoring/               # Reputation scoring
│   ├── brand_fit/             # Brand-influencer match
│   ├── pipeline/
│   │   └── run_full_pipeline.py  # Main orchestration
│   └── utils/
│       ├── logger.py          # Logging utilities
│       └── storage.py         # Storage optimization
├── Scraper.py                 # Instagram scraper
├── Converter.py               # Media downloader
├── setup_project.py           # One-click setup
├── requirements.txt           # Python dependencies
└── .env.example               # Environment template
```

## 🎯 Usage Examples

### Analyze Single Influencer

```bash
# 1. Scrape
python Scraper.py
# Enter: fitness_influencer
# Output: fitness_influencer_posts.json

# 2. Run pipeline
python -m src.pipeline.run_full_pipeline
```

### Brand Fit Analysis

```bash
# Create brand profile (brands/my_brand.json)
{
  "brand_name": "FitLife",
  "industry": "Fitness",
  "target_categories": ["fitness", "wellness", "health"],
  "brand_values": ["authenticity", "health"],
  "avoid_content": {
    "max_toxicity": 0.3,
    "max_nsfw": 0.2
  }
}

# Run brand fit analysis (Quick check)
python run_brand_analysis.py
```

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# Performance (CPU-optimized defaults)
USE_GPU=false               # Set to true if you have GPU
BATCH_SIZE_TEXT=32          # Reduce if out of memory
BATCH_SIZE_IMAGE=8
NUM_WORKERS=4

# Storage
CLEANUP_MODE="immediate"    # "immediate" (save space), "end" (batch), "none"
MAX_IMAGE_SIZE=1920         # Resize large images

# Thresholds
NSFW_THRESHOLD=0.7          # Flag images above this
TOXICITY_THRESHOLD=0.6      # Flag text above this
```

## 📈 Performance

| Metric | CPU (8 cores) | GPU (RTX 3060) |
|--------|---------------|----------------|
| **Speed** | ~5-8 posts/min | ~20-30 posts/min |
| **Memory** | 4-8 GB | 4-6 GB |
| **Storage** | ~500 MB/influencer (after cleanup) | Same |

**Expected time for 500 posts:**
- CPU: 15-25 minutes
- GPU: 5-10 minutes

## 🛠️ Requirements

- Python 3.8+
- ffmpeg (for video processing)
- 8GB+ RAM recommended
- ~5GB disk space for models

## 📝 License

Educational/Research Project

## 👥 Contributors

- Syed Uzair (22k4212)
- Saad Ahmed (22k-4345)
- Huzaifa (22k-4223)
=======
# CloutCheck AI – Influencer Reputation Analysis Pipeline

Multi-modal AI pipeline for analyzing Instagram influencer content using text toxicity detection, image NSFW analysis, video processing, and audio transcription. Generates comprehensive reputation scores and brand-influencer fit analysis.

**📚 Documentation:**
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Space efficiency & optimization details
- [Walkthrough](WALKTHROUGH.md) - Detailed guide on what was built
- [Task List](TASKS.md) - Development progress log
- [Testing Guide](TESTING.md) - How to test components

## 🚀 Quick Start

### 1. Setup

```bash
# One-click setup (installs dependencies and downloads models)
python setup_project.py

# Or manual install
pip install -r requirements.txt

# Create .env file and add your Apify token
# cp .env.example .env (Linux/Mac)
# copy .env.example .env (Windows)
# Edit .env and set APIFY_API_TOKEN=your_token_here
```

### 2. Scrape Instagram Data

```bash
python Scraper.py
# Enter username when prompted
# Output: username_posts.json
```

### 3. Run Full Pipeline

```bash
python -m src.pipeline.run_full_pipeline
```

This will:
- Preprocess scraped JSON
- Download media (images/videos)
- Analyze text (toxicity, sentiment, spam)
- Analyze images (NSFW detection)
- Calculate reputation score (0-100)
- Generate detailed report
- Clean up temporary files

## 📊 Features

### Multi-Modal AI Analysis

| Modality | Model | Purpose |
|----------|-------|---------|
| **Text** | `unitary/unbiased-toxic-roberta` | Toxicity, sentiment, insults (via Transformers) |
| **Image** | `Falconsai/nsfw_image_detection` | NSFW detection (ViT via Transformers) |
| **Video** | Frame extraction | Video content visual safety |
| **Audio** | OpenAI Whisper (`tiny`) | Speech-to-text → text analysis |

### Brand-Influencer Fit Analysis

Analyze compatibility between influencers and brands based on:
- Semantic similarity (brand voice vs. content)
- Category alignment (fitness, tech, fashion, etc.)
- Value alignment (safety scores, authenticity)
- Audience fit (engagement, demographics)

**Score:** 0-100 with detailed breakdown

### Reputation Scoring

Comprehensive 0-100 score based on:
- **Text Safety** (30%): Low toxicity, no spam
- **Content Safety** (30%): NSFW/inappropriate content
- **Engagement** (20%): Likes, comments, authenticity
- **Sentiment** (20%): Positive vs. negative content

## 🏗️ Architecture

```
┌─────────────┐
│  Scraper.py │  Instagram data via Apify
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Converter.py       │  Download images/videos
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│  Pipeline (src/pipeline/run_full_pipeline)  │
└──────┬──────────────────────────────────────┘
       │
       ├──▶ Text Analysis (Detoxify + Sentiment)
       ├──▶ Image Analysis (NudeNet)
       ├──▶ Video Analysis (Frames + Audio)
       ├──▶ Scoring & Fusion
       └──▶ Report Generation
```

## 📁 Project Structure

```
FYP/
├── src/
│   ├── config.py              # Configuration management
│   ├── data_prep/
│   │   ├── preprocess_apify_json.py   # JSON preprocessing
│   │   └── video_processor.py         # Video frame/audio extraction
│   ├── models/
│   │   ├── text_toxicity.py   # Text analysis
│   │   ├── image_nsfw.py      # Image analysis
│   │   ├── audio_analysis.py  # Audio transcription
│   │   ├── video_analysis.py  # Video processing
│   ├── scoring/               # Reputation scoring
│   ├── brand_fit/             # Brand-influencer match
│   ├── pipeline/
│   │   └── run_full_pipeline.py  # Main orchestration
│   └── utils/
│       ├── logger.py          # Logging utilities
│       └── storage.py         # Storage optimization
├── Scraper.py                 # Instagram scraper
├── Converter.py               # Media downloader
├── setup_project.py           # One-click setup
├── requirements.txt           # Python dependencies
└── .env.example               # Environment template
```

## 🎯 Usage Examples

### Analyze Single Influencer

```bash
# 1. Scrape
python Scraper.py
# Enter: fitness_influencer
# Output: fitness_influencer_posts.json

# 2. Run pipeline
python -m src.pipeline.run_full_pipeline
```

### Brand Fit Analysis

```bash
# Create brand profile (brands/my_brand.json)
{
  "brand_name": "FitLife",
  "industry": "Fitness",
  "target_categories": ["fitness", "wellness", "health"],
  "brand_values": ["authenticity", "health"],
  "avoid_content": {
    "max_toxicity": 0.3,
    "max_nsfw": 0.2
  }
}

# Run brand fit analysis (Quick check)
python run_brand_analysis.py
```

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# Performance (CPU-optimized defaults)
USE_GPU=false               # Set to true if you have GPU
BATCH_SIZE_TEXT=32          # Reduce if out of memory
BATCH_SIZE_IMAGE=8
NUM_WORKERS=4

# Storage
CLEANUP_MODE="immediate"    # "immediate" (save space), "end" (batch), "none"
MAX_IMAGE_SIZE=1920         # Resize large images

# Thresholds
NSFW_THRESHOLD=0.7          # Flag images above this
TOXICITY_THRESHOLD=0.6      # Flag text above this
```

## 📈 Performance

| Metric | CPU (8 cores) | GPU (RTX 3060) |
|--------|---------------|----------------|
| **Speed** | ~5-8 posts/min | ~20-30 posts/min |
| **Memory** | 4-8 GB | 4-6 GB |
| **Storage** | ~500 MB/influencer (after cleanup) | Same |

**Expected time for 500 posts:**
- CPU: 15-25 minutes
- GPU: 5-10 minutes

## 🛠️ Requirements

- Python 3.8+
- ffmpeg (for video processing)
- 8GB+ RAM recommended
- ~5GB disk space for models

## 📝 License

Educational/Research Project

## 👥 Contributors

- Syed Uzair (22k4212)
- Saad Ahmed (22k-4345)
- Huzaifa (22k-4223)
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
