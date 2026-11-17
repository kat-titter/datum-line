"""Slide 03, the game and the reveal (two views): a builder of its own since 26 Oct 2026. The slide is written in
figures/templates/slide03.html, edited there directly, and its images are filled from figures/assets on every build. Until then
it was hand-built HTML changed only by string and regex passes (coherence.py, refine.py); build_evidence keeps it out of them.
The confusion matrix is drawn here from results/e1 on every build."""
import json

from parts import inline_assets, icon

MONO = 'font-family="IBM Plex Mono, Menlo, monospace"'
SANS = 'font-family="Archivo, Helvetica Neue, Helvetica, sans-serif"'      # row numbers: a shorter line box than the mono, so 22 px fits a 28-unit row


def matrix():
    """03b: which lab the classifier named for every well (results/e1, 93,228 wells), true lab down, named lab across; each
    square's shade is its share of the row, light grey for none, so the diagonal is the 99.9%. Talk scale (26 Oct, Kat: "22 px
    talk-scale pass"): 22-unit squares on a 28-unit pitch and 22-unit titles; every row named, lab 2's in pink, its square the
    one pink point. The shade key is in the reader's line under it."""
    e1 = json.load(open('results/e1.json'))['all_sources']['confusion_matrix']
    num = lambda l: int(l.split('_')[1])
    order = sorted(range(len(e1['labels'])), key=lambda i: num(e1['labels'][i]))
    M = [[e1['rows_true_cols_pred'][i][j] for j in order] for i in order]
    labs = [num(e1['labels'][i]) for i in order]
    shades = ['#e4e8e9', '#a3dcc6', '#6cc3a3', '#0f8f6c', '#0a5c46']
    level = lambda share: 0 if share == 0 else 1 if share < 0.01 else 2 if share < 0.5 else 3 if share < 0.99 else 4
    C, P, x0, y0 = 20, 24, 76, 38      # 17 Nov: a 24-unit pitch, the column now starts under its why-now title (26 on 26 Oct)
    n = len(M)
    g = [f'<text x="{x0}" y="22" {SANS} font-size="22" fill="#454c50">named lab</text>',
         f'<text transform="translate(14,{y0}) rotate(90)" {SANS} font-size="22" fill="#454c50">true lab</text>']
    for i, row in enumerate(M):
        total = sum(row)
        pink = labs[i] == 2                                  # every row named (Kat, 26 Oct: "only lab 2 labelled?"); lab 2's in pink
        g.append(f'<text x="{x0 - 10}" y="{y0 + i * P + 18}" {SANS} font-size="22" font-weight="{700 if pink else 400}" fill="{"#be1e74" if pink else "#454c50"}" text-anchor="end">{labs[i]}</text>')
        for j, c in enumerate(row):
            fill = '#be1e74' if i == j and labs[i] == 2 else shades[level(c / total)]      # lab 2 named right: the one pink point
            g.append(f'<rect class="f" style="animation-delay:{0.3 + 0.025 * (i + j):.2f}s" x="{x0 + j * P}" y="{y0 + i * P}" width="{C}" height="{C}" rx="4" fill="{fill}"/>')
    W, H = x0 + n * P, y0 + n * P
    # 26 Oct (Kat: "figures: always have legend, prefer position under plot"): the shades' key on stage, under the matrix
    key = ('<div class="talk" style="display:flex; align-items:center; gap:6px; margin-top:10px; font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; '
           'font-size:22px; color:#454c50; white-space:nowrap;"><span style="margin-right:4px;">none</span>'
           + ''.join(f'<i style="width:20px; height:20px; border-radius:4px; background:{c};"></i>' for c in shades)
           + '<span style="margin-left:4px;">all of a lab&#8217;s wells</span></div>'
           '<span class="pdf" style="display:block; margin-top:4px; font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:12px; color:#666e72;">'
           'shade: the share of a row&#8217;s wells, light grey none to dark all; 93,228 wells, results/e1</span>')
    return (f'<div class="cm" style="grid-column:1/-1; margin-top:-2px;"><svg viewBox="-4 -8 {W + 8} {H + 8}" width="{W + 8:.0f}" height="{H + 8:.0f}" role="img" '
            f'aria-label="Confusion matrix of true lab against the lab the classifier named, for 93,228 wells: nearly every well on the diagonal." style="display:block;">'
            + ''.join(g) + f'</svg>{key}</div>')


TXT = "font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif; font-size:22px; line-height:30px;"
CELLS_PUBLIC = '1.8B'      # README [25]: 1,810,840,525 cells in cpg0016 (JUMP Hub, Dataset overview)


def n_labs():
    return len(json.load(open('results/e1.json'))['all_sources']['confusion_matrix']['labels'])


def source():
    """03a (17 Nov, Kat: "make it more clear 11 lab data comes from ..."): where the eleven labs' images come from, on stage where
    the labs first appear, in the grid's empty twelfth slot above the channel key. The repository names JUMP cpg0016 [7]; the same
    icon marks the public images on 05's repository view."""
    return (f'<div class="src03" style="position:absolute; left:1041px; top:440px; white-space:nowrap; {TXT} color:#454c50;">'
            f'<div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#14171a;">{icon("cells", "#14171a", 24)}{n_labs()} labs</div>'
            '<div>public JUMP data</div></div>')


def whynow():
    """03b (17 Nov, Kat: "the why now is AI thirst for large data pools, more public bio data repos"; it was a dated strip under
    02d). Two forces, each the title of the evidence it explains: the tiles are the public pool (supply), the classifier is the AI
    trained on it (demand), and the two arrows meet between them. What the model learns first is the lab: the 99.9% below."""
    head = 'display:flex; align-items:center; gap:8px; font-weight:700; color:#14171a; white-space:nowrap;'
    tip = lambda d: (f'<svg viewBox="0 0 12 16" width="12" height="16" fill="none" stroke="#454c50" stroke-width="2.2" stroke-linecap="round" '
                     f'stroke-linejoin="round" style="flex-shrink:0; margin:0 -1px;" aria-hidden="true"><path d="{d}"/></svg>')
    line = '<i style="flex:1; height:2.2px; border-radius:2px; background:#454c50;"></i>'
    meet = (f'<span class="wn wn-m" style="flex:1; display:flex; align-items:center; margin-left:8px;">{line}{tip("M4 3l6 5-6 5")}'
            f'<i style="width:14px; height:14px; border-radius:50%; background:#0f8f6c; flex-shrink:0; margin:0 5px;"></i>{tip("M8 3L2 8l6 5")}{line}</span>')
    return (f'<div class="wn wn-k" style="position:absolute; right:56px; top:118px; font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:22px; '
            'letter-spacing:0.08em; text-transform:uppercase; color:#454c50;">why now</div>'
            f'<div class="wn wn-l" style="position:absolute; left:56px; top:196px; width:650px; {TXT}">'
            f'<div style="{head}">{icon("cells", "#14171a", 24)}More public cell data{meet}</div>'
            f'<div style="color:#454c50; white-space:nowrap;">JUMP Cell Painting: {n_labs()} labs, {CELLS_PUBLIC} cells</div></div>'
            f'<div class="wn wn-r" style="position:absolute; left:720px; top:196px; {TXT}">'
            f'<div style="{head}">{icon("ai-reads", "#14171a", 24)}AI thirsty for large data pools</div></div>')


def build():
    html = inline_assets(open('figures/templates/slide03.html').read())
    for mark, piece in (('{{matrix}}', matrix()), ('{{source}}', source()), ('{{whynow}}', whynow())):
        assert html.count(mark) == 1, mark
        html = html.replace(mark, piece)
    return html
