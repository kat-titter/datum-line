"""Last pass over the hand-built slides 02 and 03 (26 Oct 2026, Kat: "always explain where core key numbers come from"): each
key number on stage gets a short source line in the foot slot every builder slide uses (bottom left, bottom:44, Plex Mono 15px).
Idempotent: each line is redrawn on every build."""
import json
import re

import parts
from parts import MONO, MUTE, SANS, results


def _template(deck, tid, fn):
    m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
    return deck if not m else deck[:m.start()] + fn(m.group(0)) + deck[m.end():]


# green as text: the brand green #0f8f6c reads 3.5 to 4.1:1 as small text on the deck's light grounds (paper, card, plot
# panel); text takes a deeper green of the same hue, #0c7559, at least 4.6:1 on all of them. Fills, bars, dots and strokes
# keep the brand green (they need 3:1). 26 Oct 2026, page-legibility-check over every view.
GREEN, GREEN_TEXT = '#0f8f6c', '#0c7559'


def green_text(deck):
    deck = re.sub(r'(?<![\w-])color:\s*%s' % GREEN, 'color:' + GREEN_TEXT, deck)                       # CSS text colour only
    return re.sub(r'<text\b[^>]*>', lambda m: m.group(0).replace(f'fill="{GREEN}"', f'fill="{GREEN_TEXT}"'), deck)   # SVG labels
# slide to slide: each slide comes forward to full size as it reaches the middle of the screen and recedes as it leaves, so the talk
# reads as one surface moving past; scroll-linked, so it follows the reader's own pace (desktop only; off with reduced motion)
DEPTH = ('<style id="dl-depth">@supports (animation-timeline: view()){@media (prefers-reduced-motion: no-preference){'
         'html:not(.narrow) .box{animation:dl-depth linear both;animation-timeline:view();animation-range:cover 0% cover 100%}'
         '@keyframes dl-depth{0%{transform:scale(.92);opacity:.3}38%,62%{transform:none;opacity:1}100%{transform:scale(.92);opacity:.3}}}}</style>')


def motion(deck):
    deck = re.sub(r'<style id="dl-depth">.*?</style>', '', deck, flags=re.S)
    return deck.replace('</head>', DEPTH + '</head>', 1)


def apply(deck):
    # 26 Oct (Kat: "move 02 and 03 into builders"): the passes that patched 02 and 03 (sources, fewer_words, normal_defined,
    # chance_grey, overlays_hide_team, talk_last, chance_tick, icon_floor, lab_tags, confusion_grid, tile_channels, real_cells)
    # left the chain; their result is figures/templates/slide02.html and slide03.html, edited there directly
    return bar_labels(doc_links(board_words(colour_meaning(motion(green_text(deck))))))


def colour_meaning(s):
    """26 Oct (Kat: "design cohesion: pink for outlier // single point, green for larger field"). Pink stays on marks for one lab,
    one batch, one well or one flagged point (and the progress bar's "you are here"); everything that was pink only for emphasis
    or decoration turns green (headline accents, the field), grey (titles, rules, borders) or ink."""
    import re
    n = {}
    def sub(pat, rep, s, key, flags=0):
        s2, k = re.subn(pat, rep, s, flags=flags); n[key] = k; return s2
    # headline accents: the second line of every headline is green, as on the talk slides
    s = sub(r'<h2\b[^>]*>.*?</h2>', lambda m: re.sub(r'color: ?#be1e74', 'color:#0c7559', m.group(0)), s, 'h2', re.S)
    # 02b: "normal" is the field's word
    s = sub(r'<span style="color:#be1e74; font-weight:(\d+);">&#8220;normal&#8221;</span>', r'<span style="color:#0c7559; font-weight:\1;">&#8220;normal&#8221;</span>', s, 'normal')
    # small uppercase titles of cards, boxes and charts: grey like every other chart title
    s = sub(r'color: ?#666e72; color: ?#be1e74;', 'color:#666e72;', s, 'title2')
    s = sub(r'text-transform: ?uppercase; color: ?#be1e74;', 'text-transform:uppercase; color:#666e72;', s, 'title')
    # accent stripes and card borders: decoration, so neutral
    s = sub(r'linear-gradient\(90deg, ?#be1e74, ?#0f8f6c\)', 'linear-gradient(90deg, #d3d8da, #d3d8da)', s, 'stripe')
    s = sub(r'linear-gradient\(90deg, #ef74ad, #3fe0a0\) border-box', 'linear-gradient(90deg, #454c50, #454c50) border-box', s, 'border')
    # the corner glow: the field's light, not pink
    s = sub(r'rgba\(190,30,116,0\.07\)', 'rgba(15,143,108,0.06)', s, 'glow')
    s = sub(r'rgba\(239,116,173,0\.16\)', 'rgba(63,224,160,0.10)', s, 'glow_dark')
    # links, footnotes, the collaborators line, money rows: ink
    s = sub(r'a \{ color: #be1e74; \}', 'a { color: #454c50; }', s, 'link')
    s = sub(r'(font-size: ?15px; line-height: ?1\.45; color: ?)#be1e74;', r'\g<1>#454c50;', s, 'foot')
    s = sub(r'(line-height:1\.35; color:)#be1e74;(">Broad Institute)', r'\1#454c50;\2', s, 'collab')
    s = sub(r'(font-size:17px; font-weight:700; color:)#be1e74;', r'\1#14171a;', s, 'money')
    # A1: the variables nobody records are not outliers; a dashed grey chip says "missing"
    s = sub(r'border: 1\.5px solid #be1e74;', 'border: 1.5px dashed #949c9f;', s, 'chips')
    for left in ('rgba(190,30,116,0.07)', 'linear-gradient(90deg, #be1e74', 'a { color: #be1e74; }', 'border: 1.5px solid #be1e74;'):
        assert left not in s, left      # idempotent: archive.html is read back, so later builds find nothing left to change
    print('colour_meaning:', ', '.join(f'{k} {v}' for k, v in n.items()))
    return s


def board_words(s):
    """26 Oct, half the words on the boards: the eyebrow keeps the board's code and its slide (the question is A0's line and the
    headline answers it); A1's lede keeps one sentence (A0's is trim()'s)."""
    import re
    s = re.sub(r'>(A\d+), if asked [^<]*?, from slide (\d+)<', r'>\1, from slide \2<', s)
    s = s.replace('What counts as &#8220;normal&#8221; depends on every variable below.<br>JUMP records the left column; nobody records the middle.',
                  'JUMP records the left column; nobody records the middle.')
    return s


DOCS = 'https://kat-titter.github.io/datum-line/docs/'


def doc_links(s):
    """26 Oct (Kat: "public pitch decks should link to public supporting docs: landscape, etc"): each slide with a document behind it
    links it in the bottom-right corner, left of the view dots; absolute URLs, so the PDF's links work too."""
    import re
    where = {3: ('whitepaper.html', 'white paper', True), 4: ('product-vision.html', 'product vision', True),
             7: ('landscape.html', 'landscape', False), 8: ('roadmap.html', 'roadmap', False), 9: ('', 'all documents', False)}
    s = s.replace("monospace; font-size:16px; color:#c9cfd1; text-decoration:none;", "monospace; font-size:22px; color:#c9cfd1; text-decoration:none;")
    s = s.replace("monospace; font-size:18px; color:#c9cfd1; text-decoration:none;", "monospace; font-size:22px; color:#c9cfd1; text-decoration:none;")      # links already placed
    s = s.replace("monospace; font-size:16px; color:#454c50; text-decoration:none;", "monospace; font-size:22px; color:#454c50; text-decoration:none;")
    s = s.replace("monospace; font-size:18px; color:#454c50; text-decoration:none;", "monospace; font-size:22px; color:#454c50; text-decoration:none;")
    for i, (page, name, dark) in where.items():
        t0 = s.find(f'<template id="t{i}">'); t1 = s.find('</template>', t0); t = s[t0:t1]
        if 'class="doc"' in t:
            continue
        m = re.search(r'<div[^>]*width:1280px; height:720px;[^>]*>', t)
        link = (f'<a class="doc" href="{DOCS}{page}" target="_blank" rel="noopener" style="position:absolute; right:104px; bottom:15px; z-index:7; '
                f'font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:22px; color:{"#c9cfd1" if dark else "#454c50"}; text-decoration:none;">{name} {parts.arrow()}</a>')
        t = t[:m.end()] + link + t[m.end():]
        s = s[:t0] + t + s[t1:]
    return s


def bar_labels(s):
    """26 Oct (legibility): white labels on the deck's green bars use the text-safe green behind them (AA 4.5:1); boards A10 etc."""
    import re
    return re.sub(r'(<rect [^>]*?)fill="#0f8f6c"(/>)(?=(?:<path[^>]*/>)?<text [^>]*fill="#ffffff")', r'\1fill="#0c7559"\2', s)
