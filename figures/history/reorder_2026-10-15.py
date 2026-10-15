"""One-off, 15 October 2026: the founder opens. Founder before the game, so the question lands as the founder's
punchline (coherence.reveal); the map moves to 04; a placeholder at 05 is then written whole by build_evidence.py
(does my control look like yours?); the pain slide ("Today: search, ask, guess") becomes appendix board A25.

Usage:  PYTHONPATH=figures python figures/history/reorder_2026-10-15.py index.html
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
assert len(blocks) == len(meta) == 35 and [e['name'] for e in meta[:10]] == ['Main', 'Game', 'Pain', 'Founder', 'Map', 'Tightens', 'Product', 'Compare', 'Milestones', 'Ask']

inner = lambda b: re.match(r'<template id="t\d+">(.*)</template>', b, flags=re.S).group(1)
number = lambda s, old, new: s.replace(f'uppercase; color:#666e72;">{old}', f'uppercase; color:#666e72;">{new}', 1)


def board(s, code, asked):
    """A talk slide as an appendix board: A-number and no pager."""
    s = PAGER_RE.sub('', s, count=1)
    return re.sub(r'(uppercase; color:#(?:666e72|949c9f);">)\d\d(</span>)', lambda k: f'{k.group(1)}{code} &#183; {asked}{k.group(2)}', s, count=1)


old = {e['name']: (inner(b), e) for b, e in zip(blocks, meta)}
founder = old['Founder'][0]
assert founder.count('">04 &#183; Founder<') == 1
game = old['Game'][0]
assert game.count('uppercase; color:#666e72;">02') == 1
new = [('Main', old['Main']),
       ('Founder', (founder.replace('">04 &#183; Founder<', '">02 &#183; Founder<'), old['Founder'][1])),
       ('Game', (number(game, '02', '03'), old['Game'][1])),
       ('Map', old['Map']),                                        # written whole by build_evidence.py (slide04.py)
       ('Controls', ('<style></style><div></div>', {'steps': None})),  # placeholder, written by build_evidence.py (slide05.py)
       ('Tightens', old['Tightens']), ('Product', old['Product']), ('Compare', old['Compare']),
       ('Milestones', old['Milestones']), ('Ask', old['Ask'])]
new += [(e['name'], old[e['name']]) for e in meta[10:]]
new += [('Pain', (board(old['Pain'][0], 'A25', 'if asked how labs answer it today'), {'steps': None}))]

out = t[:t.index(blocks[0])]
out += '\n'.join(f'<template id="t{k}">{s}</template>' for k, (name, (s, e)) in enumerate(new))
out += t[t.index(blocks[-1]) + len(blocks[-1]):]
meta_new = [{'name': name, 'steps': e['steps']} for name, (s, e) in new]
m = re.search(r'const META=(\[.*?\]);', out, flags=re.S)
out = out[:m.start(1)] + json.dumps(meta_new) + out[m.end(1):]
open(path, 'w').write(out)
print([e['name'] for e in meta_new])
