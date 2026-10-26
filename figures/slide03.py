"""Slide 03, the game and the reveal (two views): a builder of its own since 26 Oct 2026. The slide is written in
figures/templates/slide03.html, edited there directly, and its images are filled from figures/assets on every build. Until then
it was hand-built HTML changed only by string and regex passes (coherence.py, refine.py); build_evidence keeps it out of them."""
from parts import inline_assets


def build():
    return inline_assets(open('figures/templates/slide03.html').read())
