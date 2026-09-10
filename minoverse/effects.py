"""The Minoverse aesthetic post-processing stack.

These operate on RGB ``PIL.Image`` and are what give a flat composite that
cheap-edit, VHS / degraded-JPEG, heavily colour-graded look seen in the
reference edits.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter


def _np(img):
    return np.asarray(img.convert("RGB"), float)


def _img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"), "RGB")


def chromatic_aberration(img: Image.Image, shift: int = 4) -> Image.Image:
    """Offset the red and blue channels for that split-fringe VHS look."""
    r, g, b = img.convert("RGB").split()
    r = ImageChops.offset(r, shift, 0)
    b = ImageChops.offset(b, -shift, -shift // 2)
    return Image.merge("RGB", (r, g, b))


def scanlines(img: Image.Image, strength: float = 0.18, gap: int = 3) -> Image.Image:
    arr = _np(img)
    h = arr.shape[0]
    mask = np.ones(h)
    mask[::gap] = 1.0 - strength
    arr *= mask[:, None, None]
    return _img(arr)


def grain(img: Image.Image, amount: float = 14.0, seed: int = 0) -> Image.Image:
    rng = np.random.default_rng(seed)
    arr = _np(img)
    noise = rng.normal(0, amount, arr.shape[:2])[:, :, None]
    return _img(arr + noise)


def vignette(img: Image.Image, strength: float = 0.55) -> Image.Image:
    w, h = img.size
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    d = np.sqrt(((xs / w) - 0.5) ** 2 + ((ys / h) - 0.5) ** 2) / 0.707
    m = 1.0 - strength * np.clip(d, 0, 1) ** 2.2
    return _img(_np(img) * m[:, :, None])


def bloom(img: Image.Image, threshold: int = 205, radius: int = 12,
          gain: float = 0.6) -> Image.Image:
    arr = _np(img)
    lum = arr.mean(2)
    bright = np.where(lum[:, :, None] > threshold, arr, 0)
    glow = _img(bright).filter(ImageFilter.GaussianBlur(radius))
    return _img(arr + _np(glow) * gain)


def color_grade(img: Image.Image, *, tint=(255, 150, 40), shadow=(20, 8, 40),
                strength=0.35, contrast=1.18, saturation=1.35) -> Image.Image:
    """Push highlights toward ``tint`` and shadows toward ``shadow`` (split tone)."""
    arr = _np(img) / 255.0
    lum = arr.mean(2, keepdims=True)
    hi = np.asarray(tint, float) / 255.0
    lo = np.asarray(shadow, float) / 255.0
    graded = arr * (1 - strength) + (lo * (1 - lum) + hi * lum) * strength
    out = _img(graded * 255.0)
    out = ImageEnhance.Color(out).enhance(saturation)
    out = ImageEnhance.Contrast(out).enhance(contrast)
    return out


def jpeg_crunch(img: Image.Image, quality: int = 18) -> Image.Image:
    """Round-trip through low-quality JPEG for authentic compression artefacts."""
    import io
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


# --- presets -----------------------------------------------------------------

def finish(img: Image.Image, *, style="amber", seed=0, crunch=True,
           intensity=1.0) -> Image.Image:
    """Full finishing pass. ``style`` selects the split-tone grade.

    ``intensity`` (0..1) scales the degradation effects (bloom, aberration,
    grain, scanlines, vignette). Use a low value for the painting head-swaps so
    the artwork stays legible; leave it at 1.0 for the loud atmospheric edits.
    """
    grades = {
        "amber":  dict(tint=(255, 150, 40), shadow=(30, 8, 46), strength=0.34),
        "acid":   dict(tint=(200, 255, 90), shadow=(8, 30, 60), strength=0.32),
        "vapor":  dict(tint=(255, 120, 210), shadow=(30, 10, 80), strength=0.36),
        "cosmic": dict(tint=(120, 200, 255), shadow=(10, 4, 40), strength=0.30),
        "ember":  dict(tint=(255, 120, 30), shadow=(20, 0, 10), strength=0.40),
        # gentle grades for the classical-painting approach
        "paint":       dict(tint=(240, 200, 130), shadow=(30, 18, 40), strength=0.16),
        "paint_amber": dict(tint=(255, 190, 90), shadow=(28, 12, 30), strength=0.20),
    }
    g = dict(grades.get(style, grades["amber"]))
    g["strength"] *= 0.5 + 0.5 * intensity
    out = color_grade(img, **g)
    out = bloom(out, gain=0.5 * intensity)
    if intensity > 0:
        out = chromatic_aberration(out, shift=max(1, round(3 * intensity)))
    out = grain(out, amount=12.0 * intensity, seed=seed)
    out = scanlines(out, strength=0.12 * intensity)
    out = vignette(out, strength=0.5 * intensity)
    if crunch:
        out = jpeg_crunch(out, quality=int(22 + (1 - intensity) * 55))
    return out
