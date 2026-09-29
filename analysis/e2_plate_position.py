"""e2: where does one plate sit, relative to its own lab and to every other lab?

For the wells scored in e1 (results/e1-predictions.csv), features are z-scored on all
wells, each plate is reduced to the centroid of its DMSO wells, and distances are
expressed in units of the mean within-plate spread (mean distance of a well from its
own plate's centroid). For the target plate this reports:

  - distance to its own lab's centre, and the percentile of that among the lab's plates
  - distance to every other lab's centre
  - how many plates anywhere sit closer to another lab's centre than to their own

It also writes a two-dimensional PCA of a fixed subsample of wells for the figure, with
the variance each axis explains. PCA is used because it is deterministic; the distances
above are computed in the full feature space, not in the projection.

Usage:  python analysis/e2_plate_position.py [PLATE] [--wells-per-plate 8]
Needs:  cache/wells/, metadata/, results/e1-predictions.csv
Writes: results/e2-plate-position-PLATE.json, results/e2-embedding.csv,
        results/e2-displaced-plates.csv
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

import e1_lab_classifier as e1

SEED = 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('plate', nargs='?', default='1053600681')
    ap.add_argument('--wells-per-plate', type=int, default=8)
    a = ap.parse_args()

    scored = pd.read_csv('results/e1-predictions.csv', dtype=str, usecols=['Metadata_Source', 'Metadata_Plate'])
    d = e1.load_wells(sources=sorted(scored.Metadata_Source.unique()))
    d = d[d.Metadata_Plate.isin(set(scored.Metadata_Plate))].reset_index(drop=True)
    X = e1.feature_matrix(d)
    X = X.loc[:, np.isfinite(X.to_numpy()).all(axis=0)]
    Z = ((X - X.mean()) / X.std()).to_numpy('float32')

    plate = d.Metadata_Plate.to_numpy()
    lab_of = d.groupby('Metadata_Plate').Metadata_Source.first()
    cent = pd.DataFrame(Z).groupby(plate).mean()
    spread = float(np.linalg.norm(Z - cent.loc[plate].to_numpy(), axis=1).mean())
    lab_centre = cent.groupby(lab_of.loc[cent.index].to_numpy()).mean()

    dist = pd.DataFrame(
        np.linalg.norm(cent.to_numpy()[:, None, :] - lab_centre.to_numpy()[None, :, :], axis=2) / spread,
        index=cent.index, columns=lab_centre.index)
    own = pd.Series([dist.loc[p, lab_of[p]] for p in dist.index], index=dist.index)
    nearest_other = pd.Series([dist.loc[p].drop(lab_of[p]).min() for p in dist.index], index=dist.index)
    same_lab = own[lab_of.loc[own.index] == lab_of[a.plate]]

    out = {'plate': a.plate, 'lab': lab_of[a.plate], 'n_wells': int(len(d)), 'n_plates': int(len(cent)),
           'n_labs': int(len(lab_centre)), 'n_features': int(Z.shape[1]),
           'unit': 'mean distance of a well from its own plate centroid', 'within_plate_spread': round(spread, 2),
           'distance_to_own_lab': round(float(own[a.plate]), 2),
           'percentile_among_own_lab_plates': round(float((same_lab < own[a.plate]).mean() * 100)),
           'own_lab_plates': int(len(same_lab)),
           'distance_to_each_lab': {k: round(float(v), 2) for k, v in dist.loc[a.plate].sort_values().items()},
           'plates_closer_to_another_lab_than_their_own': int((nearest_other < own).sum())}

    # every plate that sits nearer another lab's centre than its own, with the local check
    # (cell count) and the classifier's vote beside it
    cells = (2 * pd.to_numeric(d['Nuclei_Number_Object_Number']) - 1).groupby(plate).mean()
    count_pct = cells.groupby(lab_of.loc[cells.index].to_numpy()).rank(pct=True) * 100
    pred = pd.read_csv('results/e1-predictions.csv', dtype=str, usecols=['Metadata_Source', 'Metadata_Plate', 'predicted'])
    own_vote = (pred.predicted == pred.Metadata_Source).groupby(pred.Metadata_Plate).mean()
    displaced = pd.DataFrame({'lab': lab_of.loc[own.index], 'batch': d.groupby('Metadata_Plate').Metadata_Batch.first().loc[own.index],
                              'distance_to_own_lab': own.round(2), 'nearest_other_lab': dist.apply(lambda r: r.drop(lab_of[r.name]).idxmin(), axis=1),
                              'distance_to_nearest_other': nearest_other.round(2), 'cells_per_well': cells.loc[own.index].round(1),
                              'cell_count_percentile_in_lab': count_pct.loc[own.index].round(0),
                              'share_of_wells_named_own_lab': own_vote.reindex(own.index).round(3)})
    displaced = displaced[displaced.distance_to_nearest_other < displaced.distance_to_own_lab]
    displaced.sort_values('distance_to_own_lab', ascending=False).to_csv('results/e2-displaced-plates.csv', index_label='plate')
    out['displaced_plates'] = {'n': int(len(displaced)), 'by_lab_and_nearest': {f'{a_} nearer {b_}': int(n) for (a_, b_), n in
                               displaced.groupby(['lab', 'nearest_other_lab']).size().items()},
                               'with_cell_count_between_25th_and_75th_percentile': int(displaced.cell_count_percentile_in_lab.between(25, 75).sum())}

    rng = np.random.default_rng(SEED)
    keep = np.sort(np.concatenate([rng.permutation(g.index.to_numpy())[:a.wells_per_plate]
                                   for _, g in d.groupby('Metadata_Plate', sort=False)]))
    keep = np.union1d(keep, np.flatnonzero(plate == a.plate))      # every well of the target plate
    pca = PCA(n_components=2, random_state=SEED).fit(Z[keep])
    xy = pca.transform(Z[keep])
    out['pca'] = {'wells': int(len(keep)), 'wells_per_plate': a.wells_per_plate,
                  'variance_explained': [round(float(v), 4) for v in pca.explained_variance_ratio_]}
    pd.DataFrame({'lab': d.Metadata_Source.to_numpy()[keep], 'plate': plate[keep],
                  'target': plate[keep] == a.plate, 'pc1': xy[:, 0].round(3), 'pc2': xy[:, 1].round(3)}
                 ).to_csv('results/e2-embedding.csv', index=False)
    json.dump(out, open(f'results/e2-plate-position-{a.plate}.json', 'w'), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
