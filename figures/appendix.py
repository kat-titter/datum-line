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


def top_line(code, asked, tag=''):
    return watermark(code) + header(f'{code} &#183; {asked}', tag)


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
                 'batch, in run order', f'{lab_name(lab)} &#183; did the known answer come out?')
    for k, b in enumerate(B):
        bad_batch = b['verdict'] == 'failed'
        h = ax.Y(0) - ax.Y(b['size'])
        g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.06 * k:.2f}s" x="{ax.X(k + 0.18):.1f}" y="{ax.Y(b["size"]):.1f}" '
                 f'width="{ax.X(0.64) - ax.X(0):.1f}" height="{h:.1f}" rx="3" fill="{PINK if bad_batch else FAINT}"/>')
        if b['batch'] in (good['batch'], bad['batch']):
            g.append(text(ax.X(k + 0.5), ax.Y(b['size']) - 10, '&#9660;', 19, INK, 'middle'))
    fk = [k for k, b in enumerate(B) if b['verdict'] == 'failed']; cx = ax.X((fk[0] + fk[-1] + 1) / 2)
    g.append(text(cx, ax.Y(14), f'{len(failed)} batches', 22, PINK, 'middle', 700) + text(cx, ax.Y(14) + 28, f'{n_failed_plates} plates', 22, PINK, 'middle', 700))
    x2 = 800
    g.append(chart_title(x2, 36, f'where on the plate does {good["compound"]} show?', 20))
    g += plate_map(x2, 112, '&#9660; a batch that came out', f'{lab_name(lab)} &#183; batch {run(good)}', set(good['wells_the_map_says_hold_it']), set(good['wells_that_look_like_it']))
    g += plate_map(x2 + 380, 112, '&#9660; a batch that failed', f'{lab_name(lab)} &#183; batch {run(bad)}', set(bad['wells_the_map_says_hold_it']), set(bad['wells_that_look_like_it']))
    ky = 366
    g.append(f'<circle cx="{x2 + 8}" cy="{ky - 6}" r="8.5" fill="none" stroke="{INK}" stroke-width="1.8"/>' + text(x2 + 26, ky, 'where the map puts it', 19, INK2))
    g.append(f'<circle cx="{x2 + 318}" cy="{ky - 6}" r="5.2" fill="{GREEN}"/>' + text(x2 + 332, ky, 'where it shows', 19, INK2))
    chart = svg(1524, 390, g, fit=True, aria='Effect size of the positive controls for thirteen batches of one lab; four consecutive batches show no effect. '
                                   'On a plate from a batch that came out, the wells the map labels are the wells that show the effect; on a failed plate none does.')
    ag = lambda v: f'{v:.2f}'.lstrip('0'); ok = [b for b in B if b['verdict'] != 'failed']
    body = f'''<div style="{BOARD}">
  {top_line('A8', 'if asked whether the assay works', 'results/e11, e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:540px;">A known answer, <span style="color:{PINK};">run in every lab.</span></h2>
    <p style="{LEDE}">Untreated wells say where a lab sits.<br>Positive controls say whether it answers.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE}">{chart}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {tile(f'{n_batches - len(failed)} of {n_batches}', 'JUMP batches &#183; known answer came out', INK, 0.4)}
    {tile(f'{also_outside} of {len(failed)}', 'failed batches &#183; flagged by untreated wells', PINK, 0.5)}
  </div>
  <div style="{NOTE}">Agreement with the field: {ag(min(f["agreement"] for f in failed))}&#8211;{ag(max(f["agreement"] for f in failed))} failed, {ag(min(b["agreement"] for b in ok))}&#8211;{ag(max(b["agreement"] for b in ok))} the rest. {known["n_plates"]:,} plates, JUMP [7]. Plates {good["plate"]}, {bad["plate"]}: public JUMP plate map.</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A9
def rho_strip(C, P, order):
    """Q2 on A9: each compound's within-lab Spearman (control distance against disagreement) beside the shuffled range."""
    W, H = 470, 62
    ax = Axes(8, 22, W - 30, 18, (0, 0.6), (0, 1))
    nul = max(C[c]['within_labs']['null_95pct'] for c in order)
    g = [f'<rect x="{ax.X(0):.1f}" y="{ax.y0}" width="{ax.X(nul) - ax.X(0):.1f}" height="{ax.h}" rx="3" fill="{GRID}"/>',
         text(ax.X(0), ax.y0 - 7, 'shuffled', 13, MUTE),
         f'<path d="M {ax.X(0):.1f} {ax.y0 + ax.h} L {ax.X(0.6):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="1.5"/>']
    for v in (0, 0.2, 0.4, 0.6):
        g.append(text(ax.X(v), ax.y0 + ax.h + 17, f'{v:g}', 13, MUTE, 'middle'))
    for c in order:
        g.append(f'<circle cx="{ax.X(C[c]["within_labs"]["spearman"]):.1f}" cy="{ax.y0 + ax.h / 2}" r="5.5" fill="{INK2}"/>')
    xp = ax.X(P['spearman'])
    g.append(f'<path d="M {xp:.1f} {ax.y0 - 3} L {xp:.1f} {ax.y0 + ax.h + 3}" stroke="{INK}" stroke-width="2.5"/>' + text(xp, ax.y0 - 7, f'pooled {P["spearman"]:.2f}', 13, INK, 'middle'))
    return (svg(W, H, g, css_width='100%', aria='Within-lab Spearman correlation per compound between control-well distance and disagreement; all eight sit above the shuffled range.')
            + f'<span style="{MONO} font-size:13px; color:{MUTE};">&#961; &#183; control distance vs disagreement &#183; dot = compound</span>')


def a9():
    e8 = results('e8-redteam.json'); C = e8['all_features']['compounds']; P = e8['all_features']['pooled_within_lab_and_compound']
    order = sorted(C, key=lambda c: -C[c]['agreement_with_own_lab'])
    ax = Axes(180, 50, 500, len(order) * 40, (0, 1), (0, len(order)))
    g = [chart_title(0, 24, 'how well a plate agrees on what a drug does', 18),
         f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>' + text(ax.X(v), ax.y0 + ax.h + 26, f'{v:g}', 20, MUTE, 'middle'))
    for k, c in enumerate(order):
        y = ax.y0 + k * 40; own, other = max(C[c]['agreement_with_own_lab'], 0), max(C[c]['agreement_with_other_labs'], 0)
        g.append(text(ax.x0 - 14, y + 26, c, 21, INK, 'end'))
        g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.05 * k:.2f}s" x="{ax.x0}" y="{y + 6}" width="{ax.X(own) - ax.x0:.1f}" height="13" rx="3" fill="{PINK}"/>')
        g.append(f'<rect class="bar" style="animation-delay:{0.3 + 0.05 * k:.2f}s" x="{ax.x0}" y="{y + 21}" width="{max(ax.X(other) - ax.x0, 1):.1f}" height="13" rx="3" fill="{GREEN}"/>')
        g.append(text(ax.X(own) + 8, y + 18, f'{own:.2f}', 18, INK2) + text(ax.X(other) + 8, y + 33, f'{other:.2f}', 18, INK2))
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 52, 'agreement: cosine of a plate&#8217;s effect &#948; with a lab&#8217;s mean effect', 20, INK2, 'middle'))
    ky = ax.y0 + ax.h + 86
    g.append(f'<rect x="{ax.x0}" y="{ky - 13}" width="26" height="13" rx="3" fill="{PINK}"/>' + text(ax.x0 + 34, ky, 'with its own lab&#8217;s other plates', 20, INK2))
    g.append(f'<rect x="{ax.x0 + 340}" y="{ky - 13}" width="26" height="13" rx="3" fill="{GREEN}"/>' + text(ax.x0 + 374, ky, 'with every other lab', 20, INK2))
    chart = svg(740, ky + 12, g, fit=True, aria='For each of eight positive controls, agreement of a plate with its own lab and with every other lab; agreement with other labs is lower for every compound.')
    s = [C[c]['effect_size']['share_of_variance_between_labs'] for c in order]
    formula = open('figures/assets/a9-formula-card.html').read().replace('class="ap"', 'class="r"')
    small = lambda code, q, body, delay, grow=1: (f'<div class="r" style="animation-delay:{delay:.2f}s; flex:{grow}; {CARD} padding:9px 18px; display:flex; flex-direction:column; justify-content:center; gap:4px;">'
        f'{label(code)}<span style="{SANS} font-size:17px; font-weight:600; line-height:1.25; color:{INK};">{q}</span>'
        + (f'<div style="{SANS} font-size:14px; line-height:1.35; color:{INK2};">{body}</div>' if body else '') + '</div>')
    body = f'''<div style="{BOARD}">
  {top_line('A9', 'if asked whether it changes the answer', 'results/e8')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Same drug.<br><span style="color:{PINK};">Different answer.</span></h2>
    <p style="{LEDE}">{len(order)} positive controls, {e8["n_labs"]} labs.<br>Between labs, each drug&#8217;s effect moves in direction and size.</p>
  </div>
  {formula}
  <div style="display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.3s; {FIGURE}">{chart}</div>
    <div style="display:flex; flex-direction:column; gap:16px; min-height:0;">
      {small('Q1 &#183; does it agree?', 'Less with other labs, for every compound.', '', 0.4)}
      {small('Q2 &#183; does it track the controls?', 'Inside labs, yes.', rho_strip(C, P, order), 0.5, 1.5)}
      {small('Q3 &#183; does it matter?', f'{100 * min(s):.0f}% to {100 * max(s):.0f}% of effect-size variance is between labs.', '', 0.6)}
    </div>
  </div>
  <div style="{NOTE}">{len(order)} positive controls &#183; {e8["n_plates"]:,} plates &#183; {e8["all_features"]["n_features"]:,} features &#183; {e8["n_labs"]} labs &#183; JUMP [7] &#183; z-scored on every other lab&#8217;s DMSO wells, clipped at 5</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A10
def a10():
    """Brightfield is the bet: the lab is named from a six-dye profile, a DNA image and a brightfield image, whole batches held out."""
    rt = results('e1-redteam.json')['tests']['batch_held_out']; im = results('e15-image-model.json')['inputs']; bf = im['brightfield']
    rows = [('six-dye profile', f'{rt["n_labs"]} labs', rt, GREEN), ('DNA stain image', f'{im["dna"]["n_labs"]} labs', im['dna'], GREEN),
            ('brightfield image', f'{bf["n_labs"]} labs', bf, PINK)]
    ax = Axes(230, 64, 440, 3 * 84, (0, 1), (0, 3))
    g = [chart_title(0, 24, 'names the lab &#183; whole batches held out', 15), f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>'
                 + text(ax.X(v), ax.y0 + ax.h + 26, f'{100 * v:.0f}' + ('%' if v == 1 else ''), 19, MUTE, 'middle'))
    for k, (name, labs, r, colour) in enumerate(rows):
        c = ax.y0 + (k + 0.5) * 84; acc = r['balanced_accuracy']
        g.append(text(ax.x0 - 14, c - 3, name, 21, PINK if colour == PINK else INK, 'end', 600 if colour == PINK else 400) + text(ax.x0 - 14, c + 19, labs, 17, MUTE, 'end'))
        g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.12 * k:.2f}s" x="{ax.x0}" y="{c - 16:.1f}" width="{ax.X(acc) - ax.x0:.1f}" height="32" rx="4" fill="{colour}"/>')
        g.append(f'<path d="M {ax.X(r["chance"]):.1f} {c - 24:.1f} L {ax.X(r["chance"]):.1f} {c + 24:.1f}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        g.append(text(ax.X(acc) + 10, c + 8, f'{100 * acc:.1f}%', 22, colour, weight=700))
    g.append(text(ax.X(rows[0][2]['chance']) - 6, ax.y0 - 10, 'kill line: chance', 17, INK))
    chart = svg(760, ax.y0 + ax.h + 36, g, fit=True, aria='Balanced accuracy naming the lab with whole batches held out: six-dye profiles, a DNA-stain image and a brightfield image all sit near 100%, far above chance.')
    uri = lambda f: 'data:image/jpeg;base64,' + base64.b64encode(open(f'figures/assets/{f}', 'rb').read()).decode()
    tile = lambda f, alt, cap, colour: (f'<div style="display:flex; flex-direction:column; gap:6px;"><img src="{uri(f)}" alt="{alt}" style="width:160px; height:160px; border-radius:10px; object-fit:cover; display:block; background:#000;">{label(cap, colour)}</div>')
    gone = ' &#183; '.join(f'<s>{v}</s>' for v in ('stain lot', 'dye lot', 'staining step'))
    fair = (f'<div class="r" style="animation-delay:0.4s; {CARD} padding:16px 20px; display:flex; flex-direction:column; gap:9px; min-width:0;">'
            f'{label("why the bet is fair", GREEN)}'
            f'<span style="{SANS} font-size:20px; font-weight:600; letter-spacing:-0.015em; line-height:1.18; color:{INK};">Fewer variables, not more</span>'
            f'<div style="display:flex; justify-content:space-between; align-items:baseline; gap:8px;"><span style="{MONO} font-size:14px; line-height:1.4; color:{MUTE};">{gone}</span>{label("A3")}</div>'
            f'<div style="display:flex; gap:12px; margin-top:auto;">' + tile('well-I01-brightfield.jpg', 'Brightfield image of well I01, plate 1053600681.', 'brightfield', PINK)
            + tile('well-I01-dna.jpg', 'DNA channel of the same field.', 'DNA stain', GREEN) + '</div>'
            f'<span style="{MONO} font-size:13px; color:{MUTE};">same field &#183; lab 2 &#183; June 2021</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A10', 'if asked whether it works without stains', 'results/e1-redteam, e15')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Shown in fluorescence.<br><span style="color:{PINK};">Bet on brightfield.</span></h2>
    <p style="{LEDE}">Evidence: six dyes.<br>Product: no dye.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,2fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.2s; {FIGURE} flex-direction:column; gap:6px;">{chart}
      <span style="{SANS} font-size:19px; font-weight:700; line-height:1.3; color:{PINK};">Next: the whole map from brightfield.</span>
      <span style="{SANS} font-size:17px; line-height:1.3; color:{MUTE};">Today: nearest lab agrees with the profile map in {bf["nearest_lab_agrees_with_profiles"]} batches.</span></div>
    {fair}
  </div>
  <div style="{NOTE}">balanced accuracy &#183; whole batches held out &#183; images: one field of one untreated well, frozen vision model, no training on cells &#183; JUMP [7]</div>
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
    names = {'as published': 'as published', 'source_1 removed from the field': 'lab 1 removed from the field',
             'source_8 removed from the field': 'lab 8 removed from the field', 'all of those labs removed': 'labs 1 and 8 both removed'}
    nbase = {'baseline is the first two batches': 2, 'baseline is the first three batches': 3}
    g = []; x0, P, y0 = 370, 34, 58
    months = [short_date(b['date']).split()[1] for b in B]
    X, shift = [], 0
    for k, mth in enumerate(months):
        shift += 10 if k and mth != months[k - 1] else 0
        X.append(x0 + k * P + shift)
    for k, b in enumerate(B):
        d, mth = short_date(b['date']).split()
        if k == 0 or mth != months[k - 1]:
            g.append(text(X[k], 20, mth, 19, MUTE))
        g.append(text(X[k] + 13, 44, d, 19, MUTE, 'middle'))
    changed = 0
    for r, (name, v) in enumerate(rt.items()):
        y = y0 + r * 33
        same = v['verdicts'] == rt['as published']['verdicts']; changed += not same
        shown = names.get(name, name) + (f' &#183; {v["n_features"]:,}' if v['n_features'] != rt['as published']['n_features'] else '')
        g.append(text(x0 - 24, y + 19, shown, 21, INK if same else PINK, 'end', 400 if same else 700))
        for k, c in enumerate(v['verdicts']):
            g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.04 * r + 0.01 * k:.2f}s" x="{X[k]}" y="{y}" width="26" height="26" rx="6" '
                     f'fill="{PINK if c == "O" else "#7cc4aa"}"/>')
        g.append(f'<rect x="{X[0] - 3}" y="{y - 3}" width="{nbase.get(name, 1) * P - 2}" height="32" rx="8" fill="none" stroke="{INK2}" stroke-width="2"/>')
    chart = svg(X[-1] + 30, y0 + len(rt) * 33, g, fit=True, aria='Verdicts for lab 2 under ten variants of the analysis; nine are identical.').replace('xMidYMid', 'xMinYMin', 1)
    grid = f'<div style="flex:1 1 0; min-width:0; display:flex; flex-direction:column; gap:10px;">{label("Lab 2 &#183; the same 13 batches, judged ten ways")}{chart}</div>'
    order = sorted(replay, key=lab_number)
    rows = ''.join(
        f'<div style="display:flex; align-items:center; gap:8px; height:17px;">'
        f'<span style="{MONO} font-size:13px; width:52px; white-space:nowrap; text-align:right; color:{INK};">{lab_name(s) if replay[s]["batches_outside"] else ""}</span>'
        f'<span style="display:flex; gap:3px;">' + ''.join(f'<i style="width:8px; height:8px; border-radius:2px; background:{PINK if b["verdict"] == "outside" else "#7cc4aa"};"></i>' for b in replay[s]['batches']) + '</span></div>'
        for s in order)
    waffle = (f'<div style="flex:0 0 auto; display:flex; flex-direction:column; gap:10px;">{label(f"the field &#183; {len(replay)} labs &#183; {n} batches")}'
              f'<div role="img" aria-label="Verdicts for {n} batches in {len(replay)} labs; {outside} are outside, in {labs_flagged} labs." style="flex:1; display:flex; flex-direction:column; justify-content:center;">{rows}</div></div>')
    body = f'''<div style="{BOARD}">
  {top_line('A11', 'if asked whether it cries wolf', 'results/e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Would it cry wolf?<br><span style="color:{PINK};">{outside} of {n}.</span></h2>
    <p style="{LEDE}">Rare across the field.<br>Same verdict under {len(rt) - changed} of {len(rt)} analyses.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} gap:32px;">{waffle}{grid}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('How rare', f'{outside} of {n} batches outside, in {labs_flagged} of {len(replay)} labs<br>{len(replay) - labs_flagged}&nbsp;labs never flag', 0.4)}
    {card('Does every plate agree', f'<span style="display:flex; align-items:baseline; gap:10px;"><b style="{SANS} font-size:22px; font-weight:600; color:{PINK};">{sum(b["plates_outside"] for b in fl)} of {sum(b["n_plates"] for b in fl)}</b><span style="{MONO} font-size:13px; color:{MUTE};">plates outside &#183; flagged</span></span>'
                                  f'<span style="display:flex; align-items:baseline; gap:10px;"><b style="{SANS} font-size:22px; font-weight:600; color:{INK2};">{sum(b["plates_outside"] for b in ok)} of {sum(b["n_plates"] for b in ok)}</b><span style="{MONO} font-size:13px; color:{MUTE};">plates outside &#183; the rest</span></span>', 0.5)}
    {card('What changes it', f'{changed} of {len(rt)} variants differs<br>its baseline takes in 21 Jun, whose cell count fell', 0.6, 1.15)}
  </div>
  <div style="{NOTE}"><span style="color:#7cc4aa;">&#9632;</span> in distribution &#160; <span style="color:{PINK};">&#9632;</span> outside &#160; <span style="color:{INK2};">&#9634;</span> baseline &#160;&#183;&#160; Outside: further from its own first batch than from the nearest other lab.</div>
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
    tile = lambda n, c, cap, colour: (f'<div style="display:flex; flex-direction:column; gap:2px; min-width:0;"><div style="aspect-ratio:1/1; max-height:120px; border-radius:10px; overflow:hidden; background:#000;">'
                                      f'<img src="{uri(f"figures/assets/a12-{n}-{c}.png")}" alt="{cap}, {c} channel, one control well of lab 2, auto-scaled." style="width:100%; height:100%; object-fit:cover; display:block;"></div>'
                                      f'{label(cap, colour)}<span style="{SANS} font-size:15px; font-weight:600; color:{colour};">{W["channels"][c][n]["p99_8"]:,} counts</span></div>')
    rows = ''.join(f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">{tile("first", c, short_date(W["date_first"]) + " &#183; " + c, MUTE)}{tile("flagged", c, short_date(W["date_flagged"]) + " &#183; " + c, PINK)}</div>' for c in channels)
    ratio = {c: W['channels'][c]['flagged']['p99_8'] / W['channels'][c]['first']['p99_8'] for c in channels + ('DNA',)}
    return (f'<div class="r" style="animation-delay:0.35s; width:300px; flex-shrink:0; {FIGURE} flex-direction:column; gap:8px; padding:15px 16px 12px; overflow:hidden;">'
            f'{label("AS THE MICROSCOPE SHOWS THEM", INK)}{rows}'
            f'<span style="{SANS} font-size:14px; line-height:1.35; color:{INK};">raw counts {ratio[channels[0]]:.0f}&#215; apart &#183; DNA {ratio["DNA"]:.0f}&#215;<br>pattern: perinuclear &#8594; whole cell</span></div>')


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
    panel(0, 'stain intensity', 'Intensity', 'mean_shift', (0, 3.5), (0, 1, 2, 3), f'mean shift from {short_date(base["date"])} &#183; sd of the field')
    panel(600, 'texture', 'Texture', 'mean_abs_shift', (0, 3.5), (0, 1, 2, 3), 'mean absolute shift &#183; same units')
    d1, d2 = short_date(first['date']), short_date(last['date'])
    ky = 60 + 4 * 54 + 88
    g.append(f'<rect x="90" y="{ky - 14}" width="26" height="14" rx="3" fill="{PINK}"/>' + text(124, ky, f'{d1} &#183; first flagged &#183; {first["n_plates"]} plates', 21, INK2))
    g.append(f'<rect x="690" y="{ky - 14}" width="26" height="14" rx="3" fill="{PALE_PINK}"/>' + text(724, ky, f'{d2} &#183; {last["n_plates"]} plates', 21, INK2))
    chart = svg(1110, ky + 12, g, fit=True, aria='Shift of stain intensity and texture features by channel for two flagged batches of lab 2, relative to its first batch.')
    pictures = raw_pair(base, B[first['batch']])
    a, b = pick(first, 'Intensity', 'ER'), pick(first, 'Intensity', 'AGP')
    cpw = [x['cells_per_well'] for x in B.values() if x['verdict'] != 'outside']
    lvl, feat = first['share_of_displacement']['by_level'], first['share_of_features']
    body = f'''<div style="{BOARD}">
  {top_line('A12', 'if asked what moved', 'results/e6')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Intensity rose.<br><span style="color:{PINK};">Cell count did not.</span></h2>
    <p style="{LEDE}">Lab 2&#8217;s flagged batches against its first batch, {short_date(base["date"])}.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.2s; flex:1 1 0; {FIGURE} justify-content:center;">{chart}</div>
    {pictures}
  </div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Reading', f'{100 * min(a["share_same_sign"], b["share_same_sign"]):.0f}% or more of {a["channel"]} and {b["channel"]} intensity features rose<br>cells per well {base["cells_per_well"]:.0f} &#8594; {B[first["batch"]]["cells_per_well"]:.0f} &#8594; {B[last["batch"]]["cells_per_well"]:.0f}<br>inside the lab&#8217;s own range, {min(cpw):.0f}&#8211;{max(cpw):.0f}', 0.4, 1.3)}
    {card('Instrument or cells', f'Image-level features carry {100 * lvl["image"]:.0f}% of the move and are {100 * feat["image"]:.0f}% of the features, so the move is not confined to acquisition. Profiles cannot tell a stain lot from biology.', 0.5)}
    {card('What a lab gets', 'Look first: exposure &#183; ER stain<br>Check: stain mix-up &#183; bleed-through &#183; biology<br>Not why: that is the lab&#8217;s to find', 0.6, 1.15)}
  </div>
  <div style="{NOTE}">means over the features of one channel &#183; sd: standard deviation of the field &#183; JUMP [7]</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A13
def a13():
    from slide04 import cell_count_chart, distance_chart
    B = results('e9-replay.json')['labs']['source_2']['batches']
    panel = lambda chart, delay: f'<div class="r" style="animation-delay:{delay}s; flex:1; {FIGURE} justify-content:center;">{chart}</div>'
    body = f"""<div style="{BOARD}">
  {top_line('A13', 'if asked how one lab moves over time', 'results/e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Alone, it looks fine.<br><span style="color:{PINK};">Among everyone, it moves.</span></h2>
    <p style="{LEDE}">Same {len(B)} batches, two views.<br>Not a verdict: a reason to look.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0;">{panel(cell_count_chart(B), 0.2)}{panel(distance_chart(B), 0.35)}</div>
  <div style="{NOTE}">unit: the field&#8217;s within-plate spread &#183; nearest lab: closest centre &#183; lab 2 &#183; U2OS &#183; 2021 &#183; JUMP [7] &#183; what moved: A12</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A14
def a14():
    e12 = results('e12-field-normalization.json')
    E = e12['every_batch']
    rows = [('agreement with every other lab', 'agree_field'), ('margin over the wrong drug', 'margin'),
            ('right drug recognised, share', 'matched'), ('agreement with own first batch', 'agree_own')]
    ways = [('raw', 'as measured', FAINT), ('own', 'own controls', MUTE), ('field', 'the field&#8217;s frame', GREEN)]
    ax = Axes(430, 50, 760, len(rows) * 84, (0, 1), (0, len(rows)))
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>' + text(ax.X(v), ax.y0 + ax.h + 26, f'{v:g}', 21, MUTE, 'middle'))
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 56, 'mean over batches &#183; cosine', 21, INK2, 'middle'))
    for r, (name, key) in enumerate(rows):
        y = ax.y0 + r * 84
        g.append(text(ax.x0 - 16, y + 38, name, 24, INK, 'end'))
        g.append(text(ax.x0 - 16, y + 62, f'above own controls in {E[key]["field_better_than_own_in"]}', 21, GREEN if key in ('agree_field', 'margin') else MUTE, 'end'))
        for j, (way, _, colour) in enumerate(ways):
            v = E[key][way]
            g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.08 * r + 0.08 * j:.2f}s" x="{ax.x0}" y="{y + 9 + j * 23}" width="{ax.X(v) - ax.x0:.1f}" height="19" rx="3" fill="{colour}"/>')
            g.append(text(ax.X(v) + 8, y + 25 + j * 23, f'{v:.2f}', 21, GREEN if way == 'field' else MUTE, weight=700 if way == 'field' else 400))
    for j, (_, name, colour) in enumerate(ways):
        g.append(f'<rect x="1250" y="{ax.y0 + 20 + j * 40}" width="26" height="16" rx="3" fill="{colour}"/>' + text(1286, ax.y0 + 35 + j * 40, name, 22, INK2))
    chart = svg(1560, ax.y0 + ax.h + 70, g, fit=True, aria='Four measures of agreement between batches under three normalisations; the field\'s frame is highest on three and level on the fourth.')
    grid = [json.load(open(f)) for f in sorted(glob.glob('results/e12-field-normalization-*.json'))]
    if grid:
        ks, sh = sorted({v['k'] for v in grid + [e12]}), sorted({v['shrink'] for v in grid + [e12]})
        n = E['n_batches']; X = lambda c: 110 + c / n * 390
        s = [f'<path d="M {X(0):.1f} 50 L {X(n):.1f} 50" stroke="{GRID}" stroke-width="1.5"/>',
             f'<path d="M {X(n / 2):.1f} 4 L {X(n / 2):.1f} 50" stroke="{FAINT}" stroke-width="1.5" stroke-dasharray="4 4"/>',
             text(X(0), 66, '0', 13, MUTE, 'middle'), text(X(n / 2), 66, 'half', 13, MUTE, 'middle'), text(X(n), 66, f'{n}', 13, MUTE, 'middle')]
        for r, (name, key) in enumerate((('agreement', 'agree_field'), ('margin', 'margin'))):
            y = 14 + r * 24
            s.append(text(0, y + 5, name, 15, INK))
            for v in [e12] + grid:
                c = int(v['every_batch'][key]['field_better_than_own_in'].split()[0])
                s.append(f'<circle cx="{X(c):.1f}" cy="{y}" r="5.5" fill="{GREEN}" stroke="#ffffff" stroke-width="1.5"/>')
                if c < n / 2:
                    s.append(text(X(c) - 12, y + 5, f'shrinkage {v["shrink"]:g}', 13, MUTE, 'end'))
        holds = (svg(520, 72, s, aria='Batches above own controls under five settings: all above half but one.')
                 + f'<span style="{MONO} font-size:13px; color:{MUTE};">batches above own controls &#183; {ks[0]}&#8211;{ks[-1]} components &#183; shrinkage {sh[0]:g}&#8211;{sh[-1]:g}</span>')
    else:
        holds = 'Sensitivity runs pending.'
    cv = E['effect_size_cv_across_batches_within_lab']
    body = f"""<div style="{BOARD}">
  {top_line('A14', 'if asked what the field&#8217;s frame buys', 'results/e12')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">One frame: <span style="color:{PINK};">what it buys.</span></h2>
    <p style="{LEDE}">Untreated wells map each batch onto a field built without its lab.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} justify-content:center;">{chart}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Does it hold', holds, 0.4)}
    {card('What it does not do', f'Effect sizes still vary between batches<br>spread {cv["raw"]:.2f} as measured &#183; {cv["own"]:.2f} own controls &#183; {cv["field"]:.2f} field&#8217;s frame', 0.5)}
  </div>
  <div style="{NOTE}">{e12["n_plates"]:,} plates, {e12["n_labs"]} labs, {len(e12["compounds"])} positive controls, {e12["k"]} principal components. Own controls: each feature standardised on the batch&#8217;s untreated wells.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A17
def a17():
    lb = results('e14-leaderboard.json')
    names = {'centre': 'off centre', 'tightness': 'plate spread', 'steadiness': 'drift', 'cells': 'cell-count gap'}
    cols = 'grid-template-columns:64px 72px 140px 56px 64px repeat(4,1fr);'
    cell = lambda s, colour=INK, weight=400, align='left': f'<span style="{SANS} font-size:15px; font-weight:{weight}; color:{colour}; text-align:{align}; font-variant-numeric:tabular-nums;">{s}</span>'
    right = ('batches', 'best', 'streak')
    head = (f'<div style="display:grid; {cols} gap:12px; padding:0 8px 4px; border-bottom:1px solid #d3d8da;">'
            + ''.join(f'<span style="text-align:{"right" if s in right else "left"};">{label(s)}</span>' for s in ('lab', 'batches', 'score', 'best', 'streak'))
            + ''.join(label(v) for v in names.values()) + '</div>')
    bar = lambda v: (f'<span style="display:inline-block; width:22px; text-align:right;">{v["median_score"]:.0f}</span>'
                     f'<i style="display:inline-block; vertical-align:middle; margin-left:8px; width:{v["median_score"]:.0f}px; height:8px; border-radius:4px; background:{PINK if v["lab"] == "source_2" else "#c3c9cb"};"></i>')
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.05 * k:.2f}s; display:grid; {cols} gap:12px; padding:3px 8px; border-bottom:1px solid #eceff0; flex:1 1 auto; align-items:center; '
        f'background:{"rgba(190,30,116,0.07)" if v["lab"] == "source_2" else "transparent"}; border-radius:6px;">'
        + cell(lab_name(v['lab']), PINK if v['lab'] == 'source_2' else INK, 700 if v['lab'] == 'source_2' else 500)
        + cell(v['n_batches'], align='right') + cell(bar(v), INK, 700) + cell(f'#{v["best"]["rank"]}', align='right') + cell(f'{v["streak"]["longest"]}', align='right')
        + ''.join(cell('&#8212;' if v[f'median_{m}'] is None else f'{v[f"median_{m}"]:.2f}') for m in names)
        + '</div>' for k, v in enumerate(lb['by_lab']))
    field = (f'<div class="r" style="animation-delay:{0.2 + 0.05 * len(lb["by_lab"]):.2f}s; display:grid; {cols} gap:12px; padding:3px 8px; flex:1 1 auto; align-items:center; border-top:1px solid {GREEN};">'
             + cell('field', GREEN, 600) + cell(lb['n_batches'], GREEN, 600, 'right') + cell('&#8212;', MUTE) + cell('&#8212;', MUTE, 400, 'right') * 2
             + ''.join(cell(f'{lb["field_median"][m]:.2f}', GREEN, 600) for m in names) + '</div>')
    table = f'<div style="display:flex; flex-direction:column; flex:1 1 0; min-width:0;">{head}{rows}{field}</div>'
    top = lb['top'][0]
    score_body = (f'<span style="display:block; {MATH} font-size:22px; line-height:1.2;">score = 100 &#8722; mean percentile</span>'
                  f'<span style="display:block; margin-top:4px; {MONO} font-size:13px; color:{MUTE};">4 measures &#183; among {lb["n_batches"]} batches &#183; higher is better</span>')
    best_body = (f'<span style="display:block; font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1;">{top["score"]:.0f}</span>'
                 f'<span style="display:block; margin-top:6px; {MONO} font-size:13px; color:{MUTE};">{lab_name(top["lab"])} &#183; {short_date(top["date"])} &#183; {top["n_plates"]} plates</span>'
                 f'<span style="display:block; {MONO} font-size:13px; color:{MUTE};">{lab_name(top["lab"])} holds {sum(r["lab"] == top["lab"] for r in lb["top"])} of top 10</span>')
    body = f"""<div style="{BOARD}">
  {top_line('A17', 'if asked about the game', 'results/e14')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">A game, <span style="color:{PINK};">not a report card.</span></h2>
    <p style="{LEDE}">Every batch ranked on its untreated wells, never on results.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} flex-direction:column; padding:17px 14px 14px;">{table}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('score', score_body, 0.5, 1.4, MUTE)}
    {card('best batch', best_body, 0.6, colour=MUTE)}
    {card('your choice to play', 'Named only if you opt in.<br>Private version for your own plates.', 0.7)}
  </div>
  <div style="{NOTE}">Lab medians; lower is better on the four measures &#183; {lb["n_plates"]:,} plates &#183; {lb["n_labs"]} labs &#183; {lb["n_batches"]} batches &#183; streak: in distribution, in a row &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A18
def a18():
    import csv, gzip
    e9 = results('e9-replay.json'); L2 = e9['labs']['source_2']
    e12 = results('e12-field-normalization.json')
    plate = L2['batches'][0]['plates'][0]
    wells = [w for w in csv.DictReader(gzip.open('metadata/well.csv.gz', 'rt')) if w['Metadata_Plate'] == plate]
    dmso = {w['Metadata_Well'] for w in wells if w['Metadata_JCP2022'] == 'JCP2022_033924'}
    P = 9
    platefig = (svg(24 * P + 16, 16 * P + 12, plate_map(8, 2, '', '', set(), dmso, P=P, colour=PINK), css_width=f'{24 * P + 16}px',
                    aria=f'One 384-well plate from lab 2: the {len(dmso)} untreated wells, in two columns, are the only wells that leave.')
                + f'<span style="{MONO} font-size:13px; color:{MUTE}; margin-top:4px;">pink: {len(dmso)} of {len(wells)} wells leave &#183; JUMP [7]</span>')
    big = lambda s: f'<span style="{SANS} font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{INK}; padding-top:2px;">{s}</span>'
    col = lambda title, colour, items: (f'<div class="r" style="flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:10px; min-width:0;">'
                                        f'{label(title, colour)}' + ''.join(
                                            f'<div style="display:flex; flex-direction:column; gap:2px; padding-top:8px; border-top:1px solid #eceff0;">'
                                            f'<span style="{SANS} font-size:17px; font-weight:600; line-height:1.25; color:{INK};">{h}</span>'
                                            + (b if b.startswith('<') else f'<span style="{SANS} font-size:15px; line-height:1.35; color:{MUTE};">{b}</span>') + '</div>' for h, b in items) + '</div>')
    leaves = col('What leaves the building', PINK, [
        ('untreated control wells only', 'images or well-level profiles, no compound'),
        ('a plate map of the control wells', platefig),
        ('nothing else', big(f'{L2["n_reference_wells"]:,}') + f'<span style="{MONO} font-size:13px; color:{MUTE};">untreated wells &#183; {len(L2["reference_labs"])} labs &#183; 0 treated</span>')])
    uses = col('What Datum Line does with it', GREEN, [
        ('builds the map', f'one centroid per plate, in a space scaled on every other lab. The lab being placed never sets its own scale ({e9["labs"]["source_2"]["n_features"]:,} features here).'),
        ('answers', 'position&#160;&#183; distance to own baseline&#160;&#183; nearest lab&#160;&#183; cells per well&#160;&#183; verdict&#160;&#183; rank'),
        ('computes a move, not a model of you', f'one matrix per batch, fitted on your controls&#160;&#183; {e12["k"]}&#160;components&#160;&#183; A19')])
    never = col('What it never sees', INK, [
        ('your treated data', 'the move is sent to you and applied on your side. Your results are normalised in your building, by you.'),
        ('your name, unless you choose', 'proposed: labs appear as a number; a lab opts in to a name. Every JUMP lab here is a number.'),
        ('your images, for long', 'proposed: images are reduced to profiles on arrival and the originals deleted; the profile of a control well is what is kept.')])
    body = f"""<div style="{BOARD}">
  {top_line('A18', 'if asked what is private', 'results/e9, e12 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Control wells leave.<br><span style="color:{PINK};">Nothing else does.</span></h2>
    <p style="{LEDE}">No compound, no target, no result.<br>Nothing to clear.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0; align-items:stretch;">{leaves}{uses}{never}</div>
  <div style="{NOTE}">Every analysis here runs on this rule &#183; github.com/kat-titter/datum-line/analysis &#183; JUMP, CC0 [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A19
def a19():
    e1 = results('e1.json')['all_sources']; e12 = results('e12-field-normalization.json')
    e15 = results('e15-image-model.json') if os.path.exists('results/e15-image-model.json') else None
    if e15 and 'balanced_accuracy' in e15['inputs'].get('brightfield', {}):
        def bar(name):
            v = 100 * e15['inputs'][name]['balanced_accuracy']
            return (f'<span style="display:flex; flex-direction:column; gap:3px;">'
                    f'<span style="display:flex; justify-content:space-between; {MONO} font-size:13px; line-height:1.2; color:{INK2};"><span>{name}</span><span>{v:.1f}%</span></span>'
                    f'<span style="display:block; height:8px; border-radius:4px; background:{PANEL};"><span style="display:block; height:100%; width:{v:.1f}%; border-radius:4px; background:{INK2};"></span></span></span>')
        short = (f'<span style="display:flex; flex-direction:column; gap:8px; padding-top:4px;">{bar("brightfield")}{bar("dna")}'
                 f'<span style="{MONO} font-size:13px; line-height:1.3; color:{MUTE};">one picture &#183; names the lab</span></span>')
    else:
        short = 'e15, running'
    big = lambda s, colour=INK: f'<span style="{SANS} font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{colour};">{s}</span>'
    step = lambda k, title, lines, body, colour: (
        f'<div class="r" style="animation-delay:{0.2 + 0.2 * k:.2f}s; flex:1; {CARD} padding:18px 20px 16px; display:flex; flex-direction:column; gap:10px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:baseline;">{label(f"step {k + 1}", MUTE)}{label(title, colour)}</span>'
        f'<div style="height:112px; display:flex; align-items:center;">{body}</div>'
        + ''.join(f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK if i == 0 else MUTE};">{l}</span>' for i, l in enumerate(lines)) + '</div>')
    arrow = f'<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" style="flex-shrink:0; align-self:center;"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="{GREEN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    uri = lambda f: 'data:image/jpeg;base64,' + base64.b64encode(open(f'figures/assets/{f}', 'rb').read()).decode()
    tile = lambda f, alt, cap: (f'<div style="display:flex; flex-direction:column; gap:4px;"><img src="{uri(f)}" alt="{alt}" style="width:92px; height:92px; border-radius:10px; object-fit:cover; display:block; background:#000;">'
                                f'<span style="{MONO} font-size:13px; line-height:1; color:{MUTE};">{cap}</span></div>')
    img = ('<div style="display:flex; gap:8px;">' + tile('well-I01-brightfield.jpg', 'Brightfield image of one untreated well.', 'brightfield')
           + tile('well-I01-dna.jpg', 'DNA channel of the same field.', 'dna') + '</div>')
    n_feat = f"{e1['n_features']:,}"
    numbers = f'<div style="display:flex; flex-direction:column; gap:4px;">{big(n_feat)}<span style="{MONO} font-size:13px; color:{MUTE};">numbers per well today</span></div>'
    acc, chance = f"{100 * e1['balanced_accuracy']:.1f}%", f"{100 * e1['chance']:.0f}%"
    mapfig = f'<div style="display:flex; flex-direction:column; gap:4px;">{big(acc, GREEN)}<span style="{MONO} font-size:13px; color:{MUTE};">a classifier names the lab; chance {chance}</span></div>'
    it = lambda s: f'<mi mathvariant="normal" style="font-style:italic">{s}</mi>'
    sub = lambda s: f'<mtext style="font-size:13px">{s}</mtext>'          # scripts held at the 13px floor; MathML would shrink them to 12
    half = '<mrow style="font-size:13px"><mspace width="0.12em"/><mn>&#189;</mn></mrow>'
    minus_half = '<mrow style="font-size:13px"><mspace width="0.12em"/><mo form="prefix" lspace="0" rspace="0">&#8722;</mo><mn>&#189;</mn></mrow>'
    formula = (f'<math style="{MATH} font-size:16px; color:{INK}; white-space:nowrap;">' + it('x&#8242;') + '<mo>=</mo>'
               + '<msubsup>' + it('C') + sub('field') + half + '</msubsup>'
               + '<msubsup>' + it('C') + sub('batch') + minus_half + '</msubsup>'
               + '<mo>(</mo>' + it('x') + '<mo>&#8722;</mo><msub>' + it('m') + sub('batch') + '</msub><mo>)</mo></math>')
    move = (f'<div style="display:flex; flex-direction:column; gap:6px;">{formula}'
            f'<span style="{MONO} font-size:13px; color:{MUTE};">per batch &#183; {e12["k"]} components</span></div>')
    steps = (step(0, 'an image', ['One untreated well.'], img, PINK) + arrow
             + step(1, 'numbers', ['CellProfiler today.<br>Vision model next:', short], numbers, MUTE) + arrow
             + step(2, 'the map', ['Z-scored on every other lab; one point per plate.', 'The lab being placed never sets its own scale.'], mapfig, GREEN) + arrow
             + step(3, 'the move', ['Your batch onto the field&#8217;s frame; applied on your side.'], move, PINK))
    body = f"""<div style="{BOARD}">
  {top_line('A19', 'if asked what the machine learning is', 'results/e1, e12, e15')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Image in.<br><span style="color:{PINK};">Place, distance, move out.</span></h2>
    <p style="{LEDE}">Data stays where it is.<br>Models and moves travel.</p>
  </div>
  <div style="display:flex; gap:12px; flex-grow:1; min-height:0; align-items:stretch;">{steps}</div>
  <div style="{NOTE}">One laptop runs the whole replay from cache in minutes. Every script: github.com/kat-titter/datum-line/analysis. What leaves a lab: A18.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A20
def a20():
    e1 = results('e1.json')['all_sources']; e9 = results('e9-replay.json')['labs']; e11 = results('e11-known-answer.json')
    near = sorted(b['to_nearest_other'] for v in e9.values() for b in v['batches'])
    n_batches = len(near); farthest = near[-1]
    own = sum(b['wells_named_own_lab'] >= 1 for v in e9.values() for b in v['batches'])
    failed_plates = sum(f['n_plates'] for f in e11['failed'])
    col = lambda title, colour, big, items, fig, cap: (
        f'<div class="r" style="flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'{label(title, colour)}<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; padding:6px 0 4px; height:50px;">{big}</span>' + ''.join(
            f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK if i == 0 else MUTE};">{l}</span>' for i, l in enumerate(items))
        + f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:6px;">{svg(240, 80, fig)}<span style="{MONO} font-size:13px; color:{MUTE};">{cap}</span></div></div>')
    # provenance: one square per batch, solid where every well names its own lab
    shares = sorted((b['wells_named_own_lab'] for v in e9.values() for b in v['batches']), reverse=True)
    waffle = [f'<rect x="{11 + (k % 22) * 10}" y="{22 + (k // 22) * 10}" width="8" height="8" rx="1.5" fill="{GREEN}" fill-opacity="{1 if s >= 1 else 0.3}"/>' for k, s in enumerate(shares)]
    # integrity: the known answer, batch by batch, in A8's colours
    lab = e11['failed'][0]['lab']; S = e11['labs'][lab]['batches']; top = max(b['size'] for b in S); w = 240 / len(S)
    bars = ([f'<rect x="{k * w + 3:.1f}" y="{76 - 56 * b["size"] / top:.1f}" width="{w - 6:.1f}" height="{56 * b["size"] / top:.1f}" rx="2" fill="{PINK if b["verdict"] == "failed" else FAINT}"/>' for k, b in enumerate(S)]
            + [f'<path d="M 0 76 H 240" stroke="{GRID}" stroke-width="1"/>'])
    # cells from nowhere: every real batch's distance to its nearest other lab, and the zone beyond the farthest
    T = lambda x, y, s, anchor='middle': f'<text x="{x:.1f}" y="{y:.1f}" style="{MONO}" font-size="13" fill="{MUTE}" text-anchor="{anchor}">{s}</text>'
    X = lambda v: 8 + v / 10 * 220
    rug = ([f'<rect x="{X(farthest):.1f}" y="22" width="{X(10) - X(farthest):.1f}" height="36" fill="{PANEL}"/>']
           + [f'<path d="M {X(v):.1f} 26 V 56" stroke="{GREEN}" stroke-width="1.5" stroke-opacity="0.4"/>' for v in near]
           + [f'<path d="M {X(farthest):.1f} 18 V 58" stroke="{INK}" stroke-width="1.5"/>', T(X(farthest) - 5, 14, 'farthest real batch', 'end')]
           + [T(X(v), 76, v) for v in (0, 5, 10)])
    # sentinels: lab 2's distance from its own first batch, batch by batch
    L = e9['source_2']['batches']; top2 = max(b['from_baseline'] for b in L)
    pts = [(10 + k * 220 / (len(L) - 1), 72 - 56 * b['from_baseline'] / top2) for k, b in enumerate(L)]
    line = ([f'<path d="M 0 76 H 240" stroke="{GRID}" stroke-width="1"/>', '<path d="' + ' '.join(f'{"M" if k == 0 else "L"} {x:.1f} {y:.1f}' for k, (x, y) in enumerate(pts)) + f'" fill="none" stroke="{PINK}" stroke-width="2" stroke-linejoin="round"/>']
            + [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PINK if b["verdict"] == "outside" else "#ffffff"}" stroke="{PINK}" stroke-width="1.5"/>' for (x, y), b in zip(pts, L)])
    where = col('provenance', GREEN, f'{100 * e1["balanced_accuracy"]:.1f}%', [
        f'of {e1["n_wells"]:,} untreated wells name their true lab, on plates the classifier never saw.'], waffle, f'{n_batches} batches &#183; {own} every well')
    labels = col('integrity', PINK, f'{len(e11["failed"])} batches', [
        f'{failed_plates} plates whose plate map says positive control, and whose cells show no effect; no other well on those plates does either.'],
        bars, f'{lab_name(lab)} &#183; effect per batch &#183; A8')
    nowhere = col('cells from nowhere', INK, f'{farthest:.0f} spreads', [
        f'the farthest any of {n_batches} real batches sits from every other lab. Beyond that, a culture is not the line it claims, or not alone.',
        'untested &#183; proposed as the first partner-lab test'], rug, 'distance to nearest other lab')
    sentinel = col('sentinels', MUTE, 'proposed', [
        'An untreated well is a canary. If the controls move and nobody changed anything, something in the room did: a lot, a reagent, the air, the water.'],
        line, 'lab 2 &#183; drift by batch &#183; A13')
    body = f"""<div style="{BOARD}">
  {top_line('A20', 'if asked about biosecurity', 'results/e1, e9, e11 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Cells cannot lie <span style="color:{PINK};">about where they came from.</span></h2>
    <p style="{LEDE}">One map of untreated wells.<br>Two checks measured, two proposed.</p>
  </div>
  <div style="display:flex; gap:14px; flex-grow:1; min-height:0; align-items:stretch;">{where}{labels}{nowhere}{sentinel}</div>
  <div style="{NOTE}">Defensive by construction: untreated wells only &#183; no result or perturbation stored &#183; distances in within-plate spreads &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A21
PRESEED = [  # eighteen months; every line is a proposal
    ('leader, to run it', '18 months', 180),
    ('scientific lead (me)', '18 months', 180),
    ('ML engineer', 'from month 7', 160),
    ('payroll overhead', '20% of salaries', 104),
    ('benchmark playground', '~60 plates &#183; planted failures &#183; partner labs or a CRO', 120),
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
    sub, total = preseed_total()
    bench = sum(k for name, _, k in PRESEED if name in ('benchmark playground', 'partner-lab bench time'))
    people = sum(k for _, _, k in PRESEED[:4])   # leader, scientific lead, ML engineer, payroll overhead
    run = sub - people - bench                   # compute, legal, travel
    seg = lambda k, c: f'<div style="flex:{k} 0 0; background:{c};"></div>'
    tag = lambda k, s, c: f'<span style="flex:{k} 0 0; min-width:0; {MONO} font-size:13px; line-height:1.3; color:{c};">{s}<br>{100 * k / sub:.0f}%</span>'
    split = (f'<div style="flex-grow:1; min-width:0; display:flex; flex-direction:column; gap:6px;">'
             f'<span style="{MONO} font-size:13px; color:{MUTE};">${sub}k planned &#215; {MULTIPLIER} = ${total / 1000:.2f}M asked</span>'
             f'<div style="display:flex; gap:2px; height:16px; border-radius:8px; overflow:hidden;">{seg(people, INK)}{seg(bench, GREEN)}{seg(run, FAINT)}</div>'
             f'<div style="display:flex; gap:2px;">{tag(people, "people", INK)}{tag(bench, "benchmark", GREEN)}{tag(run, "running", MUTE)}</div></div>')
    row = lambda name, what, k, strong=False, colour=INK, rule='border-bottom:1px solid #eceff0;', size=15: (
        f'<div style="display:grid; grid-template-columns:260px 1fr 90px; gap:16px; align-items:baseline; padding:4px 10px; {rule}">'
        f'<span style="{SANS} font-size:{size}px; font-weight:{700 if strong else 600}; color:{colour};">{name}</span>'
        f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{what}</span>'
        f'<span style="{SANS} font-size:{size}px; font-weight:{700 if strong else 500}; color:{colour}; text-align:right;">{f"${k / 1000:.2f}M" if k >= 1000 else f"${k}k"}</span></div>')
    table = (''.join(row(*r) for r in PRESEED)
             + row('planned', 'sum', sub, rule=f'border-top:1px solid {FAINT}; border-bottom:1px solid #eceff0;')
             + row(f'+ {MULTIPLIER}&#215; rule', f'most things take 2&#8211;3&#215; &#183; plan at {MULTIPLIER}&#215;', total - sub, colour=MUTE)
             + row('asked &#183; 18 months', '', total, True, PINK, rule=f'border-top:2px solid {INK}; padding-top:6px;', size=17))
    decide = lambda title, body, colour: (f'<div class="r" style="animation-delay:0.5s; flex:1; {CARD} padding:10px 16px; display:flex; flex-direction:column; gap:4px;">'
                                          f'{label(title, colour)}<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{body}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A21', 'if asked how much and what for', 'proposed &#183; every line an assumption')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">About ${total / 1000:.1f}M <span style="color:{PINK};">for eighteen months.</span></h2>
    {split}
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:10px 8px 4px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{table}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {decide('No in-house lab', 'Partner labs or a CRO.<br>Own lab: costs more, proves less.', MUTE)}
    {decide('Benchmark is inside', 'Milestone 3, paid for in this round.<br>Not a later one.', GREEN)}
    {decide('What it has to show', f'<b style="color:{GREEN}">1</b> three labs &#183; <b style="color:{GREEN}">2</b> any image &#183; <b style="color:{GREEN}">3</b> playground<br><b style="color:{PINK}">4</b> paid certificate &#8594; seed', MUTE)}
  </div>
  <div style="{NOTE}">salaries below market &#183; leader and scientific lead paid &#183; nothing here committed</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A4
def a4():
    """The cell-counting paper [2]: its abstract, excerpted verbatim, with three sentences lit."""
    hi = lambda s, colour=PINK: f'<mark style="background:{colour}1f; color:{INK}; border-radius:4px; padding:0 3px; box-shadow:0 0 0 1px {colour}44;">{s}</mark>'
    abstract = (
        '&#8230; Unfortunately, we discovered that many assays in widely used assay-activity benchmark datasets directly relate to cell health and '
        'cytotoxicity. Many other assays intend to capture a more specific phenotype, but their active compounds impact cell count, while inactives do not. '
        + hi('In both cases, counting cells achieves unexpectedly high performance in these benchmarks, making them less useful for discerning whether '
             'additional properties, such as phenotypic profiles (mRNA or Cell Painting), provide additional useful information on bioactivity.')
        + ' To accomplish this goal, ' + hi('we recommend filtering benchmarks to exclude such assays and including a cell-count baseline.', GREEN)
        + ' Using a benchmark with 24 protein-target assays, ' + hi('we confirm that models leveraging Cell Painting image-based profiles outperformed the baseline cell count model.', GREEN)
        + ' &#8230;')
    key = (f'<div style="display:flex; gap:22px; align-items:center; margin-top:auto; padding-top:10px; border-top:1px solid #eceff0; {MONO} font-size:13px; letter-spacing:0.1em; color:{MUTE};">'
           f'<span style="text-transform:uppercase;">abstract excerpt &#183; verbatim</span><span>{hi("finding")}</span><span>{hi("recommendation &#183; what held up", GREEN)}</span></div>')
    stat = lambda big, small, colour: (f'<div style="display:flex; flex-direction:column; gap:4px;"><span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; height:40px;">{big}</span>'
                                       f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{small}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A4', 'if asked why the model is not the moat', 'Nature Communications &#183; 2026 &#183; [2]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Weak benchmarks:<br><span style="color:{PINK};">counting cells often wins.</span></h2>
    <p style="{LEDE}">I coauthored this paper.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; min-height:0; {CARD} padding:18px 22px 14px; display:flex; flex-direction:column; gap:10px;">
    <p style="margin:0; {SANS} font-size:21px; line-height:1.5; color:{INK};">{abstract}</p>{key}
  </div>
  <div class="r" style="animation-delay:0.6s; display:grid; grid-template-columns:1fr 1fr 1.6fr; gap:24px; align-items:start; {CARD} padding:12px 20px;">
    {stat('209 and 270', 'assays in two widely used benchmarks<br>prior work: AUC above 0.9 on 32% of 209', INK)}
    {stat('24', 'protein-target assays<br>on them, Cell Painting profiles beat the count', GREEN)}
    <div style="display:flex; flex-direction:column; gap:4px;">{label('Why it matters here', PINK)}<span style="{SANS} font-size:18px; line-height:1.35; color:{INK};">Whoever sets the baseline sets the benchmark.</span>
      <span style="{MONO} font-size:13px; line-height:1.5; color:{MUTE};">Datum Line benchmark &#183; cell-count baseline on every task &#183; planted failures &#183; every model graded &#183; A16</span></div>
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
    left = panel('STR authentication', INK, str_fig, [('17', 'loci'), ('once', 'per line &#183; mailed card')],
                 'Standard for identity.<br>Cannot say how it behaves.', 0.2, 1)
    right = panel('Datum Line', GREEN, dl_fig, [(f'{n:,}', 'numbers per well'), ('every batch', 'images already taken')],
                  'Behaviour on the field&#8217;s map.<br>Cannot say which line it is.', 0.4, 1.9)
    seal = open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="54" height="54"')
    joint = (f'<div class="r" style="animation-delay:0.8s; display:flex; align-items:center; gap:18px; {CARD} padding:12px 20px;">'
             f'<span style="{MONO} font-size:14px; padding:6px 14px; border-radius:999px; border:1.5px solid {INK}; color:{INK};">identity &#183; STR</span>'
             f'<span style="{SANS} font-size:26px; color:{MUTE};">+</span>'
             f'<span style="{MONO} font-size:14px; padding:6px 14px; border-radius:999px; background:{GREEN}; color:#ffffff;">behaviour &#183; Datum Line</span>'
             f'<span style="{SANS} font-size:26px; color:{MUTE};">=</span>{seal}'
             f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">one certificate</span>'
             f'<span style="{MONO} font-size:14px; color:{MUTE}; margin-left:auto;">STR provider &#183; natural first integration</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A7', 'if asked how this differs from STR', 'results/e1 &#183; ATCC [14]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">STR says who.<br><span style="color:{PINK};">Images say how.</span></h2>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0; align-items:stretch;">{left}{right}</div>
  {joint}
  <div style="{NOTE}">STR: ATCC [14], 17 loci plus amelogenin. Datum Line: {e1["n_wells"]:,} untreated wells, {e1["n_plates"]:,} plates, {e1["n_labs"]} labs, JUMP [7].</div>
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


def market(i):
    v = {k: r[i] for k, r in MARKET.items()}
    subs = (v['organisations screening a few lines deep'] * v['lines each runs per quarter'] * v['price per line per quarter, $k'] * 4
            + v['organisations screening panels of hundreds to thousands of lines'] * v['site licence per year, $k'])
    certs = v['companies buying cell data they did not make'] * v['purchased datasets each certifies per year'] * v['price per certificate, $k']
    bench = v['benchmark partners'] * v['membership per partner per year, $k']
    return subs, certs, bench


def a22():
    low, base, high = (market(i) for i in range(3))
    m = lambda k: f'${k / 1000:.0f}M' if k >= 1000 else f'${k}k'
    row = lambda name, vals, strong=False, colour=INK, extra='': (
        f'<div style="display:grid; grid-template-columns:1fr 110px 110px 110px; gap:14px; align-items:baseline; padding:2px 10px; border-bottom:1px solid #eceff0;{extra}">'
        f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 500}; color:{colour};">{name}</span>'
        + ''.join(f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 400}; color:{colour if strong else MUTE}; text-align:right;">{x}</span>' for x in vals) + '</div>')
    head = row('assumption', ('low', 'base', 'high'), True, MUTE)
    keys = list(MARKET)
    streams = [('subscriptions and site licences, per year', keys[:5], 0),
               ('certificates on purchased data, per year', keys[5:8], 1),
               ('benchmark membership, per year', keys[8:], 2)]
    rows = ''.join(''.join(row(k, tuple(f'{x:,}' for x in MARKET[k])) for k in ks)
                   + row(name, tuple(m(x[i]) for x in (low, base, high)), True, INK2, ' border-bottom-color:#949c9f;')
                   for name, ks, i in streams)
    total = row('serviceable, per year, at full adoption', tuple(m(sum(x)) for x in (low, base, high)), True, INK, f' border-top:2px solid {INK}; border-bottom:none;')
    subs, certs, bench = base
    tenth = 100 * (sum(base) // 10) / sum(base)
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
  {top_line('A22', 'if asked how big', 'assumptions &#183; two counts would replace most')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">About {m(sum(base))} a year, <span style="color:{PINK};">if everyone joined.</span></h2>
    <p style="{LEDE}">Count &#215; price.<br>Three streams.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:8px; display:flex; flex-direction:column; flex-shrink:0;">{head}{rows}{total}</div>
  <div style="display:flex; gap:16px; align-items:stretch; flex-grow:1; min-height:0;">
    {figure}
    {note('The anchor', 'My own screen, run on cells that had moved: about $2.6M to redo.<br>Certificate: a slice of that.<br>Subscription: insurance against it.', PINK)}
  </div>
  <div style="{NOTE}">Prices are the proposal on A15. Academic labs and cores are free and are not in the revenue rows; they are the map.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A15
def a15():
    """Who pays, along the path: labs free, then the certificate, the benchmark and the exchange. Prices are A22's assumptions."""
    rng = lambda key: f'~${MARKET[key][0]}&#8211;{MARKET[key][2]}k'
    rows = [('labs and cores', 'a place on the map, the certificate, the game', 'free, for contributing controls', 'the map', GREEN),
            ('companies that buy cell data', 'a certificate on every dataset they buy', f'{rng("price per certificate, $k")} per certificate', 'the revenue', PINK),
            ('groups that screen continuously', 'a reading on every batch they run', f'{rng("price per line per quarter, $k")} per line, per quarter', 'the habit', GREEN),
            ('AI labs and model builders', 'the benchmark of planted failures', f'{rng("membership per partner per year, $k")} a year, as partners', 'the standard', GREEN),
            ('then: the exchange', 'certified datasets, traded lab to buyer', 'a share of each trade; the lab keeps the rest', 'the network', MUTE)]
    cols = 'grid-template-columns:270px 1fr 1fr 130px;'
    head = (f'<div style="display:grid; {cols} gap:24px; padding:0 20px 10px; border-bottom:1px solid #d3d8da;">'
            + ''.join(label(s) for s in ('who', 'what they get', 'what they pay', 'what it builds')) + '</div>')
    body_rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; {cols} gap:24px; align-items:baseline; flex:1; align-content:center; padding:16px 20px; '
        f'{"border-bottom:1px solid #eceff0;" if k < len(rows) - 2 else ""}{" border-top:1px dashed " + GREEN + ";" if who.startswith("then") else ""}">'
        f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK if not who.startswith("then") else GREEN};">{who}</span>'
        f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK2};">{get}</span>'
        f'<span style="{SANS} font-size:16px; font-weight:600; line-height:1.35; color:{colour};">{pay}</span>'
        f'<span style="{SANS} font-size:16px; color:{MUTE};">{builds}</span></div>'
        for k, (who, get, pay, builds, colour) in enumerate(rows))
    body = f"""<div style="{BOARD}">
  {top_line('A15', 'if asked who pays', 'proposed &#183; prices are the assumptions on A22')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:700px;">Labs contribute free.<br><span style="color:{PINK};">Buyers of cell data pay.</span></h2>
    <p style="{LEDE}">The certificate pays first.<br>The exchange grows from it.</p>
  </div>
  <div class="r" style="animation-delay:0.1s; {CARD} padding:18px 4px 6px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{head}{body_rows}</div>
  <div style="{NOTE}">control wells in &#183; readings out &#183; nothing else leaves the lab &#183; each reading is a certificate</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A23
def a23():
    """What data is worth, and why cell data does not convert: public figures with numbered references (figures/worth.py)."""
    from worth import DEALS, PRICES, SITES, REFS, DETAIL
    from slide06 import sites_chart
    agree = results('e12-field-normalization.json')['every_batch']['agree_field']
    deal = lambda k, big, name, what, more, ref: (
        f'<div class="r" style="animation-delay:{0.2 + 0.12 * k:.2f}s; flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'{label(name, MUTE)}<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{big}</span>'
        f'<span style="{SANS} font-size:15px; line-height:1.4; color:{INK2};">{what}</span>'
        f'<span style="{MONO} font-size:13px; line-height:1.4; color:{MUTE};">{more} [{ref}]</span></div>')
    deals = ''.join(deal(k, big, name, what, more, ref) for k, ((big, what, ref), (name, _, _), more) in enumerate(zip(PRICES, DEALS, DETAIL)))
    sites = (f'<div class="r" style="animation-delay:0.6s; {FIGURE} gap:28px; align-items:center; flex-grow:1;">'
             f'<div style="flex:0 0 560px; display:flex; flex-direction:column; gap:6px;">{label("EU-OPENSCREEN &#183; one protocol &#183; " + str(SITES["n_sites"]) + " sites &#183; " + SITES["line"], INK)}'
             f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK2};">same {SITES["supplied"]}, shipped to every site [{SITES["ref"]}]</span>{sites_chart(halo="#ffffff")}</div>'
             f'<div style="display:flex; flex-direction:column; gap:8px; min-width:0; align-self:stretch; justify-content:center; border-left:1px solid #e4e8e9; padding-left:28px;">'
             f'{label("on the map", GREEN)}'
             f'<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{GREEN};"><span style="color:{MUTE};">{agree["raw"]:.2f} &#8594;</span> {agree["field"]:.2f}</span>'
             f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE};">labs agree on the same drug &#183; {agree["field_better_in"]} batches &#183; A14</span></div></div>')
    refs = ('[10] TechCrunch, 2025 &#183; [11] Recursion, 2025 &#183; [12] eWeek, 2026 &#183; [13] Wolff et al., <em>iScience</em>, 2025 &#183; '
            'full references in the README')
    body = f"""<div style="{BOARD}">
  {top_line('A23', 'if asked what cell data is worth', 'public figures [10]&#8211;[13]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Data has a price.<br><span style="color:{PINK};">Cell data needs a standard.</span></h2>
    <p style="{LEDE}">Three public prices.<br>Cell data from four sites does not add up.</p>
  </div>
  <div style="display:flex; gap:14px; align-items:stretch;">{deals}</div>
  {sites}
  <div style="{NOTE}">{refs}</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A24
def a24():
    """Why a lab would share: what it keeps, what anyone can check, and who can buy. Measured where it says today; proposed elsewhere."""
    e1 = results('e1.json')['all_sources']
    cm = e1['confusion_matrix']['rows_true_cols_pred']
    P, G = 6, 1
    side = len(cm) * P + (len(cm) - 1) * G
    cells = ''.join(f'<rect x="{c * (P + G)}" y="{r * (P + G)}" width="{P}" height="{P}" fill="{PANEL}"/>'
                    + (f'<rect x="{c * (P + G)}" y="{r * (P + G)}" width="{P}" height="{P}" fill="{GREEN}" fill-opacity="{v / sum(row):.3f}"/>' if v else '')
                    for r, row in enumerate(cm) for c, v in enumerate(row))
    matrix = (f'<svg width="{side}" height="{side}" viewBox="0 0 {side} {side}" role="img" '
              f'aria-label="Confusion matrix, {len(cm)} labs: every row lands on its own lab, the diagonal." style="flex-shrink:0; display:block;">{cells}</svg>')
    fingerprint = (f'<span style="display:flex; align-items:center; justify-content:space-between; gap:16px;">'
                   f'<span style="display:flex; flex-direction:column; gap:4px;">'
                   f'<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{GREEN};">{100 * e1["balanced_accuracy"]:.1f}%</span>'
                   f'<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">wells name their own lab</span></span>{matrix}</span>'
                   f'<span style="{MONO} font-size:13px; color:{MUTE};">true lab &#8595; &#183; named lab &#8594; &#183; held-out plates</span>')
    cards = [
        ('control wells only', 'today', 'no compound &#183; no target &#183; no result<br>frame applied on the lab&#8217;s side'),
        ('labs leave fingerprints', 'today', fingerprint),
        ('signed and timestamped', 'proposed', 'public log &#183; anyone checks &#183; nobody backdates<br>blockchain optional'),
        ('lab keeps its data', 'proposed', 'listing is opt-in<br>withdraw any time'),
        ('known buyers', 'proposed', 'verified at sign-up &#183; odd access flagged<br>access log open to members'),
        ('low risk by design', 'today', 'cell-line images only<br>no human genetic data &#183; no pathogen data'),
    ]
    tag = lambda when: (f'<span style="{MONO} font-size:13px; padding:1px 9px; border-radius:999px; border:1px solid {GREEN if when == "today" else "#949c9f"}; '
                        f'color:{GREEN if when == "today" else MUTE};">{when}</span>')
    grid = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.08 * k:.2f}s; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:center; gap:10px;">{label(name, PINK)}{tag(when)}</span>'
        + (text if text.startswith('<span') else f'<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{text}</span>') + '</div>'
        for k, (name, when, text) in enumerate(cards))
    steps = [('lab lists', 'untreated wells<br>certificate attached', PINK),
             ('certificate checks', 'where the cells sit<br>who made them &#183; what moved', GREEN),
             ('buyer pays', 'per dataset<br>per line for screening groups', INK),
             ('lab keeps a share', 'of every sale<br>as long as the data sells', PINK)]
    arrow = f'<span aria-hidden="true" style="flex:0 0 28px; align-self:center; text-align:center; {SANS} font-size:22px; color:{MUTE};">&#8594;</span>'
    flow = (f'<div class="r" style="animation-delay:0.8s; {FIGURE} padding:17px 0 14px; gap:0; align-items:stretch; flex-grow:1;">' + arrow.join(
        f'<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:6px; padding:4px 20px; min-width:0;">'
        f'<span style="{MONO} font-size:13px; color:{MUTE};">{k + 1}</span>'
        f'<span style="{SANS} font-size:20px; font-weight:700; letter-spacing:-0.02em; color:{colour};">{head}</span>'
        f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK2};">{what}</span></div>'
        for k, (head, what, colour) in enumerate(steps)) + '</div>')
    body = f"""<div style="{BOARD}">
  {top_line('A24', 'if asked why a lab would share', 'results/e1 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Owned by the lab.<br><span style="color:{PINK};">Verified by anyone.</span></h2>
    <p style="{LEDE}">Open science, without the token.</p>
  </div>
  <div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; min-height:0;">{grid}</div>
  {flow}
  <div style="{NOTE}">nothing contracted &#183; privacy A18 &#183; biosecurity A20 &#183; open: map, code, public reference &#183; paid: certificate, A15</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ small edits to boards that are not rebuilt
INDEX_ROW = ('<div class="c" style="display:grid; grid-template-columns:40px minmax(0,1fr); column-gap:10px; align-items:baseline; padding:8px 0; '
             'border-top:1px solid #e4e8e9; animation-delay:{delay:.2f}s;"><span style="' + MONO + ' font-size:14px; color:#666e72;">{code}</span>'
             '<div style="display:flex; flex-direction:column; gap:0; min-width:0;"><span style="' + SANS + ' font-size:17px; font-weight:600; '
             'line-height:1.2; color:#14171a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{question}</span><span style="' + MONO + ' font-size:13px; line-height:1.35; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{answer}</span></div></div>')
# every board, in order; the index is written from this list alone
BOARDS = [
    ('A1', 'Why not trust the plate&#8217;s controls?', 'there is no control well'),
    ('A2', 'What is the math?', 'six operations &#183; one vector'),
    ('A3', 'Why not batch-correct it away?', 'what JUMP records'),
    ('A4', 'Is the model the moat?', 'counting cells often wins'),
    ('A5', 'Why not just count cells?', 'two ways to ask one question'),
    ('A6', 'How often do I re-certify?', 'line is not expired'),
    ('A7', 'Isn&#8217;t this STR?', 'STR says who &#183; images say how'),
    ('A8', 'Is the assay itself working?', 'known answer'),
    ('A9', 'Does it change the result?', 'same drug &#183; different answer'),
    ('A10', 'Does it work without stains?', 'bet on brightfield'),
    ('A11', 'Would it cry wolf?', 'six of 129 batches'),
    ('A12', 'What moved?', 'stain intensity, not cell count'),
    ('A13', 'How does one lab move over time?', 'lab&#8217;s check &#183; field&#8217;s view'),
    ('A14', 'What does the field&#8217;s frame buy?', 'agreement between labs'),
    ('A15', 'Who pays?', 'labs free &#183; buyers of cell data pay'),
    ('A16', 'What would the money build?', 'ugliest dataset &#183; on purpose'),
    ('A17', 'Is the leaderboard fair?', 'controls only, never results'),
    ('A18', 'What is private?', 'control wells leave &#183; nothing else does'),
    ('A19', 'What is the machine learning?', 'image in &#183; place, distance, move out'),
    ('A20', 'What about biosecurity?', 'cells cannot lie about their origin'),
    ('A21', 'How much, and what for?', 'planned at $0.9M &#183; asked at 2x'),
    ('A22', 'How big?', 'count &#215; price &#183; three streams'),
    ('A23', 'What is cell data worth?', 'priced in deals &#183; sites do not add up'),
    ('A24', 'Why would a lab share?', 'owned by the lab &#183; verified by anyone'),
    ('A25', 'How do labs answer it today?', 'search, ask, guess')]


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
                f'<span style="{SANS} font-size:15px; line-height:1.2; color:{MUTE if dashed else INK};">{name}</span>'
                f'<div style="position:relative; height:24px; margin-right:88px;">{bar}'
                f'<span style="position:absolute; left:calc({100 * v:.2f}% + 8px); top:50%; transform:translateY(-50%); {SANS} '
                f'font-size:{15 if dashed else 26}px; font-weight:{400 if dashed else 700}; letter-spacing:-0.02em; line-height:1; '
                f'color:{MUTE if dashed else colour}; white-space:nowrap;">{value}</span></div></div>')

    rows = (row('raw features', b['balanced_accuracy'], PINK, f'{100 * b["balanced_accuracy"]:.1f}%')
            + row('centred on own controls', t['plate_centred']['balanced_accuracy'], INK2, f'{100 * t["plate_centred"]["balanced_accuracy"]:.0f}%')
            + row('centred and scaled on own controls', t['plate_scaled']['balanced_accuracy'], INK2, f'{100 * t["plate_scaled"]["balanced_accuracy"]:.0f}%')
            + row(f'chance &#183; 1 in {b["n_labs"]} labs', b['chance'], None, f'{100 * b["chance"]:.0f}%', dashed=True))
    card = (f'<div class="ap" data-a3="rates" style="animation-delay:0.51s; flex-grow:1; min-width:0; {CARD} padding:16px 20px; '
            f'display:flex; flex-direction:column; justify-content:space-between; gap:10px;">'
            f'{label("naming the lab &#183; balanced accuracy")}'
            f'<div style="display:flex; flex-direction:column; gap:16px;">{rows}</div>'
            f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE};">{b["n_wells"]:,} wells &#183; '
            f'{rt["settings"]["wells_per_plate"]} per plate &#183; plates held out</span></div><!--/a3-rates-->')
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
