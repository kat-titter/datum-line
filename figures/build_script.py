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
    ('05', 'It passed every check', 'how', 'Your own past is not a reference. The field is.', 0, [
        f"One lab, {word(len(B))} batches, June to October. Cell counts stay in range.",
        "Now the same batches against the field. At the end of August the lines cross: this lab is further from its own June baseline than from another lab.",
        "Same lab, two different places. Your own past is not a reference. The field is.",
        "And it matters. The further a batch drifts, the less its answer to the same drugs agrees with its own baseline. That's the failure I lived."]),
    ('06', 'The product', 'what', 'Four months becomes one day.', 0, [
        "The product: send the control images you already take. They stay yours. One answer in a day.|",
        f"Here it is, replayed on that lab. {word(n_in).capitalize()} batches in. On {day(flag['date'])}, out: {word(weeks)} weeks before October. "
        f"And it says where to look: stain intensity, not cell count. Four months becomes one day."]),
    ('07', 'Identity, yes. Behaviour, no.', 'who else', 'The other half of the certificate.', 0, [
        "STR proves which line you have. Nothing proves it behaves like everyone else's. STR is a collaborator, not a rival."]),
    ('08', 'Three buyers, one certificate', 'who buys', 'Contributors use it free.', 0, [
        "Three buyers. Cores contribute controls and use it free: that builds the reference. Pharma and CROs pay per line, per quarter: "
        "a fraction of one unchecked screen. Cell banks pay per certified lot."]),
    ('09', 'The ugliest dataset in biology', 'the build', 'Name the failure, not just flag it.', 0, [
        "With a blank cheque I'd build the ugliest dataset in biology, on purpose. Six labs already look this different. "
        "Then plant the failures, and make every method name which one went wrong."]),
    ('10', 'Every plate, placed in the field', 'vision, ask', 'Have images of U2OS cells? Talk to me.', 0, [
        f"The vision: every plate you image, placed in the field. Here it is on public data: {n_all} batches, {word(len(replay))} labs. "
        f"{word(n_out).capitalize()} outside their baseline. {word(len(failed)).capitalize()} where a known answer failed.|",
        "What I need: images, U2OS first; ML people better than me; bench time; and a pre-seed.|",
        "Have images of U2OS cells? Talk to me.|"]),
]
CUES = {
    '04': 'Why now. The first view is a game: let the room look for four seconds.',
    '05': 'How. Dark slide: slow down. Four views of one lab, one sentence each.',
    '06': 'What. One sentence, then the strip left to right, then the certificate.',
    '10': 'Vision, then the ask. Point at the grid, then the right card. Stop on the question.',
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
    '05': {'Figure detail.': f"Second view: median distance of each batch's plates from the lab's first batch, and to the nearest other lab's centre, in units of the "
           f"field's within-plate spread; features scaled on the other {len(L2['reference_labs'])} labs, {L2['n_reference_wells']:,} wells, {L2['n_features']:,} features, "
           f"clipped at five standard deviations. By October: {last['from_baseline']:.1f} from itself, {last['to_nearest_other']:.1f} from {lab(last['nearest_other'])}; "
           f"every well is still named lab 2. On {day(low['date'])} the cell count dips to {low['cells_per_well']:.0f}, which the lab can see. "
           f"Third view: a PCA of {pca['wells']:,} wells for the eye; distances are measured in all features. Two plates of this lab sit {same['median']} spreads apart "
           f"in one batch and {far['median']} after thirteen weeks, {word(round(far['ratio_to_same_batch']))} times further. "
           f"Fourth view: one point per batch; agreement is the cosine between a batch's effect of {len(e10['compounds_pooled'])} positive controls and its lab's "
           f"first-batch effect; rho is Spearman after removing each lab's mean, minus {abs(own['spearman']):.2f} over {own['n_batches']} batches; shuffled, "
           f"minus {abs(own['null_mean']):.2f}; without lab 2, minus {abs(without['spearman']):.2f}; drift and effect from different wells, minus {abs(half['spearman']):.2f}. "
           f"Lab 2 against its June answer: {two['unflagged']:.2f} before the flag, {two['flagged']:.2f} after.",
           'Precision to hold.': "In lab 2 the flagged batches are also the last three, so inside that lab the flag and the calendar cannot be separated; the correlation "
           "uses every lab. The crosses on the fourth view are batches whose positive controls show no effect (A8); they are not drift. "
           "If you are late, skip the fourth view.",
           'For ML people.': None},
    '06': {'Figure detail.': f"Each batch is judged with only its own lab's history up to that day, against the field as published. Outside means further from its own "
           f"first batch than from the nearest other lab. The certificate is the first flag, {day(flag['date'])}: {flag['n_plates']} plates, {flag['from_baseline']:.1f} spreads "
           f"from baseline, {flag['to_nearest_other']:.1f} to the nearest lab, {flag['cells_per_well']:.0f} cells per well. {inten[0]['channel']} and {inten[1]['channel']} stain "
           f"intensity are up {inten[0]['mean_shift']:.1f} and {inten[1]['mean_shift']:.1f} standard deviations, {inten[2]['channel']} {inten[2]['mean_shift']:.1f}.",
           'Precision to hold.': f"The replay is hindsight on public data. The flagged batches hold {held} plates. The certificate says where to look, not why. "
           f"Across the field {n_out} of {n_all} batches flag, and lab 2's verdicts hold under nine of ten variants (A11, A12). Brightfield is still the bet (A10)."},
    '08': {'Precision to hold.': "The prices are a proposal, not a validated model: free for contributors, about 5 to 15 thousand dollars per line per quarter for screening "
           "groups, a fee per certified lot. One unchecked screen is about 2.6 million, so the subscription is about 170 times less. Bad-lot alerts come after the certificate."},
    '09': {'Figure detail.': "Six real untreated wells, one per lab, with each lab's instrument; across the 13 JUMP labs there are five microscope models, objective NA from "
           "0.4 to 1.0, and eight plate types. The four red-team tiles are one real well corrupted in software and are labelled simulated. The failures to plant: bubble, "
           "focus, exposure, clipped well, bad lot, wrong label."},
    '10': {'Precision to hold.': f"Price and test-set budget are not set: say \"per line, per quarter\" and \"the proof of concept sets the size\". Don't name a partner lab "
           f"until one has agreed. Name no JUMP lab beyond its number. The {word(len(failed))} failed batches are one lab's, {failed_plates} plates; the data cannot say whether "
           "the compounds were left out or the plate map is wrong, so say neither. Next it tells you what to change; then it flags a bad lot across every lab using it."},
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
    head = {'06': 'Know on day one, not month four'}.get(slide, title)
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
