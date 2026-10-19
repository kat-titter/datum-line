"""Appendix boards written whole from results: A4, A7 to A24 (A16 aside), the bars on A3, and the index that lists them."""
import glob
import json
import base64
import os
import re

from parts import *

BOARD = (f'width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 44px; display:flex; flex-direction:column; gap:14px; '
         f'{LIGHT_BG} position:relative; z-index:0; overflow:hidden;')
H2 = f'margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; flex-shrink:0;'
LEDE = f'margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE}; flex-grow:1;'
FIGURE = (f'box-sizing:border-box; background: linear-gradient(90deg, #be1e74, #0f8f6c) top / 100% 3px no-repeat, #ffffff; '
          f'border-radius:16px; padding:17px 22px 14px; box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 16px 40px rgba(20,23,26,0.10); '
          f'display:flex; align-items:stretch; min-height:0; min-width:0;')
NOTE = f'{MONO} font-size:13px; line-height:1.5; color:{MUTE};'
SUB = 'font-size:13px; line-height:0;'                  # sub- and superscripts in a NOTE line, without moving the line
HALO_PANEL = f' stroke="{PANEL}" stroke-width="4" stroke-linejoin="round" paint-order="stroke"'   # a label's halo on a map panel


def top_line(code, asked, tag=''):
    back = f' &#183; from slide {BEHIND[code]}' if code in BEHIND else ''
    right = f'<span style="{MONO} font-size:13px; letter-spacing:0.06em; color:{MUTE};">{tag.lower()}</span>' if tag else ''
    return watermark(code) + header(f'{code} &#183; {asked}{back}', '', right_html=right or ' ')


def card(title, body, delay, grow=1, colour=PINK):
    return (f'<div class="r" style="animation-delay:{delay:.2f}s; flex:{grow}; {CARD} padding:12px 18px; display:flex; flex-direction:column; gap:5px;">'
            f'{label(title, colour)}<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{body}</span></div>')


# ------------------------------------------------------------------ A8
def plate_map(x, y, title, sub, labelled, lookalike, P=13, colour=GREEN):
    """A 384-well plate: filled dots for `lookalike`, rings for `labelled`. A8 draws the field's answer in green; A18 draws your controls in pink."""
    k = P / 13
    g = [text(x, y - 34, title, 22, INK, weight=700), text(x, y - 10, sub, 20, MUTE)] if title else []
    g.append(f'<rect x="{x - 8}" y="{y - 2}" width="{24 * P + 16}" height="{16 * P + 12}" rx="10" fill="{PANEL}"/>')
    for r, row in enumerate('ABCDEFGHIJKLMNOP'):
        for c in range(1, 25):
            well = f'{row}{c:02d}'
            cx, cy = x + (c - 0.5) * P, y + 4 + (r + 0.5) * P
            if well in lookalike:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="{5.2 * k:g}" fill="{colour}"/>')
            else:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="{2.2 * k:.3g}" fill="#c3c9cb"/>')
            if well in labelled:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="{8.5 * k:.3g}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    return g


def tile(big, small, colour, delay):
    return (f'<div class="r" style="animation-delay:{delay:.2f}s; flex:1; {CARD} padding:12px 20px; display:flex; flex-direction:column; gap:4px;">'
            f'<span style="{SANS} font-size:30px; font-weight:700; letter-spacing:-0.02em; line-height:1.1; color:{colour};">{big}</span>{label(small)}</div>')


SHARE = {'a quarter': ('&#188;', 0.25), 'a third': ('&#8531;', 1 / 3), 'half': ('&#189;', 0.5)}   # the rule's words, as a symbol and a number


def a8():
    known = results('e11-known-answer.json')
    lab = known['failed'][0]['lab']
    B = known['labs'][lab]['batches']
    n_batches = sum(len(v['batches']) for v in known['labs'].values())
    failed = known['failed']; n_failed_plates = sum(f['n_plates'] for f in failed)
    replay = {b['batch']: b for b in results('e9-replay.json')['labs'][lab]['batches']}
    also_outside = sum(replay[f['batch']]['verdict'] == 'outside' for f in failed)
    good = next(p for p in known['probe'] if p['batch_verdict'] == 'came out')
    bad = next(p for p in known['probe'] if p['batch_verdict'] == 'failed' and not p['wells_that_look_like_it'])
    share = re.search(r'effect size is below (.+?) of the lab', known['rule']).group(1)     # the rule's size threshold, in its own words
    sym, frac = SHARE[share]
    line = frac * known['labs'][lab]['median_size']                                          # the size the rule fails a batch under
    assert all(b['size'] < line for b in B if b['verdict'] == 'failed'), 'the dashed line separates the failed batches'
    # 04's fig 3 (drift against agreement with its own first answer), with and without the batches that failed here
    e10 = results('e10-certificate-predicts-answer.json')
    rho = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
    rho_ok = e10['sensitivity']['without batches whose positive controls failed']['drift_vs_agreement_with_own_baseline']
    assert rho['n_batches'] - rho_ok['n_batches'] == len(failed), 'fig 3 loses exactly these batches'
    ax = Axes(96, 64, 600, 250, (0, len(B)), (0, 36))
    run = lambda b: re.findall(r'\d+', b['batch'])[0]
    g = ax.frame((0, 10, 20, 30), [(k + 0.5, run(b)) for k, b in enumerate(B)], 'size of the known drugs&#8217; effect',
                 'batch, in run order', f'{lab_name(lab)} &#183; did the known drugs work?')
    for k, b in enumerate(B):
        bad_batch = b['verdict'] == 'failed'
        h = ax.Y(0) - ax.Y(b['size'])
        g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.06 * k:.2f}s" x="{ax.X(k + 0.18):.1f}" y="{ax.Y(b["size"]):.1f}" '
                 f'width="{ax.X(0.64) - ax.X(0):.1f}" height="{h:.1f}" rx="3" fill="{INK if bad_batch else FAINT}"/>')
        if b['batch'] in (good['batch'], bad['batch']):
            g.append(text(ax.X(k + 0.5), min(ax.Y(b['size']), ax.Y(line)) - 10, '&#9660;', 19, INK, 'middle'))   # over the fail line, never on it
    g.append(f'<path d="M {ax.x0} {ax.Y(line):.1f} L {ax.x0 + ax.w + 4} {ax.Y(line):.1f}" stroke="{INK2}" stroke-width="2" stroke-dasharray="6 5"/>'
             + text(ax.x0 + ax.w + 10, ax.Y(line) + 6, f'{sym} of usual', 18, INK2))     # the fail line, drawn where the rule puts it
    fk = [k for k, b in enumerate(B) if b['verdict'] == 'failed']; cx = ax.X((fk[0] + fk[-1] + 1) / 2)
    g.append(text(cx, ax.Y(14), f'{len(failed)} batches', 22, INK, 'middle', 700) + text(cx, ax.Y(14) + 28, f'{n_failed_plates} plates', 22, INK, 'middle', 700))
    x2 = 820
    g.append(chart_title(x2, 36, 'where does the known drug show?', 20))
    g += plate_map(x2, 112, '&#9660; batch that worked', f'{lab_name(lab)} &#183; batch {run(good)}', set(good['wells_the_map_says_hold_it']), set(good['wells_that_look_like_it']))
    g += plate_map(x2 + 380, 112, '&#9660; batch that failed', f'{lab_name(lab)} &#183; batch {run(bad)}', set(bad['wells_the_map_says_hold_it']), set(bad['wells_that_look_like_it']))
    ky = 366
    g.append(f'<circle cx="{x2 + 8}" cy="{ky - 6}" r="8.5" fill="none" stroke="{INK}" stroke-width="1.8"/>' + text(x2 + 26, ky, 'where the layout says it is', 19, INK2))
    g.append(f'<circle cx="{x2 + 318}" cy="{ky - 6}" r="5.2" fill="{GREEN}"/>' + text(x2 + 332, ky, 'where the drug shows', 19, INK2))
    chart = svg(1544, 390, g, fit=True, aria=f'Effect size of the positive controls for thirteen batches of one lab, with a dashed line at {share} of the lab&#8217;s usual effect; '
                                   'four consecutive batches fall under it. On a plate from a batch that came out, the wells the layout names are the wells that show the effect; on a failed plate none does.')
    fig3 = (f'<span style="color:{MUTE};">&#8722;{abs(rho["spearman"]):.2f}</span> <span style="color:{MUTE}; font-weight:400;">&#8594;</span> '
            f'&#8722;{abs(rho_ok["spearman"]):.2f}')
    body = f'''<div style="{BOARD}">
  {top_line('A8', 'if asked whether the assay works', 'results/e11, e9, e10')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:540px;">Known answer, <span style="color:{PINK};">run in every lab.</span></h2>
    <p style="{LEDE}">Untreated wells show where a lab sits.<br>Lab 3: {len(failed)} batches where the known drugs did not work.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE}">{chart}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {tile(f'{n_batches - len(failed)} of {n_batches}', 'public batches<br>known drugs worked', INK, 0.4)}
    {tile(f'{also_outside} of {len(failed)}', 'failed batches caught by<br>untreated wells alone &#8594; use both', INK, 0.5)}
    {tile(fig3, f'fig 3 link &#183; drift vs answers<br>without these {len(failed)} batches: holds', INK, 0.6)}
  </div>
  <div style="{NOTE}">failed = under {sym} of the lab&#8217;s usual effect + unlike other labs &#183; {known["n_plates"]:,} plates &#183; maps: plates {good["plate"]}, {bad["plate"]}, JUMP layout [7]</div>
</div>'''
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
    out = SD['left_out']['source_7']; dc = SD['dose_check']; amg = dc['strongest_control_at_5_um']
    assert SD['dose_um'] == 10 and out['dose_um'] == 0.625 and SD['untreated_on_each_plate']['every_well_own_plate_dmso']
    e8 = results('e8-redteam.json'); C = e8['all_features']['compounds']
    s = [C[c]['effect_size']['share_of_variance_between_labs'] for c in C]
    labs = sorted(SD['labs'], key=lab_number); by = SD['by_lab']
    alone = [l for l in labs if by[l]['own_lab'] is None]
    wells = [w for w in R['wells'] if w['lab'] in labs]
    one_day = [l for l in labs if len({w['batch'] for w in wells if w['lab'] == l}) == 1 and by[l]['n_wells'] > 1]
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
    count = ', '.join(f'{lab_name(l)} {WORDS[by[l]["n_wells"]]}' for l in labs)
    solid = (f'{WORDS[SD["n_wells"]].capitalize()} wells: {count}. {" and ".join(lab_name(l).capitalize() for l in alone)} has no same-lab pair.<br>'
             f'Most of the gap sits beside {lab_name(big)}, on 1536-well plates: {min(with_big):.2f}&#8211;{max(with_big):.2f} against {without_big:.2f}.<br>'
             f'Its known drugs split the same way.')
    lo, hi = out['cells_vs_dmso_range_over_wells']; amg_by = amg['cells_vs_dmso_by_lab']
    rest = [amg_by[l] for l in labs]
    seven = (f'Dosed at 0.625 &#181;M, a sixteenth [7]: RSL3 left {100 * lo:.0f}&#8211;{100 * hi:.0f}% of its cells.<br>'
             f'{amg["compound"]} at 5 &#181;M left {100 * amg_by["source_7"]:.0f}% there, {100 * min(rest):.0f}&#8211;{100 * max(rest):.0f}% elsewhere: its cells respond.')
    body = f'''<div style="{BOARD}">
  {top_line('A9', 'if asked whether it changes the answer', 'results/e16, e8')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Same drug.<br><span style="color:{PINK};">Different answer.</span></h2>
    <p style="{LEDE}">RSL3 at {SD["dose_um"]:g} &#181;M from fig 4a, every well against every other.<br>Darker = more alike.</p>
  </div>
  {formula}
  <div style="display:grid; grid-template-columns:minmax(0,0.9fr) minmax(0,1.1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.3s; {FIGURE}">{rsl3_matrix(same_dose_view(R, SD))}</div>
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:6px; min-height:0;">
      {box(f'same {SD["n_plates"]} plates, each well against its own plate&#8217;s DMSO', table, 0.4, GREEN, 1.3)}
      {box('does it change the number?', say(f'Which lab ran it explains {100 * min(s):.0f}% to {100 * max(s):.0f}% of how strong a drug&#8217;s effect looks.'), 0.5, PINK)}
      {box('how solid?', say(solid), 0.6)}
      {box(f'{lab_name("source_7")}, left out', say(seven), 0.7)}
    </div>
  </div>
  <div style="{NOTE}">agreement = cosine of two wells&#8217; effects, each well minus its own plate&#8217;s DMSO wells &#183; {len(C)} drugs at full scale: {e8["n_plates"]:,} plates, {e8["n_labs"]} labs &#183; JUMP [7]</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A10
def a10():
    """Brightfield is the bet: the lab is named from a six-dye profile, a DNA image and a brightfield image of the same wells, on the
    same 8 labs and the same held-out batches, so every row has one chance level (results/e17); the same model with the labels
    shuffled is the floor. And brightfield follows lab 2's drift batch by batch much as the dye profile does (results/e17 against e9)."""
    e17 = results('e17-same-labs-every-input.json'); im = e17['inputs']; bf = im['brightfield']; pop = e17['population']
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
    # lab 2, batch by batch: how far each batch sits from its first, by the dye profile (e9) and by the brightfield image (e15)
    from datetime import date
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
    chart = svg(770, m.y0 + m.h + 34, g, fit=True, aria=f'Balanced accuracy naming which of {pop["n_labs"]} labs a well came from, the same wells and held-out batches for every input: six-dye profiles, a DNA-stain image and a brightfield image all sit near 100%; with the labels shuffled, near the chance of 1 in {pop["n_labs"]}. '
                f'Below, lab 2&#8217;s 13 batches: the distance from its first batch by dye profile and by brightfield image rise and fall together (Spearman {d["spearman"]:.2f} over the {d["n_batches"]} batches after the first).')
    uri = lambda f: 'data:image/jpeg;base64,' + base64.b64encode(open(f'figures/assets/{f}', 'rb').read()).decode()
    tile = lambda f, alt, cap, colour: (f'<div style="display:flex; flex-direction:column; gap:6px;"><img src="{uri(f)}" alt="{alt}" style="width:164px; height:280px; border-radius:10px; object-fit:cover; display:block; background:#000;">{label(cap, colour)}</div>')
    gone = ' &#183; '.join(f'<s>{v}</s>' for v in ('stain lot', 'dye lot', 'staining step'))
    fair = (f'<div class="r" style="animation-delay:0.4s; {CARD} padding:16px 20px; display:flex; flex-direction:column; gap:9px; min-width:0;">'
            f'{label("why the bet is fair", GREEN)}'
            f'<span style="{SANS} font-size:20px; font-weight:600; letter-spacing:-0.015em; line-height:1.18; color:{INK};">No dye: fewer things can go wrong</span>'
            f'<div style="display:flex; justify-content:space-between; align-items:baseline; gap:8px;"><span style="{MONO} font-size:14px; line-height:1.4; color:{MUTE};">{gone}</span>{label("A3")}</div>'
            f'<div style="display:flex; gap:12px; margin-top:auto;">' + tile('well-I01-brightfield.jpg', 'Brightfield image of well I01, plate 1053600681.', 'brightfield', INK)
            + tile('well-I01-dna.jpg', 'DNA channel of the same field.', 'DNA stain', GREEN) + '</div>'
            f'<span style="{MONO} font-size:13px; color:{MUTE};">same spot in one well &#183; lab 2</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A10', 'if asked whether it works without stains', 'results/e17, e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Shown in fluorescence.<br><span style="color:{PINK};">Bet on brightfield.</span></h2>
    <p style="{LEDE}">Evidence: cells stained with six dyes.<br>Product: plain light, no dye.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.2s; {FIGURE} flex-direction:column; gap:6px;">{chart}
      <span style="{SANS} font-size:17px; line-height:1.3; color:{MUTE};">Not yet the whole map: beyond each lab&#8217;s usual neighbour, brightfield and dye profile agree batch by batch no more than luck ({e17["nearest_lab"]["image_agrees_with_profile_permutation_null"]["brightfield"]["observed"]} of {e17["nearest_lab"]["image_agrees_with_profile_permutation_null"]["brightfield"]["n_batches"]} against {e17["nearest_lab"]["image_agrees_with_profile_permutation_null"]["brightfield"]["expected_mean"]:.0f}).</span></div>
    {fair}
  </div>
  <div style="{NOTE}">% named right, each lab counted equally, unseen batches &#183; one DMSO well per plate, {pop["n_plates"]:,} plates, the same wells and model for every row &#183; median of {len(e17["paired_splits"]["deal_seeds"])} splits of the batches &#183; profile without its {e17["settings"]["profile_features_dropped"]["count"]} frame-size columns &#183; shuffled: 5 seeds per input &#183; image model never trained on cells &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A11
def a11():
    rt = results('e9-replay-redteam.json')['source_2']
    replay = results('e9-replay.json')['labs']
    B = replay['source_2']['batches']
    n = sum(v['n_batches'] for v in replay.values()); outside = sum(v['batches_outside'] for v in replay.values())
    labs_flagged = sum(v['batches_outside'] > 0 for v in replay.values())
    fl = [b for b in B if b['verdict'] == 'outside']; ok = [b for b in B if b['verdict'] != 'outside']
    names = {'as published': 'as published', 'baseline is the first two batches': 'baseline: first 2 batches',
             'baseline is the first three batches': 'baseline: first 3 batches', 'no clipping': 'extreme values kept',
             'no image-level features': 'cell measurements only', 'image-level features only': 'whole-image measurements only',
             'all-vehicle plates removed': 'untreated-only plates removed'}
    dropped = [k.split()[0] for k in rt if k.endswith(' removed from the field')]
    names.update({f'{s} removed from the field': f'without {lab_name(s)}' for s in dropped})
    names['all of those labs removed'] = 'without labs ' + ' and '.join(str(lab_number(s)) for s in dropped)
    nbase = {'baseline is the first two batches': 2, 'baseline is the first three batches': 3}
    # slide 07's code for a batch: filled = on the map, hollow = flagged; pink = lab 2 (you), green = every other lab
    square = lambda x, y, s, flagged, colour, extra='': (
        f'<rect {extra}x="{x + 0.75:g}" y="{y + 0.75:g}" width="{s - 1.5:g}" height="{s - 1.5:g}" rx="{s / 4:g}" fill="none" stroke="{MUTE}" stroke-width="1.5"/>' if flagged
        else f'<rect {extra}x="{x:g}" y="{y:g}" width="{s:g}" height="{s:g}" rx="{s / 4:g}" fill="{colour}"/>')
    g = []; x0, P, y0 = 410, 34, 58
    months = [short_date(b['date']).split()[1] for b in B]
    X, shift = [], 0
    for k, mth in enumerate(months):
        shift += 10 if k and mth != months[k - 1] else 0
        X.append(x0 + k * P + shift)
    for k, b in enumerate(B):
        d, mth = short_date(b['date']).split()
        if k == 0 or mth != months[k - 1]:
            g.append(text(X[k], 20, mth, 23, MUTE))
        g.append(text(X[k] + 13, 44, d, 23, MUTE, 'middle'))
    changed = 0
    for r, (name, v) in enumerate(rt.items()):
        y = y0 + r * 33
        same = v['verdicts'] == rt['as published']['verdicts']; changed += not same
        shown = names.get(name, name) if same else f'&#8800; {names.get(name, name)}'
        g.append(text(x0 - 24, y + 19, shown, 25, INK2 if same else INK, 'end', 400 if same else 700))
        for k, c in enumerate(v['verdicts']):
            g.append(square(X[k], y, 26, c == 'O', PINK, f'class="f" style="animation-delay:{0.2 + 0.04 * r + 0.01 * k:.2f}s" '))
        g.append(f'<rect x="{X[0] - 3}" y="{y - 3}" width="{nbase.get(name, 1) * P - 2}" height="32" rx="8" fill="none" stroke="{INK2}" stroke-width="2"/>')
    chart = svg(X[-1] + 30, y0 + len(rt) * 33, g, fit=True, aria=f'Verdicts for lab 2 checked {len(rt)} ways; {len(rt) - changed} give the same result.').replace('xMidYMid', 'xMinYMin', 1)
    grid = f'<div style="flex:1 1 0; min-width:0; display:flex; flex-direction:column; gap:10px;">{label(f"lab 2 &#183; you &#183; {len(B)} batches &#215; {len(rt)} ways of checking", PINK)}{chart}</div>'
    order = sorted(replay, key=lab_number)
    cell, gap = 9, 3
    strip = lambda s: (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {len(replay[s]["batches"]) * (cell + gap) - gap} {cell}" width="{len(replay[s]["batches"]) * (cell + gap) - gap}" height="{cell}" aria-hidden="true" style="display:block;">'
                       + ''.join(square(k * (cell + gap), 0, cell, b['verdict'] == 'outside', PINK if s == 'source_2' else GREEN) for k, b in enumerate(replay[s]['batches'])) + '</svg>')
    rows = ''.join(
        f'<div style="display:flex; align-items:center; gap:10px; height:19px;">'
        f'<span style="{MONO} font-size:13px; width:92px; white-space:nowrap; text-align:right; color:{PINK if s == "source_2" else INK2}; font-weight:{600 if s == "source_2" else 400};">'
        f'{lab_name(s) + (" &#183; you" if s == "source_2" else "")}</span>{strip(s)}</div>'
        for s in order)
    waffle = (f'<div style="flex:0 0 auto; display:flex; flex-direction:column; gap:10px;">{label(f"all {len(replay)} labs &#183; {n} batches")}'
              f'<div role="img" aria-label="Verdicts for {n} batches in {len(replay)} labs; {outside} are flagged, in {labs_flagged} labs." style="flex:1; display:flex; flex-direction:column; justify-content:center;">{rows}</div></div>')
    differs = [name for name, v in rt.items() if v['verdicts'] != rt['as published']['verdicts']]
    assert len(differs) == changed == 1 and differs[0] in nbase, f'A11 names one variant that differs: {differs}'
    added = B[nbase[differs[0]] - 1]            # the batch that variant's baseline takes in beyond the first
    assert added['cells_per_well'] == min(b['cells_per_well'] for b in B), 'A11 says the batch it takes in has the fewest cells'
    pub, alt = rt['as published']['verdicts'], rt[differs[0]]['verdicts']
    extra = [k for k, (p, a) in enumerate(zip(pub, alt)) if a == 'O' and p != 'O']
    assert all(a == 'O' for p, a in zip(pub, alt) if p == 'O') and extra == list(range(extra[0], extra[-1] + 1)), 'A11 says the one way that differs only adds flags, in one run'
    swatch = lambda flagged, colour: square(0, 0, 11, flagged, colour)
    key = lambda svg_body, name: (f'<span style="display:flex; align-items:center; gap:7px;"><svg viewBox="-1 -1 13 13" width="13" height="13" aria-hidden="true">{svg_body}</svg>{name}</span>')
    legend = (f'<div style="display:flex; gap:22px; align-items:center; padding-top:10px; margin-top:4px; border-top:1px solid #eceff0; {MONO} font-size:13px; color:{MUTE};">'
              + key(swatch(False, PINK), 'lab 2 &#183; you') + key(swatch(False, GREEN), 'other labs') + key(swatch(True, MUTE), 'flagged')
              + key(f'<rect x="-0.5" y="-0.5" width="12" height="12" rx="3.5" fill="none" stroke="{INK2}" stroke-width="1.4"/><rect x="2.5" y="2.5" width="6" height="6" rx="1.5" fill="{PINK}"/>',
                    'baseline: the batches it is compared with') + '</div>')
    n_plates = sum(b['n_plates'] for v in replay.values() for b in v['batches'])
    NUMBERS = ['zero', 'one', 'two', 'three', 'four']
    plates = lambda bs, colour: f'<b style="{SANS} font-size:22px; font-weight:600; color:{colour};">{sum(b["plates_outside"] for b in bs)} of {sum(b["n_plates"] for b in bs)}</b>'
    body = f'''<div style="{BOARD}">
  {top_line('A11', 'if asked whether it flags too often', 'results/e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:600px;">Rarely: {outside} of {n} batches.<br><span style="color:{PINK};">Same verdict {len(rt) - changed} of {len(rt)} ways.</span></h2>
    <p style="{LEDE}">{len(replay) - labs_flagged} of {len(replay)} labs never flagged.<br>The {NUMBERS[changed]} way that differs flags more, not less.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} flex-direction:column; gap:6px;"><div style="flex:1; min-height:0; display:flex; gap:32px;">{waffle}{grid}</div>{legend}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('What a flag means', 'Batch nearer another lab than<br>its own &#8220;normal&#8221;, its first batch', 0.4, colour=MUTE)}
    {card('Lab 2 &#183; you &#183; plates flagged', f'<span style="display:flex; align-items:baseline; gap:10px;">{plates(fl, PINK)}<span style="{MONO} font-size:13px; color:{MUTE};">in flagged batches</span></span>'
                                  f'<span style="display:flex; align-items:baseline; gap:10px;">{plates(ok, INK2)}<span style="{MONO} font-size:13px; color:{MUTE};">in the other batches</span></span>', 0.5)}
    {card(f'The {NUMBERS[changed]} way that differs', f'<b style="font-weight:600;">+{len(extra)} flags, {short_date(B[extra[0]]["date"])} &#8594; {short_date(B[extra[-1]]["date"])}</b><br>'
                                  f'Its baseline takes in {short_date(added["date"])}:<br>{added["cells_per_well"]:.0f} cells per well, lab 2&#8217;s lowest &#183; A13', 0.6, 1.15, INK)}
  </div>
  <div style="{NOTE}">Each plate checked against its own lab&#8217;s first batch &#183; {n_plates:,} plates &#183; {len(replay)} labs &#183; JUMP [7] &#183; lab 2 over time: A13</div>
</div>'''
    return BASE_CSS, body, None


def raw_pair(base, flagged, channels=('ER',)):
    """One field from the first batch and one from the first flagged batch, each shown the way the microscope
    software shows it (its own window), with the raw camera counts at the 99.8th percentile printed beneath.

    Auto-scaled, both look fine; the counts differ several-fold. Written once to figures/assets/a12-*.png and
    a12-windows.json, so the deck builds without the cache."""
    import base64, json, os
    from PIL import Image
    meta_path = 'figures/assets/a12-windows.json'
    if not os.path.exists(meta_path):
        picks = {}
        for name, bt in (('first', base), ('flagged', flagged)):
            plate = next((p for p in bt['plates'] if os.path.exists(f'cache/images/source_2/{p}/meta.json')), None)
            if plate is None:
                return ''
            picks[name] = (plate, json.load(open(f'cache/images/source_2/{plate}/meta.json')))
        windows = {}
        for c in channels + ('DNA',):
            windows[c] = {}
            for n, (plate, m) in picks.items():
                lo, h = m['channels'][c]['window']
                im = Image.open(f'cache/images/source_2/{plate}/{c}.png').convert('L')
                w, hh = im.size; cc = min(w, hh)
                im.crop(((w - cc) // 2, (hh - cc) // 2, (w + cc) // 2, (hh + cc) // 2)).resize((256, 256), Image.LANCZOS).save(f'figures/assets/a12-{n}-{c}.png', optimize=True)
                windows[c][n] = {'plate': plate, 'well': m['well'], 'p99_8': round(h)}
        json.dump({'date_first': base['date'], 'date_flagged': flagged['date'], 'channels': windows}, open(meta_path, 'w'), indent=1)
    W = json.load(open(meta_path))
    uri = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
    tile = lambda n, c, cap, colour: (f'<div style="display:flex; flex-direction:column; gap:2px; min-width:0;"><div style="aspect-ratio:1/1; max-height:110px; border-radius:10px; overflow:hidden; background:#000;">'
                                      f'<img src="{uri(f"figures/assets/a12-{n}-{c}.png")}" alt="{cap}, {c} channel, one control well of lab 2, auto-scaled." style="width:100%; height:100%; object-fit:cover; display:block;"></div>'
                                      f'{label(cap, colour)}</div>')
    rows = ''.join(f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">{tile("first", c, short_date(W["date_first"]), MUTE)}{tile("flagged", c, short_date(W["date_flagged"]), PINK)}</div>' for c in channels)
    ratio = {c: W['channels'][c]['flagged']['p99_8'] / W['channels'][c]['first']['p99_8'] for c in channels + ('DNA',)}
    assert min(ratio.values()) > 1, f'A12 says raw brightness is higher in the flagged batch: {ratio}'
    c = channels[0]; counts = W['channels'][c]
    return (f'<div class="r" style="animation-delay:0.35s; width:320px; flex-shrink:0; {FIGURE} flex-direction:column; justify-content:center; gap:8px; padding:15px 16px 12px; overflow:hidden;">'
            f'{label(f"{c} &#183; both look fine on screen", INK)}{rows}'
            f'<span style="display:flex; align-items:baseline; gap:10px; padding-top:8px; border-top:1px solid #eceff0;"><b style="{SANS} font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{PINK};">{ratio[c]:.0f}&#215;</b>'
            f'<span style="{SANS} font-size:15px; line-height:1.3; color:{INK};">brighter in raw camera counts, one field each<br>{counts["first"]["p99_8"]:,} &#8594; {counts["flagged"]["p99_8"]:,}</span></span>'
            f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE};">one field each &#183; {c} pattern: around the nucleus &#8594; whole cell</span></div>')


# ------------------------------------------------------------------ A12
def a12():
    first = results('e6-what-moved-source_2-first-flag.json'); last = results('e6-what-moved-source_2.json')
    B = {b['batch']: b for b in results('e9-replay.json')['labs']['source_2']['batches']}
    base = next(b for b in B.values() if b['is_baseline'])
    pick = lambda e, m, c: next((g for g in e['groups'] if g['measurement'] == m and g['channel'] == c), None)
    channels = ['ER', 'AGP', 'Mito', 'DNA']
    g = []

    def panel(x0, title, measure, key, lim, ticks, xlabel):
        ax = Axes(x0 + 90, 60, 400, 4 * 54, lim, (0, 4))
        g.append(chart_title(x0, 34, title, 19))
        g.append(f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>')
        for v in ticks:
            g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID if v else MUTE}" stroke-width="{2 if v else 2.4}"/>')
            g.append(text(ax.X(v), ax.y0 + ax.h + 26, f'{v:g}', 20, MUTE, 'middle'))
        g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 56, xlabel, 21, INK2, 'middle'))
        for r, c in enumerate(channels):
            y = ax.y0 + r * 54
            g.append(text(ax.x0 - 14, y + 34, c, 22, INK, 'end'))
            for j, (e, colour) in enumerate(((first, PINK), (last, PALE_PINK))):
                grp = pick(e, measure, c)
                v = grp[key] if grp else 0
                assert v >= 0, f'A12 bars start at zero: {measure} {c} is {v}'
                xa, xb = ax.X(0), ax.X(v)
                g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.08 * r + 0.1 * j:.2f}s" x="{xa:.1f}" y="{y + 8 + j * 20}" width="{max(xb - xa, 1):.1f}" height="16" rx="3" fill="{colour}"/>')
                g.append(text(xb + 8, y + 23 + j * 20, f'{v:.1f}', 20, PINK if j == 0 else MUTE))
    panel(0, 'brightness', 'Intensity', 'mean_shift', (0, 3.5), (0, 1, 2, 3), f'shift from {short_date(base["date"])} &#183; 0 = none &#183; 1 = usual spread across labs')
    panel(600, 'pattern (texture)', 'Texture', 'mean_abs_shift', (0, 3.5), (0, 1, 2, 3), f'size of shift from {short_date(base["date"])} &#183; same scale')
    d1, d2 = short_date(first['date']), short_date(last['date'])
    ky = 60 + 4 * 54 + 88
    g.append(f'<rect x="90" y="{ky - 14}" width="26" height="14" rx="3" fill="{PINK}"/>' + text(124, ky, f'{d1} &#183; first flagged &#183; {first["n_plates"]} plates', 21, INK2))
    assert last['batch'] == list(B)[-1], 'A12 calls its second batch the latest'
    g.append(f'<rect x="510" y="{ky - 14}" width="26" height="14" rx="3" fill="{PALE_PINK}"/>' + text(544, ky, f'{d2} &#183; latest &#183; {last["n_plates"]} plates', 21, INK2))
    chart = svg(1110, ky + 12, g, fit=True, aria='Shift of stain intensity and texture features by channel for two flagged batches of lab 2, relative to its first batch.')
    pictures = raw_pair(base, B[first['batch']])
    a, b = pick(first, 'Intensity', 'ER'), pick(first, 'Intensity', 'AGP')
    cpw = [x['cells_per_well'] for x in B.values() if x['verdict'] != 'outside']
    lvl = first['share_of_displacement']['by_level']
    assert lvl['cell'] > lvl['image'], 'A12 says cell measurements moved, not only whole-image ones'
    assert a['direction'] == b['direction'] == 'up', 'A12 says brightness rose'
    assert all(min(cpw) <= B[x['batch']]['cells_per_well'] <= max(cpw) for x in (first, last)), 'A12 says cell count stayed inside its earlier range'
    body = f'''<div style="{BOARD}">
  {top_line('A12', 'if asked what moved', 'results/e6')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Brightness rose.<br><span style="color:{PINK};">Cell count did not.</span></h2>
    <p style="{LEDE}"><span style="color:{PINK};">Lab 2 &#183; you:</span> flagged batches against<br>its own &#8220;normal&#8221;, its first batch ({short_date(base["date"])}).</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.2s; flex:1 1 0; {FIGURE} justify-content:center;">{chart}</div>
    {pictures}
  </div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Lab 2 &#183; you &#183; in numbers', f'{a["channel"]} + {b["channel"]} brightness: up in &#8805;&#160;{100 * min(a["share_same_sign"], b["share_same_sign"]):.0f}% of measurements<br>'
                                         f'cells per well: {base["cells_per_well"]:.0f} &#8594; {B[first["batch"]]["cells_per_well"]:.0f} &#8594; {B[last["batch"]]["cells_per_well"]:.0f}<br>'
                                         f'inside its own range, {min(cpw):.0f}&#8211;{max(cpw):.0f} &#183; A13', 0.4, 1.25)}
    {card('Camera or cells?', 'Cell measurements moved,<br>not only whole&#8209;image ones.<br>New stain batch or real biology?<br>This check cannot tell.', 0.5, 1, INK)}
    {card('What you get', 'Look first: camera exposure, ER stain<br>Then: stain mix-up, colour leak, biology<br>Your lab finds the cause', 0.6, 1.05)}
  </div>
  <div style="{NOTE}">{", ".join(channels)}: {["one", "two", "three", "four", "five"][len(channels) - 1]} stain channels, each marking different parts of the cell &#183; each bar averages one channel&#8217;s measurements &#183; JUMP [7]</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A13
def a13():
    from slide04 import cell_count_chart, distance_chart
    B = results('e9-replay.json')['labs']['source_2']['batches']
    out = [b for b in B if b['verdict'] == 'outside']
    panel = lambda chart, delay: f'<div class="r" style="animation-delay:{delay}s; flex:1; {FIGURE} justify-content:center;">{chart}</div>'
    # the pink band is named by its dates, as on slide 04; how many plates it holds is A11's number, not repeated here
    distance = distance_chart(B)
    old = f'>all {sum(b["n_plates"] for b in out)} plates<'
    assert distance.count(old) == 1, f'distance_chart changed: {old}'
    distance = distance.replace(old, f'>{short_date(out[0]["date"])} &#8594; {short_date(out[-1]["date"])}<')
    body = f"""<div style="{BOARD}">
  {top_line('A13', 'if asked how one lab moves over time', 'results/e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:640px;">By its own &#8220;normal&#8221;: fine.<br><span style="color:{PINK};">Next to other labs: it moved.</span></h2>
    <p style="{LEDE}"><span style="color:{PINK};">Lab 2 &#183; you</span>, {len(B)} batches, two views.<br>Not a verdict: a reason to look.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0;">{panel(cell_count_chart(B), 0.2)}{panel(distance, 0.35)}</div>
  <div style="{NOTE}">distance unit: usual spread between wells on one plate &#183; lab 2 &#183; 2021 &#183; JUMP [7] &#183; which batches: A11 &#183; what moved: A12</div>
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
                out.append(f'<span style="{SANS} font-size:26px; color:{FAINT}; padding-bottom:22px;">&#8594;</span>')
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
    <p style="{LEDE}">{['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][len(e12["compounds"])].capitalize()} drugs with a known effect, {n} batches, {e12["n_labs"]} labs.<br>Higher is better.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} padding:22px 28px; display:flex; align-items:center;">{figure}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Nothing lost', f'Right drug recognised: {E["matched"]["own"]:.2f} &#8594; {E["matched"]["field"]:.2f}<br>Matches its own past: {E["agree_own"]["own"]:.2f} &#8594; {E["agree_own"]["field"]:.2f}', 0.4, colour=GREEN)}
    {card('Holds', f'Labs agree more: {holds("agree_field")} of {len(grid)} ways of checking<br>Drugs stay apart: {holds("margin")} of {len(grid)}', 0.5, colour=GREEN)}
    {card('Not fixed yet &#183; drug strength', f'Varies batch to batch &#183; lower is better<br>raw {100 * cv["raw"]:.0f}% &#8594; usual fix {100 * cv["own"]:.0f}% &#8594; map {100 * cv["field"]:.0f}%: steadier than the usual fix, not yet as steady as raw', 0.6, colour=INK)}
  </div>
  <div style="{NOTE}">usual fix: each batch set against its own &#8220;normal&#8221;, its untreated wells &#183; map: against every other lab&#8217;s &#183; {e12["n_plates"]:,} plates &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A17
def a17():
    lb = results('e14-leaderboard.json')
    names = {'centre': 'how unusual', 'tightness': 'plates differ', 'steadiness': 'batch to batch', 'cells': 'cell count off'}
    cols = 'grid-template-columns:64px 72px 140px 84px 84px repeat(4,1fr);'
    cell = lambda s, colour=INK, weight=400, align='left': f'<span style="{SANS} font-size:14px; font-weight:{weight}; color:{colour}; text-align:{align}; font-variant-numeric:tabular-nums;">{s}</span>'
    right = ('batches', 'best rank', 'clean run')
    head = (f'<div style="display:grid; {cols} gap:12px; padding:0 8px 4px; border-bottom:1px solid #d3d8da;">'
            + ''.join(f'<span style="text-align:{"right" if s in right else "left"};">{label(s)}</span>' for s in ('lab', 'batches', 'score', 'best rank', 'clean run'))
            + ''.join(f'<span style="text-align:right;">{label(v)}</span>' for v in names.values()) + '</div>')      # how to read them: the score card
    better = lambda v, m: v[f'median_{m}'] is not None and v[f'median_{m}'] < lb['field_median'][m]     # lower is better on all four
    bar = lambda v: (f'<span style="display:inline-block; width:22px; text-align:right;">{v["median_score"]:.0f}</span>'
                     f'<i style="display:inline-block; vertical-align:middle; margin-left:8px; width:{v["median_score"]:.0f}px; height:8px; border-radius:4px; background:{PINK if v["lab"] == "source_2" else "#c3c9cb"};"></i>')
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.05 * k:.2f}s; display:grid; {cols} gap:12px; padding:1px 8px; border-bottom:1px solid #eceff0; flex:1 1 auto; align-items:center; '
        f'background:{"rgba(190,30,116,0.07)" if v["lab"] == "source_2" else "transparent"}; border-radius:6px;">'
        + cell(lab_name(v['lab']), PINK if v['lab'] == 'source_2' else INK, 700 if v['lab'] == 'source_2' else 500)
        + cell(v['n_batches'], align='right') + cell(bar(v), INK, 700) + cell(f'#{v["best"]["rank"]}', align='right') + cell(f'{v["streak"]["longest"]}', align='right')
        + ''.join(cell('&#8212;' if v[f'median_{m}'] is None else f'{v[f"median_{m}"]:.2f}', GREEN if better(v, m) else INK, align='right') for m in names)
        + '</div>' for k, v in enumerate(lb['by_lab']))
    field = (f'<div class="r" style="animation-delay:{0.2 + 0.05 * len(lb["by_lab"]):.2f}s; display:grid; {cols} gap:12px; padding:2px 8px; flex:1 1 auto; align-items:center; border-top:1px solid {INK};">'
             + cell('all labs', INK, 600) + cell(lb['n_batches'], INK, 600, 'right') + cell('&#8212;', MUTE) + cell('&#8212;', MUTE, 400, 'right') * 2
             + ''.join(cell(f'{lb["field_median"][m]:.2f}', INK, 600, 'right') for m in names) + '</div>')
    table = f'<div style="display:flex; flex-direction:column; flex:1 1 0; min-width:0;">{head}{rows}</div>'      # the all-labs medians sit in the score card
    top = lb['top'][0]
    you = next(k for k, v in enumerate(lb['by_lab'], 1) if v['lab'] == 'source_2')      # labs ranked by their median batch
    ordinal = lambda n: f'{n}' + ('th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))
    score_body = (f'<span style="display:block; {SANS} font-size:22px; line-height:1.2;">0 to 100 &#183; higher is better</span>'
                  f'<span style="display:block; margin-top:4px; {MONO} font-size:13px; color:{MUTE};">all labs: ' + ' &#183; '.join(f'{names[m]} {lb["field_median"][m]:.2f}' for m in names) + f'<br>average rank on the four measures, among {lb["n_batches"]} batches<br>measures: lower is better &#183; green beats all labs</span>')
    best_body = (f'<span style="display:block; font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1;">{top["score"]:.0f}</span>'
                 f'<span style="display:block; margin-top:6px; {MONO} font-size:13px; color:{MUTE};">{lab_name(top["lab"])} &#183; {short_date(top["date"])} &#183; {top["n_plates"]} plates</span>'
                 f'<span style="display:block; {MONO} font-size:13px; color:{MUTE};">{lab_name(top["lab"])} holds {sum(r["lab"] == top["lab"] for r in lb["top"])} of top 10</span>')
    body = f"""<div style="{BOARD}">
  {top_line('A17', 'if asked about the leaderboard', 'results/e14')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Ranked on controls.<br><span style="color:{PINK};">Never on results.</span></h2>
    <p style="{LEDE}">Every lab scored on the other labs&#8217; scale, never its own.<br>{lab_name('source_2').capitalize()} &#183; you: {ordinal(you)} of {lb['n_labs']} labs.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} flex-direction:column; padding:17px 14px 14px;">{table}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('score', score_body, 0.5, 1.4, MUTE)}
    {card('best batch', best_body, 0.6, colour=MUTE)}
    {card('your choice to play', 'Named only if you opt in.<br>Private version for your own plates.', 0.7)}
  </div>
  <div style="{NOTE}">Lab medians &#183; {lb["n_plates"]:,} plates &#183; {lb["n_labs"]} labs &#183; clean run: batches in a row never flagged (A11) &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A18
def a18():
    import csv, gzip
    e9 = results('e9-replay.json'); L2 = e9['labs']['source_2']
    plate = L2['batches'][0]['plates'][0]
    wells = [w for w in csv.DictReader(gzip.open('metadata/well.csv.gz', 'rt')) if w['Metadata_Plate'] == plate]
    known = {'JCP2022_037716', 'JCP2022_025848', 'JCP2022_046054', 'JCP2022_035095',      # JUMP's eight positive controls (analysis/e8_pull_wells.py)
             'JCP2022_064022', 'JCP2022_050797', 'JCP2022_012818', 'JCP2022_085227'}
    dmso = {w['Metadata_Well'] for w in wells if w['Metadata_JCP2022'] == 'JCP2022_033924' or w['Metadata_JCP2022'] in known}
    rest = {w['Metadata_Well'] for w in wells} - dmso
    P = 11.5
    plate_fig = lambda filled, colour, cap, aria: (                   # one lab 2 plate, drawn twice: what leaves, and what stays
        svg(24 * P + 16, 16 * P + 12, plate_map(8, 2, '', '', set(), filled, P=P, colour=colour), css_width=f'{24 * P + 16:g}px', aria=aria)
        + f'<span style="{MONO} font-size:13px; color:{MUTE}; margin-top:4px;">{cap}</span>')
    leave = plate_fig(dmso, PINK, f'pink: {len(dmso)} of {len(wells)} wells leave &#183; JUMP [7]',
                      f'One 384-well plate from lab 2: its {len(dmso)} control wells, untreated and known drugs, are the only wells that leave.')
    stay = plate_fig(rest, INK2, f'dark: {len(rest)} of {len(wells)} wells stay with you',
                     f'The same plate: the other {len(rest)} wells, the test compounds, never leave the building.')
    big = lambda s: f'<span style="{SANS} font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{INK}; padding-top:2px;">{s}</span>'
    col = lambda title, colour, items: (f'<div class="r" style="flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:10px; min-width:0;">'
                                        f'{label(title, colour)}' + ''.join(
                                            f'<div style="display:flex; flex-direction:column; gap:2px; padding-top:8px; border-top:1px solid #eceff0;">'
                                            f'<span style="{SANS} font-size:17px; font-weight:600; line-height:1.25; color:{INK};">{h}</span>'
                                            + (b if b.startswith('<') else f'<span style="{SANS} font-size:15px; line-height:1.35; color:{MUTE};">{b}</span>') + '</div>' for h, b in items) + '</div>')
    leaves = col('What leaves the building', PINK, [
        ('control wells only: untreated and known drugs', leave),
        ('images, or numbers from them', 'proposed: images deleted once measured'),
        ('a plate map and the batch date', 'which wells, and when they were imaged')])
    uses = col('What Datum Line does with it', GREEN, [
        ('builds the map', 'one average point per plate.<br>Scale set by the other labs, never by yours.'),
        ('the map holds untreated wells only', big(f'{L2["n_reference_wells"]:,}')
         + f'<span style="{MONO} font-size:13px; color:{MUTE};">for {lab_name(L2["lab"])}: untreated wells of {len(L2["reference_labs"])} other labs<br>0 treated</span>'),
        ('answers', 'where you sit&#160;&#183; how far you moved&#160;&#183; nearest lab&#160;&#183; cell count&#160;&#183; &#8220;normal&#8221; or not'),
        ('ranks every batch', 'on its untreated wells, never on results&#160;&#183; A17'),
        ('sends a correction, not a model of you', 'one per batch, fitted on your untreated wells&#160;&#183; A19')])
    never = col('What it never sees', INK, [
        ('your treated wells', stay),
        ('your results', 'corrected in your building, by you'),
        ('your name, unless you choose', 'proposed: a number until you opt in.<br>Every lab here is a number.')])
    body = f"""<div style="{BOARD}">
  {top_line('A18', 'if asked what is private', 'results/e9, e12 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Control wells leave.<br><span style="color:{PINK};">Nothing else does.</span></h2>
    <p style="{LEDE}">No compound, no target, no result.<br>Nothing for legal to approve.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0; align-items:stretch;">{leaves}{uses}{never}</div>
  <div style="{NOTE}">In every analysis here, the map and the correction see untreated wells only &#183; github.com/kat-titter/datum-line/analysis &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A19
def a19():
    """Four steps in one figure, each a picture of the same height: the well, its numbers, the map (slide 04's projection) and the
    correction; the cards under it hold the evidence for the two steps that carry a number."""
    import math
    import slide04
    e1 = results('e1.json')['all_sources']; e12 = results('e12-field-normalization.json')
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
    g.append(f'<text x="{best[1]}" y="{best[2]}" style="{MONO}" font-size="14" font-weight="600" fill="{PINK}"{HALO_PANEL}>lab 2 &#183; you</text>')
    mapfig = svg(PW, PH, g, css_width=f'{PW}px', aria='Untreated wells from 11 labs as points, one shade of green per lab; lab 2 in pink, apart from the others.')
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
    acc, chance = f"{100 * e1['balanced_accuracy']:.1f}%", f"{100 * e1['chance']:.0f}%"
    figure = (panel(1, 'an image', PINK, img, 'one untreated well &#183; JUMP [7]') + arrow
              + panel(2, 'numbers', MUTE, numbers, 'standard software today: size, shape, brightness, texture') + arrow
              + panel(3, 'the map', GREEN, mapfig, 'each lab placed on the other labs&#8217; scale, never its own') + arrow
              + panel(4, 'the correction', PINK, move, 'one per batch, fitted on your untreated wells &#183; sketch &#183; A14'))
    evidence = (f'<span style="display:block; {SANS} font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1;">{acc}</span>'      # ink: here a high number is the problem the map solves
                f'<span style="display:block; margin-top:6px; {MONO} font-size:13px; line-height:1.5; color:{MUTE};">a computer names the lab of each well &#183; by guessing: {chance}<br>'
                f'{e1["n_wells"]:,} untreated wells &#183; {e1["n_labs"]} labs &#183; on plates it never saw</span>')
    body = f"""<div style="{BOARD}">
  {top_line('A19', 'if asked what the machine learning is', 'results/e1, e12, e17')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Image in.<br><span style="color:{PINK};">Position and correction out.</span></h2>
    <p style="{LEDE}">Results stay in the lab.<br>Untreated wells and the correction travel.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} padding:17px 22px 14px; gap:10px; align-items:flex-start;">{figure}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('every lab looks different', evidence, 0.5, colour=GREEN)}
    {card('AI image model next &#183; A10', short, 0.6, 1.3, MUTE)}
  </div>
  <div style="{NOTE}">Correction, per batch on {e12["k"]} components: x&#8242; = C<sub style="{SUB}">field</sub><sup style="{SUB}">&#189;</sup> C<sub style="{SUB}">batch</sub><sup style="{SUB}">&#8722;&#189;</sup> (x &#8722; m<sub style="{SUB}">batch</sub>) &#183; every script: github.com/kat-titter/datum-line/analysis</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A20
def a20():
    e1 = results('e1.json')['all_sources']; e9 = results('e9-replay.json')['labs']; e11 = results('e11-known-answer.json')
    rt = results('e1-redteam.json')['tests']                 # image-quality numbers alone: the microscope is in the fingerprint
    near = sorted(b['to_nearest_other'] for v in e9.values() for b in v['batches'])
    n_batches = len(near); farthest = near[-1]
    own = sum(b['wells_named_own_lab'] >= 1 for v in e9.values() for b in v['batches'])
    failed_plates = sum(f['n_plates'] for f in e11['failed'])
    W, H = 240, 180                                       # every figure the same box, so the four sit level
    pill = lambda when: (f'<span style="{MONO} font-size:13px; padding:1px 9px; border-radius:999px; border:1px solid {GREEN if when == "today" else FAINT}; '
                         f'color:{GREEN if when == "today" else MUTE};">{when}</span>')     # as on A24
    col = lambda title, colour, when, big, items, fig, cap: (
        f'<div class="r" style="flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:center; gap:8px;">{label(title, colour)}{pill(when)}</span>'
        f'<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; padding:6px 0 4px; height:50px; white-space:nowrap;">{big}</span>' + ''.join(
            f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK if i == 0 else MUTE};">{l}</span>' for i, l in enumerate(items))
        + f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:6px;">{svg(W, H, fig)}<span style="{MONO} font-size:13px; color:{MUTE};">{cap}</span></div></div>')
    T = lambda x, y, s, anchor='middle': f'<text x="{x:.1f}" y="{y:.1f}" style="{MONO}" font-size="13" fill="{MUTE}" text-anchor="{anchor}">{s}</text>'
    # provenance: one square per batch, solid where every well names its own lab
    shares = sorted((b['wells_named_own_lab'] for v in e9.values() for b in v['batches']), reverse=True)
    per_row = 14; pitch = W / per_row; rows = -(-len(shares) // per_row); top = H - rows * pitch
    waffle = [f'<rect x="{(k % per_row) * pitch + 1:.1f}" y="{top + (k // per_row) * pitch + 1:.1f}" width="{pitch - 3:.1f}" height="{pitch - 3:.1f}" rx="2" '
              f'fill="{GREEN}" fill-opacity="{1 if v >= 1 else 0.3}"/>' for k, v in enumerate(shares)]
    # integrity: the known answer, batch by batch, in A8's colours
    lab = e11['failed'][0]['lab']; S = e11['labs'][lab]['batches']; tallest = max(b['size'] for b in S); w = W / len(S); base = H - 4
    bars = ([f'<rect x="{k * w + 3:.1f}" y="{base - (H - 16) * b["size"] / tallest:.1f}" width="{w - 6:.1f}" height="{(H - 16) * b["size"] / tallest:.1f}" rx="2" '
             f'fill="{INK if b["verdict"] == "failed" else FAINT}"/>' for k, b in enumerate(S)]
            + [f'<path d="M 0 {base} H {W}" stroke="{GRID}" stroke-width="1"/>'])
    # unknown origin: every real batch's distance to its nearest other lab, and the zone beyond the farthest
    X = lambda v: 8 + v / 13 * 220
    rug = ([f'<rect x="{X(farthest):.1f}" y="22" width="{X(13) - X(farthest):.1f}" height="{H - 46}" fill="{PANEL}"/>', T(X((farthest + 13) / 2), 22 + (H - 46) / 2 + 4, 'suspect')]
           + [f'<path d="M {X(v):.1f} 26 V {H - 28}" stroke="{GREEN}" stroke-width="1.5" stroke-opacity="0.4"/>' for v in near]
           + [f'<path d="M {X(farthest):.1f} 18 V {H - 24}" stroke="{INK}" stroke-width="1.5"/>', T(X(farthest) - 5, 14, 'farthest real batch', 'end')]
           + [T(X(v), H - 4, v) for v in (0, 5, 10)])
    # early warning: lab 2's distance from its own first batch, batch by batch; filled where the map flagged it
    L = e9['source_2']['batches']; peak = max(b['from_baseline'] for b in L); moved = next(b for b in L if b['verdict'] == 'outside')
    pts = [(10 + k * 220 / (len(L) - 1), H - 8 - (H - 24) * b['from_baseline'] / peak) for k, b in enumerate(L)]
    line = ([f'<path d="M 0 {H - 4} H {W}" stroke="{GRID}" stroke-width="1"/>', '<path d="' + ' '.join(f'{"M" if k == 0 else "L"} {x:.1f} {y:.1f}' for k, (x, y) in enumerate(pts)) + f'" fill="none" stroke="{PINK}" stroke-width="2" stroke-linejoin="round"/>']
            + [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{PINK if b["verdict"] == "outside" else "#ffffff"}" stroke="{PINK}" stroke-width="1.5"/>' for (x, y), b in zip(pts, L)])
    # every caption two lines of 30 characters or fewer, so the four figures stay level
    where = col('provenance', GREEN, 'today', f'{100 * e1["balanced_accuracy"]:.1f}%', [
        f'of {e1["n_wells"]:,} untreated wells get the right lab, on unseen plates. The fingerprint is cells and microscope together: '
        f'image-quality numbers alone name the lab at {100 * rt["family:ImageQuality"]["balanced_accuracy"]:.1f}%.'], waffle, f'1 square = 1 batch<br>solid: every well right &#183; {own}')
    labels = col('integrity', INK, 'today', f'{len(e11["failed"])} batches', [
        'Label: known drug in these wells.', f'Cells: almost no effect, on {failed_plates} plates.'],
        bars, f'{lab_name(lab)} &#183; drug effect per batch<br>dark: failed &#183; A8')
    nowhere = col('unknown origin', INK, 'proposed', f'{farthest:.0f}&#215;', [
        f'Farthest of {n_batches} real batches from its nearest other lab.', 'Farther out: wrong cell line? Mixed culture? Untested.'],
        rug, 'distance to nearest other lab<br>1 line = 1 real batch')
    sentinel = col('early warning', INK, 'proposed', short_date(moved['date']), [
        f'{moved["date"][:4]}: {lab_name("source_2")}&#8217;s untreated wells moved; its cell count did not.', 'A move nobody explains: check reagents, air, water.'],
        line, f'{lab_name("source_2")} &#183; you &#183; since batch 1<br>filled: flagged &#183; A13')
    body = f"""<div style="{BOARD}">
  {top_line('A20', 'if asked about biosecurity', 'results/e1, e9, e11 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Cells show their lab.<br><span style="color:{PINK};">Labels can lie. Cells cannot.</span></h2>
    <p style="{LEDE}">One map of untreated wells, no results stored.<br>Two checks work today, two are proposed.</p>
  </div>
  <div style="display:flex; gap:14px; flex-grow:1; min-height:0; align-items:stretch;">{where}{labels}{nowhere}{sentinel}</div>
  <div style="{NOTE}">Integrity check uses each plate&#8217;s known-drug wells (A8) &#183; &#215; = times the usual spread of wells within one plate &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A21
PRESEED = [  # eighteen months; every line is a proposal
    ('leader, to run it', '18 months', 180),
    ('scientific lead (me)', '18 months', 180),
    ('ML engineer', 'from month 7', 160),
    ('payroll overhead', '20% of salaries', 104),
    ('benchmark playground', '~60 plates &#183; planted faults', 120),     # where it is made: partner labs or a contract lab (the doc and A21's card)
    ('partner-lab bench time', '3 labs &#183; controls they already image &#183; reagent top-ups &#183; shipping', 30),
    ('compute and storage', 'images &#183; models &#183; hosting &#183; API', 45),
    ('legal, IP, insurance, accounting', 'incorporation to first contract', 45),
    ('travel and partner visits', '2 benchmark partners &#183; 3 labs', 20),
]
MULTIPLIER = 2       # the rule: most things take two to three times the time and money they should; plan at two


def preseed_total():
    sub = sum(k for _, _, k in PRESEED)
    return sub, round(sub * MULTIPLIER)


def a21():
    from slide09 import MILESTONES as M     # local: slide09 imports this module at load time
    sub, total = preseed_total()
    bench = sum(k for name, _, k in PRESEED if name in ('benchmark playground', 'partner-lab bench time'))
    people = sum(k for _, _, k in PRESEED[:4])   # leader, scientific lead, ML engineer, payroll overhead
    run = sub - people - bench                   # compute, legal, travel
    seg = lambda k, c: f'<div style="flex:{k} 0 0; background:{c};"></div>'
    tag = lambda k, s, c: f'<span style="flex:{k} 0 0; min-width:0; {MONO} font-size:13px; line-height:1.3; color:{c};">{s}<br>{100 * k / sub:.0f}%</span>'
    split = (f'<div style="flex-grow:1; min-width:0; display:flex; flex-direction:column; gap:6px;">'
             f'<span style="{MONO} font-size:13px; color:{MUTE};">${sub}k planned &#215; {MULTIPLIER} = ${total / 1000:.2f}M asked</span>'
             f'<div style="display:flex; gap:2px; height:16px; border-radius:8px; overflow:hidden;">{seg(people, INK)}{seg(bench, GREEN)}{seg(run, FAINT)}</div>'
             f'<div style="display:flex; gap:2px;">{tag(people, "people", INK)}{tag(bench, "benchmark", GREEN)}{tag(run, "other", MUTE)}</div></div>')
    row = lambda name, what, k, strong=False, colour=INK, rule='border-bottom:1px solid #eceff0;', size=15: (
        f'<div style="display:grid; grid-template-columns:260px 1fr 90px; gap:16px; align-items:baseline; padding:4px 10px; {rule}">'
        f'<span style="{SANS} font-size:{size}px; font-weight:{700 if strong else 600}; color:{colour};">{name}</span>'
        f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{what}</span>'
        f'<span style="{SANS} font-size:{size}px; font-weight:{700 if strong else 500}; color:{colour}; text-align:right;">{f"${k / 1000:.2f}M" if k >= 1000 else f"${k}k"}</span></div>')
    board = {'benchmark playground': 'A16'}        # the board that shows what the line buys
    table = (''.join(row(name, what + (f' &#183; {board[name]}' if name in board else ''), k) for name, what, k in PRESEED)
             + row('planned', 'sum', sub, rule=f'border-top:1px solid {FAINT}; border-bottom:1px solid #eceff0;')
             + row('+ buffer', f'most things take 2&#8211;3&#215; the time and money planned &#183; we plan for {MULTIPLIER}&#215;', total - sub, colour=MUTE)
             + row('asked &#183; 18 months', '', total, True, PINK, rule=f'border-top:2px solid {INK}; padding-top:6px;', size=17))
    decide = lambda title, body, colour, grow=1: (f'<div class="r" style="animation-delay:0.5s; flex:{grow}; {CARD} padding:10px 16px; display:flex; flex-direction:column; gap:4px;">'
                                          f'{label(title, colour)}<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{body}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A21', 'if asked how much and what for', 'proposed &#183; every line an assumption')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">About ${total / 1000:.1f}M <span style="color:{PINK};">for eighteen months.</span></h2>
    {split}
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:10px 8px 4px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{table}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {decide('No in-house lab', 'Partner labs or a contract lab.<br>Own lab: costs more, proves less.', MUTE)}
    {decide('What the money must show', f'<b style="color:{GREEN}">1</b> {M[0][0]}, paid in this round &#183; <b style="color:{GREEN}">2</b> {M[1][0]}<br><b style="color:{GREEN}">3</b> {M[2][0]} &#183; <b style="color:{PINK}">4</b> {M[3][0]} &#8594; seed', MUTE, grow=2)}
  </div>
  <div style="{NOTE}">salaries below market &#183; leader and scientific lead paid &#183; nothing here committed</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A4
def a4():
    """The cell-counting paper [2]: its abstract, excerpted verbatim, with three sentences lit."""
    hi = lambda s, colour=PINK: f'<mark style="background:{colour}1f; color:{INK}; border-radius:4px; padding:0 3px; box-shadow:0 0 0 1px {colour}44;">{s}</mark>'
    abstract = (                                     # shortened only by whole sentences and clauses, each gap marked
        '&#8230; ' + hi('counting cells achieves unexpectedly high performance in these benchmarks, making them less useful for discerning whether '
                        'additional properties, such as phenotypic profiles (mRNA or Cell Painting), provide additional useful information on bioactivity.')
        + ' &#8230; ' + hi('we recommend filtering benchmarks to exclude such assays and including a cell-count baseline.', GREEN)
        + ' &#8230; ' + hi('we confirm that models leveraging Cell Painting image-based profiles outperformed the baseline cell count model.', GREEN)
        + ' &#8230;')
    key = (f'<div style="display:flex; gap:22px; align-items:center; margin-top:auto; padding-top:10px; border-top:1px solid #eceff0; {MONO} font-size:13px; letter-spacing:0.1em; color:{MUTE};">'
           f'<span style="text-transform:uppercase;">abstract excerpt &#183; verbatim</span><span>{hi("finding")}</span><span>{hi("recommendation &#183; what held up", GREEN)}</span></div>')
    stat = lambda big, small, colour: (f'<div style="display:flex; flex-direction:column; gap:4px;"><span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; height:40px;">{big}</span>'
                                       f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{small}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A4', 'if asked why the model is not the moat', 'Nature Communications &#183; 2026 &#183; [2]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Weak benchmarks.<br><span style="color:{PINK};">Counting cells often wins.</span></h2>
    <p style="{LEDE}">I coauthored this paper.<br>Benchmarks decide which model looks good.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; min-height:0; {CARD} padding:18px 22px 14px; display:flex; flex-direction:column; gap:10px;">
    <p style="margin:0; {SANS} font-size:26px; line-height:1.5; color:{INK}; text-wrap:pretty;">{abstract}</p>{key}
  </div>
  <div class="r" style="animation-delay:0.6s; display:grid; grid-template-columns:1fr 1fr 1.6fr; gap:24px; align-items:start; {CARD} padding:12px 20px;">
    {stat('209 and 270', 'tests in two popular benchmarks<br>many really measure cell health', INK)}
    {stat('Images win', 'on 24 tests aimed at one protein each<br>Cell Painting beat the cell count', GREEN)}
    <div style="display:flex; flex-direction:column; gap:4px;">{label('Why it matters here', PINK)}<span style="{SANS} font-size:18px; line-height:1.35; color:{INK};">Whoever sets the baseline sets the benchmark.</span>
      <span style="{MONO} font-size:13px; line-height:1.5; color:{MUTE};">benchmark playground &#183; a cell-count baseline on every task &#183; planted faults &#183; every model scored &#183; A16</span></div>
  </div>
  <div style="{NOTE}">Seal S, Dee W, &#8230; <span style="color:{PINK}; font-weight:600;">Titterton K</span>, &#8230; Carpenter AE. Counting cells can accurately predict small-molecule bioactivity benchmarks. <em>Nat Commun</em>, 2026.</div>
</div>"""
    return BASE_CSS, body, None


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
             f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">one certificate</span>'
             f'<span style="{MONO} font-size:14px; color:{MUTE}; margin-left:auto;">natural first partner: STR testing services</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A7', 'if asked how this differs from STR', 'results/e1 &#183; ATCC [14]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">STR says which cells.<br><span style="color:{PINK};">Images say how they behave.</span></h2>
    <p style="{LEDE}">One cell line, U2OS, in all {e1["n_labs"]} labs.<br>Images still name the lab: {100 * e1["balanced_accuracy"]:.1f}% right.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0; align-items:stretch;">{left}{right}</div>
  {joint}
  <div style="{NOTE}">STR: 17 loci + amelogenin, ATCC [14] &#183; Datum Line: {e1["n_wells"]:,} untreated U2OS wells &#183; {e1["n_plates"]:,} plates &#183; {e1["n_labs"]} labs &#183; plates held out &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A22
MARKET = {  # (low, base, high); every one an assumption until a count replaces it
    'organisations screening a few lines deep': (200, 400, 800),
    'lines each runs per quarter': (2, 4, 8),
    'price per line per quarter, $k': (5, 10, 15),
    'organisations screening panels of hundreds to thousands of lines': (10, 25, 50),
    'site licence per year, $k': (50, 150, 300),
    'companies buying cell data they did not make': (50, 150, 300),
    'purchased datasets each certifies per year': (2, 4, 8),
    'price per certificate, $k': (10, 25, 50),
    'benchmark partners': (4, 10, 20),
    'membership per partner per year, $k': (50, 100, 200),
}


# one screen run on cells that had changed, in the author's experience (white paper): runs a week, weeks, $k a run
SCREEN = (3, 17, 50)


def market(i):
    v = {k: r[i] for k, r in MARKET.items()}
    subs = (v['organisations screening a few lines deep'] * v['lines each runs per quarter'] * v['price per line per quarter, $k'] * 4
            + v['organisations screening panels of hundreds to thousands of lines'] * v['site licence per year, $k'])
    certs = v['companies buying cell data they did not make'] * v['purchased datasets each certifies per year'] * v['price per certificate, $k']
    bench = v['benchmark partners'] * v['membership per partner per year, $k']
    return subs, certs, bench


def a22():
    low, base, high = (market(i) for i in range(3))
    m = lambda k: f'${k / 1000:.1f}M'.replace('.0M', 'M') if k >= 1000 else f'${k}k'
    row = lambda name, vals, strong=False, colour=INK, extra='': (
        f'<div style="display:grid; grid-template-columns:1fr 110px 110px 110px; gap:14px; align-items:baseline; padding:2px 10px; border-bottom:1px solid #eceff0;{extra}">'
        f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 500}; color:{colour};">{name}</span>'
        + ''.join(f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 400}; color:{colour if strong else (INK if j == 1 else MUTE)}; text-align:right;">{x}</span>'
                  for j, x in enumerate(vals)) + '</div>')     # the base column in ink, low and high muted
    head = row('assumption', ('low', 'base', 'high'), True, MUTE)
    SHOW = {'organisations screening a few lines deep': 'organisations testing drugs on a few cell lines',     # plain words on the board; MARKET keys stay
            'lines each runs per quarter': 'cell lines each one uses per quarter',
            'price per line per quarter, $k': 'price per cell line per quarter, $k',
            'organisations screening panels of hundreds to thousands of lines': 'organisations testing drugs on hundreds to thousands of cell lines'}
    keys = list(MARKET)
    streams = [('per-line checks and site licences, per year', keys[:5], 0),
               ('certificates on purchased data, per year', keys[5:8], 1),
               ('benchmark membership, per year', keys[8:], 2)]
    rows = ''.join(''.join(row(SHOW.get(k, k), tuple(f'{x:,}' for x in MARKET[k])) for k in ks)
                   + row(name, tuple(m(x[i]) for x in (low, base, high)), True, INK2, ' border-bottom-color:#949c9f;')
                   for name, ks, i in streams)
    total = row('total per year, if every buyer joined', tuple(m(sum(x)) for x in (low, base, high)), True, INK, f' border-top:2px solid {INK}; border-bottom:none;')
    subs, certs, bench = base
    tenth = 100 * (sum(base) // 10) / sum(base)
    runs, weeks, run = SCREEN
    screen, cert = runs * weeks * run, MARKET['price per certificate, $k'][1]      # $k: the screen to redo, and one certificate at the base price
    seg = lambda v, fill, name: (f'<div style="flex:{v} 0 0; min-width:0; background:{fill}; display:flex; flex-direction:column; justify-content:center; align-items:flex-end; '
                                 f'padding:0 {8 if name else 0}px; {MONO} font-size:13px; line-height:1.2; color:#ffffff; white-space:nowrap;">{name}</div>')
    figure = (f'<div class="r" style="animation-delay:0.5s; flex:2; {FIGURE} flex-direction:column; justify-content:center; gap:8px;">'
              f'{label("base case &#183; per year", INK)}'
              f'<div style="position:relative; display:flex; height:40px; border-radius:4px; overflow:hidden;">'
              f'{seg(subs, INK2, f"subscriptions<br>{m(subs)}")}{seg(certs, FAINT, f"certificates<br>{m(certs)}")}{seg(bench, "#c3c9cb", "")}'
              f'<div style="position:absolute; left:{tenth:.1f}%; top:0; bottom:0; border-left:2px dashed #ffffff;"></div></div>'
              f'<div style="display:flex; justify-content:space-between; {MONO} font-size:13px; white-space:nowrap;">'
              f'<span style="padding-left:{tenth:.1f}%; color:{INK};">&#8593; five-year target &#183; a tenth &#183; {m(sum(base) // 10)}</span>'
              f'<span style="color:{MUTE};">benchmark {m(bench)} &#8593;</span></div></div>')
    note = lambda title, body, colour: (f'<div class="r" style="animation-delay:0.5s; flex:1; {CARD} padding:10px 16px; display:flex; flex-direction:column; gap:4px;">'
                                        f'{label(title, colour)}<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{body}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A22', 'if asked how big', 'every count and price an assumption')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">About {m(sum(base))} a year, <span style="color:{PINK};">if everyone joined.</span></h2>
    <p style="{LEDE}">Count &#215; price.<br>Three streams.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:8px; display:flex; flex-direction:column; flex-shrink:0;">{head}{rows}{total}</div>
  <div style="display:flex; gap:16px; align-items:stretch; flex-grow:1; min-height:0;">
    {figure}
    {note('Why buyers pay', f'One screen I ran on a line checked late:<br>{runs} runs a week &#215; {weeks} weeks &#215; ${run}k &#8776; ${(screen + 50) // 100 / 10:.1f}M to redo.<br>'
                            f'Certificate @ ${cert}k: about {100 * cert / screen:.0f}% of that.<br>Subscription: insurance against it.', PINK)}
  </div>
  <div style="{NOTE}">prices proposed on A15 &#183; academic labs join free &#183; they are the map, not the revenue</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A15
def a15():
    """Who pays, along the path: labs free, then the certificate, the benchmark and the exchange. Prices are A22's assumptions."""
    from slide09 import ICON     # local: slide09 imports this module at load time
    rng = lambda key: f'~${MARKET[key][0]}&#8211;{MARKET[key][2]}k'
    # what each row builds, drawn with the path's own icons and colours (slides 06, 09, 10): map and exchange green, certificate pink, benchmark flag green
    icons = {'map': PATH_ICONS['map'], 'certificate': PATH_ICONS['certificate'], 'benchmark': ICON['flag'], 'exchange': PATH_ICONS['exchange']}
    tone = {'map': GREEN, 'certificate': PINK, 'benchmark': GREEN, 'exchange': GREEN}
    rows = [('labs and core facilities', 'a place on the map<br>certificate &#183; leaderboard', 'free, for sharing controls', 'the map', 'map', GREEN),
            ('companies that buy cell data', 'a certificate on every dataset they buy', f'{rng("price per certificate, $k")} per certificate', 'first revenue', 'certificate', PINK),
            ('teams that run cell screens all&#160;year', 'a check on every batch they run', f'{rng("price per line per quarter, $k")} per cell line, per quarter', 'repeat revenue', 'certificate', INK),
            ('AI labs and model builders', 'a test set with faults planted on purpose', f'{rng("membership per partner per year, $k")} a year, as partners', 'the standard', 'benchmark', INK),
            ('then: exchange subscribers', 'access to certified data from many labs', 'a subscription &#183; each lab keeps a share', 'the network', 'exchange', MUTE)]
    cols = 'grid-template-columns:270px 1fr 1fr 160px;'
    head = (f'<div style="display:grid; {cols} gap:24px; padding:0 20px 10px; border-bottom:1px solid #d3d8da;">'
            + ''.join(label(s) for s in ('who', 'what they get', 'what they pay', 'what it builds')) + '</div>')
    mark = lambda step: (f'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="{tone[step]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
                         f'aria-hidden="true" style="vertical-align:-4px; margin-right:9px;">{icons[step]}</svg>')
    body_rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; {cols} gap:24px; align-items:baseline; flex:1; align-content:center; padding:16px 20px; '
        f'{"border-bottom:1px solid #eceff0;" if k < len(rows) - 2 else ""}{" border-top:1px dashed " + GREEN + ";" if who.startswith("then") else ""}">'
        f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK if not who.startswith("then") else GREEN};">{who}</span>'
        f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK2};">{get}</span>'
        f'<span style="{SANS} font-size:16px; font-weight:600; line-height:1.35; color:{colour};">{pay}</span>'
        f'<span style="{SANS} font-size:16px; white-space:nowrap; color:{PINK if colour == PINK else INK2};">{mark(step)}{builds}</span></div>'
        for k, (who, get, pay, builds, step, colour) in enumerate(rows))
    body = f"""<div style="{BOARD}">
  {top_line('A15', 'if asked who pays', 'proposed &#183; prices are the assumptions on A22')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:700px;">Labs join free.<br><span style="color:{PINK};">Companies pay to use the map.</span></h2>
    <p style="{LEDE}">Certificate pays first.<br>Then the exchange: access, not ownership.</p>
  </div>
  <div class="r" style="animation-delay:0.1s; {CARD} padding:18px 4px 6px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{head}{body_rows}</div>
  <div style="{NOTE}">only control wells leave a lab, untreated and known drugs, never a test compound &#183; privacy A18 &#183; the lab&#8217;s share A24</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A23
def a23():
    """What data is worth, and why cell data does not convert: public figures with numbered references (figures/worth.py)."""
    from worth import DEALS, PRICES, SITES, REFS, DETAIL
    from slide06 import sites_chart
    # plainer words than slide 06, from the same sources: worth.py and sites_chart stay as slide 06 reads them
    plain = {11: 'paid by Roche for one cell dataset', 12: 'pledged for cell data to train AI<br>funders get it a year early'}
    prices = [(big, plain.get(ref, w), ref) for big, w, ref in PRICES]
    chart = sites_chart(halo="#ffffff")
    (w0, w1), (a0, a1) = SITES['within'], SITES['across']
    agree = results('e12-field-normalization.json')['every_batch']      # what the map buys, as A14 shows it: same drugs, labs closer
    n_batches, closer = agree['n_batches'], int(agree['agree_field']['field_better_than_own_in'].split()[0])
    for old, new in (('>inside one lab<', '>same lab<'), ('>between labs<', '>different labs<'),
                     ('% replicate<', '%<'), ('% agree<', '%<'), ('>% of compounds<', '>drugs whose repeats look alike<'),
                     (f'Inside one lab {w0} to {w1} percent of compounds replicate; between labs {a0} to {a1} percent agree.',
                      f'Same lab: {w0} to {w1} percent of drugs repeat alike; different labs: {a0} to {a1} percent.')):
        assert chart.count(old) == 1, f'sites_chart changed: {old}'
        chart = chart.replace(old, new)
    number = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    deal = lambda k, big, name, what, more, ref: (
        f'<div class="r" style="animation-delay:{0.2 + 0.12 * k:.2f}s; flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'{label(name, MUTE)}<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{big}</span>'
        f'<span style="{SANS} font-size:15px; line-height:1.4; color:{INK2};">{what}</span>'
        f'<span style="margin-top:auto; {MONO} font-size:13px; line-height:1.4; color:{MUTE};">{more} [{ref}]</span></div>')   # level across the three
    deals = ''.join(deal(k, big, name, what, more, ref) for k, ((big, what, ref), (name, _, _), more) in enumerate(zip(prices, DEALS, DETAIL)))
    sites = (f'<div class="r" style="animation-delay:0.6s; {FIGURE} gap:28px; align-items:center; flex-grow:1;">'
             f'<div style="flex:0 0 560px; display:flex; flex-direction:column; gap:6px;">{label(str(SITES["n_sites"]) + " European labs &#183; one protocol &#183; one cell line", INK)}'
             f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK2};">same cells, same reagents, shipped to every lab [{SITES["ref"]}]</span>{chart}</div>'
             f'<div style="display:flex; flex-direction:column; gap:10px; min-width:0; align-self:stretch; justify-content:center; border-left:1px solid #e4e8e9; padding-left:28px;">'
             f'{label("what the paper says", MUTE)}'
             f'<span style="{SANS} font-size:26px; font-weight:600; line-height:1.25; color:{PINK}; text-wrap:balance;">&#8220;{SITES["quote"]}&#8221; '
             f'<span style="{MONO} font-size:13px; font-weight:400; color:{MUTE};">[{SITES["ref"]}]</span></span>'
             f'<div style="display:flex; flex-direction:column; gap:6px; margin-top:12px; padding-top:16px; border-top:1px solid #e4e8e9;">'
             f'{label("on one shared map &#183; JUMP [7]", GREEN)}'
             f'<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{GREEN};">{closer} of {n_batches}</span>'
             f'<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">batches: labs agree more on what a drug does &#183; A14</span></div></div></div>')
    refs = ('[7] JUMP, 2023 &#183; [10] TechCrunch, 2025 &#183; [11] Recursion, 2025 &#183; [12] eWeek, 2026 &#183; [13] Wolff et al., <em>iScience</em>, 2025 &#183; '
            'full references in the README')
    body = f"""<div style="{BOARD}">
  {top_line('A23', 'if asked what cell data is worth', 'public figures [10]&#8211;[13] &#183; results/e12')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Data has a price.<br><span style="color:{PINK};">Cell data needs a standard.</span></h2>
    <p style="{LEDE}">{number[len(prices)].capitalize()} public prices.<br>Same cells, {number[SITES['n_sites']]} labs, different results.</p>
  </div>
  <div style="display:flex; gap:14px; align-items:stretch;">{deals}</div>
  {sites}
  <div style="{NOTE}">{refs}</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A24
def a24():
    """Why a lab would share: what it keeps, what anyone can check, and who can subscribe. Measured where it says today; proposed elsewhere."""
    e1 = results('e1.json')['all_sources']
    # the number inline, so its card is no taller than its row; "anyone can check" is said once, on the card beside it
    fingerprint = (f'<span style="display:flex; flex-direction:column; gap:2px;">'
                   f'<span style="display:flex; align-items:baseline; gap:10px;"><span style="{SANS} font-size:32px; font-weight:700; letter-spacing:-0.03em; line-height:1.1; color:{GREEN};">'
                   f'{100 * e1["balanced_accuracy"]:.1f}%</span><span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">right lab out of {e1["n_labs"]}</span></span>'
                   f'<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">from control-well images <span style="{MONO} font-size:13px; color:{MUTE};">&#183; A20</span></span></span>')
    cards = [      # row 1, owned by the lab, in pink (you); row 2, verified by anyone, in green (the field)
        ('control wells only', 'today', 'no test compound &#183; no target &#183; no result<br>results never leave the lab', PINK),
        ('lab keeps its data', 'proposed', 'sharing is opt-in<br>withdraw any time', PINK),
        ('low risk by design', 'today', 'cell-line images only<br>no human genetic data &#183; no pathogen data', PINK),
        ('labs leave fingerprints', 'today', fingerprint, GREEN),
        ('signed and timestamped', 'proposed', 'public record &#183; anyone can check<br>dates cannot be changed &#183; blockchain optional', GREEN),
        ('known subscribers', 'proposed', 'verified at sign-up &#183; odd access flagged<br>access log open to members', GREEN),
    ]
    tag = lambda when: (f'<span style="{MONO} font-size:13px; padding:1px 9px; border-radius:999px; border:1px solid {GREEN if when == "today" else "#949c9f"}; '
                        f'color:{GREEN if when == "today" else MUTE};">{when}</span>')
    grid = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.08 * k:.2f}s; {CARD} padding:20px 22px 18px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:center; gap:10px;">{label(name, colour)}{tag(when)}</span>'
        + (text if text.startswith('<span') else f'<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{text}</span>') + '</div>'
        for k, (name, when, text, colour) in enumerate(cards))
    # the icons of the path on 06 and 10: the map, the certificate, the exchange; and the lab's share
    icons = dict(PATH_ICONS, share='<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5V12h8.5"/>')
    steps = [('lab shares', 'images of untreated cells<br>certificate attached', PINK, 'map'),
             ('certificate checks', 'how &#8220;normal&#8221; the cells look<br>which lab &#183; what changed', GREEN, 'certificate'),
             ('subscriber pays', 'to use certified data<br>from many labs', INK, 'exchange'),
             ('lab keeps a share', 'of every subscription<br>as long as its data is used', PINK, 'share')]
    arrow = f'<span aria-hidden="true" style="flex:0 0 28px; align-self:center; text-align:center; {SANS} font-size:22px; color:{MUTE};">&#8594;</span>'
    flow = (f'<div class="r" style="animation-delay:0.8s; {FIGURE} padding:17px 0 14px; gap:0; align-items:stretch; flex-grow:1;">' + arrow.join(
        f'<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:6px; padding:4px 20px; min-width:0;">'
        f'<svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="{colour}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" style="flex-shrink:0; margin-bottom:4px;">{icons[icon]}</svg>'
        f'<span style="{SANS} font-size:22px; font-weight:700; letter-spacing:-0.02em; color:{colour};">{head}</span>'
        f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK2}; min-height:2.7em;">{what}</span></div>'   # two lines' room, so the steps line up
        for head, what, colour, icon in steps) + '</div>')
    body = f"""<div style="{BOARD}">
  {top_line('A24', 'if asked why a lab would share', 'results/e1 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Owned by the lab.<br><span style="color:{PINK};">Verified by anyone.</span></h2>
    <p style="{LEDE}">Subscribers get access, not ownership.<br>No crypto token.</p>
  </div>
  <div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; min-height:0;">{grid}</div>
  {flow}
  <div style="{NOTE}">nothing signed yet &#183; privacy A18 &#183; biosecurity A20 &#183; prices A15</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ small edits to boards that are not rebuilt
INDEX_ROW = ('<div class="c" style="display:grid; grid-template-columns:40px minmax(0,1fr); column-gap:10px; align-items:baseline; padding:8px 0; '
             'border-top:1px solid #e4e8e9; animation-delay:{delay:.2f}s;"><span style="' + MONO + ' font-size:14px; color:#666e72;">{code}</span>'
             '<div style="display:flex; flex-direction:column; gap:0; min-width:0;"><span style="' + SANS + ' font-size:17px; font-weight:600; '
             'line-height:1.2; color:#14171a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{question}</span><span style="' + MONO + ' font-size:13px; line-height:1.35; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{answer}</span></div></div>')
# every board, in order; the index is written from this list alone
BOARDS = [
    ('A1', 'Why not trust the plate&#8217;s controls?', 'sick plate, sick control'),
    ('A2', 'What is the math?', 'six calculations on 3,773 numbers'),
    ('A3', 'Why not batch-correct it away?', 'erases most of the lab fingerprint'),
    ('A4', 'Is the model the moat?', 'counting cells often wins'),
    ('A5', 'Why not just count cells?', 'two ways to ask one question'),
    ('A6', 'How often do I re-certify?', 'your &#8220;normal&#8221; expires'),
    ('A7', 'Isn&#8217;t this cell-line DNA testing (STR)?', 'which cells &#183; how they behave'),
    ('A8', 'Is the assay itself working?', 'known answer'),
    ('A9', 'Does it change the result?', 'same drug &#183; different answer'),
    ('A10', 'Does it work without stains?', 'bet on brightfield'),
    ('A11', 'Does it flag too often?', 'rarely &#183; six of 129 batches'),
    ('A12', 'What moved?', 'stain brightness, not cell count'),
    ('A13', 'How does one lab move over time?', 'own &#8220;normal&#8221; fine &#183; other labs: moved'),
    ('A14', 'What does the map buy?', 'same drug, closer between labs'),
    ('A15', 'Who pays?', 'labs join free &#183; companies pay'),
    ('A16', 'What would the money build?', 'ugliest dataset &#183; on purpose'),
    ('A17', 'Is the leaderboard fair?', 'ranked on controls &#183; never on results'),
    ('A18', 'What is private?', 'control wells leave &#183; nothing else does'),
    ('A19', 'What is the machine learning?', 'image in &#183; position and correction out'),
    ('A20', 'What about biosecurity?', 'cells show their lab &#183; labels can lie'),
    ('A21', 'How much, and what for?', 'planned $0.9M &#215; 2 = $1.8M asked'),
    ('A22', 'How big?', 'count &#215; price &#183; three streams'),
    ('A23', 'What is cell data worth?', 'priced in deals &#183; labs disagree'),
    ('A24', 'Why would a lab share?', 'owned by the lab &#183; verified by anyone')]


def index(s):
    """The appendix index, in three even columns, with a row for every board; the header tag counts the boards."""
    rows = sorted(BOARDS, key=lambda r: int(r[0][1:]))
    if os.path.exists('results/a5-pair.json'):
        pair = results('a5-pair.json')
        if pair.get('count_close') and pair.get('texture_differs'):
            rows = [(c, q, 'same count &#183; different texture' if c == 'A5' else a) for c, q, a in rows]
    column = lambda part, k0: '<div>' + ''.join(INDEX_ROW.format(code=c, question=q, answer=a, delay=0.1 + 0.03 * (k0 + k))
                                                for k, (c, q, a) in enumerate(part)) + '</div>'
    n = len(rows); sizes = [n // 3 + (i < n % 3) for i in range(3)]; cuts = [sum(sizes[:i]) for i in range(4)]
    a = s.index('<div style="display:grid; grid-template-columns:repeat(')
    b = s.index('>', a) + 1
    head = s[a:b].replace('repeat(2,minmax(0,1fr)); column-gap:40px;', 'repeat(3,minmax(0,1fr)); column-gap:28px;')
    c = s.rindex('</div></div></template>')
    out = s[:a] + head + ''.join(column(rows[cuts[i]:cuts[i + 1]], cuts[i]) for i in range(3)) + s[c:]
    return re.sub(r'(color:#[0-9a-f]{6};">)(?:Answers on request|\d+ boards)</span>', lambda k: f'{k.group(1)}{len(rows)} boards</span>', out, count=1)


def a3_bars(s):
    """A3's right card, drawn from results/e1-redteam: naming the lab from raw features, then after each plate is centred (and scaled) on its own controls, against chance. Rewritten on every run between its own markers."""
    rt = results('e1-redteam.json'); t = rt['tests']; b = t['baseline']

    def row(name, v, colour, value, dashed=False):
        bar = (f'<div style="width:{100 * v:.2f}%; height:100%; box-sizing:border-box; border-radius:4px; '
               + (f'border:1.5px dashed {FAINT};' if dashed else f'background:{colour};') + '"></div>')
        return (f'<div style="display:flex; flex-direction:column; gap:6px;">'
                f'<span style="{SANS} font-size:16px; line-height:1.2; color:{MUTE if dashed else INK};">{name}</span>'
                f'<div style="position:relative; height:28px; margin-right:96px;">{bar}'
                f'<span style="position:absolute; left:calc({100 * v:.2f}% + 8px); top:50%; transform:translateY(-50%); {SANS} '
                f'font-size:{16 if dashed else 28}px; font-weight:{400 if dashed else 700}; letter-spacing:-0.02em; line-height:1; '
                f'color:{MUTE if dashed else colour}; white-space:nowrap;">{value}</span></div></div>')

    rows = (row('no correction', b['balanced_accuracy'], PINK, f'{100 * b["balanced_accuracy"]:.1f}%')
            + row('subtract each plate&#8217;s controls', t['plate_centred']['balanced_accuracy'], INK2, f'{100 * t["plate_centred"]["balanced_accuracy"]:.0f}%')
            + row('subtract and rescale per plate', t['plate_scaled']['balanced_accuracy'], INK2, f'{100 * t["plate_scaled"]["balanced_accuracy"]:.0f}%')
            + row(f'chance &#183; 1 in {b["n_labs"]} labs', b['chance'], None, f'{100 * b["chance"]:.0f}%', dashed=True))
    card = (f'<div class="ap" data-a3="rates" style="animation-delay:0.51s; flex-grow:1; min-width:0; {CARD} padding:16px 20px; '
            f'display:flex; flex-direction:column; justify-content:space-between; gap:10px;">'
            f'{label("can a model tell which lab?<br>higher = clearer lab fingerprint")}'
            f'<div style="display:flex; flex-direction:column; gap:22px;">{rows}</div>'
            f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE};">{b["n_wells"]:,} untreated wells, '
            f'{rt["settings"]["wells_per_plate"]} per plate<br>tested on plates it never saw</span></div><!--/a3-rates-->')
    if 'data-a3="rates"' in s:
        k0, k1 = s.index('<div class="ap" data-a3="rates"'), s.index('<!--/a3-rates-->') + len('<!--/a3-rates-->')
    else:                                          # first run: the hand-built card with three stacked numbers, up to its own closing tag
        k0 = s.index('<div class="ap" style="animation-delay:0.51s;')
        depth, k1 = 0, k0
        for tag in re.finditer(r'<(/?)div\b[^>]*>', s[k0:]):
            depth += -1 if tag.group(1) else 1
            if not depth:
                k1 = k0 + tag.end()
                break
    return s[:k0] + card + s[k1:]


def patch(deck):
    """The index of every board (t10), and the bars on A3 (t13)."""
    m = re.search(r'<template id="t10">.*?</template>', deck, flags=re.S); s = index(m.group(0))
    deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'<template id="t13">.*?</template>', deck, flags=re.S)
    deck = deck[:m.start()] + a3_bars(m.group(0)) + deck[m.end():]
    return deck
