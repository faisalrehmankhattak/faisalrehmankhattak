"""Refresh the "Recent writing" section of the profile README from the Medium RSS feed."""

import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = "https://medium.com/feed/@faisalkhattak391"
README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
MAX_POSTS = 5
START, END = "<!-- writing starts -->", "<!-- writing ends -->"


def fetch_posts():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "profile-readme-bot"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    posts = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").split("?")[0].strip()
        if title and link:
            posts.append((title, link))
    return posts[:MAX_POSTS]


def main():
    try:
        posts = fetch_posts()
    except Exception as exc:  # keep the existing README if the feed is unreachable
        print(f"Feed unavailable, leaving README unchanged: {exc}")
        return 0
    if not posts:
        print("No posts found, leaving README unchanged.")
        return 0
    lines = "\n".join(f"- [{title}]({link})" for title, link in posts)
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    new_text = pattern.sub(f"{START}\n{lines}\n{END}", text)
    if new_text != text:
        README.write_text(new_text, encoding="utf-8")
        print(f"Updated README with {len(posts)} posts.")
    else:
        print("README already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
