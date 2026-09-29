"""e6: what moved. The interpretable side of the certificate.

For one batch of one lab, the displacement from the lab's own baseline (its first batch),
feature by feature, in units of the field's standard deviation:

    d = mean(batch plates) - mean(baseline plates)

in features z-scored on every other lab and clipped, as in e9. Nothing here is a model; it
is a difference of two means, which is why a lab can act on it. Reported:

  groups     mean signed shift and mean absolute shift for every (channel, measurement)
             group of features, for example Mito intensity or DNA texture, ranked by size
  level      share of the squared displacement carried by image-level features (acquisition:
             illumination, focus, exposure) against cell-level features (Cells, Cytoplasm,
             Nuclei). This is the honest answer to "is it the instrument or the cells?"
  features   the fifteen single features that moved most, with sign

Usage:  python analysis/e6_what_moved.py [LAB] [BATCH] [TAG]   (default: source_2, its last batch;
        TAG is added to the output file name)
Needs:  cache/wells/, metadata/
Writes: results/e6-what-moved-LAB[TAG].json
"""
import json
import re
import sys

import numpy as np
import pandas as pd

import field as fd

CHANNELS = ('DNA', 'RNA', 'ER', 'AGP', 'Mito', 'Brightfield')
MEASUREMENT = re.compile(r'^(?:Cells|Cytoplasm|Nuclei|Image)_([A-Za-z]+)_')


def channel_of(name):
    found = [c for c in CHANNELS if re.search(rf'(?:_|Orig){c}(?:_|$)', name)]
    return found[0] if len(found) == 1 else ('two channels' if found else 'shape and position')


def measurement_of(name):
    m = MEASUREMENT.match(name)
    return m.group(1) if m else 'Other'


def main():
    lab = sys.argv[1] if len(sys.argv) > 1 else 'source_2'
    d, X = fd.load()
    F = fd.Field(d, X, lab)
    order, dates = fd.ordered_batches(F.batch[F.lab == lab])
    batch = sys.argv[2] if len(sys.argv) > 2 else order[-1]
    tag = sys.argv[3] if len(sys.argv) > 3 else ''
    disp = F.cent[F.of(lab, batch)].mean(axis=0) - F.cent[F.of(lab, order[0])].mean(axis=0)
    t = pd.DataFrame({'feature': F.features, 'd': disp})
    t['level'] = np.where(t.feature.str.startswith('Image_'), 'image', 'cell')
    t['compartment'] = t.feature.str.split('_').str[0]
    t['channel'] = t.feature.map(channel_of)
    t['measurement'] = t.feature.map(measurement_of)
    t['sq'] = t.d ** 2

    g = t.groupby(['channel', 'measurement']).agg(n=('d', 'size'), mean_shift=('d', 'mean'),
                                                  mean_abs_shift=('d', lambda v: v.abs().mean()),
                                                  share_same_sign=('d', lambda v: max((v > 0).mean(), (v < 0).mean())))
    g = g[g.n >= 10].sort_values('mean_abs_shift', ascending=False)
    share = lambda col: {k: round(float(v), 3) for k, v in (t.groupby(col).sq.sum() / t.sq.sum()).sort_values(ascending=False).items()}
    n_feat = t.groupby('level').size()
    out = {'lab': lab, 'batch': batch, 'date': str(dates[batch].date()) if dates[batch] is not None else None,
           'baseline_batch': order[0], 'n_plates': int(len(F.of(lab, batch))), 'n_features': int(len(t)),
           'unit': 'standard deviations of the field, z clipped to +-5',
           'distance_in_spreads': round(float(np.linalg.norm(disp) / F.spread), 2),
           'share_of_displacement': {'by_level': share('level'), 'by_compartment': share('compartment'),
                                     'by_channel': share('channel'), 'by_measurement': share('measurement')},
           'share_of_features': {k: round(float(v / len(t)), 3) for k, v in n_feat.items()},
           'groups': [{'channel': c, 'measurement': m, 'n_features': int(r.n), 'mean_shift': round(float(r.mean_shift), 2),
                       'mean_abs_shift': round(float(r.mean_abs_shift), 2), 'direction': 'up' if r.mean_shift > 0 else 'down',
                       'share_same_sign': round(float(r.share_same_sign), 2)} for (c, m), r in g.iterrows()],
           'top_features': [{'feature': r.feature, 'd': round(float(r.d), 2)}
                            for r in t.reindex(t.d.abs().sort_values(ascending=False).index).head(15).itertuples()]}
    json.dump(out, open(f'results/e6-what-moved-{lab}{tag}.json', 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ('lab', 'batch', 'distance_in_spreads', 'share_of_displacement', 'share_of_features')}, indent=1))
    for r in out['groups'][:12]:
        print(f"  {r['channel']:18} {r['measurement']:20} n={r['n_features']:4d}  {r['direction']:4} {r['mean_shift']:+.2f}  |d| {r['mean_abs_shift']:.2f}  same sign {r['share_same_sign']:.0%}")
    for r in out['top_features'][:8]:
        print('   ', r['feature'], r['d'])


if __name__ == '__main__':
    main()
