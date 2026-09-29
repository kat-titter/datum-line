"""e1 red team: is "control wells name the lab" real, or an artefact of how it was tested?

Every test reuses the e1 model and out-of-fold procedure from e1_lab_classifier.py and
changes exactly one thing, so a change in accuracy has one explanation.

  baseline         e1 as specified, plates held out
  permuted         training labels shuffled within each fold; must fall to chance
  batch_held_out   GroupKFold by batch instead of plate: no imaging run on both sides
  same_microscope  only labs on one microscope model (CV8000, read from the JUMP
                   microscope table), so the instrument model cannot be what is recognised
  no_all_vehicle   all-vehicle plates removed, in case they were handled differently
  no_position      position, count and parent/child bookkeeping features removed; these
                   depend on image size and plate layout, not on cells
  family:<name>    one CellProfiler feature family at a time
  plate_centred    each plate's own DMSO mean subtracted from its wells, which is what
                   plate-level normalisation does to a control well
  plate_scaled     centred and divided by the plate's own DMSO standard deviation

It also ranks single features by eta squared (share of variance between labs) and fits
a one-feature classifier on the top few, as a check for a trivial leak.

To keep each fit near a minute, wells are subsampled to at most --wells-per-plate per
plate with a fixed seed. Plate statistics for the plate_* tests use every well.

Usage:  python analysis/e1_redteam.py [--wells-per-plate 16] [--perms 1] [--plate 1053600681]
Needs:  cache/wells/ from e1_pull_wells.py, metadata/, results/e1-predictions.csv (the wells e1 scored)
Writes: results/e1-redteam.json
"""
import argparse
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

import e1_lab_classifier as e1

SEED = 0
# Bookkeeping and position features: functions of image size, plate layout or object
# order rather than of cell state.
POSITION = re.compile(r'_(Location|Number|Children|Parent)_|_AreaShape_(Center|BoundingBox)')
FAMILY = re.compile(r'^(?:Cells|Cytoplasm|Nuclei|Image)_([A-Za-z]+)_')


def subsample(d, n, seed=SEED):
    """At most n wells per plate, reproducibly."""
    rng = np.random.default_rng(seed)
    keep = d.groupby('Metadata_Plate', sort=False).apply(
        lambda g: pd.Series(rng.permutation(g.index.to_numpy())[:n]), include_groups=False)
    return np.sort(keep.to_numpy().ravel())


def family_of(name):
    m = FAMILY.match(name)
    return m.group(1) if m else 'Other'


def fit(X, d, groups_col='Metadata_Plate', permute_seed=None, plate=None):
    """One out-of-fold run. Returns the numbers that go in the report."""
    y = d['Metadata_Source'].to_numpy()
    g = d[groups_col].to_numpy()
    t = time.time()
    cv = e1.cross_validate(np.ascontiguousarray(X, dtype='float32'), y, g, permute_seed=permute_seed)
    out = {'n_wells': int(len(y)), 'n_labs': int(pd.unique(y).size), 'n_features': int(X.shape[1]),
           'held_out_by': groups_col, 'chance': 1 / pd.unique(y).size,
           'balanced_accuracy': float(balanced_accuracy_score(y, cv['pred'])),
           'per_fold': [float(v) for v in cv['per_fold']],
           'all_fits_converged': all(f['converged'] for f in cv['fits']),
           'seconds': round(time.time() - t)}
    if plate is not None:
        on = (d['Metadata_Plate'] == plate).to_numpy()
        if on.any():
            own = d.loc[on, 'Metadata_Source'].iloc[0]
            votes = pd.Series(cv['pred'][on]).value_counts()
            out['target_plate'] = {'plate': plate, 'own_lab': own, 'wells_scored': int(on.sum()),
                                   'share_named_own_lab': float((cv['pred'][on] == own).mean()),
                                   'votes': {k: int(v) for k, v in votes.items()}}
    return out


def eta_squared(X, y):
    """Share of each feature's variance that lies between labs."""
    grand = X.mean(axis=0)
    total = ((X - grand) ** 2).sum(axis=0)
    between = np.zeros(X.shape[1])
    for lab in np.unique(y):
        rows = X[y == lab]
        between += len(rows) * (rows.mean(axis=0) - grand) ** 2
    return between / np.where(total > 0, total, np.nan)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--wells-per-plate', type=int, default=16)
    ap.add_argument('--perms', type=int, default=1)
    ap.add_argument('--plate', default='1053600681')
    a = ap.parse_args()

    scored = pd.read_csv('results/e1-predictions.csv', dtype=str, usecols=['Metadata_Source', 'Metadata_Plate'])
    d_all = e1.load_wells(sources=sorted(scored.Metadata_Source.unique()))
    d_all = d_all[d_all.Metadata_Plate.isin(set(scored.Metadata_Plate))].reset_index(drop=True)
    X_all = e1.feature_matrix(d_all)
    finite = np.isfinite(X_all.to_numpy()).all(axis=0)
    X_all = X_all.loc[:, finite]
    cols = np.array(X_all.columns)
    print(f'{len(d_all)} wells, {d_all.Metadata_Plate.nunique()} plates, {X_all.shape[1]} features', flush=True)

    # plate-level statistics use every well on the plate
    by_plate = X_all.groupby(d_all['Metadata_Plate'].to_numpy())
    centred = X_all - by_plate.transform('mean')
    scaled = centred / by_plate.transform('std').replace(0, np.nan)

    idx = subsample(d_all, a.wells_per_plate)
    d = d_all.loc[idx].reset_index(drop=True)
    X = X_all.loc[idx].to_numpy()
    report = {'settings': {'wells_per_plate': a.wells_per_plate, 'seed': SEED, 'target_plate': a.plate,
                           'model_and_split': 'as results/e1.json unless a test says otherwise',
                           'jump_metadata_commit': Path('metadata/COMMIT').read_text().strip()},
              'tests': {}}
    T = report['tests']

    def log(name):
        r = T[name]
        print(f"{name:28} {r['balanced_accuracy']:.4f}  (chance {r['chance']:.3f}, "
              f"{r['n_features']} features, {r['n_wells']} wells, {r['seconds']} s)", flush=True)

    T['baseline'] = fit(X, d, plate=a.plate); log('baseline')
    # whole batches held out: each lab's batches are dealt round-robin into the five folds,
    # so every fold tests batches the model never saw. Labs with one batch cannot take part.
    known = d['Metadata_Batch'].notna().to_numpy()
    n_batches = d[known].groupby('Metadata_Source')['Metadata_Batch'].nunique()
    multi = d['Metadata_Source'].isin(n_batches[n_batches >= e1.N_FOLDS].index).to_numpy() & known
    db = d[multi].reset_index(drop=True)
    deal = {}
    for lab, g in db.groupby('Metadata_Source'):
        for k, batch in enumerate(sorted(g['Metadata_Batch'].unique())):
            deal[(lab, batch)] = f'fold{k % e1.N_FOLDS}'
    db['Metadata_BatchFold'] = [deal[k] for k in zip(db['Metadata_Source'], db['Metadata_Batch'])]
    T['batch_held_out'] = fit(X[multi], db, groups_col='Metadata_BatchFold', plate=a.plate); log('batch_held_out')
    T['batch_held_out']['labs'] = sorted(db['Metadata_Source'].unique())
    T['batch_held_out']['labs_left_out_for_too_few_batches'] = sorted(set(d['Metadata_Source']) - set(db['Metadata_Source']))

    scopes = pd.read_csv('metadata/microscope_config.csv').set_index('Metadata_Source')['Metadata_Microscope_Name']
    CV8000 = sorted(set(scopes[scopes == 'CV8000'].index) & set(d['Metadata_Source']))
    same = d['Metadata_Source'].isin(CV8000).to_numpy()
    T['same_microscope'] = fit(X[same], d[same].reset_index(drop=True), plate=a.plate); log('same_microscope')
    T['same_microscope']['labs'] = CV8000

    veh = d['Metadata_AllVehicle'].to_numpy()
    T['no_all_vehicle'] = fit(X[~veh], d[~veh].reset_index(drop=True)); log('no_all_vehicle')

    position = np.array([bool(POSITION.search(c)) for c in cols])
    T['no_position'] = fit(X[:, ~position], d, plate=a.plate); log('no_position')
    T['no_position']['features_removed'] = int(position.sum())

    families = pd.Series([family_of(c) for c in cols])
    for fam, n in families.value_counts().items():
        if n >= 10:
            T[f'family:{fam}'] = fit(X[:, (families == fam).to_numpy()], d); log(f'family:{fam}')

    for name, table in (('plate_centred', centred), ('plate_scaled', scaled)):
        Xp = table.loc[idx].to_numpy()
        ok = np.isfinite(Xp).all(axis=0) & (Xp.std(axis=0) > 0)
        T[name] = fit(Xp[:, ok], d, plate=a.plate); log(name)

    eta = pd.Series(eta_squared(X.astype('float64'), d['Metadata_Source'].to_numpy()), index=cols)
    top = eta.sort_values(ascending=False).head(15)
    report['single_features'] = {
        'eta_squared_top15': {k: round(float(v), 4) for k, v in top.items()},
        'share_of_features_with_eta_squared_over_0.5': float((eta > 0.5).mean()),
        'one_feature_classifier': {k: fit(X[:, [list(cols).index(k)]], d)['balanced_accuracy']
                                   for k in top.index[:3]}}
    print('top single features:', report['single_features']['one_feature_classifier'], flush=True)

    # last, because a model fitted to shuffled labels converges slowly
    nulls = [fit(X, d, permute_seed=SEED + i) for i in range(a.perms)]
    T['permuted'] = {**nulls[0], 'balanced_accuracy_each': [n['balanced_accuracy'] for n in nulls],
                     'balanced_accuracy': float(np.mean([n['balanced_accuracy'] for n in nulls]))}; log('permuted')

    Path('results').mkdir(exist_ok=True)
    json.dump(report, open('results/e1-redteam.json', 'w'), indent=2)
    print('wrote results/e1-redteam.json')


if __name__ == '__main__':
    main()
