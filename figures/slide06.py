"""Slide 06, two views. First: data is the new currency, and cell data does not convert between labs: one public price
(figures/worth.py) beside EU-OPENSCREEN's four sites [13]. Then: the map sharpens with every lab that joins (results/e13),
and the route it opens, drawn by parts.path_strip: map, certificate, exchange, and an open end."""
from parts import *
from slide04 import density_chart
from worth import PRICES, SITES


def sites_chart(tall=False, halo='#f6f7f7'):
    """EU-OPENSCREEN as reported: compounds replicate inside a site far more often than they pair across sites.
    tall is the 06a card; halo is the card colour behind the range labels, so gridlines break around them."""
    W, x0, x1 = 600, 150, 560
    H, rows, bh, g1, tick = (236, (56, 136), 28, 176, 202) if tall else (188, (42, 102), 22, 132, 156)
    X = lambda v: x0 + (x1 - x0) * v / 100
    g = []
    for v in (0, 25, 50, 75, 100):
        g.append(f'<path d="M {X(v):.1f} 18 L {X(v):.1f} {g1}" stroke="{GRID}" stroke-width="1.5"/>')
        g.append(text(X(v), tick, f'{v}%', 17, MUTE, 'middle'))
    g.append(text(X(50), H - 6, '% of compounds', 17, INK2, 'middle'))
    for k, (y, name, (lo, hi), fill, ink, verb) in enumerate(((rows[0], 'within a site', SITES['within'], '#c3c9cb', INK2, 'replicate'),
                                                               (rows[1], 'across sites', SITES['across'], PINK, PINK, 'pair'))):
        g.append(text(0, y + 6, name, 19, INK2))
        g.append(f'<rect class="bar" style="animation-delay:{0.5 + 0.3 * k:.1f}s" x="{X(lo):.1f}" y="{y - bh / 2:.0f}" width="{X(hi) - X(lo):.1f}" '
                 f'height="{bh}" rx="{bh / 2:.0f}" fill="{fill}"/>')
        g.append(text(X(lo) - 10, y + 6, f'{lo}&#8211;{hi}% {verb}', 17, ink, 'end', 600,
                      f'stroke="{halo}" stroke-width="6" stroke-linejoin="round" paint-order="stroke"'))
    return svg(W, H, g, aria=f'Within a site {SITES["within"][0]} to {SITES["within"][1]} percent of compounds replicate; across sites '
                            f'{SITES["across"][0]} to {SITES["across"][1]} percent pair.')


def economy():
    """06a: one price on the left, one hero number; the four sites on the right, in one card."""
    big, what, ref = PRICES[1]
    left = (f'<div class="r" style="animation-delay:0.3s; position:absolute; left:56px; top:{FIG_TOP}px; width:480px; height:{FIG_H}px; '
            f'display:flex; flex-direction:column; justify-content:center; gap:12px;">'
            f'<span style="{SANS} font-size:84px; font-weight:700; letter-spacing:-0.045em; line-height:0.92; color:{D_TEXT};">{big}</span>'
            f'<span style="{MONO} font-size:13px; line-height:1.6; color:{D_SOFT};">{what.split(" &#183; ")[0]} <span style="color:{D_DIM};">[{ref}]</span></span></div>')
    n = SITES['n_sites']
    plate = lambda i: (f'<rect x="{32 * i + 0.75}" y="0.75" width="24.5" height="16.5" rx="3" fill="none" stroke="{INK2}" stroke-width="1.5"/>'
                       + ''.join(f'<circle cx="{32 * i + 7 + 6 * c}" cy="{6 + 6 * r}" r="1.6" fill="{INK2}"/>' for r in range(2) for c in range(3)))
    plates = (f'<svg width="{32 * n - 6}" height="18" viewBox="0 0 {32 * n - 6} 18" aria-hidden="true" style="display:block; flex-shrink:0;">'
              + ''.join(plate(i) for i in range(n)) + '</svg>')
    row = f'<div style="display:flex; align-items:center; gap:14px;">{plates}{label(str(n) + " sites &#183; same cells, serum, dyes", INK)}</div>'
    card = (f'<div class="r" style="animation-delay:0.4s; position:absolute; left:576px; top:{FIG_TOP}px; width:648px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:18px 24px 16px; display:flex; flex-direction:column; gap:10px;">{row}'
            f'<div style="flex:1; display:flex; align-items:center;">{sites_chart(tall=True)}</div>'
            f'<span style="{SANS} font-size:19px; font-weight:600; line-height:1.3; color:{PINK};">&#8220;{SITES["quote"].split(" between")[0]}&#8221; '
            f'<span style="{MONO} font-size:13px; font-weight:400; color:{MUTE};">[{SITES["ref"]}]</span></span></div>')
    return left + card


def build():
    e13 = results('e13-baseline-density.json')
    css = BASE_CSS + '''
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1 { opacity: 1; pointer-events: auto; }
    .flow .s .f, .flow .s .r, .flow .s .bar { animation-play-state: paused; }
    .step-0 .s0 .f, .step-1 .s1 .f, .step-0 .s0 .r, .step-1 .s1 .r, .step-0 .s0 .bar, .step-1 .s1 .bar { animation-play-state: running; }
    .flow { cursor: pointer; }
'''
    H = f'position:absolute; left:56px; top:86px; width:1100px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};'
    FOOT = f'position:absolute; left:56px; bottom:44px; width:900px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    fig = lambda n: f'<span style="color:{D_TEXT}; font-weight:500;">fig {n}</span>'
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">The data economy</span>'
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(6, dark=True)}
  {header('06', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">Data is the new currency.<br><span style="color:{D_PINK};">Cell data doesn&#8217;t convert.</span></h2>
  <h2 class="s s1" style="{H}">Every lab that joins <span style="color:{D_GREEN};">sharpens the map.</span></h2>
  <div class="s s0">{economy()}</div>
  <div class="s s1">
    <div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:350px; {CARD_ON_DARK} padding:0 22px; display:flex; align-items:center; overflow:hidden;">{density_chart(e13)}</div>
    <div class="r" style="animation-delay:0.9s; position:absolute; left:56px; top:574px; width:1168px; height:60px; box-sizing:border-box; display:flex; justify-content:space-between; align-items:flex-start; padding-top:14px; border-top:1px solid rgba(246,247,247,.18);">{path_strip(dark=True, tags=False)}</div>
  </div>
  <div class="s s0" style="{FOOT}">{fig(5)} EU-OPENSCREEN &#183; one protocol &#183; {SITES["line"]} &#183; as reported [{SITES["ref"]}] &#183; A23</div>
  <div class="s s1" style="{FOOT}">{fig(6)} two maps, different labs &#183; {e13["n_plates"]:,} plates &#183; JUMP [7]</div>
  {cue(2, dark=True)}
</div>'''
    steps = {'tag': ['The data economy', 'The standard']}
    return css, body, steps
