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
        't1': ('s s2', ''),      # 26 Oct, half the words: the reader's layer keeps the source (README 28)
        # 03b: the classifier's score and chance; shown on the reveal only (.stat is 03's second view)
        't2': ('stat', ''),
    }
    for tid, (cls, stage) in lines.items():
        def put(s, cls=cls, stage=stage):
            s = re.sub(r'<div class="src [^"]*" style="[^"]*"><span class="talk"[^>]*>.*?</span></div>', '', s)
            if not stage:
                return s
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


BENCH = parts.ICONS['person']


def benches():
    """02b, shown not told (was "asked @ five benches ... answered @ none"): five people, a "?" over each in turn, then an empty reply."""
    g = []
    for k in range(5):
        x = 40 + 92 * k
        g.append(f'<g transform="translate({x - 24},40) scale(2)" fill="none" stroke="#454c50" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{BENCH}</g>')
        g.append(f'<g class="bq"><circle cx="{x + 22}" cy="30" r="15" fill="#be1e74"/>'
                 f'<text x="{x + 22}" y="37" font-family="Archivo, Helvetica, sans-serif" font-size="20" font-weight="700" fill="#ffffff" text-anchor="middle">?</text></g>')
    g.append('<g class="bq"><path d="M 488 62 H 532" stroke="#949c9f" stroke-width="2"/><path d="M 526 56 L 534 62 L 526 68" fill="none" stroke="#949c9f" stroke-width="2"/>'
             '<rect x="548" y="40" width="96" height="44" rx="14" fill="none" stroke="#949c9f" stroke-width="2" stroke-dasharray="6 6"/>'
             '<text x="596" y="69" font-family="Archivo, Helvetica, sans-serif" font-size="26" fill="#666e72" text-anchor="middle">&#8230;</text></g>')
    css = ('<style id="dl-benches">@keyframes dl-bq{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}'
           '.bq{opacity:0;transform-box:fill-box;transform-origin:center}'
           '.step-1 .bq{animation:dl-bq .4s cubic-bezier(.2,.8,.3,1.25) forwards}'
           + ''.join(f'.step-1 .bq:nth-of-type({k + 1}){{animation-delay:{0.4 + 0.28 * k:.2f}s}}' for k in range(6))
           + '@media (prefers-reduced-motion: reduce){.bq{opacity:1}}</style>')
    return css + ('<div class="benches"><svg viewBox="0 0 660 100" width="660" height="100" role="img" '
                  'aria-label="Five people each ask whether their cells look normal; no answer comes back." style="display:block;">' + ''.join(g) + '</svg></div>')


def to_reader(s, cls):
    """A block the coherence pass redraws each build, moved to the reader's layer: drop last build's copy, then mark the fresh one."""
    s = re.sub(r'<div class="%s pdf".*?</span></span></div>' % cls, '', s, flags=re.S)
    return s.replace(f'<div class="{cls}" style=', f'<div class="{cls} pdf" style=')


def fewer_words(deck):
    def t1(s):      # 02c: the email's 'To:' and subject lines, and the RUN IT / WAIT words: the cards' icons and numbers say it
        s = s.replace('<span style="' + MONO + ' font-size:13px; color:#666e72;">To: authors, U2OS paper</span>',
                      '<span class="pdf" style="' + MONO + ' font-size:13px; color:#666e72;">To: authors, U2OS paper</span>')
        s = s.replace('<span style="' + SANS + ' font-size:17px; line-height:1.45; color:#454c50;">Subject: do my U2OS cells look right?</span>',
                      '<span class="pdf" style="' + SANS + ' font-size:17px; line-height:1.45; color:#454c50;">Subject: do my U2OS cells look right?</span>')
        s = re.sub(r'<span style="(' + re.escape(MONO) + r' font-size:18px; letter-spacing:0.08em; text-transform:uppercase; color:#[0-9a-f]{6};)">(run it|wait)</span>',
                   r'<span class="pdf" style="\1">\2</span>', s)
        # 26 Oct, half the words: 02a's skills (the icons, logos and years stay); 02c's captions (the pictures and numbers show it)
        s = re.sub(r'<span style="(' + re.escape(MONO) + r' font-size:18px; color:#454c50;)">(cell imaging, AI|automated screening|expansion microscopy|neuron assays|electrophysiology|neuroscience, math)</span>',
                   r'<span class="pdf" style="\1">\2</span>', s)
        s = re.sub(r'<span style="([^"]*)">(six papers, six &#8220;normals&#8221;|one opinion|at risk|lost)</span>', r'<span class="pdf" style="\1">\2</span>', s)
        # 02b: the benches drawn, the words in the reader's layer
        s = re.sub(r'<style id="dl-benches">.*?</style><div class="benches">.*?</svg></div>', '', s, flags=re.S)
        s = re.sub(r'<span style="([^"]*)">(asked @ five benches<br>&#8230; answered @ none)</span>', lambda m: benches() + f'<span class="pdf" style="{m.group(1)}">{m.group(2)}</span>', s)
        s = re.sub(r'(<span class="pdf" style="[^"]*">asked @ five benches)', lambda m: benches() + m.group(1), s) if 'class="benches"' not in s else s
        return s

    def t2(s):      # 03: one scale-bar label in the figure legend instead of eleven; 03a's detail lines and 03b's second biosecurity line to the reader
        um = {m.group(3) for m in SCALE_LABEL.finditer(s)}
        assert len(um) <= 1, f'scale bars of different lengths: {um}'
        s = SCALE_LABEL.sub(lambda m: m.group(1) + '<span class="pdf" style="' + m.group(2) + '">' + m.group(3) + ' &#181;m</span>', s)
        s = re.sub(r'<span class="talk bars">.*?</span>', '', s)
        if um:
            s = re.sub(r'(<div class="stain-cap"[^>]*><div class="stain"[^>]*>.*?)(</div>)',
                       lambda m: m.group(1) + f'<span class="talk bars">bars {um.pop()} &#181;m</span>' + m.group(2), s, count=1, flags=re.S)
        # biosecurity stays on stage (Kat, 26 Oct: "biosecurity, decentralization, data as product, are all very important parts of
        # pitch"); this clears the reader-only copy an earlier build of this pass left
        s = re.sub(r'<div class="bio pdf"[^>]*>.*?</div>', '', s, flags=re.S)
        s = s.replace('<span style="color:#454c50;">Good actors can prove what they test.</span>', '<span class="pdf" style="color:#454c50;">Good actors can prove what they test.</span>')
        s = re.sub(r'<div class="u2os pdf".*?</span></span></span></div>', '', s, flags=re.S).replace('<div class="u2os" style=', '<div class="u2os pdf" style=')
        for cls in ('sub-protocol', 'sub-dmso'):
            s = to_reader(s, cls)
        return s
    return _template(_template(deck, 't1', t1), 't2', t2)


# 26 Oct (Kat: "slide>slide and animations: should add clarity, connect related elements. transitions add depth, tell story")
# 03b: the classifier names the labs one tile after another, then its score fills, then chance, then what it means for biosecurity
MOTION_03 = ('<style id="dl-motion">'
             + ''.join(f'.step-1 .tile:nth-child({k}) .tag{{animation-delay:{0.07 * k:.2f}s}}' for k in range(1, 13))
             + '@keyframes dl-grow{from{transform:scaleX(0)}to{transform:none}}@keyframes dl-rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}'
             + '.step-1 .stat>.sbar>div{transform-origin:left center;animation:dl-grow .9s cubic-bezier(.2,.8,.2,1) both}'
             + '.step-1 .stat>.sbar:nth-child(2)>div{animation-delay:1.0s}.step-1 .stat>.sbar:nth-child(4)>div{animation-delay:1.6s}'
             + '.step-1 .bio{animation:dl-rise .5s cubic-bezier(.2,.8,.2,1) 2.2s both}'
             + '@media (prefers-reduced-motion: reduce){.step-1 .stat>.sbar>div,.step-1 .bio{animation:none}}</style>')
# slide to slide: each slide comes forward to full size as it reaches the middle of the screen and recedes as it leaves, so the talk
# reads as one surface moving past; scroll-linked, so it follows the reader's own pace (desktop only; off with reduced motion)
DEPTH = ('<style id="dl-depth">@supports (animation-timeline: view()){@media (prefers-reduced-motion: no-preference){'
         'html:not(.narrow) .box{animation:dl-depth linear both;animation-timeline:view();animation-range:cover 0% cover 100%}'
         '@keyframes dl-depth{0%{transform:scale(.92);opacity:.3}38%,62%{transform:none;opacity:1}100%{transform:scale(.92);opacity:.3}}}}</style>')


def motion(deck):
    deck = _template(deck, 't2', lambda s: re.sub(r'<style id="dl-motion">.*?</style>', '', s, flags=re.S).replace('</style>', '</style>' + MOTION_03, 1))
    deck = re.sub(r'<style id="dl-depth">.*?</style>', '', deck, flags=re.S)
    return deck.replace('</head>', DEPTH + '</head>', 1)


# 26 Oct (Kat: '"normal" = similar to published images, past data'): the question's key word, defined where it is asked (02b), in
# icons and four words
NORMAL_DEF = ('<div class="normal-def" style="display:flex; align-items:center; gap:14px; ' + parts.SANS + ' font-size:28px; line-height:1.2; color:#14171a;">'
              '<span style="color:#be1e74; font-weight:700;">&#8220;normal&#8221;</span><span style="color:#666e72;">=</span>'
              '<span style="display:flex; align-items:center; gap:8px;">' + parts.icon('journals', '#454c50', 30) + 'published images</span>'
              '<span style="color:#666e72;">+</span>'
              '<span style="display:flex; align-items:center; gap:8px;">' + parts.icon('clock', '#454c50', 30) + 'past data</span></div>')


def normal_defined(deck):
    def t1(s):
        s = re.sub(r'<div class="normal-def".*?</span></div>', '', s, flags=re.S)
        anchor = 'look &#8220;normal&#8221;?</span></h2>'
        assert s.count(anchor) == 1, '02b question'
        return s.replace(anchor, anchor + NORMAL_DEF)
    return _template(deck, 't1', t1)


def apply(deck):
    return chance_tick(talk_last(board_words(colour_meaning(overlays_hide_team(motion(chance_grey(green_text(normal_defined(fewer_words(sources(deck)))))))))))


def overlays_hide_team(s):
    """02b and 02c cover the team panel; hide it under them, so it is neither read aloud nor counted (26 Oct)."""
    t0 = s.find('<template id="t1">'); t1 = s.find('</template>', t0)
    t = s[t0:t1]
    if 'class="team"' in t:      # archive.html is read back, so a second build finds it done
        return s
    old = '<div style="display:flex; gap:40px; align-items:stretch; flex-grow:1; min-height:0'
    assert t.count(old) == 1, t.count(old)
    t = t.replace(old, '<div class="team" style="display:flex; gap:40px; align-items:stretch; flex-grow:1; min-height:0')
    t = t.replace('</style>', '.flow:not(.step-0) .team { visibility:hidden; transition:visibility 0s .45s; }</style>', 1)
    return s[:t0] + t + s[t1:]


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


def talk_last(s):
    """26 Oct, half the words: 02c's problem stands alone (03 turns it); its search box asks in two words."""
    import re
    s = re.sub(r'(>Each lab judges &#8220;normal&#8221; alone\.)<br><span style="color:#[0-9a-f]{6};">Together, every lab can know\.</span>', r'\1', s)
    s = s.replace('>U2OS cells &#8220;normal&#8221; morphology<', '>U2OS &#8220;normal&#8221;?<')
    # 26 Oct (Kat: "lab = data source?"): yes; said once, where labs first appear. JUMP calls each source a data-generating centre [7]
    s = s.replace('93,228 wells, 11 labs, plates held out', '93,228 wells, 11 labs (a lab = one JUMP data source, its data-generating centre), plates held out')
    return s


def chance_tick(s):
    """03b (26 Oct, Kat: "single horizontal threshold"): chance is a tick on the 99.9% bar, not a second number and bar. The 9% row
    and its grey bar stay in the page, hidden: coherence anchors the biosecurity line on that grey bar every build. Skips quietly
    if the deck session has redrawn 03."""
    import re
    s = s.replace('font-size:18px; color:#666e72; white-space:nowrap;">chance 9%', 'font-size:18px; color:#454c50; white-space:nowrap;">chance 9%')      # AA on the page
    t0 = s.find('<template id="t2">'); t1 = s.find('</template>', t0); t = s[t0:t1]
    bar = '<div class="sbar" style="grid-column:1/-1; height:10px; margin-top:-8px; border-radius:5px; background:#eceeef;"><div style="width:99.9%; height:100%; border-radius:5px; background:#454c50;"></div></div>'
    if t.count(bar) != 1 or not re.search(r'<div style="display:(?:contents|none);"><span[^>]*>9%</span>', t):
        return s
    tick = ('<div class="sbar" style="grid-column:1/-1; position:relative; height:10px; margin-top:-8px; margin-bottom:34px; border-radius:5px; background:#eceeef;">'
            '<div style="width:99.9%; height:100%; border-radius:5px; background:#454c50;"></div>'
            '<div style="position:absolute; left:9.1%; top:-7px; width:3px; height:24px; margin-left:-1.5px; background:#f6f7f7; box-shadow:0 0 0 1px #666e72;"></div>'
            '<span style="position:absolute; left:9.1%; top:24px; transform:translateX(-50%); font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:18px; color:#454c50; white-space:nowrap;">chance 9%</span></div>')
    t = re.sub(r'<div style="display:contents;">(<span[^>]*>9%</span>)', r'<div style="display:none;">\1', t)
    t = re.sub(r'<div class="sbar" style="grid-column:1/-1;([^"]*)"><div style="width:9\.1%', r'<div class="sbar" style="display:none; grid-column:1/-1;\1"><div style="width:9.1%', t)
    t = t.replace(bar, tick)
    return s[:t0] + t + s[t1:]
