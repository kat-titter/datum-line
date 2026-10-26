"""Shared pieces for the slide builders: palette, type, chrome and chart axes.

Every builder in this folder writes whole slides from results/*.json, so running a builder
twice gives the same deck. Nothing on an evidence slide is typed by hand.
"""
import json
import re

SANS = "font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif;"
MONO = "font-family: 'IBM Plex Mono', Menlo, monospace;"
MATH = "font-family: 'Source Serif 4', 'STIX Two Math', 'Cambria Math', Georgia, serif; font-style: italic;"
SVG_MONO = "font-family=\"'IBM Plex Mono', Menlo, monospace\""
SVG_FONT = "font-family=\"'Archivo', 'Helvetica Neue', Helvetica, sans-serif\""

PINK, GREEN, INK, INK2, MUTE, FAINT, GRID, PANEL, PAPER = (
    '#be1e74', '#0f8f6c', '#14171a', '#454c50', '#666e72', '#949c9f', '#d3d8da', '#eceeef', '#f6f7f7')
D_PINK, D_GREEN, D_TEXT, D_SOFT, D_DIM, D_BG = '#ef74ad', '#3fe0a0', '#f6f7f7', '#c9cfd1', '#949c9f', '#14171a'
PALE_PINK = '#e9a3c6'
N_TALK = 10
N_BOARDS = 25          # A1-A25; the old A25 became slide 02's third view on 19 Oct 2026; the new A25 is the shared-data table that left slide 07 on 25 Oct
# the talk slide each appendix board backs: its top line says so, and the slide's caption cites the board
BEHIND = {'A1': '08', 'A2': '03', 'A3': '03', 'A4': '09', 'A5': '03', 'A6': '04', 'A7': '08', 'A8': '04', 'A9': '04', 'A10': '09',
          'A11': '05', 'A12': '04', 'A13': '04', 'A14': '04', 'A15': '05', 'A16': '09', 'A17': '05', 'A18': '05', 'A19': '09',
          'A20': '10', 'A21': '09', 'A22': '07', 'A23': '07', 'A24': '05', 'A25': '05'}      # since 26 Oct: the product is 05, the market 07

LIGHT_BG = ('background:#f6f7f7; background-image: radial-gradient(60% 50% at 100% 0%, rgba(190,30,116,0.07), transparent 70%), '
            'radial-gradient(50% 45% at 0% 100%, rgba(15,143,108,0.08), transparent 70%);')
DARK_BG = ('background:#14171a; background-image: radial-gradient(55% 55% at 100% 0%, rgba(239,116,173,0.16), transparent 70%), '
           'radial-gradient(50% 50% at 0% 100%, rgba(63,224,160,0.13), transparent 70%);')
CARD = ('box-sizing:border-box; background:#ffffff; border-radius:14px; '
        'box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 12px 30px rgba(20,23,26,0.09);')
CARD_ON_DARK = ('box-sizing:border-box; background: linear-gradient(#f6f7f7, #f6f7f7) padding-box, linear-gradient(90deg, #ef74ad, #3fe0a0) border-box; '
                'border-top: 3px solid transparent; border-radius: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 24px 60px rgba(0,0,0,0.45);')
FIG_TOP, FIG_H = 204, 430   # dark slides 04-07: every figure card starts at 204; full-height cards end at 634

BASE_CSS = ''':host{display:block;width:1280px;height:720px}
    a { color: #be1e74; } a:hover { color: #8e1657; }
    @keyframes rise { from { opacity:0; transform: translateY(8px);} to { opacity:1; transform:none;} }
    @keyframes fade { to { opacity: 1; } }
    @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
    .r { opacity:0; animation: rise .45s cubic-bezier(.2,.8,.2,1) forwards; }
    .f { opacity:0; animation: fade .5s ease-out forwards; }
    .bar { transform-origin: left center; transform-box: fill-box; transform: scaleX(0); animation: grow .7s cubic-bezier(.2,.8,.2,1) forwards; }
    /* 26 Oct (Kat: "animations should add clarity, connect related elements; transitions add depth, tell story"): motion follows the
       story's order, cause then effect. pop: a mark arrives (its number, its badge); draw: a line traced in the order it happened
       (needs pathLength="1"); pulse: lab 2's pink mark rings once where it appears; drop: something arrives from above. */
    @keyframes pop { from { opacity:0; transform: scale(.82); } to { opacity:1; transform: none; } }
    @keyframes draw { to { stroke-dashoffset: 0; } }
    @keyframes pulse { 0% { opacity: .85; transform: scale(1); } 100% { opacity: 0; transform: scale(2.4); } }
    @keyframes drop { from { opacity:0; transform: translateY(-26px); } to { opacity:1; transform: none; } }
    .pop { opacity:0; transform-box: fill-box; transform-origin: center; animation: pop .5s cubic-bezier(.2,.8,.3,1.25) forwards; }
    .draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 1.6s cubic-bezier(.4,0,.2,1) forwards; }
    .pulse { opacity:0; transform-box: fill-box; transform-origin: center; animation: pulse 1.3s ease-out 2 forwards; }
    .drop { opacity:0; animation: drop .6s cubic-bezier(.2,.8,.2,1) forwards; }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } .r, .f, .pop, .drop { opacity: 1; } .bar { transform: none; } .draw { stroke-dashoffset: 0; } .pulse { opacity: 0; } }
    @media print { * { box-shadow: none !important; } [style*="radial-gradient"] { background-image: none !important; } }
    h1 span, h2 span { white-space: nowrap; }
'''
HOST_PAUSE = ':host(:not(.in)) *{animation-play-state:paused!important}'
MOTION = ('f', 'r', 'bar', 'pop', 'draw', 'pulse', 'drop', 'ping')


def view_motion(n):
    """A slide with n click views: every motion class waits, paused, until its view is on screen, then plays from its start,
    so each view tells its own sequence when it is clicked to (and the first when the slide scrolls in)."""
    paused = ', '.join(f'.flow .s .{c}' for c in MOTION)
    running = ', '.join(f'.step-{k} .s{k} .{c}' for k in range(n) for c in MOTION)
    return f'{paused} {{ animation-play-state: paused; }}\n    {running} {{ animation-play-state: running; }}'


def results(name, folder='results'):
    return json.load(open(f'{folder}/{name}'))


def lab_name(source):
    return 'lab ' + source.split('_')[1]


def lab_number(source):
    return int(source.split('_')[1])


def short_date(iso):
    y, m, d = iso.split('-')
    return f"{int(d)} {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(m) - 1]}"


def greens(n):
    """n shades of the brand green, dark to light, for labs that are not the one in pink."""
    a, b = (10, 92, 70), (176, 226, 208)
    return ['#%02x%02x%02x' % tuple(round(x + (y - x) * k / max(1, n - 1)) for x, y in zip(a, b)) for k in range(n)]


PAGER_RE = re.compile(r'<div aria-hidden="true" style="position:\s*absolute; left:\s*\d+px; bottom:\s*22px;[^>]*>(?:\s*<div[^>]*></div>)+\s*</div>')


def dots(active, dark=False):
    """The pager at the bottom left of a talk slide; active counts from 1."""
    off = 'rgba(246,247,247,.28)' if dark else '#d3d8da'
    on = D_PINK if dark else PINK
    cells = ''.join(f'<div style="width:{20 if k == active else 9}px; height:4px; border-radius:2px; background:{on if k == active else off};"></div>'
                    for k in range(1, N_TALK + 1))
    return f'<div aria-hidden="true" style="position:absolute; left:56px; bottom:22px; display:flex; gap:6px; align-items:center;">{cells}</div>'


def cue(n, dark=False):
    """Bottom right of a slide with n views, level with the pager: one dot per view, the one on screen filled. No words;
    every click shows the next thing, a view or the next slide."""
    on = ', '.join(f'.step-{k} .cue i:nth-child({k + 1})' for k in range(n))
    return (f'<style>.cue i{{width:6px; height:6px; border-radius:50%; box-sizing:border-box; border:1.5px solid currentColor; transition:background .3s}} '
            f'{on}{{background:currentColor}}</style>'
            f'<div class="cue" aria-hidden="true" style="position:absolute; right:56px; bottom:21px; z-index:6; display:flex; gap:6px; '
            f'color:{"rgba(246,247,247,.55)" if dark else FAINT};">' + '<i></i>' * n + '</div>')


# Two builds from one deck. On the live talk slides the web page hides the paper apparatus (figure legends, [n] and board
# codes, slide numbers, section tags, 'proposed' notes); the PDF, which is printed without that rule, keeps all of it.
# pdf: removed from the talk view; pdfv: kept in the layout but invisible (header slots, so nothing moves).
# JUMP's "untreated" wells are cells with no reagent at all; every reference well in this deck is a DMSO well, the drug's solvent and
# no drug, JUMP's negative control [7]. One wording everywhere, applied last by the deck, documents and private pages.
DMSO_WORDS = [(r'[Uu]ntreated DMSO', 'DMSO control'), (r'untreated \(DMSO\)', 'DMSO control'), (r'untreated vs untreated', 'DMSO vs DMSO'),
              (r'images of untreated cells', 'images of control cells'), (r'\buntreated U2OS wells', 'U2OS DMSO wells'),
              (r'\buntreated-well\b', 'DMSO-well'), (r'\bUntreated\b', 'DMSO'), (r'\buntreated\b', 'DMSO')]


def dmso_words(html):
    """Name the control: DMSO wells, not untreated wells."""
    for a, b in DMSO_WORDS:
        html = re.sub(a, b, html)
    assert 'DMSO DMSO' not in html
    return html


def scale_bar(field_um, bar_um=100, inset=9, height=4, size=14, cls='scalebar', right=False):
    """A labelled scale bar for a cell image whose full width shows field_um micrometres. Place it inside the image's
    position:relative box; the bar's width is a share of that box, so it stays true at any size."""
    return (f'<div class="{cls}" style="position:absolute; {"right" if right else "left"}:{inset}px; bottom:{inset}px; width:calc(100% * {bar_um} / {field_um:.1f}); '
            f'display:flex; flex-direction:column; align-items:flex-{"end" if right else "start"}; gap:4px; pointer-events:none;">'
            f'<span style="{MONO} font-size:{size}px; line-height:1; color:#f6f7f7; white-space:nowrap; text-shadow:0 1px 2px rgba(0,0,0,.9);">{bar_um} &#181;m</span>'
            f'<div style="width:100%; height:{height}px; border-radius:2px; background:#f6f7f7;"></div></div>')


# what each image channel shows: (the dye, for the reader; what it lights up, for the room)
STAINS = {'DNA': ('Hoechst', 'DNA'), 'Brightfield': ('', 'brightfield')}      # brightfield: transmitted light, no dye channel


def stain_chip(*channels, inset=9, size=13, inline=False, short=False, dark=True, top=False):
    """A chip naming an image's channel(s): a pill bottom right of the image's position:relative box (inline: in the flow, under
    the image). short: the dye goes to the reader's layer, the room reads only what it lights up. No separator between channels."""
    bg, ink = ('rgba(20,23,26,.72)', '#f6f7f7') if dark else ('#e4e8e9', INK2)
    words = [((pdf(dye + ', ') if short else dye + ', ') if dye else '') + target for dye, target in (STAINS[c] for c in channels)]
    place = 'display:inline-flex; align-self:flex-start;' if inline else f'position:absolute; right:{inset}px; {"top" if top else "bottom"}:{inset}px; display:flex;'
    return (f'<div class="stain" style="{place} gap:8px; padding:3px 8px; border-radius:999px; background:{bg}; '
            f'{MONO} font-size:{size}px; line-height:1.3; color:{ink}; white-space:nowrap; pointer-events:none;">'
            + ''.join(f'<span>{w}</span>' for w in words) + '</div>')


def pdf(html):
    return f'<span class="pdf">{html}</span>'


def talk(html):
    """The other way round: shown on stage, left out of the PDF and the D view (the reader's layer has its own version)."""
    return f'<div class="talk">{html}</div>'


def talk_span(html):
    """talk() inline: a word or phrase shown on stage only, beside its pdf() twin."""
    return f'<span class="talk">{html}</span>'


def header(left, right, dark=False, right_html=None):
    c1, c2 = (D_DIM, D_GREEN) if dark else (MUTE, GREEN)
    r = right_html or f'<span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{c2};">{right}</span>'
    return (f'<div style="display:flex; justify-content:space-between; align-items:baseline;">'
            f'<span class="pdfv" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{c1};">{left}</span>'
            f'<span class="pdfv">{r}</span></div>')


def chart_title(x, y, s, size=21, fill=MUTE):
    """A chart title inside an SVG, in the label face: Plex Mono, uppercase, 0.1em, as label() in HTML. Size it to render 13-15px."""
    s = re.sub(r'(&#?\w+;)|([^&]+)', lambda m: m.group(1) or m.group(2).upper(), s)
    return f'<text x="{x:.1f}" y="{y:.1f}" {SVG_MONO} font-size="{size}" fill="{fill}" letter-spacing="{size * 0.1:g}">{s}</text>'


# 26 Oct 2026 (Kat: "always explain where core key numbers like est revenue per institution come from"): every talk slide's foot
# slot carries a short source line on stage, in the same place and face on every slide; the reader's layer keeps the full legend there.
STAGE_SOURCE = 'font-size:15px; line-height:1.4;'
# the one panel every number column on the dark slides sits in (04a-04c, 06, 07): stat_tile's ground, top-aligned with the figure card
PANEL_DARK = 'box-sizing:border-box; padding:14px 16px 12px; border-radius:12px; background:rgba(246,247,247,.06);'


def source(stage, full=''):
    """What goes in a foot slot: the stage's source line, then the reader's full legend. The stage line fits one line of the slot
    (1010px of Plex Mono at 15px holds about 110 characters), so it never crowds the figure card above it."""
    shown = re.sub(r'&#?\w+;', 'x', re.sub(r'<[^>]+>', '', stage))
    assert len(shown) <= 105, f'source line too long for one line ({len(shown)}): {shown}'
    return (f'<span class="talk" style="{STAGE_SOURCE}">{stage}</span>' if stage else '') + (pdf(full) if full else '')


def foot_line(html, dark=False, delay=None, stage=''):
    """The legend or source line at the bottom left of a talk slide, on the 04-07 baseline (bottom:44). With stage, the slot shows
    a short source line on stage too; without, it is the reader's only."""
    hide = '' if stage else ' pdfv'
    anim = f'class="r{hide}" style="animation-delay:{delay}s; ' if delay is not None else f'class="{hide.strip()}" style="'
    html = source(stage, html) if stage else html
    return (f'<div {anim}position:absolute; left:56px; bottom:44px; width:1010px; {MONO} font-size:13px; line-height:1.5; '
            f'color:{D_DIM if dark else MUTE};">{html}</div>')


# the nouns of the talk, drawn once and reused: a well (one dish of cells), a plate (a grid of wells), a batch (plates imaged
# together), a lab (its flask), the software that measures an image, a microscope. 24 x 24, stroke paths, no fill.
ICONS = {'well': '<circle cx="12" cy="12" r="8.5"/><circle cx="9.5" cy="10" r="1.3" fill="currentColor"/><circle cx="14.5" cy="9" r="1.3" fill="currentColor"/><circle cx="12.5" cy="14.5" r="1.3" fill="currentColor"/><circle cx="8.5" cy="14" r="1.1" fill="currentColor"/>',
         'plate': '<rect x="2.5" y="5" width="19" height="14" rx="2"/>' + ''.join(f'<circle cx="{6 + 4 * c}" cy="{8.5 + 3.5 * r}" r="1" fill="currentColor"/>' for r in range(3) for c in range(4)),
         'batch': '<rect x="4" y="9" width="17" height="11" rx="2"/><path d="M6.5 6.5h15v9"/><path d="M9 4h15v7"/>' + ''.join(f'<circle cx="{7.5 + 3.5 * c}" cy="{12.5 + 3.5 * r}" r="0.9" fill="currentColor"/>' for r in range(2) for c in range(4)),
         'lab': '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M7.5 15h9"/>',
         'measure': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 15.5l3-4 3 2.5 4-6"/><path d="M3 9h18"/>',
         'microscope': '<path d="M9 3l5 5-4 4-5-5z"/><path d="M11 11l3 3"/><path d="M14 14a5 5 0 0 1-5 6H6"/><path d="M4 21h16"/><path d="M15 14h5"/>',
         'person': '<circle cx="12" cy="8" r="3.4"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/>',
         'flag': '<path d="M4 21V4h11l-1 3 1 3H4"/><path d="M4 10h11"/>',
         'check': '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.6 2.6L16 9.5"/>',
         'patent': '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 11h6M9 14.5h6"/><circle cx="15.5" cy="18.5" r="2.2"/>',
         # a kill chain (slide 05): a drug docked in its enzyme's pocket; a lipid carrying a peroxide (O-O); a cell whose edge gives way
         # what lab-to-lab difference costs (slide 05): a hit in one lab, not the next; two datasets that do not line up; a model
         'no-replicate': '<path d="M2.5 12.5l2.8 2.8L10.5 10"/><path d="M14.5 9.5l6 6M20.5 9.5l-6 6"/>',
         'no-pool': '<ellipse cx="7" cy="5.8" rx="4" ry="1.8"/><path d="M3 5.8v9.4c0 1 1.8 1.8 4 1.8s4-.8 4-1.8V5.8"/><ellipse cx="17" cy="8.8" rx="4" ry="1.8"/><path d="M13 8.8v9.4c0 1 1.8 1.8 4 1.8s4-.8 4-1.8V8.8"/>',
         'model': '<rect x="5" y="5" width="14" height="14" rx="2.5"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
         'drug': '<path d="M10.5 20.5a5 5 0 0 1-7-7l6-6a5 5 0 0 1 7 7z"/><path d="M8.5 8.5l7 7"/>',
         'lock': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
         'binds': '<path d="M19.25 8.6A8 8 0 1 0 19.25 15.4"/><rect x="15.2" y="9.5" width="5" height="5" rx="1.5"/>',
         'peroxide': '<circle cx="7.3" cy="5.6" r="2.3"/><path d="M6.1 7.7l-1.2 2.9 1.2 2.9-1.2 2.9"/><path d="M9 8l1.3 2.8-1.3 2.9 1.5 2.6"/><path d="M10.5 16.4l1.4-0.5"/><circle cx="13.9" cy="15.4" r="2.2"/><circle cx="18.2" cy="13.5" r="2.2"/>',
         'cell-dies': '<path d="M19.88 13.39A8 8 0 0 1 9.26 19.52"/><path d="M6.86 18.13A8 8 0 0 1 6.86 5.87"/><path d="M9.26 4.48A8 8 0 0 1 19.88 10.61"/><circle cx="12" cy="12" r="2.6"/>',
         # who else answers a question about cells (slide 08): a DNA fingerprint, a parcel as shipped, a lab checking its own data, a data factory;
         # and what a tool does not see (a struck eye)
         'dna': '<path d="M7 3c0 4.5 10 4.5 10 9s-10 4.5-10 9"/><path d="M17 3c0 4.5-10 4.5-10 9s10 4.5 10 9"/><path d="M8.3 5.2h7.4M8.3 9.8h7.4M8.3 14.2h7.4M8.3 18.8h7.4"/>',
         'shipped': '<path d="M3.5 7.5L12 3l8.5 4.5v9L12 21l-8.5-4.5z"/><path d="M3.5 7.5L12 12l8.5-4.5M12 12v9"/><path d="M7.75 5.25l8.5 4.5"/>',
         'in-house': '<path d="M3.5 11L12 4l8.5 7"/><path d="M5.5 9.5V20h13V9.5"/><path d="M8.5 16.5l2.2-2.4 2.3 1.6 2.5-3.2"/>',
         'factory': '<path d="M3 20V10l5 3v-3l5 3v-3l5 3V4h3v16z"/><path d="M7 17h2M11 17h2M15 17h2"/>',
         'blind-spot': '<path d="M2.5 12s3.5-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.5 6.5-9.5 6.5S2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/><path d="M4 4l16 16"/>',
         # no, does not match: the pair to 'check' (05a, same look)
         'cross': '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
         # what the software measures in each image (04a): size, shape, brightness, texture
         'size': '<path d="M3.5 7v10M20.5 7v10M3.5 12h17M7 9l-3 3 3 3M17 9l3 3-3 3"/>',
         'shape': '<circle cx="7.5" cy="12" r="4.5"/><ellipse cx="17" cy="12" rx="3.2" ry="7.5"/>',
         'brightness': '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/>',
         'texture': '<rect x="4" y="4" width="16" height="16" rx="2.5"/><path d="M4 10l6-6M4 16L16 4M8 20L20 8M14 20l6-6"/>',
         # one protocol at every lab (06a): the same cells (03's vial), serum, dyes and protocol (03's clipboard)
         'cells': '<path d="M9 3h6M10 3v4M14 3v4"/><rect x="8" y="7" width="8" height="14" rx="2"/><path d="M8 13h8"/>',
         'serum': '<rect x="9" y="2.5" width="6" height="3" rx="1"/><path d="M9.5 5.5v2L7 10v9.5A1.5 1.5 0 0 0 8.5 21h7a1.5 1.5 0 0 0 1.5-1.5V10l-2.5-2.5v-2"/><path d="M7 14h10"/>',
         'dyes': '<path d="M9.5 3.5S4.5 9 4.5 13a5 5 0 0 0 10 0c0-4-5-9.5-5-9.5z"/><path d="M18 11s-2.6 2.9-2.6 4.8a2.6 2.6 0 0 0 5.2 0c0-1.9-2.6-4.8-2.6-4.8z"/>',
         'protocol': '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M8.5 10h7M8.5 13.5h7M8.5 17h4"/>',
         # why now (06a): animal tests, a model reading a cell image
         'animal': '<ellipse cx="11" cy="14" rx="7" ry="4.6"/><path d="M17.6 12.6l3.6 1.8-3.4 1.4"/><circle cx="13.6" cy="8.6" r="2.4"/><circle cx="15.4" cy="13" r=".8" fill="currentColor"/><path d="M4.2 15.2c-2 .6-2.4 2.8-.6 3.6 1.4.6 2.6-.2 3.8.4"/>',
         'ai-reads': '<path d="M3 8V5a2 2 0 0 1 2-2h3M16 3h3a2 2 0 0 1 2 2v3M21 16v3a2 2 0 0 1-2 2h-3M8 21H5a2 2 0 0 1-2-2v-3"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1.5"/>',
         # the certificate's rows (07b) and the batch just sent (07c, the map's pink dot in its ring)
         'count': '<circle cx="7" cy="7.5" r="3"/><circle cx="15.5" cy="5.5" r="2.5"/><circle cx="7.5" cy="16" r="3"/><path d="M15 12.5v8M19 12.5v8M13 15h8M13 18h8"/>',
         'sent': '<circle cx="12" cy="12" r="4.5" fill="currentColor"/><circle cx="12" cy="12" r="8.5"/>',
         # slide 02: how a lab checks today (search, ask by email, guess; run it or wait) and the founder's skills and record
         'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>',
         'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
         'email': '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3.5 7l8.5 6.5L20.5 7"/>',
         'run': '<path d="M8 5v14l11-7z"/>',
         'chance': '<rect x="4" y="4" width="16" height="16" rx="3.5"/><circle cx="8.6" cy="8.6" r="1.2" fill="currentColor"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/><circle cx="15.4" cy="15.4" r="1.2" fill="currentColor"/>',
         'neuron': '<circle cx="8.5" cy="8.5" r="3"/><path d="M6.4 6.4L3.5 3.5M8.5 5.5V2.5M5.5 8.5H2.5"/><path d="M10.6 10.6L18 18"/><path d="M18 18l3 .5M18 18l.5 3M18 18l2.4 2.4"/>',
         'spike': '<path d="M2.5 14.5h5.5l1.5-10.5 2.5 15 1.5-4.5h8"/>',
         'degree': '<path d="M2.5 9.5L12 5.5l9.5 4L12 13.5z"/><path d="M6.5 11.3v4.4c0 1.4 2.5 2.6 5.5 2.6s5.5-1.2 5.5-2.6v-4.4"/><path d="M21.5 9.5v5.5"/>',
         'molecule': '<path d="M9 8l4.3 2.5v5L9 18l-4.3-2.5v-5z"/><path d="M13.3 10.5l3.9-2.3 3.3 1.9"/><path d="M17.2 8.2V4.5"/>'}


def stat_tile(number, label, sub='', colour=None, dark=True, size=44, cls=''):
    """One number, one label, one line under it: the tile strip the Narcan deck uses instead of sentences."""
    bg = 'rgba(246,247,247,.06)' if dark else '#ffffff'
    ink, soft = (D_TEXT, D_SOFT) if dark else (INK, INK2)
    return (f'<div class="{cls}" style="box-sizing:border-box; padding:14px 16px 12px; border-radius:12px; background:{bg}; display:flex; flex-direction:column; gap:4px;">'
            f'<span style="{SANS} font-size:{size}px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour or ink};">{number}</span>'
            f'<span style="{SANS} font-size:19px; font-weight:600; line-height:1.25; color:{ink};">{label}</span>'
            + (f'<span style="{SANS} font-size:18px; line-height:1.3; color:{soft};">{sub}</span>' if sub else '') + '</div>')


def icon(name, colour, size=22, cls=''):
    """One icon from ICONS, as an inline SVG that takes its colour from `colour`."""
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{colour}" style="color:{colour}; flex-shrink:0;" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{" class=" + chr(34) + cls + chr(34) if cls else ""}>{ICONS.get(name) or PATH_ICONS[name]}</svg>')


PATH_ICONS = {'map': '<path d="M12 21s-6-5.5-6-10a6 6 0 0 1 12 0c0 4.5-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/>',
              'certificate': '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
              'subscriptions': '<path d="M4 8h15l-3.5-3.5M20 16H5l3.5 3.5"/>',
              'journals': '<path d="M3 5h6a3 3 0 0 1 3 3v12a2 2 0 0 0-2-2H3z"/><path d="M21 5h-6a3 3 0 0 0-3 3v12a2 2 0 0 1 2-2h7z"/>'}
PATH = [('map', 'open', 'today', 'green'), ('certificate', 'paid', 'next', 'green'), ('subscriptions', 'to the repository', 'then', 'green'),
        ('journals', 'raw images', 'raw images, every paper', 'green')]          # the pressure the standard puts on publishing


def path_strip(dark=False, tags=True, later=True, vertical=False):
    """Map, certificate, subscriptions, journals and an open end: one picture on 06 and 10 (pin and receipt match 09). The caller's row uses justify-content:space-between.
    later=False keeps only the map's 'today'; vertical stacks the steps for a side column (the caller's column spaces them)."""
    tone = {'green': D_GREEN if dark else GREEN, 'pink': D_PINK if dark else PINK}
    dim = D_DIM if dark else MUTE

    def step(name, tag, when, c):
        col = tone[c]
        icon = (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" '
                f'stroke-linejoin="round" aria-hidden="true" style="flex-shrink:0;">{PATH_ICONS[name]}</svg>')
        pill = (f'<span style="{MONO} font-size:13px; padding:2px 9px; border-radius:999px; border:1px solid {col}; color:{col};">{tag}</span>' if tags else '')
        if vertical:                                   # one line a step, in words: Map, today
            return f'<span style="{SANS} font-size:18px; line-height:1.3; color:{col};">{name.capitalize()}, <span style="color:{dim};">{when}</span></span>'
        return (f'<div style="display:flex; flex-direction:column; gap:6px; min-width:0;">'
                f'<span style="display:flex; gap:10px; align-items:center;">{icon}{label(name, col)}{pill}</span>'
                f'<span style="{MONO} font-size:13px; color:{dim}; padding-left:32px;">{when if later or name in ("map", "journals") else "&#160;"}</span></div>')
    if vertical:
        arrow = f'<span aria-hidden="true" style="{SANS} font-size:16px; line-height:14px; color:{dim}; padding-left:6px;">&#8595;</span>'
        return arrow.join(step(*p) for p in PATH) + arrow + f'<span style="{SANS} font-size:18px; line-height:14px; color:{dim}; padding-left:3px;">&#8230;</span>'
    arrow = f'<span aria-hidden="true" style="{SANS} font-size:22px; line-height:22px; color:{dim};">&#8594;</span>'
    return arrow.join(step(*p) for p in PATH) + arrow + f'<span style="{SANS} font-size:22px; line-height:22px; color:{dim};">&#8230;</span>'


def watermark(code):
    """Retired: the big faded board number was ink that carried no data. Kept so callers need not change."""
    return ''


def label(text, colour=MUTE, size=13):
    return f'<span style="{MONO} font-size:{size}px; letter-spacing:0.1em; text-transform:uppercase; color:{colour};">{text}</span>'


def text(x, y, s, size=20, fill=INK2, anchor='start', weight=400, extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" {SVG_FONT} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'


class Axes:
    """A plot area with labelled axes. Coordinates are in the SVG's own units."""

    def __init__(self, x0, y0, w, h, xlim, ylim):
        self.x0, self.y0, self.w, self.h, self.xlim, self.ylim = x0, y0, w, h, xlim, ylim

    def X(self, v):
        return self.x0 + (v - self.xlim[0]) / (self.xlim[1] - self.xlim[0]) * self.w

    def Y(self, v):
        return self.y0 + self.h - (v - self.ylim[0]) / (self.ylim[1] - self.ylim[0]) * self.h

    def frame(self, yticks, xticks, ylabel, xlabel, title=None, fmt=str, room=False):
        """room: type sized for a projected talk slide (ticks 26, axis titles 28) rather than a board read up close."""
        tick, name_size, off = (26, 28, 36) if room else (20, 22, 30)
        g = []
        if title:
            g.append(chart_title(self.x0, self.y0 - 28, title))
        g.append(f'<rect x="{self.x0}" y="{self.y0}" width="{self.w}" height="{self.h}" fill="{PANEL}"/>')
        for v in yticks:
            g.append(f'<path d="M {self.x0} {self.Y(v):.1f} L {self.x0 + self.w} {self.Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>')
            g.append(text(self.x0 - 10, self.Y(v) + 9, fmt(v), tick, MUTE, 'end'))
        for v, name in xticks:
            g.append(f'<path d="M {self.X(v):.1f} {self.y0 + self.h} L {self.X(v):.1f} {self.y0 + self.h + 8}" stroke="{MUTE}" stroke-width="2"/>')
            g.append(text(self.X(v), self.y0 + self.h + off, name, tick, MUTE, 'middle'))
        g.append(f'<path d="M {self.x0} {self.y0} L {self.x0} {self.y0 + self.h} L {self.x0 + self.w} {self.y0 + self.h}" fill="none" '
                 f'stroke="{MUTE}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
        g.append(text(self.x0 + self.w / 2, self.y0 + self.h + off + 36, xlabel, name_size, INK2, 'middle'))
        g.append(f'<g transform="translate({self.x0 - (72 if room else 62)},{self.y0 + self.h / 2:.1f}) rotate(-90)">{text(0, 0, ylabel, name_size, INK2, "middle")}</g>')
        return g


def svg(width, height, body, css_width='100%', aria=None, fit=False):
    """An inline chart. With fit, it scales to the height of its card as well as the width."""
    role = f' role="img" aria-label="{aria}"' if aria else ' aria-hidden="true"'
    size = 'flex:1 1 0; min-width:0; min-height:0; width:100%; height:100%;' if fit else f'width:{css_width}; height:auto;'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet"{role} '
            f'style="display:block; {size}">' + ''.join(body) + '</svg>')


def install(deck, tid, css, body):
    """Replace one slide's template in the deck, or append it after the last template."""
    block = f'<template id="{tid}"><style>{css}\n{HOST_PAUSE}</style>{body}</template>'
    m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
    if m:
        return deck[:m.start()] + block + deck[m.end():]
    last = list(re.finditer(r'</template>', deck))[-1]
    return deck[:last.end()] + '\n' + block + deck[last.end():]


def set_meta(deck, name, steps, after=None):
    """Set one slide's entry in the deck's META list; add it after another entry if absent."""
    m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S)
    meta = json.loads(m.group(1))
    names = [e['name'] for e in meta]
    if name in names:
        meta[names.index(name)]['steps'] = steps
    else:
        meta.insert(names.index(after) + 1 if after else len(meta), {'name': name, 'steps': steps})
    return deck[:m.start(1)] + json.dumps(meta) + deck[m.end(1):], [e['name'] for e in meta]
