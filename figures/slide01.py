"""Slide 01: the title. The question is the founder's punchline on slide 02 (figures/templates/slide02.html); the box is the product on slide 05.
Written whole; the dial on the right is figures/assets/title-dial.html. Since 26 Oct 2026 the dial tells the deck's story in one
motion: lab 2's pink ring starts off-centre, as on 04a's eleven "normals", and slides onto the field's centre, aligned; print shows
the aligned end state."""
from parts import *

ALIGN_CSS = '''
@keyframes align { from { transform: translate(0, 0); } to { transform: translate(-20px, 14px); } }
@keyframes gone { to { opacity: 0; } }
.align { animation: align 1.4s cubic-bezier(.5,0,.2,1) 1.6s forwards; }
.gap { animation: gone .6s ease-out 1.6s forwards; }
@media print { .align { transform: translate(-20px, 14px) !important; } .gap { opacity: 0 !important; } }
'''


def dial():
    """The title dial with lab 2's ring aligning onto the field's centre; the field's ring opens a little wider so both read as a target."""
    d = open('figures/assets/title-dial.html').read()
    swaps = [('<circle cx="200" cy="200" r="104" fill="none" stroke="#0f8f6c" stroke-width="4"/>',
              '<circle cx="200" cy="200" r="122" fill="none" stroke="#0f8f6c" stroke-width="4"/>'),
             ('<line x1="200" y1="200" x2="220" y2="186" stroke="#be1e74" stroke-width="2.5" stroke-linecap="round"/>',
              '<line class="gap" x1="200" y1="200" x2="220" y2="186" stroke="#be1e74" stroke-width="2.5" stroke-linecap="round"/>'),
             ('<g class="drift">', '<g class="align">')]
    for a, b in swaps:
        assert d.count(a) == 1, a[:50]
        d = d.replace(a, b)
    return d


def build():
    """26 Oct (Kat: "i sort of hate this deck ... how do you think it could spark more passion/joy?"; the joy draft, approved): the
    title over a wall of every lab's cells with a tile open for the listener's lab, and the question as it first came to Kat, at MGH,
    over one frog egg. The dial version is build_dial(), kept for one round in case the room misses it."""
    css = BASE_CSS + WALL_CSS + '''
    .t1 { margin:0; font-family:'Archivo', sans-serif; font-size:92px; font-weight:700; letter-spacing:-0.045em; line-height:0.96; color:#f6f7f7; }
    .who { position:absolute; right:56px; bottom:56px; text-align:right; font-family:'Archivo', sans-serif; font-size:22px; line-height:1.35; color:#c9cfd1; }
    '''
    body = f'''<div style="position:relative; overflow:hidden; width:1280px; height:720px; background:{INK};">
  {wall()}
  <div class="band">
    <div style="display:flex; align-items:center; gap:18px; margin-bottom:18px;">{logo(72, D_GREEN, D_PINK)}<span style="{MONO} font-size:28px; letter-spacing:0.12em; text-transform:uppercase; color:{D_TEXT};">Datum Line</span></div>
    <h1 class="t1">Every lab&#8217;s cells.<br><span style="color:{D_GREEN};">One &#8220;normal&#8221;.</span></h1>
    <p style="margin:18px 0 0; {SANS} font-size:28px; font-weight:500; line-height:1.25; color:{D_SOFT};">It started with one frog egg: does it look &#8220;normal&#8221;?</p>
  </div>
  <div class="who"><span style="display:block; font-weight:700; color:{D_TEXT};">Kat Titterton</span>Cofounder, CSO{pdf(", San Francisco")}</div>
  {dots(1, dark=True)}
</div>'''
    return css, body, None


def build_dial():
    css = BASE_CSS + open('figures/assets/title-dial.css').read() + ALIGN_CSS
    body = f'''<div style="position:relative; overflow:hidden; width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 46px; display:flex; gap:64px; align-items:stretch; {LIGHT_BG}">
  {dots(1)}
<div style="flex-grow:1; display:flex; flex-direction:column; justify-content:space-between;">
  <div style="display:flex; align-items:flex-start; height:35px;"><span style="{MONO} font-size:22px; letter-spacing:0.1em; text-transform:uppercase; color:{INK};">Datum Line</span></div>
  <div style="display:flex; flex-direction:column; gap:30px;">
    <h1 style="margin:0; {SANS} font-size:92px; font-weight:700; letter-spacing:-0.042em; line-height:0.96; color:{INK};">Every lab&#8217;s cells.<br><span style="color:{GREEN};">One &#8220;normal&#8221;.</span></h1>
    <p style="margin:0; {SANS} font-size:28px; font-weight:500; letter-spacing:-0.015em; line-height:1.2; color:{INK2};">Membership to a shared repository<br>of every lab&#8217;s control cells.</p>      <!-- 26 Oct (Kat): the product is a membership to the data -->
  </div>
  <div style="display:flex; flex-direction:column; gap:12px;">
    <div style="height:3px; width:88px; border-radius:2px; background:linear-gradient(90deg, {PINK}, {GREEN});"></div>
    <span style="display:flex; flex-direction:column; gap:2px;"><span style="{SANS} font-size:22px; font-weight:700; color:{INK};">Kat Titterton</span>
      <span style="{SANS} font-size:22px; color:{INK2};">Cofounder, CSO{pdf(", San Francisco")}</span></span>
  </div>
</div>
  {dial()}
</div>'''
    return css, body, None
