"""Slide 06, two views. First: data is the new currency, and cell data does not convert between labs (public figures
in figures/worth.py, EU-OPENSCREEN [13]). Then: the map sharpens with every lab that joins (results/e13), and the path
it opens: map, certificate, exchange, and an arrow left open."""
from parts import *
from slide05 import density_chart
from worth import PRICES, SITES

ICON = lambda d, colour: f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="{colour}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink:0;">{d}</svg>'
PATH = [('Map', 'open', 'today', D_GREEN, '<path d="M12 21s-6-5.5-6-10a6 6 0 0 1 12 0c0 4.5-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/>'),
        ('Certificate', 'paid', 'next', D_PINK, '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>'),
        ('Exchange', 'a share of each trade', 'then', D_GREEN, '<path d="M4 8h15l-3.5-3.5M20 16H5l3.5 3.5"/>')]


def sites_chart():
    """EU-OPENSCREEN as reported: compounds replicate inside a site far more often than they pair across sites."""
    W, H, x0, x1 = 600, 176, 150, 560
    X = lambda v: x0 + (x1 - x0) * v / 100
    g = []
    for v in (0, 25, 50, 75, 100):
        g.append(f'<path d="M {X(v):.1f} 18 L {X(v):.1f} 132" stroke="{GRID}" stroke-width="1.5"/>')
        g.append(text(X(v), 156, f'{v}%', 17, MUTE, 'middle'))
    for y, name, (lo, hi), colour, verb in ((42, 'within a site', SITES['within'], GREEN, 'replicate'),
                                            (102, 'across sites', SITES['across'], PINK, 'pair')):
        g.append(text(0, y + 6, name, 19, INK2))
        g.append(f'<rect class="bar" style="animation-delay:{0.5 if colour == GREEN else 0.8}s" x="{X(lo):.1f}" y="{y - 11}" width="{X(hi) - X(lo):.1f}" height="22" rx="11" fill="{colour}"/>')
        g.append(text(X(lo) - 10, y + 6, f'{lo}&#8211;{hi}% {verb}', 17, colour, 'end', 600))
    return svg(W, H, g, aria=f'Within a site {SITES["within"][0]} to {SITES["within"][1]} percent of compounds replicate; across sites '
                            f'{SITES["across"][0]} to {SITES["across"][1]} percent pair.')


def economy():
    prices = ''.join(
        f'<div class="r" style="animation-delay:{0.3 + 0.25 * k:.2f}s; display:flex; flex-direction:column; gap:4px; padding:14px 0; '
        f'{"border-top:1px solid rgba(246,247,247,.16);" if k else ""}">'
        f'<span style="{SANS} font-size:46px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{D_TEXT};">{big}</span>'
        f'<span style="{SANS} font-size:17px; line-height:1.3; color:{D_SOFT};">{what} <span style="{MONO} font-size:13px; color:{D_DIM};">[{ref}]</span></span></div>'
        for k, (big, what, ref) in enumerate(PRICES))
    left = f'<div style="position:absolute; left:56px; top:196px; width:480px; display:flex; flex-direction:column;">{prices}</div>'
    card = (f'<div class="r" style="animation-delay:0.4s; position:absolute; left:576px; top:204px; width:648px; height:340px; {CARD_ON_DARK} '
            f'padding:18px 24px 16px; display:flex; flex-direction:column; gap:10px;">'
            f'<div style="display:flex; justify-content:space-between; align-items:baseline;">{label("same protocol &#183; " + str(SITES["n_sites"]) + " sites", INK)}'
            f'{label(SITES["line"])}</div>'
            f'<span style="{SANS} font-size:18px; line-height:1.3; color:{INK2};">same {SITES["supplied"]}, shipped to every site</span>'
            f'{sites_chart()}'
            f'<span style="margin-top:auto; {SANS} font-size:19px; font-weight:600; line-height:1.3; color:{PINK};">&#8220;{SITES["quote"]}&#8221; '
            f'<span style="{MONO} font-size:13px; font-weight:400; color:{MUTE};">[{SITES["ref"]}]</span></span></div>')
    return left + card


def path():
    step = lambda name, tag, when, colour, icon: (
        f'<div style="display:flex; flex-direction:column; gap:6px; min-width:0;">'
        f'<span style="display:flex; gap:10px; align-items:center;">{ICON(icon, colour)}{label(name, colour)}'
        f'<span style="{MONO} font-size:12px; padding:2px 9px; border-radius:999px; border:1px solid {colour}; color:{colour};">{tag}</span></span>'
        f'<span style="{MONO} font-size:13px; color:{D_DIM}; padding-left:32px;">{when}</span></div>')
    arrow = f'<span style="{SANS} font-size:22px; color:{D_DIM}; padding-top:0;">&#8594;</span>'
    return arrow.join(step(*p) for p in PATH) + f'{arrow}<span style="{SANS} font-size:22px; color:{D_DIM};">&#8230;</span>'


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
    <div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:166px; width:1168px; height:372px; {CARD_ON_DARK} padding:0 22px; display:flex; align-items:center; overflow:hidden;">{density_chart(e13)}</div>
    <div class="r" style="animation-delay:0.9s; position:absolute; left:56px; top:560px; width:1168px; display:flex; gap:28px; align-items:flex-start; padding-top:14px; border-top:1px solid rgba(246,247,247,.18);">{path()}</div>
  </div>
  <div class="s s0" style="{FOOT}">{fig(4)} EU-OPENSCREEN &#183; {SITES["line"]} &#183; one protocol, {SITES["n_sites"]} sites &#183; as reported [{SITES["ref"]}] &#183; A23</div>
  <div class="s s1" style="{FOOT}">{fig(5)} two maps, different labs &#183; {e13["n_plates"]:,} plates &#183; JUMP [7] &#183; A14</div>
  <div style="position:absolute; right:56px; bottom:44px; {MONO} font-size:13px; color:{D_DIM};"><span data-h="hint">click &#8594; why it compounds</span></div>
</div>'''
    steps = {'tag': ['The data economy', 'The standard · open at the core'],
             'hint': ['click → why it compounds', 'click → start over']}
    return css, body, steps
