<<<<<<< HEAD
"""
Preprocess Apify JSON data into structured format.
Validates, cleans, and normalizes Instagram post data.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Keep emojis but normalize them
    # (Optional: could remove emojis with re.sub(r'[^\x00-\x7F]+', '', text))
    
    return text


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    if not text:
        return []
    return re.findall(r'#(\w+)', text)


def extract_mentions(text: str) -> List[str]:
    """Extract mentions from text"""
    if not text:
        return []
    return re.findall(r'@(\w+)', text)


def count_urls(text: str) -> int:
    """Count URLs in text"""
    if not text:
        return 0
    return len(re.findall(r'https?://\S+', text))


def extract_comments(post: dict) -> str:
    """
    Extract and combine all comments from a post.
    
    Args:
        post: Post dictionary
    
    Returns:
        Combined comments text
    """
    all_comments = []
    
    # First comment
    first_comment = post.get("firstComment")
    if isinstance(first_comment, str) and first_comment:
        all_comments.append(clean_text(first_comment))
    
    # Latest comments
    latest_comments = post.get("latestComments") or []
    if isinstance(latest_comments, list):
        for c in latest_comments:
            if isinstance(c, dict):
                txt = c.get("text")
                if txt:
                    all_comments.append(clean_text(txt))
            elif isinstance(c, str):
                all_comments.append(clean_text(c))
    
    return " ".join(all_comments)


def process_single_post(post: dict, influencer_username: str = None) -> Dict[str, Any]:
    """
    Process a single Instagram post into normalized format.
    
    Args:
        post: Raw post data from Apify
        influencer_username: Override username if needed
    
    Returns:
        Processed post dictionary
    """
    # Basic identifiers
    post_id = str(post.get("shortCode") or post.get("id") or "unknown")
    username = influencer_username or post.get("ownerUsername") or post.get("username") or ""
    
    # Content
    caption = clean_text(post.get("caption") or "")
    comments_text = extract_comments(post)
    
    # Engagement metrics
    likes = post.get("likesCount", 0)
    comments_count = post.get("commentsCount", 0)
    
    # Timestamp
    timestamp = post.get("timestamp") or post.get("takenAtTimestamp")
    if timestamp:
        try:
            # Convert to datetime if it's a string
            if isinstance(timestamp, str):
                post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                post_date = datetime.fromtimestamp(timestamp)
        except:
            post_date = None
    else:
        post_date = None
    
    # Media info
    is_video = bool(post.get("isVideo") or post.get("videoUrl"))
    has_multiple = bool(post.get("childPosts"))
    
    # Text features
    hashtags = extract_hashtags(caption)
    mentions = extract_mentions(caption)
    url_count = count_urls(caption)
    
    # Video-specific
    video_duration = post.get("videoDuration", 0) if is_video else 0
    video_view_count = post.get("videoViewCount", 0) if is_video else 0
    
    return {
        "username": username,
        "post_id": post_id,
        "caption": caption,
        "comments_text": comments_text,
        "likes": likes,
        "comments_count": comments_count,
        "timestamp": timestamp,
        "post_date": post_date,
        "is_video": is_video,
        "has_multiple_media": has_multiple,
        "video_duration": video_duration,
        "video_view_count": video_view_count,
        "hashtags": ",".join(hashtags) if hashtags else "",
        "hashtag_count": len(hashtags),
        "mentions": ",".join(mentions) if mentions else "",
        "mention_count": len(mentions),
        "url_count": url_count,
        "caption_length": len(caption),
        "comments_length": len(comments_text),
    }


def preprocess_apify_json(json_path: Path, output_csv: Path = None) -> pd.DataFrame:
    """
    Preprocess Apify scraped JSON into structured CSV.
    
    Args:
        json_path: Path to Apify JSON file
        output_csv: Output CSV path (optional)
    
    Returns:
        DataFrame with processed posts
    """
    logger.info(f"Processing {json_path.name}...")
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            posts = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise
    
    if not isinstance(posts, list):
        raise ValueError(f"Expected list of posts, got {type(posts)}")
    
    logger.info(f"Found {len(posts)} posts")
    
    # Extract username from filename (e.g., "username_6months_posts.json")
    username_match = json_path.stem.replace("_6months_posts", "")
    
    # Process each post
    processed_posts = []
    for i, post in enumerate(posts):
        if not isinstance(post, dict):
            logger.warning(f"Skipping non-dict post at index {i}")
            continue
        
        try:
            processed = process_single_post(post, username_match)
            processed_posts.append(processed)
        except Exception as e:
            logger.warning(f"Error processing post {i}: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(processed_posts)
    
    if df.empty:
        logger.warning("No valid posts found!")
        return df
    
    # Calculate engagement rate
    if "likes" in df.columns and "comments_count" in df.columns:
        df["total_engagement"] = df["likes"] + df["comments_count"]
    
    # Sort by date (newest first)
    if "post_date" in df.columns:
        df = df.sort_values("post_date", ascending=False).reset_index(drop=True)
    
    logger.info(f"Successfully processed {len(df)} posts for @{username_match}")
    
    # Save to CSV
    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv, index=False)
        logger.info(f"Saved to {output_csv}")
    
    return df


def process_all_json_files(input_dir: Path = None, output_dir: Path = None) -> Dict[str, pd.DataFrame]:
    """
    Process all Apify JSON files in a directory.
    
    Args:
        input_dir: Directory containing JSON files (defaults to RAW_DATA_DIR)
        output_dir: Output directory for CSVs (defaults to PROCESSED_DATA_DIR)
    
    Returns:
        Dictionary mapping username to DataFrame
    """
    input_dir = input_dir or RAW_DATA_DIR
    output_dir = output_dir or PROCESSED_DATA_DIR
    
    json_files = list(input_dir.glob("*_6months_posts.json"))
    
    if not json_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return {}
    
    logger.info(f"Found {len(json_files)} JSON files to process")
    
    results = {}
    for json_file in json_files:
        username = json_file.stem.replace("_6months_posts", "")
        output_csv = output_dir / f"{username}_processed.csv"
        
        try:
            df = preprocess_apify_json(json_file, output_csv)
            results[username] = df
        except Exception as e:
            logger.error(f"Failed to process {json_file.name}: {e}")
            continue
    
    logger.info(f"Successfully processed {len(results)} influencers")
    return results


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Process specific file
        json_path = Path(sys.argv[1])
        if json_path.exists():
            df = preprocess_apify_json(json_path)
            print(f"\nProcessed {len(df)} posts")
            print(df.head())
        else:
            print(f"File not found: {json_path}")
    else:
        # Process all files in raw data directory
        results = process_all_json_files()
        print(f"\nProcessed {len(results)} influencers")
=======
"""
Preprocess Apify JSON data into structured format.
Validates, cleans, and normalizes Instagram post data.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Keep emojis but normalize them
    # (Optional: could remove emojis with re.sub(r'[^\x00-\x7F]+', '', text))
    
    return text


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    if not text:
        return []
    return re.findall(r'#(\w+)', text)


def extract_mentions(text: str) -> List[str]:
    """Extract mentions from text"""
    if not text:
        return []
    return re.findall(r'@(\w+)', text)


def count_urls(text: str) -> int:
    """Count URLs in text"""
    if not text:
        return 0
    return len(re.findall(r'https?://\S+', text))


def extract_comments(post: dict) -> str:
    """
    Extract and combine all comments from a post.
    
    Args:
        post: Post dictionary
    
    Returns:
        Combined comments text
    """
    all_comments = []
    
    # First comment
    first_comment = post.get("firstComment")
    if isinstance(first_comment, str) and first_comment:
        all_comments.append(clean_text(first_comment))
    
    # Latest comments
    latest_comments = post.get("latestComments") or []
    if isinstance(latest_comments, list):
        for c in latest_comments:
            if isinstance(c, dict):
                txt = c.get("text")
                if txt:
                    all_comments.append(clean_text(txt))
            elif isinstance(c, str):
                all_comments.append(clean_text(c))
    
    return " ".join(all_comments)


def process_single_post(post: dict, influencer_username: str = None) -> Dict[str, Any]:
    """
    Process a single Instagram post into normalized format.
    
    Args:
        post: Raw post data from Apify
        influencer_username: Override username if needed
    
    Returns:
        Processed post dictionary
    """
    # Basic identifiers
    post_id = str(post.get("shortCode") or post.get("id") or "unknown")
    username = influencer_username or post.get("ownerUsername") or post.get("username") or ""
    
    # Content
    caption = clean_text(post.get("caption") or "")
    comments_text = extract_comments(post)
    
    # Engagement metrics
    likes = post.get("likesCount", 0)
    comments_count = post.get("commentsCount", 0)
    
    # Timestamp
    timestamp = post.get("timestamp") or post.get("takenAtTimestamp")
    if timestamp:
        try:
            # Convert to datetime if it's a string
            if isinstance(timestamp, str):
                post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                post_date = datetime.fromtimestamp(timestamp)
        except:
            post_date = None
    else:
        post_date = None
    
    # Media info
    is_video = bool(post.get("isVideo") or post.get("videoUrl"))
    has_multiple = bool(post.get("childPosts"))
    
    # Text features
    hashtags = extract_hashtags(caption)
    mentions = extract_mentions(caption)
    url_count = count_urls(caption)
    
    # Video-specific
    video_duration = post.get("videoDuration", 0) if is_video else 0
    video_view_count = post.get("videoViewCount", 0) if is_video else 0
    
    return {
        "username": username,
        "post_id": post_id,
        "caption": caption,
        "comments_text": comments_text,
        "likes": likes,
        "comments_count": comments_count,
        "timestamp": timestamp,
        "post_date": post_date,
        "is_video": is_video,
        "has_multiple_media": has_multiple,
        "video_duration": video_duration,
        "video_view_count": video_view_count,
        "hashtags": ",".join(hashtags) if hashtags else "",
        "hashtag_count": len(hashtags),
        "mentions": ",".join(mentions) if mentions else "",
        "mention_count": len(mentions),
        "url_count": url_count,
        "caption_length": len(caption),
        "comments_length": len(comments_text),
    }


def preprocess_apify_json(json_path: Path, output_csv: Path = None) -> pd.DataFrame:
    """
    Preprocess Apify scraped JSON into structured CSV.
    
    Args:
        json_path: Path to Apify JSON file
        output_csv: Output CSV path (optional)
    
    Returns:
        DataFrame with processed posts
    """
    logger.info(f"Processing {json_path.name}...")
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            posts = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise
    
    if not isinstance(posts, list):
        raise ValueError(f"Expected list of posts, got {type(posts)}")
    
    logger.info(f"Found {len(posts)} posts")
    
    # Extract username from filename (e.g., "username_6months_posts.json")
    username_match = json_path.stem.replace("_6months_posts", "")
    
    # Process each post
    processed_posts = []
    for i, post in enumerate(posts):
        if not isinstance(post, dict):
            logger.warning(f"Skipping non-dict post at index {i}")
            continue
        
        try:
            processed = process_single_post(post, username_match)
            processed_posts.append(processed)
        except Exception as e:
            logger.warning(f"Error processing post {i}: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(processed_posts)
    
    if df.empty:
        logger.warning("No valid posts found!")
        return df
    
    # Calculate engagement rate
    if "likes" in df.columns and "comments_count" in df.columns:
        df["total_engagement"] = df["likes"] + df["comments_count"]
    
    # Sort by date (newest first)
    if "post_date" in df.columns:
        df = df.sort_values("post_date", ascending=False).reset_index(drop=True)
    
    logger.info(f"Successfully processed {len(df)} posts for @{username_match}")
    
    # Save to CSV
    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv, index=False)
        logger.info(f"Saved to {output_csv}")
    
    return df


def process_all_json_files(input_dir: Path = None, output_dir: Path = None) -> Dict[str, pd.DataFrame]:
    """
    Process all Apify JSON files in a directory.
    
    Args:
        input_dir: Directory containing JSON files (defaults to RAW_DATA_DIR)
        output_dir: Output directory for CSVs (defaults to PROCESSED_DATA_DIR)
    
    Returns:
        Dictionary mapping username to DataFrame
    """
    input_dir = input_dir or RAW_DATA_DIR
    output_dir = output_dir or PROCESSED_DATA_DIR
    
    json_files = list(input_dir.glob("*_6months_posts.json"))
    
    if not json_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return {}
    
    logger.info(f"Found {len(json_files)} JSON files to process")
    
    results = {}
    for json_file in json_files:
        username = json_file.stem.replace("_6months_posts", "")
        output_csv = output_dir / f"{username}_processed.csv"
        
        try:
            df = preprocess_apify_json(json_file, output_csv)
            results[username] = df
        except Exception as e:
            logger.error(f"Failed to process {json_file.name}: {e}")
            continue
    
    logger.info(f"Successfully processed {len(results)} influencers")
    return results


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Process specific file
        json_path = Path(sys.argv[1])
        if json_path.exists():
            df = preprocess_apify_json(json_path)
            print(f"\nProcessed {len(df)} posts")
            print(df.head())
        else:
            print(f"File not found: {json_path}")
    else:
        # Process all files in raw data directory
        results = process_all_json_files()
        print(f"\nProcessed {len(results)} influencers")
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
