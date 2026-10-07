"""Slide 06: the standard, open at the core. The map sharpens with every lab that joins (results/e13); three layers, one open."""
from parts import *
from slide05 import density_chart


def build():
    e13 = results('e13-baseline-density.json')
    ref = e13['field_reference_by_labs']
    pill = lambda who, what, colour, tag: (f'<div style="flex:1; display:flex; flex-direction:column; gap:5px; min-width:0;">'
                                           f'<span style="display:flex; gap:10px; align-items:baseline;">{label(who, colour)}'
                                           f'<span style="{MONO} font-size:12px; padding:2px 9px; border-radius:999px; border:1px solid {colour}; color:{colour};">{tag}</span></span>'
                                           f'<span style="{SANS} font-size:17px; line-height:1.3; color:{D_TEXT};">{what}</span></div>')
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(6, dark=True)}
  {header('06', 'The standard &#183; open at the core', dark=True)}
  <h2 style="position:absolute; left:56px; top:86px; width:1000px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};">Every lab that joins <span style="color:{D_GREEN};">sharpens the map.</span></h2>
  <div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:166px; width:1168px; height:372px; {CARD_ON_DARK} padding:0 22px; display:flex; align-items:center; overflow:hidden;">{density_chart(e13)}</div>
  <div class="r" style="animation-delay:0.9s; position:absolute; left:56px; top:560px; width:1168px; display:flex; gap:40px; align-items:flex-start; padding-top:14px; border-top:1px solid rgba(246,247,247,.18);">
    {pill('Community', 'map, box, code and public reference', D_GREEN, 'open')}
    {pill('Data access', 'same data, structured and comparable; pre-cleaned on request', D_PINK, 'paid')}
    {pill('The benchmark', 'planted failures; every model graded, segmentation to bioactivity', D_GREEN, 'co-built')}
  </div>
  <div style="position:absolute; left:56px; bottom:44px; width:900px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};"><span style="color:{D_TEXT}; font-weight:500;">Fig. 4</span> Error: distance between two maps built from different labs. {e13["n_plates"]:,} plates, {e13["n_labs"]} labs. JUMP [7]. More: A14</div>
  <div style="position:absolute; right:56px; bottom:44px; {MONO} font-size:13px; color:{D_DIM};">Prices and terms proposed. A15</div>
</div>'''
    return BASE_CSS, body, None
