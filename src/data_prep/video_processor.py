"""
Video processing utilities for extracting frames and audio.
Optimized for CPU-based processing with ffmpeg.
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
import cv2
import numpy as np
from tqdm import tqdm

from src.config import VIDEO_FPS_SAMPLE, DATASET_DIR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg is available"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_info(video_path: Path) -> Optional[dict]:
    """
    Get video metadata using OpenCV.
    
    Args:
        video_path: Path to video file
    
    Returns:
       Dictionary with duration, fps, resolution, frame_count
    """
    try:
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "duration": duration,
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}"
        }
    except Exception as e:
        logger.error(f"Error getting video info for {video_path}: {e}")
        return None


def extract_frames(
    video_path: Path,
    output_dir: Path,
    sample_rate: int = None,
    max_frames: int = None
) -> List[Path]:
    """
    Extract frames from video at specified sample rate.
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save extracted frames
        sample_rate: Frames per second to extract (defaults to VIDEO_FPS_SAMPLE)
        max_frames: Maximum number of frames to extract
    
    Returns:
        List of paths to extracted frame images
    """
    sample_rate = sample_rate or VIDEO_FPS_SAMPLE
    output_dir.mkdir(parents=True, exist_ok=True)
    
    video_name = video_path.stem
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate frame interval
    if fps > 0:
        frame_interval = int(fps / sample_rate)
    else:
        frame_interval = 1
    
    logger.info(f"Extracting frames from {video_name} (FPS: {fps:.1f}, interval: {frame_interval})")
    
    extracted_frames = []
    frame_idx = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Sample every N frames
        if frame_idx % frame_interval == 0:
            output_path = output_dir / f"{video_name}_frame_{saved_count:04d}.jpg"
            cv2.imwrite(str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            extracted_frames.append(output_path)
            saved_count += 1
            
            if max_frames and saved_count >= max_frames:
                break
        
        frame_idx += 1
    
    cap.release()
    logger.info(f"Extracted {len(extracted_frames)} frames from {video_name}")
    
    return extracted_frames


def extract_thumbnail(video_path: Path, output_path: Path = None, time_offset: float = 0.5) -> Optional[Path]:
    """
    Extract a single thumbnail from video at specified time offset.
    
    Args:
        video_path: Path to video file
        output_path: Output image path
        time_offset: Time offset in seconds (or fraction 0-1 of video duration)
    
    Returns:
        Path to thumbnail image or None if failed
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return None
    
    # If time_offset is between 0 and 1, treat as fraction
    if 0 < time_offset < 1:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        time_offset = duration * time_offset
    
    # Set frame position
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(time_offset * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        logger.error(f"Failed to extract thumbnail from {video_path}")
        return None
    
    # Default output path
    if output_path is None:
        output_path = video_path.with_suffix('.jpg')
    
    cv2.imwrite(str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    logger.debug(f"Saved thumbnail: {output_path}")
    
    return output_path


def extract_audio(video_path: Path, output_path: Path = None) -> Optional[Path]:
    """
    Extract audio from video using ffmpeg.
    
    Args:
        video_path: Path to video file
        output_path: Output audio path (WAV format)
    
    Returns:
        Path to audio file or None if failed
    """
    if not check_ffmpeg_installed():
        logger.error("ffmpeg not installed! Cannot extract audio.")
        return None
    
    # Default output path
    if output_path is None:
        output_path = video_path.with_suffix('.wav')
    
    try:
        # Extract audio as WAV (compatible with Whisper)
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM 16-bit
            "-ar", "16000",  # 16kHz sample rate (Whisper requirement)
            "-ac", "1",  # Mono
            "-y",  # Overwrite
            str(output_path)
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        if output_path.exists():
            logger.debug(f"Extracted audio: {output_path}")
            return output_path
        else:
            logger.error("Audio extraction failed (no output file)")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg failed: {e.stderr.decode()}")
        return None
    except Exception as e:
        logger.error(f"Error extracting audio from {video_path}: {e}")
        return None


def process_video(
    video_path: Path,
    extract_frames_flag: bool = True,
    extract_audio_flag: bool = True,
    output_dir: Path = None
) -> dict:
    """
    Comprehensive video processing: extract frames and audio.
    
    Args:
        video_path: Path to video file
        extract_frames_flag: Whether to extract frames
        extract_audio_flag: Whether to extract audio
        output_dir: Output directory (defaults to temp directory)
    
    Returns:
        Dictionary with processing results
    """
    if output_dir is None:
        output_dir = DATASET_DIR / "temp_video_frames"
        output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "video_path": str(video_path),
        "success": False,
        "frames": [],
        "thumbnail": None,
        "audio": None,
        "info": None
    }
    
    # Get video info
    info = get_video_info(video_path)
    results["info"] = info
    
    if not info:
        logger.error(f"Could not get info for {video_path}")
        return results
    
    # Extract thumbnail (always)
    thumbnail_path = output_dir / f"{video_path.stem}_thumb.jpg"
    thumbnail = extract_thumbnail(video_path, thumbnail_path, time_offset=0.3)
    results["thumbnail"] = str(thumbnail) if thumbnail else None
    
    # Extract frames
    if extract_frames_flag:
        frames_dir = output_dir / video_path.stem
        frames = extract_frames(video_path, frames_dir)
        results["frames"] = [str(f) for f in frames]
    
    # Extract audio
    if extract_audio_flag:
        audio_path = output_dir / f"{video_path.stem}.wav"
        audio = extract_audio(video_path, audio_path)
        results["audio"] = str(audio) if audio else None
    
    results["success"] = True
    return results


if __name__ == "__main__":
    # Test video processing
    import sys
    
    if len(sys.argv) > 1:
        video_file = Path(sys.argv[1])
        if video_file.exists():
            print(f"Processing {video_file}...")
            result = process_video(video_file)
            print(f"Success: {result['success']}")
            print(f"Frames extracted: {len(result['frames'])}")
            print(f"Audio: {result['audio']}")
            print(f"Info: {result['info']}")
        else:
            print(f"Video file not found: {video_file}")
    else:
        print("Usage: python video_processor.py <video_file>")
