"""Appendix boards written whole from results: A4, A7 to A24 (A16 aside), the bars on A3, and the index that lists them.

The boards are written by subject in appendix_drift (A8, A11 to A13, A17), appendix_signal (A7, A9, A10, A14, A19),
appendix_trust (A18, A20, A24, A25) and appendix_business (A4, A15, A21 to A23, with the plan and market numbers), from
the parts in appendix_kit. This module gathers them, so callers read every board, price and plan from here, and it
writes the index boards and the bars on A3."""

import os
import re

from parts import *
from appendix_kit import plate_map                          # read from here by slide 07
from appendix_drift import a8, a11, a12, a13, a17
from appendix_signal import a7, a9, a10, a14, a19
from appendix_trust import a18, a20, a24, a25
from appendix_business import a4, a15, a21, a22, a23
from appendix_business import PRESEED, MULTIPLIER, preseed_total, MARKET, market, plan   # read from here by slides and docs


# ------------------------------------------------------------------ small edits to boards that are not rebuilt
# 17 Nov 2026 (Kat: "should link out to each slide (auto-scroll)"): the question is the link, the code beside it too; Q_CSS gives
# both index pages' question links their look (ink, underlined in the link colour under the pointer)
Q_CSS = '.q{color:#14171a;text-decoration:none}.q:hover{color:#8e1657;text-decoration:underline;text-underline-offset:3px}'
INDEX_ROW = ('<div class="c" style="display:grid; grid-template-columns:40px minmax(0,1fr); column-gap:10px; align-items:baseline; padding:8px 0; '
             'border-top:1px solid #e4e8e9; animation-delay:{delay:.2f}s;"><span style="' + MONO + ' font-size:14px; color:#666e72;"><a href="#{code}" style="color:inherit;">{code}</a></span>'
             '<div style="display:flex; flex-direction:column; gap:0; min-width:0;"><a class="q" href="#{code}" style="' + SANS + ' font-size:17px; font-weight:600; '
             'line-height:1.2; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{question}</a><span style="' + MONO + ' font-size:13px; line-height:1.35; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{answer}</span></div></div>')


def q_css(t):
    """Q_CSS in a template's own style block, once."""
    return t if Q_CSS in t else t.replace('</style>', Q_CSS + '</style>', 1)


# every board, in order; the index is written from this list alone
BOARDS = [
    ('A1', 'Why not trust the plate&#8217;s controls?', 'sick plate, sick control'),
    ('A2', 'What is the math?', 'six calculations on 3,773 numbers'),
    ('A3', 'Why not batch-correct it away?', 'erases most of the lab fingerprint'),
    ('A4', 'Is the model the moat?', 'counting cells often wins'),
    ('A5', 'Why not just count cells?', 'two ways to ask one question'),
    ('A6', 'How often do I check again?', 'your &#8220;normal&#8221; expires'),
    ('A7', 'Isn&#8217;t this cell-line DNA testing (STR)?', 'STR: which line &#183; images: which lab'),
    ('A8', 'Is the assay itself working?', 'known drugs show the test worked'),
    ('A9', 'Does it change the result?', 'same drug &#183; different answer'),
    ('A10', 'Does it work without stains?', 'one brightfield image names the lab'),
    ('A11', 'Does it flag too often?', 'rarely &#183; six of 129 batches'),
    ('A12', 'What moved?', 'stain brightness, not cell count'),
    ('A13', 'How does one lab move over time?', 'own &#8220;normal&#8221; fine &#183; other labs: moved'),
    ('A14', 'What does the map buy?', 'same drug, closer between labs'),
    ('A15', 'Who pays?', 'labs join free &#183; subscribers pay'),
    ('A16', 'What would the money build?', 'ugliest dataset &#183; on purpose'),
    ('A17', 'Is the leaderboard fair?', 'ranked on controls &#183; never on results'),
    ('A18', 'What is private?', 'control wells shared &#183; nothing else is'),
    ('A19', 'What is the machine learning?', 'image in &#183; position and correction out'),
    ('A20', 'What about biosecurity?', 'cells show their lab &#183; labels can lie'),
    ('A21', 'How much, and what for?', 'planned $0.9M &#215; 2 = $1.8M asked'),
    ('A22', 'How big?', f'about ${sum(market(1)) / 1000:.0f}M a year in revenue, base case'),
    ('A23', 'What is cell data worth?', 'priced in deals &#183; labs disagree'),
    ('A24', 'Why would a lab share?', 'owned by the lab &#183; verified by anyone'),
    ('A25', 'What does the shared data look like?', 'one dataset per lab &#183; every batch checked')]


# 17 Nov 2026 (Kat: "pitch should be pitch, appendix link out to supporting science and figures"): the talk prints no boards. Its
# index is one row per judge question, each linking to the board (archive.html#A7), document or results file that answers it.
SITE = 'https://kat-titter.github.io/datum-line/'
DOC_NAMES = {'docs/whitepaper.html': 'white paper', 'docs/roadmap.html': 'roadmap'}
TALK_INDEX = [
    ('Why not batch-correct it away?', ('A3', 'docs/whitepaper.html')),
    ('Does the same drug look the same in another lab?', ('A9', 'A14', 'results/e16-same-perturbation.json', 'results/e12-field-normalization.json')),
    ('Do labs rank drugs the same?', ('results/e19-rank-order.json',)),
    ('Would a lab&#8217;s own QC catch it?', ('A13', 'A12')),
    ('How often to check? Won&#8217;t it flag everything?', ('A6', 'A11')),
    ('Did the test itself work?', ('A8', 'results/e11-known-answer.json')),
    ('Doesn&#8217;t STR already tell me?', ('A7',)),
    ('Does it work without stains?', ('A10', 'results/e17-same-labs-every-input.json')),
    ('What is shared, and who owns it?', ('A18', 'A24')),
    ('Biosecurity: who uses it, and how?', ('A20',)),
    ('Reproducibility: who uses it, and how?', ('A9', 'A14', 'docs/whitepaper.html')),
    ('How does it work?', ('A19', 'A2', '04b')),
    ('What does the money buy? How big?', ('A21', 'A22', 'docs/roadmap.html'))]
# 17 Nov, later (Kat, on the index: "center, make larger? should link out to each slide (auto-scroll)"): one column of thirteen
# rows that share the page's height. The question, at 28 px, is a link to the first place that answers it; every place follows at
# 22 px, the kind said once ("archive A9 A14"). Widths measured in the deck's fonts: the longest question is 636 px, the longest
# set of links 421 px.
TALK_ROW = ('<div class="c" style="flex:1 1 0; min-height:0; display:flex; align-items:center; border-top:1px solid #e4e8e9; animation-delay:{delay:.2f}s;">'
            '<div style="display:flex; align-items:baseline; white-space:nowrap;">'
            '<a class="q" href="{url}" target="_blank" rel="noopener" style="flex:0 0 676px; ' + SANS + ' font-size:28px; font-weight:600; line-height:1.2;">{question}</a>'
            '<span style="display:flex; align-items:baseline; gap:26px; ' + MONO + ' font-size:22px; line-height:1.2; color:#666e72;">{links}</span></div></div>')


def talk_target(target):
    """One place a row of the talk's index points: (kind, address, name). A board code opens that board in the archive, a path the
    document or results file. Every target is checked here, so a link the build writes is a link that exists."""
    if re.fullmatch(r'A\d{1,2}', target):
        assert target in {c for c, _, _ in BOARDS}, target
        return 'archive', f'{SITE}archive.html#{target}', target
    if re.fullmatch(r'(0\d|10)[a-d]?', target):        # a talk slide, or one of its views, as the archive keeps it (04b: the check on one batch)
        return 'archive', f'{SITE}archive.html#{target}', target
    assert os.path.exists(target), target
    if target in DOC_NAMES:
        return '', SITE + target, DOC_NAMES[target]
    return 'results', SITE + target, os.path.basename(target).split('-')[0].split('.')[0]


def talk_links(targets):
    """A row's links, in order, each kind named once before its codes."""
    link = lambda url, name: f'<a href="{url}" target="_blank" rel="noopener" style="text-underline-offset:4px;">{name}</a>'
    out, places = [], [talk_target(x) for x in targets]
    for kind in dict.fromkeys(k for k, _, _ in places):
        links = ''.join(link(u, n) for k, u, n in places if k == kind)
        out.append(f'<span style="display:flex; align-items:baseline; gap:13px;"><span>{kind}</span>{links}</span>' if kind else links)
    return ''.join(out)


def talk_index(t):
    """The talk's index board from the archive's (template t10): the same header, the headline on one line, one column of TALK_INDEX rows."""
    a = t.index('<div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); column-gap:28px;'); b = t.index('>', a) + 1
    c = t.rindex('</div></div></template>')
    rows = ''.join(TALK_ROW.format(question=q, url=talk_target(links[0])[1], links=talk_links(links), delay=0.1 + 0.03 * k)
                   for k, (q, links) in enumerate(TALK_INDEX))
    t = q_css(t[:a] + '<div style="display:flex; flex-direction:column; flex-grow:1; min-height:0;">' + rows + t[c:])
    for old, new in (('>25 boards<', '>Supporting science<'),
                     ('<div style="display:flex; gap:28px; align-items:baseline;"><h2', '<div style="display:flex; gap:28px; align-items:center;"><h2'),
                     ('color:#14171a; width:371px; flex-shrink:0;">The rest, ', 'color:#14171a; white-space:nowrap; flex-shrink:0;">The rest, '),
                     ('font-size:19px; line-height:1.4; color:#666e72; flex-grow:1;">Every number', 'font-size:22px; line-height:1.3; color:#666e72; flex-grow:1;">Every number'),
                     ('Every number comes from the code here or a cited source.<br>Unfinished work is marked pending.',      # 26 Oct, half the words
                      f'Every number: the code here or a cited source. All 25 boards: <a href="{SITE}archive.html" target="_blank" rel="noopener">archive</a><br>'
                      f'Documents: <a href="{SITE}docs/" target="_blank" rel="noopener">white paper, product vision, roadmap, landscape</a>')):
        assert t.count(old) == 1, old
        t = t.replace(old, new, 1)
    return t


def index(s):
    """The appendix index, in three even columns, with a row for every board; the header tag counts the boards."""
    rows = sorted(BOARDS, key=lambda r: int(r[0][1:]))
    if os.path.exists('results/a5-pair.json'):
        pair = results('a5-pair.json')
        if pair.get('count_close') and pair.get('texture_differs'):
            rows = [(c, q, 'same count &#183; different texture' if c == 'A5' else a) for c, q, a in rows]
    column = lambda part, k0: '<div>' + ''.join(INDEX_ROW.format(code=c, question=q, answer=a, delay=0.1 + 0.03 * (k0 + k))
                                                for k, (c, q, a) in enumerate(part)) + '</div>'
    n = len(rows); sizes = [n // 3 + (i < n % 3) for i in range(3)]; cuts = [sum(sizes[:i]) for i in range(4)]
    a = s.index('<div style="display:grid; grid-template-columns:repeat(')
    b = s.index('>', a) + 1
    head = s[a:b].replace('repeat(2,minmax(0,1fr)); column-gap:40px;', 'repeat(3,minmax(0,1fr)); column-gap:28px;')
    c = s.rindex('</div></div></template>')
    out = s[:a] + head + ''.join(column(rows[cuts[i]:cuts[i + 1]], cuts[i]) for i in range(3)) + s[c:]
    out = q_css(out)
    return re.sub(r'(color:#[0-9a-f]{6};">)(?:Answers on request|\d+ boards)</span>', lambda k: f'{k.group(1)}{len(rows)} boards</span>', out, count=1)


def a3_bars(s):
    """A3's right card, drawn from results/e1-redteam: naming the lab from raw features, then after each plate is centred (and scaled) on its own controls, against chance. Rewritten on every run between its own markers."""
    rt = results('e1-redteam.json'); t = rt['tests']; b = t['baseline']

    def row(name, v, colour, value, dashed=False):
        bar = (f'<div style="width:{100 * v:.2f}%; height:100%; box-sizing:border-box; border-radius:4px; '
               + (f'border:1.5px dashed {FAINT};' if dashed else f'background:{colour};') + '"></div>')
        return (f'<div style="display:flex; flex-direction:column; gap:6px;">'
                f'<span style="{SANS} font-size:16px; line-height:1.2; color:{MUTE if dashed else INK};">{name}</span>'
                f'<div style="position:relative; height:28px; margin-right:96px;">{bar}'
                f'<span style="position:absolute; left:calc({100 * v:.2f}% + 8px); top:50%; transform:translateY(-50%); {SANS} '
                f'font-size:{16 if dashed else 28}px; font-weight:{400 if dashed else 700}; letter-spacing:-0.02em; line-height:1; '
                f'color:{MUTE if dashed else colour}; white-space:nowrap;">{value}</span></div></div>')

    rows = (row('no correction', b['balanced_accuracy'], PINK, f'{100 * b["balanced_accuracy"]:.1f}%')
            + row('subtract each plate&#8217;s controls', t['plate_centred']['balanced_accuracy'], INK2, f'{100 * t["plate_centred"]["balanced_accuracy"]:.0f}%')
            + row('subtract and rescale per plate', t['plate_scaled']['balanced_accuracy'], INK2, f'{100 * t["plate_scaled"]["balanced_accuracy"]:.0f}%')
            + row(f'chance &#183; 1 in {b["n_labs"]} labs', b['chance'], None, f'{100 * b["chance"]:.0f}%', dashed=True))
    card = (f'<div class="ap" data-a3="rates" style="animation-delay:0.51s; flex-grow:1; min-width:0; {CARD} padding:16px 20px; '
            f'display:flex; flex-direction:column; justify-content:space-between; gap:10px;">'
            f'{label("can a model tell which lab?<br>higher = clearer lab fingerprint")}'
            f'<div style="display:flex; flex-direction:column; gap:22px;">{rows}</div>'
            f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE};">{b["n_wells"]:,} untreated wells, '
            f'{rt["settings"]["wells_per_plate"]} per plate<br>tested on plates it never saw</span></div><!--/a3-rates-->')
    if 'data-a3="rates"' in s:
        k0, k1 = s.index('<div class="ap" data-a3="rates"'), s.index('<!--/a3-rates-->') + len('<!--/a3-rates-->')
    else:                                          # first run: the hand-built card with three stacked numbers, up to its own closing tag
        k0 = s.index('<div class="ap" style="animation-delay:0.51s;')
        depth, k1 = 0, k0
        for tag in re.finditer(r'<(/?)div\b[^>]*>', s[k0:]):
            depth += -1 if tag.group(1) else 1
            if not depth:
                k1 = k0 + tag.end()
                break
    return s[:k0] + card + s[k1:]


def patch(deck):
    """The index of every board (t10), and the bars on A3 (t13)."""
    m = re.search(r'<template id="t10">.*?</template>', deck, flags=re.S); s = index(m.group(0))
    deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'<template id="t13">.*?</template>', deck, flags=re.S)
    deck = deck[:m.start()] + a3_bars(m.group(0)) + deck[m.end():]
    return deck
