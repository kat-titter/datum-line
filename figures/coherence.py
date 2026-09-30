"""One word for one thing, figures numbered in order, one pager, pointers to the appendix,
and little text: legends only under scientific figures, one line each. Detail lives in the
speaker script.

Applied after the slides are written. Every edit is a no-op once made, so it can be re-run.
"""
import json
import re

import parts
from parts import MONO, SANS

DARK = {4, 5, 6}                       # template indices of the dark talk slides
WORDS = {                              # template id -> [(old, new)]
    't0': [('<span style="color: #0f8f6c;">Confidence</span> without control.', 'The <span style="color: #0f8f6c;">map</span> every cell lab is missing.'),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:15px; color:#454c50;">the field</span></span></div>',
            '<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:15px; color:#454c50;">the field</span></span></div>'
            '<p style="margin:0; font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:19px; line-height:1.4; color:#454c50; max-width:560px;">'
            'Send the control images you already take. Get back where your cells sit against every other lab.</p>')],
    't26': [('Across the 13 JUMP sites.', 'Across the 13 JUMP labs.')],
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
}
TRIM = {                               # fewer words on slides that are not written whole
    't1': [('text-transform:uppercase; color:#666e72;">chance</span>', 'text-transform:uppercase; color:#666e72;">chance, 1 in 11 labs</span>')],
    't7': [('Which way to move them back', 'Your data, in the field&#8217;s frame'),
           ('A bad lot, flagged across labs', 'A baseline that tightens with every lab')],
    't25': [('The labs that build the reference use it free. The labs that cannot afford to be wrong pay for it.', 'Contributors use it free. The labs that cannot afford to be wrong pay.'),
           ('free, when they contribute control images', 'free, for contributing controls'),
           ('a subscription per cell line per quarter, ~$5&#8211;15k', '~$5&#8211;15k per line, per quarter'),
           ('the network: bad-lot alerts, later', 'the network'),
           ('Proposed, not yet validated. Bad-lot alerts across the network come after the certificate. Details in docs/roadmap.', 'Proposed, not yet validated.')],
    't26': [('The variation a real lab meets, generated rather than avoided. Same cells, same protocol, no drug, and it already looks like this.', 'Same cells, same protocol, no drug. It already looks like this.'),
           ('Across the 13 JUMP labs. A real lab adds cell lines, plate types, stacks and damaged plates on top.', 'Across the 13 JUMP labs.'),
           ('A public benchmark: name the failure. Bubble, focus, clipped well, bad lot, wrong label.', 'A public benchmark: name the failure.'),
           ('A foundation other people can stand on: one phenotypic space the field converges toward, instead of Google Images.', 'One shared space for the field, instead of Google Images.')],
    't2': [('Since 2023 the field&#8217;s reference is public: JUMP, CC0 [7].', 'Since 2023 the field&#8217;s reference is public [7].')],
}
PAPERS = [('Axiom Bio', 'Cell Painting in primary human hepatocytes', 'Cell Systems', 2026),
          ('Axiom Bio', 'Counting cells predicts bioactivity benchmarks', 'Nature Communications', 2026),
          ('AbbVie', 'A neuronal tau aggregation assay', 'J Biol Chem', 2025),
          ('MIT', 'Multiplexed expansion revealing', 'Nature Communications', 2024),
          ('MGH &#183; Harvard Medical School', 'Neurosteroid photolabeling of GABA<sub>A</sub> receptors', 'Eur J Med Chem', 2019)]


def founder(s):
    """Five papers as one short line each: what, where, when. Full citations are in the README."""
    a = s.index('My work</span>') + len('My work</span>')
    b = s.index('<div style="margin-top:auto; display:flex; flex-direction:column; gap:5px;">')
    rows = ''.join(
        f'<div class="ref" style="animation-delay:{0.5 + 0.1 * k:.2f}s; display:grid; grid-template-columns:18px 1fr; column-gap:12px; align-items:baseline;">'
        f'<span style="{MONO} font-size:14px; color:#be1e74;">{k + 1}</span>'
        f'<span style="{SANS} font-size:16px; line-height:1.3; color:#14171a;">{title}<br>'
        f'<span style="{MONO} font-size:13px; color:#666e72;"><em>{journal}</em> {year} &#183; {where}</span></span></div>'
        for k, (where, title, journal, year) in enumerate(PAPERS))
    return s[:a] + '\n      ' + rows + '\n      ' + s[b:]


def legends(deck):
    """Slide 03 keeps a source line; slide 04 keeps a one-line legend, written from results."""
    e1 = json.load(open('results/e1.json'))['all_sources']
    rt = json.load(open('results/e1-redteam.json'))['tests']
    m = re.search(r'<template id="t2">.*?</template>', deck, flags=re.S)
    s = re.sub(r'(<div style="[^"]*display:block;">)(?:(?!</div>).)*?Freedman(?:(?!</div>).)*?(</div>)',
               r'\1[6] Freedman et al., <em>PLoS Biol</em>, 2015. Search results: real U2OS images from six papers.\2', m.group(0), count=1, flags=re.S)
    deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'<template id="t1">.*?</template>', deck, flags=re.S)
    s = re.sub(r'(<div class="cite"[^>]*>).*?(</div>)',
               lambda k: (k.group(1) + '<span style="color:#14171a; font-weight:500;">Fig. 1</span> '
                          f'{e1["n_wells"]:,} untreated wells, {e1["n_labs"]} labs, plates held out. JUMP [7]' + k.group(2)),
               m.group(0), count=1, flags=re.S)
    deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S)
    meta = json.loads(m.group(1))
    game = next(e for e in meta if e['name'] == 'Game')
    game['steps']['foot'][1] = (f'Normalise each plate to its own controls: {100 * e1["balanced_accuracy"]:.1f}% becomes '
                                f'{100 * rt["plate_centred"]["balanced_accuracy"]:.0f}%. A3')
    return deck[:m.start(1)] + json.dumps(meta) + deck[m.end(1):]
PAGER = parts.PAGER_RE


def apply(deck):
    report = []
    for tid, pairs in list(WORDS.items()) + list(TRIM.items()):
        m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
        s = m.group(0)
        for old, new in pairs:
            n = 0 if new in s else s.count(old)      # an edit whose result contains its input is still made once
            if n:
                s = s.replace(old, new); report.append(f'{tid}: {n} x "{old[:40]}"')
        deck = deck[:m.start()] + s + deck[m.end():]
    for k in range(parts.N_TALK):
        m = re.search(r'<template id="t%d">.*?</template>' % k, deck, flags=re.S)
        s, n = PAGER.subn(lambda _: parts.dots(k + 1, dark=k in DARK), m.group(0), count=1)
        assert n == 1, f'no pager on slide {k + 1}'
        deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'<template id="t3">.*?</template>', deck, flags=re.S)
    deck = deck[:m.start()] + founder(m.group(0)) + deck[m.end():]
    deck = legends(deck)
    # one line under each instrument on board A16
    m = re.search(r'<template id="t26">.*?</template>', deck, flags=re.S)
    s = re.sub(r'<br>NA [0-9.]+ (?:·|&#183;) [0-9.]+ (?:µ|&#181;)m(?:/px)?', '', m.group(0))
    deck = deck[:m.start()] + s + deck[m.end():]
    return deck, report
