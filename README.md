# Minoverse image builder

Automated pipeline for building the still images used across the **Uberan Mino /
Minoverse** project — the loud, degraded, cut-and-paste edits where the
characters get dropped into atmospheric worlds or onto old master paintings.

It reproduces the two hand-made approaches as code:

1. **Atmospheric** — figures cut into trippy backdrops: mandelbrot / julia
   fractals, deep-universe nebulae, psychedelic plasma skies.
2. **Old-painting head-swap** — the sillier heads cut onto the figures of a
   classical painting.

Every image is a 1080×1920 (9:16) PNG, ready for TikTok / Reels / Shorts.

> **Samples first:** see the [`output/`](output/) folder for the seven images
> the current recipes produce.

---

## How it works

```
source photo ──rembg──► transparent cutout ──┐
                                              ├─► composite ─► finishing pass ─► PNG
procedural / painting background ─────────────┘   (+ gold sigils)
```

| Step | Module | What it does |
|------|--------|--------------|
| Background | `minoverse/backgrounds.py` | Generates fractal / nebula / plasma backdrops from a seed, or loads a painting file. |
| Cutout | `minoverse/cutout.py` | Isolates the figure from its baked-in background with **rembg** (U²-Net). Cached under `characters/`. |
| Compose | `minoverse/compose.py` | Places figures (position, scale, rotation, blur, opacity, crop, fade) on the background. |
| Sigils | `minoverse/glyphs.py` | Scatters the floating gold runic hexagons, chevrons and flecks. |
| Finish | `minoverse/effects.py` | Split-tone colour grade + bloom + chromatic aberration + grain + scanlines + vignette + JPEG crunch. |

The source photos in `assets/source_images/` are *flat* — the figure already has
a background baked in (a KFC bucket, a GTA scene, a swimming pool). rembg lifts
the figure out to a clean transparent PNG, so no manual masking is needed.

---

## Setup

```bash
pip install -r requirements.txt
```

On Claude Code for the web this runs automatically via the `SessionStart` hook
(`.claude/settings.json` → `scripts/setup.sh`).

The rembg model (~176 MB) downloads itself on the first build and is reused
afterwards.

## Build

```bash
python build.py               # render every recipe into output/
python build.py nebula_descent mandelbrot_rave   # render specific ones
python build.py --list        # list recipe names
```

---

## Recipes

Recipes live in [`recipes/__init__.py`](recipes/__init__.py) as plain dicts.
Coordinates and scales are fractions of the canvas, so they're
resolution-independent.

| Recipe | Approach | Background | Characters |
|--------|----------|------------|-----------|
| `nebula_descent`  | atmospheric | cosmic nebula      | Uberan Mino, Chicken Guy, cat |
| `mandelbrot_rave` | atmospheric | amber mandelbrot   | Uberan Mino ×2, Chicken Guy |
| `plasma_worship`  | atmospheric | ember plasma       | Chicken Guy, goose, Uberan Mino |
| `vapor_gucci`     | atmospheric | vaporwave julia    | Uberan Mino, cat, goose |
| `acid_triptych`   | atmospheric | toxic-green plasma | Chicken Guy ×3 |
| `vangogh_mino`    | painting    | Van Gogh self-portrait | Uberan Mino (head) |
| `poussin_chicken` | painting    | Poussin, *Sabine Women* | Chicken Guy (head) |

### Adding your own

1. Drop source photos into `assets/source_images/` (any background — rembg
   handles it) and old paintings into `assets/paintings/`.
2. Copy a recipe and edit it:

```python
"my_edit": {
    "bg": "mandelbrot",                       # or nebula / julia / plasma / image
    "bg_kw": {"palette": "amber"},
    "style": "amber",                          # finishing grade
    "layers": [
        {"src": f"{S}/Uberan Mino.png", "x": 0.5, "y": 0.7, "scale": 0.62},
        {"src": f"{S}/chicken guy.png", "x": 0.25, "y": 0.3, "scale": 0.3,
         "blur": 1.2},                          # depth blur on a background figure
    ],
},
```

3. `python build.py my_edit`

**Layer options:** `x`, `y`, `scale` (fractions of the canvas), `rot`,
`opacity`, `blur`, `flip`, `saturation`, `aberration`, `crop` (`[l,t,r,b]`
fractions — use it to keep only a head for a painting swap), `fade_bottom`
(dissolve a head-swap seam), `head_pos` (`[x, y]` fractions — aligns the
character's head with the painting's head; omit `x`, `y` when using this),
`model` (rembg model, e.g. `u2net_human_seg`).

**Backgrounds:** `mandelbrot`, `julia`, `nebula`, `plasma` (each takes a
`palette` from `amber`, `acid`, `vapor`, `ember`, `cosmic`, `toxic`), and
`image` (`{"path": ..., "crop": [l,t,r,b]}`).

**Finishing styles:** `amber`, `acid`, `vapor`, `cosmic`, `ember`, and the
gentle `paint` / `paint_amber` for paintings. `intensity` (0–1) scales the
degradation — keep it low (~0.35) for paintings so the artwork stays readable.

---

## Characters

Uberan Mino and Chicken Guy are the leads and appear most; the cat, goose and
others are supporting cast used sparingly. See the Minoverse knowledge base for
the lore behind each.

## Assets & licensing

- `assets/source_images/` — Minoverse project source material.
- `assets/paintings/` — public-domain artworks from The Met's Open Access
  program (`isPublicDomain: true`); see `assets/paintings/SOURCES.md`. Both
  artists died well over a century ago, so the works are public domain.
- Backgrounds under the atmospheric approach are generated from code, so they
  carry no third-party rights.
