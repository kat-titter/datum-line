"""Appendix A9 and slide 04's caption, from results/e8-redteam.json and results/e1.json.
A9 reports e8 with each plate compared with every lab but its own, the same definition
slide 05 uses, so the two agree.

Usage:  python figures/build_a9.py index.html
"""
import json
import re
import sys

path = sys.argv[1]
t = open(path).read()
e8 = json.load(open('results/e8-redteam.json')); C = e8['all_features']['compounds']; P = e8['all_features']['pooled_within_lab_and_compound']
e1 = json.load(open('results/e1.json'))['all_sources']
own = [v['agreement_with_own_lab'] for v in C.values()]; other = [v['agreement_with_other_labs'] for v in C.values()]
strong = [c for c, v in C.items() if v['within_labs']['p_permutation'] < 0.01 and v['effect_size']['cv_of_lab_means_pct'] < 100]
weak = [c for c in C if c not in strong]
rho = [C[c]['within_labs']['spearman'] for c in strong]
cvb = [C[c]['effect_size']['cv_of_lab_means_pct'] for c in strong]; cvw = [C[c]['effect_size']['median_cv_within_lab_pct'] for c in strong]
best = max(C, key=lambda c: C[c]['agreement_with_own_lab'])

seg = re.search(r'<template id="t19">.*?</template>', t, flags=re.S); s = seg.group(0)
cards = re.findall(r'(<span style="[^"]*font-size:\s*13px[^"]*color:\s*#666e72[^"]*">)([^<]*(?:Every compound agrees|Yes for the five|The same compound, measured)[^<]*)(</span>)', s)
assert len(cards) == 3, len(cards)
new = [f'Every compound agrees less with other labs: own lab {min(own):.2f} to {max(own):.2f}, other labs {min(other):.2f} to {max(other):.2f}. {best} {C[best]["agreement_with_own_lab"]:.2f} against {C[best]["agreement_with_other_labs"]:.2f}.',
       f'Inside labs, yes: Spearman {min(rho):.2f} to {max(rho):.2f} for {len(strong)} compounds; pooled {P["spearman"]:.2f}, shuffled {P["null_mean"]:.2f}. Between {e8["n_labs"]} labs: same sign, not established.',
       f'Effect size differs {min(cvb):.0f}% to {max(cvb):.0f}% between labs, {min(cvw):.0f}% to {max(cvw):.0f}% inside one. {" and ".join(weak)} are too weak to measure.']
for (a, old, b), n in zip(cards, new):
    s = s.replace(a + old + b, a + n + b)
s = re.sub(r'Q2 is positive: your answers differ\.[^<]*', f'Q2 is positive inside every lab: your answers differ. {e8["n_plates"]} plates, 25 per lab, {e8["n_labs"]} labs; each plate against every lab but its own.', s)
s = s.replace('analysis/e8_same_drug_different_answer.py.', 'analysis/e8_same_drug_different_answer.py, analysis/e8_redteam.py.')
t = t[:seg.start()] + s + t[seg.end():]

# slide 04: a one-line caption, so the footer line above it stays clear
seg = re.search(r'<template id="t3">.*?</template>', t, flags=re.S); s = seg.group(0)
s, n = re.subn(r'JUMP cpg0016 \(CC0\) \[7\]\. Images: untreated wells.*?results/e1',
               f'JUMP cpg0016 (CC0) [7] &#183; {e1["n_wells"]:,} untreated wells, {e1["n_labs"]} labs, held out by plate &#183; {100 * e1["balanced_accuracy"]:.1f}% vs chance {100 * e1["chance"]:.1f}% &#183; results/e1', s, flags=re.S)
assert n == 1
t = t[:seg.start()] + s + t[seg.end():]
open(path, 'w').write(t)
print('A9 and the slide 04 caption rebuilt;', len(strong), 'strong compounds, weak:', weak)
