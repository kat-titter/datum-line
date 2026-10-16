"""One word for one thing, figures numbered in order, one pager, pointers to the appendix,
and little text: legends only under scientific figures, one line each. Detail lives in the
speaker script.

Applied after the slides are written. Every edit is a no-op once made, so it can be re-run.
"""
import base64
import json
import os
import re

import parts
import slide04
from parts import MONO, SANS, MATH

OLD_SVG_FONT = "font-family=\"'Helvetica Neue', Helvetica, Arial, sans-serif\""   # the hand-built charts' face before Archivo; old strings only
BADGE = "<span style=\"font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif; font-size: 22px; font-weight: 700; letter-spacing: -0.02em; color: #be1e74; white-space: nowrap;\">"
REF = "<span style=\"font-family: 'IBM Plex Mono', Menlo, monospace; font-size: 13px; color: #666e72; white-space: nowrap;\">"
BODY = "<span style=\"font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif; font-size: 15px; line-height: 1.35; color: #454c50;\">"
HALO = ' stroke="#eceeef" stroke-width="6" stroke-linejoin="round" paint-order="stroke"'     # a label's halo in the colour of the plot panel
TEAM_OLD = ('<div style="display:flex; flex-direction:column; gap:4px; padding-top:6px; border-top:1px solid #e4e8e9;">'
            '<span style="' + MONO + ' font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:#666e72;">Team</span>'
            '<span style="' + SANS + ' font-size:15px; line-height:1.35; color:#14171a;">one founder &#183; looking for a technical co-founder</span>'
            '<span style="' + SANS + ' font-size:15px; line-height:1.35; color:#666e72;">collaborators in industry</span></div>')
ROLE_V1 = ('<div style="display:flex; flex-direction:column; gap:4px; padding-top:6px; border-top:1px solid #e4e8e9;">'
        '<span style="' + MONO + ' font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:#666e72;">Role</span>'
        '<span style="' + SANS + ' font-size:15px; line-height:1.35; color:#14171a;">not the CEO &#183; <span style="white-space:nowrap;">I&#8217;d build the science</span></span>'
        '<span style="' + SANS + ' font-size:15px; line-height:1.35; color:#666e72;">looking for its leader <span style="white-space:nowrap;">and its home</span></span></div>')
ROLE = ('<div style="display:flex; flex-direction:column; gap:4px; padding-top:6px; border-top:1px solid #e4e8e9;">'   # two statements, two lines
        '<span style="' + MONO + ' font-size:13px; letter-spacing:0.1em; text-transform:uppercase; color:#666e72;">Role</span>'
        '<span style="' + SANS + ' font-size:15px; line-height:1.35; color:#14171a;">not the CEO<br>I&#8217;d build the science</span>'
        '<span style="' + SANS + ' font-size:15px; line-height:1.35; color:#666e72;">looking for its leader <span style="white-space:nowrap;">and its home</span></span></div>')

E1 = json.load(open('results/e1.json'))['all_sources']                  # numbers the hand-built boards quote, read from results
CENTRED = json.load(open('results/e1-redteam.json'))['tests']['plate_centred']['balanced_accuracy']
A2_LEDE = ("Every well: <span style=\"" + MATH + " color: #14171a;\">e &#8712; <span style=\"font-style:normal;\">&#8477;</span><sup style=\"font-size: 13px;\">3773</sup></span>, "
           "z-scored across the field.<br>Each result: a difference of means or a held-out classifier.")

A3_NOTE = "<span style=\"font-family: 'IBM Plex Mono', Menlo, monospace; font-size: 13px; line-height: 1.45; color: #666e72; margin-top: auto;\">"
DARK = {3, 4, 5, 6}                    # template indices of the dark talk slides: the map, controls, data, product
WORDS = {                              # template id -> [(old, new)]
    't1': [('color:#14171a;">One founder today.<br>Looking for a technical co-founder.</span>', 'color:#14171a;">one founder &#183; looking for a technical co-founder</span>'),
           ('Five labs. One <span style="color:#be1e74; font-weight:600;">unanswered question.</span>', 'five labs &#183; one <span style="color:#be1e74; font-weight:600;">unanswered question</span>'),
           ('Five labs, and the same <span style="color:#be1e74; font-weight:600;">unanswered question</span> at every bench. It made the science slow and wrong.', 'five labs &#183; one <span style="color:#be1e74; font-weight:600;">unanswered question</span>'),
           ('text-decoration:none;">macrofluidic.me/resume</a>' + TEAM_OLD, 'text-decoration:none;">macrofluidic.me/resume</a>' + ROLE),   # the vision is meant to find its own leader
           (ROLE_V1, ROLE),
           (ROLE, ''),                    # said in the script, not written: slide 10's 'a leader' and A21 carry it
           # 02a: the script says it; the timeline and the papers show it
           ('\n      <p class="row" style="margin:0 0 4px; ' + SANS + ' font-size:19px; line-height:1.38; color:#454c50; max-width:470px; animation-delay:0.08s;">five labs &#183; one '
            '<span style="color:#be1e74; font-weight:600;">unanswered question</span></p>', ''),
           ('>founding MTS &#183; hepatocytes at scale</span>', '>founding MTS</span>'),
           ('>neuroscience assays &#183; productionization</span>', '>neuroscience assays</span>'),          # one line beside the papers
           ('>Xenopus oocytes &#183; GABA<sub style="font-size:13px; line-height:0;">A</sub> receptors</span>', '>Xenopus oocytes</span>'),
           ('color:#949c9f;">Synthetic Neurobiology</span>', 'color:#949c9f;">&#x200B;</span>'),   # each blank spelled once: apply() skips a result already present
           ('color:#949c9f;">Neuroscience</span>', 'color:#949c9f;">&#X200B;</span>'),
           ('>Broad Institute &#183; MIT &#183; AbbVie &#183; EMBL-EBI<br>', '>Broad Institute &#183; EMBL-EBI<br>'),   # MIT and AbbVie are logos above
           # 02a: graduation is a step like the others; the link sits under the photo, not alone at the bottom
           ('<div style="width:12px; height:12px; border-radius:50%; background:#f6f7f7; border:2px solid #be1e74; box-sizing:border-box; transform:translateY(2px);"></div>',
            '<div aria-hidden="true" style="width:12px; height:12px; border-radius:50%; background:#be1e74; transform:translateY(2px);"></div>'),   # unique, or apply() skips it
           ('<div style="flex-grow:1;"></div>\n      <a href="https://www.macrofluidic.me/resume"', '<a class="cv" href="https://www.macrofluidic.me/resume"'),
           # 02b: "normal" is relative, so it is quoted; the benches get symbols
           ('Do my cells<br><span style="color:#be1e74;">look normal?</span></h2>', 'Do my cells<br><span style="color:#be1e74;">look &#8220;normal&#8221;?</span></h2>'),
           ('asked at five benches<br>answered at none', 'asked @ five benches<br>&#8230; answered @ none'),
           ('<div style="width:384px; flex-shrink:0; display:flex; flex-direction:column; gap:11px;">',
            '<div style="width:412px; flex-shrink:0; display:flex; flex-direction:column; gap:10px;">'),   # nine papers, one line of detail each
           ('font-size:15px; line-height:1.35; color:#666e72;">Collaborators in industry.</span>', 'font-size:15px; line-height:1.35; color:#666e72;">collaborators in industry</span>'),
           ('uppercase; color:#666e72;">02 &#183; Founder</span>', 'uppercase; color:#666e72;">02</span>'),
           ('color:#0f8f6c;">Datum Line &#183; San Francisco</span>', 'color:#0f8f6c;" data-h="tag">Founder</span>'),
           ('color:#0f8f6c;" data-h="tag">Founder</span>', 'color:#0f8f6c;" data-h="tag">Background</span>'),   # not running it: the vision looks for its own leader
           (f'<span data-h="tag" style="{MONO} font-size:14px; letter-spacing:0.1em; text-transform:uppercase; color:#0f8f6c;">The question</span>', ''),
           ('box-sizing:border-box; padding:52px 64px 48px;', 'box-sizing:border-box; padding:52px 56px 80px;'),
           ('padding:0 64px;', 'padding:0 56px;'),
           ('right:64px; bottom:16px; z-index:6;', 'right:56px; bottom:44px; z-index:6;'),
           ('line-height:0.96; color:#14171a;">&#8220;Do my cells', 'line-height:0.96; color:#14171a;">Do my cells'),
           ('look normal?</span>&#8221;</h2>', 'look normal?</span></h2>'),
           ('>asked at five benches &#183; answered at none<', '>asked at five benches<br>answered at none<'),
           ('background:#be1e74; -webkit-mask:', 'background:#454c50; -webkit-mask:'),                                                   # five logos grey
           ('alt="Massachusetts General Hospital" style="display:block; height:30px;', 'alt="Massachusetts General Hospital" style="display:block; height:24px; filter:grayscale(1);'),
           ('width:112px; height:21px;', 'width:112px; height:24px;'),
           ('>Xenopus oocytes &#183; GABA<sub>A</sub> receptors</span>', '>Xenopus oocytes &#183; GABA<sub style="font-size:13px; line-height:0;">A</sub> receptors</span>'),
           ('display:flex; flex-direction:column; gap:14px;"><div class="row"', 'display:flex; flex-direction:column; gap:29px;"><div class="row"'),
           ('bottom:-15px; width:2px;', 'bottom:-30px; width:2px;'),                                                                     # 5 connectors
           ('background:linear-gradient(90deg,#be1e74,#0f8f6c);"></div>\n      <a href', 'background:linear-gradient(90deg,#be1e74,#0f8f6c);"></div><div style="flex-grow:1;"></div>\n      <a href'),
           ('font-weight:600; line-height:1.35; color:#be1e74;">Broad Institute &#183; MIT &#183; AbbVie &#183; EMBL-EBI &#183; HESI &#183; Bayer &#183; University of Cambridge &#183; Uppsala University',
            'font-weight:500; line-height:1.35; color:#454c50;">Broad Institute &#183; MIT &#183; AbbVie &#183; EMBL-EBI<br>HESI &#183; Bayer &#183; Cambridge &#183; Uppsala'),
           ('color:#949c9f;">San Francisco</span>', 'color:#949c9f;">&#8203;</span>'),          # zero-width space keeps the row baseline;
           ('color:#949c9f;">South San Francisco</span>', 'color:#949c9f;">&#x200b;</span>'),   #   the two spellings differ on purpose (apply() skips a pair whose new text exists)
           ('<div style="width:12px; height:12px; border-radius:50%; background:#be1e74; transform:translateY(2px);"></div>\n      <span style="' + MONO + ' font-size:14px; color:#666e72; white-space:nowrap;">2017</span>',
            '<div style="width:12px; height:12px; border-radius:50%; background:#f6f7f7; border:2px solid #be1e74; box-sizing:border-box; transform:translateY(2px);"></div>\n      <span style="' + MONO + ' font-size:14px; color:#666e72; white-space:nowrap;">2017</span>'),  # the degree is a hollow ring
           ('font-size:50px; font-weight:700; letter-spacing:-0.035em;', 'font-size:44px; font-weight:700; letter-spacing:-0.035em;')],
    't26': [('Across the 13 JUMP sites.', 'Across the 13 JUMP labs.')],
    't9': [('3-site proof, then the set', '3-lab proof, then the set')],
    't10': [('Every number traces to results/e1, e1b, e2 or a numbered reference', 'Every number traces to a file in results/ or a numbered reference'),
            ('padding:52px 56px 46px; display:flex; flex-direction:column; gap:20px;', 'padding:52px 56px 44px; display:flex; flex-direction:column; gap:14px;'),
            ('font-size:42px; font-weight:600; letter-spacing:-0.03em; line-height:1.05;', 'font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05;'),
            ('width:520px; flex-shrink:0;">The rest,', 'width:371px; flex-shrink:0;">The rest,'),
            ('<div style="display:flex; gap:40px; align-items:baseline;"><h2', '<div style="display:flex; gap:28px; align-items:baseline;"><h2'),
            ('font-size:18px; line-height:1.4; color:#666e72; flex-grow:1;">Find the question, jump to the board. Every number traces to a file in results/ or a numbered reference; pending work says pending.',
             'font-size:19px; line-height:1.4; color:#666e72; flex-grow:1;">Every number traces to results/ or a numbered reference.<br>Pending work says pending.'),
            ('Every number traces to results/ or a numbered reference.<br>Pending work says pending.', 'Every number comes from the code here or a cited source.<br>Unfinished work is marked pending.')],
    't11': [('>site</text>', '>lab</text>'),
            ('Whole site off: nobody in the building can tell.', 'Whole lab off: nobody inside it can tell.'),
            ('the nesting of well, plate, batch, site and field', 'the nesting of well, plate, batch, lab and field'),
            ('or a whole institution.', 'or a whole lab.'),
            ('compound plate (source_2, 1053601756)', 'compound plate (lab 2, 1053601756)'),
            ('font-weight: 500;">Fig. 2</span>', 'font-weight: 500;">Fig. A1</span>'),
            ('flex-grow: 1;">Every result is test minus control, on the same plate. But a whole plate can be off, or a whole batch, or a whole lab. A control only sees inside its own box.</p>',
             'flex-grow: 1;">A control only sees inside its own box.</p>'),
            ('<span style="color: #14171a;">So a control only sees inside its own box.</span> If the plate is sick, so is the control. Then how would anyone know?',
             'If the plate is sick, so is the control.<br>Then how would anyone know?'),
            ('padding: 12px 18px; flex-direction: column; gap: 8px; flex-direction: column; gap: 6px;', 'padding: 12px 18px; flex-direction: row; align-items: center; gap: 16px;'),
            ('>A HEALTHY PLATE<', '>HEALTHY PLATE<'), ('>A PLATE WHERE EVERYTHING DRIFTED<', '>DRIFTED PLATE<'),
            ('>control</text>', '>ctrl</text>'), ('>after referencing</text>', '>test &#8722; ctrl</text>'),
            ('viewBox="72 44 1520 606"', 'viewBox="72 44 1560 606"'),
            ('<svg x="72" y="372" width="1520" height="278" viewBox="72 372 1520 278">', '<svg x="72" y="372" width="1560" height="278" viewBox="72 372 1560 278">'),
            ('<text x="772.0" y="464.4"', '<text x="766.0" y="464.4"'),
            ('<rect x="72" y="44" width="1520" height="606" fill="#f6f7f7"></rect>', '<rect x="72" y="44" width="1520" height="606" fill="none"></rect>'),
            ('padding: 12px 22px; display: flex; flex-direction: column; gap: 4px; flex-shrink: 0;', 'padding: 12px 22px; display: flex; flex-direction: column; gap: 4px; flex-shrink: 0; width: 340px;'),
            ("display: flex; gap: 28px; align-items: baseline; font-family: 'IBM Plex Mono', Menlo, monospace; font-style: italic; font-size: 22px;",
             "display: flex; flex-direction: column; gap: 2px; " + MATH + " font-size: 22px;"),
            ("<span style=\"font-family: 'IBM Plex Mono', Menlo, monospace; font-style: italic; font-size: 16px; color: #be1e74;\">s</span>, the plate&#8217;s state, cancels from the number. Never from the cells.",
             "<span style=\"" + MATH + " font-size: 16px; color: #be1e74;\">s</span> &#183; the plate&#8217;s state &#183; cancels from the number, never from the cells"),
            ('Fig. A1</span> Where a control sits, and what it can see. Left, a real 384-well JUMP compound plate (lab 2, 1053601756): 32 DMSO, 32 positive, 320 compound wells. Right, schematic cells and traces, and the nesting of well, plate, batch, lab and field. No measurements shown.',
             'Fig. A1</span> &#183; left: JUMP plate 1053601756, lab 2 &#183; right: schematic, no measurements'),
            ('transform: translateY(1px);"></span>compounds 320</span>', 'transform: translateY(1px);"></span>test 320</span>'),
            ("<span style=\"font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif; font-size: 15px; line-height: 1.4; color: #454c50;\">The pink wells are the plate&#8217;s zero: 32 of 384, near the edge by design.</span>", ''),
            *[(f'<text x="{x}" y="56" {OLD_SVG_FONT} font-size="20" font-weight="400" fill="#666e72" text-anchor="middle" letter-spacing="0">{n}</text>', '')
              for x, n in (('88.0', '1'), ('116.0', '2'), ('704.0', '23'), ('732.0', '24'))],
            ('padding: 52px 56px 48px; display: flex; flex-direction: column; gap: 16px;', 'padding: 52px 56px 44px; display: flex; flex-direction: column; gap: 14px;'),
            ('z-index: 0; overflow: hidden;">', 'z-index: 0; overflow: hidden;">' + parts.watermark('A1')),
            ('font-size: 46px; font-weight: 600; letter-spacing: -0.028em; line-height: 1.05; color: #14171a; width: 540px;', 'font-size: 44px; font-weight: 600; letter-spacing: -0.028em; line-height: 1.05; color: #14171a; width: 560px;'),
            ('font-size: 13px; letter-spacing: 0.11em;', 'font-size: 14px; letter-spacing: 0.1em;'),                                     # header spans (only they use 0.11em)
            ('text-transform: uppercase; color: #be1e74;">The title, meant literally', 'text-transform: uppercase; color: #0f8f6c;">The title, meant literally'),
            # plain words: the headline is the board's point, the maths is spoken in words
            ('flex-shrink: 0;">There is no control well.</h2>', 'flex-shrink: 0;">Sick plate, sick control.</h2>'),
            ('color: #0f8f6c;">The title, meant literally', 'color: #0f8f6c;">one real plate &#183; one schematic'),
            ('flex-grow: 1;">A control only sees inside its own box.</p>', 'flex-grow: 1;">Controls sit on the same plate as the tests.</p>'),
            ('color: #be1e74;">If the plate is sick, so is the control.<br>Then how would anyone know?</div>', 'color: #be1e74;">Seeing a sick plate takes a view from outside it.</div>'),
            # controls dark on the plate as in the cartoon: untreated dark, known effect light; the first swap runs once, as #949c9f is new to t11
            ('r="10.5" fill="#454c50"/>', 'r="10.5" fill="#949c9f"/>'), ('r="10.5" fill="#be1e74"/>', 'r="10.5" fill="#454c50"/>'),
            ('background: #be1e74;  margin-right: 6px; transform: translateY(1px);"></span>DMSO 32', 'background: #454c50;  margin-right: 6px; transform: translateY(1px);"></span>untreated 32'),
            ('background: #454c50;  margin-right: 6px; transform: translateY(1px);"></span>positive 32', 'background: #949c9f;  margin-right: 6px; transform: translateY(1px);"></span>known effect 32'),
            ('>DRIFTED PLATE<', '>SICK PLATE<'), ('fill="#0f8f6c">field</text>', 'fill="#0f8f6c">all labs</text>'),
            ('<span>x<sub style="font-size: 0.62em;">test</sub> = &#956; + <span class="s" style="color: #be1e74;">s</span> + &#964;(<span class="s" style="color: #be1e74;">s</span>)</span>',
             '<span>test = normal + <span class="s" style="color: #be1e74;">plate</span> + effect</span>'),
            ('<span>x<sub style="font-size: 0.62em;">ctrl</sub> = &#956; + <span class="s" style="color: #be1e74;">s</span></span>',
             '<span>control = normal + <span class="s" style="color: #be1e74;">plate</span></span>'),
            ('<span>&#916; = &#964;(<span class="s" style="color: #be1e74;">s</span>)</span>', '<span>difference = effect on this <span class="s" style="color: #be1e74;">plate</span></span>'),
            ('<span style="' + MATH + ' font-size: 16px; color: #be1e74;">s</span> &#183; the plate&#8217;s state &#183; cancels from the number, never from the cells',
             '<span style="color: #be1e74;">plate</span> cancels from the number, never from the cells')],
    't12': [('V<sub>site</sub>', 'V<sub>lab</sub>'),
            ('Microscope model separates from site because models are shared across sites.', 'Microscope model separates from lab because models are shared across labs.'),
            (BADGE + "[e5]</span>", REF + "pending</span>"),
            ("results/e1, e1b, e5, e6 &#183; [1] Ewald et al. 2026", "results/e1, e1-redteam, e1b, e6 &#183; e5 pending &#183; [1] Ewald et al. 2026"),
            ("font-family: 'IBM Plex Mono', Menlo, monospace; font-style: italic; font-size: 21px;", MATH + " font-size: 22px;"),
            ("font-family: 'IBM Plex Mono', Menlo, monospace; font-style: italic; font-size: 18px;", MATH + " font-size: 20px;"),
            ("e = &#966;(image); &#966; &#8712; {CellProfiler, CNN, ViT}</div>", "e = &#966;(image)</div>"),
            ("Which &#966; barely matters: the three performed similarly on hepatocytes. The extractor is not the asset.", "&#966; &#8712; {CellProfiler, CNN, ViT}: similar on hepatocytes.<br>Extractor is not the asset."),
            ("f : e &#8594; lab, held out by plate</div>", "f : e &#8594; lab</div>"),
            ("Logistic regression, L2, five folds. Balanced accuracy, chance 1/11. Permuted labels 9.3%. Without the 1536-well labs: 100.0%.",
             "L2 logistic regression, five folds held out by plate.<br>Chance 1 in 11 &#183; permuted labels 9.3%<br>Without 1536-well labs: 99.98%"),
            ("&#8214; E[e | plate] &#8722; E[e | field, c] &#8214;", "&#8214;E[e | plate] &#8722; E[e | field, c]&#8214;"),
            ("Difference of two means in units of the field&#8217;s spread, conditioned on c. Its direction is what moved; &#8722;d is the way back.",
             "Difference of means, in units of the field&#8217;s spread.<br>Its direction is what moved; &#8722;d is the way back."),
            ("V<sub>lab</sub> + V<sub>batch</sub>", "V<sub>lab</sub> +<br>V<sub>batch</sub>"),
            ("Nested, so shares sum to one. Microscope model separates from lab because models are shared across labs.", "Nested: shares sum to one.<br>Microscope models span labs, so the two separate."),
            ("e<sub>&#8869;</sub> = e &#8722; &#202;[e | c], then re-run f</div>", "e<sub>&#8869;</sub> = e &#8722; &#202;[e | c]</div>"),
            ("Remove only what you know is instrument, keep what may be biology. Remove each plate&#8217;s own control mean and f falls to 24%.",
             "c: known instrument variables only; then re-run f.<br>Plate-centred alone: f falls to 24%."),
            ("&#8214;), f bounded<br>", "&#8214;)<br>"),
            ("g: e&#8242; &#8594; label, e&#8242; aligned to the reference before comparison</div>", "g : e&#8242; &#8594; label</div>" + BODY + "f bounded &#183; e&#8242; aligned to the reference first</span>"),
            ("font-size: 15px; line-height: 1.45; color: #be1e74;\">Same vector, two questions. Discovery wants invariance to the lab: <span style=\"color: #0f8f6c;\">align first</span>. QC wants the lab coordinate: <span style=\"color: #be1e74;\">never align it away</span>.</div>",
             "font-size: 15px; line-height: 1.45; color: #454c50;\"><span style=\"color: #0f8f6c;\">discovery</span> &#183; align the lab away first<br><span style=\"color: #be1e74;\">QC</span> &#183; keep the lab coordinate, never align it away</div>"),
            (">Six operations on one embedding.</h2>", ">Six operations, one vector.</h2>"),
            (">Six operations, one vector.</h2>", ">Six calculations, one well.</h2>"),   # plain words, as on A0
            ("Every well becomes a vector <span style=\"font-family: 'IBM Plex Mono', Menlo, monospace; font-style: italic; color: #14171a;\">e &#8712; &#8477;<sup style=\"font-size: 0.7em;\">3773</sup></span>, z-scored across the field. Everything on the previous slides is one of these, and each one is a difference of means or a held-out classifier, so a lab can check it.",
             A2_LEDE),
            (BADGE + "[1]</span>", REF + "[1]</span>"), (BADGE + "[e6]</span>", REF + "[e6]</span>"),
            (BADGE + "24%</span>", BADGE.replace("#be1e74", "#454c50") + "24%</span>"), (BADGE + "&#948;</span>", ""),
            ("display: flex; justify-content: space-between; align-items: baseline; gap: 8px;\">", "display: flex; justify-content: space-between; align-items: flex-end; gap: 8px; height: 26px;\">"),
            ('padding: 52px 56px 48px; display: flex; flex-direction: column; gap: 14px;', 'padding: 52px 56px 44px; display: flex; flex-direction: column; gap: 14px;'),
            ('font-size: 13px; letter-spacing: 0.11em;', 'font-size: 14px; letter-spacing: 0.1em;'),
            ('text-transform: uppercase; color: #be1e74;">How the numbers are made', 'text-transform: uppercase; color: #0f8f6c;">How the numbers are made'),
            # plain words under each formula; the formulas stay for the scientist, the detail (L2, permuted labels, no-1536 check) is in the script
            (A2_LEDE, f"Each well becomes {E1['n_features']:,} numbers.<br>Each result compares averages, or tests a model on unseen plates."),
            ('>1 &#183; embedding</span>', '>1 &#183; image to numbers</span>'), ('>2 &#183; lab classifier</span>', '>2 &#183; which lab?</span>'),
            ('>3 &#183; distance, the certificate</span>', '>3 &#183; how far from normal?</span>'), ('>4 &#183; variance decomposition</span>', '>4 &#183; sources of variation</span>'),
            ('>5 &#183; regress variables out</span>', '>5 &#183; remove known causes</span>'), ('>6 &#183; morphology change, two ways</span>', '>6 &#183; did the drug change the cells?</span>'),
            ('L2 logistic regression, five folds held out by plate.<br>Chance 1 in 11 &#183; permuted labels 9.3%<br>Without 1536-well labs: 99.98%',
             f"Names the lab from one well, on plates it never saw.<br>Far above chance ({100 * E1['chance']:.0f}%): each lab leaves a fingerprint."),
            ('c: known instrument variables only; then re-run f.<br>Plate-centred alone: f falls to 24%.',
             f'Remove only causes known to be the instrument.<br>Subtracting each plate&#8217;s controls goes further: right lab only {100 * CENTRED:.0f}% of the time.'),
            ('&#966; &#8712; {CellProfiler, CNN, ViT}: similar on hepatocytes.<br>Extractor is not the asset.',
             'Three ways to turn images into numbers gave similar results on liver cells.<br>Tool is not the asset.'),
            ('Difference of means, in units of the field&#8217;s spread.<br>Its direction is what moved; &#8722;d is the way back.',
             'How far this plate&#8217;s average sits from all labs&#8217; average, in units of normal spread.<br>Direction says what moved.'),
            ('Nested: shares sum to one.<br>Microscope models span labs, so the two separate.', 'Splits variation into microscope type, lab, batch, plate, well.<br>Shares add up to 100%.'),
            ('f bounded &#183; e&#8242; aligned to the reference first',
             'Distance from the untreated average, capped so one odd well cannot dominate.<br>Or a model, after aligning to the reference.'),
            ('E[e | field, c]', 'E[e | all labs, c]'), ('&#948; = f(&#8214;e &#8722; E[e | vehicle]&#8214;)', '&#948; = b(&#8214;e &#8722; E[e | untreated]&#8214;)'),
            ("font-size: 15px; line-height: 1.35; color: #454c50;\">", "font-size: 17px; line-height: 1.35; color: #454c50;\">"),   # 6 card bodies fill their cards
            ('<span style="color: #0f8f6c;">discovery</span> &#183; align the lab away first<br><span style="color: #be1e74;">QC</span> &#183; keep the lab coordinate, never align it away',
             '<span style="color: #0f8f6c;">drug discovery</span> &#183; remove the lab first<br><span style="color: #be1e74;">quality check</span> &#183; keep the lab: it is the signal')],
    't13': [('white-space: nowrap;">site</span>', 'white-space: nowrap;">lab</span>'),
            # what travels with any image, and what nobody is asked for today
            ('white-space: nowrap;">CellProfiler version</span></div>\n    </div>',
             'white-space: nowrap;">CellProfiler version</span></div>\n      ' + A3_NOTE + 'in every image file too:<br>image size &#183; stored bit depth</span>\n    </div>'),
            ('white-space: nowrap;">CO2 and humidity</span></div>\n    </div>',
             'white-space: nowrap;">CO2 and humidity</span></div>\n      ' + A3_NOTE + 'not required to publish today [15]<br>in our own data: tracked, every one</span>\n    </div>'),
            ('image size &#183; bit depth &#183; pixel size</span>', 'image size &#183; stored bit depth</span>'),   # pixel size is optional in the format; the earlier wording
            ('not required to publish today<br>', 'not required to publish today [15]<br>'),
            ('white-space: nowrap;">sites per well</span>', 'white-space: nowrap;">fields per well</span>'),
            ("<p style=\"margin: 0; font-family: 'Source Serif 4', Georgia, serif; font-size: 18px; line-height: 1.4; color: #666e72;\">Normal is a conditional expectation, <span style=\"font-family: 'Source Serif 4', Georgia, serif; font-style: italic; color: #14171a;\">E[x | every variable below]</span>. Even JUMP, built to be comparable, records only the instrument side.</p>",
             f"<p style=\"margin: 0; {SANS} font-size: 19px; line-height: 1.4; color: #666e72;\">Normal is <span style=\"{MATH} color: #14171a;\">E[x | every variable below]</span>.</p>"),
            ('Centre each plate on its own controls, the standard first step, and the lab is named 24% of the time. It removes most of the coordinate a certificate needs.',
             'Centring each plate on its own controls is the standard first step.<br>It removes most of the coordinate a certificate needs.'),
            ('Batch correction is built to remove this signal: Arevalo J, et al., Nature Communications, 2024. Variables: JUMP datasets metadata.',
             'Batch correction is built to remove this signal: Arevalo et al., Nat Commun 2024 &#183; variables: JUMP metadata [7]'),
            ('padding: 52px 56px 48px; display: flex; flex-direction: column; gap: 16px;', 'padding: 52px 56px 44px; display: flex; flex-direction: column; gap: 14px;'),
            ('font-size: 13px; letter-spacing: 0.11em;', 'font-size: 14px; letter-spacing: 0.1em;'),
            ('A3 &#183; if asked why not batch-correct</span></div>',
             f'A3 &#183; if asked why not batch-correct</span><span style="{MONO} font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color: #0f8f6c;">results/e1-redteam</span></div>'),
            ('font-size: 13px; padding: 4px 9px;', 'font-size: 14px; padding: 5px 10px;'), ('font-size: 13px; padding: 3px 8px;', 'font-size: 14px; padding: 4px 9px;'),
            ('<div style="display: flex; flex-wrap: wrap; gap: 6px;">', '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'),
            ('<span style="color: #be1e74;">What nobody does.</span>', '<span style="color: #be1e74;">What it leaves out.</span>'),
            (f'Normal is <span style="{MATH} color: #14171a;">E[x | every variable below]</span>.', 'What counts as normal depends on every variable below.'),
            ('Centring each plate on its own controls is the standard first step.<br>It removes most of the coordinate a certificate needs.',
             'Standard first step: subtract each plate&#8217;s own controls.<br>It erases most of the lab fingerprint a certificate reads.')],
    't15': [('font-weight: 500;">Fig. 1</span>', 'font-weight: 500;">Fig. A5</span>'),
            # the mini-figures' words, rewritten here before TRIM looks for the whole FIG1 and FIG2, or a second figure goes in
            ('>cells, not the day</figcaption>', '>removes day-to-day shifts</figcaption>'),
            ('>one wild well can&#8217;t swamp it</figcaption>', '>one odd well cannot dominate</figcaption>'), ('>vehicle</text>', '>untreated</text>')],
    't19': [('in eleven buildings.', 'in eleven labs.')],
}


def _dots(cx, cy, offsets, fill):
    return ''.join(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="2.5" fill="{fill}"/>' for dx, dy in offsets)


def _figure(svg, caption):
    return (f'<figure style="margin:0; display:flex; flex-direction:column; gap:4px;">{svg}'
            f'<figcaption style="{MONO} font-size:13px; color:#666e72; white-space:nowrap;">{caption}</figcaption></figure>')


A5_G = [(-9, -6), (-2, -10), (6, -7), (10, 0), (4, 6), (-5, 5), (-11, 1), (0, -1)]
A5_P = [(-6, -4), (3, -6), (7, 2), (0, 5), (-7, 3), (1, 0)]
SVG_OPEN = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 84" width="200" height="84" aria-hidden="true" style="display:block;">'
FIG1 = _figure(SVG_OPEN + _dots(36, 40, A5_G, '#949c9f') + _dots(54, 58, A5_P, '#be1e74')
               + '<path d="M 80 42 H 112" stroke="#949c9f" stroke-width="2"/><path d="M 118 42 L 110 38 L 110 46 Z" fill="#949c9f"/>'
               + f'<text x="98" y="32" {parts.SVG_MONO} font-size="13" fill="#666e72" text-anchor="middle">align</text>'
               + _dots(160, 42, A5_G, '#949c9f') + _dots(160, 42, A5_P, '#be1e74') + '</svg>',
               'removes day-to-day shifts')
FIG2 = _figure(SVG_OPEN + '<path d="M 16 14 H 196" stroke="#949c9f" stroke-dasharray="4 4" stroke-width="1.5"/>'
               + '<path d="M 16 64 C 60 64, 70 18, 120 17 L 192 16" fill="none" stroke="#454c50" stroke-width="2"/>'
               + '<circle cx="16" cy="64" r="5" fill="#0f8f6c"/>'
               + f'<text x="6" y="80" {parts.SVG_MONO} font-size="13" fill="#666e72" text-anchor="start">untreated</text>'
               + '<circle cx="186" cy="16" r="4.5" fill="#949c9f"/></svg>',
               'one odd well cannot dominate')

DRIFT = {b['gap']: b for b in parts.results('e1b-drift-source_2.json')['bins']}   # A6 (t16) quotes its ratios from here


def a16_stat(big, small, size=26):
    """One number on A16's test-set card, as the hand-built board writes it."""
    return (f'<div style="display:flex; flex-direction:column; gap:2px;"><span style="{SANS} font-size:{size}px; font-weight:600; letter-spacing:-0.02em; line-height:1; color:#14171a; white-space:nowrap;">{big}</span>'
            f'<span style="{SANS} font-size:13px; color:#666e72; white-space:nowrap;">{small}</span></div>')


TRIM = {                               # fewer words on slides that are not written whole
    't2': [('@keyframes fade', '.grid .tile { opacity:0; animation: fade .5s ease-out forwards; } '
            + ' '.join(f'.grid .tile:nth-child({k}) {{ animation-delay:{0.15 * k:.2f}s; }}' for k in range(1, 7)) + '\n@keyframes fade'),
           ('position:absolute; left:56px; top:92px;', 'position:absolute; left:56px; top:86px;'),                    # 3 headlines
           ('padding:50px 56px 44px;', 'padding:52px 56px 48px;'),
           ('left:56px; bottom:40px; width:1010px;', 'left:56px; bottom:44px; width:1010px;'),                        # legend
           ('class="hint" style="position:absolute; right:56px; bottom:40px;', 'class="hint" style="position:absolute; right:56px; bottom:44px;'),
           ('<div style="position:absolute; left:724px; top:150px; display:inline-flex; align-items:baseline; gap:6px; padding:5px 11px; border:1px solid #c3c9cb; border-radius:999px; font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; line-height:1.3; white-space:nowrap;"><span style="color:#14171a; font-weight:500;">Cell Painting</span><span style="color:#666e72;">six dyes, 3,773 numbers per well</span></div>', ''),  # pill: its words are in the legend
           ('Could you tell? <span style="color:#0f8f6c;">A classifier can.</span>', 'Could you tell?<br><span style="color:#0f8f6c;">Classifiers can.</span>'),
           ('<div style="display:flex; align-items:center; gap:10px;"><span style="width:16px; height:16px; border-radius:4px; border:2.5px solid #be1e74; box-sizing:border-box;"></span><span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:15px; color:#be1e74;">78 wells wrong, of 93,228</span></div>', ''),
           ('<div class="stat" style="position:absolute; left:720px; top:226px; display:flex; flex-direction:column; gap:22px;">',
            '<div class="stat" style="position:absolute; left:720px; top:206px; height:396px; display:grid; grid-template-columns:auto 1fr; column-gap:18px; row-gap:22px; align-content:center; align-items:baseline;">'),  # same box as the picto
           ('<div style="display:flex; align-items:baseline; gap:18px;">', '<div style="display:contents;">'),        # 2 hits
           ('>chance &#183; 1 in 11 labs</span>', '>chance</span>'),                                              # the eleven labs are in the legend
           # pink is "you" across the deck: lab 2's tile says so from the first view, before the labs are named
           ('.step-1 .star, .step-1 .startag, .step-2 .star', '.step-0 .star, .step-0 .startag, .step-1 .star, .step-1 .startag, .step-2 .star'),
           ('font-size:13px; opacity:0;">lab 2</span><div class="loc"', 'font-size:13px; opacity:0;" data-h="you">you</span><div class="loc"'),
           # 03c: the chain sits in the figure band, the map as tall as the band
           ('<div class="chain" style="position:absolute; left:56px; top:270px; width:1168px; display:flex; gap:0; align-items:flex-start;',
            '<div class="chain" style="position:absolute; left:56px; top:204px; height:430px; width:1168px; display:flex; gap:0; align-items:center;'),
           ('height:196px; margin-top:26px;', 'height:196px; margin-top:0;'),
           # 03c: the pictures say nucleus, well, map; the map's own label says lab 2
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; color:#666e72;">one nucleus</span>\n      ', ''),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; color:#666e72;">its well</span>\n      ', ''),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; color:#666e72;">where it lands</span>\n      ', ''),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#be1e74;">lab 2</span>', ''),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#f6f7f7; opacity:.92; line-height:1;">100 &#181;m</span>', ''),
           ('<div class="picto" style="position:absolute; left:720px; top:236px; display:flex; flex-direction:column; gap:26px;">',
            '<div class="picto" style="position:absolute; left:720px; top:206px; height:396px; display:flex; flex-direction:column; justify-content:center; gap:36px;">'),
           ('width="34" height="34"', 'width="40" height="40"'),
           ('font-size:28px; font-weight:500; letter-spacing:-0.015em; color:#14171a;">', 'font-size:30px; font-weight:500; letter-spacing:-0.015em; color:#14171a;">'),
           ('font-size:22px; color:#0f8f6c;">&#10003;', 'font-size:24px; color:#0f8f6c;">&#10003;'),
           ('>same line</span>', '>same cells</span>'),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#f6f7f7; opacity:.92;">100 &#181;m</span>', ''),  # 6 tile labels; bars stay
           ('One well, <span style="color:#be1e74;">all the way out.</span>', 'One well, <span style="color:#0f8f6c;">onto the map.</span>'),
           ('<div class="chain" style="position:absolute; left:56px; top:180px;', '<div class="chain" style="position:absolute; left:56px; top:270px;'),
           ('.step-2 .chain, .step-2 .others { opacity', '.step-2 .chain { opacity'),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#454c50;">192 &#181;m&#178; &#183; <span style="color:#be1e74;">0.59</span></span>', ''),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#454c50;">93,228 wells, 11 labs</span>', ''),
           ('color:#454c50;">plate 1053600681</span>', 'color:#be1e74;">lab 2</span>'),
           ('viewBox="0 0 1180 392"', 'viewBox="54 4 1124 342"'),                                                    # PCA crop
           ('y="139" ' + OLD_SVG_FONT + ' font-size="26" font-weight="700"', 'y="143" ' + parts.SVG_MONO + ' font-size="28" font-weight="500"' + HALO),   # the halo keeps the label off the dots
           ('y="167" ' + OLD_SVG_FONT + ' font-size="22"', 'y="173" ' + parts.SVG_MONO + ' font-size="26"' + HALO),
           ('x="84" y="328" ' + OLD_SVG_FONT + ' font-size="22"', 'x="98" y="328" ' + parts.SVG_MONO + ' font-size="26"'),          # PC 1 clears the foot of PC 2
           ('translate(86,300) rotate(-90)"><text x="0" y="0" ' + OLD_SVG_FONT + ' font-size="22"', 'translate(86,308) rotate(-90)"><text x="0" y="0" ' + parts.SVG_MONO + ' font-size="26"')],  # PC 2 clears the lab at the far left
    't15': [('Distance published with the Broad [1]; transform unpublished.', 'distance published [1] &#183; transform unpublished'),   # no collaborator named
            ('Standard alignment; the tuning is ours.', 'standard alignment &#183; our tuning'),
            ('font-size: 48px; font-weight: 600;', 'font-size: 44px; font-weight: 600;'),                                              # headline text is set by a5_pair()
            ('Why now: an image classifier can answer this, and until recently nothing could. A count moves only when cells die or divide; an embedding of the whole well moves when anything changes.',
             'Count moves only when cells die or divide.<br>Image moves when anything changes.'),
            (' Same cell line, two untreated wells, and the two readouts. Left, DNA channel, JUMP cpg0016, CC0; nuclei by Otsu segmentation; detail = high-frequency energy over total, inside each nucleus. Right, the two readouts: a classifier on aligned embeddings, and a bounded distance from the vehicle centre. Alignment and distance follow published practice [1]; the specific transform and tuning are not disclosed here. [1] Ewald JD, Titterton KL, et al. <em>Cell Systems</em>, 2026.',
             ' DNA channel &#183; JUMP cpg0016 [7], CC0 &#183; nuclei by Otsu &#183; texture = high-frequency energy over total, inside nuclei'),  # a5_pair() adds the results key when the file exists
            ('padding: 56px; display: flex; flex-direction: column; gap: 18px;', 'padding: 52px 56px 44px; display: flex; flex-direction: column; gap: 14px;'),
            ('<div style="display: flex; justify-content: space-between; align-items: baseline;"><span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color: #666e72;">A5 &#183;',
             parts.watermark('A5') + '<div style="display: flex; justify-content: space-between; align-items: baseline;"><span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color: #666e72;">A5 &#183;'),
            ('color: #0f8f6c;">Published<', 'color: #0f8f6c;">Cell Systems &#183; 2026 &#183; [1]<'),                                   # D3: the source lives in the tag
            ('<div style="display:flex; gap:14px;">', '<div style="display:flex; gap:28px;">'), ('width: 300px; flex-shrink: 0;', 'width: 360px; flex-shrink: 0;'),
            ('display: flex; gap: 32px; flex-grow: 1; min-height: 0; align-items: flex-start;', 'display: flex; gap: 32px; flex-grow: 1; min-height: 0; align-items: stretch;'),   # the two method cards share the row's height
            ("font-family: 'IBM Plex Mono', Menlo, monospace; font-style:italic; font-size:17px;", MATH + ' font-size:19px;'),           # 2 hits
            ('>Method one</span>', '>method 1 &#183; classifier</span>'), ('>Method two</span>', '>method 2 &#183; distance</span>'),
            ('<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:16px; line-height:1.33; color:#454c50;">Align first, so the answer is the cells and not the day.</span>', ''),
            ('<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:16px; line-height:1.33; color:#454c50;">Bounded, so one wild well cannot swamp the score.</span>', ''),
            ('display:flex; flex-direction:column; gap:5px; animation-delay:0.30s;">', 'display:grid; grid-template-columns:1fr 224px; column-gap:20px; align-items:center; flex:1 1 0; animation-delay:0.30s;"><div style="display:flex; flex-direction:column; gap:5px; min-width:0;">'),
            ('display:flex; flex-direction:column; gap:5px; animation-delay:0.50s;">', 'display:grid; grid-template-columns:1fr 224px; column-gap:20px; align-items:center; flex:1 1 0; animation-delay:0.50s;"><div style="display:flex; flex-direction:column; gap:5px; min-width:0;">'),
            ('our tuning</span></div>', 'our tuning</span></div>' + FIG1 + '</div>'),
            ('transform unpublished</span></div>', 'transform unpublished</span></div>' + FIG2 + '</div>'),
            ('<div style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 15px; letter-spacing: 0.02em; color: #be1e74;"><span style="color: #14171a;">Both methods need the same thing to work: somebody else&#8217;s images.</span> It takes a reference to know which.</div>',
             '<div style="margin-left:392px; font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 15px; letter-spacing: 0.02em; color: #14171a;">both need a reference &#183; <span style="color: #0f8f6c;">somebody else&#8217;s images</span></div>'),
            ('width: 360px; flex-shrink: 0; display: flex; flex-direction: column; gap: 8px;', 'width: 360px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; gap: 8px;'),
            ('<div style="' + MATH + ' font-size:19px; color:#14171a; padding:2px 0;">g: e&#8242; &#8594; belongs / does not,&#160; e&#8242; = align(e)</div>', ''),   # the questions and pictures say it; A2 keeps the maths
            ('<div style="' + MATH + ' font-size:19px; color:#14171a; padding:2px 0;">&#948; = f(&#8214;e &#8722; E[e | vehicle]&#8214;),&#160; f bounded</div>', '')],
    't16': [('<text x="258.0" y="286.9"', '<text x="226.0" y="286.9" text-anchor="end"'), ('<text x="522.0" y="249.0"', '<text x="490.0" y="249.0" text-anchor="end"'),
            ('<text x="786.0" y="229.7"', '<text x="754.0" y="229.7" text-anchor="end"'), ('<text x="1050.0" y="165.6"', '<text x="1018.0" y="165.6" text-anchor="end"'),
            ('<text x="1314.0" y="86.2"', '<text x="1282.0" y="86.2" text-anchor="end"'),
            ('fill="#be1e74">1.4</text>', 'fill="#be1e74">1.40</text>'), ('fill="#be1e74">4.7</text>', 'fill="#be1e74">4.70</text>'),
            ('font-size="18" fill="#949c9f"', 'font-size="19" fill="#666e72"'),
            ('<path d="M 242.0 298.9 L 506.0', f'<path d="M 242 298.9 L 1430 298.9" stroke="#949c9f" stroke-width="2" stroke-dasharray="6 6"/><text x="1424" y="320" {parts.SVG_FONT} font-size="19" text-anchor="end" fill="#666e72">same batch</text><path d="M 242.0 298.9 L 506.0'),
            ('fill="#be1e74">4.70</text>', f'fill="#be1e74">4.70</text><path d="M 1336 296.9 L 1336 100.2 M 1328 298.9 L 1344 298.9 M 1328 98.2 L 1344 98.2" stroke="#be1e74" stroke-width="2" fill="none"/><text x="1352" y="207" {parts.SVG_FONT} font-size="26" font-weight="700" fill="#be1e74">&#215;7.5</text>'),
            ('Not known from profiles alone. The data says the lab moved and when. It does not say why.', 'Unknown from profiles.<br>Data shows when the lab moved, not why.'),
            ('>So why re-certify?<', '>How often?<'),
            ('Because your certificate is a comparison made on one day, and the baseline it was made against goes stale within weeks.', 'At least every quarter.<br>Distance &#215;4.9 by 6 to 13 weeks.'),
            ('One lab, 219 plates, 13 batches, June to October 2021. 0.63 in the same batch, 4.7 over 13 weeks. Other labs are not yet measured.', 'One lab, 219 plates, 13 batches.<br>Other labs not yet measured.'),
            ('font-size: 16px; line-height: 1.32; color: #14171a;', 'font-size: 18px; line-height: 1.35; color: #14171a;'),
            ('Two plates of one lab sit further apart the longer the gap between them. In lab 2 the distance is still rising after thirteen weeks.', 'Plates of one lab drift apart with time.<br>Still rising after 13 weeks.'),
            ('font-size: 42px; font-weight: 600;', 'font-size: 44px; font-weight: 600;'),
            ('font-size: 18px; line-height: 1.4; color: #666e72; flex-grow: 1;', 'font-size: 19px; line-height: 1.45; color: #666e72; flex-grow: 1;'),
            ('with the interquartile range. results/e1b-drift.</div>', 'with the interquartile range.</div>'),
            ('font-size: 13px; letter-spacing: 0.11em;', 'font-size: 14px; letter-spacing: 0.1em;'),
            ('text-transform: uppercase; color: #be1e74;">results/e1b-drift</span>', 'text-transform: uppercase; color: #0f8f6c;">results/e1b-drift</span>'),  # D15
            ('background: linear-gradient(#ffffff, #ffffff) padding-box, linear-gradient(90deg, #be1e74, #0f8f6c) border-box; border-top: 3px solid transparent; border-radius: 16px;',
             'background: linear-gradient(90deg, #be1e74, #0f8f6c) top / 100% 3px no-repeat, #ffffff; border-radius: 16px;'),
            ('padding: 12px 20px; display: flex;">', 'padding: 15px 20px 12px; display: flex;">'),
            ('>distance, within-plate spreads</text>', '>how different two plates are</text>'),             # plain words; the unit is in the note
            ('Median distance between plate centroids, in within-plate spreads, with the interquartile range.',
             'Dot: median plate pair. Bar: middle half of pairs.<br>1 = how far a typical untreated well sits from its plate&#8217;s average.'),
            ('At least every quarter.<br>Distance &#215;4.9 by 6 to 13 weeks.',
             f'At least every quarter.<br>By 6 to 13 weeks: &#215;{DRIFT["6 to 13 weeks"]["ratio_to_same_batch"]:g} vs same batch.'),
            ('The line is not expired. <span style="color: #be1e74;">Your baseline is.</span>',
             'Your baseline expires.<br><span style="color: #be1e74;">Re-check at least every quarter.</span>'),
            ('Unknown from profiles.<br>Data shows when the lab moved, not why.', 'This data cannot tell.<br>It shows when the lab moved, not why.')],
    # 't25' (A15) is written whole by appendix.a15 since the exchange was added; its old trims are gone
    't26': [('The variation a real lab meets, generated rather than avoided. Same cells, same protocol, no drug, and it already looks like this.', 'Same cells, same protocol, no drug. It already looks like this.'),
           ('Across the 13 JUMP labs. A real lab adds cell lines, plate types, stacks and damaged plates on top.', 'Across the 13 JUMP labs.'),
           ('A public benchmark: name the failure. Bubble, focus, clipped well, bad lot, wrong label.', 'A public benchmark: name the failure.'),
           ('A foundation other people can stand on: one phenotypic space the field converges toward, instead of Google Images.', 'One shared space for the field, instead of Google Images.'),
           ('One shared space for the field, instead of Google Images.', 'The benchmark every model is graded on. The glue between labs and the companies that buy their data.'),
           ('The benchmark every method is graded on: the glue between labs that make data and companies that buy it.', 'The benchmark every model is graded on. The glue between labs and the companies that buy their data.'),
           ('The benchmark every method is graded on, normalization to bioactivity: the glue between the labs that make data and the companies that buy it.', 'The benchmark every model is graded on. The glue between labs and the companies that buy their data.'),
           ('The benchmark every model is graded on. The glue between labs and the companies that buy their data.', 'The playground: the most-used lines, every microscope, reference perturbations, planted failures. Every normalization graded.'),
           ('>Across the 13 JUMP labs.<', '>across all 13 JUMP labs &#183; public metadata [7]<'),
           ('padding:14px 16px 12px; display:flex; flex-direction:column; justify-content:space-between; gap:10px; min-width:0; animation-delay:0.15s;',
            'padding:12px 14px 12px; display:flex; flex-direction:column; gap:8px; min-width:0; animation-delay:0.15s;'),
           ('<div style="display:flex; justify-content:space-between; align-items:flex-end; gap:12px; border-top:',
            '<div style="display:flex; justify-content:space-between; align-items:flex-end; gap:12px; margin:auto 0; border-top:'),
           ('Same cells, same protocol, no drug. It already looks like this.', 'Same cells, same protocol, no drug.<br>It already looks like this.'),
           ('font-size:15px; line-height:1.45; color:#ef74ad; white-space:nowrap;">The playground: the most-used lines, every microscope, reference perturbations, planted failures. Every normalization graded.',
            'font-size:14px; line-height:1.45; color:#c9cfd1; white-space:nowrap;"><span style="color:#3fe0a0;">playground</span> &#183; most-used lines &#183; every microscope &#183; reference perturbations &#183; planted failures &#183; every normalization graded'),
           ('>A public benchmark: name the failure.<', '>Public benchmark: name the failure.<'),
           ('padding:52px 56px 46px; display:flex; flex-direction:column; gap:18px;', 'padding:52px 56px 44px; display:flex; flex-direction:column; gap:14px;'),
           ('font-size:18px; line-height:1.4; color:#c9cfd1;', 'font-size:19px; line-height:1.45; color:#c9cfd1;'),
           ('color:#ef74ad; white-space:nowrap;">one well, simulated<', 'color:#949c9f; white-space:nowrap;">one well &#183; simulated<'),
           ('>real wells, JUMP cpg0016, CC0<', '>real wells &#183; JUMP cpg0016 &#183; CC0<'),
           ('>The test set · what six labs already send<', '>test set · what six labs already send<'),
           ('Build the ugliest dataset in biology, <span', 'Build the ugliest dataset<br>in biology, <span'),
           # plain words for a reader outside the field; these run after the pairs above that wrote the old text
           ('>test set · what six labs already send<', '>public data today · six labs<'),
           ('>real wells &#183; JUMP cpg0016 &#183; CC0<', '>real wells &#183; JUMP [7]<'),
           (a16_stat('0.4–1.0', 'objective NA'), ''), (a16_stat('0–3', 'brightfield planes'), ''), (a16_stat('0.60–0.70', 'µm per pixel'), ''),
           ('font-size:26px; font-weight:600; letter-spacing:-0.02em; line-height:1; color:#14171a;',     # the size of the big numbers on A17 to A19;
            'font-size:34px; font-weight:600; letter-spacing:-0.02em; line-height:1; color:#14171a;'),    #   before the 13 is added, which is already 34px
           ('>plate types</span></div>', '>plate layouts</span></div>' + a16_stat('13', 'labs [7]', 34)),
           ('\n      <span style="' + SANS + ' font-size:13px; line-height:1.3; color:#666e72;">across all 13 JUMP labs &#183; public metadata [7]</span>', ''),
           ('gap:12px; margin:auto 0; border-top:', 'gap:12px; margin-top:auto; border-top:'),        # the numbers sit on the card's floor, level with the red team's line
           ('most-used lines &#183; every microscope &#183; reference perturbations &#183; planted failures &#183; every normalization graded',
            'common cell lines &#183; every microscope &#183; known treatments &#183; planted faults &#183; every correction scored'),
           ('common cell lines &#183; every microscope &#183; known treatments &#183; planted faults &#183; every correction scored',
            'U2OS, A549, HepG2, iPSC [17] &#183; widefield and confocal &#183; known drugs &#183; planted faults &#183; every correction scored'),
           ('>Red team<', '>planted on purpose<'),
           ('>one well &#183; simulated<', '>simulated<'),       # the longer label and the old tag do not fit one 272px line
           ('font-size:14px; line-height:1.3; color:#454c50; margin-top:auto;">Public benchmark: name the failure.<',
            'font-size:17px; line-height:1.3; color:#14171a; margin-top:auto;">Can a model name the fault?<'),
           ('Same cells, same protocol, no drug.<br>It already looks like this.', 'Same cells, same protocol, no drug.<br>Still, each lab looks different.')],
    't35': [('&#8220;Do my cells <span style="color:#be1e74;">look normal?</span>&#8221;</h2>', 'Today: <span style="color:#be1e74;">search, ask, guess.</span></h2>'),
           ('padding:12px 0 12px 14px; margin-top:6px; border-left:3px solid #be1e74;', 'padding:8px 0 8px 14px; margin-top:4px; border-left:3px solid #be1e74;'),
           ('padding:12px 0 12px 14px; margin-top:6px; border-left:3px solid #c3c9cb;', 'padding:8px 0 8px 14px; margin-top:4px; border-left:3px solid #c3c9cb;'),
           ('<div class="p3" style="box-sizing:border-box; background:#ffffff; border:1px solid #d3d8da; border-radius:12px; padding:14px 16px 12px; display:flex; flex-direction:column; gap:8px; min-width:0; min-height:0;">',
            '<div class="p3" style="box-sizing:border-box; background:#ffffff; border:1px solid #d3d8da; border-radius:12px; padding:14px 16px 12px; display:flex; flex-direction:column; gap:8px; min-width:0; min-height:0; overflow:hidden;">'),
           ('>of R&amp;D before the SOP was fixed<', '>of R&amp;D<'), ('>of R&amp;D, before the fix<', '>of R&amp;D<'),
           ('>developing cells that were already good enough<', '>of development<'), ('>on cells that were already fine<', '>of development<'),
           ('Since 2023 the field&#8217;s reference is public: JUMP, CC0 [7].', 'Since 2023 the field&#8217;s reference is public [7].'),
           ('Since 2023 the field&#8217;s reference is public [7].', 'Since 2023 the field&#8217;s reference is public [7].<br>Since 2025 cell data carries regulatory weight [9].'),
           ('>the field&#8217;s reference goes public [7]<', '>reference goes public [7]<'), ('>cell data starts to carry regulatory weight [9]<', '>cell data gains regulatory weight [9]<'), ('>the map: eleven labs, one frame<', '>the map<'),
           ('<p style="margin:0; font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:17px; line-height:1.35; color:#454c50;">Since 2023 the field&#8217;s reference is public [7].<br>Since 2025 cell data carries regulatory weight [9].</p>',
            '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0; position:relative; padding-top:14px;">'
            '<div aria-hidden="true" style="position:absolute; left:6px; right:6px; top:5px; height:2px; background:linear-gradient(90deg,#0f8f6c,#be1e74);"></div>'
            + ''.join(f'<div style="position:relative; padding-right:12px;"><div aria-hidden="true" style="position:absolute; left:0; top:-14px; width:12px; height:12px; border-radius:50%; background:{col};"></div>'
                      f'<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:{col};">{yr}</span><br>'
                      f'<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:15px; line-height:1.3; color:#454c50;">{what}</span></div>'
                      for yr, what, col in (('2023', 'reference goes public [7]', '#0f8f6c'), ('2025', 'cell data gains regulatory weight [9]', '#0f8f6c'), ('2026', 'the map', '#be1e74')))
            + '</div>'),
           ('padding:52px 56px 44px; display:flex; flex-direction:column; gap:18px;', 'padding:52px 56px 44px; display:flex; flex-direction:column; gap:14px;'),
           ('font-size:50px; font-weight:600; letter-spacing:-0.03em; line-height:1.03;', 'font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05;'),
           ('color:#0f8f6c;">The question nobody can answer', 'color:#0f8f6c;">public sources [6], [7], [9]'),
           ('position:relative; overflow:hidden;">', 'position:relative; z-index:0; overflow:hidden;">' + parts.watermark('A25')),
           ('grid-template-columns:1fr 1fr 1fr; gap:0; position:relative; padding-top:14px;', 'grid-template-columns:1.25fr 1.25fr 0.5fr; gap:0; position:relative; padding-top:14px;'),
           ('box-sizing:border-box; background:#ffffff; border:1px solid #d3d8da; border-radius:12px;', parts.CARD),                   # 3 panels
           ('letter-spacing:-0.01em; color:#454c50;">ask around</span>', 'letter-spacing:-0.01em; color:#454c50;">ask</span>'),
           # plain words for a reader new to the field; each runs after the pair that wrote its input
           ('lab 2." style="width:100%; height:100%; object-fit:cover; display:block;"></div></div>\n</div><div class="p2"',      # a caption under the six search results
            'lab 2." style="width:100%; height:100%; object-fit:cover; display:block;"></div></div>'
            '<span style="' + SANS + ' font-size:15px; line-height:1.3; color:#454c50;">one cell line &#183; six papers &#183; all look different</span>\n</div><div class="p2"'),
           ('>Irreproducible preclinical research &#183; US &#183; per year [6]<', '>$28B a year &#183; spent on US lab research others cannot reproduce [6]<'),
           ('<span style="' + MONO + ' font-size:13px; color:#666e72;">$28B</span>', ''),        # the total now leads the line above the bar
           ('>36% &#8776; $10B &#183; reagents &amp; references<', '>36% &#8776; $10B &#183; cells and reagents<'),
           ('>64% &#183; design, analysis, protocols<', '>64% &#183; other causes<'),
           ('>run it anyway &#183; too fast<', '>run it anyway<'), ('>hold &#183; too slow<', '>wait to be sure<'),
           ('>of R&amp;D<', '>of R&amp;D dollars at risk<'), ('>of development<', '>of development lost<'),
           ('>reference goes public [7]<', '>public cell image set [7]<'), ('>cell data gains regulatory weight [9]<', '>FDA: fewer animal tests [9]<'),
           ('A25 &#183; if asked how labs answer it today', 'A25 &#183; if asked how labs check cells today')],
}
# Kat's papers, newest first: short title, journal, year, first author and the first author's institution, as printed (checked against
# PubMed, Crossref and bioRxiv on 15 Oct 2026). Full citations: README.
PAPERS = [('Cell Painting in primary human hepatocytes', 'Cell Systems', 2026, 'Ewald', 'Broad Institute'),
          ('Counting cells predicts bioactivity benchmarks', 'Nat Commun', 2026, 'Seal', 'Univ. of Cambridge'),
          ('Cell Painting of hepatotoxic botanicals', 'bioRxiv', 2026, 'Ollitrault', 'EMBL-EBI'),
          ('An antibody to pathological tau', 'Mol Neurodegen Adv', 2026, 'Yanamandra', 'AbbVie'),
          ('Capturing synaptic proteopathic seeds', 'iScience', 2026, 'Sebastian', 'AbbVie'),
          ('A neuronal tau aggregation assay', 'J Biol Chem', 2025, 'Wu', 'AbbVie'),
          ('Multiplexed imaging of brain nanostructures', 'Nat Commun', 2024, 'Kang', 'MIT'),
          ('Tau aggregation in human iPSC neurons', 'iScience', 2022, 'Manos', 'AbbVie'),
          ('Neurosteroid photolabeling of GABA<sub>A</sub> receptors', 'Eur J Med Chem', 2019, 'Wu', 'U Illinois Chicago')]


def founder(s):
    """Every paper as two short lines: what; where, when, and whose lab led it. The list replaces the old 'published with' block."""
    a = s.index('My work</span>') + len('My work</span>')
    if '<!--/refs-->' in s:
        b = s.index('<!--/refs-->') + len('<!--/refs-->')
    else:                                          # first run: up to the end of the 'published with' block
        b = s.index('</div>', s.index('Uppsala</span>', a)) + len('</div>')
    rows = ''.join(
        f'<div class="ref" style="animation-delay:{0.45 + 0.06 * k:.2f}s; display:grid; grid-template-columns:18px 1fr; column-gap:12px; align-items:baseline;">'
        f'<span style="{MONO} font-size:13px; color:#be1e74;">{k + 1}</span>'
        f'<span style="{SANS} font-size:15px; line-height:1.28; color:#14171a;">{title}<br>'
        f'<span style="{MONO} font-size:13px; color:#666e72;"><em>{journal}</em> {year} &#183; {first}, {where}</span></span></div>'
        for k, (title, journal, year, first, where) in enumerate(PAPERS))
    return s[:a] + '\n      ' + rows + '<!--/refs-->' + s[b:]


REVEAL_CSS = ('.flow .s{opacity:0;pointer-events:none;transition:opacity .5s ease}.step-1 .s1{opacity:1;pointer-events:auto}'
              '.flow{cursor:pointer}')
FOUNDER_STEPS = {'tag': ['Background', 'The question']}
LIGHT = ('background:#f6f7f7; background-image: radial-gradient(60% 50% at 100% 0%, rgba(190,30,116,0.07), transparent 70%), '
         'radial-gradient(50% 45% at 0% 100%, rgba(15,143,108,0.08), transparent 70%);')


OLD_HINT_02 = f'<span data-h="hint" style="position:absolute; right:56px; bottom:44px; z-index:6; {MONO} font-size:13px; color:#666e72;">click &#8594; the question</span>'


def reveal(s):
    """Slide 02's punchline: after the founder's story, the question she asked at every bench, on click. Each piece is added once."""
    if REVEAL_CSS not in s:
        s = s.replace('</style>', REVEAL_CSS + '</style>', 1)
    root = '<div style="width:1280px; height:720px; box-sizing:border-box; padding:52px 56px 80px;'
    if 'class="flow step-0"' not in s:
        assert s.count(root) == 1, 'the founder slide changed shape'
        s = s.replace(root, '<div class="flow step-0"' + root[4:], 1)
    if '>Do my cells<br>' not in s:
        overlay = (f'<div class="s s1" style="position:absolute; left:0; top:88px; right:0; bottom:48px; z-index:5; box-sizing:border-box; padding:0 56px; {LIGHT} '
                   f'display:flex; flex-direction:column; justify-content:center; gap:28px;">'
                   f'<h2 style="margin:0; {SANS} font-size:104px; font-weight:700; letter-spacing:-0.045em; line-height:0.96; color:#14171a;">'
                   f'Do my cells<br><span style="color:#be1e74;">look &#8220;normal&#8221;?</span></h2>'
                   f'<span style="{SANS} font-size:26px; line-height:1.3; color:#454c50;">asked @ five benches<br>&#8230; answered @ none</span></div>'
                   + parts.cue(2))
        k = s.index('>', s.index('class="flow step-0"')) + 1
        s = s[:k] + overlay + s[k:]
    return s.replace(OLD_HINT_02, parts.cue(2))     # the words that used to say 'click'


NESTING = ('<div style="flex-shrink: 0; width: 200px; display: flex;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 280" width="100%" height="100%" style="display:block; min-width:0; min-height:0;">'
           '<rect class="ring" style="animation-delay:0.75s" x="2" y="2" width="296" height="276" rx="16" fill="none" stroke="#0f8f6c" stroke-width="2.5" stroke-dasharray="6 6"/>'
           '<rect class="ring" style="animation-delay:0.60s" x="12" y="30" width="276" height="238" rx="13" fill="none" stroke="#9aa1a4" stroke-width="2"/>'
           '<rect class="ring" style="animation-delay:0.45s" x="22" y="58" width="256" height="200" rx="10" fill="none" stroke="#9aa1a4" stroke-width="2"/>'
           '<rect class="ring" style="animation-delay:0.30s" x="32" y="86" width="236" height="162" rx="8" fill="none" stroke="#9aa1a4" stroke-width="2"/>'
           f'<text x="12" y="23" {parts.SVG_FONT} font-size="20" font-weight="600" fill="#0f8f6c">all labs</text>'
           f'<text x="22" y="51" {parts.SVG_FONT} font-size="20" fill="#454c50">lab</text>'
           f'<text x="32" y="79" {parts.SVG_FONT} font-size="20" fill="#454c50">batch</text>'
           f'<text x="42" y="107" {parts.SVG_FONT} font-size="20" fill="#454c50">plate</text>'
           '<circle cx="150" cy="178" r="8" fill="#be1e74"/>'
           f'<text x="166" y="185" {parts.SVG_FONT} font-size="20" fill="#454c50">well</text></svg></div>')


def board_a1(s):
    """Board A1: well, plate, batch, lab, field drawn as boxes, labelled inside; the trace labels lifted over 13px."""
    a = s.find('<div style="flex-shrink: 0; height: 168px; display: flex;">')
    if a >= 0:
        b = s.index('</svg></div>', a) + len('</svg></div>')
        s = s[:a] + NESTING + s[b:]
    for old, new in (('font-size="21.75"', 'font-size="37"'), ('font-size="23.2"', 'font-size="38"'), ('font-size="24.65"', 'font-size="38"')):
        s = s.replace(old, new)
    return s


GAME_TILE = ('source_3', 'A12069aW')   # untreated well A02 site 1; same 0.597976 µm/px as the old tile


def game_tile(deck):
    """Slide 03's third tile from a lab the classifier saw: one whole untreated source_3 field, kept in figures/assets."""
    asset = 'figures/assets/game-lab3-dna.png'
    if not os.path.exists(asset):
        from PIL import Image
        Image.open('cache/images/%s/%s/DNA.png' % GAME_TILE).convert('L').save(asset, optimize=True)
    uri = 'data:image/png;base64,' + base64.b64encode(open(asset, 'rb').read()).decode()
    m = re.search(r'<template id="t2">.*?</template>', deck, flags=re.S)
    s = re.sub(r'<img src="data:image/png;base64,[A-Za-z0-9+/=]+" alt="Untreated DMSO well, DNA channel, lab 4\."',
               lambda _: f'<img src="{uri}" alt="Untreated DMSO well, DNA channel, lab 3."', m.group(0), count=1)
    s = s.replace('>lab 4</span>', '>lab 3</span>')
    return deck[:m.start()] + s + deck[m.end():]


def mono(x, y, s, size, fill, anchor='start', weight=400):
    return f'<text x="{x:.1f}" y="{y:.1f}" {parts.SVG_MONO} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def chain_map(s):
    """Slide 03c's map: the same projection as slide 04, as tall as the figure band, the game's plate in pink and named
    by a pink pill set in the emptiest corner near it."""
    rows = slide04.embedding()
    plate = '1053600681'
    others = sorted({r['lab'] for r in rows if r['lab'] != 'source_2'}, key=parts.lab_number)
    colour = dict(zip(others, parts.greens(len(others))))
    W, H = 600, 440
    ax, cloud = slide04.map_axes(rows, 14, 14, W - 28, H - 28, pad=0.06)
    g = [f'<rect x="{ax.x0}" y="{ax.y0}" width="{ax.w}" height="{ax.h}" rx="12" fill="{parts.PANEL}"/>']
    g += [cloud([r for r in rows if r['lab'] == l][::3], colour[l], 2.6) for l in others]
    g.append(cloud([r for r in rows if r['lab'] == 'source_2' and r['plate'] != plate][::3], parts.PALE_PINK, 2.6))
    mine = [r for r in rows if r['plate'] == plate]
    g.append(cloud(mine, parts.PINK, 3.4))
    cx = sum(ax.X(float(r['pc1'])) for r in mine) / len(mine); cy = sum(ax.Y(float(r['pc2'])) for r in mine) / len(mine)
    pts = [(ax.X(float(r['pc1'])), ax.Y(float(r['pc2']))) for r in rows[::3]]
    pw, ph = 150, 34                                    # the pill goes where the fewest wells are, close to the plate
    best = None
    for x in range(int(ax.x0) + 12, int(ax.x0 + ax.w - pw - 12), 10):
        for y in range(int(ax.y0) + 12, int(ax.y0 + ax.h - ph - 50), 10):
            crowd = sum(1 for px, py in pts if x - 8 <= px <= x + pw + 8 and y - 8 <= py <= y + ph + 8)
            far = ((x + pw / 2 - cx) ** 2 + (y + ph / 2 - cy) ** 2) ** 0.5
            score = crowd * 40 + far
            if best is None or score < best[0]:
                best = (score, x, y)
    _, px, py = best
    ex = px + pw if cx > px + pw else (px if cx < px else cx); ey = py + ph if cy > py + ph else (py if cy < py else cy)
    g.append(f'<path d="M {ex:.0f} {ey:.0f} L {cx:.0f} {cy:.0f}" stroke="{parts.PINK}" stroke-width="2.5" stroke-linecap="round"/>')
    g.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="{ph / 2}" fill="{parts.PINK}"/>'
             + mono(px + pw / 2, py + 23, 'lab 2 &#183; you', 19, '#ffffff', 'middle', 600))
    g.append(mono(ax.x0 + 14, ax.y0 + ax.h - 14, 'PC 1 &#8594;', 16, parts.MUTE))
    g.append(f'<g transform="translate({ax.x0 + 22},{ax.y0 + ax.h - 40}) rotate(-90)">' + mono(0, 0, 'PC 2 &#8594;', 16, parts.MUTE) + '</g>')
    svg = parts.svg(W, H, g, fit=True, aria='Untreated wells from 11 labs as points, one shade of green per lab; this plate in pink, inside its own lab.')
    card = (f'<div class="chainmap" style="box-sizing: border-box; background:#ffffff; border-radius:14px; box-shadow: 0 1px 2px rgba(20,23,26,0.06), '
            f'0 12px 30px rgba(20,23,26,0.09); height:430px; padding:8px; display:flex; align-items:center;">{svg}</div>')
    return re.sub(r'<div (?:class="chainmap" )?style="box-sizing: border-box; background:#ffffff; border-radius:14px;[^"]*"><svg.*?aria-label="Untreated wells from 11 labs[^"]*".*?</svg></div>',
                  lambda _: card, s, count=1, flags=re.S)


def legends(deck):
    """Board A25 (the old pain slide) keeps a source line; the game (slide 03) keeps a one-line legend, written from results."""
    e1 = json.load(open('results/e1.json'))['all_sources']
    m = re.search(r'<template id="t35">.*?</template>', deck, flags=re.S)
    s = re.sub(r'(<div style="[^"]*display:block;">)(?:(?!</div>).)*?Freedman(?:(?!</div>).)*?(</div>)',
               r'\1[6] Freedman 2015\2', m.group(0), count=1, flags=re.S)
    att = ('<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:17px; line-height:1.5; color:#949c9f;">Attached: screenshot.png</span>')
    if att in s:                                                                                              # the attachment, shown
        src = re.search(r'<img src="([^"]+)" alt="Image search result: U2OS cells, JUMP 2023, lab 2\."', s).group(1)
        s = s.replace(att, f'<div style="display:flex; align-items:flex-end; gap:12px; margin-top:8px;">'
                      f'<img src="{src}" alt="Attached screenshot: U2OS cells, JUMP 2023, lab 2." style="width:120px; height:120px; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74; outline-offset:2px;">'
                      f'<span style="{MONO} font-size:13px; color:#666e72;">screenshot.png</span></div>')
    deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'<template id="t2">.*?</template>', deck, flags=re.S)
    s = re.sub(r'<span class="num"[^>]*>\d</span>', '', m.group(0))                                         # tile numbers
    s = re.sub(r'<div class="hint"[^>]*><span data-h="hint">[^<]*</span></div>', lambda _: parts.cue(3), s, count=1)   # dots, not words
    s = re.sub(r'(<div class="cite"[^>]*>).*?(</div>)',
               lambda k: (k.group(1) + '<span style="color:#14171a; font-weight:500;">fig 1</span> '
                          f'Cell Painting &#183; DNA channel &#183; {e1["n_wells"]:,} wells &#183; {e1["n_labs"]} labs &#183; plates held out &#183; bars 100 &#181;m &#183; JUMP [7] &#183; A2, A3' + k.group(2)),
               s, count=1, flags=re.S)
    s = re.sub(r'\s*<div class="others".*?(?=\s*<div class="picto")', '', s, count=1, flags=re.S)            # unsourced other-labs row
    s = re.sub(r'<circle cx="(?:64|1168)"[^>]*/>|<circle cx="[0-9.]+" cy="(?:10|340)"[^>]*/>', '', s)         # wells clamped to the frame
    bar = lambda v, c: (f'<div class="sbar" style="grid-column:1/-1; height:10px; margin-top:-8px; border-radius:5px; background:#eceeef;">'
                        f'<div style="width:{100 * v:.1f}%; height:100%; border-radius:5px; background:{c};"></div></div>')
    if 'class="sbar"' not in s:                                                                               # the 11-fold gap, drawn
        s = s.replace('>classifier</span></div>', '>classifier</span></div>' + bar(e1['balanced_accuracy'], '#0f8f6c'), 1)
        s = s.replace('>chance</span></div>', '>chance</span></div>' + bar(e1['chance'], '#c3c9cb'), 1)
    deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S)
    meta = json.loads(m.group(1))
    game = next(e for e in meta if e['name'] == 'Game')
    game['steps']['foot'] = ['', '', '']                     # the pink footer lines leave
    game['steps']['tag'] = ['The game'] * 3              # one tag a slide; the views speak for themselves
    game['steps']['you'] = ['you', 'lab 2 \u00b7 you', 'lab 2 \u00b7 you']
    game['steps'].pop('hint', None)                     # dots, not words
    return deck[:m.start(1)] + json.dumps(meta) + deck[m.end(1):]


A5_END = '<!--/a5-->'


def a5_pair(deck):
    """Board A5: two real untreated wells (labs 5 and 6) and their two readouts from results/a5-pair.json; without it, no claim."""
    m = re.search(r'<template id="t15">.*?</template>', deck, flags=re.S)
    s = m.group(0)
    R = json.load(open('results/a5-pair.json')) if os.path.exists('results/a5-pair.json') else None
    ok = bool(R and R['count_close'] and R['texture_differs'])
    tiles = ('figures/assets/a5-lab5.png', 'figures/assets/a5-lab6.png')
    if ok and all(os.path.exists(f) for f in tiles):         # the two tiles: the first two data-URI images in t15, lab 5 then lab 6
        it = iter('data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode() for f in tiles)
        s = re.sub(r'<img src="data:image/[^"]+"', lambda k: f'<img src="{next(it)}"', s, count=2)
        s = re.sub(r'<div style="position:absolute; left:6px; bottom:5px; display:flex; flex-direction:column; gap:2px;"><div style="width:[0-9.]+%;[^"]*"></div>'
                   r'<span[^>]*>100 &#181;m</span></div>', '', s)    # the new crops carry no pixel size, so no scale bar
    cell = lambda v, c='#14171a': f'<span style="{MONO} font-size:15px; color:{c}; text-align:center;">{v}</span>'
    row = lambda a, sym, sc, b, name: (f'<div style="display:grid; grid-template-columns:128px 28px 128px 1fr; column-gap:0; align-items:baseline; padding:6px 0; border-top:1px solid #d3d8da;">'
                                       f'{cell(a)}{cell(sym, sc)}{cell(b)}<span style="{MONO} font-size:13px; color:#666e72; padding-left:10px;">{name}</span></div>')
    rows = ('<div data-a5="pair">' + (row(f"{R['lab_5']['count']:.0f}", '&#8776;', '#666e72', f"{R['lab_6']['count']:.0f}", 'count')
                                       + row(f"{R['lab_5']['texture']:.2f}", '&#8800;', '#be1e74', f"{R['lab_6']['texture']:.2f}", 'texture')
                                       + f'<div style="{MONO} font-size:13px; line-height:1.5; color:#666e72; padding-top:8px; border-top:1px solid #d3d8da;">'
                                         f'count gap {R["count_diff"] / R["count_pooled_iqr"]:.1f}&#215; usual spread &#183; same<br>'
                                         f'texture gap {R["texture_diff"] / R["texture_pooled_iqr"]:.1f}&#215; usual spread &#183; different<br>'
                                         'usual spread: plate to plate, within one lab<br>texture: % of DNA signal in fine detail</div>' if ok else '')
            + '</div>' + A5_END)
    if '<div data-a5="pair">' in s:
        k0 = s.index('<div data-a5="pair">')
        k1 = s.index(A5_END, k0) + len(A5_END)
    else:                                                     # the hand-typed rows the pair replaces
        k0 = s.index('<div style="display:grid; grid-template-columns:96px 58px 58px 1fr')
        k1 = s.index('</div>', s.rindex('grid-template-columns:96px 58px 58px 1fr')) + len('</div>')
    s = s[:k0] + rows + s[k1:]
    key = ' &#183; results/a5-pair'
    if R and key not in s:
        s = s.replace(', inside nuclei</div>', ', inside nuclei' + key + '</div>', 1)
    elif not R:
        s = s.replace(key, '')
    head = 'Same count.<br><span style="color: #be1e74;">Different texture.</span>' if ok else 'Two ways to ask<br>one question.'
    s = re.sub(r'(<h2[^>]*>).*?(</h2>)', lambda k: k.group(1) + head + k.group(2), s, count=1, flags=re.S)
    return deck[:m.start()] + s + deck[m.end():]


PAGER = parts.PAGER_RE
TITLE = 'Datum Line &#183; Do my cells look normal?'
DESCRIPTION = ('Datum Line makes cell data from any lab comparable with any other lab&#8217;s. Labs put their cells on the map for free; '
               'companies that buy cell data pay for the certificate.')
PREVIEW = 'Confidence with controls: every plate you image, placed on the map.'
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700'
         '&family=IBM+Plex+Mono:ital,wght@0,400;0,500;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;1,8..60,400&display=swap">')


# One action for the whole talk: a click, the space bar, an arrow or a presenter's clicker shows the next view if the slide has
# one, and the next slide if not, so nobody has to remember which slides step. Back undoes one view at a time.
NAV = (
    ("""if(m.steps){st.classList.add('click');st.addEventListener('click',()=>advance(S));}""",
     """st.classList.add('click');st.addEventListener('click',e=>{if(!e.composedPath().some(n=>n.tagName==='A'))next(S.i);});"""),
    (r"""function advance(S){const n=(S.step+1)%(S.m.steps.tag.length);S.step=n;const r=S.root.querySelector('[class*="step-"]');
 r.className=r.className.replace(/step-\d/,'step-'+n);
 for(const k in S.m.steps) S.root.querySelectorAll('[data-h="'+k+'"]').forEach(e=>e.textContent=S.m.steps[k][n]);}""",
     r"""function views(S){return S.m.steps?S.m.steps.tag.length:1;}
function show(S,n){S.step=n;if(!S.m.steps)return;const r=S.root.querySelector('[class*="step-"]');
 r.className=r.className.replace(/step-\d/,'step-'+n);
 for(const k in S.m.steps) S.root.querySelectorAll('[data-h="'+k+'"]').forEach(e=>e.textContent=S.m.steps[k][n]);}
function go(t,end){t=Math.max(0,Math.min(secs.length-1,t));const S=secs[t];if(S.dirty){mount(S);S.dirty=false;}show(S,end?views(S)-1:0);
 tgt=t;last=Date.now();S.st.parentNode.scrollIntoView({behavior:'smooth',block:'center'});}
function next(i){const S=secs[i];if(S.step<views(S)-1)show(S,S.step+1);else if(i<secs.length-1)go(i+1);}
function prev(i){const S=secs[i];if(S.step>0)show(S,S.step-1);else if(i>0)go(i-1,true);}"""),
    ("""addEventListener('keydown',e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const k=e.key;let t=null;const base=(Date.now()-last<900&&tgt!==null)?tgt:cur();
 if(['ArrowDown','PageDown',' '].includes(k))t=base+1;else if(['ArrowUp','PageUp'].includes(k))t=base-1;
 else if(k==='ArrowRight'||k==='Enter'){const S=secs[(Date.now()-last<900&&tgt!==null)?tgt:cur()];if(S.m.steps){advance(S);e.preventDefault();}return;}
 else if(k==='Home')t=0;else if(k==='End')t=secs.length-1;
 if(t!==null){e.preventDefault();t=Math.max(0,Math.min(secs.length-1,t));tgt=t;last=Date.now();secs[t].st.parentNode.scrollIntoView({behavior:'smooth',block:'center'});}});""",
     """addEventListener('keydown',e=>{if(e.metaKey||e.ctrlKey||e.altKey)return;const k=e.key;const base=(Date.now()-last<900&&tgt!==null)?tgt:cur();
 if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(k)){e.preventDefault();next(base);}
 else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(k)){e.preventDefault();prev(base);}
 else if(k==='Home'){e.preventDefault();go(0);}else if(k==='End'){e.preventDefault();go(secs.length-1);}});"""),
)


def navigation(deck):
    for old, new in NAV:
        if new not in deck:
            assert deck.count(old) == 1, f'the deck script changed: {old[:50]}'
            deck = deck.replace(old, new)
    return deck


def page(deck):
    """The page around the slides: its title, the link preview and the line under the last slide. No date: the deck travels."""
    end = deck.index('</head>')
    head = deck[:end]
    for pat, new in ((r'<title>[^<]*</title>', f'<title>{TITLE}</title>'),
                     (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESCRIPTION}">'),
                     (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{TITLE}">'),
                     (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{PREVIEW}">'),
                     (r'(?:<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">)+', FONTS)):   # one font request, italics for the maths
        head, n = re.subn(pat, lambda _: new, head, count=1)
        assert n == 1, f'not in the head: {pat}'
    deck = head + deck[end:]
    foot = ('<div class="foot"><div>Kat Titterton &#183; San Francisco</div>'
            '<div>Evidence shown is public JUMP Cell Painting data (CC0). Click, or press the space bar or an arrow, for the next view or slide; scroll to browse.</div>'
            '<div><a href="docs/">Documents: white paper, product vision, roadmap, landscape, brand</a></div></div>')
    last = deck.rindex('</template>')             # the page footer sits after the slides, never inside one
    tail, n = re.subn(r'<div class="foot">.*?</div></div>', lambda _: foot, deck[last:], count=1, flags=re.S)
    assert n == 1, 'no footer after the slides'
    return deck[:last] + tail


def _template(deck, tid, fn):
    m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
    return deck[:m.start()] + fn(m.group(0)) + deck[m.end():]


A16_LIGHT = ((parts.DARK_BG, parts.LIGHT_BG),
             ('position:relative; overflow:hidden;">', 'position:relative; z-index:0; overflow:hidden;">' + parts.watermark('A16')),
             ('box-sizing:border-box; background:rgba(246,247,247,.05); border:1px solid rgba(246,247,247,.14); border-radius:14px;', parts.CARD),
             ('border-top:1px solid rgba(246,247,247,.14)', 'border-top:1px solid ' + parts.GRID),
             ('color:#f6f7f7', 'color:' + parts.INK), ('color:#c9cfd1', 'color:' + parts.INK2), ('color:#949c9f', 'color:' + parts.MUTE),
             ('color:#3fe0a0', 'color:' + parts.GREEN), ('color:#ef74ad', 'color:' + parts.PINK))


def board_a16(s):
    """Board A16: one line under each instrument, and the board on the light ground of the other boards."""
    s = s.replace('<div style="aspect-ratio:1; width:100%; border-radius:8px; overflow:hidden; background:#000;">',     # the six labs' wells,
                  '<div style="aspect-ratio:1/2; width:100%; border-radius:8px; overflow:hidden; background:#000;">')   # tall enough to fill their card
    s = re.sub(r'<br>NA [0-9.]+ (?:·|&#183;) [0-9.]+ (?:µ|&#181;)m(?:/px)?', '', s)
    for old, new in A16_LIGHT:
        s = s.replace(old, new)
    return s


def apply(deck):
    report = []
    for tid, pairs in list(WORDS.items()) + list(TRIM.items()):
        m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
        s = m.group(0)
        for old, new in pairs:
            n = 0 if (new and new in s) else s.count(old)      # an edit whose result contains its input is still made once; an empty result removes
            if n:
                s = s.replace(old, new); report.append(f'{tid}: {n} x "{old[:40]}"')
        deck = deck[:m.start()] + s + deck[m.end():]
    for k in range(parts.N_TALK):
        m = re.search(r'<template id="t%d">.*?</template>' % k, deck, flags=re.S)
        s, n = PAGER.subn(lambda _: parts.dots(k + 1, dark=k in DARK), m.group(0), count=1)
        assert n == 1, f'no pager on slide {k + 1}'
        deck = deck[:m.start()] + s + deck[m.end():]
    deck = _template(deck, 't1', lambda s: reveal(founder(s)))
    m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S)
    meta = json.loads(m.group(1))
    next(e for e in meta if e['name'] == 'Founder')['steps'] = FOUNDER_STEPS
    deck = deck[:m.start(1)] + json.dumps(meta) + deck[m.end(1):]
    deck = _template(deck, 't11', board_a1)
    deck = game_tile(deck)
    deck = legends(deck)
    deck = _template(deck, 't26', board_a16)
    deck = a5_pair(deck)
    deck = _template(deck, 't2', chain_map)
    deck = deck.replace(OLD_SVG_FONT, parts.SVG_FONT)       # hand-built charts (t2, t11, t16, ...) use the builders' face
    deck = navigation(deck)
    deck = page(deck)
    return deck, report
