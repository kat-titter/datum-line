"""Slide 07: the product. First what it is, in one picture: a shared repository of raw cell images that labs feed free and
scientists, AI agents and companies subscribe to, with the map, the certificate and the benchmark inside. Then the product
as one lab would have seen it on one day; and the leaderboard. The shared-data table (every lab's controls as a dataset
with its certificate) is board A25. Written whole from results/e1, e9, e12, e2 and e14.

The batch shown is the lab's in-distribution batch with the most plates. Its whole replay is appendix A11; the leaderboard is A17.
"""
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
    ax, cloud = map_axes(rows, 24, 24, W - 48, H - 48, pad=0.06)
    others = sorted({r['lab'] for r in rows if r['lab'] != LAB}, key=lab_number)
    colour = dict(zip(others, greens(len(others))))
    g = [f'<rect width="{W}" height="{H}" rx="18" fill="{PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::3], colour[l], 4.2, 'opacity="0.7"') for l in others]
    mine = [r for r in rows if r['lab'] == LAB]
    sent = B[:B.index(now) + 1]
    g.append(cloud([r for r in mine if any(r['plate'] in b['plates'] for b in sent)], PALE_PINK, 4.2, 'opacity="0.8"'))
    here = centre([r for r in mine if r['plate'] in now['plates']])
    near = centre([r for r in rows if r['lab'] == now['nearest_other']])
    x, y = ax.X(here[0]), ax.Y(here[1]); nx, ny = ax.X(near[0]), ax.Y(near[1])
    g.append(f'<path d="M {x:.1f} {y:.1f} L {nx:.1f} {ny:.1f}" stroke="{INK2}" stroke-width="2.5" stroke-dasharray="7 7"/>')
    g.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="11" fill="{GREEN}" stroke="#ffffff" stroke-width="4"/>')
    g.append(f'<circle class="ping" cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{PINK}" stroke-width="3"/>')
    g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="{PINK}" stroke="#ffffff" stroke-width="4"/>')
    halo = f'paint-order="stroke" stroke="{PANEL}" stroke-width="8" stroke-linejoin="round"'
    g.append(text(nx + 30, ny + 54, f'closest: {lab_name(now["nearest_other"])}', 32, INK2, weight=600, extra=halo))
    g.append(f'<g class="f" style="animation-delay:1.4s"><rect x="18" y="18" width="606" height="58" rx="12" fill="{PANEL}" opacity="0.94"/>'
             f'<circle cx="44" cy="47" r="6" fill="{colour[others[len(others) // 2]]}"/>' + text(60, 57, 'one well', 30, INK2)
             + f'<circle cx="228" cy="47" r="12" fill="{PINK}" stroke="#ffffff" stroke-width="3"/>' + text(250, 57, 'this batch', 30, INK2)
             + f'<circle cx="430" cy="47" r="10" fill="{GREEN}" stroke="#ffffff" stroke-width="3"/>' + text(450, 57, 'lab centre', 30, INK2) + '</g>')
    g.append(text(28, H - 26, 'PC 1 &#8594;', 28, MUTE, extra='class="pdf"'))
    g.append(f'<g class="pdf" transform="translate(36,{H - 66}) rotate(-90)">{text(0, 0, "PC 2 &#8594;", 28, MUTE)}</g>')
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
    the certificate and the benchmark; out, by subscription, to scientists, AI agents and companies."""
    ico = lambda key, colour, size=22: (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{colour}" stroke-width="1.8" '
                                        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink:0;">{key}</svg>')
    tile = lambda lab: (f'<div style="position:relative; width:64px; height:64px;"><img src="{well_image(lab, None, f"hub-{lab}")}" alt="Control well, {lab_name(lab)}, DNA stain." '
                        f'style="width:64px; height:64px; border-radius:9px; object-fit:cover; display:block; background:#000;'
                        f'{" outline:2.5px solid " + PINK + "; outline-offset:-2.5px;" if lab == LAB else ""}">'
                        f'<span style="position:absolute; left:5px; top:5px; padding:1px 6px; border-radius:999px; background:{PINK if lab == LAB else "rgba(20,23,26,.72)"}; '
                        f'{MONO} font-size:11px; color:#ffffff;">{lab_name(lab).replace("lab ", "")}</span></div>')
    col_in = (f'<div style="display:flex; flex-direction:column; gap:10px; width:136px; flex-shrink:0;">{label("in, free", GREEN)}'
              f'<div style="display:grid; grid-template-columns:repeat(2, 64px); gap:8px;">{"".join(tile(l) for l in HUB_LABS)}</div>'
              f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK2};">{NUMBERS[n_labs]} labs{pdf(", control images (A18)")}</span></div>')
    inside = [(PATH_ICONS['map'], 'one map', 'every lab placed on it'),
              (HUB_ICONS['images'], 'raw images', 'kept, with their provenance'),
              (PATH_ICONS['certificate'], 'certificate', 'every batch read against the field'),
              ('<path d="M4 21V4h11l-1 3 1 3H4"/><path d="M4 10h11"/>', 'benchmark', 'every method graded on one test')]
    col_hub = (f'<div style="flex:1 1 0; min-width:0; display:flex; flex-direction:column; gap:9px; padding:14px 16px 12px; border-radius:14px; background:{INK};">'
               f'<span style="{MONO} font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">Datum Line</span>'
               + ''.join(f'<span style="display:flex; align-items:center; gap:10px;">{ico(i, D_GREEN, 20)}<span style="display:flex; flex-direction:column;">'
                         f'<span style="{SANS} font-size:17px; font-weight:600; line-height:1.2; color:#ffffff;">{a}</span>'
                         + pdf(f'<span style="{SANS} font-size:14px; line-height:1.25; color:{D_SOFT};">{b}</span>') + '</span></span>' for i, a, b in inside)
               + '</div>')
    out = [(HUB_ICONS['scientists'], 'scientists', 'onboard assays with confidence' + pdf(': is my batch &#8220;normal&#8221;? whose cells look like mine?')),
           (HUB_ICONS['agents'], 'AI agents', 'query comparable data' + pdf(', traced to its lab, by API')),
           (HUB_ICONS['companies'], 'companies', 'drug discovery, stronger together' + pdf(': a certificate on cell data they buy'))]
    col_out = (f'<div style="display:flex; flex-direction:column; gap:12px; width:214px; flex-shrink:0;">{label("out, by subscription", GREEN)}'
               + ''.join(f'<span style="display:flex; gap:10px; align-items:flex-start;">{ico(i, INK)}<span style="display:flex; flex-direction:column; gap:1px;">'
                         f'<span style="{SANS} font-size:18px; font-weight:600; line-height:1.2; color:{INK};">{a}</span>'
                         + f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK2};">{b}</span></span></span>' for i, a, b in out) + '</div>')
    arrow = f'<span aria-hidden="true" style="align-self:center; {SANS} font-size:28px; color:{GREEN}; padding:0 2px;">&#8594;</span>'
    foot = pdf(f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK2}; padding-top:10px; border-top:1px solid #d3d8da;">'
               f'Proposed terms: labs keep their data and a share of every subscription. A15, A24.</span>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:748px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:16px 18px 14px; display:flex; flex-direction:column; gap:12px;">'
            f'<div style="flex:1 1 0; min-height:0; display:flex; align-items:center; gap:4px;">{col_in}{arrow}{col_hub}{arrow}{col_out}</div>{foot}</div>')


def hub_side(n_wells, n_labs):
    """07a, right: how big the repository is today, and what one subscription buys."""
    say = lambda v, c=D_TEXT, size=20: f'<span style="{SANS} font-size:{size}px; line-height:1.35; color:{c};">{v}</span>'
    return (f'<div class="r" style="animation-delay:0.6s; position:absolute; left:836px; top:{FIG_TOP}px; width:388px; height:{FIG_H}px; display:flex; flex-direction:column; gap:14px;">'
            f'<span style="{SANS} font-size:88px; font-weight:700; letter-spacing:-0.045em; line-height:0.95; color:{D_TEXT};">{n_wells:,}</span>'
            + say('control wells on the map today')
            + pdf('<div style="height:1px; background:rgba(246,247,247,.18);"></div>')
            + pdf(say('One subscription: the repository, the map, the benchmark.', D_SOFT, 18))
            + pdf(say('Public archives keep finished datasets (656 TB, free [17]). This keeps every lab&#8217;s live controls, aligned and checked.', D_SOFT, 18))
            + pdf(say('Every cell result becomes checkable against the field.', D_SOFT, 18)) + '</div>')


NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']


def app(R, B, now):
    d = date.fromisoformat(now['date'])
    you = well_image(LAB, now['plates'][0], 'box-you'); near = well_image(now['nearest_other'], None, 'box-near')
    thumb = lambda uri, alt, ring='': f'<img src="{uri}" alt="{alt}" style="width:56px; height:56px; border-radius:9px; object-fit:cover; background:#000; flex-shrink:0;{ring}">'
    stack = (f'<div style="position:relative; width:76px; height:56px; flex-shrink:0;">'      # a pool of wells, not one image
             + ''.join(f'<img src="{you}" alt="" style="position:absolute; left:{10 * k}px; top:0; width:56px; height:56px; border-radius:9px; object-fit:cover; '
                       f'background:#000; box-shadow:0 0 0 2px #ffffff; opacity:{0.45 + 0.275 * k};">' for k in range(3)) + '</div>')
    drop = (f'<div style="display:flex; align-items:center; gap:14px; padding:8px 12px; border-radius:12px; border:2px dashed #aeb5b8; background:#ffffff;">'
            f'{stack}'
            f'<div style="display:flex; flex-direction:column; gap:2px; flex-grow:1; min-width:0;">'
            f'<span style="{SANS} font-size:18px; color:{INK};">{now["n_plates"]} plates</span>'
            f'<span style="{SANS} font-size:16px; color:{PINK};">{lab_name(R["lab"])}{pdf(f", {short_date(now[chr(100) + chr(97) + chr(116) + chr(101)])} {d.year}")}</span></div></div>')
    foot = (f'<div style="display:flex; align-items:center; gap:12px; padding:0 4px;">'
            f'{thumb(you, "Lab 2 cells.", f" outline:3px solid {PINK};")}'
            f'<span style="flex:1 1 0; height:2px; margin:0 16px; background:repeating-linear-gradient(90deg, {INK2} 0 4px, transparent 4px 8px);"></span>'
            f'<span style="{MONO} font-size:13px; color:{GREEN};">{lab_name(now["nearest_other"])}</span>{thumb(near, "The nearest lab&#8217;s cells.", f" outline:3px solid {GREEN};")}</div>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:{FIG_TOP}px; width:800px; height:{FIG_H}px; {CARD_ON_DARK} '
            f'padding:12px 16px 12px; display:flex; flex-direction:column; gap:10px;">{drop}'
            f'<div style="flex:1 1 0; min-height:0; display:flex;">{your_map(B, now)}</div>{foot}</div>')


def certificate(R, now, frame):
    """07a, right: ask the data in plain questions; an agent suggests them. Every answer is this batch's replay."""
    qa = lambda q, a: (f'<div style="display:flex; flex-direction:column; gap:4px; padding:10px 0; border-top:1px solid #d3d8da;">'
                       f'<span style="{SANS} font-size:18px; font-weight:600; line-height:1.3; color:{INK};">{q}</span>'
                       f'<span style="{SANS} font-size:18px; line-height:1.3; color:{INK2};">{a}</span></div>')
    pill = f'<span style="display:flex; align-items:center; gap:8px;">{icon("check", GREEN, 26)}<span style="{SANS} font-size:18px; color:{INK2};">yes</span></span>'
    own = {'inside': 'in range', 'below': 'below range', 'above': 'above range'}[now['cell_count_vs_own_history']]
    dist = f'{now["to_nearest_other"]:.1f}'
    seal = open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="64" height="64"')
    head = (f'<div style="display:flex; justify-content:space-between; align-items:center; padding-bottom:6px;">'
            f'<span style="{SANS} font-size:21px; font-weight:700; letter-spacing:-0.02em; color:{INK};">Certificate</span>{seal}</div>')
    return (f'<div class="r" style="animation-delay:1.0s; position:absolute; right:56px; top:{FIG_TOP}px; width:344px; height:{FIG_H}px; box-sizing:border-box; padding:16px 22px 14px; '
            f'background:linear-gradient(180deg,#ffffff,#f1f3f3); border-radius:16px; display:flex; flex-direction:column; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 28px 70px rgba(0,0,0,0.50);">' + head
            + qa('Do my controls look &#8220;normal&#8221;?', pill)
            + qa('Which lab is closest to mine?', f'{lab_name(now["nearest_other"])}' + pdf(f', {dist} away'))
            + qa('Do my drugs match other labs?', pill + pdf(f'<span style="{SANS} font-size:16px; color:{INK2};">closer on the map: {frame["agree_field_raw"]:.2f} &#8594; <b style="color:{GREEN};">{frame["agree_field_field"]:.2f}</b></span>'))
            + qa('Did my cells grow as usual?', pill + pdf(f'<span style="{SANS} font-size:16px; color:{INK2};">{own}: {now["cells_per_well"]:.0f} per well</span>'))
            + '</div>')


MEASURE = {'centre': 'off centre', 'tightness': 'spread', 'steadiness': 'drift from last batch', 'cells': 'off count'}
CLIMB = {'centre': 'look more typical', 'tightness': 'plates more alike', 'steadiness': 'steadier batches', 'cells': 'cell counts on target'}


def leaderboard(lb, now):
    """The field's top batches and this lab's, ranked on untreated wells alone."""
    mine = {r['batch']: r for r in lb['lab_2']}
    this = mine[now['batch']]; best = min(mine.values(), key=lambda r: r['rank'])
    line = lambda r, own, tag='': (
        f'<div style="display:grid; grid-template-columns:44px 64px 72px 1fr 54px; align-items:center; gap:10px; padding:11px 6px; border-radius:8px; '
        f'background:{"rgba(190,30,116,0.08)" if own else "transparent"}; border-top:1px solid #e4e8e9;">'
        f'<span style="{MONO} font-size:15px; color:{PINK if own else MUTE};">#{r["rank"]}</span>'
        f'<span style="{SANS} font-size:16px; font-weight:{700 if own else 500}; color:{PINK if own else INK};">{lab_name(r["lab"])}</span>'
        f'<span style="{MONO} font-size:15px; color:{MUTE};">{short_date(r["date"]) if r["date"] else r["batch"][:8]}</span>'
        f'<span style="display:flex; align-items:center; gap:8px;"><span class="bar" style="animation-delay:{0.3 + 0.07 * r["rank"] % 1:.2f}s; display:block; height:8px; border-radius:4px; '
        f'width:{r["score"]:.0f}%; background:{PINK if own else GREEN}; opacity:{1 if own else .8};"></span>'
        f'<span style="{MONO} font-size:15px; color:{PINK if own else MUTE};">{tag}</span></span>'
        f'<span style="{SANS} font-size:16px; font-weight:700; color:{PINK if own else INK}; text-align:right;">{r["score"]:.0f}</span></div>')
    head = (f'<div style="display:grid; grid-template-columns:44px 64px 72px 1fr 54px; gap:10px; padding:0 6px 4px;">'
            + ''.join(f'<span style="{SANS} font-size:16px; color:{MUTE};">{s}</span>' for s in ('rank', 'lab', 'batch', 'field score'))
            + '<span></span></div>')
    gap = f'<div aria-hidden="true" style="{MONO} font-size:13px; line-height:1; color:{MUTE}; padding:4px 6px;">&#8230;</div>'
    body = ''.join(line(r, r['lab'] == LAB) for r in lb['top'][:1])
    body += (gap if best['rank'] > 6 else '') + line(best, True, 'best')
    if this['rank'] != best['rank']:
        body += (gap if this['rank'] > best['rank'] + 1 else '') + line(this, True, 'this batch')
    return f'<div style="display:flex; flex-direction:column; flex:1 1 0; min-height:0;">{head}{body}</div>'


def standing(lb, now, B, certified):
    row = lambda name, value: (f'<div style="display:flex; flex-direction:column; gap:4px; padding:10px 0; border-top:1px solid #d3d8da;">'
                               f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">{name}</span>'
                               f'<span style="{SANS} font-size:18px; line-height:1.3; color:{INK2};">{value}</span></div>')
    mine = {r['batch']: r for r in lb['lab_2']}
    this = mine[now['batch']]
    weakest = max(this['percentile'], key=lambda m: this['percentile'][m] or 0)
    rec = max(lb['by_lab'], key=lambda b: b['streak']['longest'])
    head = (f'<div style="display:flex; flex-direction:column; gap:3px; padding-bottom:6px;">'
            f'<span style="{SANS} font-size:21px; font-weight:700; letter-spacing:-0.02em; color:{INK};">Standing</span></div>')
    big = (f'<div style="display:flex; align-items:baseline; gap:10px; padding:4px 0 8px;">'
           f'<span style="{SANS} font-size:48px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{PINK};">#{this["rank"]}</span>'
           f'<span style="{SANS} font-size:18px; color:{MUTE};">of {lb["n_batches"]} batches</span></div>')
    top = 1.1 * max(this[weakest], lb['field_median'][weakest])
    ratio = this[weakest] / lb['field_median'][weakest]
    times = 'twice' if 1.7 <= ratio < 2.2 else ('more than twice' if 2.2 <= ratio < 3 else ('three times' if 3 <= ratio < 3.5 else f'{ratio:.1f} times'))
    bar = lambda who, v, c: (f'<div style="display:grid; grid-template-columns:40px 1fr 32px; align-items:center; gap:8px;">'
                             f'<span style="{SANS} font-size:16px; color:{c};">{who}</span>'
                             f'<span style="display:block; height:8px; border-radius:4px; width:{100 * v / top:.0f}%; background:{c};"></span>'
                             f'<span style="{SANS} font-size:16px; color:{c}; text-align:right;">{v:.1f}</span></div>')
    return (f'<div class="r" style="animation-delay:0.8s; position:absolute; right:56px; top:{FIG_TOP}px; width:344px; height:{FIG_H}px; box-sizing:border-box; padding:16px 22px 14px; '
            f'background:linear-gradient(180deg,#ffffff,#f1f3f3); border-radius:16px; display:flex; flex-direction:column; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 28px 70px rgba(0,0,0,0.50);">' + head + big
            + pdf(row('Batches certified', certified))
            + row(f'To climb: {CLIMB[weakest]}', pdf(f'Lab 2&#8217;s {MEASURE[weakest]} is {times} the field&#8217;s.'
                  + f'<div style="display:flex; flex-direction:column; gap:4px; padding-top:6px;">{bar("lab 2", this[weakest], PINK)}{bar("field", lb["field_median"][weakest], GREEN)}'
                    f'<span style="{SANS} font-size:16px; color:{MUTE}; padding-top:2px;">{MEASURE[weakest]}, lower is better; streak {streak(B, now, "margin:0 6px;")} longest in the field: {rec["streak"]["longest"]}</span></div>'))
            + f'<span style="margin-top:auto; display:flex; align-items:center; gap:8px; {SANS} font-size:17px; line-height:1.35; color:{INK2};">{icon("lock", INK2, 22)}<span>private{pdf(", unless the lab shares it")}</span></span>'
            + '</div>')


def board(lb, now):
    bar = (f'<div style="display:flex; justify-content:space-between; align-items:baseline; padding:0 4px;">'
           f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK};">Ranked on controls alone</span>'
           + pdf(f'<span style="{SANS} font-size:16px; color:{MUTE};">off centre, spread, drift from last batch, cell count; U2OS, A17</span>') + '</div>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:204px; width:800px; height:430px; {CARD_ON_DARK} '
            f'padding:14px 16px 12px; display:flex; flex-direction:column; gap:8px;">{bar}{leaderboard(lb, now)}</div>')


def datasets(replay, frame, failed=()):
    """Every lab's untreated wells as one dataset with its certificate: batches on the map, provenance, how far it converts.
    A batch whose known drugs failed (results/e11) is not certified, wherever its untreated wells sit."""
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
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {CELL}" width="{W}" height="{CELL}" role="img" aria-label="{r["on_map"]} of {r["batches"]} batches certified" style="display:block;">{g}</svg>'
    shown = rows[:7]
    cols = 'grid-template-columns:86px 70px 1fr;'
    head = (f'<div style="display:grid; {cols} gap:10px; padding:0 6px 4px;">'
            + ''.join(f'<span style="{SANS} font-size:16px; color:{MUTE};">{s}</span>' for s in ('lab', 'plates', 'batches certified')) + '</div>')
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
           f'<span style="{SANS} font-size:18px; color:{MUTE};">batches certified</span></div>')
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
    lb = results('e14-leaderboard.json')
    rows = datasets(results('e9-replay.json')['labs'], results('e12-field-normalization.json')['by_lab'], results('e11-known-answer.json')['failed'])
    e1 = results('e1.json')['all_sources']; n_wells, n_labs = e1['n_wells'], e1['n_labs']
    you_row = next(r for r in rows if r['lab'] == LAB)
    css = BASE_CSS + '''
    .ping { transform-box: fill-box; transform-origin: center; animation: ping 2.2s ease-out infinite; }
    @keyframes ping { 0% { transform: scale(1); opacity: .9; } 100% { transform: scale(3.4); opacity: 0; } }
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1, .step-2 .s2 { opacity: 1; pointer-events: auto; }
    .flow .s .f, .flow .s .r, .flow .s .bar, .flow .s .ping { animation-play-state: paused; }
    .step-0 .s0 .f, .step-1 .s1 .f, .step-2 .s2 .f, .step-0 .s0 .r, .step-1 .s1 .r, .step-2 .s2 .r,
    .step-1 .s1 .bar, .step-2 .s2 .bar, .step-1 .s1 .ping { animation-play-state: running; }
    .flow { cursor: pointer; }
'''
    H = f'position:absolute; left:56px; top:86px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.05; color:{D_TEXT};'
    P = f'position:absolute; left:56px; top:146px; width:770px; margin:0; {SANS} font-size:19px; line-height:1.38; color:{D_SOFT};'
    FOOT = f'position:absolute; left:56px; bottom:44px; width:800px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">The product</span>'
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 46px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(7, dark=True)}
  {header('07', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">One shared repository<br><span style="color:{D_GREEN};">of raw cell images.</span></h2>
  <h2 class="s s1" style="{H}">Do my cells look &#8220;normal&#8221;,<br><span style="color:{D_GREEN};">next to every other lab?</span></h2>
  <h2 class="s s2" style="{H}">Which labs make<br><span style="color:{D_GREEN};">the most reliable data?</span></h2>
  <div class="s s0">{hub(n_wells, n_labs)}{hub_side(n_wells, n_labs)}</div>
  <div class="s s1">{app(R, B, now)}{certificate(R, now, frame)}</div>
  <div class="s s2">{board(lb, now)}{standing(lb, now, B, f"{you_row['on_map']} of {you_row['batches']}")}</div>
  <div class="s s0 pdfv" style="{FOOT}">the product as proposed, counts from results/e1, JUMP [7], A15, A18, A24</div>
  <div class="s s1 pdfv" style="{FOOT}"><span style="color:{D_TEXT}; font-weight:500;">fig 7</span> a proposed certificate, replayed on public data, JUMP [7], A11, A18</div>
  <div class="s s2 pdfv" style="{FOOT}"><span style="color:{D_TEXT}; font-weight:500;">fig 8</span> score = 100 &#8722; mean percentile &#183; untreated wells &#183; JUMP [7] &#183; A17</div>
  {cue(3, dark=True)}
</div>'''
    steps = {'tag': ['The product'] * 3}
    return css, body, steps
