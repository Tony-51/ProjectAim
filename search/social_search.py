import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

SOCIAL_PLATFORMS = {
    "Instagram": "site:instagram.com",
    "Facebook": "site:facebook.com",
    "X": "site:x.com",
    "YouTube": "site:youtube.com",
    "LinkedIn": "site:linkedin.com",
    "Reddit": "site:reddit.com",
}


def clean_text(text):
    """Clean search result text."""
    if not text:
        return ""

    text = text.replace("\\u003d", "=")
    text = text.replace("\\/", "/")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def search_google(query, num_results=10):
    """Search Google through SerpApi."""

    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY not found in .env file")

    response = requests.get(
        "https://serpapi.com/search",
        params={
            "engine": "google",
            "q": query,
            "num": num_results,
            "hl": "en",
            "gl": "in",
            "api_key": SERPAPI_KEY,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def detect_platform(url):
    """Identify social platform from URL."""

    url = url.lower()

    if "instagram.com" in url:
        return "Instagram"

    if "facebook.com" in url:
        return "Facebook"

    if "x.com" in url or "twitter.com" in url:
        return "X"

    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube"

    if "linkedin.com" in url:
        return "LinkedIn"

    if "reddit.com" in url:
        return "Reddit"

    return "Other"


def search_social_media(person_name):
    """
    Search multiple public social platforms using the person's name.

    NOTE:
    This does NOT claim that a result belongs to the person.
    It only collects public web results that may be relevant.
    """

    all_results = []
    seen_urls = set()

    # Different query patterns improve recall.
    query_patterns = [
        '"{name}"',
        '"{name}" profile',
        '"{name}" photo',
        '"{name}" post',
    ]

    for platform, site_query in SOCIAL_PLATFORMS.items():

        for pattern in query_patterns:

            query = (
                f'{site_query} '
                f'{pattern.format(name=person_name)}'
            )

            print()
            print(f"Searching {platform}...")
            print("Query:", query)

            try:
                data = search_google(query, num_results=10)

            except Exception as e:
                print(f"Search failed: {e}")
                continue

            organic_results = data.get("organic_results", [])

            for result in organic_results:

                url = result.get("link")

                if not url:
                    continue

                # Remove duplicates.
                if url in seen_urls:
                    continue

                detected_platform = detect_platform(url)

                # Only keep the platforms we requested.
                if detected_platform not in SOCIAL_PLATFORMS:
                    continue

                seen_urls.add(url)

                candidate = {
                    "platform": detected_platform,
                    "title": clean_text(
                        result.get("title", "")
                    ),
                    "url": url,
                    "snippet": clean_text(
                        result.get("snippet", "")
                    ),
                    "position": result.get("position"),
                    "query": query,
                }

                all_results.append(candidate)

    return all_results


def save_results(results):

    os.makedirs("data", exist_ok=True)

    output_path = "data/social_candidates.json"

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    return output_path


def print_results(results):

    print()
    print("=" * 70)
    print("TARGETED PUBLIC SOCIAL MEDIA SEARCH")
    print("=" * 70)

    print()
    print(f"Found {len(results)} targeted social results.")

    print()
    print("Top results:")

    for i, result in enumerate(results[:30], start=1):

        print()
        print(f"--- Result {i} ---")

        print(
            "Platform:",
            result["platform"]
        )

        print(
            "Title:",
            result["title"]
        )

        print(
            "URL:",
            result["url"]
        )

        if result.get("snippet"):
            print(
                "Snippet:",
                result["snippet"][:250]
            )


if __name__ == "__main__":

    print("=" * 70)
    print("TARGETED PUBLIC SOCIAL MEDIA SEARCH")
    print("=" * 70)

    person_name = input(
        "\nEnter the person's name to search: "
    ).strip()

    if not person_name:

        print("No name entered.")
        exit()

    print()
    print(
        f'Searching public social results for: "{person_name}"'
    )

    results = search_social_media(person_name)

    output_path = save_results(results)

    print_results(results)

    print()
    print(
        f"Social results saved to: {output_path}"
    )