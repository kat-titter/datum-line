"""Slide 05 since 26 Oct 2026 (07 before): the product. First what it is, in one picture: a shared repository of raw cell images that labs feed free and
scientists, AI agents and companies join as members, with the map, the check and the benchmark inside. Then the product
as one lab would have seen it on one day; and the leaderboard. The shared-data table (every lab's controls as a dataset
each batch checked) is board A25. Written whole from results/e1, e9, e12, e2 and e14.

The batch shown is the lab's in-distribution batch with the most plates. Its whole replay is appendix A11; the leaderboard is A17.
"""
import random
from datetime import date

from parts import *
from slide04 import embedding, map_axes

LAB = 'source_2'
TICK = '<path d="M -6 0.5 L -2 4.5 L 6 -4.5" fill="none" stroke="#ffffff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'


def well_image(lab, plate=None, name=None):
    """A DNA image of one untreated well, as a data URI: from cache/images when it is there, else from figures/assets."""
    import base64, glob, shutil, os
    asset = f'figures/assets/{name}.png'
    if plate is None:
        hits = sorted(glob.glob(f'cache/images/{lab}/*/DNA.png'))
    else:
        hits = [f'cache/images/{lab}/{plate}/DNA.png']
    hit = next((h for h in hits if os.path.exists(h)), None)
    if hit and not os.path.exists(asset):
        from PIL import Image
        im = Image.open(hit); w, h = im.size; c = min(w, h) // 2      # the middle of the field, so cells read at thumbnail size
        im.crop(((w - c) // 2, (h - c) // 2, (w + c) // 2, (h + c) // 2)).resize((256, 256), Image.LANCZOS).save(asset, optimize=True)
    src = asset if os.path.exists(asset) else 'figures/assets/well-I01-dna.jpg'
    kind = 'png' if src.endswith('.png') else 'jpeg'
    return f'data:image/{kind};base64,' + base64.b64encode(open(src, 'rb').read()).decode()


def centre(rows):
    return sum(float(r['pc1']) for r in rows) / len(rows), sum(float(r['pc2']) for r in rows) / len(rows)


def your_map(B, now):
    """The field in green, this lab's wells to date in pale pink, and the batch just sent as the dot."""
    rows = embedding()
    W, H = 1520, 490
    ax, cloud = map_axes(rows, 24, 24, W - 48, H - 112, pad=0.06)       # 26 Oct: the key in a strip under the plot
    others = sorted({r['lab'] for r in rows if r['lab'] != LAB}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    g = [f'<rect width="{W}" height="{H - 64}" rx="18" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::3], colour[l], 4.2, 'opacity="0.7"') for l in others]
    mine = [r for r in rows if r['lab'] == LAB]
    sent = B[:B.index(now) + 1]
    seen = [r for r in mine if any(r['plate'] in b['plates'] for b in sent)]
    seen = ([r for r in seen if r['target'] != 'True'] + random.Random(0).sample([r for r in seen if r['target'] == 'True'], 8))[::3]   # drawn as every lab is: 8 a plate, one in three
    g.append(cloud(seen, PALE_PINK, 4.2, 'opacity="0.8"'))
    here = centre([r for r in mine if r['plate'] in now['plates']])
    near = centre([r for r in rows if r['lab'] == now['nearest_other']])
    x, y = ax.X(here[0]), ax.Y(here[1]); nx, ny = ax.X(near[0]), ax.Y(near[1])
    g.append(f'<path d="M {x:.1f} {y:.1f} L {nx:.1f} {ny:.1f}" stroke="{INK2}" stroke-width="2.5" stroke-dasharray="7 7"/>')
    g.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="11" fill="{GREEN}" stroke="#ffffff" stroke-width="4"/>')
    # 26 Oct (Kat: "lines to connect related elements"): the batch in the drop zone above lands here; the stack sits about 100 units in
    g.append(f'<g class="f" style="animation-delay:0.9s"><path d="M 103 0 L {x:.1f} {y - 18:.1f}" stroke="{PINK}" stroke-width="3" stroke-dasharray="6 6" stroke-linecap="round" opacity="0.8"/></g>')
    g.append(f'<circle class="ping" cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{PINK}" stroke-width="3"/>')
    g.append(f'<circle class="pop" style="animation-delay:1.2s" cx="{x:.1f}" cy="{y:.1f}" r="16" fill="{PINK}" stroke="#ffffff" stroke-width="4"/>')
    ky = H - 14
    g.append(f'<g class="f" style="animation-delay:1.4s">'
             f'<circle cx="34" cy="{ky - 12}" r="6" fill="{colour[others[len(others) // 2]]}"/>' + text(50, ky, 'one well', 36, INK2)
             + f'<circle cx="256" cy="{ky - 12}" r="13" fill="{PINK}" stroke="#ffffff" stroke-width="3"/>' + text(280, ky, 'this batch', 36, INK2)
             + f'<circle cx="498" cy="{ky - 12}" r="11" fill="{GREEN}" stroke="#ffffff" stroke-width="3"/>' + text(520, ky, 'lab centre', 36, INK2) + '</g>')
    g.append(text(36, H - 64 - 22, 'PC 1 &#8594;', 28, MUTE, extra='class="pdf"'))
    g.append(f'<g class="pdf" transform="translate(44,{H - 64 - 60}) rotate(-90)">{text(0, 0, "PC 2 &#8594;", 28, MUTE)}</g>')
    return svg(W, H, g, aria='The field of eleven labs in green, this lab in pink, with its wells so far and a line to the nearest other lab.', fit=True)


def streak(B, now, place='margin-left:auto;'):
    """One mark per batch sent so far, and an open one for the next."""
    n = B.index(now) + 1
    mark = lambda k: (f'<g transform="translate({14 + k * 28},14)" class="f" style="animation-delay:{0.5 + 0.08 * k:.2f}s">'
                      f'<circle r="11" fill="{GREEN}"/><g transform="scale(.75)">{TICK}</g></g>')
    nxt = (f'<g transform="translate({14 + n * 28},14)"><circle r="10" fill="none" stroke="{PINK}" stroke-width="2" stroke-dasharray="4 4"/>'
           f'<path d="M -4 0 H 4 M 0 -4 V 4" stroke="{PINK}" stroke-width="2.2" stroke-linecap="round"/></g>')
    W = 28 + n * 28
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 28" width="{W}" height="28" role="img" '
            f'aria-label="{n} batches sent in a row, and a place for the next." style="display:block; flex-shrink:0; {place}">'
            + ''.join(mark(k) for k in range(n)) + nxt + '</svg>')


HUB_ICONS = {'scientists': '<circle cx="12" cy="8" r="3.4"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/>',
             'agents': '<rect x="5" y="5" width="14" height="14" rx="2.5"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
             'companies': '<path d="M3 21h18M5 21V7l7-4 7 4v14"/><path d="M9 10h2M13 10h2M9 14h2M13 14h2M9 18h2M13 18h2"/>',
             'images': '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.8"/><path d="M21 15l-5-4-7 6"/>'}
HUB_LABS = ['source_1', 'source_2', 'source_3', 'source_5', 'source_6', 'source_10']     # the six labs the room met on slide 03


def hub(n_wells, n_labs):
    """07a, left: the product in one picture. Control images come in from every lab, free; inside, the repository, the map,
    the check and the benchmark; out, by membership, to scientists, AI agents and companies."""
    ico = lambda key, colour, size=22: (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{colour}" stroke-width="1.8" '
                                        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink:0;">{key}</svg>')
    tile = lambda lab: (f'<div style="position:relative; width:64px; height:64px;"><img src="{well_image(lab, None, f"hub-{lab}")}" alt="Control well, {lab_name(lab)}, DNA stain." '
                        f'style="width:64px; height:64px; border-radius:9px; object-fit:cover; display:block; background:#000;'
                        f'{" outline:2.5px solid " + PINK + "; outline-offset:-2.5px;" if lab == LAB else ""}">'
                        f'<span class="pdf" style="position:absolute; left:5px; top:5px; padding:1px 6px; border-radius:999px; background:{PINK if lab == LAB else "rgba(20,23,26,.72)"}; '
                        f'{MONO} font-size:11px; color:#ffffff;">{lab_name(lab).replace("lab ", "")}</span></div>')
    head = lambda ico, word: (f'<span style="display:flex; align-items:center; gap:8px; {SANS} font-size:18px; font-weight:600; color:{GREEN};">'
                              f'{icon(ico, GREEN, 22)}{word}</span>')
    col_in = (f'<div style="display:flex; flex-direction:column; gap:10px; width:150px; flex-shrink:0;">{head("lab", "free")}'
              f'<div style="display:grid; grid-template-columns:repeat(2, 64px); gap:8px;">{"".join(tile(l) for l in HUB_LABS)}</div>'
              + stain_chip('DNA', size=18, inline=True, dark=False)
              + pdf(f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK2};">{NUMBERS[n_labs]} labs, control images (A18)</span>') + '</div>')
    inside = [(PATH_ICONS['map'], 'one map', 'every lab placed on it'),
              (HUB_ICONS['images'], 'raw images', 'kept, with their provenance'),
              (PATH_ICONS['certificate'], 'the check', 'every batch read against the field'),
              ('<path d="M4 21V4h11l-1 3 1 3H4"/><path d="M4 10h11"/>', 'benchmark', 'every method graded on one test')]
    col_hub = (f'<div style="flex:1 1 0; min-width:0; display:flex; flex-direction:column; gap:9px; padding:14px 16px 12px; border-radius:14px; background:{INK};">'
               f'<span style="{MONO} font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">Datum Line</span>'
               + ''.join(f'<span style="display:flex; align-items:center; gap:10px;">{ico(i, D_GREEN, 20)}<span style="display:flex; flex-direction:column;">'
                         f'<span style="{SANS} font-size:18px; font-weight:600; line-height:1.2; color:#ffffff;">{a}</span>'
                         + pdf(f'<span style="{SANS} font-size:14px; line-height:1.25; color:{D_SOFT};">{b}</span>') + '</span></span>' for i, a, b in inside)
               + '</div>')
    more = lambda v: pdf(f'<span style="font-size:14px; color:{MUTE};">{v}</span>')
    out = [(HUB_ICONS['scientists'], 'scientists', 'onboard assays with confidence' + more(': is my batch &#8220;normal&#8221;?')),
           (HUB_ICONS['agents'], 'AI agents', 'query comparable data' + more(', by API')),
           (HUB_ICONS['companies'], 'companies', 'drug discovery, stronger together' + more(': each dataset they buy, placed on the map'))]
    col_out = (f'<div style="display:flex; flex-direction:column; gap:12px; width:214px; flex-shrink:0;">{head("subscriptions", "subscription")}'
               + ''.join(f'<span style="display:flex; gap:10px; align-items:flex-start;">{ico(i, INK)}<span style="display:flex; flex-direction:column; gap:1px;">'
                         f'<span style="{SANS} font-size:18px; font-weight:600; line-height:1.2; color:{INK};">{a}</span>'
                         + f'<span style="{SANS} font-size:18px; line-height:1.3; color:{INK2};">{b}</span></span></span>' for i, a, b in out) + '</div>')
    arrow = f'<span aria-hidden="true" style="align-self:center; {SANS} font-size:28px; color:{GREEN}; padding:0 2px;">&#8594;</span>'
    foot = pdf(f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK2}; padding-top:10px; border-top:1px solid #d3d8da;">'
               f'Proposed terms: labs keep their data and a share of every subscription. A15, A24.</span>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:16px 18px 14px; display:flex; flex-direction:column; gap:12px;">'
            f'<div style="flex:1 1 0; min-height:0; display:flex; align-items:center; gap:4px;">{col_in}{arrow}{col_hub}{arrow}{col_out}</div>{foot}</div>')


def value(n_labs, n_wells):
    """05 (26 Oct, Kat: "more simple, more clear ... conventional graphs too"): one idea, one drug's shared change. AMG900 (5 uM,
    an Aurora kinase inhibitor: cells copy their DNA but cannot divide) in all eleven labs, each lab's median cell untreated and
    treated (results/e18), nuclei pink and cell bodies green; under each lab, on its column, a plain bar: its nuclear area treated
    over its own untreated, with 1x (DMSO) and the mean marked. Lab 2's bar is the one pink. The seven drugs' agreement, alone
    against aligned, left this slide for board A4 (results/e12)."""
    import base64
    e18 = results('e18-median-cell.json')
    labs = sorted(e18['labs'], key=lab_number)
    uri = lambda src, c: 'data:image/png;base64,' + base64.b64encode(open(f'figures/assets/median-cell/{src}-{c}.png', 'rb').read()).decode()
    W, Hh = 1168, 410
    S = min((1168 - 44) / (W + 12), (FIG_H - 31) / (Hh + 8))      # px per unit: the card's content box over the viewBox
    px = lambda p: round(p / S, 1)      # 26 Oct (Kat: "font types are too varied in size, font, format. especially the AMG slide")
    cx0, P = 132, 93
    cs = 74      # 26 Oct (Kat: "text a little cramped"): smaller crops, wider gaps
    X = lambda k: cx0 + k * P
    bar20 = 20 / e18['window_um'] * cs
    # 5 Nov (Kat: "design of this slide is a bit cluttered"): each fact once. The headline carries the range, so the card title, the
    # dashed mean, the "1x = DMSO" label, the colour key and the bars' sampling note leave the stage for the reader's line; the drug and
    # its dose label their own row; the bars rise on the cells' columns against two quiet gridlines, 1x and 2x.
    y1 = 40; y2 = y1 + cs + 6
    g = [text(cx0 - 14, y1 + cs / 2 + 8, 'DMSO', px(T_TEXT), INK2, 'end'),
         text(cx0 - 14, y2 + cs / 2 - 4, 'AMG900', px(T_TEXT), INK2, 'end') + text(cx0 - 14, y2 + cs / 2 + 22, f'{e18["dose_um"]} &#181;M', px(T_TEXT), INK2, 'end')]
    for k, src in enumerate(labs):
        g.append(text(X(k) + cs / 2, y1 - 12, str(lab_number(src)), px(T_TEXT), PINK if src == 'source_2' else INK2, 'middle', 700 if src == 'source_2' else 400))      # every lab named (Kat, 26 Oct: "only lab 2 labelled?")
        # 9 Nov (Kat: the unit sits above the bar): twelve crops at one scale share one labelled bar, on the last AMG900 crop
        sb = lambda y: ((f'<path d="M {X(k) + cs - 6 - bar20:.1f} {y + cs - 7} h {bar20:.1f}" stroke="#f6f7f7" stroke-width="2" stroke-linecap="round"/>'
                         + text(X(k) + cs - 6, y + cs - 12, '20 &#181;m', px(13), '#f6f7f7', 'end', extra='style="font-family:\'IBM Plex Mono\', Menlo, monospace;"'))
                        if (k == len(labs) - 1 and y == y2) else '')
        g.append(f'<g class="f" style="animation-delay:{0.3 + 0.05 * k:.2f}s"><image href="{uri(src, "dmso")}" x="{X(k)}" y="{y1}" width="{cs}" height="{cs}"/>{sb(y1)}</g>'
                 f'<g class="pop" style="animation-delay:{1.0 + 0.06 * k:.2f}s"><image href="{uri(src, "amg900")}" x="{X(k)}" y="{y2}" width="{cs}" height="{cs}"/>{sb(y2)}</g>')
    # the bars: each lab's nuclear area, AMG900 over its own DMSO, on the cells' columns; air above, none inside
    by, bh, top = 402, 118, 2.6
    Y = lambda v: by - v / top * bh
    ratio = {s_: e18['labs'][s_]['ratio'] for s_ in labs}
    mean = e18['summary']['ratio_mean']
    x_end = X(len(labs) - 1) + cs + 8
    g.append(text(cx0 - 8, Y(top) - 12, 'signal: nuclear area, fold change vs own DMSO', px(T_TEXT), INK, weight=700))      # 17 Nov (the primer): the drug's effect is the signal, 04a's spread the noise
    # 17 Nov (Kat: "AMG900: how does this increase nuclei size?"): the mechanism in a gloss where the drug's bars start; the chain
    # and its sources ([38] aborted division, [39] polyploid) are in the notes line
    # 17 Nov (Kat: "link it out in slides"): the gloss is the way in to the explainer that backs it, at
    # explainers/amg900/, which carries the same mechanism in four figures and sixteen sources
    # pink on this slide already means lab 2, so the link keeps the gloss's own ink and is marked the way every
    # other link in this deck is marked: the out-arrow glyph after the words, no underline
    _ax, _ay = x_end - 17, Y(top) - 29
    g.append(f'<a href="explainers/amg900/" target="_blank" rel="noopener">'
             + text(x_end - 24, Y(top) - 12, 'AMG900 blocks cell division: DNA doubles', px(T_TEXT), INK2, 'end')
             + f'<g transform="translate({_ax:.1f},{_ay:.1f}) scale(0.78)" fill="none" stroke="{INK2}" '
               f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               f'<path d="M7 17 17 7M9 7h8v8"/></g>'
             + '</a>')
    for v in (1, 2):
        g.append(f'<path d="M {cx0 - 8} {Y(v):.1f} H {x_end}" stroke="{GRID}" stroke-width="1.5"/>' + text(cx0 - 14, Y(v) + 8, f'{v}&#215;', px(T_TEXT), INK2, 'end'))
    g.append(f'<path d="M {cx0 - 8} {by} H {x_end}" stroke="{MUTE}" stroke-width="2"/>')
    for k, src in enumerate(labs):
        g.append(f'<rect class="bar" style="animation-delay:{1.8 + 0.05 * k:.2f}s; transform-origin:50% {by}px" x="{X(k) + cs / 2 - 20:.1f}" y="{Y(ratio[src]):.1f}" width="40" '
                 f'height="{by - Y(ratio[src]):.1f}" rx="6" fill="{PINK if src == "source_2" else "#6cc3a3"}"/>')
    # 26 Oct (pitch-deck-story: the title states the finding with its number): the range is in 05a's title, the mean on its line      # 26 Oct (review): the key number big, top right of its chart
    aria = (f'AMG900 in {len(labs)} labs, with a link to an explainer of how it enlarges nuclei: untreated and treated '
            f'median cells, nuclei pink and cell bodies green; nuclear area grows '
            f'{e18["summary"]["ratio_range"][0]:.1f} to {e18["summary"]["ratio_range"][1]:.1f} times against each lab&#8217;s own untreated cells, {mean:.1f} times on average.')
    return (f'<div class="r fig" style="animation-delay:0.1s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} padding:14px 22px; display:flex; align-items:center;">'
            f'<svg viewBox="-6 -4 {W + 12} {Hh + 8}" width="100%" height="100%" role="img" aria-label="{aria}" style="display:block;">{"".join(g)}</svg></div>')


def repository(n_labs):
    """05b until 17 Nov 2026, when workflow() took its place; kept so the view can return in one line. (26 Oct, Kat: "data repo: clarify combine existing public image data, private data. protect privacy of private data";
    "cybersecurity and insurance angle: companies can back up free hard copies of raw data like amazon glacier ... this is how to
    hook biotech"): what goes in, the public images and a company's own raw images, backed up free as the hook; what is shared,
    control wells on one map; what stays private, the rest; who pays, the members. All proposed except the public map."""
    box = lambda colour, ic, title, lines, delay: (
        f'<div class="r" style="animation-delay:{delay:.2f}s; box-sizing:border-box; padding:14px 18px; border-radius:12px; border:2px solid {colour}; '
        f'background:#ffffff; display:flex; gap:12px; align-items:flex-start;">{icon(ic, colour, 28)}<div style="display:flex; flex-direction:column; gap:2px; min-width:0;">'
        f'<span style="{SANS} font-size:{T_TEXT}px; font-weight:700; line-height:1.25; color:{PINK if colour == PINK else INK};">{title}</span>'
        + ''.join(f'<span style="{SANS} font-size:{T_TEXT}px; line-height:1.25; color:{INK2};">{line}</span>' for line in lines) + '</div></div>')
    row = lambda colour, ic, title, line: (f'<div style="display:flex; gap:12px; align-items:flex-start;">{icon(ic, colour, 28)}<div style="display:flex; flex-direction:column; gap:2px;">'
                                           f'<span style="{SANS} font-size:{T_TEXT}px; font-weight:700; line-height:1.25; color:{INK};">{title}</span>'
                                           f'<span style="{SANS} font-size:{T_TEXT}px; line-height:1.25; color:{INK2};">{line}</span></div></div>')
    label = lambda t: f'<span style="{MONO} font-size:{T_TEXT}px; letter-spacing:0.08em; text-transform:uppercase; color:{INK2};">{t}</span>'
    go = lambda delay: f'<span class="r" aria-hidden="true" style="animation-delay:{delay:.2f}s; align-self:center; {SANS} font-size:30px; color:{MUTE};">{arrow("e")}</span>'
    inputs = (f'<div style="width:330px; flex-shrink:0; display:flex; flex-direction:column; gap:14px;">{label("sources")}'
              + box(GREEN, 'cells', 'public images', ['JUMP Cell Painting' + pdf(f', {n_labs} labs, open')], 0.3)      # 17 Nov: the consortium in plain words, as on 03
              + box(PINK, 'lock', 'your raw images', ['backed up free' + pdf(', off-site'), 'the copy insurers ask for'], 0.6) + '</div>')
    vault = (f'<div class="r" style="animation-delay:1.0s; width:384px; flex-shrink:0; box-sizing:border-box; padding:18px 20px; border-radius:16px; '
             f'border:2.5px solid {INK}; background:#ffffff; display:flex; flex-direction:column; gap:18px;">'
             f'<span style="{SANS} font-size:{T_TEXT}px; font-weight:700; color:{INK};">one repository</span>'
             + row(GREEN, 'map', 'shared', 'control wells' + pdf(', on one map'))
             + row(PINK, 'lock', 'private', 'everything else' + pdf(', yours alone')) + '</div>')
    members = (f'<div class="r" style="animation-delay:1.5s; width:290px; flex-shrink:0; display:flex; flex-direction:column; gap:18px;">{label("members")}'
               + row(INK2, 'plate', 'screening teams', 'a check on every batch')
               + row(INK2, 'ai-reads', 'AI teams', 'aligned images, by API') + '</div>')
    return (f'<div class="r fig" style="animation-delay:0.1s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:26px 34px; display:flex; align-items:center; justify-content:space-between;" role="img" aria-label="Public images and a company&#8217;s own raw '
            f'images, backed up free, go into one repository; control wells are shared on one map, everything else stays private; screening teams and AI teams pay '
            f'as members.">{inputs}{go(0.8)}{vault}{go(1.3)}{members}</div>')


def workflow(B, now, known, n_labs):
    """05b since 17 Nov 2026 (Kat, "Send all five", fix 1: the view was boxes; "show the workflow: a lab uploads its control wells
    and gets a verdict, using lab 2's real case"). Three stations, drawn, left to right: a real plate of the batch, its control
    wells the only ones sent (metadata/well.csv.gz, as A18); the map, the public field in green and the batch in pink, tied to its
    own normal and to the next lab's; the check, the same two distances as ruler bars, then the verdict (results/e9, e11: the
    archive's 04b, replayed on public data). Carried over from the repository view (26 Oct): public images plus yours, only control
    wells shared, the rest private and backed up free, who pays. The insurer line left the stage: [37] is one insurer's guidance;
    it stays in the notes. Drawn 1:1, so a unit is a pixel and every label is the stage's 22 px."""
    import csv, gzip
    from appendix import plate_map
    assert now['verdict'] == 'in distribution' and known == 'came out' and now['cell_count_vs_own_history'] == 'inside'
    G_TEXT = '#0a7457'      # the green as text (AA on the card)
    W, H = 1124, 336
    nest = lambda name, x, y, c, size: (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" color="{c}" stroke-width="1.7" '
                                        f'stroke-linecap="round" stroke-linejoin="round">{ICONS.get(name) or PATH_ICONS[name]}</svg>')
    go = lambda x, y, delay: (f'<path class="f" style="animation-delay:{delay:.1f}s" d="M {x} {y} h 30 m -10 -9 l 10 9 l -10 9" fill="none" stroke="{MUTE}" '
                              f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    TOP, BOT = 42, 246      # the three drawings share one top and one bottom
    y1, y2 = 290, 320       # and the two lines under each

    # 1. the plate: one compound plate of the batch; its DMSO wells and JUMP's eight known drugs are the controls
    jcp = {'JCP2022_037716', 'JCP2022_025848', 'JCP2022_046054', 'JCP2022_035095',      # the positive controls (analysis/e8_pull_wells.py)
           'JCP2022_064022', 'JCP2022_050797', 'JCP2022_012818', 'JCP2022_085227'}
    by_plate = {}
    for w in csv.DictReader(gzip.open('metadata/well.csv.gz', 'rt')):
        if w['Metadata_Plate'] in now['plates']:
            by_plate.setdefault(w['Metadata_Plate'], []).append(w)
    is_control = lambda w: w['Metadata_JCP2022'] == 'JCP2022_033924' or w['Metadata_JCP2022'] in jcp
    plate = next(p for p in now['plates'] if 0 < sum(is_control(w) for w in by_plate.get(p, [])) < len(by_plate[p]))      # not the all-DMSO plate
    controls = {w['Metadata_Well'] for w in by_plate[plate] if is_control(w)}
    n_wells = len(by_plate[plate]); assert n_wells == 384 and len(controls) == 64, (plate, n_wells, len(controls))
    P = 12
    g = [f'<g class="f" style="animation-delay:0.2s">' + text(0, 24, f'{lab_name(LAB)}&#8217;s plate', T_TEXT, PINK, weight=700)
         + ''.join(plate_map(8, TOP - 2, '', '', set(), set(), P=P, ground='#ffffff', empty='#c3c9cb')) + '</g>']
    g.append(f'<g class="pop" style="animation-delay:0.6s">' + ''.join(
        f'<circle cx="{8 + (int(w[1:]) - 0.5) * P}" cy="{TOP + 2 + ("ABCDEFGHIJKLMNOP".index(w[0]) + 0.5) * P}" r="4.8" fill="{PINK}"/>' for w in sorted(controls)) + '</g>')
    g.append(f'<g class="f" style="animation-delay:0.8s"><circle cx="13" cy="{y1 - 8}" r="6.5" fill="{PINK}"/>' + text(34, y1, f'{len(controls)} control wells sent', T_TEXT, INK, weight=700)
             + nest('lock', 0, y2 - 21, INK2, 26) + text(34, y2, f'{n_wells - len(controls)} private, backed up free', T_TEXT, INK2) + '</g>')

    # 2. the map: every lab's public wells in green, this lab's first batches in pale pink, the batch as the pink dot
    MX, MW = 372, 400
    rows = embedding()
    pca = results('e2-plate-position-1053600681.json')['pca']
    ax, cloud = map_axes(rows, MX, TOP, MW, BOT - TOP, pad=0.06)
    others = sorted({r['lab'] for r in rows if r['lab'] != LAB}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    mine = [r for r in rows if r['lab'] == LAB]
    first = set(B[0]['plates']) | set(B[1]['plates'])
    june = [r for r in mine if r['plate'] in first and r['target'] != 'True']        # the lab's normal, as slide 04 draws it
    june = (june + random.Random(0).sample([r for r in mine if r['target'] == 'True'], pca['wells_per_plate']))[::3]
    cen = lambda pts: (sum(ax.X(float(r['pc1'])) for r in pts) / len(pts), sum(ax.Y(float(r['pc2'])) for r in pts) / len(pts))
    own, near, here = cen(june), cen([r for r in rows if r['lab'] == now['nearest_other']]), cen([r for r in mine if r['plate'] in now['plates']])
    R = 17
    g.append(go(326, (TOP + BOT) // 2, 1.0))
    g.append(f'<g class="f" style="animation-delay:1.1s">' + text(MX, 24, f'{n_labs} labs&#8217; public images<tspan fill="{PINK}">, plus yours</tspan>', T_TEXT, G_TEXT, weight=700)
             + f'<rect x="{MX}" y="{TOP}" width="{MW}" height="{BOT - TOP}" rx="12" fill="#ffffff"/>'
             + ''.join(cloud([r for r in rows if r['lab'] == l][::5], colour[l], 2.2) for l in others) + cloud(june, PALE_PINK, 2.4) + '</g>')
    # the two normals are numbered rings, as on slide 04; at this size they and the batch sit on one another, so the rings step
    # apart along the lines between the three (the batch stays where it landed), each with a short lead back to its true centre
    at = {'own': list(own), 'near': list(near)}
    for _ in range(200):
        for a, b, gap in (('own', 'near', 2 * R + 10), ('own', None, R + 22), ('near', None, R + 22)):
            q = at[b] if b else here
            dx, dy = at[a][0] - q[0], at[a][1] - q[1]; d = max((dx * dx + dy * dy) ** 0.5, 0.1)
            if d < gap:
                push = (gap - d) / (2 if b else 1)
                at[a][0] += dx / d * push; at[a][1] += dy / d * push
                if b:
                    at[b][0] -= dx / d * push; at[b][1] -= dy / d * push
    for v in at.values():
        assert MX + R + 4 <= v[0] <= MX + MW - R - 4 and TOP + R + 4 <= v[1] <= BOT - R - 4, 'a ring left the map'
    def tie(to, c, dash):
        dx, dy = to[0] - here[0], to[1] - here[1]; d = max((dx * dx + dy * dy) ** 0.5, 1)
        return f'<path d="M {here[0]:.1f} {here[1]:.1f} L {to[0] - dx / d * (R + 3):.1f} {to[1] - dy / d * (R + 3):.1f}" stroke="{c}" stroke-width="3"{dash}/>'
    def ring(true, to, c, ink, lab):
        lead = (f'<path d="M {true[0]:.1f} {true[1]:.1f} L {to[0]:.1f} {to[1]:.1f}" stroke="{INK2}" stroke-width="1.5"/>'
                f'<circle cx="{true[0]:.1f}" cy="{true[1]:.1f}" r="3.5" fill="{c}" stroke="#ffffff" stroke-width="1.2"/>')
        return (lead + f'<circle cx="{to[0]:.1f}" cy="{to[1]:.1f}" r="{R}" fill="#ffffff" stroke="{c}" stroke-width="4"/>'
                + text(to[0], to[1] + T_TEXT * 0.35, str(lab_number(lab)), T_TEXT, ink, 'middle', 700))
    g.append(f'<g class="pop" style="animation-delay:1.4s">' + ring(own, at['own'], PINK, PINK, LAB)
             + ring(near, at['near'], colour[now['nearest_other']], INK, now['nearest_other']) + '</g>')
    g.append(f'<g class="f" style="animation-delay:2.0s">' + tie(at['own'], PINK, '') + tie(at['near'], INK2, ' stroke-dasharray="7 6"') + '</g>')
    lx = max(here[0], MX + 62)      # the label above the dot, inside the map
    g.append(f'<g class="drop" style="animation-delay:1.7s"><circle cx="{here[0]:.1f}" cy="{here[1]:.1f}" r="10" fill="{PINK}" stroke="#ffffff" stroke-width="3"/>'
             + text(lx, here[1] - 20, 'new batch', T_TEXT, PINK, 'middle') + '</g>')
    g.append(f'<g class="f" style="animation-delay:3.6s">' + nest('ai-reads', MX, y1 - 21, INK2, 26) + text(MX + 34, y1, 'AI teams', T_TEXT, INK, weight=700)
             + text(MX + 34, y2, 'aligned images, by API', T_TEXT, INK2) + '</g>')

    # 3. the check: the two distances as rulers, one tick a plate spread, then the verdict
    CX = 836; bx = CX + 96
    g.append(go(790, (TOP + BOT) // 2, 2.2))
    g.append(f'<g class="f" style="animation-delay:2.3s">' + text(CX, 24, 'the check', T_TEXT, INK, weight=700) + '</g>')
    sc = 128 / max(now['from_baseline'], now['to_nearest_other'])
    for k, (v, words, c) in enumerate(((now['from_baseline'], 'own lab', PINK), (now['to_nearest_other'], 'next lab', INK2))):
        y = TOP + 22 + 40 * k
        fade = '' if k == 0 else ' opacity=".55"'
        g.append(f'<g class="f" style="animation-delay:{2.4 + 0.2 * k:.1f}s">' + text(CX, y + 8, words, T_TEXT, c, weight=700 if k == 0 else 400)
                 + f'<rect x="{bx}" y="{y - 12}" width="{v * sc:.1f}" height="24" rx="5" fill="{c}"{fade}/>'
                 + ''.join(f'<path d="M {bx + t * sc:.1f} {y - 12} v 24" stroke="#ffffff" stroke-width="2.5"/>' for t in range(1, int(v) + 1))
                 + text(bx + v * sc + 8, y + 8, f'{v:.1f}&#215;', T_TEXT, c, weight=700) + '</g>')
    vy = TOP + 138
    g.append(f'<g class="pop" style="animation-delay:3.0s">' + nest('check', CX - 2, vy - 38, GREEN, 46)
             + text(CX + 54, vy, '&#8220;normal&#8221;', T_BIG, G_TEXT, weight=700, extra='letter-spacing="-1"') + '</g>')
    g.append(f'<g class="f" style="animation-delay:3.3s">' + text(CX, BOT - 26, 'drugs match', T_TEXT, INK2) + text(CX, BOT, 'cells grew as usual', T_TEXT, INK2) + '</g>')
    g.append(f'<g class="f" style="animation-delay:3.6s">' + nest('plate', CX, y1 - 21, INK2, 26) + text(CX + 34, y1, 'screening teams', T_TEXT, INK, weight=700)
             + text(CX + 34, y2, 'a check on every batch', T_TEXT, INK2) + '</g>')
    aria = (f'The workflow, on {lab_name(LAB)}&#8217;s public data. One 384-well plate: its {len(controls)} control wells are sent, the other {n_wells - len(controls)} stay private '
            f'and are backed up free. On the map of {n_labs} labs&#8217; public images the new batch lands {now["from_baseline"]:.1f} plate spreads from its own lab&#8217;s normal and '
            f'{now["to_nearest_other"]:.1f} from the next lab&#8217;s. The check answers normal: its known drugs match and its cells grew as usual. '
            f'AI teams pay for aligned images by API, screening teams for a check on every batch.')
    return (f'<div class="r fig" style="animation-delay:0.1s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:16px 22px; display:flex; align-items:center;">{svg(W, H, g, aria=aria)}</div>'), plate, len(controls)


def hub_side(n_wells, n_labs, n_map):
    """07a, right: how big the repository is today (wells and labs, an icon each), and what one subscription buys."""
    say = lambda v, c=D_TEXT, size=20: f'<span style="{SANS} font-size:{size}px; line-height:1.35; color:{c};">{v}</span>'
    noun = lambda ico, words: f'<span style="display:flex; align-items:center; gap:8px;">{icon(ico, D_SOFT, 26)}{words}</span>'
    row = lambda ico, big, what, src: (f'<div style="display:grid; grid-template-columns:28px auto 1fr; align-items:center; gap:12px;">{icon(ico, D_GREEN, 26)}'
                                       f'<span style="{SANS} font-size:34px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{D_GREEN};">{big}</span>'
                                       f'<span style="{SANS} font-size:18px; line-height:1.25; color:{D_TEXT};">{what}{pdf(f"<span style={chr(34)}{MONO} font-size:12px; color:{D_DIM};{chr(34)}> {src}</span>")}</span></div>')
    save = (f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:14px;">'      # what a subscription saves: the author's estimates (README [28])
            f'<span style="{MONO} font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:{D_SOFT};">subscribers save</span>'
            + row('run', '$100,000s', 'a failed screen, caught early', '[28]')
            + row('clock', 'months', 'of asking around, saved', '[28]') + '</div>')
    return (f'<div class="r" style="animation-delay:0.6s; position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:14px;">'
            f'<div style="display:flex; flex-direction:column; gap:12px; padding:16px 18px 14px; border-radius:12px; background:rgba(246,247,247,.06);">'
            f'<span style="{SANS} font-size:88px; font-weight:700; letter-spacing:-0.045em; line-height:0.95; color:{D_TEXT};">{n_wells:,}</span>'
            f'<div style="display:flex; gap:24px; {SANS} font-size:20px; color:{D_TEXT};">{noun("well", "control wells, every lab")}</div>'
            + pdf(f'<span style="{MONO} font-size:12px; line-height:1.45; color:{D_DIM};">{n_map:,} of them on the map; one plate has no batch (results/e1, e13)</span>') + '</div>'
            + pdf(say('One subscription: the repository, the map, the benchmark.', D_SOFT, 18))
            + pdf(say('Public archives keep finished datasets (656 TB, free [17]). This keeps every lab&#8217;s live controls, aligned and checked.', D_SOFT, 18))
            + pdf(say('Every cell result becomes checkable against the field.', D_SOFT, 18)) + '</div>')


NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']


def app(R, B, now):
    d = date.fromisoformat(now['date'])
    you = well_image(LAB, now['plates'][0], 'box-you'); near = well_image(now['nearest_other'], None, 'box-near')
    thumb = lambda uri, alt, ring='': f'<img src="{uri}" alt="{alt}" style="width:56px; height:56px; border-radius:9px; object-fit:cover; background:#000; flex-shrink:0;{ring}">'
    stack = (f'<div class="drop" style="animation-delay:0.4s; position:relative; width:76px; height:56px; flex-shrink:0;">'      # a pool of wells, not one image
             + ''.join(f'<img src="{you}" alt="" style="position:absolute; left:{10 * k}px; top:0; width:56px; height:56px; border-radius:9px; object-fit:cover; '
                       f'background:#000; box-shadow:0 0 0 2px #ffffff; opacity:{0.45 + 0.275 * k};">' for k in range(3)) + '</div>')
    step = lambda ic, w: f'<span style="display:flex; align-items:center; gap:7px; {SANS} font-size:18px; color:{INK2};">{icon(ic, INK2, 24)}{w}</span>'
    arrow = f'<span aria-hidden="true" style="{SANS} font-size:20px; color:{MUTE};">&#8594;</span>'      # AA (FAINT was 2.8:1)
    drop = (f'<div style="display:flex; align-items:center; gap:14px; padding:8px 12px; border-radius:12px; border:2px dashed #aeb5b8; background:#ffffff;">'
            f'{stack}'
            f'<div style="display:flex; flex-direction:column; gap:2px; flex-grow:1; min-width:0;">'
            f'<span style="display:flex; align-items:center; gap:8px; {SANS} font-size:18px; color:{INK};">{icon("batch", INK2, 22)}{now["n_plates"]} plates</span>'
            f'<span style="display:flex; align-items:center; gap:8px; {SANS} font-size:18px; color:{PINK};">{icon("lab", PINK, 22)}'
            f'<span>{lab_name(R["lab"])}{pdf(f", {short_date(now[chr(100) + chr(97) + chr(116) + chr(101)])} {d.year}")}</span></span></div>'
            + '</div>')      # 26 Oct, second declutter: the image > controls > answer strip left; the headline says it
    foot = (f'<div style="display:flex; align-items:center; gap:12px; padding:0 4px;">'
            f'{thumb(you, "Lab 2 cells.", f" outline:3px solid {PINK};")}<span style="{SANS} font-size:18px; color:{PINK};">{lab_name(LAB)}</span>'
            f'<span style="flex:1 1 0; height:2px; margin:0 16px; background:repeating-linear-gradient(90deg, {INK2} 0 4px, transparent 4px 8px);"></span>'
            + '<span style="display:flex; align-items:center;">' + stain_chip('DNA', size=18, inline=True, dark=False) + '</span>'
            + f'<span style="flex:1 1 0; height:2px; margin:0 16px; background:repeating-linear-gradient(90deg, {INK2} 0 4px, transparent 4px 8px);"></span>'
            + f'<span style="{SANS} font-size:18px; color:{GREEN};">closest: {lab_name(now["nearest_other"])}</span>'
            + f'{thumb(near, "The nearest lab&#8217;s cells.", f" outline:3px solid {GREEN};")}</div>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:12px 16px 12px; display:flex; flex-direction:column; gap:10px;">{drop}'
            f'<div style="flex:1 1 0; min-height:0; display:flex;">{your_map(B, now)}</div>{foot}</div>')


def leaderboard(lb, now):
    """The field's top batches and this lab's, ranked on untreated wells alone."""
    mine = {r['batch']: r for r in lb['lab_2']}
    this = mine[now['batch']]; best = min(mine.values(), key=lambda r: r['rank'])
    cols = 'grid-template-columns:56px 84px 84px 1fr 56px;'
    line = lambda r, own, tag='': (
        f'<div style="display:grid; {cols} align-items:center; gap:12px; padding:16px 8px; border-radius:8px; '
        f'background:{"rgba(190,30,116,0.08)" if own else "transparent"}; border-top:1px solid #e4e8e9;">'
        f'<span style="{MONO} font-size:18px; color:{PINK if own else MUTE};">#{r["rank"]}</span>'
        f'<span style="{SANS} font-size:19px; font-weight:{700 if own else 500}; color:{PINK if own else INK};">{lab_name(r["lab"])}</span>'
        f'<span style="{MONO} font-size:18px; color:{MUTE};">{short_date(r["date"]) if r["date"] else r["batch"][:8]}</span>'
        f'<span style="display:flex; align-items:center; gap:10px;"><span class="bar" style="animation-delay:{0.3 + 0.07 * r["rank"] % 1:.2f}s; display:block; height:10px; border-radius:5px; '
        f'width:{r["score"]:.0f}%; background:{PINK if own else GREEN}; opacity:{1 if own else .8};"></span>'
        f'<span style="display:flex; align-items:center; gap:6px; {SANS} font-size:18px; color:{PINK if own else MUTE};">{tag}</span></span>'
        f'<span style="{SANS} font-size:19px; font-weight:700; color:{PINK if own else INK}; text-align:right;">{r["score"]:.0f}</span></div>')
    head = (f'<div style="display:grid; {cols} align-items:center; gap:12px; padding:0 8px 6px;">'
            f'<span style="{SANS} font-size:16px; color:{MUTE};">{pdf("rank")}</span>{icon("lab", MUTE, 22)}{icon("batch", MUTE, 22)}'
            f'<span style="{SANS} font-size:18px; color:{MUTE};">score, higher is better</span><span></span></div>')
    gap = f'<div aria-hidden="true" style="{MONO} font-size:18px; line-height:1; color:{MUTE}; padding:4px 8px;">&#8230;</div>'
    body = ''.join(line(r, r['lab'] == LAB) for r in lb['top'][:1])
    body += (gap if best['rank'] > 6 else '') + line(best, True, 'best')
    if this['rank'] != best['rank']:
        body += (gap if this['rank'] > best['rank'] + 1 else '') + line(this, True, icon('sent', PINK, 22) + 'this batch')
    return f'<div style="display:flex; flex-direction:column;">{head}{body}</div>'


def board(lb, now, B):      # 05c until 26 Oct; out of the talk since, kept so the view can return in one line
    rec = max(lb['by_lab'], key=lambda b: b['streak']['longest'])
    bar = pdf(f'<div style="display:flex; justify-content:space-between; align-items:baseline; padding:0 4px;">'
              f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">Ranked on controls alone</span>'
              f'<span style="{SANS} font-size:16px; color:{MUTE};">off centre, spread, drift from last batch, cell count; U2OS, A17</span></div>')
    run = (f'<div style="margin-top:auto; display:flex; align-items:center; gap:12px; padding:14px 8px 4px; border-top:1px solid #e4e8e9; {SANS} font-size:19px; color:{INK};">'
           f'{icon("lab", PINK, 24)}<span>checked in a row</span>{streak(B, now, "margin:0;")}'
           + pdf(f'<span style="{SANS} font-size:16px; color:{MUTE};">lab 2&#8217;s streak; longest in the field: {rec["streak"]["longest"]}</span>')
           + f'<span style="margin-left:auto; display:flex; align-items:center; gap:8px; color:{INK2};">{icon("lock", INK2, 22)}<span>each lab sees only its own rows</span></span></div>')
    return (f'<div class="r fig" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:16px 18px 14px; display:flex; flex-direction:column; gap:8px;">{bar}{leaderboard(lb, now)}{run}</div>')


def datasets(replay, frame, failed=()):
    """Every lab's untreated wells as one dataset, each batch checked: batches on the map, provenance, how far it converts.
    A batch whose known drugs failed (results/e11) does not pass the check, wherever its untreated wells sit."""
    failed = {(f['lab'], f['batch']) for f in failed}
    rows = []
    for lab, v in replay.items():
        B = [dict(b, verdict='failed') if (lab, b['batch']) in failed else b for b in v['batches']]
        af = frame.get(lab, {}).get('agree_field', {})
        rows.append({'lab': lab, 'batches': v['n_batches'], 'plates': v['n_plates'],
                     'on_map': sum(b['verdict'] not in ('outside', 'failed') for b in B),
                     'named': min(b.get('wells_named_own_lab', 1.0) for b in B),
                     'raw': af.get('raw'), 'field': af.get('field'),
                     'flagged': [b for b in B if b['verdict'] in ('outside', 'failed')],
                     'verdicts': [b['verdict'] for b in B]})
    return sorted(rows, key=lambda r: -r['plates'])


def exchange(rows):
    CELL, GAP = 10, 3

    def strip(r):
        fill = PINK if r['lab'] == LAB else GREEN
        g = ''.join(f'<rect x="{k*(CELL+GAP)}" y="0" width="{CELL}" height="{CELL}" rx="2.5" fill="{fill}"/>' if v not in ('outside', 'failed') else
                    f'<rect x="{k*(CELL+GAP)+0.75}" y="0.75" width="{CELL-1.5}" height="{CELL-1.5}" rx="2" fill="none" stroke="{MUTE}" stroke-width="1.5"/>' for k, v in enumerate(r['verdicts']))
        W = len(r['verdicts'])*(CELL+GAP) - GAP
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {CELL}" width="{W}" height="{CELL}" role="img" aria-label="{r["on_map"]} of {r["batches"]} batches checked" style="display:block;">{g}</svg>'
    shown = rows[:7]
    cols = 'grid-template-columns:86px 70px 1fr;'
    head = (f'<div style="display:grid; {cols} gap:10px; padding:0 6px 4px;">'
            + ''.join(f'<span style="{SANS} font-size:16px; color:{MUTE};">{s}</span>' for s in ('lab', 'plates', 'batches checked')) + '</div>')
    line = lambda r: (
        f'<div style="display:grid; {cols} align-items:center; gap:10px; padding:8px 6px; border-radius:8px; border-top:1px solid #e4e8e9; '
        f'background:{"rgba(190,30,116,0.08)" if r["lab"] == LAB else "transparent"};">'
        f'<span style="{SANS} font-size:17px; font-weight:{700 if r["lab"] == LAB else 500}; color:{PINK if r["lab"] == LAB else INK};">{lab_name(r["lab"])}{" &#183; you" if r["lab"] == LAB else ""}</span>'
        f'<span style="{SANS} font-size:17px; color:{MUTE};">{r["plates"]}</span>'
        f'{strip(r)}</div>')
    more = f'<div style="{SANS} font-size:17px; color:{MUTE}; padding:4px 6px 0;">and {len(rows) - len(shown)} more labs</div>'
    bar = (f'<div style="display:flex; justify-content:space-between; align-items:center; padding:0 4px;">'
           f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">U2OS controls, shared by {len(rows)} labs</span></div>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:800px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:14px 16px 12px; display:flex; flex-direction:column; gap:8px;">{bar}{head}{"".join(line(r) for r in shown)}{more}</div>')


def your_listing(rows):
    r = next(x for x in rows if x['lab'] == LAB)
    row = lambda name, value: (f'<div style="display:flex; flex-direction:column; gap:4px; padding:10px 0; border-top:1px solid #d3d8da;">'
                               f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">{name}</span>'
                               f'<span style="{SANS} font-size:18px; line-height:1.3; color:{INK2};">{value}</span></div>')
    head = (f'<div style="display:flex; flex-direction:column; gap:3px; padding-bottom:6px;">'
            f'<span style="{SANS} font-size:21px; font-weight:700; letter-spacing:-0.02em; color:{INK};">Your shared data</span></div>')
    big = (f'<div style="display:flex; flex-direction:column; gap:4px; padding:4px 0 8px;">'
           f'<span style="{SANS} font-size:48px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{PINK}; white-space:nowrap;">{r["on_map"]} of {r["batches"]}</span>'
           f'<span style="{SANS} font-size:18px; color:{MUTE};">batches checked</span></div>')
    return (f'<div class="r" style="animation-delay:0.8s; position:absolute; right:56px; top:{FIG_TOP}px; width:344px; height:{FIG_H}px; box-sizing:border-box; padding:16px 22px 14px; '
            f'background:linear-gradient(180deg,#ffffff,#f1f3f3); border-radius:16px; display:flex; flex-direction:column; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 28px 70px rgba(0,0,0,0.50);">' + head + big
            + row('Where it came from', f'every well traced to {lab_name(LAB)} by its images' if r['named'] >= 0.995 else f'{100 * r["named"]:.0f}% of wells traced to their lab by their images')
            + row('Who can use it', 'Subscribers, for access; you keep a share (proposed).')
            + '</div>')


def build():
    R = results('e9-replay.json')['labs'][LAB]; B = R['batches']
    now = max((b for b in B if b['verdict'] == 'in distribution'), key=lambda b: b['n_plates'])
    frame = next(b for b in results('e12-field-normalization.json')['lab_2'] if b['batch'] == now['batch'])
    e1 = results('e1.json')['all_sources']; n_wells, n_labs = e1['n_wells'], e1['n_labs']
    e18 = results('e18-median-cell.json'); e18s = e18['summary']; lo, hi = e18s['ratio_range']      # 05a's title: AMG900's nuclear growth, every lab inside this range
    n_nuc = [v['n_nuclei']['amg900'] for v in e18['labs'].values()]; assert {len(v['plates']) for v in e18['labs'].values()} == {3}
    css = BASE_CSS + '''
    .ping { transform-box: fill-box; transform-origin: center; animation: ping 2.2s ease-out infinite; }
    @keyframes ping { 0% { transform: scale(1); opacity: .9; } 100% { transform: scale(3.4); opacity: 0; } }
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1, .step-2 .s2 { opacity: 1; pointer-events: auto; }
    ''' + view_motion(2) + '''
    .flow { cursor: pointer; }
'''
    H = f'position:absolute; left:56px; top:86px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.05; color:{D_TEXT};'
    P = f'position:absolute; left:56px; top:146px; width:770px; margin:0; {SANS} font-size:19px; line-height:1.38; color:{D_SOFT};'
    FOOT = f'position:absolute; left:56px; bottom:44px; width:1168px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">The product</span>'
    e19 = results('e19-rank-order.json'); q1 = e19['q1_lab_against_lab']; a19 = e19['amg900']      # every plate, each lab's own released profile
    assert q1['labs_with_AMG900_first'] == n_labs == e19['settings']['n_labs'] and e19['settings']['dose_um'] == e18['dose_um']
    FEET = {'s0': source('', 'AMG900, a pan-Aurora kinase inhibitor [38]: cell division aborts and cells keep their doubled DNA (polyploid) [39], so nuclei grow; '
                         'JUMP&#8217;s strongest positive control, 5 &#181;M; '
                         'per lab, three plates whose known answer came out; each crop the cell of median nuclear area, 90 &#181;m across; DNA pink, AGP green; '
                         f'chart: one bar a lab, the median of {min(n_nuc)} to {max(n_nuc)} nuclei; mean &#215;{e18s["ratio_mean"]:.1f} (results/e18). '
                         f'Over every plate ({e19["settings"]["n_plates"]:,}), from each lab&#8217;s own released profile: &#215;{a19["fold_change_min"]:.1f} to {a19["fold_change_max"]:.1f}, '
                         f'median &#215;{a19["fold_change_median"]:.1f}, first of {len(e19["settings"]["drugs"])} drugs in all {q1["labs_with_AMG900_first"]} labs; the whole order agrees between labs at '
                         f'Spearman {q1["spearman_median"]:.2f} (a lab against itself {e19["ceiling_same_lab_split_half"]["spearman_median_over_labs"]:.2f}, chance {q1["chance_median"]:.2f}) '
                         '(results/e19); A14; JUMP [7]')}
    known = next(b for b in results('e11-known-answer.json')['labs'][LAB]['batches'] if b['batch'] == now['batch'])['verdict']
    flow, plate, n_controls = workflow(B, now, known, n_labs)
    FEET['s1'] = source('', f'The member check, replayed on public data: {lab_name(LAB)}, batch of {short_date(now["date"])}, {now["n_plates"]} plates. '
                       f'Plate {plate}: {n_controls} of 384 wells are controls (DMSO and JUMP&#8217;s eight known drugs), the only wells sent. '
                       f'Map: DMSO wells, one in five drawn, for the eye; rings: {lab_name(LAB)}&#8217;s and {lab_name(now["nearest_other"])}&#8217;s normals; '
                       f'bars: distance in within-plate spreads over all {R["n_features"]:,} numbers; known drugs worked; {now["cells_per_well"]:.0f} cells per well, '
                       'in its usual range (results/e9, e11). Proposed, except the public map (JUMP, CC0 [7]). Raw images backed up free, off-site and '
                       'immutable: cold storage costs about $1 per TB a month [36]; one cyber insurer asks for a weekly offline or immutable backup [37]. '
                       'The rest is encrypted and read by no one else. A11, A18, A24')
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 46px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(5, dark=True)}
  {header('05', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">The product is the data.<br><span style="color:{D_GREEN};">One drug: nuclei &#215;{lo:.1f} to {hi:.1f} in all {n_labs} labs.</span></h2>
  <div class="s s0">{value(n_labs, n_wells)}</div>
  <div class="s s0 cap" style="{FOOT}">{FEET["s0"]}</div>
  <h2 class="s s1" style="{H}">Image as usual. Send only the controls.<br><span style="color:{D_GREEN};">Know it&#8217;s &#8220;normal&#8221; before the screen.</span></h2>
  <div class="s s1">{flow}</div>
  <div class="s s1 cap" style="{FOOT}">{FEET["s1"]}</div>
  {cue(2, dark=True)}

</div>'''
    steps = {'tag': ['The product', 'The workflow']}      # 17 Nov: 05b draws the workflow (fix 1); the repository view is repository(), kept      # 26 Oct: a second view, the repository (Kat: public and private data; free backup the hook); the member check is 04's second view      # 26 Oct (Kat: "cut or merge views"): the leaderboard left the talk; A17 in the archive covers it
    return css, body, steps
