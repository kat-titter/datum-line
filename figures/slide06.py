"""Slide 06, two views. First: data is the new currency, and cell data does not convert between labs: one public price
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
WHY_NOW = (f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:8px;">'
           f'<span style="{SANS} font-size:18px; font-weight:700; color:{D_TEXT};">Why now</span>'
           + ''.join(f'<div style="display:grid; grid-template-columns:24px 50px minmax(0,1fr); align-items:center; gap:12px; padding:9px 14px; '
                     f'border-radius:10px; background:rgba(246,247,247,.06);">{icon(ico, D_SOFT, 24)}'
                     f'<span style="{MONO} font-size:18px; color:{D_SOFT};">{when}</span>'
                     f'<span style="{SANS} font-size:18px; line-height:1.25; color:{D_TEXT};">{what}{pdf(src)}</span></div>'
                     for ico, when, what, src in (('map', '2023', '1.8 billion cells, public', ' [7, 25]'),
                                                  ('animal', '2025', 'FDA moves off animal tests', ' [9]'),
                                                  ('ai-reads', 'now', 'AI reads cell images', ', A10')))
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
            + stat_tile(big, 'one cell dataset', f'Roche paid it{pdf(f": a milestone for one whole-genome map of microglia [{ref}]")}', size=72)
            + WHY_NOW + '</div>')
    return card + side


def build():
    e13 = results('e13-baseline-density.json')
    ref = e13['field_reference_by_labs']; ms = sorted(int(k) for k in ref)
    a, b = ref[str(ms[0])]['mean'], ref[str(ms[-1])]['mean']
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
  <h2 class="s s0" style="{H}">Cell data sells.<br><span style="color:{D_GREEN};">Across labs, it is not one dataset.</span></h2>
  <h2 class="s s1" style="{H}">Every lab that joins<br><span style="color:{D_GREEN};">sharpens &#8220;normal&#8221; for everyone.</span></h2>
  <div class="s s0">{economy()}</div>
  <div class="s s1">
    <div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} padding:0 18px; display:flex; align-items:center; overflow:hidden;">{density_chart(e13)}</div>
    <div class="r" style="animation-delay:0.6s; position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:12px;">
      <div style="display:grid; grid-template-columns:auto auto auto; justify-content:start; align-items:end; column-gap:18px; row-gap:10px;">
        <span style="{SANS} font-size:80px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{D_GREEN};">{a:.1f}</span>
        <span style="{SANS} font-size:80px; font-weight:700; line-height:1; color:{D_GREEN};">&#8594;</span>
        <span style="{SANS} font-size:80px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{D_GREEN};">{b:.1f}</span>
        <span class="talk" style="display:flex; gap:2px;">{"".join(icon("lab", D_SOFT, 24) for _ in range(ms[0]))}</span><span class="talk"></span>
        <span class="talk" style="display:flex; gap:2px;">{"".join(icon("lab", D_SOFT, 24) for _ in range(ms[-1]))}</span>
      </div>
      <span style="{SANS} font-size:20px; line-height:1.35; color:{D_SOFT};">error in &#8220;normal&#8221;{pdf(f": {NUMBERS[ms[0]]} lab, then {NUMBERS[ms[-1]]}")}</span>
      {pdf(f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:10px; padding-top:16px; border-top:1px solid rgba(246,247,247,.18);">{path_strip(dark=True, tags=False, vertical=True)}</div>')}
    </div>
  </div>
  <div class="s s0 pdfv" style="{FOOT} width:748px;">{fig(5)} EU-OPENSCREEN [{SITES["ref"]}], two measures: same lab, percent replicating ({SITES["line"]} at four sites, U2OS at one, filtered); other labs, percent pairing ({SITES["line"]}); A23</div>
  <div class="s s1 pdfv" style="{FOOT}">{fig(6)} error: distance between two maps from different labs, in within-plate spreads; dot: mean of 400 draws, bar: 10th to 90th percentile &#183; measured to five labs, dashed beyond &#183; {e13["n_plates"]:,} plates &#183; JUMP [7] &#183; results/e13</div>
  {cue(2, dark=True)}
</div>'''
    steps = {'tag': ['The data economy', 'The standard']}
    return css, body, steps
