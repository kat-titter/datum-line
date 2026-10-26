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
SHORT_NO = {'DNA fingerprint (STR)': 'cell behaviour', 'vendor certificate': 'after shipping', 'plate controls': 'lab drift',
            'in-house platforms': 'lab differences', 'data factories': 'other labs', 'Datum Line': 'which cell line<br>unstained images'}


def build():
    cols = 'grid-template-columns:256px 1.35fr 1fr;'
    head = (f'<div style="display:grid; {cols} gap:24px; padding:0 20px 10px; border-left:3px solid transparent; border-bottom:1px solid {GRID};">'
            + ''.join(f'<span class="pdfv" style="{SANS} font-size:16px; color:{MUTE};">{s}</span>' for s in ('tool', 'answers'))
            + f'<span style="display:flex; gap:8px; align-items:center; {SANS} font-size:18px; color:{MUTE};">{icon("blind-spot", MUTE, 20)}misses</span></div>')
    last = len(ROWS) - 1
    ref = lambda tool: (f' <span class="pdf" style="{MONO} font-size:13px; color:{MUTE}; white-space:nowrap;">{BACKED[tool]}</span>' if tool in BACKED else '')
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; {cols} gap:24px; align-items:center; flex:1; align-content:center; '
        f'padding:12px 20px; {"border-bottom:none;" if k == last else "border-bottom:1px solid #eceff0;"} '
        f'{"border-left:3px solid " + GREEN + "; background:rgba(15,143,108,0.05);" if k == last else "border-left:3px solid transparent;"}">'
        f'<span style="display:flex; gap:12px; align-items:center; {SANS} font-size:20px; font-weight:600; color:{INK};">'
        f'{icon(TOOL_ICON[tool], GREEN if k == last else INK2, 26)}<span>{tool.replace(" (STR)", pdf(" (STR)"))}</span></span>'
        f'<span style="{SANS} font-size:20px; font-weight:{600 if k == last else 500}; line-height:1.3; color:{GREEN if k == last else INK2};">'
        f'{talk_span(STAGE_Q[tool]) + pdf(q) if tool in STAGE_Q else q}</span>'
        f'<span style="{SANS} font-size:18px; line-height:1.35; color:{MUTE};">{talk_span(SHORT_NO[tool])}{pdf(no)}{ref(tool)}</span></div>'
        for k, (tool, q, no) in enumerate(ROWS))
    tiles = ''.join(      # 26 Oct (Kat: "simplify the busy figures"): the stage as six tiles, the reader keeps the table
        f'<div class="r" style="animation-delay:{0.2 + 0.08 * k:.2f}s; {CARD} padding:18px 20px 16px; display:flex; flex-direction:column; gap:10px; min-width:0;'
        f'{" box-shadow:inset 0 0 0 2px " + GREEN + "; background:#f3faf7;" if k == last else ""}">'
        f'<span style="display:flex; gap:10px; align-items:center; {SANS} font-size:18px; font-weight:600; color:{GREEN if k == last else INK2};">'
        f'{icon(TOOL_ICON[tool], GREEN if k == last else INK2, 26)}{tool.replace(" (STR)", "")}</span>'
        f'<span style="{SANS} font-size:24px; font-weight:600; line-height:1.2; color:{GREEN if k == last else INK};">{STAGE_Q.get(tool, q)}</span>'
        f'<span style="margin-top:auto; display:flex; gap:8px; align-items:flex-start; {SANS} font-size:18px; line-height:1.3; color:{MUTE};">'
        f'{icon("blind-spot", MUTE, 20)}<span>{SHORT_NO[tool].replace("<br>", ", ")}</span></span></div>'
        for k, (tool, q, no) in enumerate(ROWS))
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(8)}
  {header('08', 'Who else')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:620px; flex-shrink:0;">Six questions, six tools.<br><span style="color:{GREEN};">Use all of them.</span></h2>
    {pdf(f'<p style="margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE};">Each answers one question well.<br>Each misses something, Datum Line too.</p>')}
  </div>
  <div class="talk" style="flex-grow:1; min-height:0; display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); grid-template-rows:repeat(2, minmax(0, 1fr)); gap:16px;">{tiles}</div>
  <div class="r pdf" style="animation-delay:0.1s; {CARD} padding:16px 4px 6px; flex-direction:column; flex-grow:1; min-height:0;">{head}{rows}</div>
  {foot_line('STR: ATCC [14]')}
</div>'''
    return BASE_CSS, body, None
