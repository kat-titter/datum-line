"""Carry the verified numbers into slide 04 (template t3) and slide 06 (t5).
Every number is read from results/*.json or results/e2-embedding.csv."""
import csv, json, re, sys
import numpy as np

src, out, R = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
e1 = json.load(open(f'{R}/e1.json'))['all_sources']
tl = json.load(open(f'{R}/e2-timeline-source_2.json'))
pos = json.load(open(f'{R}/e2-plate-position-1053600681.json'))
F = "font-family=\"'Helvetica Neue', Helvetica, Arial, sans-serif\""
SANS = "font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif;"
MONO = "font-family: 'IBM Plex Mono', Menlo, monospace;"
PINK, INK, MUTE, PANEL = '#be1e74', '#454c50', '#666e72', '#eceeef'
cm = np.array(e1['confusion_matrix']['rows_true_cols_pred']); wrong = int(cm.sum() - np.trace(cm))
acc, chance = 100 * e1['balanced_accuracy'], 100 * e1['chance']
n_wells, n_labs, n_feat = f"{e1['n_wells']:,}", e1['n_labs'], f"{e1['n_features']:,}"
last = tl['batches'][-1]; near = 'lab ' + last['nearest_other'].split('_')[1]

def sub(tid, fn):
    global t
    seg = re.search(r'<template id="%s">.*?</template>' % tid, t, flags=re.S)
    t = t[:seg.start()] + fn(seg.group(0)) + t[seg.end():]

def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:70])
    return s.replace(a, b)

def scatter(target_plate):
    rows = list(csv.DictReader(open(f'{R}/e2-embedding.csv')))
    labs = sorted({r['lab'] for r in rows}, key=lambda s: int(s.split('_')[1]))
    shade = lambda k, n: '#%02x%02x%02x' % tuple(round(a + (b - a) * k / max(1, n - 1)) for a, b in zip((10, 92, 70), (176, 226, 208)))
    colour = {l: shade(k, len(labs)) for k, l in enumerate(labs)}
    xs = sorted(float(r['pc1']) for r in rows); ys = sorted(float(r['pc2']) for r in rows)
    q = lambda v, p: v[int(p * (len(v) - 1))]
    xlo, xhi, ylo, yhi = q(xs, .005), q(xs, .995), q(ys, .005), q(ys, .995)
    W, H, x0, y0, w, h = 1180, 392, 64, 10, 1104, 330
    PX = lambda v: x0 + (min(max(v, xlo), xhi) - xlo) / (xhi - xlo) * w
    PY = lambda v: y0 + h - (min(max(v, ylo), yhi) - ylo) / (yhi - ylo) * h
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Untreated wells from {len(labs)} labs as points, one shade of green per lab; this plate in pink, inside its own lab." style="width:100%; height:100%; display:block;">',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{PANEL}"/>']
    for l in labs:
        pts = [r for r in rows if r['lab'] == l and r['plate'] != target_plate][::3]
        g.append(f'<g fill="{colour[l]}" opacity="0.75">' + ''.join(f'<circle cx="{PX(float(r["pc1"])):.0f}" cy="{PY(float(r["pc2"])):.0f}" r="3.4"/>' for r in pts) + '</g>')
    mine = [r for r in rows if r['plate'] == target_plate][::4]
    g.append(f'<g fill="{PINK}">' + ''.join(f'<circle cx="{PX(float(r["pc1"])):.0f}" cy="{PY(float(r["pc2"])):.0f}" r="4"/>' for r in mine) + '</g>')
    cx = sum(PX(float(r['pc1'])) for r in mine) / len(mine); cy = sum(PY(float(r['pc2'])) for r in mine) / len(mine)
    g.append(f'<path d="M {cx - 16:.0f} {cy - 14:.0f} L {cx - 70:.0f} {cy - 62:.0f}" stroke="{PINK}" stroke-width="2.5" stroke-linecap="round"/>'
             f'<text x="{cx - 76:.0f}" y="{cy - 84:.0f}" {F} font-size="26" font-weight="700" fill="{PINK}" text-anchor="end">this plate</text>'
             f'<text x="{cx - 76:.0f}" y="{cy - 56:.0f}" {F} font-size="22" fill="{INK}" text-anchor="end">inside lab 2</text>')
    v1, v2 = [round(100 * v, 1) for v in pos['pca']['variance_explained']]
    g.append(f'<path d="M {x0} {y0} L {x0} {y0 + h} L {x0 + w} {y0 + h}" fill="none" stroke="{MUTE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<text x="{x0 + w / 2}" y="{y0 + h + 40}" {F} font-size="24" fill="{INK}" text-anchor="middle">PC 1 ({v1}% of variance)</text>'
             f'<g transform="translate({x0 - 24},{y0 + h / 2}) rotate(-90)"><text x="0" y="0" {F} font-size="24" fill="{INK}" text-anchor="middle">PC 2 ({v2}%)</text></g></svg>')
    return ''.join(g)

def f04(s):
    s = re.sub(r'(font-size:104px;[^>]*color:#0f8f6c;">)96%(</span>)', r'\g<1>%.1f%%\2' % acc, s)
    s = re.sub(r'(font-size:104px;[^>]*color:#c3c9cb;">)14%(</span>)', r'\g<1>%.0f%%\2' % chance, s)
    s = s.replace('font-size:104px; font-weight:700; letter-spacing:-0.045em; line-height:.9;', 'font-size:96px; font-weight:700; letter-spacing:-0.045em; line-height:.9;')
    s = rep(s, 'the 4% it gets wrong', f'{wrong} wells wrong, of {n_wells}')
    s = rep(s, 'JUMP cpg0016 (CC0), untreated wells, DNA channel &#183; n = 12,046, 7 labs &#183; 96.2% vs chance 14.3%, held out by plate',
            f'JUMP cpg0016 (CC0) [7]. Images: untreated wells, DNA channel, six labs. Classifier: {n_wells} untreated wells, {n_labs} labs, held out by plate; balanced accuracy {acc:.1f}% vs chance {chance:.1f}% &#183; results/e1')
    s = s.replace('3,781', n_feat)
    m = re.search(r'<img src="data:image/svg\+xml;base64,[^"]+" alt="12,046 untreated wells[^"]*"[^>]*>', s); assert m
    s = s[:m.start()] + scatter('1053600681') + s[m.end():]
    s = rep(s, '12,046 wells, 7 labs', f'{n_wells} wells, {n_labs} labs')
    return s
sub('t3', f04)

def f06(s):
    plate = last['plates'][len(last['plates']) // 2]
    s = rep(s, 'text-transform: uppercase; color:#be1e74;">plate 1053600681</span>', f'text-transform: uppercase; color:#be1e74;">lab 2 &#183; October batch</span>')
    s = rep(s, '>U2OS, untreated wells, 14 June 2021</span>', f'>U2OS, untreated wells, {last["n_plates"]} plates, 3 October 2021</span>')
    s = rep(s, '>12,046 untreated wells from 7 labs [7]</span>', f'>{n_wells} untreated wells from {n_labs} labs [7]</span>')
    s = rep(s, '0 of 384 wells look like lab 2. Local QC passed.', f'{last["from_baseline"]:.1f} spreads from your June baseline, {last["to_nearest_other"]:.1f} from {near}. Cell count normal.')
    s = rep(s, 'The same field of the same well, plate 1053600681, lab 2. The shown work is fluorescence; label-free brightfield is the bet.', 'One field of one well, two ways: lab 2, June 2021. The shown work is fluorescence; label-free brightfield is the bet.')
    return s
sub('t5', f06)
old = '"Batch correction deletes this: 96% becomes 12%. Right for discovery, wrong for QC."'
assert t.count(old) == 1
t = t.replace(old, '"Centre each plate on its own controls and this signature goes. Right for discovery, wrong for QC."')
open(out, 'w').write(t); print(f'built 04 and 06: {acc:.2f}% vs {chance:.1f}%, {wrong} wrong of {n_wells}')
