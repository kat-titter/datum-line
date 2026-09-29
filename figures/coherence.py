"""One word for one thing, figures numbered in order, one pager, pointers to the appendix.

Applied after the slides are written. Every edit is a no-op once made, so it can be re-run.
"""
import re

import parts

DARK = {4, 5, 8}                       # template indices of the dark talk slides
WORDS = {                              # template id -> [(old, new)]
    't8': [('Across the 13 JUMP sites.', 'Across the 13 JUMP labs.')],
    't9': [('3-site proof, then the set', '3-lab proof, then the set')],
    't10': [('Every number traces to results/e1, e1b, e2 or a numbered reference', 'Every number traces to a file in results/ or a numbered reference')],
    't11': [('>site</text>', '>lab</text>'),
            ('Whole site off: nobody in the building can tell.', 'Whole lab off: nobody inside it can tell.'),
            ('the nesting of well, plate, batch, site and field', 'the nesting of well, plate, batch, lab and field'),
            ('or a whole institution.', 'or a whole lab.'),
            ('compound plate (source_2, 1053601756)', 'compound plate (lab 2, 1053601756)'),
            ('font-weight: 500;">Fig. 2</span>', 'font-weight: 500;">Fig. A1</span>')],
    't12': [('V<sub>site</sub>', 'V<sub>lab</sub>'),
            ('Microscope model separates from site because models are shared across sites.', 'Microscope model separates from lab because models are shared across labs.')],
    't13': [('white-space: nowrap;">site</span>', 'white-space: nowrap;">lab</span>'),
            ('white-space: nowrap;">sites per well</span>', 'white-space: nowrap;">fields per well</span>')],
    't15': [('font-weight: 500;">Fig. 1</span>', 'font-weight: 500;">Fig. A5</span>')],
    't19': [('in eleven buildings.', 'in eleven labs.')],
    't3': [('font-weight:500;">Fig. 3</span>', 'font-weight:500;">Fig. 2</span>')],
}
POINTERS = {                           # a claim on a talk slide -> where the appendix backs it
    't3': [('"Centre each plate on its own controls: ', None)],   # the footer lives in META; handled below
}
PAGER = re.compile(r'<div aria-hidden="true" style="position:\s*absolute; left:\s*\d+px; bottom:\s*22px;[^>]*>(?:\s*<div[^>]*></div>)+\s*</div>')


def apply(deck):
    report = []
    for tid, pairs in WORDS.items():
        m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
        s = m.group(0)
        for old, new in pairs:
            n = s.count(old)
            if n:
                s = s.replace(old, new); report.append(f'{tid}: {n} x "{old[:40]}"')
        deck = deck[:m.start()] + s + deck[m.end():]
    for k in range(parts.N_TALK):
        m = re.search(r'<template id="t%d">.*?</template>' % k, deck, flags=re.S)
        s, n = PAGER.subn(lambda _: parts.dots(k + 1, dark=k in DARK), m.group(0), count=1)
        assert n == 1, f'no pager on slide {k + 1}'
        deck = deck[:m.start()] + s + deck[m.end():]
    # appendix pointer on slide 04's footer, which the deck keeps in META
    old = 'Right for discovery, wrong for QC."'
    if old in deck and 'wrong for QC. A3"' not in deck:
        deck = deck.replace(old, 'Right for discovery, wrong for QC. A3"')
    return deck, report
