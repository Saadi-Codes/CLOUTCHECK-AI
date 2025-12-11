"""
Image NSFW detection using Hugging Face Transformers.
Uses Falconsai/nsfw_image_detection (ViT) to avoid Windows DLL issues.
"""

import warnings
warnings.filterwarnings('ignore')

from typing import List, Dict, Union
from pathlib import Path
from PIL import Image
from transformers import pipeline
import torch

from src.config import IMAGE_NSFW_MODEL, IMAGE_NSFW_THRESHOLD,DEVICE
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageNSFWAnalyzer:
    """NSFW analysis using Transformers pipeline"""
    
    def __init__(self):
        self.device = DEVICE
        self.model_name = IMAGE_NSFW_MODEL
        self.threshold = IMAGE_NSFW_THRESHOLD
        
        logger.info(f"Initializing ImageNSFWAnalyzer with model: {self.model_name}")
        logger.info(f"Target device: {self.device}")
        
        try:
            # Initialize pipeline
            # device=0 for CUDA, -1 for CPU
            device_id = 0 if self.device == "cuda" else -1
            
            self.classifier = pipeline(
                "image-classification", 
                model=self.model_name, 
                device=device_id
            )
            logger.info("✓ NSFW model loaded successfully")
            
        except Exception as e:
            logger.error(f"CRITICAL: Could not load NSFW model: {e}")
            logger.warning("Falling back to safe mode (scores will be 0.0)")
            self.classifier = None
        
    def analyze_image(self, image_path: Union[str, Path]) -> Dict[str, Union[float, bool, List]]:
        """
        Analyze a single image.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with nsfw_score (0.0 to 1.0)
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            return self._default_result()
            
        # If model failed to load, return safe default
        if self.classifier is None:
            return self._default_result(note="Model failed to load")
        
        try:
            # Run inference
            # Pipeline handles image opening, but we can check validity first
            try:
                img = Image.open(image_path)
                img.verify()
            except Exception:
                logger.warning(f"Invalid image file: {image_path}")
                return self._default_result(note="Invalid image file")
            
            # The pipeline accepts path strings
            results = self.classifier(str(image_path))
            
            # Results format: [{'label': 'nsfw', 'score': 0.9}, {'label': 'normal', 'score': 0.1}]
            # Convert to dictionary mapping
            scores = {r['label'].lower(): r['score'] for r in results}
            
            # Get nsfw score (label might be 'nsfw' or 'NSFW')
            nsfw_score = scores.get('nsfw', 0.0)
            
            is_nsfw = nsfw_score > self.threshold
            safe_score = 1.0 - nsfw_score
            
            return {
                "image_path": str(image_path),
                "nsfw_score": float(nsfw_score),
                "is_nsfw": is_nsfw,
                "safe_score": float(safe_score),
                "detections": results,  # detailed breakdown
                "detection_count": 1 if is_nsfw else 0,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return self._default_result(note=str(e))
    
    def analyze_batch(self, image_paths: List[Union[str, Path]]) -> List[Dict]:
        """
        Analyze multiple images.
        """
        # Sequential for now to be safe, pipeline handles batches but needs list of images
        results = []
        for image_path in image_paths:
            result = self.analyze_image(image_path)
            results.append(result)
        return results
    
    def _default_result(self, note: str = "") -> Dict:
        """Return default result for failed analysis"""
        return {
            "image_path": None,
            "nsfw_score": 0.0,
            "is_nsfw": False,
            "safe_score": 1.0,
            "detections": [],
            "detection_count": 0,
            "note": note
        }
    
    def check_image_quality(self, image_path: Union[str, Path]) -> Dict[str, Union[int, float]]:
        """
        Check basic image quality metrics.
        """
        try:
            img = Image.open(image_path)
            width, height = img.size
            file_size = Path(image_path).stat().st_size
            aspect_ratio = width / height if height > 0 else 0
            
            return {
                "width": width,
                "height": height,
                "aspect_ratio": round(aspect_ratio, 2),
                "resolution": f"{width}x{height}",
                "file_size_kb": round(file_size / 1024, 2)
            }
        except Exception:
            return {}


# Global instance
_image_analyzer_instance = None


def get_image_analyzer() -> ImageNSFWAnalyzer:
    """Get or create global ImageNSFWAnalyzer instance"""
    global _image_analyzer_instance
    if _image_analyzer_instance is None:
        _image_analyzer_instance = ImageNSFWAnalyzer()
    return _image_analyzer_instance


if __name__ == "__main__":
    # verification
    import sys
    
    print("Initializing logic...")
    analyzer = ImageNSFWAnalyzer()
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print(f"\nAnalyzing: {img_path}")
        res = analyzer.analyze_image(img_path)
        print(f"NSFW Score: {res['nsfw_score']:.4f}")
        print(f"Is NSFW: {res['is_nsfw']}")
        print(f"Details: {res['detections']}")
    else:
        print("Usage: python src/models/image_nsfw.py <path_to_image>")

