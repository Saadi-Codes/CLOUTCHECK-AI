<<<<<<< HEAD
"""
Storage optimization utilities for CloutCheck AI.
Handles temporary media cleanup, compression, and disk space management.
"""

import shutil
from pathlib import Path
from typing import List, Optional
import pandas as pd

from src.config import (
    DATASET_DIR, IMAGES_DIR, VIDEOS_DIR, 
    CLEANUP_MEDIA, COMPRESS_METADATA
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def get_directory_size(path: Path) -> int:
    """
    Calculate total size of directory in bytes.
    
    Args:
        path: Directory path
    
    Returns:
        Size in bytes
    """
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except Exception as e:
        logger.warning(f"Error calculating size of {path}: {e}")
    return total


def format_bytes(bytes_size: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def cleanup_media_files(keep_thumbnails: bool = True) -> dict:
    """
    Clean up downloaded media files to save storage.
    
    Args:
        keep_thumbnails: If True, keep thumbnail images
    
    Returns:
        Dictionary with cleanup statistics
    """
    if not CLEANUP_MEDIA:
        logger.info("Media cleanup disabled in config")
        return {"cleaned": False}
    
    stats = {
        "images_deleted": 0,
        "videos_deleted": 0,
        "space_freed": 0
    }
    
    # Clean up videos
    if VIDEOS_DIR.exists():
        video_size = get_directory_size(VIDEOS_DIR)
        video_files = list(VIDEOS_DIR.glob("*.mp4"))
        
        for video_file in video_files:
            try:
                video_file.unlink()
                stats["videos_deleted"] += 1
            except Exception as e:
                logger.warning(f"Failed to delete {video_file}: {e}")
        
        stats["space_freed"] += video_size
        logger.info(f"Deleted {stats['videos_deleted']} videos, freed {format_bytes(video_size)}")
    
    # Clean up images (optionally keep thumbnails)
    if IMAGES_DIR.exists() and not keep_thumbnails:
        image_size = get_directory_size(IMAGES_DIR)
        image_files = list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png"))
        
        for image_file in image_files:
            try:
                image_file.unlink()
                stats["images_deleted"] += 1
            except Exception as e:
                logger.warning(f"Failed to delete {image_file}: {e}")
        
        stats["space_freed"] += image_size
        logger.info(f"Deleted {stats['images_deleted']} images, freed {format_bytes(image_size)}")
    
    stats["cleaned"] = True
    stats["total_freed_readable"] = format_bytes(stats["space_freed"])
    
    logger.info(f"Total space freed: {stats['total_freed_readable']}")
    stats["cleaned"] = True
    stats["total_freed_readable"] = format_bytes(stats["space_freed"])
    
    logger.info(f"Total space freed: {stats['total_freed_readable']}")
    return stats


def cleanup_file(file_path: Path):
    """
    Safely delete a single file.
    
    Args:
        file_path: Path to file to delete
    """
    try:
        if file_path.exists():
            size = file_path.stat().st_size
            file_path.unlink()
            logger.debug(f"Deleted {file_path.name} ({format_bytes(size)})")
            return True
    except Exception as e:
        logger.warning(f"Failed to delete {file_path}: {e}")
    return False


def save_metadata(df: pd.DataFrame, output_path: Path, compress: bool = None):
    """
    Save metadata with optional compression.
    
    Args:
        df: DataFrame to save
        output_path: Output file path
        compress: Use compression (defaults to COMPRESS_METADATA config)
    """
    compress = compress if compress is not None else COMPRESS_METADATA
    
    if compress and output_path.suffix == '.csv':
        # Use Parquet for better compression
        parquet_path = output_path.with_suffix('.parquet')
        df.to_parquet(parquet_path, index=False, compression='gzip')
        logger.info(f"Saved compressed metadata to {parquet_path}")
        
        # Also save CSV for compatibility
        df.to_csv(output_path, index=False)
        logger.info(f"Saved CSV metadata to {output_path}")
    else:
        df.to_csv(output_path, index=False)
        logger.info(f"Saved metadata to {output_path}")


def load_metadata(metadata_path: Path) -> pd.DataFrame:
    """
    Load metadata from CSV or Parquet.
    
    Args:
        metadata_path: Path to metadata file
    
    Returns:
        DataFrame
    """
    parquet_path = metadata_path.with_suffix('.parquet')
    
    if parquet_path.exists():
        logger.info(f"Loading compressed metadata from {parquet_path}")
        return pd.read_parquet(parquet_path)
    elif metadata_path.exists():
        logger.info(f"Loading metadata from {metadata_path}")
        return pd.read_csv(metadata_path)
    else:
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")


def create_temp_directory(base_name: str) -> Path:
    """
    Create a temporary directory for processing.
    
    Args:
        base_name: Base name for the temp directory
    
    Returns:
        Path to created directory
    """
    temp_dir = DATASET_DIR / f"temp_{base_name}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created temp directory: {temp_dir}")
    return temp_dir


def cleanup_temp_directory(temp_dir: Path):
    """
    Remove temporary directory and its contents.
    
    Args:
        temp_dir: Directory to remove
    """
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Removed temp directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove temp directory {temp_dir}: {e}")


def get_disk_usage_report() -> dict:
    """
    Get disk usage statistics for CloutCheck directories.
    
    Returns:
        Dictionary with size information
    """
    report = {}
    
    for name, path in [
        ("Images", IMAGES_DIR),
        ("Videos", VIDEOS_DIR),
        ("Dataset Total", DATASET_DIR),
    ]:
        if path.exists():
            size = get_directory_size(path)
            report[name] = {
                "bytes": size,
                "readable": format_bytes(size)
            }
    
    return report


def print_storage_report():
    """Print a formatted storage usage report"""
    logger.info("=" * 50)
    logger.info("STORAGE USAGE REPORT")
    logger.info("=" * 50)
    
    report = get_disk_usage_report()
    for name, data in report.items():
        logger.info(f"{name:.<30} {data['readable']:>15}")
    
    logger.info("=" * 50)
=======
"""
Storage optimization utilities for CloutCheck AI.
Handles temporary media cleanup, compression, and disk space management.
"""

import shutil
from pathlib import Path
from typing import List, Optional
import pandas as pd

from src.config import (
    DATASET_DIR, IMAGES_DIR, VIDEOS_DIR, 
    CLEANUP_MEDIA, COMPRESS_METADATA
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def get_directory_size(path: Path) -> int:
    """
    Calculate total size of directory in bytes.
    
    Args:
        path: Directory path
    
    Returns:
        Size in bytes
    """
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except Exception as e:
        logger.warning(f"Error calculating size of {path}: {e}")
    return total


def format_bytes(bytes_size: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def cleanup_media_files(keep_thumbnails: bool = True) -> dict:
    """
    Clean up downloaded media files to save storage.
    
    Args:
        keep_thumbnails: If True, keep thumbnail images
    
    Returns:
        Dictionary with cleanup statistics
    """
    if not CLEANUP_MEDIA:
        logger.info("Media cleanup disabled in config")
        return {"cleaned": False}
    
    stats = {
        "images_deleted": 0,
        "videos_deleted": 0,
        "space_freed": 0
    }
    
    # Clean up videos
    if VIDEOS_DIR.exists():
        video_size = get_directory_size(VIDEOS_DIR)
        video_files = list(VIDEOS_DIR.glob("*.mp4"))
        
        for video_file in video_files:
            try:
                video_file.unlink()
                stats["videos_deleted"] += 1
            except Exception as e:
                logger.warning(f"Failed to delete {video_file}: {e}")
        
        stats["space_freed"] += video_size
        logger.info(f"Deleted {stats['videos_deleted']} videos, freed {format_bytes(video_size)}")
    
    # Clean up images (optionally keep thumbnails)
    if IMAGES_DIR.exists() and not keep_thumbnails:
        image_size = get_directory_size(IMAGES_DIR)
        image_files = list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png"))
        
        for image_file in image_files:
            try:
                image_file.unlink()
                stats["images_deleted"] += 1
            except Exception as e:
                logger.warning(f"Failed to delete {image_file}: {e}")
        
        stats["space_freed"] += image_size
        logger.info(f"Deleted {stats['images_deleted']} images, freed {format_bytes(image_size)}")
    
    stats["cleaned"] = True
    stats["total_freed_readable"] = format_bytes(stats["space_freed"])
    
    logger.info(f"Total space freed: {stats['total_freed_readable']}")
    stats["cleaned"] = True
    stats["total_freed_readable"] = format_bytes(stats["space_freed"])
    
    logger.info(f"Total space freed: {stats['total_freed_readable']}")
    return stats


def cleanup_file(file_path: Path):
    """
    Safely delete a single file.
    
    Args:
        file_path: Path to file to delete
    """
    try:
        if file_path.exists():
            size = file_path.stat().st_size
            file_path.unlink()
            logger.debug(f"Deleted {file_path.name} ({format_bytes(size)})")
            return True
    except Exception as e:
        logger.warning(f"Failed to delete {file_path}: {e}")
    return False


def save_metadata(df: pd.DataFrame, output_path: Path, compress: bool = None):
    """
    Save metadata with optional compression.
    
    Args:
        df: DataFrame to save
        output_path: Output file path
        compress: Use compression (defaults to COMPRESS_METADATA config)
    """
    compress = compress if compress is not None else COMPRESS_METADATA
    
    if compress and output_path.suffix == '.csv':
        # Use Parquet for better compression
        parquet_path = output_path.with_suffix('.parquet')
        df.to_parquet(parquet_path, index=False, compression='gzip')
        logger.info(f"Saved compressed metadata to {parquet_path}")
        
        # Also save CSV for compatibility
        df.to_csv(output_path, index=False)
        logger.info(f"Saved CSV metadata to {output_path}")
    else:
        df.to_csv(output_path, index=False)
        logger.info(f"Saved metadata to {output_path}")


def load_metadata(metadata_path: Path) -> pd.DataFrame:
    """
    Load metadata from CSV or Parquet.
    
    Args:
        metadata_path: Path to metadata file
    
    Returns:
        DataFrame
    """
    parquet_path = metadata_path.with_suffix('.parquet')
    
    if parquet_path.exists():
        logger.info(f"Loading compressed metadata from {parquet_path}")
        return pd.read_parquet(parquet_path)
    elif metadata_path.exists():
        logger.info(f"Loading metadata from {metadata_path}")
        return pd.read_csv(metadata_path)
    else:
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")


def create_temp_directory(base_name: str) -> Path:
    """
    Create a temporary directory for processing.
    
    Args:
        base_name: Base name for the temp directory
    
    Returns:
        Path to created directory
    """
    temp_dir = DATASET_DIR / f"temp_{base_name}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created temp directory: {temp_dir}")
    return temp_dir


def cleanup_temp_directory(temp_dir: Path):
    """
    Remove temporary directory and its contents.
    
    Args:
        temp_dir: Directory to remove
    """
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Removed temp directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove temp directory {temp_dir}: {e}")


def get_disk_usage_report() -> dict:
    """
    Get disk usage statistics for CloutCheck directories.
    
    Returns:
        Dictionary with size information
    """
    report = {}
    
    for name, path in [
        ("Images", IMAGES_DIR),
        ("Videos", VIDEOS_DIR),
        ("Dataset Total", DATASET_DIR),
    ]:
        if path.exists():
            size = get_directory_size(path)
            report[name] = {
                "bytes": size,
                "readable": format_bytes(size)
            }
    
    return report


def print_storage_report():
    """Print a formatted storage usage report"""
    logger.info("=" * 50)
    logger.info("STORAGE USAGE REPORT")
    logger.info("=" * 50)
    
    report = get_disk_usage_report()
    for name, data in report.items():
        logger.info(f"{name:.<30} {data['readable']:>15}")
    
    logger.info("=" * 50)
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
