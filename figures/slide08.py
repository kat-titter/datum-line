"""Slide 08: who else answers a question about your cells. Six tools, six questions, each with what it does not see.

Written whole. Datum Line is one row of the table and, since 17 Nov (Kat: "datum line should check yes to all of these", "Keep six
solid"), checks every column. What is proposed and not yet measured (identity and contamination read from control images) is said in
the notes line, the script and the judge Q&A, not on the slide. The collaborative line (use all of them) stays.
"""
from parts import *

ROWS = [
    ('DNA fingerprint (STR)', 'Is it the line the label says?', 'how the cells behave'),
    ('vendor certificate', 'Was it fine when it shipped?', 'anything after shipping'),
    ('plate controls', 'Did this plate work?', 'a whole lab drifting'),
    ('in-house platforms', 'Is my own data consistent?', 'lab differences; it removes them'),
    ('data factories', 'Where do I get cell data at scale?', 'other labs&#8217; &#8220;normal&#8221;'),
    ('Datum Line', 'Do my cells look &#8220;normal&#8221;, next to every other lab?', 'unstained images, not yet; identity and contamination from images, proposed and not yet measured'),
]
BACKED = {'DNA fingerprint (STR)': 'A7', 'plate controls': 'A1', 'in-house platforms': 'A3', 'data factories': 'A23', 'Datum Line': 'A10'}   # the board behind each gap
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
SEES_FOR_US = {'in-house platforms': 'unstained cells'}      # Datum Line's own gap, and who covers it
SHORT_NO = {'DNA fingerprint (STR)': 'cell behaviour', 'vendor certificate': 'after shipping', 'plate controls': 'lab drift',
            'in-house platforms': 'lab differences', 'data factories': 'other labs', 'Datum Line': 'unstained images'}


# 26 Oct (Kat: "datum line sees every lab: this slide is a mess. look @ examples of competitive landscape slides in pitch decks"):
# the conventional comparison table (practitioner guides: a table for feature differences, 4 to 6 defensible criteria, real
# competitors named, no rigged axes). Rows are the tools a phenotypic screen runs on; a check where a tool does the step, nothing
# where it does not; Datum Line's row in pink, a check in every column (17 Nov). It hosts every lab's raw control images
# and runs on them (Kat, 26 Oct: "datum line runs and hosts raw images not outputs").
# 17 Nov (Kat: "not just image platforms, other batch QC cell line ID tools"): the table is how a lab checks a batch today, one
# question a column: identity (STR), contamination (mycoplasma), the certificate that reports both when a line ships, plate QC (Z'),
# then the image tools as one row and the reference data. Still a check where the tool's own documentation says it answers the
# question and nothing where it does not. 17 Nov, later (Kat: "Keep six solid"): Datum Line checks all six; identity and culture clean
# from control images are proposed, not yet measured, and STR stays the standard for identity (the notes line, the script, the Q&A).
SCREEN = [  # (name, what it is, source, questions it answers)
    ('STR profiling', 'DNA fingerprint: is it the line the label says? ATCC', '[14]', {0}),
    ('Mycoplasma test', 'culture, DNA stain or PCR: is the culture clean?', '[29]', {1}),
    ('Certificate of analysis', 'ATCC, ECACC: identity and no mycoplasma, when the line shipped', '[29]', {0, 1}),
    ('Z&#8242;-factor', 'did this plate&#8217;s controls separate?', '[30]', {2}),
    ('CellProfiler, Harmony, pycytominer', 'measure cells, normalise each plate to its own DMSO; Genedata Screener too', '[32&#8211;35]', {3}),
    ('JUMP, Recursion', 'reference data at scale', '[7, 11]', {4}),
    ('Datum Line', 'every lab&#8217;s controls, one repository', '', {0, 1, 2, 3, 4, 5}),      # 17 Nov (Kat: "datum line should check yes to all of these"); was {5}
]      # 17 Nov, night (review fix 3: rings for the two proposed checks were drawn; Kat: "we can def detect contamination from images (culture clean), etc. all checks"): six solid
STEPS = ['cell line<br>identity', 'culture<br>clean', 'plate<br>worked', 'image<br>analysis', 'reference<br>data', 'every lab,<br>over time']      # the question each answers, two short lines each


def build():
    check = lambda c: (f'<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-label="yes">'
                       f'<path d="M5 12.5l4.5 4.5L19 7.5"/></svg>')
    cols = '390px repeat(6, minmax(0, 1fr))'
    head = (f'<div style="display:grid; grid-template-columns:{cols}; align-items:end; padding:0 16px 12px; border-bottom:2px solid {INK};">'
            f'<span></span>' + ''.join(f'<span style="text-align:center; white-space:nowrap; {SANS} font-size:22px; line-height:1.15; font-weight:{700 if k == len(STEPS) - 1 else 400}; '
                                       f'color:{PINK if k == len(STEPS) - 1 else INK2};">{n}</span>' for k, n in enumerate(STEPS)) + '</div>')
    rows = ''
    for k, (name, what, ref, met) in enumerate(SCREEN):
        dl = name == 'Datum Line'
        rows += (f'<div class="r" style="animation-delay:{0.3 + 0.13 * k:.2f}s; display:grid; grid-template-columns:{cols}; align-items:center; padding:5px 16px; '
                 f'{"background:rgba(190,30,116,0.06); border-radius:10px; margin-top:6px;" if dl else "border-bottom:1px solid #e4e8e9;"}">'
                 f'<span style="display:flex; flex-direction:column;"><span style="{SANS} font-size:{T_TEXT}px; font-weight:700; color:{PINK if dl else INK};">{name}</span>'
                 + pdf(f'<span style="{SANS} font-size:16px; color:{MUTE};">{what}{" " + ref if ref else ""}</span>') + '</span>'      # who they are: names the room knows; the gloss for the reader
                 + ''.join(f'<span style="display:flex; justify-content:center;">{check(PINK if dl else GREEN) if j in met else ""}</span>' for j in range(len(STEPS)))
                 + '</div>')
    glue = (f'<div class="f" style="animation-delay:1.6s; margin-top:14px; display:flex; align-items:center; gap:12px; {SANS} font-size:22px; color:{INK};">'
            f'{icon("map", PINK, 28)}<span>Datum Line hosts every lab&#8217;s raw control images, and runs on them.</span></div>')      # 26 Oct (Kat): raw images, not other tools' outputs
    # 26 Oct: "why not them" (JUMP an archive, Recursion its own cells, Revvity the microscope) lives in the script and docs/landscape.html
    figure = f'<div style="display:flex; flex-direction:column;">{head}{rows}{glue}</div>'
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:20px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(8)}
  {header('08', 'The landscape')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:900px; flex-shrink:0;">No tool watches every lab over time.<br><span style="color:{GREEN};">Datum Line asks all six, of every lab.</span></h2>
  </div>
  <div style="flex-grow:1; min-height:0; position:relative;">{figure}</div>
  {foot_line('how a lab checks a batch today: STR profiling, ATCC [14]; mycoplasma by culture, DNA stain and PCR, and the per-lot certificate of analysis that reports identity and no mycoplasma, ATCC and ECACC [29]; Z&#8242;-factor [30]; CellProfiler [32], Harmony, Revvity [33], pycytominer [34], Genedata Screener [35]; JUMP [7], Recursion [11]. A check: the tool answers that question, from its own documentation; a certificate answers when the line ships. Datum Line&#8217;s checks on identity and culture clean are read from control images: proposed, not yet measured; STR stays the standard for identity. It reads fluorescence today. docs/landscape.html')}
</div>'''
    return BASE_CSS, body, None
