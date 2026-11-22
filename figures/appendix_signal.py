"""Appendix boards on what the images carry, written whole from results: A7 (how this differs from STR), A9 (does it
change the answer?), A10 (does it work without stains?), A14 (what the map buys) and A19 (what the machine learning is)."""

import base64
import glob
import json
import os

from parts import *
from appendix_kit import BOARD, H2, LEDE, FIGURE, NOTE, SUB, HALO_PANEL, top_line, card, who_uses


# ------------------------------------------------------------------ A7
def a7():
    e1 = results('e1.json')['all_sources']
    n = e1['n_features']
    # STR: seventeen loci, drawn as the ladder a capillary trace is read from
    rng = __import__('random').Random(7)
    ladder = ''.join(f'<rect x="{18 + k * 24}" y="{134 - h}" width="9" height="{h}" rx="2" fill="{INK}" opacity=".85"/>' for k, h in enumerate(40 + rng.randint(0, 70) for _ in range(17)))
    str_fig = (f'<svg viewBox="0 0 440 150" width="100%" aria-label="Seventeen bars, one per STR locus." style="display:block; max-height:176px;">{ladder}'
               f'<line x1="14" y1="134" x2="430" y2="134" stroke="{MUTE}" stroke-width="1.5"/></svg>')
    # Datum Line: every number per well, drawn as dots
    cols, pitch = 97, 6.4
    rows = -(-n // cols)
    dots = ''.join(f'<circle cx="{6 + (k % cols) * pitch:.1f}" cy="{6 + (k // cols) * pitch:.1f}" r="2" fill="{GREEN}"/>' for k in range(n))
    dl_fig = (f'<svg viewBox="0 0 {cols * pitch + 8:.0f} {rows * pitch + 8:.0f}" width="100%" aria-label="{n:,} dots, one per number measured in every well." style="display:block; width:100%; max-height:176px;">{dots}</svg>')
    stat = lambda big, small, colour: (f'<div style="display:flex; flex-direction:column; gap:2px; min-width:0;"><span style="{SANS} font-size:30px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{colour};">{big}</span>'
                                       f'<span style="{MONO} font-size:13px; color:{MUTE};">{small}</span></div>')
    panel = lambda title, colour, fig, stats, line, delay, grow: (
        f'<div class="r" style="animation-delay:{delay}s; flex:{grow}; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:12px; min-width:0;">'
        f'{label(title, colour)}<div style="height:176px; flex:none; display:flex; align-items:center; justify-content:center;">{fig}</div>'
        f'<div style="display:grid; grid-template-columns:repeat({len(stats)},minmax(0,1fr)); gap:14px;">{"".join(stat(b, s, colour) for b, s in stats)}</div>'
        f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK}; padding-top:8px; border-top:1px solid #eceff0;">{line}</span></div>')
    left = panel('STR &#183; DNA fingerprint', INK, str_fig, [('17', 'DNA markers'), ('periodic', 'per cell line [14]')],
                 'Standard test for identity.<br>Cannot say where or how the cells were grown.', 0.2, 1)
    right = panel('Datum Line', GREEN, dl_fig, [(f'{n:,}', 'numbers per well'), ('every batch', 'images already taken')],
                  'Shows where cells were made, next to other labs.<br>Cannot say which cell line it is.', 0.4, 1.9)
    seal = open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="54" height="54"')
    joint = (f'<div class="r" style="animation-delay:0.8s; display:flex; align-items:center; gap:18px; {CARD} padding:12px 20px;">'
             f'<span style="{MONO} font-size:14px; padding:6px 14px; border-radius:999px; border:1.5px solid {INK}; color:{INK};">identity &#183; STR</span>'
             f'<span style="{SANS} font-size:26px; color:{MUTE};">+</span>'
             f'<span style="{MONO} font-size:14px; padding:6px 14px; border-radius:999px; background:{GREEN}; color:#ffffff;">behaviour &#183; Datum Line</span>'
             f'<span style="{SANS} font-size:26px; color:{MUTE};">=</span>{seal}'
             f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">one record of the line</span>'
             f'<span style="{MONO} font-size:14px; color:{MUTE}; margin-left:auto;">natural first partner: STR testing services</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A7', 'if asked how this differs from STR', 'results/e1 &#183; ATCC [14]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">STR says which cells.<br><span style="color:{PINK};">Images say how they behave.</span></h2>
    <p style="{LEDE}">One cell line, U2OS, in all {e1["n_labs"]} labs.<br>Images still name the lab: {100 * e1["balanced_accuracy"]:.1f}% right.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0; align-items:stretch;">{left}{right}</div>
  {joint}
  <div class="note" style="{NOTE}">STR: 17 loci + amelogenin, ATCC [14] &#183; Datum Line: {e1["n_wells"]:,} untreated U2OS wells &#183; {e1["n_plates"]:,} plates &#183; {e1["n_labs"]} labs &#183; plates held out &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A9
def ramp(v, lo=(238, 241, 241), hi=(10, 104, 78)):
    """Agreement as a shade of the map's green: 0 (or less) near the panel, 1 the darkest."""
    v = min(max(v, 0), 1)
    return '#%02x%02x%02x' % tuple(round(a + (b - a) * v) for a, b in zip(lo, hi))


def rsl3_matrix(R):
    """A9's figure, the numbers behind 05's RSL3 tiles: one RSL3 well on each of 12 plates in four labs, every well against
    every other (cosine of the two effects). A lab's wells sit together, outlined; a well against itself is left blank.
    Right: each lab's wells, and its mean agreement with its own lab and with the other labs."""
    M = R['cosine_matrix']; names = M['order']; V = M['values']
    lab_of = [n.split()[0] for n in names]
    idx = sorted(range(len(names)), key=lambda i: (lab_number(lab_of[i]), i))
    labs = sorted(set(lab_of), key=lab_number)
    by = R['by_lab']
    assert all(by[l]['n_wells'] == lab_of.count(l) for l in labs), 'one row per well'
    c, x0, y0, n = (26 if len(idx) > 9 else 32), 92, 74, len(idx)
    g = [chart_title(0, 22, 'RSL3 at 10 &#181;M, every well against every other', 17)]
    for r, i in enumerate(idx):
        for q, j in enumerate(idx):
            fill = '#ffffff' if i == j else ramp(V[i][j])
            g.append(f'<rect x="{x0 + q * c + 1}" y="{y0 + r * c + 1}" width="{c - 2}" height="{c - 2}" rx="3" fill="{fill}"'
                     + (f' stroke="{GRID}" stroke-width="1"' if i == j else '') + '/>')
    xt = x0 + n * c + 34
    cols = ((xt + 22, 'wells'), (xt + 120, 'same lab'), (xt + 246, 'other labs'))
    mono = lambda x, y, t, size, fill, anchor='middle', weight=400: (f'<text x="{x:.1f}" y="{y:.1f}" {SVG_MONO} font-size="{size}" font-weight="{weight}" '
                                                                     f'fill="{fill}" text-anchor="{anchor}">{t}</text>')
    g += [mono(x, y0 - 12, t.upper(), 21, MUTE) for x, t in cols]
    start = 0
    for l in labs:
        k = lab_of.count(l); mid = y0 + (start + k / 2) * c
        g.append(f'<rect x="{x0 + start * c}" y="{y0 + start * c}" width="{k * c}" height="{k * c}" rx="4" fill="none" stroke="{INK}" stroke-width="2.2"/>')
        g.append(text(x0 - 12, mid + 8, lab_name(l), 24, INK, 'end'))
        g.append(text(x0 + (start + k / 2) * c, y0 - 12, lab_name(l), 21, INK2, 'middle'))
        own = by[l]['own_lab']
        g.append(mono(cols[0][0], mid + 7, f'{k}', 19, INK2)
                 + mono(cols[1][0], mid + 7, f'{own:.2f}' if own is not None else '&#8212;', 19, INK if own is not None else MUTE, weight=600)
                 + mono(cols[2][0], mid + 7, f'{by[l]["other_labs"]:.2f}', 19, INK2))
        if start:
            g.append(f'<path d="M {xt - 6} {y0 + start * c} L {xt + 322} {y0 + start * c}" stroke="{GRID}" stroke-width="1"/>')
        start += k
    ky = y0 + n * c + 34
    stops = ''.join(f'<stop offset="{v:g}" stop-color="{ramp(v)}"/>' for v in (0, 0.5, 1))
    g.append(f'<defs><linearGradient id="a9ramp">{stops}</linearGradient></defs>'
             f'<rect x="{x0}" y="{ky - 12}" width="156" height="14" rx="3" fill="url(#a9ramp)"/>'
             + mono(x0, ky + 20, '0', 21, MUTE) + mono(x0 + 156, ky + 20, '1', 21, MUTE)
             + text(x0 + 172, ky + 1, 'agreement &#183; 1 = same effect &#183; 0 = unrelated', 21, INK2))
    return svg(xt + 330, ky + 26, g, fit=True, aria=f'RSL3: {n} wells, one per plate, from {len(labs)} labs, each compared with every other. '
               'Wells of the same lab agree; wells of different labs mostly do not.')


WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']


def same_dose_view(R, SD):
    """05a's comparison, well by well: the RSL3 wells of the labs that ran it at the same dose, and their numbers among themselves."""
    M = R['cosine_matrix']; keep = [i for i, n in enumerate(M['order']) if n.split()[0] in SD['labs']]
    assert len(keep) == SD['n_wells']
    return {'cosine_matrix': {'order': [M['order'][i] for i in keep], 'values': [[M['values'][i][j] for j in keep] for i in keep]},
            'by_lab': SD['by_lab']}


def a9():
    """05's RSL3 at one dose, well by well: the small numbers behind its tiles, the eight known drugs on the same plates (5 uM in
    every lab), and DMSO against DMSO as the floor, every well measured against its own plate's DMSO wells. Lab 7, dosed at a
    sixteenth [7], is shown beside the comparison, never in it, with a same-dose check that its cells respond. Then the eight
    drugs at full scale (results/e8): which lab ran a drug moves how strong its effect looks."""
    e16 = results('e16-same-perturbation.json'); R = e16['RSL3']['result']; SD = e16['RSL3']['same_dose_only']; K = SD['compared']
    out = SD['left_out']['source_7']
    assert SD['dose_um'] == 10 and out['dose_um'] == 0.625 and SD['untreated_on_each_plate']['every_well_own_plate_dmso']
    e8 = results('e8-redteam.json'); C = e8['all_features']['compounds']
    s = [C[c]['effect_size']['share_of_variance_between_labs'] for c in C]
    # 17 Nov 2026 (the talk's index: "Reproducibility: who uses it, and how?"): one worked case, the drift check before a screen is read
    drift = results('e10-certificate-predicts-answer.json')['inside_labs']['drift_vs_agreement_with_own_baseline']
    assert drift['spearman'] < drift['null_5pct'] < 0, 'more drift, weaker drug answers, beyond the shuffled batches'
    labs = sorted(SD['labs'], key=lab_number)
    big = 'source_9'                                                   # the one lab on 1536-well plates among these [7]
    L = SD['lab_by_lab']; others = [l for l in labs if l != big]
    with_big = [L[l][big] for l in others]; without_big = L[others[0]][others[1]]
    assert max(with_big) < without_big, 'most of the gap sits beside the 1536-well lab'
    formula = open('figures/assets/a9-formula-card.html').read().replace('class="ap"', 'class="r"')
    cell = lambda v, colour=INK, weight=400: f'<span style="{MONO} font-size:15px; font-weight:{weight}; color:{colour}; text-align:right;">{v}</span>'
    head = lambda t: f'<span style="{MONO} font-size:13px; letter-spacing:0.08em; text-transform:uppercase; color:{MUTE}; text-align:right;">{t}</span>'
    n_drugs = len(SD['controls_on_the_same_plates'])
    rows = [(f'RSL3, {SD["dose_um"]:g} &#181;M', K['own_lab']['RSL3'], K['other_labs']['RSL3'], INK),
            (f'{n_drugs} known drugs, 5 &#181;M, median', K['own_lab']['controls_median'], K['other_labs']['controls_median'], INK2),
            ('DMSO vs DMSO', K['own_lab']['dmso_noise'], K['other_labs']['dmso_noise'], MUTE)]
    table = (f'<div style="display:grid; grid-template-columns:1fr 78px 92px; column-gap:10px; row-gap:5px; align-items:baseline;">'
             + '<span></span>' + head('same lab') + head('other labs')
             + ''.join(f'<span style="{SANS} font-size:15px; line-height:1.25; color:{INK};">{name}</span>{cell(f"{a:.2f}", col, 600)}{cell(f"{b:.2f}", col)}'
                       for name, a, b, col in rows) + '</div>')
    box = lambda title, inner, delay, colour=MUTE, grow=1: (f'<div class="r" style="animation-delay:{delay:.2f}s; flex:none; {CARD} padding:8px 18px; display:flex; '
                                                    f'flex-direction:column; justify-content:center; gap:6px; min-height:0;">{label(title, colour)}{inner}</div>')
    say = lambda t: f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{t}</span>'
    body = f'''<div style="{BOARD}">
  {top_line('A9', 'if asked whether it changes the answer', 'results/e16, e8, e10')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Same drug.<br><span style="color:{PINK};">Different answer.</span></h2>
    <p style="{LEDE}">Darker = more alike.</p>
  </div>
  {formula}
  <div style="display:grid; grid-template-columns:minmax(0,0.9fr) minmax(0,1.1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.3s; {FIGURE}">{rsl3_matrix(same_dose_view(R, SD))}</div>
    <div style="display:flex; flex-direction:column; justify-content:flex-start; gap:14px; min-height:0;">      <!-- two answers, stacked from the top -->
      {box(f'same {SD["n_plates"]} plates, each well against its own plate&#8217;s DMSO', table, 0.4, GREEN, 1.3)}
      {box('does it change the number?', say(f'Which lab ran it explains {100 * min(s):.0f}% to {100 * max(s):.0f}% of how strong a drug&#8217;s effect looks.'), 0.5, PINK)}
      {box('who uses it, and how', who_uses([('screening team', 'checks each batch&#8217;s controls before reading its drugs'),
                                             ('lab repeating a result', 'compares against the field&#8217;s normal, not only its own'),
                                             ('journal or funder', 'asks for the check with the raw images')]), 0.6, GREEN)}
      {box('worked case', say(f'{drift["n_labs"]} labs, {drift["n_batches"]} batches: the further a batch drifts from its lab&#8217;s first, the less its known drugs agree with that lab&#8217;s first answers (Spearman &#8722;{abs(drift["spearman"]):.2f}).'), 0.7, PINK)}
    </div>
  </div>
  <div class="note" style="{NOTE}">{WORDS[SD["n_wells"]].capitalize()} wells: an example, not proof &#183; {lab_name("source_7")}, dosed at a sixteenth, left out &#183; agreement = cosine of two wells&#8217; effects, each well minus its own plate&#8217;s DMSO wells &#183; {len(C)} drugs at full scale: {e8["n_plates"]:,} plates, {e8["n_labs"]} labs &#183; worked case: results/e10, each lab against its own first batch; shuffled batches pass &#8722;{abs(drift["null_5pct"]):.2f} one time in twenty &#183; JUMP [7]</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A10
def a10_bars(e17):
    """A10's bars: can one well tell which lab it came from, by each input on the same wells, against the shuffled floor.
    Returns the marks and their axes, which the drift strip under them shares."""
    im = e17['inputs']; bf = im['brightfield']; pop = e17['population']
    assert len({(im[k]['n_plates'], im[k]['n_labs'], im[k]['chance']) for k in im}) == 1, 'every row: same plates, same labs, same chance'
    shuffled = {'balanced_accuracy': sum(im[k]['shuffled_labels']['mean'] for k in im) / len(im), 'chance': pop['chance']}
    rows = [('six-dye profile', 'same wells', im['profile'], GREEN), ('DNA stain image', 'same wells', im['dna'], GREEN),
            ('brightfield image', 'same wells', bf, INK), ('labels shuffled', 'control', shuffled, FAINT)]
    P = 52
    ax = Axes(230, 64, 440, len(rows) * P, (0, 1), (0, len(rows)))
    g = [chart_title(0, 24, f'can one well tell which of {pop["n_labs"]} labs it came from?', 15), f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>'
                 + text(ax.X(v), ax.y0 + ax.h + 26, f'{100 * v:.0f}' + ('%' if v == 1 else ''), 19, MUTE, 'middle'))
    for k, (name, labs, r, colour) in enumerate(rows):
        c = ax.y0 + (k + 0.5) * P; acc = r.get('median_over_splits', r['balanced_accuracy'])     # median of 20 splits; the shuffled row has one
        g.append(text(ax.x0 - 14, c - 3, name, 21, PINK if colour == PINK else INK, 'end', 600 if colour == PINK else 400) + text(ax.x0 - 14, c + 19, labs, 17, MUTE, 'end'))
        g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.12 * k:.2f}s" x="{ax.x0}" y="{c - 14:.1f}" width="{ax.X(acc) - ax.x0:.1f}" height="28" rx="4" fill="{colour}"/>')
        g.append(f'<path d="M {ax.X(r["chance"]):.1f} {c - 20:.1f} L {ax.X(r["chance"]):.1f} {c + 20:.1f}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        g.append(text(ax.X(acc) - 12, c + 8, f'{100 * acc:.1f}%', 22, '#ffffff', 'end', 700) if acc > 0.3
                 else text(ax.X(r['chance']) + 12, c + 8, f'{100 * acc:.0f}%', 22, INK, 'start', 700))
    g.append(text(ax.X(pop['chance']) - 6, ax.y0 - 10, f'random guess, 1 in {pop["n_labs"]}', 17, INK))
    return g, ax


def a10_drift(e17, ax):
    """A10's strip under the bars: lab 2, batch by batch, by dye profile and by brightfield image. Returns its marks, its axes
    and the numbers the caption reads."""
    # lab 2, batch by batch: how far each batch sits from its first, by the dye profile (e9) and by the brightfield image (e15)
    from datetime import date
    g = []
    D = e17['lab_2_drift']
    B = results('e9-replay.json')['labs']['source_2']['batches']
    assert [b['from_baseline'] for b in B] == D['e9_from_baseline'] and [b['batch'] for b in B] == D['batches'], 'the brightfield drift is read on the same 13 batches'
    after = D['spearman_after_first_batch']                    # the first batch is 0 for every line by construction, so it is left out of the rank test
    d = {'by_profile': D['e9_from_baseline'], 'by_image': D['by_input']['brightfield'], 'spearman': after['with_e9_from_baseline']['brightfield'], 'n_batches': after['n_batches']}
    day = lambda iso: date.fromisoformat(iso).toordinal()
    t0, t1 = day(B[0]['date']), day(B[-1]['date'])
    m = Axes(ax.x0, ax.y0 + ax.h + 82, ax.w, 72, (t0, t1), (0, 1))
    g.append(chart_title(0, m.y0 - 18, f'does brightfield see {lab_name("source_2")} drift? &#183; each line scaled to its peak', 15))
    g.append(f'<rect x="{m.x0 - 8}" y="{m.y0 - 6}" width="{m.w + 16}" height="{m.h + 12}" fill="{PANEL}"/>')
    for name, vals, colour, y in (('dye profile', d['by_profile'], GREEN, m.y0 + 24), ('brightfield', d['by_image'], INK, m.y0 + 56)):
        top = max(vals)
        pts = [(m.X(day(b['date'])), m.Y(v / top)) for b, v in zip(B, vals)]
        g.append(f'<path d="M ' + ' L '.join(f'{x:.1f} {yy:.1f}' for x, yy in pts) + f'" fill="none" stroke="{colour}" stroke-width="2.6" stroke-linejoin="round"/>'
                 + ''.join(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="3.6" fill="{colour}"/>' for x, yy in pts))
        g.append(text(m.x0 - 14, y, name, 19, colour, 'end', 600 if colour == PINK else 400))
    first = date.fromordinal(t0)
    g.append(text(m.X(t0), m.y0 + m.h + 26, first.strftime('%b'), 16, MUTE, 'middle'))      # the first batch's month, then the 1st of each month after
    for mo in range(first.month + 1, date.fromordinal(t1).month + 1):
        g.append(text(m.X(day(f'{first.year}-{mo:02d}-01')), m.y0 + m.h + 26, date(2000, mo, 1).strftime('%b'), 16, MUTE, 'middle'))
    g.append(text(m.x0 + m.w + 14, m.y0 + 30, f'&#961; = {d["spearman"]:.2f}', 20, INK, 'start', 600)
             + text(m.x0 + m.w + 14, m.y0 + 54, f'{d["n_batches"]} batches', 16, MUTE) + text(m.x0 + m.w + 14, m.y0 + 74, 'after the first', 16, MUTE))
    return g, m, d


def a10_fair():
    """A10's right card: why the brightfield bet is fair, one well in brightfield and in the DNA stain."""
    uri = lambda f: 'data:image/jpeg;base64,' + base64.b64encode(open(f'figures/assets/{f}', 'rb').read()).decode()
    tile = lambda f, alt, cap, colour: (f'<div style="display:flex; flex-direction:column; gap:6px;"><img src="{uri(f)}" alt="{alt}" style="width:164px; height:280px; border-radius:10px; object-fit:cover; display:block; background:#000;">{label(cap, colour)}</div>')
    gone = ' &#183; '.join(f'<s>{v}</s>' for v in ('stain lot', 'dye lot', 'staining step'))
    return (f'<div class="r" style="animation-delay:0.4s; {CARD} padding:16px 20px; display:flex; flex-direction:column; gap:9px; min-width:0;">'
            f'{label("why the bet is fair", GREEN)}'
            f'<span style="{SANS} font-size:20px; font-weight:600; letter-spacing:-0.015em; line-height:1.18; color:{INK};">No dye: fewer things can go wrong</span>'
            f'<div style="display:flex; justify-content:space-between; align-items:baseline; gap:8px;"><span style="{MONO} font-size:14px; line-height:1.4; color:{MUTE};">{gone}</span>{label("A3")}</div>'
            f'<div style="display:flex; gap:12px; margin-top:auto;">' + tile('well-I01-brightfield.jpg', 'Brightfield image of well I01, plate 1053600681.', 'brightfield', INK)
            + tile('well-I01-dna.jpg', 'DNA channel of the same field.', 'DNA stain', GREEN) + '</div>'
            f'<span style="{MONO} font-size:13px; color:{MUTE};">same spot in one well &#183; lab 2</span></div>')


def a10():
    """Brightfield is the bet: the lab is named from a six-dye profile, a DNA image and a brightfield image of the same wells, on the
    same 8 labs and the same held-out batches, so every row has one chance level (results/e17); the same model with the labels
    shuffled is the floor. And brightfield follows lab 2's drift batch by batch much as the dye profile does (results/e17 against e9)."""
    e17 = results('e17-same-labs-every-input.json'); pop = e17['population']
    g, ax = a10_bars(e17)
    drift, m, d = a10_drift(e17, ax)
    g += drift
    chart = svg(770, m.y0 + m.h + 34, g, fit=True, aria=f'Balanced accuracy naming which of {pop["n_labs"]} labs a well came from, the same wells and held-out batches for every input: six-dye profiles, a DNA-stain image and a brightfield image all sit near 100%; with the labels shuffled, near the chance of 1 in {pop["n_labs"]}. '
                f'Below, lab 2&#8217;s 13 batches: the distance from its first batch by dye profile and by brightfield image rise and fall together (Spearman {d["spearman"]:.2f} over the {d["n_batches"]} batches after the first).')
    fair = a10_fair()
    body = f"""<div style="{BOARD}">
  {top_line('A10', 'if asked whether it works without stains', 'results/e17, e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Shown in fluorescence.<br><span style="color:{PINK};">Bet on brightfield.</span></h2>
    <p style="{LEDE}">Evidence: six dyes.<br>Product: no dye.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.2s; {FIGURE} flex-direction:column; gap:6px;">{chart}
      <span style="{SANS} font-size:17px; line-height:1.3; color:{MUTE};">Not yet the whole map: beyond each lab&#8217;s usual neighbour, brightfield and dye profile agree batch by batch no more than luck ({e17["nearest_lab"]["image_agrees_with_profile_permutation_null"]["brightfield"]["observed"]} of {e17["nearest_lab"]["image_agrees_with_profile_permutation_null"]["brightfield"]["n_batches"]} against {e17["nearest_lab"]["image_agrees_with_profile_permutation_null"]["brightfield"]["expected_mean"]:.0f}).</span></div>
    {fair}
  </div>
  <div class="note" style="{NOTE}">% named right, each lab counted equally, unseen batches &#183; one DMSO well per plate, {pop["n_plates"]:,} plates, the same wells and model for every row &#183; median of {len(e17["paired_splits"]["deal_seeds"])} splits of the batches &#183; profile without its {e17["settings"]["profile_features_dropped"]["count"]} frame-size columns &#183; shuffled: 5 seeds per input &#183; image model never trained on cells &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A14
def a14():
    """Board A14, for someone outside the field: the same known drugs, read three ways, agree more between labs on the map."""
    e12 = results('e12-field-normalization.json')
    E = e12['every_batch']
    n = E['n_batches']
    count = lambda v: int(v.split()[0])

    def strip(key):
        """raw -> usual fix -> the map, the last in green."""
        cells = [(E[key]['raw'], 'raw', MUTE), (E[key]['own'], 'usual fix', MUTE), (E[key]['field'], 'on the map', GREEN)]
        out = []
        for k, (v, name, colour) in enumerate(cells):
            if k:
                out.append(f'<span style="{SANS} font-size:26px; color:{MUTE}; padding-bottom:22px;">&#8594;</span>')      # AA (FAINT was 2.8:1)
            out.append(f'<div style="display:flex; flex-direction:column; gap:2px;"><span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.03em; '
                       f'line-height:1; color:{colour};">{v:.2f}</span><span style="{MONO} font-size:13px; color:{colour if k == 2 else MUTE};">{name}</span></div>')
        return f'<div style="display:flex; align-items:flex-end; gap:14px;">{"".join(out)}</div>'

    def waffle(better):
        cells = ''.join(f'<i style="display:block; width:14px; height:14px; border-radius:3px; background:{GREEN if k < better else GRID};"></i>' for k in range(n))
        return f'<div style="display:grid; grid-template-columns:repeat(25, 14px); gap:4px;">{cells}</div>'

    def half(question, key, scale):
        better = count(E[key]['field_better_than_own_in'])
        return (f'<div style="flex:1; display:flex; flex-direction:column; gap:14px;">'
                f'<span style="{SANS} font-size:22px; font-weight:600; letter-spacing:-0.01em; color:{INK};">{question}</span>'
                f'{strip(key)}<span style="{MONO} font-size:13px; color:{MUTE};">{scale}</span>'
                f'{waffle(better)}'
                f'<span style="display:flex; flex-direction:column; gap:2px;"><span style="{SANS} font-size:16px; color:{INK};"><b style="color:{GREEN};">{better} of {n} batches</b> higher on the map than with the usual fix</span>'
                f'<span style="{MONO} font-size:13px; color:{MUTE};">than raw: {E[key]["field_better_in"]}</span></span></div>')

    grid = [json.load(open(f)) for f in sorted(glob.glob('results/e12-field-normalization-*.json'))] + [e12]
    holds = lambda key: sum(count(v['every_batch'][key]['field_better_than_own_in']) > n / 2 for v in grid)
    cv = E['effect_size_cv_across_batches_within_lab']
    figure = (f'<div style="display:flex; gap:40px; align-items:stretch;">'
              + half('Do labs agree on what a drug does?', 'agree_field', '1 = every lab sees the same effect')
              + f'<div style="width:1px; background:{GRID};"></div>'
              + half('Can you still tell the drugs apart?', 'margin', 'gap to the nearest wrong drug &#183; higher is easier')
              + '</div>')
    body = f"""<div style="{BOARD}">
  {top_line('A14', 'if asked what the map buys', 'results/e12')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Same drug, two labs.<br><span style="color:{PINK};">Closer on the map.</span></h2>
    <p style="{LEDE}">{['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][len(e12["compounds"])].capitalize()} known drugs, {n} batches.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} padding:22px 28px; display:flex; align-items:center;">{figure}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Nothing lost', f'Right drug recognised: {E["matched"]["own"]:.2f} &#8594; {E["matched"]["field"]:.2f}<br>Matches its own past: {E["agree_own"]["own"]:.2f} &#8594; {E["agree_own"]["field"]:.2f}', 0.4, colour=GREEN)}
    {card('Holds', f'Labs agree more: {holds("agree_field")} of {len(grid)} ways of checking<br>Drugs stay apart: {holds("margin")} of {len(grid)}', 0.5, colour=GREEN)}
    {card('Not fixed yet &#183; drug strength', f'Varies batch to batch &#183; lower is better<br>raw {100 * cv["raw"]:.0f}% &#8594; usual fix {100 * cv["own"]:.0f}% &#8594; map {100 * cv["field"]:.0f}%: steadier than the usual fix, not yet as steady as raw', 0.6, colour=INK)}
  </div>
  <div class="note" style="{NOTE}">usual fix: each batch set against its own &#8220;normal&#8221;, its untreated wells &#183; map: against every other lab&#8217;s &#183; {e12["n_plates"]:,} plates &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A19
def a19_short():
    """A19's card on the image model: naming the lab from one brightfield or DNA picture (results/e17, as on A10)."""
    e15 = results('e17-same-labs-every-input.json') if os.path.exists('results/e17-same-labs-every-input.json') else None   # same labs, wells, split (A10)
    if e15 and 'balanced_accuracy' in e15['inputs'].get('brightfield', {}):
        def bar(name, shown):
            v = 100 * e15['inputs'][name]['median_over_splits']         # median of 20 splits (A10)
            return (f'<span style="display:flex; flex-direction:column; gap:3px;">'
                    f'<span style="display:flex; justify-content:space-between; {MONO} font-size:13px; line-height:1.2; color:{INK2};"><span>{shown} &#183; {e15["inputs"][name]["n_labs"]} labs</span><span>{v:.1f}%</span></span>'
                    f'<span style="display:block; height:8px; border-radius:4px; background:{PANEL};"><span style="display:block; height:100%; width:{v:.1f}%; border-radius:4px; background:{INK2};"></span></span></span>')
        short = (f'<span style="display:flex; flex-direction:column; gap:8px; padding-top:4px;">{bar("brightfield", "brightfield")}{bar("dna", "DNA stain")}'
                 f'<span style="{MONO} font-size:13px; line-height:1.3; color:{MUTE};">right lab, from one picture</span></span>')
    else:
        short = 'e15, running'
    return short


def a19_map(PW, PH):
    """A19's third picture: slide 04's map in small, lab 2 labelled where the fewest wells are."""
    import math
    import slide04
    # 3: the map, slide 04's projection in small: lab 2 in pink, the other labs in green
    rows = slide04.embedding()
    others = sorted({r['lab'] for r in rows if r['lab'] != 'source_2'}, key=lab_number)
    shade = dict(zip(others, greens(len(others))))
    ax, cloud = slide04.map_axes(rows, 4, 4, PW - 8, PH - 8, pad=0.06)
    mine = [r for r in rows if r['lab'] == 'source_2']
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" rx="10" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::5], shade[l], 1.7) for l in others] + [cloud(mine[::3], PINK, 1.9)]
    pts = [(ax.X(float(r['pc1'])), ax.Y(float(r['pc2']))) for r in rows[::5]]
    cx = sum(ax.X(float(r['pc1'])) for r in mine) / len(mine); cy = sum(ax.Y(float(r['pc2'])) for r in mine) / len(mine)
    lw, lh = 84, 16                                       # the label goes where the fewest wells are, close to lab 2
    best = min(((sum(1 for px, py in pts if x - 4 <= px <= x + lw + 4 and y - lh - 4 <= py <= y + 4) * 40 + math.hypot(x + lw / 2 - cx, y - lh / 2 - cy), x, y)
                for x in range(int(ax.x0) + 8, int(ax.x0 + ax.w - lw - 8), 4) for y in range(int(ax.y0) + lh + 8, int(ax.y0 + ax.h - 8), 4)))
    g.append(f'<text x="{best[1]}" y="{best[2]}" style="{MONO}" font-size="14" font-weight="600" fill="{PINK}"{HALO_PANEL}>lab 2</text>')
    mapfig = svg(PW, PH, g, css_width=f'{PW}px', aria='Untreated wells from 11 labs as points, one shade of green per lab; lab 2 in pink, apart from the others.')
    return mapfig


def a19_sketch(PW, PH):
    """A19's fourth picture: the correction as a sketch, your batch moved onto the map."""
    import math
    # 4: the correction, drawn as a sketch: your batch, off the map, moved onto it
    flower = lambda x0, y0, R, n: [(x0 + R * math.sqrt(i / n) * math.cos(2.39996 * i), y0 + R * math.sqrt(i / n) * math.sin(2.39996 * i)) for i in range(1, n + 1)]
    T = lambda x, y, s, colour=MUTE: f'<text x="{x}" y="{y}" style="{MONO}" font-size="14" fill="{colour}" text-anchor="middle">{s}</text>'
    mx, my = 178, PH / 2 + 8
    sketch = ([f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{GREEN}" fill-opacity="0.55"/>' for x, y in flower(mx, my, 58, 70)]
              + [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="none" stroke="{PINK}" stroke-width="1.4"/>' for x, y in flower(52, 52, 26, 16)]
              + [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PINK}"/>' for x, y in flower(mx, my, 26, 16)]
              + [f'<path d="M 84 56 Q 116 58 130 92" fill="none" stroke="{GREEN}" stroke-width="2.4" stroke-linecap="round"/>'
                 f'<path d="M 122 86 L 131 95 L 134 82" fill="none" stroke="{GREEN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
                 T(52, 98, 'your batch', PINK), T(mx, PH - 10, 'the map', GREEN)])
    move = svg(PW, PH, sketch, css_width=f'{PW}px', aria='Sketch: your batch, pink rings off the map, is moved by the correction onto the map, among the green wells.')
    return move


def a19():
    """Four steps in one figure, each a picture of the same height: the well, its numbers, the map (slide 04's projection) and the
    correction; the cards under it hold the evidence for the two steps that carry a number."""
    e1 = results('e1.json')['all_sources']; e12 = results('e12-field-normalization.json')
    short = a19_short()
    PW, PH = 252, 196                                     # every picture the same box
    panel = lambda k, title, colour, picture, cap: (
        f'<div style="flex:1 1 0; min-width:0; display:flex; flex-direction:column; gap:10px;">{label(f"{k} &#183; {title}", colour)}'
        f'<div style="height:{PH}px; display:flex; align-items:center; justify-content:center;">{picture}</div>'
        f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE};">{cap}</span></div>')
    arrow = (f'<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" style="flex-shrink:0; margin-top:{27 + PH / 2 - 14:.0f}px;">'
             f'<path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="{GREEN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    # 1: one untreated well, two ways to image it
    uri = lambda f: 'data:image/jpeg;base64,' + base64.b64encode(open(f'figures/assets/{f}', 'rb').read()).decode()
    tile = lambda f, alt, cap: (f'<div style="display:flex; flex-direction:column; gap:5px;"><img src="{uri(f)}" alt="{alt}" style="width:118px; height:{PH - 22}px; border-radius:10px; object-fit:cover; display:block; background:#000;">'
                                f'<span style="{MONO} font-size:13px; line-height:1; color:{INK2};">{cap}</span></div>')
    img = ('<div style="display:flex; gap:10px;">' + tile('well-I01-brightfield.jpg', 'Brightfield image of one untreated well.', 'brightfield')
           + tile('well-I01-dna.jpg', 'DNA channel of the same field.', 'DNA stain') + '</div>')
    # 2: the numbers
    numbers = (f'<div style="display:flex; flex-direction:column; gap:6px;"><span style="{SANS} font-size:56px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{e1["n_features"]:,}</span>'
               f'<span style="{SANS} font-size:17px; line-height:1.3; color:{INK2};">numbers per well</span></div>')
    mapfig = a19_map(PW, PH)
    move = a19_sketch(PW, PH)
    figure = (panel(1, 'an image', INK, img, 'one untreated well &#183; JUMP [7]') + arrow
              + panel(2, 'numbers', MUTE, numbers, 'standard software today: size, shape, brightness, texture') + arrow
              + panel(3, 'the map', GREEN, mapfig, 'each lab placed on the other labs&#8217; scale, never its own') + arrow
              + panel(4, 'the correction', INK, move, 'one per batch, fitted on your untreated wells &#183; sketch &#183; A14'))
    body = f"""<div style="{BOARD}">
  {top_line('A19', 'if asked what the machine learning is', 'results/e1, e12, e17')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Image in.<br><span style="color:{GREEN};">Position and correction out.</span></h2>
    <p style="{LEDE}"></p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} padding:17px 22px 14px; gap:10px; align-items:flex-start;">{figure}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('AI image model next &#183; A10', short, 0.6, 1.3, MUTE)}
  </div>
  <div class="note" style="{NOTE}">Correction, per batch on {e12["k"]} components: x&#8242; = C<sub style="{SUB}">field</sub><sup style="{SUB}">&#189;</sup> C<sub style="{SUB}">batch</sub><sup style="{SUB}">&#8722;&#189;</sup> (x &#8722; m<sub style="{SUB}">batch</sub>) &#183; every script: github.com/kat-titter/datum-line/analysis</div>
</div>"""
    return BASE_CSS, body, None
