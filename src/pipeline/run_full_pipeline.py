<<<<<<< HEAD
"""
Main pipeline orchestration for CloutCheck AI.
Runs complete influencer reputation analysis from scraped data.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List
from tqdm import tqdm

from src.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR,
    DATASET_DIR, CLEANUP_MEDIA, CLEANUP_MODE
)
from src.utils.logger import setup_logger, log_section
from src.utils.storage import cleanup_media_files, print_storage_report, cleanup_file
from src.data_prep.preprocess_apify_json import preprocess_apify_json
from src.models.text_toxicity import get_text_analyzer
from src.models.image_nsfw import get_image_analyzer
from src.models.video_analysis import get_video_analyzer
from src.brand_fit.brand_analyzer import BrandFitAnalyzer
from Converter import main as convert_media

logger = setup_logger(__name__)


def analyze_influencer_posts(username: str) -> Dict:
    """
    Run complete analysis pipeline for an influencer.
    
    Args:
        username: Instagram username
    
    Returns:
        Dictionary with comprehensive analysis results
    """
    log_section(logger, f"Analyzing @{username}")
    
    # Load processed posts
    processed_csv = PROCESSED_DATA_DIR / f"{username}_processed.csv"
    
    if not processed_csv.exists():
        logger.error(f"Processed data not found: {processed_csv}")
        logger.info("Please run data preprocessing first")
        return None
    
    df = pd.read_csv(processed_csv)
    logger.info(f"Loaded {len(df)} posts for @{username}")
    
    # Initialize analyzers
    text_analyzer = get_text_analyzer()
    image_analyzer = get_image_analyzer()
    
    # Analyze text content (captions + comments)
    logger.info("Analyzing text content...")
    text_results = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Text analysis"):
        # Combine caption and comments
        caption = row.get("caption", "") or ""
        comments = row.get("comments_text", "") or ""
        combined_text = f"{caption} {comments}".strip()
        
        if combined_text:
            try:
                result = text_analyzer.analyze_text(combined_text)
                spam = text_analyzer.detect_spam_patterns(combined_text)
                
                text_results.append({
                    "post_id": row["post_id"],
                    "toxicity": result["toxicity"],
                    "severe_toxicity": result.get("severe_toxicity", 0),
                    "identity_attack": result.get("identity_attack", 0),
                    "insult": result.get("insult", 0),
                    "sentiment_score": result["sentiment_score"],
                    "spam_score": spam["spam_score"]
                })
            except Exception as e:
                logger.warning(f"Text analysis failed for post {row['post_id']}: {e}")
                continue
    
    
    #Analyze images
    logger.info("Analyzing images...")
    image_results = []
    
    images_dir = DATASET_DIR / "images"
    if images_dir.exists():
        image_files = list(images_dir.glob(f"{username}_*.jpg"))
        logger.info(f"Found {len(image_files)} images")
        
        for img_path in tqdm(image_files, desc="Image analysis"):
            try:
                result = image_analyzer.analyze_image(img_path)
                image_results.append(result)
            except Exception as e:
                logger.warning(f"Image analysis failed for {img_path.name}: {e}")
                continue

    # Analyze videos (frames + audio)
    logger.info("Analyzing videos...")
    video_analyzer = get_video_analyzer()
    
    videos_dir = DATASET_DIR / "videos"
    if videos_dir.exists():
        video_files = list(videos_dir.glob(f"{username}_*.mp4"))
        logger.info(f"Found {len(video_files)} videos")
        
        for vid_path in tqdm(video_files, desc="Video analysis"):
            try:
                # Analyze video (frames + audio)
                vid_result = video_analyzer.analyze_video(vid_path)
                
                # 1. Integrate Audio Text Analysis
                if vid_result.get("audio_analysis") and vid_result["audio_analysis"].get("text_analysis"):
                    aa = vid_result["audio_analysis"]
                    ta = aa["text_analysis"]
                    spam = aa.get("spam_detection", {"spam_score": 0})
                    
                    text_results.append({
                        "post_id": vid_path.name, # Use filename as ID
                        "toxicity": ta["toxicity"],
                        "severe_toxicity": ta.get("severe_toxicity", 0),
                        "identity_attack": ta.get("identity_attack", 0),
                        "insult": ta.get("insult", 0),
                        "sentiment_score": ta["sentiment_score"],
                        "spam_score": spam["spam_score"]
                    })
                
                # 2. Integrate Frame Analysis (NSFW)
                if vid_result.get("frame_analysis"):
                    fa = vid_result["frame_analysis"]
                    # Add as a "virtual" image result representing the video
                    image_results.append({
                        "image_path": str(vid_path),
                        "nsfw_score": fa["avg_nsfw_score"],
                        "is_nsfw": fa["max_nsfw_score"] > 0.7, # Threshold check
                        "safe_score": 1.0 - fa["avg_nsfw_score"]
                    })
                
                # Immediate Cleanup (Space Efficiency)
                if CLEANUP_MODE == "immediate":
                    cleanup_file(vid_path)
                    
            except Exception as e:
                logger.warning(f"Video analysis failed for {vid_path.name}: {e}")
                continue
    
    # Calculate aggregate scores
    logger.info("Calculating aggregate scores...")
    
    avg_toxicity = sum(r["toxicity"] for r in text_results) / len(text_results) if text_results else 0
    avg_sentiment = sum(r["sentiment_score"] for r in text_results) / len(text_results) if text_results else 0
    avg_spam = sum(r["spam_score"] for r in text_results) / len(text_results) if text_results else 0
    
    avg_nsfw = sum(r["nsfw_score"] for r in image_results) / len(image_results) if image_results else 0
    nsfw_count = sum(1 for r in image_results if r["is_nsfw"]) if image_results else 0
    
    # Calculate engagement metrics
    total_likes = df["likes"].sum() if "likes" in df.columns else 0
    total_comments = df["comments_count"].sum() if "comments_count" in df.columns else 0
    avg_likes = df["likes"].mean() if "likes" in df.columns else 0
    avg_comments = df["comments_count"].mean() if "comments_count" in df.columns else 0
    
    # Calculate reputation score (0-100)
    # Higher is better: low toxicity, positive sentiment, low spam, low NSFW
    toxicity_penalty = avg_toxicity * 30
    spam_penalty = avg_spam * 20
    nsfw_penalty = avg_nsfw * 30
    sentiment_bonus = max(0, avg_sentiment) * 10
    
    # NEW: Penalize specific severe infractions (max scores)
    max_identity_attack = max((r.get("identity_attack", 0) for r in text_results), default=0)
    max_insult = max((r.get("insult", 0) for r in text_results), default=0)
    max_severe = max((r.get("severe_toxicity", 0) for r in text_results), default=0)
    
    severe_penalty = 0
    if max_identity_attack > 0.1: severe_penalty += 20
    if max_insult > 0.1: severe_penalty += 10
    if max_severe > 0.1: severe_penalty += 30
    
    reputation_score = max(0, min(100, 
        100 - toxicity_penalty - spam_penalty - nsfw_penalty - severe_penalty + sentiment_bonus
    ))
    
    # Compile results
    results = {
        "username": username,
        "analysis_date": datetime.now().isoformat(),
        "posts_analyzed": len(df),
        
        "text_analysis": {
            "avg_toxicity": round(avg_toxicity, 3),
            "avg_sentiment": round(avg_sentiment, 3),
            "avg_spam_score": round(avg_spam, 3),
            "max_identity_attack": round(max((r.get("identity_attack", 0) for r in text_results), default=0), 3),
            "max_insult": round(max((r.get("insult", 0) for r in text_results), default=0), 3),
            "max_severe_toxicity": round(max((r.get("severe_toxicity", 0) for r in text_results), default=0), 3)
        },
        
        "image_analysis": {
            "images_analyzed": len(image_results),
            "avg_nsfw_score": round(avg_nsfw, 3),
            "nsfw_images_found": nsfw_count,
            "nsfw_ratio": round(nsfw_count / len(image_results), 3) if image_results else 0
        },
        
        "engagement_metrics": {
            "total_likes": int(total_likes),
            "total_comments": int(total_comments),
            "avg_likes_per_post": round(avg_likes, 2),
            "avg_comments_per_post": round(avg_comments, 2)
        },
        
        "reputation_score": round(reputation_score, 2),
        "rating": get_rating(reputation_score)
    }
    
    # Run Brand Fit Analysis
    brand_fits = []
    brands_dir = Path("brands")
    if brands_dir.exists():
        for brand_file in brands_dir.glob("*.json"):
            try:
                analyzer = BrandFitAnalyzer(brand_file)
                fit_result = analyzer.analyze_fit(results)
                brand_fits.append(fit_result)
            except Exception as e:
                logger.error(f"Error analyzing brand fit for {brand_file.name}: {e}")
    
    results["brand_fits"] = brand_fits

    
    return results


def get_rating(score: float) -> str:
    """Convert numeric score to rating"""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 40:
        return "Poor"
    else:
        return "Very Poor"


def save_results(results: Dict, output_path: Path):
    """Save analysis results to JSON"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to: {output_path}")


def print_results_summary(results: Dict):
    """Print formatted results summary"""
    print("\n" + "="*70)
    print(f"  INFLUENCER REPUTATION REPORT: @{results['username']}")
    print("="*70)
    
    print(f"\nREPUTATION SCORE: {results['reputation_score']}/100")
    print(f"   Rating: {results['rating']}")
    
    print(f"\nText Analysis ({results['posts_analyzed']} posts):")
    ta = results['text_analysis']
    print(f"   Toxicity: {ta['avg_toxicity']:.3f}")
    print(f"   Sentiment: {ta['avg_sentiment']:.3f}")
    print(f"   Spam Score: {ta['avg_spam_score']:.3f}")
    
    print(f"\nImage Analysis ({results['image_analysis']['images_analyzed']} images):")
    ia = results['image_analysis']
    print(f"   NSFW Score: {ia['avg_nsfw_score']:.3f}")
    print(f"   Flagged Images: {ia['nsfw_images_found']}")
    
    print(f"\nEngagement:")
    em = results['engagement_metrics']
    print(f"   Total Likes: {em['total_likes']:,}")
    print(f"   Total Comments: {em['total_comments']:,}")
    print(f"   Avg Likes/Post: {em['avg_likes_per_post']:,}")
    
    if results.get("brand_fits"):
        print(f"\nBrand Fit Analysis:")
        for fit in results["brand_fits"]:
            print(f"   {fit['brand_name']}: {fit['fit_score']}/100 ({fit['rating']})")
            if fit['risk_factors']:
                print(f"     Risks: {', '.join(fit['risk_factors'][:2])}")
    
    print("\n" + "="*70)


def main():
    """Main pipeline execution"""
    log_section(logger, "CLOUTCHECK AI - FULL PIPELINE")
    
    # Check for JSON files
    json_files = list(Path(".").glob("*_posts.json"))
    
    if not json_files:
        logger.error("No *_posts.json files found")
        logger.info("\nPlease run Scraper.py first:")
        logger.info("  python Scraper.py")
        return
    
    logger.info(f"Found {len(json_files)} influencer(s) to analyze")
    
    for json_file in json_files:
        username = json_file.stem.replace("_posts", "")
        logger.info(f"\nProcessing @{username}...")
        
        try:
            # Stage 1: Preprocess JSON
            log_section(logger, f"STAGE 1: Preprocessing Data ({username})")
            output_csv = PROCESSED_DATA_DIR / f"{username}_processed.csv"
            
            # Move JSON to raw data dir
            raw_json = RAW_DATA_DIR / json_file.name
            if not raw_json.exists():
                json_file.rename(raw_json)
                logger.info(f"Moved JSON to {raw_json}")
            
            df = preprocess_apify_json(raw_json, output_csv)
            
            # Stage 2: Download media (skip if already done)
            images_dir = DATASET_DIR / "images"
            videos_dir = DATASET_DIR / "videos"
            
            # Check if media already downloaded (check for ANY media files)
            has_images = images_dir.exists() and len(list(images_dir.glob("*.jpg"))) > 0
            has_videos = videos_dir.exists() and len(list(videos_dir.glob("*.mp4"))) > 0
            
            if has_images or has_videos:
                logger.info("Media already downloaded, skipping Stage 2...")
                logger.info(f"  Images: {len(list(images_dir.glob('*.jpg')))} files")
                if videos_dir.exists():
                    logger.info(f"  Videos: {len(list(videos_dir.glob('*.mp4')))} files")
            else:
                log_section(logger, f"STAGE 2: Downloading Media ({username})")
                logger.info("Running Converter.py...")
                convert_media()
            
            # Stage 3: Run analysis
            log_section(logger, f"STAGE 3: Running AI Analysis ({username})")
            results = analyze_influencer_posts(username)
            
            if results:
                # Save results
                output_path = RESULTS_DIR / f"{username}_analysis.json"
                save_results(results, output_path)
                
                # Print summary
                print_results_summary(results)
                
                # Stage 4: Cleanup
                if CLEANUP_MEDIA:
                    log_section(logger, "STAGE 4: Cleanup")
                    cleanup_media_files(keep_thumbnails=True)
                    print_storage_report()
                
                logger.info(f"\nAnalysis complete for @{username}")
            
        except Exception as e:
            logger.error(f"Failed to analyze @{username}: {e}", exc_info=True)
            continue
    
    log_section(logger, "PIPELINE COMPLETE")
    logger.info("All influencers processed successfully!")


if __name__ == "__main__":
    main()
=======
"""
Main pipeline orchestration for CloutCheck AI.
Runs complete influencer reputation analysis from scraped data.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List
from tqdm import tqdm

from src.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR,
    DATASET_DIR, CLEANUP_MEDIA, CLEANUP_MODE
)
from src.utils.logger import setup_logger, log_section
from src.utils.storage import cleanup_media_files, print_storage_report, cleanup_file
from src.data_prep.preprocess_apify_json import preprocess_apify_json
from src.models.text_toxicity import get_text_analyzer
from src.models.image_nsfw import get_image_analyzer
from src.models.video_analysis import get_video_analyzer
from src.brand_fit.brand_analyzer import BrandFitAnalyzer
from Converter import main as convert_media

logger = setup_logger(__name__)


def analyze_influencer_posts(username: str) -> Dict:
    """
    Run complete analysis pipeline for an influencer.
    
    Args:
        username: Instagram username
    
    Returns:
        Dictionary with comprehensive analysis results
    """
    log_section(logger, f"Analyzing @{username}")
    
    # Load processed posts
    processed_csv = PROCESSED_DATA_DIR / f"{username}_processed.csv"
    
    if not processed_csv.exists():
        logger.error(f"Processed data not found: {processed_csv}")
        logger.info("Please run data preprocessing first")
        return None
    
    df = pd.read_csv(processed_csv)
    logger.info(f"Loaded {len(df)} posts for @{username}")
    
    # Initialize analyzers
    text_analyzer = get_text_analyzer()
    image_analyzer = get_image_analyzer()
    
    # Analyze text content (captions + comments)
    logger.info("Analyzing text content...")
    text_results = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Text analysis"):
        # Combine caption and comments
        caption = row.get("caption", "") or ""
        comments = row.get("comments_text", "") or ""
        combined_text = f"{caption} {comments}".strip()
        
        if combined_text:
            try:
                result = text_analyzer.analyze_text(combined_text)
                spam = text_analyzer.detect_spam_patterns(combined_text)
                
                text_results.append({
                    "post_id": row["post_id"],
                    "toxicity": result["toxicity"],
                    "severe_toxicity": result.get("severe_toxicity", 0),
                    "identity_attack": result.get("identity_attack", 0),
                    "insult": result.get("insult", 0),
                    "sentiment_score": result["sentiment_score"],
                    "spam_score": spam["spam_score"]
                })
            except Exception as e:
                logger.warning(f"Text analysis failed for post {row['post_id']}: {e}")
                continue
    
    
    #Analyze images
    logger.info("Analyzing images...")
    image_results = []
    
    images_dir = DATASET_DIR / "images"
    if images_dir.exists():
        image_files = list(images_dir.glob(f"{username}_*.jpg"))
        logger.info(f"Found {len(image_files)} images")
        
        for img_path in tqdm(image_files, desc="Image analysis"):
            try:
                result = image_analyzer.analyze_image(img_path)
                image_results.append(result)
            except Exception as e:
                logger.warning(f"Image analysis failed for {img_path.name}: {e}")
                continue

    # Analyze videos (frames + audio)
    logger.info("Analyzing videos...")
    video_analyzer = get_video_analyzer()
    
    videos_dir = DATASET_DIR / "videos"
    if videos_dir.exists():
        video_files = list(videos_dir.glob(f"{username}_*.mp4"))
        logger.info(f"Found {len(video_files)} videos")
        
        for vid_path in tqdm(video_files, desc="Video analysis"):
            try:
                # Analyze video (frames + audio)
                vid_result = video_analyzer.analyze_video(vid_path)
                
                # 1. Integrate Audio Text Analysis
                if vid_result.get("audio_analysis") and vid_result["audio_analysis"].get("text_analysis"):
                    aa = vid_result["audio_analysis"]
                    ta = aa["text_analysis"]
                    spam = aa.get("spam_detection", {"spam_score": 0})
                    
                    text_results.append({
                        "post_id": vid_path.name, # Use filename as ID
                        "toxicity": ta["toxicity"],
                        "severe_toxicity": ta.get("severe_toxicity", 0),
                        "identity_attack": ta.get("identity_attack", 0),
                        "insult": ta.get("insult", 0),
                        "sentiment_score": ta["sentiment_score"],
                        "spam_score": spam["spam_score"]
                    })
                
                # 2. Integrate Frame Analysis (NSFW)
                if vid_result.get("frame_analysis"):
                    fa = vid_result["frame_analysis"]
                    # Add as a "virtual" image result representing the video
                    image_results.append({
                        "image_path": str(vid_path),
                        "nsfw_score": fa["avg_nsfw_score"],
                        "is_nsfw": fa["max_nsfw_score"] > 0.7, # Threshold check
                        "safe_score": 1.0 - fa["avg_nsfw_score"]
                    })
                
                # Immediate Cleanup (Space Efficiency)
                if CLEANUP_MODE == "immediate":
                    cleanup_file(vid_path)
                    
            except Exception as e:
                logger.warning(f"Video analysis failed for {vid_path.name}: {e}")
                continue
    
    # Calculate aggregate scores
    logger.info("Calculating aggregate scores...")
    
    avg_toxicity = sum(r["toxicity"] for r in text_results) / len(text_results) if text_results else 0
    avg_sentiment = sum(r["sentiment_score"] for r in text_results) / len(text_results) if text_results else 0
    avg_spam = sum(r["spam_score"] for r in text_results) / len(text_results) if text_results else 0
    
    avg_nsfw = sum(r["nsfw_score"] for r in image_results) / len(image_results) if image_results else 0
    nsfw_count = sum(1 for r in image_results if r["is_nsfw"]) if image_results else 0
    
    # Calculate engagement metrics
    total_likes = df["likes"].sum() if "likes" in df.columns else 0
    total_comments = df["comments_count"].sum() if "comments_count" in df.columns else 0
    avg_likes = df["likes"].mean() if "likes" in df.columns else 0
    avg_comments = df["comments_count"].mean() if "comments_count" in df.columns else 0
    
    # Calculate reputation score (0-100)
    # Higher is better: low toxicity, positive sentiment, low spam, low NSFW
    toxicity_penalty = avg_toxicity * 30
    spam_penalty = avg_spam * 20
    nsfw_penalty = avg_nsfw * 30
    sentiment_bonus = max(0, avg_sentiment) * 10
    
    # NEW: Penalize specific severe infractions (max scores)
    max_identity_attack = max((r.get("identity_attack", 0) for r in text_results), default=0)
    max_insult = max((r.get("insult", 0) for r in text_results), default=0)
    max_severe = max((r.get("severe_toxicity", 0) for r in text_results), default=0)
    
    severe_penalty = 0
    if max_identity_attack > 0.1: severe_penalty += 20
    if max_insult > 0.1: severe_penalty += 10
    if max_severe > 0.1: severe_penalty += 30
    
    reputation_score = max(0, min(100, 
        100 - toxicity_penalty - spam_penalty - nsfw_penalty - severe_penalty + sentiment_bonus
    ))
    
    # Compile results
    results = {
        "username": username,
        "analysis_date": datetime.now().isoformat(),
        "posts_analyzed": len(df),
        
        "text_analysis": {
            "avg_toxicity": round(avg_toxicity, 3),
            "avg_sentiment": round(avg_sentiment, 3),
            "avg_spam_score": round(avg_spam, 3),
            "max_identity_attack": round(max((r.get("identity_attack", 0) for r in text_results), default=0), 3),
            "max_insult": round(max((r.get("insult", 0) for r in text_results), default=0), 3),
            "max_severe_toxicity": round(max((r.get("severe_toxicity", 0) for r in text_results), default=0), 3)
        },
        
        "image_analysis": {
            "images_analyzed": len(image_results),
            "avg_nsfw_score": round(avg_nsfw, 3),
            "nsfw_images_found": nsfw_count,
            "nsfw_ratio": round(nsfw_count / len(image_results), 3) if image_results else 0
        },
        
        "engagement_metrics": {
            "total_likes": int(total_likes),
            "total_comments": int(total_comments),
            "avg_likes_per_post": round(avg_likes, 2),
            "avg_comments_per_post": round(avg_comments, 2)
        },
        
        "reputation_score": round(reputation_score, 2),
        "rating": get_rating(reputation_score)
    }
    
    # Run Brand Fit Analysis
    brand_fits = []
    brands_dir = Path("brands")
    if brands_dir.exists():
        for brand_file in brands_dir.glob("*.json"):
            try:
                analyzer = BrandFitAnalyzer(brand_file)
                fit_result = analyzer.analyze_fit(results)
                brand_fits.append(fit_result)
            except Exception as e:
                logger.error(f"Error analyzing brand fit for {brand_file.name}: {e}")
    
    results["brand_fits"] = brand_fits

    
    return results


def get_rating(score: float) -> str:
    """Convert numeric score to rating"""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 40:
        return "Poor"
    else:
        return "Very Poor"


def save_results(results: Dict, output_path: Path):
    """Save analysis results to JSON"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to: {output_path}")


def print_results_summary(results: Dict):
    """Print formatted results summary"""
    print("\n" + "="*70)
    print(f"  INFLUENCER REPUTATION REPORT: @{results['username']}")
    print("="*70)
    
    print(f"\nREPUTATION SCORE: {results['reputation_score']}/100")
    print(f"   Rating: {results['rating']}")
    
    print(f"\nText Analysis ({results['posts_analyzed']} posts):")
    ta = results['text_analysis']
    print(f"   Toxicity: {ta['avg_toxicity']:.3f}")
    print(f"   Sentiment: {ta['avg_sentiment']:.3f}")
    print(f"   Spam Score: {ta['avg_spam_score']:.3f}")
    
    print(f"\nImage Analysis ({results['image_analysis']['images_analyzed']} images):")
    ia = results['image_analysis']
    print(f"   NSFW Score: {ia['avg_nsfw_score']:.3f}")
    print(f"   Flagged Images: {ia['nsfw_images_found']}")
    
    print(f"\nEngagement:")
    em = results['engagement_metrics']
    print(f"   Total Likes: {em['total_likes']:,}")
    print(f"   Total Comments: {em['total_comments']:,}")
    print(f"   Avg Likes/Post: {em['avg_likes_per_post']:,}")
    
    if results.get("brand_fits"):
        print(f"\nBrand Fit Analysis:")
        for fit in results["brand_fits"]:
            print(f"   {fit['brand_name']}: {fit['fit_score']}/100 ({fit['rating']})")
            if fit['risk_factors']:
                print(f"     Risks: {', '.join(fit['risk_factors'][:2])}")
    
    print("\n" + "="*70)


def main():
    """Main pipeline execution"""
    log_section(logger, "CLOUTCHECK AI - FULL PIPELINE")
    
    # Check for JSON files
    json_files = list(Path(".").glob("*_posts.json"))
    
    if not json_files:
        logger.error("No *_posts.json files found")
        logger.info("\nPlease run Scraper.py first:")
        logger.info("  python Scraper.py")
        return
    
    logger.info(f"Found {len(json_files)} influencer(s) to analyze")
    
    for json_file in json_files:
        username = json_file.stem.replace("_posts", "")
        logger.info(f"\nProcessing @{username}...")
        
        try:
            # Stage 1: Preprocess JSON
            log_section(logger, f"STAGE 1: Preprocessing Data ({username})")
            output_csv = PROCESSED_DATA_DIR / f"{username}_processed.csv"
            
            # Move JSON to raw data dir
            raw_json = RAW_DATA_DIR / json_file.name
            if not raw_json.exists():
                json_file.rename(raw_json)
                logger.info(f"Moved JSON to {raw_json}")
            
            df = preprocess_apify_json(raw_json, output_csv)
            
            # Stage 2: Download media (skip if already done)
            images_dir = DATASET_DIR / "images"
            videos_dir = DATASET_DIR / "videos"
            
            # Check if media already downloaded (check for ANY media files)
            has_images = images_dir.exists() and len(list(images_dir.glob("*.jpg"))) > 0
            has_videos = videos_dir.exists() and len(list(videos_dir.glob("*.mp4"))) > 0
            
            if has_images or has_videos:
                logger.info("Media already downloaded, skipping Stage 2...")
                logger.info(f"  Images: {len(list(images_dir.glob('*.jpg')))} files")
                if videos_dir.exists():
                    logger.info(f"  Videos: {len(list(videos_dir.glob('*.mp4')))} files")
            else:
                log_section(logger, f"STAGE 2: Downloading Media ({username})")
                logger.info("Running Converter.py...")
                convert_media()
            
            # Stage 3: Run analysis
            log_section(logger, f"STAGE 3: Running AI Analysis ({username})")
            results = analyze_influencer_posts(username)
            
            if results:
                # Save results
                output_path = RESULTS_DIR / f"{username}_analysis.json"
                save_results(results, output_path)
                
                # Print summary
                print_results_summary(results)
                
                # Stage 4: Cleanup
                if CLEANUP_MEDIA:
                    log_section(logger, "STAGE 4: Cleanup")
                    cleanup_media_files(keep_thumbnails=True)
                    print_storage_report()
                
                logger.info(f"\nAnalysis complete for @{username}")
            
        except Exception as e:
            logger.error(f"Failed to analyze @{username}: {e}", exc_info=True)
            continue
    
    log_section(logger, "PIPELINE COMPLETE")
    logger.info("All influencers processed successfully!")


if __name__ == "__main__":
    main()
>>>>>>> 8bf316f0f1e5a33d7051e28b6dde11854481b5fc
