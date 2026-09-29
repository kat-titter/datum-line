"""e2 timeline: one lab, batch by batch: does the local check move, and does the position?

For each batch of one lab, in date order:

  cells_per_well       mean cells per untreated well: the check the lab already runs
  from_baseline        distance of the batch's plates from the centre of the lab's first
                       batch (its own baseline), in within-plate spreads
  to_nearest_other     distance to the nearest other lab's centre, same units
  named_own_lab        share of wells the e1 classifier, which never saw the plate,
                       still names as this lab

A batch whose cell count is steady while from_baseline exceeds to_nearest_other passed
the local check and sits nearer another lab than its own past.

Distances use z-scores clipped to +-5 so that a handful of extreme feature values cannot
carry the result. The batch date is read from the batch name (YYYYMMDD).

Usage:  python analysis/e2_lab_timeline.py [LAB]        (default source_2)
Needs:  cache/wells/, metadata/, results/e1-predictions.csv
Writes: results/e2-timeline-LAB.json
"""
import json
import sys

import numpy as np
import pandas as pd

import e1_lab_classifier as e1

CLIP = 5.0
COUNT = 'Nuclei_Number_Object_Number'


def main():
    lab = sys.argv[1] if len(sys.argv) > 1 else 'source_2'
    d = e1.load_wells().reset_index(drop=True)
    X = e1.feature_matrix(d)
    X = X.loc[:, np.isfinite(X.to_numpy()).all(axis=0)]
    Z = np.clip(((X - X.mean()) / X.std()).to_numpy('float32'), -CLIP, CLIP)

    plate = d.Metadata_Plate.to_numpy()
    lab_of = d.groupby('Metadata_Plate').Metadata_Source.first()
    batch_of = d.groupby('Metadata_Plate').Metadata_Batch.first()
    cent = pd.DataFrame(Z).groupby(plate).mean()
    spread = float(np.linalg.norm(Z - cent.loc[plate].to_numpy(), axis=1).mean())
    others = cent.groupby(lab_of.loc[cent.index].to_numpy()).mean().drop(lab)

    cells = (2 * pd.to_numeric(d[COUNT]) - 1).groupby(plate).mean()
    pred = pd.read_csv('results/e1-predictions.csv', dtype=str, usecols=['Metadata_Source', 'Metadata_Plate', 'predicted'])
    own_vote = (pred.predicted == pred.Metadata_Source).groupby(pred.Metadata_Plate).mean()

    mine = [p for p in cent.index if lab_of[p] == lab]
    dates = pd.to_datetime(batch_of.loc[mine].str.extract(r'^(\d{8})')[0], format='%Y%m%d', errors='coerce')
    order = dates.dropna().groupby(batch_of.loc[dates.dropna().index]).first().sort_values()
    baseline = cent.loc[batch_of.loc[mine][batch_of.loc[mine] == order.index[0]].index].mean().to_numpy()

    rows = []
    for b, day in order.items():
        plates = [p for p in mine if batch_of[p] == b]
        V = cent.loc[plates].to_numpy()
        to_other = np.linalg.norm(V[:, None, :] - others.to_numpy()[None, :, :], axis=2) / spread
        from_base = np.linalg.norm(V - baseline, axis=1) / spread
        rows.append({'batch': b, 'date': str(day.date()), 'n_plates': len(plates),
                     'cells_per_well': round(float(cells.loc[plates].mean()), 1),
                     'from_baseline': round(float(np.median(from_base)), 2),
                     'to_nearest_other': round(float(np.median(to_other.min(axis=1))), 2),
                     'nearest_other': others.index[np.bincount(to_other.argmin(axis=1)).argmax()],
                     'plates_nearer_another_lab': int((to_other.min(axis=1) < from_base).sum()),
                     'named_own_lab': round(float(own_vote.reindex(plates).mean()), 4),
                     'plates': plates})
    out = {'lab': lab, 'baseline_batch': order.index[0], 'n_wells_in_field': int(len(d)),
           'n_labs': int(lab_of.nunique()), 'n_features': int(Z.shape[1]), 'z_clip': CLIP,
           'within_plate_spread': round(spread, 2), 'batches': rows}
    json.dump(out, open(f'results/e2-timeline-{lab}.json', 'w'), indent=2)
    for r in rows:
        print(f"{r['date']}  {r['batch']:22} n={r['n_plates']:3d}  cells {r['cells_per_well']:6.1f}  "
              f"from baseline {r['from_baseline']:5.2f}  nearest other {r['to_nearest_other']:5.2f} ({r['nearest_other']})  "
              f"nearer another lab {r['plates_nearer_another_lab']:2d}  named own lab {r['named_own_lab']:.3f}")


if __name__ == '__main__':
    main()
