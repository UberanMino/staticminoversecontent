"""Sample scene recipes.

Each entry is a plain dict describing one finished image. `build.py` turns each
into a `minoverse.Scene` and renders it. Copy an entry, point the layers at your
own source images, and you have a new automated edit.

Coordinates and scales are fractions of the 1080x1920 canvas, so they are
resolution-independent. `src` paths are relative to the repo root.
"""

S = "assets/source_images"

RECIPES = {
    # --- Approach 1: atmospheric backgrounds -----------------------------

    # Deep-universe nebula. Uberan Mino front and centre; Chicken Guy and a
    # familiar cat drift in the upper field (with depth blur).
    "nebula_descent": {
        "bg": "nebula",
        "bg_kw": {"palette": "cosmic", "seed": 7, "stars": 1100},
        "style": "cosmic",
        "seed": 7,
        "glyph_seed": 3,
        "layers": [
            {"src": f"{S}/Uberan Mino.png", "x": 0.50, "y": 0.70, "scale": 0.66},
            {"src": f"{S}/chicken guy.png", "x": 0.24, "y": 0.30, "scale": 0.30,
             "blur": 1.2, "rot": -6},
            {"src": f"{S}/image (11).png", "x": 0.80, "y": 0.24, "scale": 0.24,
             "blur": 0.8, "flip": True},
        ],
    },

    # Trippy Mandelbrot fractal (explicitly one of the requested looks).
    # The same Uberan Mino figure echoed at two depths + a screaming Chicken Guy.
    "mandelbrot_rave": {
        "bg": "mandelbrot",
        "bg_kw": {"palette": "amber", "center": [-0.7463, 0.1102],
                  "zoom": 0.0009, "iters": 320},
        "style": "amber",
        "seed": 4,
        "glyph_seed": 11,
        "layers": [
            {"src": f"{S}/Uberan Mino (2).png", "x": 0.30, "y": 0.32, "scale": 0.34,
             "blur": 2.0, "opacity": 0.85, "rot": 8},
            {"src": f"{S}/chicken guy (3).png", "x": 0.74, "y": 0.66, "scale": 0.40,
             "aberration": 3},
            {"src": f"{S}/Uberan Mino.png", "x": 0.40, "y": 0.78, "scale": 0.60},
        ],
    },

    # Psychedelic plasma sky in hot ember tones — the orange, blown-out,
    # over-saturated register.
    "plasma_worship": {
        "bg": "plasma",
        "bg_kw": {"palette": "ember", "scale": 1.3, "seed": 2},
        "style": "ember",
        "seed": 9,
        "glyph_seed": 5,
        "layers": [
            {"src": f"{S}/chicken guy.png", "x": 0.52, "y": 0.62, "scale": 0.72,
             "saturation": 1.2},
            {"src": f"{S}/image (6).png", "x": 0.83, "y": 0.72, "scale": 0.42,
             "blur": 1.0, "flip": True},
            {"src": f"{S}/Uberan Mino (2).png", "x": 0.16, "y": 0.30, "scale": 0.28,
             "blur": 1.6, "opacity": 0.9},
        ],
    },

    # Julia fractal in vaporwave magenta/blue. Uberan Mino hero shot flanked by
    # the cat and the goose.
    "vapor_gucci": {
        "bg": "julia",
        "bg_kw": {"palette": "vapor", "c": [-0.8, 0.156], "zoom": 1.5},
        "style": "vapor",
        "seed": 15,
        "glyph_seed": 8,
        "layers": [
            {"src": f"{S}/image (11).png", "x": 0.22, "y": 0.34, "scale": 0.30,
             "blur": 1.0, "rot": 5},
            {"src": f"{S}/Uberan Mino.png", "x": 0.54, "y": 0.72, "scale": 0.64,
             "aberration": 2},
            {"src": f"{S}/image (6).png", "x": 0.84, "y": 0.40, "scale": 0.30,
             "blur": 1.4, "flip": True, "opacity": 0.92},
        ],
    },

    # Acid-green plasma. Chicken Guy triptych — the same figure echoed three
    # times at different depths, as in the reference edits.
    # --- Approach 2: silly heads swapped onto classical paintings --------

    # Van Gogh's "Self-Portrait with a Straw Hat" wearing Uberan Mino's head.
    # Light finishing keeps the painting legible; only the head + a few sigils
    # sit on top. (Echoes the reference edit that swapped a face onto a Van Gogh.)
    "vangogh_mino": {
        "bg": "image",
        "bg_kw": {"path": "assets/paintings/vangogh_strawhat.jpg"},
        "style": "paint_amber",
        "intensity": 0.35,
        "glyph_seed": 6,
        "glyph_count": 4,
        "seed": 6,
        "layers": [
            {"src": f"{S}/Uberan Mino (2).png", "x": 0.515, "y": 0.32, "scale": 0.29,
             "crop": [0.02, 0.0, 0.80, 0.4], "fade_bottom": 0.4},
        ],
    },

    # Poussin's "Abduction of the Sabine Women" with Chicken Guy dropped into
    # the melee. Portrait crop of the central group.
    "poussin_chicken": {
        "bg": "image",
        "bg_kw": {"path": "assets/paintings/poussin_sabine.jpg",
                  "crop": [0.42, 0.0, 0.80, 1.0]},
        "style": "paint",
        "intensity": 0.4,
        "glyph_seed": 9,
        "glyph_count": 4,
        "seed": 2,
        "layers": [
            {"src": f"{S}/chicken guy.png", "x": 0.5, "y": 0.46, "scale": 0.26,
             "crop": [0.12, 0.0, 0.95, 0.4], "fade_bottom": 0.35, "rot": -4},
        ],
    },

    "acid_triptych": {
        "bg": "plasma",
        "bg_kw": {"palette": "toxic", "scale": 1.6, "seed": 21},
        "style": "acid",
        "seed": 21,
        "glyph_seed": 14,
        "layers": [
            {"src": f"{S}/chicken guy (3).png", "x": 0.20, "y": 0.30, "scale": 0.30,
             "blur": 2.2, "opacity": 0.8, "rot": -10},
            {"src": f"{S}/chicken guy (3).png", "x": 0.80, "y": 0.34, "scale": 0.34,
             "blur": 1.4, "opacity": 0.9, "rot": 8, "flip": True},
            {"src": f"{S}/chicken guy.png", "x": 0.50, "y": 0.74, "scale": 0.62,
             "aberration": 3},
        ],
    },
}
