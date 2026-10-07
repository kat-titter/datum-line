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
    't3': [('Five labs, and the same <span style="color:#be1e74; font-weight:600;">unanswered question</span> at every bench. It made the science slow and wrong.', 'Five labs. One <span style="color:#be1e74; font-weight:600;">unanswered question.</span>'),
           ('text-decoration:none;">macrofluidic.me/resume</a>',
            'text-decoration:none;">macrofluidic.me/resume</a>'
            '<div style="display:flex; flex-direction:column; gap:4px; padding-top:6px; border-top:1px solid #e4e8e9;">'
            '<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:#666e72;">Team</span>'
            '<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:15px; line-height:1.35; color:#14171a;">One founder today.<br>Looking for a technical co-founder.</span>'
            '<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:15px; line-height:1.35; color:#666e72;">Collaborating labs: insitro, Axiom Bio, Soley.</span></div>'),
           ('font-size:15px; line-height:1.35; color:#666e72;">Collaborators in industry.</span>', 'font-size:15px; line-height:1.35; color:#666e72;">Collaborating labs: insitro, Axiom Bio, Soley.</span>')],
    't20': [('The test: e1 on the brightfield planes of the same 93,228 wells. <span style="color:#14171a; font-weight:600;">[pending]</span>',
             'First test: a frozen vision model names the lab from one brightfield field at 99.6%, 8 labs (results/e15). <span style="color:#14171a; font-weight:600;">Next: the whole map from brightfield.</span>')],
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
    't1': [('@keyframes fade', '.grid .tile { opacity:0; animation: fade .5s ease-out forwards; } '
            + ' '.join(f'.grid .tile:nth-child({k}) {{ animation-delay:{0.15 * k:.2f}s; }}' for k in range(1, 7)) + '\n@keyframes fade'),
           ('text-transform:uppercase; color:#666e72;">chance</span>', 'text-transform:uppercase; color:#666e72;">chance, 1 in 11 labs</span>')],
    't25': [('>What is at stake<', '>what is at stake<'), ('>What they pay<', '>what they pay<'), ('>What it builds<', '>what it builds<'),
            ('The labs that build the reference use it free. The labs that cannot afford to be wrong pay for it.', 'Contributors use it free. The labs that cannot afford to be wrong pay.'),
           ('free, when they contribute control images', 'free, for contributing controls'),
           ('a subscription per cell line per quarter, ~$5&#8211;15k', '~$5&#8211;15k per line, per quarter'),
           ('the network: bad-lot alerts, later', 'the network'),
           ('Proposed, not yet validated. Bad-lot alerts across the network come after the certificate. Details in docs/roadmap.', 'Proposed, not yet validated.')],
    't26': [('The variation a real lab meets, generated rather than avoided. Same cells, same protocol, no drug, and it already looks like this.', 'Same cells, same protocol, no drug. It already looks like this.'),
           ('Across the 13 JUMP labs. A real lab adds cell lines, plate types, stacks and damaged plates on top.', 'Across the 13 JUMP labs.'),
           ('A public benchmark: name the failure. Bubble, focus, clipped well, bad lot, wrong label.', 'A public benchmark: name the failure.'),
           ('A foundation other people can stand on: one phenotypic space the field converges toward, instead of Google Images.', 'One shared space for the field, instead of Google Images.'),
           ('One shared space for the field, instead of Google Images.', 'The benchmark every model is graded on. The glue between labs and the companies that buy their data.'),
           ('The benchmark every method is graded on: the glue between labs that make data and companies that buy it.', 'The benchmark every model is graded on. The glue between labs and the companies that buy their data.'),
           ('The benchmark every method is graded on, normalization to bioactivity: the glue between the labs that make data and the companies that buy it.', 'The benchmark every model is graded on. The glue between labs and the companies that buy their data.')],
    't2': [('&#8220;Do my cells <span style="color:#be1e74;">look normal?</span>&#8221;</h2>', 'Today: <span style="color:#be1e74;">search, ask, guess.</span></h2>'),
           ('>of R&amp;D before the SOP was fixed<', '>of R&amp;D<'), ('>of R&amp;D, before the fix<', '>of R&amp;D<'),
           ('>developing cells that were already good enough<', '>of development<'), ('>on cells that were already fine<', '>of development<'),
           ('Since 2023 the field&#8217;s reference is public: JUMP, CC0 [7].', 'Since 2023 the field&#8217;s reference is public [7].'),
           ('Since 2023 the field&#8217;s reference is public [7].', 'Since 2023 the field&#8217;s reference is public [7].<br>Since 2025 cell data carries regulatory weight [9].'),
           ('>the field&#8217;s reference goes public [7]<', '>reference goes public [7]<'), ('>cell data starts to carry regulatory weight [9]<', '>cell data gains regulatory weight [9]<'), ('>the map: eleven labs, one frame<', '>the map<'),
           ('<p style="margin:0; font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:17px; line-height:1.35; color:#454c50;">Since 2023 the field&#8217;s reference is public [7].<br>Since 2025 cell data carries regulatory weight [9].</p>',
            '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0; position:relative; padding-top:14px;">'
            '<div aria-hidden="true" style="position:absolute; left:6px; right:6px; top:5px; height:2px; background:linear-gradient(90deg,#0f8f6c,#be1e74);"></div>'
            + ''.join(f'<div style="position:relative; padding-right:12px;"><div aria-hidden="true" style="position:absolute; left:0; top:-14px; width:12px; height:12px; border-radius:50%; background:{col};"></div>'
                      f'<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:{col};">{yr}</span><br>'
                      f'<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:15px; line-height:1.3; color:#454c50;">{what}</span></div>'
                      for yr, what, col in (('2023', 'reference goes public [7]', '#0f8f6c'), ('2025', 'cell data gains regulatory weight [9]', '#0f8f6c'), ('2026', 'the map', '#be1e74')))
            + '</div>')],
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
               r'\1[6] Freedman et al., <em>PLoS Biol</em>, 2015. Six real U2OS papers.\2', m.group(0), count=1, flags=re.S)
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
    game['steps']['foot'][1] = f'{100 * e1["balanced_accuracy"]:.1f}% \u2192 {100 * rt["plate_centred"]["balanced_accuracy"]:.0f}% normalised to itself. A3'
    game['steps']['foot'][2] = 'Shape, not count.'
    return deck[:m.start(1)] + json.dumps(meta) + deck[m.end(1):]
PAGER = parts.PAGER_RE


def apply(deck):
    report = []
    for tid, pairs in list(WORDS.items()) + list(TRIM.items()):
        m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
        s = m.group(0)
        for old, new in pairs:
            n = 0 if (new and new in s) else s.count(old)      # an edit whose result contains its input is still made once; an empty result removes
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
