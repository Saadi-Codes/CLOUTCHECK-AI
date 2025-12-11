<<<<<<< HEAD
"""
One-click setup script for CloutCheck AI pipeline.
Creates directory structure, installs dependencies, downloads models.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if env_example.exists():
        with open(env_example, 'r') as src:
            content = src.read()
        
        with open(env_file, 'w') as dst:
            dst.write(content)
        
        print("✓ Created .env file from .env.example")
        print("Please edit .env and add your APIFY_API_TOKEN")
        return False
    else:
        print(".env.example not found")
        return False


def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print("✓ ffmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ffmpeg not found")
        print(" Please install ffmpeg:")
        print("   - Windows: choco install ffmpeg OR download from https://ffmpeg.org/")
        print("   - Mac: brew install ffmpeg")
        print("   - Linux: sudo apt install ffmpeg")
        return False


def install_dependencies():
    """Install Python dependencies"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("requirements.txt not found")
        return False
    
    print("Installing Python dependencies...")
    print("This may take several minutes...\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\nDependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nFailed to install dependencies: {e}")
        return False


def download_models():
    """Download required AI models"""
    print("Downloading AI models...")
    print("This will download ~2GB of models. Please be patient...")
    
    try:
        # Import after installing dependencies
        from detoxify import Detoxify
        from sentence_transformers import SentenceTransformer
        import whisper
        
        # Detoxify (text toxicity)
        print("\n1/3 Downloading Detoxify model...")
        _ = Detoxify("unbiased-small")
        print("✓ Detoxify ready")
        
        # Sentence transformers (brand fit)
        print("\n2/3 Downloading Sentence Transformer...")
        _ = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✓ Sentence Transformer ready")
        
        # Whisper (audio transcription)
        print("\n3/3 Downloading Whisper model...")
        _ = whisper.load_model("tiny")
        print("✓ Whisper ready")
        
        print("\n✓ All models downloaded successfully")
        return True
        
    except Exception as e:
        print(f"\nFailed to download models: {e}")
        return False


def verify_structure():
    """Verify directory structure"""
    required_dirs = [
        "src/data_prep",
        "src/models",
        "src/scoring",
        "src/brand_fit",
        "src/pipeline",
        "src/utils",
        "data/raw",
        "data/processed",
        "dataset/images",
        "dataset/videos",
        "results",
        "brands",
        "models_cache",
        "logs"
    ]
    
    print("Verifying directory structure...")
    all_exist = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created: {dir_path}")
            all_exist = False
    
    if all_exist:
        print("All directories exist")
    else:
        print("Directory structure created")
    
    return True


def main():
    """Main setup process"""
    print_header("CLOUTCHECK AI - SETUP WIZARD")
    
    print("\nThis script will:")
    print("  1. Create directory structure")
    print("  2. Set up environment variables")
    print("  3. Install Python dependencies")
    print("  4. Download AI models (~2GB)")
    print("  5. Verify ffmpeg installation")
    
    response = input("\nProceed with setup? (y/n): ").strip().lower()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Directory structure
    print_header("STEP 1: Directory Structure")
    if not verify_structure():
        print("Failed to create directory structure")
        return
    
    # Step 2: Environment file
    print_header("STEP 2: Environment Configuration")
    env_ready = create_env_file()
    
    # Step 3: Install dependencies
    print_header("STEP 3: Installing Dependencies")
    if not install_dependencies():
        print("\nSetup failed at dependency installation")
        return
    
    # Step 4: Download models
    print_header("STEP 4: Downloading AI Models")
    if not download_models():
        print("\nSetup failed at model download")
        print("You can try downloading models manually later")
    
    # Step 5: Check ffmpeg
    print_header("STEP 5: Checking System Requirements")
    ffmpeg_ok = check_ffmpeg()
    
    # Final summary
    print_header("SETUP COMPLETE!")
    
    if env_ready and ffmpeg_ok:
        print("\nCloutCheck AI is ready to use!")
        print("\nNext steps:")
        print("  1. Run the scraper: python Scraper.py")
        print("  2. Convert media: python Converter.py")
        print("  3. Run pipeline: python -m src.pipeline.run_full_pipeline")
    else:
        print("\nSetup completed with warnings:")
        if not env_ready:
            print("  - Please edit .env and add your APIFY_API_TOKEN")
        if not ffmpeg_ok:
            print("  - Please install ffmpeg for video processing")
        
        print("\nAfter fixing these issues, you can start using CloutCheck AI!")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
=======
"""
One-click setup script for CloutCheck AI pipeline.
Creates directory structure, installs dependencies, downloads models.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if env_example.exists():
        with open(env_example, 'r') as src:
            content = src.read()
        
        with open(env_file, 'w') as dst:
            dst.write(content)
        
        print("✓ Created .env file from .env.example")
        print("Please edit .env and add your APIFY_API_TOKEN")
        return False
    else:
        print(".env.example not found")
        return False


def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print("✓ ffmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ffmpeg not found")
        print(" Please install ffmpeg:")
        print("   - Windows: choco install ffmpeg OR download from https://ffmpeg.org/")
        print("   - Mac: brew install ffmpeg")
        print("   - Linux: sudo apt install ffmpeg")
        return False


def install_dependencies():
    """Install Python dependencies"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("requirements.txt not found")
        return False
    
    print("Installing Python dependencies...")
    print("This may take several minutes...\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\nDependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nFailed to install dependencies: {e}")
        return False


def download_models():
    """Download required AI models"""
    print("Downloading AI models...")
    print("This will download ~2GB of models. Please be patient...")
    
    try:
        # Import after installing dependencies
        from detoxify import Detoxify
        from sentence_transformers import SentenceTransformer
        import whisper
        
        # Detoxify (text toxicity)
        print("\n1/3 Downloading Detoxify model...")
        _ = Detoxify("unbiased-small")
        print("✓ Detoxify ready")
        
        # Sentence transformers (brand fit)
        print("\n2/3 Downloading Sentence Transformer...")
        _ = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✓ Sentence Transformer ready")
        
        # Whisper (audio transcription)
        print("\n3/3 Downloading Whisper model...")
        _ = whisper.load_model("tiny")
        print("✓ Whisper ready")
        
        print("\n✓ All models downloaded successfully")
        return True
        
    except Exception as e:
        print(f"\nFailed to download models: {e}")
        return False


def verify_structure():
    """Verify directory structure"""
    required_dirs = [
        "src/data_prep",
        "src/models",
        "src/scoring",
        "src/brand_fit",
        "src/pipeline",
        "src/utils",
        "data/raw",
        "data/processed",
        "dataset/images",
        "dataset/videos",
        "results",
        "brands",
        "models_cache",
        "logs"
    ]
    
    print("Verifying directory structure...")
    all_exist = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created: {dir_path}")
            all_exist = False
    
    if all_exist:
        print("All directories exist")
    else:
        print("Directory structure created")
    
    return True


def main():
    """Main setup process"""
    print_header("CLOUTCHECK AI - SETUP WIZARD")
    
    print("\nThis script will:")
    print("  1. Create directory structure")
    print("  2. Set up environment variables")
    print("  3. Install Python dependencies")
    print("  4. Download AI models (~2GB)")
    print("  5. Verify ffmpeg installation")
    
    response = input("\nProceed with setup? (y/n): ").strip().lower()
    if response != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Directory structure
    print_header("STEP 1: Directory Structure")
    if not verify_structure():
        print("Failed to create directory structure")
        return
    
    # Step 2: Environment file
    print_header("STEP 2: Environment Configuration")
    env_ready = create_env_file()
    
    # Step 3: Install dependencies
    print_header("STEP 3: Installing Dependencies")
    if not install_dependencies():
        print("\nSetup failed at dependency installation")
        return
    
    # Step 4: Download models
    print_header("STEP 4: Downloading AI Models")
    if not download_models():
        print("\nSetup failed at model download")
        print("You can try downloading models manually later")
    
    # Step 5: Check ffmpeg
    print_header("STEP 5: Checking System Requirements")
    ffmpeg_ok = check_ffmpeg()
    
    # Final summary
    print_header("SETUP COMPLETE!")
    
    if env_ready and ffmpeg_ok:
        print("\nCloutCheck AI is ready to use!")
        print("\nNext steps:")
        print("  1. Run the scraper: python Scraper.py")
        print("  2. Convert media: python Converter.py")
        print("  3. Run pipeline: python -m src.pipeline.run_full_pipeline")
    else:
        print("\nSetup completed with warnings:")
        if not env_ready:
            print("  - Please edit .env and add your APIFY_API_TOKEN")
        if not ffmpeg_ok:
            print("  - Please install ffmpeg for video processing")
        
        print("\nAfter fixing these issues, you can start using CloutCheck AI!")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
