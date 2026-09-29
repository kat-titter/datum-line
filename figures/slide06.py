"""Slide 06: the product, replayed on one real lab. Written whole from results/e9 and e6."""
from datetime import date

from parts import *

TILE_W, TILE_GAP, TILE_H = 52, 6, 84


def intensity_sentence(e6):
    """What moved, in one sentence, from the intensity groups of e6."""
    g = sorted([x for x in e6['groups'] if x['measurement'] == 'Intensity'], key=lambda x: -abs(x['mean_shift']))
    way = lambda x: 'up' if x['mean_shift'] > 0 else 'down'
    a, b = g[0], g[1]
    return f"{a['channel']} and {b['channel']} stain intensity, {way(a)} {abs(a['mean_shift']):.1f} and {abs(b['mean_shift']):.1f} sd"


def tile(b, k):
    x = k * (TILE_W + TILE_GAP)
    out, base = b['verdict'] == 'outside', b['is_baseline']
    colour = PINK if out else (FAINT if base else GREEN)
    if out:
        glyph = f'<path d="M -8 -8 L 8 8 M 8 -8 L -8 8" stroke="#ffffff" stroke-width="3.2" stroke-linecap="round"/>'
    elif base:
        glyph = '<circle r="4.5" fill="#ffffff"/>'
    else:
        glyph = '<path d="M -8 0.5 L -2.5 6 L 8 -6" fill="none" stroke="#ffffff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
    word = 'out' if out else ('base' if base else 'in')
    # the entrance animation sets a CSS transform, so the position sits on an outer group
    return (f'<g transform="translate({x},0)"><g class="r" style="animation-delay:{0.25 + 0.09 * k:.2f}s">'
            f'<rect width="{TILE_W}" height="{TILE_H}" rx="9" fill="#ffffff"/>'
            f'<rect width="{TILE_W}" height="7" rx="3.5" fill="{colour}"/>'
            f'<g transform="translate({TILE_W / 2},38)"><circle r="15" fill="{colour}"/>{glyph}</g>'
            f'<text x="{TILE_W / 2}" y="73" font-family="IBM Plex Mono, Menlo, monospace" font-size="13" fill="{colour if out else INK2}" '
            f'text-anchor="middle" letter-spacing="0.6">{word.upper()}</text></g></g>')


def replay_strip(B):
    n = len(B); W = n * TILE_W + (n - 1) * TILE_GAP
    cx = lambda k: k * (TILE_W + TILE_GAP) + TILE_W / 2
    lo, hi = 140, 210
    y = lambda v: 18 + 64 - (v - lo) / (hi - lo) * 64
    mono = 'font-family="IBM Plex Mono, Menlo, monospace" font-size="13"'
    g = [f'<text x="0" y="10" {mono} fill="{D_DIM}" letter-spacing="1.3">WHAT THE LAB SAW &#183; CELLS PER UNTREATED WELL</text>']
    g.append('<path d="' + ' '.join(f'{"M" if k == 0 else "L"} {cx(k):.1f} {y(b["cells_per_well"]):.1f}' for k, b in enumerate(B))
             + f'" fill="none" stroke="{D_DIM}" stroke-width="1.5" opacity=".6"/>')
    low = min(range(n), key=lambda k: B[k]['cells_per_well'])
    for k, b in enumerate(B):
        g.append(f'<circle cx="{cx(k):.1f}" cy="{y(b["cells_per_well"]):.1f}" r="5" fill="{D_SOFT}"/>')
        if k in (0, low, n - 1):
            g.append(f'<text x="{cx(k):.1f}" y="{y(b["cells_per_well"]) + (22 if k == low else -12):.1f}" {mono} fill="{D_SOFT}" text-anchor="middle">{b["cells_per_well"]:.0f}</text>')
    top = 126
    g.append(f'<text x="0" y="{top - 12}" {mono} fill="{D_DIM}" letter-spacing="1.3">WHAT THE CERTIFICATE WOULD HAVE SAID</text>')
    g.append(f'<g transform="translate(0,{top})">' + ''.join(tile(b, k) for k, b in enumerate(B)) + '</g>')
    for k, b in enumerate(B):
        g.append(f'<text x="{cx(k):.1f}" y="{top + TILE_H + 22}" {mono} fill="{D_SOFT}" text-anchor="middle">{short_date(b["date"])}</text>')
        g.append(f'<text x="{cx(k):.1f}" y="{top + TILE_H + 42}" {mono} fill="{D_DIM}" text-anchor="middle">{b["n_plates"]}</text>')
    g.append(f'<text x="{W + 12}" y="{top + TILE_H + 42}" {mono} fill="{D_DIM}">plates</text>')
    out = [k for k, b in enumerate(B) if b['verdict'] == 'outside']
    x0, x1, yb = cx(out[0]) - TILE_W / 2, cx(out[-1]) + TILE_W / 2, top + TILE_H + 58
    weeks = round((date.fromisoformat(B[-1]['date']) - date.fromisoformat(B[out[0]]['date'])).days / 7)
    g.append(f'<g class="f" style="animation-delay:1.7s"><path d="M {x0} {yb} v 8 H {x1} v -8" fill="none" stroke="{D_PINK}" stroke-width="2"/>'
             f'<text x="{x1}" y="{yb + 32}" font-family="Archivo, Helvetica, sans-serif" font-size="19" font-weight="600" fill="{D_PINK}" text-anchor="end">'
             f'out from {short_date(B[out[0]]["date"])}: {weeks} weeks before October</text></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 70} {yb + 44}" width="{W + 70}" height="{yb + 44}" role="img" '
            f'aria-label="Thirteen batches of lab 2 in date order. Cell counts stay in range. The certificate reads in distribution for ten batches and outside for the last three." '
            f'style="display:block; overflow:visible;">' + ''.join(g) + '</svg>')


def certificate(R, flag, e6):
    row = lambda name, value: (f'<div style="display:flex; flex-direction:column; gap:2px; padding:7px 0; border-top:1px solid #d3d8da;">'
                               f'{label(name)}<span style="{SANS} font-size:15px; line-height:1.3; color:{INK};">{value}</span></div>')
    pills = (f'<span style="display:flex; gap:8px; padding:3px 0 5px;">'
             f'<span style="{MONO} font-size:13px; padding:4px 10px; border-radius:999px; border:1.5px solid #c3c9cb; color:#949c9f;">in distribution</span>'
             f'<span style="{MONO} font-size:13px; padding:4px 10px; border-radius:999px; background:{PINK}; color:#f6f7f7;">outside it</span></span>')
    own = {'inside': 'in range', 'below': 'below range', 'above': 'above range'}[flag['cell_count_vs_own_history']]
    d = date.fromisoformat(flag['date'])
    when = f"{lab_name(R['lab'])} &#183; {d.day} {d.strftime('%B')} {d.year}"
    seal = open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="76" height="76"')
    head = (f'<div style="display:flex; justify-content:space-between; align-items:center; padding-bottom:6px;">'
            f'<div style="display:flex; flex-direction:column; gap:3px;">'
            f'<span style="{SANS} font-size:21px; font-weight:700; letter-spacing:-0.02em; color:{INK};">Certificate</span>'
            f'{label(when, PINK)}</div>{seal}</div>')
    n_plates, n_ref, n_labs = flag['n_plates'], R['n_reference_wells'], len(R['reference_labs'])
    drift, other, cells = flag['from_baseline'], flag['to_nearest_other'], flag['cells_per_well']
    return (f'<div class="r" style="animation-delay:1.2s; position:absolute; right:56px; top:106px; width:344px; box-sizing:border-box; padding:16px 22px 14px; '
            f'background:linear-gradient(180deg,#ffffff,#f1f3f3); border-radius:16px; display:flex; flex-direction:column; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 28px 70px rgba(0,0,0,0.50);">' + head
            + row('Your cells', f'U2OS &#183; {n_plates} plates')
            + row('Compared with', f'{n_ref:,} wells &#183; {n_labs} labs')
            + row('Result', pills + f'{drift:.1f} from your baseline &#183; {other:.1f} to the nearest lab')
            + row('Your own check', f'{cells:.0f} cells per well &#183; {own}')
            + row('What moved', intensity_sentence(e6))
            + f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE}; padding-top:6px; border-top:1px solid #d3d8da;">'
            f'Held by nobody who sells you cells, media or the instrument.</span></div>')


def build():
    R = results('e9-replay.json')['labs']['source_2']; B = R['batches']
    e6 = results('e6-what-moved-source_2-first-flag.json')
    flag = next(b for b in B if b['verdict'] == 'outside')
    assert e6['batch'] == flag['batch'], 'e6 must describe the first flagged batch'
    out = [b for b in B if b['verdict'] == 'outside']
    who = lab_name(R['lab']).capitalize()
    held = ', '.join(str(b['n_plates']) for b in out[:-1]) + f' and {out[-1]["n_plates"]}'
    css = BASE_CSS
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 46px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(6, dark=True)}
  {header('06', 'The product &#183; a growth chart for cell lines', dark=True)}
  <h2 style="position:absolute; left:56px; top:86px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.05; color:{D_TEXT};">Know on day one, <span style="color:{D_PINK};">not month four.</span></h2>
  <p style="position:absolute; left:56px; top:146px; width:770px; margin:0; {SANS} font-size:19px; line-height:1.38; color:{D_SOFT};">Send the control images you already take. Get back <span style="color:{D_TEXT}; font-weight:600;">where you sit, and what moved.</span></p>
  <div style="position:absolute; left:56px; top:232px;">{replay_strip(B)}</div>
  {certificate(R, flag, e6)}
  <div style="position:absolute; left:56px; bottom:44px; width:800px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};"><span style="color:{D_TEXT}; font-weight:500;">Fig. 5</span> {who}&#8217;s {len(B)} batches, replayed against the published field. JUMP [7]. More: A11, A12</div>
</div>'''
    return css, body, None
