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
    # 26 Oct (Kat: "add go-to-market from the roadmap ... why now in the first minute"): why now moved to 02c (figures/templates/slide02.html);
    # this strip says how the network starts, who pays, and the channel (docs/roadmap.html, phases and revenue model)
    from slide09 import PARTNERS
    gtm = [('lab', f'{PARTNERS} partner labs join', '(A21)'), ('certificate', 'screening labs subscribe', '(A22)'),
           ('ai-reads', 'AI teams subscribe by API', '(A15)')]
    go = f'<span aria-hidden="true" style="{SANS} font-size:{T_TEXT}px; color:{INK2};">{arrow("e")}</span>'
    strip = (f'<div class="r pdf" style="animation-delay:3.4s; display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px 0 2px; border-top:1px solid #e4e8e9; white-space:nowrap;">'
             f'<span style="{MONO} font-size:{T_TEXT}px; letter-spacing:0.08em; text-transform:uppercase; color:{INK2};">go-to-market</span>'
             + go.join(f'<span style="display:inline-flex; align-items:center; gap:8px;">{icon(ic, INK2, 26)}<span style="{SANS} font-size:22px; color:{INK};">{what}</span>'
                          f'{pdf(f"<span style={chr(34)}{MONO} font-size:12px; color:{MUTE};{chr(34)}>{ref}</span>")}</span>' for ic, what, ref in gtm)
             + '</div>')
    inner = f'''<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} padding:10px 18px 12px; display:flex; flex-direction:column; overflow:hidden;"><div style="flex:1; min-height:0; display:flex; align-items:center;">{density_chart(e13, wide=True)}</div>{strip}</div>'''
    foot = (f'{fig(5)} error: distance between two maps from different labs, in within-plate spreads; dot: mean of 400 draws, bar: 10th to 90th percentile; '
            f'measured to five labs, dashed beyond; {e13["n_plates"]:,} plates; JUMP [7]; results/e13')
    stage = ''      # its 6.2 -> 2.8 is derived on 05a; the full legend stays in the reader's layer
    five = ['zero', 'one', 'two', 'three', 'four', 'five', 'six'][ms[-1]]      # the most labs a reference was built from
    title = (f'Every lab that joins sharpens &#8220;normal&#8221;:<br><span style="color:{D_GREEN};">error {a:.1f} with one lab, {b:.1f} with {five}.</span>')
    body = one_view('06', 'The standard', title, inner, foot, stage=stage)      # 26 Oct (pitch-deck-story): the finding with its number
    return CSS, body, None


def revenue():
    """07 (26 Oct, Kat: "five year plan slide not very clear"): two plain panels. Left, the plan: revenue a year, years 1 to 5, each
    bar labelled, the fifth the target in pink; the path is an assumption (first revenue of about $0.1M in year 2, as 09's 18 months
    to the first paying member; a tenth of the market in year 5), so about x4 a year. Right, who pays: every likely buyer (A22's
    base case) as one bar split by stream, the tenth bracketed in pink, then each stream's price and total. Sized 1:1 in px."""
    from appendix import MARKET
    b = {k: v[1] for k, v in MARKET.items()}
    streams = [('screening labs', b['organisations screening a few lines deep'] * b['lines each runs per quarter'] * b['price per line per quarter, $k'] * 4,
                f"${b['price per line per quarter, $k']}k/line/quarter", '#0a5c46'),
               ('buyers of cell data', b['companies buying cell data they did not make'] * b['purchased datasets each places on the map per year'] * b['price per dataset membership, $k'],
                f"${b['price per dataset membership, $k']}k/dataset", '#36a883'),
               ('big screening panels', b['organisations screening panels of hundreds to thousands of lines'] * b['site licence per year, $k'],
                f"${b['site licence per year, $k']}k/year", '#0f8f6c'),
               ('benchmark partners', b['benchmark partners'] * b['membership per partner per year, $k'],
                f"${b['membership per partner per year, $k']}k/year", '#8fc9b2')]
    total = sum(v for _, v, _, _ in streams) / 1000               # $M a year
    tenth = total / 10
    first, years = 0.1, 5
    rate = (tenth / first) ** (1 / (years - 2))
    path = [0] + [first * rate ** k for k in range(years - 1)]      # $M a year, years 1 to 5
    money = lambda v: '$0' if not v else (f'${v:.1f}M' if v < 10 else f'${v:.0f}M')
    W, H = 1120, 392
    g = []
    # left: the plan
    x0, xb, yt, yb, bw, step = 30, 560, 70, 288, 64, 104
    g.append(text(0, 24, 'five-year plan, revenue a year', T_TEXT, INK, weight=700))
    g.append(f'<path d="M {x0} {yb} H {xb}" stroke="{MUTE}" stroke-width="2"/>')
    for i, v in enumerate(path):
        x = x0 + 24 + i * step
        h = v / tenth * (yb - yt)
        hot = i == years - 1
        if h:
            g.append(f'<rect class="bar" style="animation-delay:{0.4 + 0.25 * i:.2f}s; transform-origin:{x + bw / 2}px {yb}px" x="{x}" y="{yb - max(h, 3):.1f}" '
                     f'width="{bw}" height="{max(h, 3):.1f}" rx="6" fill="{PINK if hot else GREEN}"/>')
        g.append(f'<g class="f" style="animation-delay:{0.6 + 0.25 * i:.2f}s">' + text(x + bw / 2, yb - max(h, 3) - 12, money(v), T_TEXT,
                                                                                         PINK if hot else INK, 'middle', 700 if hot else 400) + '</g>')
        g.append(text(x + bw / 2, yb + 30, str(i + 1), T_TEXT, INK2, 'middle'))
    g.append(text(x0 + 24 + 2 * step + bw / 2, yb + 60, 'year', T_TEXT, INK2, 'middle'))
    # its key, under the plot (Kat, 26 Oct: "figures: always have legend, prefer position under plot")
    ky = yb + 92
    g.append(f'<rect x="0" y="{ky - 17}" width="16" height="20" rx="3" fill="{GREEN}"/>' + text(26, ky, f'assumed: about &#215;{rate:.0f} a year from year 2', T_TEXT, INK2)
             + f'<rect x="436" y="{ky - 17}" width="16" height="20" rx="3" fill="{PINK}"/>' + text(462, ky, 'the target', T_TEXT, INK2))
    # right: who pays, every likely buyer as one bar, the tenth bracketed
    rx, rw, by, bh = 620, 500, 56, 40
    g.append(text(rx, 24, 'who pays, every likely buyer', T_TEXT, INK, weight=700))
    x = rx
    for k, (who, v, price, c) in enumerate(streams):
        w = v / 1000 / total * rw
        g.append(f'<rect class="f" style="animation-delay:{0.3 + 0.2 * k:.2f}s" x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{c}"/>')
        x += w
    tw = rw / 10
    g.append(f'<g class="f" style="animation-delay:1.6s"><path d="M {rx} {by + bh + 8} V {by + bh + 16} H {rx + tw:.1f} V {by + bh + 8}" fill="none" stroke="{PINK}" stroke-width="3"/>'
             + text(rx, by + bh + 46, f'a tenth: {money(tenth)}/year', T_TEXT, PINK, weight=700) + '</g>')
    for k, (who, v, price, c) in enumerate(streams):
        y = 186 + k * 46
        g.append(f'<g class="f" style="animation-delay:{0.5 + 0.2 * k:.2f}s"><rect x="{rx}" y="{y - 17}" width="16" height="20" rx="3" fill="{c}"/>'
                 + text(rx + 26, y, who, T_TEXT, INK) + text(rx + 252, y, price, T_TEXT, INK2)
                 + text(rx + rw, y, f'${v / 1000:g}M', T_TEXT, INK, 'end') + '</g>')      # the market's own figures: $3.75M, $1M
    aria = (f'Left: revenue a year in the plan, $0 in year 1, then {", ".join(money(v) for v in path[1:])} in years 2 to 5, about {rate:.0f} times a year; '
            f'right: every likely buyer, ${total:.0f}M a year: ' + ', '.join(f'{w} ${v / 1000:g}M' for w, v, _, _ in streams) + f'; a tenth, {money(tenth)}, is the target.')
    chart = svg(W, H, g, fit=True, aria=aria)
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
          + MARKET['companies buying cell data they did not make'][0] * MARKET['purchased datasets each places on the map per year'][0] * MARKET['price per dataset membership, $k'][0]
          + MARKET['benchmark partners'][0] * MARKET['membership per partner per year, $k'][0])
    foot = (f'{fig(6)} base case of A22: every count and price an assumption until a count replaces it; low case ${lo / 1000:.1f}M/year; academic labs join free and are the map, not the revenue; '
            f'AI usage by API not priced; beyond the base case, AI cell data is a $1.8B push [12] and irreproducible research costs $28B/year [6]; why now is on 02, go-to-market on 06')
    h2 = f'Every likely buyer: $84M/year.<br><span style="color:{D_GREEN};">Five-year target: a tenth, $8.4M/year.</span>'      # 26 Oct: the market, then the goal, with its number
    stage = ''
    return CSS, one_view('07', 'The market', h2, revenue(), foot, 1168, stage=stage), None      # 26 Oct: no side column


def build():
    """Kept for reference: the two views as one slide, as it ran until 26 Oct."""
    return build_density()
