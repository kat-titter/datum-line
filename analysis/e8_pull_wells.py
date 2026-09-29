"""e8 wells: pull DMSO and positive-control wells from JUMP cpg0016 compound plates.

JUMP runs the same eight positive controls beside DMSO on every compound plate, so the
field already contains the experiment e8 needs. This script keeps only those wells from
each plate's well-level profile: one parquet per plate under
cache/poscon/<source>/<plate>.parquet. Anonymous HTTPS, no credentials. Plates already
cached are skipped, so the script is resumable.

--per-source caps the number of plates per lab, taken at even spacing through each lab's
sorted plate list. Without it every eligible plate is pulled.

Usage:  python analysis/e8_pull_wells.py [--per-source N]
Needs:  metadata/plate.csv.gz, metadata/well.csv.gz
Writes: cache/poscon/...
"""
import argparse
import concurrent.futures as cf
import io
import time
import urllib.request
from pathlib import Path

import pandas as pd

URL = 'https://cellpainting-gallery.s3.amazonaws.com/cpg0016-jump/{s}/workspace/profiles/{b}/{p}/{p}.parquet'
OUT = Path('cache/poscon')
DMSO = 'JCP2022_033924'
POSCON = ['JCP2022_037716', 'JCP2022_025848', 'JCP2022_046054', 'JCP2022_035095',
          'JCP2022_064022', 'JCP2022_050797', 'JCP2022_012818', 'JCP2022_085227']
KEYS = ['Metadata_Source', 'Metadata_Batch', 'Metadata_Plate']


def wanted_wells(meta_dir='metadata'):
    """DMSO and positive-control wells on compound plates that carry both."""
    wells = pd.read_csv(f'{meta_dir}/well.csv.gz', dtype=str)
    plates = pd.read_csv(f'{meta_dir}/plate.csv.gz', dtype=str)
    plates = plates[plates.Metadata_PlateType == 'COMPOUND'][KEYS]
    w = wells[['Metadata_Plate', 'Metadata_Well', 'Metadata_JCP2022']].merge(plates, on='Metadata_Plate')
    w = w[w.Metadata_JCP2022.isin([DMSO] + POSCON)]
    has_dmso = set(w[w.Metadata_JCP2022 == DMSO].Metadata_Plate)
    has_poscon = set(w[w.Metadata_JCP2022.isin(POSCON)].Metadata_Plate)
    return w[w.Metadata_Plate.isin(has_dmso & has_poscon)]


def choose_plates(w, per_source):
    chosen = []
    for _, g in w.drop_duplicates('Metadata_Plate').groupby('Metadata_Source'):
        plates = sorted(g.Metadata_Plate)
        step = max(1, len(plates) // per_source) if per_source else 1
        chosen += plates[::step][:per_source]
    return chosen


def pull(rows):
    r = rows.iloc[0]
    out = OUT / r.Metadata_Source / f'{r.Metadata_Plate}.parquet'
    if out.exists():
        return 'cached'
    url = URL.format(s=r.Metadata_Source, b=r.Metadata_Batch, p=r.Metadata_Plate)
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(url, timeout=180).read()
            break
        except Exception as e:  # network hiccups: back off and retry
            if attempt == 3:
                return f'FAILED {e}'
            time.sleep(2 ** attempt)
    d = pd.read_parquet(io.BytesIO(raw))
    d['Metadata_Plate'] = d['Metadata_Plate'].astype(str)
    d = d.drop(columns=[c for c in ('Metadata_Source', 'Metadata_Batch') if c in d.columns])
    d = d.merge(rows[['Metadata_Well', 'Metadata_JCP2022', 'Metadata_Source', 'Metadata_Batch']], on='Metadata_Well')
    out.parent.mkdir(parents=True, exist_ok=True)
    d.to_parquet(out.with_suffix('.tmp'))
    out.with_suffix('.tmp').rename(out)
    return f'{len(d)} wells'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--per-source', type=int, default=None)
    a = ap.parse_args()
    w = wanted_wells()
    chosen = choose_plates(w, a.per_source)
    groups = [g for _, g in w[w.Metadata_Plate.isin(chosen)].groupby('Metadata_Plate')]
    print(f'{w.Metadata_Plate.nunique()} eligible plates, {len(groups)} chosen', flush=True)
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(pull, g): g.iloc[0] for g in groups}
        for i, f in enumerate(cf.as_completed(futs), 1):
            r = futs[f]
            print(f'[{i}/{len(futs)}] {r.Metadata_Source} {r.Metadata_Plate}: {f.result()}', flush=True)


if __name__ == '__main__':
    main()
