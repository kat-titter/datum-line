"""Appendix boards on what a lab shares and who can rely on it, written whole from results: A18 (what is private?), A20
(biosecurity), A24 (why would a lab share?) and A25 (what the shared data looks like)."""

from parts import *
from appendix_kit import BOARD, H2, LEDE, FIGURE, NOTE, top_line, plate_map, who_uses


# ------------------------------------------------------------------ A18
def a18_columns(L2, wells, dmso, rest):
    """A18's three columns: what is shared (the control wells), what Datum Line does with it, what it never reads."""
    # 9 Nov (Kat: "a little too gray ... more playful, poppy ... gigantic block of cold white not good look"): colour by meaning,
    # one row grid. Green is what leaves the lab, pink what stays yours (the deck's "you"), Datum Line between them in white with a
    # green-to-pink edge. The three cards share one subgrid (label, figure, two rows), so their rows line up and the figure row takes
    # the spare height: no empty block under a short column. "Your backup" joined the lede, so it is said once. Section labels in
    # ink: refine's colour pass keeps pink titles for the one lab, so the tints, plates and counts carry the colour.
    G_T, G_TINT, G_LINE = '#0a7457', '#e6f4ee', '#cfe6da'          # green text (AA), its card tint and hairline
    P_TINT, P_LINE = '#fbeaf3', '#f2cfe0'                          # pink card tint and hairline
    P = 13.5
    plate = lambda filled, colour, aria: svg(24 * P + 16, 16 * P + 12, plate_map(8, 2, '', '', set(), filled, P=P, colour=colour, ground='#ffffff', empty='#d3d8da'),
                                            css_width=f'{24 * P + 16:g}px', aria=aria)
    count = lambda n, colour: f'<span style="{MONO} font-size:14px; font-weight:600; color:{colour};">{n} of {len(wells)} wells</span>'
    head = lambda h: f'<span style="{SANS} font-size:17px; font-weight:600; line-height:1.25; color:{INK};">{h}</span>'
    fig = lambda h, inner, cap: (f'<div style="display:flex; flex-direction:column; gap:8px; min-height:0;">{head(h)}'
                                 f'<div style="flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px;">{inner}{cap}</div></div>')
    row = lambda h, b, line: (f'<div style="display:flex; flex-direction:column; gap:2px; padding-top:9px; border-top:1.5px solid {line};">{head(h)}'
                              f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK2};">{b}</span></div>')
    card = lambda bg, title, colour, figure, rows, line, delay: (
        f'<div class="r" style="animation-delay:{delay}s; display:grid; grid-template-rows:subgrid; grid-row:span 4; row-gap:12px; min-width:0; '
        f'box-sizing:border-box; border-radius:16px; padding:16px 20px 16px; {bg}">'
        f'{label(title, colour)}{figure}' + ''.join(row(h, b, line) for h, b in rows) + '</div>')
    leaves = card(f'background:{G_TINT};', 'What is shared', INK,
                  fig('control wells only: untreated and known drugs',
                      plate(dmso, GREEN, f'One 384-well plate from lab 2: its {len(dmso)} control wells, untreated and known drugs, are the only wells shared.'),
                      count(len(dmso), G_T)),
                  [('images, or numbers from them', 'proposed: images deleted once measured'),
                   ('a plate map and the batch date', 'which wells, and when they were imaged')], G_LINE, 0.2)
    labs = len(L2['reference_labs'])
    hero = (f'<span style="{SANS} font-size:72px; font-weight:700; letter-spacing:-0.04em; line-height:0.9; color:{G_T};">{L2["n_reference_wells"]:,}</span>'
            f'<span style="display:flex; gap:3px;">{"".join(icon("lab", GREEN, 24) for _ in range(labs))}</span>')
    uses = card(f'background: linear-gradient(#ffffff, #ffffff) padding-box, linear-gradient(90deg, {GREEN}, {PINK}) border-box; border-top:4px solid transparent; padding-top:12px; '      # 4 px less: its edge, so every label sits on one line
                f'box-shadow: 0 1px 2px rgba(20,23,26,0.06), 0 14px 34px rgba(20,23,26,0.10);', 'What Datum Line does with it', INK,
                fig('the map holds untreated wells only', hero,
                    f'<span style="{MONO} font-size:14px; color:{INK2}; text-align:center;">untreated wells of {labs} other labs<br>'
                    f'<span style="color:{PINK}; font-weight:600;">0 treated</span></span>'),
                [('builds the map', 'scale set by the other labs, never its own'),
                 ('answers', '&#8220;normal&#8221; or not, how far it moved, nearest lab')], '#eceff0', 0.35)      # 26 Oct: the ranking and the correction live on archive A17 and A7
    never = card(f'background:{P_TINT};', 'What it never reads', INK,
                 fig('your treated wells',
                     plate(rest, PINK, f'The same plate: the other {len(rest)} wells, the test compounds, are never shared or read.'),
                     count(len(rest), PINK)),
                 [('your results', 'corrected in your building, by you'),
                  ('your name, unless you choose', 'proposed: a number until you opt in')], P_LINE, 0.5)
    return leaves, uses, never


def a18():
    import csv, gzip
    e9 = results('e9-replay.json'); L2 = e9['labs']['source_2']
    plate = L2['batches'][0]['plates'][0]
    wells = [w for w in csv.DictReader(gzip.open('metadata/well.csv.gz', 'rt')) if w['Metadata_Plate'] == plate]
    known = {'JCP2022_037716', 'JCP2022_025848', 'JCP2022_046054', 'JCP2022_035095',      # JUMP's eight positive controls (analysis/e8_pull_wells.py)
             'JCP2022_064022', 'JCP2022_050797', 'JCP2022_012818', 'JCP2022_085227'}
    dmso = {w['Metadata_Well'] for w in wells if w['Metadata_JCP2022'] == 'JCP2022_033924' or w['Metadata_JCP2022'] in known}
    rest = {w['Metadata_Well'] for w in wells} - dmso
    leaves, uses, never = a18_columns(L2, wells, dmso, rest)
    body = f"""<div style="{BOARD}">
  {top_line('A18', 'if asked what is private', 'results/e9, e12 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Control wells are shared.<br><span style="color:{GREEN};">Nothing else is.</span></h2>
    <p style="{LEDE}">Proposed: a free backup of the rest, encrypted with <span style="color:{PINK}; font-weight:600;">your key</span>.</p>
  </div>
  <div style="display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); grid-template-rows:auto 1fr auto auto; column-gap:16px; flex-grow:1; min-height:0;">{leaves}{uses}{never}</div>
  <div class="note" style="{NOTE}">In every analysis here, the map and the correction see untreated wells only &#183; github.com/kat-titter/datum-line/analysis &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A20
def pill(when):
    """A20's today or proposed tag."""
    return (f'<span style="{MONO} font-size:13px; padding:1px 9px; border-radius:999px; border:1px solid {GREEN if when == "today" else FAINT}; '
            f'color:{GREEN if when == "today" else MUTE};">{when}</span>')     # as on A24


def a20_columns(e1, e9, e11, lab, near, farthest, n_batches, own, failed_plates):
    """A20's four columns, each a number, a line and a small figure in one box: provenance, integrity, unknown origin, early warning."""
    W, H = 240, 118                                       # every figure the same box, so the four sit level; short, so the opt-in strip fits under them
    col = lambda title, colour, when, big, items, fig, cap: (
        f'<div class="r" style="flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:center; gap:8px;">{label(title, colour)}{pill(when)}</span>'
        f'<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; padding:6px 0 4px; height:50px; white-space:nowrap;">{big}</span>' + ''.join(
            f'<span style="{SANS} font-size:15px; line-height:1.35; color:{INK if i == 0 else MUTE};">{l}</span>' for i, l in enumerate(items))
        + f'<div style="margin-top:auto; display:flex; flex-direction:column; gap:6px;">{svg(W, H, fig)}<span style="{MONO} font-size:13px; color:{MUTE};">{cap}</span></div></div>')
    T = lambda x, y, s, anchor='middle': f'<text x="{x:.1f}" y="{y:.1f}" style="{MONO}" font-size="13" fill="{MUTE}" text-anchor="{anchor}">{s}</text>'
    # provenance: one square per batch, solid where every well names its own lab
    shares = sorted((b['wells_named_own_lab'] for v in e9.values() for b in v['batches']), reverse=True)
    per_row = 20; pitch = W / per_row; rows = -(-len(shares) // per_row); top = H - rows * pitch
    waffle = [f'<rect x="{(k % per_row) * pitch + 1:.1f}" y="{top + (k // per_row) * pitch + 1:.1f}" width="{pitch - 3:.1f}" height="{pitch - 3:.1f}" rx="2" '
              f'fill="{GREEN}" fill-opacity="{1 if v >= 1 else 0.3}"/>' for k, v in enumerate(shares)]
    # integrity: the known answer, batch by batch, in A8's colours
    S = e11['labs'][lab]['batches']; tallest = max(b['size'] for b in S); w = W / len(S); base = H - 4
    bars = ([f'<rect x="{k * w + 3:.1f}" y="{base - (H - 16) * b["size"] / tallest:.1f}" width="{w - 6:.1f}" height="{(H - 16) * b["size"] / tallest:.1f}" rx="2" '
             f'fill="{INK if b["verdict"] == "failed" else FAINT}"/>' for k, b in enumerate(S)]
            + [f'<path d="M 0 {base} H {W}" stroke="{GRID}" stroke-width="1"/>'])
    # unknown origin: every real batch's distance to its nearest other lab, and the zone beyond the farthest
    X = lambda v: 8 + v / 13 * 220
    rug = ([f'<rect x="{X(farthest):.1f}" y="22" width="{X(13) - X(farthest):.1f}" height="{H - 46}" fill="{PANEL}"/>', T(X((farthest + 13) / 2), 22 + (H - 46) / 2 + 4, 'suspect').replace(f'fill="{MUTE}"', f'fill="{INK2}"')]      # MUTE on the panel is 4.47:1
           + [f'<path d="M {X(v):.1f} 26 V {H - 28}" stroke="{GREEN}" stroke-width="1.5" stroke-opacity="0.4"/>' for v in near]
           + [f'<path d="M {X(farthest):.1f} 18 V {H - 24}" stroke="{INK}" stroke-width="1.5"/>', T(X(farthest) - 5, 14, 'farthest real batch', 'end')]
           + [T(X(v), H - 4, v) for v in (0, 5, 10)])
    # early warning: lab 2's distance from its own first batch, batch by batch; filled where the map flagged it
    L = e9['source_2']['batches']; peak = max(b['from_baseline'] for b in L); moved = next(b for b in L if b['verdict'] == 'outside')
    pts = [(10 + k * 220 / (len(L) - 1), H - 8 - (H - 24) * b['from_baseline'] / peak) for k, b in enumerate(L)]
    line = ([f'<path d="M 0 {H - 4} H {W}" stroke="{GRID}" stroke-width="1"/>', '<path d="' + ' '.join(f'{"M" if k == 0 else "L"} {x:.1f} {y:.1f}' for k, (x, y) in enumerate(pts)) + f'" fill="none" stroke="{PINK}" stroke-width="2" stroke-linejoin="round"/>']
            + [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{PINK if b["verdict"] == "outside" else "#ffffff"}" stroke="{PINK}" stroke-width="1.5"/>' for (x, y), b in zip(pts, L)])
    # every caption two lines of 30 characters or fewer, so the four figures stay level
    where = col('provenance', GREEN, 'today', f'{100 * e1["balanced_accuracy"]:.1f}%', [
        f'of {e1["n_wells"]:,} untreated wells get the right lab, on unseen plates: cells and microscope together.'], waffle, f'1 square = 1 batch<br>solid: every well right &#183; {own}')
    labels = col('integrity', INK, 'today', f'{len(e11["failed"])} batches', [
        'Label: known drug in these wells.', f'Cells: almost no effect, on {failed_plates} plates.'],
        bars, f'{lab_name(lab)} &#183; drug effect per batch<br>dark: failed &#183; A8')
    nowhere = col('unknown origin', INK, 'proposed', f'{farthest:.0f}&#215;', [
        f'Farthest of {n_batches} real batches from its nearest other lab.'],
        rug, 'distance to nearest other lab<br>1 line = 1 real batch')
    sentinel = col('early warning', INK, 'proposed', short_date(moved['date']), [
        f'{moved["date"][:4]}: {lab_name("source_2")}&#8217;s untreated wells moved; its cell count did not.'],
        line, f'{lab_name("source_2")}, since batch 1<br>filled: flagged, A13')
    return where, labels, nowhere, sentinel


def a20():
    e1 = results('e1.json')['all_sources']; e9 = results('e9-replay.json')['labs']; e11 = results('e11-known-answer.json')
    near = sorted(b['to_nearest_other'] for v in e9.values() for b in v['batches'])
    n_batches = len(near); farthest = near[-1]
    own = sum(b['wells_named_own_lab'] >= 1 for v in e9.values() for b in v['batches'])
    failed_plates = sum(f['n_plates'] for f in e11['failed'])
    assert len({f['lab'] for f in e11['failed']}) == 1, 'the worked case is one lab'
    # 17 Nov 2026 (Kat: "more detail on applications for biosecurity"): who uses it, and how, beside the headline; the worked case
    # is the integrity column, its plates counted from results/e11
    users = (f'<div style="flex-grow:1; align-self:center; display:flex; flex-direction:column; gap:5px;">{label("who uses it, and how", GREEN)}'
             + who_uses([('funder or journal', 'checks that data came from the lab on its label'),
                         ('data buyer', f'checks known drugs worked: here, {failed_plates} plates failed'),
                         ('lab or company', 'opts in, to prove what it tests (proposed)')], 16) + '</div>')
    lab = e11['failed'][0]['lab']
    where, labels, nowhere, sentinel = a20_columns(e1, e9, e11, lab, near, farthest, n_batches, own, failed_plates)
    # 26 Oct 2026, proposed: good actors prove what they test. Opt-in only; the map itself stores no results and watches no one's research.
    optin = (f'<div class="r" style="{CARD} padding:12px 20px; display:flex; align-items:center; gap:18px;">'
             f'<span style="display:flex; flex-direction:column; gap:6px; flex-shrink:0;">{label("declared vs observed", INK)}{pill("proposed, opt-in")}</span>'
             f'<span style="{SANS} font-size:15px; line-height:1.4; color:{INK2};">A company that wants the good-actor mark sends treated wells and says what is in them. '
             f'The map flags cells that look like a known toxic class [7]. Only what a lab sends is seen.</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A20', 'if asked about biosecurity', 'results/e1, e9, e11 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Cells show their lab.<br><span style="color:{GREEN};">Labels can lie. Cells cannot.</span></h2>
    {users}
  </div>
  <div style="display:flex; gap:14px; flex-grow:1; min-height:0; align-items:stretch;">{where}{labels}{nowhere}{sentinel}</div>
  {optin}
  <div class="note" style="{NOTE}">Two work today, three are proposed &#183; worked case: {lab_name(lab)}, {len(e11["failed"])} batches, {failed_plates} plates (results/e11) &#183; integrity check uses each plate&#8217;s known-drug wells (A8) &#183; &#215; = times the usual spread of wells within one plate &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A24
def a24():
    """Why a lab would share: what it keeps, what anyone can check, and who can subscribe. Measured where it says today; proposed elsewhere."""
    cards = [      # row 1, owned by the lab, in pink (you); row 2, verified by anyone, in green (the field)
        ('control wells only', 'today', 'no test compound &#183; no target &#183; no result<br>is ever shared or read', INK),
        ('lab keeps its data', 'proposed', 'sharing is opt-in<br>withdraw any time', INK),
        ('low risk by design', 'today', 'cell-line images only<br>no human genetic data &#183; no pathogen data', INK),
        ('signed and timestamped', 'proposed', 'public record &#183; anyone can check<br>dates cannot be changed &#183; blockchain optional', GREEN),
        ('known members', 'proposed', 'verified at sign-up &#183; odd access flagged<br>access log open to members', GREEN),
        ('open code and data', 'today', 'code: MIT, on GitHub<br>data: JUMP, CC0; every number from a script', GREEN),      # 26 Oct (Kat: "ready for desci community")
    ]
    tag = lambda when: (f'<span style="{MONO} font-size:13px; padding:1px 9px; border-radius:999px; border:1px solid {GREEN if when == "today" else "#949c9f"}; '
                        f'color:{GREEN if when == "today" else MUTE};">{when}</span>')
    grid = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.08 * k:.2f}s; grid-column:span 2; {CARD} padding:20px 22px 18px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'<span style="display:flex; justify-content:space-between; align-items:center; gap:10px;">{label(name, colour)}{tag(when)}</span>'
        + (text if text.startswith('<span') else f'<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{text}</span>') + '</div>'
        for k, (name, when, text, colour) in enumerate(cards))
    # the icons of the path on 06 and 10: the map, the certificate, subscriptions; and the lab's share
    icons = dict(PATH_ICONS, share='<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5V12h8.5"/>')
    steps = [('lab shares', 'control images, opt-in<br>credited by name on the map', INK, 'map'),
             ('the map checks', 'how &#8220;normal&#8221; the cells look<br>which lab, what changed', GREEN, 'certificate'),
             ('members subscribe', 'to aligned data<br>from every lab', INK, 'subscriptions'),
             ('lab keeps a share', 'of every membership<br>as long as its data is used', INK, 'share')]
    arrow = f'<span aria-hidden="true" style="flex:0 0 28px; align-self:center; text-align:center; {SANS} font-size:22px; color:{MUTE};">&#8594;</span>'
    flow = (f'<div class="r" style="animation-delay:0.8s; {FIGURE} padding:17px 0 14px; gap:0; align-items:stretch; flex-grow:1;">' + arrow.join(
        f'<div style="flex:1; display:flex; flex-direction:column; justify-content:center; gap:6px; padding:4px 20px; min-width:0;">'
        f'<svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="{colour}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" style="flex-shrink:0; margin-bottom:4px;">{icons[icon]}</svg>'
        f'<span style="{SANS} font-size:22px; font-weight:700; letter-spacing:-0.02em; color:{colour};">{head}</span>'
        f'<span style="{SANS} font-size:18px; line-height:1.4; color:{INK2};">{what}</span></div>'   # 17 Nov night (Kat: "only A24 looks sparse"): the second lines back on the board (26 Oct had sent them to the reader)
        for head, what, colour, icon in steps) + '</div>')
    body = f"""<div style="{BOARD}">
  {top_line('A24', 'if asked why a lab would share', 'results/e1 &#183; proposed where marked')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Owned by the lab.<br><span style="color:{GREEN};">Verified by anyone.</span></h2>
    <p style="{LEDE}"><span style="display:inline-block; vertical-align:-8px; margin-right:10px; line-height:0;">{icon('no-token', PINK, 28)}</span>No crypto token.</p>
  </div>
  <div style="display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:14px; min-height:0;">{grid}</div>
  {flow}
  <div class="note" style="{NOTE}">nothing signed yet &#183; privacy A18 &#183; biosecurity A20 &#183; prices A15</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A25
def a25():
    """The shared data: every lab's controls as one dataset, each batch checked against the field (the table that was slide 07's fourth
    view until 25 Oct 2026). Batches checked per lab from results/e9 and e11; provenance from e1; the terms are proposed."""
    import slide07
    rows = slide07.datasets(results('e9-replay.json')['labs'], results('e12-field-normalization.json')['by_lab'], results('e11-known-answer.json')['failed'])
    e1 = results('e1.json')['all_sources']
    CELL, GAP = 11, 3
    def strip(r):
        fill = PINK if r['lab'] == slide07.LAB else GREEN
        g = ''.join(f'<rect x="{k * (CELL + GAP)}" y="0" width="{CELL}" height="{CELL}" rx="2.5" fill="{fill}"/>' if v not in ('outside', 'failed') else
                    f'<rect x="{k * (CELL + GAP) + 0.75}" y="0.75" width="{CELL - 1.5}" height="{CELL - 1.5}" rx="2" fill="none" stroke="{MUTE}" stroke-width="1.5"/>'
                    for k, v in enumerate(r['verdicts']))
        W = len(r['verdicts']) * (CELL + GAP) - GAP
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {CELL}" width="{W}" height="{CELL}" role="img" '
                f'aria-label="{r["on_map"]} of {r["batches"]} batches checked" style="display:block;">{g}</svg>')
    cols = 'grid-template-columns:120px 70px 1fr 90px;'
    head = (f'<div style="display:grid; {cols} gap:14px; padding:0 18px 8px; border-bottom:1px solid {GRID};">'
            + ''.join(label(t) for t in ('lab', 'plates', 'batches, in run order', 'checked')) + '</div>')
    you = slide07.LAB
    line = lambda r, k: (
        f'<div class="r" style="animation-delay:{0.15 + 0.04 * k:.2f}s; display:grid; {cols} align-items:center; gap:14px; padding:7px 18px; '
        f'background:{"rgba(190,30,116,0.07)" if r["lab"] == you else "transparent"}; border-bottom:1px solid #eceff0;">'
        f'<span style="{SANS} font-size:16px; font-weight:{700 if r["lab"] == you else 500}; color:{PINK if r["lab"] == you else INK};">{lab_name(r["lab"])}{" (you)" if r["lab"] == you else ""}</span>'
        f'<span style="{MONO} font-size:14px; color:{MUTE};">{r["plates"]}</span>{strip(r)}'
        f'<span style="{MONO} font-size:14px; color:{INK2}; text-align:right;">{r["on_map"]} of {r["batches"]}</span></div>')
    table = f'<div class="r" style="animation-delay:0.1s; {CARD} padding:14px 0 4px; display:flex; flex-direction:column; min-height:0; overflow:hidden;">{head}{"".join(line(r, k) for k, r in enumerate(rows))}</div>'
    card = lambda title, text, colour, delay: (f'<div class="r" style="animation-delay:{delay:.2f}s; {CARD} padding:16px 20px; display:flex; flex-direction:column; gap:8px;">'
                                               f'{label(title, colour)}<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">{text}</span></div>')
    side = (f'<div style="display:flex; flex-direction:column; gap:12px;">'
            + card('what a square is', 'one batch of a lab&#8217;s DMSO wells; filled: on the map and its known drugs worked; hollow: off the map, or a known drug failed (A8, A11)', MUTE, 0.3)
            + card('where it came from', f'every well traced to its lab by its images: {100 * e1["balanced_accuracy"]:.1f}% named right of {e1["n_labs"]} labs (A20)', GREEN, 0.4)
            + card('who can use it', 'members, for access to checked data from many labs; the lab keeps its data and a share of every membership (proposed, A15, A24)', PINK, 0.5)
            + '</div>')
    body = f"""<div style="{BOARD}">
  {top_line('A25', 'if asked what the shared data looks like', 'results/e9, e11, e12 &#183; terms proposed')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Every lab&#8217;s controls,<br><span style="color:{PINK};">as one dataset each.</span></h2>
    <p style="{LEDE}">U2OS controls shared by {len(rows)} labs, replayed on public data.<br>Every batch is checked against the field.</p>
  </div>
  <div style="display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:16px; flex-grow:1; min-height:0;">{table}{side}</div>
  <div class="note" style="{NOTE}">batches checked = on the map and known drugs worked &#183; {sum(r["plates"] for r in rows):,} plates &#183; JUMP [7]</div>
</div>"""
    return BASE_CSS, body, None
