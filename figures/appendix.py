"""Appendix boards written whole from results: A8 (known answer), A9 (same drug), A11 (cry wolf), A12 (what moved),
A13 (one lab over time), A14 (what the field's frame does), and the index that lists them."""
import glob
import json
import base64
import os
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


def top_line(code, asked, tag):
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
  {top_line('A8', 'if asked whether the assay works', 'Is the assay working?')}
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
  <div style="{NOTE}">Number above each bar: agreement with the field. {known["n_plates"]:,} plates, JUMP [7]. Plate map: public JUMP metadata. results/e11</div>
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
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 52, 'agreement: cosine between a plate&#8217;s effect &#948; and a lab&#8217;s mean effect of the same compound', 19, INK2, 'middle'))
    g.append(f'<g transform="translate({ax.x0 - 186},{ax.y0 + ax.h / 2:.1f}) rotate(-90)">{text(0, 0, "positive control (compound)", 19, INK2, "middle")}</g>')
    ky = ax.y0 + ax.h + 86
    g.append(f'<rect x="{ax.x0}" y="{ky - 13}" width="26" height="13" rx="3" fill="#c3c9cb"/>' + text(ax.x0 + 34, ky, 'with its own lab&#8217;s other plates', 20, INK2))
    g.append(f'<rect x="{ax.x0 + 380}" y="{ky - 13}" width="26" height="13" rx="3" fill="{PINK}"/>' + text(ax.x0 + 414, ky, 'with every other lab', 20, INK2))
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
  {top_line('A9', 'if asked whether it changes the answer', 'Does it change the answer?')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:580px;">Same drug. <span style="color:{PINK};">Different answer.</span></h2>
    <p style="{LEDE}">Labs running the same assay slightly differently rank the same compounds differently.<br>A hit list made in one lab is not the hit list in another.</p>
  </div>
  {formula}
  <div style="display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.3s; {FIGURE}">{chart}</div>
    <div style="display:flex; flex-direction:column; gap:10px; min-height:0;">
      {small('Q1 &#183; does it agree?', 'Less with other labs, for every compound.', f'Grey: a plate&#8217;s &#948; against the mean &#948; of its own lab&#8217;s other plates. Pink: against each other lab&#8217;s mean, averaged. {best}: {C[best]["agreement_with_own_lab"]:.2f} and {C[best]["agreement_with_other_labs"]:.2f}.', 0.4)}
      {small('Q2 &#183; does it track the controls?', 'Inside labs, yes.', f'Spearman between a plate&#8217;s control-well distance to the other labs and its disagreement with them: {min(rho):.2f} to {max(rho):.2f} by compound; pooled {P["spearman"]:.2f}, shuffled {P["null_mean"]:.2f}.', 0.5)}
      {small('Q3 &#183; does it matter?', f'Effect size differs {min(cvb):.0f}% to {max(cvb):.0f}% between labs.', f'Effect size is |&#948;|. Coefficient of variation of the lab means, by compound; inside one lab, plate to plate: {min(cvw):.0f}% to {max(cvw):.0f}%.', 0.6)}
    </div>
  </div>
  <div style="{NOTE}">Eight fixed compounds, {e8["n_plates"]:,} plates, {e8["all_features"]["n_features"]:,} features, {e8["n_labs"]} labs, JUMP [7]. Z-scored on every other lab&#8217;s DMSO wells, clipped at 5. results/e8-redteam</div>
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
  {top_line('A11', 'if asked whether it cries wolf', 'results/e9')}
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
  <div style="{NOTE}">Outside: further from its own first batch than from the nearest other lab. Flagged batches hold {", ".join(str(b["n_plates"]) for b in fl)} plates.</div>
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
                w, hh = im.size; cc = min(w, hh) // 2
                im.crop(((w - cc) // 2, (hh - cc) // 2, (w + cc) // 2, (hh + cc) // 2)).resize((256, 256), Image.LANCZOS).save(f'figures/assets/a12-{n}-{c}.png', optimize=True)
                windows[c][n] = {'plate': plate, 'well': m['well'], 'p99_8': round(h)}
        json.dump({'date_first': base['date'], 'date_flagged': flagged['date'], 'channels': windows}, open(meta_path, 'w'), indent=1)
    W = json.load(open(meta_path))
    uri = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
    tile = lambda n, c, cap, colour: (f'<div style="display:flex; flex-direction:column; gap:2px; min-width:0;"><div style="aspect-ratio:1/1; max-height:118px; border-radius:10px; overflow:hidden; background:#000;">'
                                      f'<img src="{uri(f"figures/assets/a12-{n}-{c}.png")}" alt="{cap}, {c} channel, one control well of lab 2, auto-scaled." style="width:100%; height:100%; object-fit:cover; display:block;"></div>'
                                      f'{label(cap, colour)}<span style="{SANS} font-size:15px; font-weight:600; color:{colour};">{W["channels"][c][n]["p99_8"]:,} counts</span></div>')
    rows = ''.join(f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">{tile("first", c, short_date(W["date_first"]) + " &#183; " + c, MUTE)}{tile("flagged", c, short_date(W["date_flagged"]) + " &#183; " + c, PINK)}</div>' for c in channels)
    ratio = {c: W['channels'][c]['flagged']['p99_8'] / W['channels'][c]['first']['p99_8'] for c in channels + ('DNA',)}
    return (f'<div class="r" style="animation-delay:0.35s; width:300px; flex-shrink:0; {FIGURE} flex-direction:column; gap:10px; padding:14px 16px;">'
            f'{label("AS THE MICROSCOPE SHOWS THEM", INK)}{rows}'
            f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">Auto-scaled, both look fine. Counts differ {ratio[channels[0]]:.0f}&#215;; DNA {ratio["DNA"]:.0f}&#215;. The pattern moved too: perinuclear, then whole cell.</span></div>')


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
    pictures = raw_pair(base, B[first['batch']])
    a, b = pick(first, 'Intensity', 'ER'), pick(first, 'Intensity', 'AGP')
    a2, b2 = pick(last, 'Intensity', 'ER'), pick(last, 'Intensity', 'AGP')
    lvl, feat = first['share_of_displacement']['by_level'], first['share_of_features']
    body = f'''<div style="{BOARD}">
  {top_line('A12', 'if asked what moved', 'results/e6')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Intensity rose. <span style="color:{PINK};">Cell count did not.</span></h2>
    <p style="{LEDE}">The certificate&#8217;s distance is a difference of two means, so it reads feature by feature.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0;">
    <div class="r" style="animation-delay:0.2s; flex:1 1 0; {FIGURE} justify-content:center;">{chart}</div>
    {pictures}
  </div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Reading', f'On {d1}, {a["channel"]} and {b["channel"]} intensity sit {a["mean_shift"]:.1f} and {b["mean_shift"]:.1f} sd above June, and {100 * min(a["share_same_sign"], b["share_same_sign"]):.0f}% or more of those features moved the same way. By {d2}: {a2["mean_shift"]:.1f} and {b2["mean_shift"]:.1f}. Cells per well: {base["cells_per_well"]:.0f}, then {B[first["batch"]]["cells_per_well"]:.0f} and {B[last["batch"]]["cells_per_well"]:.0f}.', 0.4, 1.3)}
    {card('Instrument or cells', f'Image-level features carry {100 * lvl["image"]:.0f}% of the move and are {100 * feat["image"]:.0f}% of the features, so the move is not confined to acquisition. Profiles cannot tell a stain lot from biology.', 0.5)}
    {card('What a lab gets', 'Where to look first: exposure and the ER stain, whose pattern changed as well as its brightness. Stain mix-up, bleed-through or biology are the three things to check. Not why: that is the lab&#8217;s to find, a day after the run and not four months.', 0.6)}
  </div>
  <div style="{NOTE}">Shift from the lab&#8217;s first batch, in standard deviations of the field; means over the features of one channel.</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A13
def a13():
    from slide05 import cell_count_chart, distance_chart
    B = results('e9-replay.json')['labs']['source_2']['batches']
    out = [b for b in B if b['verdict'] == 'outside']; last = B[-1]
    nearest = [b['nearest_other'] for b in B]
    runs = [n for k, n in enumerate(nearest) if k == 0 or n != nearest[k - 1]]
    changes = ' &#8594; '.join(lab_name(n) for n in runs)
    panel = lambda chart, delay: f'<div class="r" style="animation-delay:{delay}s; flex:1; {FIGURE} justify-content:center;">{chart}</div>'
    body = f"""<div style="{BOARD}">
  {top_line('A13', 'if asked how one lab moves over time', 'results/e9')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Alone, it looks fine. <span style="color:{PINK};">Among everyone, it moves.</span></h2>
    <p style="{LEDE}">Same {len(B)} batches, two views.<br>Left: the lab&#8217;s own check. Right: its place on the map, and whom it resembles.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0;">{panel(cell_count_chart(B), 0.2)}{panel(distance_chart(B), 0.35)}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Looking at itself', f'Cells per well stay between {min(b["cells_per_well"] for b in B):.0f} and {max(b["cells_per_well"] for b in B):.0f}. Every batch passes. Odd things can sit comfortably inside a lab&#8217;s own range.', 0.5)}
    {card('Looking at the map', f'From {short_date(out[0]["date"])} the batches sit further from the lab&#8217;s own first batch than from another lab. The lab they most resemble changes: {changes}.', 0.6, 1.2)}
    {card('What a change means', 'Not a verdict. Resembling a different lab than you did is a reason to look: interest when you meant to change something, concern when you did not.', 0.7)}
  </div>
  <div style="{NOTE}">Distances in units of the field&#8217;s within-plate spread; the nearest lab is the lab whose centre is closest. Lab 2, U2OS, 2021. JUMP [7]. What moved: A12.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A14
def a14():
    e12 = results('e12-field-normalization.json'); e13 = results('e13-baseline-density.json')
    E = e12['every_batch']
    rows = [('agreement with every other lab', 'agree_field'), ('margin over the wrong drug', 'margin'),
            ('right drug recognised', 'matched'), ('agreement with own first batch', 'agree_own')]
    ways = [('raw', 'as measured', FAINT), ('own', 'own controls', MUTE), ('field', 'the field&#8217;s frame', PINK)]
    ax = Axes(430, 50, 760, len(rows) * 84, (0, 1), (0, len(rows)))
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>' + text(ax.X(v), ax.y0 + ax.h + 26, f'{v:g}', 19, MUTE, 'middle'))
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 56, f'mean over {E["n_batches"]} batches (cosine, or share for the third row)', 20, INK2, 'middle'))
    for r, (name, key) in enumerate(rows):
        y = ax.y0 + r * 84
        g.append(text(ax.x0 - 16, y + 38, name, 22, INK, 'end'))
        g.append(text(ax.x0 - 16, y + 62, f'above own controls in {E[key]["field_better_than_own_in"]}', 18, PINK if key in ('agree_field', 'margin') else MUTE, 'end'))
        for j, (way, _, colour) in enumerate(ways):
            v = E[key][way]
            g.append(f'<rect class="bar" style="animation-delay:{0.2 + 0.08 * r + 0.08 * j:.2f}s" x="{ax.x0}" y="{y + 9 + j * 23}" width="{ax.X(v) - ax.x0:.1f}" height="19" rx="3" fill="{colour}"/>')
            g.append(text(ax.X(v) + 8, y + 25 + j * 23, f'{v:.2f}', 18, PINK if way == 'field' else MUTE, weight=700 if way == 'field' else 400))
    for j, (_, name, colour) in enumerate(ways):
        g.append(f'<rect x="1250" y="{ax.y0 + 20 + j * 40}" width="26" height="16" rx="3" fill="{colour}"/>' + text(1286, ax.y0 + 35 + j * 40, name, 21, INK2))
    chart = svg(1560, ax.y0 + ax.h + 70, g, fit=True, aria='Four measures of agreement between batches under three normalisations; the field\'s frame is highest on three and level on the fourth.')
    grid = [json.load(open(f)) for f in sorted(glob.glob('results/e12-field-normalization-*.json'))]
    span = lambda key: sorted(int(v['every_batch'][key]['field_better_than_own_in'].split()[0]) for v in grid)
    if grid:
        a, m = span('agree_field'), span('margin')
        ks, sh = sorted({v['k'] for v in grid + [e12]}), sorted({v['shrink'] for v in grid + [e12]})
        holds = (f'With {", ".join(str(k) for k in ks[:-1])} or {ks[-1]} components and shrinkage from {sh[0]:g} to {sh[-1]:g}: above own controls in '
                 f'{a[0]} to {a[-1]} of {E["n_batches"]} batches for agreement, {m[0]} to {m[-1]} for margin.')
    else:
        holds = 'Sensitivity runs pending.'
    cv = E['effect_size_cv_across_batches_within_lab']; own = e13['own_baseline_by_plates']; moves = e13['reference_moves_when_one_lab_leaves']
    body = f"""<div style="{BOARD}">
  {top_line('A14', 'if asked what the field&#8217;s frame buys', 'results/e12, e13')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">One frame: <span style="color:{PINK};">what it buys.</span></h2>
    <p style="{LEDE}">Each batch&#8217;s untreated wells are moved onto the field&#8217;s, built without that lab. The drugs are the test.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} justify-content:center;">{chart}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('Does it hold', holds, 0.4)}
    {card('What it does not do', f'A lab&#8217;s agreement with its own first batch does not change: {E["agree_own"]["raw"]:.2f}, then {E["agree_own"]["field"]:.2f}. Effect sizes vary more between batches: {cv["raw"]:.2f} becomes {cv["field"]:.2f}. The gain is between labs, and it is modest: {E["agree_field"]["own"]:.2f} to {E["agree_field"]["field"]:.2f} over own controls.', 0.5, 1.2)}
    {card('How dense', f'A lab&#8217;s own baseline settles by eight plates: {own["1"]["mean"]:.2f} to {own["8"]["mean"]:.2f} spreads. The field&#8217;s reference moves {moves["mean"]:.2f} when one lab leaves.', 0.6)}
  </div>
  <div style="{NOTE}">{e12["n_plates"]:,} plates, {e12["n_labs"]} labs, {len(e12["compounds"])} positive controls, {e12["k"]} principal components. Own controls: each feature standardised on the batch&#8217;s untreated wells.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A17
def a17():
    lb = results('e14-leaderboard.json')
    names = {'centre': 'typical', 'tightness': 'tight', 'steadiness': 'steady', 'cells': 'count'}
    cols = 'grid-template-columns:70px 80px 110px 90px 110px 1fr 1fr 1fr 1fr;'
    cell = lambda s, colour=INK, weight=400, align='left': f'<span style="{SANS} font-size:15px; font-weight:{weight}; color:{colour}; text-align:{align};">{s}</span>'
    head = (f'<div style="display:grid; {cols} gap:12px; padding:0 8px 4px; border-bottom:1px solid #d3d8da;">'
            + ''.join(label(s) for s in ('lab', 'batches', 'median score', 'best', 'streak'))
            + ''.join(label(f'median {v}', GREEN) for v in names.values()) + '</div>')
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.05 * k:.2f}s; display:grid; {cols} gap:12px; padding:3px 8px; border-bottom:1px solid #eceff0; '
        f'background:{"rgba(190,30,116,0.07)" if v["lab"] == "source_2" else "transparent"}; border-radius:6px;">'
        + cell(lab_name(v['lab']), PINK if v['lab'] == 'source_2' else INK, 700 if v['lab'] == 'source_2' else 500)
        + cell(v['n_batches']) + cell(f'{v["median_score"]:.0f}', INK, 700) + cell(f'#{v["best"]["rank"]}') + cell(f'{v["streak"]["longest"]}')
        + ''.join(cell('&#8212;' if v[f'median_{m}'] is None else f'{v[f"median_{m}"]:.2f}') for m in names)
        + '</div>' for k, v in enumerate(lb['by_lab']))
    table = f'<div style="display:flex; flex-direction:column; flex:1 1 0; min-width:0;">{head}{rows}</div>'
    top = lb['top'][0]; b = lb['badges']
    body = f"""<div style="{BOARD}">
  {top_line('A17', 'if asked about the game', 'results/e14')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">A game, <span style="color:{PINK};">not a report card.</span></h2>
    <p style="{LEDE}">Every batch ranked on its untreated wells, never on results.<br>Labs are a number unless they choose a name. The same arithmetic runs privately on your own plates with data access.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; {FIGURE} flex-direction:column; padding:14px 14px;">{table}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {card('The score', f'Four measures in within-plate spreads, each a percentile among {lb["n_batches"]} batches: distance from the field&#8217;s centre, spread of the batch&#8217;s plates, distance from the previous batch, cells per well against the field. 100 minus the mean.', 0.5, 1.4)}
    {card('The best batch', f'{lab_name(top["lab"])}, {short_date(top["date"])}, {top["n_plates"]} plates: score {top["score"]:.0f}. {lab_name(b["best batch"]).capitalize()} holds {sum(r["lab"] == b["best batch"] for r in lb["top"])} of the top ten and the longest streak, {lb["by_lab"][0]["streak"]["longest"]}.', 0.6)}
    {card('Your choice to play', 'Nothing in the score touches a treated well or a result, and nobody is named without opting in. The board is for climbing; the private version is for your own plates.', 0.7)}
  </div>
  <div style="{NOTE}">{lb["n_plates"]:,} plates, {lb["n_labs"]} labs, {lb["n_batches"]} batches. Streaks: consecutive batches in distribution (results/e9). JUMP [7].</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A18
def a18():
    e9 = results('e9-replay.json'); L2 = e9['labs']['source_2']
    e12 = results('e12-field-normalization.json')
    col = lambda title, colour, items: (f'<div class="r" style="flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:10px; min-width:0;">'
                                        f'{label(title, colour)}' + ''.join(
                                            f'<div style="display:flex; flex-direction:column; gap:2px; padding-top:8px; border-top:1px solid #eceff0;">'
                                            f'<span style="{SANS} font-size:17px; font-weight:600; line-height:1.25; color:{INK};">{h}</span>'
                                            f'<span style="{SANS} font-size:15px; line-height:1.35; color:{MUTE};">{b}</span></div>' for h, b in items) + '</div>')
    leaves = col('What leaves the building', PINK, [
        ('Untreated control wells only', 'images or the well-level profile of the wells with no compound. No treated well, no compound identity, no target, no result.'),
        ('A plate map of the control wells', 'which wells are controls; nothing about what the other wells hold.'),
        ('Nothing else', f'on this public replay that is {L2["n_reference_wells"]:,} untreated wells from {len(L2["reference_labs"])} other labs, and not one treated well.')])
    uses = col('What Datum Line does with it', GREEN, [
        ('Builds the map', f'one centroid per plate, in a space scaled on every other lab. The lab being placed never sets its own scale ({e9["labs"]["source_2"]["n_features"]:,} features here).'),
        ('Answers', 'where the plate sits, distance from the lab&#8217;s own baseline and to the nearest lab, cells per well, the verdict, the rank.'),
        ('Computes a move, not a model of you', f'the field&#8217;s frame is one matrix per batch, fitted on your controls: x&#8242; = C<sub>field</sub><sup>&#189;</sup> C<sub>batch</sub><sup>&#8722;&#189;</sup> (x &#8722; m<sub>batch</sub>), {e12["k"]} components.')])
    never = col('What it never sees', INK, [
        ('Your treated data', 'the move is sent to you and applied on your side. Your results are normalised in your building, by you.'),
        ('Your name, unless you choose', 'labs appear on the map and the board as a number by default; a lab opts in to a name. Every JUMP lab here is a number.'),
        ('Your images, for long', 'proposed: images are reduced to profiles on arrival and the originals deleted; the profile of a control well is what is kept.')])
    body = f"""<div style="{BOARD}">
  {top_line('A18', 'if asked what is private', 'results/e9, e12 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Control wells leave. <span style="color:{PINK};">Nothing else does.</span></h2>
    <p style="{LEDE}">A control well has no compound, no target and no result, so there is nothing to clear. The map is built from those wells alone; the frame it produces is applied to your treated data by you.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0; align-items:stretch;">{leaves}{uses}{never}</div>
  <div style="{NOTE}">Every analysis in this deck runs on this rule and is public: github.com/kat-titter/datum-line/analysis. The public map is JUMP, CC0 [7]. Retention and naming are proposed, not yet contracted.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A19
def a19():
    import os
    from slide07 import well_image, LAB
    e1 = results('e1.json')['all_sources']; e12 = results('e12-field-normalization.json')
    e15 = results('e15-image-model.json') if os.path.exists('results/e15-image-model.json') else None
    if e15 and 'balanced_accuracy' in e15['inputs'].get('brightfield', {}):
        b = e15['inputs']['brightfield']; d = e15['inputs']['dna']
        vision = (f'a frozen vision model, no training on cells, names the lab from one raw image: {100 * b["balanced_accuracy"]:.1f}% brightfield '
                  f'({b["n_labs"]} labs), {100 * d["balanced_accuracy"]:.1f}% DNA ({d["n_labs"]} labs). It sees lab 2&#8217;s autumn move (&#961; {d["lab_2_drift"]["spearman"]:.2f}); it does not yet reproduce the map&#8217;s neighbours')
    big = lambda s, colour=INK: f'<span style="{SANS} font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{colour};">{s}</span>'
    step = lambda k, title, lines, body, colour: (
        f'<div class="r" style="animation-delay:{0.2 + 0.2 * k:.2f}s; flex:1; {CARD} padding:18px 20px 16px; display:flex; flex-direction:column; gap:10px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:baseline;">{label(f"step {k + 1}", MUTE)}{label(title, colour)}</span>'
        f'<div style="height:112px; display:flex; align-items:center;">{body}</div>'
        + ''.join(f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK if i == 0 else MUTE};">{l}</span>' for i, l in enumerate(lines)) + '</div>')
    arrow = f'<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" style="flex-shrink:0; align-self:center;"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="{GREEN}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    img = f'<img src="{well_image(LAB, None, "box-you")}" alt="A control well, DNA stain." style="width:112px; height:112px; border-radius:12px; object-fit:cover; background:#000;">'
    n_feat = f"{e1['n_features']:,}"
    numbers = f'<div style="display:flex; flex-direction:column; gap:4px;">{big(n_feat)}<span style="{MONO} font-size:13px; color:{MUTE};">numbers per well today</span></div>'
    acc, chance = f"{100 * e1['balanced_accuracy']:.1f}%", f"{100 * e1['chance']:.0f}%"
    mapfig = f'<div style="display:flex; flex-direction:column; gap:4px;">{big(acc, GREEN)}<span style="{MONO} font-size:13px; color:{MUTE};">a classifier names the lab; chance {chance}</span></div>'
    move = (f'<div style="display:flex; flex-direction:column; gap:6px;"><span style="{SANS} font-size:22px; color:{INK};">x&#8242; = C<sub>field</sub><sup>&#189;</sup> C<sub>batch</sub><sup>&#8722;&#189;</sup> (x &#8722; m<sub>batch</sub>)</span>'
            f'<span style="{MONO} font-size:13px; color:{MUTE};">one matrix per batch, {e12["k"]} components</span></div>')
    steps = (step(0, 'an image', ['One untreated well, any channel.', 'A Cell Painting profile today; the picture itself is now tested (step 2).'], img, PINK) + arrow
             + step(1, 'numbers', ['CellProfiler features per well.', vision + '.'], numbers, GREEN) + arrow
             + step(2, 'the map', ['Z-scored on every other lab; one point per plate.', 'The lab being placed never sets its own scale.'], mapfig, GREEN) + arrow
             + step(3, 'the move', ['Your batch onto the field&#8217;s frame.', 'Sent to you; applied to treated data on your side.'], move, PINK))
    who = (f'<div class="r" style="animation-delay:1.1s; display:grid; grid-template-columns:1fr 1fr 1fr; gap:24px; padding-top:14px; border-top:1px solid #d3d8da;">'
           f'<div>{label("People", PINK)}<p style="margin:4px 0 0; {SANS} font-size:16px; line-height:1.35; color:{INK};">the box, the glimpse, the game</p></div>'
           f'<div>{label("Agents", GREEN)}<p style="margin:4px 0 0; {SANS} font-size:16px; line-height:1.35; color:{INK};">the API, the coordinates, the benchmark</p></div>'
           f'<div>{label("Both", INK)}<p style="margin:4px 0 0; {SANS} font-size:16px; line-height:1.35; color:{INK};">every drop sharpens the map; every graded model raises the bar</p></div></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A19', 'if asked what the machine learning is', 'results/e1, e12, e15')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Image in. <span style="color:{PINK};">Place, distance, move out.</span></h2>
    <p style="{LEDE}">Four steps. The model is the cheap part; the map and the rule that nobody sets their own scale are the product.</p>
  </div>
  <div style="display:flex; gap:12px; flex-grow:1; min-height:0; align-items:stretch;">{steps}</div>
  {who}
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
    col = lambda title, colour, big, items: (f'<div class="r" style="flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
                                             f'{label(title, colour)}<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; padding:6px 0 4px;">{big}</span>' + ''.join(
                                                 f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK if i == 0 else MUTE};">{l}</span>' for i, l in enumerate(items)) + '</div>')
    where = col('Where did this come from?', GREEN, f'{100 * e1["balanced_accuracy"]:.1f}%', [
        f'of {e1["n_wells"]:,} untreated wells name their true lab, on plates the classifier never saw.',
        f'A plate claimed from one lab and made in another is caught by its cells. In the replay, {own} of {n_batches} batches have every well naming its own lab (results/e1, e9).'])
    labels = col('Do the labels tell the truth?', PINK, f'{len(e11["failed"])} batches', [
        f'{failed_plates} plates whose plate map says positive control, and whose cells show no effect; no other well on those plates does either.',
        'The data said what was done to the cells, not what the label said. Left out or mislabelled, the map cannot tell; that it is wrong, it can (results/e11).'])
    nowhere = col('Cells from nowhere', INK, f'{farthest:.0f} spreads', [
        f'the farthest any of {n_batches} real batches sits from every other lab. Beyond that, a culture is not the line it claims, or not alone.',
        'Misidentified lines and contamination are the common case; untested here, and proposed as the first partner-lab test.'])
    sentinel = col('Sentinel cells', MUTE, 'proposed', [
        'An untreated well is a canary. If the controls move and nobody changed anything, something in the room did: a lot, a reagent, the air, the water.',
        'Lab 2&#8217;s autumn is what that looks like on public data (A13). Alerts across labs come after the certificate.'])
    body = f"""<div style="{BOARD}">
  {top_line('A20', 'if asked about biosecurity', 'results/e1, e9, e11 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Cells cannot lie <span style="color:{PINK};">about where they came from.</span></h2>
    <p style="{LEDE}">Provenance, integrity and a tripwire, from the same map.<br>Control wells only: nothing about agents, compounds or targets ever leaves a lab (A18).</p>
  </div>
  <div style="display:flex; gap:14px; flex-grow:1; min-height:0; align-items:stretch;">{where}{labels}{nowhere}{sentinel}</div>
  <div style="{NOTE}">Defensive by construction: the map holds untreated wells, the benchmark grades methods on planted imaging failures, and no result or perturbation is stored. JUMP [7].</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A21
PRESEED = [  # eighteen months; every line is a proposal
    ('Founder', '18 months', 180),
    ('Technical co-founder', '18 months', 180),
    ('ML engineer', 'from month 7', 160),
    ('Payroll overhead', '20% of salaries', 104),
    ('The benchmark dataset', 'about 60 plates with planted failures, run where the cells already are; a CRO if needed', 120),
    ('Partner-lab bench time', 'three labs image the controls they already take; reagent top-ups and shipping', 30),
    ('Compute and storage', 'images, models, hosting, the API', 45),
    ('Legal, IP, insurance, accounting', 'incorporation to first contract', 45),
    ('Travel and partner visits', 'two benchmark partners, three labs', 20),
]
MULTIPLIER = 2       # the rule: most things take two to three times the time and money they should; plan at two


def preseed_total():
    sub = sum(k for _, _, k in PRESEED)
    return sub, round(sub * MULTIPLIER)


def a21():
    sub, total = preseed_total()
    bench = sum(k for name, _, k in PRESEED if name in ('The benchmark dataset', 'Partner-lab bench time'))
    row = lambda name, what, k, strong=False, colour=INK: (
        f'<div style="display:grid; grid-template-columns:260px 1fr 90px; gap:16px; align-items:baseline; padding:2px 10px; border-bottom:1px solid #eceff0;">'
        f'<span style="{SANS} font-size:15px; font-weight:{700 if strong else 600}; color:{colour};">{name}</span>'
        f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{what}</span>'
        f'<span style="{SANS} font-size:15px; font-weight:{700 if strong else 500}; color:{colour}; text-align:right;">{f"${k / 1000:.2f}M" if k >= 1000 else f"${k}k"}</span></div>')
    table = ''.join(row(*r) for r in PRESEED) + row('As planned', 'the lines above', sub) + row(f'The {MULTIPLIER}&#215; rule', 'most things take two to three times what they should; plan at two', total - sub) + row('Eighteen months', 'about', total, True, PINK)
    decide = lambda title, body, colour: (f'<div class="r" style="animation-delay:0.5s; flex:1; {CARD} padding:10px 16px; display:flex; flex-direction:column; gap:4px;">'
                                          f'{label(title, colour)}<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{body}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A21', 'if asked how much and what for', 'proposed; every line an assumption')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">About ${total / 1000:.1f}M <span style="color:{PINK};">for eighteen months.</span></h2>
    <p style="{LEDE}">People first, then the benchmark. No lab of our own.<br>Planned at ${sub / 1000:.1f}M; asked at {MULTIPLIER}&#215;.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:10px 8px 4px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{table}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {decide('No in-house lab', 'Partner labs image the controls they already take; the benchmark runs where the cells are, or at a CRO. A lab of our own would cost more and prove less.', GREEN)}
    {decide('The ugly dataset is inside', f'${bench}k of the ${sub / 1000:.1f}M planned, about {100 * bench / sub:.0f}%, builds the benchmark and the bench time around it. It is milestone three, not a later round.', PINK)}
    {decide('What it has to show', 'The four milestones on slide 09. Then a seed.', INK)}
  </div>
  <div style="{NOTE}">Salaries are below market and assume founders are paid. The multiplier is the only line not itemised, and the one most often right. Nothing here is committed.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A4
def a4():
    """The cell-counting paper [2]: its whole abstract, verbatim, with three sentences lit."""
    hi = lambda s, colour=PINK: f'<mark style="background:{colour}1f; color:{INK}; border-radius:4px; padding:0 3px; box-shadow:0 0 0 1px {colour}44;">{s}</mark>'
    abstract = (
        'Accurately predicting the activity of a chemical in each bioactivity assay based on its already-known properties is extremely useful in drug '
        'development. Unfortunately, we discovered that many assays in widely used assay-activity benchmark datasets directly relate to cell health and '
        'cytotoxicity. Many other assays intend to capture a more specific phenotype, but their active compounds impact cell count, while inactives do not. '
        + hi('In both cases, counting cells achieves unexpectedly high performance in these benchmarks, making them less useful for discerning whether '
             'additional properties, such as phenotypic profiles (mRNA or Cell Painting), provide additional useful information on bioactivity.')
        + ' To accomplish this goal, ' + hi('we recommend filtering benchmarks to exclude such assays and including a cell-count baseline.', GREEN)
        + ' Using a benchmark with 24 protein-target assays, ' + hi('we confirm that models leveraging Cell Painting image-based profiles outperformed the baseline cell count model.', GREEN)
        + ' We propose several other practical recommendations for benchmarking machine learning models for predicting bioactivity and assessing the added '
        'value of mRNA, protein, or image-based profiles.')
    key = (f'<div style="display:flex; gap:22px; align-items:center; padding-top:10px; border-top:1px solid #eceff0; {MONO} font-size:12px; letter-spacing:0.06em; color:{MUTE};">'
           f'<span>ABSTRACT, VERBATIM</span><span>{hi("the finding")}</span><span>{hi("the recommendation, and what held up", GREEN)}</span></div>')
    stat = lambda big, small, colour: (f'<div style="display:flex; flex-direction:column; gap:4px;"><span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; height:40px;">{big}</span>'
                                       f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{small}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A4', 'if asked why the model is not the moat', 'Seal et al., Nature Communications, 2026 [2]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:640px;">The benchmarks are so weak that <span style="color:{PINK};">counting cells often wins.</span></h2>
    <p style="{LEDE}">A paper I coauthored. The bottleneck was never the model.<br>It is what you are comparing against.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; min-height:0; {CARD} padding:18px 22px 14px; display:flex; flex-direction:column; gap:10px;">
    <p style="margin:0; {SANS} font-size:18px; line-height:1.5; color:{INK};">{abstract}</p>{key}
  </div>
  <div class="r" style="animation-delay:0.6s; display:grid; grid-template-columns:1fr 1fr 1.6fr; gap:24px; align-items:start; {CARD} padding:12px 20px;">
    {stat('209 and 270', 'assays in the benchmarks the field scored itself on; prior work reported AUC above 0.9 on 32% of 209', INK)}
    {stat('24', 'protein-target assays left once cell-health assays were filtered out; there, profiles beat the count', GREEN)}
    <div style="display:flex; flex-direction:column; gap:4px;">{label('Why it matters here', PINK)}<span style="{SANS} font-size:16px; line-height:1.35; color:{INK};">Whoever sets the baseline sets the benchmark. That is why the benchmark is a milestone, not a paper: planted failures, a cell-count baseline on every task, every model graded (A16).</span></div>
  </div>
  <div style="{NOTE}">Seal S, Dee W, &#8230; Titterton K, &#8230; Carpenter AE. Counting cells can accurately predict small-molecule bioactivity benchmarks. <em>Nat Commun</em>, 2026.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A7
def a7():
    e1 = results('e1.json')['all_sources']
    n = e1['n_features']
    # STR: seventeen loci, drawn as the ladder a capillary trace is read from
    rng = __import__('random').Random(7)
    ladder = ''.join(f'<rect x="{18 + k * 24}" y="{30 + rng.randint(0, 40)}" width="9" height="{50 + rng.randint(0, 36)}" rx="2" fill="{INK}" opacity=".85"/>' for k in range(17))
    str_fig = (f'<svg viewBox="0 0 440 150" width="100%" aria-label="Seventeen bars, one per STR locus." style="display:block; max-height:196px;">{ladder}'
               f'<line x1="14" y1="134" x2="430" y2="134" stroke="{MUTE}" stroke-width="1.5"/></svg>')
    # Datum Line: every number per well, drawn as dots
    cols, pitch = 97, 6.4
    rows = -(-n // cols)
    dots = ''.join(f'<circle cx="{6 + (k % cols) * pitch:.1f}" cy="{6 + (k // cols) * pitch:.1f}" r="2" fill="{GREEN if (k * 7919) % 11 else PINK}"/>' for k in range(n))
    dl_fig = (f'<svg viewBox="0 0 {cols * pitch + 8:.0f} {rows * pitch + 8:.0f}" width="100%" aria-label="{n:,} dots, one per number measured in every well." style="display:block; width:100%; max-height:196px;">{dots}</svg>')
    stat = lambda big, small, colour: (f'<div style="display:flex; flex-direction:column; gap:2px; min-width:0;"><span style="{SANS} font-size:30px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{colour};">{big}</span>'
                                       f'<span style="{MONO} font-size:12px; color:{MUTE};">{small}</span></div>')
    panel = lambda title, colour, fig, stats, line, delay, grow: (
        f'<div class="r" style="animation-delay:{delay}s; flex:{grow}; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:12px; min-width:0;">'
        f'{label(title, colour)}<div style="flex-grow:1; display:flex; align-items:center;">{fig}</div>'
        f'<div style="display:grid; grid-template-columns:repeat({len(stats)},minmax(0,1fr)); gap:14px;">{"".join(stat(b, s, colour) for b, s in stats)}</div>'
        f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK}; padding-top:8px; border-top:1px solid #eceff0;">{line}</span></div>')
    left = panel('STR authentication', INK, str_fig, [('17', 'loci'), ('once', 'per line, from a mailed card'), ('who', 'which line it is')],
                 'The standard for identity. Two cultures with the same fingerprint can behave differently.', 0.2, 1)
    right = panel('Datum Line', GREEN, dl_fig, [(f'{n:,}', 'numbers per well'), ('every batch', 'from images already taken'), ('how', 'the way it behaves, against every lab')],
                  'Behaviour, placed on the field&#8217;s map. Cannot say which line it is.', 0.4, 1.9)
    seal = open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="54" height="54"')
    joint = (f'<div class="r" style="animation-delay:0.8s; display:flex; align-items:center; gap:18px; {CARD} padding:12px 20px;">'
             f'<span style="{MONO} font-size:14px; padding:6px 14px; border-radius:999px; border:1.5px solid {INK}; color:{INK};">identity &#183; STR</span>'
             f'<span style="{SANS} font-size:26px; color:{MUTE};">+</span>'
             f'<span style="{MONO} font-size:14px; padding:6px 14px; border-radius:999px; background:{GREEN}; color:#ffffff;">behaviour &#183; Datum Line</span>'
             f'<span style="{SANS} font-size:26px; color:{MUTE};">=</span>{seal}'
             f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">one certificate.</span>'
             f'<span style="{SANS} font-size:16px; color:{MUTE}; margin-left:auto;">Partner, not rival: the STR provider is the natural first integration.</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A7', 'if asked how this differs from STR', 'identity and behaviour')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">STR says who. <span style="color:{PINK};">Images say how.</span></h2>
    <p style="{LEDE}">Not a competitor: the other half of the same certificate.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0; align-items:stretch;">{left}{right}</div>
  {joint}
  <div style="{NOTE}">STR: ATCC cell authentication service, 17 loci plus amelogenin. Datum Line: {e1["n_wells"]:,} untreated wells, {e1["n_plates"]:,} plates, 11 labs, JUMP [7].</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A22
MARKET = {  # (low, base, high); every one an assumption until a count replaces it
    'organisations screening with high-content imaging': (200, 400, 800),
    'cell lines each runs per quarter': (2, 5, 10),
    'price per line per quarter, $k': (5, 10, 15),
    'companies buying cell data they did not make': (50, 150, 300),
    'purchased datasets each certifies per year': (2, 4, 8),
    'price per certificate, $k': (10, 25, 50),
    'benchmark partners': (4, 10, 20),
    'membership per partner per year, $k': (50, 100, 200),
}


def market(i):
    v = {k: r[i] for k, r in MARKET.items()}
    subs = v['organisations screening with high-content imaging'] * v['cell lines each runs per quarter'] * v['price per line per quarter, $k'] * 4
    certs = v['companies buying cell data they did not make'] * v['purchased datasets each certifies per year'] * v['price per certificate, $k']
    bench = v['benchmark partners'] * v['membership per partner per year, $k']
    return subs, certs, bench


def a22():
    low, base, high = (market(i) for i in range(3))
    m = lambda k: f'${k / 1000:.0f}M' if k >= 1000 else f'${k}k'
    row = lambda name, vals, strong=False, colour=INK: (
        f'<div style="display:grid; grid-template-columns:1fr 110px 110px 110px; gap:14px; align-items:baseline; padding:2px 10px; border-bottom:1px solid #eceff0;">'
        f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 500}; color:{colour};">{name}</span>'
        + ''.join(f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 400}; color:{colour if strong else MUTE}; text-align:right;">{x}</span>' for x in vals) + '</div>')
    head = row('assumption', ('low', 'base', 'high'), True, MUTE)
    rows = ''.join(row(k, tuple(f'{x:,}' for x in r)) for k, r in MARKET.items())
    out = (row('Subscriptions, per year', tuple(m(x[0]) for x in (low, base, high)), True, GREEN)
           + row('Certificates on purchased data, per year', tuple(m(x[1]) for x in (low, base, high)), True, PINK)
           + row('Benchmark membership, per year', tuple(m(x[2]) for x in (low, base, high)), True, GREEN)
           + row('Serviceable, per year, at full adoption', tuple(m(sum(x)) for x in (low, base, high)), True, INK))
    note = lambda title, body, colour: (f'<div class="r" style="animation-delay:0.5s; flex:1; {CARD} padding:10px 16px; display:flex; flex-direction:column; gap:4px;">'
                                        f'{label(title, colour)}<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{body}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A22', 'if asked how big', 'assumptions, not facts; two counts would replace most of them')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">About {m(sum(base))} a year, <span style="color:{PINK};">if everyone joined.</span></h2>
    <p style="{LEDE}">Bottom up. The first two rows matter most.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:8px 8px 2px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{head}{rows}{out}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {note('What would replace the guesses', 'A count of organisations with high-content imaging (instrument installed base is the proxy); lines per organisation from the first three labs.', GREEN)}
    {note('The anchor', 'One screen run on cells that had moved is about $2.6M to redo. A certificate is a slice of that; a subscription is insurance against it.', PINK)}
    {note('Ten percent', f'A tenth of the base case is about {m(sum(base) // 10)} a year: the five-year bar.', INK)}
  </div>
  <div style="{NOTE}">Prices are the proposal on A15. Academic labs and cores are free and are not in the revenue rows; they are the map.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ small edits to boards that are not rebuilt
INDEX_ROW = ('<div class="c" style="display:grid; grid-template-columns:44px minmax(0,1fr); column-gap:14px; align-items:baseline; padding:6px 0; '
             'border-top:1px solid #e4e8e9; animation-delay:{delay:.2f}s;"><span style="' + MONO + ' font-size:14px; color:#be1e74;">{code}</span>'
             '<div style="display:flex; flex-direction:column; gap:0; min-width:0;"><span style="' + SANS + ' font-size:18px; font-weight:600; '
             'line-height:1.25; color:#14171a;">{question}</span><span style="' + MONO + ' font-size:13px; line-height:1.35; color:#666e72;">{answer}</span></div></div>')
ROW = re.compile(r'<div class="c" style="display:grid; grid-template-columns:44px[^>]*>\s*<span[^>]*>(A\d+)</span>\s*<div[^>]*>\s*<span[^>]*>(.*?)</span>\s*<span[^>]*>(.*?)</span>\s*</div>\s*</div>', re.S)
NEW_BOARDS = [('A11', 'Would it cry wolf?', 'Six of 129 batches'), ('A12', 'What moved?', 'Stain intensity, not cell count'),
              ('A13', 'How does one lab move over time?', 'The lab&#8217;s check and the field&#8217;s view'),
              ('A14', 'What does the field&#8217;s frame buy?', 'Agreement between labs'),
              ('A15', 'Who pays?', 'Three buyers, one certificate'), ('A16', 'What would the money build?', 'The ugliest dataset, on purpose'),
              ('A17', 'Is the leaderboard fair?', 'Controls only, never results'),
              ('A18', 'What is private?', 'Control wells leave; nothing else does'),
              ('A19', 'What is the machine learning?', 'Image in; place, distance, move out'),
              ('A20', 'What about biosecurity?', 'Cells cannot lie about where they came from'),
              ('A21', 'How much, and what for?', 'Planned at $0.9M, asked at 2x; no lab of our own'),
              ('A22', 'How big?', 'Bottom up, every assumption on the board')]


def index(s):
    """The appendix index, in two even columns, with a row for every board."""
    rows = {code: (code, q, a) for code, q, a in ROW.findall(s)}
    rows.update({r[0]: r for r in NEW_BOARDS})
    rows = sorted(rows.values(), key=lambda r: int(r[0][1:]))
    half = (len(rows) + 1) // 2
    column = lambda part, k0: '<div>' + ''.join(INDEX_ROW.format(code=c, question=q, answer=a, delay=0.1 + 0.04 * (k0 + k))
                                                for k, (c, q, a) in enumerate(part)) + '</div>'
    a = s.index('<div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr));')
    a = s.index('>', a) + 1
    b = s.rindex('</div></div></template>')
    return s[:a] + column(rows[:half], 0) + column(rows[half:], half) + s[b:]


def patch(deck):
    """Index entries for the new boards, and the brightfield pair on A10."""
    m = re.search(r'<template id="t10">.*?</template>', deck, flags=re.S); s = index(m.group(0))
    deck = deck[:m.start()] + s + deck[m.end():]

    m = re.search(r'<template id="t20">.*?</template>', deck, flags=re.S); s = m.group(0)
    e15 = results('e15-image-model.json') if os.path.exists('results/e15-image-model.json') else None
    if e15 and 'balanced_accuracy' in e15['inputs'].get('brightfield', {}) and 'names the lab from one brightfield' not in s:
        b = e15['inputs']['brightfield']
        line = (f'<div class="r" style="animation-delay:0.6s; margin-top:10px; padding:10px 14px; border-radius:10px; background:rgba(15,143,108,0.08);">'
                f'<span style="{SANS} font-size:16px; line-height:1.35; color:#14171a;"><span style="color:#0f8f6c; font-weight:700;">First evidence, {b["n_plates"]:,} plates, {b["n_labs"]} labs:</span> a frozen vision model, no training on cells, '
                f'names the lab from one brightfield image at {100 * b["balanced_accuracy"]:.1f}% (chance {100 * b["chance"]:.0f}%), whole batches held out. results/e15</span></div>')
        k = s.find('One field of one well, two ways.')
        k = s.find('</div>', s.find('</div>', k) + 6) + 6
        s = s[:k] + line + s[k:]
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
