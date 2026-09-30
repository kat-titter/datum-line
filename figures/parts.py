"""Shared pieces for the slide builders: palette, type, chrome and chart axes.

Every builder in this folder writes whole slides from results/*.json, so running a builder
twice gives the same deck. Nothing on an evidence slide is typed by hand.
"""
import json
import re

SANS = "font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif;"
MONO = "font-family: 'IBM Plex Mono', Menlo, monospace;"
SVG_FONT = "font-family=\"'Helvetica Neue', Helvetica, Arial, sans-serif\""

PINK, GREEN, INK, INK2, MUTE, FAINT, GRID, PANEL, PAPER = (
    '#be1e74', '#0f8f6c', '#14171a', '#454c50', '#666e72', '#949c9f', '#d3d8da', '#eceeef', '#f6f7f7')
D_PINK, D_GREEN, D_TEXT, D_SOFT, D_DIM, D_BG = '#ef74ad', '#3fe0a0', '#f6f7f7', '#c9cfd1', '#949c9f', '#14171a'
PALE_PINK = '#e9a3c6'
N_TALK = 10

LIGHT_BG = ('background:#f6f7f7; background-image: radial-gradient(60% 50% at 100% 0%, rgba(190,30,116,0.07), transparent 70%), '
            'radial-gradient(50% 45% at 0% 100%, rgba(15,143,108,0.08), transparent 70%);')
DARK_BG = ('background:#14171a; background-image: radial-gradient(55% 55% at 100% 0%, rgba(239,116,173,0.16), transparent 70%), '
           'radial-gradient(50% 50% at 0% 100%, rgba(63,224,160,0.13), transparent 70%);')
CARD = ('box-sizing:border-box; background:#ffffff; border-radius:14px; '
        'box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 12px 30px rgba(20,23,26,0.09);')
CARD_ON_DARK = ('box-sizing:border-box; background: linear-gradient(#f6f7f7, #f6f7f7) padding-box, linear-gradient(90deg, #ef74ad, #3fe0a0) border-box; '
                'border-top: 3px solid transparent; border-radius: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.30), 0 24px 60px rgba(0,0,0,0.45);')

BASE_CSS = ''':host{display:block;width:1280px;height:720px}
    a { color: #be1e74; } a:hover { color: #8e1657; }
    @keyframes rise { from { opacity:0; transform: translateY(8px);} to { opacity:1; transform:none;} }
    @keyframes fade { to { opacity: 1; } }
    @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
    .r { opacity:0; animation: rise .45s cubic-bezier(.2,.8,.2,1) forwards; }
    .f { opacity:0; animation: fade .5s ease-out forwards; }
    .bar { transform-origin: left center; transform-box: fill-box; transform: scaleX(0); animation: grow .7s cubic-bezier(.2,.8,.2,1) forwards; }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } .r, .f { opacity: 1; } .bar { transform: none; } }
    @media print { * { box-shadow: none !important; } [style*="radial-gradient"] { background-image: none !important; } }
    h1 span, h2 span { white-space: nowrap; }
'''
HOST_PAUSE = ':host(:not(.in)) *{animation-play-state:paused!important}'


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


def header(left, right, dark=False, right_html=None):
    c1, c2 = (D_DIM, D_GREEN) if dark else (MUTE, GREEN)
    r = right_html or f'<span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{c2};">{right}</span>'
    return (f'<div style="display:flex; justify-content:space-between; align-items:baseline;">'
            f'<span style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:{c1};">{left}</span>{r}</div>')


def watermark(code):
    return (f'<div aria-hidden="true" style="position:absolute; right:-18px; top:-70px; z-index:-1; {SANS} font-size:280px; font-weight:700; '
            f'letter-spacing:-0.06em; line-height:1; color:#edf0f1; pointer-events:none;">{code}</div>')


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

    def frame(self, yticks, xticks, ylabel, xlabel, title=None, fmt=str):
        g = []
        if title:
            g.append(text(self.x0, self.y0 - 28, title, 22, MUTE, extra='letter-spacing="2.2"'))
        g.append(f'<rect x="{self.x0}" y="{self.y0}" width="{self.w}" height="{self.h}" fill="{PANEL}"/>')
        for v in yticks:
            g.append(f'<path d="M {self.x0} {self.Y(v):.1f} L {self.x0 + self.w} {self.Y(v):.1f}" stroke="{GRID}" stroke-width="2"/>')
            g.append(text(self.x0 - 10, self.Y(v) + 7, fmt(v), 20, MUTE, 'end'))
        for v, name in xticks:
            g.append(f'<path d="M {self.X(v):.1f} {self.y0 + self.h} L {self.X(v):.1f} {self.y0 + self.h + 8}" stroke="{MUTE}" stroke-width="2"/>')
            g.append(text(self.X(v), self.y0 + self.h + 30, name, 20, MUTE, 'middle'))
        g.append(f'<path d="M {self.x0} {self.y0} L {self.x0} {self.y0 + self.h} L {self.x0 + self.w} {self.y0 + self.h}" fill="none" '
                 f'stroke="{MUTE}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
        g.append(text(self.x0 + self.w / 2, self.y0 + self.h + 62, xlabel, 22, INK2, 'middle'))
        g.append(f'<g transform="translate({self.x0 - 62},{self.y0 + self.h / 2:.1f}) rotate(-90)">{text(0, 0, ylabel, 22, INK2, "middle")}</g>')
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
