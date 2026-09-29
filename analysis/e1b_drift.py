"""e1b: how far apart do two runs of the same cells sit, as a function of time between them?

For one lab, every plate is reduced to the centroid of its DMSO wells (features z-scored
on that lab's wells) and every pair of plates is binned by the days between their
batches. Distances are in units of the mean within-plate spread. The batch date is read
from the batch name where it starts with YYYYMMDD; plates without a date are left out.

Same-batch pairs are the baseline. If later bins rise and then level off, a lab's
baseline goes stale and then stays inside an envelope.

Usage:  python analysis/e1b_drift.py [LAB]          (default source_2)
Needs:  cache/wells/, metadata/
Writes: results/e1b-drift-LAB.json
"""
import json
import re
import sys
from itertools import combinations

import numpy as np
import pandas as pd

import e1_lab_classifier as e1

BINS = [(0, 0, 'same batch'), (1, 14, '1 to 14 days'), (15, 42, '2 to 6 weeks'),
        (43, 91, '6 to 13 weeks'), (92, 10_000, 'over 13 weeks')]


def main():
    lab = sys.argv[1] if len(sys.argv) > 1 else 'source_2'
    d = e1.load_wells(sources=[lab]).reset_index(drop=True)
    X = e1.feature_matrix(d)
    X = X.loc[:, np.isfinite(X.to_numpy()).all(axis=0)]
    Z = ((X - X.mean()) / X.std()).to_numpy('float32')
    plate = d.Metadata_Plate.to_numpy()
    cent = pd.DataFrame(Z).groupby(plate).mean()
    spread = float(np.linalg.norm(Z - cent.loc[plate].to_numpy(), axis=1).mean())

    batch = d.groupby('Metadata_Plate').Metadata_Batch.first()
    date = pd.to_datetime(batch.str.extract(r'^(\d{8})')[0], format='%Y%m%d', errors='coerce').dropna()
    cent = cent.loc[cent.index.intersection(date.index)]
    rows = []
    for p, q in combinations(cent.index, 2):
        days = abs((date[p] - date[q]).days)
        if days == 0 and batch[p] != batch[q]:
            continue
        rows.append((days, float(np.linalg.norm(cent.loc[p].to_numpy() - cent.loc[q].to_numpy()) / spread)))
    t = pd.DataFrame(rows, columns=['days', 'distance'])
    out = {'lab': lab, 'n_plates': int(len(cent)), 'n_batches': int(batch.loc[cent.index].nunique()),
           'first_batch': str(date.min().date()), 'last_batch': str(date.max().date()),
           'n_features': int(Z.shape[1]), 'within_plate_spread': round(spread, 2), 'bins': []}
    for lo, hi, name in BINS:
        x = t[(t.days >= lo) & (t.days <= hi)].distance
        if len(x):
            out['bins'].append({'gap': name, 'n_pairs': int(len(x)), 'median': round(float(x.median()), 2),
                                'mean': round(float(x.mean()), 2),
                                'iqr': [round(float(x.quantile(.25)), 2), round(float(x.quantile(.75)), 2)]})
    base = out['bins'][0]['median']
    for b in out['bins']:
        b['ratio_to_same_batch'] = round(b['median'] / base, 2)
    json.dump(out, open(f'results/e1b-drift-{lab}.json', 'w'), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
