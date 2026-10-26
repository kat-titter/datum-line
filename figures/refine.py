"""Last pass over the hand-built slides 02 and 03 (26 Oct 2026, Kat: "always explain where core key numbers come from"): each
key number on stage gets a short source line in the foot slot every builder slide uses (bottom left, bottom:44, Plex Mono 15px).
Idempotent: each line is redrawn on every build."""
import json
import re

import parts
from parts import MONO, MUTE, SANS, results
from appendix import SCREEN

SLOT = (f'position:absolute; left:56px; bottom:44px; width:1010px; z-index:6; {MONO} line-height:1.5; color:{MUTE};')


def _template(deck, tid, fn):
    m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
    return deck if not m else deck[:m.start()] + fn(m.group(0)) + deck[m.end():]


def _line(cls, stage):
    return f'<div class="src {cls}" style="{SLOT}">{parts.source(stage)}</div>'


def sources(deck):
    runs, weeks, run = SCREEN
    e1 = results('e1.json')['all_sources']
    lines = {
        # 02c: the guess card's $100,000s and months
        't1': ('s s2', f'$100,000s: about ${run}k a screening run (author&#8217;s screens)'),
        # 03b: the classifier's score and chance; shown on the reveal only (.stat is 03's second view)
        't2': ('stat', f'{100 * e1["balanced_accuracy"]:.1f}%: plates the model never saw; chance 1 in {e1["n_labs"]}'),
    }
    for tid, (cls, stage) in lines.items():
        def put(s, cls=cls, stage=stage):
            s = re.sub(r'<div class="src [^"]*" style="[^"]*"><span class="talk"[^>]*>.*?</span></div>', '', s)
            i = s.rindex('</div>', 0, s.rindex('</template>'))           # inside the slide's root, so its view classes apply
            return s[:i] + _line(cls, stage) + s[i:]
        deck = _template(deck, tid, put)
    return deck


# green as text: the brand green #0f8f6c reads 3.5 to 4.1:1 as small text on the deck's light grounds (paper, card, plot
# panel); text takes a deeper green of the same hue, #0c7559, at least 4.6:1 on all of them. Fills, bars, dots and strokes
# keep the brand green (they need 3:1). 26 Oct 2026, page-legibility-check over every view.
GREEN, GREEN_TEXT = '#0f8f6c', '#0c7559'


def green_text(deck):
    deck = re.sub(r'(?<![\w-])color:\s*%s' % GREEN, 'color:' + GREEN_TEXT, deck)                       # CSS text colour only
    return re.sub(r'<text\b[^>]*>', lambda m: m.group(0).replace(f'fill="{GREEN}"', f'fill="{GREEN_TEXT}"'), deck)   # SVG labels


def chance_grey(deck):
    """03b's chance number was #c3c9cb, 1.6:1; large text needs 3:1, so it takes #7d8588 (3.5:1) and still reads fainter."""
    return _template(deck, 't2', lambda s: re.sub(r'(font-size:96px;[^"]*color:)#c3c9cb(;">\d+%<)', r'\1#7d8588\2', s))


# 26 Oct, second declutter (Kat: "declutter didnt change enough"): what the stage repeats goes to the reader's layer
SCALE_LABEL = re.compile(r'(<div class="(?:bar|scalebar)" style="[^"]*">)<span style="([^"]*)">(\d+) &#181;m</span>')


def fewer_words(deck):
    def t1(s):      # 02c: the email's 'To:' and subject lines, and the RUN IT / WAIT words: the cards' icons and numbers say it
        s = s.replace('<span style="' + MONO + ' font-size:13px; color:#666e72;">To: authors, U2OS paper</span>',
                      '<span class="pdf" style="' + MONO + ' font-size:13px; color:#666e72;">To: authors, U2OS paper</span>')
        s = s.replace('<span style="' + SANS + ' font-size:17px; line-height:1.45; color:#454c50;">Subject: do my U2OS cells look right?</span>',
                      '<span class="pdf" style="' + SANS + ' font-size:17px; line-height:1.45; color:#454c50;">Subject: do my U2OS cells look right?</span>')
        return re.sub(r'<span style="(' + re.escape(MONO) + r' font-size:18px; letter-spacing:0.08em; text-transform:uppercase; color:#[0-9a-f]{6};)">(run it|wait)</span>',
                      r'<span class="pdf" style="\1">\2</span>', s)

    def t2(s):      # 03: one scale-bar label in the figure legend instead of eleven
        um = {m.group(3) for m in SCALE_LABEL.finditer(s)}
        assert len(um) <= 1, f'scale bars of different lengths: {um}'
        s = SCALE_LABEL.sub(lambda m: m.group(1) + '<span class="pdf" style="' + m.group(2) + '">' + m.group(3) + ' &#181;m</span>', s)
        s = re.sub(r'<span class="talk bars">.*?</span>', '', s)
        if um:
            s = re.sub(r'(<div class="stain-cap"[^>]*><div class="stain"[^>]*>.*?)(</div>)',
                       lambda m: m.group(1) + f'<span class="talk bars">bars {um.pop()} &#181;m</span>' + m.group(2), s, count=1, flags=re.S)
        # biosecurity stays on stage (Kat, 26 Oct: "biosecurity, decentralization, data as product, are all very important parts of
        # pitch"); this clears the reader-only copy an earlier build of this pass left
        return re.sub(r'<div class="bio pdf"[^>]*>.*?</div>', '', s, flags=re.S)
    return _template(_template(deck, 't1', t1), 't2', t2)


def apply(deck):
    return chance_grey(green_text(fewer_words(sources(deck))))
