"""Slide 05: one lab, four clicks. Written whole from results/e9, e1b, e2 and e10."""
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
    g.append(text(ax.X(day(low['date'])) + 18, ax.Y(low['cells_per_well']) + 7, f"{low['cells_per_well']:.0f}: the lab sees this one", 20, INK2))
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


def field_map(B, lab, pca):
    rows = list(csv.DictReader(open('results/e2-embedding.csv')))
    first = set(B[0]['plates']) | set(B[1]['plates'])
    last = set(B[-1]['plates'])
    others = sorted({r['lab'] for r in rows if r['lab'] != lab}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    xs = sorted(float(r['pc1']) for r in rows); ys = sorted(float(r['pc2']) for r in rows)
    q = lambda v, p: v[int(p * (len(v) - 1))]
    ax = Axes(84, 20, 1010, 540, (q(xs, .005), q(xs, .995)), (q(ys, .005), q(ys, .995)))
    clampx = lambda v: ax.X(min(max(v, ax.xlim[0]), ax.xlim[1]))
    clampy = lambda v: ax.Y(min(max(v, ax.ylim[0]), ax.ylim[1]))
    cloud = lambda pts, fill, r, extra='': (f'<g fill="{fill}" {extra}>' + ''.join(
        f'<circle cx="{clampx(float(p["pc1"])):.0f}" cy="{clampy(float(p["pc2"])):.0f}" r="{r}"/>' for p in pts) + '</g>')
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::3], colour[l], 3.6, 'opacity="0.75"') for l in others]
    mine = [r for r in rows if r['lab'] == lab]
    g.append(cloud([r for r in mine if r['plate'] in first], PALE_PINK, 3.6, 'opacity="0.9"'))
    g.append(cloud([r for r in mine if r['plate'] in last], PINK, 4.2))
    v1, v2 = [round(100 * v, 1) for v in pca['variance_explained']]
    g.append(f'<path d="M {ax.x0} {ax.y0} L {ax.x0} {ax.y0 + ax.h} L {ax.x0 + ax.w} {ax.y0 + ax.h}" fill="none" stroke="{MUTE}" '
             f'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 44, f'PC 1 ({v1}% of variance)', 26, INK2, 'middle'))
    g.append(f'<g transform="translate({ax.x0 - 30},{ax.y0 + ax.h / 2}) rotate(-90)">{text(0, 0, f"PC 2 ({v2}% of variance)", 26, INK2, "middle")}</g>')
    lx, ly = ax.x0 + ax.w + 44, ax.y0 + 24
    g.append(text(lx, ly, 'LAB', 24, MUTE, extra='letter-spacing="2"'))
    legend = [(f'{lab_name(lab)}, June', PALE_PINK, True), (f'{lab_name(lab)}, October', PINK, True)] + [(lab_name(l), colour[l], False) for l in others]
    for k, (name, c, own) in enumerate(legend):
        y = ly + 44 + k * 42
        g.append(f'<circle cx="{lx + 11}" cy="{y - 9}" r="11" fill="{c}"/>' + text(lx + 36, y, name, 28, PINK if own else INK2, weight=700 if own else 400))
    return svg(1460, 640, g, aria='Principal components of untreated wells, one shade of green per lab; lab 2 in June and lab 2 in October sit in different places.')


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
    g += [dot(p, '#8fbfae', 6, 'opacity="0.8"') for p in pts if p['lab'] != lab and not p['positive_controls_failed']]
    g += [f'<path d="M {ax.X(p["drift"]) - 7:.1f} {ax.Y(p["agree_own_baseline"]) - 7:.1f} l 14 14 m 0 -14 l -14 14" stroke="{MUTE}" stroke-width="2.5" stroke-linecap="round"/>' for p in failed]
    g += [dot(p, PINK, 9, f'stroke="{PANEL}" stroke-width="2"') for p in pts if p['lab'] == lab]
    out = [p for p in pts if p['lab'] == lab and p['outside']]
    g += [f'<circle cx="{ax.X(p["drift"]):.1f}" cy="{ax.Y(p["agree_own_baseline"]):.1f}" r="15" fill="none" stroke="{PINK}" stroke-width="2"/>' for p in out]
    cx, cy = sum(ax.X(p['drift']) for p in out) / len(out), min(ax.Y(p['agree_own_baseline']) for p in out)
    g.append(text(cx, cy - 50, f'ringed: {lab_name(lab)}&#8217;s last three batches', 22, PINK, 'middle', 700))
    g.append(text(ax.X(1.2), ax.Y(0.62), f'{lab_name(lab)} in pink, every other lab in green', 20, MUTE))
    if failed:
        fx, fy = max(ax.X(p['drift']) for p in failed) + 18, sum(ax.Y(p['agree_own_baseline']) for p in failed) / len(failed)
        g.append(text(fx, fy + 2, 'known answer failed (A8)', 20, MUTE))
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    half = e10['sensitivity']['split half: drift and effect from different DMSO wells']['drift_vs_agreement_with_own_baseline']
    two = e10['flagged_against_unflagged'][lab]['with_own_baseline']
    rx = 1080
    g.append(text(rx, ax.y0 - 28, 'INSIDE LABS', 22, MUTE, extra='letter-spacing="2.2"'))
    g.append(text(rx, ax.y0 + 74, f'&#961; = &#8722;{abs(a["spearman"]):.2f}', 72, PINK, weight=700))
    for k, line in enumerate(('the further a batch drifts from its', 'lab&#8217;s baseline, the less its drug', 'answers agree with that baseline')):
        g.append(text(rx, ax.y0 + 116 + 28 * k, line, 22, INK2))
    without = e10['sensitivity'][f'without {lab}']['drift_vs_agreement_with_own_baseline']
    g.append(text(rx, ax.y0 + 210, f'{a["n_batches"]} batches, {a["n_labs"]} labs; shuffled {a["null_mean"]:+.2f}'.replace('-', '&#8722;'), 20, FAINT))
    g.append(text(rx, ax.y0 + 238, f'without {lab_name(lab)} &#8722;{abs(without["spearman"]):.2f}; from different wells &#8722;{abs(half["spearman"]):.2f}', 20, FAINT))
    g.append(text(rx, ax.y0 + 300, f'{lab_name(lab)}&#8217;s agreement with its June answer', 22, GREEN, weight=700))
    g.append(text(rx, ax.y0 + 340, f'{two["unflagged"]:.2f}', 40, INK2, weight=700))
    g.append(text(rx + 96, ax.y0 + 340, 'before the flag', 20, INK2))
    g.append(text(rx, ax.y0 + 384, f'{two["flagged"]:.2f}', 40, PINK, weight=700))
    g.append(text(rx + 96, ax.y0 + 384, 'after it', 20, INK2))
    return svg(1600, 530, g, aria='Drift from baseline against agreement of drug answers for every batch of every lab; agreement falls as drift rises.')


def build():
    lab = 'source_2'
    R = results('e9-replay.json')['labs'][lab]; B = R['batches']
    e10 = results('e10-certificate-predicts-answer.json')
    drift = results('e1b-drift-source_2.json')
    pca = results('e2-plate-position-1053600681.json')['pca']
    last, flag = B[-1], next(b for b in B if b['verdict'] == 'outside')
    near = lab_name(last['nearest_other'])
    same, far = drift['bins'][0], drift['bins'][-1]
    a = e10['inside_labs']['drift_vs_agreement_with_own_baseline']

    css = BASE_CSS + '''
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1, .step-2 .s2, .step-3 .s3 { opacity: 1; pointer-events: auto; }
    .flow .s .f, .flow .s .r, .flow .s .bar { animation-play-state: paused; }
    .step-0 .s0 .f, .step-1 .s1 .f, .step-2 .s2 .f, .step-3 .s3 .f,
    .step-0 .s0 .r, .step-1 .s1 .r, .step-2 .s2 .r, .step-3 .s3 .r { animation-play-state: running; }
    .flow { cursor: pointer; }
'''
    H = (f'position:absolute; left:56px; top:86px; width:760px; margin:0; {SANS} font-size:44px; font-weight:600; '
         f'letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};')
    FOOT = f'position:absolute; left:56px; bottom:44px; width:1010px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    LEAD = f'display:block; {MONO} font-size:15px; line-height:1.45; color:{D_PINK}; padding-bottom:4px;'
    fig = lambda n: f'<span style="color:{D_TEXT}; font-weight:500;">Fig. {n}</span>'
    card = lambda left, width, inner, pad='14px 22px': (f'<div style="position:absolute; left:{left}px; top:200px; width:{width}px; height:380px; '
                                                          f'{CARD_ON_DARK} padding:{pad}; display:flex; align-items:center; overflow:hidden;">{inner}</div>')
    chip = (f'<span style="{MONO} font-size:13px; padding:4px 10px; border-radius:999px; border:1px solid {D_PINK}; color:{D_PINK}; '
            f'white-space:nowrap;">{lab_name(lab)} &#183; June to October 2021</span>')
    right = (f'<span style="display:flex; gap:12px; align-items:baseline;">{chip}'
             f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">What its own lab can see</span></span>')
    big = lambda n, lines: (f'<div style="position:absolute; right:56px; top:82px; display:flex; align-items:center; gap:18px;">'
                            f'<span style="{SANS} font-size:96px; font-weight:700; letter-spacing:-0.045em; line-height:0.9; color:{D_PINK};">{n}</span>'
                            f'<span style="display:flex; flex-direction:column; gap:6px;">' + ''.join(
                                f'<span style="{MONO} font-size:13px; color:{c};">{t}</span>' for t, c in lines) + '</span></div>')
    pill = (f'<div style="position:absolute; right:56px; top:96px; {MONO} font-size:15px; padding:8px 16px 8px 10px; display:flex; align-items:center; '
            f'gap:8px; border-radius:999px; border:2px solid {D_GREEN}; color:{D_GREEN};">'
            f'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="{D_GREEN}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/></svg><span>local QC passed</span></div>')
    seven = (f'<div style="position:absolute; left:56px; top:236px; width:360px; display:flex; flex-direction:column; gap:12px;">'
             f'<span style="{SANS} font-size:84px; font-weight:700; letter-spacing:-0.045em; line-height:0.92; color:{D_PINK};">{far["ratio_to_same_batch"]:.0f}&#215;</span>'
             f'<span style="{MONO} font-size:13px; line-height:1.6; color:{D_SOFT};">two plates of one lab sit<br><span style="color:{D_TEXT};">{same["median"]:.1f}</span> '
             f'spreads apart in the same batch<br><span style="color:{D_TEXT};">{far["median"]:.1f}</span> apart {far["gap"]} later</span></div>')

    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(5, dark=True)}
  {header('05', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">It passed every check.</h2>
  <h2 class="s s1" style="{H}">By October, <span style="color:{D_PINK};">nearer {near} than itself.</span></h2>
  <h2 class="s s2" style="{H}">Same lab, <span style="color:{D_PINK};">two different places.</span></h2>
  <h2 class="s s3" style="{H}">The same drug, <span style="color:{D_PINK};">a different answer.</span></h2>
  <div class="s s0">{pill}</div>
  <div class="s s1">{big(f'{last["from_baseline"]:.1f}', [('spreads from its own June baseline', D_SOFT), (f'{last["to_nearest_other"]:.1f} to {near}', D_TEXT), (f'cells per well {last["cells_per_well"]:.0f}: inside its own range', D_SOFT)])}</div>
  <div class="s s0 s1" style="opacity:1;">{card(56, 572, cell_count_chart(B))}</div>
  <div class="s s1">{card(652, 572, distance_chart(B))}</div>
  <div class="s s2"><span style="position:absolute; left:56px; top:146px; {SANS} font-size:17px; line-height:1.4; color:{D_DIM};">Same lab, same line, same protocol.</span>{seven}
    {card(456, 768, field_map(B, lab, pca), '12px 20px')}</div>
  <div class="s s3">{card(56, 1168, answer_chart(e10, lab), '0 22px')}</div>
  <div class="s s0" style="{FOOT}">Cells per untreated well, {lab_name(lab)}, {len(B)} batches, June to October 2021. <span style="color:{D_TEXT};">Click for what only the field can see.</span></div>
  <div class="s s1" style="{FOOT}">{fig(3)} Left: mean cells per untreated well, per batch. Right: median distance of each batch&#8217;s plates from the lab&#8217;s first batch, and to the nearest other lab&#8217;s centre. Features scaled on the other {len(R["reference_labs"])} labs, {R["n_reference_wells"]:,} wells, {R["n_features"]:,} features [7]. Fluorescence; brightfield is the bet. results/e9</div>
  <div class="s s2" style="{FOOT}"><span style="{LEAD}">Your own past is not a reference. The field is.</span>{fig(4)} PCA of {pca["wells"]:,} untreated wells, {pca["wells_per_plate"]} per plate. Distances are measured in all {R["n_features"]:,} features, not in this projection. results/e2, e1b</div>
  <div class="s s3" style="{FOOT}"><span style="{LEAD}">The number on the certificate predicts how far your answers have moved.</span>{fig(5)} One point per batch, {a["n_batches"]} batches, {a["n_labs"]} labs, {e10["n_plates"]:,} plates. Agreement: cosine between a batch&#8217;s effect of {len(e10["compounds_pooled"])} positive controls and its lab&#8217;s first-batch effect. &#961; is Spearman after removing each lab&#8217;s mean [7]. More: A8, A9. results/e10</div>
  <div style="position:absolute; right:56px; bottom:44px; {MONO} font-size:13px; color:{D_DIM};"><span data-h="hint">click &#8594; the field</span></div>
</div>'''
    # the cell-count card stays for the first two states
    body = body.replace('<div class="s s0 s1" style="opacity:1;">', '<div class="s s01">')
    css += '    .step-0 .s01, .step-1 .s01 { opacity: 1; } .step-0 .s01 .f, .step-1 .s01 .f { animation-play-state: running; }\n'
    steps = {'tag': ['What its own lab can see', 'Four months later', 'Where the wells sit', 'The same drug, a different answer'],
             'hint': ['click → the field', 'click → the map', 'click → the drug', 'click → start over']}
    return css, body, steps
