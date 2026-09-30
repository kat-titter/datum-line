"""e12: does normalising a lab to the field bring its answers back?

The certificate measures where a lab's controls sit. The same measurement can be used as
a map: move each batch's control wells onto the field's control wells, apply that same
move to the treated wells, and ask whether the batch's drug answers now agree better

  with the lab's own first batch     (is the lab's own baseline tighter?)
  with every other lab               (is the lab comparable with the field?)
  with the right compound            (can a drug measured here be recognised there?)

Only untreated wells are used to learn the move. The positive controls are the test.

Space      features z-scored on the DMSO wells of every other lab, clipped, then projected
           on the first K principal components of those labs' DMSO wells
Raw        effect = mean(compound wells) - mean(DMSO wells) on the same plate
Own        each feature standardised on the batch's own DMSO wells before projection: the
           usual normalisation to a plate's or batch's own controls
Scaled     the same idea inside the projection: each component divided by the batch's own
           DMSO standard deviation
Field      the batch's DMSO mean and covariance are moved onto the field's:
           x' = C_field^(1/2) C_batch^(-1/2) (x - m_batch), with C_batch shrunk toward C_field
Matching   a batch's effect of compound c is matched to the nearest of the field's eight
           compound effects; the share matched to c itself is reported (chance 1 in 8)
Margin     agreement with the right compound minus mean agreement with the other seven.
           A move that made every effect look alike would raise agreement and not margin,
           so margin is the number to trust.
Reported   over the compounds on which labs agree (results/e10, compounds_pooled)

Usage:  python analysis/e12_field_normalization.py [--k 200] [--shrink 0.2] [--tag -k100]
Needs:  cache/poscon/, results/e9-replay.json, results/e10-certificate-predicts-answer.json
Writes: results/e12-field-normalization.json
"""
import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.decomposition import PCA

import e10_certificate_predicts_answer as e10
import field as fd

SEED = 0
METHODS = ('raw', 'own', 'scaled', 'field')
SD_FLOOR = 0.1      # of the field's standard deviation: a feature that does not vary in a batch is not divided by nothing


def sqrtm(C, inverse=False, floor=1e-6):
    w, V = np.linalg.eigh(C)
    w = np.maximum(w, floor * w.max())
    return (V * (w ** (-0.5 if inverse else 0.5))) @ V.T


def cosine(a, b):
    return float(e10.unit(a) @ e10.unit(b))


def effects_for(meta, X, judged, k, shrink, rng):
    """Every batch's effect of every compound, four ways, in a space the judged lab did not shape."""
    Z = e10.scaled(meta, X, judged)
    lab = meta.Metadata_Source.to_numpy(); dmso = (meta.Metadata_JCP2022 == e10.DMSO).to_numpy()
    ref = np.flatnonzero(dmso & (lab != judged))
    pca = PCA(n_components=k, random_state=SEED).fit(Z[rng.choice(ref, min(len(ref), 20000), replace=False)])
    P = pca.transform(Z).astype('float64')
    W = pca.components_.astype('float64')
    C_field = np.cov(P[ref].T)
    half_field = sqrtm(C_field)

    out = {m: {} for m in METHODS}
    idx = meta.groupby(['Metadata_Source', 'Metadata_Batch']).indices
    for (s, b), rows in idx.items():
        m = meta.iloc[rows]
        d = (m.Metadata_JCP2022 == e10.DMSO).to_numpy()
        if d.sum() < 30:
            continue
        Pb, Zb = P[rows], Z[rows]
        Pd = Pb[d]
        C_batch = (1 - shrink) * np.cov(Pd.T) + shrink * C_field
        move = half_field @ sqrtm(C_batch, inverse=True)
        sd = Pd.std(axis=0)
        sd_features = np.maximum(Zb[d].std(axis=0), SD_FLOOR)
        plate = m.Metadata_Plate.to_numpy(); jcp = m.Metadata_JCP2022.to_numpy()
        per, per_features = {}, {}
        for p in np.unique(plate):
            on = plate == p
            if not (on & d).any():
                continue
            ctrl, ctrl_features = Pb[on & d].mean(axis=0), Zb[on & d].mean(axis=0)
            for j, name in e10.POSCON.items():
                w = on & (jcp == j)
                if w.any():
                    per.setdefault(name, []).append(Pb[w].mean(axis=0) - ctrl)
                    per_features.setdefault(name, []).append(Zb[w].mean(axis=0) - ctrl_features)
        for name, v in per.items():
            raw = np.mean(v, axis=0)
            out['raw'][(s, b, name)] = raw
            out['own'][(s, b, name)] = W @ (np.mean(per_features[name], axis=0) / sd_features)
            out['scaled'][(s, b, name)] = raw / sd
            out['field'][(s, b, name)] = move @ raw
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--k', type=int, default=200)
    ap.add_argument('--shrink', type=float, default=0.2)
    ap.add_argument('--reuse', action='store_true', help='summarise results/e12-points.csv without recomputing')
    ap.add_argument('--tag', default='', help='added to the output file names, for sensitivity runs')
    a = ap.parse_args()
    replay = json.load(open('results/e9-replay.json'))['labs']
    pooled = json.load(open('results/e10-certificate-predicts-answer.json'))['compounds_pooled']
    failed = {(f['lab'], f['batch']) for f in json.load(open('results/e10-certificate-predicts-answer.json'))['batches_whose_positive_controls_failed']}
    rows = []
    if not a.reuse:
        meta, X, _ = e10.load()
        rng = np.random.default_rng(SEED)
    for lab in ([] if a.reuse else sorted(set(meta.Metadata_Source) & set(replay))):
        eff = effects_for(meta, X, lab, a.k, a.shrink, rng)
        info = {b['batch']: b for b in replay[lab]['batches']}
        first = replay[lab]['batches'][0]['batch']
        for method in METHODS:
            E = eff[method]
            fieldv = {}
            for name in e10.POSCON.values():
                labs = {}
                for (s, b, c), v in E.items():
                    if c == name and s != lab and (s, b) not in failed:
                        labs.setdefault(s, []).append(v)
                fieldv[name] = np.mean([np.mean(v, axis=0) for v in labs.values()], axis=0)
            names = list(fieldv)
            for (s, b, c), v in E.items():
                if s != lab or b not in info or (s, b) in failed:
                    continue
                own = E.get((lab, first, c))
                rows.append({'lab': lab, 'batch': b, 'run': info[b]['run'], 'compound': c, 'method': method,
                             'drift': info[b]['from_baseline'], 'outside': info[b]['verdict'] == 'outside',
                             'agree_field': cosine(v, fieldv[c]),
                             'agree_wrong': float(np.mean([cosine(v, fieldv[n]) for n in names if n != c])),
                             'agree_own': cosine(v, own) if own is not None and b != first else np.nan,
                             'matched': names[int(np.argmax([cosine(v, fieldv[n]) for n in names]))] == c,
                             'size': float(np.linalg.norm(v))})
        print(lab, 'done', flush=True)
    if a.reuse:
        t = pd.read_csv(f'results/e12-points{a.tag}.csv')
    else:
        t = pd.DataFrame(rows)
        t.to_csv(f'results/e12-points{a.tag}.csv', index=False)
    n_plates = int(json.load(open('results/e10-certificate-predicts-answer.json'))['n_plates'])
    t = t[t.compound.isin(pooled)]
    per_batch = t.groupby(['lab', 'batch', 'run', 'drift', 'outside', 'method'], as_index=False).agg(
        agree_field=('agree_field', 'mean'), agree_own=('agree_own', 'mean'), matched=('matched', 'mean'), size=('size', 'mean'),
        agree_wrong=('agree_wrong', 'mean'))
    per_batch['margin'] = per_batch.agree_field - per_batch.agree_wrong
    wide = per_batch.pivot_table(index=['lab', 'batch', 'run', 'drift', 'outside'], columns='method',
                                 values=['agree_field', 'agree_own', 'matched', 'size', 'margin']).reset_index()

    def summary(w):
        o = {'n_batches': int(len(w))}
        for metric in ('agree_own', 'agree_field', 'margin', 'matched'):
            o[metric] = {m: round(float(w[(metric, m)].mean()), 3) for m in METHODS}
            for m in METHODS[1:]:
                d = (w[(metric, m)] - w[(metric, 'raw')]).dropna()
                o[metric][f'{m}_better_in'] = f'{int((d > 0).sum())} of {len(d)}'
                o[metric][f'{m}_p_wilcoxon'] = float(wilcoxon(d).pvalue) if len(d) > 5 and (d != 0).any() else None
            d = (w[(metric, 'field')] - w[(metric, 'own')]).dropna()      # the frame against the usual practice, not only against nothing
            o[metric]['field_better_than_own_in'] = f'{int((d > 0).sum())} of {len(d)}'
            o[metric]['field_against_own_p_wilcoxon'] = float(wilcoxon(d).pvalue) if len(d) > 5 and (d != 0).any() else None
        cv = lambda m: float(np.median([g[('size', m)].std() / g[('size', m)].mean() for _, g in w.groupby(('lab', '')) if len(g) > 2] or [np.nan]))
        o['effect_size_cv_across_batches_within_lab'] = {m: round(cv(m), 3) for m in METHODS}
        return o

    drifted = wide[wide[('drift', '')] >= wide[('drift', '')].quantile(0.75)]
    out = {'k': a.k, 'shrink': a.shrink, 'compounds': pooled, 'n_plates': n_plates,
           'n_labs': int(t.lab.nunique()), 'batches_left_out_for_failed_positive_controls': len(failed),
           'every_batch': summary(wide), 'most_drifted_quarter': summary(drifted),
           'outside_batches': summary(wide[wide[('outside', '')]]), 'by_lab': {l: summary(g) for l, g in wide.groupby(('lab', ''))},
           'lab_2': [{'batch': r[('batch', '')], 'run': int(r[('run', '')]), 'drift': float(r[('drift', '')]), 'outside': bool(r[('outside', '')]),
                      **{f'{metric}_{m}': (None if pd.isna(r[(metric, m)]) else round(float(r[(metric, m)]), 3))
                         for metric in ('agree_own', 'agree_field') for m in METHODS}}
                     for _, r in wide[wide[('lab', '')] == 'source_2'].sort_values(('run', '')).iterrows()]}
    means = {l: v['agree_field'] for l, v in out['by_lab'].items()}
    out['labs_where_field_is_highest'] = f"{sum(v['field'] > max(v['raw'], v['own']) for v in means.values())} of {len(means)}"
    json.dump(out, open(f'results/e12-field-normalization{a.tag}.json', 'w'), indent=1)
    for k in ('every_batch', 'most_drifted_quarter', 'outside_batches'):
        print(k, json.dumps(out[k]))


if __name__ == '__main__':
    main()
