#!/usr/bin/env python3
"""
Self-hosted GitHub stats card -- fetches real stats via GitHub's public REST API
and renders a clean SVG card matching the terminal aesthetic.
"""
import os
import sys
import requests
from collections import Counter

USERNAME = os.environ.get("GH_PROFILE_USER", "YogeshModi24")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "stats-card.svg")

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"
SECTION = "#58a6ff"
GREEN = "#3fb950"
ACCENT = "#22d3ee"

W = 490
PAD = 20
TITLEBAR_H = 30
LINE_H = 22


def fetch_json(url):
    r = requests.get(url, headers={"User-Agent": "profile-stats-bot/1.0"}, timeout=30)
    r.raise_for_status()
    return r.json()


def get_stats():
    user = fetch_json(f"https://api.github.com/users/{USERNAME}")
    repos = []
    page = 1
    while True:
        batch = fetch_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        page += 1
        if page > 5:
            break

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    public_repos = user.get("public_repos", len(repos))
    followers = user.get("followers", 0)

    lang_counter = Counter()
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counter[lang] += 1
    top_langs = lang_counter.most_common(5)

    return {
        "public_repos": public_repos,
        "followers": followers,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "top_langs": top_langs,
    }


LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219",
    "C++": "#f34b7d", "C": "#555555", "Go": "#00ADD8",
    "Rust": "#dea584", "Shell": "#89e051", "Jupyter Notebook": "#DA5B0B",
    "PHP": "#4F5D95", "Ruby": "#701516", "Swift": "#F05138",
    "Dart": "#00B4AB", "Vue": "#41b883", "EJS": "#a91e50",
}


def render(stats):
    lang_max = stats["top_langs"][0][1] if stats["top_langs"] else 1
    lang_rows_h = len(stats["top_langs"]) * 26 + 10
    H = TITLEBAR_H + 30 + 5 * LINE_H + 30 + lang_rows_h + PAD

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs><linearGradient id="sbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#sbg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">yogesh@github: ~$ gh stats</text>')

    y = TITLEBAR_H + 30
    parts.append(f'<text x="{PAD}" y="{y}" fill="{SECTION}" font-size="13" font-weight="700">— GitHub Stats</text>')
    parts.append(f'<line x1="{PAD+140}" y1="{y-4}" x2="{W-PAD}" y2="{y-4}" stroke="{FRAME}" stroke-opacity="0.8"/>')
    y += LINE_H + 4

    rows = [
        ("Repos", str(stats["public_repos"])),
        ("Followers", str(stats["followers"])),
        ("Total Stars", str(stats["total_stars"])),
        ("Total Forks", str(stats["total_forks"])),
    ]
    for key, val in rows:
        parts.append(f'<text x="{PAD}" y="{y}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>')
        parts.append(f'<text x="{PAD+130}" y="{y}" fill="{INK}" font-size="12.5">{val}</text>')
        y += LINE_H

    y += 10
    parts.append(f'<text x="{PAD}" y="{y}" fill="{SECTION}" font-size="13" font-weight="700">— Top Languages</text>')
    parts.append(f'<line x1="{PAD+170}" y1="{y-4}" x2="{W-PAD}" y2="{y-4}" stroke="{FRAME}" stroke-opacity="0.8"/>')
    y += 20

    bar_max_w = W - PAD * 2 - 110
    for lang, count in stats["top_langs"]:
        color = LANG_COLORS.get(lang, "#8b949e")
        bar_w = max(6, int(bar_max_w * count / lang_max))
        parts.append(f'<circle cx="{PAD+4}" cy="{y-4}" r="4" fill="{color}"/>')
        parts.append(f'<text x="{PAD+14}" y="{y}" fill="{INK}" font-size="11.5">{lang}</text>')
        parts.append(f'<rect x="{PAD+95}" y="{y-11}" width="{bar_w}" height="8" rx="4" fill="{color}" opacity="0.85"/>')
        y += 26

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    try:
        stats = get_stats()
    except Exception as e:
        print(f"Failed to fetch stats: {e}", file=sys.stderr)
        sys.exit(1)
    svg = render(stats)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes) -- repos={stats['public_repos']} stars={stats['total_stars']}")
