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
    W, Hh = 1168, 430
    S = min((1168 - 44) / (W + 12), (FIG_H - 31) / (Hh + 8))      # px per unit: the card's content box over the viewBox
    px = lambda p: round(p / S, 1)      # 26 Oct (Kat: "font types are too varied in size, font, format. especially the AMG slide")
    cx0, P = 132, 93
    cs = 74      # 26 Oct (Kat: "text a little cramped"): smaller crops, wider gaps
    X = lambda k: cx0 + k * P
    bar20 = 20 / e18['window_um'] * cs
    g = [text(0, 22, f'AMG900, {e18["dose_um"]} &#181;M: cells can&#8217;t divide', px(T_TEXT), INK, weight=700)]
    y1, y2 = 68, 68 + cs + 6                                   # 26 Oct (talk scale): lab 2's 25-unit number clears the title
    g.append(text(cx0 - 14, y1 + cs / 2 + 8, 'DMSO', px(T_TEXT), INK2, 'end') + text(cx0 - 14, y2 + cs / 2 + 8, 'AMG900', px(T_TEXT), INK2, 'end'))
    for k, src in enumerate(labs):
        g.append(text(X(k) + cs / 2, y1 - 10, str(lab_number(src)), px(T_TEXT), PINK if src == 'source_2' else INK2, 'middle', 700 if src == 'source_2' else 400))      # every lab named (Kat, 26 Oct: "only lab 2 labelled?")
        sb = lambda y: f'<path d="M {X(k) + cs - 6 - bar20:.1f} {y + cs - 7} h {bar20:.1f}" stroke="#ffffff" stroke-width="2"/>'
        g.append(f'<g class="f" style="animation-delay:{0.3 + 0.05 * k:.2f}s"><image href="{uri(src, "dmso")}" x="{X(k)}" y="{y1}" width="{cs}" height="{cs}"/>{sb(y1)}</g>'
                 f'<g class="pop" style="animation-delay:{1.0 + 0.06 * k:.2f}s"><image href="{uri(src, "amg900")}" x="{X(k)}" y="{y2}" width="{cs}" height="{cs}"/>{sb(y2)}</g>')
    ly = y2 + cs + 34                                           # the key, bottom left of the cells
    g.append(f'<rect x="{cx0}" y="{ly - 18}" width="20" height="20" rx="4" fill="{PINK}"/>' + text(cx0 + 28, ly, 'nuclei (DNA)', px(T_TEXT), INK2)
             + f'<rect x="{cx0 + 212}" y="{ly - 18}" width="20" height="20" rx="4" fill="{GREEN}"/>' + text(cx0 + 240, ly, 'cell body (actin, membrane)', px(T_TEXT), INK2)
             + f'<path d="M {cx0 + 596} {ly - 8} h {bar20:.1f}" stroke="{INK}" stroke-width="2"/>' + text(cx0 + 596 + bar20 + 8, ly, '20 &#181;m', px(T_TEXT), INK2))
    # the bars: each lab's nuclear area, AMG900 over its own DMSO, on the cells' columns
    by, bh, top = 394, 84, 2.6      # the plot's top clears the cells' key; its own key goes under it
    Y = lambda v: by - v / top * bh
    ratio = {s_: e18['labs'][s_]['ratio'] for s_ in labs}
    mean = e18['summary']['ratio_mean']
    g.append(text(0, by - bh - 16, 'nuclear area, over own DMSO', px(T_TEXT), INK, weight=700))
    nuclei = [e18['labs'][s_]['n_nuclei']['amg900'] for s_ in labs]
    g.append(f'<rect x="{cx0}" y="{by + 14}" width="14" height="20" rx="3" fill="#6cc3a3"/>'      # 26 Oct (Kat: "always have legend, under plot")
             + text(cx0 + 24, by + 32, f'one bar a lab: the median of {min(nuclei)} to {max(nuclei)} nuclei, {e18["labs"][labs[0]]["plates"]} plates', px(T_TEXT), INK2))
    g.append(f'<path d="M {cx0 - 8} {by} H {X(len(labs) - 1) + cs + 8}" stroke="{MUTE}" stroke-width="2"/>')
    g.append(f'<path d="M {cx0 - 8} {Y(1):.1f} H {X(len(labs) - 1) + cs + 8}" stroke="{MUTE}" stroke-width="1.5"/>' + text(cx0 - 14, Y(1) + 9, '1&#215; = DMSO', px(T_TEXT), INK2, 'end'))
    for k, src in enumerate(labs):
        g.append(f'<rect class="bar" style="animation-delay:{1.8 + 0.05 * k:.2f}s; transform-origin:50% {by}px" x="{X(k) + cs / 2 - 20:.1f}" y="{Y(ratio[src]):.1f}" width="40" '
                 f'height="{by - Y(ratio[src]):.1f}" rx="6" fill="{PINK if src == "source_2" else "#6cc3a3"}"/>')
    g.append(f'<g class="f" style="animation-delay:2.6s"><path d="M {cx0 - 8} {Y(mean):.1f} H {X(len(labs) - 1) + cs + 8}" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="8 6"/>'
             + text(cx0 - 14, Y(mean) + 9, f'mean &#215;{mean:.1f}', px(T_TEXT), GREEN, 'end', 700) + '</g>')
    # 26 Oct (pitch-deck-story: the title states the finding with its number): the range is in 05a's title, the mean on its line      # 26 Oct (review): the key number big, top right of its chart
    aria = (f'AMG900 in {len(labs)} labs: untreated and treated median cells, nuclei pink and cell bodies green; nuclear area grows '
            f'{e18["summary"]["ratio_range"][0]:.1f} to {e18["summary"]["ratio_range"][1]:.1f} times against each lab&#8217;s own untreated cells, {mean:.1f} times on average.')
    return (f'<div class="r" style="animation-delay:0.1s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} padding:14px 22px; display:flex; align-items:center;">'
            f'<svg viewBox="-6 -4 {W + 12} {Hh + 8}" width="100%" height="100%" role="img" aria-label="{aria}" style="display:block;">{"".join(g)}</svg></div>')


def repository(n_labs):
    """05b (26 Oct, Kat: "data repo: clarify combine existing public image data, private data. protect privacy of private data";
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
              + box(GREEN, 'cells', 'public images', [f'JUMP, {n_labs} labs, open'], 0.3)
              + box(PINK, 'lock', 'your raw images', ['backed up free, off-site', 'the copy insurers ask for'], 0.6) + '</div>')
    vault = (f'<div class="r" style="animation-delay:1.0s; width:384px; flex-shrink:0; box-sizing:border-box; padding:18px 20px; border-radius:16px; '
             f'border:2.5px solid {INK}; background:#ffffff; display:flex; flex-direction:column; gap:18px;">'
             f'<span style="{SANS} font-size:{T_TEXT}px; font-weight:700; color:{INK};">one repository</span>'
             + row(GREEN, 'map', 'shared', 'control wells, on one map')
             + row(PINK, 'lock', 'private', 'everything else, yours alone') + '</div>')
    members = (f'<div class="r" style="animation-delay:1.5s; width:290px; flex-shrink:0; display:flex; flex-direction:column; gap:18px;">{label("members")}'
               + row(INK2, 'plate', 'screening teams', 'a check on every batch')
               + row(INK2, 'ai-reads', 'AI teams', 'aligned images, by API') + '</div>')
    return (f'<div class="r" style="animation-delay:0.1s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:26px 34px; display:flex; align-items:center; justify-content:space-between;" role="img" aria-label="Public images and a company&#8217;s own raw '
            f'images, backed up free, go into one repository; control wells are shared on one map, everything else stays private; screening teams and AI teams pay '
            f'as members.">{inputs}{go(0.8)}{vault}{go(1.3)}{members}</div>')


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
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:1168px; height:{FIG_H}px; {CARD_ON_DARK} '
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
    lo, hi = results('e18-median-cell.json')['summary']['ratio_range']      # 05a's title: AMG900's nuclear growth, every lab inside this range
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
    FOOT = f'position:absolute; left:56px; bottom:44px; width:1010px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">The product</span>'
    FEET = {'s0': source('', f'{results("e13-baseline-density.json")["n_wells"]:,} of the {n_wells:,} wells on the map (one plate has no batch). Public archives keep finished datasets (656 TB, free [17]); this keeps every lab&#8217;s live controls, aligned and checked. Left: AMG900, JUMP&#8217;s strongest positive control, an Aurora kinase inhibitor; per lab, one plate from each of up to three batches whose known answer came out, site 1; each crop is one whole cell, the one of median nuclear area, 90 &#181;m across, the rest black; one brightness scale per lab from its DMSO cells, for both conditions; DNA (Hoechst) pink, AGP (phalloidin, WGA) green; bars 20 &#181;m; dashed: mean change; 5 &#181;M, JUMP [7] and JUMP-Target&#8217;s recommended dose (results/e18). The seven known drugs&#8217; agreement across labs, alone against aligned: A14 (results/e12). JUMP [7], A15, A18, A24')}
    FEET['s1'] = source('', 'Proposed, except the public map. Public images: JUMP, CC0 [7]. A company&#8217;s raw images are backed up free in cold storage, '
                       'off-site and immutable; cold archive storage costs about $1 per TB a month (AWS S3 Glacier Deep Archive [36]); one cyber insurer asks '
                       'for at least one weekly backup that is offline or immutable, kept two weeks (St&#246;ik [37]). Only control wells are shared, and only '
                       'when the lab chooses; the rest is encrypted and seen by no one else. A15, A18, A24')
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 46px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(5, dark=True)}
  {header('05', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">The product is the data.<br><span style="color:{D_GREEN};">One drug: nuclei &#215;{lo:.1f} to {hi:.1f} in all {n_labs} labs.</span></h2>
  <div class="s s0">{value(n_labs, n_wells)}</div>
  <div class="s s0" style="{FOOT}">{FEET["s0"]}</div>
  <h2 class="s s1" style="{H}">{n_labs} labs&#8217; public images, plus yours.<br><span style="color:{D_GREEN};">Only control wells are shared.</span></h2>
  <div class="s s1">{repository(n_labs)}</div>
  <div class="s s1" style="{FOOT}">{FEET["s1"]}</div>
  {cue(2, dark=True)}

</div>'''
    steps = {'tag': ['The product', 'The repository']}      # 26 Oct: a second view, the repository (Kat: public and private data; free backup the hook); the member check is 04's second view      # 26 Oct (Kat: "cut or merge views"): the leaderboard left the talk; A17 in the archive covers it
    return css, body, steps
