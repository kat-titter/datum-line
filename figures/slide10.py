"""Slide 10: what is already on the map, where it goes, and what it needs. Written whole from results/e9; the needs are A21's
plan, read from appendix.PRESEED, so the slide and the board say the same thing."""
from parts import *
from appendix import preseed_total
from slide09 import plan, PARTNERS

BENCHMARK_PARTNERS = plan('travel and partner visits', r'(\d+) benchmark partners')

CELL, GAP, ROW = 16, 3, 27
NUM = ['zero', 'one', 'two', 'three', 'four', 'five', 'six']


def field_grid(replay):
    """Every batch of every lab as one square, a shade of green per lab, and an open row for the next lab."""
    labs = sorted(replay, key=lab_number)
    shade = dict(zip(labs, greens(len(labs))))
    x0 = 66
    mono = 'font-family="IBM Plex Mono, Menlo, monospace" font-size="15"'
    g = []
    for r, lab in enumerate(labs):
        y = r * ROW
        g.append(f'<text class="pdf" x="{x0 - 12}" y="{y + 12}" {mono} fill="{MUTE}" text-anchor="end">{lab_name(lab)}</text>')
        for k, b in enumerate(replay[lab]['batches']):
            g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.012 * (r * 6 + k):.2f}s" x="{x0 + k * (CELL + GAP)}" y="{y}" '
                     f'width="{CELL}" height="{CELL}" rx="3.5" fill="{shade[lab]}"/>')
    y = len(labs) * ROW + 6
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
    """The round first, stated plainly; then what else it needs, leader first; then the ask to the room."""
    total = preseed_total()[1]
    items = [('leader', 'to run it', 'person'),
             ('bench time', f'{NUM[PARTNERS]} labs', 'lab'),
             ('benchmark', f'{NUM[BENCHMARK_PARTNERS]} partners', 'flag')]
    row = lambda name, fact, ic: (
        f'<div style="display:grid; grid-template-columns:30px 1fr; align-items:center; gap:10px;">{icon(ic, INK2, 24)}'
        f'<span style="display:flex; flex-direction:column; gap:2px;"><span style="{SANS} font-size:19px; font-weight:600; line-height:1.2; color:{INK};">{name}</span>'
        f'<span style="{SANS} font-size:16px; line-height:1.3; color:{MUTE};">{fact}</span></span></div>')
    return (f'<div class="r" style="{CARD} padding:18px 24px; display:flex; flex-direction:column; gap:12px; animation-delay:0.35s; min-width:0;">'
            f'<span style="{SANS} font-size:56px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{INK};">${total / 1000:.1f}M</span>'
            f'<span style="{SANS} font-size:18px; color:{INK2};">pre-seed{pdf(" &#183; eighteen months &#183; A21")}</span>'
            f'<div style="display:flex; flex-direction:column; justify-content:space-around; flex-grow:1; padding:8px 0 10px; border-top:1px solid #e4e8e9;">'
            + ''.join(row(*i) for i in items) + '</div>'
            f'<div style="height:80px; box-sizing:border-box; padding-top:14px; border-top:1px solid #e4e8e9; {SANS} font-size:26px; font-weight:600; '
            f'letter-spacing:-0.015em; line-height:1.2; color:{PINK};">Have control images?<br>Talk to me.</div></div>')


def build():
    replay = results('e9-replay.json')['labs']
    n_plates = sum(v['n_plates'] for v in replay.values())
    left = f'''<div class="r" style="{CARD} padding:18px 24px 18px; display:flex; flex-direction:column; gap:12px; animation-delay:0.2s; min-width:0;">
      <div style="flex-grow:1; display:flex; align-items:center;">{field_grid(replay)}</div>
    </div>'''
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(10)}
  {header('10', 'Where this goes')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:620px; flex-shrink:0;">Every plate imaged,<br><span style="color:{GREEN};">placed on the map.</span></h2>
    <p class="pdfv" style="margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE};">Labs share control images, free.<br>Each sees its &#8220;normal&#8221; next to everyone else&#8217;s.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">{left}{needs()}</div>
  {foot_line(f'<span style="color:{INK}; font-weight:500;">fig 10</span> 1 square = 1 batch &#183; {n_plates:,} plates &#183; JUMP [7] &#183; A15, A20, A22, A24')}
</div>'''
    return BASE_CSS, body, None
