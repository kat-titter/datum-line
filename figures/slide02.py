"""Slide 02, the founder, the question and the gap (three views): a builder of its own since 26 Oct 2026. The slide is written in
figures/templates/slide02.html, edited there directly, and its images are filled from figures/assets on every build. Until then
it was hand-built HTML changed only by string and regex passes (coherence.py, refine.py); build_evidence keeps it out of them."""
from parts import inline_assets, drop_view


def build(talk=False):
    """17 Nov 2026 (Kat: "pitch should be pitch"): the talk ends on 02c. The fourth view (eleven cells, "Each lab judges normal
    alone") stays in the archive, where the template is used whole; the same cells are on 03 and 05."""
    t = open('figures/templates/slide02.html').read()
    if talk:
        dots = '<i></i><i></i><i></i><i></i></div>'
        assert t.count(dots) == 1, 'slide 02: four view dots expected'
        t = drop_view(t, 3).replace(dots, dots[8:], 1)
    return inline_assets(t)
