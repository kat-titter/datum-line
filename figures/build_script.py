"""Speaker script: the lines that carry numbers, written from results/*.json.

Paragraphs are found by their timestamp or label inside a slide's section and replaced
whole, so this can be run again after any analysis changes. Everything else in the script
is left as written.

Usage:  python figures/build_script.py
"""
import json
import re
from datetime import date

R = 'results'
e1 = json.load(open(f'{R}/e1.json'))['all_sources']
rt = json.load(open(f'{R}/e1-redteam.json'))['tests']
replay = json.load(open(f'{R}/e9-replay.json'))['labs']
B = replay['source_2']['batches']
e6 = json.load(open(f'{R}/e6-what-moved-source_2-first-flag.json'))
e10 = json.load(open(f'{R}/e10-certificate-predicts-answer.json'))
e11 = json.load(open(f'{R}/e11-known-answer.json'))
drift = json.load(open(f'{R}/e1b-drift-source_2.json'))

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
two = e10['flagged_against_unflagged']['source_2']['with_own_baseline']
inten = sorted([g for g in e6['groups'] if g['measurement'] == 'Intensity'], key=lambda g: -abs(g['mean_shift']))
n_all = sum(v['n_batches'] for v in replay.values()); n_out = sum(v['batches_outside'] for v in replay.values())
failed = e11['failed']
far = drift['bins'][-1]
acc, centred = f"{100 * e1['balanced_accuracy']:.1f}", f"{100 * rt['plate_centred']['balanced_accuracy']:.0f}"
held = ', '.join(str(b['n_plates']) for b in out[:-1]) + f' and {out[-1]["n_plates"]}'

LINES = {
    '04': {
        '1:28': f"Why now: this data is public, {word(e1['n_labs'])} labs, free, and embeddings are a commodity. Same-size nuclei, different texture: "
                f"that's what moves the point. The model isn't the hard part. The reference is. <em>Click.</em>",
    },
    '05': {
        '1:45': f"One lab, {word(len(B))} batches, June to October. Cells per well stay in range. On {day(low['date'])} they dip, and the lab can see that. "
                f"After that, nothing to see. <em>Click.</em>",
        '1:52': f"The same batches, placed against the field. At the end of August the pink line crosses the green: this lab is now further from its own "
                f"June baseline than from another lab. By October, {last['from_baseline']:.1f} spreads from itself and {last['to_nearest_other']:.1f} from "
                f"{lab(last['nearest_other'])}. Every well is still recognisably lab 2. <em>Click.</em>",
        '2:02': f"Here is the map: every untreated well, one shade of green per lab. June and October are different places. Two plates of this lab sit "
                f"{word(round(far['ratio_to_same_batch']))} times further apart after thirteen weeks than inside one batch. Your own past is not a reference. "
                f"The field is. <em>Click.</em>",
        'Fourth click, if there is time.': f"The same drug, a different answer. Every point is one batch of one lab. The further a batch has drifted from its "
                f"lab's baseline, the less its answers to the same drugs agree with that baseline: rho minus {abs(own['spearman']):.2f}, {own['n_batches']} batches, "
                f"{word(own['n_labs'])} labs. Lab 2's agreement with its own June answer: {two['unflagged']:.2f} before the flag, {two['flagged']:.2f} after. "
                f"That is the failure I lived: profiles that would not align to the field's reference. <em>Click.</em>",
        'For ML people.': f"The line is on the board in the second state of 04. Centring each plate on its own controls takes lab identity from {acc} to "
                f"{centred} percent: right for discovery, wrong for QC. On the fourth click of 05, the correlation is inside labs, after removing each lab's mean. "
                f"In lab 2 the flagged batches are also the last three, so inside that lab the flag and the calendar cannot be separated. "
                f"The crosses are batches whose positive controls show no effect (A8); they are not drift.",
    },
    '06': {
        '2:20': "The product: the control-well images you already take. They stay yours. We place them against the field. One answer in a day: "
                "in or out, and which features moved.",
        '2:35': f"Here it is, replayed on lab 2. {word(len(B)).capitalize()} batches, each judged with only what was known that day. "
                f"The first sets the baseline. {word(len(B) - len(out) - 1).capitalize()} come back in distribution. On {day(flag['date'])} it says outside: {word(weeks)} weeks before the "
                f"October batch was run. And it says where to look: {inten[0]['channel']} and {inten[1]['channel']} stain intensity, up almost "
                f"{word(round(inten[0]['mean_shift']))} standard deviations. Cell count unchanged. Four months becomes one day. <em>Click.</em>",
        'Precision to hold.': f"The replay is hindsight on public data, against the field as published. The flagged batches hold {held} plates. "
                f"The certificate says where to look, not why. Across the field {n_out} of {n_all} batches flag, and lab 2's verdicts hold under nine of ten "
                f"variants (A11, A12). Brightfield is still the bet (A10).",
    },
    '10': {
        '3:35': f"That's the vision, and here it is on public data: {n_all} batches, {word(len(replay))} labs, every one replayed. {word(n_out).capitalize()} sit "
                f"outside their own baseline. In {word(len(failed))}, the known answer did not come out. Every certificate adds a plate to the reference, and the "
                f"reference is the moat: nobody can build it alone.",
        'Precision to hold.': f"Price and test-set budget are not set: say \"per line, per quarter\" and \"the proof of concept sets the size\". Don't name a "
                f"partner lab until one has agreed. Name no JUMP lab beyond its number. The {word(len(failed))} failed batches are one lab's, "
                f"{sum(f['n_plates'] for f in failed)} plates; the data cannot say whether the compounds were left out or the plate map is wrong, so say neither.",
    },
}
CUES = {
    '05': '<em>How. Dark slide: slow down. Four views of one lab.</em>',
    '06': '<em>What. Read the sentence under the headline. Then the strip, left to right: thirteen uploads. Then the certificate for the first flag.</em>',
    '10': '<em>Vision, then the ask. Point at the grid: every batch of every lab. Then the right card.</em>',
}
HEADINGS = {'05': 'It passed every check (1:45&#8211;2:20, four views)'}

path = 'docs/speaker-script.html'
s = open(path).read()
for slide, lines in LINES.items():
    m = re.search(r'<h3><span class="sn">%s</span>.*?(?=<h3>|<h2|</main>|</body>)' % slide, s, flags=re.S)
    sec = m.group(0)
    if slide in HEADINGS:
        sec = re.sub(r'(<h3><span class="sn">%s</span>).*?(</h3>)' % slide, lambda k: k.group(1) + HEADINGS[slide] + k.group(2), sec, count=1, flags=re.S)
    if slide in CUES:
        sec = re.sub(r'(</h3>\s*<p>)<em>.*?</em>(</p>)', lambda k: k.group(1) + CUES[slide] + k.group(2), sec, count=1, flags=re.S)
    last_p = None
    for key, line in lines.items():
        pat = re.compile(r'<p><strong>%s</strong>.*?</p>' % re.escape(key), flags=re.S)
        new = f'<p><strong>{key}</strong> {line}</p>'
        if pat.search(sec):
            sec = pat.sub(lambda _: new, sec, count=1)
        else:                                   # a new note goes at the end of the slide's section
            sec = sec.rstrip() + '\n' + new + '\n\n'
    s = s[:m.start()] + sec + s[m.end():]
s = re.sub(r'(<td>05 It passed every check</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>)[^<]*(</td>)', r'\g<1>3\2', s)
# the run of show states the real length
timed = re.findall(r'<p><strong>\d:\d\d</strong>(.*?)</p>', s, flags=re.S)
n_words = sum(len(re.sub(r'<[^>]+>', ' ', re.sub(r'<em>.*?</em>', '', x)).split()) for x in timed)
s = re.sub(r'about \d+ spoken words(?:, [^.]*?a minute)?', f'about {round(n_words, -1)} spoken words, {n_words / 150:.1f} minutes at 150 words a minute', s, count=1)
open(path, 'w').write(s)
print('script written:', sum(len(v) for v in LINES.values()), 'lines from results')
