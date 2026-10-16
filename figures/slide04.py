"""Slide 04: the map, in two views. Written whole from results/e2 and e10.

The density chart is slide 06 (slide06.py); the frame chart is board A14; the two charts of one lab
over time are board A13. All are kept here because they share the axes and the map."""
import csv
from datetime import date

from parts import *


def time_axis(batches, x0, w, y0, h, ylim):
    d0 = date.fromisoformat(batches[0]['date']); span = (date.fromisoformat(batches[-1]['date']) - d0).days
    ax = Axes(x0, y0, w, h, (-0.06 * span, 1.06 * span), ylim)
    day = lambda iso: (date.fromisoformat(iso) - d0).days
    months = [(day(f'{d0.year}-{m:02d}-01') if m > d0.month else 0, name)
              for m, name in ((6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Oct'))]
    return ax, day, months


def outside_band(B, ax, day):
    """A faint pink band over the batches that are outside, from midway after the last batch inside to the right edge."""
    k = next(i for i, b in enumerate(B) if b['verdict'] == 'outside')
    x = (ax.X(day(B[k - 1]['date'])) + ax.X(day(B[k]['date']))) / 2
    return f'<rect x="{x:.1f}" y="{ax.y0}" width="{ax.x0 + ax.w - x:.1f}" height="{ax.h}" fill="{PINK}" opacity="0.07"/>'


def cell_count_chart(B):
    n_plates = sum(b['n_plates'] for b in B)
    ax, day, months = time_axis(B, 96, 640, 64, 376, (130, 220))
    g = ax.frame((150, 175, 200), months, 'cells per untreated well',
                 f'batch date, 2021 ({len(B)} batches, {n_plates} plates)', 'lab&#8217;s own check: cells per well')
    g.append(outside_band(B, ax, day))
    for k, b in enumerate(B):
        late = b['verdict'] == 'outside'
        g.append(f'<circle class="f" style="animation-delay:{0.15 + 0.07 * k:.2f}s" cx="{ax.X(day(b["date"])):.1f}" '
                 f'cy="{ax.Y(b["cells_per_well"]):.1f}" r="{11 if late else 9}" fill="{PINK if late else PALE_PINK}"/>')
    low = min(B, key=lambda b: b['cells_per_well'])
    assert low['cell_count_vs_own_history'] == 'below', 'A13 says the lab catches this dip'
    g.append(text(ax.X(day(low['date'])) + 18, ax.Y(low['cells_per_well']) + 7, f"{low['cells_per_well']:.0f}: lab catches this dip", 20, INK2))
    out = [b for b in B if b['verdict'] == 'outside']
    x, y = ax.X(day(out[-1]['date'])) - 4, ax.Y(min(b['cells_per_well'] for b in out)) + 58
    g.append(f'<g class="f" style="animation-delay:1.3s">{text(x, y, "last three batches", 26, PINK, "end", 700)}'
             f'{text(x, y + 30, "{:.0f} to {:.0f} cells per well".format(min(b["cells_per_well"] for b in out), max(b["cells_per_well"] for b in out)), 22, INK2, "end")}'
             f'{text(x, y + 58, "inside the lab&#8217;s own range", 22, INK2, "end")}</g>')
    return svg(760, 510, g, aria='Cells per untreated well for each batch of lab 2; the last three batches are inside the range of the earlier ones.')


def distance_chart(B):
    """Distance from the lab's own first batch and to the nearest other lab; a ribbon under the dates names the nearest lab."""
    top = 2 * (int(max(b['from_baseline'] for b in B) / 2) + 1)
    ax, day, months = time_axis(B, 96, 640, 64, 376, (0, top))
    g = ax.frame(range(0, top + 1, 4), months, 'distance &#183; higher = further apart', '', 'compared with other labs')
    g.append(outside_band(B, ax, day))
    out = [b for b in B if b['verdict'] == 'outside']
    n = sum(b['n_plates'] for b in out); assert n == sum(b['plates_outside'] for b in out)
    g.append(f'<g class="f" style="animation-delay:1.3s">{text(ax.x0 + ax.w - 8, ax.y0 + ax.h - 40, f"all {n} plates", 20, PINK, "end", 700)}'
             f'{text(ax.x0 + ax.w - 8, ax.y0 + ax.h - 14, "nearer another lab", 20, PINK, "end", 700)}</g>')
    path = lambda key: ' '.join(f'{"M" if k == 0 else "L"} {ax.X(day(b["date"])):.1f} {ax.Y(b[key]):.1f}' for k, b in enumerate(B))
    g.append(f'<path d="{path("to_nearest_other")}" fill="none" stroke="{GREEN}" stroke-width="3" stroke-linejoin="round"/>')
    g.append(f'<path d="{path("from_baseline")}" fill="none" stroke="{PINK}" stroke-width="3.6" stroke-linejoin="round"/>')
    for b in B:
        g.append(f'<circle cx="{ax.X(day(b["date"])):.1f}" cy="{ax.Y(b["to_nearest_other"]):.1f}" r="6" fill="{GREEN}"/>')
        g.append(f'<circle cx="{ax.X(day(b["date"])):.1f}" cy="{ax.Y(b["from_baseline"]):.1f}" r="7" fill="{PINK}"/>')
    # the nearest lab, one ribbon segment per run of batches that share it
    xs = [ax.X(day(b['date'])) for b in B]
    runs = []
    for k, b in enumerate(B):
        if k and b['nearest_other'] == B[k - 1]['nearest_other']: runs[-1][1] = k
        else: runs.append([k, k, b['nearest_other']])
    for j, (i0, i1, src) in enumerate(runs):
        a = ax.x0 if i0 == 0 else (xs[i0 - 1] + xs[i0]) / 2 + 1
        z = ax.x0 + ax.w if i1 == len(B) - 1 else (xs[i1] + xs[i1 + 1]) / 2 - 1
        g.append(f'<g class="f" style="animation-delay:{0.6 + 0.3 * j:.2f}s"><rect x="{a:.1f}" y="{ax.y0 + ax.h + 40}" width="{z - a:.1f}" height="28" rx="6" fill="{GREEN}"/>'
                 f'{text((a + z) / 2, ax.y0 + ax.h + 60, ("nearest: " if j == 0 else "") + lab_name(src), 19, "#ffffff", "middle", 700)}</g>')
    g.append(text(ax.x0 + 30, ax.y0 + 38, 'from its own first batch', 24, PINK, weight=700))
    g.append(text(ax.x0 + 30, ax.y0 + 70, 'to the nearest other lab', 24, GREEN, weight=700))
    assert all((b['from_baseline'] > b['to_nearest_other']) == (b['verdict'] == 'outside') for b in B), 'A13 says a batch is flagged when pink is above green'
    g.append(text(ax.x0 + 30, ax.y0 + 102, 'flagged when pink is above green', 20, INK2))
    return svg(760, 510, g, aria=f'Distance of each batch of lab 2 from its own first batch and to the nearest other lab; the nearest lab changes {len(runs) - 1} times.')


def embedding():
    return list(csv.DictReader(open('results/e2-embedding.csv')))


def map_axes(rows, x0, y0, w, h, pad=0.0):
    """Axes that hold the middle 99% of the wells. With pad, the limits widen by that share of the range on each side and wells beyond them are left out; without it they are clamped to the edge."""
    xs = sorted(float(r['pc1']) for r in rows); ys = sorted(float(r['pc2']) for r in rows)
    q = lambda v, p: v[int(p * (len(v) - 1))]
    lim = lambda v: (q(v, .005) - pad * (q(v, .995) - q(v, .005)), q(v, .995) + pad * (q(v, .995) - q(v, .005)))
    ax = Axes(x0, y0, w, h, lim(xs), lim(ys))
    keep = lambda p: not pad or (ax.xlim[0] <= float(p['pc1']) <= ax.xlim[1] and ax.ylim[0] <= float(p['pc2']) <= ax.ylim[1])
    clampx = lambda v: ax.X(min(max(v, ax.xlim[0]), ax.xlim[1]))
    clampy = lambda v: ax.Y(min(max(v, ax.ylim[0]), ax.ylim[1]))
    cloud = lambda pts, fill, r, extra='': (f'<g fill="{fill}" {extra}>' + ''.join(
        f'<circle cx="{clampx(float(p["pc1"])):.0f}" cy="{clampy(float(p["pc2"])):.0f}" r="{r}"/>' for p in pts if keep(p)) + '</g>')
    return ax, cloud


def field_map(B, lab, pca, one, both=True):
    """Untreated wells in the first two principal components, one shade of green per lab, and how far apart two labs' normals sit."""
    rows = embedding()
    first = set(B[0]['plates']) | set(B[1]['plates'])
    last = set(B[-1]['plates']) if both else set()
    others = sorted({r['lab'] for r in rows if r['lab'] != lab}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    ax, cloud = map_axes(rows, 20, 20, 1000, 568, pad=0.06)
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" rx="18" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::3], colour[l], 3.6, f'class="f" style="animation-delay:{0.15 + 0.09 * k:.2f}s"') for k, l in enumerate(others)]
    mine = [r for r in rows if r['lab'] == lab]
    late = f'class="f" style="animation-delay:{0.25 + 0.09 * len(others):.2f}s"'
    june = [r for r in mine if r['plate'] in first]
    g.append(cloud(june, PALE_PINK if both else PINK, 3.6 if both else 4.2, late))
    g.append(cloud([r for r in mine if r['plate'] in last], PINK, 4.2, late))
    xs = [ax.X(float(r['pc1'])) for r in june]; ys = [ax.Y(float(r['pc2'])) for r in june]
    month = date.fromisoformat(B[1]['date']).strftime('%B')
    g.append(f'<g {late}>' + text(min(xs) - 14, sum(ys) / len(ys) + 9, f'{lab_name(lab)} &#183; {month}', 26, PINK, 'end', 700) + '</g>')
    g.append(text(ax.x0 + 22, ax.y0 + ax.h - 18, 'PC 1 &#8594;', 20, MUTE))
    g.append(f'<g transform="translate({ax.x0 + 30},{ax.y0 + ax.h - 50}) rotate(-90)">{text(0, 0, "PC 2 &#8594;", 20, MUTE)}</g>')
    return svg(1040, 608, g, aria=f'Principal components of untreated wells, one shade of green per lab; each lab forms its own group; two labs&#8217; normals sit {one:.1f} within-plate spreads apart.')


def answer_chart(e10, lab):
    """Each batch: drift from its lab's baseline against agreement with its own first-batch drug answers."""
    pts = [dict(b, lab=l) for l, bs in e10['batches'].items() for b in bs if b['agree_own_baseline'] is not None]
    top = 2 * (int(max(p['drift'] for p in pts) / 2) + 1)
    ax = Axes(110, 64, 900, 440, (0, top), (0, 1))            # whole plot: x axis and titles
    main = Axes(110, 64, 900, 386, (0, top), (0.55, 1))       # batches whose known answer came out
    strip = Axes(110, 464, 900, 40, (0, top), (0, 0.25))      # the four whose positive controls failed
    g = ax.frame((), [(v, str(v)) for v in range(0, top + 1, 2)], '', 'drift from own baseline &#183; within-plate spreads', None)
    for v in (0.6, 0.7, 0.8, 0.9, 1):
        g.append(f'<path d="M {ax.x0} {main.Y(v):.1f} L {ax.x0 + ax.w} {main.Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>' + text(ax.x0 - 10, main.Y(v) + 7, f'{v:g}', 20, MUTE, 'end'))
    g.append(text(ax.x0 - 10, strip.y0 + 27, '&lt; 0.25', 20, MUTE, 'end'))
    g.append(f'<rect x="{ax.x0 - 3}" y="{main.y0 + main.h}" width="{ax.w + 3}" height="14" fill="{PAPER}"/>')
    g.append(f'<path d="M {ax.x0 - 8} {main.y0 + main.h + 4} l 16 -8 M {ax.x0 - 8} {main.y0 + main.h + 18} l 16 -8" stroke="{MUTE}" stroke-width="2.5" stroke-linecap="round"/>')
    g.append(f'<g transform="translate({ax.x0 - 62},{main.y0 + main.h / 2:.1f}) rotate(-90)">{text(0, 0, "agreement with own first answer", 22, INK2, "middle")}</g>')
    dot = lambda p, fill, r, extra='': f'<circle cx="{ax.X(p["drift"]):.1f}" cy="{main.Y(p["agree_own_baseline"]):.1f}" r="{r}" fill="{fill}" {extra}/>'
    failed = [p for p in pts if p['positive_controls_failed']]
    g.append('<g class="f" style="animation-delay:0.2s">' + ''.join(dot(p, '#8fbfae', 6) for p in pts if p['lab'] != lab and not p['positive_controls_failed']) + '</g>')
    g += [f'<path d="M {ax.X(p["drift"]) - 6:.1f} {strip.Y(p["agree_own_baseline"]) - 6:.1f} l 12 12 m 0 -12 l -12 12" stroke="{MUTE}" stroke-width="2.5" stroke-linecap="round"/>' for p in failed]
    g.append('<g class="f" style="animation-delay:0.7s">' + ''.join(dot(p, PINK, 9, f'stroke="{PANEL}" stroke-width="2"') for p in pts if p['lab'] == lab) + '</g>')
    out = [p for p in pts if p['lab'] == lab and p['outside']]
    g.append('<g class="f" style="animation-delay:1.2s">' + ''.join(f'<circle cx="{ax.X(p["drift"]):.1f}" cy="{main.Y(p["agree_own_baseline"]):.1f}" r="15" fill="none" stroke="{PINK}" stroke-width="2"/>' for p in out) + '</g>')
    cx, cy = sum(ax.X(p['drift']) for p in out) / len(out), min(main.Y(p['agree_own_baseline']) for p in out)
    when = lambda p: short_date(f'{p["batch"][:4]}-{p["batch"][4:6]}-{p["batch"][6:8]}')
    g.append(f'<g class="f" style="animation-delay:1.2s">{text(cx, cy - 50, f"{lab_name(lab)} &#183; {when(out[0])} to {when(out[-1])}", 22, PINK, "middle", 700)}</g>')
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    return svg(1040, 608, g, aria=f'Drift from baseline against agreement of drug answers for every batch of every lab; agreement falls as drift rises (Spearman &#8722;{abs(a["spearman"]):.2f}); the {NUMBERS[len(failed)]} batches whose known answer failed sit below 0.25.')


def density_chart(e13):
    """The field's reference tightens as labs join: distance between two references built from m labs each."""
    ref = e13['field_reference_by_labs']; ms = sorted(int(k) for k in ref)
    top = 2 * (int(max(v['p90'] for v in ref.values()) / 2) + 1)
    ax = Axes(110, 64, 900, 376, (0.5, 11.5), (0, top))
    g = ax.frame(range(0, top + 1, 2), [(m, str(m)) for m in range(1, 12)], 'error in &#8220;normal&#8221;, in within-plate spreads', 'labs on the map')
    one = ref[str(ms[0])]['mean']
    pts = [(ax.X(x), ax.Y(one / x ** 0.5)) for x in (1 + k * 0.1 for k in range(101))]
    seg = lambda p: ' '.join(f'{"M" if i == 0 else "L"} {x:.1f} {y:.1f}' for i, (x, y) in enumerate(p))
    g.append(f'<path d="{seg(pts[:41])}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 7" opacity=".7"/>')
    g.append(f'<path d="{seg(pts[40:])}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 7" opacity=".25"/>')
    for m in ms:
        v = ref[str(m)]
        g.append(f'<path d="M {ax.X(m):.1f} {ax.Y(v["p10"]):.1f} L {ax.X(m):.1f} {ax.Y(v["p90"]):.1f}" stroke="{GREEN}" stroke-width="3" opacity=".4"/>')
        g.append(f'<circle class="f" style="animation-delay:{0.2 + 0.15 * m:.2f}s" cx="{ax.X(m):.1f}" cy="{ax.Y(v["mean"]):.1f}" r="10" fill="{GREEN}"/>')
        if m in (ms[0], ms[-1]):
            g.append(text(ax.X(m) + 16, ax.Y(v['mean']) - 12, f'{v["mean"]:.1f}', 22, GREEN, weight=700))
    n = e13['n_labs']
    g.append(f'<path d="M {ax.X(n):.1f} {ax.y0 + ax.h} L {ax.X(n):.1f} {ax.y0 + ax.h - 36}" stroke="{INK2}" stroke-width="2"/>' + text(ax.X(n) - 10, ax.y0 + ax.h - 14, 'today', 22, INK2, 'end'))
    g.append(text(ax.X(8), ax.Y(one / 8 ** 0.5) - 16, '1/&#8730;n', 26, GREEN, 'middle', extra=f'style="{MATH}" opacity=".8"'))
    a, b = ref[str(ms[0])]['mean'], ref[str(ms[-1])]['mean']
    return svg(1040, 530, g, fit=True, aria=f'The error in normal, measured as the distance between two maps built from different labs, falls from {a:.1f} spreads with {NUMBERS[ms[0]]} lab to {b:.1f} with {NUMBERS[ms[-1]]}.')


NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven']


def frame_chart(e12):
    """Agreement with every other lab on the same drugs, per lab: as measured, on its own controls, in the field's frame."""
    labs = sorted(e12['by_lab'], key=lab_number)
    cols = [('raw', 'as', 'measured', 140), ('own', 'on its own', 'controls', 450), ('field', 'in the field&#8217;s', 'frame', 760)]
    ax = Axes(110, 64, 900, 376, (0, 1), (0.5, 0.9))
    g = [text(ax.x0, ax.y0 - 28, 'AGREEMENT WITH EVERY OTHER LAB, ON THE SAME DRUGS', 22, MUTE, extra='letter-spacing="2.2"'),
         f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0.5, 0.6, 0.7, 0.8, 0.9):
        g.append(f'<path d="M {ax.x0} {ax.Y(v):.1f} L {ax.x0 + ax.w} {ax.Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>' + text(ax.x0 - 10, ax.Y(v) + 7, f'{v:g}', 20, MUTE, 'end'))
    for key, l1, l2, x in cols:
        g.append(text(ax.x0 + x, ax.y0 + ax.h + 32, l1, 21, INK2, 'middle') + text(ax.x0 + x, ax.y0 + ax.h + 58, l2, 21, PINK if key == 'field' else INK2, 'middle', 700 if key == 'field' else 400))
    for k, lab in enumerate(labs):
        v = e12['by_lab'][lab]['agree_field']
        pts = [(ax.x0 + x, ax.Y(v[key])) for key, _, _, x in cols]
        own = lab == 'source_2'
        colour = PINK if own else '#5fae94'
        g.append(f'<path class="f" style="animation-delay:{0.2 + 0.06 * k:.2f}s" d="M {pts[0][0]} {pts[0][1]:.1f} L {pts[1][0]} {pts[1][1]:.1f} L {pts[2][0]} {pts[2][1]:.1f}" fill="none" stroke="{colour}" stroke-width="{3.6 if own else 2.4}" opacity="{1 if own else .75}"/>')
        g += [f'<circle cx="{x}" cy="{y:.1f}" r="{7 if own else 5}" fill="{colour}"/>' for x, y in pts]
    g.append(f'<g transform="translate({ax.x0 - 62},{ax.y0 + ax.h / 2:.1f}) rotate(-90)">{text(0, 0, "agreement (cosine)", 22, INK2, "middle")}</g>')
    a = e12['every_batch']['agree_field']
    rx = 1080
    g.append(text(rx, ax.y0 - 28, 'every lab moves up', 22, MUTE, extra='letter-spacing="2.2"'))
    g.append(text(rx, ax.y0 + 74, f'{a["raw"]:.2f} &#8594; {a["field"]:.2f}', 72, PINK, weight=700))
    for k, line in enumerate(('same drugs, closer answers:', f'higher in {a["field_better_in"]} batches', f'{e12["n_labs"]} lines, one per lab')):
        g.append(text(rx, ax.y0 + 116 + 30 * k, line, 24 if k < 2 else 20, INK2 if k < 2 else FAINT))
    g.append(text(rx, ax.y0 + 300, 'against its own controls', 22, GREEN, weight=700))
    g.append(text(rx, ax.y0 + 340, f'{a["own"]:.2f} &#8594; {a["field"]:.2f}', 40, INK2, weight=700))
    g.append(text(rx, ax.y0 + 372, f'higher in {a["field_better_than_own_in"]} batches', 20, INK2))
    return svg(1600, 530, g, aria='Agreement between labs on the effect of the same drugs, per lab: as measured, normalised to its own controls, and moved into the field\'s frame. It is highest in the field\'s frame for ten of eleven labs.')


def build():
    lab = 'source_2'
    R = results('e9-replay.json')['labs'][lab]; B = R['batches']
    e10 = results('e10-certificate-predicts-answer.json'); e13 = results('e13-baseline-density.json')
    pca = results('e2-plate-position-1053600681.json')['pca']
    e1 = results('e1.json')['all_sources']
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    one = e13['field_reference_by_labs']['1']['mean']

    css = BASE_CSS + '''
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1 { opacity: 1; pointer-events: auto; }
    .flow .s .f, .flow .s .r, .flow .s .bar { animation-play-state: paused; }
    .step-0 .s0 .f, .step-1 .s1 .f, .step-0 .s0 .r, .step-1 .s1 .r { animation-play-state: running; }
    .flow { cursor: pointer; }
'''
    H = (f'position:absolute; left:56px; top:86px; width:900px; margin:0; {SANS} font-size:44px; font-weight:600; '
         f'letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};')
    FOOT = f'position:absolute; left:56px; bottom:44px; width:1010px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    fig = lambda n: f'<span style="color:{D_TEXT}; font-weight:500;">fig {n}</span>'
    card = lambda inner: (f'<div style="position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} padding:0 18px; overflow:hidden;">'
                          f'<div style="position:relative; width:100%; height:100%;">{inner}</div></div>')
    layer = lambda k, inner: f'<div class="s s{k}" style="position:absolute; inset:0; display:flex; align-items:center;">{inner}</div>'
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">The map</span>'
    n_labs = NUMBERS[e13['n_labs']].capitalize()
    two = e10['flagged_against_unflagged'][lab]['with_own_baseline']
    mine = e10['batches'][lab]; out = [b for b in mine if b['outside']]; calm = sorted(b['drift'] for b in mine if not b['outside'])
    usual = (calm[len(calm) // 2 - 1] + calm[len(calm) // 2]) / 2 if len(calm) % 2 == 0 else calm[len(calm) // 2]
    times = (min(b['drift'] for b in out) / usual, max(b['drift'] for b in out) / usual)
    when = lambda b: short_date(f'{b["batch"][:4]}-{b["batch"][4:6]}-{b["batch"][6:8]}')
    big = lambda v, c, size=64: f'<span style="{SANS} font-size:{size}px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{c};">{v}</span>'
    small = lambda v, c=D_SOFT: f'<span style="{MONO} font-size:13px; line-height:1.5; color:{c};">{v}</span>'
    side = lambda k, inner: (f'<div class="s s{k}" style="position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; '
                             f'display:flex; flex-direction:column; gap:14px;">{inner}</div>')
    bar = lambda w, c, name: (f'<div style="display:flex; align-items:center; gap:12px;"><span style="display:block; width:{w:.0f}px; height:12px; border-radius:3px; background:{c};"></span>'
                              f'<span style="{SANS} font-size:16px; color:{D_SOFT};">{name}</span></div>')
    rule = '<div style="height:1px; background:rgba(246,247,247,.18); margin:6px 0;"></div>'
    right_a = side(0, label('between labs', D_GREEN) + big(f'{one:.1f}', D_GREEN, 72)
                   + bar(one * 30, D_GREEN, 'lab to lab') + bar(30, '#6b7377', 'inside one plate')
                   + small(f'labs sit {one:.1f}&#215; farther apart<br>than wells on one plate'))
    right_b = side(1, label('inside labs', D_GREEN) + big(f'&#961; = &#8722;{abs(a["spearman"]):.2f}', D_GREEN)
                   + small('more drift &#183; less agreement') + rule
                   + label(f'{lab_name(lab)} &#183; you &#183; {when(out[0])} to {when(out[-1])}', D_PINK)
                   + f'<span style="{SANS} font-size:18px; line-height:1.35; color:{D_TEXT};">drifted {times[0]:.0f}&#8211;{times[1]:.0f}&#215; its summer level</span>'
                   + '<div style="display:flex; align-items:baseline; gap:10px;">' + big('%.2f' % two['unflagged'], D_DIM, 48)
                   + f'<span style="{SANS} font-size:30px; color:{D_DIM};">&#8594;</span>' + big('%.2f' % two['flagged'], D_PINK, 48) + '</div>'
                   + small('same drugs, matched against its own June answers'))
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(4, dark=True)}
  {header('04', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">{n_labs} labs.<br><span style="color:{D_PINK};">{n_labs} &#8220;normals.&#8221;</span></h2>
  <h2 class="s s1" style="{H}">Where you sit <span style="color:{D_PINK};">predicts what you measure.</span></h2>
  {card(layer(0, field_map(B, lab, pca, one, both=False)) + layer(1, answer_chart(e10, lab)))}
  {right_a}{right_b}
  <div class="s s0" style="{FOOT}">{fig(2)} {pca["wells"]:,} untreated wells &#183; PCA of {e1["n_features"]:,} numbers &#183; JUMP [7]</div>
  <div class="s s1" style="{FOOT}">{fig(3)} {a["n_batches"]} batches &#183; {a["n_labs"]} labs &#183; JUMP [7] &#183; A8, A13</div>
  {cue(2, dark=True)}
</div>'''
    steps = {'tag': ['The map', 'The map']}
    return css, body, steps
