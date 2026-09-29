"""e10: does the number on the certificate predict the answer a drug gives?

e9 gives every batch of every lab a drift from the lab's own baseline. JUMP runs the same
positive controls on every compound plate. So for every batch we can ask how well the
lab's measured effect of a fixed compound still agrees

  with the field    cosine between the batch's effect and the mean effect of every other
                    lab (lab means averaged, so a large lab does not dominate)
  with itself       cosine between the batch's effect and the same lab's first-batch effect

and whether that agreement falls as the certificate's drift rises.

Effect     mean(compound wells) - mean(DMSO wells), per plate, then averaged over the
           batch's plates; features z-scored on the DMSO wells of every other lab, clipped
Compounds  the positive controls the field agrees on: mean agreement between labs above
           AGREE in this data. The weak ones are reported but not pooled.
Tests      1. Inside labs: Spearman between drift and agreement across batches, after
              removing each lab's mean; null by shuffling batches inside their lab.
           2. Flagged against unflagged batches of the same lab: difference in agreement;
              exact null over every way of choosing that many batches from the lab.
Caveats    In lab 2 the flagged batches are also the last three, so the flag and the
           calendar cannot be separated inside that lab. Test 1 uses every lab.
           A batch whose positive controls show no effect at all (e11) says nothing about
           drift, so test 1 is reported with and without such batches, and without each
           of the labs that carry flagged batches.

Usage:  python analysis/e10_certificate_predicts_answer.py
Needs:  cache/poscon/ from e8_pull_wells.py, results/e9-replay.json, metadata/
Writes: results/e10-certificate-predicts-answer.json
"""
import json
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import e1_lab_classifier as e1
import field as fd

DMSO = 'JCP2022_033924'
POSCON = {'JCP2022_037716': 'AMG900', 'JCP2022_025848': 'dexamethasone', 'JCP2022_046054': 'FK-866',
          'JCP2022_035095': 'LY2109761', 'JCP2022_064022': 'NVS-PAK1-1', 'JCP2022_050797': 'quinidine',
          'JCP2022_012818': 'TC-S-7004', 'JCP2022_085227': 'aloxistatin'}
AGREE = 0.5
FAIL = 0.3          # a batch's positive controls failed when agreement is below this ...
FAIL_SIZE = 0.25    # ... and the effect is smaller than this share of the lab's median effect
PERMS = 2000
SEED = 0


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n else v


def load():
    meta, X = fd.load_poscon()
    return meta, X.to_numpy(), list(X.columns)


def scale(meta, X, judged):
    """Mean and standard deviation of the DMSO wells of every lab but the judged one."""
    ref = (meta.Metadata_Source != judged).to_numpy() & (meta.Metadata_JCP2022 == DMSO).to_numpy()
    mu, sd = X[ref].mean(axis=0), X[ref].std(axis=0)
    return mu, sd, sd > 0


def scaled(meta, X, judged):
    mu, sd, ok = scale(meta, X, judged)
    return np.clip((X[:, ok] - mu[ok]) / sd[ok], -fd.CLIP, fd.CLIP)


def batch_effects(meta, X, judged, Z=None, control=None):
    """Effect of every compound in every batch of every lab, scaled without the judged lab.

    control, if given, marks the DMSO wells allowed to serve as the plate's control."""
    Z = scaled(meta, X, judged) if Z is None else Z
    allowed = np.ones(len(meta), bool) if control is None else control
    idx = meta.groupby(['Metadata_Source', 'Metadata_Batch', 'Metadata_Plate', 'Metadata_JCP2022']).indices
    ctrl = {k[:3]: Z[i[allowed[i]]].mean(axis=0) for k, i in idx.items() if k[3] == DMSO and allowed[i].any()}
    per_plate = {}
    for (s, b, p, j), i in idx.items():
        if j in POSCON and (s, b, p) in ctrl:
            per_plate.setdefault((s, b, POSCON[j]), []).append(Z[i].mean(axis=0) - ctrl[(s, b, p)])
    return {k: np.mean(v, axis=0) for k, v in per_plate.items()}, {k: len(v) for k, v in per_plate.items()}


def batch_drift(meta, Z, lab, wells):
    """Median distance of each batch's plates from the lab's first batch, from the given DMSO wells."""
    here = (meta.Metadata_Source == lab).to_numpy() & (meta.Metadata_JCP2022 == DMSO).to_numpy() & wells
    m = meta[here]
    cent = pd.DataFrame(Z[here]).groupby([m.Metadata_Batch.to_numpy(), m.Metadata_Plate.to_numpy()]).mean()
    order, _ = fd.ordered_batches(m.Metadata_Batch)
    baseline = cent.loc[order[0]].mean().to_numpy()
    return {b: float(np.median(np.linalg.norm(cent.loc[b].to_numpy() - baseline, axis=1))) for b in order}


def positive_controls_failed(agreement, size, lab):
    """True for batches where the known answer did not come out: see e11."""
    median = size.groupby(lab).transform('median')
    return (agreement < FAIL) & (size < FAIL_SIZE * median)


def centred(x, groups):
    return x - x.groupby(groups).transform('mean')


def within_lab_spearman(t, x, y, rng):
    a, b = centred(t[x], t.lab), centred(t[y], t.lab)
    rho = spearmanr(a, b).statistic
    null = np.array([spearmanr(a.groupby(t.lab).transform(lambda s: rng.permutation(s.to_numpy())), b).statistic
                     for _ in range(PERMS)])
    return {'spearman': round(float(rho), 3), 'null_mean': round(float(null.mean()), 3),
            'null_5pct': round(float(np.percentile(null, 5)), 3),
            'p_one_sided': float(max((null <= rho).mean(), 1 / PERMS)), 'n_batches': int(len(t)),
            'n_labs': int(t.lab.nunique())}


def flagged_against_rest(g, y):
    """Exact test: is the flagged batches' mean lower than that of every other equal-sized choice?"""
    v = g[y].to_numpy(); f = g.outside.to_numpy(); k = int(f.sum())
    if k == 0 or k == len(v):
        return None
    observed = v[f].mean() - v[~f].mean()
    diffs = np.array([v[list(c)].mean() - np.delete(v, list(c)).mean() for c in combinations(range(len(v)), k)])
    return {'flagged': round(float(v[f].mean()), 3), 'unflagged': round(float(v[~f].mean()), 3),
            'difference': round(float(observed), 3), 'n_flagged': k, 'n_unflagged': int(len(v) - k),
            'n_arrangements': int(len(diffs)), 'p_exact_one_sided': float((diffs <= observed + 1e-12).mean())}


def main():
    replay = json.load(open('results/e9-replay.json'))['labs']
    meta, X, _ = load()
    labs = sorted(set(meta.Metadata_Source) & set(replay))
    print(f'{len(meta):,} wells, {meta.Metadata_Plate.nunique():,} plates, {len(labs)} labs, {X.shape[1]:,} features', flush=True)

    # split-half control: drift is measured on one random half of each plate's DMSO wells and
    # the drug effect against the other half, so no well contributes to both numbers
    half = np.random.default_rng(SEED).random(len(meta)) < 0.5
    rows = []
    for lab in labs:
        Z = scaled(meta, X, lab)
        eff, n_plates = batch_effects(meta, X, lab, Z)
        eff_b, _ = batch_effects(meta, X, lab, Z, control=~half)
        drift_a = batch_drift(meta, Z, lab, half)
        del Z
        drift = {b['batch']: b for b in replay[lab]['batches']}
        first = replay[lab]['batches'][0]['batch']
        for name in POSCON.values():
            others = {}
            for (s, b, c), v in eff.items():
                if c == name and s != lab:
                    others.setdefault(s, []).append(v)
            if len(others) < 3:
                continue
            fieldv = np.mean([np.mean(v, axis=0) for v in others.values()], axis=0)
            for (s, b, c), v in eff.items():
                if s == lab and c == name and b in drift:
                    own, own_b, v_b = eff.get((lab, first, name)), eff_b.get((lab, first, name)), eff_b.get((s, b, c))
                    later = own is not None and b != first
                    rows.append({'lab': lab, 'batch': b, 'run': drift[b]['run'], 'compound': name,
                                 'n_plates': n_plates[(s, b, c)],
                                 'drift': drift[b]['from_baseline'], 'ratio': drift[b]['from_baseline'] / drift[b]['to_nearest_other'],
                                 'outside': drift[b]['verdict'] == 'outside',
                                 'agree_field': float(unit(v) @ unit(fieldv)),
                                 'agree_own_baseline': float(unit(v) @ unit(own)) if later else np.nan,
                                 'drift_half': drift_a.get(b, np.nan),
                                 'agree_own_half': float(unit(v_b) @ unit(own_b)) if later and v_b is not None and own_b is not None else np.nan,
                                 'size': float(np.linalg.norm(v))})
        print(lab, 'done', flush=True)
    t = pd.DataFrame(rows)
    between = t.groupby('compound').agree_field.mean().round(3)
    strong = sorted(between[between > AGREE].index)
    rng = np.random.default_rng(SEED)

    pooled = (t[t.compound.isin(strong)].groupby(['lab', 'batch', 'run', 'drift', 'ratio', 'outside'], as_index=False)
              .agg(agree_field=('agree_field', 'mean'), agree_own_baseline=('agree_own_baseline', 'mean'),
                   size=('size', 'mean'), drift_half=('drift_half', 'mean'), agree_own_half=('agree_own_half', 'mean')))
    pooled['failed'] = positive_controls_failed(pooled.agree_field, pooled['size'], pooled.lab)
    later = pooled.dropna(subset=['agree_own_baseline'])

    def both(rows):
        return {'drift_vs_agreement_with_field': within_lab_spearman(rows, 'drift', 'agree_field', rng),
                'drift_vs_agreement_with_own_baseline': within_lab_spearman(rows.dropna(subset=['agree_own_baseline']),
                                                                            'drift', 'agree_own_baseline', rng)}
    flagged_labs = sorted(pooled[pooled.outside].lab.unique())
    sensitivity = {'without batches whose positive controls failed': both(pooled[~pooled.failed])}
    for lab in flagged_labs:
        sensitivity[f'without {lab}'] = both(pooled[pooled.lab != lab])
    sensitivity['without any lab that has a flagged batch'] = both(pooled[~pooled.lab.isin(flagged_labs)])
    sensitivity['split half: drift and effect from different DMSO wells'] = {
        'drift_vs_agreement_with_own_baseline': within_lab_spearman(pooled.dropna(subset=['agree_own_half', 'drift_half']),
                                                                    'drift_half', 'agree_own_half', rng)}
    raw = pooled.dropna(subset=['agree_own_baseline'])
    sensitivity['not centred by lab: every batch as one point'] = {
        'drift_vs_agreement_with_own_baseline': {'spearman': round(float(spearmanr(raw.drift, raw.agree_own_baseline).statistic), 3),
                                                 'n_batches': int(len(raw)), 'n_labs': int(raw.lab.nunique())}}
    out = {'n_wells': int(len(meta)), 'n_plates': int(meta.Metadata_Plate.nunique()), 'n_labs': len(labs),
           'n_features': int(X.shape[1]), 'agreement_with_the_field_by_compound': between.to_dict(),
           'compounds_pooled': strong, 'threshold': AGREE, 'permutations': PERMS,
           'inside_labs': both(pooled), 'sensitivity': sensitivity,
           'batches_whose_positive_controls_failed': [{'lab': r.lab, 'batch': r.batch} for r in pooled[pooled.failed].itertuples()],
           'by_compound': {c: within_lab_spearman(t[t.compound == c], 'drift', 'agree_field', rng) for c in POSCON.values()
                           if (t.compound == c).sum() > 20},
           'flagged_against_unflagged': {}, 'batches': {}}
    for lab, g in pooled.groupby('lab'):
        g = g.sort_values('run')
        out['batches'][lab] = [{'batch': r.batch, 'run': int(r.run), 'drift': r.drift, 'outside': bool(r.outside),
                                'positive_controls_failed': bool(r.failed), 'effect_size': round(r.size, 2),
                                'agree_field': round(r.agree_field, 3),
                                'agree_own_baseline': None if np.isnan(r.agree_own_baseline) else round(r.agree_own_baseline, 3)}
                               for r in g.itertuples()]
        g = g[~g.failed]          # a batch with no measurable effect has no answer to compare
        test = flagged_against_rest(g, 'agree_field')
        if test:
            test['with_own_baseline'] = flagged_against_rest(g.dropna(subset=['agree_own_baseline']), 'agree_own_baseline')
            out['flagged_against_unflagged'][lab] = test
    json.dump(out, open('results/e10-certificate-predicts-answer.json', 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ('compounds_pooled', 'inside_labs', 'sensitivity',
                                          'batches_whose_positive_controls_failed', 'flagged_against_unflagged')}, indent=1))
    for lab in out['flagged_against_unflagged']:
        print(lab, [(b['run'], 'O' if b['outside'] else '.', b['agree_field'], b['agree_own_baseline']) for b in out['batches'][lab]])


if __name__ == '__main__':
    main()
