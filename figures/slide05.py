"""Slide 05: does my control look like yours? Eight positive controls run across the JUMP labs agree less with other labs
than with their own lab's plates (results/e8); on the map, labs agree more on the same drug and tell drugs apart better
(results/e12). Two views: the drop, then the map's answer. The detail is boards A9 and A14. Written whole."""
from parts import *


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
    own = sum(C[c]['agreement_with_own_lab'] for c in C) / len(C)
    other = sum(C[c]['agreement_with_other_labs'] for c in C) / len(C)
    lower = sum(C[c]['agreement_with_other_labs'] < C[c]['agreement_with_own_lab'] for c in C)
    agree, margin = e12['agree_field'], e12['margin']
    assert lower == len(C), 'script says all eight drop'
    stat = lambda before, after, colour, what: (f'<div style="display:flex; flex-direction:column; gap:4px;">'
        f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1;"><span style="color:{D_DIM};">{before}</span> '
        f'<span style="color:{D_DIM}; font-weight:400;">&#8594;</span> <span style="color:{colour};">{after}</span></span>'
        f'<span style="{MONO} font-size:13px; line-height:1.45; color:{D_SOFT};">{what}</span></div>')
    third = ('drugs told apart &#183; up in every batch' if margin['field_better_in'] == f"{e12['n_batches']} of {e12['n_batches']}"
             else f'drugs told apart &#183; up in {margin["field_better_in"]}')
    right = (f'<div class="r" style="animation-delay:0.9s; position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:20px;">'
             + stat(f'{own:.2f}', f'{other:.2f}', D_PINK, 'agreement per plate &#183; own lab &#8594; other labs')
             + '<div class="s s1" style="display:flex; flex-direction:column; gap:20px; flex:1;">'
             + f'<div style="height:1px; background:rgba(246,247,247,.18);"></div>{label("on the map &#183; per batch", D_GREEN)}'
             + stat(f'{agree["raw"]:.2f}', f'{agree["field"]:.2f}', D_GREEN, f'agreement with other labs &#183; up in {agree["field_better_in"]}')
             + stat(f'{margin["raw"]:.2f}', f'{margin["field"]:.2f}', D_GREEN, third)
             + f'<span style="{SANS} font-size:26px; font-weight:600; line-height:1.25; letter-spacing:-0.01em; color:{D_TEXT}; margin-top:auto;">Lab comes out.<br>Drug stays.</span></div></div>')
    css = BASE_CSS + '''
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1 { opacity: 1; pointer-events: auto; }
    .flow .s .f, .flow .s .r, .flow .s .bar { animation-play-state: paused; }
    .step-0 .s0 .f, .step-1 .s1 .f, .step-0 .s0 .r, .step-1 .s1 .r { animation-play-state: running; }
    .flow { cursor: pointer; }
'''
    tag = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">Positive controls</span>'
    fig = f'<span style="color:{D_TEXT}; font-weight:500;">fig 4</span>'
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(5, dark=True)}
  {header('05', '', dark=True, right_html=tag)}
  <h2 style="position:absolute; left:56px; top:86px; width:1100px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};">Does my control <span style="color:{D_PINK};">look like yours?</span></h2>
  <div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} padding:14px 20px 10px; display:flex; align-items:center; overflow:hidden;">{controls_chart(C)}</div>
  {foot_line(f'{fig} eight positive controls &#183; {e8["n_plates"]:,} plates &#183; {e8["n_labs"]} labs &#183; JUMP [7] &#183; A9, A14', dark=True)}
  <div style="position:absolute; right:56px; bottom:44px; {MONO} font-size:13px; color:{D_DIM};"><span data-h="hint">click &#8594; on the map</span></div>
  {right}
</div>'''
    return css, body, {'tag': ['Positive controls', 'On the map'], 'hint': ['click \u2192 on the map', '\u2193 the data economy']}
