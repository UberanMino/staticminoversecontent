"""Automated figure isolation via rembg (U^2-Net).

The source material is flat photos with baked-in backgrounds (a KFC bucket, a
GTA scene, a swimming pool ...). This module lifts the figure out to a clean
transparent PNG, then caches it under ``characters/`` so the model only runs
once per source image.
"""
from __future__ import annotations

import hashlib
import os

from PIL import Image, ImageFilter

_SESSIONS: dict = {}
CACHE_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "characters")


def _session(model: str):
    if model not in _SESSIONS:
        from rembg import new_session
        _SESSIONS[model] = new_session(model)
    return _SESSIONS[model]


def _cache_key(path: str, model: str, feather: int) -> str:
    st = os.stat(path)
    raw = f"{os.path.abspath(path)}|{st.st_mtime_ns}|{st.st_size}|{model}|{feather}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def cutout(path: str, *, model: str = "u2net", feather: int = 2,
           trim: bool = True, use_cache: bool = True) -> Image.Image:
    """Return an RGBA cutout of the main figure in ``path``.

    ``model`` may be any rembg model, e.g. ``u2net`` (general) or
    ``u2net_human_seg`` (people). Results are cached under ``characters/``.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = _cache_key(path, model, feather)
    stem = os.path.splitext(os.path.basename(path))[0].replace(" ", "_")
    cache_path = os.path.join(CACHE_DIR, f"{stem}.{key}.png")
    if use_cache and os.path.exists(cache_path):
        return Image.open(cache_path).convert("RGBA")

    from rembg import remove
    src = Image.open(path).convert("RGBA")
    out = remove(
        src,
        session=_session(model),
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=12,
        alpha_matting_erode_size=8,
    ).convert("RGBA")

    if feather:
        a = out.getchannel("A").filter(ImageFilter.GaussianBlur(feather))
        out.putalpha(a)
    if trim:
        bbox = out.getbbox()
        if bbox:
            out = out.crop(bbox)

    out.save(cache_path)
    return out
