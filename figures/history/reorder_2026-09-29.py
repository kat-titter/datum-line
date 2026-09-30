"""One-off, 29 September 2026: the VC order. Game and Pain before Founder; the map and why it
compounds before the product; who buys and the test set become appendix boards A15 and A16;
two placeholders (t5, t8) are then written whole by build_evidence.py.

Usage:  PYTHONPATH=figures python figures/history/reorder_2026-09-29.py index.html
"""
import json
import re
import sys

from parts import PAGER_RE

path = sys.argv[1]
t = open(path).read()
blocks = re.findall(r'<template id="t\d+">.*?</template>', t, flags=re.S)
m = re.search(r'const META=(\[.*?\]);', t, flags=re.S)
meta = json.loads(m.group(1))
assert len(blocks) == len(meta) == 25 and [e['name'] for e in meta[:10]] == ['Main', 'Founder', 'Pain', 'Game', 'Flow', 'Close', 'Compare', 'Compete', 'Vision', 'Ask']

inner = lambda b: re.match(r'<template id="t\d+">(.*)</template>', b, flags=re.S).group(1)
number = lambda s, old, new: s.replace(f'uppercase; color:#666e72;">{old}', f'uppercase; color:#666e72;">{new}', 1) \
                              .replace(f'uppercase; color:#949c9f;">{old}', f'uppercase; color:#949c9f;">{new}', 1)


def board(s, code, asked):
    """A talk slide as an appendix board: A-number and no pager (no watermark: these roots have no stacking context)."""
    s = PAGER_RE.sub('', s, count=1)
    return re.sub(r'(uppercase; color:#(?:666e72|949c9f);">)\d\d(</span>)', lambda k: f'{k.group(1)}{code} &#183; {asked}{k.group(2)}', s, count=1)


old = {e['name']: (inner(b), e) for b, e in zip(blocks, meta)}
new = [('Main', old['Main']),
       ('Game', (number(old['Game'][0], '04', '02'), old['Game'][1])),
       ('Pain', old['Pain']),
       ('Founder', (old['Founder'][0].replace('">02 &#183; Founder<', '">04 &#183; Founder<'), old['Founder'][1])),
       ('Map', old['Flow']),
       ('Tightens', old['Compete']),                # placeholder, written by build_evidence.py
       ('Product', old['Close']),
       ('Compare', (number(old['Compare'][0], '07', '08'), old['Compare'][1])),
       ('Milestones', old['Vision']),               # placeholder, written by build_evidence.py
       ('Ask', old['Ask'])]
new += [(e['name'], old[e['name']]) for e in meta[10:]]
new += [('Buyers', (board(old['Compete'][0], 'A15', 'if asked who pays'), {'steps': None})),
        ('TestSet', (board(old['Vision'][0], 'A16', 'if asked what the money builds'), {'steps': None}))]

out = t[:t.index(blocks[0])]
out += '\n'.join(f'<template id="t{k}">{s}</template>' for k, (name, (s, e)) in enumerate(new))
out += t[t.index(blocks[-1]) + len(blocks[-1]):]
meta_new = [{'name': name, 'steps': e['steps']} for name, (s, e) in new]
m = re.search(r'const META=(\[.*?\]);', out, flags=re.S)
out = out[:m.start(1)] + json.dumps(meta_new) + out[m.end(1):]
open(path, 'w').write(out)
print([e['name'] for e in meta_new])
