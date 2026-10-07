"""Slide 07: the product, as one lab would have seen it on one day, and the leaderboard. Written whole from results/e9, e12, e2 and e14.

The batch shown is the lab's in-distribution batch with the most plates. Its whole replay is appendix A11; the leaderboard is A17.
"""
from datetime import date

from parts import *
from slide05 import embedding, map_axes

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
    W, H = 1520, 560
    ax, cloud = map_axes(rows, 0, 0, W, H)
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
    g.append(f'<circle class="ping" cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{PINK}" stroke-width="3"/>')
    g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="{PINK}" stroke="#ffffff" stroke-width="4"/>')
    g.append(text(x, y + 56, 'you', 34, PINK, 'middle', 700))
    g.append(text(nx + 30, ny + 54, f'{now["to_nearest_other"]:.1f} to {lab_name(now["nearest_other"])}', 28, INK2, weight=600))
    g.append(text(28, H - 26, 'PC 1 &#8594;', 22, MUTE))
    g.append(f'<g transform="translate(36,{H - 66}) rotate(-90)">{text(0, 0, "PC 2 &#8594;", 22, MUTE)}</g>')
    return svg(W, H, g, aria='The field of eleven labs in green, this lab in pink, with its wells so far and a line to the nearest other lab.', fit=True)


def streak(B, now):
    """One mark per batch sent so far, and an open one for the next."""
    n = B.index(now) + 1
    mark = lambda k: (f'<g transform="translate({14 + k * 28},14)" class="f" style="animation-delay:{0.5 + 0.08 * k:.2f}s">'
                      f'<circle r="11" fill="{GREEN}"/><g transform="scale(.75)">{TICK}</g></g>')
    nxt = (f'<g transform="translate({14 + n * 28},14)"><circle r="10" fill="none" stroke="{PINK}" stroke-width="2" stroke-dasharray="4 4"/>'
           f'<path d="M -4 0 H 4 M 0 -4 V 4" stroke="{PINK}" stroke-width="2.2" stroke-linecap="round"/></g>')
    W = 28 + n * 28
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 28" width="{W}" height="28" role="img" '
            f'aria-label="{n} batches sent in a row, and a place for the next." style="display:block; flex-shrink:0; margin-left:auto;">'
            + ''.join(mark(k) for k in range(n)) + nxt + '</svg>')


def app(R, B, now):
    d = date.fromisoformat(now['date'])
    n = B.index(now) + 1
    you = well_image(LAB, now['plates'][0], 'box-you'); near = well_image(now['nearest_other'], None, 'box-near')
    thumb = lambda uri, alt: f'<img src="{uri}" alt="{alt}" style="width:56px; height:56px; border-radius:9px; object-fit:cover; background:#000; flex-shrink:0;">'
    drop = (f'<div style="display:flex; align-items:center; gap:14px; padding:8px 12px; border-radius:12px; border:2px dashed #aeb5b8; background:#ffffff;">'
            f'{thumb(you, "The control well that was dropped in: lab 2, DNA stain.")}'
            f'<div style="display:flex; flex-direction:column; gap:2px; flex-grow:1; min-width:0;">'
            f'<span style="{SANS} font-size:16px; color:{INK};">{lab_name(R["lab"])} &#183; plate {now["plates"][0]} &#183; {d.day} {d.strftime("%B")} {d.year}</span>'
            f'<span style="{MONO} font-size:13px; color:{MUTE};">one control well, DNA channel, as imaged</span></div>'
            f'<span style="{MONO} font-size:13px; padding:5px 12px; border-radius:999px; background:{GREEN}; color:#ffffff;">answered</span></div>')
    foot = (f'<div style="display:flex; align-items:center; gap:14px; padding:0 4px;">{thumb(you, "Your cells.")}{thumb(near, "The nearest lab&#8217;s cells.")}'
            f'<span style="{SANS} font-size:17px; color:{INK};"><span style="font-weight:700;">Yours, and {lab_name(now["nearest_other"])}&#8217;s.</span> '
            f'<span style="color:{MUTE};">{now["to_nearest_other"]:.1f} apart.</span></span>{streak(B, now)}</div>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:204px; width:800px; height:430px; {CARD_ON_DARK} '
            f'padding:12px 16px 12px; display:flex; flex-direction:column; gap:10px;">{drop}'
            f'<div style="flex:1 1 0; min-height:0; display:flex;">{your_map(B, now)}</div>{foot}</div>')


def certificate(R, now, frame):
    row = lambda name, value: (f'<div style="display:flex; flex-direction:column; gap:2px; padding:8px 0; border-top:1px solid #d3d8da;">'
                               f'{label(name)}<span style="{SANS} font-size:15px; line-height:1.3; color:{INK};">{value}</span></div>')
    pill = (f'<span style="display:flex; padding:3px 0 5px;"><span style="{MONO} font-size:13px; padding:4px 12px; border-radius:999px; '
            f'background:{GREEN}; color:#ffffff;">in distribution</span></span>')
    own = {'inside': 'in range', 'below': 'below range', 'above': 'above range'}[now['cell_count_vs_own_history']]
    d = date.fromisoformat(now['date'])
    when = f"{lab_name(R['lab'])} &#183; {d.day} {d.strftime('%B')} {d.year}"
    seal = open('figures/assets/seal.svg').read().replace('width="86" height="86"', 'width="76" height="76"')
    head = (f'<div style="display:flex; justify-content:space-between; align-items:center; padding-bottom:6px;">'
            f'<div style="display:flex; flex-direction:column; gap:3px;">'
            f'<span style="{SANS} font-size:21px; font-weight:700; letter-spacing:-0.02em; color:{INK};">The answer</span>'
            f'{label(when, PINK)}</div>{seal}</div>')
    up = f'<span style="color:{GREEN}; font-weight:700;">{frame["agree_field_raw"]:.2f} &#8594; {frame["agree_field_field"]:.2f}</span>'
    return (f'<div class="r" style="animation-delay:1.0s; position:absolute; right:56px; top:106px; width:344px; box-sizing:border-box; padding:16px 22px 14px; '
            f'background:linear-gradient(180deg,#ffffff,#f1f3f3); border-radius:16px; display:flex; flex-direction:column; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 28px 70px rgba(0,0,0,0.50);">' + head
            + row('Your cells', f'U2OS &#183; {now["n_plates"]} plates')
            + row('Where you sit', pill + f'{now["from_baseline"]:.1f} from your baseline &#183; {now["to_nearest_other"]:.1f} to {lab_name(now["nearest_other"])}, the nearest')
            + row('Your own check', f'{now["cells_per_well"]:.0f} cells per well &#183; {own}')
            + row('Your reference', f'{R["n_reference_plates"]:,} plates &#183; {len(R["reference_labs"])} labs')
            + row('Your data, made comparable', f'agreement with other labs {up}')
            + f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE}; padding-top:8px; border-top:1px solid #d3d8da;">'
            f'This page is the certificate. Held by nobody who sells you cells.</span></div>')


MEASURE = {'centre': 'typical', 'tightness': 'tight', 'steadiness': 'steady', 'cells': 'count'}


def leaderboard(lb, now):
    """The field's top batches and this lab's, ranked on untreated wells alone."""
    mine = {r['batch']: r for r in lb['lab_2']}
    this = mine[now['batch']]; best = min(mine.values(), key=lambda r: r['rank'])
    rows = lb['top'][:5] + [best] + ([this] if this['rank'] != best['rank'] else [])
    line = lambda r, own, tag='': (
        f'<div style="display:grid; grid-template-columns:44px 64px 78px 52px 1fr 54px; align-items:center; gap:10px; padding:7px 6px; border-radius:8px; '
        f'background:{"rgba(190,30,116,0.08)" if own else "transparent"}; border-top:1px solid #e4e8e9;">'
        f'<span style="{MONO} font-size:14px; color:{PINK if own else MUTE};">#{r["rank"]}</span>'
        f'<span style="{SANS} font-size:15px; font-weight:{700 if own else 500}; color:{PINK if own else INK};">{lab_name(r["lab"])}</span>'
        f'<span style="{MONO} font-size:13px; color:{MUTE};">{short_date(r["date"]) if r["date"] else r["batch"][:8]}</span>'
        f'<span style="{MONO} font-size:13px; color:{MUTE};">{r["n_plates"]} pl</span>'
        f'<span style="display:flex; align-items:center; gap:8px;"><span class="bar" style="animation-delay:{0.3 + 0.07 * r["rank"] % 1:.2f}s; display:block; height:8px; border-radius:4px; '
        f'width:{r["score"]:.0f}%; background:{PINK if own else GREEN}; opacity:{1 if own else .8};"></span>'
        f'<span style="{MONO} font-size:12px; color:{PINK if own else MUTE};">{tag}</span></span>'
        f'<span style="{SANS} font-size:15px; font-weight:700; color:{PINK if own else INK}; text-align:right;">{r["score"]:.0f}</span></div>')
    head = (f'<div style="display:grid; grid-template-columns:44px 64px 78px 52px 1fr 54px; gap:10px; padding:0 6px 4px;">'
            + ''.join(label(s) for s in ('rank', 'lab', 'batch', 'plates', 'field score'))
            + f'<span style="{MONO} font-size:13px; color:{MUTE}; text-align:right;">/100</span></div>')
    body = ''.join(line(r, r['lab'] == LAB, 'your best' if r is best else ('this batch' if r is this else '')) for r in rows)
    gap = f'<div style="{MONO} font-size:13px; color:{MUTE}; padding:4px 6px 0;">&#8230; {lb["n_batches"] - 5} more batches</div>'
    parts = body.split('<div style="display:grid', 6)
    body = '<div style="display:grid'.join(parts[:6]) + gap + '<div style="display:grid' + '<div style="display:grid'.join(parts[6:]) if len(parts) > 6 else body
    key = ' &#183; '.join(f'<span style="color:{INK};">{v}</span>' for v in MEASURE.values())
    foot = (f'<div style="margin-top:auto; padding:10px 6px 0; border-top:1px solid #e4e8e9; {MONO} font-size:13px; color:{MUTE};">'
            f'four measures, each a percentile among {lb["n_batches"]} batches: {key}</div>')
    return f'<div style="display:flex; flex-direction:column; flex:1 1 0; min-height:0;">{head}{body}{foot}</div>'


def standing(lb, now, B):
    row = lambda name, value: (f'<div style="display:flex; flex-direction:column; gap:2px; padding:8px 0; border-top:1px solid #d3d8da;">'
                               f'{label(name)}<span style="{SANS} font-size:15px; line-height:1.3; color:{INK};">{value}</span></div>')
    mine = {r['batch']: r for r in lb['lab_2']}
    this = mine[now['batch']]; best = min(mine.values(), key=lambda r: r['rank'])
    weakest = max(this['percentile'], key=lambda m: this['percentile'][m] or 0)
    top_lab = lb['by_lab'][0]
    n = B.index(now) + 1
    when = f'{lab_name(LAB)} &#183; {short_date(now["date"])}'
    head = (f'<div style="display:flex; flex-direction:column; gap:3px; padding-bottom:6px;">'
            f'<span style="{SANS} font-size:21px; font-weight:700; letter-spacing:-0.02em; color:{INK};">Your standing</span>'
            f'{label(when, PINK)}</div>')
    big = (f'<div style="display:flex; align-items:baseline; gap:10px; padding:4px 0 8px;">'
           f'<span style="{SANS} font-size:56px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{PINK};">#{this["rank"]}</span>'
           f'<span style="{SANS} font-size:16px; color:{MUTE};">of {lb["n_batches"]} batches &#183; score {this["score"]:.0f}</span></div>')
    badges = ' &#183; '.join(f'{k}: {lab_name(v)}' for k, v in lb['badges'].items() if k in ('closest to the centre', 'tightest plates', 'longest streak'))
    return (f'<div class="r" style="animation-delay:0.8s; position:absolute; right:56px; top:106px; width:344px; box-sizing:border-box; padding:16px 22px 14px; '
            f'background:linear-gradient(180deg,#ffffff,#f1f3f3); border-radius:16px; display:flex; flex-direction:column; '
            f'box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 28px 70px rgba(0,0,0,0.50);">' + head + big
            + row('Your best', f'#{best["rank"]}, {short_date(best["date"])} &#183; score {best["score"]:.0f}')
            + row('Your streak', f'{n} batches in a row &#183; the field&#8217;s longest: {lb["by_lab"][0]["streak"]["longest"]}, {lab_name(lb["badges"]["longest streak"])}')
            + row('To climb', f'{MEASURE[weakest]}: {this[weakest]:.1f} against {lb["field_median"][weakest]:.1f} for the field')
            + row('The lab to beat', f'{lab_name(top_lab["lab"])} &#183; median score {top_lab["median_score"]:.0f} over {top_lab["n_batches"]} batches')
            + f'<span style="{MONO} font-size:13px; line-height:1.45; color:{MUTE}; padding-top:8px; border-top:1px solid #d3d8da;">{badges}</span></div>')


def board(lb, now):
    bar = (f'<div style="display:flex; justify-content:space-between; align-items:center; padding:0 4px;">'
           f'<span style="{MONO} font-size:13px; letter-spacing:0.08em; text-transform:uppercase; color:{MUTE};">Leaderboard &#183; U2OS &#183; {lb["n_batches"]} batches &#183; {lb["n_labs"]} labs</span>'
           f'<span style="{MONO} font-size:13px; padding:4px 12px; border-radius:999px; background:{GREEN}; color:#ffffff;">controls only, never results</span></div>')
    return (f'<div class="r" style="animation-delay:0.2s; position:absolute; left:56px; top:204px; width:800px; height:430px; {CARD_ON_DARK} '
            f'padding:14px 16px 12px; display:flex; flex-direction:column; gap:8px;">{bar}{leaderboard(lb, now)}</div>')


def build():
    R = results('e9-replay.json')['labs'][LAB]; B = R['batches']
    now = max((b for b in B if b['verdict'] == 'in distribution'), key=lambda b: b['n_plates'])
    frame = next(b for b in results('e12-field-normalization.json')['lab_2'] if b['batch'] == now['batch'])
    lb = results('e14-leaderboard.json')
    css = BASE_CSS + '''
    .ping { transform-box: fill-box; transform-origin: center; animation: ping 2.2s ease-out infinite; }
    @keyframes ping { 0% { transform: scale(1); opacity: .9; } 100% { transform: scale(3.4); opacity: 0; } }
    .flow .s { opacity: 0; pointer-events: none; transition: opacity .5s ease; }
    .step-0 .s0, .step-1 .s1 { opacity: 1; pointer-events: auto; }
    .flow .s .f, .flow .s .r, .flow .s .bar, .flow .s .ping { animation-play-state: paused; }
    .step-0 .s0 .f, .step-1 .s1 .f, .step-0 .s0 .r, .step-1 .s1 .r, .step-0 .s0 .bar, .step-1 .s1 .bar, .step-0 .s0 .ping { animation-play-state: running; }
    .flow { cursor: pointer; }
'''
    H = f'position:absolute; left:56px; top:86px; margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.05; color:{D_TEXT};'
    P = f'position:absolute; left:56px; top:146px; width:770px; margin:0; {SANS} font-size:19px; line-height:1.38; color:{D_SOFT};'
    FOOT = f'position:absolute; left:56px; bottom:44px; width:800px; {MONO} font-size:13px; line-height:1.5; color:{D_DIM};'
    right = f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{D_GREEN};">The product &#183; the map</span>'
    body = f'''<div class="flow step-0" style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 46px; {DARK_BG} position:relative; overflow:hidden;">
  {dots(7, dark=True)}
  {header('07', '', dark=True, right_html=right)}
  <h2 class="s s0" style="{H}">Drop an image. <span style="color:{D_PINK};">Get an answer.</span></h2>
  <h2 class="s s1" style="{H}">A game <span style="color:{D_PINK};">you can win.</span></h2>
  <p class="s s0" style="{P}">Where your cells sit, <span style="color:{D_TEXT}; font-weight:600;">whose they look like, and their cells next to yours.</span></p>
  <p class="s s1" style="{P}">Every batch ranked on its controls alone: <span style="color:{D_TEXT}; font-weight:600;">how typical, how tight, how steady.</span><br>Never on results.</p>
  <div class="s s0">{app(R, B, now)}{certificate(R, now, frame)}</div>
  <div class="s s1">{board(lb, now)}{standing(lb, now, B)}</div>
  <div class="s s0" style="{FOOT}"><span style="color:{D_TEXT}; font-weight:500;">Fig. 5</span> {lab_name(R['lab']).capitalize()} on {short_date(now['date'])}, replayed against the published field. JUMP [7]. More: A11</div>
  <div class="s s1" style="{FOOT}"><span style="color:{D_TEXT}; font-weight:500;">Fig. 6</span> Field score: 100 minus the mean percentile of four measures on untreated wells. JUMP [7]. More: A17</div>
  <div style="position:absolute; right:56px; bottom:44px; {MONO} font-size:13px; color:{D_DIM};"><span data-h="hint">click &#8594; the leaderboard</span></div>
</div>'''
    steps = {'tag': ['The product \u00b7 the box', 'The product \u00b7 the leaderboard'],
             'hint': ['click \u2192 the leaderboard', 'click \u2192 start over']}
    return css, body, steps
