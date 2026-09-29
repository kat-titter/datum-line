"""e8 wells: pull DMSO and positive-control wells from JUMP cpg0016 compound plates.

JUMP runs the same eight positive controls beside DMSO on every compound plate, so the
field already contains the experiment e8 needs. This script keeps only those wells from
each plate's well-level profile. Anonymous HTTPS, no credentials.

Each plate's profile has to be downloaded whole, so --per-source caps the number of
plates per lab. Plates are taken at even spacing through each lab's sorted plate list,
which spreads the sample across batches and is reproducible.

Usage:  python analysis/e8_pull_wells.py metadata results/e8_profiles.parquet [--per-source 25]
Writes: one parquet of well-level profiles with Metadata_Source, Metadata_Batch,
        Metadata_Plate, Metadata_Well and Metadata_JCP2022.
"""
import argparse
import io
import time
import urllib.request

import pandas as pd

URL = 'https://cellpainting-gallery.s3.amazonaws.com/cpg0016-jump/{s}/workspace/profiles/{b}/{p}/{p}.parquet'
DMSO = 'JCP2022_033924'
POSCON = ['JCP2022_037716', 'JCP2022_025848', 'JCP2022_046054', 'JCP2022_035095',
          'JCP2022_064022', 'JCP2022_050797', 'JCP2022_012818', 'JCP2022_085227']
KEYS = ['Metadata_Source', 'Metadata_Batch', 'Metadata_Plate']


def wanted_wells(meta_dir):
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
    """Evenly spaced plates per lab; all of them if per_source is None."""
    chosen = []
    for _, g in w.drop_duplicates('Metadata_Plate').groupby('Metadata_Source'):
        plates = sorted(g.Metadata_Plate)
        step = max(1, len(plates) // per_source) if per_source else 1
        chosen += plates[::step][:per_source]
    return chosen


def fetch(url, attempts=4):
    for k in range(attempts):
        try:
            return urllib.request.urlopen(url, timeout=120).read()
        except Exception:  # network hiccups: back off and retry
            if k == attempts - 1:
                raise
            time.sleep(2 ** k)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('metadata')
    ap.add_argument('out')
    ap.add_argument('--per-source', type=int, default=None)
    a = ap.parse_args()

    w = wanted_wells(a.metadata)
    chosen = choose_plates(w, a.per_source)
    print(f'{w.Metadata_Plate.nunique()} eligible plates, {len(chosen)} chosen, '
          f'{w[w.Metadata_Plate.isin(chosen)].Metadata_Source.nunique()} labs', flush=True)
    frames, start = [], time.time()
    for i, plate in enumerate(chosen):
        rows = w[w.Metadata_Plate == plate]
        r = rows.iloc[0]
        try:
            raw = fetch(URL.format(s=r.Metadata_Source, b=r.Metadata_Batch, p=plate))
        except Exception as e:
            print('skip', plate, str(e)[:80], flush=True)
            continue
        d = pd.read_parquet(io.BytesIO(raw))
        d['Metadata_Plate'] = d['Metadata_Plate'].astype(str)
        d = d.drop(columns=[c for c in ('Metadata_Source', 'Metadata_Batch') if c in d.columns])
        frames.append(d.merge(rows[['Metadata_Well', 'Metadata_JCP2022', 'Metadata_Source', 'Metadata_Batch']],
                              on='Metadata_Well'))
        if i % 20 == 0:
            print(f'{i + 1}/{len(chosen)} plates, {time.time() - start:.0f} s', flush=True)
    pd.concat(frames, ignore_index=True).to_parquet(a.out)
    print('wrote', a.out, len(frames), 'plates')


if __name__ == '__main__':
    main()
