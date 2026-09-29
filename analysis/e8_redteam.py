"""e8 red team: does "same drug, different answer" survive the obvious objections?

e8 reports, per positive control, how well plates agree on a compound's effect and
whether disagreement tracks how far a plate's controls sit from the field. Objections
tested here, one at a time, on the same wells and the same definitions:

  own_lab_in_field   e8 compares each plate with a field mean that includes the plate's
                     own lab. Here the field is every OTHER lab (leave one lab out), for
                     both the effect and the control distance.
  between_or_within  Is the link between control distance and disagreement a fact about
                     labs (between) or about plates inside a lab (within)? Lab means are
                     correlated across labs; plate values are correlated after removing
                     each lab's mean, with a null that shuffles plates within their lab.
  magnitude          How much of the spread in effect size lies between labs, as a share
                     of variance, and how the spread inside a lab compares.
  no_position        Everything above with position, count and bookkeeping features
                     removed, in case image size or layout drives the result.

Definitions follow e8_same_drug_different_answer.py: effect = mean(compound wells) minus
mean(DMSO wells) on the same plate, in features z-scored on the field's DMSO wells.

Usage:  python analysis/e8_redteam.py results/e8_profiles.parquet [--perms 500]
Writes: results/e8-redteam.json
"""
import argparse
import json
import re

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

DMSO = 'JCP2022_033924'
POSCON = {'JCP2022_037716': 'AMG900', 'JCP2022_025848': 'dexamethasone', 'JCP2022_046054': 'FK-866',
          'JCP2022_035095': 'LY2109761', 'JCP2022_064022': 'NVS-PAK1-1', 'JCP2022_050797': 'quinidine',
          'JCP2022_012818': 'TC-S-7004', 'JCP2022_085227': 'aloxistatin'}
POSITION = re.compile(r'_(Location|Number|Children|Parent)_|_AreaShape_(Center|BoundingBox)')
SEED = 0


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n else v


def load(path):
    d = pd.read_parquet(path)
    for c in ('Metadata_Source', 'Metadata_Plate', 'Metadata_JCP2022'):
        d[c] = d[c].astype(str)
    feats = [c for c in d.columns if not c.startswith('Metadata_')]
    X = d[feats].apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan)
    X = X.loc[:, X.notna().all() & (X.std() > 0) & (X.abs().max() < 1e6)]
    return d[['Metadata_Source', 'Metadata_Plate', 'Metadata_JCP2022']].reset_index(drop=True), X.reset_index(drop=True)


def plate_table(meta, X):
    """Per plate: lab, DMSO centroid, and the effect vector of each compound."""
    dm = (meta.Metadata_JCP2022 == DMSO).to_numpy()
    mu, sd = X[dm].mean(), X[dm].std().replace(0, np.nan)
    Z = ((X - mu) / sd).fillna(0.0).to_numpy('float32')
    lab = meta.groupby('Metadata_Plate').Metadata_Source.first()
    rows = meta.groupby(['Metadata_Plate', 'Metadata_JCP2022']).indices
    ctrl = {p: Z[i].mean(axis=0) for (p, j), i in rows.items() if j == DMSO}
    effect = {name: {p: Z[i].mean(axis=0) - ctrl[p] for (p, j), i in rows.items() if j == jcp and p in ctrl}
              for jcp, name in POSCON.items()}
    spread = float(np.mean([np.linalg.norm(Z[i] - ctrl[p], axis=1).mean()
                            for (p, j), i in rows.items() if j == DMSO]))
    return lab, ctrl, effect, spread


def within_lab_null(x, y, labs, perms, rng):
    """Spearman after removing lab means, with plates shuffled inside their lab."""
    x = x - x.groupby(labs).transform('mean')
    y = y - y.groupby(labs).transform('mean')
    rho = spearmanr(x, y).statistic
    null = np.array([spearmanr(x.groupby(labs).transform(lambda s: rng.permutation(s.to_numpy())), y).statistic
                     for _ in range(perms)])
    return float(rho), float(null.mean()), float(np.percentile(null, 95)), float((null >= rho).mean())


def analyse(meta, X, perms):
    lab, ctrl, effect, spread = plate_table(meta, X)
    rng = np.random.default_rng(SEED)
    labs = sorted(lab.unique())
    lab_ctrl = {l: np.mean([ctrl[p] for p in ctrl if lab[p] == l], axis=0) for l in labs}
    # control distance to the centroid of every other lab, in within-plate spreads
    d_ctrl = {p: float(np.linalg.norm(v - np.mean([lab_ctrl[l] for l in labs if l != lab[p]], axis=0)) / spread)
              for p, v in ctrl.items()}
    out, pooled = {}, []
    for name, eff in effect.items():
        if len(eff) < 6:
            continue
        lab_eff = {l: np.mean([v for p, v in eff.items() if lab[p] == l], axis=0)
                   for l in labs if any(lab[p] == l for p in eff)}
        rows = []
        for p, v in eff.items():
            others = np.mean([m for l, m in lab_eff.items() if l != lab[p]], axis=0)
            rows.append({'plate': p, 'lab': lab[p], 'control_distance': d_ctrl[p],
                         'disagreement': 1 - float(unit(v) @ unit(others)),
                         'agreement_own_lab': float(unit(v) @ unit(lab_eff[lab[p]])),
                         'size': float(np.linalg.norm(v))})
        t = pd.DataFrame(rows)
        by_lab = t.groupby('lab')[['control_distance', 'disagreement', 'size']].mean()
        between = spearmanr(by_lab.control_distance, by_lab.disagreement)
        rho_w, null_mean, null_95, p_w = within_lab_null(t.control_distance, t.disagreement, t.lab, perms, rng)
        grand = t['size'].mean()
        ss_between = (t.groupby('lab')['size'].transform('mean') - grand).pow(2).sum()
        out[name] = {
            'n_plates': len(t), 'n_labs': int(t.lab.nunique()),
            'agreement_with_other_labs': round(1 - float(t.disagreement.mean()), 3),
            'agreement_with_own_lab': round(float(t.agreement_own_lab.mean()), 3),
            'between_labs': {'spearman': round(float(between.statistic), 3), 'p': float(between.pvalue),
                             'n_labs': len(by_lab)},
            'within_labs': {'spearman': round(rho_w, 3), 'null_mean': round(null_mean, 3),
                            'null_95pct': round(null_95, 3), 'p_permutation': p_w},
            'effect_size': {'mean': round(grand, 2),
                            'share_of_variance_between_labs': round(float(ss_between / (t['size'] - grand).pow(2).sum()), 3),
                            'cv_of_lab_means_pct': round(100 * float(by_lab['size'].std() / by_lab['size'].mean()), 1),
                            'median_cv_within_lab_pct': round(100 * float(
                                (t.groupby('lab')['size'].std() / t.groupby('lab')['size'].mean()).median()), 1)}}
        pooled.append(t.assign(compound=name))
    allp = pd.concat(pooled, ignore_index=True)
    key = allp.lab + '|' + allp.compound   # remove lab and compound means together
    rho_w, null_mean, null_95, p_w = within_lab_null(allp.control_distance, allp.disagreement, key, perms, rng)
    return {'n_features': int(X.shape[1]), 'within_plate_spread': round(spread, 2), 'compounds': out,
            'pooled_within_lab_and_compound': {'n_points': len(allp), 'spearman': round(rho_w, 3),
                                               'null_mean': round(null_mean, 3), 'null_95pct': round(null_95, 3),
                                               'p_permutation': p_w}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('profiles')
    ap.add_argument('--perms', type=int, default=500)
    a = ap.parse_args()
    meta, X = load(a.profiles)
    report = {'settings': {'perms': a.perms, 'seed': SEED, 'field': 'every lab except the plate\'s own'},
              'n_wells': len(meta), 'n_plates': int(meta.Metadata_Plate.nunique()),
              'n_labs': int(meta.Metadata_Source.nunique()),
              'all_features': analyse(meta, X, a.perms)}
    keep = [c for c in X.columns if not POSITION.search(c)]
    report['no_position'] = analyse(meta, X[keep], a.perms)
    json.dump(report, open('results/e8-redteam.json', 'w'), indent=2)
    for k in ('all_features', 'no_position'):
        print(k, report[k]['n_features'], 'features; pooled within lab:', report[k]['pooled_within_lab_and_compound'])
        for c, v in report[k]['compounds'].items():
            print(f"  {c:14} other labs {v['agreement_with_other_labs']:.2f}  own lab {v['agreement_with_own_lab']:.2f}  "
                  f"between rho {v['between_labs']['spearman']:+.2f} (p {v['between_labs']['p']:.3f})  "
                  f"within rho {v['within_labs']['spearman']:+.2f} (p {v['within_labs']['p_permutation']:.3f})  "
                  f"size: {v['effect_size']['share_of_variance_between_labs']:.2f} between labs")


if __name__ == '__main__':
    main()
