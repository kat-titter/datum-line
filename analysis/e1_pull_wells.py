"""e1 wells: pull DMSO wells from JUMP cpg0016 compound plates into a local cache.

One parquet per plate under cache/wells/<source>/<plate>.parquet, holding only the
DMSO rows (JCP2022_033924) of the Gallery's well-level profile. Anonymous HTTPS,
no credentials. Plates already cached are skipped, so the script is resumable.

Usage:
  python analysis/e1_pull_wells.py                   # every compound plate that carries DMSO wells
  python analysis/e1_pull_wells.py PLATES.csv        # columns Metadata_Source, Metadata_Batch, Metadata_Plate
Needs:  metadata/plate.csv.gz, metadata/well.csv.gz
Writes: cache/wells/...
"""
import sys, io, time, urllib.request, concurrent.futures as cf
from pathlib import Path
import pandas as pd

DMSO = 'JCP2022_033924'
URL = 'https://cellpainting-gallery.s3.amazonaws.com/cpg0016-jump/{s}/workspace/profiles/{b}/{p}/{p}.parquet'
OUT = Path('cache/wells')


def pull(row, dmso_wells):
    out = OUT / row.Metadata_Source / f'{row.Metadata_Plate}.parquet'
    if out.exists():
        return 'cached'
    url = URL.format(s=row.Metadata_Source, b=row.Metadata_Batch, p=row.Metadata_Plate)
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(url, timeout=120).read()
            break
        except Exception as e:  # network hiccups: back off and retry
            if attempt == 3:
                return f'FAILED {e}'
            time.sleep(2 ** attempt)
    d = pd.read_parquet(io.BytesIO(raw))
    d = d[d['Metadata_Well'].isin(dmso_wells)]
    out.parent.mkdir(parents=True, exist_ok=True)
    d.to_parquet(out.with_suffix('.tmp'))
    out.with_suffix('.tmp').rename(out)
    return f'{len(d)} wells'


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
        futs = {ex.submit(pull, r, dmso.get((r.Metadata_Source, r.Metadata_Plate), set())): r
                for r in plates.itertuples()}
        for i, f in enumerate(cf.as_completed(futs), 1):
            r = futs[f]
            print(f'[{i}/{len(futs)}] {r.Metadata_Source} {r.Metadata_Plate}: {f.result()}', flush=True)


if __name__ == '__main__':
    main()
