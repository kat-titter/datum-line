"""Slide 04: the map, in two views. Written whole from results/e2 and e10.

The density chart is slide 06 (slide06.py); the frame chart is board A14; the two charts of one lab
over time are board A13. All are kept here because they share the axes and the map."""
import csv
import random
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
    g = ax.frame(range(0, top + 1, 4), months, 'distance (higher = further apart)', '', 'compared with other labs')
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
    june = [r for r in mine if r['plate'] in first and r['target'] != 'True']        # 8 wells a plate, as e2 kept for every plate;
    june = (june + random.Random(0).sample([r for r in mine if r['target'] == 'True'], pca['wells_per_plate']))[::3]   # the all-well plate cut to 8 at random, as e2 cut the rest; then one in three, as for every lab
    g.append(cloud(june, PALE_PINK if both else PINK, 3.6 if both else 4.2, late))
    g.append(cloud([r for r in mine if r['plate'] in last], PINK, 4.2, late))
    xs = [ax.X(float(r['pc1'])) for r in june]; ys = [ax.Y(float(r['pc2'])) for r in june]
    month = date.fromisoformat(B[1]['date']).strftime('%B')
    g.append(f'<g {late}>' + text(min(xs) - 14, sum(ys) / len(ys) + 9, f'{lab_name(lab)}, {month}', 28, PINK, 'end', 700) + '</g>')
    # what one mark is (25 Oct: "one point = one lab centroid? should be more clear"): one dot is one well, each lab a shade
    kx, ky = ax.x0 + ax.w - 330, ax.y0 + 14                      # top right, the one corner the wells leave clear
    shades = ''.join(f'<circle cx="{kx + 26 + 13 * k}" cy="{ky + 52}" r="5.5" fill="{colour[l]}"/>' for k, l in enumerate(others[::2][:5]))
    g.append(f'<g class="f" style="animation-delay:1.2s"><rect x="{kx}" y="{ky}" width="314" height="76" rx="12" fill="{PANEL}" opacity="0.94"/>'
             f'<circle cx="{kx + 26}" cy="{ky + 22}" r="5.5" fill="{colour[others[len(others) // 2]]}"/>' + text(kx + 44, ky + 31, 'one well', 27, INK2)
             + shades + text(kx + 100, ky + 62, 'one shade per lab', 27, INK2) + '</g>')
    g.append(text(ax.x0 + 22, ax.y0 + ax.h - 18, 'PC 1 &#8594;', 20, MUTE, extra='class="pdf"'))
    g.append(f'<g class="pdf" transform="translate({ax.x0 + 30},{ax.y0 + ax.h - 50}) rotate(-90)">{text(0, 0, "PC 2 &#8594;", 20, MUTE)}</g>')
    return svg(1040, 608, g, aria=f'Principal components of untreated wells, one shade of green per lab; each lab forms its own group; two labs&#8217; normals sit {one:.1f} within-plate spreads apart.')


def trajectory_chart(e10, lab):
    """04b: one lab through time. Top, its controls' drift from its first batch; below, how well its drug answers still match
    that first batch; one date axis, so the batches the controls flagged line up with the answers that moved.
    25 Oct 2026: "show trajectory through time more clearly ... how does this predict what is measured?" """
    bs = sorted(e10['batches'][lab], key=lambda b: b['batch'][:8])
    when = lambda b: date(int(b['batch'][:4]), int(b['batch'][4:6]), int(b['batch'][6:8]))
    first, last = when(bs[0]), when(bs[-1])
    lo, hi = date(first.year, first.month, 1), date.fromordinal(last.toordinal() + 12)       # the axis ends just after the last batch
    X = lambda d: 130 + (d - lo).days / (hi - lo).days * 860
    top = Axes(130, 78, 860, 170, (0, 1), (0, 14))
    low = Axes(130, 362, 860, 160, (0, 1), (0.6, 1))
    flagged = [b for b in bs if b['outside']]
    assert flagged == bs[-len(flagged):], 'the flagged batches are the last ones'
    x0, x1 = X(when(flagged[0])) - 18, X(when(flagged[-1])) + 18
    g = [f'<rect x="{x0:.1f}" y="62" width="{x1 - x0:.1f}" height="{low.y0 + low.h - 62 + 4}" rx="12" fill="{PINK}" opacity="0.08"/>']
    for ax, ticks, fmt in ((top, (0, 5, 10), lambda v: f'{v:g}'), (low, (0.6, 0.8, 1), lambda v: f'{v:g}')):
        g += [f'<path d="M {ax.x0} {ax.Y(v):.1f} L {ax.x0 + ax.w} {ax.Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>' + text(ax.x0 - 12, ax.Y(v) + 9, fmt(v), 27, MUTE, 'end') for v in ticks]
    m = date(lo.year, lo.month, 1)
    while m < hi:
        g.append(text(X(m) + 4, low.y0 + low.h + 40, m.strftime('%b'), 27, MUTE) + f'<path d="M {X(m):.1f} {low.y0 + low.h} l 0 10" stroke="{MUTE}" stroke-width="2"/>')
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    g.append(f'<path d="M {low.x0} {low.y0 + low.h} L {low.x0 + low.w} {low.y0 + low.h}" stroke="{MUTE}" stroke-width="2"/>')
    head = lambda y, ic, words, note: (f'<g transform="translate({top.x0 - 4},{y - 25})">{icon(ic, INK2, 30)}</g>'
                                      + text(top.x0 + 36, y, words, 27, INK, weight=600) + note)
    g.append(head(46, 'well', 'controls: drift from first batch', ''))
    g.append(head(304, 'drug', 'drug answers: match with first batch (1 = perfect)', ''))
    g.append(text(x0 - 14, 104, 'flagged from controls alone', 27, PINK, 'end', 700))
    line = lambda ax, key, pts: ('<path d="M ' + ' L '.join(f'{X(when(b)):.1f} {ax.Y(b[key]):.1f}' for b in pts)
                                 + f'" fill="none" stroke="{PINK}" stroke-width="3" stroke-linejoin="round" opacity="0.45"/>')
    dot = lambda ax, key, b: (f'<circle cx="{X(when(b)):.1f}" cy="{ax.Y(b[key]):.1f}" r="9" fill="{PINK}" stroke="{PANEL}" stroke-width="2"/>'
                              + (f'<circle cx="{X(when(b)):.1f}" cy="{ax.Y(b[key]):.1f}" r="16" fill="none" stroke="{PINK}" stroke-width="2.5"/>' if b['outside'] else ''))
    answered = [b for b in bs if b['agree_own_baseline'] is not None]
    two = e10['flagged_against_unflagged'][lab]['with_own_baseline']; calm = [b for b in answered if not b['outside']]
    assert abs(sum(b['agree_own_baseline'] for b in calm) / len(calm) - two['unflagged']) < 0.001, 'the dashed line is the 0.85 beside the chart'
    mean = lambda xa, xb, v, c: f'<path d="M {xa:.1f} {low.Y(v):.1f} L {xb:.1f} {low.Y(v):.1f}" stroke="{c}" stroke-width="3" stroke-dasharray="9 7" stroke-linecap="round"/>'
    g.append('<g class="f" style="animation-delay:0.3s">' + line(top, 'drift', bs) + ''.join(dot(top, 'drift', b) for b in bs) + '</g>')
    g.append('<g class="f" style="animation-delay:0.8s">' + line(low, 'agree_own_baseline', answered) + ''.join(dot(low, 'agree_own_baseline', b) for b in answered)
             + f'<circle cx="{X(first):.1f}" cy="{low.Y(1):.1f}" r="9" fill="{PANEL}" stroke="{PINK}" stroke-width="3"/>'
             + text(X(first) + 18, low.Y(1) - 14, 'first batch', 27, MUTE) + '</g>')
    g.append('<g class="f" style="animation-delay:1.2s">' + mean(X(when(calm[0])), X(when(calm[-1])), two['unflagged'], MUTE) + mean(x0 + 8, x1 - 8, two['flagged'], PINK) + '</g>')
    return svg(1040, 608, g, aria=f'{lab_name(lab)}, batch by batch from {first:%B} to {last:%B}: when its control wells drift, its drug answers stop matching its first batch; '
               f'the {NUMBERS[len(flagged)]} batches its controls flagged are the ones whose answers moved most.')


def answer_chart(e10, lab):
    """Each batch: drift from its lab's baseline against agreement with its own first-batch drug answers."""
    pts = [dict(b, lab=l) for l, bs in e10['batches'].items() for b in bs if b['agree_own_baseline'] is not None]
    top = 2 * (int(max(p['drift'] for p in pts) / 2) + 1)
    ax = Axes(110, 64, 900, 440, (0, top), (0, 1))            # whole plot: x axis and titles
    main = Axes(110, 64, 900, 386, (0, top), (0.55, 1))       # batches whose known answer came out
    strip = Axes(110, 464, 900, 40, (0, top), (0, 0.25))      # the four whose positive controls failed
    g = ax.frame((), [(v, str(v)) for v in range(0, top + 1, 2)], '', 'drift from its first batch &#8594;', None, room=True)
    for v in (0.6, 0.7, 0.8, 0.9, 1):
        g.append(f'<path d="M {ax.x0} {main.Y(v):.1f} L {ax.x0 + ax.w} {main.Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>' + text(ax.x0 - 10, main.Y(v) + 9, f'{v:g}', 26, MUTE, 'end'))
    g.append(text(ax.x0 - 10, strip.y0 + 29, '&lt; 0.25', 24, MUTE, 'end'))
    g.append(f'<rect x="{ax.x0 - 3}" y="{main.y0 + main.h}" width="{ax.w + 3}" height="14" fill="{PAPER}"/>')
    g.append(f'<path d="M {ax.x0 - 8} {main.y0 + main.h + 4} l 16 -8 M {ax.x0 - 8} {main.y0 + main.h + 18} l 16 -8" stroke="{MUTE}" stroke-width="2.5" stroke-linecap="round"/>')
    g.append(f'<g transform="translate({ax.x0 - 62},{main.y0 + main.h / 2 - 16:.1f}) rotate(-90)">{text(0, 0, "agreement with first batch (1 = perfect)", 26, INK2, "middle")}</g>')
    dot = lambda p, fill, r, extra='': f'<circle cx="{ax.X(p["drift"]):.1f}" cy="{main.Y(p["agree_own_baseline"]):.1f}" r="{r}" fill="{fill}" {extra}/>'
    failed = [p for p in pts if p['positive_controls_failed']]
    g.append('<g class="f" style="animation-delay:0.2s">' + ''.join(dot(p, '#8fbfae', 6) for p in pts if p['lab'] != lab and not p['positive_controls_failed']) + '</g>')
    g += [f'<path d="M {ax.X(p["drift"]) - 6:.1f} {strip.Y(p["agree_own_baseline"]) - 6:.1f} l 12 12 m 0 -12 l -12 12" stroke="{MUTE}" stroke-width="2.5" stroke-linecap="round"/>' for p in failed]
    g.append('<g class="f" style="animation-delay:0.7s">' + ''.join(dot(p, PINK, 9, f'stroke="{PANEL}" stroke-width="2"') for p in pts if p['lab'] == lab) + '</g>')
    out = [p for p in pts if p['lab'] == lab and p['outside']]
    g.append('<g class="f" style="animation-delay:1.2s">' + ''.join(f'<circle cx="{ax.X(p["drift"]):.1f}" cy="{main.Y(p["agree_own_baseline"]):.1f}" r="15" fill="none" stroke="{PINK}" stroke-width="2"/>' for p in out) + '</g>')
    cx, cy = sum(ax.X(p['drift']) for p in out) / len(out), min(main.Y(p['agree_own_baseline']) for p in out)
    when = lambda p: short_date(f'{p["batch"][:4]}-{p["batch"][4:6]}-{p["batch"][6:8]}')
    last = max(out, key=lambda p: p['drift'])                 # the label sits over the far ring, clear of lab 2's summer dots
    g.append(f'<g class="f" style="animation-delay:1.2s">{text(ax.X(last["drift"]) + 15, main.Y(last["agree_own_baseline"]) - 30, f"{lab_name(lab)}, autumn", 28, PINK, "end", 700)}</g>')
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    return svg(1040, 608, g, aria=f'Drift from baseline against agreement of drug answers for every batch of every lab; agreement falls as drift rises (Spearman &#8722;{abs(a["spearman"]):.2f}); the {NUMBERS[len(failed)]} batches whose known answer failed sit below 0.25.')


def density_chart(e13):
    """The field's reference tightens as labs join: distance between two references built from m labs each."""
    ref = e13['field_reference_by_labs']; ms = sorted(int(k) for k in ref)
    top = 2 * (int(max(v['p90'] for v in ref.values()) / 2) + 1)
    ax = Axes(110, 64, 900, 376, (0.5, 11.5), (0, top))
    g = ax.frame(range(0, top + 1, 2), [(m, str(m)) for m in range(1, 12, 2)], 'error in &#8220;normal&#8221; (lower is better)', 'labs on the map', room=True)
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
            g.append(text(ax.X(m) + 16, ax.Y(v['mean']) - 12, f'{v["mean"]:.1f}', 28, GREEN, weight=700))
    n = e13['n_labs']
    g.append(text(ax.X(3), ax.Y(ref['3']['p90']) - 16, 'measured', 26, GREEN, 'middle', 600))       # the dots, named where they are, as 'expected' names the dashes
    g.append(f'<path d="M {ax.X(n):.1f} {ax.y0 + ax.h} L {ax.X(n):.1f} {ax.y0 + ax.h - 36}" stroke="{INK2}" stroke-width="2"/>' + text(ax.X(n) - 10, ax.y0 + ax.h - 14, 'labs today', 26, INK2, 'end'))
    g.append(text(ax.X(8), ax.Y(one / 8 ** 0.5) - 18, 'expected', 26, GREEN, 'middle', extra='opacity=".8"'))       # measured to five labs; beyond, the curve
    g.append(text(ax.X(8), ax.Y(one / 8 ** 0.5) - 50, '1/&#8730;n', 24, GREEN, 'middle', extra=f'class="pdf" style="{MATH}" opacity=".8"'))
    a, b = ref[str(ms[0])]['mean'], ref[str(ms[-1])]['mean']
    return svg(1010, 530, g, fit=True, aria=f'The error in normal, measured as the distance between two maps built from different labs, falls from {a:.1f} spreads with {NUMBERS[ms[0]]} lab to {b:.1f} with {NUMBERS[ms[-1]]}.')


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
    seen = [b for b in e10['batches'][lab] if b['agree_own_baseline'] is not None]
    day = lambda b: short_date(f'{b["batch"][:4]}-{b["batch"][4:6]}-{b["batch"][6:8]}')
    span = lambda flagged: (lambda bs: f'{day(bs[0])} to {day(bs[-1])}')(sorted((b for b in seen if b['outside'] == flagged), key=lambda b: b['batch']))
    assert sum(not b['outside'] for b in seen) == two['n_unflagged'] and sum(b['outside'] for b in seen) == two['n_flagged'], 'the seasons count the same batches as e10'
    mine = e10['batches'][lab]; out = [b for b in mine if b['outside']]; calm = sorted(b['drift'] for b in mine if not b['outside'])
    usual = (calm[len(calm) // 2 - 1] + calm[len(calm) // 2]) / 2 if len(calm) % 2 == 0 else calm[len(calm) // 2]
    times = (min(b['drift'] for b in out) / usual, max(b['drift'] for b in out) / usual)
    when = lambda b: short_date(f'{b["batch"][:4]}-{b["batch"][4:6]}-{b["batch"][6:8]}')
    big = lambda v, c, size=64: f'<span style="{SANS} font-size:{size}px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{c};">{v}</span>'
    small = lambda v, c=D_SOFT: f'<span style="{MONO} font-size:13px; line-height:1.5; color:{c};">{v}</span>'
    side = lambda k, inner: (f'<div class="s s{k}" style="position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; '
                             f'display:flex; flex-direction:column; gap:14px;">{inner}</div>')
    bar = lambda w, c, name, ic: (f'<div style="display:flex; align-items:center; gap:10px;"><span style="display:block; width:{w:.0f}px; height:12px; border-radius:3px; background:{c}; flex-shrink:0;"></span>'
                                  f'{icon(ic, D_SOFT, 20)}<span style="{SANS} font-size:18px; color:{D_SOFT};">{name}</span></div>')
    gloss = lambda ic, word, what: (f'<span style="display:flex; align-items:center; gap:8px;">{icon(ic, D_SOFT, 22)}<span style="{SANS} font-size:15px; line-height:1.2; color:{D_SOFT};">'
                                    f'<span style="color:{D_TEXT}; font-weight:600;">{word}</span><br>{what}</span></span>')
    glossary = (f'<div style="margin-top:auto; display:flex; justify-content:space-between; gap:10px; padding-top:8px; border-top:1px solid rgba(246,247,247,.18);">'
                + gloss('well', 'well', 'one dish of cells') + gloss('plate', 'plate', 'grid of wells') + gloss('lab', 'lab', 'one site') + '</div>')
    rule = '<div style="height:1px; background:rgba(246,247,247,.18); margin:6px 0;"></div>'
    dash = lambda c: f'<span style="display:inline-block; width:20px; border-top:3px dashed {c}; vertical-align:middle; margin-right:7px;"></span>'      # the key to the dashed means in the chart
    say = lambda v, c=D_TEXT, size=20: f'<span style="{SANS} font-size:{size}px; line-height:1.35; color:{c};">{v}</span>'
    import base64
    well = 'data:image/png;base64,' + base64.b64encode(open('figures/assets/box-you.png', 'rb').read()).decode()
    arrow = f'<span aria-hidden="true" style="{SANS} font-size:22px; color:{D_DIM};">&#8594;</span>'
    pair = lambda a, b='': (f'<span style="display:flex; flex-direction:column; {SANS} font-size:18px; line-height:1.15; color:{D_SOFT};"><span style="color:{D_TEXT};">{a}</span>'
                            + (f'<span style="font-size:14px; color:{D_DIM};">{b}</span>' if b else '') + '</span>')
    strip = (f'<div style="display:flex; align-items:center; gap:8px;">'
             f'<img src="{well}" alt="One control well of lab 2." style="width:40px; height:40px; border-radius:8px; object-fit:cover; background:#000; outline:2px solid {D_PINK}; outline-offset:-2px; flex-shrink:0;">'
             + pair('one well') + arrow + icon('measure', D_SOFT, 26)
             + pair(f'{e1["n_features"]:,} measurements') + arrow
             + f'<span style="display:inline-block; width:14px; height:14px; border-radius:50%; background:{D_PINK}; flex-shrink:0;"></span>'
             + pair('one point') + '</div>')      # the pipeline, since slide 03's third view folded in here: software measures each image, the numbers place it
    kinds = lambda ic: f'<span style="display:flex; align-items:center; gap:5px;">{icon(ic, D_SOFT, 20)}<span style="{SANS} font-size:18px; color:{D_SOFT};">{ic}</span></span>'
    what = (f'<div style="display:flex; justify-content:space-between; margin-top:-6px; padding-bottom:10px; border-bottom:1px solid rgba(246,247,247,.18);">'
            + ''.join(kinds(ic) for ic in ('size', 'shape', 'brightness', 'texture')) + '</div>')      # what the measurements are, a glyph each (Kat, 25 Oct: the four words stay)
    right_a = side(0, strip + what
                   + f'<div style="display:flex; align-items:baseline; gap:14px; margin-top:auto;">{big(f"{round(one)}&#215;", D_GREEN, 88)}{say("further apart", D_TEXT, 24)}</div>'
                   + bar(one * 30, D_GREEN, 'lab to lab', 'lab') + bar(30, '#6b7377', 'spread inside one plate', 'plate')
                   + pdf(small(f'{one:.1f}: the mean distance between two labs&#8217; centres, in units of a well&#8217;s mean distance from its own plate&#8217;s centre; all {e13["n_features"]:,} numbers (results/e13)')) + glossary)
    right_b = side(1, f'<span style="{SANS} font-size:20px; font-weight:700; color:{D_PINK};">Lab 2</span>'
                   + pdf(say('By autumn it had drifted.') + ' ' + small(f'From {when(out[0])} to {when(out[-1])}, {times[0]:.0f}&#8211;{times[1]:.0f}&#215; its summer level (results/e10).'))

                   + '<div style="display:grid; grid-template-columns:auto auto auto auto; justify-content:start; align-items:baseline; column-gap:10px; row-gap:4px;">'
                   + f'<span style="align-self:center;">{icon("drug", D_SOFT, 30)}</span>'
                   + big('%.2f' % two['unflagged'], D_DIM, 56) + f'<span style="{SANS} font-size:32px; color:{D_DIM};">&#8594;</span>' + big('%.2f' % two['flagged'], D_PINK, 56)
                   + '<span></span>' + say(dash(D_DIM) + 'before', D_SOFT, 18) + '<span></span>' + say(dash(D_PINK) + 'flagged', D_SOFT, 18) + '</div>'
                   + pdf(small(f'match with the first batch: {NUMBERS[two["n_unflagged"]]} batches {span(False)}, {NUMBERS[two["n_flagged"]]} flagged {span(True)}'))
                   + f'<div style="display:flex; align-items:center; gap:10px; margin-top:auto;">{icon("well", D_TEXT, 28)}'
                     f'<span style="{SANS} font-size:18px; line-height:1.2; color:{D_TEXT};">controls<br>drift</span>{arrow}{icon("drug", D_TEXT, 28)}'
                     f'<span style="{SANS} font-size:18px; line-height:1.2; color:{D_TEXT};">drug answers<br>shift</span></div>'
                   + f'<div style="display:flex; align-items:flex-start; gap:10px; margin-bottom:auto;">{icon("lab", D_SOFT, 24)}' + say(f'across {NUMBERS[a["n_labs"]]} labs' + pdf(f': &#961; = &#8722;{abs(a["spearman"]):.2f}, {a["n_batches"]} batches, each lab centred (e10, A6)'), D_SOFT, 18) + '</div>'
                   + f'<span style="display:flex; align-items:center; gap:8px; margin-top:18px; padding-top:12px; border-top:1px solid rgba(246,247,247,.18); {SANS} font-size:15px; color:{D_SOFT};">{icon("batch", D_SOFT, 22)}<span><span style="color:{D_TEXT}; font-weight:600;">batch</span>: one run of plates</span></span>')
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(4, dark=True)}
  {header('04', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">{n_labs} labs.<br><span style="color:{D_GREEN};">{n_labs} &#8220;normals&#8221;.</span></h2>
  <h2 class="s s1" style="{H}">Controls alone flagged the batches<br><span style="color:{D_GREEN};">whose drug results shifted.</span></h2>
  {card(layer(0, field_map(B, lab, pca, one, both=False)) + layer(1, trajectory_chart(e10, lab)))}
  {right_a}{right_b}
  <div class="s s0 pdfv" style="{FOOT}">{fig(2)} dots: DMSO wells, {pca["wells_per_plate"]} per plate, one in three drawn; PCA of {pca["wells"]:,} wells, for the eye (distances use all {e1["n_features"]:,} numbers); plates: 384 wells, 1,536 in labs 1 and 9; strip: a lab 2 DMSO well, Hoechst, DNA; JUMP [7]; A2, A3, A13</div>
  <div class="s s1 pdfv" style="{FOOT}">{fig(3)} {lab_name(lab)}, {len(e10["batches"][lab])} batches; drift: control wells&#8217; distance from the first batch, in within-plate spreads; match: seven known drugs, 5 &#181;M; dashed: means; flagged: most plates nearer another lab than the first batch (e9); A6; JUMP [7]</div>
  {cue(2, dark=True)}
</div>'''
    steps = {'tag': ['The map', 'The map']}
    return css, body, steps
