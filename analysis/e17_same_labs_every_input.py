"""e17: which input names the lab best, when every input sees the same labs, plates and wells?

The deck's lab-naming numbers come from different label sets: the six-dye profile from
e1-redteam's batch_held_out (10 labs, chance one in ten), DNA and RGB images from e15
(11 labs, one in eleven), brightfield from e15 (8 labs, one in eight). A higher number on
fewer labs is not a better input. Here every input is scored on one population and one split,
so every row has the same chance.

  Population  the plates that have all three e15 image embeddings; brightfield exists in
              8 labs, so these are its 1,338 plates, and DNA and RGB are cut to the same plates
  Unit        the one imaged untreated (DMSO) well per plate, named in
              cache/images/LAB/PLATE/meta.json
  Inputs      profile      that well's CellProfiler profile from cache/wells/; features as
                           e1.feature_matrix (numeric, no nulls, non-constant) plus finite,
                           chosen on these wells only, label-free
              dna, rgb, brightfield   e15's frozen DINOv2 embedding of one field of that well
  Folds       one fold vector shared by all four inputs: whole batches held out, five folds,
              each lab's batches shuffled and dealt round-robin as e15.name_the_lab deals
              them (seed 0), so a lab with few batches sits in fewer test folds
  Model       StandardScaler fit on the training fold, LogisticRegression(C=0.5,
              max_iter=2000), the same for every input; convergence of every fit recorded
  Metric      balanced accuracy on the pooled out-of-fold predictions; per fold; per lab
  Control     training labels shuffled inside each training fold, five seeds: must fall to
              chance, one in eight
  Sensitivity C=1.0, e1's setting, to show the result does not hang on C; and the batches
              dealt into folds by four other seeds, to show how much the split alone moves it
  How sure    a 95% interval from 2,000 draws of batches with replacement inside each lab,
              on the out-of-fold predictions (no refit), for each input and for its
              difference from the profile; and, plate by plate, which plates only one names

Then e15's two geometry checks on the same wells, with the profile of the same well as the
reference, so image and profile are compared on equal terms:

  lab 2 drift  every input z-scored on the other seven labs; distance of each lab 2 batch
               mean from its first batch, over the other labs' mean within-lab spread
               (e15's rule); Spearman of each image input against the profile, and of every
               input against e9's from_baseline where batches match
  nearest lab  for every batch of every lab, the nearest other lab by batch mean, same
               scaling; each image input against the profile, k of n

Scaling is e15's except that a column with no spread among the other labs is dropped, as
field.py does, instead of divided by 1e-9; the count dropped is reported. Both geometry
checks are repeated with z-scores clipped at 5, e9's rule.

Usage:  python analysis/e17_same_labs_every_input.py
Needs:  results/e15-embeddings-{dna,rgb,brightfield}.parquet (e15_image_model.py),
        cache/images/ (e15_pull_images.py), cache/wells/ (e1_pull_wells.py),
        results/e9-replay.json, results/e1-redteam.json and results/e15-image-model.json
        (read only to set the earlier numbers beside the new ones)
Writes: results/e17-same-labs-every-input.json
"""
import json
import time
import warnings
from pathlib import Path

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
INPUTS = ['profile'] + IMAGES
C, C_SENSITIVITY, MAX_ITER, N_FOLDS, SEED, N_SHUFFLES = 0.5, 1.0, 2000, 5, 0, 5
SPLIT_SEEDS, N_BOOT = (1, 2, 3, 4), 2000
JUDGED, CLIP = 'source_2', 5.0


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
    return m, E


def profiles(m):
    """The well-level profile of each plate's imaged DMSO well, in the population's row order."""
    rows = []
    for s, p, b in zip(m.source, m.plate, m.batch):
        meta = json.load(open(f'cache/images/{s}/{p}/meta.json'))
        assert (meta['source'], str(meta['plate']), meta['batch']) == (s, p, b), f'{s}/{p}: image metadata disagrees'
        w = pd.read_parquet(f'cache/wells/{s}/{p}.parquet')
        w['Metadata_Plate'] = w['Metadata_Plate'].astype(str)
        r = w[w.Metadata_Well == meta['well']]
        assert len(r) == 1, f'{s}/{p}: {len(r)} profiles for imaged well {meta["well"]}'
        rows.append(r)
    d = pd.concat(rows, ignore_index=True)
    assert (d.Metadata_Source.to_numpy() == m.source.to_numpy()).all() and (d.Metadata_Plate.to_numpy() == m.plate.to_numpy()).all()
    X = e1.feature_matrix(d)
    X = X.loc[:, np.isfinite(X.to_numpy()).all(axis=0)]
    return d, X


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


def score(X, lab, batch, folds):
    y, classes = lab, np.unique(lab)
    t = time.time()
    pred, fits = cross_validate(X, y, folds)
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
    # the same fit on other deals of the batches into folds, to see how much the split alone moves it
    others = [cross_validate(X, y, deal_folds(lab, batch, seed=s)) for s in SPLIT_SEEDS]
    ot = [float(balanced_accuracy_score(y, p)) for p, _ in others]
    r = {'n_plates': int(len(y)), 'n_labs': int(len(classes)), 'labs': [str(c) for c in classes],
         'n_features': int(X.shape[1]), 'chance': round(1 / len(classes), 4),
         'balanced_accuracy': round(float(balanced_accuracy_score(y, pred)), 4),
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
                          'all_fits_converged': all(f['converged'] for _, fs in others for f in fs)},
         'seconds': round(time.time() - t)}
    return r, pred


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


def geometry(inputs, lab, batch, replay, clip=None):
    labs = sorted(set(lab))
    # lab 2 drift, batches in e9's run order
    e9b = replay[JUDGED]['batches']
    assert {b['batch'] for b in e9b} == set(batch[lab == JUDGED]), 'lab 2 batches differ from e9'
    order = [b['batch'] for b in e9b]
    by = {n: lab_drift(E, lab, batch, order, clip) for n, E in inputs.items()}
    from_baseline = [b['from_baseline'] for b in e9b]
    drift = {'lab': JUDGED, 'n_batches': len(order), 'batches': order,
             'by_input': {n: [round(v, 2) for v in by[n][0]] for n in inputs},
             'e9_from_baseline': from_baseline,
             'spearman_with_profile_same_wells': {n: rho(by[n][0], by['profile'][0]) for n in IMAGES},
             'spearman_with_e9_from_baseline': {n: rho(by[n][0], from_baseline) for n in inputs},
             'columns_dropped_for_no_spread': {n: by[n][1] for n in inputs}}
    # nearest other lab, every batch of every lab
    near = {n: nearest_other(E, lab, batch, clip) for n, E in inputs.items()}
    e9 = {(l, b['batch']): b['nearest_other'] for l in labs for b in replay[l]['batches']}
    nearest = {'n_batches': len(near['profile'][0]), 'labs_to_choose_from': len(labs) - 1,
               'chance_if_one_picked_at_random': round(1 / (len(labs) - 1), 4),
               'image_agrees_with_profile_same_wells': {n: agree(near[n][0], near['profile'][0]) for n in IMAGES},
               'agrees_with_e9_map': {n: agree(near[n][0], e9) for n in inputs},
               'e9_nearest_lab_outside_these_labs': sum(v not in labs for k, v in e9.items() if k in near['profile'][0]),
               'columns_dropped_for_no_spread': {n: near[n][1] for n in inputs}}
    return drift, nearest


def main():
    t = time.time()
    m, E = population()
    d, X = profiles(m)
    lab, batch = m.source.to_numpy(), m.batch.to_numpy()
    inputs = {'profile': X.to_numpy(dtype='float64'), **E}
    assert all(len(v) == len(lab) for v in inputs.values())
    folds = deal_folds(lab, batch)
    print(f'{len(m)} plates, {len(set(lab))} labs, {len(set(zip(lab, batch)))} batches; '
          f'profile {X.shape[1]} features, images {E["dna"].shape[1]} dimensions ({round(time.time() - t)} s to load)', flush=True)

    out = {'question': 'which input names the lab best, on the same labs, plates and wells, with one split and one chance level',
           'settings': {'population': 'plates with all three e15 image embeddings (dna, rgb, brightfield)',
                        'unit': 'the one imaged untreated (DMSO) well per plate, from cache/images/LAB/PLATE/meta.json',
                        'profile_features': 'e1.feature_matrix (numeric, no nulls, non-constant) and finite, chosen on these wells',
                        'folds': f'one fold vector for every input: whole batches held out, {N_FOLDS} folds, each lab\'s batches '
                                 f'shuffled (numpy default_rng seed {SEED}) and dealt round-robin, as e15.name_the_lab',
                        'model': f'StandardScaler fit on the training fold; LogisticRegression(C={C}, max_iter={MAX_ITER}), lbfgs, multinomial',
                        'metric': 'balanced accuracy (mean recall over labs) on pooled out-of-fold predictions',
                        'negative_control': f'training labels shuffled inside each training fold, seeds {SEED} to {SEED + N_SHUFFLES - 1}',
                        'sensitivity': f'C={C_SENSITIVITY:g}, e1\'s setting',
                        'geometry_scaling': 'z-scored on every lab but the judged one (e15); a column with no spread there is dropped (field.py); '
                                            'no clipping, and again clipped at 5 (e9)',
                        'jump_metadata_commit': Path('metadata/COMMIT').read_text().strip().split()[0]},
           'population': {'n_plates': int(len(m)), 'n_labs': int(len(set(lab))), 'labs': sorted(set(lab)),
                          'chance': round(1 / len(set(lab)), 4), 'n_batches': int(len(set(zip(lab, batch)))),
                          'plates_per_lab': {k: int(v) for k, v in m.groupby('source').plate.nunique().items()},
                          'batches_per_lab': {k: int(v) for k, v in m.groupby('source').batch.nunique().items()},
                          'test_fold': [{'fold': k, 'n_plates': int((folds == k).sum()), 'n_batches': int(len(set(zip(lab[folds == k], batch[folds == k])))),
                                         'labs': sorted(set(lab[folds == k]))} for k in range(N_FOLDS)]},
           'inputs': {}}
    preds = {}
    for n in INPUTS:
        r, preds[n] = score(inputs[n], lab, batch, folds)
        out['inputs'][n] = r
        print(f"{n:12} balanced accuracy {r['balanced_accuracy']:.4f} (chance {r['chance']:.3f}), shuffled mean {r['shuffled_labels']['mean']:.4f} "
              f"max {r['shuffled_labels']['max']:.4f}, C=1 {r['C_1']['balanced_accuracy']:.4f}, converged {r['all_fits_converged']}, {r['seconds']} s", flush=True)

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
    out['settings']['other_splits'] = f'the real fit again with the batches dealt by seeds {", ".join(map(str, SPLIT_SEEDS))}'
    print('compared with profile:', json.dumps(out['compared_with_profile']), flush=True)

    replay = json.load(open('results/e9-replay.json'))['labs']
    drift, nearest = geometry(inputs, lab, batch, replay)
    drift_c, nearest_c = geometry(inputs, lab, batch, replay, clip=CLIP)
    out['lab_2_drift'] = {**drift, 'clipped_at_5': {k: drift_c[k] for k in ('by_input', 'spearman_with_profile_same_wells', 'spearman_with_e9_from_baseline')}}
    out['nearest_lab'] = {**nearest, 'clipped_at_5': {k: nearest_c[k] for k in ('image_agrees_with_profile_same_wells', 'agrees_with_e9_map')}}
    print('lab 2 drift, Spearman with profile:', drift['spearman_with_profile_same_wells'], 'with e9:', drift['spearman_with_e9_from_baseline'], flush=True)
    print('nearest lab, image vs profile:', nearest['image_agrees_with_profile_same_wells'], 'vs e9:', nearest['agrees_with_e9_map'], flush=True)

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
    out['seconds'] = round(time.time() - t)
    Path('results').mkdir(exist_ok=True)
    json.dump(out, open('results/e17-same-labs-every-input.json', 'w'), indent=1)
    print('wrote results/e17-same-labs-every-input.json')


if __name__ == '__main__':
    main()
