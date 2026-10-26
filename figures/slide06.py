"""Slides 06 and 07 since 26 Oct 2026 (one slide of two views before): the network effect, then the market. First: data is the new currency, and cell data does not convert between labs: one public price
(figures/worth.py) beside EU-OPENSCREEN's four sites [13]. Then: the map sharpens with every lab that joins (results/e13),
and the route it opens, drawn by parts.path_strip: map, certificate, subscriptions, and an open end."""
from parts import *
from slide04 import density_chart, NUMBERS
from worth import PRICES, SITES


def sites_chart(tall=False, halo='#f6f7f7'):
    """EU-OPENSCREEN as reported: compounds replicate inside a site far more often than they pair across sites.
    tall is the 06a card; halo is the card colour behind the range labels, so gridlines break around them."""
    W, x0, x1 = 600, 170, 560
    H, rows, bh, g1, tick = (236, (56, 136), 28, 176, 202) if tall else (188, (42, 102), 22, 132, 156)
    X = lambda v: x0 + (x1 - x0) * v / 100
    g = []
    for v in (0, 50, 100):
        g.append(f'<path d="M {X(v):.1f} 18 L {X(v):.1f} {g1}" stroke="{GRID}" stroke-width="1.5"/>')
        g.append(text(X(v), tick, f'{v}%', 17, MUTE, 'middle'))
    g.append(text(X(50), H - 6, '% of compounds', 17, INK2, 'middle'))
    flask = lambda x, y: (f'<g transform="translate({x},{y - 13})" fill="none" stroke="{INK2}" stroke-width="1.7" stroke-linecap="round" '
                          f'stroke-linejoin="round" aria-hidden="true">{ICONS["lab"]}</g>')
    for k, (y, name, (lo, hi), fill, ink, verb, n) in enumerate(((rows[0], 'same lab', SITES['within'], '#c3c9cb', INK2, 'replicate', 1),
                                                                  (rows[1], 'other labs', SITES['across'], INK2, INK2, 'agree', 2))):
        g += [flask(28 * (2 - n + i), y) for i in range(n)]                    # one flask, then two: the same picture as 05b's rows
        g.append(text(62, y + 6, name, 19, INK2))
        g.append(f'<rect class="bar" style="animation-delay:{0.5 + 0.3 * k:.1f}s" x="{X(lo):.1f}" y="{y - bh / 2:.0f}" width="{X(hi) - X(lo):.1f}" '
                 f'height="{bh}" rx="{bh / 2:.0f}" fill="{fill}"/>')
        g.append(text(X(lo) - 10, y + 6, f'{lo}&#8211;{hi}% {verb}', 17, ink, 'end', 600,
                      f'stroke="{halo}" stroke-width="6" stroke-linejoin="round" paint-order="stroke"'))
    return svg(W, H, g, aria=f'Inside one lab {SITES["within"][0]} to {SITES["within"][1]} percent of compounds replicate; between labs '
                            f'{SITES["across"][0]} to {SITES["across"][1]} percent agree.')


# why now, in three short lines; each one is a board or a numbered reference in the PDF
WHY_NOW = (f'<div style="display:flex; flex-direction:column; gap:8px;">'
           f'<span style="{SANS} font-size:18px; font-weight:700; color:{D_TEXT};">Why now</span>'
           + ''.join(f'<div class="r" style="animation-delay:{0.9 + 0.18 * k:.2f}s; display:grid; grid-template-columns:24px 50px minmax(0,1fr); align-items:center; gap:12px; padding:9px 14px; '
                     f'border-radius:10px; background:rgba(246,247,247,.06);">{icon(ico, D_SOFT, 24)}'
                     f'<span style="{MONO} font-size:18px; color:{D_SOFT};">{when}</span>'
                     f'<span style="{SANS} font-size:18px; line-height:1.25; color:{D_TEXT};">{what}{pdf(src)}</span></div>'
                     for k, (ico, when, what, src) in enumerate((('map', '2023', '1.8 billion cells, public (JUMP)', ' [7, 25]'),
                                                  ('animal', '2025', 'FDA moves off animal tests', ' [9]'),
                                                  ('certificate', '2025', 'Roche paid $30M for one cell map', ', Recursion Q3 2025 results [11]'),
                                                  ('ai-reads', 'now', 'AI reads cell images', ', A10'))))
           + pdf(f'<span style="{MONO} font-size:12px; line-height:1.45; color:{D_DIM};">JUMP went public from 2023 [7] and counts 1,810,840,525 cells today; source_15 is not counted, '
                 f'so these are not this map&#8217;s eleven labs [25]</span>')
           + '</div>')


QREF = '<span style="{MONO} font-size:13px; font-weight:400; color:{MUTE};"> [{ref}]</span>'


def economy():
    """06a: the four sites in the figure card on the left; one price, the hero number, on the dark side to the right."""
    big, what, ref = PRICES[1]
    n = SITES['n_sites']
    chip = lambda ico, word: f'<span style="display:flex; align-items:center; gap:6px;">{icon(ico, INK2, 24)}{word}</span>'
    labs = f'<span style="display:flex; gap:2px;">{"".join(icon("lab", INK2, 24) for _ in range(n))}</span>'      # four labs, one flask each
    row = (f'<div style="display:flex; align-items:center; gap:18px; {SANS} font-size:18px; color:{INK};">{labs}<span>Same</span>'
           + ''.join(chip(i, w) for i, w in (('cells', 'cells'), ('serum', 'serum'), ('dyes', 'dyes'), ('protocol', 'protocol')))
           + pdf(f'<span style="color:{INK2};">supplied centrally [{SITES["ref"]}]</span>') + '</div>')
    card = (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:18px 24px 16px; display:flex; flex-direction:column; gap:10px;">{row}'
            f'<div style="flex:1; display:flex; align-items:center;">{sites_chart(tall=True)}</div>'
            f'<div style="display:flex; flex-direction:column; gap:3px;">'
            f'<span style="{SANS} font-size:20px; font-weight:600; line-height:1.3; color:{INK};">&#8220;{SITES["quote"]}&#8221;</span>'
            f'<span style="{SANS} font-size:18px; color:{INK2};">EU-OPENSCREEN, 2025{pdf(", " + NUMBERS[n] + " sites" + QREF.format(MONO=MONO, MUTE=MUTE, ref=SITES["ref"]))}</span></div></div>')
    side = (f'<div class="r" style="animation-delay:0.6s; position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; '
            f'display:flex; flex-direction:column; gap:12px;">'
            + WHY_NOW + '</div>')      # 26 Oct, simpler figures: the $30M joins Why now as one row
    return card + side


CSS = BASE_CSS + '''
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0 { opacity: 1; pointer-events: auto; }
    ''' + view_motion(1) + '''
'''
H = f'position:absolute; left:56px; top:86px; width:1100px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};'
FOOT = f'position:absolute; left:56px; bottom:44px; width:900px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
fig = lambda n: f'<span style="color:{D_TEXT}; font-weight:500;">fig {n}</span>'


def one_view(num, tag, h2, inner, foot, foot_w=1010, stage=''):
    """A dark talk slide with one view: since 26 Oct the network effect (06) and the market (07) are slides of their own."""
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">{tag}</span>'
    return f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(int(num), dark=True)}
  {header(num, '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">{h2}</h2>
  <div class="s s0">{inner}</div>
  <div class="s s0{'' if stage else ' pdfv'}" style="{FOOT} width:{foot_w}px;">{source(stage, foot) if stage else foot}</div>
</div>'''


def flywheel():
    """06, stage only: the growth loop in four steps (26 Oct 2026). Labs share controls free; each lab sharpens the map (this slide's
    curve); subscribers pay for the sharper data; labs get a share (the proposed terms, A15, A24), so the next lab joins."""
    step = lambda ico, words, d: (f'<div class="pop" style="animation-delay:{d}s; display:flex; flex-direction:column; align-items:center; gap:6px; text-align:center;">{icon(ico, D_GREEN, 30)}'
                               f'<span style="{SANS} font-size:18px; line-height:1.2; color:{D_TEXT};">{words}</span></div>')
    arrow = lambda a: f'<span class="f" aria-hidden="true" style="animation-delay:2.3s; display:flex; justify-content:center; align-items:center; {SANS} font-size:24px; color:{D_SOFT};">{a}</span>'
    return (f'<div class="talk" style="{PANEL_DARK} padding:20px 16px 16px;">'      # 26 Oct: in the one number panel, top-aligned like 04 and 07
            f'<div style="display:grid; grid-template-columns:1fr 34px 1fr; grid-template-rows:auto 30px auto; align-items:center; row-gap:4px;">'
            + step('lab', 'labs upload', 1.5) + arrow('&#8594;') + step('map', 'map sharpens', 1.7)
            + arrow('&#8593;') + arrow('&#8635;') + arrow('&#8595;')
            + step('subscriptions', 'labs keep a share', 2.1) + arrow('&#8592;') + step('certificate', 'AI teams pay', 1.9)
            + '</div>'
            + f'<div class="r" style="animation-delay:2.5s; display:flex; align-items:center; gap:10px; margin-top:16px; {SANS} font-size:18px; line-height:1.3; color:{D_TEXT};">{icon("lock", D_GREEN, 26)}'
              f'<span>Labs own their data.</span></div>'      # 26 Oct (Kat): decentralization, on stage (the loop is stage-only; A24 has the terms)
            + f'<div class="r" style="animation-delay:2.7s; display:flex; align-items:center; gap:10px; margin-top:10px; {SANS} font-size:18px; line-height:1.3; color:{D_TEXT};">{icon("model", D_GREEN, 26)}'
              f'<span>AI teams return better models, opt-in.</span></div>'      # 26 Oct: the map learns from its AI customers; opt-in, they keep their models
            + '</div>')


def build_density():
    """06: every lab that joins sharpens "normal" for everyone (results/e13), after the product, as its network effect."""
    e13 = results('e13-baseline-density.json')
    ref = e13['field_reference_by_labs']; ms = sorted(int(k) for k in ref)
    a, b = ref[str(ms[0])]['mean'], ref[str(ms[-1])]['mean']
    inner = f'''<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} padding:0 18px; display:flex; align-items:center; overflow:hidden;">{density_chart(e13)}</div>
    <div class="r" style="animation-delay:0.6s; position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:12px;">
      {pdf(f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:10px; padding-top:16px; border-top:1px solid rgba(246,247,247,.18);">{path_strip(dark=True, tags=False, vertical=True)}</div>')}
      {flywheel()}
    </div>'''
    foot = (f'{fig(5)} error: distance between two maps from different labs, in within-plate spreads; dot: mean of 400 draws, bar: 10th to 90th percentile; '
            f'measured to five labs, dashed beyond; {e13["n_plates"]:,} plates; JUMP [7]; results/e13')
    stage = ''      # its 6.2 -> 2.8 is derived on 05a; the full legend stays in the reader's layer
    body = one_view('06', 'The standard', 'Every lab that joins<br><span style="color:{D_GREEN};">sharpens &#8220;normal&#8221; for everyone.</span>'.replace('{D_GREEN}', D_GREEN), inner, foot, stage=stage)
    return CSS, body, None


def revenue():
    """07 (26 Oct, Kat: "show revenue scale by projected number of institutional subscribers"): yearly revenue against institutions
    subscribed, at A22's assumed site licence (low, base, high), straight multiplication; AI usage by API comes on top and is not priced."""
    from appendix import MARKET
    lo, base, hi = MARKET['site licence per year, $k']
    few, line = MARKET['lines each runs per quarter'][1], MARKET['price per line per quarter, $k'][1]      # the other route to one institution's year: 4 x $10k x 4
    assert abs(few * line * 4 - base) <= 0.1 * base, 'the two routes to one institution agree within a tenth'
    ns = (10, 25, 50, 100, 200)
    W, Hh, x0, y0, w, h = 700, 322, 70, 26, 600, 232          # drawn at the card's height, so its 17-18px labels render at about that size
    top = 200 * hi / 1000                                     # $M at the high price and 200 institutions
    X = lambda k: x0 + (k + 0.5) * w / len(ns); Y = lambda m: y0 + h - m / top * h
    g = [f'<path d="M {x0} {y0 + h} H {x0 + w}" stroke="{MUTE}" stroke-width="2"/>']
    for v in (0, 20, 40, 60):
        g.append(f'<path d="M {x0} {Y(v):.1f} H {x0 + w}" stroke="{GRID}" stroke-width="1.5"/>' + text(x0 - 10, Y(v) + 6, f'${v}M', 17, MUTE, 'end'))
    for k, n in enumerate(ns):
        b, l, u = n * base / 1000, n * lo / 1000, n * hi / 1000
        g.append(f'<rect class="bar" style="animation-delay:{0.3 + 0.1 * k:.1f}s" x="{X(k) - 30:.1f}" y="{Y(b):.1f}" width="60" height="{Y(0) - Y(b):.1f}" rx="6" fill="{GREEN}"/>')
        g.append(f'<g class="f" style="animation-delay:{0.8 + 0.1 * k:.1f}s"><path d="M {X(k):.1f} {Y(u):.1f} V {Y(l):.1f}" stroke="{INK2}" stroke-width="2"/>'
                 f'<path d="M {X(k) - 8:.1f} {Y(u):.1f} H {X(k) + 8:.1f} M {X(k) - 8:.1f} {Y(l):.1f} H {X(k) + 8:.1f}" stroke="{INK2}" stroke-width="2"/></g>')      # the range after its bar
        g.append(f'<g class="f" style="animation-delay:{0.8 + 0.1 * k:.1f}s">' + text(X(k), Y(u) - 10, f'${b:g}M', 18, INK, 'middle', 700) + '</g>')
        g.append(text(X(k), y0 + h + 26, f'{n}', 18, INK2, 'middle'))
    g.append(text(x0 + w / 2, y0 + h + 56, 'institutions subscribed', 18, INK2, 'middle'))
    chart = svg(W, Hh, g, fit=True, aria=f'Yearly revenue grows with institutions subscribed: at ${base}k each, 100 institutions is ${100 * base / 1000:g}M a year.')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:16px 24px 12px; display:flex; flex-direction:column; gap:6px;">'
            f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">Yearly revenue, at ${base}k per institution</span>'
            f'<span style="{MONO} font-size:15px; line-height:1.4; color:{MUTE};">${base}k = a site licence, or {few} cell lines &#215; ${line}k a quarter{pdf(f" (A22); bars ${lo}k to ${hi}k")}</span>'
            f'<div style="flex:1; min-height:0; display:flex; align-items:center;">{chart}</div>'
            f'<span style="{SANS} font-size:18px; color:{INK2};">API usage on top.</span></div>')


def build_economy():
    """07: what cell data is worth, and why it does not pool across labs today (figures/worth.py, EU-OPENSCREEN [13]); why now."""
    foot = (f'{fig(8)} EU-OPENSCREEN [{SITES["ref"]}], two measures: same lab, percent replicating ({SITES["line"]} at four sites, U2OS at one, filtered); '
            f'other labs, percent pairing ({SITES["line"]}); A23')
    from appendix import MARKET
    base = MARKET['site licence per year, $k'][1]
    foot = f'{fig(6)} revenue = institutions &#215; site licence, ${base}k a year assumed (A22); bars: $50k to $300k; AI usage by API not priced; EU-OPENSCREEN on A23'
    h2 = f'Every institution adds revenue.<br><span style="color:{D_GREEN};">100 of them: ${100 * base / 1000:g}M a year.</span>'
    side = economy()
    side = side[side.index('<div class="r" style="animation-delay:0.6s;'):]          # keep the $30M and why-now column
    stage = ''      # the $30M tile names its source; the 1.8 billion row says JUMP
    return CSS, one_view('07', 'The market', h2, revenue() + side, foot, 1010, stage=stage), None


def build():
    """Kept for reference: the two views as one slide, as it ran until 26 Oct."""
    return build_density()
