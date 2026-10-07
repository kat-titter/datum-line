"""Slide 10: what is already in the frame, and the ask. Written whole from results/e9 and e13."""
from parts import *

CELL, GAP, ROW = 14, 3, 21


def field_grid(replay):
    """Every batch of every lab as one square, a shade of green per lab, and an open row for the next lab."""
    labs = sorted(replay, key=lab_number)
    shade = dict(zip(labs, greens(len(labs))))
    x0 = 66
    mono = 'font-family="IBM Plex Mono, Menlo, monospace" font-size="13"'
    g = []
    for r, lab in enumerate(labs):
        y = r * ROW
        g.append(f'<text x="{x0 - 12}" y="{y + 12}" {mono} fill="{MUTE}" text-anchor="end">{lab_name(lab)}</text>')
        for k, b in enumerate(replay[lab]['batches']):
            g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.012 * (r * 6 + k):.2f}s" x="{x0 + k * (CELL + GAP)}" y="{y}" '
                     f'width="{CELL}" height="{CELL}" rx="3.5" fill="{shade[lab]}"/>')
    y = len(labs) * ROW + 4
    g.append(f'<text x="{x0 - 12}" y="{y + 12}" {mono} fill="{PINK}" text-anchor="end" font-weight="600">you</text>')
    for k in range(6):
        g.append(f'<rect class="f" style="animation-delay:{1.2 + 0.08 * k:.2f}s" x="{x0 + k * (CELL + GAP) + 1}" y="{y + 1}" width="{CELL - 2}" height="{CELL - 2}" rx="3" '
                 f'fill="none" stroke="{PINK}" stroke-width="1.6" stroke-dasharray="3 3"/>')
    widest = max(len(replay[l]['batches']) for l in labs)
    W, H = x0 + widest * (CELL + GAP), y + CELL + 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Every batch of every lab in run order, one square each, with an open row for the next lab." style="display:block;">' + ''.join(g) + '</svg>')


def build():
    replay = results('e9-replay.json')['labs']
    n = sum(v['n_batches'] for v in replay.values())
    n_plates = sum(v['n_plates'] for v in replay.values())
    step = lambda name, what, colour: (f'<div style="display:flex; flex-direction:column; gap:4px; min-width:0;">{label(name, colour)}'
                                       f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK};">{what}</span></div>')
    left = f'''<div class="r" style="{CARD} padding:18px 24px 18px; display:flex; flex-direction:column; gap:12px; animation-delay:0.2s; min-width:0;">
      <div style="display:flex; justify-content:space-between; align-items:baseline; white-space:nowrap;"><span>{label('Fig. 7', INK)} {label('&#183; Already on the map')}</span><span style="{MONO} font-size:13px; color:{MUTE};">{n} batches &#183; {len(replay)} labs &#183; JUMP [7]</span></div>
      {field_grid(replay)}
      <span style="{SANS} font-size:18px; line-height:1.35; color:{INK};"><span style="color:{GREEN}; font-weight:600;">{n_plates:,} plates, one map.</span> Next row is yours.</span>
      <div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px; margin-top:auto; padding-top:14px; border-top:1px solid #e4e8e9;">
        {step('Now', 'U2OS, fluorescence', GREEN)}{step('Next', 'more lines; brightfield, already at 99.6% on one image', GREEN)}{step('Then', 'the map a field shares', PINK)}
      </div>
    </div>'''
    need = open('figures/assets/slide10-what-i-need.html').read().replace('class="c"', 'class="r"')
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 52px; display:flex; flex-direction:column; gap:20px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(10)}
  {header('10', 'Where this goes, and what I need')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.04; color:{INK}; width:520px; flex-shrink:0;">Every plate you image, <span style="color:{GREEN};">placed on the map.</span></h2>
    <p style="margin:0; {SANS} font-size:18px; line-height:1.4; color:{MUTE}; flex-grow:1;">One map for people and for agents, held by nobody who sells you cells.<br>Everyone learns and grows together.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,1.5fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">{left}{need}</div>
</div>'''
    return BASE_CSS, body, None
