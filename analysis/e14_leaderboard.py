"""e14: the leaderboard. Every batch of every lab scored against the whole field on its
untreated wells alone, so a lab can compete on how it grows cells and never on its results.

Four measures per batch, each in units of the field's within-plate spread, lower is better,
each ranked as a percentile among every batch in the field:

  centre     median distance of the batch's plates from the field's centre (the mean of the
             other labs' centres): how typical the cells are
  tightness  mean distance of the batch's plates from their own centroid: how alike the plates are
  steadiness distance of the batch's centroid from the lab's previous batch: how repeatable
  cells      |log ratio| of cells per untreated well to the field's median

Field score = 100 minus the mean percentile, so 100 is the best batch the field has seen.
The judged lab never sets its own scale: each lab is scored in a space z-scored on the other labs.
Streaks come from the replay (results/e9): consecutive batches in distribution.

Usage:  python analysis/e14_leaderboard.py
Needs:  cache/wells/, results/e9-replay.json
Writes: results/e14-leaderboard.json
"""
import json

import numpy as np
import pandas as pd

import field as fd

MEASURES = ('centre', 'tightness', 'steadiness', 'cells')


def score_lab(d, X, lab):
    F = fd.Field(d, X, judged_lab=lab)
    centre = np.mean([F.lab_centre[l] for l in F.ref_labs], axis=0)
    field_cells = float(np.median(F.cells[np.isin(F.lab, F.ref_labs)]))
    order, dates = fd.ordered_batches(F.batch[F.lab == lab])
    rows, prev = [], None
    for k, b in enumerate(order):
        r = F.of(lab, b)
        c = F.cent[r].mean(axis=0)
        rows.append({'lab': lab, 'batch': b, 'run': k + 1, 'date': str(dates[b].date()) if dates[b] is not None else None,
                     'n_plates': int(len(r)), 'cells_per_well': round(float(F.cells[r].mean()), 1),
                     'centre': float(np.median(F.distance(r, centre))),
                     'tightness': float(np.linalg.norm(F.cent[r] - c, axis=1).mean() / F.spread) if len(r) > 1 else np.nan,
                     'steadiness': float(np.linalg.norm(c - prev) / F.spread) if prev is not None else np.nan,
                     'cells': abs(float(np.log(F.cells[r].mean() / field_cells)))})
        prev = c
    return rows


def streaks(replay):
    out = {}
    for lab, v in replay.items():
        run, best, cur = 0, 0, 0
        for b in v['batches']:
            run = run + 1 if b['verdict'] != 'outside' else 0
            best = max(best, run)
        out[lab] = {'longest': best, 'current': run}
    return out


def main():
    d, X = fd.load()
    replay = json.load(open('results/e9-replay.json'))['labs']
    labs = sorted(set(d.Metadata_Source) & set(replay))
    t = pd.DataFrame([r for lab in labs for r in score_lab(d, X, lab)])
    for m in MEASURES:
        t[f'{m}_pct'] = t[m].rank(pct=True) * 100          # NaN stays NaN and is left out of the mean
    t['score'] = 100 - t[[f'{m}_pct' for m in MEASURES]].mean(axis=1)
    t = t.sort_values('score', ascending=False).reset_index(drop=True)
    t['rank'] = np.arange(1, len(t) + 1)
    rnd = lambda v: None if pd.isna(v) else round(float(v), 2)
    row = lambda r: {'rank': int(r['rank']), 'lab': r['lab'], 'batch': r['batch'], 'date': r['date'], 'run': int(r['run']), 'n_plates': int(r['n_plates']),
                     'score': round(float(r['score']), 1), 'cells_per_well': r['cells_per_well'], **{m: rnd(r[m]) for m in MEASURES},
                     'percentile': {m: rnd(r[f'{m}_pct']) for m in MEASURES}}
    by_lab = []
    st = streaks(replay)
    for lab, g in t.groupby('lab'):
        best = g.iloc[0]
        by_lab.append({'lab': lab, 'n_batches': int(len(g)), 'median_score': round(float(g.score.median()), 1),
                       'best': row(best), 'streak': st[lab],
                       **{f'median_{m}': rnd(g[m].median()) for m in MEASURES}})
    by_lab.sort(key=lambda v: -v['median_score'])
    field_median = {m: rnd(t[m].median()) for m in MEASURES}
    badges = {'closest to the centre': min(by_lab, key=lambda v: v['median_centre'])['lab'],
              'tightest plates': min(by_lab, key=lambda v: v['median_tightness'])['lab'],
              'steadiest': min((v for v in by_lab if v['median_steadiness'] is not None), key=lambda v: v['median_steadiness'])['lab'],
              'longest streak': max(by_lab, key=lambda v: v['streak']['longest'])['lab'],
              'best batch': t.iloc[0]['lab']}
    out = {'n_batches': int(len(t)), 'n_labs': len(labs), 'n_plates': int(t.n_plates.sum()), 'measures': list(MEASURES),
           'score': '100 minus the mean percentile rank of the four measures among every batch in the field',
           'top': [row(r) for _, r in t.head(10).iterrows()],
           'by_lab': by_lab, 'badges': badges, 'field_median': field_median,
           'lab_2': [row(r) for _, r in t[t.lab == 'source_2'].sort_values('run').iterrows()]}
    json.dump(out, open('results/e14-leaderboard.json', 'w'), indent=1)
    print(json.dumps({'top': out['top'][:5], 'by_lab': [(v['lab'], v['median_score'], v['best']['rank'], v['streak']) for v in by_lab], 'badges': badges}, indent=1))


if __name__ == '__main__':
    main()
