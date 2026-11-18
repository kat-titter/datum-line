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
    SHORT = {'executive director, to run it': 'an executive director', 'scientific lead (me)': 'scientific lead (me)', 'ML engineer': 'ML engineer, from month 7',
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
    """09 since 17 Nov (pitch minimum: "use minimum necessary compelling science and figures for pitch"): one full-width timeline,
    a tick per stage. Today (public data, no revenue yet), then the eighteen months the round pays for on one card (four steps in
    order, the first paying member the one pink point), then the five-year FRO. The budget bars and their key left the talk:
    board A21 lists every line (26 Oct's bar chart is in the archive's history)."""
    sub, total = preseed_total()
    steps = [(t, s_) for t, _, _, s_ in MILESTONES]
    LINE_Y, R, CARD_X, STEP, TOP = 116, 24, 330, 162, 164      # the line's height, a step's radius, where the card starts, a step's width, where labels start
    lab = f'{SANS} font-size:{T_TEXT}px; line-height:1.2; text-wrap:balance;'
    cap = f'position:absolute; top:22px; {MONO} font-size:{T_TEXT}px; letter-spacing:0.08em; text-transform:uppercase; color:{INK2};'
    mile = ''.join(
        f'<div class="r" style="animation-delay:{1.0 + 0.2 * k:.2f}s; position:absolute; left:{CARD_X + 22 + k * STEP}px; top:{LINE_Y - R}px; width:{STEP - 14}px;">'
        f'<span style="width:{2 * R}px; height:{2 * R}px; border-radius:50%; box-sizing:border-box; display:flex; align-items:center; justify-content:center; '
        f'{"background:" + PINK + ";" if k == PAID else "background:#ffffff; border:2.5px solid " + GREEN + ";"} {SANS} font-size:{T_TEXT}px; font-weight:700; '
        f'color:{"#ffffff" if k == PAID else GREEN};">{k + 1}</span>'      # the number inside its circle: one element, its own background
        f'<span style="display:block; margin-top:{TOP - LINE_Y - R}px; {lab} font-weight:600; color:{PINK if k == PAID else INK};">{talk_span(stage) + pdf(title)}</span></div>'
        for k, (title, stage) in enumerate(steps))
    # 26 Oct (Kat: "a progress line"): where the plan starts, done on public data, with the honest revenue count
    today = (f'<span style="{cap} left:0;">today</span>'
             f'<div class="r" style="animation-delay:0.4s; position:absolute; left:0; top:{LINE_Y - 14}px; width:{CARD_X - 24}px;">'
             f'<span style="display:block; width:28px; height:28px; border-radius:50%; background:{GREEN};"></span>'
             f'<span style="display:block; margin-top:{TOP - LINE_Y - 14}px; {lab} font-weight:600; color:{INK};">{N_LABS} labs, {N_BATCHES} batches mapped</span>'
             f'<span style="display:block; {lab} line-height:1.3; color:{INK2};">from public data{pdf(" (JUMP [7], results/e9)")}; no revenue yet</span></div>')
    card_w = 22 + len(steps) * STEP + 8
    card = (f'<div class="r" style="animation-delay:0.7s; position:absolute; left:{CARD_X}px; top:0; width:{card_w}px; height:100%; {CARD}"></div>'
            f'<span style="{cap} left:{CARD_X + 22}px;">by month 18</span>')
    tip = 1160      # the line runs from today's dot, through the card, to an arrowhead at the five-year FRO
    line = (f'<svg aria-hidden="true" width="1168" height="{LINE_Y + 12}" viewBox="0 0 1168 {LINE_Y + 12}" style="position:absolute; left:0; top:0; overflow:visible;">'
            f'<path d="M 14 {LINE_Y} H {tip - 2}" stroke="{GREEN}" stroke-width="3" opacity=".5"/>'
            f'<path d="M {tip - 12} {LINE_Y - 9} L {tip} {LINE_Y} L {tip - 12} {LINE_Y + 9}" fill="none" stroke="{GREEN}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    fro = (f'<span class="r" style="animation-delay:1.9s; position:absolute; right:0; top:{TOP}px; width:{1168 - CARD_X - card_w - 16}px; text-align:right; '
           f'{lab} color:{INK2};">five-year FRO funding</span>')      # 17 Nov (Kat: "Nonprofit FRO"): was "seed round"
    timeline = (f'<div role="img" aria-label="Today: {N_LABS} labs and {N_BATCHES} batches mapped from public data, no revenue yet. By month 18, in order: '
                + ', '.join(s_ for _, s_ in steps) + f'. Then five-year FRO funding." style="position:relative; width:1168px; height:268px;">{card}{line}{today}{mile}{fro}</div>')
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:18px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(9)}
  {header('09', 'The raise')}
  <div style="display:flex; gap:40px; align-items:flex-start;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:1168px; flex-shrink:0;">Raising ${total / 1000:.1f}M to start a nonprofit FRO:<br><span style="color:{GREEN};">18 months to first paying members, then the five-year FRO.</span></h2>
  </div>
  <div style="flex-grow:1; min-height:0; display:flex; align-items:center;">{timeline}</div>
  {foot_line('proposed; milestones in order, not dated; every line an assumption (A21)', delay=1.2, stage='')}
</div>'''
    return BASE_CSS, body, None
