"""Slide 05: does my control look like yours? First one control everybody uses: RSL3, in four JUMP labs (results/e16), well by
well. Then all eight JUMP positive controls agree less with other labs than with their own lab's plates (results/e8), and on
the map labs agree more on the same drug and tell drugs apart better (results/e12). The detail is boards A9 and A14. Written whole."""
import base64

from parts import *

PUBMED_RSL3 = 1211       # PubMed records for 'RSL3', all fields, 15 Oct 2026 [16]; it grows daily, so the slide rounds it


def rsl3_card(e16):
    """05a: each lab's untreated well above its RSL3 well, same plate, DNA stain, 300 micrometres; the share of cells left under each."""
    R = e16['RSL3']['result']['by_lab']; img = e16['images']['labs']
    labs = sorted(R, key=lab_number)
    uri = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
    odd = max(labs, key=lambda l: R[l]['cells_vs_dmso'])
    tile = lambda f, alt, ring: (f'<img src="{uri(f)}" alt="{alt}" style="width:100%; aspect-ratio:1; border-radius:8px; display:block; '
                                 f'background:#000;{ring}">')
    cells = []
    for l in labs:
        ch = img[l]['channels']['DNA']
        left = R[l]['cells_vs_dmso']
        cells.append(f'<div style="display:flex; flex-direction:column; gap:7px; min-width:0;"><span style="{SANS} font-size:17px; font-weight:600; color:{INK};">{lab_name(l)}</span>'
                     + tile(ch['dmso'], f'Untreated well, {lab_name(l)}, DNA stain.', '')
                     + tile(ch['rsl3'], f'RSL3 well on the same plate, {lab_name(l)}, DNA stain.', f' outline:{4 if l == odd else 2}px solid {INK if l == odd else INK2}; outline-offset:-{4 if l == odd else 2}px;')
                     + f'<span style="{SANS} font-size:18px; font-weight:{700 if l == odd else 500}; color:{INK};">{100 * left:.0f}% of cells left</span></div>')
    rows = (f'<div style="display:grid; grid-template-rows:22px 1fr 1fr 24px; row-gap:7px; padding-right:4px; {SANS} font-size:16px; color:{MUTE};">'
            f'<span></span><span style="align-self:center;">untreated</span><span style="align-self:center; color:{INK};">RSL3</span><span></span></div>')
    return (f'<div style="display:flex; flex-direction:column; gap:10px; width:100%;">'
            f'<span style="{SANS} font-size:18px; color:{INK};">RSL3, a common ferroptosis control, in about {round(PUBMED_RSL3, -2):,} papers.{pdf(" [16]")}</span>'
            f'<div style="display:grid; grid-template-columns:72px repeat({len(labs)}, minmax(0, 1fr)); column-gap:12px;">{rows}{"".join(cells)}</div></div>')


def controls_chart(C):
    """For each positive control, grey dot: pairs of plates in one lab; dark dot: pairs across labs; arrow: the drop.
    Plate pairs (results/e8-same-drug-different-answer), so no plate is compared with a mean that includes it."""
    order = sorted(C, key=lambda c: -C[c]['agreement_same_lab'])
    row = 42
    ax = Axes(190, 18, 540, len(order) * row, (0, 1), (0, len(order)))
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>'
                 + text(ax.X(v), ax.y0 + ax.h + 28, f'{v:g}', 21, MUTE, 'middle'))
    for k, c in enumerate(order):
        cy = ax.y0 + k * row + 21
        own, other = max(C[c]['agreement_same_lab'], 0), max(C[c]['agreement_across_labs'], 0)
        xo, xp = ax.X(own), ax.X(other)
        g.append(text(ax.x0 - 14, cy + 7, c, 22, INK2, 'end'))
        mark = (f'<path d="M {xo:.1f} {cy} L {xp + 14:.1f} {cy}" stroke="#c3c9cb" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M {xp + 9:.1f} {cy} l 10 -6 l 0 12 z" fill="#c3c9cb"/>'
                f'<circle cx="{xo:.1f}" cy="{cy}" r="7" fill="{FAINT}"/><circle cx="{xp:.1f}" cy="{cy}" r="8" fill="{INK2}"/>')
        if k == 0:
            mark += text(xp - 14, cy + 6, 'other labs', 18, INK2, 'end', 600) + text(xo + 14, cy + 6, 'own lab', 18, MUTE)
        g.append(f'<g class="f" style="animation-delay:{0.3 + 0.06 * k:.2f}s">{mark}</g>')
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 58, 'agreement on what the drug does &#183; 1 = identical', 21, INK2, 'middle'))
    return svg(760, ax.y0 + ax.h + 66, g, fit=True, aria='For each of eight positive controls, a plate agrees less with other labs than with its own lab.')


def build():
    e8 = results('e8-redteam.json')
    C = results('e8-same-drug-different-answer.json')['compounds']      # plate pairs, same lab and across labs
    e11 = results('e11-known-answer.json')
    e12 = results('e12-field-normalization.json')['every_batch']
    e16 = results('e16-same-perturbation.json')
    R = e16['RSL3']['result']
    own = sum(C[c]['agreement_same_lab'] for c in C) / len(C)
    other = sum(C[c]['agreement_across_labs'] for c in C) / len(C)
    lower = sum(C[c]['agreement_across_labs'] < C[c]['agreement_same_lab'] for c in C)
    agree, margin = e12['agree_field'], e12['margin']
    assert lower == len(C), 'script says all eight drop'
    by = R['by_lab']; odd = max(by, key=lambda l: by[l]['cells_vs_dmso']); rest = [by[l]['cells_vs_dmso'] for l in by if l != odd]
    assert not any(f['lab'] == odd for f in e11['failed']), f'{odd} failed a known-drug check: the slide says its other controls worked'
    stat = lambda before, after, colour, what: (f'<div style="display:flex; flex-direction:column; gap:4px;">'
        f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1;"><span style="color:{D_DIM};">{before}</span> '
        f'<span style="color:{D_DIM}; font-weight:400;">&#8594;</span> <span style="color:{colour};">{after}</span></span>'
        f'<span style="{MONO} font-size:13px; line-height:1.45; color:{D_SOFT};">{what}</span></div>')
    third = ('drugs told apart &#183; up in every batch' if margin['field_better_in'] == f"{e12['n_batches']} of {e12['n_batches']}"
             else f'drugs told apart &#183; up in {margin["field_better_in"]}')
    rule = '<div style="height:1px; background:rgba(246,247,247,.18);"></div>'
    side = lambda k, inner, delay: (f'<div class="s s{k}"><div class="r" style="animation-delay:{delay}s; position:absolute; left:836px; top:{FIG_TOP}px; '
                                    f'width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:20px;">{inner}</div></div>')
    say = lambda v, c=D_TEXT, size=20: f'<span style="{SANS} font-size:{size}px; line-height:1.35; color:{c};">{v}</span>'
    right_a = side(0, f'<span style="{SANS} font-size:96px; font-weight:700; letter-spacing:-0.045em; line-height:0.95; color:{D_TEXT};">{100 * by[odd]["cells_vs_dmso"]:.0f}%</span>'
                   + say(f'of cells left in {lab_name(odd)} after RSL3.<br><span style="color:{D_SOFT};">{100 * min(rest):.0f}&#8211;{100 * max(rest):.0f}% in the other three labs.</span>')
                   + say(f'{lab_name(odd).capitalize()}&#8217;s other known drugs worked{pdf(" (A8)")}, so the camera is not the reason.', D_SOFT, 18)
                   + rule
                   + say('Across labs its wells agree far less.', D_TEXT, 20)
                   + pdf(say(f'Well to well: {R["own_lab"]:.2f} within a lab &#8594; {R["other_labs"]:.2f} across labs (1 = identical, results/e16).', D_DIM, 15))
                   + say(f'1 to 5 wells per lab: an example, not proof.', D_DIM, 17), 0.6)
    right_b = side(1, stat(f'{own:.2f}', f'{other:.2f}', D_TEXT, '')
                   + say(f'All {NUMBERS[len(C)]} known drugs: two plates agree less across labs than inside one. 1 = identical.', D_SOFT, 18)
                   + rule
                   + say('On the map, labs agree a little more:', D_TEXT, 20)
                   + f'<span style="{SANS} font-size:56px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{D_GREEN};">{agree["field_better_than_own_in"]}</span>'
                   + say('batches where labs agree more on the map than after each lab&#8217;s own correction.', D_SOFT, 18)
                   + pdf(f'<span style="{MONO} font-size:13px; line-height:1.5; color:{D_DIM};">pairs of plates, {NUMBERS[len(C)]} drugs (results/e8-same-drug-different-answer); per batch, '
                         f'{len(results("e12-field-normalization.json")["compounds"])} drugs: {agree["raw"]:.2f} raw &#8594; {agree["own"]:.2f} usual fix &#8594; {agree["field"]:.2f} on the map (results/e12)</span>'), 0.9)
    css = BASE_CSS + '''
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1 { opacity: 1; pointer-events: auto; }
    .flow .s .f, .flow .s .r, .flow .s .bar { animation-play-state: paused; }
    .step-0 .s0 .f, .step-1 .s1 .f, .step-0 .s0 .r, .step-1 .s1 .r { animation-play-state: running; }
    .flow { cursor: pointer; }
'''
    tag = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">Positive controls</span>'
    fig = lambda n: f'<span style="color:{D_TEXT}; font-weight:500;">fig {n}</span>'
    card = lambda k, inner, pad: (f'<div class="s s{k}"><div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; '
                                  f'{CARD_ON_DARK} padding:{pad}; display:flex; align-items:center; overflow:hidden;">{inner}</div></div>')
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(5, dark=True)}
  {header('05', '', dark=True, right_html=tag)}
  <h2 style="position:absolute; left:56px; top:86px; width:1100px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};">Does my control look like yours?</h2>
  {card(0, rsl3_card(e16), '14px 20px 12px')}
  {card(1, controls_chart(C), '14px 20px 10px')}
  <div class="s s0">{foot_line(f'{fig("4a")} RSL3 screened as a compound at JUMP&#8217;s dose &#183; one well per plate, 1&#8211;5 per lab, beside its untreated wells &#183; % of cells left: lab mean &#183; DNA stain, 300 &#181;m &#183; JUMP [7] &#183; PubMed [16] &#183; A9', dark=True)}</div>
  <div class="s s1">{foot_line(f'{fig("4b")} agreement between pairs of plates, same lab and across labs &#183; {e8["n_plates"]:,} plates &#183; {e8["n_labs"]} labs &#183; JUMP [7] &#183; A9, A14', dark=True)}</div>
  {cue(2, dark=True)}
  {right_a}{right_b}
</div>'''
    return css, body, {'tag': ['Positive controls', 'Positive controls']}


NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven']
