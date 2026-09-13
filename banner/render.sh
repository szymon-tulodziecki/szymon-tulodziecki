#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="$here/hero-robots.gif"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

grade="hue=h=-22:s=0.42,eq=contrast=1.12:brightness=-0.05,\
colorbalance=rs=-0.18:gs=0.05:bs=0.02:gm=0.03"

python3 "$here/fetch_stats.py" "$work/stats.json"

ffmpeg -y -v error -ss 2 -i "$here/source.mp4" -frames:v 1 \
    -vf "$grade" "$work/edge.png"

python3 "$here/make_banner.py" "$work/edge.png" "$work/stats.json" \
    "$work/banner.png"

ffmpeg -y -v error -i "$here/source.mp4" -i "$work/banner.png" \
    -filter_complex "[0:v]$grade,pad=1010:554:0:0:color=black,fps=10[v];\
[v][1:v]overlay=0:0[o];[o]split[a][b];\
[a]palettegen=stats_mode=full:max_colors=256[p];\
[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" \
    -loop 0 "$out"

echo "$out: $(du -h "$out" | cut -f1)"
