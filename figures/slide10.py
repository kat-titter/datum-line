"""Slide 10: what is already on the map, where it goes, and what it needs. Written whole from results/e9; the needs are A21's
plan, read from appendix.PRESEED, so the slide and the board say the same thing."""
from parts import *
from appendix import preseed_total
from slide09 import plan, PARTNERS

BENCHMARK_PARTNERS = plan('travel and partner visits', r'(\d+) benchmark partners')

CELL, GAP, ROW = 16, 3, 27
NUM = ['zero', 'one', 'two', 'three', 'four', 'five', 'six']


def flask(x, y, colour, dashed=False):
    """The deck's lab (ICONS['lab']) at 18px inside an SVG, on stage only: the reader's layer names the lab in words."""
    dash = ' stroke-dasharray="2.6 2.6"' if dashed else ''
    return (f'<g class="talk" transform="translate({x},{y}) scale(0.75)" fill="none" stroke="{colour}" stroke-width="2.3" '
            f'stroke-linecap="round" stroke-linejoin="round"{dash}>{ICONS["lab"]}</g>')


def field_grid(replay):
    """10 since 26 Oct (Kat: "i like the green square look like github frequency. use this in a plot style"): every lab's
    batches as a contribution graph. One row a lab, one square a batch in run order, its shade the plates in it (four levels at
    the quartiles, light to dark), light grey where a lab has no batch yet; the next lab's row open and dashed. The key reads
    Less to More, as on GitHub."""
    labs = sorted(replay, key=lab_number)
    plates = sorted(b['n_plates'] for l in labs for b in replay[l]['batches'])
    cut = [plates[len(plates) * q // 4] for q in (1, 2, 3)]
    shades = ['#a3dcc6', '#6cc3a3', '#0f8f6c', '#0a5c46']
    level = lambda n: sum(n > c for c in cut)
    cols = max(len(replay[l]['batches']) for l in labs)
    # 26 Oct (talk scale): the grid's width sets its scale (about 0.74 of its units on the slide), so 22 px row numbers need 30
    # units; rows sit 38 apart so those numbers clear each other, columns 30 apart so the grid still fits its column
    C, PX, PY, x0 = 22, 30, 38, 60
    S = 760 / (x0 + cols * PX + 8)      # px per unit: the grid fills the left column, 2/3 of the 1152-px row less 8 px
    F, BIG = round(T_TEXT / S, 1), round(T_BIG / S, 1)      # 26 Oct (Kat: "font types are too varied in size")
    g = []
    for r, lab in enumerate(labs):
        y = r * PY
        g.append(text(x0 - 14, y + 20, str(lab_number(lab)), F, PINK if lab == 'source_2' else INK2, 'end', 700 if lab == 'source_2' else 400))      # every lab named (Kat, 26 Oct)
        bs = replay[lab]['batches']
        for k in range(cols):
            fill = shades[level(bs[k]['n_plates'])] if k < len(bs) else '#e4e8e9'
            g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.03 * k:.2f}s" x="{x0 + k * PX}" y="{y}" width="{C}" height="{C}" rx="3" fill="{fill}"/>')
    y = len(labs) * PY + 6
    g.append(text(x0 - 14, y + 22, '+', F, PINK, 'end', 700))      # 26 Oct: the open row is the listener's lab, one lab: pink
    for k in range(cols):
        g.append(f'<rect class="f" style="animation-delay:{1.4 + 0.03 * k:.2f}s" x="{x0 + k * PX + 1}" y="{y + 1}" width="{C - 2}" height="{C - 2}" rx="3" '
                 f'fill="none" stroke="{PINK}" stroke-width="1.6" stroke-dasharray="3 3"/>')
    n = sum(len(replay[l]['batches']) for l in labs)
    ky = y + PY + 64                                             # the key, bottom left, clear of the open row's +
    key = (text(0, ky, f'{n}', BIG, INK, weight=700, extra='letter-spacing="-1.2"') + text(122, ky - 4, 'batches today; the open row, yours', F, INK2)
           + text(0, ky + 52, 'Less', F, INK2) + ''.join(f'<rect x="{82 + q * PX}" y="{ky + 30}" width="{C}" height="{C}" rx="3" fill="{c}"/>' for q, c in enumerate(['#e4e8e9'] + shades))
           + text(82 + 5 * PX + 8, ky + 52, 'More plates', F, INK2))
    W, H = x0 + cols * PX, ky + 62
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -8 {W + 8} {H + 8}" width="100%" role="img" '
            f'aria-label="Every batch of every lab in run order, one square each, shaded by plates, {n} today, with an open row for the next lab." style="display:block; max-height:100%;">' + ''.join(g) + key + '</svg>')

def needs():
    """The round first, stated plainly; then what else it needs, leader first; then the ask to the room."""
    total = preseed_total()[1]
    items = sorted([(1, 'leader', ', to run it', 'person'),                  # A21's lines: leader; partner-lab bench time; benchmark partners
                    (PARTNERS, 'partner labs', ', bench time', 'lab'),
                    (BENCHMARK_PARTNERS, 'benchmark partners', '', 'flag')], key=lambda i: i[0])      # 1, 2, 3 (Kat, 26 Oct)
    soft = lambda t: pdf(f'<span style="font-weight:400; color:{MUTE};">{t}</span>') if t else ''
    row = lambda n, name, more, ic: (
        f'<div style="display:grid; grid-template-columns:30px 30px 1fr; align-items:center; gap:10px;">{icon(ic, INK2, 24)}'
        f'<span style="{SANS} font-size:{T_SUB}px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{INK};">{n}</span>'
        f'<span style="{SANS} font-size:22px; line-height:1.2; color:{INK};">{name}{soft(more)}</span></div>')
    return (f'<div class="r" style="padding:4px 0 0 28px; border-left:2px solid #e4e8e9; display:flex; flex-direction:column; gap:12px; animation-delay:0.35s; min-width:0;">'      # 26 Oct: no card box
            f'<span style="{SANS} font-size:{T_HERO}px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{INK};">${total / 1000:.1f}M</span>'
            f'<span style="{SANS} font-size:{T_TEXT}px; line-height:1.3; color:{INK};">pre-seed for 18 months:<br>first members, then the seed{pdf(", A21")}</span>'
            f'<div style="display:flex; flex-direction:column; justify-content:space-around; flex-grow:1; padding:8px 0 10px; border-top:1px solid #e4e8e9;">'
            f'<span style="{MONO} font-size:22px; letter-spacing:0.08em; text-transform:uppercase; color:{INK2};">looking for</span>'
            + ''.join(row(*i) for i in items) + '</div>'
            f'<div style="height:80px; box-sizing:border-box; padding-top:14px; border-top:1px solid #e4e8e9; {SANS} font-size:{T_SUB}px; font-weight:600; '
            f'letter-spacing:-0.015em; line-height:1.2; color:{INK};">Have control images?<br>Talk to me.</div></div>')


def build():
    """26 Oct (Kat: "more passion/joy"; the joy draft, approved): 01's wall again, the listener's tile lit, and the ask under it,
    with the link. The batch grid and the needs card (field_grid, needs, build_grid) stay one round in case they are missed."""
    total = preseed_total()[1]
    words = ['zero', 'one', 'two', 'three', 'four', 'five']
    small = f'{SANS} font-size:22px; line-height:1.35; color:{D_SOFT};'
    css = BASE_CSS + WALL_CSS
    body = f'''<div style="position:relative; overflow:hidden; width:1280px; height:720px; background:{INK};">
  {wall(lit=True)}
  <div class="band" style="padding-bottom:64px;">
    <h2 style="margin:0; {SANS} font-size:72px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{D_TEXT};">There&#8217;s a tile for your lab.<br><span style="color:{D_GREEN};">Let&#8217;s map &#8220;normal&#8221; together.</span></h2>
    <div style="display:grid; grid-template-columns:auto 1fr auto; gap:48px; align-items:end; margin-top:28px;">
      <div><div style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{D_TEXT};">${total / 1000:.1f}M</div><div style="{small}">pre-seed for 18 months{pdf(", A21")}</div></div>
      <div style="{small}">looking for a leader, {words[PARTNERS]} partner labs<br>and {words[BENCHMARK_PARTNERS]} benchmark partners</div>
      <div style="text-align:right;"><div style="{SANS} font-size:28px; font-weight:600; line-height:1.2; color:{D_PINK};">Have control images? Talk to me.</div>
        <div style="{MONO} font-size:22px; color:{D_SOFT}; margin-top:6px;">kat-titter.github.io/datum-line</div></div>
    </div>
  </div>
  <a class="code" href="https://github.com/kat-titter/datum-line" target="_blank" rel="noopener" style="position:absolute; right:330px; bottom:15px; z-index:7; {MONO} font-size:22px; color:{D_SOFT}; text-decoration:none;">open code {arrow()}</a>
  {dots(10, dark=True)}
</div>'''
    return css, body, None


def build_grid():
    replay = results('e9-replay.json')['labs']
    n_plates = sum(v['n_plates'] for v in replay.values())
    per = sorted(b['n_plates'] for v in replay.values() for b in v['batches'])
    med, lo, hi = per[len(per) // 2], per[0], per[-1]          # 129 batches: the middle one is the median
    left = f'''<div class="r" style="padding:6px 8px 0 0; display:flex; flex-direction:column; gap:12px; animation-delay:0.2s; min-width:0;">
      <div style="flex-grow:1; display:flex; align-items:center;">{field_grid(replay)}</div>
    </div>'''
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(10)}
  {header('10', 'The vision')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:620px; flex-shrink:0;">Every plate imaged,<br><span style="color:{GREEN};">placed on the map.</span></h2>
    <p class="pdfv" style="margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE};">Labs share control images, free.<br>Each sees its &#8220;normal&#8221; next to everyone else&#8217;s.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">{left}{needs()}</div>
  <a class="code" href="https://github.com/kat-titter/datum-line" target="_blank" rel="noopener" style="position:absolute; right:330px; bottom:15px; z-index:7; {MONO} font-size:22px; color:{INK2}; text-decoration:none;">open code {arrow()}</a>      <!-- 26 Oct (Kat: "ready for desci community"): MIT, public -->
  {foot_line(stage='', html=f'<span style="color:{INK}; font-weight:500;">fig 7</span> one square: one batch, in run order, shaded by plates at the quartiles; a median of {med} plates ({lo} to {hi}); {n_plates:,} plates, JUMP [7], results/e9; A15, A20, A22, A24')}
</div>'''
    return BASE_CSS, body, None
