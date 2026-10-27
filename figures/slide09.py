"""Slide 09: what the money buys, in four milestones. It is the plan, not a measurement: each card shows where the milestone
starts today (U2OS on the public map, eleven labs, one brightfield image, the certificate's seal) and names the board behind it."""
import base64
import re

from parts import *
from appendix import preseed_total, MULTIPLIER, PRESEED, MARKET

E15 = results('e17-same-labs-every-input.json')['inputs']['brightfield']   # same 8 labs and wells as every other input (A10)
BF = 100 * E15['median_over_splits']          # median of 20 splits of the batches (A10)
CHANCE = 100 * E15['chance']                  # one lab in eight
N_LABS = len(results('e9-replay.json')['labs'])       # labs on the map today
N_BATCHES = sum(len(v['batches']) for v in results('e9-replay.json')['labs'].values())     # batches on the map today, as 10's key counts them


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
# 26 Oct (Kat: "implement all suggested change"; "product is really subscription/membership to data repo"): the first labs outside JUMP,
# then the first paying member (a screening lab, the wedge, as the roadmap's phase 1 puts paid pilots by month 9), then the
# benchmark and the model; the paying member is the one pink point. appendix.a21 reads the titles.
LINE = MARKET['price per line per quarter, $k']
MILESTONES = [(f'data from {WORD[PARTNERS]} partner labs, the first outside JUMP', pdf('U2OS first, then any line'), 'map', 'first data outside JUMP'),
              ('first paying member', pdf(f'a screening lab, ~${LINE[0]}&#8211;{LINE[2]}k/line/quarter, A22'), 'receipt', 'first paying member'),
              ('benchmark playground', pdf('known drugs, planted faults, A4, A16'), 'flag', 'benchmark playground'),
              ('model for any cell', pdf(f'from one brightfield image; chance {CHANCE:.1f}%, A10, A19'), 'image', 'model for any cell')]
PAID = 1      # the paying member: the one pink step

SQ = 24


def square(fill=None, colour=GREEN, size=SQ):
    """One cell of a milestone figure: filled where it exists today, dashed where the money builds it."""
    if fill:
        return f'<span style="display:block; width:{size}px; height:{size}px; border-radius:5px; background:{fill};"></span>'
    return f'<span style="display:block; width:{size}px; height:{size}px; border-radius:5px; box-sizing:border-box; border:1.6px dashed {colour};"></span>'


def playground():
    """Four lines by two kinds of microscope; U2OS is filled, as it is on the public map today."""
    cell = lambda k: f'<span style="display:flex; justify-content:center;">{square(GREEN if k == 0 else None, FAINT)}</span>'
    head = '<span></span>' + ''.join(f'<span style="{SANS} font-size:18px; color:{MUTE}; text-align:center;">{s}</span>' for s in SCOPES)
    rows = ''.join(f'<span style="{SANS} font-size:18px; color:{INK2};">{line}</span>' + cell(k) + cell(k) for k, line in enumerate(LINES))
    return (f'<div role="img" aria-label="Four cell lines by two kinds of microscope; U2OS on both exists today." '
            f'style="display:grid; grid-template-columns:60px 80px 80px; column-gap:8px; row-gap:9px; align-items:center;">{head}{rows}</div>')


def labs():
    """Every lab on the map today, one flask each (the deck's lab, as on 04a), and the partner labs the money adds, dashed: drawn, not built."""
    dashed = icon('lab', GREEN, 26).replace('stroke-width="1.7"', 'stroke-width="1.7" stroke-dasharray="2.2 2.4"')
    cells = [icon('lab', GREEN, 26)] * N_LABS + [dashed] * PARTNERS
    per = (len(cells) + 1) // 2
    grid = (f'<div style="display:grid; grid-template-columns:repeat({per},26px); gap:6px 7px;">' + ''.join(cells) + '</div>')
    return (f'<div role="img" aria-label="{N_LABS} labs on the map today and {PARTNERS} partner labs to come." style="display:flex; flex-direction:column; gap:10px;">'
            f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{N_LABS} <span style="color:{GREEN};">+ {PARTNERS}</span></span>'
            f'<div style="height:96px; display:flex; align-items:center;">{grid}</div>'
            f'<span style="{SANS} font-size:18px; line-height:1.35; color:{MUTE};">labs{pdf(f" + {PARTNERS} partners")}</span></div>')


def any_image():
    """One DMSO well in brightfield, and how often a frozen image model names its lab from that one picture."""
    uri = 'data:image/jpeg;base64,' + base64.b64encode(open('figures/assets/well-I01-brightfield.jpg', 'rb').read()).decode()
    return (f'<div style="display:flex; flex-direction:column; gap:10px; width:100%;">'
            f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{BF:.1f}%</span>'
            f'<div style="position:relative; width:100%; height:96px;"><img src="{uri}" alt="Brightfield image of one DMSO well, lab 2." '
            f'style="width:100%; height:96px; border-radius:10px; object-fit:cover; object-position:50% 85%; display:block; background:#000;">{stain_chip("Brightfield", inset=7, short=True)}</div>'
            f'<span style="{SANS} font-size:18px; line-height:1.35; color:{MUTE};">right lab{pdf(" of " + str(E15["n_labs"]) + " labs with brightfield")}</span></div>')


def seal():
    return (open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="116" height="116"')
            .replace('stroke="#be1e74"', f'stroke="{GREEN}"'))      # a company's certificate: no lab-2 pink here (07b's seal is lab 2's and keeps it)


FIGURE = [playground, labs, any_image, seal]


def money(sub, total):
    """09 (26 Oct, Kat: "raising how much, for what? should be more clear"): where the round goes, one bar: people, the benchmark
    (playground and partner-lab bench time), the rest; each part asked at A21's planned cost times the overrun rule, so the parts
    add to the headline's total."""
    bench = sum(k for name, _, k in PRESEED if name in ('benchmark playground', 'partner-lab bench time'))
    people = sum(k for _, _, k in PRESEED[:4])
    parts = [('people', people, INK2), ('benchmark', bench, '#0c7559'),      # the text-safe green: white on it is AA
             ('compute, legal, travel', sub - people - bench, MUTE)]
    seg = lambda k, name, v, c: (f'<div class="r" style="animation-delay:{0.3 + 0.2 * k:.1f}s; flex:{v} 1 0; min-width:0; height:46px; box-sizing:border-box; padding:0 14px; '
                                 f'display:flex; align-items:center; justify-content:space-between; gap:8px; background:{c}; {SANS} font-size:20px; color:#ffffff; white-space:nowrap; overflow:hidden;">'
                                 f'<span>{name if v / sub > 0.15 else ""}</span><span style="font-weight:700;">${v * MULTIPLIER / 1000:.2f}M</span></div>')
    # 26 Oct (Kat: "business model more sexy specifics: how much $ raise, what to use it on"): under each part, its line items, named
    # and asked (A21's planned cost x the overrun rule), so every dollar of the round has a place
    SHORT = {'leader, to run it': 'a leader to run it', 'scientific lead (me)': 'scientific lead (me)', 'ML engineer': 'ML engineer, from month 7',
             'payroll overhead': 'payroll overhead', 'benchmark playground': 'playground, ~60 plates', 'partner-lab bench time': '3 partner labs',
             'compute and storage': 'compute', 'legal, IP, insurance, accounting': 'legal, IP', 'travel and partner visits': 'travel'}
    groups = [PRESEED[:4], [r for r in PRESEED if r[0] in ('benchmark playground', 'partner-lab bench time')],
              [r for r in PRESEED[4:] if r[0] not in ('benchmark playground', 'partner-lab bench time')]]
    assert sum(k for grp in groups for *_, k in grp) == sub, 'every line item in one part'
    item = lambda name, k: (f'<span style="display:flex; justify-content:space-between; gap:10px; {SANS} font-size:18px; line-height:1.25; color:{INK2};">'
                            f'<span>{SHORT[name]}</span><span style="{MONO} color:{INK};">${k * MULTIPLIER}k</span></span>')
    items = ''.join(f'<div class="r" style="animation-delay:{0.5 + 0.2 * g:.1f}s; flex:{parts[g][1]} 1 0; min-width:0; padding:0 14px; display:flex; flex-direction:column; gap:2px;">'
                    + ''.join(item(n, k) for n, _, k in grp) + '</div>' for g, grp in enumerate(groups))
    return (f'<div style="display:flex; flex-direction:column; gap:6px; flex-shrink:0;">'
            f'<div style="display:flex; gap:3px; border-radius:8px; overflow:hidden;">' + ''.join(seg(k, *p) for k, p in enumerate(parts)) + '</div>'
            f'<div style="display:flex; gap:3px;">{items}</div>'
            f'<div style="{MONO} font-size:18px; color:{MUTE};">${sub}k planned &#215; {MULTIPLIER} for overruns (A21)</div></div>')


def build():
    """09 since 26 Oct (Kat: "more simple, more clear ... conventional graphs too"): the round as a plain bar chart, one bar per line
    item at its asked cost (A21's plan x the overrun rule), coloured by what it pays for; the milestones as a plain timeline, the
    first paying member the one pink point. The milestone pictures (playground grid, labs, brightfield image, seal) left."""
    sub, total = preseed_total()
    SHORT = {'leader, to run it': 'a leader to run it', 'scientific lead (me)': 'scientific lead (me)', 'ML engineer': 'ML engineer',
             'payroll overhead': 'payroll overhead', 'benchmark playground': 'benchmark data, ~60 plates', 'partner-lab bench time': 'data from 3 partners'}
    BENCH = ('benchmark playground', 'partner-lab bench time')
    group = lambda name: 'data' if name in BENCH else ('people' if name in [r[0] for r in PRESEED[:4]] else 'running')      # the money that makes data
    COL = {'people': INK2, 'data': '#0c7559', 'running': '#949c9f'}
    # 26 Oct (Kat: "open issues: close them", 09 at 95 words): every people and benchmark line stays; the three running lines
    # (compute, legal, travel) are one bar here and line by line on A21 and in the roadmap; the group totals left the key
    rows = [(SHORT[n], k, group(n)) for n, _, k in sorted(PRESEED, key=lambda r: (['people', 'data', 'running'].index(group(r[0])), -r[2])) if group(n) != 'running']
    rows.append(('compute, legal, travel', sum(k for n, _, k in PRESEED if group(n) == 'running'), 'running'))
    W, lx, bw, P, bh = 740, 300, 340, 37, 27      # 26 Oct (review): talk-scale labels
    vmax = max(k for _, k, _ in rows)      # bars at the plan; the contingency is the line under the key
    g = []
    for k, (label, cost, grp) in enumerate(rows):
        y = k * P + 10
        v = cost
        g.append(f'<g class="r" style="animation-delay:{0.3 + 0.06 * k:.2f}s">' + text(lx - 14, y + 20, label, 22, INK, 'end')
                 + f'<rect class="bar" style="animation-delay:{0.35 + 0.06 * k:.2f}s; transform-origin:{lx}px 0" x="{lx}" y="{y}" width="{bw * v / vmax:.1f}" height="{bh}" rx="5" fill="{COL[grp]}"/>'
                 + text(lx + bw * v / vmax + 10, y + 20, f'${v}k', 22, INK2) + '</g>')
    H = len(rows) * P + 10
    key = ''.join(f'<span style="display:inline-flex; align-items:center; gap:8px;"><i style="width:16px; height:16px; border-radius:3px; background:{COL[gname]};"></i>'
                  f'{gname}</span>' for gname in COL)
    chart = (f'<div style="display:flex; flex-direction:column; gap:10px; width:{W}px;">'
             f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="The round line by line: '
             + '; '.join(f'{label} ${k}k' for label, k, _ in rows) + f'." style="display:block;">' + ''.join(g) + '</svg>'
             f'<div style="display:flex; gap:22px; flex-wrap:wrap; {SANS} font-size:22px; color:{INK2};">{key}</div>'
             f'<span style="{SANS} font-size:{T_TEXT}px; color:{MUTE};">${sub}k plan + ${total - sub}k contingency = ${total / 1000:.2f}M (A21)</span></div>')
    steps = [(t, s_) for t, _, _, s_ in MILESTONES]
    mile = ''.join(
        f'<div class="r" style="animation-delay:{1.2 + 0.2 * k:.2f}s; position:relative; padding:0 0 26px 44px;">'
        f'<span style="position:absolute; left:0; top:-1px; width:32px; height:32px; border-radius:50%; box-sizing:border-box; display:flex; align-items:center; justify-content:center; '
        f'{"background:" + PINK + ";" if k == PAID else "background:" + PAPER + "; border:2.5px solid " + GREEN + ";"} {SANS} font-size:22px; font-weight:700; '
        f'color:{"#ffffff" if k == PAID else GREEN};">{k + 1}</span>'      # the number inside its circle: one element, its own background
        f'<span style="{SANS} font-size:22px; font-weight:600; line-height:1.2; color:{PINK if k == PAID else INK};">{talk_span(stage) + pdf(title)}</span></div>'
        for k, (title, stage) in enumerate(steps))
    # 26 Oct (Kat: "a progress line"): where the plan starts, done on public data, with the honest revenue count
    today = (f'<span style="{MONO} font-size:22px; letter-spacing:0.08em; text-transform:uppercase; color:{INK2}; margin-bottom:12px;">today</span>'
             f'<div class="r" style="animation-delay:1.0s; position:relative; padding:0 0 28px 44px;">'
             f'<span style="position:absolute; left:6px; top:4px; width:20px; height:20px; border-radius:50%; background:{GREEN};"></span>'
             f'<span style="display:block; {SANS} font-size:22px; font-weight:600; line-height:1.2; color:{INK};">{N_LABS} labs, {N_BATCHES} batches mapped</span>'
             f'<span style="display:block; {SANS} font-size:22px; line-height:1.3; color:{INK2};">from public data{pdf(" (JUMP [7], results/e9)")}; no revenue yet</span></div>')
    timeline = (f'<div style="position:relative; flex:1; padding-left:28px; border-left:2px solid #e4e8e9; display:flex; flex-direction:column; justify-content:center;">'
                + today +
                f'<span style="{MONO} font-size:22px; letter-spacing:0.08em; text-transform:uppercase; color:{INK2}; margin-bottom:18px;">by month 18</span>'
                f'<div style="position:relative;"><i style="position:absolute; left:15px; top:14px; bottom:40px; width:2px; background:{GREEN}; opacity:.5;"></i>{mile}</div>'
                f'<span style="{SANS} font-size:{T_TEXT}px; color:{INK2}; padding-left:44px;">{arrow("e")} seed round</span></div>')
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:18px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(9)}
  {header('09', 'The raise')}
  <div style="display:flex; gap:40px; align-items:flex-start;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:1100px; flex-shrink:0;">Raising ${total / 1000:.1f}M pre-seed for 18 months:<br><span style="color:{GREEN};">first paying members, then the seed.</span></h2>
  </div>
  <div style="flex-grow:1; min-height:0; display:flex; gap:44px; align-items:stretch;">{chart}{timeline}</div>
  {foot_line('proposed; milestones in order, not dated; every line an assumption (A21)', delay=1.2, stage='')}
</div>'''
    return BASE_CSS, body, None
