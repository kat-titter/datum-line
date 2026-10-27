"""Slide 04: the map, then the problem and the proof, in three views (05b folded in on 26 Oct 2026). Written whole from results/e2 and e10.

The density chart is slide 06 (slide06.py); the frame chart is board A14; the two charts of one lab
over time are board A13. All are kept here because they share the axes and the map."""
import csv
import random
import statistics
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


CARD_W = 1132      # px: the dark slides' figure cards, inside their 18-px padding


def field_map(B, lab, pca, one, both=True, now=None, side=None, width=1040):
    """Untreated wells in the first two principal components, one shade of green per lab, and how far apart two labs' normals sit.
    side (26 Oct, Kat: "cut the side panels"): a function drawing into the figure's own right part, past the map, given where the
    new batch lands; width is then the whole figure's."""
    px = lambda p: round(p * width / CARD_W, 1)      # 26 Oct (Kat: "font types are too varied in size"): text in px on stage
    rows = embedding()
    first = set(B[0]['plates']) | set(B[1]['plates'])
    last = set(B[-1]['plates']) if both else set()
    others = sorted({r['lab'] for r in rows if r['lab'] != lab}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    ax, cloud = map_axes(rows, 20, 20, 1000, 466, pad=0.06)          # 26 Oct: two key rows under the plot
    mine = [r for r in rows if r['lab'] == lab]
    june = [r for r in mine if r['plate'] in first and r['target'] != 'True']        # 8 wells a plate, as e2 kept for every plate;
    june = (june + random.Random(0).sample([r for r in mine if r['target'] == 'True'], pca['wells_per_plate']))[::3]   # the all-well plate cut to 8 at random, as e2 cut the rest; then one in three, as for every lab
    # 26 Oct (Kat: "number lab centroids. legend more clear and comprehensive"): each lab's "normal", the centre of its wells, is a
    # numbered badge (lab 2's in pink, at its June centre). Badges closer than they are wide move apart along the line between them,
    # with a short line back to the true centre. Wells under a badge are hidden by it, so they are not drawn.
    def centre(pts):
        return sum(ax.X(float(r['pc1'])) for r in pts) / len(pts), sum(ax.Y(float(r['pc2'])) for r in pts) / len(pts)
    pos = {l: centre([r for r in rows if r['lab'] == l]) for l in others}
    pos[lab] = centre(june)
    R = 25      # 26 Oct: room for two-digit numbers at the badge size
    badge = {l: list(p) for l, p in pos.items()}
    for _ in range(80):                                   # until no two badges touch, with room for the pulse ring
        for i, l in enumerate(badge):
            for m in list(badge)[i + 1:]:
                dx, dy = badge[m][0] - badge[l][0], badge[m][1] - badge[l][1]; d = max((dx * dx + dy * dy) ** 0.5, 0.1)
                if d < 2 * R + 14:
                    push = (2 * R + 14 - d) / 2
                    badge[l][0] -= dx / d * push; badge[l][1] -= dy / d * push; badge[m][0] += dx / d * push; badge[m][1] += dy / d * push
    under = lambda r: any((ax.X(float(r['pc1'])) - bx) ** 2 + (ax.Y(float(r['pc2'])) - by) ** 2 < (R + 4) ** 2 for bx, by in badge.values())
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" rx="18" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l and not under(r)][::3], colour[l], 3.6, f'class="f" style="animation-delay:{0.15 + 0.09 * k:.2f}s"') for k, l in enumerate(others)]
    late = 'class="f" style="animation-delay:1.7s"'      # as the flying well lands
    g.append(cloud([r for r in june if not under(r)], PALE_PINK if both else PINK, 3.6 if both else 4.2, late))
    g.append(cloud([r for r in mine if r['plate'] in last and not under(r)], PINK, 4.2, late))
    xs = [ax.X(float(r['pc1'])) for r in june]; ys = [ax.Y(float(r['pc2'])) for r in june]
    month = date.fromisoformat(B[1]['date']).strftime('%B')
    g.append(f'<g class="pdf">' + text(min(xs) - 22, sum(ys) / len(ys) + 9, f'{lab_name(lab)}, {month}', 28, PINK, 'end', 700) + '</g>')      # on stage the pink badge says lab 2

    def mark(l, x, y, bx, by, r=R, size=px(T_TEXT)):      # a lab's number: 22 px on stage
        c, ink = (PINK, PINK) if l == lab else (colour[l], INK)
        moved = (bx - x) ** 2 + (by - y) ** 2 > 36
        lead = (f'<path d="M {x:.1f} {y:.1f} L {bx:.1f} {by:.1f}" stroke="{INK2}" stroke-width="2"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{c}" stroke="#ffffff" stroke-width="1.5"/>') if moved else ''
        return (lead + f'<circle data-bg="1" cx="{bx:.1f}" cy="{by:.1f}" r="{r}" fill="#ffffff" stroke="{c}" stroke-width="5"/>'
                + text(bx, by + size * 0.35, str(lab_number(l)), size, ink, 'middle', 700))
    order = sorted(badge, key=lab_number); t2 = 1.9 + 0.08 * order.index(lab)
    keep = (lab, now['nearest_other']) if now else order      # 04b (26 Oct, half the words): only the two labs the certificate compares keep their numbers
    leads, marks = [], []
    for k, l in enumerate(order):
        m, fade = mark(l, *pos[l], *badge[l]), ''
        if l not in keep:
            m, fade = re.sub(r'<text[^>]*>[^<]*</text>$', '', m).replace('fill="#ffffff"', 'fill="none"'), ' opacity=".5"'      # a faint ring, not a white hole
        cut = m.index('<circle data-bg="1"')                   # every lead line and true-centre dot under every badge, so no dot lands on a number
        leads.append(f'<g class="pop" style="animation-delay:{1.9 + 0.08 * k:.2f}s"{fade}>{m[:cut]}</g>')
        marks.append(f'<g class="pop" style="animation-delay:{1.9 + 0.08 * k:.2f}s"{fade}>{m[cut:]}</g>')
    g += leads + marks
    g.append(f'<circle class="pulse" style="animation-delay:{t2 + 0.6:.2f}s" cx="{badge[lab][0]:.1f}" cy="{badge[lab][1]:.1f}" r="{R}" fill="none" stroke="{PINK}" stroke-width="4"/>')
    # the key, one row (26 Oct, half the words): a well, a lab's "normal", and how to read distance
    kx, k1 = ax.x0 + 8, ax.y0 + ax.h + 44
    shades = [colour[others[i]] for i in (0, len(others) // 2, len(others) - 1)]
    if not now:
        g.append(f'<g class="f" style="animation-delay:2.9s">'
                 + ''.join(f'<circle cx="{kx + 6 + 13 * i}" cy="{k1 - 9}" r="5" fill="{c}"/>' for i, c in enumerate(shades))
                 + text(kx + 52, k1, f'one well ({pca["wells"]:,})', px(T_TEXT), INK2)
                 + mark(others[4], kx + 360, k1 - 10, kx + 360, k1 - 10, r=24)
                 + text(kx + 392, k1, 'a lab&#8217;s &#8220;normal&#8221;', px(T_TEXT), INK2)
                 + text(ax.x0 + ax.w - 8, k1, 'closer = more alike', px(T_TEXT), INK2, 'end') + '</g>')
        # one well becomes one point: a lab 2 well flies onto the map and shrinks into its June dot (show, don't tell)
        import base64
        uri = 'data:image/png;base64,' + base64.b64encode(open('figures/assets/box-you.png', 'rb').read()).decode()
        sx, sy, sz = ax.x0 + 40, ax.y0 + 40, 110
        tx, ty = pos[lab][0] - (sx + sz / 2), pos[lab][1] - (sy + sz / 2)
        g.append(f'<style>@keyframes dl-fly{{0%{{opacity:0;transform:none}}12%,50%{{opacity:1;transform:none}}100%{{opacity:0;transform:translate({tx:.0f}px,{ty:.0f}px) scale(.06)}}}}'
                 f'.dl-fly{{opacity:0;transform-box:fill-box;transform-origin:center;animation:dl-fly 1.7s cubic-bezier(.5,0,.2,1) .2s forwards}}</style>'
                 f'<g class="dl-fly"><image href="{uri}" x="{sx}" y="{sy}" width="{sz}" height="{sz}" preserveAspectRatio="xMidYMid slice"/>'
                 f'<rect x="{sx}" y="{sy}" width="{sz}" height="{sz}" rx="10" fill="none" stroke="{PINK}" stroke-width="5"/></g>')
    if now:      # 26 Oct (Kat: "figures: always have legend, prefer position under plot"): 04b's key, under the map
        g.append(''.join(f'<circle cx="{kx + 6 + 13 * i}" cy="{k1 - 9}" r="5" fill="{c}"/>' for i, c in enumerate(shades))
                 + text(kx + 52, k1, 'one well', px(T_TEXT), INK2)
                 + mark(others[4], kx + 234, k1 - 10, kx + 234, k1 - 10, r=24)
                 + text(kx + 266, k1, 'a lab&#8217;s &#8220;normal&#8221;', px(T_TEXT), INK2)
                 + f'<circle cx="{kx + 560}" cy="{k1 - 10}" r="13" fill="{PINK}" stroke="#ffffff" stroke-width="3"/>'
                 + text(kx + 586, k1, f'new batch, {now["n_plates"]} plates', px(T_TEXT), INK2))
    if now:      # 26 Oct (Kat: "show lab projection one slide"): the certificate view is this same map, still, with one new batch landing
        # 26 Oct (Kat: "new batch slide, what is the point? looks like it went out of distribution"): the check made visible. The batch
        # is 2.8 plate spreads from its own lab's normal and 4.4 from the next lab's, in all features (the map is only for the eye):
        # nearer its own lab, so "normal". Solid pink to its own lab, dashed ink to the next.
        here = centre([r for r in mine if r['plate'] in now['plates']]); own, near = badge[lab], badge[now['nearest_other']]
        g = [re.sub(r' class="(?:f|pop)" style="animation-delay:[0-9.]+s"', '', e) for e in g if 'class="pulse"' not in e]
        def tie(to, c, dash):
            dx_, dy_ = to[0] - here[0], to[1] - here[1]; d = max((dx_ ** 2 + dy_ ** 2) ** 0.5, 1)
            end = (to[0] - dx_ / d * (R + 4), to[1] - dy_ / d * (R + 4))
            return f'<path d="M {here[0]:.1f} {here[1]:.1f} L {end[0]:.1f} {end[1]:.1f}" stroke="{c}" stroke-width="3.5"{dash}/>'
        g.append(f'<g class="f" style="animation-delay:0.9s">' + tie(own, PINK, '') + tie(near, INK, ' stroke-dasharray="8 7"') + '</g>')      # the numbers: the certificate's bars
        g.append(f'<g class="drop" style="animation-delay:0.3s"><circle cx="{here[0]:.1f}" cy="{here[1]:.1f}" r="15" fill="{PINK}" stroke="#ffffff" stroke-width="4"/>'
                 + text(here[0] - 26, here[1] + 10, 'new batch', px(T_TEXT), PINK, 'end') + '</g>')      # left, where the map is empty
        g.append(f'<circle class="pulse" style="animation-delay:0.9s" cx="{here[0]:.1f}" cy="{here[1]:.1f}" r="15" fill="none" stroke="{PINK}" stroke-width="4"/>')
    g.append(text(ax.x0 + 22, ax.y0 + ax.h - 18, 'PC 1 &#8594;', 20, MUTE, extra='class="pdf"'))
    g.append(f'<g class="pdf" transform="translate({ax.x0 + 30},{ax.y0 + ax.h - 50}) rotate(-90)">{text(0, 0, "PC 2 &#8594;", 20, MUTE)}</g>')
    if side:
        g += side(here if now else None)
    return svg(width, 608, g, aria=f'Principal components of untreated wells, one shade of green per lab; each lab forms its own group; two labs&#8217; normals sit {one:.1f} within-plate spreads apart.')


def trajectory_chart(e10, lab, both=True):
    """04b: one lab through time. Top, its controls' drift from its first batch; below, how well its drug answers still match
    that first batch; one date axis, so the batches the controls flagged line up with the answers that moved.
    25 Oct 2026: "show trajectory through time more clearly ... how does this predict what is measured?" """
    bs = sorted(e10['batches'][lab], key=lambda b: b['batch'][:8])
    when = lambda b: date(int(b['batch'][:4]), int(b['batch'][4:6]), int(b['batch'][6:8]))
    first, last = when(bs[0]), when(bs[-1])
    lo, hi = date(first.year, first.month, 1), date.fromordinal(last.toordinal() + 12)       # the axis ends just after the last batch
    X = lambda d: 130 + (d - lo).days / (hi - lo).days * 860
    top = Axes(130, 78, 860, 170, (0, 1), (0, 14)) if both else Axes(130, 78, 860, 444, (0, 1), (0, 14))
    low = Axes(130, 362, 860, 160, (0, 1), (0.6, 1)) if both else top          # stage: the date axis sits under the one panel
    flagged = [b for b in bs if b['outside']]
    assert flagged == bs[-len(flagged):], 'the flagged batches are the last ones'
    x0, x1 = X(when(flagged[0])) - 18, X(when(flagged[-1])) + 18
    at = lambda b: 0.3 + 1.6 * (X(when(b)) - X(first)) / max(1.0, X(last) - X(first))      # when the traced line reaches a batch
    g = [f'<g class="f" style="animation-delay:{at(flagged[0]) - 0.15:.2f}s"><rect x="{x0:.1f}" y="62" width="{x1 - x0:.1f}" height="{low.y0 + low.h - 62 + 4}" rx="12" fill="{PINK}" opacity="0.08"/></g>']
    for ax, ticks, fmt in ((top, (0, 5, 10), lambda v: f'{v:g}'), (low, (0.6, 0.8, 1), lambda v: f'{v:g}'))[:2 if both else 1]:
        g += [f'<path d="M {ax.x0} {ax.Y(v):.1f} L {ax.x0 + ax.w} {ax.Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>' + text(ax.x0 - 12, ax.Y(v) + 9, fmt(v), 27, MUTE, 'end') for v in ticks]
    m = date(lo.year, lo.month, 1)
    while m < hi:
        g.append(text(X(m) + 4, low.y0 + low.h + 40, m.strftime('%b'), 27, MUTE) + f'<path d="M {X(m):.1f} {low.y0 + low.h} l 0 10" stroke="{MUTE}" stroke-width="2"/>')
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    g.append(f'<path d="M {low.x0} {low.y0 + low.h} L {low.x0 + low.w} {low.y0 + low.h}" stroke="{MUTE}" stroke-width="2"/>')
    head = lambda y, ic, words, note: (f'<g transform="translate({top.x0 - 4},{y - 25})">{icon(ic, INK2, 30)}</g>'
                                      + text(top.x0 + 36, y, words, 27, INK, weight=600) + note)
    g.append(head(46, 'well', 'controls: distance from first batch', ''))
    # 26 Oct (Kat: "controls drift: what is y axis? distance?"): the unit, horizontal at the top of the axis, as 04a's 6x counts it
    g.append(text(top.x0 + 12, top.y0 + 24, 'plate spreads', 22, MUTE))      # inside the plot's empty top left
    if both:
        g.append(head(304, 'drug', 'drug answers: match with first batch (1 = perfect)', ''))
    g.append(f'<g class="f" style="animation-delay:{at(flagged[0]):.2f}s">' + text(x0 - 14, 104, 'flagged', 27, PINK, 'end', 700) + '</g>')
    line = lambda ax, key, pts: ('<path d="M ' + ' L '.join(f'{X(when(b)):.1f} {ax.Y(b[key]):.1f}' for b in pts)
                                 + f'" fill="none" stroke="{PINK}" stroke-width="3" stroke-linejoin="round" opacity="0.45"/>')
    dot = lambda ax, key, b: (f'<circle cx="{X(when(b)):.1f}" cy="{ax.Y(b[key]):.1f}" r="9" fill="{PINK}" stroke="{PANEL}" stroke-width="2"/>'
                              + (f'<circle cx="{X(when(b)):.1f}" cy="{ax.Y(b[key]):.1f}" r="16" fill="none" stroke="{PINK}" stroke-width="2.5"/>' if b['outside'] else ''))
    answered = [b for b in bs if b['agree_own_baseline'] is not None]
    two = e10['flagged_against_unflagged'][lab]['with_own_baseline']; calm = [b for b in answered if not b['outside']]
    assert abs(sum(b['agree_own_baseline'] for b in calm) / len(calm) - two['unflagged']) < 0.001, 'the dashed line is the 0.85 beside the chart'
    mean = lambda xa, xb, v, c: f'<path d="M {xa:.1f} {low.Y(v):.1f} L {xb:.1f} {low.Y(v):.1f}" stroke="{c}" stroke-width="3" stroke-dasharray="9 7" stroke-linecap="round"/>'
    g.append(line(top, 'drift', bs).replace('<path ', '<path class="draw" pathLength="1" style="animation-delay:0.3s" ', 1)
             + ''.join(f'<g class="pop" style="animation-delay:{at(b):.2f}s">{dot(top, "drift", b)}</g>' for b in bs))
    if not both:
        return svg(1040, 608, g, aria=f'{lab_name(lab)}, batch by batch from {first:%B} to {last:%B}: its control wells drift from its first batch; '
                   f'the {NUMBERS[len(flagged)]} batches its controls flagged are the last ones.')
    g.append('<g class="f" style="animation-delay:0.8s">' + line(low, 'agree_own_baseline', answered) + ''.join(dot(low, 'agree_own_baseline', b) for b in answered)
             + f'<circle cx="{X(first):.1f}" cy="{low.Y(1):.1f}" r="9" fill="{PANEL}" stroke="{PINK}" stroke-width="3"/>'
             + text(X(first) + 18, low.Y(1) - 14, 'first batch', 27, MUTE) + '</g>')
    g.append('<g class="f" style="animation-delay:1.2s">' + mean(X(when(calm[0])), X(when(calm[-1])), two['unflagged'], MUTE) + mean(x0 + 8, x1 - 8, two['flagged'], PINK) + '</g>')
    return svg(1040, 608, g, aria=f'{lab_name(lab)}, batch by batch from {first:%B} to {last:%B}: when its control wells drift, its drug answers stop matching its first batch; '
               f'the {NUMBERS[len(flagged)]} batches its controls flagged are the ones whose answers moved most.')


RED = PINK      # 26 Oct (Kat: "red ring: this is not color in guide"): a flagged batch is an outlier, ringed in the guide's pink, a white gap between


def tint(f, a=(0xd2, 0x45, 0x8b), b=(0x6e, 0x0b, 0x3f)):
    """Lab 2's pink in time: f = 0 the first batch (light), 1 the last (dark)."""
    return '#' + ''.join(f'{round(x + (y - x) * f):02x}' for x, y in zip(a, b))


def drift_chart(e10, R, lab):
    """04c since 26 Oct, two panels (Kat: "one plot two y axis, single horizontal threshold"; "more control drift = less drug
    [answers]? correlation plot supporting"; "simple two-three panel figure is okay").
    Left, lab 2 in time: the controls' drift on the left axis, in units of the distance to the nearest other lab, so the flag rule
    (nearer another lab than its own first batch, e9) is one line at 1; the drug answers' match with the first batch on the right
    axis, falling in the weeks the drift crosses the line (dashed means 0.85, 0.67).
    Right, every lab: each batch's drift and drug-answer match, each minus its lab's mean, as e10 tests them; rho = -0.71 over 118
    batches (permutation p = 0.0005). Lab 2 in pink; the four batches whose positive controls failed as crosses."""
    import statistics as st
    e9 = {b['batch']: b for b in R['batches']}
    bs = sorted(e10['batches'][lab], key=lambda b: b['batch'][:8])
    ratio = {b['batch']: e9[b['batch']]['from_baseline'] / e9[b['batch']]['to_nearest_other'] for b in bs}
    assert all((ratio[b['batch']] > 1) == b['outside'] for b in bs), 'for this lab the batch ratio and the plate-majority flag agree'
    when = lambda b: date(int(b['batch'][:4]), int(b['batch'][4:6]), int(b['batch'][6:8]))
    first, last = when(bs[0]), when(bs[-1])
    lo, hi = date(first.year, first.month, 1), date.fromordinal(last.toordinal() + 12)
    x0, w, y0, h = 96, 560, 74, 258      # 26 Oct (Kat: "y axis should always be labelled, explain simply"): two-line titles above
    X = lambda d: x0 + (d - lo).days / (hi - lo).days * w
    L = lambda v: y0 + h - v / 2 * h                      # left: 0 to 2 nearest-lab distances
    Rt = lambda v: y0 + h - (v - 0.5) / 0.5 * h          # right: 0.5 to 1 match
    at = lambda b: 0.5 + 1.6 * (X(when(b)) - X(first)) / max(1.0, X(last) - X(first))
    flagged = [b for b in bs if b['outside']]; answered = [b for b in bs if b['agree_own_baseline'] is not None]
    two = e10['flagged_against_unflagged'][lab]['with_own_baseline']; calm = [b for b in answered if not b['outside']]
    g = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{PANEL}"/>']
    g.append(f'<g class="f" style="animation-delay:0.1s"><path d="M {x0} {L(1):.1f} H {x0 + w}" stroke="{INK2}" stroke-width="2.5" stroke-dasharray="10 7"/>'
             + text(x0 + w - 10, L(1) - 10, 'flag', T_TEXT, INK2, 'end') + '</g>')      # the threshold in ink: pink stays on lab 2
    g.append(f'<path d="M {x0} {y0} V {y0 + h} H {x0 + w} V {y0}" fill="none" stroke="{MUTE}" stroke-width="2.5"/>')
    g += [text(x0 - 10, L(v) + 8, f'{v:g}', T_TEXT, PINK, 'end') for v in (0, 1, 2)]
    m = date(lo.year, lo.month, 1)
    while m < hi:
        g.append(text(X(m), y0 + h + 32, m.strftime('%b'), T_TEXT, MUTE) + f'<path d="M {X(m):.1f} {y0 + h} l 0 9" stroke="{MUTE}" stroke-width="2"/>')      # months start on their tick: the axis title's edge
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    g.append(text(x0, y0 - 40, f'{lab_name(lab)}&#8217;s controls, drift', T_TEXT, INK, weight=700) + text(x0, y0 - 12, '1 = as far as another lab', T_TEXT, INK2))      # 26 Oct (Kat: "more simple"): one series, one axis
    path = lambda f, pts: 'M ' + ' L '.join(f'{X(when(b)):.1f} {f(b):.1f}' for b in pts)
    g.append(f'<path class="draw" pathLength="1" style="animation-delay:0.5s" d="{path(lambda b: L(ratio[b["batch"]]), bs)}" fill="none" stroke="{PINK}" stroke-width="3.5" stroke-linejoin="round"/>')
    # 26 Oct (Kat: "lab 2 trajectory: unique shade for each point (scale by time), highlight red outline when out of
    # distribution"): each batch its own pink, light to dark in time, the same shade on the right panel; a red ring when flagged
    shade = {b['batch']: tint(k / max(1, len(bs) - 1)) for k, b in enumerate(bs)}
    for b in bs:
        y = L(ratio[b['batch']])
        g.append(f'<g class="pop" style="animation-delay:{at(b):.2f}s"><circle cx="{X(when(b)):.1f}" cy="{y:.1f}" r="8.5" fill="{shade[b["batch"]]}" stroke="{PANEL}" stroke-width="2"/>'
                 + (f'<circle cx="{X(when(b)):.1f}" cy="{y:.1f}" r="15" fill="none" stroke="{RED}" stroke-width="3.5"/>' if b['outside'] else '') + '</g>')
    # right: every lab, each batch against its own lab's mean
    pts = []
    for l, rows in e10['batches'].items():
        p = [b for b in rows if b['agree_own_baseline'] is not None]
        mx, my = st.mean(b['drift'] for b in p), st.mean(b['agree_own_baseline'] for b in p)
        pts += [dict(b, lab=l, dx=b['drift'] - mx, dy=b['agree_own_baseline'] - my) for b in p]
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    assert len(pts) == a['n_batches'], 'the panel draws the batches e10 tests'
    sx0, sw = 730, 370
    SX = lambda v: sx0 + (v + 5) / 15 * sw               # -5 to +10 plate spreads
    SY = lambda v: y0 + h - (v + 0.6) / 0.9 * h          # -0.6 to +0.3
    g.append(f'<rect x="{sx0}" y="{y0}" width="{sw}" height="{h}" fill="{PANEL}"/>'
             f'<path d="M {SX(0):.1f} {y0} V {y0 + h} M {sx0} {SY(0):.1f} H {sx0 + sw}" stroke="{GRID}" stroke-width="2"/>'
             f'<path d="M {sx0} {y0} V {y0 + h} H {sx0 + sw}" fill="none" stroke="{MUTE}" stroke-width="2.5"/>')
    g.append(text(sx0, y0 - 40, f'drug answers, {a["n_batches"]} batches', T_TEXT, INK, weight=700) + text(sx0, y0 - 12, 'against the lab&#8217;s usual', T_TEXT, INK2))
    g += [text(sx0 - 10, SY(v) + 9, f'{v:+.1f}'.replace('+0.0', '0').replace('-', '&#8722;'), 24, INK2, 'end', extra='class="pdf"') for v in (-0.4, 0, 0.2)]
    g += [text(SX(v), y0 + h + 30, f'{v:+g}'.replace('+0', '0').replace('-', '&#8722;'), 24, MUTE, 'middle', extra='class="pdf"') for v in (-4, 0, 4, 8)]
    g.append(text(sx0 + sw / 2, y0 + h + 36, 'controls&#8217; drift', T_TEXT, INK2, 'middle', extra='class="talk"')      # stage: ticks in the reader's layer
             + text(sx0 + sw / 2, y0 + h + 58, 'controls&#8217; drift, against the lab&#8217;s usual', 22, INK2, 'middle', extra='class="pdf"'))
    cross = lambda p: (f'<path d="M {(p["at"][0] if "at" in p else SX(p["dx"])) - 5:.1f} {(p["at"][1] if "at" in p else SY(p["dy"])) - 5:.1f} l 10 10 m 0 -10 l -10 10" '
                       f'stroke="{MUTE}" stroke-width="2.2" stroke-linecap="round"/>')
    g.append('<g class="f" style="animation-delay:3.4s">' + ''.join(cross(p) if p['positive_controls_failed'] else f'<circle cx="{SX(p["dx"]):.1f}" cy="{SY(p["dy"]):.1f}" r="5" fill="{GREEN}" opacity=".45"/>'
                                                                for p in pts if p['lab'] != lab) + '</g>')
    g.append('<g class="f" style="animation-delay:3.8s">' + ''.join(f'<circle cx="{SX(p["dx"]):.1f}" cy="{SY(p["dy"]):.1f}" r="7.5" fill="{shade.get(p["batch"], PINK)}" stroke="{PANEL}" stroke-width="1.5"/>'
                                                                + (f'<circle cx="{SX(p["dx"]):.1f}" cy="{SY(p["dy"]):.1f}" r="14" fill="none" stroke="{RED}" stroke-width="3"/>' if p['outside'] else '')
                                                                for p in pts if p['lab'] == lab) + '</g>')
    g.append(f'<g class="pop" style="animation-delay:4.2s">' + text(sx0 + sw - 12, y0 + 50, f'&#8722;{abs(a["spearman"]):.2f}', T_BIG, INK, 'end', 700)
             + text(sx0 + sw - 12, y0 + 80, 'rank correlation', T_TEXT, INK2, 'end') + '</g>')      # the 118 batches are in the reader's line      # 26 Oct (review): the key number big, top right
    ly = y0 + h + 64      # 26 Oct (Kat: "figures: always have legend, prefer position under plot"): each panel's key under it
    g.append(f'<defs><linearGradient id="dl-time" x1="0" x2="1"><stop offset="0" stop-color="{tint(0)}"/><stop offset="1" stop-color="{tint(1)}"/></linearGradient></defs>'
             f'<g class="f" style="animation-delay:0.3s"><rect x="{x0}" y="{ly - 13}" width="62" height="12" rx="6" fill="url(#dl-time)"/>'
             f'<path d="M {x0 + 60} {ly - 16} l 11 9 l -11 9 z" fill="{tint(1)}"/>'
             + text(x0 + 84, ly, f'a batch, {first:%B} to {last:%B} ({len(bs)})', T_TEXT, INK2)
             + f'<circle cx="{x0 + 440}" cy="{ly - 7}" r="12" fill="none" stroke="{RED}" stroke-width="3"/>' + text(x0 + 460, ly, 'flagged', T_TEXT, INK2) + '</g>')
    g.append(f'<g class="f" style="animation-delay:3.4s"><circle cx="{sx0 + 6}" cy="{ly - 7}" r="6" fill="{GREEN}" opacity=".45"/>'
             + text(sx0 + 20, ly, 'a batch', T_TEXT, INK2) + cross({'dx': 0, 'dy': 0, 'at': (sx0 + 120, ly - 7)})
             + text(sx0 + 136, ly, 'known drugs failed', T_TEXT, INK2) + '</g>')
    # 26 Oct (pitch skill, Hale: "CliffsNotes right on the slide"): the conclusion written where the data shows it, below lab 2's
    # drifted batches, clear of the four failed-control crosses
    g.append(f'<g class="pop" style="animation-delay:4.5s">' + text(SX(3), SY(-0.36), 'more drift,', T_TEXT, INK, weight=700)
             + text(SX(3), SY(-0.36) + 27, 'weaker answers', T_TEXT, INK, weight=700) + '</g>')
    return svg(1132, 406, g, fit=True, aria=f'Left: {lab_name(lab)}, batch by batch from {first:%B} to {last:%B}; its controls cross the flag line in its last {NUMBERS[len(flagged)]} batches. '
               f'Right: in every lab, batches that drift more than the lab&#8217;s usual give drug answers that match less '
               f'(Spearman &#8722;{abs(a["spearman"]):.2f}, {a["n_batches"]} batches, {a["n_labs"]} labs).')


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


def density_chart(e13, wide=False):
    """The field's reference tightens as labs join: distance between two references built from m labs each.
    wide (06 since 26 Oct, one figure across the slide): the labs drop onto the curve one at a time, then the curve is drawn on to
    today's eleven; "Labs own their data." sits in the plot's empty corner (decentralization stays on stage)."""
    ref = e13['field_reference_by_labs']; ms = sorted(int(k) for k in ref)
    top = 2 * (int(max(v['p90'] for v in ref.values()) / 2) + 1)
    ax = Axes(40, 70, 1060, 172, (0.5, 11.5), (0, top)) if wide else Axes(110, 64, 900, 376, (0.5, 11.5), (0, top))      # wide: shorter since 26 Oct, so 06's why-now strip fits under it
    t = (lambda m: 0.5 + 0.5 * (m - 1)) if wide else (lambda m: 0.2 + 0.15 * m)      # when lab m lands
    g = ax.frame(range(0, top + 1, 2), [(m, str(m)) for m in (1, 6, 11)], '' if wide else 'error in &#8220;normal&#8221; (lower is better)', 'labs on the map', fmt=lambda v: '', room=True)
    if wide:      # expected rings beyond the measured labs, dashed, on the curve: the ring keeps shrinking to today's eleven
        g.append(f'<g class="f" style="animation-delay:{t(ms[-1]) + 0.8:.2f}s">' + ''.join(
            f'<circle cx="{ax.X(x):.1f}" cy="{ax.Y(ref[str(ms[0])]["mean"] / x ** 0.5):.1f}" r="{5.5 * ref[str(ms[0])]["mean"] / x ** 0.5:.1f}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="5 5" opacity=".7"/>'
            for x in (8, 11)) + '</g>')
    if wide:      # the axis title reads across, above the plot, where the long rotated one was cut
        g.append(text(ax.x0, ax.y0 - 40, 'error in &#8220;normal&#8221;', T_TEXT, INK, weight=700)
                 + text(ax.x0, ax.y0 - 12, 'lower: a screen sees smaller drug effects, a model learns cells, not labs', T_TEXT, INK2))
        ky = ax.y0 + ax.h + 106      # 26 Oct (Kat: "figures: always have legend, prefer position under plot"): the marks, under the axis title
        g.append(f'<g class="f" style="animation-delay:{t(ms[-1]) + 1.2:.2f}s"><circle cx="{ax.x0 + 7}" cy="{ky - 7}" r="6" fill="{GREEN}"/>'
                 + text(ax.x0 + 22, ky, f'mean of {ref[str(ms[0])]["draws"]} draws', T_TEXT, INK2)
                 + f'<path d="M {ax.x0 + 254} {ky - 19} V {ky + 5}" stroke="{GREEN}" stroke-width="3" opacity=".4"/>' + text(ax.x0 + 268, ky, '10th to 90th percentile', T_TEXT, INK2)
                 + f'<circle cx="{ax.x0 + 560}" cy="{ky - 7}" r="13" fill="none" stroke="{GREEN}" stroke-width="3"/>' + text(ax.x0 + 582, ky, 'ring: the error', T_TEXT, INK2) + '</g>')      # 26 Oct (Kat): every y axis named, simply
    one = ref[str(ms[0])]['mean']
    pts = [(ax.X(x), ax.Y(one / x ** 0.5)) for x in (1 + k * 0.1 for k in range(101))]
    seg = lambda p: ' '.join(f'{"M" if i == 0 else "L"} {x:.1f} {y:.1f}' for i, (x, y) in enumerate(p))
    t1 = t(ms[-1]) + 0.4 if wide else 1.25
    g.append(f'<g class="f" style="animation-delay:{t1:.2f}s"><path d="{seg(pts[:41])}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 7" opacity=".7"/></g>')
    g.append(f'<g class="f" style="animation-delay:{t1 + 0.35:.2f}s"><path d="{seg(pts[40:])}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 7" opacity=".25"/></g>')
    for m in ms:
        v = ref[str(m)]
        c = PINK if wide and m == ms[0] else GREEN      # 26 Oct: one lab alone is a single point, pink; the field it joins, green
        ring = (f'<circle cx="{ax.X(m):.1f}" cy="{ax.Y(v["mean"]):.1f}" r="{5.5 * v["mean"]:.1f}" fill="none" stroke="{c}" stroke-width="3"/>'
                if wide else '')                        # 26 Oct (plan): each point a ring as wide as its error, so "normal" visibly tightens
        g.append(f'<g class="{"drop" if wide else "f"}" style="animation-delay:{t(m):.2f}s">'
                 f'<path d="M {ax.X(m):.1f} {ax.Y(v["p10"]):.1f} L {ax.X(m):.1f} {ax.Y(v["p90"]):.1f}" stroke="{c}" stroke-width="3" opacity=".4"/>'
                 f'{ring}<circle cx="{ax.X(m):.1f}" cy="{ax.Y(v["mean"]):.1f}" r="{6 if wide else 10}" fill="{c}"/></g>')
        if m in (ms[0], ms[-1]):
            off = 5.5 * v['mean'] * 0.75 + 10 if wide else 16      # clear of its ring
            g.append(f'<g class="f" style="animation-delay:{t(m) + 0.3:.2f}s">' + text(ax.X(m) + off, ax.Y(v['mean']) - off * 0.6, f'{v["mean"]:.1f}', T_SUB, c, weight=700) + '</g>')
    n = e13['n_labs']
    g.append(f'<g class="f" style="animation-delay:{t(3):.2f}s">' + text(ax.X(3), ax.Y(ref['3']['p90']) - 16, 'measured', T_TEXT, GREEN, 'middle') + '</g>')       # the dots, named where they are, as 'expected' names the dashes
    g.append(f'<path d="M {ax.X(n):.1f} {ax.y0 + ax.h} L {ax.X(n):.1f} {ax.y0 + ax.h - 36}" stroke="{INK2}" stroke-width="2"/>' + text(ax.X(n) - 10, ax.y0 + ax.h - 14, 'labs today', T_TEXT, INK2, 'end'))
    g.append(f'<g class="f" style="animation-delay:{t1 + 0.45:.2f}s">' + text(ax.X(8), ax.Y(one / 8 ** 0.5) - 18, 'expected', T_TEXT, GREEN, 'middle', extra='opacity=".8"') + '</g>')
    if wide:
        g.append(f'<g class="f" style="animation-delay:{t1 + 0.9:.2f}s"><svg x="{ax.x0 + ax.w - 390}" y="{ax.y0 - 64}" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{INK}" '
                 f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS.get("lock") or PATH_ICONS["lock"]}</svg>'
                 + text(ax.x0 + ax.w, ax.y0 - 40, 'Labs own their data, earn a share.', T_TEXT, INK, 'end', 700) + '</g>')      # the data area holds only data       # measured to five labs; beyond, the curve
    g.append(text(ax.X(8), ax.Y(one / 8 ** 0.5) - 50, '1/&#8730;n', 24, GREEN, 'middle', extra=f'class="pdf" style="{MATH}" opacity=".8"'))
    a, b = ref[str(ms[0])]['mean'], ref[str(ms[-1])]['mean']
    return svg(*((1132, 358) if wide else (1010, 530)), g, fit=True, aria=f'The error in normal, measured as the distance between two maps built from different labs, falls from {a:.1f} spreads with {NUMBERS[ms[0]]} lab to {b:.1f} with {NUMBERS[ms[-1]]}.')


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
    every = [b for v in results('e9-replay.json')['labs'].values() for b in v['batches']]
    global CELLS, BATCH      # the nested scale on 04a: cells in a well, a lab's batches from its first (medians, e9)
    CELLS = round(statistics.median(b['cells_per_well'] for b in every if b.get('cells_per_well')), -1)
    CELLS = int(CELLS)
    BATCH = statistics.median(b['from_baseline'] for b in every if not b['is_baseline'] and b['verdict'] == 'in distribution')
    e10 = results('e10-certificate-predicts-answer.json'); e13 = results('e13-baseline-density.json')
    pca = results('e2-plate-position-1053600681.json')['pca']
    e1 = results('e1.json')['all_sources']
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    one = e13['field_reference_by_labs']['1']['mean']
    # 26 Oct (Kat: "total length limit 27 pages"): the known-drugs view (04b) left the talk; its gain is 05a's 86% tile and its
    # science boards A9 and A14. slide05.known_drugs() still draws it, so it can come back as layer and side 1 here.

    css = BASE_CSS + '''
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1, .step-2 .s2 { opacity: 1; pointer-events: auto; }
    .flow .map01 { opacity: 0; transition: opacity .5s ease; } .step-0 .map01, .step-1 .map01 { opacity: 1; }      /* the map card holds views 0 and 1; not an .s, so each layer's motion waits for its own view */
    ''' + view_motion(3) + '''
    .flow { cursor: pointer; }
'''
    H = (f'position:absolute; left:56px; top:86px; width:900px; margin:0; {SANS} font-size:44px; font-weight:600; '
         f'letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};')
    FOOT = f'position:absolute; left:56px; bottom:44px; width:1010px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    fig = lambda n: f'<span style="color:{D_TEXT}; font-weight:500;">fig {n}</span>'
    card = lambda inner: (f'<div style="position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} padding:0 18px; overflow:hidden;">'
                          f'<div style="position:relative; width:100%; height:100%;">{inner}</div></div>')
    layer = lambda k, inner: f'<div class="s s{k}" style="position:absolute; inset:0; display:flex; align-items:center;">{inner}</div>'
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">The map</span>'
    n_labs = NUMBERS[e13['n_labs']].capitalize()
    # 26 Oct (Kat: "cut the side panels"): the 6x and the certificate are drawn in the map's own figure, right of the map
    px = lambda p: round(p * 1640 / CARD_W, 1)      # 04a and 04b draw into the map's figure, 1640 units across the card

    def ruler(_):
        # 26 Oct (Kat: "cell > well > plate > lab build up should be more clear"; "rings: well, plate, lab spread. quantify all
        # nested loops/space"): the scale nested, in plate spreads. One well is about 220 cells (median, results/e9); wells sit 1x
        # from their plate's centre (the unit); a lab's batches 1.6x from its first (median of batches in distribution, e9);
        # two labs' normals 6x apart (e13). Rings drawn to scale, 40 units a spread.
        u, a0, cy = 40, 1150, 330
        a1 = a0 + one * u
        g = [f'<g class="f" style="animation-delay:2.4s">' + text(1090, 150, f'{round(one)}&#215;', px(T_HERO), GREEN, weight=700, extra='letter-spacing="-4"')
             + text(1090, 204, 'between two labs', px(T_TEXT), INK2) + '</g>']
        g.append(f'<path class="bar" style="animation-delay:3.0s; animation-duration:1.1s" d="M {a0} {cy} L {a1 - u:.1f} {cy}" stroke="{MUTE}" stroke-width="2.5" stroke-dasharray="6 7"/>')
        g.append(f'<g class="pop" style="animation-delay:2.6s"><circle cx="{a0}" cy="{cy}" r="{BATCH * u:.1f}" fill="none" stroke="{PINK}" stroke-width="3" stroke-dasharray="7 6"/>'
                 f'<circle cx="{a0}" cy="{cy}" r="{u}" fill="none" stroke="{PINK}" stroke-width="4"/><circle cx="{a0}" cy="{cy}" r="7" fill="{PINK}"/></g>')
        g.append(f'<g class="pop" style="animation-delay:3.4s"><circle cx="{a1:.1f}" cy="{cy}" r="{u}" fill="none" stroke="{GREEN}" stroke-width="4"/><circle cx="{a1:.1f}" cy="{cy}" r="7" fill="{GREEN}"/></g>')
        g.append(f'<g class="f" style="animation-delay:3.6s">' + text(a0, cy + BATCH * u + 40, 'lab 2', px(T_TEXT), PINK, 'middle', 700)
                 + text(a1, cy + BATCH * u + 40, 'another lab', px(T_TEXT), INK2, 'middle') + '</g>')
        rows = [(f'<circle cx="1104" cy="{{y}}" r="6" fill="{INK2}"/>', f'one well: ~{CELLS} cells'),
                (f'<circle cx="1104" cy="{{y}}" r="13" fill="none" stroke="{PINK}" stroke-width="3.5"/>', '1&#215; wells on one plate'),
                (f'<circle cx="1104" cy="{{y}}" r="13" fill="none" stroke="{PINK}" stroke-width="2.5" stroke-dasharray="5 4"/>', f'{BATCH:.1f}&#215; a lab&#8217;s batches')]
        for k, (mark, words) in enumerate(rows):
            y = 484 + 42 * k
            g.append(f'<g class="f" style="animation-delay:{3.8 + 0.2 * k:.1f}s">' + mark.replace('{y}', f'{y - 10}') + text(1132, y, words, px(T_TEXT), INK2) + '</g>')
        return g
    def cert(_):
        assert now['verdict'] == 'in distribution' and known == 'came out' and now['cell_count_vs_own_history'] == 'inside'
        nest = lambda name, x, y, c, size: (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" '
                                            f'stroke-linecap="round" stroke-linejoin="round">{ICONS.get(name) or PATH_ICONS[name]}</svg>')
        g = [f'<g class="f" style="animation-delay:1.0s">' + text(1100, 104, 'Member check', px(T_TEXT), INK, weight=700) + text(1100, 146, 'a new batch, in all features', px(T_TEXT), PINK) + '</g>']
        # 26 Oct (Kat: "what is the point here? looks like it went out of distribution"): the check itself, in all features: the new
        # batch sits 2.8 plate spreads from its own lab's normal and 4.4 from the next lab's, so it is its lab's (results/e9)
        sc = 200 / max(now['from_baseline'], now['to_nearest_other'])      # the longer bar 200 units: its label clears the seal
        for k, (v, words, c) in enumerate(((now['from_baseline'], 'own lab', PINK), (now['to_nearest_other'], 'next lab', INK2))):
            y = 196 + 44 * k
            fade = '' if k == 0 else ' opacity=".55"'      # quoted: an unquoted value swallowed the "/>" and hid the label after it
            g.append(f'<g class="f" style="animation-delay:{1.2 + 0.2 * k:.1f}s">' + text(1100, y + 11, words, px(T_TEXT), c, weight=700 if k == 0 else 400)
                     + f'<rect x="1250" y="{y - 12}" width="{v * sc:.1f}" height="26" rx="5" fill="{c}"{fade}/>'
                     + text(1250 + v * sc + 10, y + 11, f'{v:.1f}&#215;', px(T_TEXT), c, weight=700) + '</g>')
        g.append(f'<g class="f" style="animation-delay:1.5s">' + text(1100, 290, 'bar: distance, in plate spreads', px(T_TEXT), INK2) + '</g>')      # 26 Oct (figure-design)
        for k, (ic, words) in enumerate((('well', 'nearer its own lab'), ('drug', 'drugs match'), ('count', 'grew as usual'))):
            y = 352 + 84 * k
            g.append(f'<g class="f" style="animation-delay:{1.6 + 0.3 * k:.1f}s"><path d="M 1100 {y - 46} H 1620" stroke="{GRID}" stroke-width="2"/>'
                     + nest(ic, 1094, y - 38, INK2, 56) + text(1170, y + 2, words, px(T_TEXT), INK) + '</g>'
                     + f'<g class="pop" style="animation-delay:{1.9 + 0.3 * k:.1f}s">{nest("check", 1560, y - 36, GREEN, 52)}</g>')
        return g
    # 26 Oct: 04c's drug-answers panel left; its 0.85 -> 0.67 is drawn on drift_chart's right axis
    SRC = ('', '', '')      # 26 Oct, half the words: the full legends stay in the reader's layer
    # 26 Oct (Kat: "similar slides next to each other; show lab projection one slide"): the certificate (05b until now) is this slide's
    # second view, the same map with one new batch landing on it, so the projection is drawn once; the drift over time follows it
    replay = results('e9-replay.json')['labs'][lab]
    now = max((b for b in B if b['verdict'] == 'in distribution'), key=lambda b: b['n_plates'])
    frame = next(b for b in results('e12-field-normalization.json')['lab_2'] if b['batch'] == now['batch'])
    known = next(b for b in results('e11-known-answer.json')['labs'][lab]['batches'] if b['batch'] == now['batch'])['verdict']
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(4, dark=True)}
  {header('04', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">{n_labs} labs.<br><span style="color:{D_GREEN};">{n_labs} &#8220;normals&#8221;.</span></h2>
  <h2 class="s s1" style="{H}">Send the controls.<br><span style="color:{D_GREEN};">Know it&#8217;s &#8220;normal&#8221; before the screen.</span></h2>
  <h2 class="s s2" style="{H}">Controls catch drift<br><span style="color:{D_GREEN};">before any drug is read.</span></h2>
  <div class="map01">{card(layer(0, field_map(B, lab, pca, one, both=False, side=ruler, width=1640)) + layer(1, field_map(B, lab, pca, one, both=False, now=now, side=cert, width=1640)))}</div>
  <div class="s s2" style="position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} padding:10px 18px; display:flex; align-items:center; overflow:hidden;">{drift_chart(e10, replay, lab)}</div>
  <div class="s s0" style="{FOOT}">{source(SRC[0], f'{fig(2)} dots: DMSO wells, {pca["wells_per_plate"]} per plate, one in three drawn; PCA of {pca["wells"]:,} wells, for the eye (distances use all {e1["n_features"]:,} numbers); plates: 384 wells, 1,536 in labs 1 and 9; 6&#215;: two labs&#8217; centres sit {one:.1f} plate spreads apart on average, a plate spread being a well&#8217;s mean distance from its own plate&#8217;s centre, all {e13["n_features"]:,} numbers (results/e13); JUMP [7]; A2, A3, A13')}</div>
  <div class="s s1" style="{FOOT}">{source('', f'{fig(3)} the member check, replayed on public data; closest lab in all {replay["n_features"]:,} numbers: {lab_name(now["nearest_other"])}, {now["to_nearest_other"]:.1f} within-plate spreads away; known drugs worked; agreement with other labs {frame["agree_field_raw"]:.2f} measured, {frame["agree_field_field"]:.2f} on the map; {now["cells_per_well"]:.0f} cells per well, in its usual range; JUMP [7], results/e9, e11, e12; A11, A18')}</div>
  <div class="s s2" style="{FOOT}">{source(SRC[2], f'{fig(4)} {lab_name(lab)}, {len(e10["batches"][lab])} batches; drift: control wells&#8217; distance from the first batch, in within-plate spreads; drift: distance from the first batch over distance to the nearest other lab&#8217;s centre, so 1 is the flag line (most plates nearer another lab than the first batch, e9); right: every batch&#8217;s drift and match minus its lab&#8217;s mean, Spearman over all labs, permutation p = 0.0005, crosses: positive controls failed (results/e10); A6; JUMP [7]')}</div>
  {cue(3, dark=True)}
</div>'''
    steps = {'tag': ['The map', 'The check', 'The proof']}
    return css, body, steps
