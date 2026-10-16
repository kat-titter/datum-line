"""Slide 10: what is already on the map, where it goes, and what it needs. Written whole from results/e9; the needs are A21's
plan, read from appendix.PRESEED, so the slide and the board say the same thing."""
from parts import *
from appendix import preseed_total
from slide09 import plan, PARTNERS

BENCHMARK_PARTNERS = plan('travel and partner visits', r'(\d+) benchmark partners')

CELL, GAP, ROW = 16, 3, 27


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
    y = len(labs) * ROW + 6
    g.append(f'<text x="{x0 - 12}" y="{y + 12}" {mono} fill="{PINK}" text-anchor="end" font-weight="600">you</text>')
    for k in range(6):
        g.append(f'<rect class="f" style="animation-delay:{1.2 + 0.08 * k:.2f}s" x="{x0 + k * (CELL + GAP) + 1}" y="{y + 1}" width="{CELL - 2}" height="{CELL - 2}" rx="3" '
                 f'fill="none" stroke="{PINK}" stroke-width="1.6" stroke-dasharray="3 3"/>')
    widest = max(len(replay[l]['batches']) for l in labs)
    W, H = x0 + widest * (CELL + GAP), y + CELL + 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Every batch of every lab in run order, one square each, with an open row for the next lab." style="display:block;">' + ''.join(g) + '</svg>')


ICON = {'leader': '<circle cx="9" cy="8" r="3"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 14.2A4.5 4.5 0 0 1 21 18.5"/>',
        'bench': '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M7.5 15h9"/>',
        'funding': '<circle cx="12" cy="12" r="8.5"/><path d="M14.5 9.2c-.6-.8-1.5-1.2-2.5-1.2-1.4 0-2.5.8-2.5 1.9 0 2.6 5.2 1.3 5.2 4.1 0 1.1-1.1 2-2.7 2-1.1 0-2.1-.5-2.7-1.3M12 6.5v1.5M12 16v1.5"/>',
        'partners': '<path d="M4 17.5l4-4 3 3 5-6 4 4M4 6.5h16M4 11h5"/>'}


def needs():
    """What it needs, leader first, each with the one fact from the plan that makes it specific; then the ask."""
    total = preseed_total()[1]
    items = [('leader', 'to run it'),
             ('bench', f'{PARTNERS} partner labs'),
             ('funding', f'${total / 1000:.1f}M &#183; 18 months &#183; A21'),
             ('partners', f'{BENCHMARK_PARTNERS} for the benchmark')]
    row = lambda name, fact: (
        f'<div style="display:grid; grid-template-columns:40px 1fr; column-gap:14px; align-items:center;">'
        f'<svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="{INK2}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="display:block;">{ICON[name]}</svg>'
        f'<span style="display:flex; flex-direction:column; gap:2px;"><span style="{SANS} font-size:19px; font-weight:600; line-height:1.2; color:{INK};">{name}</span>'
        f'<span style="{MONO} font-size:13px; line-height:1.3; color:{MUTE};">{fact}</span></span></div>')
    return (f'<div class="r" style="{CARD} padding:18px 24px; display:flex; flex-direction:column; gap:12px; animation-delay:0.35s; min-width:0;">'
            f'{label("what it needs")}<div style="display:flex; flex-direction:column; justify-content:space-around; flex-grow:1; padding:4px 0 10px;">'
            + ''.join(row(*i) for i in items) + '</div>'
            f'<div style="height:80px; box-sizing:border-box; padding-top:14px; border-top:1px solid #e4e8e9; {SANS} font-size:26px; font-weight:600; '
            f'letter-spacing:-0.015em; line-height:1.2; color:{PINK};">Have control images?<br>Talk to me.</div></div>')


def build():
    replay = results('e9-replay.json')['labs']
    n_plates = sum(v['n_plates'] for v in replay.values())
    left = f'''<div class="r" style="{CARD} padding:18px 24px 18px; display:flex; flex-direction:column; gap:12px; animation-delay:0.2s; min-width:0;">
      {field_grid(replay)}
      <div style="margin-top:auto; height:80px; box-sizing:border-box; padding-top:14px; border-top:1px solid #e4e8e9; display:flex; justify-content:space-between; align-items:flex-start;">{path_strip(dark=False, tags=False, later=False)}</div>
    </div>'''
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(10)}
  {header('10', 'Where this goes')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:620px; flex-shrink:0;">Every plate you image,<br><span style="color:{GREEN};">placed on the map.</span></h2>
    <p style="margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE};">Labs share control images, free.<br>Each sees its &#8220;normal&#8221; next to everyone else&#8217;s.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">{left}{needs()}</div>
  {foot_line(f'<span style="color:{INK}; font-weight:500;">fig 10</span> 1 square = 1 batch &#183; {n_plates:,} plates &#183; JUMP [7] &#183; A15, A24')}
</div>'''
    return BASE_CSS, body, None
