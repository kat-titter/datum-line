"""Write the evidence slides into the deck from results/*.json. Run from the repository root:

    PYTHONPATH=figures python figures/build_evidence.py [index.html]

Each slide is written whole, so the builder can be run again after any analysis changes.
"""
import os
import re
import json
import sys

import parts
import slide01
import slide04
import slide05
import slide06
import slide07
import slide08
import slide09
import slide10
import appendix
import coherence
import refine

deck_path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
out_path = sys.argv[2] if len(sys.argv) > 2 else deck_path
# 26 Oct 2026 (Kat: "12 appendix slides, the rest archive"): archive.html is the full deck, every board, and the build's source;
# index.html is the talk, the index and the twelve boards a judge is most likely to ask for (trim() below)
FULL = 'archive.html'
src = FULL if deck_path == 'index.html' and os.path.exists(FULL) else deck_path
deck = open(src).read()

css, body, _ = slide01.build()
deck = parts.install(deck, 't0', css, body)

# 26 Oct 2026: problem, proof, then product. Slot names stay (they key META and the boards); what fills them moved:
# 04 the map, known drugs, the flagged batches; 05 the product; 06 the network effect; 07 the market and why now.
for tid, name, build in (('t3', 'Map', slide04.build), ('t4', 'Controls', slide07.build), ('t5', 'Tightens', slide06.build_density),
                         ('t6', 'Product', slide06.build_economy), ('t7', 'Compare', slide08.build), ('t8', 'Milestones', slide09.build), ('t9', 'Ask', slide10.build)):
    css, body, steps = build()
    deck = parts.install(deck, tid, css, body)
    deck, names = parts.set_meta(deck, name, steps)      # clicks come from the slide itself; none means one view

for tid, board in (('t14', appendix.a4), ('t17', appendix.a7), ('t18', appendix.a8), ('t19', appendix.a9), ('t20', appendix.a10)):
    css, body, _ = board()
    deck = parts.install(deck, tid, css, body)
for name, board, after in (('Replay', appendix.a11, 'Brightfield'), ('Moved', appendix.a12, 'Replay'),
                           ('OverTime', appendix.a13, 'Moved'), ('Frame', appendix.a14, 'OverTime'),
                           ('Leaderboard', appendix.a17, 'TestSet'), ('Private', appendix.a18, 'Leaderboard'), ('Technology', appendix.a19, 'Private'), ('Biosecurity', appendix.a20, 'Technology'), ('Preseed', appendix.a21, 'Biosecurity'), ('Market', appendix.a22, 'Preseed'),
                           ('Buyers', appendix.a15, 'Frame'), ('Worth', appendix.a23, 'Market'), ('Trust', appendix.a24, 'Worth'), ('Shared', appendix.a25, 'Trust')):
    deck, names = parts.set_meta(deck, name, None, after=after)
    css, body, _ = board()
    deck = parts.install(deck, f't{names.index(name)}', css, body)
deck = appendix.patch(deck)

deck, report = coherence.apply(deck)
print('coherence:', len(report), 'edits')
deck = refine.apply(deck)                         # 26 Oct: stage source lines on the hand-built slides 02 and 03

# 26 Oct, later: twelve appendix slides in all, the index A0 and eleven boards; A7 (STR) joins the archive, since slide 08's DNA
# fingerprint row answers it on stage
KEEP = {'A3', 'A9', 'A10', 'A14', 'A15', 'A18', 'A19', 'A20', 'A21', 'A22', 'A24'}      # codes stay as in the archive


def trim(deck):
    """The talk deck from the full one: drop the archived boards' templates and META entries, renumber the templates in order, and
    drop their rows from the index board A0 (board codes keep their archive numbers, so every citation still finds its board)."""
    m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S); meta = json.loads(m.group(1))
    code = lambda i: f'A{i - 10}' if i > 10 else ''
    keep = [i for i in range(len(meta)) if i <= 10 or code(i) in KEEP]
    temps = {int(t.group(1)): t.group(0) for t in re.finditer(r'<template id="t(\d+)">.*?</template>', deck, flags=re.S)}
    first = min(t.start() for t in re.finditer(r'<template id="t\d+">', deck))
    body = deck
    for t in temps.values():
        body = body.replace(t, '', 1)
    out = ''.join(re.sub(r'^<template id="t\d+">', f'<template id="t{k}">', temps[i]) for k, i in enumerate(keep))
    body = body[:first] + out + body[first:]
    m = re.search(r'const META=(\[.*?\]);', body, flags=re.S)
    body = body[:m.start(1)] + json.dumps([meta[i] for i in keep]) + body[m.end(1):]
    gone = {code(i) for i in range(11, len(meta)) if code(i) not in KEEP}
    a0 = re.search(r'<template id="t10">.*?</template>', body, flags=re.S)
    t = a0.group(0)
    # the kept rows, re-flowed into three even columns in code order (deleting rows in place left them 2, 3 and 6 deep)
    rows = [r for r in re.finditer(r'<div class="c" style="display:grid; grid-template-columns:40px[^"]*"><span style="[^"]*">(A\d+)</span><div[^>]*>.*?</div></div>',
                                   t, flags=re.S) if r.group(1) not in gone]
    n = len(rows); sizes = [n // 3 + (i < n % 3) for i in range(3)]; cuts = [sum(sizes[:i]) for i in range(4)]
    g = t.index('<div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr));'); g = t.index('>', g) + 1
    end = t.rindex('</div></div></template>')
    t = t[:g] + ''.join('<div>' + ''.join(r.group(0) for r in rows[cuts[i]:cuts[i + 1]]) + '</div>' for i in range(3)) + t[end:]
    t = t.replace('>25 boards<', f'>{len(KEEP)} boards<')
    t = t.replace('Every number comes from the code here or a cited source.<br>Unfinished work is marked pending.',      # 26 Oct, half the words
                  'Every number: the code here or a cited source.<br>All 25 boards: archive.html')
    body = body[:a0.start()] + t + body[a0.end():]
    # 26 Oct (Kat: "re-index slides"): the live boards number A1 to A11 in order, every reference follows; a reference to a board
    # that lives only in the archive reads "archive A6", so it cannot be taken for a live code. Text nodes only (never data URIs).
    live = sorted(KEEP, key=lambda c: int(c[1:])); new = {c: f'A{k + 1}' for k, c in enumerate(live)}
    code = lambda m: new.get(m.group(0)) or (m.group(0) if m.group(0) == 'A0' else 'archive ' + m.group(0))
    retext = lambda t: re.sub(r'(?<=>)([^<>]+)(?=<)', lambda n: re.sub(r'(?<![\w-])A\d{1,2}(?![\w-])', code, n.group(1)), t)
    return re.sub(r'<template id="t\d+">.*?</template>', lambda m: retext(m.group(0)), body, flags=re.S), new


if out_path == 'index.html':
    open(FULL, 'w').write(deck)                    # the full deck, kept and published as the archive
deck, CODES = trim(deck)
open(out_path, 'w').write(deck)
print('written', out_path, len(deck) // 1024, 'KB;', len(json.loads(re.search(r'const META=(\[.*?\]);', deck, flags=re.S).group(1))), 'slides')
