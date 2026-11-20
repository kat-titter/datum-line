"""The frame and small parts every appendix board is drawn with: its box, headline, lede, figure card and note, the top
line, a card, a 384-well plate and the who-uses rows."""

from parts import *


BOARD = (f'width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 44px; display:flex; flex-direction:column; gap:14px; '
         f'{LIGHT_BG} position:relative; z-index:0; overflow:hidden;')
H2 = f'margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; flex-shrink:0;'
LEDE = f'margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE}; flex-grow:1;'
FIGURE = (f'box-sizing:border-box; background: linear-gradient(90deg, #be1e74, #0f8f6c) top / 100% 3px no-repeat, #ffffff; '
          f'border-radius:16px; padding:17px 22px 14px; box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 16px 40px rgba(20,23,26,0.10); '
          f'display:flex; align-items:stretch; min-height:0; min-width:0;')
NOTE = f'{MONO} font-size:13px; line-height:1.5; color:{MUTE};'
SUB = 'font-size:13px; line-height:0;'                  # sub- and superscripts in a NOTE line, without moving the line
HALO_PANEL = f' stroke="{PANEL}" stroke-width="4" stroke-linejoin="round" paint-order="stroke"'   # a label's halo on a map panel


def top_line(code, asked, tag=''):
    back = f' &#183; from slide {BEHIND[code]}' if code in BEHIND else ''
    right = f'<span class="note" style="{MONO} font-size:13px; letter-spacing:0.06em; color:{MUTE};">{tag}</span>' if tag else ''      # names keep their case (A22, ATCC, Nature Communications)
    return watermark(code) + header(f'{code} &#183; {asked}{back}', '', right_html=right or ' ')


def card(title, body, delay, grow=1, colour=PINK, center=False):
    # center (17 Nov night, Kat: "centering helps negative space look less weird"): a short card's words sit in the middle of its height
    return (f'<div class="r" style="animation-delay:{delay:.2f}s; flex:{grow}; {CARD} padding:12px 18px; display:flex; flex-direction:column; gap:5px;{" justify-content:center;" if center else ""}">'
            f'{label(title, colour)}<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{body}</span></div>')


def plate_map(x, y, title, sub, labelled, lookalike, P=13, colour=GREEN, ground=PANEL, empty='#c3c9cb'):
    """A 384-well plate: filled dots for `lookalike`, rings for `labelled`. A8 draws the field's answer in green; A18 draws your controls in pink."""
    k = P / 13
    g = [text(x, y - 34, title, 22, INK, weight=700), text(x, y - 10, sub, 20, MUTE)] if title else []
    g.append(f'<rect x="{x - 8}" y="{y - 2}" width="{24 * P + 16}" height="{16 * P + 12}" rx="10" fill="{ground}"/>')
    for r, row in enumerate('ABCDEFGHIJKLMNOP'):
        for c in range(1, 25):
            well = f'{row}{c:02d}'
            cx, cy = x + (c - 0.5) * P, y + 4 + (r + 0.5) * P
            if well in lookalike:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="{5.2 * k:g}" fill="{colour}"/>')
            else:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="{2.2 * k:.3g}" fill="{empty}"/>')
            if well in labelled:
                g.append(f'<circle cx="{cx}" cy="{cy}" r="{8.5 * k:.3g}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    return g


def who_uses(rows, size=15):
    """17 Nov 2026 (Kat: "more detail on applications for biosecurity, reproducibility in science"): who uses a check, and how.
    One row per user: who in ink, what they do with it beside it."""
    return (f'<div style="display:grid; grid-template-columns:auto minmax(0,1fr); column-gap:14px; row-gap:3px; align-items:baseline;">'
            + ''.join(f'<span style="{SANS} font-size:{size}px; font-weight:600; line-height:1.3; color:{INK}; white-space:nowrap;">{who}</span>'
                      f'<span style="{SANS} font-size:{size}px; line-height:1.3; color:{INK2};">{how}</span>' for who, how in rows) + '</div>')
