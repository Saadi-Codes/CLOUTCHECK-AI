<<<<<<< HEAD
"""
Centralized configuration management for CloutCheck AI pipeline.
Handles environment variables, paths, and model settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============= BASE PATHS =============
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATASET_DIR = BASE_DIR / "dataset"
RESULTS_DIR = BASE_DIR / "results"
BRANDS_DIR = BASE_DIR / "brands"
MODELS_CACHE_DIR = BASE_DIR / "models_cache"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, DATASET_DIR, RESULTS_DIR, BRANDS_DIR, MODELS_CACHE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data subdirectories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Dataset subdirectories
IMAGES_DIR = DATASET_DIR / "images"
VIDEOS_DIR = DATASET_DIR / "videos"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# ============= API KEYS =============
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")  # Optional Hugging Face token

# ============= PERFORMANCE SETTINGS =============
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
DEVICE = "cuda" if USE_GPU else "cpu"

# CPU-optimized batch sizes (can increase if more RAM available)
BATCH_SIZE_TEXT = int(os.getenv("BATCH_SIZE_TEXT", "32"))
BATCH_SIZE_IMAGE = int(os.getenv("BATCH_SIZE_IMAGE", "8"))
BATCH_SIZE_AUDIO = int(os.getenv("BATCH_SIZE_AUDIO", "4"))
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))

# Download settings
NUM_DOWNLOAD_WORKERS = int(os.getenv("NUM_DOWNLOAD_WORKERS", "10"))
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ============= STORAGE SETTINGS =============
CLEANUP_MEDIA = os.getenv("CLEANUP_MEDIA", "true").lower() == "true"
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "1920"))  # Max width in pixels
COMPRESS_METADATA = os.getenv("COMPRESS_METADATA", "true").lower() == "true"
VIDEO_FPS_SAMPLE = int(os.getenv("VIDEO_FPS_SAMPLE", "1"))  # Frames per second to extract
CLEANUP_MODE = os.getenv("CLEANUP_MODE", "immediate")  # Options: "immediate", "end", "none"

# ============= MODEL SETTINGS =============
# Text models
TEXT_TOXICITY_MODEL = "unbiased-small"  # Detoxify model variant
TEXT_SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Image models
IMAGE_NSFW_MODEL = "Falconsai/nsfw_image_detection"  # Transformers model
IMAGE_NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.7"))

# Audio models
AUDIO_WHISPER_MODEL = "tiny"  # Options: tiny, base, small, medium, large

# Brand fit models
BRAND_SIMILARITY_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BRAND_CATEGORY_MODEL = "facebook/bart-large-mnli"  # Zero-shot classifier

# ============= SCORING THRESHOLDS =============
TOXICITY_THRESHOLD = float(os.getenv("TOXICITY_THRESHOLD", "0.6"))
NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.7"))
BRAND_FIT_MIN_SCORE = int(os.getenv("BRAND_FIT_MIN_SCORE", "60"))
MIN_ENGAGEMENT_RATE = float(os.getenv("MIN_ENGAGEMENT_RATE", "0.01"))  # 1%

# ============= SCORING WEIGHTS =============
# Content fusion weights (must sum to 1.0)
WEIGHT_TEXT_TOXICITY = 0.25
WEIGHT_IMAGE_NSFW = 0.25
WEIGHT_ENGAGEMENT = 0.30
WEIGHT_AUTHENTICITY = 0.20

# Brand fit weights (must sum to 1.0)
WEIGHT_SEMANTIC_SIMILARITY = 0.30
WEIGHT_CATEGORY_ALIGNMENT = 0.25
WEIGHT_VALUE_ALIGNMENT = 0.25
WEIGHT_AUDIENCE_FIT = 0.20

# ============= LOGGING SETTINGS =============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============= HELPER FUNCTIONS =============
def get_model_cache_path(model_name: str) -> Path:
    """Get cache path for a specific model"""
    safe_name = model_name.replace("/", "_").replace("\\", "_")
    return MODELS_CACHE_DIR / safe_name


def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    if not APIFY_API_TOKEN:
        errors.append("APIFY_API_TOKEN not set in .env file")
    
    # Validate weight sums
    fusion_weight_sum = (WEIGHT_TEXT_TOXICITY + WEIGHT_IMAGE_NSFW + 
                        WEIGHT_ENGAGEMENT + WEIGHT_AUTHENTICITY)
    if abs(fusion_weight_sum - 1.0) > 0.01:
        errors.append(f"Content fusion weights must sum to 1.0 (current: {fusion_weight_sum})")
    
    brand_weight_sum = (WEIGHT_SEMANTIC_SIMILARITY + WEIGHT_CATEGORY_ALIGNMENT + 
                       WEIGHT_VALUE_ALIGNMENT + WEIGHT_AUDIENCE_FIT)
    if abs(brand_weight_sum - 1.0) > 0.01:
        errors.append(f"Brand fit weights must sum to 1.0 (current: {brand_weight_sum})")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


# Run validation on import
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"Warning: {e}")
=======
"""
Centralized configuration management for CloutCheck AI pipeline.
Handles environment variables, paths, and model settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============= BASE PATHS =============
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATASET_DIR = BASE_DIR / "dataset"
RESULTS_DIR = BASE_DIR / "results"
BRANDS_DIR = BASE_DIR / "brands"
MODELS_CACHE_DIR = BASE_DIR / "models_cache"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, DATASET_DIR, RESULTS_DIR, BRANDS_DIR, MODELS_CACHE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data subdirectories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Dataset subdirectories
IMAGES_DIR = DATASET_DIR / "images"
VIDEOS_DIR = DATASET_DIR / "videos"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# ============= API KEYS =============
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")  # Optional Hugging Face token

# ============= PERFORMANCE SETTINGS =============
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
DEVICE = "cuda" if USE_GPU else "cpu"

# CPU-optimized batch sizes (can increase if more RAM available)
BATCH_SIZE_TEXT = int(os.getenv("BATCH_SIZE_TEXT", "32"))
BATCH_SIZE_IMAGE = int(os.getenv("BATCH_SIZE_IMAGE", "8"))
BATCH_SIZE_AUDIO = int(os.getenv("BATCH_SIZE_AUDIO", "4"))
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))

# Download settings
NUM_DOWNLOAD_WORKERS = int(os.getenv("NUM_DOWNLOAD_WORKERS", "10"))
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# ============= STORAGE SETTINGS =============
CLEANUP_MEDIA = os.getenv("CLEANUP_MEDIA", "true").lower() == "true"
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "1920"))  # Max width in pixels
COMPRESS_METADATA = os.getenv("COMPRESS_METADATA", "true").lower() == "true"
VIDEO_FPS_SAMPLE = int(os.getenv("VIDEO_FPS_SAMPLE", "1"))  # Frames per second to extract
CLEANUP_MODE = os.getenv("CLEANUP_MODE", "immediate")  # Options: "immediate", "end", "none"

# ============= MODEL SETTINGS =============
# Text models
TEXT_TOXICITY_MODEL = "unbiased-small"  # Detoxify model variant
TEXT_SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Image models
IMAGE_NSFW_MODEL = "Falconsai/nsfw_image_detection"  # Transformers model
IMAGE_NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.7"))

# Audio models
AUDIO_WHISPER_MODEL = "tiny"  # Options: tiny, base, small, medium, large

# Brand fit models
BRAND_SIMILARITY_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BRAND_CATEGORY_MODEL = "facebook/bart-large-mnli"  # Zero-shot classifier

# ============= SCORING THRESHOLDS =============
TOXICITY_THRESHOLD = float(os.getenv("TOXICITY_THRESHOLD", "0.6"))
NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.7"))
BRAND_FIT_MIN_SCORE = int(os.getenv("BRAND_FIT_MIN_SCORE", "60"))
MIN_ENGAGEMENT_RATE = float(os.getenv("MIN_ENGAGEMENT_RATE", "0.01"))  # 1%

# ============= SCORING WEIGHTS =============
# Content fusion weights (must sum to 1.0)
WEIGHT_TEXT_TOXICITY = 0.25
WEIGHT_IMAGE_NSFW = 0.25
WEIGHT_ENGAGEMENT = 0.30
WEIGHT_AUTHENTICITY = 0.20

# Brand fit weights (must sum to 1.0)
WEIGHT_SEMANTIC_SIMILARITY = 0.30
WEIGHT_CATEGORY_ALIGNMENT = 0.25
WEIGHT_VALUE_ALIGNMENT = 0.25
WEIGHT_AUDIENCE_FIT = 0.20

# ============= LOGGING SETTINGS =============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============= HELPER FUNCTIONS =============
def get_model_cache_path(model_name: str) -> Path:
    """Get cache path for a specific model"""
    safe_name = model_name.replace("/", "_").replace("\\", "_")
    return MODELS_CACHE_DIR / safe_name


def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    if not APIFY_API_TOKEN:
        errors.append("APIFY_API_TOKEN not set in .env file")
    
    # Validate weight sums
    fusion_weight_sum = (WEIGHT_TEXT_TOXICITY + WEIGHT_IMAGE_NSFW + 
                        WEIGHT_ENGAGEMENT + WEIGHT_AUTHENTICITY)
    if abs(fusion_weight_sum - 1.0) > 0.01:
        errors.append(f"Content fusion weights must sum to 1.0 (current: {fusion_weight_sum})")
    
    brand_weight_sum = (WEIGHT_SEMANTIC_SIMILARITY + WEIGHT_CATEGORY_ALIGNMENT + 
                       WEIGHT_VALUE_ALIGNMENT + WEIGHT_AUDIENCE_FIT)
    if abs(brand_weight_sum - 1.0) > 0.01:
        errors.append(f"Brand fit weights must sum to 1.0 (current: {brand_weight_sum})")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


# Run validation on import
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"Warning: {e}")
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
