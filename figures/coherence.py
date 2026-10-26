"""One word for one thing, figures numbered in order, one pager, pointers to the appendix,
and little text: legends only under scientific figures, one line each. Detail lives in the
speaker script.

Applied after the slides are written. Every edit is a no-op once made, so it can be re-run.
"""
import base64
import json
import os
import re

import appendix
import parts
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
NOTE_LINE = f'<div style="{MONO} font-size: 13px; line-height: 1.5; color: #666e72;">'     # a board's one source line, at the bottom left
A1_FIG = '<span style="color: #14171a; font-weight: 500;">Fig. A1</span> &#183; left: JUMP plate 1053601756, lab 2 &#183; right: schematic, no measurements'
# A1's last row: the takeaway, in a card beside the arithmetic (it floated in the empty half), and the caption on the board's source line
A1_TAIL = ('<div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: center; gap: 6px;">\n'
           f'      <div style="{MONO} font-size: 15px; line-height: 1.45; color: #be1e74;">Seeing a sick plate takes a view from outside it.</div>\n'
           f'      <span style="{MONO} font-size: 13px; line-height: 1.5; color: #666e72;">{A1_FIG}</span>\n    </div>\n  </div>')
A1_SEE = (f'<div style="flex-grow: 1; {parts.CARD} padding: 12px 22px; display: flex; flex-direction: column; justify-content: center; gap: 6px;">'
          + parts.label('what can see a sick plate?', parts.GREEN)
          + f'<span style="{SANS} font-size: 18px; line-height: 1.4; color: #14171a;">A view from outside the plate.<br>'
            'Same cells in other labs: <span style="color: #0f8f6c;">the map</span>.</span></div>\n  </div>\n  ' + NOTE_LINE + A1_FIG + '</div>')
A2_FOOT = ('<div style="display: flex; justify-content: space-between; align-items: baseline; gap: 24px;">\n'
           f'    <div style="{MONO} font-size: 15px; line-height: 1.45; color: #454c50;"><span style="color: #0f8f6c;">drug discovery</span> &#183; remove the lab first<br>'
           '<span style="color: #be1e74;">quality check</span> &#183; keep the lab: it is the signal</div>\n'
           f'    <span style="{MONO} font-size: 13px; color: #666e72; white-space: nowrap;">results/e1, e1-redteam, e1b, e6 &#183; e5 pending &#183; [1] Ewald et al. 2026</span>\n  </div>')
A2_24 = ("remove known causes</span><span style=\"font-family: 'Archivo', 'Helvetica Neue', Helvetica, sans-serif; font-size: 22px; font-weight: 700; "
         "letter-spacing: -0.02em; color: #454c50; white-space: nowrap;\">24%</span>")      # A2 card 5's corner: plate-centring, not the formula
A2_PEND = "remove known causes</span><span style=\"font-family: 'IBM Plex Mono', Menlo, monospace; font-size: 13px; color: #666e72; white-space: nowrap;\">pending</span>"
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
           ('>founding MTS</span>', '>founding scientist</span>'), ('>Xenopus oocytes</span>', '>frog eggs</span>'),   # plain words
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
           # the bio at a size the room can read
           ('font-size:14px; color:#454c50;">', 'font-size:17px; color:#454c50;">'),
           ('font-size:14px; color:#666e72; white-space:nowrap;">', 'font-size:16px; color:#666e72; white-space:nowrap;">'),
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
    't26': [('font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color:#0f8f6c;">proposed &#183; $120k planned &#183; A21<', 'font-size: 13px; letter-spacing: 0.06em; color:#666e72;">proposed &#183; $120k planned &#183; A21<'),
            ('Across the 13 JUMP sites.', 'Across the 13 JUMP labs.')],
    't9': [('3-site proof, then the set', '3-lab proof, then the set')],
    't10': [('Every number traces to results/e1, e1b, e2 or a numbered reference', 'Every number traces to a file in results/ or a numbered reference'),
            ('padding:52px 56px 46px; display:flex; flex-direction:column; gap:20px;', 'padding:52px 56px 44px; display:flex; flex-direction:column; gap:14px;'),
            ('font-size:42px; font-weight:600; letter-spacing:-0.03em; line-height:1.05;', 'font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05;'),
            ('width:520px; flex-shrink:0;">The rest,', 'width:371px; flex-shrink:0;">The rest,'),
            ('The rest, <span style="color:#be1e74;">if you ask.</span>', 'The rest, <span style="color:#0f8f6c;">for questions.</span>'),   # no "you" in a headline; pink is lab 2
            ('<div style="display:flex; gap:40px; align-items:baseline;"><h2', '<div style="display:flex; gap:28px; align-items:baseline;"><h2'),
            ('font-size:18px; line-height:1.4; color:#666e72; flex-grow:1;">Find the question, jump to the board. Every number traces to a file in results/ or a numbered reference; pending work says pending.',
             'font-size:19px; line-height:1.4; color:#666e72; flex-grow:1;">Every number traces to results/ or a numbered reference.<br>Pending work says pending.'),
            ('Every number traces to results/ or a numbered reference.<br>Pending work says pending.', 'Every number comes from the code here or a cited source.<br>Unfinished work is marked pending.')],
    't11': [('font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color: #0f8f6c;">one real plate &#183; one schematic<', 'font-size: 13px; letter-spacing: 0.06em; color: #666e72;">one real plate &#183; one schematic<'),
            ('>site</text>', '>lab</text>'),
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
             '<span style="color: #be1e74;">plate</span> cancels from the number, never from the cells'),
            # one grammar with the other boards: two statements on two lines; "normal" is relative, so quoted; nothing floats
            ('flex-shrink: 0;">Sick plate, sick control.</h2>', 'flex-shrink: 0;">Sick plate.<br><span style="color: #be1e74;">Sick control.</span></h2>'),
            ('<span>test = normal + <span class="s"', '<span>test = &#8220;normal&#8221; + <span class="s"'),
            ('<span>control = normal + <span class="s"', '<span>control = &#8220;normal&#8221; + <span class="s"'),
            (A1_TAIL, A1_SEE)],
    't12': [('font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color: #0f8f6c;">How the numbers are made<', 'font-size: 13px; letter-spacing: 0.06em; color: #666e72;">how the numbers are made<'),
            ('V<sub>site</sub>', 'V<sub>lab</sub>'),
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
            ('>5 &#183; regress variables out</span>', '>5 &#183; remove known causes</span>'),
            (A2_24, A2_PEND),                                                                    # the formula was never run ('>6 &#183; morphology change, two ways</span>', '>6 &#183; did the drug change the cells?</span>'),
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
             '<span style="color: #0f8f6c;">drug discovery</span> &#183; remove the lab first<br><span style="color: #be1e74;">quality check</span> &#183; keep the lab: it is the signal'),
            # one grammar with the other boards: two statements on two lines, the lede beside them, one source line at the foot
            ('flex-shrink: 0;">Six calculations, one well.</h2>',
             f'flex-shrink: 0;">One well, {E1["n_features"]:,} numbers.<br><span style="color: #be1e74;">Six calculations.</span></h2>'),
            (f'font-size: 18px; line-height: 1.4; color: #666e72; flex-grow: 1;">Each well becomes {E1["n_features"]:,} numbers.<br>Each result compares averages, or tests a model on unseen plates.</p>',
             'font-size: 19px; line-height: 1.45; color: #666e72; flex-grow: 1;">Results compare averages, or test a model on unseen plates.<br>'
             '<span style="color: #0f8f6c;">Drug discovery</span> removes the lab; <span style="color: #be1e74;">a quality check</span> reads it.</p>'),
            (A2_FOOT, NOTE_LINE + 'results/e1, e1-redteam, e1b, e6 &#183; e5 pending &#183; [1] Ewald et al. 2026</div>'),
            ('>3 &#183; how far from normal?</span>', '>3 &#183; how far from &#8220;normal&#8221;?</span>'),
            ('in units of normal spread.<br>', 'in units of usual spread.<br>')],                    # A5's word for plate-to-plate spread
    't13': [('background:#be1e74;"></div><span style="position:absolute; left:calc(99.83%', 'background:#454c50;"></div><span style="position:absolute; left:calc(99.83%'),
            ('white-space: nowrap;">site</span>', 'white-space: nowrap;">lab</span>'),
            # the dose: one lab ran compounds at 1/16 and the per-well metadata does not say so [7]
            ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 14px; padding: 4px 9px; border-radius: 999px; border: 1.5px solid #be1e74; color: #14171a; white-space: nowrap;">CO2 and humidity</span></div>', '<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 14px; padding: 4px 9px; border-radius: 999px; border: 1.5px solid #be1e74; color: #14171a; white-space: nowrap;">CO2 and humidity</span><span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size: 14px; padding: 4px 9px; border-radius: 999px; border: 1.5px solid #be1e74; color: #14171a; white-space: nowrap;">compound dose</span></div>'),
            ('font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color: #0f8f6c;">results/e1-redteam<', 'font-size: 13px; letter-spacing: 0.06em; color: #666e72;">results/e1-redteam<'),
            ('left:calc(99.83% + 8px); top:50%; transform:translateY(-50%); font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:28px; font-weight:700; letter-spacing:-0.02em; line-height:1; color:#be1e74;',
             'left:calc(99.83% + 8px); top:50%; transform:translateY(-50%); font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:28px; font-weight:700; letter-spacing:-0.02em; line-height:1; color:#454c50;'),   # pink is you
            # what travels with any image, and what nobody is asked for today
            ('white-space: nowrap;">CellProfiler version</span></div>\n    </div>',
             'white-space: nowrap;">CellProfiler version</span></div>\n      ' + A3_NOTE + 'in every image file too:<br>image size &#183; stored bit depth</span>\n    </div>'),
            ('white-space: nowrap;">CO2 and humidity</span></div>\n    </div>',
             'white-space: nowrap;">CO2 and humidity</span></div>\n      ' + A3_NOTE + 'not required to publish today<br>in our own data: tracked, every one</span>\n    </div>'),
            ('image size &#183; bit depth &#183; pixel size</span>', 'image size &#183; stored bit depth</span>'),   # pixel size is optional in the format; the earlier wording
            ('not required to publish today [15]<br>', 'not required to publish today<br>'),   # [15] is about images, not culture variables
            ('white-space: nowrap;">sites per well</span>', 'white-space: nowrap;">fields per well</span>'),
            ("<p style=\"margin: 0; font-family: 'Source Serif 4', Georgia, serif; font-size: 18px; line-height: 1.4; color: #666e72;\">Normal is a conditional expectation, <span style=\"font-family: 'Source Serif 4', Georgia, serif; font-style: italic; color: #14171a;\">E[x | every variable below]</span>. Even JUMP, built to be comparable, records only the instrument side.</p>",
             f"<p style=\"margin: 0; {SANS} font-size: 19px; line-height: 1.4; color: #666e72;\">Normal is <span style=\"{MATH} color: #14171a;\">E[x | every variable below]</span>.</p>"),
            ('Centre each plate on its own controls, the standard first step, and the lab is named 24% of the time. It removes most of the coordinate a certificate needs.',
             'Centring each plate on its own controls is the standard first step.<br>It removes most of the coordinate a certificate needs.'),
            ('Batch correction is built to remove this signal: Arevalo J, et al., Nature Communications, 2024. Variables: JUMP datasets metadata.',
             'Batch correction is built to remove this signal [18] &#183; variables: JUMP metadata [7]'),
            ('padding: 52px 56px 48px; display: flex; flex-direction: column; gap: 16px;', 'padding: 52px 56px 44px; display: flex; flex-direction: column; gap: 14px;'),
            ('font-size: 13px; letter-spacing: 0.11em;', 'font-size: 14px; letter-spacing: 0.1em;'),
            ('A3 &#183; if asked why not batch-correct</span></div>',
             f'A3 &#183; if asked why not batch-correct</span><span style="{MONO} font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color: #0f8f6c;">results/e1-redteam</span></div>'),
            ('font-size: 13px; padding: 4px 9px;', 'font-size: 14px; padding: 5px 10px;'), ('font-size: 13px; padding: 3px 8px;', 'font-size: 14px; padding: 4px 9px;'),
            ('<div style="display: flex; flex-wrap: wrap; gap: 6px;">', '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'),
            ('<span style="color: #be1e74;">What nobody does.</span>', '<span style="color: #be1e74;">What it leaves out.</span>'),
            (f'Normal is <span style="{MATH} color: #14171a;">E[x | every variable below]</span>.', 'What counts as normal depends on every variable below.'),
            ('Centring each plate on its own controls is the standard first step.<br>It removes most of the coordinate a certificate needs.',
             'Standard first step: subtract each plate&#8217;s own controls.<br>It erases most of the lab fingerprint a certificate reads.'),
            # one grammar with the other boards: two statements on two lines, the lede beside them; the answer moves from the floor to the lede
            ('<div style="display: flex; flex-direction: column; gap: 8px;">\n    <h2', '<div style="display: flex; gap: 40px; align-items: baseline;">\n    <h2'),
            ('line-height: 1.05; color: #14171a;">What JUMP records. <span style="color: #be1e74;">What it leaves out.</span></h2>',
             'line-height: 1.05; color: #14171a; width: 560px; flex-shrink: 0;">What JUMP records.<br><span style="color: #be1e74;">What it leaves out.</span></h2>'),
            ('font-size: 19px; line-height: 1.4; color: #666e72;">What counts as normal depends on every variable below.</p>',
             'font-size: 19px; line-height: 1.45; color: #666e72; flex-grow: 1;">What counts as &#8220;normal&#8221; depends on every variable below.<br>'
             'Standard correction erases most of what a certificate reads.</p>'),
            ('Batch correction is built to remove this signal: Arevalo et al., Nat Commun 2024', 'Batch correction is built to remove this signal [18]'),   # reference 18
            ('depends on every variable below.<br>Standard correction erases most of what a certificate reads.</p>',
             'depends on every variable below.<br>JUMP records the left column; nobody records the middle.</p>'),   # the lede adds, the headline says
            (f'\n  <div style="{MONO} font-size: 15px; line-height: 1.45; color: #be1e74;">Standard first step: subtract each plate&#8217;s own controls.<br>'
             'It erases most of the lab fingerprint a certificate reads.</div>', ''),
            ('<div style="display: flex; flex-wrap: wrap; gap: 8px;">', '<div style="display: flex; flex-wrap: wrap; gap: 10px;">')],          # the chips fill the taller cards
    't15': [('font-weight: 500;">Fig. 1</span>', 'font-weight: 500;">Fig. A5</span>'),
            # the mini-figures' words, rewritten here before TRIM looks for the whole FIG1 and FIG2, or a second figure goes in
            ('>cells, not the day</figcaption>', '>removes day-to-day shifts</figcaption>'),
            ('>one wild well can&#8217;t swamp it</figcaption>', '>one odd well cannot dominate</figcaption>'), ('>vehicle</text>', '>untreated</text>'),
            ('line-height: 1.05; color: #14171a; width: 540px; flex-shrink: 0;">', 'line-height: 1.05; color: #14171a; width: 560px; flex-shrink: 0;">')],   # the lede on A1-A4's line
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

E1B = parts.results('e1b-drift-source_2.json')
DRIFT = {b['gap']: b for b in E1B['bins']}   # A6 (t16) quotes its ratios, its lab and its dates from here


PLAYGROUND_K = next(k for name, _, k in appendix.PRESEED if name == 'benchmark playground')   # A16's tag quotes A21's line
PLAYGROUND = {'lines': ('U2OS', 'A549', 'HepG2', 'iPSC'), 'microscopes': ('widefield', 'confocal')}   # proposed; as on slide 09; lines [17]


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
           # the room must read these: the lab chips, the two nouns beside the numbers, the pipeline words
           ("monospace; font-size:13px; opacity:0;", "monospace; font-size:16px; opacity:0;"),
           ('left:9px; top:9px; padding:4px 9px;', 'left:9px; top:9px; padding:5px 11px;'),
           ('font-size:15px; letter-spacing:.08em; text-transform:uppercase; color:#454c50;">classifier', 'font-size:18px; letter-spacing:.08em; text-transform:uppercase; color:#454c50;">classifier'),
           ('font-size:15px; letter-spacing:.08em; text-transform:uppercase; color:#666e72;">chance</span>', 'font-size:18px; letter-spacing:.08em; text-transform:uppercase; color:#666e72;">chance</span>'),
           ('font-size:18px; letter-spacing:.08em; text-transform:uppercase; color:#454c50;">classifier &#183; 11 labs</span>', SANS + ' font-size:18px; color:#454c50;">names the right lab, of 11</span>'),   # nouns, not labels
           ('font-size:18px; letter-spacing:.08em; text-transform:uppercase; color:#666e72;">chance</span>', SANS + ' font-size:18px; color:#666e72;">a random guess</span>'),
           ('font-size:13px; color:#666e72; text-align:center; line-height:1.4;">3,773<br>numbers', 'font-size:17px; color:#666e72; text-align:center; line-height:1.4;">3,773<br>numbers'),
           ('font-size:13px; color:#be1e74;">one point</span>', 'font-size:17px; color:#be1e74;">one point</span>'),
           # one ink for the headlines; the classifier's 99.9% is the problem, not a win, so it is not green
           ('Could you tell?<br><span style="color:#0f8f6c;">Classifiers can.</span>', 'Could you tell?<br>A classifier can.'),
           ('One well, <span style="color:#0f8f6c;">onto the map.</span>', 'One well, onto the map.'),
           ('line-height:.9; color:#0f8f6c;">99.9%</span>', 'line-height:.9; color:#14171a;">99.9%</span>'),
           ('height:100%; border-radius:5px; background:#0f8f6c;"></div></div>', 'height:100%; border-radius:5px; background:#454c50;"></div></div>'),
           ('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#f6f7f7; opacity:.92; line-height:1;">20 &#181;m</span>',
            '<span class="pdf" style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#f6f7f7; opacity:.92; line-height:1;">20 &#181;m</span>'),
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
           ('<div class="picto" style="position:absolute; left:720px; top:236px; display:flex; flex-direction:column; gap:26px;">',
            '<div class="picto" style="position:absolute; left:720px; top:206px; height:396px; display:flex; flex-direction:column; justify-content:center; gap:36px;">'),
           ('width="34" height="34"', 'width="40" height="40"'),
           ('font-size:28px; font-weight:500; letter-spacing:-0.015em; color:#14171a;">', 'font-size:30px; font-weight:500; letter-spacing:-0.015em; color:#14171a;">'),
           ('font-size:22px; color:#0f8f6c;">&#10003;', 'font-size:24px; color:#0f8f6c;">&#10003;'),
           ('>same line</span>', '>same cells</span>'),
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
            ('fill="#be1e74">4.70</text>', f'fill="#be1e74">4.70</text><path d="M 1336 296.9 L 1336 100.2 M 1328 298.9 L 1344 298.9 M 1328 98.2 L 1344 98.2" stroke="#be1e74" stroke-width="2" fill="none"/><text x="1352" y="207" {parts.SVG_FONT} font-size="26" font-weight="700" fill="#be1e74">&#215;{DRIFT["over 13 weeks"]["ratio_to_same_batch"]:.1f}</text>'),
            ('Not known from profiles alone. The data says the lab moved and when. It does not say why.', 'Unknown from profiles.<br>Data shows when the lab moved, not why.'),
            ('>So why re-certify?<', '>How often?<'),
            ('Because your certificate is a comparison made on one day, and the baseline it was made against goes stale within weeks.', 'At least every quarter.<br>Distance &#215;4.9 by 6 to 13 weeks.'),
            ('One lab, 219 plates, 13 batches, June to October 2021. 0.63 in the same batch, 4.7 over 13 weeks. Other labs are not yet measured.', 'One lab, 219 plates, 13 batches.<br>Other labs not yet measured.'),
            ('font-size: 16px; line-height: 1.32; color: #14171a;', 'font-size: 18px; line-height: 1.35; color: #14171a;'),
            ('Two plates of one lab sit further apart the longer the gap between them. In lab 2 the distance is still rising after thirteen weeks.', 'Plates of one lab drift apart with time.<br>Still rising after 13 weeks.'),
            ('Plates of one lab drift apart with time.<br>Still rising after 13 weeks.', 'Plates of one lab drift apart within two weeks.<br>The jump past 13 weeks is lab 2&#8217;s autumn move (A13).'),
            ('Plates of one lab drift apart within two weeks.<br>The jump past 13 weeks is lab 2&#8217;s autumn move (A13).',
             f'Two plates from one batch differ by {DRIFT["same batch"]["median"]}; two weeks apart, {DRIFT["1 to 14 days"]["median"]}.<br>The jump past 13 weeks is lab 2&#8217;s autumn move (A13).'),
            ('font-size: 42px; font-weight: 600;', 'font-size: 44px; font-weight: 600;'),
            ('font-size: 18px; line-height: 1.4; color: #666e72; flex-grow: 1;', 'font-size: 19px; line-height: 1.45; color: #666e72; flex-grow: 1;'),
            ('with the interquartile range. results/e1b-drift.</div>', 'with the interquartile range.</div>'),
            ('with the interquartile range.</div>', 'with the interquartile range &#183; 4,723 features, lab 2&#8217;s own set; A13 uses the field&#8217;s 3,773.</div>'),
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
            ('Unknown from profiles.<br>Data shows when the lab moved, not why.', 'This data cannot tell.<br>It shows when the lab moved, not why.'),
            # "normal" is relative: the baseline a lab is compared against is its "normal"; the pink line is lab 2, the lab the talk follows
            ('Your baseline expires.<br><span style="color: #be1e74;">', 'Your &#8220;normal&#8221; expires.<br><span style="color: #be1e74;">'),
            ('<rect x="110" y="30" width="1320" height="300" fill="#eceeef"/>',
             f'<rect x="110" y="30" width="1320" height="300" fill="#eceeef"/><text x="134" y="74" {parts.SVG_FONT} font-size="26" font-weight="700" fill="#be1e74">'
             f'{parts.lab_name(E1B["lab"])}, you</text><text x="134" y="104" {parts.SVG_FONT} font-size="20" fill="#454c50">'
             f'{parts.short_date(E1B["first_batch"])} to {parts.short_date(E1B["last_batch"])} {E1B["last_batch"][:4]}</text>'),
            # the headline says how often; the card says how fast, in the chart's own unit (times the same-batch distance)
            ('>How often?<', '>How fast?<'),
            (f'At least every quarter.<br>By 6 to 13 weeks: &#215;{DRIFT["6 to 13 weeks"]["ratio_to_same_batch"]:g} vs same batch.',
             f'Within 2 weeks: &#215;{DRIFT["1 to 14 days"]["ratio_to_same_batch"]:.1f} vs same batch.<br>6 to 13 weeks: &#215;{DRIFT["6 to 13 weeks"]["ratio_to_same_batch"]:.1f}.'),
            ('This data cannot tell.<br>It shows when the lab moved, not why.', f'This data shows when, not why.<br>What moved in {parts.lab_name(E1B["lab"])}: A12.'),
            ('Dot: median plate pair. Bar: middle half of pairs.<br>1 = how far a typical untreated well sits from its plate&#8217;s average.',
             'dot = median pair of plates &#183; bar = middle half of pairs &#183; 1 = how far a typical untreated well sits from its plate&#8217;s average &#183; JUMP [7]')],
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
           ('Same cells, same protocol, no drug.<br>It already looks like this.', 'Same cells, same protocol, no drug.<br>Still, each lab looks different.'),
           # the answer first: two statements as the headline, what the money builds as the lede; the cards are the reasons
           ('width:560px; flex-shrink:0;">Build the ugliest dataset<br>in biology, <span style="color:#be1e74;">on purpose.</span></h2>',
            'width:560px; flex-shrink:0;">Ugliest dataset in biology.<br><span style="color:#be1e74;">On purpose.</span></h2>'),
           ('Same cells, same protocol, no drug.<br>Still, each lab looks different.',
            f'{len(PLAYGROUND["lines"])} cell lines &#215; {len(PLAYGROUND["microscopes"])} microscope types &#215; known drugs<br>+ planted faults. Every correction method scored.'),
           ('color:#0f8f6c;">public data today · six labs</span>', 'color:#0f8f6c;">today &#183; same cells, same protocol, no drug</span>'),
           ('text-transform:uppercase; color:#14171a;">lab 2</span>', 'text-transform:uppercase; color:#be1e74;">lab 2 &#183; you</span>'),   # pink is you, as on 03-07
           ('>planted on purpose<', '>planted faults<'),        # the lede's words; 'on purpose' is the headline's
           ('color:#0f8f6c;">If someone wrote the cheque</span>', f'color:#0f8f6c;">proposed &#183; ${PLAYGROUND_K}k planned &#183; A21</span>'),
           # the question sits on a rule level with the numbers' rule on the left card, so no empty band opens above it
           (f'<span style="{SANS} font-size:17px; line-height:1.3; color:#14171a; margin-top:auto;">Can a model name the fault?</span>',
            f'<div style="margin-top:auto; height:61px; box-sizing:border-box; border-top:1px solid #d3d8da; padding-top:10px; display:flex; align-items:flex-end;">'
            f'<span style="{SANS} font-size:17px; line-height:1.3; color:#14171a;">Can a model name the fault?</span></div>'),
           (f'<div style="{MONO} font-size:14px; line-height:1.45; color:#454c50; white-space:nowrap;"><span style="color:#0f8f6c;">playground</span> &#183; U2OS, A549, HepG2, iPSC [17] &#183; widefield and confocal &#183; known drugs &#183; planted faults &#183; every correction scored</div>',
            f'<div style="{MONO} font-size:13px; line-height:1.5; color:#666e72; white-space:nowrap;">cell lines: {", ".join(PLAYGROUND["lines"])} [17] &#183; microscope types: {" + ".join(PLAYGROUND["microscopes"])}</div>')],
    't35': [('font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase; color:#0f8f6c;">public sources [6], [7], [9]<', 'font-size: 13px; letter-spacing: 0.06em; color:#666e72;">public sources [6], [7], [9]<'),
            ('class="p1" style="flex:0 0 36%; box-sizing:border-box; background:#be1e74;', 'class="p1" style="flex:0 0 36%; box-sizing:border-box; background:#454c50;'),   # pink is you
            ('&#8220;Do my cells <span style="color:#be1e74;">look normal?</span>&#8221;</h2>', 'Today: <span style="color:#be1e74;">search, ask, guess.</span></h2>'),
            ('<div style="height:112px; border-radius:6px; overflow:hidden; background:#000;">', '<div style="height:94px; border-radius:6px; overflow:hidden; background:#000;">'),   # six tiles, under the footer
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
           ('A25 &#183; if asked how labs answer it today', 'A25 &#183; if asked how labs check cells today'),
           # two statements, two lines; "normal" is relative, so it is quoted; the map is green; no empty bands in cards 2 and 3
           ('Today: <span style="color:#be1e74;">search, ask, guess.</span></h2>',
            'Today: search, ask, guess.<br><span style="color:#be1e74;">Each lab judges &#8220;normal&#8221; alone.</span></h2>'),
           ('>do my U2OS cells look normal</span>', '>do my U2OS cells look &#8220;normal&#8221;</span>'),
           ('height:2px; background:linear-gradient(90deg,#0f8f6c,#be1e74);"></div>', 'height:2px; background:#0f8f6c;"></div>'),   # unique, or apply() skips it
           ('background:#be1e74;"></div><span style="' + MONO + ' font-size:13px; color:#be1e74;">2026</span><br>'
            '<span style="' + SANS + ' font-size:15px; line-height:1.3; color:#454c50;">the map</span>',
            'background:#0f8f6c;"></div><span style="' + MONO + ' font-size:13px; color:#0f8f6c;">2026</span><br>'
            '<span style="' + SANS + ' font-size:15px; font-weight:600; line-height:1.3; color:#0f8f6c;">the map</span>'),
           ('padding:18px 18px; display:flex; flex-direction:column; gap:4px;">', 'padding:18px 18px; display:flex; flex-direction:column; gap:4px; flex:1; min-height:0;">'),
           ('<div style="display:flex; align-items:flex-end; gap:12px; margin-top:8px;">', '<div style="display:flex; align-items:flex-end; gap:12px; margin-top:auto;">'),
           ('style="width:150px; height:150px; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74;',
            'style="width:120px; height:120px; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74;'),   # the cards end above the footer
           ('>screenshot.png</span></div></div>\n\n</div>',
            '>screenshot.png</span></div></div>'
            '<span style="' + SANS + ' font-size:15px; line-height:1.3; color:#454c50; margin-top:auto;">one screenshot &#183; one opinion</span>\n</div>'),
           ('line-height:1.3; color:#454c50;">one cell line &#183; six papers &#183; all look different</span>',      # the two captions on one baseline
            'line-height:1.3; color:#454c50; margin-top:auto;">one cell line &#183; six papers &#183; all look different</span>'),
           ('gap:3px; padding:8px 0 8px 14px; margin-top:4px; border-left:3px solid', 'gap:3px; padding:8px 0 8px 14px; margin-top:4px; flex:1; justify-content:center; border-left:3px solid')],
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
    s = re.sub(r'<span((?:(?!class=)[^>])*)>My work</span>', lambda m: f'<span class="pdf"{m.group(1)}>My work</span>', s, count=1)   # the list is the handout's; the logos carry the stage
    a = s.index('My work</span>') + len('My work</span>')
    if '<!--/refs-->' in s:
        b = s.index('<!--/refs-->') + len('<!--/refs-->')
    else:                                          # first run: up to the end of the 'published with' block
        b = s.index('</div>', s.index('Uppsala</span>', a)) + len('</div>')
    rows = ''.join(
        f'<div class="ref pdf" style="animation-delay:{0.45 + 0.06 * k:.2f}s; display:grid; grid-template-columns:18px 1fr; column-gap:12px; align-items:baseline;">'
        f'<span style="{MONO} font-size:13px; color:#666e72; text-align:right;">{k + 1}</span>'
        f'<span style="{SANS} font-size:17px; line-height:1.28; color:#14171a;">{title}<br>'
        f'<span style="{MONO} font-size:14px; color:#666e72;"><em>{journal}</em> {year} &#183; {first}, {where}</span></span></div>'
        for k, (title, journal, year, first, where) in enumerate(PAPERS))
    return s[:a] + '\n      ' + rows + '<!--/refs-->' + s[b:]


# 25 Oct 2026, "founder slide: less text, focus on institutions and skills, show expertise with publications and patent".
# Each row keeps its institution and years and names one skill; three tiles carry the record. Counts: the papers from PAPERS,
# the compounds from the CV (macrofluidic.me/resume: two Cell Painting datasets, 100,000+ compounds), the patent applications
# filed at Axiom Bio (count to be confirmed by Kat; None shows the icon alone).
SKILLS = {'founding scientist': 'cell imaging, AI', 'neuroscience assays': 'automated screening', 'expansion microscopy': 'expansion microscopy',
          'tau, neurons': 'neuron assays', 'frog eggs': 'electrophysiology', 'neuroscience + math biology': 'neuroscience, math'}
SKILL_ICONS = {'cell imaging, AI': 'measure', 'automated screening': 'plate', 'expansion microscopy': 'microscope', 'neuron assays': 'neuron',
               'electrophysiology': 'spike', 'neuroscience, math': 'degree'}       # one drawn noun before each skill
COMPOUNDS_IMAGED = '100,000+'
FT_CSS = '.ft{transition:opacity .4s ease}.step-1 .ft,.step-2 .ft{opacity:0}'
PATENT_APPLICATIONS = 2                        # Kat, 25 Oct 2026: two filed at Axiom Bio, fine to show


def founder_tiles(s):
    """02a: institutions, years and one skill each on the timeline; three small tiles (papers, patent applications, compounds
    imaged) under the photo, where they fit on stage and leave the right column to the PDF's paper list."""
    for old, new in SKILLS.items():
        s = s.replace(f'font-size:17px; color:#454c50;">{old}</span>', f'font-size:17px; color:#454c50;">{new}</span>')
    s = s.replace('text-transform: uppercase; color:#949c9f;">Harvard Medical School</span>', 'text-transform: uppercase; color:#949c9f;">MGH</span>')
    for skill, name in SKILL_ICONS.items():                  # an icon before each skill, at the stage floor; once, since the 17px span is gone after
        s = s.replace(f'padding-top:2px;"><span style="{MONO} font-size:17px; color:#454c50;">{skill}</span>',
                      f'padding-top:2px;">{parts.icon(name, "#454c50", 20)}<span style="{MONO} font-size:18px; color:#454c50;">{skill}</span>')
    s = s.replace('text-transform: uppercase; color:#949c9f;">BA</span>', 'text-transform: uppercase; color:#949c9f;" class="pdf">BA</span>')   # the cap says it on stage
    s = s.replace('<span style="color:#be1e74;">Kat</span>herine Titterton</h2>', 'Kat Titterton</h2>')     # what she is called; pink means lab 2
    s = s.replace('<div style="display:flex; flex-direction:column; gap:18px;"><div class="row"', '<div style="display:flex; flex-direction:column; gap:29px;"><div class="row"')
    s = s.replace('top:16px; bottom:-19px; width:2px; background:#be1e74; opacity:.25;', 'top:16px; bottom:-30px; width:2px; background:#be1e74; opacity:.25;')
    # pink means lab 2 and nothing else: the timeline, the link and the reader's paper list go to ink and grey
    s = s.replace('border-radius:50%; background:#be1e74; transform:translateY(2px);', 'border-radius:50%; background:#454c50; transform:translateY(2px);')
    s = s.replace('width:2px; background:#be1e74; opacity:.25;', 'width:2px; background:#c3c9cb;')
    s = s.replace('letter-spacing:0.06em; color:#be1e74; text-decoration:none;">macrofluidic.me/resume</a>', 'letter-spacing:0.06em; color:#666e72; text-decoration:none;">macrofluidic.me/resume</a>')
    s = s.replace('text-transform: uppercase; color:#be1e74;">My work</span>', 'text-transform: uppercase; color:#666e72;">My work</span>')
    peer = [p for p in PAPERS if p[1] != 'bioRxiv']; nc = {1: 'one', 2: 'two', 3: 'three'}[sum(p[1] == 'Nat Commun' for p in peer)]
    tile = lambda n, label, sub: (f'<div style="box-sizing:border-box; padding:8px 12px 7px; border-radius:10px; background:#ffffff; '
                                  f'box-shadow:0 1px 2px rgba(20,23,26,.06), 0 6px 16px rgba(20,23,26,.06); display:flex; flex-direction:column; gap:2px;">'
                                  f'<span style="{SANS} font-size:24px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:#14171a;">{n}</span>'
                                  f'<span style="{SANS} font-size:14px; font-weight:600; line-height:1.2; color:#14171a;">{label}</span>'
                                  f'<span style="{SANS} font-size:12px; line-height:1.25; color:#666e72;">{sub}</span></div>')
    patent_n = PATENT_APPLICATIONS if PATENT_APPLICATIONS else parts.icon('patent', '#14171a', 24)
    record = ((len(peer), 'peer-reviewed papers', f'{nc} in Nature Communications', 'journals', True),
              (None, 'patent applications', 'Axiom Bio, bioactivity detection', 'patent', True),
              (COMPOUNDS_IMAGED, 'compounds imaged', 'two Cell Painting datasets', 'molecule', False))   # (n, label, sub, icon, sub on stage)
    tiles = ('<div class="ft pdf" style="display:flex; flex-direction:column; gap:6px; margin-top:12px;">'
             + ''.join(tile(n if n else patent_n, label, sub) for n, label, sub, _, _ in record) + '</div>')
    big = lambda n, label, sub, ic: (f'<div style="flex:1; box-sizing:border-box; padding:16px 22px; border-radius:14px; background:#ffffff; '
                                     f'box-shadow:0 1px 2px rgba(20,23,26,.06), 0 12px 30px rgba(20,23,26,.07); display:flex; flex-direction:column; justify-content:center; gap:4px;">'
                                     f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                                     f'<span style="{SANS} font-size:52px; font-weight:700; letter-spacing:-0.04em; line-height:1; color:#14171a;">{n}</span>{parts.icon(ic, "#454c50", 40)}</div>'
                                     f'<span style="{SANS} font-size:19px; font-weight:600; line-height:1.25; color:#14171a; margin-top:4px;">{label}</span>'
                                     + (f'<span style="{SANS} font-size:18px; line-height:1.3; color:#666e72;">{sub}</span>' if sub else '') + '</div>')
    stage = ('<div class="ft talk" style="height:538px; display:flex; flex-direction:column; gap:14px;">'
             + ''.join(big(n if n else (PATENT_APPLICATIONS or parts.icon('patent', '#14171a', 52)), label, sub if on_stage else '', ic)
                       for n, label, sub, ic, on_stage in record) + '</div>')
    while '<div class="ft' in s:                                     # redraw the tiles wherever an earlier build left them
        i = s.index('<div class="ft'); s = s[:i] + s[_div_end(s, i):]
    s = s.replace('>macrofluidic.me/resume</a>', '>macrofluidic.me/resume</a>' + tiles, 1)
    s = s.replace('<div style="width:412px; flex-shrink:0; display:flex; flex-direction:column; gap:10px;">',
                  '<div style="width:412px; flex-shrink:0; display:flex; flex-direction:column; gap:10px;">' + stage, 1)
    if FT_CSS not in s:
        s = s.replace('</style>', FT_CSS + '</style>', 1)
    s = s.replace('<div style="width:412px; flex-shrink:0; display:flex; flex-direction:column; gap:5px;">', '<div style="width:412px; flex-shrink:0; display:flex; flex-direction:column; gap:10px;">')
    return s


REVEAL_CSS = ('.flow .s{opacity:0;pointer-events:none;transition:opacity .5s ease}.step-1 .s1{opacity:1;pointer-events:auto}'
              '.flow{cursor:pointer}')
FOUNDER_STEPS = {'tag': ['Background', 'The question', 'Today']}
LIGHT = ('background:#f6f7f7; background-image: radial-gradient(60% 50% at 100% 0%, rgba(190,30,116,0.07), transparent 70%), '
         'radial-gradient(50% 45% at 0% 100%, rgba(15,143,108,0.08), transparent 70%);')


OLD_HINT_02 = f'<span data-h="hint" style="position:absolute; right:56px; bottom:44px; z-index:6; {MONO} font-size:13px; color:#666e72;">click &#8594; the question</span>'


TODAY_CSS = '.step-2 .s2{opacity:1;pointer-events:auto}'


def _div_end(s, i):
    """Index just past the </div> that closes the <div opening at i."""
    depth = 0
    for t in re.finditer(r'<div\b|</div>', s[i:]):
        depth += 1 if t.group(0) == '<div' else -1
        if depth == 0:
            return i + t.end()
    raise ValueError('unbalanced div')


def today(deck):
    """Slide 02's third view, after the question: how a lab answers it today (search, ask, guess) and what each way costs. It was
    board A25; Kat moved it into the talk on 19 Oct 2026. Moved once from t35 into t1, then kept in t1; the board and its index
    entry go. Its why-now line stays on slide 06, where the talk already says it."""
    t35 = re.search(r'<template id="t35">.*?</template>', deck, flags=re.S)
    t1 = re.search(r'<template id="t1">.*?</template>', deck, flags=re.S)
    s = t1.group(0)
    if t35 and 'class="s s2"' not in s:
        a = t35.group(0)
        i = a.index('<div style="display:flex; flex-direction:column; gap:8px;">'); cost = a[i:_div_end(a, i)]
        j = a.index('<div style="flex-grow:1; min-height:0; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:18px;">'); ways = a[j:_div_end(a, j)]
        cost, n = re.subn(r'<span style="[^"]*text-transform:uppercase; color:#454c50;">\$28B a year, spent on US lab research others cannot reproduce \[6\]</span>',
                          lambda _: f'<span style="{SANS} font-size:19px; line-height:1.3; color:#454c50;">$28B a year of US lab research others cannot reproduce'
                                    + parts.pdf(' [6]') + '</span>', cost)
        assert n == 1, 'the cost line changed'
        cost = cost.replace("font-size:14px; color:#f6f7f7;", "font-size:16px; color:#f6f7f7;").replace("font-size:14px; color:#454c50;", "font-size:16px; color:#454c50;")
        cost = cost.replace('height:36px; border-radius:8px;', 'height:40px; border-radius:8px;')
        ways = ways.replace('height:94px; border-radius:6px;', 'height:104px; border-radius:6px;')          # the six search results, larger on stage
        view = (f'<div class="s s2" style="position:absolute; left:0; top:88px; right:0; bottom:86px; z-index:5; box-sizing:border-box; padding:0 56px 0; {LIGHT} '
                f'display:flex; flex-direction:column; gap:18px;">'
                f'<h2 style="margin:0; {SANS} font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:#14171a;">'
                f'Today each lab judges its own &#8220;normal&#8221;, <span style="color:#0f8f6c;">alone</span>.</h2>{cost}{ways}</div>')
        k = _div_end(s, s.index('<div class="s s1"'))
        s = s[:k] + view + s[k:]
        deck = deck[:t1.start()] + s + deck[t1.end():]
        deck = re.sub(r'<template id="t35">.*?</template>\s*', '', deck, count=1, flags=re.S)
        m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S); meta = json.loads(m.group(1))
        assert len(meta) == 36 and meta[35]['name'] == 'Pain', 'A25 is the last board'
        deck = deck[:m.start(1)] + json.dumps(meta[:35]) + deck[m.end(1):]

    def three(t):
        if TODAY_CSS not in t:
            t = t.replace(REVEAL_CSS, REVEAL_CSS + TODAY_CSS, 1)
        t = t.replace('<div class="s s2" style="position:absolute; left:0; top:88px; right:0; bottom:48px;',      # cards end where every talk figure ends
                      '<div class="s s2" style="position:absolute; left:0; top:88px; right:0; bottom:86px;')
        t = t.replace('height:118px; border-radius:6px;', 'height:104px; border-radius:6px;')
        t = re.sub(r'<div style="display:flex; flex-direction:column; gap:8px;">(\s*<div style="display:flex; justify-content:space-between; align-items:baseline; gap:24px;">\s*<span[^>]*>\$28B)',
                   r'<div class="pdf" style="display:flex; flex-direction:column; gap:8px;">\1', t, count=1)        # the $28B bar: a second idea, for the reader
        t = t.replace('>do my U2OS cells look &#8220;normal&#8221;<', '>do my cells look &#8220;normal&#8221;<')
        t = re.sub(r'<span style="[^"]*">To: whoever ran this line last</span>', '', t, count=1)           # the subject line says it
        t = t.replace('>Subject: does this look right to you?<', '>does this look right to you?<')
        t = t.replace('>one cell line, six papers, all look different<', '>six papers, six &#8220;normals&#8221;<')
        # 25 Oct review: the right papers for two images, and only one of the five published images is a control well,
        # so the caption says looks until control wells replace them; the images' sources and licences in the PDF
        t = t.replace('U2OS cells, Stadler 2013,', 'U2OS cells, Stadler 2012,').replace('>Stadler 2013</span>', '>Stadler 2012</span>')
        t = t.replace('U2OS cells, Wawer 2017,', 'U2OS cells, Bray 2017,').replace('>Wawer 2017</span>', '>Bray 2017</span>')
        # 25 Oct: each published tile is now a negative-control well from the same screen and plate, pulled by
        # analysis/pull_search_tiles.py (provenance in results/search-tiles.json), so the caption says normals again
        tiles = json.load(open('results/search-tiles.json'))['tiles']
        for tile in tiles:
            name = os.path.basename(tile['file'])[len('search-'):-len('.jpg')].split('-')     # doil-2009 -> Doil 2009
            who = f'{name[0].capitalize()} {name[1]}'
            uri = 'data:image/jpeg;base64,' + base64.b64encode(open(tile['file'], 'rb').read()).decode()
            t, n = re.subn(r'<img src="data:image/jpeg;base64,[^"]*" alt="Image search result: U2OS cells, ' + who + r', [^"]*"',
                           lambda _: f'<img src="{uri}" alt="Image search result: U2OS cells, {who}, negative-control well."', t, count=1)
            assert n == 1, f'no search tile for {who}'
        t = t.replace('>six papers, six looks</span>', '>six papers, six &#8220;normals&#8221;</span>')
        credit = ('<span class="pdf img-credit" style="' + MONO + ' font-size:11px; line-height:1.4; color:#666e72;">negative-control wells, IDR idr0010, idr0036, idr0025, '
                  'idr0033, idr0016 (results/search-tiles.json); JUMP [7]; Doil and Rohban CC BY 4.0, Gustafsdottir and Bray CC0, Stadler CC BY-SA 3.0</span>')
        t = re.sub(r'<span class="pdf img-credit"[^>]*>.*?</span>', lambda _: '', t, count=1, flags=re.S)
        t = t.replace('>six papers, six &#8220;normals&#8221;</span>', '>six papers, six &#8220;normals&#8221;</span>' + credit, 1)
        t = t.replace('>of R&amp;D dollars at risk<', '>dollars at risk<').replace('>of development lost<', '>lost<')
        t = t.replace('>one screenshot, one opinion<', '>one opinion<')
        t = re.sub(r'<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#666e72;">[123]</span>', '', t)   # the cards read left to right
        t = t.replace('>run it anyway<', '>run it<').replace('>wait to be sure<', '>wait<')
        t = t.replace('normal&#8221;, alone.</h2>', 'normal&#8221;, <span style="color:#0f8f6c;">alone</span>.</h2>')      # one phrase lit, as on every talk slide
        # 25 Oct: the search and the email name the cell line. The query reads as typed; each result carries its paper; the
        # email goes to a U2OS paper's authors ("show more specifically web search for U2OS, email to U2OS authors").
        t = t.replace('>do my cells look &#8220;normal&#8221;<', '>U2OS cells &#8220;normal&#8221; morphology<')
        t = re.sub(r'<div style="height:104px; border-radius:6px; overflow:hidden; background:#000;">(<img src="[^"]*" alt="Image search result: U2OS cells, ([^,]+), [^"]*"[^>]*>)</div>',
                   lambda m: (f'<div style="display:flex; flex-direction:column; gap:3px; min-width:0; min-height:0;"><div style="flex:1; min-height:0; border-radius:6px; overflow:hidden; background:#000;">{m.group(1)}</div>'
                              f'<span style="{SANS} font-size:11px; line-height:1.2; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{m.group(2)}</span></div>'), t)
        t = t.replace('<div style="display:flex; flex-direction:column; gap:3px; min-width:0;"><div style="height:94px; border-radius:6px; overflow:hidden; background:#000;">',
                      '<div style="display:flex; flex-direction:column; gap:3px; min-width:0; min-height:0;"><div style="flex:1; min-height:0; border-radius:6px; overflow:hidden; background:#000;">')
        t = t.replace('<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:6px;"><div style="display:flex; flex-direction:column; gap:3px;',
                      '<div style="display:grid; grid-template-columns:repeat(3,1fr); grid-template-rows:repeat(2,minmax(0,1fr)); gap:10px 6px; flex:1; min-height:0;"><div style="display:flex; flex-direction:column; gap:3px;')
        t = t.replace('<div style="display:flex; align-items:flex-end; gap:12px; margin-top:auto;"><img ',
                      '<div style="display:flex; flex-direction:column; gap:6px; margin-top:14px; flex:1; min-height:0;"><img ')
        t = t.replace('style="width:120px; height:120px; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74; outline-offset:2px;">',
                      'style="flex:1; min-height:0; width:100%; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74; outline-offset:2px;">')
        t = re.sub(r'<span class="pdf" style="([^"]*font-size:34px[^"]*)">hundreds of thousands</span>', r'<span style="\1">$100,000s</span>', t, count=1)
        t = t.replace('>dollars at risk<', '>at risk<')
        # the cost's source, for the reader (docs/whitepaper.html, "Who pays"); an earlier wording is replaced, so a rebuild is stable
        t = re.sub(r'<span class="pdf"><span [^>]*>[^<]*\(docs/whitepaper\.html\)</span></span>', '', t, count=1)
        risk = parts.pdf('<span style="' + MONO + ' font-size:11px; line-height:1.4; color:#666e72;">about $50k a run, 3 runs a week, in the author&#8217;s experience [28]</span>')
        wait = parts.pdf('<span style="' + MONO + ' font-size:11px; line-height:1.4; color:#666e72;">asking or re-running to be sure, the author&#8217;s estimate [28]</span>')
        t = re.sub(r'<span class="pdf"><span [^>]*>[^<]*the author&#8217;s (?:experience|estimate) \[\d+\]</span></span>', '', t)   # each note is added once below, whatever its old number
        t = t.replace('font-size:17px; line-height:1.3; color:#454c50;">at risk</span>', 'font-size:18px; line-height:1.3; color:#454c50;">at risk</span>')
        t = t.replace('font-size:18px; line-height:1.3; color:#454c50;">at risk</span>', 'font-size:18px; line-height:1.3; color:#454c50;">at risk</span>' + risk, 1)
        t = t.replace('line-height:1.05; color:#454c50;">months</span></div>',
                      'line-height:1.05; color:#454c50;">months</span><span style="' + SANS + ' font-size:18px; line-height:1.3; color:#454c50;">lost</span></div>', 1)
        t = t.replace(SANS + ' font-size:17px; line-height:1.3; color:#454c50;">lost</span>', SANS + ' font-size:18px; line-height:1.3; color:#454c50;">lost</span>')
        t = t.replace(SANS + ' font-size:18px; line-height:1.3; color:#454c50;">lost</span></div>', SANS + ' font-size:18px; line-height:1.3; color:#454c50;">lost</span>' + wait + '</div>', 1)
        t = t.replace('<span style="' + MONO + ' font-size:11px; line-height:1.2; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">',
                      '<span style="' + SANS + ' font-size:11px; line-height:1.2; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">')
        t = t.replace('<span style="' + SANS + ' font-size:17px; line-height:1.5; color:#454c50;">does this look right to you?</span>',
                      '<span style="' + MONO + ' font-size:13px; color:#666e72;">To: authors, U2OS paper</span>'
                      '<span style="' + SANS + ' font-size:17px; line-height:1.45; color:#454c50;">Subject: do my U2OS cells look right?</span>')
        t = re.sub(r'<span style="([^"]*font-size:34px[^"]*)">hundreds of thousands</span>', r'<span class="pdf" style="\1">hundreds of thousands</span>', t, count=1)
        t = t.replace('<span style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#666e72;">screenshot.png</span>',
                      '<span class="pdf" style="font-family: \'IBM Plex Mono\', Menlo, monospace; font-size:13px; color:#666e72;">screenshot.png</span>')
        for old, new in (('border-left:3px solid #be1e74;"><span style="display:flex; align-items:center; gap:7px;"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#be1e74"',
                          'border-left:3px solid #454c50;"><span style="display:flex; align-items:center; gap:7px;"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#454c50"'),
                         ('text-transform:uppercase; color:#be1e74;">run it anyway</span>', 'text-transform:uppercase; color:#454c50;">run it anyway</span>'),
                         ('line-height:1.05; color:#be1e74;">hundreds of thousands</span>', 'line-height:1.05; color:#14171a;">hundreds of thousands</span>')):
            t = t.replace(old, new)                                                                  # pink means you; the guess card is nobody
        t = t.replace('>Today each lab judges its own &#8220;normal&#8221;, <span style="color:#0f8f6c;">alone</span>.</h2>',
                      '>Each lab judges &#8220;normal&#8221;, <span style="color:#0f8f6c;">alone</span>.</h2>')          # the plainest claim
        t = t.replace('>Each lab judges &#8220;normal&#8221;, <span style="color:#0f8f6c;">alone</span>.</h2>',
                      '>Each lab judges &#8220;normal&#8221; alone.<br><span style="color:#0f8f6c;">A wrong call costs $100,000s.</span></h2>')   # the pain with its price (README [28])
        t = t.replace('<span style="' + SANS + ' font-size:11px; line-height:1.2; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">',
                      '<span class="pdf" style="' + SANS + ' font-size:11px; line-height:1.2; color:#666e72; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">')   # paper names: the reader's
        for way, name in (('search', 'search'), ('ask', 'email'), ('guess', 'chance')):
            t = t.replace(f'<span style="{SANS} font-size:18px; font-weight:600; letter-spacing:-0.01em; color:#454c50;">{way}</span>',
                          f'<span style="display:flex; align-items:center; gap:8px; {SANS} font-size:18px; font-weight:600; letter-spacing:-0.01em; color:#454c50;">'
                          f'{parts.icon(name, "#454c50", 20)}{way}</span>')
        t = t.replace('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#454c50" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink:0;">'
                      '<path d="M12 3v18"/><path d="M16.5 7.5a3.5 3 0 0 0-3.5-2.5h-2.5a3 3 0 0 0 0 6h3a3 3 0 0 1 0 6h-2.5a3.5 3 0 0 1-3.5-2.5"/></svg>',
                      parts.icon('run', '#454c50', 22))                                      # '$' only in $100,000s
        t = t.replace('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#666e72" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink:0;">'
                      '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>', parts.icon('clock', '#666e72', 22))
        t = t.replace('font-size:13px; letter-spacing:0.08em; text-transform:uppercase; color:#454c50;">run it</span>', 'font-size:18px; letter-spacing:0.08em; text-transform:uppercase; color:#454c50;">run it</span>')
        t = t.replace('font-size:13px; letter-spacing:0.08em; text-transform:uppercase; color:#666e72;">wait</span>', 'font-size:18px; letter-spacing:0.08em; text-transform:uppercase; color:#666e72;">wait</span>')
        t = t.replace('font-size:15px; line-height:1.3; color:#454c50; margin-top:auto;">', 'font-size:18px; line-height:1.3; color:#454c50; margin-top:auto;">')   # six papers; one opinion
        t = t.replace('alt="Image search result: U2OS cells, Rohban 2017, Cell Painting."', 'alt="Image search result: U2OS cells, Rohban 2017, negative-control well."')
        # the sixth search result was the emailed screenshot itself (lab 2's well, 03's pink tile); it becomes another JUMP lab's DMSO well,
        # lab 3's (source_3 A12069aW A02, JCP2022_033924 in metadata/well.csv.gz), so the attachment is the only lab 2 image on the view
        if 'JUMP 2023, lab 3, DMSO control well.' not in t:
            import io
            from PIL import Image
            buf = io.BytesIO(); Image.open('figures/assets/game-lab3-dna.png').convert('RGB').resize((300, 300), Image.LANCZOS).save(buf, 'JPEG', quality=85)
            lab3 = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
            t = re.sub(r'<img src="data:image/jpeg;base64,[^"]*" alt="Image search result: U2OS cells, JUMP 2023, lab 2\."',
                       lambda _: f'<img src="{lab3}" alt="Image search result: U2OS cells, JUMP 2023, lab 3, DMSO control well."', t, count=1)
        if 'class="stain"' not in t:                                                         # the emailed image says what is lit
            t = t.replace('<div style="display:flex; flex-direction:column; gap:6px; margin-top:14px; flex:1; min-height:0;"><img ',
                          '<div style="display:flex; flex-direction:column; gap:6px; margin-top:14px; flex:1; min-height:0;"><div style="position:relative; flex:1; min-height:0; display:flex;"><img ', 1)
            t = t.replace('alt="Attached screenshot: U2OS cells, JUMP 2023, lab 2." style="flex:1; min-height:0; width:100%; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74; outline-offset:2px;">',
                          'alt="Attached screenshot: U2OS cells, JUMP 2023, lab 2." style="flex:1; min-height:0; width:100%; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74; outline-offset:2px;">'
                          + parts.stain_chip('DNA', size=14) + '</div>', 1)
        return t.replace(parts.cue(2), parts.cue(3))
    return _template(deck, 't1', three)


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
    s = s.replace(OLD_HINT_02, parts.cue(2))        # the words that used to say 'click'
    # the turn said aloud on 02b, for the reader; any earlier wording of the line is replaced, so a rebuild is stable
    s = re.sub(r'<span class="pdf"><span [^>]*>&#8220;Normal&#8221; compared with whom\?.*?</span></span>', '', s, count=1, flags=re.S)
    s = s.replace('&#8230; answered @ none</span>', '&#8230; answered @ none</span>' + parts.pdf(
        f'<span style="{SANS} font-size:17px; line-height:1.4; color:#666e72;">&#8220;Normal&#8221; compared with whom?<br>Each lab&#8217;s own checks can pass '
        'while labs still disagree (slides 03 and 04, A13).</span>'), 1)
    s = re.sub(r'<div class="pdfv" style="position:absolute; z-index:6; left:56px; bottom:44px;[^"]*">today: search, ask, guess(?:, | &#183; )A25</div>', '', s)
    return s                                     # how labs answer it today is the slide's third view now, not a board (today())


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


def board_a2(s):
    """Board A2: the two numbers in the card corners, read from results on every run (pink: names the lab; grey: after each plate's controls are subtracted)."""
    s = re.sub(r'(letter-spacing: -0\.02em; color: #be1e74; white-space: nowrap;">)[0-9.]+%(</span>)',
               lambda k: f'{k.group(1)}{100 * E1["balanced_accuracy"]:.1f}%{k.group(2)}', s, count=1)
    return re.sub(r'(letter-spacing: -0\.02em; color: #454c50; white-space: nowrap;">)[0-9.]+%(</span>)',
                  lambda k: f'{k.group(1)}{100 * CENTRED:.0f}%{k.group(2)}', s, count=1)


GAME_TILE = ('source_3', 'A12069aW')   # untreated well A02 site 1; same 0.597976 µm/px as the old tile


# image width in pixels of each lab's camera, from the TIFF shapes in cache/images/*/meta.json; with the pixel size in
# metadata/microscope_config.csv it gives the width of one whole field. Every slide 03 tile is one whole field: checked by
# nucleus size against each lab's own images of known scale, within 2% for all six.
NATIVE_PX = {'source_1': 1080, 'source_2': 996, 'source_3': 1080, 'source_5': 998, 'source_6': 970, 'source_10': 1000}
OLD_BAR = re.compile(r'<div (class="bar" )?style="position:absolute; left:(\d+)px; bottom:\d+px; display:flex; flex-direction:column; gap:\d+px;">'
                     r'<div style="width: calc\(100% \* 100 / \(\d+ \* ([0-9.]+)\)\); min-width:\d+px; height:([0-9.]+)px; border-radius:2px; background:#f6f7f7;"></div></div>')

# 03c's single nucleus is a crop of the lab 2 well beside it: 11.6% of that picture's width, found by template matching
# (r = 1.000) at the box the pink outline marks. Its 20 micrometre bar had the same fixed-minimum fault and a label hidden on stage.
NUCLEUS_SHARE = 0.116
OLD_NUCLEUS_BAR = re.compile(r'<div style="position:absolute; left:7px; bottom:7px; display:flex; flex-direction:column; gap:3px;"><div style="width:[0-9.]+%; '
                             r'min-width:\d+px; height:3px; border-radius:2px; background:#f6f7f7;"></div><span class="pdf"[^>]*>20 &#181;m</span></div>')


def scale_bars(deck):
    """Slide 03's bars were drawn for a 1080-pixel field in every lab, with a minimum width that made all six the same length.
    Each becomes 100 micrometres of its own lab's field, with its unit written above it."""
    import pandas as pd
    px = pd.read_csv('metadata/microscope_config.csv').drop_duplicates('Metadata_Source').set_index('Metadata_Source').Metadata_Pixel_Size_Microns
    field = {}
    for src, n in NATIVE_PX.items():
        field.setdefault(round(float(px[src]), 6), set()).add(round(n * float(px[src]), 1))
    assert all(len(v) == 1 for v in field.values()), 'one field width per pixel size'

    def new(m):
        um = next(iter(field[round(float(m.group(3)), 6)]))
        inset = int(m.group(2))
        return parts.scale_bar(um, inset=inset, height=float(m.group(4)), size=14 if m.group(1) else 13, cls='bar' if m.group(1) else 'scalebar')
    nucleus = parts.scale_bar(NUCLEUS_SHARE * NATIVE_PX['source_2'] * float(px['source_2']), bar_um=20, inset=7, height=3, size=13)
    return _template(deck, 't2', lambda t: OLD_NUCLEUS_BAR.sub(lambda _: nucleus, OLD_BAR.sub(new, t)))


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


A25_REFS = ('[6] Freedman et al., <em>PLoS Biology</em>, 2015 &#183; [7] JUMP, 2023 &#183; [9] US FDA, 2025 &#183; '
            'full references in the README')     # every source the board cites, as A23 lists its own


def legends(deck):
    """Board A25 (the old pain slide) keeps a source line; the game (slide 03) keeps a one-line legend, written from results."""
    e1 = json.load(open('results/e1.json'))['all_sources']
    m = re.search(r'<template id="t35">.*?</template>', deck, flags=re.S)
    if m:                                                    # A25 until it moves into slide 02 (today())
        s = re.sub(r'(<div style="[^"]*display:block;">)(?:(?!</div>).)*?Freedman(?:(?!</div>).)*?(</div>)',
                   r'\1' + A25_REFS + r'\2', m.group(0), count=1, flags=re.S)
        att = ('<span style="font-family: \'Archivo\', \'Helvetica Neue\', Helvetica, sans-serif; font-size:17px; line-height:1.5; color:#949c9f;">Attached: screenshot.png</span>')
        if att in s:                                                                                              # the attachment, shown
            src = re.search(r'<img src="([^"]+)" alt="Image search result: U2OS cells, JUMP 2023, lab 2\."', s).group(1)
            s = s.replace(att, f'<div style="display:flex; align-items:flex-end; gap:12px; margin-top:8px;">'
                          f'<img src="{src}" alt="Attached screenshot: U2OS cells, JUMP 2023, lab 2." style="width:120px; height:120px; object-fit:cover; display:block; border-radius:6px; outline:2px solid #be1e74; outline-offset:2px;">'
                          f'<span style="{MONO} font-size:13px; color:#666e72;">screenshot.png</span></div>')
        deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'<template id="t2">.*?</template>', deck, flags=re.S)
    s = re.sub(r'<span class="num"[^>]*>\d</span>', '', m.group(0))                                         # tile numbers
    s = re.sub(r'<div class="hint"[^>]*><span data-h="hint">[^<]*</span></div>', lambda _: parts.cue(2), s, count=1)   # dots, not words
    s = s.replace(parts.cue(3), parts.cue(2))                                                        # two views since 25 Oct: the third folded into 04
    if '.tag:empty{display:none}' not in s:
        s = s.replace('</style>', '.tag:empty{display:none}</style>', 1)                               # an empty pink pill shows nothing
    s = s.replace('>names the right lab, of 11<', '>right lab, of 11<').replace('>a random guess<', '>chance<')   # 25 Oct: half the words
    s = s.replace('>One lab, or six?</div>', '>One lab, <span style="color:#0f8f6c;">or six?</span></div>')
    s = s.replace('>Could you tell?<br>A classifier can.</div>', '>Could you tell?<br><span style="color:#0f8f6c;">A classifier can.</span></div>')
    s = s.replace('>Could you tell?<br><span style="color:#0f8f6c;">A classifier can.</span></div>',
                  '>Could anyone tell?<br><span style="color:#0f8f6c;">A classifier can.</span></div>')   # 25 Oct: no "you" in a headline; pink carries it
    s = re.sub(r'(<div class="cite(?: pdfv)?"[^>]*>).*?(</div>)',
               lambda k: (k.group(1) + '<span style="color:#14171a; font-weight:500;">fig 1</span> '
                          f'Cell Painting &#183; images: DNA channel &#183; classifier: {e1["n_features"]:,} numbers per well from all channels &#183; {e1["n_wells"]:,} wells &#183; {e1["n_labs"]} labs &#183; plates held out &#183; bars 100 &#181;m &#183; JUMP [7] &#183; A2, A3, A5' + k.group(2)),
               s, count=1, flags=re.S)
    s = re.sub(r'\s*<div class="others".*?(?=\s*<div class="picto")', '', s, count=1, flags=re.S)            # unsourced other-labs row
    s = re.sub(r'<circle cx="(?:64|1168)"[^>]*/>|<circle cx="[0-9.]+" cy="(?:10|340)"[^>]*/>', '', s)         # wells clamped to the frame
    bar = lambda v, c: (f'<div class="sbar" style="grid-column:1/-1; height:10px; margin-top:-8px; border-radius:5px; background:#eceeef;">'
                        f'<div style="width:{100 * v:.1f}%; height:100%; border-radius:5px; background:{c};"></div></div>')
    if 'class="sbar"' not in s:                                                                               # the 11-fold gap, drawn
        s = s.replace('>classifier</span></div>', '>classifier</span></div>' + bar(e1['balanced_accuracy'], '#454c50'), 1)
        s = s.replace('>chance</span></div>', '>chance</span></div>' + bar(e1['chance'], '#c3c9cb'), 1)
    s = s.replace('color:#454c50;">classifier</span>', f'color:#454c50;">classifier &#183; {e1["n_labs"]} labs</span>', 1)       # once: the literal is gone after
    # 26 Oct review. The pink pill on lab 2's tile was empty on 03a (.tag:empty misses .startag): it carries the lab flask, and the
    # runtime text (META 'you': '' then 'lab 2') goes in a span beside it, since textContent would wipe the icon
    s = s.replace('font-size:16px; opacity:0;" data-h="you">you</span>',
                  'font-size:16px; opacity:0; display:flex; align-items:center; gap:6px;">' + parts.icon('lab', '#f6f7f7', 18) + '<span data-h="you"></span></span>')
    s = s.replace('monospace; font-size:16px; opacity:0;', 'monospace; font-size:18px; opacity:0;')       # the lab chips at the stage floor
    s = s.replace('<div class="star" style="position:absolute; inset:0; border-radius:12px; box-shadow: inset 0 0 0 4px #be1e74; opacity:0;"></div>',
                  '<div class="star" style="position:absolute; inset:0; border-radius:12px; outline:4px solid #be1e74; outline-offset:-4px; opacity:0;"></div>')   # prints, unlike a shadow
    s = s.replace('<span style="' + MONO + ' font-size:24px; color:#0f8f6c;">&#10003;</span>', parts.icon('check', '#454c50', 30))   # one check symbol; green is the field
    # what the cells are (next-pass 12): one line for the room, the sources for the reader
    u2os = ('<div class="u2os" style="box-sizing:border-box; width:504px; margin-top:-26px; padding-left:56px; display:flex; flex-direction:column; gap:8px;">'
            f'<span style="{SANS} font-size:18px; line-height:1.3; color:#454c50;">U2OS: human bone cancer cells</span>'
            + parts.pdf(f'<span style="display:flex; flex-direction:column; gap:4px; {MONO} font-size:12px; line-height:1.45; color:#666e72;">'
                        '<span>osteosarcoma (bone cancer) from a 15-year-old&#8217;s tibia, described in 1967 [26]</span>'
                        '<span>the one line in JUMP&#8217;s full dataset, so every lab here grew it [27]</span>'
                        '<span>chosen over A549 by a slim margin, for its public data [27]</span>'
                        '<span>named in 11 of the Cell Painting Gallery&#8217;s 28 datasets [17]</span>'
                        '<span>a cancer line: &#8220;normal&#8221; means its DMSO baseline, not healthy tissue</span></span>') + '</div>')
    s = re.sub(r'<div class="u2os".*?</span></span></span></div>', '', s, count=1, flags=re.S)
    s = s.replace('color:#14171a;">same cells</span>' + parts.icon('check', '#454c50', 30) + '</div>',
                  'color:#14171a;">same cells</span>' + parts.icon('check', '#454c50', 30) + '</div>' + u2os, 1)
    # one chip for the grid, on its last tile (all six are DNA), bottom right, sized to clear the 100 um label; redrawn on every build
    s = re.sub(r'<div class="stain"[^>]*>.*?</div>', '', s, count=1, flags=re.S)
    s = s.replace('alt="DMSO control well, DNA channel, lab 10." style="width:100%; height:100%; object-fit:cover; display:block;">',
                  'alt="DMSO control well, DNA channel, lab 10." style="width:100%; height:100%; object-fit:cover; display:block;">' + parts.stain_chip('DNA', size=12, inset=7), 1)
    s = s.replace('font-size:18px; color:#666e72;">chance</span>',
                  'font-size:18px; color:#666e72; display:inline-flex; align-items:center; gap:8px;">' + parts.icon('chance', '#666e72', 22) + 'chance</span>')
    # the third view folded into 04a on 25 Oct; its never-shown chain (a nucleus, its well, a map) leaves the page
    if '<div class="chain"' in s:
        i = s.index('<div class="chain"'); s = s[:i].rstrip(' ') + s[_div_end(s, i):].lstrip()
    s = s.replace('<div class="h h2" style="position:absolute; left:56px; top:86px; width:640px; ' + SANS + ' font-size:44px; font-weight:600; letter-spacing:-0.028em; line-height:1.05; color:#14171a;">One well, onto the map.</div>', '')
    deck = deck[:m.start()] + s + deck[m.end():]
    m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S)
    meta = json.loads(m.group(1))
    game = next(e for e in meta if e['name'] == 'Game')
    game['steps']['foot'] = ['', '']                         # the pink footer lines leave
    game['steps']['tag'] = ['The game'] * 2              # one tag a slide; the views speak for themselves; the map step moved to 04 on 25 Oct
    game['steps']['you'] = ['', 'lab 2']                  # pink says "you"; the word is spoken, never written (25 Oct 2026)
    game['steps']['sub'] = game['steps'].get('sub', ['', '', ''])[:2]
    game['steps'].pop('hint', None)                     # dots, not words
    return deck[:m.start(1)] + json.dumps(meta) + deck[m.end(1):]


A5_START, A5_END = '<!--a5-->', '<!--/a5-->'
A5_ROW = '<div style="display: flex; gap: 32px; flex-grow: 1; min-height: 0; align-items: stretch;">'   # the hand-built row the board replaced, through its caption
A5_CAPTION = '<div style="border-top: 1px solid #d3d8da; padding-top: 10px;'
FIGURE_CARD = ('box-sizing:border-box; background: linear-gradient(90deg, #be1e74, #0f8f6c) top / 100% 3px no-repeat, #ffffff; border-radius:16px; '
               'box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 16px 40px rgba(20,23,26,0.10);')   # appendix.FIGURE's ground: the figure card of A6 and A14


def a5_body(R, ok, uris):
    """A5 in the boards' grammar: one figure card (two typical untreated wells, the count and the texture beside them), three cards,
    one caption. Every number from results/a5-pair; without a confirmed pair the wells are shown and nothing is claimed."""
    G, P, INK, INK2, MUTE, FAINT = parts.GREEN, parts.PINK, parts.INK, parts.INK2, parts.MUTE, parts.FAINT

    def tile(uri, n, delay):
        scope = R[f'lab_{n}']['microscope'].split(', ')[:2] if R else []      # e.g. CV8000, confocal
        return (f'<figure class="ap" style="animation-delay:{delay:.2f}s; margin:0; display:flex; flex-direction:column; gap:8px;">'
                f'<div style="position:relative; width:256px; height:256px;"><img src="{uri}" alt="Untreated well of the same cell line, DNA channel, lab {n}." style="display:block; width:256px; height:256px; border-radius:10px; background:#0c0e10;">'
                + (parts.scale_bar(R[f'lab_{n}']['tile']['um'], inset=10) if R and 'tile' in R[f'lab_{n}'] else '') + '</div>'
                f'<figcaption style="display:flex; gap:10px; align-items:baseline;">{parts.label(f"lab {n}", INK)}'
                f'<span style="{SANS} font-size:13px; color:{MUTE};">{" &#183; ".join(scope)}</span></figcaption></figure>')

    def readout(name, colour, a, sym, b, gap, verdict, delay):
        return (f'<div class="ap" style="animation-delay:{delay:.2f}s; display:flex; flex-direction:column; gap:8px;">{parts.label(name, P if colour == P else MUTE)}'
                f'<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.03em; line-height:1; color:{colour}; white-space:nowrap;">'
                f'{a} <span style="font-weight:400; color:{FAINT if colour != P else P};">{sym}</span> {b}</span>'
                f'<span style="{MONO} font-size:13px; color:{MUTE};">gap {gap:.1f}&#215; the usual spread &#8594; {verdict}</span></div>')

    def card(title, body, colour, delay):
        return (f'<div class="ap" style="animation-delay:{delay:.2f}s; flex:1; min-width:0; {parts.CARD} padding:12px 18px; display:flex; flex-direction:column; gap:5px;">'
                f'{parts.label(title, colour)}<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{body}</span></div>')

    same = bool(R) and R['lab_5']['microscope'] == R['lab_6']['microscope']
    top = 'same cell line &#183; same protocol' + (' &#183; same microscope' if same else '')
    side = ''
    if ok:
        side = (f'<div style="flex-grow:1; min-width:0; display:flex; flex-direction:column; gap:22px;">'
                + readout('cells counted', INK2, R['lab_5']['count'], '&#8776;', R['lab_6']['count'], R['count_diff'] / R['count_pooled_iqr'], 'same', 0.45)
                + readout('fine detail &#183; % of DNA signal', P, f"{R['lab_5']['texture']:.2f}%", '&#8800;', f"{R['lab_6']['texture']:.2f}%",
                          R['texture_diff'] / R['texture_pooled_iqr'], 'different', 0.6)
                + f'<span style="{MONO} font-size:13px; line-height:1.5; color:{MUTE};">fine detail: finer than {1 / R["cutoff_cycles_per_um"]:g} &#181;m, inside nuclei<br>'
                  'usual spread: plate to plate, within one lab</span></div>')
    figure = (f'<div class="ap" style="animation-delay:0.20s; flex-grow:1; min-height:0; {FIGURE_CARD} padding:16px 24px; display:flex; flex-direction:column; gap:12px;">'
              f'<div style="display:flex; justify-content:space-between; align-items:baseline; gap:16px;">{parts.label(top, G)}'
              + (f'<span style="{MONO} font-size:13px; color:{MUTE};">each lab&#8217;s typical plate</span>' if ok else '') + '</div>'
              f'<div style="flex-grow:1; min-height:0; display:flex; gap:56px; align-items:center;"><div style="display:flex; gap:20px; flex-shrink:0;">'
              f'{tile(uris[0], 5, 0.27)}{tile(uris[1], 6, 0.35)}</div>{side}</div></div>')
    cards = [('two ways to read it &#183; A2', 'Classifier: does it belong with past runs?<br>Distance: how far out, which way back?', MUTE),
             ('both need a reference', f'Somebody else&#8217;s images.<br>That is <span style="color:{G};">the map</span>.', G)]
    if ok:
        rob, pairs = R['robustness']['main'], R['lab_5']['n_plates'] * R['lab_6']['n_plates']
        cards.insert(0, ('not one lucky pair', f"All {pairs:,} plate pairs, lab 5 &#215; lab 6:<br>texture differs in {100 * rob['pairs_texture_differs']:.0f}%, "
                                               f"count in {100 * (1 - rob['pairs_count_close']):.0f}%.", G))
    row = '<div style="display:flex; gap:16px; align-items:stretch;">' + ''.join(card(t, b, c, 0.75 + 0.1 * k) for k, (t, b, c) in enumerate(cards)) + '</div>'
    squares = f' &#183; {R["lab_5"]["tile"]["um"]} &#181;m squares' if R else ''
    caption = (NOTE_LINE + f'<span style="color: #14171a; font-weight: 500;">Fig. A5</span> DNA channel{squares} &#183; JUMP cpg0016 [7], CC0 &#183; '
               'nuclei by Otsu &#183; both ways: published [1], our tuning unpublished</div>')
    return figure + '\n  ' + row + '\n  ' + caption


def a5_pair(deck):
    """Board A5: two real untreated wells (labs 5 and 6), each its lab's typical plate, and their two readouts from results/a5-pair.json;
    without it, no claim. The board below the headline is rewritten whole between its markers on every run."""
    m = re.search(r'<template id="t15">.*?</template>', deck, flags=re.S)
    s = m.group(0)
    R = json.load(open('results/a5-pair.json')) if os.path.exists('results/a5-pair.json') else None
    ok = bool(R and R['count_close'] and R['texture_differs'])
    if A5_START in s:
        k0 = s.index(A5_START)
        k1 = s.index(A5_END, k0) + len(A5_END)
    else:                                                     # first run: the hand-built row, the floating line under it and the caption
        k0 = s.index(A5_ROW)
        k1 = s.index('</div></div>', s.index(A5_CAPTION, k0)) + len('</div></div>')
    tiles = ('figures/assets/a5-lab5.png', 'figures/assets/a5-lab6.png')
    if all(os.path.exists(f) for f in tiles):
        uris = ['data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode() for f in tiles]
    else:                                                     # the two wells already in the board, lab 5 then lab 6
        uris = re.findall(r'<img src="(data:image/[^"]+)"', s[k0:k1])[:2]
    s = s[:k0] + A5_START + a5_body(R, ok, uris) + A5_END + s[k1:]
    s = s.replace(A5_END + '</div></div>\n</div></template>', A5_END + '\n</div></template>')   # two stray closing tags the old row left behind
    if R:                                                    # D3: the board's source in its tag; [1] stays in the caption
        s = s.replace('color: #0f8f6c;">Cell Systems &#183; 2026 &#183; [1]<', 'color: #0f8f6c;">results/a5-pair<')
    head = 'Same count.<br><span style="color: #be1e74;">Different texture.</span>' if ok else 'Two ways to ask<br>one question.'
    s = re.sub(r'(<h2[^>]*>).*?(</h2>)', lambda k: k.group(1) + head + k.group(2), s, count=1, flags=re.S)
    return deck[:m.start()] + s + deck[m.end():]


PAGER = parts.PAGER_RE
TITLE = 'Datum Line: Do my cells look &#8220;normal&#8221;?'
DESCRIPTION = ('Datum Line is a shared repository of raw cell images from every lab, on one map. Labs put their cells on the map for free; '
               'companies that buy cell data pay for the certificate.')
PREVIEW = 'Confidence with controls: every plate imaged, placed on the map.'
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


HIDE_JS = "'.pdf{display:none!important}.pdfv{visibility:hidden!important}'"
# the talk view hides the paper apparatus; D shows it again (the PDF always has it)
_TAIL = "else if(k==='End'){e.preventDefault();go(secs.length-1);}});"
_D = ("else if(k==='End'){e.preventDefault();go(secs.length-1);}\n"
      " else if(k==='d'||k==='D'){window.__details=!window.__details;secs.forEach(S=>{if(S.hide)S.hide.textContent=window.__details?'':" + HIDE_JS + ";});}});")
NAV = NAV[:2] + ((NAV[2][0], NAV[2][1].replace(_TAIL, _D)),) + NAV[3:] + (
    ("function mount(S){S.root.replaceChildren(document.getElementById('t'+S.i).content.cloneNode(true));S.step=0;}",
     "function mount(S){S.root.replaceChildren(document.getElementById('t'+S.i).content.cloneNode(true));S.step=0;\n"
     " if(S.i<10){S.hide=document.createElement('style');S.hide.textContent=window.__details?'':" + HIDE_JS + ";S.root.appendChild(S.hide);}}"),)


TALK_JS = "'.talk{display:none!important}'"


def navigation(deck):
    deck = deck.replace("d.textContent='Appendix · answers on request'", "d.textContent='Appendix: answers on request'")
    plain, staged = "window.__details?'':" + HIDE_JS, "window.__details?" + TALK_JS + ":" + HIDE_JS
    deck = deck.replace(staged, plain)                       # the NAV pairs below are written against the plain form
    for old, new in NAV:
        if new not in deck:
            assert deck.count(old) == 1, f'the deck script changed: {old[:50]}'
            deck = deck.replace(old, new)
    return deck.replace(plain, staged)                       # .talk: stage only, hidden when D shows the reader's layer


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
    foot = ('<div class="foot"><div>Kat Titterton, San Francisco</div>'
            '<div>Evidence shown is public JUMP Cell Painting data (CC0). Click, or press the space bar or an arrow, for the next view or slide; press D for sources and figure legends; scroll to browse.</div>'
            '<div><a href="docs/">Documents: white paper, product vision, roadmap, landscape, brand</a></div></div>')
    last = deck.rindex('</template>')             # the page footer sits after the slides, never inside one
    tail, n = re.subn(r'<div class="foot">.*?</div></div>', lambda _: foot, deck[last:], count=1, flags=re.S)
    assert n == 1, 'no footer after the slides'
    return deck[:last] + tail


def _template(deck, tid, fn):
    m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
    if not m:
        return deck
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
    if 'lab 4.' in s:                                            # lab 4 is on no other page: the same lab 3 tile as slide 03 (both Phenix, widefield)
        uri = 'data:image/png;base64,' + base64.b64encode(open('figures/assets/game-lab3-dna.png', 'rb').read()).decode()
        s = re.sub(r'<img src="data:image/[a-z]+;base64,[A-Za-z0-9+/=]+" alt="Untreated DMSO well, DNA channel, lab 4\."',
                   lambda _: f'<img src="{uri}" alt="Untreated DMSO well, DNA channel, lab 3."', s, count=1)
        s = s.replace('>lab 4</span>', '>lab 3</span>', 1)
    for old, new in A16_LIGHT:
        s = s.replace(old, new)
    s = re.sub(r'(<div style="aspect-ratio:1/2; width:100%; border-radius:8px; overflow:hidden; background:#000;)("><img src="[^"]+" alt="Untreated DMSO well, DNA channel, lab 2\.")',
               r'\1 outline:2px solid #be1e74; outline-offset:2px;\2', s)       # lab 2's well ringed in pink: you (an outline survives print)
    s = a16_bars(s)
    for name, n in a16_counts().items():                         # the public set's variety, counted from JUMP's metadata [7]
        s = re.sub(r'(font-size:34px;[^"]*">)\d+(</span><span style="[^"]*">' + re.escape(name) + '</span>)', lambda k: f'{k.group(1)}{n}{k.group(2)}', s)
    return s


def field_um(source):
    """Width of one whole field of a lab's camera, in micrometres: image width in pixels times pixel size [7]."""
    import csv
    px = {r['Metadata_Source']: float(r['Metadata_Pixel_Size_Microns']) for r in csv.DictReader(open('metadata/microscope_config.csv'))}
    return round(NATIVE_PX[source] * px[source], 1)


A16_TILE = re.compile(r'(<div style="aspect-ratio:1/2; width:100%; border-radius:8px; overflow:hidden; background:#000;)([^"]*">)'
                      r'(<img src="[^"]+" alt="(?:Untreated DMSO|DMSO control) well, DNA channel, lab (\d+)\."[^>]*>)(?!<div class="scalebar")')


SCALEBAR = re.compile(r'<div class="scalebar" style="[^"]*"><span style="[^"]*">\d+ &#181;m</span><div style="[^"]*"></div></div>')


def a16_bars(s):
    """A16's six wells are the slide 03 fields cut to twice as tall as wide: the full field height shows, so the tile's width is
    half a field and the bar is 100 micrometres of that. Redrawn every build, after the board's colours are set."""
    s = SCALEBAR.sub('', s)
    s = re.sub(r'(<div style="aspect-ratio:1/2; width:100%; border-radius:8px; overflow:hidden; background:#000;) position:relative;([^"]*"><img src="[^"]+" alt="(?:Untreated DMSO|DMSO control) well, DNA channel, lab \d+\.")',
               r'\1\2', s)                                    # only the six labs' tiles, never the planted faults
    return A16_TILE.sub(lambda m: f'{m.group(1)} position:relative;{m.group(2)}{m.group(3)}'
                                  + parts.scale_bar(field_um(f'source_{m.group(4)}') / 2, inset=7, height=3.5, size=13), s)


def a16_counts():
    import csv
    import gzip
    plates = list(csv.DictReader(gzip.open('metadata/plate.csv.gz', 'rt')))
    scopes = {r['Metadata_Microscope_Name'] for r in csv.DictReader(open('metadata/microscope_config.csv'))}
    return {'microscope models': len(scopes), 'plate layouts': len({p['Metadata_PlateType'] for p in plates}),
            'labs [7]': len({p['Metadata_Source'] for p in plates})}


def headlines(deck):
    """Every appendix board's headline is the plain answer to the question in its top line: one sentence, one ink, numbers from results."""
    import appendix                                 # here, not at the top: appendix is imported by the builders that coherence follows
    replay = json.load(open('results/e9-replay.json'))['labs']
    n = sum(v['n_batches'] for v in replay.values()); out = sum(v['batches_outside'] for v in replay.values())
    total = appendix.preseed_total()[1]
    year = sum(appendix.market(1))
    word = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    head = {
        'A1': 'If the plate is sick, its controls are sick too.',
        'A2': 'Every result is one of six plain calculations.',
        'A3': 'The usual correction erases most of the lab&#8217;s fingerprint.',
        'A4': 'On weak benchmarks, counting cells often wins.',
        'A5': 'Same cell count, different texture: only images see it.',
        'A6': 'Plates drift within two weeks: re-check every batch.',
        'A7': 'STR says which line; images say where it was made.',
        'A8': 'Known drugs show whether the test itself worked.',
        'A9': 'The same drug looks less alike in another lab.',
        'A10': 'One brightfield image already names the lab.',
        'A11': f'It flags rarely: {word[out] if out < 10 else out} of {n} batches.',
        'A12': 'Stain brightness rose; the cell count did not.',
        'A13': 'By its own count lab 2 was fine; beside other labs, it had moved.',
        'A14': 'On the map, labs agree a little more on the same drug.',
        'A15': 'Labs join free; subscribers pay for access.',
        'A16': 'Biology&#8217;s ugliest dataset, built on purpose.',
        'A17': 'Ranked on controls, never on results.',
        'A18': 'Only control wells leave the lab.',
        'A19': 'An image goes in; a position and a correction come out.',
        'A20': 'Every lab leaves a fingerprint, so a wrong label stands out.',
        'A21': f'About ${total / 1000:.1f}M for eighteen months, mostly people.',
        'A22': f'About ${year / 1000:.0f}M a year, if every likely buyer joined.',
        'A23': 'Cell data sells, but across labs it is not one dataset.',
        'A24': 'The lab keeps its data and a share; anyone can check it.',
        'A25': 'Every lab&#8217;s controls, as one dataset each, with its certificate.',
    }
    for k in range(11, 11 + parts.N_BOARDS):
        code = f'A{k - 10}'
        deck = _template(deck, f't{k}', lambda t: re.sub(r'(<h2[^>]*>).*?(</h2>)', lambda m: m.group(1) + head[code] + m.group(2), t, count=1, flags=re.S))
    return deck


WATERMARK = re.compile(r'<div aria-hidden="true" style="position:\s*absolute; right:\s*-18px; top:\s*-70px;[^>]*>A\d+</div>')


def no_watermark(deck):
    """The hand-built boards carried the faded board number themselves; parts.watermark() is retired, so these go too."""
    for n in (11, 12, 13, 15, 16, 26):
        deck = _template(deck, f't{n}', lambda t: WATERMARK.sub('', t, count=1))
    return deck


def stage(deck):
    """Slides 02 and 03 are hand-built: mark their slide numbers, section tags and figure legend for the PDF only (see parts.pdf)."""
    mono = "font-family: 'IBM Plex Mono', Menlo, monospace; font-size: 14px; letter-spacing: 0.1em; text-transform: uppercase;"
    for tid, num in (('t1', '02'), ('t2', '03')):
        def mark(s, num=num):
            s = s.replace(f'<span style="{mono} color:#666e72;">{num}</span>', f'<span class="pdfv" style="{mono} color:#666e72;">{num}</span>', 1)
            s = s.replace(f'<span style="{mono} color:#0f8f6c;" data-h="tag">', f'<span class="pdfv" style="{mono} color:#0f8f6c;" data-h="tag">', 1)
            s = s.replace(f'<span style="{mono} color:#0f8f6c;"><span data-h="tag">', f'<span class="pdfv" style="{mono} color:#0f8f6c;"><span data-h="tag">', 1)
            return s.replace('<div class="cite" style=', '<div class="cite pdfv" style=', 1)
        deck = _template(deck, tid, mark)
    return deck


MIDDOT = re.compile(r'(?:&#160;|\s)*(?:&#183;|&#xb7;|·)(?:&#160;|\s)*')


def no_middots(deck):
    """Kat's rule: no dots separating text. 'lab 2 · you' becomes 'lab 2 (you)'; every other ' · ' becomes ', '."""
    out, pos = [], 0
    for m in re.finditer(r'<template id="t\d+">.*?</template>', deck, flags=re.S):
        s = m.group(0)
        s = re.sub(r'(\w[\w ]{0,12}?)(?:&#160;|\s)*(?:&#183;|·)(?:&#160;|\s)*you\b', r'\1 (you)', s)       # the lab the talk follows
        s = re.sub(r'(?<=[^\s>])(?:&#160;|\s)*(?:&#183;|·)(?:&#160;|\s)*(?=[^\s<])', ', ', s)                 # between words
        s = MIDDOT.sub(' ', s)                                                                                # beside a tag: a space
        out.append(deck[pos:m.start()] + s); pos = m.end()
    return ''.join(out) + deck[pos:]


def behind(deck):
    """Hand-built boards name the talk slide they back, as the written boards do through appendix.top_line."""
    for n in (11, 12, 13, 15, 16, 26):
        code = f'A{n - 10}'
        deck = _template(deck, f't{n}', lambda s: s if 'from slide' in s else re.sub(
            r'(>%s &#183; if asked[^<]*)<' % code, lambda m: m.group(1) + f' &#183; from slide {parts.BEHIND[code]}<', s, count=1))
    return deck


def apply(deck):
    report = []
    for tid, pairs in list(WORDS.items()) + list(TRIM.items()):
        m = re.search(r'<template id="%s">.*?</template>' % tid, deck, flags=re.S)
        if not m:                                               # a board that moved into the talk (A25 is slide 02's third view)
            continue
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
    deck = _template(deck, 't1', lambda s: reveal(founder_tiles(founder(s))))
    deck = today(deck)
    m = re.search(r'const META=(\[.*?\]);', deck, flags=re.S)
    meta = json.loads(m.group(1))
    next(e for e in meta if e['name'] == 'Founder')['steps'] = FOUNDER_STEPS
    deck = deck[:m.start(1)] + json.dumps(meta) + deck[m.end(1):]
    deck = _template(deck, 't11', board_a1)
    deck = _template(deck, 't12', board_a2)
    deck = game_tile(deck)
    deck = scale_bars(deck)
    deck = legends(deck)
    deck = _template(deck, 't26', board_a16)
    deck = a5_pair(deck)
    deck = deck.replace(OLD_SVG_FONT, parts.SVG_FONT)       # hand-built charts (t2, t11, t16, ...) use the builders' face
    deck = behind(deck)
    deck = no_middots(deck)
    deck = parts.dmso_words(deck)                            # the control by its name: DMSO wells [7]
    deck = no_watermark(deck)
    deck = stage(deck)
    deck = headlines(deck)
    deck = navigation(deck)
    deck = page(deck)
    return deck, report
