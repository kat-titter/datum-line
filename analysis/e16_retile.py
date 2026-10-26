"""Re-crop slide 05a's tiles without re-running e16: the same wells, sites and display windows (results/e16 images block),
each 300 um crop moved to where its nucleus count is nearest what the well's measured count predicts for that area
(e16.typical_crop; counts from cache/e16/wells, as e16 reads them). The numbers in results/e16 do not change.

Fetches each lab's load-data CSV and four field images (two wells, two channels) from the Cell Painting Gallery, about 25 MB.
Usage, from the repository root:  .venv/bin/python analysis/e16_retile.py
"""
import io
import json
import sys

import pandas as pd

sys.path.insert(0, 'analysis')
import e15_pull_images as e15                                                   # noqa: E402
import field as fd                                                              # noqa: E402
from e16_same_perturbation import TILE_UM, tiff, tile, typical_crop             # noqa: E402

path = 'results/e16-same-perturbation.json'
res = json.load(open(path))
for lab, info in res['images']['labs'].items():
    ld = pd.read_csv(io.BytesIO(e15.fetch(e15.LOAD.format(s=lab, b=info['batch'], p=info['plate']))), dtype=str)
    row = lambda w: ld[(ld.Metadata_Well == w) & (ld.Metadata_Site == info['site'])].iloc[0]
    wells = {'rsl3': info['well'], 'dmso': info['dmso_well']}
    dna = {k: tiff(row(w)['URL_OrigDNA']) for k, w in wells.items()}
    wd = pd.read_parquet(f'cache/e16/wells/{lab}/{info["plate"]}.parquet').set_index('Metadata_Well')
    count = {k: 2 * float(wd.loc[w, fd.COUNT]) - 1 for k, w in wells.items()}      # nuclei per field, as e16's meta.cells
    side = min(round(TILE_UM / info['um_per_px']), *dna['rsl3'].shape)
    at = {k: typical_crop(dna[k], side, count[k]) for k in dna}
    for c, ch in info['channels'].items():
        for k, w in wells.items():
            im = dna[k] if c == 'DNA' else tiff(row(w)[f'URL_Orig{c}'])
            crop = tile(im, ch['window_from_dmso'], info['um_per_px'], ch[k], at[k])['crop_px']
            ch['crop_px' if k == 'rsl3' else 'dmso_crop_px'] = crop
    print(f'  {lab}: rsl3 crop at {at["rsl3"]}, DMSO crop at {at["dmso"]}', flush=True)
json.dump(res, open(path, 'w'), indent=1)
print('written', path)
