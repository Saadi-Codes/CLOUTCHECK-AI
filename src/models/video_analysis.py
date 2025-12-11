<<<<<<< HEAD
"""
Video content analysis combining frame-based image analysis.
Processes extracted frames through image models.
"""

from typing import List, Dict, Union
from pathlib import Path
import numpy as np

from src.data_prep.video_processor import process_video, get_video_info
from src.models.image_nsfw import get_image_analyzer
from src.models.audio_analysis import get_audio_analyzer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VideoAnalyzer:
    """Video content analysis using frame and audio extraction"""
    
    def __init__(self):
        logger.info("Initializing VideoAnalyzer")
        self.image_analyzer = get_image_analyzer()
        self.audio_analyzer = get_audio_analyzer()
    
    def analyze_video(
        self,
        video_path: Union[str, Path],
        analyze_frames: bool = True,
        analyze_audio: bool = True,
        max_frames: int = None
    ) -> Dict:
        """
        Comprehensive video analysis.
        
        Args:
            video_path: Path to video file
            analyze_frames: Whether to analyze extracted frames
            analyze_audio: Whether to transcribe and analyze audio
            max_frames: Maximum frames to analyze (None = all)
        
        Returns:
            Dictionary with complete video analysis
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            logger.error(f"Video not found: {video_path}")
            return self._default_result()
        
        logger.info(f"Analyzing video: {video_path.name}")
        
        # Get video info
        video_info = get_video_info(video_path)
        
        # Process video (extract frames and audio)
        processed = process_video(
            video_path,
            extract_frames_flag=analyze_frames,
            extract_audio_flag=analyze_audio
        )
        
        result = {
            "video_path": str(video_path),
            "video_info": video_info,
            "processed": processed["success"],
            "frame_analysis": None,
            "audio_analysis": None
        }
        
        # Analyze frames
        if analyze_frames and processed.get("frames"):
            frame_paths = [Path(f) for f in processed["frames"]]
            
            # Limit number of frames if specified
            if max_frames:
                frame_paths = frame_paths[:max_frames]
            
            logger.info(f"Analyzing {len(frame_paths)} frames...")
            frame_results = self.image_analyzer.analyze_batch(frame_paths)
            
            # Aggregate frame scores
            frame_analysis = self._aggregate_frame_scores(frame_results)
            result["frame_analysis"] = frame_analysis
        
        # Analyze audio
        if analyze_audio and processed.get("audio"):
            audio_path = Path(processed["audio"])
            logger.info(f"Analyzing audio from {audio_path.name}...")
            
            audio_result = self.audio_analyzer.analyze_audio_with_text_model(audio_path)
            result["audio_analysis"] = audio_result
        
        return result
    
    def _aggregate_frame_scores(self, frame_results: List[Dict]) -> Dict:
        """
        Aggregate scores from multiple frames.
        
        Args:
            frame_results: List of frame analysis results
        
        Returns:
            Aggregated scores
        """
        if not frame_results:
            return {
                "avg_nsfw_score": 0.0,
                "max_nsfw_score": 0.0,
                "nsfw_frame_count": 0,
                "total_frames": 0,
                "nsfw_ratio": 0.0
            }
        
        nsfw_scores = [r["nsfw_score"] for r in frame_results]
        is_nsfw_list = [r["is_nsfw"] for r in frame_results]
        
        return {
            "avg_nsfw_score": float(np.mean(nsfw_scores)),
            "max_nsfw_score": float(np.max(nsfw_scores)),
            "min_nsfw_score": float(np.min(nsfw_scores)),
            "nsfw_frame_count": sum(is_nsfw_list),
            "total_frames": len(frame_results),
            "nsfw_ratio": sum(is_nsfw_list) / len(is_nsfw_list) if is_nsfw_list else 0.0,
            "frame_scores": nsfw_scores
        }
    
    def _default_result(self) -> Dict:
        """Return default result for failed analysis"""
        return {
            "video_path": None,
            "video_info": None,
            "processed": False,
            "frame_analysis": None,
            "audio_analysis": None
        }


# Global instance
_video_analyzer_instance = None


def get_video_analyzer() -> VideoAnalyzer:
    """Get or create global VideoAnalyzer instance"""
    global _video_analyzer_instance
    if _video_analyzer_instance is None:
        _video_analyzer_instance = VideoAnalyzer()
    return _video_analyzer_instance


if __name__ == "__main__":
    # Test video analyzer
    import sys
    
    if len(sys.argv) > 1:
        video_file = Path(sys.argv[1])
        if video_file.exists():
            analyzer = VideoAnalyzer()
            
            print("\n" + "="*70)
            print(f"VIDEO ANALYSIS TEST: {video_file.name}")
            print("="*70)
            
            result = analyzer.analyze_video(video_file, max_frames=10)
            
            # Video info
            if result["video_info"]:
                info = result["video_info"]
                print(f"\nVideo Info:")
                print(f"  Duration: {info['duration']:.1f}s")
                print(f"  FPS: {info['fps']:.1f}")
                print(f"  Resolution: {info['resolution']}")
            
            # Frame analysis
            if result["frame_analysis"]:
                fa = result["frame_analysis"]
                print(f"\nFrame Analysis:")
                print(f"  Frames analyzed: {fa['total_frames']}")
                print(f"  Avg NSFW score: {fa['avg_nsfw_score']:.3f}")
                print(f"  Max NSFW score: {fa['max_nsfw_score']:.3f}")
                print(f"  NSFW ratio: {fa['nsfw_ratio']:.1%}")
            
            # Audio analysis
            if result["audio_analysis"]:
                aa = result["audio_analysis"]
                print(f"\nAudio Analysis:")
                print(f"  Language: {aa['language']}")
                print(f"  Words: {aa['word_count']}")
                if aa.get("text_analysis"):
                    ta = aa["text_analysis"]
                    print(f"  Toxicity: {ta['toxicity']:.3f}")
                    print(f"  Sentiment: {ta['sentiment_label']}")
        else:
            print(f"Video file not found: {video_file}")
    else:
        print("Usage: python video_analysis.py <video_file>")
=======
"""
Video content analysis combining frame-based image analysis.
Processes extracted frames through image models.
"""

from typing import List, Dict, Union
from pathlib import Path
import numpy as np

from src.data_prep.video_processor import process_video, get_video_info
from src.models.image_nsfw import get_image_analyzer
from src.models.audio_analysis import get_audio_analyzer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VideoAnalyzer:
    """Video content analysis using frame and audio extraction"""
    
    def __init__(self):
        logger.info("Initializing VideoAnalyzer")
        self.image_analyzer = get_image_analyzer()
        self.audio_analyzer = get_audio_analyzer()
    
    def analyze_video(
        self,
        video_path: Union[str, Path],
        analyze_frames: bool = True,
        analyze_audio: bool = True,
        max_frames: int = None
    ) -> Dict:
        """
        Comprehensive video analysis.
        
        Args:
            video_path: Path to video file
            analyze_frames: Whether to analyze extracted frames
            analyze_audio: Whether to transcribe and analyze audio
            max_frames: Maximum frames to analyze (None = all)
        
        Returns:
            Dictionary with complete video analysis
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            logger.error(f"Video not found: {video_path}")
            return self._default_result()
        
        logger.info(f"Analyzing video: {video_path.name}")
        
        # Get video info
        video_info = get_video_info(video_path)
        
        # Process video (extract frames and audio)
        processed = process_video(
            video_path,
            extract_frames_flag=analyze_frames,
            extract_audio_flag=analyze_audio
        )
        
        result = {
            "video_path": str(video_path),
            "video_info": video_info,
            "processed": processed["success"],
            "frame_analysis": None,
            "audio_analysis": None
        }
        
        # Analyze frames
        if analyze_frames and processed.get("frames"):
            frame_paths = [Path(f) for f in processed["frames"]]
            
            # Limit number of frames if specified
            if max_frames:
                frame_paths = frame_paths[:max_frames]
            
            logger.info(f"Analyzing {len(frame_paths)} frames...")
            frame_results = self.image_analyzer.analyze_batch(frame_paths)
            
            # Aggregate frame scores
            frame_analysis = self._aggregate_frame_scores(frame_results)
            result["frame_analysis"] = frame_analysis
        
        # Analyze audio
        if analyze_audio and processed.get("audio"):
            audio_path = Path(processed["audio"])
            logger.info(f"Analyzing audio from {audio_path.name}...")
            
            audio_result = self.audio_analyzer.analyze_audio_with_text_model(audio_path)
            result["audio_analysis"] = audio_result
        
        return result
    
    def _aggregate_frame_scores(self, frame_results: List[Dict]) -> Dict:
        """
        Aggregate scores from multiple frames.
        
        Args:
            frame_results: List of frame analysis results
        
        Returns:
            Aggregated scores
        """
        if not frame_results:
            return {
                "avg_nsfw_score": 0.0,
                "max_nsfw_score": 0.0,
                "nsfw_frame_count": 0,
                "total_frames": 0,
                "nsfw_ratio": 0.0
            }
        
        nsfw_scores = [r["nsfw_score"] for r in frame_results]
        is_nsfw_list = [r["is_nsfw"] for r in frame_results]
        
        return {
            "avg_nsfw_score": float(np.mean(nsfw_scores)),
            "max_nsfw_score": float(np.max(nsfw_scores)),
            "min_nsfw_score": float(np.min(nsfw_scores)),
            "nsfw_frame_count": sum(is_nsfw_list),
            "total_frames": len(frame_results),
            "nsfw_ratio": sum(is_nsfw_list) / len(is_nsfw_list) if is_nsfw_list else 0.0,
            "frame_scores": nsfw_scores
        }
    
    def _default_result(self) -> Dict:
        """Return default result for failed analysis"""
        return {
            "video_path": None,
            "video_info": None,
            "processed": False,
            "frame_analysis": None,
            "audio_analysis": None
        }


# Global instance
_video_analyzer_instance = None


def get_video_analyzer() -> VideoAnalyzer:
    """Get or create global VideoAnalyzer instance"""
    global _video_analyzer_instance
    if _video_analyzer_instance is None:
        _video_analyzer_instance = VideoAnalyzer()
    return _video_analyzer_instance


if __name__ == "__main__":
    # Test video analyzer
    import sys
    
    if len(sys.argv) > 1:
        video_file = Path(sys.argv[1])
        if video_file.exists():
            analyzer = VideoAnalyzer()
            
            print("\n" + "="*70)
            print(f"VIDEO ANALYSIS TEST: {video_file.name}")
            print("="*70)
            
            result = analyzer.analyze_video(video_file, max_frames=10)
            
            # Video info
            if result["video_info"]:
                info = result["video_info"]
                print(f"\nVideo Info:")
                print(f"  Duration: {info['duration']:.1f}s")
                print(f"  FPS: {info['fps']:.1f}")
                print(f"  Resolution: {info['resolution']}")
            
            # Frame analysis
            if result["frame_analysis"]:
                fa = result["frame_analysis"]
                print(f"\nFrame Analysis:")
                print(f"  Frames analyzed: {fa['total_frames']}")
                print(f"  Avg NSFW score: {fa['avg_nsfw_score']:.3f}")
                print(f"  Max NSFW score: {fa['max_nsfw_score']:.3f}")
                print(f"  NSFW ratio: {fa['nsfw_ratio']:.1%}")
            
            # Audio analysis
            if result["audio_analysis"]:
                aa = result["audio_analysis"]
                print(f"\nAudio Analysis:")
                print(f"  Language: {aa['language']}")
                print(f"  Words: {aa['word_count']}")
                if aa.get("text_analysis"):
                    ta = aa["text_analysis"]
                    print(f"  Toxicity: {ta['toxicity']:.3f}")
                    print(f"  Sentiment: {ta['sentiment_label']}")
        else:
            print(f"Video file not found: {video_file}")
    else:
        print("Usage: python video_analysis.py <video_file>")
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
