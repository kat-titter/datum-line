"""Slide 08: who else answers a question about your cells. Six tools, six questions, each with what it does not see.

Written whole. Datum Line is one row among six, with its own gap stated, so the slide reads as a landscape and not a scorecard.
Each gap names the board that backs it; the collaborative line (use all of them) is the headline, not a footnote.
"""
from parts import *

ROWS = [
    ('DNA fingerprint (STR)', 'Is it the line the label says?', 'how the cells behave'),
    ('vendor certificate', 'Was it fine when it shipped?', 'anything after shipping'),
    ('plate controls', 'Did this plate work?', 'a whole lab drifting'),
    ('in-house platforms', 'Is my own data consistent?', 'lab differences; it removes them'),
    ('data factories', 'Where do I get cell data at scale?', 'other labs&#8217; &#8220;normal&#8221;'),
    ('Datum Line', 'Do my cells look &#8220;normal&#8221;, next to every other lab?', 'which cell line it is; unstained images, not yet'),
]
BACKED = {'DNA fingerprint (STR)': 'A7', 'plate controls': 'A1', 'in-house platforms': 'A3', 'data factories': 'A23', 'Datum Line': 'A7, A10'}   # the board behind each gap
# on stage: each tool drawn, its question short, its gap in two or three words (fair: Datum Line's own gap too); the PDF keeps ROWS whole
TOOL_ICON = {'DNA fingerprint (STR)': 'dna', 'vendor certificate': 'shipped', 'plate controls': 'plate', 'in-house platforms': 'in-house',
             'data factories': 'factory', 'Datum Line': 'map'}
STAGE_Q = {'Datum Line': '&#8220;Normal&#8221;, next to every lab?', 'DNA fingerprint (STR)': 'Right cell line?', 'vendor certificate': 'Fine when shipped?', 'in-house platforms': 'Own data consistent?',
           'data factories': 'Cell data at scale?'}
# 26 Oct (Kat: "six tools: show industry knowledge, name specific tools, illustrate covering each others blind spots and synergy"):
# each tool by the products a lab would name (sources in README 14, 29-32), and the hub that shows who sees whose blind spot
NAMED = {'DNA fingerprint (STR)': 'ATCC STR profiling', 'vendor certificate': 'ATCC, ECACC certificates', 'plate controls': 'Z&#8242;-factor',
         'in-house platforms': 'Incucyte, CellProfiler', 'data factories': 'Recursion, JUMP'}
NAMED_REF = {'DNA fingerprint (STR)': '[14]', 'vendor certificate': '[29]', 'plate controls': '[30]', 'in-house platforms': '[31, 32]', 'data factories': '[7, 11]'}
SEES_FOR_US = {'DNA fingerprint (STR)': 'which cell line', 'in-house platforms': 'unstained cells'}      # Datum Line's own gaps, and who covers them
SHORT_NO = {'DNA fingerprint (STR)': 'cell behaviour', 'vendor certificate': 'after shipping', 'plate controls': 'lab drift',
            'in-house platforms': 'lab differences', 'data factories': 'other labs', 'Datum Line': 'which cell line<br>unstained images'}


# 26 Oct (Kat: "six tools; commonly used in phenotypic screening space. reduce # of columns? pink emphasis what blind spots
# datum line fills, how it's the glue / central repo"): the slide's tools are the ones a phenotypic screen runs on, each named and
# sourced; five steps of a screen as columns; every tool sees one lab, so the last column is the blind spot they share, and Datum
# Line fills it in pink, as the repository under all of them. ROWS above stays for the landscape document (build_docs).
SCREEN = [  # (name, what it is, source, steps it does)
    ('CellProfiler', 'image analysis, open source', '[32]', {0}),
    ('Harmony', 'Revvity&#8217;s Opera Phenix software', '[33]', {0}),
    ('pycytominer', 'profiles, each plate to its own DMSO', '[34]', {2}),
    ('Genedata Screener', 'screen QC and normalisation', '[35]', {1, 2}),
    ('JUMP, Recursion', 'reference data at scale', '[7, 11]', {3}),
]
STEPS = ['measure each cell', 'pass each plate', 'scale to its own controls', 'reference data', '&#8220;normal&#8221; across labs, over time']


def build():
    C, P, lx = 42, 150, 300
    cols = len(STEPS)
    assert set().union(*(m for *_, m in SCREEN)) == set(range(cols - 1)), 'the five tools cover every step but the last'
    hdr = ''.join(f'<span style="position:absolute; left:{lx + k * P + C / 2:.0f}px; bottom:0; transform:translateX(-50%); width:{P - 10}px; text-align:center; '
                  f'{SANS} font-size:18px; line-height:1.2; color:{PINK if k == cols - 1 else INK2}; font-weight:{700 if k == cols - 1 else 400};">{n}</span>' for k, n in enumerate(STEPS))
    def row(label, sub, met, d, fill, bold=False, colour=INK):
        cells = ''.join(f'<i class="pop" style="animation-delay:{d + 0.04 * j:.2f}s; position:absolute; left:{lx + j * P}px; top:0; width:{C}px; height:{C}px; border-radius:7px; '
                        f'background:{fill(j) if j in met else "#e4e8e9"};"></i>' for j in range(cols))
        return (f'<div class="r" style="animation-delay:{d - 0.1:.2f}s; position:relative; height:{C}px;">'
                f'<span style="position:absolute; left:0; top:50%; transform:translateY(-50%); display:flex; flex-direction:column; width:{lx - 20}px; {SANS} font-size:21px; '
                f'font-weight:{700 if bold else 600}; line-height:1.1; color:{colour};">{label}'
                + (pdf(f'<span style="{SANS} font-size:16px; font-weight:400; color:{MUTE}; margin-top:2px;">{sub}</span>') if sub else '') + f'</span>{cells}</div>')      # the gloss, for the reader
    tools = ''.join(row(n, what + pdf(' ' + ref), met, 0.3 + 0.15 * k, lambda j: '#6cc3a3') for k, (n, what, ref, met) in enumerate(SCREEN))
    dl = row('Datum Line', 'every lab&#8217;s controls, one repository', {cols - 1}, 1.4, lambda j: PINK, bold=True, colour=PINK)      # its one square: the blind spot all five share
    # the glue: Datum Line runs under every tool, a pink band across all the columns, feeding each lab's controls in
    band = (f'<div class="f" style="animation-delay:1.8s; position:relative; height:26px;">'
            f'<i style="position:absolute; left:{lx - 8}px; width:{cols * P - (P - C) + 16}px; top:4px; height:18px; border-radius:9px; background:{PINK}; opacity:.18;"></i>'
            f'<span style="position:absolute; left:{lx + 4}px; top:2px; {SANS} font-size:18px; color:{PINK};">under every tool: each lab&#8217;s controls, aligned in one place</span></div>')
    key = (f'<div class="f" style="animation-delay:2.6s; display:flex; gap:22px; align-items:center; {SANS} font-size:18px; color:{INK2};">'
           f'<span style="display:inline-flex; gap:8px; align-items:center;"><i style="width:18px; height:18px; border-radius:4px; background:#6cc3a3;"></i>does this step</span>'
           f'<span style="display:inline-flex; gap:8px; align-items:center;"><i style="width:18px; height:18px; border-radius:4px; background:#e4e8e9;"></i>blind spot</span>'
           f'<span style="display:inline-flex; gap:8px; align-items:center;"><i style="width:18px; height:18px; border-radius:4px; background:{PINK};"></i>what Datum Line fills</span></div>')
    figure = (f'<div style="position:relative; height:100%; display:flex; flex-direction:column; gap:10px;">'
              f'<div style="position:relative; height:46px;">{hdr}</div>'
              f'<div style="display:flex; flex-direction:column; gap:8px;">{tools}</div>{band}{dl}'
              f'<div style="margin-top:auto;">{key}</div></div>')      # the band and Datum Line's row show the glue; no separate 'together' row
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(8)}
  {header('08', 'The landscape')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:900px; flex-shrink:0;">Each tool sees one lab.<br><span style="color:{GREEN};">Datum Line sees every lab.</span></h2>
  </div>
  <div style="flex-grow:1; min-height:0; position:relative;">{figure}</div>
  {foot_line('tools as a phenotypic screen runs them: CellProfiler [32]; Harmony, Revvity [33]; pycytominer [34]; Genedata Screener [35]; JUMP [7], Recursion [11]. Each works inside one lab&#8217;s data; none compares a lab&#8217;s controls with other labs&#8217;. The wider landscape (cell-line checks, vendor certificates): docs/landscape.html')}
</div>'''
    return BASE_CSS, body, None
