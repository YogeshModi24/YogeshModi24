#!/usr/bin/env python3
"""
Self-hosted GitHub stats card -- fetches real stats via GitHub's public REST API
and renders a polished SVG card: icon + big bold number stat tiles, plus a
top-languages bar list. Matches the terminal aesthetic of the other cards.
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
SECTION = "#58a6ff"
TILE_BG = "#161b22"

W = 490
PAD = 20
TITLEBAR_H = 30


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

# simple icon glyphs drawn as tiny inline SVG paths (no external deps / emoji font issues)
def icon(kind, x, y, color):
    s = 15  # icon box size
    if kind == "repo":
        return (f'<g transform="translate({x},{y})" stroke="{color}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round">'
                 f'<path d="M2 1.5h8.5a1.5 1.5 0 0 1 1.5 1.5v10a1 1 0 0 1-1 1H3a1.5 1.5 0 0 1-1.5-1.5V3A1.5 1.5 0 0 1 2 1.5Z"/>'
                 f'<path d="M2 11.5H12"/></g>')
    if kind == "followers":
        return (f'<g transform="translate({x},{y})" stroke="{color}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round">'
                 f'<circle cx="5" cy="4" r="2.3"/><path d="M1 13c0-2.5 1.8-4 4-4s4 1.5 4 4"/>'
                 f'<circle cx="11.5" cy="5" r="1.8"/><path d="M9.5 13c0-2 1-3.5 3-3.5"/></g>')
    if kind == "star":
        return (f'<g transform="translate({x},{y})" fill="{color}">'
                 f'<path d="M7 0.5l1.9 4 4.4.6-3.2 3 0.8 4.4L7 10.4 3.1 12.5l0.8-4.4-3.2-3 4.4-.6Z"/></g>')
    if kind == "fork":
        return (f'<g transform="translate({x},{y})" stroke="{color}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round">'
                 f'<circle cx="3.5" cy="2.5" r="1.5"/><circle cx="10.5" cy="2.5" r="1.5"/><circle cx="7" cy="11.5" r="1.5"/>'
                 f'<path d="M3.5 4v2a2 2 0 0 0 2 2h3a2 2 0 0 0 2-2V4"/><path d="M7 8v2"/></g>')
    return ""


def render(stats):
    stat_tiles = [
        ("repo", "Repos", stats["public_repos"], "#58a6ff"),
        ("followers", "Followers", stats["followers"], "#3fb950"),
        ("star", "Stars", stats["total_stars"], "#f2cc60"),
        ("fork", "Forks", stats["total_forks"], "#bc8cff"),
    ]

    tile_w = (W - PAD * 2 - 12) / 2
    tile_h = 70
    lang_max = stats["top_langs"][0][1] if stats["top_langs"] else 1
    lang_row_h = 28
    lang_block_h = len(stats["top_langs"]) * lang_row_h + 36
    H = TITLEBAR_H + 24 + tile_h * 2 + 12 + lang_block_h + PAD

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

    # 2x2 stat tiles
    ty = TITLEBAR_H + 22
    for idx, (kind, label, value, color) in enumerate(stat_tiles):
        col = idx % 2
        row = idx // 2
        tx = PAD + col * (tile_w + 12)
        y = ty + row * (tile_h + 12)
        parts.append(f'<rect x="{tx}" y="{y}" width="{tile_w}" height="{tile_h}" rx="10" fill="{TILE_BG}" stroke="{FRAME}"/>')
        parts.append(icon(kind, tx + 16, y + 16, color))
        parts.append(f'<text x="{tx+16}" y="{y+48}" fill="{color}" font-size="26" font-weight="700">{value}</text>')
        parts.append(f'<text x="{tx+16}" y="{y+62}" fill="{MUTED}" font-size="11.5">{label}</text>')

    y = ty + 2 * tile_h + 12 + 26
    parts.append(f'<text x="{PAD}" y="{y}" fill="{SECTION}" font-size="13" font-weight="700">— Top Languages</text>')
    parts.append(f'<line x1="{PAD+170}" y1="{y-4}" x2="{W-PAD}" y2="{y-4}" stroke="{FRAME}" stroke-opacity="0.8"/>')
    y += 22

    bar_max_w = W - PAD * 2 - 110
    for lang, count in stats["top_langs"]:
        color = LANG_COLORS.get(lang, "#8b949e")
        bar_w = max(8, int(bar_max_w * count / lang_max))
        parts.append(f'<circle cx="{PAD+5}" cy="{y-4}" r="4.5" fill="{color}"/>')
        parts.append(f'<text x="{PAD+16}" y="{y}" fill="{INK}" font-size="12">{lang}</text>')
        parts.append(f'<rect x="{PAD+96}" y="{y-12}" width="{bar_max_w}" height="9" rx="4.5" fill="{FRAME}" opacity="0.4"/>')
        parts.append(f'<rect x="{PAD+96}" y="{y-12}" width="{bar_w}" height="9" rx="4.5" fill="{color}"/>')
        y += lang_row_h

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
