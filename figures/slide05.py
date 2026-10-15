"""Slide 05: does my control look like yours? Eight positive controls run in every JUMP lab agree less with other labs
than with their own lab's plates (results/e8); on the map, labs agree more on the same drug and tell drugs apart better
(results/e12). The detail is boards A9 and A14. Written whole."""
from parts import *


def controls_chart(C):
    """For each positive control: agreement of a plate with its own lab's other plates (grey) and with every other lab (pink)."""
    order = sorted(C, key=lambda c: -C[c]['agreement_with_own_lab'])
    row = 42
    ax = Axes(190, 18, 540, len(order) * row, (0, 1), (0, len(order)))
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>'
                 + text(ax.X(v), ax.y0 + ax.h + 26, f'{v:g}', 19, MUTE, 'middle'))
    for k, c in enumerate(order):
        y = ax.y0 + k * row
        own, other = max(C[c]['agreement_with_own_lab'], 0), max(C[c]['agreement_with_other_labs'], 0)
        g.append(text(ax.x0 - 14, y + 27, c, 20, INK, 'end'))
        g.append(f'<rect class="bar" style="animation-delay:{0.3 + 0.05 * k:.2f}s" x="{ax.x0}" y="{y + 7}" width="{ax.X(own) - ax.x0:.1f}" height="13" rx="3" fill="#c3c9cb"/>')
        g.append(f'<rect class="bar" style="animation-delay:{0.45 + 0.05 * k:.2f}s" x="{ax.x0}" y="{y + 22}" width="{max(ax.X(other) - ax.x0, 1):.1f}" height="13" rx="3" fill="{PINK}"/>')
        g.append(text(ax.X(own) + 8, y + 19, f'{own:.2f}', 16, MUTE) + text(ax.X(other) + 8, y + 34, f'{other:.2f}', 16, PINK, weight=600))
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 54, 'agreement on what the drug does (cosine)', 19, INK2, 'middle'))
    ky = ax.y0 + ax.h + 86
    g.append(f'<rect x="{ax.x0}" y="{ky - 13}" width="24" height="13" rx="3" fill="#c3c9cb"/>' + text(ax.x0 + 32, ky, 'with its own lab&#8217;s other plates', 18, INK2))
    g.append(f'<rect x="{ax.x0 + 330}" y="{ky - 13}" width="24" height="13" rx="3" fill="{PINK}"/>' + text(ax.x0 + 362, ky, 'with every other lab', 18, INK2))
    return svg(760, ky + 12, g, fit=True, aria='For each of eight positive controls run in every lab, a plate agrees less with other labs than with its own lab.')


def build():
    e8 = results('e8-redteam.json')
    C = e8['all_features']['compounds']
    e12 = results('e12-field-normalization.json')['every_batch']
    own = sum(C[c]['agreement_with_own_lab'] for c in C) / len(C)
    other = sum(C[c]['agreement_with_other_labs'] for c in C) / len(C)
    lower = sum(C[c]['agreement_with_other_labs'] < C[c]['agreement_with_own_lab'] for c in C)
    agree, margin = e12['agree_field'], e12['margin']
    words = {8: 'all eight'}.get(lower, f'{lower} of {len(C)}')
    stat = lambda big, colour, what: (f'<div style="display:flex; flex-direction:column; gap:4px;">'
                                      f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour};">{big}</span>'
                                      f'<span style="{MONO} font-size:13px; line-height:1.45; color:{D_SOFT};">{what}</span></div>')
    right = (f'<div class="r" style="animation-delay:0.9s; position:absolute; left:836px; top:172px; width:388px; display:flex; flex-direction:column; gap:20px;">'
             f'<span style="{SANS} font-size:24px; font-weight:600; line-height:1.25; color:{D_TEXT};">Less than it looks like your own.<br>For {words}.</span>'
             + stat(f'{own:.2f} &#8594; {other:.2f}', D_PINK, 'average agreement &#183; own lab &#8594; other labs')
             + f'<div style="height:1px; background:rgba(246,247,247,.18);"></div>{label("on the map", D_GREEN)}'
             + stat(f'{agree["raw"]:.2f} &#8594; {agree["field"]:.2f}', D_GREEN, f'labs agree on the same drug &#183; {agree["field_better_in"]} batches')
             + stat(f'{margin["raw"]:.2f} &#8594; {margin["field"]:.2f}', D_TEXT, f'drugs told apart &#183; {margin["field_better_in"]} batches')
             + f'<span style="{SANS} font-size:18px; line-height:1.3; color:{D_SOFT};">The lab comes out.<br>The drug stays.</span></div>')
    tag = f'<span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">Positive controls</span>'
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 48px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(5, dark=True)}
  {header('05', '', dark=True, right_html=tag)}
  <h2 style="position:absolute; left:56px; top:86px; width:1100px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};">Does my control <span style="color:{D_PINK};">look like yours?</span></h2>
  <div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:166px; width:748px; height:420px; {CARD_ON_DARK} padding:14px 20px 10px; display:flex; align-items:center; overflow:hidden;">{controls_chart(C)}</div>
  <div style="position:absolute; left:56px; bottom:44px; width:1000px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};"><span style="color:{D_TEXT}; font-weight:500;">fig 4</span> eight positive controls, run in every lab &#183; {e8["n_plates"]:,} plates &#183; {e8["n_labs"]} labs &#183; JUMP [7] &#183; A9, A14</div>
  {right}
</div>'''
    return BASE_CSS, body, None
