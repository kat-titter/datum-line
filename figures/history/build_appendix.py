"""Carry the verified numbers into the appendix (A2, A3, A6, A10) and slide 04's footer.
Every number is read from results/*.json."""
import json, re, sys

src, out, R = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
e1 = json.load(open(f'{R}/e1.json')); full, no1536 = e1['all_sources'], e1['without_1536_well_sources']
rt = json.load(open(f'{R}/e1-redteam.json'))['tests']
dr = json.load(open(f'{R}/e1b-drift-source_2.json'))
F = "font-family=\"'Helvetica Neue', Helvetica, Arial, sans-serif\""
pc = lambda x, d=0: f'{100 * x:.{d}f}%'
acc, chance = pc(full['balanced_accuracy'], 1), pc(full['chance'])
centred, scaled, perm = pc(rt['plate_centred']['balanced_accuracy']), pc(rt['plate_scaled']['balanced_accuracy']), pc(rt['permuted']['balanced_accuracy'], 1)
n_rt = f"{rt['baseline']['n_wells']:,}"; n_wells = f"{full['n_wells']:,}"; n_feat = str(full['n_features'])
bins = dr['bins']


def sub(tid, fn):
    global t
    seg = re.search(r'<template id="%s">.*?</template>' % tid, t, flags=re.S)
    t = t[:seg.start()] + fn(seg.group(0)) + t[seg.end():]


def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:70])
    return s.replace(a, b)


def a2(s):
    s = rep(s, '>3781<', f'>{n_feat}<')
    s = rep(s, '>96%<', f'>{acc}<')
    s = rep(s, 'Model and folds: [results/e1]. Balanced accuracy, chance 1/7. Permuted labels 15.2%. Without the 1536-well source: still 96%.',
            f'Logistic regression, L2, five folds. Balanced accuracy, chance 1/{full["n_labs"]}. Permuted labels {perm}. Without the 1536-well labs: {pc(no1536["balanced_accuracy"], 1)}.')
    s = rep(s, '>12%<', f'>{centred}<')
    s = rep(s, 'Remove only what you know is instrument, keep what may be biology. Remove the whole batch, as reference alignment or covariance matching does, and f collapses.',
            f'Remove only what you know is instrument, keep what may be biology. Remove each plate&#8217;s own control mean and f falls to {centred}.')
    return s


def a3(s):
    s = rep(s, '>96%<', f'>{acc}<'); s = rep(s, '>14%<', f'>{centred}<'); s = rep(s, '>12%<', f'>{scaled}<')
    s = rep(s, '>per-plate standardised<', '>plate-centred<')
    s = rep(s, '>at chance, 1 in 7<', f'>own control mean removed; chance {chance}<')
    s = rep(s, '>per-batch whitening (TVN)<', '>plate-centred and scaled<')
    s = rep(s, '>below chance: the coordinate is gone<', '>own control spread removed too<')
    s = rep(s, 'Same 12,046 wells, same held-out-by-plate split. results/e1.', f'{n_rt} wells, 16 per plate, plates held out. results/e1-redteam.')
    s = rep(s, 'Per-batch whitening, the standard fix, names the lab 12% of the time: below chance. It deletes the coordinate a certificate needs.',
            f'Centre each plate on its own controls, the standard first step, and the lab is named {centred} of the time. It removes most of the coordinate a certificate needs.')
    return s


def drift_chart():
    W, H, x0, y0, w, h = 1500, 430, 110, 30, 1320, 300
    top = max(b['iqr'][1] for b in bins) * 1.1
    Y = lambda v: y0 + h - v / top * h
    X = lambda k: x0 + (k + 0.5) * w / len(bins)
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Median distance between two plates of one lab rises with the time between them." style="display:block; width:100%; height:100%;">',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#eceeef"/>']
    for v in range(0, int(top) + 1, 2):
        g.append(f'<path d="M {x0} {Y(v):.1f} L {x0 + w} {Y(v):.1f}" stroke="#d3d8da" stroke-width="2"/><text x="{x0 - 12}" y="{Y(v) + 7:.1f}" {F} font-size="20" fill="#666e72" text-anchor="end">{v}</text>')
    g.append(f'<path d="' + ' '.join(f'{"M" if k == 0 else "L"} {X(k):.1f} {Y(b["median"]):.1f}' for k, b in enumerate(bins)) + '" fill="none" stroke="#be1e74" stroke-width="3.6"/>')
    for k, b in enumerate(bins):
        g.append(f'<path d="M {X(k):.1f} {Y(b["iqr"][0]):.1f} L {X(k):.1f} {Y(b["iqr"][1]):.1f}" stroke="#be1e74" stroke-width="3" opacity=".45"/>'
                 f'<circle cx="{X(k):.1f}" cy="{Y(b["median"]):.1f}" r="9" fill="#be1e74"/>'
                 f'<text x="{X(k) + 16:.1f}" y="{Y(b["median"]) - 12:.1f}" {F} font-size="22" font-weight="700" fill="#be1e74">{b["median"]}</text>'
                 f'<text x="{X(k):.1f}" y="{y0 + h + 32}" {F} font-size="20" fill="#454c50" text-anchor="middle">{b["gap"]}</text>'
                 f'<text x="{X(k):.1f}" y="{y0 + h + 58}" {F} font-size="18" fill="#949c9f" text-anchor="middle">{b["n_pairs"]:,} pairs</text>')
    g.append(f'<path d="M {x0} {y0} L {x0} {y0 + h} L {x0 + w} {y0 + h}" fill="none" stroke="#666e72" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<text x="{x0 + w / 2}" y="{y0 + h + 92}" {F} font-size="22" fill="#454c50" text-anchor="middle">time between the two plates&#8217; batches</text>'
             f'<g transform="translate(36,{y0 + h / 2}) rotate(-90)"><text x="0" y="0" {F} font-size="22" fill="#454c50" text-anchor="middle">distance, within-plate spreads</text></g></svg>')
    return ''.join(g)


def a6(s):
    same, far = bins[0], bins[-1]
    s = rep(s, 'Two runs of the same cells drift apart for about three months, then stop. Drift is bounded, not runaway, which is exactly why a reference is possible at all.',
            f'Two plates of one lab sit further apart the longer the gap between them. In lab 2 the distance is still rising after thirteen weeks.')
    s = rep(s, 'No. A plateau means the state stays inside an envelope. Cells three months old are not on their way somewhere worse.',
            'Not known from profiles alone. The data says the lab moved and when. It does not say why.')
    s = rep(s, 'Because your certificate is a comparison made on one day. By three months it is as stale as it will ever get, so a quarter buys the whole useful life of one reading.',
            'Because your certificate is a comparison made on one day, and the baseline it was made against goes stale within weeks.')
    s = rep(s, 'One institution, 31 plates, 8 runs, June to October. The last bin is 30 pairs, so 2.30 then 2.12 is a plateau, not a decline. Every partner re-measures it.',
            f'One lab, {dr["n_plates"]} plates, {dr["n_batches"]} batches, June to October 2021. {same["median"]} in the same batch, {far["median"]} {far["gap"]}. Other labs are not yet measured.')
    s = re.sub(r'Distance between plate centroids, scaled by the spread of wells within a plate; matched well counts\..*?results/e1b\.',
               'Median distance between plate centroids, in within-plate spreads, with the interquartile range. results/e1b-drift.', s, flags=re.S)
    s = s.replace('>results/e1b<', '>results/e1b-drift<')
    # the old figure drew a plateau; replace whatever sits inside the large card
    m = re.search(r'<svg\b[^>]*>(?:(?!</svg>).)*a ceiling, not a cliff.*?</svg>', s, flags=re.S)
    if m is None:
        m = re.search(r'<img [^>]*alt="[^"]*"[^>]*>', s); assert m, 'A6 figure not found'
    return s[:m.start()] + drift_chart() + s[m.end():]


def a10(s):
    s = rep(s, 'Vehicle-only U2OS wells, seven institutions: the lab is named 96% of the time, chance 14%. results/e1',
            f'Untreated U2OS wells, {full["n_labs"]} labs: the lab is named {acc} of the time, chance {chance}. results/e1')
    return rep(s, 'the same 12,046 wells', f'the same {n_wells} wells')


for tid, fn in (('t12', a2), ('t13', a3), ('t16', a6), ('t20', a10)):
    sub(tid, fn)
old = '"Centre each plate on its own controls and this signature goes. Right for discovery, wrong for QC."'
assert t.count(old) == 1
t = t.replace(old, f'"Centre each plate on its own controls: {acc} becomes {centred}. Right for discovery, wrong for QC."')
open(out, 'w').write(t)
print('appendix built:', acc, centred, scaled, perm)
