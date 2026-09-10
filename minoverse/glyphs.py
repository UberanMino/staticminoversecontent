"""Floating golden 'sigil' decorations and particle flecks.

These are the little amber runic hexagons, chevrons, dotted rings, four-point
sparkles and gold flecks that drift over the reference edits. Drawn as vectors
onto a transparent layer so they can be composited anywhere.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw, ImageFilter

GOLD = (224, 164, 40, 255)
GOLD_SOFT = (240, 200, 90, 230)


def _poly(cx, cy, r, n, rot=0.0):
    return [
        (cx + r * math.cos(rot + 2 * math.pi * i / n),
         cy + r * math.sin(rot + 2 * math.pi * i / n))
        for i in range(n)
    ]


def _hex_sigil(d, cx, cy, r, col):
    d.polygon(_poly(cx, cy, r, 6, math.pi / 6), outline=col, width=max(2, r // 14))
    d.polygon(_poly(cx, cy, r * 0.6, 6, math.pi / 6), outline=col, width=max(1, r // 20))
    for p in _poly(cx, cy, r * 0.6, 6, math.pi / 6):
        d.line([(cx, cy), p], fill=col, width=1)


def _chevrons(d, cx, cy, r, col):
    for k in range(3):
        rr = r * (0.5 + 0.28 * k)
        d.line([(cx - rr, cy + rr * 0.5), (cx, cy - rr * 0.5),
                (cx + rr, cy + rr * 0.5)], fill=col, width=max(2, r // 16), joint="curve")


def _dotted_ring(d, cx, cy, r, col, dots=14):
    for p in _poly(cx, cy, r, dots):
        d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=col)
    d.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4],
              outline=col, width=2)


def _sparkle(d, cx, cy, r, col):
    for a in range(4):
        ang = a * math.pi / 2
        d.line([(cx, cy),
                (cx + r * math.cos(ang), cy + r * math.sin(ang))],
               fill=col, width=2)
    d.ellipse([cx - r * 0.12, cy - r * 0.12, cx + r * 0.12, cy + r * 0.12], fill=col)


_SHAPES = [_hex_sigil, _chevrons, _dotted_ring, _sparkle]


def sigil_layer(w: int, h: int, *, count=7, flecks=90, seed=0,
                color=GOLD) -> Image.Image:
    """Return a transparent RGBA layer of scattered gold sigils + flecks."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    for _ in range(flecks):
        x, y = rng.randint(0, w), rng.randint(0, h)
        s = rng.randint(2, 6)
        a = rng.randint(120, 240)
        d.polygon(_poly(x, y, s, rng.choice([3, 4]), rng.random() * 3),
                  fill=(color[0], color[1], color[2], a))

    for _ in range(count):
        x = rng.randint(int(w * 0.05), int(w * 0.95))
        y = rng.randint(int(h * 0.05), int(h * 0.95))
        r = rng.randint(int(h * 0.03), int(h * 0.08))
        shape = rng.choice(_SHAPES)
        a = rng.randint(150, 235)
        shape(d, x, y, r, (color[0], color[1], color[2], a))

    # soft glow copy under the crisp lines
    glow = layer.filter(ImageFilter.GaussianBlur(3))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out = Image.alpha_composite(out, glow)
    out = Image.alpha_composite(out, layer)
    return out
