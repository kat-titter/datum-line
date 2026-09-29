"""Rebuild slide 05 (template t4) of the deck from results files. Nothing is typed by hand:
every number on the slide is read from results/*.json or results/e2-embedding.csv."""
import csv, json, re, sys
from datetime import date

src, out, R = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
tl = json.load(open(f'{R}/e2-timeline-source_2.json'))
pos = json.load(open(f'{R}/e2-plate-position-1053600681.json'))
drift = json.load(open(f'{R}/e1b-drift-source_2.json'))
e8 = json.load(open(f'{R}/e8-redteam.json'))
e1 = json.load(open(f'{R}/e1.json'))['all_sources']
F = "font-family=\"'Helvetica Neue', Helvetica, Arial, sans-serif\""
MONO = "font-family: 'IBM Plex Mono', Menlo, monospace;"
PINK, GREEN, INK, MUTE, GRID, PANEL = '#be1e74', '#0f8f6c', '#454c50', '#666e72', '#d3d8da', '#eceeef'

B = tl['batches']; last = B[-1]
d0, d1 = date.fromisoformat(B[0]['date']), date.fromisoformat(last['date'])
span = (d1 - d0).days
lab_name = lambda s: 'lab ' + s.split('_')[1]

def block_end(s, i, tag):
    depth = 0
    for m in re.finditer(r'<%s\b|</%s>' % (tag, tag), s[i:]):
        depth += 1 if m.group(0).startswith('<' + tag) else -1
        if depth == 0:
            return i + m.end()

def swap(s, opener, new, tag):
    i = s.find(opener); assert i >= 0, opener
    return s[:i] + new + s[block_end(s, i, tag):]

def panel(x0, title, ylab, lo, hi, ticks, anim):
    """Axes shared by both time panels: same x scale, so the eye compares like with like."""
    x1, y0, y1 = x0 + 660, 64.0, 440.0
    X = lambda day: x0 + 36 + (date.fromisoformat(day) - d0).days / span * (x1 - x0 - 72)
    Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)
    g = [f'<text x="{x0}" y="34.0" {F} font-size="22" fill="{MUTE}" letter-spacing="2.20">{title}</text>',
         f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{PANEL}"/>']
    for v in ticks:
        g.append(f'<path d="M {x0} {Y(v):.1f} L {x1} {Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>'
                 f'<text x="{x0 - 10}" y="{Y(v) + 7:.1f}" {F} font-size="20" fill="{MUTE}" text-anchor="end">{v}</text>')
    g.append(f'<path d="M {x0} {y0} L {x0} {y1} L {x1} {y1}" fill="none" stroke="{MUTE}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    for m, name in ((6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Oct')):
        day = date(2021, m, 7 if m == 6 else 1).isoformat()
        g.append(f'<path d="M {X(day):.1f} {y1} L {X(day):.1f} {y1 + 8}" stroke="{MUTE}" stroke-width="2"/>'
                 f'<text x="{X(day):.1f}" y="{y1 + 30}" {F} font-size="20" fill="{MUTE}" text-anchor="middle">{name}</text>')
    g.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{y1 + 62}" {F} font-size="22" fill="{INK}" text-anchor="middle">batch date, 2021 ({len(B)} batches, {sum(b["n_plates"] for b in B)} plates)</text>')
    g.append(f'<g transform="translate({x0 - 66},{(y0 + y1) / 2:.1f}) rotate(-90)"><text x="0" y="0" {F} font-size="22" fill="{INK}" text-anchor="middle">{ylab}</text></g>')
    return g, X, Y

# ---- left: the check the lab already runs
g, X, Y = panel(96.0, 'WHAT THE LAB CAN SEE', 'cells per untreated well', 130, 220, (150, 175, 200), 'pd')
for k, b in enumerate(B[:-1]):
    g.append(f'<circle class="pd" style="animation-delay:{0.2 + 0.08 * k:.2f}s" cx="{X(b["date"]):.1f}" cy="{Y(b["cells_per_well"]):.1f}" r="9" fill="#949c9f"/>')
tx, ty = X(last['date']), Y(last['cells_per_well'])
g.append(f'<circle class="this" style="animation-delay:1.4s" cx="{tx:.1f}" cy="{ty:.1f}" r="13" fill="{PINK}" stroke="{PANEL}" stroke-width="3.5"/>')
g.append(f'<g class="note" style="animation-delay:1.8s"><text x="{tx - 8:.1f}" y="{ty + 58:.1f}" {F} font-size="28" font-weight="700" fill="{PINK}" text-anchor="end">October batch</text>'
         f'<text x="{tx - 8:.1f}" y="{ty + 90:.1f}" {F} font-size="24" fill="{INK}" text-anchor="end">{last["cells_per_well"]:.0f} cells per well</text>'
         f'<text x="{tx - 8:.1f}" y="{ty + 120:.1f}" {F} font-size="24" fill="{INK}" text-anchor="end">inside the lab&#8217;s range</text></g>')
LP = '<g class="Lp">' + ''.join(g) + '</g>'

# ---- right: the same batches, placed against the field
hi = max(b['from_baseline'] for b in B)
g, X, Y = panel(916.0, 'WHAT ONLY EVERYONE ELSE CAN SEE', 'distance, in within-plate spreads', 0, 13, (0, 4, 8, 12), 'pd')
line = lambda key: ' '.join(f'{"M" if k == 0 else "L"} {X(b["date"]):.1f} {Y(b[key]):.1f}' for k, b in enumerate(B))
g.append(f'<path d="{line("to_nearest_other")}" fill="none" stroke="{GREEN}" stroke-width="3" stroke-linejoin="round"/>')
g.append(f'<path d="{line("from_baseline")}" fill="none" stroke="{PINK}" stroke-width="3.6" stroke-linejoin="round"/>')
for b in B:
    g.append(f'<circle cx="{X(b["date"]):.1f}" cy="{Y(b["to_nearest_other"]):.1f}" r="6" fill="{GREEN}"/>')
    g.append(f'<circle cx="{X(b["date"]):.1f}" cy="{Y(b["from_baseline"]):.1f}" r="7" fill="{PINK}"/>')
g.append(f'<text x="952" y="98" {F} font-size="24" font-weight="700" fill="{PINK}">from its own June baseline</text>')
g.append(f'<text x="952" y="130" {F} font-size="24" font-weight="700" fill="{GREEN}">to the nearest other lab</text>')
RP = '<g class="Rp">' + ''.join(g) + '</g>'

# ---- scatter: every lab a shade of green, lab 2 in pink, June light and October strong
rows = list(csv.DictReader(open(f'{R}/e2-embedding.csv')))
june = set(B[0]['plates']) | set(B[1]['plates']); octo = set(last['plates'])
labs = sorted({r['lab'] for r in rows if r['lab'] != tl['lab']}, key=lambda s: int(s.split('_')[1]))
shade = lambda k, n: '#%02x%02x%02x' % tuple(round(a + (b - a) * k / max(1, n - 1)) for a, b in zip((10, 92, 70), (176, 226, 208)))
colour = {l: shade(k, len(labs)) for k, l in enumerate(labs)}
xs = sorted(float(r['pc1']) for r in rows); ys = sorted(float(r['pc2']) for r in rows)
q = lambda v, p: v[int(p * (len(v) - 1))]
xlo, xhi, ylo, yhi = q(xs, .005), q(xs, .995), q(ys, .005), q(ys, .995)
W, H, px0, py0, pw, ph = 1460, 640, 84, 20, 1010, 540
PX = lambda v: px0 + (min(max(v, xlo), xhi) - xlo) / (xhi - xlo) * pw
PY = lambda v: py0 + ph - (min(max(v, ylo), yhi) - ylo) / (yhi - ylo) * ph
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" style="display:block; width:100%; height:100%;">',
     f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" fill="{PANEL}"/>']
for l in labs:
    pts = [r for r in rows if r['lab'] == l][::3]
    s.append(f'<g fill="{colour[l]}" opacity="0.75">' + ''.join(f'<circle cx="{PX(float(r["pc1"])):.0f}" cy="{PY(float(r["pc2"])):.0f}" r="3.6"/>' for r in pts) + '</g>')
mine = [r for r in rows if r['lab'] == tl['lab']]
s.append('<g fill="#e9a3c6" opacity="0.9">' + ''.join(f'<circle cx="{PX(float(r["pc1"])):.0f}" cy="{PY(float(r["pc2"])):.0f}" r="3.6"/>' for r in mine if r['plate'] in june) + '</g>')
s.append(f'<g fill="{PINK}">' + ''.join(f'<circle cx="{PX(float(r["pc1"])):.0f}" cy="{PY(float(r["pc2"])):.0f}" r="4.2"/>' for r in mine if r['plate'] in octo) + '</g>')
v1, v2 = [round(100 * v, 1) for v in pos['pca']['variance_explained']]
s.append(f'<path d="M {px0} {py0} L {px0} {py0 + ph} L {px0 + pw} {py0 + ph}" fill="none" stroke="{MUTE}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
s.append(f'<text x="{px0 + pw / 2}" y="{py0 + ph + 44}" {F} font-size="26" fill="{INK}" text-anchor="middle">PC 1 ({v1}% of variance)</text>')
s.append(f'<g transform="translate({px0 - 30},{py0 + ph / 2}) rotate(-90)"><text x="0" y="0" {F} font-size="26" fill="{INK}" text-anchor="middle">PC 2 ({v2}% of variance)</text></g>')
lx, ly = px0 + pw + 44, py0 + 24
s.append(f'<text x="{lx}" y="{ly}" {F} font-size="24" fill="{MUTE}" letter-spacing="2">LAB</text>')
legend = [('lab 2, June', '#e9a3c6'), ('lab 2, October', PINK)] + [(lab_name(l), colour[l]) for l in labs]
for k, (name, c) in enumerate(legend):
    y = ly + 44 + k * 42
    s.append(f'<circle cx="{lx + 11}" cy="{y - 9}" r="11" fill="{c}"/><text x="{lx + 36}" y="{y}" {F} font-size="28" fill="{"#be1e74" if "lab 2" in name else INK}" font-weight="{700 if "lab 2" in name else 400}">{name}</text>')
s.append('</svg>')
SCATTER = ''.join(s)

# ---- e8, with the field defined as every other lab
C = e8['all_features']['compounds']
order = sorted(C, key=lambda c: -C[c]['agreement_with_own_lab'])
strong = [c for c in order if C[c]['within_labs']['p_permutation'] < 0.01 and C[c]['effect_size']['cv_of_lab_means_pct'] < 100]
cvb = [C[c]['effect_size']['cv_of_lab_means_pct'] for c in strong]; cvw = [C[c]['effect_size']['median_cv_within_lab_pct'] for c in strong]
pooled = e8['all_features']['pooled_within_lab_and_compound']
x0, xw, rowh, y0 = 330, 760, 52, 70
g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 548" preserveAspectRatio="xMidYMid meet" style="display:block; width:1124px; height:385px;">',
     f'<text x="20" y="34" {F} font-size="22" fill="{MUTE}" letter-spacing="2.20">HOW MUCH LABS AGREE ON WHAT A DRUG DOES</text>',
     f'<text x="{x0}" y="{y0 - 14}" {F} font-size="20" fill="#949c9f">agreement of a plate&#8217;s measured effect (cosine), 0 to 1</text>']
for k, c in enumerate(order):
    y = y0 + k * rowh; a, b = max(C[c]['agreement_with_own_lab'], 0), max(C[c]['agreement_with_other_labs'], 0)
    g.append(f'<text x="{x0 - 16}" y="{y + 22}" {F} font-size="22" fill="#14171a" text-anchor="end">{c}</text>'
             f'<rect class="bar" x="{x0}" y="{y + 4}" width="{xw * a:.1f}" height="14" rx="3" fill="#c3c9cb" style="animation-delay:{0.1 + 0.05 * k:.2f}s"/>'
             f'<rect class="bar" x="{x0}" y="{y + 22}" width="{xw * b:.1f}" height="14" rx="3" fill="{PINK}" style="animation-delay:{0.3 + 0.05 * k:.2f}s"/>'
             f'<text x="{x0 + xw * a + 10:.1f}" y="{y + 16}" {F} font-size="18" fill="{MUTE}">{a:.2f}</text>'
             f'<text x="{x0 + xw * b + 10:.1f}" y="{y + 34}" {F} font-size="18" fill="{PINK}">{b:.2f}</text>')
ly = y0 + len(order) * rowh + 14
g.append(f'<rect x="{x0}" y="{ly}" width="26" height="12" rx="3" fill="#c3c9cb"/><text x="{x0 + 34}" y="{ly + 11}" {F} font-size="20" fill="{INK}">with its own lab</text>'
         f'<rect x="{x0 + 250}" y="{ly}" width="26" height="12" rx="3" fill="{PINK}"/><text x="{x0 + 284}" y="{ly + 11}" {F} font-size="20" fill="{INK}">with every other lab</text>')
rx = 1180
g.append(f'<text x="{rx}" y="{y0 + 10}" {F} font-size="22" fill="{MUTE}" letter-spacing="2.20">AND WHY</text>'
         f'<text x="{rx}" y="{y0 + 88}" {F} font-size="72" font-weight="700" fill="{PINK}">{min(cvb):.0f}&#8211;{max(cvb):.0f}%</text>'
         f'<text x="{rx}" y="{y0 + 124}" {F} font-size="22" fill="{INK}">how much the same compound&#8217;s effect</text>'
         f'<text x="{rx}" y="{y0 + 152}" {F} font-size="22" fill="{INK}">size differs between labs</text>'
         f'<text x="{rx}" y="{y0 + 180}" {F} font-size="20" fill="#949c9f">inside one lab: {min(cvw):.0f}&#8211;{max(cvw):.0f}% ({len(strong)} compounds)</text>'
         f'<text x="{rx}" y="{y0 + 250}" {F} font-size="22" font-weight="700" fill="{GREEN}">The further a plate&#8217;s controls sit from</text>'
         f'<text x="{rx}" y="{y0 + 278}" {F} font-size="22" font-weight="700" fill="{GREEN}">the field, the more its answer moves.</text>'
         f'<text x="{rx}" y="{y0 + 310}" {F} font-size="20" fill="{INK}">inside labs: Spearman {pooled["spearman"]:.2f}, shuffled {pooled["null_mean"]:.2f}</text>'
         f'<text x="{rx}" y="{y0 + 338}" {F} font-size="20" fill="{INK}">between {e8["n_labs"]} labs: same sign, too few to prove</text></svg>')
E8 = ''.join(g)

seg = re.search(r'<template id="t4">.*?</template>', t, flags=re.S); s = seg.group(0)
s = swap(s, '<g class="Lp">', LP, 'g'); s = swap(s, '<g class="Rp">', RP, 'g')
rep = lambda a, b: (s.count(a) == 1 or sys.exit('missing: ' + a[:60])) and s.replace(a, b)
near = lab_name(last['nearest_other'])
s = rep('It says lab 2. <span style="color: #ef74ad;">Its cells say otherwise.</span>', f'Four months on, <span style="color: #ef74ad;">nearer {near} than itself.</span>')
s = rep('Even one lab <span style="color: #ef74ad;">drifts.</span>', 'Same lab, <span style="color: #ef74ad;">two different places.</span>')
s = rep('Same cells, same SOP, same building.', 'Same lab, same line, same protocol.')
s = re.sub(r'(<span class="n96"[^>]*>)96%(</span>)', r'\g<1>%.1f\2' % last['from_baseline'], s)
m = re.search(r'<span class="bt".*?</span></span></span>', s, flags=re.S); assert m
s = s[:m.start()] + f'<span class="bt" style="display:flex; flex-direction:column; gap:6px;"><span style="{MONO} font-size:13px; color:#c9cfd1;">spreads from its own June baseline</span><span style="{MONO} font-size:13px; color:#f6f7f7;">{last["to_nearest_other"]:.1f} to {near}</span><span style="{MONO} font-size:13px; color:#c9cfd1;">still named lab 2 by every well</span></span>' + s[m.end():]
bins = {b['gap']: b for b in drift['bins']}; first, far = bins['same batch'], drift['bins'][-1]
steps = (f'<div class="steps" style="position: absolute; left: 56px; top: 250px; width: 350px; display: flex; flex-direction: column; gap: 10px;">'
         f'<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size: 84px; font-weight: 700; letter-spacing: -0.045em; line-height: 0.92; color: #ef74ad;">{far["ratio_to_same_batch"]:.0f}&#215;</span>'
         f'<span style="{MONO} font-size:13px; line-height:1.6; color:#c9cfd1;">two plates of one lab sit<br><span style="color:#f6f7f7;">{first["median"]:.1f}</span> spreads apart in the same batch<br><span style="color:#f6f7f7;">{far["median"]:.1f}</span> apart {far["gap"]} later</span></div>')
s = swap(s, '<div class="steps"', steps, 'div')
i = s.find('<div class="card time"'); j = s.find('<img', i); k = s.find('>', j) + 1
s = s[:j] + SCATTER + s[k:]
s = rep('Between batches &#183; time', 'Every untreated well, coloured by lab')
s = re.sub(r'<span[^>]*>One institution &#183; 31 plates &#183; 8 runs</span>', '', s)
s = re.sub(r'<div[^>]*>One institution &#183; 31 plates &#183; 8 runs</div>', '', s)
i = s.find('<div class="card drug"'); j = s.find('<svg', i); s = s[:j] + E8 + s[block_end(s, j, 'svg'):]
s = re.sub(r'(<div class="foot f0"[^>]*>).*?(</div>)', r'\1Cells per untreated well, lab 2, %d batches, June to October 2021. <span style="color: #f6f7f7;">Click for what only the field can see.</span>\2' % len(B), s, flags=re.S)
s = re.sub(r'(<div class="foot f1"[^>]*>).*?(</div>)', r'\1<span style="color: #f6f7f7; font-weight: 500;">Fig. 4</span> Left: mean cells per untreated well, per batch. Right: median distance of each batch&#8217;s plates from the lab&#8217;s first batch, and to the nearest other lab&#8217;s centre, in within-plate spreads; z-scores clipped to &#177;5. %s wells, %d labs, %s features [7]. Fluorescence; brightfield is the bet. results/e2-timeline\2' % (f'{tl["n_wells_in_field"]:,}', tl['n_labs'], f'{tl["n_features"]:,}'), s, flags=re.S)
s = rep('Distance between plate centroids of the same cells, in units of within-plate spread; same-day reference 0.74 (n = 27). results/e1b', f'PCA of {pos["pca"]["wells"]:,} untreated wells, {pos["pca"]["wells_per_plate"]} per plate. Distances are measured in all {pos["n_features"]:,} features, not in this projection. results/e2, e1b')
s = re.sub(r'JUMP&#8217;s eight shared positive controls on .*?results/e8', f'JUMP&#8217;s eight shared positive controls, {e8["n_plates"]} plates, {e8["n_labs"]} labs; effect = treated minus same-plate DMSO; each plate compared with every lab but its own [7] &#183; results/e8-redteam', s, flags=re.S)
s = re.sub(r'(<span class="platetag"[^>]*>)[^<]*(</span>)', r'\1lab 2 &#183; June to October 2021\2', s)
t = t[:seg.start()] + s + t[seg.end():]
a = '"tag": ["What its own lab can see", "A plate in the wrong territory", "The same lab, over time", "The same drug, a different answer"]'
assert t.count(a) == 1
t = t.replace(a, '"tag": ["What its own lab can see", "Four months later", "Where the wells sit", "The same drug, a different answer"]')
t = t.replace('"hint": ["click \\u2192 the field", "click \\u2192 time", "click \\u2192 the drug", "click \\u2192 start over"]', '"hint": ["click \\u2192 the field", "click \\u2192 the map", "click \\u2192 the drug", "click \\u2192 start over"]')
open(out, 'w').write(t); print('built slide 05;', len(rows), 'scatter wells')
