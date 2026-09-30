"""Slide 06: the product, as one lab would have seen it on one day. Written whole from results/e9, e12 and e2.

The batch shown is the lab's in-distribution batch with the most plates. Its whole replay is appendix A11.
"""
from datetime import date

from parts import *
from slide05 import embedding, map_axes

LAB = 'source_2'
TICK = '<path d="M -6 0.5 L -2 4.5 L 6 -4.5" fill="none" stroke="#ffffff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'


def centre(rows):
    return sum(float(r['pc1']) for r in rows) / len(rows), sum(float(r['pc2']) for r in rows) / len(rows)


def your_map(B, now):
    """The field in green, this lab's wells to date in pale pink, and the batch just sent as the dot."""
    rows = embedding()
    W, H = 1520, 560
    ax, cloud = map_axes(rows, 0, 0, W, H)
    others = sorted({r['lab'] for r in rows if r['lab'] != LAB}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    g = [f'<rect width="{W}" height="{H}" rx="18" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::3], colour[l], 4.2, 'opacity="0.7"') for l in others]
    mine = [r for r in rows if r['lab'] == LAB]
    sent = B[:B.index(now) + 1]
    g.append(cloud([r for r in mine if any(r['plate'] in b['plates'] for b in sent)], PALE_PINK, 4.2, 'opacity="0.8"'))
    here = centre([r for r in mine if r['plate'] in now['plates']])
    near = centre([r for r in rows if r['lab'] == now['nearest_other']])
    x, y = ax.X(here[0]), ax.Y(here[1]); nx, ny = ax.X(near[0]), ax.Y(near[1])
    g.append(f'<path d="M {x:.1f} {y:.1f} L {nx:.1f} {ny:.1f}" stroke="{INK2}" stroke-width="2.5" stroke-dasharray="7 7"/>')
    g.append(f'<circle class="ping" cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{PINK}" stroke-width="3"/>')
    g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="{PINK}" stroke="#ffffff" stroke-width="4"/>')
    g.append(text(x, y + 56, 'you', 34, PINK, 'middle', 700))
    g.append(text(nx + 30, ny + 54, f'{now["to_nearest_other"]:.1f} to {lab_name(now["nearest_other"])}', 28, INK2, weight=600))
    g.append(text(28, H - 26, 'PC 1 &#8594;', 22, MUTE))
    g.append(f'<g transform="translate(36,{H - 66}) rotate(-90)">{text(0, 0, "PC 2 &#8594;", 22, MUTE)}</g>')
    return svg(W, H, g, aria='The field of eleven labs in green, this lab in pink, with its wells so far and a line to the nearest other lab.', fit=True)


def streak(B, now):
    """One mark per batch sent so far, and an open one for the next."""
    n = B.index(now) + 1
    mark = lambda k: (f'<g transform="translate({18 + k * 40},18)" class="f" style="animation-delay:{0.5 + 0.08 * k:.2f}s">'
                      f'<circle r="15" fill="{GREEN}"/>{TICK}</g>')
    nxt = (f'<g transform="translate({18 + n * 40},18)"><circle r="14" fill="none" stroke="{PINK}" stroke-width="2.5" stroke-dasharray="5 5"/>'
           f'<path d="M -6 0 H 6 M 0 -6 V 6" stroke="{PINK}" stroke-width="2.6" stroke-linecap="round"/></g>')
    W = 36 + n * 40
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 36" width="{W}" height="36" role="img" '
            f'aria-label="{n} batches sent in a row, and a place for the next." style="display:block; flex-shrink:0;">'
            + ''.join(mark(k) for k in range(n)) + nxt + '</svg>')


def app(R, B, now):
    d = date.fromisoformat(now['date'])
    n = B.index(now) + 1
    bar = (f'<div style="display:flex; justify-content:space-between; align-items:center; padding:0 4px;">'
           f'<span style="{MONO} font-size:13px; letter-spacing:0.08em; text-transform:uppercase; color:{MUTE};">{lab_name(R["lab"])} &#183; U2OS &#183; {d.day} {d.strftime("%B")} {d.year}</span>'
           f'<span style="{MONO} font-size:13px; padding:4px 12px; border-radius:999px; background:{PINK}; color:#ffffff;">{now["n_plates"]} plates of controls, sent</span></div>')
    foot = (f'<div style="display:flex; align-items:center; gap:16px; padding:0 4px;">{streak(B, now)}'
            f'<span style="{SANS} font-size:17px; color:{INK};"><span style="font-weight:700;">{n} batches in a row.</span> '
            f'<span style="color:{MUTE};">Each one adds to the reference.</span></span></div>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:204px; width:800px; height:430px; {CARD_ON_DARK} '
            f'padding:14px 16px 14px; display:flex; flex-direction:column; gap:10px;">{bar}'
            f'<div style="flex:1 1 0; min-height:0; display:flex;">{your_map(B, now)}</div>{foot}</div>')


def certificate(R, now, frame):
    row = lambda name, value: (f'<div style="display:flex; flex-direction:column; gap:2px; padding:8px 0; border-top:1px solid #d3d8da;">'
                               f'{label(name)}<span style="{SANS} font-size:15px; line-height:1.3; color:{INK};">{value}</span></div>')
    pill = (f'<span style="display:flex; padding:3px 0 5px;"><span style="{MONO} font-size:13px; padding:4px 12px; border-radius:999px; '
            f'background:{GREEN}; color:#ffffff;">in distribution</span></span>')
    own = {'inside': 'in range', 'below': 'below range', 'above': 'above range'}[now['cell_count_vs_own_history']]
    d = date.fromisoformat(now['date'])
    when = f"{lab_name(R['lab'])} &#183; {d.day} {d.strftime('%B')} {d.year}"
    seal = open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="76" height="76"')
    head = (f'<div style="display:flex; justify-content:space-between; align-items:center; padding-bottom:6px;">'
            f'<div style="display:flex; flex-direction:column; gap:3px;">'
            f'<span style="{SANS} font-size:21px; font-weight:700; letter-spacing:-0.02em; color:{INK};">Certificate</span>'
            f'{label(when, PINK)}</div>{seal}</div>')
    up = f'<span style="color:{GREEN}; font-weight:700;">{frame["agree_field_raw"]:.2f} &#8594; {frame["agree_field_field"]:.2f}</span>'
    return (f'<div class="r" style="animation-delay:1.0s; position:absolute; right:56px; top:106px; width:344px; box-sizing:border-box; padding:16px 22px 14px; '
            f'background:linear-gradient(180deg,#ffffff,#f1f3f3); border-radius:16px; display:flex; flex-direction:column; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 28px 70px rgba(0,0,0,0.50);">' + head
            + row('Your cells', f'U2OS &#183; {now["n_plates"]} plates')
            + row('Where you sit', pill + f'{now["from_baseline"]:.1f} from your baseline &#183; {now["to_nearest_other"]:.1f} to the nearest lab')
            + row('Your own check', f'{now["cells_per_well"]:.0f} cells per well &#183; {own}')
            + row('Your reference', f'{R["n_reference_plates"]:,} plates &#183; {len(R["reference_labs"])} labs')
            + row('Your data, in the field&#8217;s frame', f'agreement with other labs {up}')
            + f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE}; padding-top:8px; border-top:1px solid #d3d8da;">'
            f'Held by nobody who sells you cells, media or the instrument.</span></div>')


def build():
    R = results('e9-replay.json')['labs'][LAB]; B = R['batches']
    now = max((b for b in B if b['verdict'] == 'in distribution'), key=lambda b: b['n_plates'])
    frame = next(b for b in results('e12-field-normalization.json')['lab_2'] if b['batch'] == now['batch'])
    css = BASE_CSS + '''
    .ping { transform-box: fill-box; transform-origin: center; animation: ping 2.2s ease-out infinite; }
    @keyframes ping { 0% { transform: scale(1); opacity: .9; } 100% { transform: scale(3.4); opacity: 0; } }
'''
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 46px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(6, dark=True)}
  {header('06', 'The product &#183; a growth chart for cell lines', dark=True)}
  <h2 style="position:absolute; left:56px; top:86px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.05; color:{D_TEXT};">Send your controls. <span style="color:{D_PINK};">See where you stand.</span></h2>
  <p style="position:absolute; left:56px; top:146px; width:770px; margin:0; {SANS} font-size:19px; line-height:1.38; color:{D_SOFT};">The images you already take. Back: <span style="color:{D_TEXT}; font-weight:600;">your place in the field, and your data in its frame.</span></p>
  {app(R, B, now)}
  {certificate(R, now, frame)}
  <div style="position:absolute; left:56px; bottom:44px; width:800px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};"><span style="color:{D_TEXT}; font-weight:500;">Fig. 6</span> {lab_name(R['lab']).capitalize()} on {short_date(now['date'])}, replayed against the published field. JUMP [7]. More: A11</div>
</div>'''
    return css, body, None
