import glob
import json
from io import BytesIO
from pathlib import Path
from typing import Optional

import requests
from PIL import Image
import pandas as pd
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
IMAGES_DIR = DATASET_DIR / "images"
VIDEOS_DIR = DATASET_DIR / "videos"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def download_binary(url: str) -> Optional[bytes]:
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"[!] Failed to download: {url} ({e})")
        return None


def save_image(username: str, index: int, url: str) -> Optional[str]:
    # Filename: username_index.jpg
    filename = f"{username}_{index}.jpg"
    out_path = IMAGES_DIR / filename
    
    # Skip if file already exists
    if out_path.exists():
        return str(out_path.relative_to(BASE_DIR))
    
    content = download_binary(url)
    if content is None:
        return None

    try:
        img = Image.open(BytesIO(content)).convert("RGB")
        img.save(out_path, format="JPEG", quality=90)
        return str(out_path.relative_to(BASE_DIR))
    except Exception as e:
        print(f"[!] Failed to save image from {url}: {e}")
        return None


def save_video(username: str, index: int, url: str) -> Optional[str]:
    # Filename: username_v_index.mp4
    filename = f"{username}_v_{index}.mp4"
    out_path = VIDEOS_DIR / filename
    
    # Skip if file already exists
    if out_path.exists():
        return str(out_path.relative_to(BASE_DIR))
    
    content = download_binary(url)
    if content is None:
        return None

    try:
        # Save binary right to mp4
        with open(out_path, "wb") as vf:
            vf.write(content)
        return str(out_path.relative_to(BASE_DIR))
    except Exception as e:
        print(f"[!] Failed to save video from {url}: {e}")
        return None


def extract_comments(post: dict) -> str:
    all_comments = []

    first_comment = post.get("firstComment")
    if isinstance(first_comment, str):
        all_comments.append(first_comment)

    latest_comments = post.get("latestComments") or []
    if isinstance(latest_comments, list):
        for c in latest_comments:
            txt = c.get("text") if isinstance(c, dict) else None
            if txt:
                all_comments.append(txt)

    return " ".join(all_comments)


def process_post(post: dict, meta_rows: list, counters: dict):
    post_id = str(post.get("shortCode") or post.get("id") or "unknown")
    username = post.get("ownerUsername") or post.get("username") or "unknown"
    caption = post.get("caption") or ""
    comments_text = extract_comments(post)
    likes = post.get("likesCount", 0)
    comments_count = post.get("commentsCount", 0)
    timestamp = post.get("timestamp") or post.get("takenAtTimestamp")

    is_video = bool(post.get("isVideo") or post.get("videoUrl"))
    main_image_url = post.get("displayUrl")
    main_video_url = post.get("videoUrl")

    # Ensure counters exist for this username
    if username not in counters:
        counters[username] = {"image": 0, "video": 0}

    if is_video and main_video_url:
        counters[username]["video"] += 1
        vid_idx = counters[username]["video"]
        saved_path = save_video(username, vid_idx, main_video_url)
        
        if saved_path:
            meta_rows.append({
                "username": username,
                "post_id": post_id,
                "media_index": vid_idx,
                "media_type": "video",
                "file_path": saved_path,
                "caption": caption,
                "comments_text": comments_text,
                "likes": likes,
                "comments_count": comments_count,
                "timestamp": timestamp,
            })

        if main_image_url:
            counters[username]["image"] += 1
            img_idx = counters[username]["image"]
            thumb_path = save_image(username, img_idx, main_image_url)
            if thumb_path:
                meta_rows.append({
                    "username": username,
                    "post_id": post_id,
                    "media_index": img_idx,
                    "media_type": "thumbnail",
                    "file_path": thumb_path,
                    "caption": caption,
                    "comments_text": comments_text,
                    "likes": likes,
                    "comments_count": comments_count,
                    "timestamp": timestamp,
                })
    else:
        if main_image_url:
            counters[username]["image"] += 1
            img_idx = counters[username]["image"]
            saved_path = save_image(username, img_idx, main_image_url)
            if saved_path:
                meta_rows.append({
                    "username": username,
                    "post_id": post_id,
                    "media_index": img_idx,
                    "media_type": "image",
                    "file_path": saved_path,
                    "caption": caption,
                    "comments_text": comments_text,
                    "likes": likes,
                    "comments_count": comments_count,
                    "timestamp": timestamp,
                })

    child_posts = post.get("childPosts") or []
    for child in child_posts:
        child_is_video = bool(child.get("isVideo") or child.get("videoUrl"))
        child_image = child.get("displayUrl")
        child_video = child.get("videoUrl")

        if child_is_video and child_video:
            counters[username]["video"] += 1
            vid_idx = counters[username]["video"]
            saved_path = save_video(username, vid_idx, child_video)
            
            if saved_path:
                meta_rows.append({
                    "username": username,
                    "post_id": post_id,
                    "media_index": vid_idx,
                    "media_type": "video",
                    "file_path": saved_path,
                    "caption": caption,
                    "comments_text": comments_text,
                    "likes": likes,
                    "comments_count": comments_count,
                    "timestamp": timestamp,
                })

            if child_image:
                counters[username]["image"] += 1
                img_idx = counters[username]["image"]
                thumb_path = save_image(username, img_idx, child_image)
                if thumb_path:
                    meta_rows.append({
                        "username": username,
                        "post_id": post_id,
                        "media_index": img_idx,
                        "media_type": "thumbnail",
                        "file_path": thumb_path,
                        "caption": caption,
                        "comments_text": comments_text,
                        "likes": likes,
                        "comments_count": comments_count,
                        "timestamp": timestamp,
                    })
        else:
            if child_image:
                counters[username]["image"] += 1
                img_idx = counters[username]["image"]
                saved_path = save_image(username, img_idx, child_image)
                if saved_path:
                    meta_rows.append({
                        "username": username,
                        "post_id": post_id,
                        "media_index": img_idx,
                        "media_type": "image",
                        "file_path": saved_path,
                        "caption": caption,
                        "comments_text": comments_text,
                        "likes": likes,
                        "comments_count": comments_count,
                        "timestamp": timestamp,
                    })


def main():
    json_files = glob.glob("*_posts.json")

    if not json_files:
        print("[!] No *_posts.json files found in this directory.")
        return

    print(f"[+] Found {len(json_files)} JSON files:")
    for f in json_files:
        print("   -", f)

    meta_rows: list[dict] = []
    counters = {}  # Dictionary to track counts per username

    for json_path in json_files:
        print(f"\n[+] Processing {json_path} ...")
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                posts = json.load(f)
            except json.JSONDecodeError as e:
                print(f"[!] Failed to parse {json_path}: {e}")
                continue

        if not isinstance(posts, list):
            print(f"[!] {json_path} does not contain a list at top level, skipping.")
            continue

        for post in posts:
            if not isinstance(post, dict):
                continue
            process_post(post, meta_rows, counters)

    if not meta_rows:
        print("[!] No media saved, nothing to write to metadata.")
        return

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(meta_rows)
    meta_path = DATASET_DIR / "metadata.csv"
    df.to_csv(meta_path, index=False, encoding="utf-8")
    print(f"\n[✓] Finished. Saved {len(meta_rows)} media items.")
    print(f"[✓] Metadata: {meta_path}")
    print(f"[✓] Images in: {IMAGES_DIR}")
    print(f"[✓] Videos in: {VIDEOS_DIR}")


if __name__ == "__main__":
    main()
