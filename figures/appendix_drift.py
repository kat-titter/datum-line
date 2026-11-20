"""Appendix boards on one lab's batches over time, written whole from results: A8 (did the known drugs work?), A11 (does it
flag too often?), A12 (what moved?), A13 (how one lab moves over time) and A17 (the leaderboard)."""

import re

from parts import *
from appendix_kit import BOARD, H2, LEDE, FIGURE, NOTE, top_line, card, plate_map


# ------------------------------------------------------------------ A8
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
                 f'width="{ax.X(0.64) - ax.X(0):.1f}" height="{h:.1f}" rx="3" fill="{PINK if bad_batch else FAINT}"/>')      # 17 Nov (Kat: "evry slide should use 1 or both colors"): the failed batches are the outliers, pink
        if b['batch'] in (good['batch'], bad['batch']):
            g.append(text(ax.X(k + 0.5), min(ax.Y(b['size']), ax.Y(line)) - 10, '&#9660;', 19, INK, 'middle'))   # over the fail line, never on it
    g.append(f'<path d="M {ax.x0} {ax.Y(line):.1f} L {ax.x0 + ax.w + 4} {ax.Y(line):.1f}" stroke="{INK2}" stroke-width="2" stroke-dasharray="6 5"/>'
             + text(ax.x0 + ax.w + 10, ax.Y(line) + 6, f'{sym} of usual', 18, INK2))     # the fail line, drawn where the rule puts it
    fk = [k for k, b in enumerate(B) if b['verdict'] == 'failed']; cx = ax.X((fk[0] + fk[-1] + 1) / 2)
    g.append(text(cx, ax.Y(14), f'{len(failed)} batches', 22, PINK, 'middle', 700) + text(cx, ax.Y(14) + 28, f'{n_failed_plates} plates', 22, PINK, 'middle', 700))
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
  <div class="note" style="{NOTE}">failed = under {sym} of the lab&#8217;s usual effect + unlike other labs &#183; {known["n_plates"]:,} plates &#183; maps: plates {good["plate"]}, {bad["plate"]}, JUMP layout [7]</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A11
# slide 07's code for a batch: filled = on the map, hollow = flagged; pink = lab 2 (you), green = every other lab
def batch_square(x, y, s, flagged, colour, extra=''):
    return (
        f'<rect {extra}x="{x + 0.75:g}" y="{y + 0.75:g}" width="{s - 1.5:g}" height="{s - 1.5:g}" rx="{s / 4:g}" fill="none" stroke="{MUTE}" stroke-width="1.5"/>' if flagged
        else f'<rect {extra}x="{x:g}" y="{y:g}" width="{s:g}" height="{s:g}" rx="{s / 4:g}" fill="{colour}"/>')


def a11_variant_names(rt):
    """A11's plain names for the red team's ways of checking, and how many batches each variant's baseline takes in."""
    names = {'as published': 'as published', 'baseline is the first two batches': 'baseline: first 2 batches',
             'baseline is the first three batches': 'baseline: first 3 batches', 'no clipping': 'extreme values kept',
             'no image-level features': 'cell measurements only', 'image-level features only': 'whole-image measurements only',
             'all-vehicle plates removed': 'untreated-only plates removed'}
    dropped = [k.split()[0] for k in rt if k.endswith(' removed from the field')]
    names.update({f'{s} removed from the field': f'without {lab_name(s)}' for s in dropped})
    names['all of those labs removed'] = 'without labs ' + ' and '.join(str(lab_number(s)) for s in dropped)
    nbase = {'baseline is the first two batches': 2, 'baseline is the first three batches': 3}
    return names, nbase


def a11_grid(rt, B, names, nbase):
    """A11's right panel: lab 2's batches, one row per way of checking; a row whose verdicts differ is marked. Returns the
    panel and how many rows differ."""
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
            g.append(batch_square(X[k], y, 26, c == 'O', PINK, f'class="f" style="animation-delay:{0.2 + 0.04 * r + 0.01 * k:.2f}s" '))
        g.append(f'<rect x="{X[0] - 3}" y="{y - 3}" width="{nbase.get(name, 1) * P - 2}" height="32" rx="8" fill="none" stroke="{INK2}" stroke-width="2"/>')
    chart = svg(X[-1] + 30, y0 + len(rt) * 33, g, fit=True, aria=f'Verdicts for lab 2 checked {len(rt)} ways; {len(rt) - changed} give the same result.').replace('xMidYMid', 'xMinYMin', 1)
    grid = f'<div style="flex:1 1 0; min-width:0; display:flex; flex-direction:column; gap:10px;">{label(f"lab 2 &#183; you &#183; {len(B)} batches &#215; {len(rt)} ways of checking", PINK)}{chart}</div>'
    return grid, changed


def a11_waffle(replay, n, outside, labs_flagged):
    """A11's left panel: every lab's batches in run order, flagged ones hollow."""
    order = sorted(replay, key=lab_number)
    cell, gap = 9, 3
    strip = lambda s: (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {len(replay[s]["batches"]) * (cell + gap) - gap} {cell}" width="{len(replay[s]["batches"]) * (cell + gap) - gap}" height="{cell}" aria-hidden="true" style="display:block;">'
                       + ''.join(batch_square(k * (cell + gap), 0, cell, b['verdict'] == 'outside', PINK if s == 'source_2' else GREEN) for k, b in enumerate(replay[s]['batches'])) + '</svg>')
    rows = ''.join(
        f'<div style="display:flex; align-items:center; gap:10px; height:19px;">'
        f'<span style="{MONO} font-size:13px; width:92px; white-space:nowrap; text-align:right; color:{PINK if s == "source_2" else INK2}; font-weight:{600 if s == "source_2" else 400};">'
        f'{lab_name(s) + (" &#183; you" if s == "source_2" else "")}</span>{strip(s)}</div>'
        for s in order)
    waffle = (f'<div style="flex:0 0 auto; display:flex; flex-direction:column; gap:10px;">{label(f"all {len(replay)} labs &#183; {n} batches")}'
              f'<div role="img" aria-label="Verdicts for {n} batches in {len(replay)} labs; {outside} are flagged, in {labs_flagged} labs." style="flex:1; display:flex; flex-direction:column; justify-content:center;">{rows}</div></div>')
    return waffle


def a11_differs(rt, B, nbase, changed):
    """The one way of checking that differs: the batch its baseline takes in, and the batches it flags beyond the published ones."""
    differs = [name for name, v in rt.items() if v['verdicts'] != rt['as published']['verdicts']]
    assert len(differs) == changed == 1 and differs[0] in nbase, f'A11 names one variant that differs: {differs}'
    added = B[nbase[differs[0]] - 1]            # the batch that variant's baseline takes in beyond the first
    assert added['cells_per_well'] == min(b['cells_per_well'] for b in B), 'A11 says the batch it takes in has the fewest cells'
    pub, alt = rt['as published']['verdicts'], rt[differs[0]]['verdicts']
    extra = [k for k, (p, a) in enumerate(zip(pub, alt)) if a == 'O' and p != 'O']
    assert all(a == 'O' for p, a in zip(pub, alt) if p == 'O') and extra == list(range(extra[0], extra[-1] + 1)), 'A11 says the one way that differs only adds flags, in one run'
    return added, extra


def a11_legend():
    """A11's key: lab 2, other labs, flagged, and the baseline outline."""
    swatch = lambda flagged, colour: batch_square(0, 0, 11, flagged, colour)
    key = lambda svg_body, name: (f'<span style="display:flex; align-items:center; gap:7px;"><svg viewBox="-1 -1 13 13" width="13" height="13" aria-hidden="true">{svg_body}</svg>{name}</span>')
    legend = (f'<div style="display:flex; gap:22px; align-items:center; padding-top:10px; margin-top:4px; border-top:1px solid #eceff0; {MONO} font-size:13px; color:{MUTE};">'
              + key(swatch(False, PINK), 'lab 2 &#183; you') + key(swatch(False, GREEN), 'other labs') + key(swatch(True, MUTE), 'flagged')
              + key(f'<rect x="-0.5" y="-0.5" width="12" height="12" rx="3.5" fill="none" stroke="{INK2}" stroke-width="1.4"/><rect x="2.5" y="2.5" width="6" height="6" rx="1.5" fill="{PINK}"/>',
                    'baseline: the batches it is compared with') + '</div>')
    return legend


def a11():
    rt = results('e9-replay-redteam.json')['source_2']
    replay = results('e9-replay.json')['labs']
    B = replay['source_2']['batches']
    n = sum(v['n_batches'] for v in replay.values()); outside = sum(v['batches_outside'] for v in replay.values())
    labs_flagged = sum(v['batches_outside'] > 0 for v in replay.values())
    fl = [b for b in B if b['verdict'] == 'outside']; ok = [b for b in B if b['verdict'] != 'outside']
    names, nbase = a11_variant_names(rt)
    grid, changed = a11_grid(rt, B, names, nbase)
    waffle = a11_waffle(replay, n, outside, labs_flagged)
    added, extra = a11_differs(rt, B, nbase, changed)
    legend = a11_legend()
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
  <div class="note" style="{NOTE}">Each plate checked against its own lab&#8217;s first batch &#183; {n_plates:,} plates &#183; {len(replay)} labs &#183; JUMP [7] &#183; lab 2 over time: A13</div>
</div>'''
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A12
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


def e6_group(e, m, c):
    """e6's group of features for one measurement and channel, or None."""
    return next((g for g in e['groups'] if g['measurement'] == m and g['channel'] == c), None)


def a12_chart(first, last, B, base, channels):
    """A12's bars: how far brightness and texture moved in each channel, first flagged batch and latest, from the first batch."""
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
                grp = e6_group(e, measure, c)
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
    return chart


def a12():
    first = results('e6-what-moved-source_2-first-flag.json'); last = results('e6-what-moved-source_2.json')
    B = {b['batch']: b for b in results('e9-replay.json')['labs']['source_2']['batches']}
    base = next(b for b in B.values() if b['is_baseline'])
    channels = ['ER', 'AGP', 'Mito', 'DNA']
    chart = a12_chart(first, last, B, base, channels)
    pictures = raw_pair(base, B[first['batch']])
    a, b = e6_group(first, 'Intensity', 'ER'), e6_group(first, 'Intensity', 'AGP')
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
  <div class="note" style="{NOTE}">{", ".join(channels)}: {["one", "two", "three", "four", "five"][len(channels) - 1]} stain channels, each marking different parts of the cell &#183; each bar averages one channel&#8217;s measurements &#183; JUMP [7]</div>
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
    <p style="{LEDE}"><span style="color:{PINK};">Lab 2</span>, {len(B)} batches, two views.<br>Not a verdict: a reason to look.</p>
  </div>
  <div style="display:flex; gap:16px; flex-grow:1; min-height:0;">{panel(cell_count_chart(B), 0.2)}{panel(distance, 0.35)}</div>
  <div class="note" style="{NOTE}">distance unit: usual spread between wells on one plate &#183; lab 2 &#183; 2021 &#183; JUMP [7] &#183; which batches: A11 &#183; what moved: A12</div>
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
    {card('best batch', best_body, 0.6, colour=MUTE, center=True)}
    {card('your choice to play', 'Named only if you opt in.<br>Private version for your own plates.', 0.7, center=True)}
  </div>
  <div class="note" style="{NOTE}">Lab medians &#183; {lb["n_plates"]:,} plates &#183; {lb["n_labs"]} labs &#183; clean run: batches in a row never flagged (A11) &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None
