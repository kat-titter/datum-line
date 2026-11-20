"""The proposed plan and market, and the appendix boards that show them. PRESEED and MULTIPLIER (the eighteen months asked
for), MARKET and SCREEN (the market assumptions) and plan() (the five-year path) are one source for the boards and for
slide06.py, slide09.py, slide10.py, coherence.py and build_docs.py, which read them through appendix. Boards: A4 (why the
model is not the moat), A15 (who pays?), A21 (how much, and what for?), A22 (how big?) and A23 (what cell data is worth)."""

from parts import *
from appendix_kit import BOARD, H2, LEDE, FIGURE, NOTE, top_line, card


# ------------------------------------------------------------------ A21
PRESEED = [  # eighteen months; every line is a proposal
    ('executive director, to run it', '18 months', 180),      # 17 Nov (Kat: "Nonprofit FRO", "An executive director"): was 'leader'
    ('scientific lead (me)', '18 months', 180),
    ('ML engineer', 'from month 7', 160),
    ('payroll overhead', '20% of salaries', 104),
    ('benchmark playground', '~60 plates &#183; planted faults', 120),     # where it is made: partner labs or a contract lab (the doc and A21's card)
    ('partner-lab bench time', '3 labs &#183; controls they already image &#183; reagent top-ups &#183; shipping', 30),
    ('compute and storage', 'images &#183; models &#183; hosting &#183; API', 45),
    ('legal, IP, insurance, accounting', 'incorporation to first contract', 45),
    ('travel and partner visits', '2 benchmark partners &#183; 3 labs', 20),
]
MULTIPLIER = 2       # the rule: most things take two to three times the time and money they should; plan at two


def preseed_total():
    sub = sum(k for _, _, k in PRESEED)
    return sub, round(sub * MULTIPLIER)


def a21():
    from slide09 import MILESTONES as M     # local: slide09 imports this module at load time
    sub, total = preseed_total()
    bench = sum(k for name, _, k in PRESEED if name in ('benchmark playground', 'partner-lab bench time'))
    people = sum(k for _, _, k in PRESEED[:4])   # executive director, scientific lead, ML engineer, payroll overhead
    run = sub - people - bench                   # compute, legal, travel
    seg = lambda k, c: f'<div style="flex:{k} 0 0; background:{c};"></div>'
    tag = lambda k, s, c: f'<span style="flex:{k} 0 0; min-width:0; {MONO} font-size:13px; line-height:1.3; color:{c};">{s}<br>{100 * k / sub:.0f}%</span>'
    split = (f'<div style="flex-grow:1; min-width:0; display:flex; flex-direction:column; gap:6px;">'
             f'<span style="{MONO} font-size:13px; color:{MUTE};">${sub}k plan + ${total - sub}k contingency = ${total / 1000:.2f}M asked</span>'
             f'<div style="display:flex; gap:2px; height:16px; border-radius:8px; overflow:hidden;">{seg(people, INK)}{seg(bench, GREEN)}{seg(run, FAINT)}</div>'
             f'<div style="display:flex; gap:2px;">{tag(people, "people", INK)}{tag(bench, "benchmark", GREEN)}{tag(run, "other", MUTE)}</div></div>')
    row = lambda name, what, k, strong=False, colour=INK, rule='border-bottom:1px solid #eceff0;', size=15: (
        f'<div style="display:grid; grid-template-columns:260px 1fr 90px; gap:16px; align-items:baseline; padding:4px 10px; {rule}">'
        f'<span style="{SANS} font-size:{size}px; font-weight:{700 if strong else 600}; color:{colour};">{name}</span>'
        f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{what}</span>'
        f'<span style="{SANS} font-size:{size}px; font-weight:{700 if strong else 500}; color:{colour}; text-align:right;">{f"${k / 1000:.2f}M" if k >= 1000 else f"${k}k"}</span></div>')
    board = {'benchmark playground': 'A16'}        # the board that shows what the line buys
    table = (''.join(row(name, what + (f' &#183; {board[name]}' if name in board else ''), k) for name, what, k in PRESEED)
             + row('planned', 'sum', sub, rule=f'border-top:1px solid {FAINT}; border-bottom:1px solid #eceff0;')
             + row('+ contingency', f'most things take 2&#8211;3&#215; the time and money planned &#183; we plan for {MULTIPLIER}&#215;', total - sub, colour=MUTE)
             + row('asked &#183; 18 months', '', total, True, PINK, rule=f'border-top:2px solid {INK}; padding-top:6px;', size=17))
    decide = lambda title, body, colour, grow=1: (f'<div class="r" style="animation-delay:0.5s; flex:{grow}; {CARD} padding:10px 16px; display:flex; flex-direction:column; gap:4px;">'
                                          f'{label(title, colour)}<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{body}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A21', 'if asked how much and what for', 'proposed &#183; every line an assumption')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">About ${total / 1000:.1f}M <span style="color:{PINK};">for eighteen months.</span></h2>
    {split}
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:10px 8px 4px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{table}</div>
  <div style="display:flex; gap:16px; align-items:stretch;">
    {decide('No in-house lab', 'Partner labs or a contract lab.<br>Own lab: costs more, proves less.', MUTE)}
    {decide('What the money must show', f'<b style="color:{GREEN}">1</b> {M[0][0]}, paid from this grant &#183; <b style="color:{GREEN}">2</b> {M[1][0]}<br><b style="color:{GREEN}">3</b> {M[2][0]} &#183; <b style="color:{GREEN}">4</b> {M[3][0]} &#8594; five-year FRO funding', MUTE, grow=2)}
  </div>
  <div class="note" style="{NOTE}">salaries below market &#183; executive director and scientific lead paid &#183; nothing here committed</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A22
MARKET = {  # (low, base, high); every one an assumption until a count replaces it
    'organisations screening a few lines deep': (200, 400, 800),
    'lines each runs per quarter': (2, 4, 8),
    'price per line per quarter, $k': (5, 10, 15),
    'organisations screening panels of hundreds to thousands of lines': (10, 25, 50),
    'site licence per year, $k': (50, 150, 300),
    'companies buying cell data they did not make': (50, 150, 300),
    'purchased datasets each places on the map per year': (2, 4, 8),
    'price per dataset membership, $k': (10, 25, 50),
    'benchmark partners': (4, 10, 20),
    'membership per partner per year, $k': (50, 100, 200),
}


# one screen run on cells that had changed, in the author's experience (white paper): runs a week, weeks, $k a run
SCREEN = (3, 17, 50)


def market(i):
    v = {k: r[i] for k, r in MARKET.items()}
    subs = (v['organisations screening a few lines deep'] * v['lines each runs per quarter'] * v['price per line per quarter, $k'] * 4
            + v['organisations screening panels of hundreds to thousands of lines'] * v['site licence per year, $k'])
    certs = v['companies buying cell data they did not make'] * v['purchased datasets each places on the map per year'] * v['price per dataset membership, $k']
    bench = v['benchmark partners'] * v['membership per partner per year, $k']
    return subs, certs, bench


def plan():
    """The base case by stream, and the five-year path to a tenth of it: one source for slide 07 (who pays) and board A22 (the path).
    The path is an assumption: first revenue of about $0.1M in year 2 (09's first paying member), a tenth of the base case in year 5."""
    b = {k: v[1] for k, v in MARKET.items()}
    streams = [('screening labs', b['organisations screening a few lines deep'] * b['lines each runs per quarter'] * b['price per line per quarter, $k'] * 4,
                f"${b['price per line per quarter, $k']}k/line/quarter", '#0a5c46'),
               ('buyers of cell data', b['companies buying cell data they did not make'] * b['purchased datasets each places on the map per year'] * b['price per dataset membership, $k'],
                f"${b['price per dataset membership, $k']}k/dataset", '#36a883'),
               ('big screening panels', b['organisations screening panels of hundreds to thousands of lines'] * b['site licence per year, $k'],
                f"${b['site licence per year, $k']}k/year", '#0f8f6c'),
               ('benchmark partners', b['benchmark partners'] * b['membership per partner per year, $k'],
                f"${b['membership per partner per year, $k']}k/year", '#8fc9b2')]
    total = sum(v for _, v, _, _ in streams) / 1000               # $M a year
    assert round(total * 1000) == sum(market(1)), 'the streams and the base case disagree'
    tenth = total / 10
    first, years = 0.1, 5
    rate = (tenth / first) ** (1 / (years - 2))
    path = [0] + [first * rate ** k for k in range(years - 1)]      # $M a year, years 1 to 5
    money = lambda v: '$0' if not v else (f'${v:.1f}M' if v < 10 else f'${v:.0f}M')
    return streams, total, tenth, path, rate, money


def dollars(k):
    """$k in thousands, as $1.5M (whole millions without the .0) or $50k."""
    return f'${k / 1000:.1f}M'.replace('.0M', 'M') if k >= 1000 else f'${k}k'


def a22_table(low, base, high):
    """A22's assumptions, low, base and high, each stream's sum under its rows and the total. Returns head, rows and total."""
    row = lambda name, vals, strong=False, colour=INK, extra='': (
        f'<div style="display:grid; grid-template-columns:1fr 110px 110px 110px; gap:14px; align-items:baseline; padding:2px 10px; border-bottom:1px solid #eceff0;{extra}">'
        f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 500}; color:{colour};">{name}</span>'
        + ''.join(f'<span style="{SANS} font-size:14px; font-weight:{700 if strong else 400}; color:{colour if strong else (INK if j == 1 else MUTE)}; text-align:right;">{x}</span>'
                  for j, x in enumerate(vals)) + '</div>')     # the base column in ink, low and high muted
    head = row('assumption', ('low', 'base', 'high'), True, MUTE)
    SHOW = {'organisations screening a few lines deep': 'organisations testing drugs on a few cell lines',     # plain words on the board; MARKET keys stay
            'lines each runs per quarter': 'cell lines each one uses per quarter',
            'price per line per quarter, $k': 'price per cell line per quarter, $k',
            'organisations screening panels of hundreds to thousands of lines': 'organisations testing drugs on hundreds to thousands of cell lines'}
    keys = list(MARKET)
    streams = [('per-line checks and site licences, per year', keys[:5], 0),
               ('dataset memberships on purchased data, per year', keys[5:8], 1),
               ('benchmark membership, per year', keys[8:], 2)]
    rows = ''.join(''.join(row(SHOW.get(k, k), tuple(f'{x:,}' for x in MARKET[k])) for k in ks)
                   + row(name, tuple(dollars(x[i]) for x in (low, base, high)), True, INK2, ' border-bottom-color:#949c9f;')
                   for name, ks, i in streams)
    total = row('total per year, if every buyer joined', tuple(dollars(sum(x)) for x in (low, base, high)), True, INK, f' border-top:2px solid {INK}; border-bottom:none;')
    return head, rows, total


def a22_bar(base):
    """A22's base case as one bar, one segment per stream, with the five-year target marked at a tenth."""
    subs, certs, bench = base
    tenth = 100 * (sum(base) // 10) / sum(base)
    seg = lambda v, fill, name: (f'<div style="flex:{v} 0 0; min-width:0; background:{fill}; display:flex; flex-direction:column; justify-content:center; align-items:flex-end; '
                                 f'padding:0 {8 if name else 0}px; {MONO} font-size:13px; line-height:1.2; color:{INK if fill == GREENS[1] else "#ffffff"}; white-space:nowrap;">{name}</div>')
    GREENS = [plan()[0][k][3] for k in (0, 1, 3)]      # 17 Nov: slide 07's stream colours (screening, buyers of cell data, benchmark), so bar and slide read as one
    figure = (f'<div class="r" style="animation-delay:0.5s; flex:2; {FIGURE} flex-direction:column; justify-content:center; gap:8px;">'
              f'{label("base case &#183; per year", INK)}'
              f'<div style="position:relative; display:flex; height:40px; border-radius:4px; overflow:hidden;">'
              f'{seg(subs, GREENS[0], f"screening<br>{dollars(subs)}")}{seg(certs, GREENS[1], f"datasets<br>{dollars(certs)}")}{seg(bench, GREENS[2], "")}'
              f'<div style="position:absolute; left:{tenth:.1f}%; top:0; bottom:0; border-left:2px dashed #ffffff;"></div></div>'
              f'<div style="display:flex; justify-content:space-between; {MONO} font-size:13px; white-space:nowrap;">'
              f'<span style="padding-left:{tenth:.1f}%; color:{PINK};">&#8593; five-year target &#183; a tenth &#183; {dollars(sum(base) // 10)}</span>'
              f'<span style="color:{MUTE};">benchmark {dollars(bench)} &#8593;</span></div></div>')
    return figure


def a22_path(base):
    """A22's five-year path (17 Nov: it left slide 07), from the plan slide 07 uses. Returns the figure and the yearly rate."""
    # 17 Nov (pitch minimum): the five-year path left slide 07 and is drawn here, in the lede slot, from the helper slide 07 uses
    _, _, tenth_m, path, rate, money = plan()
    assert round(tenth_m * 1000) == sum(base) // 10, 'the path ends on the tenth the bar marks'
    pw, ph, px0, pstep, pbw, pyb, pmax = 420, 104, 150, 56, 44, 82, 50
    pg = [text(0, 38, 'five-year path', 15, INK, weight=700), text(0, 60, 'revenue a year', 15, INK2),
          f'<path d="M {px0 - 8} {pyb} H {pw}" stroke="{MUTE}" stroke-width="1.5"/>']
    for i, v in enumerate(path):
        x, h, hot = px0 + i * pstep, max(v / tenth_m * pmax, 2) if v else 0, i == len(path) - 1
        if h:
            pg.append(f'<rect x="{x}" y="{pyb - h:.1f}" width="{pbw}" height="{h:.1f}" rx="3" fill="{PINK if hot else GREEN}"/>')
        pg.append(text(x + pbw / 2, pyb - h - 6, money(v), 14, PINK if hot else INK, 'middle', 700 if hot else 400))
        pg.append(text(x + pbw / 2, pyb + 18, f'year {i + 1}' if not i else str(i + 1), 14, INK2, 'middle'))
    path_fig = (f'<div class="r" style="animation-delay:0.3s; flex:0 0 {pw}px; align-self:flex-end;">'
                + svg(pw, ph, pg, aria='Revenue a year in the five-year path: $0 in year 1, then ' + ', '.join(money(v) for v in path[1:])
                      + ' in years 2 to 5; year 5 is a tenth of the base case.') + '</div>')
    return path_fig, rate


def a22():
    low, base, high = (market(i) for i in range(3))
    head, rows, total = a22_table(low, base, high)
    figure = a22_bar(base)
    runs, weeks, run = SCREEN
    screen, cert = runs * weeks * run, MARKET['price per dataset membership, $k'][1]      # $k: the screen to redo, and one dataset membership at the base price
    note = lambda title, body, colour: (f'<div class="r" style="animation-delay:0.5s; flex:1; {CARD} padding:10px 16px; display:flex; flex-direction:column; justify-content:center; gap:4px;">'      # 17 Nov night: centred (Kat)
                                        f'{label(title, colour)}<span style="{SANS} font-size:15px; line-height:1.35; color:{INK};">{body}</span></div>')
    path_fig, rate = a22_path(base)
    body = f"""<div style="{BOARD}">
  {top_line('A22', 'if asked how big', 'every count and price an assumption')}
  <div style="display:flex; gap:40px; align-items:baseline; justify-content:space-between;">
    <h2 style="{H2} width:700px;">About {dollars(sum(base))} a year in revenue, <span style="color:{PINK};">if everyone joined.</span></h2>
    {path_fig}
  </div>
  <div class="r" style="animation-delay:0.2s; {CARD} padding:8px; display:flex; flex-direction:column; flex-shrink:0;">{head}{rows}{total}</div>
  <div style="display:flex; gap:16px; align-items:stretch; flex-grow:1; min-height:0;">
    {figure}
    {note('Why buyers pay', f'A line checked late, in a screen I ran:<br>{runs} runs a week &#215; {weeks} weeks &#215; ${run}k &#8776; ${(screen + 50) // 100 / 10:.1f}M to redo.<br>'
                            f'A ${cert}k dataset membership: about {100 * cert / screen:.0f}% of that.', PINK)}
  </div>
  <div class="note" style="{NOTE}">prices proposed on A15 &#183; academic labs join free &#183; they are the map, not the revenue &#183; path assumed: about &#215;{rate:.0f} a year from year 2</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A4
def a4():
    """The cell-counting paper [2]: its abstract, excerpted verbatim, with three sentences lit."""
    hi = lambda s, colour=PINK: f'<mark style="background:{colour}1f; color:{INK}; border-radius:4px; padding:0 3px; box-shadow:0 0 0 1px {colour}44;">{s}</mark>'
    abstract = (                                     # shortened only by whole sentences and clauses, each gap marked
        '&#8230; ' + hi('counting cells achieves unexpectedly high performance in these benchmarks, making them less useful for discerning whether '
                        'additional properties, such as phenotypic profiles (mRNA or Cell Painting), provide additional useful information on bioactivity.')
        + ' &#8230; ' + hi('we recommend filtering benchmarks to exclude such assays and including a cell-count baseline.', GREEN)
        + ' &#8230; ' + hi('we confirm that models leveraging Cell Painting image-based profiles outperformed the baseline cell count model.', GREEN)
        + ' &#8230;')
    key = (f'<div style="display:flex; gap:22px; align-items:center; margin-top:auto; padding-top:10px; border-top:1px solid #eceff0; {MONO} font-size:13px; letter-spacing:0.1em; color:{MUTE};">'
           f'<span style="text-transform:uppercase;">abstract excerpt &#183; verbatim</span><span>{hi("finding")}</span><span>{hi("recommendation &#183; what held up", GREEN)}</span></div>')
    stat = lambda big, small, colour: (f'<div style="display:flex; flex-direction:column; gap:4px;"><span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{colour}; height:40px;">{big}</span>'
                                       f'<span style="{SANS} font-size:14px; line-height:1.3; color:{MUTE};">{small}</span></div>')
    body = f"""<div style="{BOARD}">
  {top_line('A4', 'if asked why the model is not the moat', 'Nature Communications &#183; 2026 &#183; [2]')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:560px;">Weak benchmarks.<br><span style="color:{PINK};">Counting cells often wins.</span></h2>
    <p style="{LEDE}">I coauthored this paper.<br>Benchmarks decide which model looks good.</p>
  </div>
  <div class="r" style="animation-delay:0.2s; flex-grow:1; min-height:0; {CARD} padding:18px 22px 14px; display:flex; flex-direction:column; gap:10px;">
    <p style="margin:0; {SANS} font-size:26px; line-height:1.5; color:{INK}; text-wrap:pretty;">{abstract}</p>{key}
  </div>
  <div class="r" style="animation-delay:0.6s; display:grid; grid-template-columns:1fr 1fr 1.6fr; gap:24px; align-items:start; {CARD} padding:12px 20px;">
    {stat('209 and 270', 'tests in two popular benchmarks<br>many really measure cell health', INK)}
    {stat('Images win', 'on 24 tests aimed at one protein each<br>Cell Painting beat the cell count', GREEN)}
    <div style="display:flex; flex-direction:column; gap:4px;">{label('Why it matters here', PINK)}<span style="{SANS} font-size:18px; line-height:1.35; color:{INK};">Whoever sets the baseline sets the benchmark.</span>
      <span style="{MONO} font-size:13px; line-height:1.5; color:{MUTE};">benchmark playground &#183; a cell-count baseline on every task &#183; planted faults &#183; every model scored &#183; A16</span></div>
  </div>
  <div class="note" style="{NOTE}">Seal S, Dee W, &#8230; <span style="color:{PINK}; font-weight:600;">Titterton K</span>, &#8230; Carpenter AE. Counting cells can accurately predict small-molecule bioactivity benchmarks. <em>Nat Commun</em>, 2026.</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A15
def a15():
    """Who pays: every row is a membership to the repository (26 Oct, Kat: "product is really subscription/membership to data repo"); labs
    join free by uploading; screening teams pay first. Prices are A22's assumptions."""
    from slide09 import ICON     # local: slide09 imports this module at load time
    rng = lambda key: f'~${MARKET[key][0]}&#8211;{MARKET[key][2]}k'
    # what each row builds, drawn with the path's own icons and colours (slides 06, 09, 10): map and subscriptions green, certificate pink, benchmark flag green
    icons = {'map': PATH_ICONS['map'], 'certificate': PATH_ICONS['certificate'], 'benchmark': ICON['flag'], 'subscriptions': PATH_ICONS['subscriptions']}
    tone = {'map': GREEN, 'certificate': GREEN, 'benchmark': GREEN, 'subscriptions': GREEN}
    # 26 Oct 2026 (Kat): labs pay their way by uploading; AI teams pay the most, by API, and that is the main revenue
    rows = [('labs and core facilities', 'membership: the repository and the map;<br>a check on every batch, the leaderboard', 'nothing: uploading controls earns it', 'the map', 'map', GREEN),
            ('teams that run cell screens all&#160;year', 'membership: a check on every batch they run', f'{rng("price per line per quarter, $k")}/line/quarter', 'first revenue', 'subscriptions', INK),
            ('AI labs and model builders', 'membership by API: aligned raw images from every lab', 'the most: priced by use, not yet set', 'main revenue', 'subscriptions', INK),
            ('companies that buy cell data', 'membership: each dataset they buy, placed on the map', f'{rng("price per dataset membership, $k")}/dataset', 'data revenue', 'subscriptions', INK),
            ('benchmark partners', 'membership: a test set with faults planted on purpose', f'{rng("membership per partner per year, $k")}/year', 'the standard', 'benchmark', INK)]
    cols = 'grid-template-columns:270px 1fr 1fr 160px;'
    head = (f'<div style="display:grid; {cols} gap:24px; padding:0 20px 10px; border-bottom:1px solid #d3d8da;">'
            + ''.join(label(s) for s in ('who', 'what they get', 'what they pay', 'what it builds')) + '</div>')
    mark = lambda step: (f'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="{tone[step]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
                         f'aria-hidden="true" style="vertical-align:-4px; margin-right:9px;">{icons[step]}</svg>')
    body_rows = ''.join(
        f'<div class="r" style="animation-delay:{0.2 + 0.1 * k:.2f}s; display:grid; {cols} gap:24px; align-items:baseline; flex:1; align-content:center; padding:16px 20px; '
        f'{"border-bottom:1px solid #eceff0;" if k < len(rows) - 2 else ""}{" border-top:1px dashed " + GREEN + ";" if who.startswith("then") else ""}">'
        f'<span style="{SANS} font-size:18px; font-weight:600; color:{INK if not who.startswith("then") else GREEN};">{who}</span>'
        f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK2};">{get}</span>'
        f'<span style="{SANS} font-size:16px; font-weight:600; line-height:1.35; color:{colour};">{pay}</span>'
        f'<span style="{SANS} font-size:16px; white-space:nowrap; color:{INK2};">{mark(step)}{builds}</span></div>'
        for k, (who, get, pay, builds, step, colour) in enumerate(rows))
    body = f"""<div style="{BOARD}">
  {top_line('A15', 'if asked who pays', 'proposed &#183; prices are the assumptions on A22')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:700px;">Labs earn access by uploading.<br><span style="color:{GREEN};">AI teams pay the most, by API.</span></h2>
    <p style="{LEDE}"></p>
  </div>
  <div class="r" style="animation-delay:0.1s; {CARD} padding:18px 4px 6px; display:flex; flex-direction:column; flex-grow:1; min-height:0;">{head}{body_rows}</div>
  <div class="note" style="{NOTE}">only control wells are shared, untreated and known drugs, never a test compound &#183; privacy A18 &#183; the lab&#8217;s share A24</div>
</div>"""
    return BASE_CSS, body, None


# ------------------------------------------------------------------ A23
def a23():
    """What data is worth, and why cell data does not convert: public figures with numbered references (figures/worth.py)."""
    from worth import DEALS, PRICES, SITES, REFS, DETAIL
    from slide06 import sites_chart
    # plainer words than slide 06, from the same sources: worth.py and sites_chart stay as slide 06 reads them
    plain = {11: 'paid by Roche for one cell dataset', 12: 'pledged for cell data to train AI<br>funders get it a year early'}
    prices = [(big, plain.get(ref, w), ref) for big, w, ref in PRICES]
    chart = sites_chart(halo="#ffffff")
    (w0, w1), (a0, a1) = SITES['within'], SITES['across']
    agree = results('e12-field-normalization.json')['every_batch']      # what the map buys, as A14 shows it: same drugs, labs closer
    n_batches, closer = agree['n_batches'], int(agree['agree_field']['field_better_than_own_in'].split()[0])
    for old, new in (('% replicate<', '%<'), ('% agree<', '%<'), ('>% of compounds<', '>drugs whose repeats look alike<'),
                     (f'Inside one lab {w0} to {w1} percent of compounds replicate; between labs {a0} to {a1} percent agree.',
                      f'Same lab: {w0} to {w1} percent of drugs repeat alike; different labs: {a0} to {a1} percent.')):
        assert chart.count(old) == 1, f'sites_chart changed: {old}'
        chart = chart.replace(old, new)
    number = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    deal = lambda k, big, name, what, more, ref: (
        f'<div class="r" style="animation-delay:{0.2 + 0.12 * k:.2f}s; flex:1; {CARD} padding:16px 20px 14px; display:flex; flex-direction:column; gap:8px; min-width:0;">'
        f'{label(name, MUTE)}<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{INK};">{big}</span>'
        f'<span style="{SANS} font-size:15px; line-height:1.4; color:{INK2};">{what}</span>'
        f'<span style="margin-top:auto; {MONO} font-size:13px; line-height:1.4; color:{MUTE};">{more} [{ref}]</span></div>')   # level across the three
    deals = ''.join(deal(k, big, name, what, more, ref) for k, ((big, what, ref), (name, _, _), more) in enumerate(zip(prices, DEALS, DETAIL)))
    sites = (f'<div class="r" style="animation-delay:0.6s; {FIGURE} gap:28px; align-items:center; flex-grow:1;">'
             f'<div style="flex:0 0 560px; display:flex; flex-direction:column; gap:6px;">{label(str(SITES["n_sites"]) + " European labs, one protocol", INK)}'
             f'<span style="{SANS} font-size:16px; line-height:1.35; color:{INK2};">same cells, same reagents, shipped to every lab [{SITES["ref"]}]</span>{chart}</div>'
             f'<div style="display:flex; flex-direction:column; gap:10px; min-width:0; align-self:stretch; justify-content:center; border-left:1px solid #e4e8e9; padding-left:28px;">'
             f'{label("what the paper says", MUTE)}'
             f'<span style="{SANS} font-size:26px; font-weight:600; line-height:1.25; color:{INK}; text-wrap:balance;">&#8220;{SITES["quote"]}&#8221; '
             f'<span style="{MONO} font-size:13px; font-weight:400; color:{MUTE};">[{SITES["ref"]}]</span></span>'
             f'<div style="display:flex; flex-direction:column; gap:6px; margin-top:12px; padding-top:16px; border-top:1px solid #e4e8e9;">'
             f'{label("on one shared map &#183; JUMP [7]", GREEN)}'
             f'<span style="{SANS} font-size:40px; font-weight:700; letter-spacing:-0.035em; line-height:1; color:{GREEN};">{closer} of {n_batches}</span>'
             f'<span style="{SANS} font-size:16px; line-height:1.4; color:{INK};">batches: labs agree more than on their own controls, A14</span></div></div></div>')
    refs = ('[7] JUMP, 2023 &#183; [10] TechCrunch, 2025 &#183; [11] Recursion, 2025 &#183; [12] eWeek, 2026 &#183; [13] Wolff et al., <em>iScience</em>, 2025 &#183; '
            'full references in the README')
    body = f"""<div style="{BOARD}">
  {top_line('A23', 'if asked what cell data is worth', 'public figures [10]&#8211;[13] &#183; results/e12')}
  <div style="display:flex; gap:40px; align-items:baseline;">
    <h2 style="{H2} width:620px;">Data has a price.<br><span style="color:{PINK};">Cell data needs a standard.</span></h2>
    <p style="{LEDE}">{number[len(prices)].capitalize()} public prices.<br>Same cells, {number[SITES['n_sites']]} labs, different results.</p>
  </div>
  <div style="display:flex; gap:14px; align-items:stretch;">{deals}</div>
  {sites}
  <div class="note" style="{NOTE}">{refs}</div>
</div>"""
    return BASE_CSS, body, None
