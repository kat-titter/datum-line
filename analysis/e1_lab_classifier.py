"""e1: can a classifier name the lab from DMSO control wells alone?

The single definition of the e1 classifier. Every other analysis that says "same split
as e1" (e7, the vote breakdown) imports from here instead of re-specifying anything.

  Wells     DMSO (JCP2022_033924) wells on every JUMP cpg0016 COMPOUND plate, all 11
            sources that have them; one row per well (the Gallery's well-level profile).
  Features  every non-Metadata column; drop any column with a null or zero variance
            (decided on the whole table, label-free); z-score fit on training folds only.
  Model     multinomial logistic regression, L2, one fixed C, no tuning.
  Split     GroupKFold by plate, 5 folds: no plate in both train and test.
  Metric    balanced accuracy (macro recall) on the pooled out-of-fold predictions,
            plus per-fold values and the per-class recall table.
  Nulls     (a) training labels permuted within each fold, test labels untouched;
            (b) the whole run repeated without the 1536-well sources (source_1, source_9).

Usage:  python analysis/e1_lab_classifier.py [--perms N]
Needs:  cache/wells/ from e1_pull_wells.py, metadata/ at the commit in metadata/COMMIT
Writes: results/e1.json, results/e1-predictions.csv
"""
import argparse, json, time, warnings
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import balanced_accuracy_score, recall_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.exceptions import ConvergenceWarning

DMSO = 'JCP2022_033924'
WELLS = Path('cache/wells')
SOURCES_1536 = ['source_1', 'source_9']
C, MAX_ITER, N_FOLDS, SEED = 1.0, 1000, 5, 0


def load_wells(sources=None):
    """DMSO wells from the cache, with batch, plate type and an all-vehicle flag attached."""
    files = sorted(WELLS.glob('*/*.parquet'))
    if sources is not None:
        files = [f for f in files if f.parent.name in set(sources)]
    d = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    d['Metadata_Plate'] = d['Metadata_Plate'].astype(str)
    plates = pd.read_csv('metadata/plate.csv.gz', dtype=str)
    d = d.merge(plates, on=['Metadata_Source', 'Metadata_Plate'], how='left')
    w = pd.read_csv('metadata/well.csv.gz', dtype=str)
    frac = (w.Metadata_JCP2022 == DMSO).groupby([w.Metadata_Source, w.Metadata_Plate]).mean()
    d['Metadata_AllVehicle'] = [frac.get((s, p), 0) == 1.0 for s, p in zip(d.Metadata_Source, d.Metadata_Plate)]
    return d


def feature_matrix(d):
    """All non-Metadata columns, minus any with a null or zero variance. Label-free."""
    feats = [c for c in d.columns if not c.startswith('Metadata_')]
    X = d[feats].apply(pd.to_numeric, errors='coerce').astype('float32')
    X = X.loc[:, X.notna().all() & (X.std() > 0)]
    return X


def model():
    return make_pipeline(StandardScaler(),
                         LogisticRegression(C=C, penalty='l2', solver='lbfgs', max_iter=MAX_ITER))


def folds(groups):
    return list(GroupKFold(n_splits=N_FOLDS).split(np.zeros(len(groups)), groups=groups))


def cross_validate(X, y, groups, permute_seed=None, keep_proba=False):
    """Out-of-fold predictions. With permute_seed, training labels are shuffled within each fold."""
    classes = np.unique(y)
    pred = np.empty(len(y), dtype=object); fold = np.zeros(len(y), int)
    proba = np.zeros((len(y), len(classes)), 'float32') if keep_proba else None
    per_fold, n_iter = [], []
    rng = np.random.default_rng(permute_seed)
    for k, (tr, te) in enumerate(folds(groups)):
        ytr = rng.permutation(y[tr]) if permute_seed is not None else y[tr]
        m = model()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', ConvergenceWarning)
            m.fit(X[tr], ytr)
        lr = m[-1]
        n_iter.append({'fold': k, 'n_iter': int(lr.n_iter_.max()),
                       'converged': not any(issubclass(c.category, ConvergenceWarning) for c in caught)})
        assert list(lr.classes_) == list(classes), 'a class is missing from a training fold'
        pred[te] = m.predict(X[te]); fold[te] = k
        if keep_proba:
            proba[te] = m.predict_proba(X[te])
        per_fold.append(balanced_accuracy_score(y[te], pred[te]))
    return {'pred': pred, 'fold': fold, 'proba': proba, 'classes': classes,
            'per_fold': per_fold, 'fits': n_iter}


def summarise(y, cv):
    classes = cv['classes']
    rec = recall_score(y, cv['pred'], labels=classes, average=None)
    return {'balanced_accuracy': float(balanced_accuracy_score(y, cv['pred'])),
            'balanced_accuracy_per_fold': [float(v) for v in cv['per_fold']],
            'chance': 1 / len(classes),
            'per_class_recall': {c: float(r) for c, r in zip(classes, rec)},
            'predicted_share': {c: float(np.mean(cv['pred'] == c)) for c in classes},
            'true_share': {c: float(np.mean(y == c)) for c in classes},
            'confusion_matrix': {'labels': list(classes),
                                 'rows_true_cols_pred': confusion_matrix(y, cv['pred'], labels=classes).tolist()},
            'fits': cv['fits']}


def run(d, perms, keep_proba=False):
    X = feature_matrix(d)
    y = d['Metadata_Source'].to_numpy(); g = d['Metadata_Plate'].to_numpy()
    t = time.time(); cv = cross_validate(X.to_numpy(), y, g, keep_proba=keep_proba)
    out = {'n_wells': int(len(d)), 'n_plates': int(pd.unique(g).size), 'n_labs': int(pd.unique(y).size),
           'n_features': int(X.shape[1]), 'wells_per_lab': d['Metadata_Source'].value_counts().sort_index().to_dict(),
           'plates_per_lab': d.groupby('Metadata_Source')['Metadata_Plate'].nunique().to_dict(),
           **summarise(y, cv), 'seconds': round(time.time() - t)}
    nulls = [cross_validate(X.to_numpy(), y, g, permute_seed=SEED + i) for i in range(perms)]
    out['permuted_null'] = {'n_permutations': perms,
                            'balanced_accuracy': [float(balanced_accuracy_score(y, n['pred'])) for n in nulls]}
    return out, cv, X


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--perms', type=int, default=3); a = ap.parse_args()
    d = load_wells()
    full, cv, X = run(d, a.perms, keep_proba=True)
    no1536, _, _ = run(d[~d.Metadata_Source.isin(SOURCES_1536)].reset_index(drop=True), a.perms)
    settings = {'wells': 'DMSO (JCP2022_033924) wells on every COMPOUND plate in metadata/plate.csv.gz',
                'features': 'all non-Metadata columns; drop any with a null or zero variance; '
                            'z-score fit on training folds only',
                'model': f'LogisticRegression(penalty=l2, C={C}, solver=lbfgs, multinomial, max_iter={MAX_ITER}), '
                         'no tuning',
                'split': f'GroupKFold(n_splits={N_FOLDS}) by Metadata_Plate',
                'metric': 'balanced accuracy (macro recall) on pooled out-of-fold predictions',
                'null_permuted': 'training labels permuted within each fold; test labels untouched',
                'null_no_1536': f'same run without {SOURCES_1536}',
                'jump_metadata_commit': Path('metadata/COMMIT').read_text().strip()}
    import sklearn
    Path('results').mkdir(exist_ok=True)
    json.dump({'settings': settings, 'sklearn': sklearn.__version__, 'all_sources': full,
               'without_1536_well_sources': no1536},
              open('results/e1.json', 'w'), indent=2)
    p = d[['Metadata_Source', 'Metadata_Batch', 'Metadata_Plate', 'Metadata_Well', 'Metadata_AllVehicle']].copy()
    p['fold'] = cv['fold']; p['predicted'] = cv['pred']
    for i, c in enumerate(cv['classes']):
        p[f'p_{c}'] = np.round(cv['proba'][:, i], 5)
    p.to_csv('results/e1-predictions.csv', index=False)
    print(json.dumps({k: full[k] for k in ('n_wells', 'n_labs', 'n_features', 'balanced_accuracy', 'chance')}, indent=2))


if __name__ == '__main__':
    main()
