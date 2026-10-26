"""Slide 05: even known drugs look different across labs. First one control everybody uses: RSL3, at the same dose in three JUMP labs
(results/e16, same_dose_only), its structure as JUMP records it (results/rsl3-structure.json), each RSL3 well beside a DMSO
well of the same plate. Lab 7 ran it at a sixteenth of the dose [7] and is left out of the comparison (A9 shows it). Then all
eight JUMP positive controls, 5 uM in every lab [7], agree less with other labs than with their own lab's plates (results/e8),
and on the map labs agree more on the same drug (results/e12). The detail is boards A9 and A14. Written whole."""
import base64
import json
import re

from parts import *

PUBMED_RSL3 = 1211       # PubMed records for 'RSL3', all fields, 15 Oct 2026 [16]; it grows daily, so the slide rounds it
# what each positive control acts on: JUMP-Target compound annotations, targets from the Drug Repurposing Hub [24]
TARGETS = {'AMG900': 'blocks Aurora kinases', 'dexamethasone': 'activates the glucocorticoid receptor', 'FK-866': 'blocks NAMPT, NAD+ supply',
           'LY2109761': 'blocks TGF-&#946; receptors', 'NVS-PAK1-1': 'blocks PAK1 kinase', 'quinidine': 'blocks ion channels',
           'TC-S-7004': 'blocks DYRK1A/B kinases', 'aloxistatin': 'blocks cysteine proteases'}
CONTROL_UM, COMPOUND_UM = 5, 10                 # JUMP methods [7]: positive controls 5 uM in every lab; library compounds 10 uM (lab 7: 0.625)


def formula(f):
    """C23H21ClN2O5 with its counts as subscripts."""
    return re.sub(r'(\d+)', r'<sub>\1</sub>', f)


def structure():
    """RSL3 as JUMP records it (figures/structure.py drew it from metadata/compound.csv.gz), the reactive group shaded."""
    rec = json.load(open('results/rsl3-structure.json'))
    assert rec['inchikey_matches_jump'] and not rec['any_stereo_specified'], 'the drawing is the record, and the record has no stereochemistry'
    svg_ = open('figures/assets/rsl3-warhead.svg').read()
    svg_ = re.sub(r'<\?xml[^>]*>\s*', '', svg_).replace('#e3e6e7', GRID)          # the shade a step darker, so it reads on the card
    svg_ = re.sub(r"width='\d+px' height='\d+px'", "width='100%' style='display:block; height:auto;'", svg_, count=1)
    return svg_, rec


def rsl3_card(e16):
    """05a. Left: the molecule (as JUMP records it), its reactive group shaded, and what it does to a cell. Right: the three labs
    that ran RSL3 at the same dose, each lab's DMSO well above its RSL3 well on the same plate, DNA stain, 300 micrometres, and the
    share of cells left under each. Lab 7 (0.625 uM, a sixteenth [7]) is left out here and shown on A9."""
    S = e16['RSL3']['same_dose_only']; B = S['by_lab']; img = e16['images']['labs']
    labs = sorted(S['labs'], key=lab_number)
    assert S['dose_um'] == COMPOUND_UM and all(l in img for l in labs)
    uri = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
    tile = lambda f, alt, ring: (f'<img src="{uri(f)}" alt="{alt}" style="width:100%; aspect-ratio:1; border-radius:8px; display:block; '
                                 f'background:#000;{ring}">')
    span = lambda html, extra='': f'<span style="grid-column:1 / -1; {extra}">{html}</span>'
    grid = ''.join(f'<span style="display:flex; align-items:center; gap:5px; {SANS} font-size:18px; font-weight:600; color:{INK};">{icon("lab", INK2, 18)}{lab_name(l)}</span>' for l in labs)
    grid += span('DMSO, no drug', f'{SANS} font-size:18px; color:{MUTE};')
    um = {img[l]['tile_um'] for l in labs}; assert len(um) == 1, 'one scale for every tile'
    bar = scale_bar(um.pop(), inset=7, height=3.5, size=13, right=True)
    grid += ''.join(f'<div style="position:relative;">{tile(img[l]["channels"]["DNA"]["dmso"], f"DMSO well, {lab_name(l)}, DNA stain.", "")}{bar if k == 0 else ""}</div>'
                    for k, l in enumerate(labs))
    grid += span(f'RSL3, {COMPOUND_UM} &#181;M, 48 h', f'{SANS} font-size:18px; font-weight:600; color:{INK};')
    grid += ''.join(f'<div style="position:relative;">' + tile(img[l]['channels']['DNA']['rsl3'], f'RSL3 well on the same plate, {lab_name(l)}, DNA stain.',
                         f' outline:2px solid {INK2}; outline-offset:-2px;') + (stain_chip('DNA', inset=7, size=13, top=True) if k == len(labs) - 1 else '') + '</div>'
                    for k, l in enumerate(labs))      # one chip for both rows, where the field is empty
    grid += ''.join(f'<span style="{SANS} white-space:nowrap; color:{INK};"><span style="font-size:20px; font-weight:700;">{100 * B[l]["cells_vs_dmso"]:.0f}%</span>'
                    + '</span>' for k, l in enumerate(labs))
    drawing, rec = structure()
    step = lambda ic, t, first=False: ((f'<span style="color:{MUTE}; font-size:13px; line-height:1; padding-left:6px;">&#8595;</span>' if not first else '')
                                       + f'<span style="display:flex; gap:8px; align-items:center;">{icon(ic, INK2, 22)}<span>{t}</span></span>')
    shade = f'<span style="background:{GRID}; border-radius:4px; padding:0 4px;">shaded group</span>'
    chem = (f'<div style="display:flex; flex-direction:column; gap:6px; min-width:0;">'
            f'<span style="{SANS} font-size:24px; font-weight:700; letter-spacing:-0.02em; line-height:1; color:{INK};">RSL3</span>'
            + f'<div style="width:212px; margin:2px 0 0 2px;">{drawing}</div>'
            + pdf(f'<span style="{MONO} font-size:11px; line-height:1.35; color:{MUTE};">{formula(rec["formula"])}, as JUMP records it,<br>no stereo; active form (1S,3R) [19]</span>')
            + f'<div style="display:flex; flex-direction:column; gap:2px; {SANS} font-size:18px; line-height:1.3; color:{INK};">'
            + step('binds', f'{shade} binds GPX4{pdf(f"<span style={chr(34)}{MONO} font-size:11px; color:{MUTE};{chr(34)}>&#8201;[19,21]</span>")}', True)
            + step('peroxide', f'lipid peroxides pile up{pdf(f"<span style={chr(34)}{MONO} font-size:11px; color:{MUTE};{chr(34)}>&#8201;[20,22]</span>")}')
            + step('cell-dies', f'cell dies <span style="color:{MUTE};">ferroptosis</span>{pdf(f"<span style={chr(34)}{MONO} font-size:11px; color:{MUTE};{chr(34)}>&#8201;[20]</span>")}')
            + '</div></div>')
    wells = (f'<div style="display:grid; grid-template-columns:repeat({len(labs)}, 132px); column-gap:10px; row-gap:5px; align-content:center;">'
             f'{grid}</div>')
    return (f'<div style="display:flex; justify-content:space-between; align-items:center; gap:20px; width:100%;">'
            f'<div style="flex:1 1 0; min-width:0;">{chem}</div>{wells}</div>')


def controls_chart(C):
    """For each positive control, grey dot: pairs of plates in one lab; dark dot: pairs across labs; arrow: the drop.
    Plate pairs (results/e8-same-drug-different-answer), so no plate is compared with a mean that includes it."""
    order = sorted(C, key=lambda c: -C[c]['agreement_same_lab'])
    assert set(order) == set(TARGETS), 'one target line per control'
    row = 44
    ax = Axes(268, 18, 470, len(order) * row, (0, 1), (0, len(order)))
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" fill="{PANEL}"/>']
    for v in (0, 0.25, 0.5, 0.75, 1):
        g.append(f'<path d="M {ax.X(v):.1f} {ax.y0} L {ax.X(v):.1f} {ax.y0 + ax.h}" stroke="{GRID}" stroke-width="2"/>'
                 + text(ax.X(v), ax.y0 + ax.h + 28, f'{v:g}', 21, MUTE, 'middle'))
    for k, c in enumerate(order):
        cy = ax.y0 + k * row + 22
        own, other = max(C[c]['agreement_same_lab'], 0), max(C[c]['agreement_across_labs'], 0)
        xo, xp = ax.X(own), ax.X(other)
        g.append(text(ax.x0 - 14, cy + 7, c, 21, INK, 'end', 600) + text(ax.x0 - 14, cy + 25, TARGETS[c], 14, MUTE, 'end', 400, 'class="pdf"'))
        mark = (f'<path d="M {xo:.1f} {cy} L {xp + 14:.1f} {cy}" stroke="#c3c9cb" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M {xp + 9:.1f} {cy} l 10 -6 l 0 12 z" fill="#c3c9cb"/>'
                f'<circle cx="{xo:.1f}" cy="{cy}" r="7" fill="{FAINT}"/><circle cx="{xp:.1f}" cy="{cy}" r="8" fill="{INK2}"/>')
        if k == 0:
            mark += text(xp - 14, cy + 7, 'other labs', 20, INK2, 'end', 600) + text(xo + 14, cy + 7, 'same lab', 20, MUTE)
        g.append(f'<g class="f" style="animation-delay:{0.3 + 0.06 * k:.2f}s">{mark}</g>')
    g.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 54, 'agreement (1 = perfect)', 20, INK2, 'middle', extra='class="talk"')
             + text(ax.x0 + ax.w / 2, ax.y0 + ax.h + 54, 'agreement on what the drug does (1 = perfect)', 20, INK2, 'middle', extra='class="pdf"'))
    return svg(760, ax.y0 + ax.h + 62, g, fit=True, aria=f'For each of eight positive controls, all at {CONTROL_UM} micromolar in every lab, a plate agrees less with '
               'other labs than with its own lab. Under each drug, what it acts on.')


def build():
    e8 = results('e8-redteam.json')
    partial = ', '.join(f'{c} in {v["n_labs"]}' for c, v in e8['all_features']['compounds'].items() if v['n_labs'] < e8['n_labs'])      # LY2109761 runs in 10 of the 11 labs
    C = results('e8-same-drug-different-answer.json')['compounds']      # plate pairs, same lab and across labs
    e12 = results('e12-field-normalization.json')['every_batch']
    e16 = results('e16-same-perturbation.json')
    R = e16['RSL3']['result']
    own = sum(C[c]['agreement_same_lab'] for c in C) / len(C)
    other = sum(C[c]['agreement_across_labs'] for c in C) / len(C)
    lower = sum(C[c]['agreement_across_labs'] < C[c]['agreement_same_lab'] for c in C)
    agree, margin = e12['agree_field'], e12['margin']
    assert lower == len(C), 'script says all eight drop'
    e10 = results('e10-certificate-predicts-answer.json')                 # e12 is reported over the drugs labs agree on
    by = e10['agreement_with_the_field_by_compound']
    assert sorted(results('e12-field-normalization.json')['compounds']) == sorted(e10['compounds_pooled'])
    left_out = ', '.join(f'{c} {by[c]:.2f}' for c in by if c not in e10['compounds_pooled']) + f', under {e10["threshold"]}, e10'
    SD = e16['RSL3']['same_dose_only']                              # the labs at 10 uM; JUMP methods [7]: source_7 at 0.625 uM
    out = SD['left_out']
    assert set(out) == {'source_7'} and out['source_7']['dose_um'] == 0.625, 'lab 7 is left out for its dose, and only lab 7'
    cells = [SD['by_lab'][l]['cells_vs_dmso'] for l in SD['labs']]
    same = SD['controls_on_the_same_plates']; ctl = SD['compared']
    assert SD['own_lab'] > SD['other_labs'] and ctl['own_lab']['controls_median'] > ctl['other_labs']['controls_median']
    stat = lambda before, after, colour, what: (f'<div style="display:flex; flex-direction:column; gap:4px;">'
        f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.035em; line-height:1;"><span style="color:{D_DIM};">{before}</span> '
        f'<span style="color:{D_DIM}; font-weight:400;">&#8594;</span> <span style="color:{colour};">{after}</span></span>'
        f'<span style="{MONO} font-size:13px; line-height:1.45; color:{D_SOFT};">{what}</span></div>')
    rule = '<div style="height:1px; background:rgba(246,247,247,.18);"></div>'
    side = lambda k, inner, delay: (f'<div class="s s{k}"><div class="r" style="animation-delay:{delay}s; position:absolute; left:836px; top:{FIG_TOP}px; '
                                    f'width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:20px;">{inner}</div></div>')
    say = lambda v, c=D_TEXT, size=20: f'<span style="{SANS} font-size:{size}px; line-height:1.35; color:{c};">{v}</span>'
    tick = lambda ic, c, words, size=22: f'<span style="display:flex; align-items:center; gap:10px;">{icon(ic, c, 28)}{say(words, c, size)}</span>'
    alike = lambda v, c, ic, words: (f'<div style="display:flex; align-items:center; gap:10px;"><span style="display:block; width:{240 * v:.0f}px; height:12px; border-radius:3px; background:{c}; flex-shrink:0;"></span>'
                                     f'{ic}{say(words, D_SOFT, 18)}</div>')
    right_a = side(0, f'<div style="display:flex; flex-direction:column; gap:6px;"><span style="{SANS} font-size:96px; font-weight:700; letter-spacing:-0.045em; line-height:0.95; color:{D_TEXT};">{100 * min(cells):.0f}&#8211;{100 * max(cells):.0f}%</span>'
                   + say('cells left', D_TEXT, 22) + '</div>'
                   + tick('check', D_SOFT, 'same dose, same kill')
                   + rule.replace('style="', 'style="margin-top:auto; ', 1)
                   + tick('cross', D_TEXT, 'same look')
                   + '<div style="display:flex; flex-direction:column; gap:10px; margin-top:-6px;">'
                   + alike(SD['own_lab'], D_SOFT, icon('lab', D_SOFT, 20), 'same lab')
                   + alike(SD['other_labs'], D_DIM, icon('lab', D_DIM, 20) + icon('lab', D_DIM, 20), 'other labs') + '</div>'
                   + pdf(say(f'Bars: agreement well to well at {COMPOUND_UM} &#181;M, {SD["own_lab"]:.2f} in the same lab, {SD["other_labs"]:.2f} across labs (1 = perfect); '
                             f'known drugs on the same plates {ctl["own_lab"]["controls_median"]:.2f} &#8594; {ctl["other_labs"]["controls_median"]:.2f}.<br>'
                             f'An example, not proof: {NUMBERS[SD["n_wells"]]} wells in {NUMBERS[len(cells)]} labs (A9).', D_DIM, 15)), 0.6)
    ref = lambda r: pdf(f'<span style="{MONO} font-size:12px; color:{D_DIM};">&#8201;{r}</span>')
    cost = lambda ic, words, r: (f'<span style="display:flex; align-items:center; gap:12px;">{icon(ic, D_TEXT, 26)}'
                                 f'<span style="{SANS} font-size:19px; line-height:1.25; color:{D_TEXT};">{words}{ref(r)}</span></span>')
    right_b = side(1, f'<div style="display:flex; flex-direction:column; gap:18px;">'
                      f'<span style="{MONO} font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:{D_SOFT};">what it costs</span>'
                   + cost('no-replicate', 'hits don&#8217;t replicate', '[13], e8')
                   + cost('no-pool', 'data won&#8217;t pool', '06, [13]')
                   + cost('model', 'models learn the lab', '03, e1') + '</div>'
                   + pdf(f'<span style="{MONO} font-size:13px; line-height:1.45; color:{D_DIM};">mean agreement between plates: same lab {own:.2f} &#8594; other labs {other:.2f}</span>')
                   + f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:12px;">'
                     f'<span style="{MONO} font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">on the map</span>'
                   + stat_tile(agree["field_better_than_own_in"], f'<span style="display:flex; align-items:center; gap:8px;">{icon("map", D_GREEN, 22)}batches agree more with other labs</span>',
                               f'than on their own controls<br>by chance: about {round(e12["n_batches"] / 2)}', D_GREEN, size=48) + '</div>', 0.9)
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
  <h2 style="position:absolute; left:56px; top:86px; width:1100px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{D_TEXT};">Even known drugs <span style="color:{D_GREEN};">look different across labs</span>.</h2>
  {card(0, rsl3_card(e16), '14px 20px 12px')}
  {card(1, f'<div style="display:flex; flex-direction:column; gap:4px; width:100%; height:100%;"><div style="display:flex; align-items:center; gap:12px;">{icon("drug", INK2, 22)}'
           f'<span style="{SANS} font-size:18px; color:{INK};">{NUMBERS[len(C)].capitalize()} known drugs, {CONTROL_UM} &#181;M in every lab.</span></div>'
           f'<div style="flex:1; min-height:0; display:flex; align-items:center;">{controls_chart(C)}</div></div>', '14px 20px 10px')}
  <div class="s s0">{foot_line(f'{fig("4a")} RSL3 at JUMP&#8217;s dose [7], one well per plate; cells left: nuclei per field against the same plate&#8217;s DMSO wells, lab means; lab 7 (0.625 &#181;M, {100 * out["source_7"]["cells_vs_dmso"]:.0f}% left) left out, A9; {round(PUBMED_RSL3, -2):,}+ PubMed records on RSL3 [16]; it blocks TXNRD1, not recombinant GPX4 [22]', dark=True)}</div>
  <div class="s s1">{foot_line(f'{fig("4b")} plate pairs, same lab and across labs, {CONTROL_UM} &#181;M [7], {e8["n_plates"]:,} plates, {e8["n_labs"]} labs ({partial}), targets [24]; per batch, {len(results("e12-field-normalization.json")["compounds"])} drugs labs agree on ({left_out}): {agree["raw"]:.2f} raw &#8594; {agree["own"]:.2f} usual fix &#8594; {agree["field"]:.2f} on the map; A9, A14, results/e8, e12', dark=True)}</div>
  {cue(2, dark=True)}
  {right_a}{right_b}
</div>'''
    return css, body, {'tag': ['Positive controls', 'Positive controls']}



def known_drugs():
    """The eight known drugs, as one view of the problem slide (04b since 26 Oct): (card inner, side inner, caption).
    Plate pairs agree less across labs than inside one lab (results/e8); on the map they agree more (results/e12)."""
    e8 = results('e8-redteam.json')
    partial = ', '.join(f'{c} in {v["n_labs"]}' for c, v in e8['all_features']['compounds'].items() if v['n_labs'] < e8['n_labs'])      # LY2109761 runs in 10 of the 11 labs
    C = results('e8-same-drug-different-answer.json')['compounds']
    e12 = results('e12-field-normalization.json')['every_batch']
    own = sum(C[c]['agreement_same_lab'] for c in C) / len(C)
    other = sum(C[c]['agreement_across_labs'] for c in C) / len(C)
    assert sum(C[c]['agreement_across_labs'] < C[c]['agreement_same_lab'] for c in C) == len(C), 'script says all eight drop'
    agree = e12['agree_field']
    e10 = results('e10-certificate-predicts-answer.json'); by = e10['agreement_with_the_field_by_compound']
    left_out = ', '.join(f'{c} {by[c]:.2f}' for c in by if c not in e10['compounds_pooled']) + f', under {e10["threshold"]}, e10'
    ref = lambda r: pdf(f'<span style="{MONO} font-size:12px; color:{D_DIM};">&#8201;{r}</span>')
    cost = lambda ic, words, r: (f'<span style="display:flex; align-items:center; gap:12px;">{icon(ic, D_TEXT, 26)}'
                                 f'<span style="{SANS} font-size:19px; line-height:1.25; color:{D_TEXT};">{words}{ref(r)}</span></span>')
    card = (f'<div style="display:flex; flex-direction:column; gap:4px; width:100%; height:100%; box-sizing:border-box; padding:14px 2px 10px;">'
            f'<div style="display:flex; align-items:center; gap:12px;">{icon("drug", INK2, 22)}'
            f'<span style="{SANS} font-size:18px; color:{INK};">{NUMBERS[len(C)].capitalize()} known drugs, {CONTROL_UM} &#181;M in every lab.</span></div>'
            f'<div style="flex:1; min-height:0; display:flex; align-items:center;">{controls_chart(C)}</div></div>')
    side = (''      # 26 Oct declutter: the value list left (05a says it); the proof stays
            + pdf(f'<span style="{MONO} font-size:13px; line-height:1.45; color:{D_DIM};">mean agreement between plates: same lab {own:.2f} &#8594; other labs {other:.2f}</span>')
            + f'<div style="display:flex; flex-direction:column; gap:12px;">'
              f'<span style="{MONO} font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">on the map</span>'
            + stat_tile(agree["field_better_than_own_in"], f'<span style="display:flex; align-items:center; gap:8px;">{icon("map", D_GREEN, 22)}batches agree more with other labs</span>',
                        f'than on their own controls<br>by chance: about {round(e12["n_batches"] / 2)}', D_GREEN, size=48) + '</div>')
    foot = (f'plate pairs, same lab and across labs, {CONTROL_UM} &#181;M [7], {e8["n_plates"]:,} plates, {e8["n_labs"]} labs ({partial}), targets [24]; '
            f'{len(results("e12-field-normalization.json")["compounds"])} drugs labs agree on: {agree["raw"]:.2f} raw, {agree["own"]:.2f} usual fix, {agree["field"]:.2f} on the map; RSL3 A9; A14, e8, e12')
    return card, side, foot

NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven']
