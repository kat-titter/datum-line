"""Slide 08: who else answers a question about your cells. Five tools, five questions, each with what it does and does not do.

Written whole. Datum Line is one row among five, with its own gap stated, so the slide reads as a landscape and not a scorecard.
"""
from parts import *

ROWS = [
    ('STR authentication', 'Is it the line the label says?', 'nothing about behaviour'),
    ('vendor certificate', 'Was it fine when it shipped?', 'nothing after shipping'),
    ('plate controls', 'Did this plate work?', 'cannot see a whole lab drift'),
    ('phenomics platforms', 'Is my own data consistent?', 'removes lab differences by design'),
    ('Datum Line', 'Where do my cells sit, against every other lab?', 'cannot say which line; fluorescence today'),
]


def build():
    head = (f'<div style="display:grid; grid-template-columns:260px 1fr 1fr; gap:24px; padding:0 20px 10px; border-bottom:1px solid #d3d8da;">'
            + ''.join(label(s) for s in ('tool', 'the question it answers', 'what it does not do')) + '</div>')
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; grid-template-columns:260px 1fr 1fr; gap:24px; align-items:baseline; '
        f'padding:22px 20px; border-bottom:1px solid #eceff0; {"border-left:3px solid " + PINK + "; background:rgba(190,30,116,0.04);" if k == len(ROWS) - 1 else "border-left:3px solid transparent;"}">'
        f'<span style="{SANS} font-size:20px; font-weight:600; color:{INK};">{tool}</span>'
        f'<span style="{SANS} font-size:19px; font-weight:600; line-height:1.3; color:{PINK if k == len(ROWS) - 1 else GREEN};">{q}</span>'
        f'<span style="{SANS} font-size:17px; line-height:1.35; color:{MUTE};">{no}</span></div>'
        for k, (tool, q, no) in enumerate(ROWS))
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 52px; display:flex; flex-direction:column; gap:18px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(8)}
  {header('08', 'Who else')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.04; color:{INK}; width:560px; flex-shrink:0;">Five questions, <span style="color:{PINK};">five tools.</span></h2>
    <p style="margin:0; {SANS} font-size:18px; line-height:1.4; color:{MUTE}; flex-grow:1;">Use all of them.<br>One did not exist.</p>
  </div>
  <div class="r" style="animation-delay:0.1s; {CARD} padding:18px 4px 6px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{head}{rows}</div>
  <div style="{MONO} font-size:13px; color:{MUTE};">A7, A3</div>
</div>'''
    return BASE_CSS, body, None
