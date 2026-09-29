"""Slide 10: the field, replayed, and the ask. Written whole from results/e9 and e11."""
from parts import *

CELL, GAP, ROW = 14, 3, 21
IN = '#7cc4aa'      # the brand green at about half strength, as a solid so the entrance fade does not change it


def field_grid(replay, known):
    labs = sorted(replay, key=lab_number)
    failed = {(f['lab'], f['batch']) for f in known['failed']}
    widest = max(len(replay[l]['batches']) for l in labs)
    x0 = 66
    g = []
    for r, lab in enumerate(labs):
        y = r * ROW
        own = lab == 'source_2'
        g.append(f'<text x="{x0 - 12}" y="{y + 12}" font-family="IBM Plex Mono, Menlo, monospace" font-size="13" fill="{PINK if own else MUTE}" text-anchor="end">{lab_name(lab)}</text>')
        for k, b in enumerate(replay[lab]['batches']):
            x = x0 + k * (CELL + GAP)
            out = b['verdict'] == 'outside'
            g.append(f'<rect class="f" style="animation-delay:{0.2 + 0.012 * (r * 6 + k):.2f}s" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3.5" '
                     f'fill="{PINK if out else IN}"/>')
            if (lab, b['batch']) in failed:
                g.append(f'<path d="M {x + 3.5} {y + 3.5} l 7 7 m 0 -7 l -7 7" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    W, H = x0 + widest * (CELL + GAP), len(labs) * ROW
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="Every batch of every lab in run order, coloured by the certificate it would have received." style="display:block;">' + ''.join(g) + '</svg>')


def build():
    replay = results('e9-replay.json')['labs']
    known = results('e11-known-answer.json')
    n = sum(v['n_batches'] for v in replay.values())
    n_plates = sum(v['n_plates'] for v in replay.values())
    outside = sum(v['batches_outside'] for v in replay.values())
    failed = len(known['failed'])
    key = lambda mark, word: f'<span style="display:flex; gap:7px; align-items:center;">{mark}{word}</span>'
    square = lambda c, o: f'<span style="width:13px; height:13px; border-radius:3.5px; background:{c}; opacity:{o}; display:block;"></span>'
    cross = (f'<svg viewBox="0 0 14 14" width="13" height="13" aria-hidden="true"><path d="M 3 3 l 8 8 m 0 -8 l -8 8" stroke="{INK}" '
             f'stroke-width="2" stroke-linecap="round"/></svg>')
    step = lambda name, what, colour: (f'<div style="display:flex; flex-direction:column; gap:4px; min-width:0;">{label(name, colour)}'
                                       f'<span style="{SANS} font-size:16px; line-height:1.3; color:{INK};">{what}</span></div>')
    left = f'''<div class="r" style="{CARD} padding:18px 24px 18px; display:flex; flex-direction:column; gap:12px; animation-delay:0.2s; min-width:0;">
      <div style="display:flex; justify-content:space-between; align-items:baseline; white-space:nowrap;"><span>{label('Fig. 7', INK)} {label('&#183; The field, replayed')}</span><span style="{MONO} font-size:13px; color:{MUTE};">{n} batches &#183; {len(replay)} labs [7] &#183; results/e9, e11</span></div>
      {field_grid(replay, known)}
      <div style="display:flex; gap:22px; align-items:center; {MONO} font-size:13px; color:{MUTE};">{key(square(IN, 1), 'in distribution')}{key(square(PINK, 1), 'outside')}{key(cross, 'known answer failed')}<span style="margin-left:auto;">run order &#8594;</span></div>
      <span style="{SANS} font-size:18px; line-height:1.35; color:{INK};"><span style="color:{PINK}; font-weight:600;">{outside} of {n}</span> batches outside their own baseline. <span style="font-weight:600;">{failed}</span> where the known answer failed.</span>
      <div style="display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:18px; margin-top:auto; padding-top:14px; border-top:1px solid #e4e8e9;">
        {step('Next', 'what to change, which lots work', GREEN)}{step('Then', 'bad-lot alerts across labs', GREEN)}{step('The set', 'a reference built to break', PINK)}{step('Beyond', 'microscopes, catalogue, drift', MUTE)}
      </div>
    </div>'''
    need = open('figures/assets/slide10-what-i-need.html').read().replace('class="c"', 'class="r"')
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 52px; display:flex; flex-direction:column; gap:20px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(10)}
  {header('10', 'Where this goes, and what I need')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.04; color:{INK}; width:520px; flex-shrink:0;">Every plate you image, <span style="color:{GREEN};">placed in the field.</span></h2>
    <p style="margin:0; {SANS} font-size:18px; line-height:1.4; color:{MUTE}; flex-grow:1;">A growth chart for cell lines. Every certificate adds a plate to the reference, and the reference is what nobody can build alone.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,1.5fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">{left}{need}</div>
</div>'''
    return BASE_CSS, body, None
