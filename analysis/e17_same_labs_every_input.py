"""e17: which input names the lab best, when every input sees the same labs, plates and wells?

The deck's lab-naming numbers come from different label sets: the six-dye profile from
e1-redteam's batch_held_out (10 labs, chance one in ten), DNA and RGB images from e15
(11 labs, one in eleven), brightfield from e15 (8 labs, one in eight). A higher number on
fewer labs is not a better input. Here every input is scored on one population and one split,
so every row has the same chance.

  Population  the plates that have all three e15 image embeddings; brightfield exists in
              8 labs, so these are its 1,338 plates, and DNA and RGB are cut to the same plates;
              what that cut drops from e15's DNA and RGB population is counted lab by lab
  Unit        one DMSO well per plate, the one e15_pull_images.py imaged, named in
              cache/images/LAB/PLATE/meta.json: mostly A02, an edge well, not an interior one
              (counted below). Same wells is not same data: the profile summarises every site
              of the well, measured on 16-bit images in five channels; each image input is one
              8-bit field of it
  Inputs      profile      that well's CellProfiler profile from cache/wells/; features as
                           e1.feature_matrix (numeric, no nulls, non-constant) plus finite,
                           chosen on these wells only, label-free; then every column that is
                           constant within every lab is dropped: these are the pixel count of
                           the camera frame (acquisition format, not cells), which the image
                           inputs do not see once every field is resized to 518 x 518 (they still
                           see scale and magnification)
              profile_with_frame_columns   the same profile with those columns kept, so the
                           change is visible
              dna, rgb, brightfield   e15's frozen DINOv2 embedding of one field of that well
  Folds       one fold vector shared by all inputs: whole batches held out, five folds,
              each lab's batches shuffled and dealt round-robin as e15.name_the_lab deals
              them (seed 0), so a lab with few batches sits in fewer test folds
  Model       StandardScaler fit on the training fold, LogisticRegression(C=0.5,
              max_iter=2000), the same for every input; convergence of every fit recorded
  Metric      balanced accuracy on the pooled out-of-fold predictions; per fold; per lab
  Control     training labels shuffled inside each training fold, five seeds: must fall to
              chance, one in eight
  Sensitivity C=1.0, e1's setting, to show the result does not hang on C
  Paired      the batches dealt into folds by seeds 0 to 19, the same rule, every input on the
  splits      same deal each time: each input's balanced accuracy, each image minus the
              profile, and on how many deals each image is at least as good; the headline
              number stays seed 0
  How sure    a 95% interval from 2,000 draws of batches with replacement inside each lab,
              on the out-of-fold predictions (no refit), for each input and for its
              difference from the profile; and, plate by plate, which plates only one names

Then e15's two geometry checks on the same wells, with the profile of the same well as the
reference, so image and profile are compared on equal terms:

  lab 2 drift  every input z-scored on the other seven labs; distance of each lab 2 batch
               mean from its first batch, over the other labs' mean within-lab spread
               (e15's rule); Spearman of each image input against the profile, and of every
               input against e9's from_baseline where batches match; again without the first
               batch, which is 0 for every input by construction
  nearest lab  for every batch of every lab, the nearest other lab by batch mean, same
               scaling; each image input against the profile, k of n; chance read from a
               permutation null: the image's answers shuffled among the batches of the same
               judged lab (so how often it picks each lab is kept), 5,000 draws

Scaling is e15's except that a column with no spread among the other labs is dropped, as
field.py does, instead of divided by 1e-9; the count dropped is reported. Both geometry
checks are repeated with z-scores clipped at 5, e9's rule.

Nothing in the output depends on the clock, so two runs write the same file.

Usage:  python analysis/e17_same_labs_every_input.py
Needs:  results/e15-embeddings-{dna,rgb,brightfield}.parquet (e15_image_model.py),
        cache/images/ (e15_pull_images.py), cache/wells/ (e1_pull_wells.py),
        results/e9-replay.json, results/e1-redteam.json and results/e15-image-model.json
        (read only to set the earlier numbers beside the new ones)
Writes: results/e17-same-labs-every-input.json
"""
import json
import os
import re
import time
import warnings
from collections import Counter
from pathlib import Path

# one BLAS thread unless the caller sets otherwise: these fits are small, threaded BLAS on a busy machine was over
# twenty times slower per fit, and one thread keeps the order of every sum fixed, so two runs write the same file
for _v in ('OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score
from sklearn.preprocessing import StandardScaler

import e1_lab_classifier as e1

# numpy 2.0 on Apple's Accelerate BLAS raises divide-by-zero, overflow and invalid-value warnings
# from matmul on finite inputs (a product of two random normal matrices does it too); they are
# silenced here, and every fit is checked for finite coefficients and decision values instead
warnings.filterwarnings('ignore', message='(divide by zero|overflow|invalid value) encountered in matmul', category=RuntimeWarning)

IMAGES = ['dna', 'rgb', 'brightfield']
INPUTS = ['profile', 'profile_with_frame_columns'] + IMAGES
C, C_SENSITIVITY, MAX_ITER, N_FOLDS, SEED, N_SHUFFLES = 0.5, 1.0, 2000, 5, 0, 5
SPLIT_SEEDS, N_BOOT = (1, 2, 3, 4), 2000
PAIRED_SEEDS = tuple(range(20))
N_PERM = 5000
JUDGED, CLIP = 'source_2', 5.0
assert PAIRED_SEEDS[0] == SEED and set(SPLIT_SEEDS) <= set(PAIRED_SEEDS)


def lab_key(l):
    return int(str(l).split('_')[1])


def population():
    """The plates with all three embeddings, one row each, aligned across inputs."""
    emb = {n: pd.read_parquet(f'results/e15-embeddings-{n}.parquet') for n in IMAGES}
    for n, e in emb.items():
        e['plate'] = e['plate'].astype(str)
        assert not e.duplicated(['source', 'plate']).any(), f'{n}: a plate appears twice'
    keys = {n: set(zip(e.source, e.plate)) for n, e in emb.items()}
    common = keys['dna'] & keys['rgb'] & keys['brightfield']
    assert keys['brightfield'] <= keys['dna'] and keys['brightfield'] <= keys['rgb'], 'a brightfield plate has no DNA or RGB embedding'
    assert common == keys['brightfield'], 'the population is not the brightfield plates'
    m = pd.DataFrame(sorted(common), columns=['source', 'plate'])
    E, batches = {}, {}
    for n, e in emb.items():
        e = m.merge(e, on=['source', 'plate'], how='left', validate='one_to_one')
        batches[n] = e['batch'].to_numpy()
        assert (batches[n] == batches['dna']).all(), f'{n}: batch labels differ from dna'
        E[n] = e[[c for c in e.columns if c.startswith('e') and c[1:].isdigit()]].to_numpy(dtype='float64')
    assert len({tuple(v.shape) for v in E.values()}) == 1 and all(len(v) == len(m) for v in E.values())
    m['batch'] = batches['dna']
    return m, E, emb


def relative_to_e15(m, emb):
    """What cutting e15's DNA and RGB plates to the brightfield plates drops, lab by lab."""
    e15 = json.load(open('results/e15-image-model.json'))['inputs']
    full = {}
    for n in ('dna', 'rgb'):
        e = emb[n]
        assert len(e) == e15[n]['n_plates'] and e.source.nunique() == e15[n]['n_labs'], f'{n}: embedding file and e15-image-model.json disagree'
        full[n] = e.groupby('source').agg(plates=('plate', 'nunique'), batches=('batch', 'nunique'))
    assert full['dna'].equals(full['rgb']), 'e15 DNA and RGB populations differ'
    full = full['dna']
    here = m.groupby('source').agg(plates=('plate', 'nunique'), batches=('batch', 'nunique'))
    per_lab = {}
    for l in sorted(full.index, key=lab_key):
        p, b = (int(here.loc[l, 'plates']), int(here.loc[l, 'batches'])) if l in here.index else (0, 0)
        per_lab[l] = {'e15_plates': int(full.loc[l, 'plates']), 'e15_batches': int(full.loc[l, 'batches']), 'plates': p, 'batches': b,
                      'plates_dropped': int(full.loc[l, 'plates']) - p, 'batches_dropped': int(full.loc[l, 'batches']) - b}
    gone = [l for l, v in per_lab.items() if v['plates'] == 0]
    cut = [l for l, v in per_lab.items() if 0 < v['plates'] < v['e15_plates']]
    say = lambda l: f"lab {lab_key(l)} keeps {per_lab[l]['plates']} of {per_lab[l]['e15_plates']} plates and {per_lab[l]['batches']} of {per_lab[l]['e15_batches']} batches"
    return {'e15_dna_and_rgb': {'n_plates': int(full.plates.sum()), 'n_labs': int(len(full)), 'n_batches': int(full.batches.sum())},
            'n_plates_dropped': int(full.plates.sum()) - int(len(m)),
            'n_batches_dropped': int(full.batches.sum()) - int(m.groupby('source').batch.nunique().sum()),
            'labs_dropped': gone, 'labs_cut': cut, 'per_lab': per_lab,
            'note': (f"a plate is kept only if it has a brightfield image: labs {', '.join(str(lab_key(l)) for l in gone)} kept none and are dropped; "
                     + '; '.join(say(l) for l in cut) + '. The other labs keep every plate.')}


def profiles(m):
    """The well-level profile of each plate's imaged DMSO well, in the population's row order."""
    rows, metas = [], []
    for s, p, b in zip(m.source, m.plate, m.batch):
        meta = json.load(open(f'cache/images/{s}/{p}/meta.json'))
        assert (meta['source'], str(meta['plate']), meta['batch']) == (s, p, b), f'{s}/{p}: image metadata disagrees'
        w = pd.read_parquet(f'cache/wells/{s}/{p}.parquet')
        w['Metadata_Plate'] = w['Metadata_Plate'].astype(str)
        r = w[w.Metadata_Well == meta['well']]
        assert len(r) == 1, f'{s}/{p}: {len(r)} profiles for imaged well {meta["well"]}'
        # a 1536-well plate names rows AA to AF or columns past 24; the DMSO wells cached are enough to tell
        big = any(re.fullmatch(r'[A-Z]{2}\d+', x) or int(re.sub(r'\D', '', x)) > 24 for x in w.Metadata_Well)
        rows.append(r); metas.append({**meta, 'plate_format': '1536' if big else '384'})
    d = pd.concat(rows, ignore_index=True)
    assert (d.Metadata_Source.to_numpy() == m.source.to_numpy()).all() and (d.Metadata_Plate.to_numpy() == m.plate.to_numpy()).all()
    X = e1.feature_matrix(d)
    X = X.loc[:, np.isfinite(X.to_numpy()).all(axis=0)]
    return d, X, metas


def constant_within_every_lab(X, lab):
    """Columns with zero spread inside every lab on these wells: they can only say which lab, never which well."""
    V = X.to_numpy()
    flat = np.ones(V.shape[1], bool)
    for l in np.unique(lab):
        flat &= V[lab == l].max(axis=0) == V[lab == l].min(axis=0)
    return [c for c, f in zip(X.columns, flat) if f]


def imaged_wells(m, metas):
    """Which well was imaged, plate by plate, and the size of its camera frame."""
    wells = Counter(meta['well'] for meta in metas)
    by_lab = {l: dict(sorted(Counter(f"{meta['well']} on {meta['plate_format']}-well plates" for s, meta in zip(m.source, metas) if s == l).items()))
              for l in sorted(set(m.source), key=lab_key)}
    frame = np.array([np.prod(meta['channels']['DNA']['shape']) for meta in metas], dtype='float64')
    return dict(wells.most_common()), by_lab, frame


def deal_folds(lab, batch, seed=SEED):
    """e15.name_the_lab's split, once: each lab's batches shuffled, then dealt round-robin."""
    rng = np.random.default_rng(seed)
    folds = np.zeros(len(lab), int)
    for l in np.unique(lab):
        bs = np.unique(batch[lab == l]); rng.shuffle(bs)
        for i, b in enumerate(bs):
            folds[(lab == l) & (batch == b)] = i % N_FOLDS
    return folds


def cross_validate(X, y, folds, c=C, permute_seed=None):
    """Out-of-fold predictions. With permute_seed, training labels are shuffled inside each fold."""
    classes = np.unique(y)
    rng = np.random.default_rng(permute_seed)
    pred, fits = np.empty(len(y), dtype=object), []
    for k in range(N_FOLDS):
        tr, te = folds != k, folds == k
        assert set(y[tr]) == set(classes), f'fold {k}: a lab is missing from training'
        ytr = rng.permutation(y[tr]) if permute_seed is not None else y[tr]
        sc = StandardScaler().fit(X[tr])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', ConvergenceWarning)
            clf = LogisticRegression(C=c, max_iter=MAX_ITER).fit(sc.transform(X[tr]), ytr)
        fits.append({'fold': k, 'n_iter': int(clf.n_iter_.max()),
                     'converged': not any(issubclass(w.category, ConvergenceWarning) for w in caught)})
        dec = clf.decision_function(sc.transform(X[te]))
        assert np.isfinite(clf.coef_).all() and np.isfinite(clf.intercept_).all() and np.isfinite(dec).all(), f'fold {k}: a non-finite fit'
        pred[te] = clf.classes_[dec.argmax(axis=1)]
    return pred, fits


def fold_balanced_accuracy(y, pred):
    # a test fold that lacks a lab (source_11 has three batches) can still have plates named as it;
    # sklearn warns, and the score is the mean recall over the labs the fold holds
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='y_pred contains classes not in y_true')
        return float(balanced_accuracy_score(y, pred))


def spread(v):
    return {'median': round(float(np.median(v)), 4), 'min': round(float(np.min(v)), 4), 'max': round(float(np.max(v)), 4)}


def score(X, lab, deals):
    """The real fit on every deal (deals[SEED] is the headline split), the shuffled control and C=1 on the headline split."""
    y, classes, folds = lab, np.unique(lab), deals[SEED]
    t = time.time()
    runs = {s: cross_validate(X, y, deals[s]) for s in PAIRED_SEEDS}
    pred, fits = runs[SEED]
    per_fold = []
    for k in range(N_FOLDS):
        te = folds == k
        per_fold.append({'fold': k, 'n_plates': int(te.sum()), 'n_labs': int(len(np.unique(y[te]))),
                         'accuracy': round(float(accuracy_score(y[te], pred[te])), 4),
                         'balanced_accuracy': round(fold_balanced_accuracy(y[te], pred[te]), 4)})
    rec = recall_score(y, pred, labels=classes, average=None)
    shuffled = [cross_validate(X, y, folds, permute_seed=SEED + i) for i in range(N_SHUFFLES)]
    sh = [float(balanced_accuracy_score(y, p)) for p, _ in shuffled]
    p1, f1 = cross_validate(X, y, folds, c=C_SENSITIVITY)
    split_ba = {s: float(balanced_accuracy_score(y, p)) for s, (p, _) in runs.items()}
    ot = [split_ba[s] for s in SPLIT_SEEDS]
    r = {'n_plates': int(len(y)), 'n_labs': int(len(classes)), 'labs': [str(c) for c in classes],
         'n_features': int(X.shape[1]), 'chance': round(1 / len(classes), 4),
         'balanced_accuracy': round(split_ba[SEED], 4),
         'median_over_splits': round(float(np.median(list(split_ba.values()))), 4),
         'plates_named_wrongly': int((pred != y).sum()),
         'per_fold': per_fold,
         'per_lab_recall': {str(c): round(float(r), 4) for c, r in zip(classes, rec)},
         'all_fits_converged': all(f['converged'] for f in fits), 'fits': fits,
         'shuffled_labels': {'seeds': [SEED + i for i in range(N_SHUFFLES)],
                             'balanced_accuracy_each': [round(v, 4) for v in sh],
                             'mean': round(float(np.mean(sh)), 4), 'max': round(float(np.max(sh)), 4),
                             'all_fits_converged': all(f['converged'] for _, fs in shuffled for f in fs)},
         f'C_{C_SENSITIVITY:g}': {'balanced_accuracy': round(float(balanced_accuracy_score(y, p1)), 4),
                                 'all_fits_converged': all(f['converged'] for f in f1)},
         'other_splits': {'fold_seeds': list(SPLIT_SEEDS), 'balanced_accuracy_each': [round(v, 4) for v in ot],
                          'min': round(min(ot), 4), 'max': round(max(ot), 4),
                          'all_fits_converged': all(f['converged'] for s in SPLIT_SEEDS for f in runs[s][1])}}
    converged = {s: all(f['converged'] for f in fs) for s, (_, fs) in runs.items()}
    return r, pred, split_ba, converged, round(time.time() - t)


def paired_splits(split_ba, converged):
    """Every input on the same twenty deals: how far the split alone moves each, and each image against the profile on the same deal."""
    ba = {n: np.array([split_ba[n][s] for s in PAIRED_SEEDS]) for n in split_ba}
    diff = {n: ba[n] - ba['profile'] for n in IMAGES}
    at_least = {n: int((np.round(diff[n], 10) >= 0).sum()) for n in IMAGES}
    return {'deal_seeds': list(PAIRED_SEEDS),
            'rule': 'each seed deals every lab\'s batches into the five folds as the headline split does (seed 0 is the headline split); '
                    'every input is fitted on the same deal each time',
            'balanced_accuracy': {n: [round(float(v), 4) for v in ba[n]] for n in ba},
            'image_minus_profile': {n: [round(float(v), 4) for v in diff[n]] for n in IMAGES},
            'seeds_image_at_least_as_good_as_profile': {n: f'{at_least[n]} of {len(PAIRED_SEEDS)}' for n in IMAGES},
            'seeds_image_at_least_as_good_as_profile_count': at_least,
            'by_input': {n: spread(ba[n]) for n in ba},
            'image_minus_profile_by_input': {n: spread(diff[n]) for n in IMAGES},
            'all_fits_converged': {n: all(converged[n].values()) for n in converged}}


def bootstrap(preds, lab, batch, n=N_BOOT, seed=SEED):
    """Batches drawn with replacement inside each lab; the out-of-fold predictions are kept, not refitted."""
    rng = np.random.default_rng(seed)
    groups = [[np.flatnonzero((lab == l) & (batch == b)) for b in np.unique(batch[lab == l])] for l in np.unique(lab)]
    draws = {k: [] for k in preds}
    for _ in range(n):
        idx = np.concatenate([g[i] for g in groups for i in rng.integers(len(g), size=len(g))])
        for k, p in preds.items():
            draws[k].append(balanced_accuracy_score(lab[idx], p[idx]))
    return {k: np.array(v) for k, v in draws.items()}


def ci(v):
    return [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]


def scaled_on_others(E, lab, judged, clip=None):
    """z-scored on every lab but the judged one; columns with no spread there are dropped."""
    ref = lab != judged
    mu, sd = E[ref].mean(axis=0), E[ref].std(axis=0)
    ok = sd > 0
    Z = (E[:, ok] - mu[ok]) / sd[ok]
    if clip:
        np.clip(Z, -clip, clip, out=Z)
    return Z, int((~ok).sum())


def lab_drift(E, lab, batch, order, clip=None):
    """e15's drift: each batch mean's distance from the first batch, over the other labs' mean within-lab spread."""
    Z, dropped = scaled_on_others(E, lab, JUDGED, clip)
    first = Z[(lab == JUDGED) & (batch == order[0])].mean(axis=0)
    spread = np.mean([np.linalg.norm(Z[lab == l] - Z[lab == l].mean(axis=0), axis=1).mean() for l in np.unique(lab) if l != JUDGED])
    return [float(np.linalg.norm(Z[(lab == JUDGED) & (batch == b)].mean(axis=0) - first) / spread) for b in order], dropped


def nearest_other(E, lab, batch, clip=None):
    """For every batch of every lab: the nearest other lab by batch mean, scaled without the judged lab."""
    out, dropped = {}, 0
    for judged in np.unique(lab):
        Z, n = scaled_on_others(E, lab, judged, clip); dropped = max(dropped, n)
        centres = {l: Z[lab == l].mean(axis=0) for l in np.unique(lab) if l != judged}
        for b in np.unique(batch[lab == judged]):
            c = Z[(lab == judged) & (batch == b)].mean(axis=0)
            out[(str(judged), str(b))] = min(centres, key=lambda l: np.linalg.norm(c - centres[l]))
    return out, dropped


def rho(a, b):
    return round(float(spearmanr(a, b).statistic), 3)


def agree(a, b):
    keys = sorted(set(a) & set(b))
    return f'{sum(a[k] == b[k] for k in keys)} of {len(keys)}'


def agreement_null(image, profile, n=N_PERM, seed=SEED):
    """How many batches two maps agree on by luck: the image's nearest-lab answers shuffled among the batches of the
    same judged lab, so how often the image picks each lab, for each judged lab, is kept. One-sided p, add-one."""
    keys = sorted(image)
    assert keys == sorted(profile)
    rng = np.random.default_rng(seed)
    observed = sum(image[k] == profile[k] for k in keys)
    null, exact = np.zeros(n, int), 0.0
    for judged in sorted({k[0] for k in keys}, key=lab_key):
        ks = [k for k in keys if k[0] == judged]
        a, b = np.array([image[k] for k in ks]), np.array([profile[k] for k in ks])
        null += (rng.permuted(np.tile(a, (n, 1)), axis=1) == b).sum(axis=1)
        exact += sum(int((a == x).sum()) * int((b == x).sum()) for x in sorted(set(a))) / len(ks)
    return {'observed': int(observed), 'n_batches': len(keys), 'expected_mean': round(float(null.mean()), 2),
            'expected_exact': round(exact, 2), 'percentile_95': round(float(np.percentile(null, 95)), 1),
            'p_one_sided': round(float((1 + (null >= observed).sum()) / (n + 1)), 4)}


def geometry(inputs, lab, batch, replay, clip=None):
    labs = sorted(set(lab))
    # lab 2 drift, batches in e9's run order
    e9b = replay[JUDGED]['batches']
    assert {b['batch'] for b in e9b} == set(batch[lab == JUDGED]), 'lab 2 batches differ from e9'
    order = [b['batch'] for b in e9b]
    by = {n: lab_drift(E, lab, batch, order, clip) for n, E in inputs.items()}
    assert all(by[n][0][0] == 0 for n in inputs), 'the first batch is not at distance 0 from itself'
    from_baseline = [b['from_baseline'] for b in e9b]
    drift = {'lab': JUDGED, 'n_batches': len(order), 'batches': order,
             'by_input': {n: [round(v, 2) for v in by[n][0]] for n in inputs},
             'e9_from_baseline': from_baseline,
             'spearman_with_profile_same_wells': {n: rho(by[n][0], by['profile'][0]) for n in IMAGES},
             'spearman_with_e9_from_baseline': {n: rho(by[n][0], from_baseline) for n in inputs},
             'spearman_after_first_batch': {
                 'n_batches': len(order) - 1, 'left_out': order[0],
                 'why': 'every input is 0 at the first batch by construction (its distance from itself), so the first pair is left out',
                 'with_profile_same_wells': {n: rho(by[n][0][1:], by['profile'][0][1:]) for n in IMAGES},
                 'with_e9_from_baseline': {n: rho(by[n][0][1:], from_baseline[1:]) for n in inputs}},
             'columns_dropped_for_no_spread': {n: by[n][1] for n in inputs}}
    # nearest other lab, every batch of every lab
    near = {n: nearest_other(E, lab, batch, clip) for n, E in inputs.items()}
    e9 = {(l, b['batch']): b['nearest_other'] for l in labs for b in replay[l]['batches']}
    null = {n: agreement_null(near[n][0], near['profile'][0]) for n in IMAGES}
    nearest = {'n_batches': len(near['profile'][0]), 'labs_to_choose_from': len(labs) - 1,
               'chance_if_one_picked_at_random': round(1 / (len(labs) - 1), 4),
               'image_agrees_with_profile_same_wells': {n: agree(near[n][0], near['profile'][0]) for n in IMAGES},
               'image_agrees_with_profile_permutation_null': null,
               'agrees_with_e9_map': {n: agree(near[n][0], e9) for n in inputs},
               'e9_nearest_lab_outside_these_labs': sum(v not in labs for k, v in e9.items() if k in near['profile'][0]),
               'columns_dropped_for_no_spread': {n: near[n][1] for n in inputs}}
    return drift, nearest


def main():
    t = time.time()
    m, E, emb = population()
    d, X_all, metas = profiles(m)
    lab, batch = m.source.to_numpy(), m.batch.to_numpy()
    wells, wells_by_lab, frame = imaged_wells(m, metas)
    flat = constant_within_every_lab(X_all, lab)
    X = X_all.drop(columns=flat)
    inputs = {'profile': X.to_numpy(dtype='float64'), 'profile_with_frame_columns': X_all.to_numpy(dtype='float64'), **E}
    assert list(inputs) == INPUTS and all(len(v) == len(lab) for v in inputs.values())
    deals = {s: deal_folds(lab, batch, seed=s) for s in PAIRED_SEEDS}
    folds = deals[SEED]
    print(f'{len(m)} plates, {len(set(lab))} labs, {len(set(zip(lab, batch)))} batches; profile {X.shape[1]} features '
          f'({len(flat)} constant within every lab dropped of {X_all.shape[1]}), images {E["dna"].shape[1]} dimensions ({round(time.time() - t)} s to load)', flush=True)

    # the dropped columns alone, on the same deals, to show what they carry; and the frame-sized columns the rule keeps
    alone = lambda cols: [float(balanced_accuracy_score(lab, cross_validate(X_all[cols].to_numpy(dtype='float64'), lab, deals[s])[0])) for s in PAIRED_SEEDS]
    fa = alone(flat)
    per_lab_value = {l: sorted({float(v) for c in flat for v in X_all.loc[lab == l, c]}) for l in sorted(set(lab), key=lab_key)}
    per_lab_frame = {l: sorted({float(v) for v in frame[lab == l]}) for l in per_lab_value}
    assert all(len(v) == 1 for v in per_lab_value.values()) and all(len(v) == 1 for v in per_lab_frame.values()), 'a lab with two frame sizes'
    gap = {l: per_lab_frame[l][0] - per_lab_value[l][0] for l in per_lab_value}
    assert all(abs(g) <= 1e-3 * per_lab_frame[l][0] for l, g in gap.items()), 'a column constant within every lab is not the camera frame\'s pixel count'
    same = [l for l, g in gap.items() if g == 0]
    kept_area = [c for c in X.columns if 'TotalArea' in c]
    ka = alone(kept_area) if kept_area else None
    fmt = Counter((meta['well'], meta['plate_format'], s) for s, meta in zip(m.source, metas))
    c04_big = sum(v for (w, f, s), v in fmt.items() if w == 'C04' and f == '1536')
    c04_small = {s: v for (w, f, s), v in sorted(fmt.items(), key=lambda kv: lab_key(kv[0][2])) if w == 'C04' and f == '384'}
    assert {s for (w, f, s) in fmt if f == '1536'} == {'source_1'} and wells.get('A02', 0) + wells.get('A23', 0) + wells.get('C04', 0) == len(m), \
        'imaged wells are not A02, A23 or C04, or a 1536-well plate outside lab 1'

    out = {'question': 'which input names the lab best, on the same labs, plates and wells, with one split and one chance level',
           'settings': {'population': 'plates with all three e15 image embeddings (dna, rgb, brightfield)',
                        'unit': (f"one DMSO well per plate, the well e15_pull_images.py imaged (cache/images/LAB/PLATE/meta.json): the first DMSO well "
                                 f"in well order, an interior one if the plate has one; JUMP's 384-well compound plates mostly hold DMSO only in "
                                 f"columns 02 and 23, so it is mostly A02, an edge well, not an interior one. A02 on {wells.get('A02', 0):,} plates and "
                                 f"A23 on {wells.get('A23', 0)} (edge wells); C04 on {wells.get('C04', 0)}: {c04_big} on lab 1's 1536-well plates, where C04 "
                                 f"is the third row, and {sum(c04_small.values())} on 384-well plates in labs "
                                 + ', '.join(f"{lab_key(l)} ({v})" for l, v in c04_small.items())
                                 + ", where it is interior. Same wells is not same data: the profile is JUMP's well-level CellProfiler profile, measured "
                                   "on the 16-bit originals in five fluorescence channels and summarised over every site of the well; each image input "
                                   "is one field of the well (its first site), saved as an 8-bit PNG 512 pixels on the long side and resized to "
                                   "518 x 518 for the model"),
                        'imaged_well_counts': wells,
                        'imaged_well_counts_by_lab': wells_by_lab,
                        'profile_features': 'e1.feature_matrix (numeric, no nulls, non-constant) and finite, chosen on these wells; '
                                            'then the columns constant within every lab dropped (profile_features_dropped)',
                        'profile_features_dropped': {
                            'rule': 'zero spread inside every lab on these wells (acquisition format, not cells): such a column can only say which lab',
                            'count': len(flat), 'names': flat,
                            'of_features': int(X_all.shape[1]),
                            'value_per_lab': {l: v[0] if len(v) == 1 else v for l, v in per_lab_value.items()},
                            'camera_frame_pixels_per_lab': {l: v[0] for l, v in per_lab_frame.items()},
                            'why': (f'each is the area of the image CellProfiler measured, in pixels: the camera frame (height x width of the original '
                                    f'image) in {len(same)} of {len(gap)} labs'
                                    + ''.join(f', and {int(g)} pixels short of it in lab {lab_key(l)}' for l, g in gap.items() if g != 0)
                                    + '; the image inputs do not see the pixel count once every field is resized to 518 x 518, though they still see scale and magnification'),
                            'balanced_accuracy_alone': {'seed_0': round(fa[0], 4), **spread(fa), 'over': f'deal seeds {PAIRED_SEEDS[0]} to {PAIRED_SEEDS[-1]}'},
                            'kept_as': 'inputs.profile_with_frame_columns'},
                        **({'frame_sized_columns_kept': {
                            'names': kept_area, 'count': len(kept_area),
                            'why': 'TotalArea columns that vary inside labs (the background area: the frame minus what the cells cover), so the rule keeps them; '
                                   'they still carry the frame size',
                            'balanced_accuracy_alone': {'seed_0': round(ka[0], 4), **spread(ka), 'over': f'deal seeds {PAIRED_SEEDS[0]} to {PAIRED_SEEDS[-1]}'}}}
                           if kept_area else {}),
                        'folds': f'one fold vector for every input: whole batches held out, {N_FOLDS} folds, each lab\'s batches '
                                 f'shuffled (numpy default_rng seed {SEED}) and dealt round-robin, as e15.name_the_lab',
                        'model': f'StandardScaler fit on the training fold; LogisticRegression(C={C}, max_iter={MAX_ITER}), lbfgs, multinomial',
                        'metric': 'balanced accuracy (mean recall over labs) on pooled out-of-fold predictions',
                        'negative_control': f'training labels shuffled inside each training fold, seeds {SEED} to {SEED + N_SHUFFLES - 1}',
                        'sensitivity': f'C={C_SENSITIVITY:g}, e1\'s setting',
                        'geometry_scaling': 'z-scored on every lab but the judged one (e15); a column with no spread there is dropped (field.py); '
                                            'no clipping, and again clipped at 5 (e9)',
                        'blas_threads': {v: os.environ[v] for v in ('OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')},
                        'jump_metadata_commit': Path('metadata/COMMIT').read_text().strip().split()[0]},
           'population': {'n_plates': int(len(m)), 'n_labs': int(len(set(lab))), 'labs': sorted(set(lab)),
                          'chance': round(1 / len(set(lab)), 4), 'n_batches': int(len(set(zip(lab, batch)))),
                          'plates_per_lab': {k: int(v) for k, v in m.groupby('source').plate.nunique().items()},
                          'batches_per_lab': {k: int(v) for k, v in m.groupby('source').batch.nunique().items()},
                          'relative_to_e15': relative_to_e15(m, emb),
                          'test_fold': [{'fold': k, 'n_plates': int((folds == k).sum()), 'n_batches': int(len(set(zip(lab[folds == k], batch[folds == k])))),
                                         'labs': sorted(set(lab[folds == k]))} for k in range(N_FOLDS)]},
           'inputs': {}}
    preds, split_ba, converged = {}, {}, {}
    for n in INPUTS:
        r, preds[n], split_ba[n], converged[n], secs = score(inputs[n], lab, deals)
        out['inputs'][n] = r
        print(f"{n:27} balanced accuracy {r['balanced_accuracy']:.4f} (median over {len(PAIRED_SEEDS)} deals {r['median_over_splits']:.4f}, chance {r['chance']:.3f}), "
              f"shuffled mean {r['shuffled_labels']['mean']:.4f} max {r['shuffled_labels']['max']:.4f}, C=1 {r['C_1']['balanced_accuracy']:.4f}, "
              f"converged {r['all_fits_converged']}, {secs} s", flush=True)
    out['paired_splits'] = paired_splits(split_ba, converged)
    print('paired splits:', json.dumps(out['paired_splits']['by_input']), out['paired_splits']['seeds_image_at_least_as_good_as_profile'], flush=True)

    # how sure: batches resampled inside each lab, and plate by plate against the profile
    boot = bootstrap(preds, lab, batch)
    for n in INPUTS:
        out['inputs'][n]['batch_bootstrap_95'] = ci(boot[n])
    right = {n: preds[n] == lab for n in INPUTS}
    out['compared_with_profile'] = {
        n: {'difference_in_balanced_accuracy': round(float(balanced_accuracy_score(lab, preds[n]) - balanced_accuracy_score(lab, preds['profile'])), 4),
            'difference_batch_bootstrap_95': ci(boot[n] - boot['profile']),
            'share_of_draws_above_profile': round(float(np.mean(boot[n] > boot['profile'])), 3),
            'plates_both_right': int((right[n] & right['profile']).sum()),
            'plates_only_this_right': int((right[n] & ~right['profile']).sum()),
            'plates_only_profile_right': int((~right[n] & right['profile']).sum()),
            'plates_both_wrong': int((~right[n] & ~right['profile']).sum())} for n in IMAGES}
    out['settings']['bootstrap'] = f'{N_BOOT} draws, seed {SEED}: batches with replacement inside each lab, out-of-fold predictions kept; 2.5th and 97.5th percentiles'
    out['settings']['other_splits'] = f'the real fit again with the batches dealt by seeds {", ".join(map(str, SPLIT_SEEDS))} (read from paired_splits)'
    out['settings']['paired_splits'] = (f'the batches dealt by seeds {PAIRED_SEEDS[0]} to {PAIRED_SEEDS[-1]}, the same rule as the headline split, every input '
                                        f'on the same deal each time; inputs.<name>.balanced_accuracy stays seed {SEED}')
    print('compared with profile:', json.dumps(out['compared_with_profile']), flush=True)

    replay = json.load(open('results/e9-replay.json'))['labs']
    drift, nearest = geometry(inputs, lab, batch, replay)
    drift_c, nearest_c = geometry(inputs, lab, batch, replay, clip=CLIP)
    out['lab_2_drift'] = {**drift, 'clipped_at_5': {k: drift_c[k] for k in ('by_input', 'spearman_with_profile_same_wells', 'spearman_with_e9_from_baseline',
                                                                            'spearman_after_first_batch')}}
    exp = {n: nearest['image_agrees_with_profile_permutation_null'][n]['expected_mean'] for n in IMAGES}
    at_random = nearest['n_batches'] * nearest['chance_if_one_picked_at_random']
    nearest['chance_if_one_picked_at_random_note'] = (
        (f"understates chance: it assumes the {nearest['labs_to_choose_from']} other labs are picked evenly, but both maps favour some labs, "
         f"so they agree by luck more often than {at_random:.1f} of {nearest['n_batches']}; the permutation null expects "
         f"{min(exp.values()):.1f} to {max(exp.values()):.1f} (image_agrees_with_profile_permutation_null)")
        if min(exp.values()) > at_random else
        f"the permutation null (image_agrees_with_profile_permutation_null) expects {min(exp.values()):.1f} to {max(exp.values()):.1f} of "
        f"{nearest['n_batches']}, against {at_random:.1f} at one in {nearest['labs_to_choose_from']}; read the null")
    nearest['permutation_null'] = (f'{N_PERM} draws, seed {SEED}: the image\'s nearest-lab answers shuffled among the batches of the same judged lab, '
                                   'so how often it picks each lab is kept; agreement with the profile counted each time; one-sided p = '
                                   '(1 + draws at or above the observed) / (1 + draws); expected_exact is the mean over every shuffle, worked out')
    out['nearest_lab'] = {**nearest, 'clipped_at_5': {k: nearest_c[k] for k in ('image_agrees_with_profile_same_wells', 'image_agrees_with_profile_permutation_null',
                                                                                 'agrees_with_e9_map')}}
    print('lab 2 drift, Spearman with profile:', drift['spearman_with_profile_same_wells'], 'with e9:', drift['spearman_with_e9_from_baseline'],
          'after the first batch:', json.dumps(drift['spearman_after_first_batch']), flush=True)
    print('nearest lab, image vs profile:', nearest['image_agrees_with_profile_same_wells'], 'vs e9:', nearest['agrees_with_e9_map'], flush=True)
    print('nearest lab, permutation null:', json.dumps(nearest['image_agrees_with_profile_permutation_null']),
          'clipped:', json.dumps(nearest_c['image_agrees_with_profile_permutation_null']), flush=True)

    # the earlier numbers, read from their files, so the change of label set is visible beside them
    bho = json.load(open('results/e1-redteam.json'))['tests']['batch_held_out']
    e15 = json.load(open('results/e15-image-model.json'))['inputs']
    out['earlier_numbers_on_other_label_sets'] = {
        'profile_e1_redteam_batch_held_out': {'n_labs': bho['n_labs'], 'chance': round(bho['chance'], 4), 'balanced_accuracy': round(bho['balanced_accuracy'], 4),
                                              'unit': f"up to {json.load(open('results/e1-redteam.json'))['settings']['wells_per_plate']} untreated wells per plate"},
        **{f'{n}_e15': {'n_labs': e15[n]['n_labs'], 'chance': e15[n]['chance'], 'balanced_accuracy': e15[n]['balanced_accuracy'],
                        'unit': 'one imaged untreated well per plate'} for n in IMAGES if 'balanced_accuracy' in e15[n]}}
    import sklearn
    out['sklearn'] = sklearn.__version__
    Path('results').mkdir(exist_ok=True)
    json.dump(out, open('results/e17-same-labs-every-input.json', 'w'), indent=1)
    print(f'wrote results/e17-same-labs-every-input.json ({round(time.time() - t)} s)')


if __name__ == '__main__':
    main()
