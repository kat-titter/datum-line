"""e13: denser is tighter. How much does a baseline wobble, and what shrinks it?

A baseline is a mean, so it has an uncertainty. Two are measured, in units of the field's
within-plate spread, as the distance between two independent estimates of the same thing:

  a lab's own baseline   two disjoint sets of k plates from one batch of one lab,
                         for k = 1, 2, 4, 8, 16: what more of your own plates buys
  the field's reference  two disjoint sets of m labs (each lab reduced to its centre),
                         for m = 1 to 5: what each lab that joins buys everyone

Every draw is random with a fixed seed; the mean and the 10th to 90th percentile are kept.
Features are z-scored on every well and clipped, since no lab is being judged here.

Usage:  python analysis/e13_baseline_density.py [--draws 400]
Needs:  cache/wells/, metadata/
Writes: results/e13-baseline-density.json
"""
import argparse
import json

import numpy as np

import field as fd

SEED = 0


def spread_of(d):
    return {'mean': round(float(np.mean(d)), 3), 'p10': round(float(np.percentile(d, 10)), 3),
            'p90': round(float(np.percentile(d, 90)), 3), 'draws': int(len(d))}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--draws', type=int, default=400)
    a = ap.parse_args()
    d, X = fd.load()
    F = fd.Field(d, X, judged_lab=None)
    rng = np.random.default_rng(SEED)
    labs = F.ref_labs

    batches = [(l, b) for l in labs for b in np.unique(F.batch[F.lab == l])]
    own = {}
    for k in (1, 2, 4, 8, 16):
        big = [F.of(l, b) for l, b in batches if len(F.of(l, b)) >= 2 * k]
        dist = []
        for _ in range(a.draws):
            rows = rng.permutation(big[rng.integers(len(big))])
            dist.append(np.linalg.norm(F.cent[rows[:k]].mean(axis=0) - F.cent[rows[k:2 * k]].mean(axis=0)) / F.spread)
        own[k] = {**spread_of(dist), 'batches_large_enough': len(big)}

    centre = np.stack([F.lab_centre[l] for l in labs])
    reference = {}
    for m in range(1, len(labs) // 2 + 1):
        dist = []
        for _ in range(a.draws):
            pick = rng.permutation(len(labs))
            dist.append(np.linalg.norm(centre[pick[:m]].mean(axis=0) - centre[pick[m:2 * m]].mean(axis=0)) / F.spread)
        reference[m] = spread_of(dist)
    # how much does the whole reference move if any one lab is taken away?
    whole = centre.mean(axis=0)
    leave_one_out = [float(np.linalg.norm(np.delete(centre, i, axis=0).mean(axis=0) - whole) / F.spread) for i in range(len(labs))]

    plates_per_batch = [int(len(F.of(l, b))) for l, b in batches]
    out = {'unit': 'mean distance of a well from its own plate centroid', 'within_plate_spread': round(F.spread, 2),
           'n_wells': int(F.n_wells.sum()), 'n_plates': int(len(F.plates)), 'n_labs': len(labs), 'n_batches': len(batches),
           'n_features': F.n_features, 'plates_per_batch_median': int(np.median(plates_per_batch)),
           'own_baseline_by_plates': own, 'field_reference_by_labs': reference,
           'reference_moves_when_one_lab_leaves': {'mean': round(float(np.mean(leave_one_out)), 3), 'max': round(float(np.max(leave_one_out)), 3)}}
    json.dump(out, open('results/e13-baseline-density.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
