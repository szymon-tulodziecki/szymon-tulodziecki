#!/usr/bin/env python3
"""Doprowadza wygenerowany render 3D do pelnej palety Kanagawa Dragon.

github-profile-3d-contrib przez SETTING_JSON pozwala ustawic tylko czesc
kolorow, wiec dwie rzeczy trzeba poprawic po fakcie:

  1. Tlo - SETTING_JSON przyjmuje wylacznie jednolity kolor, a chcemy gradient.
  2. Kolory jezykow - brane sa z linguista GitHuba (zolty JS, niebieski Python,
     czerwony Blade...) i kompletnie rozjezdzaja sie z paleta.

    python3 .github/scripts/dragonize-render.py profile-3d-contrib/profile-dragon.svg
"""

import re
import sys
import pathlib

GRAD_ID = "dragon-bg"
GRAD = (
    f'<defs><linearGradient id="{GRAD_ID}" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#1A1818"/>'
    '<stop offset="1" stop-color="#1F2422"/>'
    "</linearGradient></defs>"
)

# kolory, ktore juz sa dragonem - nie ruszamy ich przy przemalowywaniu jezykow
KEEP = {
    "#c5c9c5", "#181616", "#c4b28a", "#7a8382", "#8ba4b0",
    "#1a1818", "#1f2422",
}

# sekwencja dla wykresu jezykow - rozroznialne, ale wszystkie w palecie.
# Znaczenie niesie legenda z nazwami, wiec nie potrzebujemy kolorow linguista.
CATEGORICAL = [
    "#8A9A7B",  # szalwia
    "#8BA4B0",  # przykurzony blekit
    "#C4B28A",  # piaskowy
    "#C4746E",  # przygaszona czerwien
    "#A292A3",  # wyblakly roz
    "#8992A7",  # stalowy fiolet
    "#8EA4A2",  # szarozielony
    "#B6927B",  # terakota
]


def dragonize(path: pathlib.Path) -> None:
    svg = path.read_text(encoding="utf-8")

    if GRAD_ID in svg:
        print(f"{path}: juz przetworzony, pomijam")
        return

    # ── 1. gradient w tle ────────────────────────────────────────────────
    # tylko .fill-bg; .stroke-bg zostaje jednolity, bo sluzy do obrysow bryl
    svg, n = re.subn(
        r"(\.fill-bg\s*\{\s*fill:\s*)#[0-9A-Fa-f]{6}(\s*;?\s*\})",
        rf"\1url(#{GRAD_ID})\2",
        svg,
        count=1,
    )
    if n != 1:
        sys.exit(f"BLAD: nie znalazlem reguly .fill-bg w {path}")

    svg, n = re.subn(r"(<svg\b[^>]*>)", rf"\1{GRAD}", svg, count=1)
    if n != 1:
        sys.exit(f"BLAD: nie znalazlem znacznika <svg> w {path}")

    # ── 2. kolory jezykow -> paleta dragona ──────────────────────────────
    # to, co zostalo z twardych hexow i nie jest dragonem, to kolory linguista.
    # Kolejnosc pierwszego wystapienia = malejacy udzial jezyka.
    found, seen = [], set()
    for m in re.finditer(r"#[0-9A-Fa-f]{6}\b", svg):
        c = m.group(0).lower()
        if c not in KEEP and c not in seen:
            seen.add(c)
            found.append(m.group(0))

    for i, old in enumerate(found):
        svg = re.sub(re.escape(old), CATEGORICAL[i % len(CATEGORICAL)], svg, flags=re.I)

    path.write_text(svg, encoding="utf-8")
    print(f"{path}: gradient + {len(found)} kolorow jezykow przemalowanych na dragona")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uzycie: dragonize-render.py <plik.svg> [...]")
    for arg in sys.argv[1:]:
        dragonize(pathlib.Path(arg))
