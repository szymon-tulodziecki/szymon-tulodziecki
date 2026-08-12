#!/usr/bin/env python3
"""Doprowadza wygenerowany render 3D do palety Kanagawa Dragon i doszywa naglowek.

github-profile-3d-contrib przez SETTING_JSON pozwala ustawic tylko czesc rzeczy,
wiec trzy poprawki robimy po fakcie:

  1. Naglowek - imie i tagline wchodza do TEGO SAMEGO pliku co render, zeby
     README bylo jednym obrazkiem zamiast dwoch. Plotno rosnie o HEADER_H,
     oryginalna zawartosc zjezdza w dol.
  2. Tlo - SETTING_JSON przyjmuje wylacznie jednolity kolor, a chcemy gradient.
  3. Kolory jezykow - brane z linguista GitHuba (zolty JS, niebieski Python,
     czerwony Blade) i kompletnie rozjezdzaja sie z paleta.

    python3 .github/scripts/dragonize-render.py profile-3d-contrib/profile-dragon.svg
"""

import re
import sys
import pathlib

MARK = "dragon-hdr"  # znacznik idempotencji
HEADER_H = 165

NAME = "Szymon Tułodziecki"
TAGLINE = "full-stack · embedded · devops"

FG = "#C5C9C5"
MUTED = "#7A8382"
ACCENT = "#C4B28A"

# gradient tla - wyrazny, ale wciaz dragon: zielen -> wegiel -> fiolet
GRAD_STOPS = [(0.0, "#1E2622"), (0.55, "#1A1818"), (1.0, "#1D1E26")]

# kolory, ktore juz sa dragonem - nie ruszamy ich przy przemalowywaniu jezykow
KEEP = {
    "#c5c9c5", "#181616", "#c4b28a", "#7a8382", "#8ba4b0",
    "#1e2622", "#1a1818", "#1d1e26",
}

# pelna paleta akcentow dragona, uporzadkowana pod maksymalne rozroznienie
# sasiednich wycinkow. Znaczenie niesie legenda z nazwami jezykow.
CATEGORICAL = [
    "#8A9A7B",  # szalwia
    "#8BA4B0",  # przykurzony blekit
    "#C4B28A",  # piaskowy
    "#C4746E",  # przygaszona czerwien
    "#8992A7",  # stalowy fiolet
    "#8EA4A2",  # szarozielony
    "#B6927B",  # terakota
    "#A292A3",  # wyblakly roz
    "#87A987",  # jasna zielen
    "#949FB5",  # morski
    "#A6A69C",  # ciepla szarosc
]


def build_head(cx: int) -> str:
    stops = "".join(
        f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GRAD_STOPS
    )
    return f"""<defs><linearGradient id="dragon-bg" x1="0" y1="0" x2="1" y2="1">{stops}</linearGradient></defs>\
<style>\
.{MARK}-name {{ font: 700 54px "Fira Code","JetBrains Mono",ui-monospace,"DejaVu Sans Mono",monospace; }}\
.{MARK}-tag {{ font: 400 18px "Fira Code","JetBrains Mono",ui-monospace,"DejaVu Sans Mono",monospace; letter-spacing: 3px; }}\
.{MARK}-rule {{ stroke-dasharray: 220; stroke-dashoffset: 220; animation: {MARK}-draw 1s ease-out .2s both, {MARK}-glow 3.5s ease-in-out 1.4s infinite; }}\
@keyframes {MARK}-draw {{ to {{ stroke-dashoffset: 0; }} }}\
@keyframes {MARK}-glow {{ 0%,100% {{ opacity:.5 }} 50% {{ opacity:1 }} }}\
</style>"""


def build_header(cx: int) -> str:
    return (
        f'<g text-anchor="middle">'
        f'<text class="{MARK}-name" x="{cx}" y="80" fill="{FG}">{NAME}</text>'
        f'<text class="{MARK}-tag" x="{cx}" y="116" fill="{MUTED}">{TAGLINE}</text>'
        f'</g>'
        f'<line class="{MARK}-rule" x1="{cx - 110}" y1="138" x2="{cx + 110}" y2="138" '
        f'stroke="{ACCENT}" stroke-width="2" stroke-linecap="round"/>'
    )


def dragonize(path: pathlib.Path) -> None:
    svg = path.read_text(encoding="utf-8")

    if MARK in svg:
        print(f"{path}: juz przetworzony, pomijam")
        return

    m = re.match(r"<svg\b([^>]*)>", svg)
    if not m:
        sys.exit(f"BLAD: {path} nie zaczyna sie od <svg>")
    attrs = m.group(1)
    w = int(re.search(r'width="(\d+)"', attrs).group(1))
    h = int(re.search(r'height="(\d+)"', attrs).group(1))
    new_h = h + HEADER_H

    end = svg.rfind("</svg>")
    body = svg[m.end():end]

    # ── style zostaje na wierzchu, reszta zjezdza pod naglowek ───────────
    sm = re.search(r"<style>.*?</style>", body, re.S)
    if not sm:
        sys.exit(f"BLAD: nie znalazlem <style> w {path}")
    orig_style, rest = sm.group(0), body[sm.end():]

    # oryginalny prostokat tla znika - malujemy wlasny na calym plotnie
    rest, n = re.subn(
        r'<rect[^>]*class="fill-bg"[^>]*>(?:</rect>)?', "", rest, count=1
    )
    if n != 1:
        sys.exit(f"BLAD: nie znalazlem prostokata tla (.fill-bg) w {path}")

    cx = w // 2
    new_attrs = (
        re.sub(r'height="\d+"', f'height="{new_h}"', attrs)
        .replace(f'viewBox="0 0 {w} {h}"', f'viewBox="0 0 {w} {new_h}"')
    )

    svg = (
        f"<svg{new_attrs}>"
        f"{orig_style}"
        f"{build_head(cx)}"
        f'<rect x="0" y="0" width="{w}" height="{new_h}" fill="url(#dragon-bg)"/>'
        f"{build_header(cx)}"
        f'<g transform="translate(0,{HEADER_H})">{rest}</g>'
        f"</svg>"
    )

    # ── kolory jezykow -> paleta dragona ─────────────────────────────────
    found, seen = [], set()
    for mm in re.finditer(r"#[0-9A-Fa-f]{6}\b", svg):
        c = mm.group(0).lower()
        if c not in KEEP and c not in seen:
            seen.add(c)
            found.append(mm.group(0))

    for i, old in enumerate(found):
        svg = re.sub(re.escape(old), CATEGORICAL[i % len(CATEGORICAL)], svg, flags=re.I)

    path.write_text(svg, encoding="utf-8")
    print(
        f"{path}: naglowek + gradient, plotno {w}x{h} -> {w}x{new_h}, "
        f"{len(found)} kolorow jezykow przemalowanych"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uzycie: dragonize-render.py <plik.svg> [...]")
    for arg in sys.argv[1:]:
        dragonize(pathlib.Path(arg))
