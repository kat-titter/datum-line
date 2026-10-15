"""Slide 10: what is already in the frame, and the ask. Written whole from results/e9 and e13."""
from parts import *

CELL, GAP, ROW = 14, 3, 21
VALUES = 'open map &#183; signed certificates &#183; shared upside'      # the open-science half: what a contributing lab can count on


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


def route():
    """Where the map goes: three stops and an open end. The first exists today; the rest is direction, not a promise."""
    stop = lambda name, when, colour, filled: (
        f'<div style="display:flex; align-items:center; gap:10px; min-width:0;">'
        f'<span style="width:14px; height:14px; border-radius:50%; flex-shrink:0; box-sizing:border-box; '
        f'{"background:" + colour if filled else "border:2.5px solid " + colour};"></span>'
        f'<span style="display:flex; flex-direction:column; gap:1px;"><span style="{SANS} font-size:18px; font-weight:700; color:{colour if filled else INK};">{name}</span>'
        f'<span style="{MONO} font-size:13px; color:{MUTE};">{when}</span></span></div>')
    arrow = f'<span style="flex:1; height:2px; min-width:24px; background:linear-gradient(90deg,{GREEN},{PINK}); opacity:.5;"></span>'
    return (f'<div style="margin-top:auto; padding-top:14px; border-top:1px solid #e4e8e9; display:flex; align-items:center; gap:12px;">'
            + stop('map', 'today', GREEN, True) + arrow + stop('certificate', 'next', PINK, False) + arrow
            + stop('exchange', 'then', GREEN, False) + arrow + f'<span style="{SANS} font-size:22px; color:{MUTE};">&#8230;</span></div>')


def build():
    replay = results('e9-replay.json')['labs']
    n = sum(v['n_batches'] for v in replay.values())
    n_plates = sum(v['n_plates'] for v in replay.values())
    step = lambda name, what, colour: (f'<div style="display:flex; flex-direction:column; gap:4px; min-width:0;">{label(name, colour)}'
                                       f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK};">{what}</span></div>')
    left = f'''<div class="r" style="{CARD} padding:18px 24px 18px; display:flex; flex-direction:column; gap:12px; animation-delay:0.2s; min-width:0;">
      <div style="display:flex; justify-content:space-between; align-items:baseline; white-space:nowrap;"><span>{label('fig 10', INK)} {label('&#183; already on the map')}</span><span style="{MONO} font-size:13px; color:{MUTE};">{n} batches &#183; {len(replay)} labs &#183; JUMP [7]</span></div>
      {field_grid(replay)}
      <span style="{SANS} font-size:18px; line-height:1.35; color:{INK};"><span style="color:{GREEN}; font-weight:600;">{n_plates:,} plates</span> &#183; next row is yours</span>
      {route()}

    </div>'''
    need = open('figures/assets/slide10-what-i-need.html').read().replace('class="c"', 'class="r"')
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 52px; display:flex; flex-direction:column; gap:20px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(10)}
  {header('10', 'Where this goes, and what I need')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.04; color:{INK}; width:520px; flex-shrink:0;">Every plate you image, <span style="color:{GREEN};">placed on the map.</span></h2>
    <p style="margin:0; {SANS} font-size:18px; line-height:1.4; color:{MUTE}; flex-grow:1;">{VALUES}</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,1.5fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">{left}{need}</div>
</div>'''
    return BASE_CSS, body, None
