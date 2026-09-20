"""Generate the 1280x640 social preview card used when a link is shared.

Usage:
    pip install pillow
    python scripts/build_social_preview.py

GitHub has no API for setting a repository's social preview, so upload the
result by hand: Settings -> General -> Social preview -> Edit -> Upload.
Links shared without one render as a bare grey box, which measurably hurts
click-through from Twitter, LinkedIn, Slack and Discord.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    print("Install Pillow:  pip install pillow", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "social-preview.png"

WIDTH, HEIGHT = 1280, 640
BG = (15, 18, 22)
CARD = (21, 26, 33)
FG = (230, 233, 238)
MUTED = (151, 163, 178)
ACCENT = (127, 178, 229)
LINE = (35, 42, 51)

TITLE = "Interview Cracker"
TAGLINE = "Interview prep that explains why an answer is right"
STATS = [
    ("19", "subject question banks"),
    ("20", "challenges by pattern"),
    ("150", "runnable examples"),
]
FOOTER = "github.com/Irish-Joseph/Interview_Cracker"

FONT_CANDIDATES = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_REGULAR = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load(paths: list[str], size: int):
    for path in paths:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main() -> int:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    bold_xl = load(FONT_CANDIDATES, 78)
    bold_md = load(FONT_CANDIDATES, 46)
    regular = load(FONT_REGULAR, 33)
    small = load(FONT_REGULAR, 26)

    # Accent bar down the left edge.
    draw.rectangle([0, 0, 14, HEIGHT], fill=ACCENT)

    draw.text((72, 96), TITLE, font=bold_xl, fill=FG)
    draw.text((72, 200), TAGLINE, font=regular, fill=MUTED)
    draw.line([(72, 268), (WIDTH - 72, 268)], fill=LINE, width=2)

    # Three stat cards.
    card_w, card_h, gap = 340, 150, 24
    x, y = 72, 318
    for value, label in STATS:
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=14,
                               fill=CARD, outline=LINE, width=2)
        draw.text((x + 26, y + 26), value, font=bold_md, fill=ACCENT)
        draw.text((x + 26, y + 90), label, font=small, fill=MUTED)
        x += card_w + gap

    draw.text((72, HEIGHT - 66), FOOTER, font=small, fill=MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT, "PNG", optimize=True)
    print("wrote {} ({}x{}, {:.0f} KB)".format(
        OUT.relative_to(ROOT), WIDTH, HEIGHT, OUT.stat().st_size / 1024))
    print("Upload it at: Settings -> General -> Social preview -> Edit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
