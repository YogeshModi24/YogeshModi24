#!/usr/bin/env python3
"""
Self-hosted typing/rotating-tagline SVG -- cycles through a list of taglines
with a typewriter effect using pure CSS/SMIL animation. No external service.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "typing-card.svg")

TAGLINES = [
    "Full-Stack Developer",
    "AI / ML Engineer",
    "B.Tech AI Student",
    "Building agentic systems",
    "LangGraph + RAG enthusiast",
]

W, H = 490, 374
PAD = 20
TITLEBAR_H = 30

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#58a6ff"
GREEN = "#3fb950"

CHAR_DUR = 0.05      # seconds per character typed
HOLD_DUR = 1.4        # how long the full line holds before erasing
ERASE_DUR = 0.5        # seconds to erase the whole line


def build():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs><linearGradient id="tbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#tbg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">yogesh@github: ~$ whoami --verbose</text>')

    cy = TITLEBAR_H + (H - TITLEBAR_H) / 2

    parts.append(f'<text x="{PAD}" y="{cy - 30}" fill="{GREEN}" font-size="14">$ echo $ROLE</text>')

    # total cycle time per line
    line_total = len(max(TAGLINES, key=len)) * CHAR_DUR + HOLD_DUR + ERASE_DUR
    n = len(TAGLINES)
    total_cycle = line_total * n

    css_parts = []
    for i, line in enumerate(TAGLINES):
        type_dur = len(line) * CHAR_DUR
        start = i * line_total
        css_parts.append(f"""
.line{i} {{
  animation: cycle{i} {total_cycle:.2f}s steps(1) infinite;
  opacity: 0;
}}
@keyframes cycle{i} {{
  0% {{ opacity: 0; }}
  {start/total_cycle*100:.3f}% {{ opacity: 0; }}
  {(start+0.01)/total_cycle*100:.3f}% {{ opacity: 1; }}
  {(start+line_total-0.01)/total_cycle*100:.3f}% {{ opacity: 1; }}
  {(start+line_total)/total_cycle*100:.3f}% {{ opacity: 0; }}
  100% {{ opacity: 0; }}
}}
.clip{i} {{
  animation: typeclip{i} {total_cycle:.2f}s steps(1) infinite;
}}
@keyframes typeclip{i} {{
  0%, {start/total_cycle*100:.3f}% {{ width: 0; }}
  {(start)/total_cycle*100:.3f}% {{ width: 0; }}
  {(start+type_dur)/total_cycle*100:.3f}% {{ width: {len(line)*8.4:.0f}px; }}
  {(start+line_total-ERASE_DUR)/total_cycle*100:.3f}% {{ width: {len(line)*8.4:.0f}px; }}
  {(start+line_total)/total_cycle*100:.3f}% {{ width: 0; }}
  100% {{ width: 0; }}
}}
""")

    parts.append(f'<style>{"".join(css_parts)}</style>')

    for i, line in enumerate(TAGLINES):
        parts.append(f'<g class="line{i}">')
        parts.append(f'<clipPath id="cp{i}"><rect class="clip{i}" x="0" y="0" height="30"/></clipPath>')
        parts.append(f'<g clip-path="url(#cp{i})">')
        parts.append(f'<text x="{PAD}" y="{cy}" fill="{ACCENT}" font-size="20" font-weight="700">&gt; {line}</text>')
        parts.append('</g></g>')

    parts.append(f'<rect x="{PAD}" y="{cy+8}" width="{4}" height="{22}" fill="{INK}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="0.9s" repeatCount="indefinite"/></rect>')

    parts.append(f'<text x="{PAD}" y="{cy + 60}" fill="{MUTED}" font-size="12">exploring AI/ML, agentic systems &amp; full-stack product engineering</text>')

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = build()
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg)} bytes)")
