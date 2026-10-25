"""Slide 09: what the money buys, in four milestones. It is the plan, not a measurement: each card shows where the milestone
starts today (U2OS on the public map, eleven labs, one unstained image, the certificate's seal) and names the board behind it."""
import base64
import re

from parts import *
from appendix import preseed_total, MULTIPLIER, PRESEED, MARKET

E15 = results('e17-same-labs-every-input.json')['inputs']['brightfield']   # same 8 labs and wells as every other input (A10)
BF = 100 * E15['median_over_splits']          # median of 20 splits of the batches (A10)
N_LABS = len(results('e9-replay.json')['labs'])       # labs on the map today


def plan(name, pattern):
    """A number from one line of A21's plan, so the slides and the budget cannot disagree."""
    what = next(w for n, w, _ in PRESEED if n == name)
    return int(re.search(pattern, what).group(1))


PARTNERS = plan('partner-lab bench time', r'(\d+) labs')   # partner labs the money brings onto the map
WORD = ['zero', 'one', 'two', 'three', 'four', 'five', 'six']
LINES, SCOPES = ['U2OS', 'A549', 'HepG2', 'iPSC'], ['widefield', 'confocal']   # the playground [17], A16; U2OS is the public map today

ICON = {'map': '<path d="M12 21s-6-5.5-6-10a6 6 0 0 1 12 0c0 4.5-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/>',
        'image': '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3.5"/><path d="M3 9h2M19 9h2"/>',
        'flag': '<path d="M4 21V4h11l-1 3 1 3H4"/><path d="M4 10h11"/>',
        'receipt': '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>'}
# the benchmark comes first: it is what makes the standard everyone else tests against. appendix.a21 reads the titles.
CERT = MARKET['price per certificate, $k']                 # who pays first, and roughly how much (A15, A22: an assumption)
MILESTONES = [('benchmark playground', '+ known drugs + planted faults' + pdf(' &#183; A4, A16'), 'flag'),
              (f'{WORD[PARTNERS]} partner labs on the map', 'U2OS first, then any line', 'map'),
              ('model for any image', 'from one unstained image' + pdf(' &#183; A10, A19'), 'image'),
              ('first paid certificate', f'a company pays ~${CERT[0]}&#8211;{CERT[2]}k to check cell data it bought' + pdf(' &#183; A15'), 'receipt')]

SQ = 24


def square(fill=None, colour=GREEN, size=SQ):
    """One cell of a milestone figure: filled where it exists today, dashed where the money builds it."""
    if fill:
        return f'<span style="display:block; width:{size}px; height:{size}px; border-radius:5px; background:{fill};"></span>'
    return f'<span style="display:block; width:{size}px; height:{size}px; border-radius:5px; box-sizing:border-box; border:1.6px dashed {colour};"></span>'


def playground():
    """Four lines by two kinds of microscope; U2OS is filled, as it is on the public map today."""
    cell = lambda k: f'<span style="display:flex; justify-content:center;">{square(GREEN if k == 0 else None, FAINT)}</span>'
    head = '<span></span>' + ''.join(f'<span style="{SANS} font-size:16px; color:{MUTE}; text-align:center;">{s}</span>' for s in SCOPES)
    rows = ''.join(f'<span style="{SANS} font-size:16px; color:{INK2};">{line}</span>' + cell(k) + cell(k) for k, line in enumerate(LINES))
    return (f'<div role="img" aria-label="Four cell lines by two kinds of microscope; U2OS on both exists today." '
            f'style="display:grid; grid-template-columns:52px 78px 78px; column-gap:8px; row-gap:9px; align-items:center;">{head}{rows}</div>')


def labs():
    """Every lab on the map today, one square each in its own green, and the partner labs the money adds, open and pink."""
    shades = greens(N_LABS)
    cells = [square(c) for c in shades] + [square(None, PINK) for _ in range(PARTNERS)]
    per = (len(cells) + 1) // 2
    grid = (f'<div style="display:grid; grid-template-columns:repeat({per},{SQ}px); gap:7px;">' + ''.join(cells) + '</div>')
    return (f'<div role="img" aria-label="{N_LABS} labs on the map today and {PARTNERS} partner labs to come." style="display:flex; flex-direction:column; gap:10px;">'
            f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{N_LABS} <span style="color:{PINK};">+ {PARTNERS}</span></span>'
            f'{grid}<span style="{SANS} font-size:16px; color:{MUTE};">labs today <span style="color:{PINK};">+ {PARTNERS} partners</span></span></div>')


def any_image():
    """One unstained well, and how often a frozen image model names its lab from that one picture."""
    uri = 'data:image/jpeg;base64,' + base64.b64encode(open('figures/assets/well-I01-brightfield.jpg', 'rb').read()).decode()
    return (f'<div style="display:flex; gap:16px; align-items:flex-end;">'
            f'<img src="{uri}" alt="One untreated well, no stain." style="width:96px; height:96px; border-radius:10px; object-fit:cover; display:block; background:#000; flex-shrink:0;">'
            f'<div style="display:flex; flex-direction:column; gap:6px;"><span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{BF:.1f}%</span>'
            f'<span style="{SANS} font-size:16px; line-height:1.35; color:{MUTE}; white-space:nowrap;">right lab today, {E15["n_labs"]} labs</span></div></div>')


def seal():
    return open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="116" height="116"')


FIGURE = [playground, labs, any_image, seal]


def build():
    sub, total = preseed_total()
    n = len(MILESTONES)
    colour = lambda k: GREEN
    cards = ''.join(
        f'<div class="r" style="animation-delay:{0.3 + 0.18 * k:.2f}s; {CARD} padding:20px 22px 20px; display:flex; flex-direction:column; gap:12px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:center;"><span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{colour(k)};">{k + 1}</span>'
        '</span>'
        f'<div style="flex:1 1 0; min-height:0; display:flex; align-items:center;">{FIGURE[k]()}</div>'
        f'<span style="{SANS} font-size:22px; font-weight:600; letter-spacing:-0.015em; line-height:1.15; color:{INK};">{title}</span>'
        f'<span style="{SANS} font-size:18px; line-height:1.35; color:{MUTE}; min-height:49px;">{what}</span></div>'
        for k, (title, what, icon) in enumerate(MILESTONES))
    W, y, last = 1168, 16, 140 + (n - 1) * 296
    line = ''.join(f'<circle class="f" style="animation-delay:{0.3 + 0.18 * k:.2f}s" cx="{140 + k * 296}" cy="{y}" r="6" fill="{PAPER}" '
                   f'stroke="{colour(k)}" stroke-width="2.5"/>' for k in range(n))
    timeline = (f'<svg viewBox="0 0 {W} 24" width="{W}" height="24" role="img" aria-label="Four milestones in order, then the seed round." style="display:block; flex-shrink:0; margin-top:8px;">'
                f'<line x1="0" y1="{y}" x2="{last}" y2="{y}" stroke="{GREEN}" stroke-width="2.5" stroke-linecap="round"/>'
                f'<line x1="{last}" y1="{y}" x2="{W - 118}" y2="{y}" stroke="{GREEN}" stroke-width="2" stroke-dasharray="6 6"/>{line}'
                f'<text x="{W}" y="{y + 5}" {SVG_MONO} font-size="14" fill="{MUTE}" text-anchor="end">&#8594; seed round</text></svg>')
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(9)}
  {header('09', 'What the money buys')}
  <div style="display:flex; gap:40px; align-items:flex-start;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:620px; flex-shrink:0;">Eighteen months,<br>four milestones.</h2>
    <div style="display:flex; flex-direction:column; gap:8px; margin-top:-7px;"><span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{INK};">${total / 1000:.1f}M</span>
      {pdf(f'<span style="{SANS} font-size:16px; color:{MUTE};">${sub / 1000:.1f}M line by line, &#215;{MULTIPLIER} for the usual overrun &#183; A21</span>')}</div>
  </div>
  {timeline}
  <div style="display:grid; grid-template-columns:repeat({n},minmax(0,1fr)); gap:16px; align-items:stretch; flex-grow:1; min-height:0;">{cards}</div>
  {foot_line('proposed &#183; milestones in order, not dated', delay=1.2)}
</div>'''
    return BASE_CSS, body, None
