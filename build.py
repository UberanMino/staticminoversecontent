#!/usr/bin/env python3
"""Build Minoverse edits from recipes.

    python build.py                 # render every recipe -> output/
    python build.py nebula_descent  # render one (or several) by name
    python build.py --list          # list available recipes

Each recipe generates a procedural background, isolates the figures from the
source photos with rembg (cached under characters/), composites them, drops in
the gold sigils, and runs the full VHS / colour-grade finishing pass.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

from minoverse import build_scene
from recipes import RECIPES

OUT = os.path.join(os.path.dirname(__file__), "output")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render Minoverse edits.")
    ap.add_argument("names", nargs="*", help="recipe names (default: all)")
    ap.add_argument("--list", action="store_true", help="list recipes and exit")
    ap.add_argument("--out", default=OUT, help="output directory")
    args = ap.parse_args(argv)

    if args.list:
        for name in RECIPES:
            print(name)
        return 0

    names = args.names or list(RECIPES)
    unknown = [n for n in names if n not in RECIPES]
    if unknown:
        print(f"unknown recipe(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"available: {', '.join(RECIPES)}", file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    for name in names:
        t0 = time.time()
        print(f"[build] {name} ...", flush=True)
        scene = build_scene(RECIPES[name])
        img = scene.render()
        path = os.path.join(args.out, f"{name}.png")
        img.save(path)
        print(f"[build] {name} -> {path}  ({img.size[0]}x{img.size[1]}, "
              f"{time.time() - t0:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
