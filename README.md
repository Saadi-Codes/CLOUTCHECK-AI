# Instagram Scraper & Media Dataset

## Project Summary

This repository contains a Python-based workflow for scraping Instagram posts, processing media, and preparing a dataset suitable for machine learning applications. The project leverages **Apify** for data extraction and organizes images and videos for model training.

---

## Features

* Scrape posts from multiple Instagram accounts.
* Collect posts from the last **6 months** automatically.
* Support for:

  * Single posts (images or videos)
  * Carousels (`Sidecar`)
  * Reels
* Export post metadata as JSON.
* Convert images to `.jpg` and videos/Reels to `.mp4`.
* Consolidate all media into a structured dataset.

---

## Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

2. Create a virtual environment (recommended):

```bash
python -m venv scrapper2
source scrapper2/Scripts/activate  # Windows
# OR
source scrapper2/bin/activate      # Linux/Mac
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Configure your API key securely via `.env`:

```env
APIFY_API_TOKEN=your_apify_api_token_here
```

---

## Scripts Overview

### **Scraper.py**

* Collects Instagram posts for a given username.
* Saves data as `{username}_6months_posts.json`.
* Uses `.env` for secure API token storage.

### **Converter.py**

* Processes all JSON files in the repo directory.
* Converts media into:

  * `dataset/images/*.jpg`
  * `dataset/videos/*.mp4`
* Handles multiple influencers in one consolidated dataset.
* Supports all post types: Image, Video, Sidecar, Reel.

---

## Dataset Structure

```
dataset/
   images/
       <post_id>_<index>.jpg
   videos/
       <post_id>_<index>.mp4
```

* Each post is uniquely identified by Instagram `shortCode` and index.
* Images and videos are stored together in one unified dataset for training.

---

## Usage

1. Run the scraper to collect posts:

```bash
python Scraper.py
```

* Enter the Instagram username when prompted.

2. Convert scraped JSON to media dataset:

```bash
python Converter.py
```

* The dataset folder will be populated automatically.

---

## Git & Large File Handling

* Dataset media files are tracked using **Git LFS** due to their size.
* Ensure Git LFS is installed:

```bash
git lfs install
git lfs track "dataset/images/*"
git lfs track "dataset/videos/*"
```

* `.gitignore` excludes `.env` and temporary Python files:

```
.env
__pycache__/
*.pyc
```

---

## Notes

* Designed for research and training machine learning models.
* Supports multiple accounts and aggregates posts into a single dataset.
* API token is never hard-coded and must be stored in `.env`.
