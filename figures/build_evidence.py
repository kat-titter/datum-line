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
import slide02
import slide03
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
stored = open(src).read()

def assemble(deck, talk):
    """Every slide and board written into the stored deck, then the wording passes. talk=False is the archive, with every view;
    talk=True is the pitch: slide 02 ends on its third view and slide 04 keeps the map and the drift (17 Nov 2026, Kat: "pitch
    should be pitch, appendix link out to supporting science and figures")."""
    css, body, _ = slide01.build()
    deck = parts.install(deck, 't0', css, body)

    # 26 Oct 2026: problem, proof, then product. Slot names stay (they key META and the boards); what fills them moved:
    # 04 the map, known drugs, the flagged batches; 05 the product; 06 the network effect; 07 the market and why now.
    for tid, name, build in (('t3', 'Map', lambda: slide04.build(talk)), ('t4', 'Controls', slide07.build), ('t5', 'Tightens', slide06.build_density),
                             ('t6', 'Product', slide06.build_economy), ('t7', 'Compare', slide08.build), ('t8', 'Milestones', slide09.build), ('t9', 'Ask', slide10.build)):
        css, body, steps = build()
        deck = parts.install(deck, tid, css, body)
        deck, names = parts.set_meta(deck, name, steps)      # clicks come from the slide itself; none means one view

    for tid, board in (('t14', appendix.a4), ('t17', appendix.a7), ('t18', appendix.a8), ('t19', appendix.a9), ('t20', appendix.a10)):
        css, body, _ = board()
        deck = parts.install(deck, tid, css, body)
    # 17 Nov 2026 (Kat: "Nonprofit FRO"): board A21's section name was "Preseed"; rename the stored entry, so set_meta finds it and adds none
    assert ('{"name": "Preseed",' in deck) != ('{"name": "First 18 months",' in deck), 'A21: one name, old or new'
    deck = deck.replace('{"name": "Preseed",', '{"name": "First 18 months",', 1)
    for name, board, after in (('Replay', appendix.a11, 'Brightfield'), ('Moved', appendix.a12, 'Replay'),
                               ('OverTime', appendix.a13, 'Moved'), ('Frame', appendix.a14, 'OverTime'),
                               ('Leaderboard', appendix.a17, 'TestSet'), ('Private', appendix.a18, 'Leaderboard'), ('Technology', appendix.a19, 'Private'), ('Biosecurity', appendix.a20, 'Technology'), ('First 18 months', appendix.a21, 'Biosecurity'), ('Market', appendix.a22, 'First 18 months'),
                               ('Buyers', appendix.a15, 'Frame'), ('Worth', appendix.a23, 'Market'), ('Trust', appendix.a24, 'Worth'), ('Shared', appendix.a25, 'Trust')):
        deck, names = parts.set_meta(deck, name, None, after=after)
        css, body, _ = board()
        deck = parts.install(deck, f't{names.index(name)}', css, body)
    deck = appendix.patch(deck)

    # 26 Oct 2026 (Kat: "move 02 and 03 into builders"): 02 and 03 are written by their own builders; the passes below patched their
    # hand-built HTML and no longer see them (held under another id while the passes run, then written whole)
    OWN = (('t1', lambda: slide02.build(talk)), ('t2', slide03.build))
    for tid, _ in OWN:
        deck = deck.replace(f'<template id="{tid}">', f'<template id="held-{tid}">', 1)
    deck, report = coherence.apply(deck)
    print('coherence:', len(report), 'edits')
    deck = refine.apply(deck)
    for tid, build in OWN:
        deck = parts.put_template(deck.replace(f'<template id="held-{tid}">', f'<template id="{tid}">', 1), tid, build())
    if talk:      # slide 02's views are named in coherence.FOUNDER_STEPS; the talk has the first three
        deck, _ = parts.set_meta(deck, 'Founder', {'tag': coherence.FOUNDER_STEPS['tag'][:3]})
    return deck


# 26 Oct, later: twelve appendix slides in all, the index A0 and eleven boards; A7 (STR) joins the archive, since slide 08's DNA
# fingerprint row answers it on stage.
# 26 Oct, later still: 05 gained the repository view, so A15 (who pays) went to the archive to keep 27 pages; 05b names the members
# and 07 their prices
# 1 Nov (Kat: "Google Images, email, cost slide from before ... add it in as problem expansion"): 02 gained a fourth view (02c,
# search, ask, guess), so A14 (labs agree a little more on the same drug, on the map) went to the archive to keep 27 pages: its
# effect is the smallest on the boards, and A9 (the same drug looks less alike in another lab) answers the same question
# 17 Nov 2026 (Kat: "pitch should be pitch, appendix link out to supporting science and figures"): the talk prints no boards; its
# index (appendix.talk_index) links each judge question to the board in the archive, the document or the results file. Until then
# nine boards printed: A3, A9, A10, A18, A19, A20, A21, A22, A24.
KEEP = set()      # codes stay as in the archive; a board that returns here also needs its row in appendix.TALK_INDEX


def trim(deck):
    """The talk deck from the full one: drop the archived boards' templates and META entries, renumber the templates in order, and
    write the talk's own index on A0, linking out (board codes keep their archive numbers, so every citation still finds its board)."""
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
    # 26 Oct (Kat: "re-index slides"): the live boards number A1 to A11 in order, every reference follows; a reference to a board
    # that lives only in the archive reads "archive A6", so it cannot be taken for a live code. Text nodes only (never data URIs).
    live = sorted(KEEP, key=lambda c: int(c[1:])); new = {c: f'A{k + 1}' for k, c in enumerate(live)}
    code = lambda m: new.get(m.group(0)) or (m.group(0) if m.group(0) == 'A0' else 'archive ' + m.group(0))
    retext = lambda t: re.sub(r'(?<=>)([^<>]+)(?=<)', lambda n: re.sub(r'(?<![\w-])A\d{1,2}(?![\w-])', code, n.group(1)), t)
    body = re.sub(r'<template id="t\d+">.*?</template>', lambda m: retext(m.group(0)), body, flags=re.S)
    a0 = re.search(r'<template id="t10">.*?</template>', body, flags=re.S)
    return body[:a0.start()] + appendix.talk_index(a0.group(0)) + body[a0.end():], new


# 17 Nov 2026: every slide and board has an address: archive.html#A7 is board A7, #04 slide 04, #04b its second view. The page's
# script makes one section per slide; this gives each its id and goes to the one in the link, on load and when the hash changes.
# Stripped and added again on every build (the script is stored in the archive, the build's source), so two builds agree.
HOOK, WATCH = 'box.appendChild(st);sec.appendChild(box);', 'secs.forEach(S=>io.observe(S.st));'
ANCHOR_ID = "/*anchor*/sec.id=i<10?String(i+1).padStart(2,'0'):'A'+(i-10);/*/anchor*/"
# 17 Nov, later (Kat: "should link out to each slide (auto-scroll)"): a second click on the link the address already names goes
# again, where the browser fires no hashchange. The jump stays instant: a smooth scroll across twenty slides could not be checked
# in the preview pane, which draws no frames while hidden.
ANCHOR_GO = ("\n/*anchor*/function jump(){const h=location.hash.slice(1),m=h.match(/^(\\d\\d)([a-d])$/),el=document.getElementById(m?m[1]:h);"
             "if(!el)return;el.scrollIntoView({block:'center'});if(m){const S=secs[+m[1]-1];show(S,Math.min(views(S)-1,m[2].charCodeAt(0)-97));}}"
             "\njump();addEventListener('hashchange',jump);"
             "addEventListener('click',e=>{const a=e.composedPath().find(n=>n.tagName==='A');if(a&&a.getAttribute('href')===location.hash)jump();});/*/anchor*/")
FIRST = ("if(i>=10)sec.id='A'+(i-10);", "\nfunction jump(){const el=location.hash.length>1&&document.getElementById(location.hash.slice(1));"
         "if(el)el.scrollIntoView({block:'center'});}\njump();addEventListener('hashchange',jump);")      # as first committed, unmarked


def anchors(deck):
    for old in FIRST:
        deck = deck.replace(old, '')
    deck = re.sub(r'\n?/\*anchor\*/.*?/\*/anchor\*/', '', deck, flags=re.S)
    assert deck.count(HOOK) == 1 and deck.count(WATCH) == 1, 'the page script moved: anchors not added'
    return deck.replace(HOOK, ANCHOR_ID + HOOK, 1).replace(WATCH, WATCH + ANCHOR_GO, 1)


if out_path == 'index.html':
    open(FULL, 'w').write(anchors(assemble(stored, talk=False)))      # the full deck, kept and published as the archive
deck, CODES = trim(anchors(assemble(stored, talk=True)))
open(out_path, 'w').write(deck)
print('written', out_path, len(deck) // 1024, 'KB;', len(json.loads(re.search(r'const META=(\[.*?\]);', deck, flags=re.S).group(1))), 'slides')
