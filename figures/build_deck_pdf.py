"""Write a print page for the deck: one 1280x720 page per slide state, animations settled.
Chrome then prints it to datum-line-deck.pdf. Slides with click states get one page each.

Usage:  python figures/build_deck_pdf.py index.html OUT.html
        chrome --headless --print-to-pdf=datum-line-deck.pdf --no-pdf-header-footer OUT.html
"""
import json
import re
import sys

src, out = sys.argv[1], sys.argv[2]
t = open(src).read()
links = '\n'.join(re.findall(r'<link[^>]*>', re.search(r'<head>(.*?)</head>', t, flags=re.S).group(1)))
meta = json.loads(re.search(r'const META=(\[.*?\]);', t, flags=re.S).group(1))
templates = re.findall(r'<template id="t\d+">.*?</template>', t, flags=re.S)
assert len(templates) == len(meta)

pages = []
for i, m in enumerate(meta):
    states = len(next(iter(m['steps'].values()))) if m['steps'] else 1
    pages += [(i, s) for s in range(states)]

page = f'''<!doctype html><html><head><meta charset="utf-8"><title>Datum Line</title>{links}
<style>@page {{ size: 1280px 720px; margin: 0; }} html, body {{ margin: 0; background: #fff; }}
.pg {{ width: 1280px; height: 720px; overflow: hidden; page-break-after: always; break-after: page; }}</style></head><body>
{''.join(templates)}
<script>
const META = {json.dumps(meta)};
const PAGES = {json.dumps(pages)};
// settle every animation and transition at its end state; keep shadows and gradients as on screen
const SETTLE = '*{{animation-delay:0s!important;animation-duration:.001s!important;animation-iteration-count:1!important;transition:none!important}}';
for (const [i, s] of PAGES) {{
  const host = document.createElement('div'); host.className = 'pg in';
  const root = host.attachShadow({{mode: 'open'}});
  root.appendChild(document.getElementById('t' + i).content.cloneNode(true));
  const st = document.createElement('style'); st.textContent = SETTLE; root.appendChild(st);
  const steps = META[i].steps;
  if (steps) {{
    const el = root.querySelector('[class*="step-"]');
    el.className = el.className.replace(/step-\\d/, 'step-' + s);
    for (const k in steps) root.querySelectorAll('[data-h="' + k + '"]').forEach(e => e.textContent = steps[k][s]);
  }}
  document.body.appendChild(host);
}}
</script></body></html>'''
open(out, 'w').write(page)
print(len(pages), 'pages:', ' '.join(f'{i + 1}.{s}' if meta[i]['steps'] else str(i + 1) for i, s in pages))
