"""Slide notes: every slide's fine print, taken off the slides and kept here, so the slides carry only what the room needs.

10 Nov 2026 (Kat: "the text figure legends and fine print on the bottom of the slides is reading busy. lets save this info for
slide notes and/or script. try to keep the slides lowest essential text"). The builders still write each legend, source line
and board footnote into the deck, marked as the reader's layer (.pdf, .pdfv) or a note (.note); the stage and the PDF hide
them, D in the web deck shows them in place. This script reads them back out of index.html and writes:

  private/slide-notes.html      one section per slide or board: its headline, then its fine print, word for word
  private/speaker-script.html   a "Fine print, off the slide." paragraph under each talk slide (replaced on every run)

Usage:  python figures/build_notes.py [index.html]        (from the repository root; private/ is ignored by git)
"""
import html
import json
import os
import re
import sys

deck = open(sys.argv[1] if len(sys.argv) > 1 else 'index.html').read()
meta = json.loads(re.search(r'const META=(\[.*?\]);', deck, flags=re.S).group(1))
templates = re.findall(r'<template id="t\d+">(.*?)</template>', deck, flags=re.S)
assert len(templates) == len(meta)

VOID = {'br', 'img', 'hr', 'input', 'meta', 'link', 'source', 'wbr', 'path', 'circle', 'rect', 'line', 'stop', 'use', 'image'}


def text(fragment):
    fragment = re.sub(r'<br\s*/?>', ' ', fragment)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


def marked(tpl):
    """The text of every element whose class marks it as fine print (pdf, pdfv, note), outermost only, in page order."""
    tpl = re.sub(r'<style>.*?</style>|<script>.*?</script>|data:[a-z/+]+;base64,[A-Za-z0-9+/=]+', '', tpl, flags=re.S)
    out, i = [], 0
    opener = re.compile(r'<([a-z][a-z0-9]*)\b[^>]*\bclass="(?:[^"]*\s)?(?:pdf|pdfv|note)(?:\s[^"]*)?"[^>]*>', re.I)
    while True:
        m = opener.search(tpl, i)
        if not m:
            return out
        tag, depth, j = m.group(1).lower(), 1, m.end()
        tok = re.compile(r'<(/?)([a-z][a-z0-9]*)\b[^>]*?(/?)>', re.I)
        while depth and (t := tok.search(tpl, j)):
            name = t.group(2).lower()
            if name == tag and name not in VOID and not t.group(3):
                depth += -1 if t.group(1) else 1
            j = t.end()
        out.append(text(tpl[m.end():t.start() if t else len(tpl)]))
        i = j


def headline(tpl):
    h = re.search(r'<h[12][^>]*>(.*?)</h[12]>', tpl, flags=re.S)
    return text(h.group(1)) if h else ''


sections = []
for i, (m, tpl) in enumerate(zip(meta, templates)):
    seen, notes = set(), []
    for n in marked(tpl):
        n = n.strip(' ,;·')
        if len(n) < 12 or n in seen or any(n in k for k in seen):      # inline crumbs ("[7]", ", ") belong to a longer note
            continue
        seen.add(n); notes.append(n)
    code = f'{i + 1:02d}' if i < 10 else m['name']
    sections.append((i, code, m['name'], headline(tpl), notes))

css = ("body{margin:0;padding:32px 16px 64px;background:#fff;color:#14171a;font-family:Archivo,'Helvetica Neue',Helvetica,sans-serif;"
       "font-size:16px;line-height:1.5}main{max-width:860px;margin:0 auto}h1{font-size:28px;letter-spacing:-0.02em;margin:0 0 4px}"
       ".lead{color:#666e72;margin:0 0 24px}section{padding:16px 0;border-top:1px solid #dfe3e5}h2{font-size:18px;margin:0 0 8px}"
       ".n{font-family:'IBM Plex Mono',Menlo,monospace;font-weight:400;color:#be1e74;margin-right:8px}"
       "li{font-family:'IBM Plex Mono',Menlo,monospace;font-size:13px;line-height:1.55;color:#454c50;margin:0 0 6px}"
       ".none{color:#949c9f;font-size:14px}")
body = ''.join(f'<section><h2><span class="n">{code}</span>{html.escape(name)}: {html.escape(h)}</h2>'
               + (f'<ul>{"".join(f"<li>{html.escape(n)}</li>" for n in notes)}</ul>' if notes else '<p class="none">no fine print</p>')
               + '</section>' for _, code, name, h, notes in sections)
os.makedirs('private', exist_ok=True)
open('private/slide-notes.html', 'w').write(
    f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
    f'<title>Datum Line · Slide notes</title><style>{css}</style></head><body><main><h1>Slide notes</h1>'
    f'<p class="lead">Every legend, source line and footnote taken off the slides, word for word, slide by slide. Written from '
    f'index.html by figures/build_notes.py; D in the web deck shows the same text in place.</p>{body}</main></body></html>')

# the speaker script: one paragraph under each talk slide, replaced on every run
path = 'private/speaker-script.html'
if os.path.exists(path):
    s = open(path).read()
    KEY = 'Fine print, off the slide.'
    s = re.sub(r'<p><strong>' + re.escape(KEY) + r'</strong>.*?</p>\n?', '', s, flags=re.S)
    heads = list(re.finditer(r'<h3><span class="sn">(\d\d)</span>', s))
    for k in reversed(range(len(heads))):
        code = heads[k].group(1)
        sec = next((x for x in sections if x[1] == code), None)
        if not sec or not sec[4]:
            continue
        end = heads[k + 1].start() if k + 1 < len(heads) else (s.find('</main>', heads[k].end()) if '</main>' in s[heads[k].end():] else len(s))
        para = f'<p><strong>{KEY}</strong> ' + ' &#183; '.join(html.escape(n) for n in sec[4]) + '</p>\n'
        s = s[:end] + para + s[end:]
    open(path, 'w').write(s)

print(f'notes: {sum(len(x[4]) for x in sections)} items over {sum(1 for x in sections if x[4])} of {len(sections)} slides '
      f'-> private/slide-notes.html' + (', private/speaker-script.html' if os.path.exists(path) else ''))
