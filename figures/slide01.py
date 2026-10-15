"""Slide 01: the title, quiet on purpose. The question is the founder's punchline on slide 02 (coherence.reveal); the box is
the product on slide 07. Written whole; the dial on the right is figures/assets/title-dial.html."""
from parts import *


def build():
    css = BASE_CSS + open('figures/assets/title-dial.css').read() + '''
'''
    dial = open('figures/assets/title-dial.html').read()
    body = f'''<div style="position:relative; overflow:hidden; width:1280px; height:720px; box-sizing:border-box; padding:88px; display:flex; gap:64px; align-items:stretch; {LIGHT_BG}">
  {dots(1)}
<div style="flex-grow:1; display:flex; flex-direction:column; justify-content:space-between;">
  <div style="display:flex; justify-content:space-between; align-items:baseline; gap:24px;"><span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{INK};">Datum Line</span><span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{PINK};">AI &#215; Bio</span></div>
  <div style="display:flex; flex-direction:column; gap:30px;">
    <h1 style="margin:0; {SANS} font-size:76px; font-weight:700; letter-spacing:-0.038em; line-height:0.98; color:{INK};"><span style="color:{GREEN};">Confidence</span><br>with controls.</h1>
    <p style="margin:0; {SANS} font-size:28px; font-weight:500; letter-spacing:-0.015em; line-height:1.2; color:{INK2};">A shared map for every lab&#8217;s cells.</p>
  </div>
  <div style="display:flex; flex-direction:column; gap:14px;">
    <div style="height:3px; width:88px; border-radius:2px; background:linear-gradient(90deg, {PINK}, {GREEN});"></div>
    <span style="{MONO} font-size:14px; color:{MUTE};">Kat Titterton &#183; San Francisco</span>
  </div>
</div>
  {dial}
</div>'''
    return css, body, None
