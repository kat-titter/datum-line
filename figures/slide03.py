"""Slide 03, the game and the reveal (two views): a builder of its own since 26 Oct 2026. The slide is written in
figures/templates/slide03.html, edited there directly, and its images are filled from figures/assets on every build. Until then
it was hand-built HTML changed only by string and regex passes (coherence.py, refine.py); build_evidence keeps it out of them.
The confusion matrix is drawn here from results/e1 on every build."""
import json

from parts import inline_assets

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
    C, P, x0, y0 = 22, 28, 76, 38
    n = len(M)
    g = [f'<text x="{x0}" y="22" {SANS} font-size="22" fill="#454c50">named lab</text>',
         f'<text transform="translate(14,{y0}) rotate(90)" {SANS} font-size="22" fill="#454c50">true lab</text>']
    for i, row in enumerate(M):
        total = sum(row)
        pink = labs[i] == 2                                  # every row named (Kat, 26 Oct: "only lab 2 labelled?"); lab 2's in pink
        g.append(f'<text x="{x0 - 10}" y="{y0 + i * P + 19}" {SANS} font-size="22" font-weight="{700 if pink else 400}" fill="{"#be1e74" if pink else "#454c50"}" text-anchor="end">{labs[i]}</text>')
        for j, c in enumerate(row):
            fill = '#be1e74' if i == j and labs[i] == 2 else shades[level(c / total)]      # lab 2 named right: the one pink point
            g.append(f'<rect class="f" style="animation-delay:{0.3 + 0.025 * (i + j):.2f}s" x="{x0 + j * P}" y="{y0 + i * P}" width="{C}" height="{C}" rx="4" fill="{fill}"/>')
    W, H = x0 + n * P, y0 + n * P
    key = ('<span class="pdf" style="display:block; margin-top:4px; font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:12px; color:#666e72;">'
           'shade: the share of a row&#8217;s wells, light grey none to dark all; 93,228 wells, results/e1</span>')
    return (f'<div class="cm" style="grid-column:1/-1; margin-top:-2px;"><svg viewBox="-4 -8 {W + 8} {H + 8}" width="{W + 8:.0f}" height="{H + 8:.0f}" role="img" '
            f'aria-label="Confusion matrix of true lab against the lab the classifier named, for 93,228 wells: nearly every well on the diagonal." style="display:block;">'
            + ''.join(g) + f'</svg>{key}</div>')


def build():
    return inline_assets(open('figures/templates/slide03.html').read()).replace('{{matrix}}', matrix())
