"""e9: replay the certificate. What would each batch of a lab have been told?

Every batch of a lab is treated as an upload, in run order, and judged against the
published field. The lab joins with its first batch, which becomes its baseline.

Scale      features are z-scored on the wells of every other lab and clipped to +-5, so
           the lab being judged never sets its own scale
Unit       the field's mean within-plate spread
Baseline   the centroid of the plates in the lab's first batch
Verdict    a plate is OUTSIDE when it sits further from its lab's own baseline than from
           the nearest other lab's centre; a batch is outside when most of its plates are
Percentile the batch's drift from baseline, ranked among the drift of every batch of
           every other lab from that lab's own first batch: a growth chart
Local      mean cells per untreated well, the check the lab already runs, reported as
           inside, below or above the range of the lab's own earlier batches

The field is the dataset as published, so this is what a lab would see if it uploaded
each batch today. Only the lab's own history is restricted to the past.

With --redteam the verdicts are recomputed under a different baseline, without clipping,
without image-level features, without all-vehicle plates, and with the nearest labs removed.

Usage:  python analysis/e9_replay.py [LAB ...] [--redteam]      (default: every lab)
Needs:  cache/wells/, metadata/; results/e1-predictions.csv if present
Writes: results/e9-replay.json, and results/e9-replay-redteam.json with --redteam
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import field as fd


def drift_of_reference_labs(F):
    """Drift of every later batch of every reference lab from that lab's own first batch."""
    out = []
    for lab in F.ref_labs:
        order, _ = fd.ordered_batches(F.batch[F.lab == lab])
        base = F.cent[F.of(lab, order[0])].mean(axis=0)
        out += [float(np.median(F.distance(F.of(lab, b), base))) for b in order[1:]]
    return np.array(out)


_NAMED = None


def named_own_lab(path='results/e1-predictions.csv'):
    """Per plate, the share of wells the e1 classifier names as the plate's own lab; empty if e1 has not run."""
    global _NAMED
    if _NAMED is None:
        _NAMED = {}
        if Path(path).exists():
            p = pd.read_csv(path, dtype=str, usecols=['Metadata_Source', 'Metadata_Plate', 'predicted'])
            _NAMED = (p.predicted == p.Metadata_Source).groupby(p.Metadata_Plate).mean().to_dict()
    return _NAMED


def replay(F, lab, n_baseline=1):
    order, dates = fd.ordered_batches(F.batch[F.lab == lab])
    base_rows = np.concatenate([F.of(lab, b) for b in order[:n_baseline]])
    baseline = F.cent[base_rows].mean(axis=0)
    reference = drift_of_reference_labs(F)
    rows = []
    for k, b in enumerate(order):
        r = F.of(lab, b)
        from_base = F.distance(r, baseline)
        to_other, which = F.to_nearest_lab(r)
        outside = from_base > to_other
        labs, n = np.unique(which, return_counts=True)
        drift = float(np.median(from_base))
        rows.append({'batch': b, 'date': str(dates[b].date()) if dates[b] is not None else None, 'run': k + 1,
                     'is_baseline': k < n_baseline, 'n_plates': int(len(r)),
                     'cells_per_well': round(float(F.cells[r].mean()), 1),
                     'from_baseline': round(drift, 2),
                     'to_nearest_other': round(float(np.median(to_other)), 2),
                     'nearest_other': str(labs[n.argmax()]),
                     'plates_outside': int(outside.sum()),
                     'verdict': 'outside' if outside.mean() > 0.5 else 'in distribution',
                     'drift_percentile_in_field': round(float((reference < drift).mean() * 100)),
                     'plates': [str(p) for p in F.plates[r]]})
    named = named_own_lab()
    for r in rows:   # does the e1 classifier, which never saw the plate, still recognise the lab?
        share = [named[p] for p in r['plates'] if p in named]
        r['wells_named_own_lab'] = round(float(np.mean(share)), 4) if share else None
    cells = np.array([r['cells_per_well'] for r in rows])
    for r in rows:   # the local check, with only the past available; no verdict until two batches exist
        past = cells[:r['run'] - 1]
        r['cell_count_vs_own_history'] = (None if len(past) < 2 else
                                         'below' if r['cells_per_well'] < past.min() else
                                         'above' if r['cells_per_well'] > past.max() else 'inside')
    return {'lab': lab, 'n_batches': len(rows), 'n_plates': int(sum(r['n_plates'] for r in rows)),
            'dated': rows[0]['date'] is not None, 'reference_labs': F.ref_labs,
            'n_reference_wells': int(F.n_wells[np.isin(F.lab, F.ref_labs)].sum()),
            'n_reference_plates': int(np.isin(F.lab, F.ref_labs).sum()),
            'n_reference_batches': int(len(reference)), 'n_features': F.n_features,
            'within_plate_spread': round(F.spread, 2),
            'batches_outside': int(sum(r['verdict'] == 'outside' for r in rows)), 'batches': rows}


def verdicts(result):
    return ''.join('O' if r['verdict'] == 'outside' else '.' for r in result['batches'])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('labs', nargs='*')
    ap.add_argument('--redteam', action='store_true')
    a = ap.parse_args()
    d, X = fd.load()
    labs = a.labs or sorted(d.Metadata_Source.unique())
    print(f'{len(d):,} wells, {d.Metadata_Plate.nunique():,} plates, {X.shape[1]:,} features', flush=True)
    Path('results').mkdir(exist_ok=True)

    if not a.redteam:
        out = {'rule': 'outside when a plate is further from its own lab\'s first batch than from the nearest other lab\'s centre',
               'z_clip': fd.CLIP, 'labs': {}}
        for lab in labs:
            out['labs'][lab] = replay(fd.Field(d, X, lab), lab)
            print(f'{lab:10} {verdicts(out["labs"][lab])}', flush=True)
        json.dump(out, open('results/e9-replay.json', 'w'), indent=1)
        return

    image_level = np.array([c.startswith('Image_') for c in X.columns])
    ordinary = ~d.Metadata_AllVehicle.to_numpy()
    out = {}
    for lab in labs:
        base = replay(fd.Field(d, X, lab), lab)
        nearest = sorted({r['nearest_other'] for r in base['batches'] if r['verdict'] == 'outside'})
        variants = {'as published': base,
                    'baseline is the first two batches': replay(fd.Field(d, X, lab), lab, n_baseline=2),
                    'baseline is the first three batches': replay(fd.Field(d, X, lab), lab, n_baseline=3),
                    'no clipping': replay(fd.Field(d, X, lab, clip=None), lab),
                    'no image-level features': replay(fd.Field(d, X, lab, keep=~image_level), lab),
                    'image-level features only': replay(fd.Field(d, X, lab, keep=image_level), lab),
                    'all-vehicle plates removed': replay(fd.Field(d[ordinary].reset_index(drop=True),
                                                                  X[ordinary].reset_index(drop=True), lab), lab)}
        for other in nearest:
            variants[f'{other} removed from the field'] = replay(fd.Field(d, X, lab, drop_labs=[other]), lab)
        if len(nearest) > 1:
            variants['all of those labs removed'] = replay(fd.Field(d, X, lab, drop_labs=nearest), lab)
        out[lab] = {name: {'verdicts': verdicts(v), 'batches_outside': v['batches_outside'], 'n_features': v['n_features'],
                           'from_baseline': [r['from_baseline'] for r in v['batches']],
                           'to_nearest_other': [r['to_nearest_other'] for r in v['batches']]}
                    for name, v in variants.items()}
        for name, v in out[lab].items():
            print(f'{lab:10} {name:38} {v["verdicts"]}', flush=True)
    json.dump(out, open('results/e9-replay-redteam.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
