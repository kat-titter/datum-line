"""Slide 08: who else answers a question about your cells. Six tools, six questions, each with what it does not see.

Written whole. Datum Line is one row among six, with its own gap stated, so the slide reads as a landscape and not a scorecard.
Each gap names the board that backs it; the collaborative line (use all of them) is the headline, not a footnote.
"""
from parts import *

ROWS = [
    ('DNA fingerprint (STR)', 'Is it the line the label says?', 'how the cells behave'),
    ('vendor certificate', 'Was it fine when it shipped?', 'anything after shipping'),
    ('plate controls', 'Did this plate work?', 'a whole lab drifting'),
    ('in-house platforms', 'Is my own data consistent?', 'lab differences; it removes them'),
    ('data factories', 'Where do I get cell data at scale?', 'other labs&#8217; &#8220;normal&#8221;'),
    ('Datum Line', 'Do my cells look &#8220;normal&#8221;, next to every other lab?', 'which cell line it is; unstained images, not yet'),
]
BACKED = {'DNA fingerprint (STR)': 'A7', 'plate controls': 'A1', 'in-house platforms': 'A3', 'data factories': 'A23', 'Datum Line': 'A7, A10'}   # the board behind each gap
# on stage: each tool drawn, its question short, its gap in two or three words (fair: Datum Line's own gap too); the PDF keeps ROWS whole
TOOL_ICON = {'DNA fingerprint (STR)': 'dna', 'vendor certificate': 'shipped', 'plate controls': 'plate', 'in-house platforms': 'in-house',
             'data factories': 'factory', 'Datum Line': 'map'}
STAGE_Q = {'Datum Line': '&#8220;Normal&#8221;, next to every lab?', 'DNA fingerprint (STR)': 'Right cell line?', 'vendor certificate': 'Fine when shipped?', 'in-house platforms': 'Own data consistent?',
           'data factories': 'Cell data at scale?'}
# 26 Oct (Kat: "six tools: show industry knowledge, name specific tools, illustrate covering each others blind spots and synergy"):
# each tool by the products a lab would name (sources in README 14, 29-32), and the hub that shows who sees whose blind spot
NAMED = {'DNA fingerprint (STR)': 'ATCC STR profiling', 'vendor certificate': 'ATCC, ECACC certificates', 'plate controls': 'Z&#8242;-factor',
         'in-house platforms': 'Incucyte, CellProfiler', 'data factories': 'Recursion, JUMP'}
NAMED_REF = {'DNA fingerprint (STR)': '[14]', 'vendor certificate': '[29]', 'plate controls': '[30]', 'in-house platforms': '[31, 32]', 'data factories': '[7, 11]'}
SEES_FOR_US = {'DNA fingerprint (STR)': 'which cell line', 'in-house platforms': 'unstained cells'}      # Datum Line's own gaps, and who covers them
SHORT_NO = {'DNA fingerprint (STR)': 'cell behaviour', 'vendor certificate': 'after shipping', 'plate controls': 'lab drift',
            'in-house platforms': 'lab differences', 'data factories': 'other labs', 'Datum Line': 'which cell line<br>unstained images'}


def build():
    cols = 'grid-template-columns:256px 1.35fr 1fr;'
    head = (f'<div style="display:grid; {cols} gap:24px; padding:0 20px 10px; border-left:3px solid transparent; border-bottom:1px solid {GRID};">'
            + ''.join(f'<span class="pdfv" style="{SANS} font-size:16px; color:{MUTE};">{s}</span>' for s in ('tool', 'answers'))
            + f'<span style="display:flex; gap:8px; align-items:center; {SANS} font-size:18px; color:{MUTE};">{icon("blind-spot", MUTE, 20)}misses</span></div>')
    last = len(ROWS) - 1
    ref = lambda tool: (f' <span class="pdf" style="{MONO} font-size:13px; color:{MUTE}; white-space:nowrap;">{BACKED[tool]}</span>' if tool in BACKED else '')
    rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; {cols} gap:24px; align-items:center; flex:1; align-content:center; '
        f'padding:12px 20px; {"border-bottom:none;" if k == last else "border-bottom:1px solid #eceff0;"} '
        f'{"border-left:3px solid " + GREEN + "; background:rgba(15,143,108,0.05);" if k == last else "border-left:3px solid transparent;"}">'
        f'<span style="display:flex; gap:12px; align-items:center; {SANS} font-size:20px; font-weight:600; color:{INK};">'
        f'{icon(TOOL_ICON[tool], GREEN if k == last else INK2, 26)}<span>{tool.replace(" (STR)", pdf(" (STR)"))}'
        f'{"<br><span style=" + chr(34) + MONO + " font-size:13px; font-weight:400; color:" + MUTE + ";" + chr(34) + ">" + NAMED[tool] + " " + NAMED_REF[tool] + "</span>" if tool in NAMED else ""}</span></span>'
        f'<span style="{SANS} font-size:20px; font-weight:{600 if k == last else 500}; line-height:1.3; color:{GREEN if k == last else INK2};">'
        f'{talk_span(STAGE_Q[tool]) + pdf(q) if tool in STAGE_Q else q}</span>'
        f'<span style="{SANS} font-size:18px; line-height:1.35; color:{MUTE};">{talk_span(SHORT_NO[tool])}{pdf(no)}{ref(tool)}</span></div>'
        for k, (tool, q, no) in enumerate(ROWS))
    # the stage: Datum Line in the middle, five tools around it; each line carries the tool's blind spot (Datum Line sees it), and two
    # green chips carry Datum Line's own (STR and the label-free instruments see them). Container 1168 x 446, the flex area under the headline.
    W, H, cw, ch, hw, hh = 1168, 446, 250, 124, 300, 150
    place = {'DNA fingerprint (STR)': (0, 0, 'L'), 'vendor certificate': (0, 161, 'L'), 'plate controls': (0, 322, 'L'),
             'in-house platforms': (W - cw, 40, 'R'), 'data factories': (W - cw, 282, 'R')}
    hx, hy = (W - hw) / 2, 120
    hub_pt = {'DNA fingerprint (STR)': (hx, hy + 35), 'vendor certificate': (hx, hy + 75), 'plate controls': (hx, hy + 115),
              'in-house platforms': (hx + hw, hy + 35), 'data factories': (hx + hw, hy + 115)}
    ends = {t: ((x + cw, y + ch / 2) if side == 'L' else (x, y + ch / 2), hub_pt[t]) for t, (x, y, side) in place.items()}
    lines = ''.join(f'<line class="f" style="animation-delay:{0.6 + 0.12 * k:.2f}s" x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" stroke="#aeb5b8" stroke-width="2" '
                    f'marker-end="url(#to-hub)"{" marker-start=" + chr(34) + "url(#to-tool)" + chr(34) if t in SEES_FOR_US else ""}/>'
                    for k, (t, (a, b)) in enumerate(ends.items()))
    marks = (f'<defs><marker id="to-hub" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#aeb5b8"/></marker>'
             f'<marker id="to-tool" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{GREEN}"/></marker></defs>')
    svg_lines = f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true" style="position:absolute; left:0; top:0;">{marks}{lines}</svg>'
    chip = lambda x, y, ico, colour, words, d, bg='#ffffff', fx=0, fy=0: (      # outer span centres the chip; inner one travels in from (fx, fy) along its line
        f'<span style="position:absolute; left:{x:.0f}px; top:{y:.0f}px; transform:translate(-50%, -50%);">'
        f'<span class="dl-travel" style="--fx:{fx:.0f}px; --fy:{fy:.0f}px; animation-delay:{d:.2f}s; display:flex; align-items:center; gap:6px; '
        f'padding:4px 12px; border-radius:999px; background:{bg}; border:1px solid #d3d8da; {SANS} font-size:18px; line-height:1.2; color:{colour}; white-space:nowrap;">'
        f'{icon(ico, colour, 24)}{words}</span></span>')
    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)          # chips sit in the open gap between a card and the hub
    chips = ''.join(chip(mid(a, b)[0], mid(a, b)[1] - (16 if t in SEES_FOR_US else 0), 'blind-spot', MUTE, SHORT_NO[t], 1.0 + 0.12 * k, fx=(a[0] - b[0]) / 2, fy=(a[1] - b[1]) / 2)
                    for k, (t, (a, b)) in enumerate(ends.items()))      # each blind spot slides from its tool toward Datum Line
    chips += ''.join(chip(mid(a, b)[0], mid(a, b)[1] + 16, 'check', GREEN, SEES_FOR_US[t], 1.9 + 0.15 * k, '#f3faf7', fx=(b[0] - a[0]) / 2, fy=(b[1] - a[1]) / 2)
                     for k, (t, (a, b)) in enumerate((t, e) for t, e in ends.items() if t in SEES_FOR_US))
    tool_card = lambda t, x, y, k: (
        f'<div class="r" style="animation-delay:{0.15 + 0.08 * k:.2f}s; position:absolute; left:{x}px; top:{y}px; width:{cw}px; height:{ch}px; padding:12px 16px; box-sizing:border-box; '      # 26 Oct: no card boxes; the hub is the one box
        f'display:flex; flex-direction:column; gap:4px;">'
        f'<span style="margin:auto 0; display:flex; gap:12px; align-items:center; {SANS} font-size:21px; font-weight:600; line-height:1.2; color:{INK};">{icon(TOOL_ICON[t], INK2, 26)}{NAMED[t]}</span></div>')
    hub = (f'<div class="pop" style="animation-delay:0.4s; position:absolute; left:{hx:.0f}px; top:{hy}px; width:{hw}px; height:{hh}px; {CARD} border:2px solid {GREEN}; '
           f'background:#f3faf7; padding:14px 20px; display:flex; flex-direction:column; justify-content:center; gap:8px;">'
           f'<span style="display:flex; gap:10px; align-items:center; {SANS} font-size:20px; font-weight:700; color:{GREEN};">{icon("map", GREEN, 26)}Datum Line</span>'
           f'<span style="{SANS} font-size:22px; font-weight:600; line-height:1.2; color:{INK};">&#8220;Normal&#8221;, every lab?</span></div>')
    key = (f'<div class="f" style="animation-delay:2.4s; position:absolute; left:0; bottom:-6px; display:flex; gap:22px; '      # 26 Oct: keys sit bottom left, on every slide
           f'{SANS} font-size:18px; line-height:1.3; color:{INK2};">'
           f'<span style="display:flex; gap:6px; align-items:center;">{icon("blind-spot", MUTE, 24)}blind spot</span>'
           f'<span style="display:flex; gap:6px; align-items:center;">{icon("check", GREEN, 24)}covered</span></div>')
    figure = (svg_lines + ''.join(tool_card(t, x, y, k) for k, (t, (x, y, _)) in enumerate(place.items())) + hub + chips + key)
    body = f'''<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px; display:flex; flex-direction:column; gap:14px; {LIGHT_BG} position:relative; overflow:hidden;">
  {dots(8)}
  {header('08', 'The landscape')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:{INK}; width:620px; flex-shrink:0;">Six tools, six blind spots.<br><span style="color:{GREEN};">Use all of them.</span></h2>
    {pdf(f'<p style="margin:0; {SANS} font-size:19px; line-height:1.45; color:{MUTE};">Each answers one question well.<br>Each misses something, Datum Line too.</p>')}
  </div>
  <div class="talk" style="flex-grow:1; min-height:0; position:relative;">{figure}</div>
  <div class="r pdf" style="animation-delay:0.1s; {CARD} padding:16px 4px 6px; flex-direction:column; flex-grow:1; min-height:0;">{head}{rows}</div>
  {foot_line('STR: ATCC [14]')}
</div>'''
    css = BASE_CSS + ('@keyframes dl-travel{from{opacity:0;transform:translate(var(--fx),var(--fy))}to{opacity:1;transform:none}}'
                      '.dl-travel{opacity:0;animation:dl-travel .9s cubic-bezier(.3,.1,.2,1) forwards}'
                      '@media (prefers-reduced-motion: reduce){.dl-travel{opacity:1}}')
    return css, body, None
