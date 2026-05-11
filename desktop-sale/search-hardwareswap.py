#!/usr/bin/env python3
"""Search r/hardwareswap for recent listings and extract asking prices."""

import json
import re
import time
import urllib.request

# (label, search queries, keywords to look for near prices)
PARTS = [
    ("RTX 4090 FE", ["4090 Founders", "4090 FE"], ["4090"]),
    ("Ryzen 7950X3D", ["7950X3D"], ["7950"]),
    ("DDR5 64GB 6000", ["Corsair Vengeance DDR5 64GB", "DDR5 64GB 6000"], ["64gb", "2x32", "vengeance"]),
    ("Crucial T700 1TB", ["Crucial T700"], ["t700"]),
    ("ASUS B650E-I", ["B650E-I"], ["b650e-i", "b650e i"]),
    ("Corsair SF850L", ["SF850L"], ["sf850"]),
    ("Fractal Terra", ["Fractal Terra"], ["terra"]),
]

HEADERS = {"User-Agent": "desktop-sale-research/0.1"}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def search(query: str, limit: int = 15) -> list[dict]:
    url = (
        f"https://www.reddit.com/r/hardwareswap/search.json"
        f"?q={urllib.request.quote(query)}&restrict_sr=on&sort=new&t=month&limit={limit}"
    )
    data = fetch_json(url)
    posts = []
    for child in data.get("data", {}).get("children", []):
        d = child["data"]
        posts.append({
            "title": d["title"],
            "permalink": d["permalink"],
            "url": f"https://reddit.com{d['permalink']}",
            "flair": d.get("link_flair_text", ""),
            "selftext": d.get("selftext", ""),
        })
    return posts


def find_price_on_line(line: str) -> list[int]:
    """Extract all dollar amounts from a single line."""
    prices = []
    for m in re.finditer(r"\$\s*([\d,]+(?:\.\d{2})?)", line):
        try:
            p = int(float(m.group(1).replace(",", "")))
            if 15 <= p <= 5000:
                prices.append(p)
        except ValueError:
            continue
    return prices


def extract_prices(body: str, keywords: list[str]) -> tuple[list[int], str | None]:
    """
    Try multiple strategies to find a price for this part:
    1. Lines containing both a keyword and a $ amount
    2. Keyword on one line, $ amount on the next line (table rows, etc.)
    3. If nothing works, return the snippet near the keyword for manual review.
    """
    lines = body.split("\n")
    prices = []
    snippet_lines = []

    for i, line in enumerate(lines):
        line_lower = line.lower()
        matched_keyword = any(kw.lower() in line_lower for kw in keywords)

        if not matched_keyword:
            continue

        # Strategy 1: price on the same line
        line_prices = find_price_on_line(line)
        if line_prices:
            prices.extend(line_prices)
            continue

        # Strategy 2: check the next 2 lines (e.g. table formatting, line breaks)
        for offset in range(1, 3):
            if i + offset < len(lines):
                line_prices = find_price_on_line(lines[i + offset])
                if line_prices:
                    prices.extend(line_prices)
                    break

        # Strategy 3: check preceding 2 lines (some formats put price first)
        if not prices:
            for offset in range(1, 3):
                if i - offset >= 0:
                    line_prices = find_price_on_line(lines[i - offset])
                    if line_prices:
                        prices.extend(line_prices)
                        break

        # Collect snippet context regardless
        start = max(0, i - 1)
        end = min(len(lines), i + 3)
        snippet_lines.extend(lines[start:end])

    # Deduplicate prices
    prices = sorted(set(prices))

    snippet = None
    if not prices and snippet_lines:
        snippet = "\n".join(f"      | {l.strip()}" for l in snippet_lines[:8] if l.strip())

    return prices, snippet


def main():
    all_results: dict[str, list[dict]] = {}

    for label, queries, keywords in PARTS:
        print(f"\nSearching: {label}...", flush=True)
        seen_urls = set()
        entries = []

        for query in queries:
            try:
                posts = search(query)
            except Exception as e:
                print(f"  Error searching '{query}': {e}")
                time.sleep(2)
                continue

            for p in posts:
                if p["url"] in seen_urls:
                    continue

                flair = (p.get("flair") or "").upper()
                if "BUYING" in flair:
                    continue
                seen_urls.add(p["url"])

                prices, snippet = extract_prices(p["selftext"], keywords)

                entries.append({
                    "title": p["title"],
                    "url": p["url"],
                    "flair": p.get("flair", ""),
                    "prices": prices,
                    "snippet": snippet,
                })

            time.sleep(2)

        all_results[label] = entries

    # Summary
    print("\n")
    print("=" * 70)
    print("  HARDWARESWAP PRICE SUMMARY")
    print("=" * 70)

    for label, _, _ in PARTS:
        entries = all_results.get(label, [])
        all_prices = []
        print(f"\n  {label}")
        print(f"  {'-' * 60}")

        for e in entries:
            flair_str = f" [{e['flair']}]" if e["flair"] else ""
            title = e["title"][:75] + ("..." if len(e["title"]) > 75 else "")

            if e["prices"]:
                price_str = ", ".join(f"${p:,}" for p in e["prices"])
                all_prices.extend(e["prices"])
                print(f"    {price_str:>20}  {title}{flair_str}")
            elif e["snippet"]:
                print(f"    {'(snippet below)':>20}  {title}{flair_str}")
                print(e["snippet"])
            else:
                print(f"    {'(no body text)':>20}  {title}{flair_str}")

        if all_prices:
            low = min(all_prices)
            high = max(all_prices)
            sorted_prices = sorted(all_prices)
            med = sorted_prices[len(sorted_prices) // 2]
            print(f"\n    Range: ${low:,} – ${high:,}  |  Median: ${med:,}  |  {len(all_prices)} prices")
        else:
            print("\n    No prices found.")

    print()


if __name__ == "__main__":
    main()
