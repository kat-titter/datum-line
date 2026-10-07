"""Slide 05: the map, in two views. Written whole from results/e2 and e10.

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


def cell_count_chart(B):
    n_plates = sum(b['n_plates'] for b in B)
    ax, day, months = time_axis(B, 96, 640, 64, 376, (130, 220))
    g = ax.frame((150, 175, 200), months, 'cells per untreated well',
                 f'batch date, 2021 ({len(B)} batches, {n_plates} plates)', 'WHAT THE LAB CAN SEE')
    for k, b in enumerate(B):
        late = b['verdict'] == 'outside'
        g.append(f'<circle class="f" style="animation-delay:{0.15 + 0.07 * k:.2f}s" cx="{ax.X(day(b["date"])):.1f}" '
                 f'cy="{ax.Y(b["cells_per_well"]):.1f}" r="{11 if late else 9}" fill="{PINK if late else FAINT}"/>')
    low = min(B, key=lambda b: b['cells_per_well'])
    g.append(text(ax.X(day(low['date'])) + 18, ax.Y(low['cells_per_well']) + 7, f"{low['cells_per_well']:.0f}: the lab sees this", 20, INK2))
    out = [b for b in B if b['verdict'] == 'outside']
    x, y = ax.X(day(out[-1]['date'])) - 4, ax.Y(min(b['cells_per_well'] for b in out)) + 58
    g.append(f'<g class="f" style="animation-delay:1.3s">{text(x, y, "last three batches", 26, PINK, "end", 700)}'
             f'{text(x, y + 30, "{:.0f} to {:.0f} cells per well".format(min(b["cells_per_well"] for b in out), max(b["cells_per_well"] for b in out)), 22, INK2, "end")}'
             f'{text(x, y + 58, "inside the lab&#8217;s own range", 22, INK2, "end")}</g>')
    return svg(760, 510, g, aria='Cells per untreated well for each batch of lab 2; the last three batches are inside the range of the earlier ones.')


def distance_chart(B):
    top = 2 * (int(max(b['from_baseline'] for b in B) / 2) + 1)
    ax, day, months = time_axis(B, 96, 640, 64, 376, (0, top))
    g = ax.frame(range(0, top + 1, 4), months, 'distance, in within-plate spreads',
                 'batch date, 2021 (same batches)', 'WHAT ONLY EVERYONE ELSE CAN SEE')
    path = lambda key: ' '.join(f'{"M" if k == 0 else "L"} {ax.X(day(b["date"])):.1f} {ax.Y(b[key]):.1f}' for k, b in enumerate(B))
    g.append(f'<path d="{path("to_nearest_other")}" fill="none" stroke="{GREEN}" stroke-width="3" stroke-linejoin="round"/>')
    g.append(f'<path d="{path("from_baseline")}" fill="none" stroke="{PINK}" stroke-width="3.6" stroke-linejoin="round"/>')
    for b in B:
        g.append(f'<circle cx="{ax.X(day(b["date"])):.1f}" cy="{ax.Y(b["to_nearest_other"]):.1f}" r="6" fill="{GREEN}"/>')
        g.append(f'<circle cx="{ax.X(day(b["date"])):.1f}" cy="{ax.Y(b["from_baseline"]):.1f}" r="7" fill="{PINK}"/>')
    g.append(text(ax.x0 + 30, ax.y0 + 38, 'from its own June baseline', 24, PINK, weight=700))
    g.append(text(ax.x0 + 30, ax.y0 + 70, 'to the nearest other lab', 24, GREEN, weight=700))
    return svg(760, 510, g, aria='Distance of each batch of lab 2 from its own first batch and from the nearest other lab; the lines cross at the end of August.')


def embedding():
    return list(csv.DictReader(open('results/e2-embedding.csv')))


def map_axes(rows, x0, y0, w, h):
    """Axes that hold the middle 99% of the wells, and a cloud drawer that clamps the rest to the edge."""
    xs = sorted(float(r['pc1']) for r in rows); ys = sorted(float(r['pc2']) for r in rows)
    q = lambda v, p: v[int(p * (len(v) - 1))]
    ax = Axes(x0, y0, w, h, (q(xs, .005), q(xs, .995)), (q(ys, .005), q(ys, .995)))
    clampx = lambda v: ax.X(min(max(v, ax.xlim[0]), ax.xlim[1]))
    clampy = lambda v: ax.Y(min(max(v, ax.ylim[0]), ax.ylim[1]))
    cloud = lambda pts, fill, r, extra='': (f'<g fill="{fill}" {extra}>' + ''.join(
        f'<circle cx="{clampx(float(p["pc1"])):.0f}" cy="{clampy(float(p["pc2"])):.0f}" r="{r}"/>' for p in pts) + '</g>')
    return ax, cloud


def field_map(B, lab, pca, both=True):
    """Untreated wells in the first two principal components, one shade of green per lab."""
    rows = embedding()
    first = set(B[0]['plates']) | set(B[1]['plates'])
    last = set(B[-1]['plates']) if both else set()
    others = sorted({r['lab'] for r in rows if r['lab'] != lab}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    ax, cloud = map_axes(rows, 84, 20, 1010, 540)
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::3], colour[l], 3.6, f'class="f" style="animation-delay:{0.15 + 0.09 * k:.2f}s"') for k, l in enumerate(others)]
    mine = [r for r in rows if r['lab'] == lab]
    late = f'class="f" style="animation-delay:{0.25 + 0.09 * len(others):.2f}s"'
    g.append(cloud([r for r in mine if r['plate'] in first], PALE_PINK if both else PINK, 3.6 if both else 4.2, late))
    g.append(cloud([r for r in mine if r['plate'] in last], PINK, 4.2, late))
    v1, v2 = [round(100 * v, 1) for v in pca['variance_explained']]
    g.append(f'<path d="M {ax.x0} {ax.y0} L {ax.x0} {ax.y0 + ax.h} L {ax.x0 + ax.w} {ax.y0 + ax.h}" fill="none" stroke="{MUTE}" '
             f'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 44, f'PC 1 ({v1}% of variance)', 26, INK2, 'middle'))
    g.append(f'<g transform="translate({ax.x0 - 30},{ax.y0 + ax.h / 2}) rotate(-90)">{text(0, 0, f"PC 2 ({v2}% of variance)", 26, INK2, "middle")}</g>')
    lx, ly = ax.x0 + ax.w + 44, ax.y0 + 24
    g.append(text(lx, ly, 'LAB', 24, MUTE, extra='letter-spacing="2"'))
    legend = ([(f'{lab_name(lab)}, June', PALE_PINK, True), (f'{lab_name(lab)}, October', PINK, True)] if both
              else [(lab_name(lab), PINK, True)]) + [(lab_name(l), colour[l], False) for l in others]
    for k, (name, c, own) in enumerate(legend):
        y = ly + 44 + k * 42
        g.append(f'<circle cx="{lx + 11}" cy="{y - 9}" r="11" fill="{c}"/>' + text(lx + 36, y, name, 28, PINK if own else INK2, weight=700 if own else 400))
    return svg(1460, 640, g, aria='Principal components of untreated wells, one shade of green per lab; each lab forms its own group.')


def answer_chart(e10, lab):
    """Each batch: drift from its lab's baseline against agreement with its own first-batch drug answers."""
    pts = [dict(b, lab=l) for l, bs in e10['batches'].items() for b in bs if b['agree_own_baseline'] is not None]
    top = 2 * (int(max(p['drift'] for p in pts) / 2) + 1)
    ax = Axes(110, 64, 900, 376, (0, top), (0, 1))
    g = ax.frame((0, 0.25, 0.5, 0.75, 1), [(v, str(v)) for v in range(0, top + 1, 2)],
                 'agreement with the lab&#8217;s own first answer', 'drift from the lab&#8217;s own baseline, in within-plate spreads',
                 'EVERY BATCH OF EVERY LAB', fmt=lambda v: f'{v:g}')
    dot = lambda p, fill, r, extra='': f'<circle cx="{ax.X(p["drift"]):.1f}" cy="{ax.Y(max(p["agree_own_baseline"], 0)):.1f}" r="{r}" fill="{fill}" {extra}/>'
    failed = [p for p in pts if p['positive_controls_failed']]
    g.append('<g class="f" style="animation-delay:0.2s">' + ''.join(dot(p, '#8fbfae', 6) for p in pts if p['lab'] != lab and not p['positive_controls_failed']) + '</g>')
    g += [f'<path d="M {ax.X(p["drift"]) - 7:.1f} {ax.Y(p["agree_own_baseline"]) - 7:.1f} l 14 14 m 0 -14 l -14 14" stroke="{MUTE}" stroke-width="2.5" stroke-linecap="round"/>' for p in failed]
    g.append('<g class="f" style="animation-delay:0.7s">' + ''.join(dot(p, PINK, 9, f'stroke="{PANEL}" stroke-width="2"') for p in pts if p['lab'] == lab) + '</g>')
    out = [p for p in pts if p['lab'] == lab and p['outside']]
    g.append('<g class="f" style="animation-delay:1.2s">' + ''.join(f'<circle cx="{ax.X(p["drift"]):.1f}" cy="{ax.Y(p["agree_own_baseline"]):.1f}" r="15" fill="none" stroke="{PINK}" stroke-width="2"/>' for p in out) + '</g>')
    cx, cy = sum(ax.X(p['drift']) for p in out) / len(out), min(ax.Y(p['agree_own_baseline']) for p in out)
    g.append(f'<g class="f" style="animation-delay:1.2s">{text(cx, cy - 50, f"{lab_name(lab)}, autumn", 22, PINK, "middle", 700)}</g>')
    if failed:
        fx, fy = max(ax.X(p['drift']) for p in failed) + 18, sum(ax.Y(p['agree_own_baseline']) for p in failed) / len(failed)
        g.append(text(fx, fy + 2, 'known answer failed', 20, MUTE))
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    two = e10['flagged_against_unflagged'][lab]['with_own_baseline']
    rx = 1080
    g.append(text(rx, ax.y0 - 28, 'INSIDE LABS', 22, MUTE, extra='letter-spacing="2.2"'))
    g.append(text(rx, ax.y0 + 74, f'&#961; = &#8722;{abs(a["spearman"]):.2f}', 72, PINK, weight=700))
    for k, line in enumerate(('the further from your baseline,', 'the further from your own answers')):
        g.append(text(rx, ax.y0 + 116 + 30 * k, line, 24, INK2))
    g.append(text(rx, ax.y0 + 300, f'{lab_name(lab)} against its own June answer', 22, GREEN, weight=700))
    g.append(text(rx, ax.y0 + 340, f'{two["unflagged"]:.2f}', 40, INK2, weight=700))
    g.append(text(rx + 96, ax.y0 + 340, 'before the flag', 20, INK2))
    g.append(text(rx, ax.y0 + 384, f'{two["flagged"]:.2f}', 40, PINK, weight=700))
    g.append(text(rx + 96, ax.y0 + 384, 'after it', 20, INK2))
    return svg(1600, 530, g, aria='Drift from baseline against agreement of drug answers for every batch of every lab; agreement falls as drift rises.')


def density_chart(e13):
    """The field's reference tightens as labs join: distance between two references built from m labs each."""
    ref = e13['field_reference_by_labs']; ms = sorted(int(k) for k in ref)
    top = 2 * (int(max(v['p90'] for v in ref.values()) / 2) + 1)
    ax = Axes(110, 64, 900, 376, (0.5, 11.5), (0, top))
    g = ax.frame(range(0, top + 1, 2), [(m, str(m)) for m in range(1, 12)], 'how far two references disagree, in spreads',
                 'labs in the reference', 'DENSER IS TIGHTER')
    one = ref[str(ms[0])]['mean']
    guide = ' '.join(f'{"M" if k == 0 else "L"} {ax.X(1 + k * 0.1):.1f} {ax.Y(one / (1 + k * 0.1) ** 0.5):.1f}' for k in range(101))
    g.append(f'<path d="{guide}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 7" opacity=".7"/>')
    for m in ms:
        v = ref[str(m)]
        g.append(f'<path d="M {ax.X(m):.1f} {ax.Y(v["p10"]):.1f} L {ax.X(m):.1f} {ax.Y(v["p90"]):.1f}" stroke="{GREEN}" stroke-width="3" opacity=".4"/>')
        g.append(f'<circle class="f" style="animation-delay:{0.2 + 0.15 * m:.2f}s" cx="{ax.X(m):.1f}" cy="{ax.Y(v["mean"]):.1f}" r="10" fill="{GREEN}"/>')
        g.append(text(ax.X(m) + 16, ax.Y(v['mean']) - 12, f'{v["mean"]:.1f}', 22, GREEN, weight=700))
    g.append(text(ax.X(11), ax.Y(one / 11 ** 0.5) - 20, f'{e13["n_labs"]} labs today', 22, INK2, 'end'))
    g.append(text(ax.X(6.3), ax.Y(one / 6.3 ** 0.5) - 58, 'dashed: one over root n', 19, FAINT))
    rx = 1080; a, b = ref[str(ms[0])]['mean'], ref[str(ms[-1])]['mean']
    g.append(text(rx, ax.y0 - 28, 'THE REFERENCE', 22, MUTE, extra='letter-spacing="2.2"'))
    g.append(text(rx, ax.y0 + 74, f'{a:.1f} &#8594; {b:.1f}', 72, GREEN, weight=700))
    for k, line in enumerate((f'from one lab to {NUMBERS[ms[-1]]}:', 'every lab that joins sharpens', 'the map for everyone')):
        g.append(text(rx, ax.y0 + 116 + 30 * k, line, 24, INK2))
    g.append(text(rx, ax.y0 + 300, 'your own baseline', 22, PINK, weight=700))
    own = e13['own_baseline_by_plates']
    g.append(text(rx, ax.y0 + 340, f'{own["1"]["mean"]:.1f} &#8594; {own["8"]["mean"]:.1f}', 40, INK2, weight=700))
    g.append(text(rx, ax.y0 + 372, 'from one plate to eight, then flat', 20, INK2))
    return svg(1600, 530, g, aria='The disagreement between two references falls as each is built from more labs, from 6.2 spreads with one lab to 2.8 with five.')


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
    g.append(text(rx, ax.y0 - 28, 'EVERY LAB MOVES UP', 22, MUTE, extra='letter-spacing="2.2"'))
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
    fig = lambda n: f'<span style="color:{D_TEXT}; font-weight:500;">Fig. {n}</span>'
    card = lambda left, width, inner, pad='14px 22px': (f'<div style="position:absolute; left:{left}px; top:200px; width:{width}px; height:380px; '
                                                          f'{CARD_ON_DARK} padding:{pad}; display:flex; align-items:center; overflow:hidden;">{inner}</div>')
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">Eleven labs, eleven normals</span>'
    apart = (f'<div class="r" style="animation-delay:1.3s; position:absolute; left:56px; top:236px; width:360px; display:flex; flex-direction:column; gap:12px;">'
             f'<span style="{SANS} font-size:84px; font-weight:700; letter-spacing:-0.045em; line-height:0.92; color:{D_PINK};">{one:.1f}</span>'
             f'<span style="{MONO} font-size:13px; line-height:1.6; color:{D_SOFT};">spreads between one lab&#8217;s<br>normal and another&#8217;s</span></div>')
    n_labs = NUMBERS[e13['n_labs']].capitalize()
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(5, dark=True)}
  {header('05', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">{n_labs} labs. <span style="color:{D_PINK};">{n_labs} normals.</span></h2>
  <h2 class="s s1" style="{H}">Where you sit <span style="color:{D_PINK};">predicts what you measure.</span></h2>
  <div class="s s0">{apart}{card(456, 768, field_map(B, lab, pca, both=False), '12px 20px')}</div>
  <div class="s s1">{card(56, 1168, answer_chart(e10, lab), '0 22px')}</div>
  <div class="s s0" style="{FOOT}">{fig(2)} {pca["wells"]:,} untreated wells, same line, same protocol. PCA, for the eye only. JUMP [7]</div>
  <div class="s s1" style="{FOOT}">{fig(3)} One point per batch: {a["n_batches"]} batches, {a["n_labs"]} labs. JUMP [7]. More: A8, A13, A14</div>
  <div style="position:absolute; right:56px; bottom:44px; {MONO} font-size:13px; color:{D_DIM};"><span data-h="hint">click &#8594; why the map matters</span></div>
</div>'''
    steps = {'tag': ['Eleven labs, eleven normals', 'Why the map matters'],
             'hint': ['click \u2192 why the map matters', 'click \u2192 start over']}
    return css, body, steps
