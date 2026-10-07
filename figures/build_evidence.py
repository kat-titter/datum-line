"""Write the evidence slides into the deck from results/*.json. Run from the repository root:

    PYTHONPATH=figures python figures/build_evidence.py [index.html]

Each slide is written whole, so the builder can be run again after any analysis changes.
"""
import sys

import parts
import slide01
import slide05
import slide06
import slide07
import slide08
import slide09
import slide10
import appendix
import coherence

deck_path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
out_path = sys.argv[2] if len(sys.argv) > 2 else deck_path
deck = open(deck_path).read()

css, body, _ = slide01.build()
deck = parts.install(deck, 't0', css, body)

css, body, steps = slide05.build()
deck = parts.install(deck, 't4', css, body)
deck, names = parts.set_meta(deck, 'Map', steps)

for tid, module in (('t5', slide06), ('t6', slide07), ('t7', slide08), ('t8', slide09), ('t9', slide10)):
    css, body, steps = module.build()
    deck = parts.install(deck, tid, css, body)
    if steps:
        deck, names = parts.set_meta(deck, 'Product', steps)

for tid, board in (('t14', appendix.a4), ('t17', appendix.a7), ('t18', appendix.a8), ('t19', appendix.a9)):
    css, body, _ = board()
    deck = parts.install(deck, tid, css, body)
for name, board, after in (('Replay', appendix.a11, 'Brightfield'), ('Moved', appendix.a12, 'Replay'),
                           ('OverTime', appendix.a13, 'Moved'), ('Frame', appendix.a14, 'OverTime'),
                           ('Leaderboard', appendix.a17, 'TestSet'), ('Private', appendix.a18, 'Leaderboard'), ('Technology', appendix.a19, 'Private'), ('Biosecurity', appendix.a20, 'Technology'), ('Preseed', appendix.a21, 'Biosecurity'), ('Market', appendix.a22, 'Preseed')):
    deck, names = parts.set_meta(deck, name, None, after=after)
    css, body, _ = board()
    deck = parts.install(deck, f't{names.index(name)}', css, body)
deck = appendix.patch(deck)

deck, report = coherence.apply(deck)
print('coherence:', len(report), 'edits')

open(out_path, 'w').write(deck)
print('written', out_path, len(deck) // 1024, 'KB;', len(names), 'slides')
