import json
import os
import requests
from PIL import Image
from io import BytesIO


# ------------------------------
# Utility functions
# ------------------------------

def download_file(url, save_path):
    """Download file from URL and save locally."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ Saved: {save_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False


def save_image_as_jpg(url, save_path):
    """Download image from URL and save as JPG."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        rgb_image = image.convert('RGB')
        rgb_image.save(save_path, format='JPEG', quality=95)
        print(f"✅ Image saved: {save_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to save image {url}: {e}")
        return False


def extract_video_url(post):
    """Extract video URL from post data."""
    # Try different possible locations for video URL
    video_url = (
        post.get("videoUrl") or
        post.get("video_url") or
        post.get("displayUrl") if post.get("type") == "Video" else None
    )
    return video_url


# ------------------------------
# Setup dataset folders
# ------------------------------

os.makedirs("dataset/images", exist_ok=True)
os.makedirs("dataset/videos", exist_ok=True)
os.makedirs("dataset/metadata", exist_ok=True)

# ------------------------------
# Find all JSON files ending with _6months_posts.json
# ------------------------------

json_files = [f for f in os.listdir() if f.endswith("_6months_posts.json")]
if not json_files:
    raise FileNotFoundError("No scraper JSON files found in this folder!")

print(f"🔹 Found {len(json_files)} JSON files: {json_files}\n")

# ------------------------------
# Statistics tracking
# ------------------------------

stats = {
    "total_posts": 0,
    "images_downloaded": 0,
    "videos_downloaded": 0,
    "failed_downloads": 0
}

# ------------------------------
# Process each JSON file
# ------------------------------

for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print(f"📁 Processing {len(posts)} posts from {json_file}")
    print("-" * 60)

    for post in posts:
        stats["total_posts"] += 1
        post_id = post.get("shortCode") or post.get("id", f"unknown_{stats['total_posts']}")
        post_type = post.get("type", "Unknown")

        # Save metadata for each post
        metadata = {
            "post_id": post_id,
            "type": post_type,
            "caption": post.get("caption", ""),
            "url": post.get("url", ""),
            "timestamp": post.get("timestamp", ""),
            "likes": post.get("likesCount", 0),
            "comments": post.get("commentsCount", 0)
        }

        metadata_path = f"dataset/metadata/{post_id}.json"
        with open(metadata_path, "w", encoding="utf-8") as mf:
            json.dump(metadata, mf, indent=2, ensure_ascii=False)

        # ------------------
        # Handle Sidecar posts (carousel)
        # ------------------
        if post_type == "Sidecar":
            # Check for carouselMedia first
            carousel_media = post.get("carouselMedia", [])

            # If no carouselMedia, check childPosts
            if not carousel_media:
                carousel_media = post.get("childPosts", [])

            # If still no media, try images array
            if not carousel_media and post.get("images"):
                for idx, img_url in enumerate(post["images"]):
                    save_path = f"dataset/images/{post_id}_{idx}.jpg"
                    if save_image_as_jpg(img_url, save_path):
                        stats["images_downloaded"] += 1
                    else:
                        stats["failed_downloads"] += 1
            else:
                for idx, media in enumerate(carousel_media):
                    media_type = media.get("type", "Image")

                    if media_type == "Image":
                        img_url = media.get("displayUrl") or media.get("imageUrl") or media.get("url")
                        if img_url:
                            save_path = f"dataset/images/{post_id}_{idx}.jpg"
                            if save_image_as_jpg(img_url, save_path):
                                stats["images_downloaded"] += 1
                            else:
                                stats["failed_downloads"] += 1

                    elif media_type == "Video":
                        video_url = extract_video_url(media)
                        if video_url:
                            save_path = f"dataset/videos/{post_id}_{idx}.mp4"
                            if download_file(video_url, save_path):
                                stats["videos_downloaded"] += 1
                            else:
                                stats["failed_downloads"] += 1

        # ------------------
        # Handle single Image posts
        # ------------------
        elif post_type == "Image":
            # Try displayUrl first, then images array
            img_url = post.get("displayUrl")
            if img_url:
                save_path = f"dataset/images/{post_id}_0.jpg"
                if save_image_as_jpg(img_url, save_path):
                    stats["images_downloaded"] += 1
                else:
                    stats["failed_downloads"] += 1
            elif post.get("images"):
                for idx, img_url in enumerate(post["images"]):
                    save_path = f"dataset/images/{post_id}_{idx}.jpg"
                    if save_image_as_jpg(img_url, save_path):
                        stats["images_downloaded"] += 1
                    else:
                        stats["failed_downloads"] += 1

        # ------------------
        # Handle Video/Reel posts
        # ------------------
        elif post_type == "Video" or "reel" in post.get("url", "").lower():
            video_url = extract_video_url(post)
            if video_url:
                save_path = f"dataset/videos/{post_id}_0.mp4"
                if download_file(video_url, save_path):
                    stats["videos_downloaded"] += 1
                else:
                    stats["failed_downloads"] += 1
            else:
                print(f"⚠️  No video URL found for post {post_id} (type: {post_type})")
                stats["failed_downloads"] += 1

    print()

# ------------------------------
# Print final statistics
# ------------------------------

print("=" * 60)
print("📊 DATASET EXTRACTION COMPLETE")
print("=" * 60)
print(f"Total posts processed: {stats['total_posts']}")
print(f"Images downloaded: {stats['images_downloaded']}")
print(f"Videos downloaded: {stats['videos_downloaded']}")
print(f"Failed downloads: {stats['failed_downloads']}")
print(f"\n📁 Dataset saved in 'dataset/' folder:")
print(f"   - Images: dataset/images/")
print(f"   - Videos: dataset/videos/")
print(f"   - Metadata: dataset/metadata/")
print("=" * 60)