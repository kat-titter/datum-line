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
                     for k, (ico, when, what, src) in enumerate((('map', '2023', '1.8B cells, public', ' (JUMP) [7, 25]'),
                                                  ('animal', '2025', 'FDA: fewer animal tests', ' [9]'),
                                                  ('certificate', '2025', '$30M per cell map', ': Roche to Recursion, Q3 2025 results [11]'),
                                                  ('ai-reads', 'now', 'AI reads cells', ', A10'))))
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
    ARROW = {'&#8594;': 0, '&#8595;': 90, '&#8592;': 180, '&#8593;': 270}
    arrow = lambda a: (f'<span class="f" aria-hidden="true" style="animation-delay:2.3s; display:flex; justify-content:center; align-items:center;">'
                       + (f'<svg viewBox="0 0 24 24" width="22" height="22" style="transform:rotate({ARROW[a]}deg);"><path d="M4 12h15M14 7l5 5-5 5" fill="none" stroke="{D_SOFT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
                          if a in ARROW else f'<svg viewBox="0 0 24 24" width="22" height="22"><path d="M19 12a7 7 0 1 1-2.1-5" fill="none" stroke="{D_SOFT}" stroke-width="2" stroke-linecap="round"/><path d="M17 3v4h-4" fill="none" stroke="{D_SOFT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
                       + '</span>')
    return (f'<div class="talk" style="{PANEL_DARK} padding:20px 16px 16px;">'      # 26 Oct: in the one number panel, top-aligned like 04 and 07
            f'<div style="display:grid; grid-template-columns:1fr 34px 1fr; grid-template-rows:auto 30px auto; align-items:center; row-gap:4px;">'
            + step('lab', 'labs upload', 1.5) + arrow('&#8594;') + step('map', 'map sharpens', 1.7)
            + arrow('&#8593;') + arrow('&#8635;') + arrow('&#8595;')
            + step('subscriptions', 'labs earn', 2.1) + arrow('&#8592;') + step('certificate', 'AI teams pay', 1.9)
            + '</div>'
            + f'<div class="r" style="animation-delay:2.5s; display:flex; align-items:center; gap:10px; margin-top:16px; {SANS} font-size:18px; line-height:1.3; color:{D_TEXT};">{icon("lock", D_GREEN, 26)}'
              f'<span>Labs own their data.</span></div>'      # 26 Oct (Kat): decentralization, on stage (the loop is stage-only; A24 has the terms)
            + f'<div class="r pdf" style="animation-delay:2.7s; display:flex; align-items:center; gap:10px; margin-top:10px; {SANS} font-size:18px; line-height:1.3; color:{D_TEXT};">{icon("model", D_GREEN, 26)}'
              f'<span>AI teams return better models, opt-in.</span></div>'      # 26 Oct: the map learns from its AI customers; opt-in, they keep their models
            + '</div>')


def build_density():
    """06: every lab that joins sharpens "normal" for everyone (results/e13), after the product, as its network effect."""
    e13 = results('e13-baseline-density.json')
    ref = e13['field_reference_by_labs']; ms = sorted(int(k) for k in ref)
    a, b = ref[str(ms[0])]['mean'], ref[str(ms[-1])]['mean']
    # 26 Oct (Kat: "cut the side panels"): one chart across the slide; the loop panel left the stage (05 and A24 carry it)
    # 26 Oct (Kat: "add go-to-market from the roadmap ... why now in the first minute"): why now moved to 02c (refine.real_cells);
    # this strip says how the network starts, who pays, and the channel (docs/roadmap.html, phases and revenue model)
    from slide09 import PARTNERS
    gtm = [('lab', f'{PARTNERS} partner labs upload', '(A21)'), ('certificate', 'screening labs subscribe', '(A22)'),
           ('shipped', 'vendors ship the certificate', '(roadmap)')]
    arrow = f'<span aria-hidden="true" style="{SANS} font-size:22px; color:{INK2};">&#8594;</span>'
    strip = (f'<div class="r" style="animation-delay:3.4s; display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px 0 2px; border-top:1px solid #e4e8e9; white-space:nowrap;">'
             f'<span style="{SANS} font-size:21px; font-weight:700; color:{INK};">Go-to-market</span>'
             + arrow.join(f'<span style="display:inline-flex; align-items:center; gap:8px;">{icon(ic, INK2, 24)}<span style="{SANS} font-size:20px; color:{INK};">{what}</span>'
                          f'{pdf(f"<span style={chr(34)}{MONO} font-size:12px; color:{MUTE};{chr(34)}>{ref}</span>")}</span>' for ic, what, ref in gtm)
             + '</div>')
    inner = f'''<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} padding:10px 18px 12px; display:flex; flex-direction:column; overflow:hidden;"><div style="flex:1; min-height:0; display:flex; align-items:center;">{density_chart(e13, wide=True)}</div>{strip}</div>'''
    foot = (f'{fig(5)} error: distance between two maps from different labs, in within-plate spreads; dot: mean of 400 draws, bar: 10th to 90th percentile; '
            f'measured to five labs, dashed beyond; {e13["n_plates"]:,} plates; JUMP [7]; results/e13')
    stage = ''      # its 6.2 -> 2.8 is derived on 05a; the full legend stays in the reader's layer
    body = one_view('06', 'The standard', 'Every lab that joins<br><span style="color:{D_GREEN};">sharpens &#8220;normal&#8221; for everyone.</span>'.replace('{D_GREEN}', D_GREEN), inner, foot, stage=stage)
    return CSS, body, None


def revenue():
    """07 (26 Oct, Kat: "this slide seems weak"): the market, not one multiplication. A22's base case, every likely buyer, as
    84 squares of $1M a year, coloured by who pays, each stream's count x price beside it; the five-year target (a tenth)
    outlined. Every count and price is an assumption (A22); the low and high cases are in the reader's line."""
    from appendix import MARKET
    b = {k: v[1] for k, v in MARKET.items()}
    streams = [('per-line checks', b['organisations screening a few lines deep'] * b['lines each runs per quarter'] * b['price per line per quarter, $k'] * 4,
                f"{b['organisations screening a few lines deep']} labs &#215; {b['lines each runs per quarter']} lines &#215; ${4 * b['price per line per quarter, $k']}k a year", '#0a5c46'),
               ('site licences', b['organisations screening panels of hundreds to thousands of lines'] * b['site licence per year, $k'],
                f"{b['organisations screening panels of hundreds to thousands of lines']} panels &#215; ${b['site licence per year, $k']}k a year", '#0f8f6c'),
               ('certificates', b['companies buying cell data they did not make'] * b['purchased datasets each certifies per year'] * b['price per certificate, $k'],
                f"{b['companies buying cell data they did not make']} buyers &#215; {b['purchased datasets each certifies per year']} datasets &#215; ${b['price per certificate, $k']}k", '#36a883'),
               ('benchmark', b['benchmark partners'] * b['membership per partner per year, $k'],
                f"{b['benchmark partners']} partners &#215; ${b['membership per partner per year, $k']}k a year", '#8fc9b2')]
    total = sum(v for _, v, _, _ in streams)                      # $k a year
    counts = [round(v / 1000) for _, v, _, _ in streams]          # squares of $1M
    assert sum(counts) == round(total / 1000), 'the squares add to the total'
    cols, P, S = 14, 46, 38
    g, k = [], 0
    for si, (name, v, how, c) in enumerate(streams):
        cells = ''.join(f'<rect x="{(q % cols) * P}" y="{(q // cols) * P}" width="{S}" height="{S}" rx="5" fill="{c}"/>' for q in range(k, k + counts[si]))
        g.append(f'<g class="f" style="animation-delay:{0.3 + 0.35 * si:.2f}s">{cells}</g>')
        k += counts[si]
    rows = -(-k // cols)
    tenth = total / 10 / 1000                                     # squares in the five-year target
    full = int(tenth)
    tx = full * P - (P - S) / 2 + (tenth - full) * P
    g.append(f'<path class="draw" style="animation-delay:2.0s" pathLength="1" d="M {-5} {-5} H {tx:.1f} V {S + 5} H -5 Z" fill="none" stroke="{PINK}" stroke-width="3.5"/>')      # the one target: pink
    g.append(f'<g class="f" style="animation-delay:2.6s">' + text(0, -18, f'five-year target: a tenth, ${tenth:.1f}M', 22, PINK, weight=700) + '</g>')
    g.append(f'<g class="f" style="animation-delay:2.8s"><rect x="0" y="{rows * P + 14}" width="18" height="18" rx="3" fill="{INK2}"/>'
             + text(28, rows * P + 30, 'one square: $1M a year', 22, INK2) + '</g>')
    lx = cols * P + 40
    # 26 Oct (Kat: "business model more sexy specifics: ... revenue model"): the legend is the price list, who pays, for what, at
    # what price, and the count x price that gives each stream's square count; labs join free; AI teams pay by API, not yet priced
    price = {'per-line checks': '$10k a line, a quarter', 'site licences': '$150k a year', 'certificates': '$25k per dataset', 'benchmark': '$100k a year'}
    who = {'per-line checks': 'screening labs', 'site licences': 'big screening panels', 'certificates': 'buyers of cell data', 'benchmark': 'benchmark partners'}
    for si, (name, v, how, c) in enumerate(streams):
        y = 22 + si * 64
        g.append(f'<g class="f" style="animation-delay:{0.3 + 0.35 * si:.2f}s"><rect x="{lx}" y="{y - 16}" width="18" height="18" rx="3" fill="{c}"/>'
                 + text(lx + 30, y, who[name], 24, INK) + text(lx + 440, y, f'${v / 1000:g}M', 24, INK, 'end', 700)
                 + text(lx + 30, y + 28, price[name], 22, INK2, weight=700) + text(lx + 440, y + 28, how.split(' &#215; $')[0], 22, MUTE, 'end') + '</g>')
    yf = 22 + len(streams) * 64
    g.append(f'<g class="f" style="animation-delay:{0.3 + 0.35 * len(streams):.2f}s">'      # 26 Oct (Kat: "more simple"): the unpriced side, one line
             f'<rect x="{lx}" y="{yf - 16}" width="18" height="18" rx="3" fill="none" stroke="{MUTE}" stroke-width="1.5"/>'
             + text(lx + 30, yf, 'academic labs: free', 24, INK) + text(lx + 440, yf, 'AI teams: by API', 24, INK2, 'end')
             + text(lx + 30, yf + 28, 'labs are the map; API pricing not yet set', 20, MUTE, extra='class="pdf"') + '</g>')      # 26 Oct (pitch skill, word budget): the reader's
    W, Hh = lx + 450, max(rows * P + 46, yf + 40)
    chart = svg(W, Hh + 50, [f'<g transform="translate(6, 44)">'] + g + ['</g>'], fit=True,
                aria=f'Every likely buyer: ${total / 1000:.0f}M a year, as {k} squares of $1M: ' + ', '.join(f'{n} ${v / 1000:g}M' for n, v, _, _ in streams)
                     + f'; the five-year target, a tenth, ${tenth:.1f}M.')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:16px 24px 12px; display:flex; align-items:center;">{chart}</div>')


def build_economy():
    """07: what cell data is worth, and why it does not pool across labs today (figures/worth.py, EU-OPENSCREEN [13]); why now."""
    foot = (f'{fig(8)} EU-OPENSCREEN [{SITES["ref"]}], two measures: same lab, percent replicating ({SITES["line"]} at four sites, U2OS at one, filtered); '
            f'other labs, percent pairing ({SITES["line"]}); A23')
    from appendix import MARKET
    base = MARKET['site licence per year, $k'][1]
    from appendix import MARKET
    lo = (MARKET['organisations screening a few lines deep'][0] * MARKET['lines each runs per quarter'][0] * MARKET['price per line per quarter, $k'][0] * 4
          + MARKET['organisations screening panels of hundreds to thousands of lines'][0] * MARKET['site licence per year, $k'][0]
          + MARKET['companies buying cell data they did not make'][0] * MARKET['purchased datasets each certifies per year'][0] * MARKET['price per certificate, $k'][0]
          + MARKET['benchmark partners'][0] * MARKET['membership per partner per year, $k'][0])
    foot = (f'{fig(6)} base case of A22: every count and price an assumption until a count replaces it; low case ${lo / 1000:.1f}M a year; academic labs join free and are the map, not the revenue; '
            f'AI usage by API not priced; why now is on 02, go-to-market on 06')
    h2 = f'Every likely buyer: $84M a year.<br><span style="color:{D_GREEN};">Five-year target: a tenth.</span>'      # 26 Oct: the market, then the goal
    stage = ''
    return CSS, one_view('07', 'The market', h2, revenue(), foot, 1168, stage=stage), None      # 26 Oct: no side column


def build():
    """Kept for reference: the two views as one slide, as it ran until 26 Oct."""
    return build_density()
