import requests
import json
import os
import time
from datetime import datetime

# Add required User-Agent header
HEADERS = {"User-Agent": "TrendPulse/1.0"}

# HackerNews API endpoints
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
NEW_STORIES_URL = "https://hacker-news.firebaseio.com/v0/newstories.json"
BEST_STORIES_URL = "https://hacker-news.firebaseio.com/v0/beststories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

# Category keywords (case-insensitive)
CATEGORIES = {
    "technology": ["AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports": ["NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"]
}

def assign_category(title):
    """Return category based on keywords in the title."""
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return category
    return None

def main():
    # Step 1: Fetch top story IDs (first 500)
    try:
        story_ids1 = requests.get(TOP_STORIES_URL, headers=HEADERS).json()[:500]
    except Exception as e:
        print("Failed to fetch top stories:", e)
        return
    try:
        story_ids2 = requests.get(NEW_STORIES_URL, headers=HEADERS).json()[:500]
        story_ids1=story_ids1 + story_ids2
    except Exception as e:
        print("Failed to fetch new stories:", e)
        return
    try:
        story_ids3 = requests.get(BEST_STORIES_URL, headers=HEADERS).json()[:500]
        story_ids=story_ids1 + story_ids3
    except Exception as e:
        print("Failed to fetch best stories:", e)
        return

    collected = []
    # Step 2: Loop through categories
    for category in CATEGORIES.keys():
        count = 0
        for sid in story_ids:
            if count >= 25:  # limit 25 per category
                break
            try:
                data = requests.get(ITEM_URL.format(sid), headers=HEADERS).json()
            except Exception as e:
                print(f"Failed to fetch story {sid}: {e}")
                continue

            if data and "title" in data:
                assigned = assign_category(data["title"])
                if assigned == category:
                    collected.append({
                        "post_id": data.get("id"),
                        "title": data.get("title"),
                        "category": assigned,
                        "score": data.get("score", 0),
                        "num_comments": data.get("descendants", 0),
                        "author": data.get("by", ""),
                        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    count += 1

        # Sleep 2 seconds between category loops
        time.sleep(2)

    # Step 3: Save to JSON file
    os.makedirs("data", exist_ok=True)
    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2)

    print(f"Collected {len(collected)} stories. Saved to {filename}")

if __name__ == "__main__":

    main()
