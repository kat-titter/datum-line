"""Write the public documents from results/*.json: whitepaper, brand, landscape, roadmap and
product vision. The documents as first published are kept in figures/assets/docs-original;
this reads those and writes docs/, so it can be run again after any analysis changes.
Every number is read from results/*.json. Run from the repository root.

Usage:  python figures/build_docs.py
"""
import json
import re

from parts import dmso_words  # one wording for the control wells
from appendix import MARKET, PRESEED, MULTIPLIER, market, preseed_total   # the proposed prices and the plan, one source with the deck

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
e12 = json.load(open(f'{R}/e12-field-normalization.json'))
e13 = json.load(open(f'{R}/e13-baseline-density.json'))
GRID = [json.load(open(f)) for f in sorted(__import__('glob').glob(f'{R}/e12-field-normalization-*.json'))]
LB = json.load(open(f'{R}/e14-leaderboard.json'))

pc = lambda x, d=0: f'{100 * x:.{d}f}%'
price_range = lambda key: f'${MARKET[key][0]}&#8211;{MARKET[key][2]}k'     # a proposed price, low to high, as board A15 shows it
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
FAILED_FLAGGED = sum(b['verdict'] == 'outside' for b in replay[FAILED[0]['lab']]['batches'] if b['batch'] in {f['batch'] for f in FAILED})
INT = sorted([g for g in e6['groups'] if g['measurement'] == 'Intensity'], key=lambda g: -abs(g['mean_shift']))
WEEKS = round((__import__('datetime').date.fromisoformat(OCT['date']) - __import__('datetime').date.fromisoformat(FLAG['date'])).days / 7)
BINS = {b['gap']: b for b in dr['bins']}; SAME, MID, FAR = BINS['same batch'], BINS['6 to 13 weeks'], dr['bins'][-1]
POOLED = e8['pooled_within_lab_and_compound']
WORDS = {4: 'four', 5: 'five', 6: 'six', 7: 'seven', 9: 'nine', 11: 'eleven'}


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



E17 = json.load(open('results/e17-same-labs-every-input.json'))   # every input on the same labs, wells and split
# ------------------------------------------------------------------ whitepaper
w = open(f'{SRC}/whitepaper.src.html.txt').read()
w = block(w, 'a classifier names the institution from untreated wells alone', 'Every result in cell biology is a difference from a control, and nothing checks the control against anyone else&#8217;s. '
          f'On the public JUMP Cell Painting dataset, a classifier names the lab from untreated wells alone {ACC} of the time against {CHANCE} chance, so &#8220;normal&#8221; is a lab-specific coordinate, not a shared one. '
          f'The normalisations that make cross-lab discovery possible erase that coordinate (centring each plate on its own controls drops lab identity to {CENTRED}): right for discovery, wrong for quality control. '
          'Datum Line keeps the coordinate and uses it: one shared repository of every lab&#8217;s raw control images, placed on one map against the published field and every lab running the same line. '
          'A lab that shares its controls joins free and gets back, on every batch, its distance from the field and the direction of any shift; teams that use the data join as members, '
          'screening teams per cell line and AI teams by API, and each lab keeps a share. '
          f'The bet is label-free brightfield. On the same {E17["population"]["n_labs"]} labs, wells and held-out batches, one brightfield image names the lab {100 * E17["inputs"]["brightfield"]["median_over_splits"]:.1f}% of the time (median of {len(E17["paired_splits"]["deal_seeds"])} splits), '
          f'and the six-dye profile of those wells {100 * E17["inputs"]["profile"]["median_over_splits"]:.1f}% (results/e17); placing a picture on the map is not yet shown.')
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
w = block(w, 'set by the drift plateau', '<b>Membership.</b> The product is a membership to the repository: access for a period, not ownership of the data. A lab that shares its control wells joins free '
          'and keeps a share of every membership for as long as its data is used. Screening teams pay first, '
          f'{price_range("price per line per quarter, $k")} per cell line per quarter, for a check on every batch; AI teams pay the most, by use, for aligned raw images from every lab '
          f'through an API; companies that buy cell data pay {price_range("price per dataset membership, $k")} per dataset placed on the map. Prices are proposals until the first '
          'partner labs and members set them. <b>What is shared:</b> untreated control-well images only; no compounds, targets or results. A company that also '
          'backs up its raw images with us, free, keeps them encrypted with its own key: the copy cyber insurers ask for, which nobody else can read (proposed).')
w = w.replace('Brightfield near 14% chance', f'Brightfield near {pc(full["chance"])} chance')

# ------------------------------------------------------------------ brand
b = open(f'{SRC}/brand.src.html.txt').read()
b = b.replace('96.2% &#183; CHANCE 14.3% &#183; n = 12,046', f'{ACC} &#183; CHANCE {CHANCE} &#183; n = {WELLS}').replace('96.2% · CHANCE 14.3% · n = 12,046', f'{ACC} · CHANCE {CHANCE} · n = {WELLS}')
b = b.replace('96% of untreated wells name their own lab; chance is 14%', f'{ACC} of untreated wells name their own lab; chance is {pc(full["chance"])}')
b = swap(b, 'Dark slides (05, 06) use ink', 'Dark slides (04, 05, 06, 07) use ink')
b = swap(b, 'eight dashes bottom left, 10 × 4', 'ten dashes bottom left, 9 × 4')
b = swap(b, '"It passed every check", not "Plate-level QC"', '"Eleven labs. Eleven normals.", not "Inter-laboratory variation"')
b = swap(b, 'a stamp for the certificate', 'a pin for a place on the map, a receipt for a membership')       # the path icons of slides 06 and 10 (parts.PATH_ICONS)
# ------------------------------------------------------------------ landscape, roadmap, product vision
l = open(f'{SRC}/landscape.src.html.txt').read()
l = swap(l, 'This is slide 07 as a table', 'This is slide 08 as a table')
l = swap(l, "slide 03's bug", "board A1's bug")
l = swap(l, "seven institutions' U2OS controls", f"{WORDS[LABS]} labs' U2OS controls")
l = swap(l, 'Slide 06 shows whitening drops lab identity from 96% to 12%', f'Appendix A3 shows that centring a plate on its own controls drops lab identity from {ACC} to {CENTRED}')
l = swap(l, "the 96% can't yet separate them", f'partly: every feature family names the lab, but labs on one microscope model are still told apart ({SCOPE})')
l = swap(l, 'one institution, 31 plates', f'one lab, {N_L2} plates, and drift still rising at four months')
_m = lambda k: f'${k / 1000:.1f}M'.replace('.0M', 'M') if k >= 1000 else f'${k}k'
_low, _base, _high = (market(i) for i in range(3))
_sub, _total = preseed_total()
_rows = ''.join(f'<tr><td>{k}</td><td>{r[0]:,}</td><td>{r[1]:,}</td><td>{r[2]:,}</td></tr>' for k, r in MARKET.items())
_out = (f'<tr><th>Per-line checks and site licences, per year</th><th>{_m(_low[0])}</th><th>{_m(_base[0])}</th><th>{_m(_high[0])}</th></tr>'
        f'<tr><th>Dataset memberships on purchased data, per year</th><th>{_m(_low[1])}</th><th>{_m(_base[1])}</th><th>{_m(_high[1])}</th></tr>'
        f'<tr><th>Benchmark membership, per year</th><th>{_m(_low[2])}</th><th>{_m(_base[2])}</th><th>{_m(_high[2])}</th></tr>'
        f'<tr><th>Serviceable, per year, at full adoption</th><th>{_m(sum(_low))}</th><th>{_m(sum(_base))}</th><th>{_m(sum(_high))}</th></tr>')
_cost = ''.join(f'<tr><td>{n.replace(" (me)", "")}</td><td>{w}</td><td>${k}k</td></tr>' for n, w, k in PRESEED)   # the doc is not in Kat's voice
l = swap(l, '<h2>Risks and answers</h2>', f"""<h2>The market, bottom up</h2>
<p>No public count exists of organisations running high-content imaging on cell lines, so the model below starts from assumptions and says so. What the public record gives: the high-content screening market is reported at about US$1.8B in 2025 by one analyst and US$3.4B in 2024 by another, with instruments the largest segment [L1, L2]; the JUMP consortium that produced the public map was ten pharmaceutical companies, the Broad Institute and Ksilink, with six supporting technology companies [L3]; and a 2024 systematic review traces a decade of Cell Painting adoption across academia and industry without a count of sites [L4]. At a few hundred thousand dollars per system and a five-to-seven-year life, the instrument revenue alone implies an installed base in the thousands of systems. The first row below is therefore conservative: it counts organisations that screen continuously on cell lines, not every core that owns an instrument. Labs come in two kinds: some run a few lines deep (a primary line and a co-culture, say), some run panels of hundreds to thousands of genotypes wide. A price per line fits the first; a site licence fits the second; both are rows. Cores and academic labs are free in this model; they are the map, not the revenue.</p>
<div class="tw"><table><thead><tr><th>Assumption</th><th>Low</th><th>Base</th><th>High</th></tr></thead><tbody>{_rows}{_out}</tbody></table></div>
<p>A tenth of the base case is about {_m(sum(_base) // 10)} a year, the five-year bar. The anchor on the value side is one screen run on cells that had moved: about US$2.6M of work to redo. Prices are the proposal in the business model section; the two rows that matter most, organisations and lines per organisation, are replaced by counts from the first three partner labs and from the instrument installed base as soon as either exists. The same table is board A22 in the deck.</p>
<h2>What the plan costs</h2>
<p>Eighteen months, planned line by line and asked at {MULTIPLIER}&#215;, on the rule that most things take two to three times the time and money they should. Planned ${_sub / 1000:.1f}M; asked about ${_total / 1000:.1f}M. No lab of our own: partner labs image the controls they already take, and the benchmark runs where the cells already are or at a CRO. The benchmark playground is inside the plan as milestone three, not a later round. Board A21 in the deck carries the same lines.</p>
<div class="tw"><table><thead><tr><th>Line</th><th>What</th><th>Planned</th></tr></thead><tbody>{_cost}<tr><th>As planned</th><th></th><th>${_sub / 1000:.2f}M</th></tr><tr><th>Asked, at {MULTIPLIER}&#215;</th><th></th><th>${_total / 1000:.2f}M</th></tr></tbody></table></div>
<h2>Partner labs</h2>
<p>No partner lab is named until an agreement is public. U2OS is the on-ramp to the public map; a lab on any other line starts that line's map from its first batch, and it becomes a cross-lab map when a second lab on the same line joins.</p>
<h2>Risks and answers</h2>""")
l = swap(l, '</ol></main></body></html>', """<li id="L1">High Content Screening Market Size, Share and Forecast 2034. Credence Research. credenceresearch.com/report/high-content-screenings-market</li>
<li id="L2">High Content Screening/Imaging: Technologies and Global Markets. BCC Research. bccresearch.com/market-research/biotechnology/high-content-screening-imaging-technologies-and-global-markets.html</li>
<li id="L3">Broad Institute launches academic-industry cell imaging consortium to speed drug discovery and development. Broad Institute press release. broadinstitute.org/node/631466</li>
<li id="L4">Seal S, et al. A Decade in a Systematic Review: The Evolution and Impact of Cell Painting. arXiv:2405.02767, 2024.</li>
</ol></main></body></html>""")
r = open(f'{SRC}/roadmap.src.html.txt').read()
r = swap(r, 'brightfield near 14% chance', f'brightfield near {pc(full["chance"])} chance')
r = swap(r, 'the quarter comes from the measured drift plateau', 'the quarter is a starting cadence, and the drift measured so far argues for more often')
r = swap(r, 'not the 96%', f'not the {ACC}')
# the vision looks for its own leader; Kat would build the science, not run the company
r = swap(r, 'founder at a below-market salary; four hires', 'a leader and a scientific lead at below-market salaries; four hires')
r = swap(r, "You hold science, product and the pitch; the first hire covers what phase 0 needs most and may be worth a cofounder's equity.",
         'A leader comes before any of them, someone to run the company. You hold the science; the first hire covers what phase 0 needs most.')
r = swap(r, 'A CEO hire, a sales team, or a wet lab of your own:', 'A sales team or a wet lab of your own:')
r = swap(r, '<td>First hire as cofounder or employee</td>\n<td>more equity given</td>\n<td>a partner on the riskiest phase</td>\n<td>cofounder, if the fit is there</td>',
         '<td>Who leads it</td>\n<td>the lead, and its equity</td>\n<td>someone whose job is to run it, while you build the science</td>\n<td>a leader, or a home that already has one</td>')
# 26 Oct 2026 (Kat: "open issues: close them"): the roadmap asks what the deck asks, the pre-seed of A21 (appendix.PRESEED at
# twice its planned cost, 18 months to a first paid certificate); the $3M round after the kill tests stays as option B
_sub, _total = preseed_total(); ASK = f'${_total / 1000:.1f}M'
r = swap(r, 'Once they pass, raise about <strong>$3M on a post-money SAFE</strong> to fund 24 months: four early hires, a three-site proof, and the reference built to break.',
         f'Then raise about <strong>{ASK} for 18 months</strong>, the deck&#8217;s pre-seed, to the first paying members and the seed: a leader, '
         f'an ML engineer, three partner labs and the benchmark playground, a ${_sub}k plan with an equal contingency.')
r = swap(r, 'pre-seed ~$3M SAFE &#183; 24 months', f'pre-seed ~{ASK} &#183; 18 months')
r = swap(r, 'Recommendation: about $3M on a post-money SAFE, raised right after phase 0 passes, to fund 24 months through phase 2.</strong> Run the kill tests first (weeks, not months, and nearly free), then raise on evidence instead of a hypothesis.',
         f'Recommendation: about {ASK}, the deck&#8217;s pre-seed, to fund 18 months to the first paying members and the seed.</strong> The kill tests '
         f'run first on public data; the round buys three partner labs, a paid pilot with a screening lab by month 9, the benchmark playground and a '
         f'model for any cell. The product is a membership to the repository: labs join free by uploading, screening teams and AI teams subscribe; '
         f'biotech companies come in through a free, private backup of their raw images.')
r = swap(r, 'So $3M sits just above the squeezed middle while keeping the simpler instrument.',
         f'So {ASK} sits in the squeezed middle and is raised on what the public map already shows; about $3M is the size to choose if the '
         f'kill tests land before the round.')
r = swap(r, '<td>A · Small pre-seed</td>\n<td>\\~$1.5M</td>\n<td>now</td>\n<td>least dilution</td>\n<td>lands in the thinning middle [1]; runs out mid phase 1</td>',
         f'<td><strong>A · Pre-seed now, the deck&#8217;s ask</strong></td>\n<td><strong>\\~{ASK}</strong></td>\n<td><strong>now</strong></td>\n'
         f'<td><strong>18 months to the first paying members</strong></td>\n<td><strong>lands in the thinning middle [1]</strong></td>')
r = swap(r, '<td><strong>B · Pre-seed after kill tests</strong></td>\n<td><strong>\\~$3M</strong></td>\n<td><strong>month 2–3</strong></td>\n'
            '<td><strong>priced on evidence; covers phases 1–2</strong></td>\n<td><strong>2–3 months of runway from savings or a grant</strong></td>',
         '<td>B · Pre-seed after kill tests</td>\n<td>\\~$3M</td>\n<td>month 2–3</td>\n<td>priced on evidence; covers phases 1–2</td>\n'
         '<td>2–3 months of runway from savings or a grant</td>')
_a = r.index('<p>Two thirds of the money is people;'); _b = r.index('<p>The order matters more than the split', _a)
_people = sum(k for _, _, k in PRESEED[:4])
r = (r[:_a] + f'<p>About {round(100 * _people / _sub)}% of the money is people; the benchmark playground and the partner labs are the lines that buy '
     f'the moat. Each line is the plan; the contingency below it doubles the plan (estimates, not offers).</p>\n<div class="tw"><table>\n<thead>\n<tr>\n'
     f'<th>Line</th>\n<th>18 months</th>\n<th>Share</th>\n<th>What it buys</th>\n</tr>\n</thead>\n<tbody>\n'
     + ''.join(f'<tr>\n<td>{name}</td>\n<td>${k}k</td>\n<td>{round(100 * k / _sub)}%</td>\n<td>{what}</td>\n</tr>\n' for name, what, k in PRESEED)
     + f'<tr>\n<td>contingency</td>\n<td>${_total - _sub}k</td>\n<td>+100%</td>\n<td>most things take two to three times the time and money planned; we plan for {MULTIPLIER}&#215;</td>\n</tr>\n'
     + f'<tr>\n<td><strong>Total</strong></td>\n<td><strong>\\~{ASK}</strong></td>\n<td></td>\n'
       f'<td>${_sub}k plan + ${_total - _sub}k contingency</td>\n</tr>\n</tbody>\n</table></div>\n' + r[_b:])
r = swap(r, 'A leader comes before any of them, someone to run the company. You hold the science; the first hire covers what phase 0 needs most.',
         'A leader comes before any of them, someone to run the company. The pre-seed pays for the leader and the first hire, the ML engineer from '
         'month 7; the other three come with the seed. You hold the science.')
r = swap(r, '<td>Founding ML engineer</td>\n<td>month 0–2</td>', '<td>Founding ML engineer</td>\n<td>month 7</td>')
r = swap(r, '<td>Assay and imaging scientist</td>\n<td>month 3</td>', '<td>Assay and imaging scientist</td>\n<td>with the seed</td>')
r = swap(r, '<td>Data platform engineer</td>\n<td>month 9</td>', '<td>Data platform engineer</td>\n<td>with the seed</td>')
r = swap(r, '<td>Partnerships lead</td>\n<td>month 12 (fractional first)</td>', '<td>Partnerships lead</td>\n<td>with the seed (fractional first)</td>')
r = swap(r, '<td>24 months of runway</td>', '<td>18 months of runway</td>')
v0 = open(f'{SRC}/product-vision.src.html.txt').read()     # head, mast and the habit sections; the rest is written below

# ------------------------------------------------------------------ one frame, and how dense
E12 = e12['every_batch']; BETWEEN, MARGIN, SELF = E12['agree_field'], E12['margin'], E12['agree_own']
USUAL = 'own' if 'own' in BETWEEN else 'scaled'          # the usual normalisation to a batch's own controls
CV = E12['effect_size_cv_across_batches_within_lab']
REF = e13['field_reference_by_labs']; REF_1, REF_N = REF[min(REF, key=int)], REF[max(REF, key=int)]
REF_LABS = max(REF, key=int)
PLATES_1, PLATES_8 = e13['own_baseline_by_plates']['1'], e13['own_baseline_by_plates']['8']
LEAVES = e13['reference_moves_when_one_lab_leaves']
better = lambda v: int(v['field_better_in'].split()[0])
KS = ', '.join(str(g['k']) for g in GRID if g['k'] != e12['k'])
SHRINKS = ' or '.join(format(g['shrink'], 'g') for g in GRID if g['shrink'] != e12['shrink'])
WINS = [int(g['every_batch']['agree_field']['field_better_than_own_in'].split()[0]) for g in GRID]
HOLDS = f"With {KS} components or shrinkage of {SHRINKS}, the frame is above own controls in {min(WINS)} to {max(WINS)} of {E12['n_batches']} batches." if GRID else ''

# ------------------------------------------------------------------ the replay, what moved, the answer, the known answer
minus = lambda x, d=2: f'&#8722;{abs(x):.{d}f}'
INT_LINE = (f'{INT[0]["channel"]} and {INT[1]["channel"]} stain intensity up {INT[0]["mean_shift"]:.1f} and {INT[1]["mean_shift"]:.1f} '
            f'standard deviations, {INT[2]["channel"]} up {INT[2]["mean_shift"]:.1f}')
HELD = ', '.join(str(x['n_plates']) for x in FLAGGED[:-1]) + f' and {FLAGGED[-1]["n_plates"]}'
FLAG_DAY = f"{int(FLAG['date'][8:])} August"


w = swap(w, '<p><b>Why correction is not the answer.</b>',
         f'<p><b>One frame.</b> The same measurement that places a lab can move it. Each batch&#8217;s untreated wells are mapped onto the field&#8217;s mean and '
         f'covariance, built without that lab, in {e12["k"]} principal components, and the same map is applied to the treated wells. On the positive controls, agreement '
         f'with every other lab rises from {BETWEEN["raw"]:.2f} to {BETWEEN["field"]:.2f}, in {BETWEEN["field_better_in"]} batches; the margin over the wrong compound '
         f'rises in {MARGIN["field_better_in"]}, so the map does not make every compound look alike. Normalised to the batch&#8217;s own controls, the usual practice, agreement is '
         f'{BETWEEN[USUAL]:.2f}, and the frame is above that in {BETWEEN["field_better_than_own_in"]} batches. The gain is between labs: agreement with a lab&#8217;s own first batch is unchanged ({SELF["raw"]:.2f}, {SELF["field"]:.2f}) and the '
         f'spread of effect size between batches of a lab is {CV["raw"]:.2f} as measured, {CV["own"]:.2f} on own controls and {CV["field"]:.2f} in the frame (results/e12).</p>\n'
         f'<p><b>Density.</b> Two references built from one lab each sit {REF_1["mean"]:.1f} within-plate spreads apart; from {REF_LABS} labs each, {REF_N["mean"]:.1f}, '
         f'close to one over root n. A lab&#8217;s own baseline settles by eight plates ({PLATES_1["mean"]:.2f} to {PLATES_8["mean"]:.2f}). The reference is what '
         f'tightens with every lab that joins (results/e13).</p>\n'
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
         f'controls show no effect, and no other well on those plates does. Untreated wells flagged only {FAILED_FLAGGED} of those {len(FAILED)} batches, which is why the check has two halves '
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

# ------------------------------------------------------------------ 26 Oct (Kat: "certificate is weak product. product is really subscription/membership to data repo")
# the white paper and roadmap sell a membership to the repository; the per-batch check is what members use. A vendor's
# certificate of analysis is someone else's product and keeps its name.
w = swap(w, '3 &#183; Certificate distance', '3 &#183; Distance to the field')
w = swap(w, '<p>The certificate is a difference of two means', '<p>The check is a difference of two means')
w = swap(w, 'chance: the certificate needs one stain', 'chance: the check needs one stain')
w = swap(w, '<span class="num">6</span>Industry position</h2>', '<span class="num">6</span>The repository and its members</h2>')
w = swap(w, 'Datum Line is the behaviour half, held by nobody who sells cells, media or instruments.</p>',
         'Datum Line is the behaviour half: one repository of every lab&#8217;s control images, held by nobody who sells cells, media or instruments, and joined as a member.</p>')
w = block(w, '<b>Who pays.</b>', '<b>Who joins.</b> Academic labs and cores share their control wells and join free, on every new line (at stake: the paper). Pharma and CRO screening '
          'teams join first as paying members, for a check on every batch and every transfer (at stake: the screen; one line checked late cost about $2.6M in the author&#8217;s '
          'experience: 3 runs a week for 17 weeks at about $50k a run). AI teams join by API, for aligned raw images from every lab, and pay the most. Cell banks and vendors '
          'join for every lot they ship (at stake: the lot and every lab that bought it).')
w = swap(w, 'so the first customer is compared with the field', 'so the first member is compared with the field')
w = swap(w, 'Every upload widens the reference, and', f'Every lab that shares tightens the reference (two references built from one lab each sit {REF_1["mean"]:.1f} '
         f'within-plate spreads apart; from {REF_LABS} labs each, {REF_N["mean"]:.1f}; results/e13), and')
w = swap(w, '<b style="color:#be1e74">Certificate</b><span>U2OS vs JUMP</span>', '<b style="color:#be1e74">Map and check</b><span>U2OS vs JUMP</span>')
w = swap(w, '<b style="color:#14171a">3-site proof</b><span>protocol advice</span>', '<b style="color:#14171a">3-site proof</b><span>first paying members</span>')
r = swap(r, 'labs upload and certificates agree', 'labs share and members pay')
r = swap(r, 'gate &#8594; certificates agree', 'gate &#8594; checks agree')
r = swap(r, 'the certificate needs one cheap stain', 'the check needs one cheap stain')
r = swap(r, 'their certificates agree with independent checks', 'their checks agree with independent ones')
r = swap(r, 'certificates disagree with ground truth', 'checks disagree with ground truth')
r = swap(r, '<td>Certificates that hold up</td>', '<td>Checks that hold up</td>')
r = swap(r, '<td>Paying pilots</td>', '<td>Paying members</td>')
r = swap(r, '<td>Free certificates for contributing labs</td>', '<td>Free membership for contributing labs</td>')
r = swap(r, 'before vendor or alert revenue', 'before AI, dataset or vendor memberships')
_a = r.index('<h2><span class="num">05</span>Revenue model</h2>'); _b = r.index('<p><strong>Unit economics', _a)      # the members of board A15, at its prices
r = (r[:_a] + '<h2><span class="num">05</span>Membership and revenue</h2>\n'
     '<p>Identity testing already has a price: $217 per human STR sample at ATCC [5], $255 with a database search at the Johns Hopkins core [6]. That buys one identity check. '
     'Membership buys a behaviour check on every batch and the repository behind it, so it is priced per cell line per quarter; the quarter is a starting cadence, '
     'and the drift measured so far argues for more often.</p>\n'
     '<div class="tw"><table>\n<thead>\n<tr>\n<th>Member</th>\n<th>Price (proposed)</th>\n<th>What&#8217;s at stake for them</th>\n<th>Role</th>\n</tr>\n</thead>\n<tbody>\n'
     + ''.join(f'<tr>\n<td>{who}</td>\n<td>{price}</td>\n<td>{stake}</td>\n<td>{role}</td>\n</tr>\n' for who, price, stake, role in [
         ('Academic labs and cores', 'free for labs that share their control images; ~$500&#8211;1,000 per line-quarter for a private check', 'the paper', 'grows the map'),
         ('Pharma and CRO screening teams', f'~{price_range("price per line per quarter, $k")} per line-quarter, or a site licence', 'the screen; one late-caught line cost ~$2.6M', 'first revenue'),
         ('AI labs and model builders', 'by API, priced by use; the most', 'a model that fails on another lab&#8217;s cells', 'main revenue'),
         ('Companies that buy cell data', f'~{price_range("price per dataset membership, $k")} per dataset placed on the map', 'data they did not make and must trust', 'data revenue'),
         ('Cell banks and vendors', 'a membership for each line they sell: every lot checked against the field before it ships', 'the lot and every lab that bought it', 'the channel'),
         ('Later: bad-lot alerts', 'part of membership', 'every screen run on a drifting lot', 'only the network can make it')])
     + '</tbody>\n</table></div>\n' + r[_b:])

# ------------------------------------------------------------------ landscape: slide 08 written out from its own list, never a scorecard
from slide08 import ROWS as TOOLS
_a = l.index('<h2>Identity, yes. Behaviour, no.</h2>')
_b = l.index('</table></div>', _a) + len('</table></div>')
l = (l[:_a] + f'<h2>{WORDS.get(len(TOOLS), str(len(TOOLS))).capitalize()} questions, {WORDS.get(len(TOOLS), str(len(TOOLS)))} tools</h2>\n'
     '<p>Slide 08, written out: each tool, the question it answers well, and what it does not see, Datum Line&#8217;s own gaps included. '
     'Use all of them; the last one did not exist.</p>\n<div class="tw"><table>\n<thead>\n<tr><th>Tool</th><th>The question it answers</th><th>Does not see</th></tr>\n'
     '</thead>\n<tbody>\n' + ''.join(f'<tr><td><strong>{t}</strong></td><td>{q}</td><td>{n}</td></tr>\n' for t, q, n in TOOLS)
     + '</tbody>\n</table></div>' + l[_b:])
# the product is a membership (26 Oct); what other tools certify keeps the verb
l = swap(l, "Datum's product is the one thing none of them can sell: a neutral, cross-lab reference for what normal looks like, refreshed on a measured schedule.",
         "Datum's product is the one thing none of them can sell: membership to a neutral, cross-lab repository of what normal looks like, refreshed with every batch a lab shares.")
l = swap(l, 'exactly the coordinate a certificate needs to keep', 'exactly the coordinate the check needs to keep')
l = swap(l, '<td>a certificate per line, per quarter; a baseline on day one for a new line</td>', '<td>free membership: a check on every batch, and a baseline on day one for a new line</td>')
l = swap(l, 'a behaviour line beside identity on one certificate', 'a behaviour line beside identity on one report')
l = swap(l, 'Pitch Datum as the second line on the same certificate a lab already files.', 'Pitch Datum as the second line on the authentication record a lab already files.')
l = swap(l, 'the cheapest possible input to a certificate', 'the cheapest possible input to the check')
l = swap(l, '; that is the coordinate a certificate needs.', '; that is the coordinate the check needs.')
l = swap(l, 'customers and data partners. Their models get better inputs when the plates feeding them are certified.',
         'members and data partners. Their models get better inputs when the plates feeding them are aligned across labs, read by API.')
l = swap(l, 'offer the consortium the certificate as its natural next step', 'offer the consortium the repository as its natural next step: new plates from its members, checked against the map it built')
l = swap(l, 'Certificate is<br>more precise', 'The check is<br>more precise')
l = swap(l, 'and sell the per-lab, per-quarter certificate.', 'and sell membership: the check on every batch and the aligned images.')
l = swap(l, 'first certificates are for lines JUMP already covers (U2OS)', 'first members work on lines JUMP already covers (U2OS)')
l = swap(l, '<td>only untreated control images leave the lab; no compounds, no results</td>', '<td>only untreated control images are shared; no compounds, no results</td>')
l = swap(l, '<td>target customers</td>', '<td>first paying members</td>')

# ------------------------------------------------------------------ product vision: a membership to the repository
def product_vision(v0):
    """The product vision, written whole around membership to the repository (26 Oct, Kat: "product is really
    subscription/membership to data repo"): labs join free by sharing and keep a share, screening teams pay first,
    AI teams pay the most by API, and the check on every batch is a member feature.

    Keeps the original head, the habit loop and the magic moments; every number is read from results/, is a
    numbered public figure in figures/worth.py, or is a proposed price in appendix.MARKET."""
    import sys
    sys.path.insert(0, 'figures')
    from worth import DEALS, SITES, REFS
    plates_all = sum(x['n_plates'] for x in replay.values())
    raw, field = BETWEEN['raw'], BETWEEN['field']
    top = LB['by_lab'][0]
    line, dataset, bench = (price_range(k) for k in ('price per line per quarter, $k', 'price per dataset membership, $k', 'membership per partner per year, $k'))
    table = lambda head, rows: ('<div class="tw"><table>\n<thead>\n<tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>\n</thead>\n<tbody>\n'
                                + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>\n' for r in rows) + '</tbody>\n</table></div>\n')
    loop = lambda n, title, phases, back: (f'<figure><div class="fighead"><span class="fn">Fig. {n}</span> {title}</div>\n<div class="loop4">'
                                           + '<div class="arr">&#8594;</div>'.join(f'<div class="ph{" hot" if hot else ""}"><b>{a}</b><span class="ln">{b}</span></div>' for a, b, hot in phases)
                                           + f'</div>\n<div class="loopback">{back}</div></figure>\n')
    habit = v0[v0.index('<h2><span class="num">01</span>The habit loop</h2>'):v0.index('<h2><span class="num">03</span>The revenue loop</h2>')]
    habit = habit.replace('<span class="num">01</span>The habit loop', '<span class="num">03</span>The habit loop').replace('<span class="num">02</span>Six magic moments', '<span class="num">04</span>Six magic moments')
    habit = habit.replace('<span class="fn">Fig. 1</span>', '<span class="fn">Fig. 2</span>')
    habit = swap(habit, '<strong>The certificate as currency</strong>', '<strong>The check as currency</strong>')
    habit = swap(habit, 'ordered by when a new customer meets it', 'ordered by when a new member meets it')
    body = (
        '<h2>Vision</h2>\n'
        '<p>Every lab that images cells should know where its cells sit among everyone else&#8217;s, and every dataset made from cells should carry that answer with it. '
        'Datum Line is one shared repository of raw cell images from every lab, on one map, and the product is a membership to it. Labs join free by sharing the '
        'control images they already take, and keep a share of what their data earns. Teams that use the data pay: screening teams first, for a check on every batch '
        'they run; AI teams the most, for aligned images from every lab by API. The arrow after that is left open on purpose.</p>\n'
        '<p>The habit comes first, the way Strava&#8217;s segments place a run among everyone who ran the same stretch of road. Here the road is the cell line, '
        'and the field is every lab that ran it. Everything below serves one rule: <strong>uploading must be effortless, and the answer must be worth looking at.</strong></p>\n'
        '<h2><span class="num">01</span>Why now</h2>\n'
        f'<p><b>Cell data has a price.</b> {DEALS[0][1]} [{DEALS[0][2]}] {DEALS[1][1]} [{DEALS[1][2]}] {DEALS[2][1]} [{DEALS[2][2]}]</p>\n'
        f'<p><b>Cell data does not convert.</b> EU-OPENSCREEN ran one Cell Painting protocol at {SITES["n_sites"]} sites, with {SITES["supplied"]} supplied centrally. '
        f'Within a site, {SITES["within"][0]} to {SITES["within"][1]}% of compounds replicate; across sites, {SITES["across"][0]} to {SITES["across"][1]}% pair, '
        f'and the authors call the profiles &#8220;{SITES["quote"]}&#8221; [{SITES["ref"]}]. On the public JUMP data, a classifier names the lab from untreated wells '
        f'alone at {ACC} against {CHANCE} chance. Whoever makes cell data comparable sets its exchange rate.</p>\n'
        '<h2><span class="num">02</span>The path</h2>\n'
        + loop(1, 'A starting point, not an end state', [('Map', 'open &#183; today', True), ('Members', 'screening teams &#183; next', False),
                                                      ('API', 'AI teams &#183; then', False), ('Journals &#8230;', 'raw images with every paper; the rest left open', False)],
               'each stage pays for the next, and none is promised a date')
        + table(['Stage', 'What it is', 'Who pays', 'What has to be true', 'Status'], [
            ['<strong>Map</strong>', 'every lab&#8217;s untreated wells placed on one map; the box, the code and the public reference', 'nobody: open, and never crippled',
             'labs upload the controls they already image', f'today: {LABS} labs, {N_ALL} batches, {plates_all:,} plates of public data'],
            ['<strong>Members</strong>', 'the repository, and a check on every batch: where the cells sit, which lab they look like, what moved',
             f'teams that screen all year, {line} per cell line per quarter; companies that buy cell data, {dataset} per dataset',
             'the map holds for the line', 'next: the first paying member, a screening team; prices proposed on board A15'],
            ['<strong>API</strong>', 'aligned raw images from every lab, each traced to the lab that made it', 'AI labs and model builders, by use, and the most; each lab gets a share',
             'labs choose to share; the map makes labs agree', 'then'],
            ['<strong>&#8230;</strong>', 'what the map makes possible next: journals asking for raw control images with every paper, alerts when a lot drifts across labs, a graded benchmark, models trained on every lab&#8217;s controls', '', '', 'open']])
        + habit
        + '<h2><span class="num">05</span>Membership</h2>\n'
        '<p>Membership is access to the repository for a period, not ownership of the data. A lab that shares joins free; everyone else pays by how they use it. '
        'The check on every batch is what screening teams pay for first; aligned images from every lab are what AI teams pay the most for. '
        'A biotech&#8217;s first step costs nothing: a backup of its raw images, off-site and immutable, the copy cyber insurers ask for, encrypted with its own key; '
        'its control wells join the map when it chooses.</p>\n'
        + loop(3, 'Every membership pays the labs that made the data', [('A lab shares', 'its untreated wells, opt-in, credited by name on the map', False),
                                                                ('The map checks', 'where the cells sit, which lab they look like, what moved', False),
                                                                ('Members subscribe', 'screening teams per cell line, AI teams by API', True),
                                                                ('The lab keeps a share', 'of every membership, for as long as its data is used', False)],
               '&#8634; every lab that shares widens the map, and a wider map makes every check sharper')
        + table(['Who joins', 'What membership gives', 'Price, proposed', 'Role'], [
            ['labs and core facilities', 'the repository and the map; a check on every batch; the leaderboard', 'free: sharing controls earns it', 'the map'],
            ['biotech companies', 'their raw images backed up off-site and immutable, private to them; their controls join the map when they choose', 'free', 'the hook'],
            ['teams that run cell screens all year', 'a check on every batch they run, against every lab on the same line', f'{line} per cell line per quarter', 'first revenue'],
            ['AI labs and model builders', 'aligned raw images from every lab, by API', 'the most: priced by use, not yet set', 'main revenue'],
            ['companies that buy cell data', 'each dataset they buy, placed on the map', f'{dataset} per dataset', 'data revenue'],
            ['benchmark partners', 'a test set with faults planted on purpose', f'{bench} per year', 'the standard']])
        + table(['What members get', 'Why it is worth paying for'], [
            ['<strong>The check</strong>', f'the comparison a lab cannot make alone: on the public data, {N_OUT} of {N_ALL} batches sat off the map, in {LABS_OUT} of {LABS} labs (results/e9)'],
            ['<strong>Aligned data</strong>', f'it converts: on the map, agreement between labs on the same drugs goes from {raw:.2f} to {field:.2f} (board A14)'],
            ['<strong>Early access</strong>', f'a window before data goes public, which consortia already sell: a year, at the virtual-cell initiative [{DEALS[2][2]}]'],
            ['<strong>The benchmark</strong>', 'AI labs and model builders graded on planted faults, with a cell-count baseline on every task (board A16)']])
        + '<p><b>What never gets sold.</b> A lab&#8217;s treated data, its results, its name without consent, a ranking of instruments, or a verdict for hire. '
        'Membership buys access and the check; it never buys a better verdict. Prices and shares are proposals (boards A15 and A22) until the first partner labs and the first members set them.</p>\n'
        '<h2><span class="num">06</span>Trust, without the token</h2>\n'
        '<p>The open-science half of the product, and the reason a lab would share.</p>\n'
        + table(['Promise', 'How', 'Status'], [
            ['<strong>Control wells only</strong>', 'nothing else is shared: no compound, no target, no result; the frame is applied on the lab&#8217;s side', 'today'],
            ['<strong>A private backup</strong>', 'raw images a company backs up with us are encrypted with its own key; Datum Line cannot read them', 'proposed'],
            ['<strong>Every lab leaves a fingerprint</strong>', f'{ACC} of untreated wells name their own lab on plates the model never saw, so a dataset claimed from one lab and made in another is caught', 'today'],
            ['<strong>Signed and timestamped</strong>', 'every check signed, its fingerprint written to a public log: anyone can verify it, nobody can backdate it; a blockchain is one such log, not a requirement', 'proposed'],
            ['<strong>The lab keeps its data</strong>', 'sharing is a choice and can be withdrawn; a share of every membership goes to the lab that made the data', 'proposed'],
            ['<strong>Known members</strong>', 'members verified at sign-up; unusual access flagged; every access in a log the members can read', 'proposed'],
            ['<strong>Open code and data</strong>', 'the code is MIT on GitHub, the public data is JUMP&#8217;s under CC0, and every number comes from a script anyone can rerun', 'today'],
            ['<strong>Low risk by design</strong>', 'images of cell lines: no human genetic data and no pathogen data; the map holds untreated wells only', 'today']])
        + '<p>For a decentralized-science audience this is the point: open data, verifiable records and contributor upside, without a token to speculate on and without '
        'betting on anyone&#8217;s results.</p>\n'
        '<h2><span class="num">07</span>The game</h2>\n'
        f'<p>Every batch a lab sends is ranked against every batch the field has seen, on its untreated wells alone: how typical the cells are, how alike the plates are, '
        f'how steady the lab is from batch to batch, and cells per well against the field. Nothing in the score touches a treated well or a result, so the only way to climb '
        f'is better culture and imaging practice. On the public data, {lab_label(top["lab"])} holds the field&#8217;s longest streak, {top["streak"]["longest"]} batches '
        f'(results/e14). A lab sees its rank, its personal best, its streak and the lab to beat.</p>\n'
        + table(['Do', 'Don&#8217;t', 'Why'], [
            ['rank practice, never results', 'rank a lab&#8217;s results or its drugs', 'the only way up is better culture and imaging'],
            ['labs are numbers until they choose a name', 'publish a lab&#8217;s name or rank without consent', 'shame makes labs hide their worst plates, which teach the field most'],
            ['credit for uploading flagged plates', 'penalise a batch for sitting off the map', 'a failure uploaded is worth more than a success'],
            ['explain every flag with cells and a likely fix', 'show a bare red dot', 'a verdict without a reason reads as judgement'],
            ['let the instrument trigger uploads', 'send nudges to protect a streak', 'the reward is the answer, not the visit']])
        + '<h2><span class="num">08</span>Metrics</h2>\n'
        '<p>North star: the share of a lab&#8217;s plates that upload with no human action. If it is high, the loop turns; if people have to remember, nothing else matters.</p>\n'
        + table(['Metric', 'What it tells you'], [
            ['automatic upload share', 'the habit exists without effort'],
            ['flagged plates uploaded, not deleted', 'labs trust the product with bad news'],
            ['labs per line, lines per lab', 'the map is widening'],
            ['labs sharing to the repository', 'labs trust the repository with their data'],
            ['paying members, and how many renew', 'membership is worth paying for, again'],
            ['share of each membership paid to the lab', 'contributors are earning, so more will share'],
            ['checks cited outside the lab', 'the check has become currency']])
        + '<h2><span class="num">09</span>What could go wrong</h2>\n'
        + table(['Risk', 'Why it is real', 'Answer'], [
            ['cold start', 'no map without labs, no labs without a map', 'seed from JUMP&#8217;s public controls; U2OS first, any other line from its first batch'],
            ['labs will not share', 'data is a lab&#8217;s edge, and pharma data is intellectual property', 'a lab that keeps its images private still gets the check, as a paying member, the way screening teams do; sharing is free, optional and pays the lab'],
            ['AI teams train on public data for free', 'JUMP and other public sets are open to anyone', 'the open map stays free; members pay for what public data lacks: every lab aligned, new batches as labs share them, the lab behind every image'],
            ['public data must stay free', 'NIH-funded labs must share the data behind their findings', 'charge members for the check, alignment and compute, never for access to data a lab owes the public'],
            ['buyers want designed data at scale', 'the deals above buy factories and consortia, not leftovers', 'place factory and consortium data on the map too; the benchmark grades their models'],
            ['a platform builds its own map', 'phenomics companies hold the most images', 'no one can check their own drift against themselves; the reference has to be neutral and open']])
        + '<h2>References</h2>\n<ol>\n<li value="7">Chandrasekaran SN, et al. JUMP Cell Painting dataset. <em>bioRxiv</em>, 2023.</li>\n'
        + ''.join(f'<li value="{k}">{v}</li>\n' for k, v in REFS.items()) + '</ol>\n')
    a = v0.index('</header>') + len('</header>')
    b = v0.index('</main>')
    v = v0[:a] + body + v0[b:]
    v = swap(v, '<h1>Where do <span class="acc">my cells</span> sit?</h1>', '<h1>One repository, <span class="acc">every lab&#8217;s cells</span>.</h1>')
    v = swap(v, '<p class="sub">A habit worth having, and <span class="grn">the loop that pays for it</span>.</p>',
             '<p class="sub">Free for labs that share, a membership for teams that use the data, and <span class="grn">a place where cell data converts</span>.</p>')
    return v

lab_label = lambda source: 'lab ' + source.split('_')[1]
v = product_vision(v0)

def undated(text):
    """No event date on a document: the eyebrow keeps its subject and the byline its author, so a document travels."""
    text, a = re.subn(r'(<span class="acc">AI &#215; Bio) &#183; (?:\d{1,2} Sept|September 2026)(</span>)', r'\1\2', text)
    text, b = re.subn(r' &#183; \d{1,2} September 2026(</div>)', r'\1', text)
    assert a == 1 and b == 1, 'a dated header changed shape'   # access dates of sources, in the text, stay
    return text


# write only once every replacement has succeeded, so a failed run leaves the documents untouched
for path, text in (('docs/whitepaper.html', w), ('docs/brand.html', b),
                   ('docs/landscape.html', l), ('docs/roadmap.html', r), ('docs/product-vision.html', v)):
    open(path, 'w').write(undated(dmso_words(text)).replace('\\~', '~'))      # 26 Oct: a Markdown escape showed as "\\~$3M"
print('documents rebuilt:', ACC, CHANCE, WELLS, CENTRED, SCALED, PERM, BATCH, SCOPE)
