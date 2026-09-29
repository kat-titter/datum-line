"""Write the documents from results/*.json: judge Q&A, whitepaper, brand, landscape, roadmap
and product vision. The documents as first published are kept in figures/assets/docs-original;
this reads those and writes docs/, so it can be run again after any analysis changes.
Every number is read from results/*.json. Run from the repository root.

Usage:  python figures/build_docs.py
"""
import json
import re

R = 'results'
e1 = json.load(open(f'{R}/e1.json')); full, no1536 = e1['all_sources'], e1['without_1536_well_sources']
rt = json.load(open(f'{R}/e1-redteam.json'))['tests']
replay = json.load(open(f'{R}/e9-replay.json'))['labs']
L2 = replay['source_2']; B2 = L2['batches']
e6 = json.load(open(f'{R}/e6-what-moved-source_2-first-flag.json'))
e10 = json.load(open(f'{R}/e10-certificate-predicts-answer.json'))
e11 = json.load(open(f'{R}/e11-known-answer.json'))
SRC = 'figures/assets/docs-original'
pos = json.load(open(f'{R}/e2-plate-position-1053600681.json'))
dr = json.load(open(f'{R}/e1b-drift-source_2.json'))
e8 = json.load(open(f'{R}/e8-redteam.json'))['all_features']

pc = lambda x, d=0: f'{100 * x:.{d}f}%'
ACC, CHANCE = pc(full['balanced_accuracy'], 1), pc(full['chance'], 1)
WELLS, PLATES, LABS, FEAT = f"{full['n_wells']:,}", f"{full['n_plates']:,}", full['n_labs'], f"{full['n_features']:,}"
PERM, CENTRED, SCALED = pc(rt['permuted']['balanced_accuracy'], 1), pc(rt['plate_centred']['balanced_accuracy']), pc(rt['plate_scaled']['balanced_accuracy'])
BATCH, SCOPE = pc(rt['batch_held_out']['balanced_accuracy'], 1), pc(rt['same_microscope']['balanced_accuracy'], 2)
N_SCOPE, N_RT = len(rt['same_microscope']['labs']), f"{rt['baseline']['n_wells']:,}"
NO1536, N_NO1536 = pc(no1536['balanced_accuracy'], 2), no1536['n_labs']
OCT = B2[-1]; NEAR = 'lab ' + OCT['nearest_other'].split('_')[1]
FLAG = next(b for b in B2 if b['verdict'] == 'outside')
FLAGGED = [b for b in B2 if b['verdict'] == 'outside']
N_BATCH, N_L2 = len(B2), sum(b['n_plates'] for b in B2)
N_ALL = sum(v['n_batches'] for v in replay.values()); N_OUT = sum(v['batches_outside'] for v in replay.values())
LABS_OUT = sum(v['batches_outside'] > 0 for v in replay.values())
OWN = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
HALF = e10['sensitivity']['split half: drift and effect from different DMSO wells']['drift_vs_agreement_with_own_baseline']
TWO = e10['flagged_against_unflagged']['source_2']['with_own_baseline']
FAILED = e11['failed']; FAILED_PLATES = sum(f['n_plates'] for f in FAILED); FAILED_LAB = 'lab ' + FAILED[0]['lab'].split('_')[1]
INT = sorted([g for g in e6['groups'] if g['measurement'] == 'Intensity'], key=lambda g: -abs(g['mean_shift']))
WEEKS = round((__import__('datetime').date.fromisoformat(OCT['date']) - __import__('datetime').date.fromisoformat(FLAG['date'])).days / 7)
BINS = {b['gap']: b for b in dr['bins']}; SAME, MID, FAR = BINS['same batch'], BINS['6 to 13 weeks'], dr['bins'][-1]
POOLED = e8['pooled_within_lab_and_compound']
WORDS = {7: 'seven', 9: 'nine', 11: 'eleven', 4: 'four'}


def swap(text, old, new):
    assert text.count(old) == 1, f'expected once: {old[:60]}'
    return text.replace(old, new)


def block(html, marker, new_inner, tags=('p', 'td', 'li', 'span', 'figcaption', 'th')):
    """Replace the inner HTML of the smallest listed element whose text contains marker."""
    i = html.find(marker)
    assert i >= 0, f'marker not found: {marker[:60]}'
    assert html.count(marker) == 1, f'marker not unique: {marker[:60]}'
    start = max(html.rfind(f'<{t}>', 0, i) for t in tags)
    start = max(start, max(html.rfind(f'<{t} ', 0, i) for t in tags))
    tag = re.match(r'<(\w+)', html[start:]).group(1)
    open_end = html.find('>', start) + 1
    close = html.find(f'</{tag}>', i)
    return html[:open_end] + new_inner + html[close:]


def drift_svg():
    F = 'font-family="Archivo, sans-serif"'; M = 'font-family="IBM Plex Mono, monospace"'
    W, H, x0, y0, w, h = 680, 260, 56, 14, 600, 170
    bins = dr['bins']; top = max(b['iqr'][1] for b in bins) * 1.1
    Y = lambda v: y0 + h - v / top * h
    X = lambda k: x0 + (k + 0.5) * w / len(bins)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Median distance between two plates of one lab against the time between their batches: it rises from {SAME["median"]} in the same batch to {FAR["median"]} {FAR["gap"]}, and does not level off." style="display:block;max-width:680px">',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="currentColor" opacity="0.06"/>']
    for v in range(0, int(top) + 1, 2):
        g.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x0 + w}" y2="{Y(v):.1f}" stroke="currentColor" opacity="0.15"/><text x="{x0 - 8}" y="{Y(v) + 4:.1f}" text-anchor="end" {M} font-size="13" fill="currentColor" opacity="0.7">{v}</text>')
    g.append('<path d="' + ' '.join(f'{"M" if k == 0 else "L"} {X(k):.1f} {Y(b["median"]):.1f}' for k, b in enumerate(bins)) + '" fill="none" stroke="#be1e74" stroke-width="2.4"/>')
    for k, b in enumerate(bins):
        g.append(f'<line x1="{X(k):.1f}" y1="{Y(b["iqr"][0]):.1f}" x2="{X(k):.1f}" y2="{Y(b["iqr"][1]):.1f}" stroke="#be1e74" stroke-width="2" opacity=".4"/>'
                 f'<circle cx="{X(k):.1f}" cy="{Y(b["median"]):.1f}" r="5" fill="#be1e74"/>'
                 f'<text x="{X(k) - 8:.1f}" y="{Y(b["median"]) - 10:.1f}" text-anchor="end" {F} font-weight="600" font-size="14" fill="#be1e74">{b["median"]}</text>'
                 f'<text x="{X(k):.1f}" y="{y0 + h + 18}" text-anchor="middle" {M} font-size="13" fill="currentColor">{b["gap"]}</text>'
                 f'<text x="{X(k):.1f}" y="{y0 + h + 35}" text-anchor="middle" {M} font-size="13" fill="currentColor" opacity="0.7">{b["n_pairs"]:,} pairs</text>')
    g.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="currentColor" opacity="0.6" stroke-width="1.5"/><line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="currentColor" opacity="0.6" stroke-width="1.5"/>'
             f'<text x="{x0 + w / 2}" y="{y0 + h + 58}" text-anchor="middle" {M} font-size="13" fill="currentColor">time between the two plates&#8217; batches</text>'
             f'<text transform="translate(14,{y0 + h / 2}) rotate(-90)" text-anchor="middle" {M} font-size="13" fill="currentColor">distance (spreads)</text></svg>')
    return ''.join(g)


def accuracy_svg():
    F = 'font-family="Archivo, sans-serif" font-weight="600" font-size="15"'; M = 'font-family="IBM Plex Mono, monospace" font-size="13"'
    rows = [('Raw, plates held out', full['balanced_accuracy'], '#be1e74', '#be1e74'),
            ('Permuted labels', rt['permuted']['balanced_accuracy'], '#b7bec1', 'currentColor'),
            ('Plate-centred', rt['plate_centred']['balanced_accuracy'], '#b7bec1', 'currentColor'),
            ('Plate-centred and scaled', rt['plate_scaled']['balanced_accuracy'], '#b7bec1', 'currentColor')]
    g = ['<svg viewBox="0 0 680 204" width="100%" role="img" aria-label="Lab identity accuracy under four conditions" style="display:block;max-width:680px">']
    for k, (name, v, fill, ink) in enumerate(rows):
        y = 18 + 40 * k; wd = 400 * v
        g.append(f'<text x="208" y="{y + 14}" text-anchor="end" {M} fill="currentColor">{name}</text><rect x="220" y="{y}" width="{wd:.1f}" height="20" rx="3" fill="{fill}"/>'
                 f'<text x="{228 + wd:.1f}" y="{y + 15}" {F} fill="{ink}">{pc(v, 1)}</text>')
    cx = 220 + 400 * full['chance']
    g.append(f'<line x1="{cx:.1f}" y1="10" x2="{cx:.1f}" y2="174" stroke="#0f8f6c" stroke-width="1.5" stroke-dasharray="4 3"/>'
             f'<text x="{cx:.1f}" y="192" text-anchor="middle" {M} fill="#0f8f6c">chance {CHANCE}</text></svg>')
    return ''.join(g)


# ------------------------------------------------------------------ judge Q&A
q = open(f'{SRC}/judge-qa.html').read()
q = block(q, 'Correction takes 96% to 12%', f'Centring a plate on its own controls takes {ACC} to {CENTRED}: it removes most of the coordinate a certificate needs.')
q = block(q, 'drift plateaus there. One institution so far', 'Every quarter at most. In one lab the baseline is stale within weeks and still moving after thirteen.')
q = block(q, 'because drift plateaus at about three months', '<strong>What does it cost?</strong> Per line, per quarter. The figure isn\'t set; the proof of concept sets it. The quarter is a starting cadence: in the one lab measured, a baseline is stale within weeks. <em>Board A11.</em>')
q = block(q, '3,781 measurements per well here', f'{FEAT} measurements per well here, aggregated from single cells.')
q = block(q, 'drops lab identity to 11.8% here', f'Typical Variation Normalization: PCA-whitening fit on control wells so that they become spherical. Not run here; centring each plate on its own controls takes lab identity to {CENTRED}.')
q = block(q, 'Average hit rate across the seven labs', f'Average hit rate across the {WORDS[LABS]} labs.')
q = block(q, 'chance is 1/K = 14.3% for K = 7', f'Mean per-class recall; chance is 1/K = {CHANCE} for K = {LABS}.')
q = block(q, 'Permuted-label balanced accuracy 15.2%', f'Permuted-label balanced accuracy {PERM} against {CHANCE} chance.')
q = block(q, 'then plateaus (one institution, 31 plates)', f'Distance between plate centroids grows with the time between batches and is still rising after thirteen weeks (one lab, {N_L2} plates).')
q = block(q, 'correction drops lab identity from 96% to 12%', f'<strong>Isn\'t this just batch effect? Everyone knows about that.</strong> Yes, and everyone removes it. The published JUMP benchmark tested ten correction methods and found Harmony best at removing it [5]. I\'m saying the thing being removed is a measurement of your lab\'s state. On our data, centring each plate on its own controls drops lab identity from {ACC} to {CENTRED} (white paper Fig. 1; board A3). On Monday, that\'s the coordinate a lab can no longer see.')
q = block(q, 'I can\'t separate them yet with seven labs', f'<strong>Couldn\'t it be the microscope, not the cells?</strong> Partly. The signature is the whole pipeline: instrument, staining, handling and cells. It is not the microscope model alone: the {WORDS[N_SCOPE]} labs on a CV8000 are told apart as well as all {WORDS[LABS]}, at {SCOPE}. Image-quality features alone also name the lab, so I say "the lab", not "the cells". What matters to a customer is that position predicts the answer: inside every lab, plates whose controls sit further from the field disagree more about the same compound (Spearman {POOLED["spearman"]:.2f}, shuffled {POOLED["null_mean"]:.2f}; results/e8-redteam).')
q = block(q, 'all 384 of its control wells classify as another institution', f'<strong>Why that lab? Is it representative?</strong> It\'s the clearest case, not the average. Lab 2 has {N_BATCH} batches across four months, so its drift can be followed. Its October batch has a normal cell count, {OCT["cells_per_well"]:.0f} per well, so no local rule fires, and sits {OCT["from_baseline"]:.1f} spreads from the lab\'s own June baseline against {OCT["to_nearest_other"]:.1f} from {NEAR}. Every one of its wells is still named lab 2: identity intact, position moved. Across the field, {N_OUT} of {N_ALL} batches are outside, in {LABS_OUT} labs. An earlier version of this deck said one plate\'s 384 wells classified as another lab. That did not reproduce and is withdrawn; all 384 are named lab 2 (analysis/README).')
q = block(q, '0 of 384 wells named as its own lab', '<strong>Surely a good lab catches this with its own QC?</strong> Only inside the box it can see. A control well catches a bad well. Plate-level QC catches a bad plate, as long as the rest of the plate is fine. Batch-level QC catches a bad batch against that lab\'s own history. Nothing inside a building catches the building: if the whole site has drifted, every local check passes, because every local reference drifted with it. That is what slide 05 shows on one real lab: cell counts in range from June to October, while its October plates sit further from its own June baseline than from another lab (white paper &#167;3). ML calls this domain shift and made it a benchmark with RxRx1 [4]. The reference has to sit outside every box.')
q = block(q, 'Is the 96% leakage?', f'<strong>Is the {ACC} leakage?</strong> Held out by plate, so no test plate was seen in training; holding out whole batches gives {BATCH}. Shuffle the labels and it scores {PERM} against {CHANCE} chance, so the chance line is real. Drop the two labs that use 1536-well plates and the remaining {WORDS[N_NO1536]} score {NO1536}, so it isn\'t plate format. Remove position and count features and nothing changes (results/e1-redteam).')
q = block(q, 'Raw z-scored features reach 96.2%', f'<strong>What\'s the metric, exactly?</strong> Balanced accuracy: mean recall across the {WORDS[LABS]} labs, so chance is one over {WORDS[LABS]}. Raw z-scored features reach {ACC}; centring each plate on its own controls drops that to {CENTRED}, and scaling as well to {SCALED} (white paper Fig. 1). For scale: the JUMP batch-correction benchmark scored ten such methods on this dataset [5].')
q = block(q, '12,046 vehicle wells, 7 institutions', f'{WELLS} untreated wells, {PLATES} plates, {LABS} labs, JUMP cpg0016, CC0')
q = block(q, '3,781 CellProfiler well-level features', f'{FEAT} CellProfiler well-level features, z-scored on the training folds')
q = block(q, 'balanced accuracy = mean recall over 7 labs', f'balanced accuracy = mean recall over {LABS} labs; chance 1/{LABS} = {CHANCE}')
assert q.count('<td>96.2%</td>') == 1
q = q.replace('<td>96.2%</td>', f'<td>{ACC}</td>')
q = block(q, 'permuted labels 15.2%; without the 1536-well source', f'permuted labels {PERM}; without the 1536-well labs {NO1536}; whole batches held out {BATCH}')
q = block(q, 'per-plate standardisation 14%; per-batch TVN whitening 11.8%', f'plate-centred {CENTRED}; plate-centred and scaled {SCALED} ({N_RT} wells)')
q = block(q, 'distance between runs grows from 0.74', f'<strong>How often?</strong> At least every quarter. In one lab\'s data, the distance between two plates grows from {SAME["median"]} in the same batch to {MID["median"]} at six to thirteen weeks and {FAR["median"]} beyond, and had not levelled off in four months (white paper Fig. 2; slide 05, click 3). An earlier version said it plateaus; on the full data it does not. It\'s one lab and {N_L2} plates, so it gets re-measured at every partner.')

# ------------------------------------------------------------------ whitepaper
w = open(f'{SRC}/whitepaper.html').read()
w = block(w, 'a classifier names the institution from untreated wells alone', 'Every result in cell biology is a difference from a control, and nothing checks the control against anyone else&#8217;s. '
          f'On the public JUMP Cell Painting dataset, a classifier names the lab from untreated wells alone {ACC} of the time against {CHANCE} chance, so &#8220;normal&#8221; is a lab-specific coordinate, not a shared one. '
          f'The normalisations that make cross-lab discovery possible erase that coordinate (centring each plate on its own controls drops lab identity to {CENTRED}): right for discovery, wrong for quality control. '
          'Datum Line keeps the coordinate and uses it. A lab&#8217;s control-well images are placed against the published field and every lab running the same line, and the lab gets back a certificate, a distance, and the direction of any shift. '
          'The bet still to be proven is that label-free brightfield carries the same signal as five-stain fluorescence; the test is specified and pending.')
i = w.find('<svg viewBox="0 0 680 204"'); j = w.find('</svg>', i) + 6
assert i >= 0
w = w[:i] + accuracy_svg() + w[j:]
w = block(w, 'Balanced accuracy naming one of 7 institutions', f'Balanced accuracy naming one of {LABS} labs from untreated JUMP wells; {WELLS} wells, {FEAT} features, plates held out. Normalisation and permutation tests on {N_RT} wells. results/e1, e1-redteam.')
i = w.find('<table><thead><tr><th>Plate 1053600681</th>'); j = w.find('</table>', i) + 8
assert i >= 0
w = w[:i] + ('<table><thead><tr><th>Lab 2, October 2021 batch</th><th>Result</th><th>File</th></tr></thead><tbody>'
             f'<tr><td>Cells per untreated well</td><td>{OCT["cells_per_well"]:.0f}; inside the lab&#8217;s range, no local QC rule fires</td><td>results/e2-timeline</td></tr>'
             f'<tr><td>Distance from the lab&#8217;s own June baseline</td><td><b class="acc">{OCT["from_baseline"]:.1f}</b> within-plate spreads</td><td>results/e2-timeline</td></tr>'
             f'<tr><td>Distance to the nearest other lab ({NEAR})</td><td>{OCT["to_nearest_other"]:.1f}</td><td>results/e2-timeline</td></tr>'
             f'<tr><td>Wells still named as their own lab</td><td>{pc(OCT["wells_named_own_lab"])}</td><td>results/e1</td></tr></tbody></table>') + w[j:]
w = block(w, 'yet every one of its 384 vehicle wells sits in another', '<b>Space.</b> The batch above passes the check its own lab runs, yet sits further from the lab&#8217;s own June baseline than from another lab&#8217;s centre. Local QC cannot see this by construction (section 1).')
i = w.find('<img src="data:image/svg+xml;base64,'); j = w.find('>', w.find('alt="Distance between two runs', i)) + 1
assert 0 <= i < j
w = w[:i] + drift_svg() + w[j:]
w = block(w, 'one institution, 31 plates, 8 runs, June to October', f'Median distance between plate centroids of one lab, in within-plate spreads, with the interquartile range; lab 2, {N_L2} plates, {N_BATCH} batches, June to October 2021. results/e1b-drift.')
w = block(w, 'grows from 0.74 for same-day pairs', f'<b>Time.</b> Within one lab, the distance between two plates grows from {SAME["median"]} in the same batch to {MID["median"]} at 6 to 13 weeks and {FAR["median"]} beyond. It had not levelled off in four months, so a lab&#8217;s own history stops being a valid comparison within weeks.')
w = w.replace('<sup>3781</sup>', f'<sup>{full["n_features"]}</sup>')
w = w.replace('does the lab leave a fingerprint (96.2%)', f'does the lab leave a fingerprint ({ACC})')
w = w.replace('the same 12,046 wells', f'the same {WELLS} wells')
w = w.replace('a permuted-label baseline at chance (15.2%)', f'a permuted-label baseline at chance ({PERM})')
w = w.replace('removal of the 1536-well source', 'removal of the 1536-well labs')
w = w.replace('seven institutions&#8217; U2OS controls', f'{WORDS[LABS]} labs&#8217; U2OS controls')
w = block(w, 'set by the drift plateau', '<b>Price.</b> Per line, per quarter, as a starting cadence; the drift measured so far argues for more often. The figure is not yet set. <b>What leaves the building:</b> untreated control-well images only; no compounds, targets or results.')
w = w.replace('Brightfield near 14% chance', f'Brightfield near {pc(full["chance"])} chance')

# ------------------------------------------------------------------ brand
b = open(f'{SRC}/brand.html').read()
b = b.replace('96.2% &#183; CHANCE 14.3% &#183; n = 12,046', f'{ACC} &#183; CHANCE {CHANCE} &#183; n = {WELLS}').replace('96.2% · CHANCE 14.3% · n = 12,046', f'{ACC} · CHANCE {CHANCE} · n = {WELLS}')
b = b.replace('96% of untreated wells name their own lab; chance is 14%', f'{ACC} of untreated wells name their own lab; chance is {pc(full["chance"])}')
# ------------------------------------------------------------------ landscape, roadmap, product vision
l = open(f'{SRC}/landscape.html').read()
l = swap(l, "seven institutions' U2OS controls", f"{WORDS[LABS]} labs' U2OS controls")
l = swap(l, 'Slide 06 shows whitening drops lab identity from 96% to 12%', f'Appendix A3 shows that centring a plate on its own controls drops lab identity from {ACC} to {CENTRED}')
l = swap(l, "the 96% can't yet separate them", f'partly: every feature family names the lab, but labs on one microscope model are still told apart ({SCOPE})')
l = swap(l, 'one institution, 31 plates', f'one lab, {N_L2} plates, and drift still rising at four months')
r = open(f'{SRC}/roadmap.html').read()
r = swap(r, 'brightfield near 14% chance', f'brightfield near {pc(full["chance"])} chance')
r = swap(r, 'the quarter comes from the measured drift plateau', 'the quarter is a starting cadence, and the drift measured so far argues for more often')
r = swap(r, 'not the 96%', f'not the {ACC}')
v = open(f'{SRC}/product-vision.html').read()
v = swap(v, 'The quarter is not arbitrary: drift plateaus near three months, so one reading covers its useful life.', 'The quarter is a starting cadence: in the one lab measured, a baseline is stale within weeks.')

# ------------------------------------------------------------------ the replay, what moved, the answer, the known answer
minus = lambda x, d=2: f'&#8722;{abs(x):.{d}f}'
INT_LINE = (f'{INT[0]["channel"]} and {INT[1]["channel"]} stain intensity up {INT[0]["mean_shift"]:.1f} and {INT[1]["mean_shift"]:.1f} '
            f'standard deviations, {INT[2]["channel"]} up {INT[2]["mean_shift"]:.1f}')
HELD = ', '.join(str(x['n_plates']) for x in FLAGGED[:-1]) + f' and {FLAGGED[-1]["n_plates"]}'
FLAG_DAY = f"{int(FLAG['date'][8:])} August"

q = swap(q, "<td>Positive controls certify the assay; JUMP plates carry eight.</td>",
         f"<td>In {FAILED_LAB}, {len(FAILED)} batches, {FAILED_PLATES} plates: the positive controls show no effect. Untreated wells cannot see that.</td>")
q = swap(q, "<td>That's e8, pending; if not, the pitch narrows to QC.</td>",
         f"<td>Yes. Inside labs, drift predicts how far a drug's answer moves: &#961; = {minus(OWN['spearman'])}, {OWN['n_batches']} batches.</td>")
q = swap(q, "<td>Why would a lab upload?</td>\n<td>Useful on day one against JUMP; better with every lab.</td>\n<td>A11</td>",
         "<td>Why would a lab upload?</td>\n<td>Useful on day one against JUMP; better with every lab.</td>\n<td>06, 08</td>")
q = swap(q, "<td>What does the money build?</td>\n<td>A reference built to break, graded against planted failures.</td>\n<td>A12</td>\n</tr>",
         "<td>What does the money build?</td>\n<td>A reference built to break, graded against planted failures.</td>\n<td>09</td>\n</tr>\n"
         f"<tr>\n<td>Would it cry wolf?</td>\n<td>{N_OUT} of {N_ALL} batches flag, in {LABS_OUT} of {LABS} labs. Same verdict under nine of ten variants.</td>\n<td>A11</td>\n</tr>\n"
         f"<tr>\n<td>What moved?</td>\n<td>{INT[0]['channel']} and {INT[1]['channel']} stain intensity, up {INT[0]['mean_shift']:.1f} and {INT[1]['mean_shift']:.1f} sd. Cell count did not.</td>\n<td>A12</td>\n</tr>")
q = swap(q, '<em>Board A12.</em>', '<em>Slide 09.</em>')
q = swap(q, '<em>Board A11.</em>', '<em>Slide 08.</em>')
q = swap(q, "<h2>Machine learning</h2>",
         f"<p><strong>Would it have caught anything real?</strong> Yes, in hindsight, on public data. I replayed lab 2's {N_BATCH} batches as uploads, "
         f"each judged with only what was known that day. The first sets the baseline and the next {N_BATCH - len(FLAGGED) - 1} come back in distribution. The batch of {FLAG_DAY} comes back outside, and so do the next two: "
         f"{WEEKS} weeks before the October batch was run. The flagged batches' cell counts sit inside the lab's own range. "
         f"The flagged batches hold {HELD} plates, and every one of those plates is outside (slide 06; board A11).</p>\n"
         f"<p><strong>Would it cry wolf?</strong> Across the field, {N_OUT} of {N_ALL} batches flag, in {LABS_OUT} of {LABS} labs; "
         f"{LABS - LABS_OUT} labs never flag. For lab 2 the verdicts are identical under nine of ten variants: a different baseline, no clipping, "
         f"cell-level features only, image-level features only, all-vehicle plates removed, the nearest labs removed. "
         f"The one that changes them is a baseline that takes in the June batch whose cell count fell (board A11).</p>\n"
         f"<p><strong>Does the flag matter to my results?</strong> Yes. For every batch of every lab I measured how well its effect of the shared positive controls "
         f"agrees with the same lab's first batch. Inside labs, the further a batch has drifted the less it agrees: Spearman {minus(OWN['spearman'])} over "
         f"{OWN['n_batches']} batches in {OWN['n_labs']} labs, against {minus(OWN['null_mean'])} when batches are shuffled inside their lab, and {minus(HALF['spearman'])} "
         f"when drift and drug effect are measured on different wells. Lab 2's agreement with its own June answer is {TWO['unflagged']:.2f} before the flag and "
         f"{TWO['flagged']:.2f} after (slide 05, click 4). In lab 2 the flagged batches are also the last three, so inside that one lab the flag and the calendar "
         f"cannot be separated; the correlation uses every lab.</p>\n"
         f"<p><strong>What moved?</strong> On {FLAG_DAY}: {INT_LINE}, with nearly every intensity feature moving the same way. Cell count did not move. "
         f"Image-level features carry {pc(e6['share_of_displacement']['by_level']['image'])} of the shift and are {pc(e6['share_of_features']['image'])} of the features, "
         f"so it is not confined to acquisition. That says where to look first, staining and exposure; it does not say why (board A12).</p>\n"
         f"<p><strong>Do you need shared positive controls?</strong> Not to place a lab; untreated wells do that. To know the assay answers at all, yes, and the field "
         f"already carries them. In {FAILED_LAB}, {len(FAILED)} consecutive batches, {FAILED_PLATES} plates, the wells the public plate map labels as positive controls "
         f"show no effect, and no other well on those plates does. The untreated-well certificate flagged only "
         f"{sum(1 for f in FAILED if any(x['batch'] == f['batch'] and x['verdict'] == 'outside' for x in replay[f['lab']]['batches']))} of those {len(FAILED)} batches. "
         f"Two checks, two kinds of failure. I do not know whether the compounds were left out or the map is wrong; the data cannot say (board A8).</p>\n"
         "<h2>Machine learning</h2>")

w = swap(w, '<p><b>Why correction is not the answer.</b>',
         f'<p><b>Replay.</b> Every batch of every lab was replayed as an upload and judged against the published field, each lab scaled on the other ten. '
         f'A plate is outside when it sits further from its lab&#8217;s own first batch than from the nearest other lab&#8217;s centre. {N_OUT} of {N_ALL} batches '
         f'are outside, in {LABS_OUT} of {LABS} labs. In lab 2 the first is {FLAG_DAY} 2021, {WEEKS} weeks before the October batch; its cell count is inside the '
         f'lab&#8217;s own range. Lab 2&#8217;s verdicts are unchanged under nine of ten variants of the analysis (results/e9).</p>\n'
         f'<p><b>What moved.</b> The distance is a difference of two means, so it reads feature by feature. On {FLAG_DAY}: {INT_LINE}. '
         f'Cell-level features carry {pc(e6["share_of_displacement"]["by_level"]["cell"])} of the shift. Profiles cannot tell a stain lot from biology; '
         f'they say where to look (results/e6).</p>\n'
         f'<p><b>Does it matter.</b> JUMP runs the same positive controls on every compound plate. Inside labs, the further a batch has drifted from its lab&#8217;s '
         f'baseline, the less its measured drug effects agree with that baseline: Spearman {minus(OWN["spearman"])}, {OWN["n_batches"]} batches, {OWN["n_labs"]} labs, '
         f'{e10["n_plates"]:,} plates; {minus(OWN["null_mean"])} when batches are shuffled inside their lab; {minus(HALF["spearman"])} when drift and effect use '
         f'different wells (results/e10).</p>\n'
         f'<p><b>The known answer.</b> In {FAILED_LAB}, {len(FAILED)} consecutive batches, {FAILED_PLATES} plates, the wells the public plate map labels as positive '
         f'controls show no effect, and no other well on those plates does. Untreated wells cannot see this, which is why a certificate has two halves '
         f'(results/e11).</p>\n<p><b>Why correction is not the answer.</b>')
w = swap(w, 'Four claims are not yet proven, and each has a named test that could fail.', 'Each claim has a named test that could fail. Two have now been run.')
w = swap(w, 'Spearman near zero: cells differ but answers do not</td><td><span class="pend">pending</span></td>',
         f'Spearman near zero: cells differ but answers do not</td><td>run: {minus(OWN["spearman"])} inside labs; across {LABS} labs the sign agrees and the count is too small</td>')
w = swap(w, 'Nearly all variance in <span class="m">V<sub>model</sub></span>: a calibration product</td><td><span class="pend">pending</span></td>',
         f'Nearly all variance in <span class="m">V<sub>model</sub></span>: a calibration product</td><td>in part: {WORDS[N_SCOPE]} labs on one microscope model '
         f'separate at {SCOPE}; decomposition pending</td>')
w = swap(w, 'Unbounded drift elsewhere: no stable reference</td><td>one site</td>', 'Unbounded drift elsewhere: no stable reference</td><td>one lab; still rising at four months</td>')
w = swap(w, 'Variance decomposition, microscope model separated from site', 'Variance decomposition, microscope model separated from lab')
w = swap(w, 'Repeat e1b at each partner site', 'Repeat e1b at each partner lab')
w = swap(w, 'Does drift generalize beyond one institution?', 'Does drift generalize beyond one lab?')
w = swap(w, 'Results files (results/e1, e1b, e8)', 'Results files (results/, produced by the scripts in analysis/)')
r = swap(r, 'if e8 shows cells differ but answers do not, the pitch narrows to QC', 'e8 and e10 now show that answers move with position, so the pitch is not QC alone')

# write only once every replacement has succeeded, so a failed run leaves the documents untouched
for path, text in (('docs/judge-qa.html', q), ('docs/whitepaper.html', w), ('docs/brand.html', b),
                   ('docs/landscape.html', l), ('docs/roadmap.html', r), ('docs/product-vision.html', v)):
    open(path, 'w').write(text)
print('documents rebuilt:', ACC, CHANCE, WELLS, CENTRED, SCALED, PERM, BATCH, SCOPE)
