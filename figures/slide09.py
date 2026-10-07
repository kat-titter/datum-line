"""Slide 09: what the money buys, in four milestones. Nothing here is measured; it is the plan."""
from parts import *
from appendix import preseed_total

MILESTONES = [('Three labs on the map', 'collaborating labs: insitro, Axiom Bio, Soley. U2OS controls, live answers every batch'),
              ('Model that reads any image', 'the map from the picture itself, brightfield included: the bet on A10'),
              ('Benchmark, with two partners', 'two companies contribute failures and get their methods graded. A16'),
              ('First paid certificate', 'on a dataset a company bought and could not align')]


TODAY = 'One founder. Eleven labs of public data, one cell line, fluorescence. Every number in this deck.'
THEN = 'Three partner labs live, a model that reads any image, the benchmark with two partners, and a first paid certificate.'


def build():
    total = f'{preseed_total()[1] / 1000:.1f}'
    n = len(MILESTONES)
    cards = ''.join(
        f'<div class="r" style="animation-delay:{0.3 + 0.18 * k:.2f}s; {CARD} padding:22px 22px 20px; display:flex; flex-direction:column; gap:10px; min-width:0;">'
        f'<span style="{SANS} font-size:44px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:{PINK if k == n - 1 else GREEN};">{k + 1}</span>'
        f'<span style="{SANS} font-size:22px; font-weight:600; letter-spacing:-0.015em; line-height:1.15; color:{INK};">{title}</span>'
        f'<span style="{SANS} font-size:16px; line-height:1.35; color:{MUTE};">{what}</span></div>'
        for k, (title, what) in enumerate(MILESTONES))
    line = ''.join(f'<circle class="f" style="animation-delay:{0.3 + 0.18 * k:.2f}s" cx="{146 + k * 292}" cy="10" r="7" fill="{PINK if k == n - 1 else GREEN}"/>' for k in range(n))
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 52px; display:flex; flex-direction:column; gap:22px; justify-content:flex-start; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(9)}
  {header('09', 'What the money buys')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.04; color:{INK}; width:560px; flex-shrink:0;">Eighteen months, <span style="color:{PINK};">four milestones.</span></h2>
    <p style="margin:0; {SANS} font-size:18px; line-height:1.4; color:{MUTE}; flex-grow:1;">Pre-seed of about ${total}M, eighteen months. A21<br>Each milestone is something a partner lab can see on the map.</p>
  </div>
  <svg viewBox="0 0 1168 20" width="1168" height="20" aria-hidden="true" style="display:block; margin-top:14px;"><line x1="0" y1="10" x2="1168" y2="10" stroke="{GREEN}" stroke-width="2.5" stroke-linecap="round"/>{line}</svg>
  <div style="display:grid; grid-template-columns:repeat({n},minmax(0,1fr)); gap:16px; margin-top:-8px; align-items:stretch;">{cards}</div>
  <div class="r" style="animation-delay:1.1s; display:grid; grid-template-columns:1fr 40px 1fr; align-items:center; gap:0; margin-top:auto; padding:18px 0 0; border-top:1px solid #e4e8e9;">
    <div style="display:flex; flex-direction:column; gap:6px;">{label('Today', MUTE)}<span style="{SANS} font-size:19px; line-height:1.3; color:{INK};">{TODAY}</span></div>
    <span style="{SANS} font-size:28px; color:{GREEN}; text-align:center;">&#8594;</span>
    <div style="display:flex; flex-direction:column; gap:6px;">{label('Month 18', PINK)}<span style="{SANS} font-size:19px; line-height:1.3; color:{INK};">{THEN}</span></div>
  </div>
  <div style="{MONO} font-size:13px; color:{MUTE};">Proposed. The proof of concept sets the size.</div>
</div>'''
    return BASE_CSS, body, None
