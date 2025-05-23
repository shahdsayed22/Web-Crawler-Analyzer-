import os
import json
import sys
from datetime import datetime

from crawler.crawlability import analyze_robots
from crawler.extractor import scrape_page
from crawler.js_handler import scrape_with_playwright


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_result(data, prefix):
    ensure_dir("results")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"results/{prefix}_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved: {path}")


def run(url, js=False):
    print(f"\n🔍 Analyzing: {url}")

    # 1. robots.txt analysis
    robots = analyze_robots(url)
    print(f"🧭 Robots.txt: {'✅ Crawl allowed' if robots['can_crawl'] else '❌ Disallowed'}")

    if not robots["can_crawl"]:
        print("⛔ Skipping - blocked by robots.txt")
        return

    # 2. content extraction
    if js:
        print("\n⚙️ Using JS rendering (Playwright)")
        content = scrape_with_playwright(url)
    else:
        print("\n⚙️ Using HTML extraction (requests + BS4)")
        content = scrape_page(url)

    # 3. print summary
    if content.get("error") or not content.get("success", True):
        print(f"❌ Error: {content.get('error', 'Unknown')}")
    else:
        print(f"✅ Title: {content.get('title')}")
        print(f"🔗 Links: {len(content.get('links', []))}")

        if content.get("screenshot_path"):
            print(f"🖼️ Screenshot saved to: {content['screenshot_path']}")

    # 4. save final result
    result = {
        "url": url,
        "robots": robots,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    save_result(result, "crawl")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://booking.com"
    js_mode = "--js" in sys.argv
    run(url, js=js_mode)
