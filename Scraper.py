import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()
API_TOKEN = os.getenv("APIFY_API_TOKEN")

if not API_TOKEN:
    raise ValueError("APIFY_API_TOKEN not found in .env!")

# Initialize client
client = ApifyClient(API_TOKEN)

def build_actor_input(username: str):
    """Construct input for Apify Instagram Scraper"""
    username = username.strip().replace(" ", "")
    profile_url = f"https://www.instagram.com/{username}/"

    six_months_ago = (
        datetime.utcnow() - timedelta(days=365)
    ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    return {
        "directUrls": [profile_url],
        "resultsType": "posts",
        "resultsLimit": 500,
        "onlyPostsNewerThan": six_months_ago,
        "isUserTaggedFeedURL": False,
        "isUserReelFeedURL": False,
        "enhanceUserSearchWithFacebookPage": False,
        "addParentData": False,
    }


def scrape_instagram(username: str, months: int = 6):
    actor_input = build_actor_input(username)

    print(f"Running scrape for @{username}...")

    try:
        # Start actor
        run = client.actor("apify/instagram-scraper").call(run_input=actor_input)

        # Retrieve dataset items
        dataset = client.dataset(run["defaultDatasetId"])
        items = [item for item in dataset.iterate_items()]

        # Save raw results
        output_file = f"{username}_posts.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)

        print(f"Completed! {len(items)} posts found.")
        print(f"Saved to: {output_file}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    username = input("Enter Instagram username (without @): ").strip().lstrip("@")

    if not username:
        print("Username cannot be empty.")
        exit(1)

    scrape_instagram(username)
