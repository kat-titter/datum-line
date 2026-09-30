"""Speaker script: every spoken line, the clock and the run of show, written from results/*.json.

The pitch runs under five minutes. Spoken lines are short; detail that is not on the slide
lives here in the notes. The clock is computed from the word count, so it cannot drift from
the lines. Notes that are not listed below are left as written.

Usage:  python figures/build_script.py
"""
import json
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
    ('01', 'Control is an illusion', 'hook', 'Confidence without control.', 0, [
        "Hi, I'm Kat. Every result in biology is a difference from a control, and nobody checks the control. So I'm building confidence without it."]),
    ('02', 'Founder', 'self', 'This is the thing I kept needing and nobody sold.', 0, [
        "Five labs, and the same question at every bench: do my cells look normal? Nobody could answer it.",
        "At Axiom we onboarded hepatocytes through a good CRO. Their checks passed; ours passed. The first sign anything had moved came from outside: "
        "the Broad couldn't align our profiles to their reference.|",
        "This is the thing I kept needing and nobody sold."]),
    ('03', 'Do my cells look normal?', 'us, now', 'Cells are the input nobody certifies.', 0, [
        "It's not just me. About twenty-eight billion dollars a year of US preclinical research can't be reproduced, and a third of that is inputs.|",
        "Today you search, you ask around, then you guess. I've seen one lab run too fast and one hold too long. Cells are the input nobody certifies."]),
    ('04', 'One lab, or six?', 'why now', "The model isn't the hard part. The reference is.", 4, [
        "Six untreated wells. Same line, same protocol, no drug. One lab, or six?",
        f"Six. Nobody here can tell. A classifier can: {acc} percent, against {chance} by chance, on plates it never saw.",
        "Why now: this data is public and free, and models are a commodity. The model isn't the hard part. The reference is."]),
    ('05', 'One frame for every lab', 'how', 'One frame, and every lab that joins tightens it.', 0, [
        f"{word(len(replay)).capitalize()} labs, same cells, same protocol: {word(len(replay))} different normals. That's what the classifier saw.",
        "Put them in one frame, and the reference tightens with every lab that joins.",
        f"In that frame, answers move closer. The same drugs, measured in every lab, agree better: "
        f"in {word(int(e12['labs_where_field_is_highest'].split()[0]))} of {word(len(e12['by_lab']))} labs, better than their own controls can do.",
        "And where you sit predicts what you measure. So the map is worth having."]),
    ('06', 'The product', 'what', 'Send your controls. See where you stand.', 0, [
        "The product: send the control images you already take. They stay yours.|",
        "Back comes your place in the field, a certificate you can show, and your data in the field's frame. "
        "Every batch you send makes the reference denser, for you and for everyone. It's a growth chart your cells come back to."]),
    ('07', 'Identity, yes. Behaviour, no.', 'who else', 'The other half of the certificate.', 0, [
        "STR proves which line you have. Nothing proves it behaves like everyone else's. STR is a collaborator, not a rival."]),
    ('08', 'Three buyers, one certificate', 'who buys', 'Contributors use it free.', 0, [
        "Three buyers. Cores contribute controls and use it free: that builds the reference. Pharma and CROs pay per line, per quarter: "
        "a fraction of one unchecked screen. Cell banks pay per certified lot."]),
    ('09', 'The ugliest dataset in biology', 'the build', 'Name the failure, not just flag it.', 0, [
        "With a blank cheque I'd build the ugliest dataset in biology, on purpose. Six labs already look this different. "
        "Then plant the failures, and make every method name which one went wrong."]),
    ('10', 'Every plate, placed in the field', 'vision, ask', 'Have images of U2OS cells? Talk to me.', 0, [
        f"The vision: every plate you image, placed in the field. Already in the frame, from public data: {n_all} batches, {word(len(replay))} labs. "
        "The next row is yours.|",
        "What I need: images, U2OS first; ML people better than me; bench time; and a pre-seed.|",
        "Have images of U2OS cells? Talk to me.|"]),
]
CUES = {
    '04': 'Why now. The first view is a game: let the room look for four seconds.',
    '05': 'How. Dark slide: slow down. Four views, one sentence each.',
    '06': 'What. One sentence, then the map, then the certificate, then the row of ticks.',
    '10': 'Vision, then the ask. Point at the open row, then the right card. Stop on the question.',
}
# detail that is not on the slide; each replaces the note of the same label in that slide's section
NOTES = {
    '03': {'Precision to hold.': "$28B is a 2015 US estimate; the 36% covers all reagents and reference materials, not only cells. The search card shows six real "
           "U2OS images from six papers, 2009 to 2023, via IDR and JUMP; sources are in the README. Card 3 names neither lab and gives no exact figure; "
           "keep it that way on stage. Growth chart is the metaphor if you need one: nobody plots their cells against the population."},
    '04': {'Precision to hold.': f"{word(e1['n_labs']).capitalize()} labs, {e1['n_wells']:,} untreated wells, {e1['n_plates']:,} plates, held out by plate; {wrong} wells wrong. "
           f"Holding out whole batches gives {100 * rt['batch_held_out']['balanced_accuracy']:.1f}%; labs on one microscope model, "
           f"{100 * rt['same_microscope']['balanced_accuracy']:.2f}%. The signature is in every feature family, image-quality features included, so it reflects the "
           "whole imaging pipeline as well as the cells. Say \"the lab\", not \"the cells\". Cell Painting fluorescence; brightfield is the bet.",
           'For ML people.': f"The line on the second view: normalising each plate to its own controls takes lab identity from {acc} to {centred} percent. "
           "Right for discovery, wrong for QC (A3)."},
    '05': {'Figure detail.': f"First view: a PCA of {pca['wells']:,} untreated wells for the eye; distances are measured in all features. The number is the mean distance "
           f"between two labs' centres, {ref_one['mean']:.1f} within-plate spreads. "
           f"Second view: two references, each built from the same number of labs that share none; with one lab each they sit {ref_one['mean']:.1f} apart, with "
           f"{n_ref_labs} each {ref_most['mean']:.1f}. The dashed line is one over root n. A lab's own baseline settles sooner: {own_plates['1']['mean']:.2f} with one plate, "
           f"{own_plates['8']['mean']:.2f} with eight, then flat. "
           f"Third view: each batch's untreated wells are moved onto the field's mean and covariance, built without that lab, and the same move is applied to the treated wells. "
           f"Agreement is the cosine between a batch's effect of {len(e12['compounds'])} positive controls and the mean effect in the other labs: {between['raw']:.2f} as measured, "
           f"{between['field']:.2f} in the field's frame, higher in {between['field_better_in']} batches. Normalised to the batch's own controls, the usual practice, {between[OWN]:.2f}; "
           f"the frame is above that in {between['field_better_than_own_in']} batches. "
           f"Fourth view: one point per batch; rho is Spearman after removing each lab's mean, minus {abs(own['spearman']):.2f} over {own['n_batches']} batches; shuffled, "
           f"minus {abs(own['null_mean']):.2f}; without lab 2, minus {abs(without['spearman']):.2f}; drift and effect from different wells, minus {abs(half['spearman']):.2f}.",
           'Precision to hold.': f"The gain from the field's frame is consistent and modest: {between['raw']:.2f} as measured, {between[OWN]:.2f} on own controls, {between['field']:.2f} in the frame. It is between labs. A lab's agreement with "
           f"its own first batch does not change ({E['agree_own']['raw']:.2f}, {E['agree_own']['field']:.2f}), and effect sizes vary more from batch to batch "
           f"({cv['raw']:.2f} becomes {cv['field']:.2f}). Say \"closer\", not \"the same\". The margin over the wrong drug rises in {E['margin']['field_better_in']} batches, "
           "so the frame is not making every drug look alike (A14). The ringed points on the fourth view are one lab's autumn batches (A13); the crosses are batches whose "
           "positive controls show no effect (A8). If you are late, skip the fourth view.",
           'For ML people.': None},
    '06': {'Figure detail.': f"One real lab on one real day: lab 2, {day(now['date'])}, {now['n_plates']} plates, chosen as its in-distribution batch with the most plates. "
           f"{now['from_baseline']:.1f} spreads from its own baseline, {now['to_nearest_other']:.1f} to {lab(now['nearest_other'])}, {now['cells_per_well']:.0f} cells per well. "
           f"The reference is {L2['n_reference_plates']:,} plates from the other {len(L2['reference_labs'])} labs. In the field's frame this batch's agreement with the other labs goes "
           f"from {frame['agree_field_raw']:.2f} to {frame['agree_field_field']:.2f}. The ticks are the batches sent so far; the open one is the next.",
           'Precision to hold.': f"This is a replay on public data, not a customer. The same lab's later batches sit outside its baseline from {day(flag['date'])}, and the certificate "
           f"says so and says where to look: {inten[0]['channel']} and {inten[1]['channel']} stain intensity (A11, A12, A13). Across the field {n_out} of {n_all} batches are outside. "
           "Bring that up if asked whether it ever says no. Brightfield is still the bet (A10)."},
    '08': {'Precision to hold.': "The prices are a proposal, not a validated model: free for contributors, about 5 to 15 thousand dollars per line per quarter for screening "
           "groups, a fee per certified lot. One unchecked screen is about 2.6 million, so the subscription is about 170 times less. Bad-lot alerts come after the certificate."},
    '09': {'Figure detail.': "Six real untreated wells, one per lab, with each lab's instrument; across the 13 JUMP labs there are five microscope models, objective NA from "
           "0.4 to 1.0, and eight plate types. The four red-team tiles are one real well corrupted in software and are labelled simulated. The failures to plant: bubble, "
           "focus, exposure, clipped well, bad lot, wrong label."},
    '10': {'Precision to hold.': f"Price and test-set budget are not set: say \"per line, per quarter\" and \"the proof of concept sets the size\". Don't name a partner lab "
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
    views = f', {word(len(lines))} views' if slide in ('04', '05') else ''
    head = {'06': 'Send your controls. See where you stand'}.get(slide, title)
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
s = re.sub(r"If you're late at 2:20, cut[^<]*", "If you're late, skip the fourth view of 05 and the first sentence of 10.", s, count=1)
s = re.sub(r'<title>.*?</title>', '<title>Datum Line · Speaker script</title>', s, count=1, flags=re.S)
open(path, 'w').write(s)
print(f'script written: {total_words} spoken words, {total_clicks} clicks, runs {clock(t)}')
for r in rows:
    print('  ', r[0], r[2], f'{r[3]} s', f'{r[4]} clicks')
