"""Speaker script: every spoken line, the clock and the run of show, written from results/*.json.

The pitch runs under five minutes. Spoken lines are short; detail that is not on the slide
lives here in the notes. The clock is computed from the word count, so it cannot drift from
the lines. Notes that are not listed below are left as written.

Usage:  python figures/build_script.py
"""
import json
import math
import re
from datetime import date

R = 'results'
WPM = 150                 # a calm speaking pace
PER_CLICK = 2             # seconds to click and let the slide settle
LIMIT = 5 * 60

e1 = json.load(open(f'{R}/e1.json'))['all_sources']
rt = json.load(open(f'{R}/e1-redteam.json'))['tests']
replay = json.load(open(f'{R}/e9-replay.json'))['labs']
L2 = replay['source_2']; B = L2['batches']
e6 = json.load(open(f'{R}/e6-what-moved-source_2-first-flag.json'))
e10 = json.load(open(f'{R}/e10-certificate-predicts-answer.json'))
e11 = json.load(open(f'{R}/e11-known-answer.json'))
drift = json.load(open(f'{R}/e1b-drift-source_2.json'))
pca = json.load(open(f'{R}/e2-plate-position-1053600681.json'))['pca']
e12 = json.load(open(f'{R}/e12-field-normalization.json'))
e13 = json.load(open(f'{R}/e13-baseline-density.json'))
lb = json.load(open(f'{R}/e14-leaderboard.json'))

NUM = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen']
word = lambda n: NUM[n] if n < len(NUM) else str(n)
MONTH = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
day = lambda iso: f'{int(iso[8:])} {MONTH[int(iso[5:7])]}'
lab = lambda s: 'lab ' + s.split('_')[1]

out = [b for b in B if b['verdict'] == 'outside']
flag, last = out[0], B[-1]
low = min(B, key=lambda b: b['cells_per_well'])
weeks = round((date.fromisoformat(last['date']) - date.fromisoformat(flag['date'])).days / 7)
own = e10['inside_labs']['drift_vs_agreement_with_own_baseline']
half = e10['sensitivity']['split half: drift and effect from different DMSO wells']['drift_vs_agreement_with_own_baseline']
without = e10['sensitivity']['without source_2']['drift_vs_agreement_with_own_baseline']
two = e10['flagged_against_unflagged']['source_2']['with_own_baseline']
inten = sorted([g for g in e6['groups'] if g['measurement'] == 'Intensity'], key=lambda g: -abs(g['mean_shift']))
n_all = sum(v['n_batches'] for v in replay.values()); n_out = sum(v['batches_outside'] for v in replay.values())
failed = e11['failed']; failed_plates = sum(f['n_plates'] for f in failed)
far = drift['bins'][-1]; same = drift['bins'][0]
acc, chance = f"{100 * e1['balanced_accuracy']:.1f}", word(round(100 * e1['chance']))
centred = f"{100 * rt['plate_centred']['balanced_accuracy']:.0f}"
held = ', '.join(str(b['n_plates']) for b in out[:-1]) + f' and {out[-1]["n_plates"]}'
n_in = len(B) - len(out) - 1
now = max((b for b in B if b['verdict'] == 'in distribution'), key=lambda b: b['n_plates'])     # the batch on slide 06
frame = next(b for b in e12['lab_2'] if b['batch'] == now['batch'])
E = e12['every_batch']; between = E['agree_field']
OWN = 'own' if 'own' in between else 'scaled'          # the usual normalisation to a batch's own controls
ref = e13['field_reference_by_labs']; ref_one, ref_most = ref[min(ref, key=int)], ref[max(ref, key=int)]
n_ref_labs = word(int(max(ref, key=int)))
own_plates = e13['own_baseline_by_plates']
cv = E['effect_size_cv_across_batches_within_lab']
wrong = sum(sum(r) for r in e1['confusion_matrix']['rows_true_cols_pred']) - sum(r[i] for i, r in enumerate(e1['confusion_matrix']['rows_true_cols_pred']))

# slide -> (title, beat, one line to land, extra pause in seconds, [spoken lines; each ends with a click unless marked])
TALK = [
    ('01', 'Control is an illusion', 'hook', 'Cell data from any lab, comparable with any other\'s.', 0, [
        "Hi, I'm Kat. Datum Line makes cell data from any lab comparable with any other lab's. "
        "Labs put their cells on the map for free. The companies that buy cell data pay for the certificate."]),
    ('02', 'One lab, or six?', 'shown', "The model isn't the hard part. The map is.", 4, [
        "Six untreated wells. Same line, same protocol, no drug. One lab, or six?",
        f"Six. Nobody here can tell. A classifier can: {acc} percent across {word(e1['n_labs'])} labs, against {chance} by chance, on plates it never saw.",
        "Why now: this data is public and free, and models are a commodity. The model isn't the hard part. The map is."]),
    ('03', 'Do my cells look normal?', 'felt', 'Every company that buys cell data gets this problem delivered.', 0, [
        "So every lab asks the same question, and can't answer it. About twenty-eight billion dollars a year of US preclinical research can't be reproduced, "
        "and a third of that is inputs.|",
        "Today you search, you ask around, then you guess. I've seen one lab run too fast and one hold too long. "
        "And every company that buys cell data gets this problem delivered."]),
    ('04', 'Founder', 'lived', 'This is the thing I kept needing and nobody sold.', 0, [
        "I've asked it at five benches. Nobody could answer it.",
        "At Axiom we onboarded hepatocytes through a good CRO. Their checks passed; ours passed. The first sign anything had moved came from outside: "
        "the Broad couldn't align our profiles to their reference.|",
        "This is the thing I kept needing and nobody sold."]),
    ('05', 'The map', 'the map', 'Where you sit predicts what you measure.', 0, [
        f"{word(len(replay)).capitalize()} labs, same cells, same protocol: {word(len(replay))} different normals. That's what the classifier saw.",
        "And where a lab sits on this map predicts how far its drug answers have moved. The map is worth having."]),
    ('06', 'Every lab that joins sharpens the map', 'why it compounds', 'The labs that build it use it free.', 0, [
        f"Put them on one map and it sharpens with every lab that joins: {word(round(ref_one['mean']))} apart with one lab, under {word(math.ceil(ref_most['mean']))} with {n_ref_labs}. "
        "The labs that upload use it free. The companies that buy cell data pay for the certificate."]),
    ('07', 'The product', 'what', 'Send your controls. See where you stand.', 0, [
        "The product: send the control images you already take. They stay yours.|",
        "Back comes your place on the map, a certificate you can show, and data every other lab can compare. "
        "Every batch you send sharpens the map, for you and for everyone.",
        "And it's a game you can win. Every batch is ranked against the whole field on its controls alone: how typical, how tight, how steady. "
        "Your best, your streak, and the lab to beat."]),
    ('08', 'Identity, yes. Behaviour, no.', 'who else', 'The other half of the certificate.', 0, [
        "STR proves which line you have. Nothing proves it behaves like everyone else's. STR is a collaborator, not a rival."]),
    ('09', 'Eighteen months, four milestones', 'the money', 'A first paid certificate.', 0, [
        "Eighteen months: three labs live on the map, brightfield proven, the ugliest dataset in biology built on purpose and graded, "
        "and a first paid certificate on data somebody bought."]),
    ('10', 'Every plate, placed in the field', 'vision, ask', 'Have images of U2OS cells? Talk to me.', 0, [
        f"Every plate you image, placed on the map. Already there, from public data: {n_all} batches, {word(len(replay))} labs. The next row is yours.|",
        "What I need: images, U2OS first; ML people better than me; bench time; and a pre-seed.|",
        "Have images of U2OS cells? Talk to me.|"]),
]
CUES = {
    '01': "On screen while you're introduced. Two lines drop from the top like dive lines: green is the field's datum, pink is yours. Say the one sentence.",
    '02': 'Shown. The first view is a game: let the room look for four seconds.',
    '03': 'Felt. Point at the pink slice, then the six search results, then the two edges of card 3: run it, or hold.',
    '04': 'Lived. Let the logos and the pink line under your name do the credential work.',
    '05': 'The map. Dark slide: slow down. Two views, one sentence each.',
    '06': 'Why it compounds. Point at the curve, then the three prices. This is the moat and the business model in one breath.',
    '07': 'What. One sentence, then the map, then the certificate, then the row of ticks. Click: the leaderboard, and point at the pink rows.',
    '09': 'The money. Four cards left to right; the pink one is the milestone that pays.',
    '10': 'Vision, then the ask. Point at the open row, then the right card. Stop on the question.',
}
# detail that is not on the slide; each replaces the note of the same label in that slide's section
NOTES = {
    '03': {'Precision to hold.': "$28B is a 2015 US estimate; the 36% covers all reagents and reference materials, not only cells. The search card shows six real "
           "U2OS images from six papers, 2009 to 2023, via IDR and JUMP; sources are in the README. Card 3 names neither lab and gives no exact figure; "
           "keep it that way on stage. Growth chart is the metaphor if you need one: nobody plots their cells against the population."},
    '02': {'Why now, in full.': "Three things that were not true three years ago. JUMP made the field's reference public and CC0 in 2023 [7], so the map exists and it "
           "works on eleven labs. Image models are a commodity, so nobody wins on the model; they win on the reference. And on 10 April 2025 the FDA announced a plan to "
           "phase out animal-testing requirements in favour of new approach methods [9], so cell-based data starts to carry regulatory weight, and data that carries "
           "regulatory weight needs a calibration standard. Nobody holds it yet.",
           'Precision to hold.': f"{word(e1['n_labs']).capitalize()} labs, {e1['n_wells']:,} untreated wells, {e1['n_plates']:,} plates, held out by plate; {wrong} wells wrong. "
           f"Holding out whole batches gives {100 * rt['batch_held_out']['balanced_accuracy']:.1f}%; labs on one microscope model, "
           f"{100 * rt['same_microscope']['balanced_accuracy']:.2f}%. The signature is in every feature family, image-quality features included, so it reflects the "
           "whole imaging pipeline as well as the cells. Say \"the lab\", not \"the cells\". Cell Painting fluorescence; brightfield is the bet.",
           'For ML people.': f"The line on the second view: normalising each plate to its own controls takes lab identity from {acc} to {centred} percent. "
           "Right for discovery, wrong for QC (A3)."},
    '04': {'Why me, in one breath.': "I have been on every side of the transaction: I built the assays (AbbVie, insitro), I ran the outsourced data purchase that did not "
           "align (Axiom, the CRO, the Broad flagging it), I invented bioactivity methods that measure what cells do rather than what the label says, and I published "
           "with the Broad, which built the reference. The buyer, the maker and the method inventor in one person is the honest reason founder comes before product."},
    '05': {'Figure detail.': f"First view: a PCA of {pca['wells']:,} untreated wells for the eye; distances are measured in all features. The number is the mean distance "
           f"between two labs' centres, {ref_one['mean']:.1f} within-plate spreads. "
           f"Second view: one point per batch; agreement is the cosine between a batch's effect of {len(e10['compounds_pooled'])} positive controls and its lab's "
           f"first-batch effect; rho is Spearman after removing each lab's mean, minus {abs(own['spearman']):.2f} over {own['n_batches']} batches; shuffled, "
           f"minus {abs(own['null_mean']):.2f}; without lab 2, minus {abs(without['spearman']):.2f}; drift and effect from different wells, minus {abs(half['spearman']):.2f}. "
           f"Lab 2 against its June answer: {two['unflagged']:.2f} before the flag, {two['flagged']:.2f} after.",
           'Precision to hold.': "In lab 2 the flagged batches are also the last three, so inside that lab the flag and the calendar cannot be separated; the correlation "
           "uses every lab. The ringed points are one lab's autumn batches (A13); the crosses are batches whose positive controls show no effect (A8). "
           f"If asked whether the map changes a lab's results: yes, modestly. In the field's frame, agreement between labs on the same drugs goes from {between['raw']:.2f} "
           f"to {between['field']:.2f}, above the usual normalisation to a batch's own controls ({between[OWN]:.2f}) in {between['field_better_than_own_in']} batches; "
           "it does not change a lab's agreement with itself (A14).",
           'For ML people.': None},
    '06': {'Figure detail.': f"Two references, each built from the same number of labs that share none; with one lab each they sit {ref_one['mean']:.1f} within-plate "
           f"spreads apart, with {n_ref_labs} each {ref_most['mean']:.1f}. The dashed line is one over root n. Eleven labs can make at most two disjoint sets of five, "
           f"so the curve stops there. A lab's own baseline settles sooner: {own_plates['1']['mean']:.2f} with one plate, {own_plates['8']['mean']:.2f} with eight, then flat. "
           f"The reference of all {e13['n_labs']} labs moves {e13['reference_moves_when_one_lab_leaves']['mean']:.2f} when one lab is removed.",
           'Precision to hold.': "The prices are a proposal, not a validated model: free for contributors, about 5 to 15 thousand dollars per line per quarter for screening "
           "groups, a fee per certified lot. One unchecked screen is about 2.6 million, so the subscription is about 170 times less (A15). Bad-lot alerts across labs "
           "come after the certificate; don't promise them."},
    '07': {'Figure detail.': f"One real lab on one real day: lab 2, {day(now['date'])}, {now['n_plates']} plates, chosen as its in-distribution batch with the most plates. "
           f"{now['from_baseline']:.1f} spreads from its own baseline, {now['to_nearest_other']:.1f} to {lab(now['nearest_other'])}, {now['cells_per_well']:.0f} cells per well. "
           f"The reference is {L2['n_reference_plates']:,} plates from the other {len(L2['reference_labs'])} labs. In the field's frame this batch's agreement with the other labs goes "
           f"from {frame['agree_field_raw']:.2f} to {frame['agree_field_field']:.2f}. The ticks are the batches sent so far; the open one is the next.",
           'The game.': f"Field score is 100 minus the mean percentile of four measures on untreated wells alone: distance from the field's centre, spread of the batch's "
           f"plates, distance from the lab's previous batch, and cells per well against the field's median. {lab(lb['by_lab'][0]['lab']).capitalize()} holds "
           f"{sum(r['lab'] == lb['by_lab'][0]['lab'] for r in lb['top'])} of the top ten and a streak of {lb['by_lab'][0]['streak']['longest']}. Lab 2's best is "
           f"#{min(lb['lab_2'], key=lambda r: r['rank'])['rank']} of {lb['n_batches']}; the batch on the slide is #{next(r for r in lb['lab_2'] if r['batch'] == now['batch'])['rank']}. "
           "Nothing in the score touches a treated well, so the only way to climb is better culture and imaging practice; say that if anyone asks whether a leaderboard is bad for science (A17).",
           'Precision to hold.': f"This is a replay on public data, not a customer. The same lab's later batches sit outside its baseline from {day(flag['date'])}, and the certificate "
           f"says so and says where to look: {inten[0]['channel']} and {inten[1]['channel']} stain intensity (A11, A12, A13). Across the field {n_out} of {n_all} batches are outside. "
           "Bring that up if asked whether it ever says no. Brightfield is still the bet (A10)."},
    '09': {'Figure detail.': "Milestones, not dates: the pre-seed size is not set and the proof of concept sets it. Three partner labs means three labs sending U2OS "
           "controls every batch and reading certificates; none has agreed yet, so say \"three\" and not a name. Brightfield proven means the same map from label-free "
           "images (A10). The test set is the ugliest dataset on purpose: six labs' real wells plus planted failures, bubble, focus, exposure, clipped well, bad lot, "
           "wrong label, with every method graded on naming the failure (A16). A first paying line is one pharma cell line on a per-quarter subscription.",
           'Precision to hold.': None},
    '10': {'Why here.': "San Francisco has the densest cluster anywhere of companies that buy cell data they did not make and train models on it, plus JUMP partners. "
           "The first ten customers are a walk away, and two of them are on the resume. Name none of them as customers until one has agreed; "
           "say \"the companies that buy cell data\".",
           'Precision to hold.': f"Price and test-set budget are not set: say \"per line, per quarter\" and \"the proof of concept sets the size\". Don't name a partner lab "
           f"until one has agreed. Name no JUMP lab beyond its number. The grid is {n_all} batches and {sum(v['n_plates'] for v in replay.values()):,} plates; each square is a batch. "
           "Now is U2OS in fluorescence; more lines and brightfield are next and are not yet shown."},

}

words = lambda s: len(re.sub(r'<[^>]+>', ' ', s.replace('|', '')).split())
clock = lambda t: f'{int(t) // 60}:{int(t) % 60:02d}'

path = 'docs/speaker-script.html'
s = open(path).read()
t = 0.0
rows, total_words, total_clicks = [], 0, 0
for slide, title, beat, land, pause, lines in TALK:
    start = t
    paras = []
    for line in lines:
        click = not line.endswith('|')
        text = line.rstrip('|')
        paras.append(f'<p><strong>{clock(t)}</strong> {text}{" <em>Click.</em>" if click else ""}</p>')
        t += words(text) * 60 / WPM + (PER_CLICK if click else 0)
        total_clicks += click
    t += pause
    total_words += sum(words(l) for l in lines)
    n_clicks = sum(not l.endswith('|') for l in lines)
    rows.append((slide, title, f'{clock(start)}&#8211;{clock(t)}', round(t - start), n_clicks, beat, land))

    m = re.search(r'<h3><span class="sn">%s</span>.*?(?=<h3>|<h2|</main>|</body>)' % slide, s, flags=re.S)
    sec = m.group(0)
    views = f', {word(len(lines))} views' if slide in ('02', '05') else (', two views' if slide == '07' else '')
    head = {'07': 'Send your controls. See where you stand'}.get(slide, title)
    sec = re.sub(r'(<h3><span class="sn">%s</span>).*?(</h3>)' % slide, lambda k: f'{k.group(1)}{head} ({rows[-1][2]}{views}){k.group(2)}', sec, count=1, flags=re.S)
    if slide in CUES:
        sec = re.sub(r'(</h3>\s*<p>)<em>.*?</em>(</p>)', lambda k: f'{k.group(1)}<em>{CUES[slide]}</em>{k.group(2)}', sec, count=1, flags=re.S)
    sec = re.sub(r'<p><strong>(?:\d:\d\d|Fourth click, if there is time\.)</strong>.*?</p>\s*', '', sec, flags=re.S)
    sec = re.sub(r'(</h3>\s*<p><em>.*?</em></p>\s*)', lambda k: k.group(1) + '\n'.join(paras) + '\n', sec, count=1, flags=re.S)
    for key, note in NOTES.get(slide, {}).items():
        pat = re.compile(r'<p><strong>%s</strong>.*?</p>\s*' % re.escape(key), flags=re.S)
        new = f'<p><strong>{key}</strong> {note}</p>\n' if note else ''
        sec = pat.sub(lambda _: new, sec, count=1) if pat.search(sec) else sec.rstrip() + '\n' + new + '\n'
    sec = re.sub(r'\n{2,}', '\n', sec).rstrip() + '\n\n'      # the same spacing on every run
    s = s[:m.start()] + sec + s[m.end():]

assert t < LIMIT, f'the pitch runs {clock(t)}, over five minutes'
body = ''.join(f'<tr>\n<td>{a} {b}</td>\n<td>{c}</td>\n<td>{d}</td>\n<td>{e}</td>\n<td>{f}</td>\n<td>{g}</td>\n</tr>\n' for a, b, c, d, e, f, g in rows)
s = re.sub(r'(<tbody>\s*)<tr>\s*<td>01 .*?(</tbody>)', lambda k: k.group(1) + body + k.group(2), s, count=1, flags=re.S)
s = re.sub(r'(<h1[^>]*>).*?(</h1>)', r'\1Under five minutes, <span class="acc">ten slides.</span>\2', s, count=1, flags=re.S)
s = re.sub(r'(<p>)(?:Four|Under five) minutes, ten slides, about .*?(The spine:)',
           lambda k: (f'{k.group(1)}Under five minutes, ten slides: {total_words} spoken words and {total_clicks} clicks, {clock(t)} at {WPM} words a minute. '
                      f'Detail that is not on a slide is in the notes here. {k.group(2)}'), s, count=1, flags=re.S)
s = re.sub(r"If you're late[^<]*", "If you're late, skip the second sentence of 03 and the first sentence of 10.", s, count=1)
s = re.sub(r'The spine: <strong>.*?</p>', 'The spine: <strong>shown, felt, lived</strong> (02, 03, 04), then <strong>the map, why it compounds, the product</strong> (05, 06, 07), '
           'then <strong>who else, the money, the ask</strong> (08, 09, 10). 08 is the fastest slide: one beat.</p>', s, count=1, flags=re.S)
s = re.sub(r'<title>.*?</title>', '<title>Datum Line · Speaker script</title>', s, count=1, flags=re.S)
open(path, 'w').write(s)
print(f'script written: {total_words} spoken words, {total_clicks} clicks, runs {clock(t)}')
for r in rows:
    print('  ', r[0], r[2], f'{r[3]} s', f'{r[4]} clicks')
