import json
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = "https://jobsearch.api.jobtechdev.se/search"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_jobs(query: str, limit: int = 100):
    """
    Fetch job ads from the Swedish JobTech API.

    query: Search term, for example 'python', 'data engineer', 'azure'
    limit: Number of ads to fetch
    """

    params = {
        "q": query,
        "limit": limit,
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def save_raw_json(data, query: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = query.replace(" ", "_").lower()

    output_path = RAW_DIR / f"job_ads_{safe_query}_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print(f"Saved raw data to: {output_path}")


def main():
    queries = [
        "python",
        "data engineer",
        "sql",
        "azure",
        "machine learning",
    ]

    for query in queries:
        print(f"Fetching jobs for query: {query}")
        data = fetch_jobs(query=query, limit=100)
        save_raw_json(data, query)


if __name__ == "__main__":
    main()