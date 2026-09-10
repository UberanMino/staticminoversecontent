"""Procedural Minoverse backgrounds.

Everything here is generated from code (no stock imagery), so it is copyright
clean and reproducible from a seed. These cover the "atmospheric" approach:
trippy mandelbrot fractals, deep-universe nebulae and psychedelic plasma skies.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

# --- colour ramps ------------------------------------------------------------

PALETTES = {
    # name        dark ->                                    -> bright
    "amber":  [(8, 4, 18), (90, 24, 8), (232, 128, 20), (255, 232, 150)],
    "acid":   [(6, 0, 26), (0, 110, 90), (168, 240, 40), (250, 255, 205)],
    "vapor":  [(18, 0, 42), (120, 20, 158), (60, 120, 255), (255, 128, 205)],
    "ember":  [(0, 0, 0), (74, 10, 10), (214, 58, 18), (255, 176, 62)],
    "cosmic": [(2, 0, 10), (20, 10, 60), (120, 40, 160), (90, 190, 255)],
    "toxic":  [(2, 8, 6), (10, 60, 40), (40, 190, 120), (210, 255, 180)],
}


def ramp(palette, n: int = 512) -> np.ndarray:
    """Return an (n, 3) float lookup table interpolated across ``palette``."""
    cols = np.asarray(PALETTES[palette] if isinstance(palette, str) else palette, float)
    stops = np.linspace(0.0, 1.0, len(cols))
    xs = np.linspace(0.0, 1.0, n)
    return np.stack([np.interp(xs, stops, cols[:, c]) for c in range(3)], axis=1)


def _apply_ramp(t: np.ndarray, palette) -> np.ndarray:
    """Map a float field ``t`` in [0, 1] through a palette to an RGB uint8 array."""
    lut = ramp(palette)
    idx = np.clip((t * (len(lut) - 1)).astype(int), 0, len(lut) - 1)
    return lut[idx].astype("uint8")


def _img(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"), "RGB")


# --- value noise -------------------------------------------------------------

def _value_noise(w: int, h: int, octaves: int, rng: np.random.Generator) -> np.ndarray:
    """Fractal value noise in [0, 1], built by summing upscaled random octaves."""
    acc = np.zeros((h, w), float)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cells = 2 ** (o + 2)
        base = rng.random((cells, cells))
        layer = np.asarray(
            Image.fromarray((base * 255).astype("uint8")).resize((w, h), Image.BICUBIC),
            float,
        ) / 255.0
        acc += amp * layer
        tot += amp
        amp *= 0.55
    acc /= tot
    acc -= acc.min()
    acc /= max(acc.max(), 1e-6)
    return acc


# --- generators --------------------------------------------------------------

def mandelbrot(w: int, h: int, *, center=(-0.746, 0.108), zoom=0.0055,
               iters=260, palette="amber", swirl=1.0, seed=0) -> Image.Image:
    """A detailed, smoothly-coloured Mandelbrot region -> trippy fractal sky."""
    ar = w / h
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    cx = (xs / w - 0.5) * zoom * w * ar / max(w, 1) * 3.0 + center[0]
    cy = (ys / h - 0.5) * zoom * h / max(h, 1) * 3.0 + center[1]
    c = cx + 1j * cy
    z = np.zeros_like(c)
    div = np.zeros((h, w), float)
    mask = np.ones((h, w), bool)
    for i in range(iters):
        z[mask] = z[mask] * z[mask] + c[mask]
        esc = mask & (z.real * z.real + z.imag * z.imag > 4.0)
        # smooth (continuous) iteration count
        div[esc] = i + 1 - np.log(np.log(np.abs(z[esc]) + 1e-9) + 1e-9) / np.log(2)
        mask &= ~esc
    div[mask] = iters
    t = div / iters
    t = np.power(t, 0.42)                       # lift midtones
    t = (t * swirl + np.sin(t * 9.0) * 0.06 * swirl) % 1.0
    return _img(_apply_ramp(t, palette))


def julia(w: int, h: int, *, c=(-0.8, 0.156), zoom=1.6, iters=220,
          palette="vapor", seed=0) -> Image.Image:
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    zx = (xs / w - 0.5) * 2.0 * zoom * (w / h)
    zy = (ys / h - 0.5) * 2.0 * zoom
    z = zx + 1j * zy
    cc = complex(*c)
    div = np.zeros((h, w), float)
    mask = np.ones((h, w), bool)
    for i in range(iters):
        z[mask] = z[mask] * z[mask] + cc
        esc = mask & (z.real ** 2 + z.imag ** 2 > 4.0)
        div[esc] = i + 1 - np.log(np.log(np.abs(z[esc]) + 1e-9) + 1e-9) / np.log(2)
        mask &= ~esc
    div[mask] = iters
    t = np.power(div / iters, 0.5)
    return _img(_apply_ramp(t, palette))


def nebula(w: int, h: int, *, palette="cosmic", octaves=6, stars=900, seed=0) -> Image.Image:
    """Deep-universe background: layered cloud noise plus a scatter of stars."""
    rng = np.random.default_rng(seed)
    clouds = _value_noise(w, h, octaves, rng)
    ridged = 1.0 - np.abs(_value_noise(w, h, octaves, rng) * 2 - 1)
    field = np.clip(clouds * 0.7 + ridged * 0.5, 0, 1)
    field = np.power(field, 1.4)
    arr = _apply_ramp(field, palette).astype(float)
    # stars
    sx = rng.integers(0, w, stars)
    sy = rng.integers(0, h, stars)
    br = rng.random(stars) ** 3
    for x, y, b in zip(sx, sy, br):
        v = 140 + b * 115
        arr[y, x] = np.maximum(arr[y, x], v)
    img = _img(arr)
    glow = img.filter(ImageFilter.GaussianBlur(1.2))
    return Image.blend(img, glow, 0.35)


def plasma(w: int, h: int, *, palette="acid", scale=1.0, seed=0) -> Image.Image:
    """Psychedelic plasma sky from summed sinusoids."""
    rng = np.random.default_rng(seed)
    ph = rng.random(4) * 6.283
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    x = xs / w * 6.283 * (2.5 * scale)
    y = ys / h * 6.283 * (2.5 * scale)
    v = (
        np.sin(x + ph[0])
        + np.sin(y * 0.8 + ph[1])
        + np.sin((x + y) * 0.5 + ph[2])
        + np.sin(np.sqrt((x - 3.14) ** 2 + (y - 3.14) ** 2) + ph[3])
    )
    t = (v - v.min()) / (v.max() - v.min())
    t = (t + np.sin(t * 12.0) * 0.05) % 1.0
    img = _img(_apply_ramp(t, palette))
    return img.filter(ImageFilter.GaussianBlur(0.6))


def from_image(w: int, h: int, *, path: str, crop=None, seed=0) -> Image.Image:
    """Use a local image (e.g. a classical painting) as the backplate.

    ``crop`` is an optional (left, top, right, bottom) box in *fractions* of the
    source image, applied before a centre-cropping cover-fit to the canvas.
    """
    src = Image.open(path).convert("RGB")
    if crop:
        sw, sh = src.size
        box = (int(crop[0] * sw), int(crop[1] * sh),
               int(crop[2] * sw), int(crop[3] * sh))
        src = src.crop(box)
    # cover-fit: scale so the image fills the canvas, then centre-crop
    sw, sh = src.size
    scale = max(w / sw, h / sh)
    src = src.resize((max(1, int(sw * scale)), max(1, int(sh * scale))), Image.LANCZOS)
    sw, sh = src.size
    left, top = (sw - w) // 2, (sh - h) // 2
    return src.crop((left, top, left + w, top + h))


GENERATORS = {
    "mandelbrot": mandelbrot,
    "julia": julia,
    "nebula": nebula,
    "plasma": plasma,
    "image": from_image,
}


def make(kind: str, w: int, h: int, **kw) -> Image.Image:
    return GENERATORS[kind](w, h, **kw)
