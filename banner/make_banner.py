#!/usr/bin/env python3

import colorsys
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 1010
PHOTO_H = 358
PANEL_H = 196
H = PHOTO_H + PANEL_H

FG = (197, 201, 197)
MUTED = (122, 131, 130)
DIM = (90, 96, 95)
ACCENT = (196, 178, 138)
TRACK = (43, 44, 42)

BACKDROP = [(0.0, (30, 38, 34)), (0.55, (26, 24, 24)), (1.0, (29, 30, 38))]

FALLBACK = [
    (138, 154, 123),
    (139, 164, 176),
    (196, 178, 138),
    (196, 116, 110),
    (137, 146, 167),
    (142, 164, 162),
    (182, 146, 123),
]

SAMPLE_REGION = (430, 20, 960, 330)
SAMPLE_COLORS = 48
SAMPLE_MIN_LIGHT = 0.20
SAMPLE_MAX_LIGHT = 0.86
SAMPLE_MIN_DISTANCE = 55
LIFT_FLOOR = 0.50
LIFT_CEIL = 0.74
SATURATION = (0.20, 0.30)

TAGLINE = "full-stack · embedded · devops"
LEFT_TITLE = "BY THE NUMBERS"
RIGHT_TITLE = "LANGUAGES"

PAD = 52
COLUMN_X = 470
GUTTER = W - PAD
SCRIM_END = 0.58
SCRIM_MAX = 130

TOP_LANGUAGES = 5
ROW_H = 23
SPECTRUM_H = 5
SPECTRUM_DIM = 0.34

FONT_FILES = {}


def font_index():
    if FONT_FILES:
        return FONT_FILES
    roots = [
        "/usr/share/fonts", "/usr/local/share/fonts",
        os.path.expanduser("~/.local/share/fonts"),
        os.path.expanduser("~/.fonts"),
    ]
    for root in roots:
        for dirpath, _, names in os.walk(root):
            for name in names:
                FONT_FILES.setdefault(name, os.path.join(dirpath, name))
    return FONT_FILES


def font_file(*candidates):
    index = font_index()
    for name in candidates:
        if name in index:
            return index[name]
    sys.exit(f"BLAD: brak fontu, szukane: {', '.join(candidates)}")


def regular(size):
    return ImageFont.truetype(font_file(
        "JetBrainsMono-Regular.ttf", "JetBrainsMonoNerdFont-Regular.ttf",
        "JetBrainsMonoNLNerdFont-Regular.ttf", "DejaVuSansMono.ttf",
    ), size)


def bold(size):
    return ImageFont.truetype(font_file(
        "JetBrainsMono-Bold.ttf", "JetBrainsMonoNerdFont-Bold.ttf",
        "JetBrainsMonoNLNerdFont-Bold.ttf", "DejaVuSansMono-Bold.ttf",
    ), size)


def lightness(rgb):
    return colorsys.rgb_to_hls(*[c / 255 for c in rgb])[1]


def distance(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def lifted(rgb):
    hue, light, sat = colorsys.rgb_to_hls(*[c / 255 for c in rgb])
    light = min(max(light, LIFT_FLOOR), LIFT_CEIL)
    sat = min(max(sat, SATURATION[0]), SATURATION[1])
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(hue, light, sat))


def palette_from(frame, count):
    sample = frame.crop(SAMPLE_REGION).convert(
        "P", palette=Image.Palette.ADAPTIVE, colors=SAMPLE_COLORS
    ).convert("RGB")
    tally = sorted(
        sample.getcolors(maxcolors=SAMPLE_COLORS * 4) or [], reverse=True
    )

    picked = []
    for _, rgb in tally:
        if not SAMPLE_MIN_LIGHT <= lightness(rgb) <= SAMPLE_MAX_LIGHT:
            continue
        if any(distance(rgb, taken) < SAMPLE_MIN_DISTANCE for taken in picked):
            continue
        picked.append(rgb)
        if len(picked) == count:
            break

    colors = [lifted(rgb) for rgb in picked]
    return colors + FALLBACK[: max(0, count - len(colors))]


def number(value):
    return f"{value:,}"


def decimal(value, places=1):
    return f"{value:.{places}f}"


def backdrop():
    strip = Image.new("RGB", (W, 1))
    pixels = strip.load()
    for x in range(W):
        t = x / (W - 1)
        for i in range(len(BACKDROP) - 1):
            left, right = BACKDROP[i], BACKDROP[i + 1]
            if left[0] <= t <= right[0]:
                k = (t - left[0]) / (right[0] - left[0])
                pixels[x, 0] = tuple(
                    round(left[1][c] + (right[1][c] - left[1][c]) * k)
                    for c in range(3)
                )
                break
    return strip.resize((W, PANEL_H))


def paint_scrim(canvas):
    mask = Image.new("L", (W, 1))
    for x in range(W):
        fade = max(0.0, 1.0 - x / (W * SCRIM_END))
        mask.putpixel((x, 0), int(SCRIM_MAX * fade ** 1.4))
    canvas.paste(
        Image.new("RGBA", (W, PHOTO_H), (12, 12, 16, 255)),
        (0, 0),
        mask.resize((W, PHOTO_H)),
    )


def paint_panel(canvas, edge):
    base = backdrop()
    bleed = Image.blend(
        edge.crop((0, PHOTO_H - 1, W, PHOTO_H)).convert("RGB")
            .resize((W, PANEL_H)).filter(ImageFilter.GaussianBlur(7)),
        base,
        0.55,
    )
    settle = Image.new("L", (1, PANEL_H))
    for y in range(PANEL_H):
        settle.putpixel((0, y), min(255, int(255 * (y / 30) ** 0.7)))
    panel = Image.composite(base, bleed, settle.resize((W, PANEL_H)))
    canvas.paste(panel.convert("RGBA"), (0, PHOTO_H))


def tracked(draw, xy, text, font, fill, tracking, shadow=False):
    x, y = xy
    for char in text:
        if shadow:
            draw.text((x + 2, y + 2), char, font=font, fill=(10, 10, 12, 170))
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking
    return x


def name_lines(name):
    parts = name.split()
    if len(parts) < 2:
        return [name]
    return [parts[0], " ".join(parts[1:])]


def draw_identity(draw, name, tagline):
    lines = name_lines(name)
    size = 46
    while size > 22:
        face = bold(size)
        if max(draw.textlength(line, font=face) for line in lines) <= 372:
            break
        size -= 1
    face = bold(size)
    step = round(size * 1.24)
    top = 108 if len(lines) > 1 else 142

    for i, line in enumerate(lines):
        tracked(draw, (PAD, top + i * step), line, face, FG, 0, shadow=True)

    rule_y = top + len(lines) * step + 18
    draw.line(
        [(PAD + 2, rule_y), (PAD + 152, rule_y)], fill=ACCENT + (255,), width=2
    )
    tracked(
        draw, (PAD + 2, rule_y + 18), tagline, regular(14), MUTED, 2.4,
        shadow=True,
    )


def draw_tiles(draw, top, tiles):
    tracked(draw, (PAD, top), LEFT_TITLE, bold(12), ACCENT, 3)
    for i, (value, label) in enumerate(tiles):
        x = PAD + 196 * (i % 2)
        y = top + 32 + 62 * (i // 2)
        draw.text((x, y), value, font=bold(25), fill=FG + (255,))
        draw.text((x + 2, y + 34), label, font=regular(11), fill=DIM + (255,))


def draw_languages(draw, top, ranked, total_bytes, palette):
    tracked(draw, (COLUMN_X, top), RIGHT_TITLE, bold(12), ACCENT, 3)
    draw.text(
        (GUTTER, top), f"{decimal(total_bytes / 1e6)} MB of code",
        font=regular(12), fill=DIM + (255,), anchor="ra",
    )

    label = regular(12)
    value = bold(12)
    bar_x = COLUMN_X + 136
    bar_w = 264

    for i, (name, share) in enumerate(ranked[:TOP_LANGUAGES]):
        y = top + 30 + ROW_H * i
        middle = y + ROW_H // 2
        draw.text((COLUMN_X, middle), name, font=label, fill=MUTED + (255,),
                  anchor="lm")
        draw.rounded_rectangle(
            [bar_x, middle - 3, bar_x + bar_w, middle + 3], radius=3,
            fill=TRACK + (255,),
        )
        filled = max(6, round(bar_w * share / 100))
        draw.rounded_rectangle(
            [bar_x, middle - 3, bar_x + filled, middle + 3], radius=3,
            fill=palette[i % len(palette)] + (255,),
        )
        draw.text((GUTTER, middle), f"{decimal(share)}%", font=value,
                  fill=FG + (255,), anchor="rm")


def dimmed(color):
    base = BACKDROP[1][1]
    return tuple(
        round(c * (1 - SPECTRUM_DIM) + b * SPECTRUM_DIM)
        for c, b in zip(color, base)
    )


def draw_spectrum(canvas, ranked, palette):
    strip = Image.new("RGBA", (W, SPECTRUM_H))
    painter = ImageDraw.Draw(strip)
    x = 0.0
    for i, (_, share) in enumerate(ranked):
        width = W * share / 100
        painter.rectangle(
            [x, 0, x + width, SPECTRUM_H],
            fill=dimmed(palette[i % len(palette)]) + (255,),
        )
        x += width
    canvas.paste(strip, (0, H - SPECTRUM_H))


def ranking(stats):
    weights = stats.get("shares") or stats["languages"]
    total = sum(weights.values())
    return [(name, 100 * weight / total) for name, weight in
            sorted(weights.items(), key=lambda item: -item[1])]


def build(edge_path, stats_path, out_path):
    with open(stats_path, encoding="utf-8") as handle:
        stats = json.load(handle)

    languages = stats["languages"]
    ranked = ranking(stats)
    frame = Image.open(edge_path).convert("RGB")
    palette = palette_from(frame, TOP_LANGUAGES + 2)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    paint_scrim(canvas)
    paint_panel(canvas, frame)

    draw = ImageDraw.Draw(canvas)
    draw_identity(draw, stats["name"], stats["tagline"] or TAGLINE)

    top = PHOTO_H + 22
    draw.line(
        [(COLUMN_X - 30, top - 4), (COLUMN_X - 30, top + 152)],
        fill=TRACK + (255,), width=1,
    )
    draw_tiles(draw, top, [
        (number(stats["repos"]), "repositories"),
        (number(len(languages)), "languages"),
        (number(stats["stars"]), "stars"),
        (number(stats["contributions"]), "contributions / year"),
    ])
    draw_languages(draw, top, ranked, sum(languages.values()), palette)
    draw_spectrum(canvas, ranked, palette)

    canvas.save(out_path)
    print(f"{out_path}: {W}x{H}, {len(ranked)} jezykow")


if __name__ == "__main__":
    build(*sys.argv[1:4])
