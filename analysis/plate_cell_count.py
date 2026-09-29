"""Local check: is a plate's cell count normal for its own lab?

Cell count is the check every lab already runs. For one plate, this reports the mean
number of cells per untreated (DMSO) well and where that falls among the other plates
of the same lab, within the same batch and across the whole lab.

The well-level profile carries no count column. Nuclei_Number_Object_Number is the mean
object index per image, (n + 1) / 2 for n nuclei, so the count is 2 * value - 1.

Usage:  python analysis/plate_cell_count.py [PLATE]      (default 1053600681)
Needs:  cache/wells/ from e1_pull_wells.py, metadata/
Writes: results/cell-count-PLATE.json, results/cell-count-PLATE.csv
"""
import json
import sys
from pathlib import Path

import pandas as pd

COUNT = 'Nuclei_Number_Object_Number'
WELLS = Path('cache/wells')


def plate_counts(lab):
    rows = []
    for f in sorted((WELLS / lab).glob('*.parquet')):
        d = pd.read_parquet(f, columns=['Metadata_Plate', COUNT])
        cells = 2 * d[COUNT] - 1
        rows.append({'plate': str(d.Metadata_Plate.iloc[0]), 'n_wells': len(d),
                     'cells_per_well': float(cells.mean()), 'cv_across_wells': float(cells.std() / cells.mean())})
    return pd.DataFrame(rows)


def percentile(values, x):
    return float((values < x).mean() * 100)


def main():
    plate = sys.argv[1] if len(sys.argv) > 1 else '1053600681'
    meta = pd.read_csv('metadata/plate.csv.gz', dtype=str).set_index('Metadata_Plate')
    lab, batch = meta.loc[plate, 'Metadata_Source'], meta.loc[plate, 'Metadata_Batch']
    t = plate_counts(lab)
    t['batch'] = t.plate.map(meta.Metadata_Batch)
    t['same_batch'] = t.batch == batch
    this = t[t.plate == plate].iloc[0]
    same = t[t.same_batch]
    out = {'plate': plate, 'lab': lab, 'batch': batch, 'count_feature': COUNT,
           'cells_per_well': round(this.cells_per_well, 1), 'n_wells': int(this.n_wells),
           'same_batch': {'n_plates': len(same), 'mean': round(same.cells_per_well.mean(), 1),
                          'sd': round(same.cells_per_well.std(), 1),
                          'percentile': round(percentile(same.cells_per_well, this.cells_per_well))},
           'whole_lab': {'n_plates': len(t), 'mean': round(t.cells_per_well.mean(), 1),
                         'sd': round(t.cells_per_well.std(), 1),
                         'percentile': round(percentile(t.cells_per_well, this.cells_per_well))}}
    Path('results').mkdir(exist_ok=True)
    json.dump(out, open(f'results/cell-count-{plate}.json', 'w'), indent=2)
    t.sort_values('cells_per_well').to_csv(f'results/cell-count-{plate}.csv', index=False)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
