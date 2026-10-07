"""Slide 01: the question, as a box. Written whole; the dial on the right is figures/assets/title-dial.html."""
from parts import *


def box():
    """The product in one drawing: a drop zone with a control image in it, and the answer it is about to give."""
    return (f'<div class="box" style="display:flex; align-items:center; gap:14px; width:560px; box-sizing:border-box; padding:12px 14px; border-radius:14px; '
            f'background:#ffffff; border:2px dashed #aeb5b8; box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 12px 30px rgba(20,23,26,0.08);">'
            f'<img src="{dna_uri()}" alt="A control well, DNA stain." style="width:52px; height:52px; border-radius:9px; object-fit:cover; background:#000; flex-shrink:0;">'
            f'<div style="display:flex; flex-direction:column; gap:3px; flex-grow:1; min-width:0;">'
            f'<span style="{SANS} font-size:17px; color:{INK};">control image, any microscope</span>'
            f'<span style="{MONO} font-size:13px; color:{MUTE};">no compound, no target, no result</span></div>'
            f'<span style="{MONO} font-size:14px; padding:9px 18px; border-radius:999px; background:{PINK}; color:#ffffff; flex-shrink:0;">ask</span></div>')


def dna_uri():
    from slide07 import well_image, LAB
    return well_image(LAB, None, 'box-you')


def build():
    css = BASE_CSS + open('figures/assets/title-dial.css').read() + '''
    .box { opacity:0; animation: rise .6s cubic-bezier(.2,.8,.2,1) 1.1s forwards; }
'''
    dial = open('figures/assets/title-dial.html').read()
    body = f'''<div style="position:relative; overflow:hidden; width:1280px; height:720px; box-sizing:border-box; padding:88px; display:flex; gap:64px; align-items:stretch; {LIGHT_BG}">
  {dots(1)}
<div style="flex-grow:1; display:flex; flex-direction:column; justify-content:space-between;">
  <div style="display:flex; justify-content:space-between; align-items:baseline; gap:24px;"><span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{INK};">Datum Line</span><span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{PINK};">AI &#215; Bio &#183; 9 Dec</span></div>
  <div style="display:flex; flex-direction:column; gap:30px;">
    <h1 style="margin:0; {SANS} font-size:76px; font-weight:700; letter-spacing:-0.038em; line-height:0.98; color:{INK};">&#8220;Do my cells<br><span style="color:{PINK};">look normal?</span>&#8221;</h1>
    <p style="margin:0; {SANS} font-size:30px; font-weight:600; letter-spacing:-0.02em; line-height:1.15; color:{INK};">Drop an image.<br><span style="color:{GREEN};">Get an answer</span> against every other lab.</p>
    {box()}
  </div>
  <div style="display:flex; flex-direction:column; gap:14px;">
    <p style="margin:0; {SANS} font-size:18px; line-height:1.4; color:#454c50; max-width:560px;">Labs ask for free.<br>Companies that buy cell data pay for the certificate.</p>
    <div style="height:3px; width:88px; border-radius:2px; background:linear-gradient(90deg, {PINK}, {GREEN});"></div>
    <span style="{MONO} font-size:14px; color:{MUTE};">Kat Titterton &#183; San Francisco</span>
  </div>
</div>
  {dial}
</div>'''
    return css, body, None
