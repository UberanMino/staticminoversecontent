#!/usr/bin/env bash
# Install the Python dependencies for the Minoverse image builder.
# Run automatically by the SessionStart hook (see .claude/settings.json) and
# safe to run by hand. Never fails the session: errors are reported, not fatal.
set -u

cd "$(dirname "$0")/.." || exit 0

echo "[minoverse setup] installing Python dependencies ..."
pip install --quiet --disable-pip-version-check -r requirements.txt \
    && echo "[minoverse setup] dependencies ready." \
    || echo "[minoverse setup] pip install failed - run 'pip install -r requirements.txt' manually."

# The rembg model (~176 MB) downloads lazily on the first build; nothing to do here.
exit 0
