from apify_client import ApifyClient
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
API_TOKEN = os.getenv("APIFY_API_TOKEN")

if not API_TOKEN:
    raise ValueError("API token not found! Make sure APIFY_API_TOKEN is set in .env")

# Initialize the ApifyClient with API token from .env
client = ApifyClient(API_TOKEN)

# Ask user for the Instagram username
username = input("Enter the Instagram username (without @): ").strip().replace(" ", "")
profile_url = f"https://www.instagram.com/{username}/"

# Calculate the date 6 months ago (ISO format)
six_months_ago = (datetime.utcnow() - timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# Prepare the Actor input (cleaned: removed invalid fields)
run_input = {
    "directUrls": [profile_url],
    "resultsType": "posts",
    "resultsLimit": 500,
    "onlyPostsNewerThan": six_months_ago,
    "isUserTaggedFeedURL": False,
    "isUserReelFeedURL": False,
    "enhanceUserSearchWithFacebookPage": False,
    "addParentData": False,
}

print(f"🔍 Starting Instagram scrape for @{username} (last 6 months)...")

try:
    # Run the Instagram scraper Actor and wait for it to finish
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)

    # Collect results
    results = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]

    # Save results to JSON
    output_file = f"{username}_6months_posts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"✅ Scraping complete for @{username}. Found {len(results)} posts (last 6 months).")
    print(f"📁 Results saved to '{output_file}'")

except Exception as e:
    print(f"❌ Error during scraping: {e}")
