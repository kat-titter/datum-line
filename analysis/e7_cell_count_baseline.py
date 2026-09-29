"""e7: can a cell count alone name the lab?

The baseline the benchmarks paper insists on, applied to our own claim. Wells, split,
model and metric all come from e1_lab_classifier; the only change is the feature set.

  A  cell count only            1 feature   (Cells_Number_Object_Number)
  B  count + a few size/shape   <=10        (area, eccentricity, DNA mean intensity)
  C  all features               e1's full set -> the e1 number

The well-level profiles carry no explicit count column. Cells_Number_Object_Number is the
mean object index per image, (n + 1) / 2 for n cells, so it is monotonic in cell count
and a linear model sees the same information.

Report balanced accuracy for each, with the permuted-label null, held out by plate.
If A already scores high, say so on the slide: the honest version of the claim is
whatever survives the baseline. If A is near chance and C is high, the claim is that
shape, not density, carries the lab.

Usage:  python analysis/e7_cell_count_baseline.py [--perms N]
Writes: results/e7-cell-count-baseline.json
"""
import argparse, json, re
from sklearn.metrics import balanced_accuracy_score
import e1_lab_classifier as e1

COUNT = 'Cells_Number_Object_Number'
BASIC = r'^(Cells|Nuclei)_(AreaShape_Area|AreaShape_Eccentricity|Intensity_MeanIntensity_DNA)$'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--perms', type=int, default=3); a = ap.parse_args()
    d = e1.load_wells()
    X = e1.feature_matrix(d)
    assert COUNT in X.columns, f'{COUNT} dropped by the e1 feature filter'
    basic = [COUNT] + [c for c in X.columns if re.search(BASIC, c)][:9]
    sets = {'A_count_only': [COUNT], 'B_count_plus_basic': basic, 'C_all_features': list(X.columns)}
    y = d['Metadata_Source'].to_numpy(); g = d['Metadata_Plate'].to_numpy()
    out = {'n_wells': int(len(d)), 'n_labs': int(len(set(y))), 'chance': 1 / len(set(y)),
           'split': 'e1: GroupKFold by plate, 5 folds; model and features per e1_lab_classifier',
           'features': {k: (v if len(v) <= 10 else f'{len(v)} columns') for k, v in sets.items()},
           'balanced_accuracy': {}, 'permuted_null': {}}
    full = json.load(open('results/e1.json'))['all_sources']  # C is e1 itself: read, do not refit
    assert full['n_wells'] == len(d) and full['n_features'] == X.shape[1], 'cache changed since e1 ran'
    out['balanced_accuracy']['C_all_features'] = full['balanced_accuracy']
    out['permuted_null']['C_all_features'] = full['permuted_null']['balanced_accuracy']
    for k, cols in sets.items():
        if k == 'C_all_features':
            continue
        Xk = X[cols].to_numpy()
        out['balanced_accuracy'][k] = float(balanced_accuracy_score(y, e1.cross_validate(Xk, y, g)['pred']))
        out['permuted_null'][k] = [float(balanced_accuracy_score(y, e1.cross_validate(Xk, y, g, permute_seed=e1.SEED + i)['pred']))
                                   for i in range(a.perms)]
    json.dump(out, open('results/e7-cell-count-baseline.json', 'w'), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
