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
        cells.append(f'<div style="display:flex; flex-direction:column; gap:7px; min-width:0;">{label(lab_name(l), INK)}'
                     + tile(ch['dmso'], f'Untreated well, {lab_name(l)}, DNA stain.', '')
                     + tile(ch['rsl3'], f'RSL3 well on the same plate, {lab_name(l)}, DNA stain.', f' outline:3px solid {PINK if l == odd else INK2}; outline-offset:-3px;')
                     + f'<span style="{SANS} font-size:17px; font-weight:{700 if l == odd else 500}; color:{PINK if l == odd else INK};">{100 * left:.0f}% cells left</span></div>')
    rows = (f'<div style="display:grid; grid-template-rows:20px 1fr 1fr 22px; row-gap:7px; padding-right:4px; {MONO} font-size:13px; color:{MUTE};">'
            f'<span></span><span style="align-self:center;">untreated</span><span style="align-self:center; color:{INK};">RSL3</span><span></span></div>')
    return (f'<div style="display:flex; flex-direction:column; gap:10px; width:100%;">'
            f'{label(f"RSL3 &#183; a standard ferroptosis control &#183; in about {round(PUBMED_RSL3, -2):,} papers [16]")}'
            f'<div style="display:grid; grid-template-columns:72px repeat({len(labs)}, minmax(0, 1fr)); column-gap:12px;">{rows}{"".join(cells)}</div></div>')


def controls_chart(C):
    """For each positive control, grey dot: own lab; pink dot: every other lab; arrow: the drop."""
    order = sorted(C, key=lambda c: -C[c]['agreement_with_own_lab'])
    row = 42
    ax = Axes(190, 18, 540, len(order) * row, (0, 1), (0, len(order)))
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>'
                 + text(ax.X(v), ax.y0 + ax.h + 26, f'{v:g}', 19, MUTE, 'middle'))
    for k, c in enumerate(order):
        cy = ax.y0 + k * row + 21
        own, other = max(C[c]['agreement_with_own_lab'], 0), max(C[c]['agreement_with_other_labs'], 0)
        xo, xp = ax.X(own), ax.X(other)
        g.append(text(ax.x0 - 14, cy + 6, c, 20, INK2, 'end'))
        mark = (f'<path d="M {xo:.1f} {cy} L {xp + 14:.1f} {cy}" stroke="#c3c9cb" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M {xp + 9:.1f} {cy} l 10 -6 l 0 12 z" fill="#c3c9cb"/>'
                f'<circle cx="{xo:.1f}" cy="{cy}" r="7" fill="{FAINT}"/><circle cx="{xp:.1f}" cy="{cy}" r="8" fill="{PINK}"/>')
        if k == len(order) - 1:
            mark += text(xp - 14, cy + 6, 'other labs', 16, PINK, 'end', 600) + text(xo + 14, cy + 6, 'own lab', 16, MUTE)
        g.append(f'<g class="f" style="animation-delay:{0.3 + 0.06 * k:.2f}s">{mark}</g>')
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 54, 'agreement on what the drug does (cosine)', 19, INK2, 'middle'))
    return svg(760, ax.y0 + ax.h + 66, g, fit=True, aria='For each of eight positive controls, a plate agrees less with other labs than with its own lab.')


def build():
    e8 = results('e8-redteam.json')
    C = e8['all_features']['compounds']
    e12 = results('e12-field-normalization.json')['every_batch']
    e16 = results('e16-same-perturbation.json')
    R = e16['RSL3']['result']
    own = sum(C[c]['agreement_with_own_lab'] for c in C) / len(C)
    other = sum(C[c]['agreement_with_other_labs'] for c in C) / len(C)
    lower = sum(C[c]['agreement_with_other_labs'] < C[c]['agreement_with_own_lab'] for c in C)
    agree, margin = e12['agree_field'], e12['margin']
    assert lower == len(C), 'script says all eight drop'
    by = R['by_lab']; odd = max(by, key=lambda l: by[l]['cells_vs_dmso']); rest = [by[l]['cells_vs_dmso'] for l in by if l != odd]
    stat = lambda before, after, colour, what: (f'<div style="display:flex; flex-direction:column; gap:4px;">'
        f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1;"><span style="color:{D_DIM};">{before}</span> '
        f'<span style="color:{D_DIM}; font-weight:400;">&#8594;</span> <span style="color:{colour};">{after}</span></span>'
        f'<span style="{MONO} font-size:13px; line-height:1.45; color:{D_SOFT};">{what}</span></div>')
    third = ('drugs told apart &#183; up in every batch' if margin['field_better_in'] == f"{e12['n_batches']} of {e12['n_batches']}"
             else f'drugs told apart &#183; up in {margin["field_better_in"]}')
    rule = '<div style="height:1px; background:rgba(246,247,247,.18);"></div>'
    side = lambda k, inner, delay: (f'<div class="s s{k}"><div class="r" style="animation-delay:{delay}s; position:absolute; left:836px; top:{FIG_TOP}px; '
                                    f'width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:20px;">{inner}</div></div>')
    right_a = side(0, label(f'same drug &#183; {NUMBERS[R["n_labs"]]} labs', D_GREEN)
                   + stat(f'{R["own_lab"]:.2f}', f'{R["other_labs"]:.2f}', D_PINK, 'agreement, well to well &#183; same lab &#8594; other labs<br>1 = same effect')
                   + rule
                   + f'<span style="{SANS} font-size:20px; line-height:1.35; color:{D_TEXT};">{lab_name(odd)}: <b style="color:{D_PINK};">{100 * by[odd]["cells_vs_dmso"]:.0f}%</b> of cells left<br>'
                     f'<span style="color:{D_SOFT};">the others: {100 * min(rest):.0f}&#8211;{100 * max(rest):.0f}%</span></span>'
                   + f'<span style="{SANS} font-size:16px; line-height:1.4; color:{D_SOFT};">{lab_name(odd)}&#8217;s other controls worked:<br>the drug response differed, not the camera</span>'
                   + f'<span style="{MONO} font-size:13px; line-height:1.5; color:{D_DIM}; margin-top:auto;">one well per plate &#183; {R["n_plates"]} plates &#183; small numbers, A9</span>', 0.6)
    right_b = side(1, stat(f'{own:.2f}', f'{other:.2f}', D_PINK, f'all {NUMBERS[len(C)]} JUMP controls &#183; own lab &#8594; other labs')
                   + rule + label('on the map &#183; per batch', D_GREEN)
                   + stat(f'{agree["raw"]:.2f}', f'{agree["field"]:.2f}', D_GREEN, f'agreement with other labs &#183; up in {agree["field_better_in"]}')
                   + stat(f'{margin["raw"]:.2f}', f'{margin["field"]:.2f}', D_GREEN, third), 0.9)   # 'Lab comes out. Drug stays.' is said, not written
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
  <h2 style="position:absolute; left:56px; top:86px; width:1100px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};">Does my control <span style="color:{D_PINK};">look like yours?</span></h2>
  {card(0, rsl3_card(e16), '14px 20px 12px')}
  {card(1, controls_chart(C), '14px 20px 10px')}
  <div class="s s0">{foot_line(f'{fig("4a")} RSL3 &#183; one well per plate, beside its untreated wells &#183; DNA stain, 300 &#181;m &#183; JUMP [7] &#183; PubMed [16]', dark=True)}</div>
  <div class="s s1">{foot_line(f'{fig("4b")} {e8["n_plates"]:,} plates &#183; {e8["n_labs"]} labs &#183; JUMP [7] &#183; A9, A14', dark=True)}</div>
  {cue(2, dark=True)}
  {right_a}{right_b}
</div>'''
    return css, body, {'tag': ['Positive controls', 'Positive controls']}


NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven']
