"""Appendix boards written whole from results: A8 (known answer), A11 (cry wolf), A12 (what moved)."""
import base64
import re

from parts import *

BOARD = (f'width:1280px; height:720px; box-sizing:border-box; padding:48px 56px 44px; display:flex; flex-direction:column; gap:14px; '
         f'{LIGHT_BG} position:relative; z-index:0; overflow:hidden;')
H2 = f'margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; flex-shrink:0;'
LEDE = f'margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE}; flex-grow:1;'
FIGURE = (f'box-sizing:border-box; background: linear-gradient(#ffffff, #ffffff) padding-box, linear-gradient(90deg, #be1e74, #0f8f6c) border-box; '
          f'border-top:3px solid transparent; border-radius:16px; padding:14px 22px; box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 16px 40px rgba(20,23,26,0.10); '
          f'display:flex; align-items:stretch; min-height:0; min-width:0;')
NOTE = f'{MONO} font-size:13px; line-height:1.5; color:{MUTE};'


def top(code, asked, tag):
    return (watermark(code) + f'<div style="display:flex; justify-content:space-between; align-items:baseline;">'
            f'<span style="{MONO} font-size:13px; letter-spacing:0.11em; text-transform:uppercase; color:{MUTE};">{code} &#183; {asked}</span>'
            f'<span style="{MONO} font-size:13px; letter-spacing:0.11em; text-transform:uppercase; color:{PINK};">{tag}</span></div>')


def card(title, body, delay, grow=1):
    return (f'<div class="r" style="animation-delay:{delay:.2f}s; flex:{grow}; {CARD} padding:12px 18px; display:flex; flex-direction:column; gap:5px;">'
            f'{label(title, PINK)}<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{body}</span></div>')


# ------------------------------------------------------------------ A8
def plate_map(x, y, title, sub, labelled, lookalike):
    P = 13
    g = [text(x, y - 34, title, 22, INK, weight=700), text(x, y - 10, sub, 20, MUTE)]
    g.append(f'<rect x="{x - 8}" y="{y - 2}" width="{24 * P + 16}" height="{16 * P + 12}" rx="10" fill="{PANEL}"/>')
    for r, row in enumerate('ABCDEFGHIJKLMNOP'):
        for c in range(1, 25):
            well = f'{row}{c:02d}'
            cx, cy = x + (c - 0.5) * P, y + 4 + (r + 0.5) * P
            if well in lookalike:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="5.2" fill="{PINK}"/>')
            else:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="2.2" fill="#c3c9cb"/>')
            if well in labelled:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="8.5" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    return g


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
    ax = Axes(96, 64, 600, 250, (0, len(B)), (0, 36))
    run = lambda b: re.findall(r'\d+', b['batch'])[0]
    g = ax.frame((0, 10, 20, 30), [(k + 0.5, run(b)) for k, b in enumerate(B)], 'effect size of the positive controls',
                 f'{lab_name(lab)}, batch number, in run order', f'{lab_name(lab).upper()} &#183; DID THE KNOWN ANSWER COME OUT?')
    for k, b in enumerate(B):
        bad_batch = b['verdict'] == 'failed'
        h = ax.Y(0) - ax.Y(b['size'])
        g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.06 * k:.2f}s" x="{ax.X(k + 0.18):.1f}" y="{ax.Y(b["size"]):.1f}" '
                 f'width="{ax.X(0.64) - ax.X(0):.1f}" height="{h:.1f}" rx="3" fill="{PINK if bad_batch else FAINT}"/>')
        g.append(text(ax.X(k + 0.5), ax.Y(b['size']) - 8, f'{b["agreement"]:.2f}'.lstrip('0') if b['agreement'] < 1 else '1', 17, PINK if bad_batch else MUTE, 'middle'))
    g.append(text(ax.X(9.5), ax.Y(14), f'{len(failed)} batches, {n_failed_plates} plates', 22, PINK, 'middle', 700))
    x2 = 800
    g.append(text(x2, 36, f'WHERE ON THE PLATE DOES {good["compound"].upper()} SHOW?', 22, MUTE, extra='letter-spacing="2.2"'))
    g += plate_map(x2, 112, 'a batch that came out', f'plate {good["plate"]}', set(good['wells_the_map_says_hold_it']), set(good['wells_that_look_like_it']))
    g += plate_map(x2 + 380, 112, 'a batch that failed', f'plate {bad["plate"]}', set(bad['wells_the_map_says_hold_it']), set(bad['wells_that_look_like_it']))
    ky = 366
    g.append(f'<circle cx="{x2 + 8}" cy="{ky - 6}" r="8.5" fill="none" stroke="{INK}" stroke-width="1.8"/>' + text(x2 + 26, ky, 'where the plate map puts it', 19, INK2))
    g.append(f'<circle cx="{x2 + 318}" cy="{ky - 6}" r="5.2" fill="{PINK}"/>' + text(x2 + 332, ky, 'wells that look like it', 19, INK2))
    chart = svg(1560, 390, g, fit=True, aria='Effect size of the positive controls for thirteen batches of one lab; four consecutive batches show no effect. '
                                   'On a plate from a batch that came out, the wells the map labels are the wells that show the effect; on a failed plate none does.')
    body = f'''<div style="{BOARD}">
  {top('A8', 'if asked whether the assay works', 'Is the assay working?')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:540px;">A known answer, <span style="color:{PINK};">run in every lab.</span></h2>
    <p style="{LEDE}">Untreated wells certify where a lab sits. Positive controls certify that the assay answers at all. The field already runs the same eight.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE}">{chart}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Runs now on JUMP', f'Every compound plate carries eight positive controls. In {n_batches - len(failed)} of {n_batches} batches the known answer came out.', 0.4)}
    {card('What the field caught', f'{lab_name(lab).capitalize()}, {len(failed)} consecutive batches, {n_failed_plates} plates: the wells the plate map labels as positive controls show no effect, and no other well on the plate does.', 0.5, 1.25)}
    {card('Two checks, two failures', f'The untreated-well certificate flagged {also_outside} of these {len(failed)} batches. A plate can sit in the right place and still not answer.', 0.6)}
  </div>
  <div style="{NOTE}">Number above each bar: agreement with the field. Effect: mean of the positive-control wells minus the mean of the same plate&#8217;s DMSO wells, averaged over {len(known["compounds"])} compounds; features scaled on the other labs. Whole plates downloaded and every well compared with the field&#8217;s effect of {good["compound"]}. The plate map is the public JUMP metadata [7]. results/e11</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A9
def a9():
    e8 = results('e8-redteam.json'); C = e8['all_features']['compounds']; P = e8['all_features']['pooled_within_lab_and_compound']
    order = sorted(C, key=lambda c: -C[c]['agreement_with_own_lab'])
    ax = Axes(210, 50, 560, len(order) * 40, (0, 1), (0, len(order)))
    g = [text(0, 24, 'HOW WELL A PLATE AGREES ON WHAT A DRUG DOES', 22, MUTE, extra='letter-spacing="2.2"'),
         f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>' + text(ax.X(v), ax.y0 + ax.h + 26, f'{v:g}', 19, MUTE, 'middle'))
    for k, c in enumerate(order):
        y = ax.y0 + k * 40; own, other = max(C[c]['agreement_with_own_lab'], 0), max(C[c]['agreement_with_other_labs'], 0)
        g.append(text(ax.x0 - 14, y + 26, c, 21, INK, 'end'))
        g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.05 * k:.2f}s" x="{ax.x0}" y="{y + 6}" width="{ax.X(own) - ax.x0:.1f}" height="13" rx="3" fill="#c3c9cb"/>')
        g.append(f'<rect class="bar" style="animation-delay:{0.3 + 0.05 * k:.2f}s" x="{ax.x0}" y="{y + 21}" width="{max(ax.X(other) - ax.x0, 1):.1f}" height="13" rx="3" fill="{PINK}"/>')
        g.append(text(ax.X(own) + 8, y + 18, f'{own:.2f}', 17, MUTE) + text(ax.X(other) + 8, y + 33, f'{other:.2f}', 17, PINK))
    ky = ax.y0 + ax.h + 58
    g.append(f'<rect x="{ax.x0}" y="{ky - 13}" width="26" height="13" rx="3" fill="#c3c9cb"/>' + text(ax.x0 + 34, ky, 'with its own lab', 20, INK2))
    g.append(f'<rect x="{ax.x0 + 230}" y="{ky - 13}" width="26" height="13" rx="3" fill="{PINK}"/>' + text(ax.x0 + 264, ky, 'with every other lab', 20, INK2))
    chart = svg(860, ky + 12, g, fit=True, aria='For each of eight positive controls, agreement of a plate with its own lab and with every other lab; agreement with other labs is lower for every compound.')
    strong = [c for c in order if C[c]['effect_size']['cv_of_lab_means_pct'] < 100]
    rho = [C[c]['within_labs']['spearman'] for c in order]
    cvb = [C[c]['effect_size']['cv_of_lab_means_pct'] for c in strong]; cvw = [C[c]['effect_size']['median_cv_within_lab_pct'] for c in strong]
    best = order[0]
    formula = (open('figures/assets/a9-formula-card.html').read().replace('class="ap"', 'class="r"')
               .replace('padding: 16px 22px;', 'padding: 11px 22px;').replace('gap: 8px;', 'gap: 4px;').replace('font-size: 26px;', 'font-size: 23px;'))
    small = lambda code, q, body, delay: (f'<div class="r" style="animation-delay:{delay:.2f}s; flex:1; {CARD} padding:9px 18px; display:flex; flex-direction:column; gap:2px;">'
                                          f'<div style="display:flex; justify-content:space-between;">{label(code)}{label("[e8]", PINK)}</div>'
                                          f'<span style="{SANS} font-size:17px; font-weight:600; line-height:1.25; color:{INK};">{q}</span>'
                                          f'<span style="{SANS} font-size:14px; line-height:1.35; color:{INK2};">{body}</span></div>')
    body = f'''<div style="{BOARD}">
  {top('A9', 'if asked whether it changes the answer', 'Does it change the answer?')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:580px;">Same drug. <span style="color:{PINK};">Different answer.</span></h2>
    <p style="{LEDE}">The field already contains the experiment: eight fixed compounds, each measured {e8['n_plates']:,} times, in {e8['n_labs']} labs.</p>
  </div>
  {formula}
  <div style="display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.3s; {FIGURE}">{chart}</div>
    <div style="display:flex; flex-direction:column; gap:10px; min-height:0;">
      {small('Q1 &#183; does it agree?', 'Less with other labs, for every compound.', f'{best}: {C[best]["agreement_with_own_lab"]:.2f} with its own lab, {C[best]["agreement_with_other_labs"]:.2f} with the others.', 0.4)}
      {small('Q2 &#183; does it track the controls?', 'Inside labs, yes.', f'Spearman {min(rho):.2f} to {max(rho):.2f} by compound; pooled {P["spearman"]:.2f}, shuffled {P["null_mean"]:.2f}. Between labs: same sign, too few labs.', 0.5)}
      {small('Q3 &#183; does it matter?', f'Effect size differs {min(cvb):.0f}% to {max(cvb):.0f}% between labs.', f'Inside one lab: {min(cvw):.0f}% to {max(cvw):.0f}%.', 0.6)}
    </div>
  </div>
  <div style="{NOTE}">{e8['n_plates']:,} compound plates, {e8['n_wells']:,} wells [7]. Agreement: cosine between a plate&#8217;s effect and a lab mean; each plate is compared with every lab but its own. The certificate&#8217;s own test is on slide 05, fourth view. results/e8-redteam</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A11
def a11():
    rt = results('e9-replay-redteam.json')['source_2']
    replay = results('e9-replay.json')['labs']
    B = replay['source_2']['batches']
    n = sum(v['n_batches'] for v in replay.values()); outside = sum(v['batches_outside'] for v in replay.values())
    labs_flagged = sum(v['batches_outside'] > 0 for v in replay.values())
    fl = [b for b in B if b['verdict'] == 'outside']; ok = [b for b in B if b['verdict'] != 'outside']
    names = {'as published': 'as on slide 06', 'source_1 removed from the field': 'lab 1 removed from the field',
             'source_8 removed from the field': 'lab 8 removed from the field', 'all of those labs removed': 'labs 1 and 8 both removed'}
    g = [text(0, 22, 'LAB 2 &#183; THE SAME 13 BATCHES, JUDGED TEN WAYS', 22, MUTE, extra='letter-spacing="2.2"')]
    x0, P = 470, 34
    for k, b in enumerate(B):
        g.append(text(x0 + k * P + 13, 58, short_date(b['date']).split()[0], 17, MUTE, 'middle'))
        g.append(text(x0 + k * P + 13, 76, short_date(b['date']).split()[1], 15, FAINT, 'middle'))
    changed = 0
    for r, (name, v) in enumerate(rt.items()):
        y = 92 + r * 33
        same = v['verdicts'] == rt['as published']['verdicts']; changed += not same
        g.append(text(x0 - 24, y + 19, names.get(name, name), 21, INK if same else PINK, 'end', 400 if same else 700))
        for k, c in enumerate(v['verdicts']):
            g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.04 * r + 0.01 * k:.2f}s" x="{x0 + k * P}" y="{y}" width="26" height="26" rx="6" '
                     f'fill="{PINK if c == "O" else "#7cc4aa"}"/>')
        g.append(text(x0 + 13 * P + 14, y + 19, f'{v["n_features"]:,} features', 19, FAINT))
    chart = svg(1100, 92 + len(rt) * 33 + 6, g, fit=True, aria='Verdicts for lab 2 under ten variants of the analysis; nine are identical.')
    body = f'''<div style="{BOARD}">
  {top('A11', 'if asked whether it cries wolf', 'results/e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Would it cry wolf? <span style="color:{PINK};">{outside} of {n}.</span></h2>
    <p style="{LEDE}">A flag is only worth something if it is rare, and if it survives the choices made to compute it. Both are measured.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} justify-content:center;">{chart}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('How rare', f'{outside} of {n} batches are outside, in {labs_flagged} of {len(replay)} labs. {len(replay) - labs_flagged} labs never flag.', 0.4)}
    {card('Does every plate agree', f'In lab 2&#8217;s flagged batches {sum(b["plates_outside"] for b in fl)} of {sum(b["n_plates"] for b in fl)} plates are outside. In its other {len(ok)} batches, {sum(b["plates_outside"] for b in ok)} of {sum(b["n_plates"] for b in ok)}.', 0.5)}
    {card('What changes it', f'{changed} of {len(rt)} variants: a baseline that takes in 21 June, the batch whose cell count fell. A baseline should be a batch the lab trusts.', 0.6, 1.15)}
  </div>
  <div style="{NOTE}">Rule: a plate is outside when it sits further from its lab&#8217;s first batch than from the nearest other lab&#8217;s centre. Each lab is scaled on the other ten, so it never sets its own scale. Flagged batches hold {", ".join(str(b["n_plates"]) for b in fl)} plates.</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A12
def a12():
    first = results('e6-what-moved-source_2-first-flag.json'); last = results('e6-what-moved-source_2.json')
    B = {b['batch']: b for b in results('e9-replay.json')['labs']['source_2']['batches']}
    base = next(b for b in B.values() if b['is_baseline'])
    pick = lambda e, m, c: next((g for g in e['groups'] if g['measurement'] == m and g['channel'] == c), None)
    channels = ['ER', 'AGP', 'Mito', 'DNA']
    g = []

    def panel(x0, title, measure, key, lim, ticks, xlabel):
        ax = Axes(x0 + 90, 60, 520, 4 * 62, lim, (0, 4))
        g.append(text(x0, 34, title, 22, MUTE, extra='letter-spacing="2.2"'))
        g.append(f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>')
        for v in ticks:
            g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID if v else MUTE}" stroke-width="{2 if v else 2.4}"/>')
            g.append(text(ax.X(v), ax.y0 + ax.h + 26, f'{v:+g}' if lim[0] < 0 else f'{v:g}', 19, MUTE, 'middle'))
        g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 56, xlabel, 20, INK2, 'middle'))
        for r, c in enumerate(channels):
            y = ax.y0 + r * 62
            g.append(text(ax.x0 - 14, y + 38, c, 22, INK, 'end'))
            for j, (e, colour) in enumerate(((first, PINK), (last, PALE_PINK))):
                grp = pick(e, measure, c)
                v = grp[key] if grp else 0
                xa, xb = sorted((ax.X(0), ax.X(v)))
                g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.08 * r + 0.1 * j:.2f}s" x="{xa:.1f}" y="{y + 10 + j * 22}" width="{max(xb - xa, 1):.1f}" height="18" rx="3" fill="{colour}"/>')
                g.append(text(xb + 8 if v >= 0 else xa - 8, y + 25 + j * 22, f'{v:+.1f}' if lim[0] < 0 else f'{v:.1f}', 18, PINK if j == 0 else MUTE, 'start' if v >= 0 else 'end'))
    panel(0, 'STAIN INTENSITY', 'Intensity', 'mean_shift', (-1, 3.6), (-1, 0, 1, 2, 3), 'mean shift from June, in standard deviations of the field')
    panel(760, 'TEXTURE', 'Texture', 'mean_abs_shift', (0, 3.6), (0, 1, 2, 3), 'mean absolute shift, same units')
    d1, d2 = short_date(first['date']), short_date(last['date'])
    ky = 60 + 4 * 62 + 94
    g.append(f'<rect x="90" y="{ky - 14}" width="26" height="14" rx="3" fill="{PINK}"/>' + text(124, ky, f'{d1}, the first flagged batch ({first["n_plates"]} plates)', 20, INK2))
    g.append(f'<rect x="560" y="{ky - 14}" width="26" height="14" rx="3" fill="{PALE_PINK}"/>' + text(594, ky, f'{d2} ({last["n_plates"]} plates)', 20, INK2))
    chart = svg(1500, ky + 14, g, fit=True, aria='Shift of stain intensity and texture features by channel for two flagged batches of lab 2, relative to its June baseline.')
    a, b = pick(first, 'Intensity', 'ER'), pick(first, 'Intensity', 'AGP')
    a2, b2 = pick(last, 'Intensity', 'ER'), pick(last, 'Intensity', 'AGP')
    lvl, feat = first['share_of_displacement']['by_level'], first['share_of_features']
    body = f'''<div style="{BOARD}">
  {top('A12', 'if asked what moved', 'results/e6')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Stain intensity rose. <span style="color:{PINK};">Cell count did not.</span></h2>
    <p style="{LEDE}">The certificate&#8217;s distance is a difference of two means, so it reads feature by feature.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} justify-content:center;">{chart}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Reading', f'On {d1}, {a["channel"]} and {b["channel"]} intensity sit {a["mean_shift"]:.1f} and {b["mean_shift"]:.1f} sd above June, and {100 * min(a["share_same_sign"], b["share_same_sign"]):.0f}% or more of those features moved the same way. By {d2}: {a2["mean_shift"]:.1f} and {b2["mean_shift"]:.1f}. Cells per well: {base["cells_per_well"]:.0f}, then {B[first["batch"]]["cells_per_well"]:.0f} and {B[last["batch"]]["cells_per_well"]:.0f}.', 0.4, 1.3)}
    {card('Instrument or cells', f'Image-level features carry {100 * lvl["image"]:.0f}% of the move and are {100 * feat["image"]:.0f}% of the features, so the move is not confined to acquisition. Profiles cannot tell a stain lot from biology.', 0.5)}
    {card('What a lab gets', 'Where to look first: staining and exposure in two channels. Not why. The cause is the lab&#8217;s to find, a day after the run and not four months.', 0.6)}
  </div>
  <div style="{NOTE}">Shift: mean of the batch&#8217;s plates minus mean of the lab&#8217;s first batch, per feature, in features scaled on the other ten labs and clipped to &#177;5. Bars are means over the features of one channel and measurement ({a["n_features"]} intensity and {pick(first, "Texture", "ER")["n_features"]} texture features per channel).</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ small edits to boards that are not rebuilt
INDEX_ROW = ('<div class="c" style="display:grid; grid-template-columns:44px minmax(0,1fr); column-gap:14px; align-items:baseline; padding:17px 0; '
             'border-top:1px solid #e4e8e9; animation-delay:{delay}s;"><span style="' + MONO + ' font-size:14px; color:#be1e74;">{code}</span>'
             '<div style="display:flex; flex-direction:column; gap:2px; min-width:0;"><span style="' + SANS + ' font-size:21px; font-weight:600; '
             'line-height:1.25; color:#14171a;">{question}</span><span style="' + MONO + ' font-size:14px; line-height:1.35; color:#666e72;">{answer}</span></div></div>')
NEW_BOARDS = [('A11', 'Would it cry wolf?', 'Six of 129 batches', '0.50'), ('A12', 'What moved?', 'Stain intensity, not cell count', '0.54')]


def patch(deck):
    """Index entries for the new boards, and the brightfield pair on A10."""
    m = re.search(r'<template id="t10">.*?</template>', deck, flags=re.S); s = m.group(0)
    for code, q, a, delay in NEW_BOARDS:
        if f'>{code}</span>' not in s:
            k = s.rfind('</div></div></div>')          # end of the right-hand column
            s = s[:k] + INDEX_ROW.format(code=code, question=q, answer=a, delay=delay) + s[k:]
    deck = deck[:m.start()] + s + deck[m.end():]

    m = re.search(r'<template id="t20">.*?</template>', deck, flags=re.S); s = m.group(0)
    if 'One field of one well' not in s:
        uri = lambda f: 'data:image/jpeg;base64,' + base64.b64encode(open(f'figures/assets/{f}', 'rb').read()).decode()
        img = lambda f, alt, cap, colour: (f'<div style="display:flex; flex-direction:column; gap:6px;"><div style="width:118px; height:118px; border-radius:10px; '
                                           f'overflow:hidden; background:#000;"><img src="{uri(f)}" alt="{alt}" style="width:100%; height:100%; object-fit:cover; display:block;"></div>'
                                           f'{label(cap, colour)}</div>')
        pair = (f'<div style="display:flex; gap:12px; align-items:flex-end; margin-top:auto; padding-top:10px;">'
                + img('well-I01-brightfield.jpg', 'Brightfield image of well I01, plate 1053600681.', 'brightfield', PINK)
                + img('well-I01-dna.jpg', 'DNA channel of the same field.', 'DNA stain', GREEN)
                + f'<span style="{SANS} font-size:14px; line-height:1.35; color:{MUTE}; padding-bottom:24px;">One field of one well, two ways. Lab 2, June 2021.</span></div>')
        k = s.find('JUMP images brightfield beside the stains'); k = s.find('</span>', k) + len('</span>')
        s = s[:k] + pair + s[k:]
    deck = deck[:m.start()] + s + deck[m.end():]
    return deck
