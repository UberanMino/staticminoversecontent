"""Scene composition: background + figure layers + glyphs + finishing pass."""
from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image, ImageEnhance, ImageFilter

from . import backgrounds, effects, glyphs
from .cutout import cutout


@dataclass
class Layer:
    """One figure placed on the canvas.

    Positions/scales are fractions of the canvas so recipes stay
    resolution-independent.
    """
    src: str                      # path to a source image
    x: float = 0.5                # centre x (0..1)
    y: float = 0.7                # centre y (0..1)
    scale: float = 0.5            # height as a fraction of canvas height
    rot: float = 0.0              # degrees
    opacity: float = 1.0
    blur: float = 0.0             # gaussian blur (depth / motion)
    flip: bool = False
    model: str = "u2net"
    saturation: float = 1.0       # per-layer colour push
    aberration: int = 0           # per-layer channel split
    crop: tuple | None = None     # (l, t, r, b) fractions of the cutout to keep
                                  # e.g. head-only for a painting head-swap
    fade_bottom: float = 0.0      # fraction of height to fade to transparent at
                                  # the bottom (dissolves a head-swap seam)


@dataclass
class Scene:
    bg: str                       # background generator kind
    bg_kw: dict = field(default_factory=dict)
    layers: list = field(default_factory=list)
    style: str = "amber"          # finishing grade
    glyphs: bool = True
    glyph_seed: int = 0
    glyph_count: int = 7          # number of large sigils
    intensity: float = 1.0        # 0..1 degradation strength (low for paintings)
    width: int = 1080
    height: int = 1920
    seed: int = 0

    # -- rendering ----------------------------------------------------------

    def _place(self, canvas: Image.Image, layer: Layer):
        fig = cutout(layer.src, model=layer.model)
        if layer.crop:
            l, t, r, b = layer.crop
            w0, h0 = fig.size
            fig = fig.crop((int(l * w0), int(t * h0), int(r * w0), int(b * h0)))
            bbox = fig.getbbox()
            if bbox:
                fig = fig.crop(bbox)
        if layer.flip:
            fig = fig.transpose(Image.FLIP_LEFT_RIGHT)
        target_h = int(self.height * layer.scale)
        target_w = max(1, int(fig.width * target_h / fig.height))
        fig = fig.resize((target_w, target_h), Image.LANCZOS)

        if layer.saturation != 1.0:
            rgb = ImageEnhance.Color(fig.convert("RGB")).enhance(layer.saturation)
            rgb.putalpha(fig.getchannel("A"))
            fig = rgb
        if layer.aberration:
            rgb = effects.chromatic_aberration(fig.convert("RGB"), layer.aberration)
            rgb.putalpha(fig.getchannel("A"))
            fig = rgb
        if layer.rot:
            fig = fig.rotate(layer.rot, expand=True, resample=Image.BICUBIC)
        if layer.blur:
            fig = fig.filter(ImageFilter.GaussianBlur(layer.blur))
        if layer.fade_bottom > 0:
            import numpy as np
            a = np.asarray(fig.getchannel("A"), float)
            h = a.shape[0]
            start = int(h * (1.0 - layer.fade_bottom))
            if start < h:
                ramp = np.linspace(1.0, 0.0, h - start)
                a[start:, :] *= ramp[:, None]
            fig.putalpha(Image.fromarray(a.astype("uint8")))
        if layer.opacity < 1.0:
            a = fig.getchannel("A").point(lambda p: int(p * layer.opacity))
            fig.putalpha(a)

        cx, cy = int(self.width * layer.x), int(self.height * layer.y)
        canvas.alpha_composite(fig, (cx - fig.width // 2, cy - fig.height // 2))

    def render(self) -> Image.Image:
        bg = backgrounds.make(self.bg, self.width, self.height, **self.bg_kw)
        canvas = bg.convert("RGBA")

        for layer in self.layers:
            self._place(canvas, layer)

        if self.glyphs:
            sig = glyphs.sigil_layer(self.width, self.height, seed=self.glyph_seed,
                                     count=self.glyph_count)
            canvas = Image.alpha_composite(canvas, sig)

        out = effects.finish(canvas.convert("RGB"), style=self.style,
                             seed=self.seed, intensity=self.intensity)
        return out


def build_scene(spec: dict) -> Scene:
    """Build a Scene from a plain dict (as loaded from a recipe file)."""
    layers = [Layer(**l) for l in spec.get("layers", [])]
    return Scene(
        bg=spec["bg"],
        bg_kw=spec.get("bg_kw", {}),
        layers=layers,
        style=spec.get("style", "amber"),
        glyphs=spec.get("glyphs", True),
        glyph_seed=spec.get("glyph_seed", spec.get("seed", 0)),
        glyph_count=spec.get("glyph_count", 7),
        intensity=spec.get("intensity", 1.0),
        width=spec.get("width", 1080),
        height=spec.get("height", 1920),
        seed=spec.get("seed", 0),
    )
