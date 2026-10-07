"""e15, part 1: one untreated well of every compound plate, as images.

For each plate: the first interior DMSO well in well order, its first site, every channel the
lab recorded (DNA, ER, AGP, Mito, RNA, and brightfield where the lab kept one). Each channel
is saved as an 8-bit PNG of the whole field, scaled to 512 pixels on the long side, with the
pixel window set by that image's 0.5th and 99.8th percentiles. The 16-bit originals are not
kept. The well, site, original shape and window are written beside the images.

Interior wells only (rows C to N, columns 4 to 21), so edge effects are not in the picture.

Usage:  python analysis/e15_pull_images.py [plates.csv]     resumable; about 20 GB of downloads
Needs:  metadata/plate.csv.gz, metadata/well.csv.gz (jump-cellpainting/datasets @ 016e865), cache/wells/
Writes: cache/images/{source}/{plate}/{channel}.png and meta.json
"""
import concurrent.futures as cf
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
from PIL import Image

DMSO = 'JCP2022_033924'
BUCKET = 'https://cellpainting-gallery.s3.amazonaws.com/'
LOAD = BUCKET + 'cpg0016-jump/{s}/workspace/load_data_csv/{b}/{p}/load_data.csv'
OUT = Path('cache/images')
CHANNELS = ['DNA', 'ER', 'AGP', 'Mito', 'RNA', 'Brightfield']
INTERIOR = re.compile(r'^[C-N](0[4-9]|1[0-9]|2[01])$')
SIDE = 512


def fetch(url, tries=4):
    for attempt in range(tries):
        try:
            return urllib.request.urlopen(url, timeout=180).read()
        except Exception as e:  # network hiccups: back off and retry
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)


def to_png(raw):
    im = tifffile.imread(io.BytesIO(raw)).astype(np.float32)
    if im.ndim == 3:
        im = im[0]
    lo, hi = np.percentile(im, [0.5, 99.8])
    x = np.clip((im - lo) / max(hi - lo, 1), 0, 1)
    h, w = im.shape
    scale = SIDE / max(h, w)
    png = Image.fromarray((x * 255).astype(np.uint8)).resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    return png, {'shape': [int(h), int(w)], 'window': [float(lo), float(hi)]}


def pull(row, wells):
    out = OUT / row.Metadata_Source / row.Metadata_Plate
    if (out / 'meta.json').exists():
        return 'cached'
    ld = pd.read_csv(io.BytesIO(fetch(LOAD.format(s=row.Metadata_Source, b=row.Metadata_Batch, p=row.Metadata_Plate))), dtype=str)
    here = ld[ld.Metadata_Well.isin(wells) & ld.Metadata_Well.str.match(INTERIOR)]
    if here.empty:
        here = ld[ld.Metadata_Well.isin(wells)]
    if here.empty:
        return 'no untreated well in load_data'
    well = sorted(here.Metadata_Well)[0]
    site = sorted(here[here.Metadata_Well == well].Metadata_Site, key=lambda s: int(s))[0]
    r = here[(here.Metadata_Well == well) & (here.Metadata_Site == site)].iloc[0]
    meta = {'source': row.Metadata_Source, 'batch': row.Metadata_Batch, 'plate': row.Metadata_Plate, 'well': well, 'site': str(site), 'channels': {}}
    out.mkdir(parents=True, exist_ok=True)
    for c in CHANNELS:
        col = f'URL_Orig{c}'
        if col not in r or pd.isna(r[col]):
            continue
        png, info = to_png(fetch(r[col].replace('s3://cellpainting-gallery/', BUCKET)))
        png.save(out / f'{c}.png', optimize=True)
        meta['channels'][c] = info
    (out / 'meta.json').write_text(json.dumps(meta))
    return f'{well} site {site}, {len(meta["channels"])} channels'


def main():
    w = pd.read_csv('metadata/well.csv.gz', dtype=str)
    w = w[w.Metadata_JCP2022 == DMSO]
    if len(sys.argv) > 1:
        plates = pd.read_csv(sys.argv[1], dtype=str)
    else:
        plates = pd.read_csv('metadata/plate.csv.gz', dtype=str)
        plates = plates[(plates.Metadata_PlateType == 'COMPOUND') & plates.Metadata_Plate.isin(set(w.Metadata_Plate))]
    print(f'{len(plates)} plates, {plates.Metadata_Source.nunique()} labs', flush=True)
    dmso = w.groupby(['Metadata_Source', 'Metadata_Plate'])['Metadata_Well'].apply(set).to_dict()
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(pull, r, dmso.get((r.Metadata_Source, r.Metadata_Plate), set())): r for r in plates.itertuples()}
        for i, f in enumerate(cf.as_completed(futs), 1):
            r = futs[f]
            try:
                print(f'[{i}/{len(futs)}] {r.Metadata_Source} {r.Metadata_Plate}: {f.result()}', flush=True)
            except Exception as e:
                print(f'[{i}/{len(futs)}] {r.Metadata_Source} {r.Metadata_Plate}: FAILED {e}', flush=True)


if __name__ == '__main__':
    main()
