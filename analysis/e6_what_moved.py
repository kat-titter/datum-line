"""e6: what moved, and which way back. The interpretable side of the certificate.

For one plate (default 1053600681), take its DMSO wells and the field's DMSO wells from
the other sources, on the same z-scored features used for e1. The displacement is

    d = mean(plate) - mean(field)                       (per feature, in field SD units)

Report (1) its length, the certificate's distance; (2) the top 15 features by |d| with
sign, which is the "what"; (3) |d| aggregated by compartment (Cells/Cytoplasm/Nuclei)
and channel (DNA/RNA/ER/AGP/Mito) from the CellProfiler feature names, which is the
"where"; (4) the direction back is -d, so each top feature reads as a to-do:
"Mito texture is low relative to the field: raise it" and so on. Nothing here is a
model; it is the difference of two means, which is why a lab can act on it.

Usage: python e6_what_moved.py PROFILES.parquet [plate]
Writes: results/e6-what-moved.json
"""
import sys, json, re, numpy as np, pandas as pd
d = pd.read_parquet(sys.argv[1]); plate = sys.argv[2] if len(sys.argv) > 2 else '1053600681'
d['Metadata_Plate'] = d['Metadata_Plate'].astype(str)
feats = [c for c in d.columns if not c.startswith('Metadata_')]
X = d[feats].apply(pd.to_numeric, errors='coerce'); X = X.loc[:, X.notna().all() & (X.std() > 0)]
me = d['Metadata_Plate'] == plate
src = d.loc[me, 'Metadata_Source'].iloc[0]
field = X[(d['Metadata_Source'] != src)]                     # every other lab
mu, sd = field.mean(), field.std()
Z = (X - mu) / sd
disp = Z[me].mean()                                          # displacement in field SD units
out = {'plate': plate, 'source': src, 'n_plate_wells': int(me.sum()), 'n_field_wells': int(len(field)),
       'distance': float(np.sqrt((disp ** 2).sum())), 'top_features': []}
for f, v in disp.abs().sort_values(ascending=False).head(15).items():
    out['top_features'].append({'feature': f, 'd': float(disp[f]), 'back': 'raise' if disp[f] < 0 else 'lower'})
def part(f, i): 
    p = f.split('_'); return p[i] if len(p) > i else 'other'
comp = disp.abs().groupby(lambda f: part(f, 0)).sum(); comp = (comp / comp.sum()).round(3)
chan = disp.abs().groupby(lambda f: next((c for c in ('DNA', 'RNA', 'ER', 'AGP', 'Mito') if re.search(rf'(^|_){c}(_|$)', f)), 'none')).sum(); chan = (chan / chan.sum()).round(3)
out['share_by_compartment'] = comp.to_dict(); out['share_by_channel'] = chan.to_dict()
json.dump(out, open('results/e6-what-moved.json', 'w'), indent=2); print(json.dumps(out, indent=2)[:2000])
