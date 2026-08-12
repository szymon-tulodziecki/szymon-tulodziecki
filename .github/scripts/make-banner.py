#!/usr/bin/env python3
"""Generuje assets/banner.svg - izometryczny baner w palecie Kanagawa Dragon.

Ten sam jezyk wizualny co profile-3d-contrib/profile-dragon.svg: te same bryly,
ta sama rampa kolorow, ta sama projekcja 2:1. Baner jest statyczny (imie sie nie
zmienia), wiec generujemy go recznie, a nie w codziennym workflow:

    python3 .github/scripts/make-banner.py
"""

import pathlib
import random

# ── paleta ──────────────────────────────────────────────────────────────────
BG_FROM, BG_TO = "#1A1818", "#1F2422"
FG = "#C5C9C5"
MUTED = "#7A8382"
ACCENT = "#C4B28A"
RAMP = ["#252523", "#414A3C", "#5C6B52", "#768B6C", "#A0B78D"]

# scianki boczne sa ciemniejsze od gornej - te same wspolczynniki co 3d-contrib
LEFT_K, RIGHT_K = 0.84, 0.70

# ── geometria ───────────────────────────────────────────────────────────────
W, H = 1280, 340           # viewBox
TW, TH = 46, 24            # szerokosc/wysokosc kafla (projekcja 2:1)
COLS, DEPTH = 25, 4        # kolumny i rzedy w glab
LEVEL_H = 15               # wysokosc jednego poziomu bryly
BASE_Y = 300               # linia gruntu, na ktorej stoi pole

NAME = "Szymon Tułodziecki"
TAGLINE = "full-stack · embedded · devops"


def shade(hex_color: str, k: float) -> str:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % (int(r * k), int(g * k), int(b * k))


def block(cx: float, gy: float, levels: int) -> str:
    """Jedna bryla stojaca na gruncie (cx, gy). Rosnie w GORE od gruntu."""
    h = levels * LEVEL_H
    top_c = RAMP[levels]
    hw, hh = TW / 2, TH / 2
    cy = gy - h  # srodek gornej scianki: podniesiony o wysokosc bryly
    top = f"{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}"
    left = f"{cx - hw},{cy} {cx},{cy + hh} {cx},{gy + hh} {cx - hw},{gy}"
    right = f"{cx + hw},{cy} {cx},{cy + hh} {cx},{gy + hh} {cx + hw},{gy}"
    return (
        f'<polygon points="{left}" fill="{shade(top_c, LEFT_K)}"/>'
        f'<polygon points="{right}" fill="{shade(top_c, RIGHT_K)}"/>'
        f'<polygon points="{top}" fill="{top_c}"/>'
    )


def build() -> str:
    rnd = random.Random(20260812)  # deterministycznie - ten sam baner za kazdym razem
    field_w = COLS * TW + DEPTH * TW / 2
    x0 = (W - field_w) / 2 + TW / 2

    groups = []
    # rzedy od tylu do przodu: pozniej narysowane zaslaniaja wczesniejsze
    for d in range(DEPTH):
        for c in range(COLS):
            cx = x0 + c * TW + d * TW / 2
            cy = BASE_Y - (DEPTH - 1 - d) * TH / 2

            # przednie rzedy wyzsze - pole opada ku tylowi
            ceiling = [2, 3, 4, 4][d]
            levels = rnd.randint(0, ceiling)

            delay = c * 26 + d * 70
            groups.append(
                f'<g class="b" style="animation-delay:{delay}ms">{block(cx, cy, levels)}</g>'
            )

    blocks = "\n".join(groups)
    text_delay = COLS * 26 + 180

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{NAME} — {TAGLINE}">
  <title>{NAME} — {TAGLINE}</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG_FROM}"/>
      <stop offset="1" stop-color="{BG_TO}"/>
    </linearGradient>
  </defs>
  <style>
    .b {{ animation: rise .55s cubic-bezier(.2,.85,.3,1) both; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(16px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .t {{ animation: fade .7s ease-out both; animation-delay: {text_delay}ms; }}
    @keyframes fade {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .rule {{
      stroke-dasharray: 200; stroke-dashoffset: 200;
      animation: draw .9s ease-out both, glow 3.5s ease-in-out {text_delay + 900}ms infinite;
      animation-delay: {text_delay + 120}ms;
    }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    @keyframes glow {{ 0%,100% {{ opacity: .45; }} 50% {{ opacity: 1; }} }}
    .name {{ font: 700 60px "Fira Code", "JetBrains Mono", ui-monospace, "DejaVu Sans Mono", monospace; }}
    .tag  {{ font: 400 19px "Fira Code", "JetBrains Mono", ui-monospace, "DejaVu Sans Mono", monospace; letter-spacing: 3px; }}
  </style>

  <rect width="{W}" height="{H}" fill="url(#bg)"/>

{blocks}

  <g class="t" text-anchor="middle">
    <text class="name" x="{W // 2}" y="112" fill="{FG}">{NAME}</text>
    <text class="tag"  x="{W // 2}" y="150" fill="{MUTED}">{TAGLINE}</text>
  </g>
  <line class="rule" x1="{W // 2 - 100}" y1="172" x2="{W // 2 + 100}" y2="172"
        stroke="{ACCENT}" stroke-width="2" stroke-linecap="round"/>
</svg>
"""


if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parents[2] / "assets" / "banner.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"zapisano {out} ({out.stat().st_size} B)")
