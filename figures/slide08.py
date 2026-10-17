"""Slide 08: who else answers a question about your cells. Six tools, six questions, each with what it does not see.

Written whole. Datum Line is one row among six, with its own gap stated, so the slide reads as a landscape and not a scorecard.
Each gap names the board that backs it; the collaborative line (use all of them) is the headline, not a footnote.
"""
from parts import *

ROWS = [
    ('DNA fingerprint (STR)', 'Is it the line the label says?', 'how the cells behave'),
    ('vendor certificate', 'Was it fine when it shipped?', 'anything after shipping'),
    ('plate controls', 'Did this plate work?', 'a whole lab drifting'),
    ('in-house platforms', 'Is my own data consistent?', 'lab differences, removed on purpose'),
    ('data factories', 'Where do I get cell data at scale?', 'other labs&#8217; &#8220;normal&#8221;'),
    ('Datum Line', 'Do my cells look &#8220;normal&#8221;, next to other labs?', 'which cell line it is; unstained images, not yet'),
]
BACKED = {'DNA fingerprint (STR)': 'A7', 'plate controls': 'A1', 'in-house platforms': 'A3', 'data factories': 'A23', 'Datum Line': 'A7, A10'}   # the board behind each gap


def build():
    cols = 'grid-template-columns:236px 1.3fr 1fr;'
    head = (f'<div style="display:grid; {cols} gap:24px; padding:0 20px 10px; border-left:3px solid transparent; border-bottom:1px solid {GRID};">'
            + ''.join(f'<span style="{SANS} font-size:16px; color:{MUTE};">{s}</span>' for s in ('tool', 'answers', 'does not see')) + '</div>')
    last = len(ROWS) - 1
    ref = lambda tool: (f' <span class="pdf" style="{MONO} font-size:13px; color:{MUTE}; white-space:nowrap;">{BACKED[tool]}</span>' if tool in BACKED else '')
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; {cols} gap:24px; align-items:baseline; flex:1; align-content:center; '
        f'padding:12px 20px; {"border-bottom:none;" if k == last else "border-bottom:1px solid #eceff0;"} '
        f'{"border-left:3px solid " + GREEN + "; background:rgba(15,143,108,0.05);" if k == last else "border-left:3px solid transparent;"}">'
        f'<span style="{SANS} font-size:20px; font-weight:600; color:{INK};">{tool}</span>'
        f'<span style="{SANS} font-size:20px; font-weight:{600 if k == last else 500}; line-height:1.3; color:{GREEN if k == last else INK2};">{q}</span>'
        f'<span style="{SANS} font-size:18px; line-height:1.35; color:{MUTE};">{no}{ref(tool)}</span></div>'
        for k, (tool, q, no) in enumerate(ROWS))
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(8)}
  {header('08', 'Who else')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:620px; flex-shrink:0;">Six questions, six tools.<br>Use all of them.</h2>
    {pdf(f'<p style="margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE};">Each answers one question well.<br>Each misses something, Datum Line too.</p>')}
  </div>
  <div class="r" style="animation-delay:0.1s; {CARD} padding:16px 4px 6px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{head}{rows}</div>
  {foot_line('STR: ATCC [14]')}
</div>'''
    return BASE_CSS, body, None
