"""Slide 08: who else answers a question about your cells. Six tools, six questions, each with what it does not see.

Written whole. Datum Line is one row among six, with its own gap stated, so the slide reads as a landscape and not a scorecard.
"""
from parts import *

ROWS = [
    ('STR authentication', 'Is it the line the label says?', 'behaviour'),
    ('vendor certificate', 'Was it fine when it shipped?', 'after shipping'),
    ('plate controls', 'Did this plate work?', 'whole lab drifting'),
    ('phenomics platforms', 'Is my own data consistent?', 'lab differences, by design'),
    ('data factories', 'Where do I get cell data at scale?', 'other labs&#8217; normal'),
    ('Datum Line', 'Where do my cells sit, against every other lab?', 'which line &#183; beyond fluorescence, yet'),
]


def build():
    cols = 'grid-template-columns:220px 1.15fr 1fr;'
    head = (f'<div style="display:grid; {cols} gap:24px; padding:0 20px 10px; border-left:3px solid transparent; border-bottom:1px solid #d3d8da;">'
            + ''.join(label(s) for s in ('', '', 'does not see')) + '</div>')
    last = len(ROWS) - 1
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; {cols} gap:24px; align-items:baseline; flex:1; align-content:center; '
        f'padding:17px 20px; {"border-bottom:none;" if k == last else "border-bottom:1px solid #eceff0;"} '
        f'{"border-left:3px solid " + PINK + "; background:rgba(190,30,116,0.04);" if k == last else "border-left:3px solid transparent;"}">'
        f'<span style="{SANS} font-size:20px; font-weight:600; color:{INK};">{tool}</span>'
        f'<span style="{SANS} font-size:20px; font-weight:{600 if k == last else 500}; line-height:1.3; color:{PINK if k == last else INK2};">{q}</span>'
        f'<span style="{SANS} font-size:18px; line-height:1.35; color:{MUTE};">{no}</span></div>'
        for k, (tool, q, no) in enumerate(ROWS))
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:16px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(8)}
  {header('08', 'Who else')}
  <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.04; color:{INK};">Six questions, <span style="color:{GREEN};">six tools.</span></h2>
  <div class="r" style="animation-delay:0.1s; {CARD} padding:18px 4px 6px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{head}{rows}</div>
  {foot_line('use all of them &#183; A3, A7, A23')}
</div>'''
    return BASE_CSS, body, None
