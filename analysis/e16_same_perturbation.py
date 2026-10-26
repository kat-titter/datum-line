"""e16: many labs run the same reference perturbation. Does it look the same in every lab?

Slide 05 asks "does my control look like yours?". A lab that runs a reference compound to
show its assay works is comparing its answer with everyone else's. JUMP holds two
ferroptosis inducers on its compound plates, one well per plate:

  RSL3     JCP2022_087365, GPX4 inhibitor        12 plates in four labs
  erastin  JCP2022_006961, system xc- inhibitor  11 plates in six labs

Every well is measured the way e8 measures the eight positive controls: effect = the well
minus the mean of its own plate's DMSO wells, in e8's features, z-scored on the field's
DMSO wells (every plate in cache/poscon). Then, per lab:

  own lab      mean cosine between a well's effect and the lab's other wells, on other plates
  other labs   mean cosine between a well's effect and another lab's wells, averaged over
               the other labs so each lab counts once
  size         length of the effect, in e8's units
  cells        nuclei per image, as a share of the same plate's DMSO wells

One well is noisier than e8's plate means (about four wells of each control per plate), so
the numbers are read against references measured in exactly the same way on the same plates:

  positive controls  the eight JUMP controls, one well at a time against its plate's DMSO,
                     pairs from different plates only, each lab counted once
  noise              a DMSO well against the rest of its plate's DMSO; and two DMSO wells at
                     the same position on two plates of one lab, which share any layout effect
                     the way one lab's RSL3 wells do (they sit at one position in each lab)
  e8 field         e8-redteam.json and e8-same-drug-different-answer.json, read as they are:
                     plate means, every plate of every lab

The eight controls are also re-measured from e8-redteam's definition on the RSL3 plates, so
nothing is compared across two definitions without saying so. no_position repeats the
summaries without position, count and bookkeeping features, as e8_redteam.py does.

Dose. JUMP assayed library compounds at 10 uM at every site except source_7, at 0.625 uM;
the positive controls were 5 uM at every site [7]. The well metadata does not record it.
RSL3.same_dose_only repeats RSL3, its controls and its noise on the wells and plates of the
labs at 10 uM only, measured exactly as the all-lab result; the lab at 0.625 uM is reported
beside it (left_out), with each lab's cells left and dose (dose_check). It also checks, well
by well, that each RSL3 well was measured against its own plate's DMSO wells, all of them.

Images: per lab, the RSL3 well with the highest mean cosine with its lab's other RSL3 wells
(the only well, where a lab has one), the middle site of the well, a 300 um square from the
centre of the field at 256 px. DNA, and the channel that carries the largest share of RSL3's
effect, each beside a typical DMSO well on the same plate (cell count nearest the plate's DMSO median), same site. Each
lab is shown in the pixel window of its own DMSO image (1st and 99.7th percentiles, as the
game tiles), so RSL3 and DMSO are comparable inside a lab; brightness between labs is not.

Usage:  python analysis/e16_same_perturbation.py
Needs:  metadata/*.csv.gz and metadata/microscope_config.csv, cache/poscon/ (e8_pull_wells.py),
        results/e8-redteam.json, results/e8-same-drug-different-answer.json
Writes: cache/e16/, results/e16-same-perturbation.json,
        figures/assets/e16-rsl3-SOURCE.png, e16-rsl3-SOURCE-CHANNEL.png,
        figures/assets/e16-dmso-SOURCE.png, e16-dmso-SOURCE-CHANNEL.png
"""
import concurrent.futures as cf
import io
import json
import re
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
from PIL import Image

import e8_pull_wells as pull8
import e15_pull_images as e15
import field as fd
from e6_what_moved import channel_of
from e8_redteam import DMSO, POSCON, POSITION

PERTURBATIONS = {'JCP2022_087365': 'RSL3', 'JCP2022_006961': 'erastin'}
# compound dose by site, from the JUMP methods [7]: 10 uM everywhere except source_7 at 0.625 uM; positive controls 5 uM at every site
DOSE_UM = {'default': 10.0, 'source_7': 0.625}
WHAT = {'RSL3': 'GPX4 inhibitor; induces ferroptosis', 'erastin': 'system xc- inhibitor; induces ferroptosis'}
CACHE = Path('cache/e16')
ASSETS = Path('figures/assets')
SCALE = CACHE / 'field-scale.json'
TILE_UM, TILE_PX = 300, 256
WINDOW = (1, 99.7)
SECOND = ('ER', 'AGP', 'Mito')            # e8's feature set has no RNA-channel features


def r3(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 3)


# ---------------------------------------------------------------- data

def wanted_wells(meta_dir='metadata'):
    """DMSO, positive-control, RSL3 and erastin wells of every compound plate that holds RSL3 or erastin."""
    wells = pd.read_csv(f'{meta_dir}/well.csv.gz', dtype=str)
    plates = pd.read_csv(f'{meta_dir}/plate.csv.gz', dtype=str)
    plates = plates[plates.Metadata_PlateType == 'COMPOUND'][pull8.KEYS]
    w = wells[['Metadata_Plate', 'Metadata_Well', 'Metadata_JCP2022']].merge(plates, on='Metadata_Plate')
    target = set(w[w.Metadata_JCP2022.isin(PERTURBATIONS)].Metadata_Plate)
    return w[w.Metadata_Plate.isin(target) & w.Metadata_JCP2022.isin([DMSO, *POSCON, *PERTURBATIONS])]


def pull_plates(w):
    """Well-level profiles of those plates, through e8's own puller, into cache/e16/wells."""
    pull8.OUT = CACHE / 'wells'
    groups = [g for _, g in w.groupby('Metadata_Plate')]
    with cf.ThreadPoolExecutor(8) as ex:
        for g, res in zip(groups, ex.map(pull8.pull, groups)):
            print(f'  {g.Metadata_Source.iloc[0]} {g.Metadata_Plate.iloc[0]}: {res}', flush=True)
            if str(res).startswith('FAILED'):
                raise SystemExit(res)


def field_scale():
    """e8's feature set and scale, one plate at a time: the columns fd.load_poscon() keeps, and the
    mean and SD of each over the field's DMSO wells.

    fd.load_poscon() holds every well in memory at once; this reads one plate file at a time and
    applies the same rules to the whole: a feature is kept when it is present, numeric and finite
    in every well, below 1e6 in absolute value, and not constant. Values are cast to float32
    first, as e1.feature_matrix does. Kept in cache/e16/field-scale.json; recomputed when the
    number of cached plates changes.
    """
    files = sorted(Path('cache/poscon').glob('*/*.parquet'))
    if SCALE.exists():
        s = json.loads(SCALE.read_text())
        if s['n_files'] == len(files):
            return s
    print(f'scaling on the field: {len(files)} plates in cache/poscon, one at a time', flush=True)
    cols, ok, lo, hi = None, None, None, None
    n, mean, m2 = 0, None, None
    plates = set()
    for k, f in enumerate(files):
        d = pd.read_parquet(f)
        if cols is None:
            cols = [c for c in d.columns if not c.startswith('Metadata_')]
            ok = np.ones(len(cols), bool)
            lo, hi = np.full(len(cols), np.inf), np.full(len(cols), -np.inf)
            mean, m2 = np.zeros(len(cols)), np.zeros(len(cols))
        X = d.reindex(columns=cols)
        num = X.select_dtypes('number').columns
        X = pd.concat([X[num], X.drop(columns=num).apply(pd.to_numeric, errors='coerce')], axis=1)[cols]
        v = X.to_numpy('float32').astype('float64')
        ok &= np.isfinite(v).all(axis=0) & (np.abs(v).max(axis=0) < 1e6)
        lo, hi = np.fmin(lo, np.nanmin(v, axis=0)), np.fmax(hi, np.nanmax(v, axis=0))
        dm = v[(d.Metadata_JCP2022.astype(str) == DMSO).to_numpy()]
        if len(dm):   # Chan et al.: merge this plate's DMSO mean and sum of squares into the running ones
            nb, mb = len(dm), dm.mean(axis=0)
            delta = mb - mean
            m2 += ((dm - mb) ** 2).sum(axis=0) + delta ** 2 * n * nb / (n + nb)
            mean += delta * nb / (n + nb)
            n += nb
        plates.add(str(d.Metadata_Plate.iloc[0]))
        if (k + 1) % 200 == 0:
            print(f'  {k + 1} plates', flush=True)
    ok &= hi > lo
    sd = np.sqrt(m2 / (n - 1))
    s = {'n_files': len(files), 'n_dmso_wells': int(n), 'n_plates': len(plates),
         'features': [c for c, o in zip(cols, ok) if o],
         'mu': [float(x) for x in mean[ok]], 'sd': [float(x) for x in sd[ok]]}
    SCALE.parent.mkdir(parents=True, exist_ok=True)
    SCALE.write_text(json.dumps(s))
    return s


def load(scale):
    files = sorted((CACHE / 'wells').glob('*/*.parquet'))
    d = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    for c in ('Metadata_Source', 'Metadata_Batch', 'Metadata_Plate', 'Metadata_Well', 'Metadata_JCP2022'):
        d[c] = d[c].astype(str)
    feats = scale['features']
    missing = [f for f in feats if f not in d.columns]
    if missing:
        raise SystemExit(f'{len(missing)} of e8\'s features are missing from these plates, e.g. {missing[:3]}')
    X = d[feats].apply(pd.to_numeric, errors='coerce').to_numpy('float64')
    sd = np.array(scale['sd'])
    sd[sd == 0] = np.nan
    Z = (X - np.array(scale['mu'])) / sd
    bad = ~np.isfinite(Z)
    meta = d[['Metadata_Source', 'Metadata_Batch', 'Metadata_Plate', 'Metadata_Well', 'Metadata_JCP2022']].copy()
    meta.columns = ['lab', 'batch', 'plate', 'well', 'jcp']
    meta['compound'] = meta.jcp.map({DMSO: 'DMSO', **POSCON, **PERTURBATIONS})
    meta['cells'] = 2 * pd.to_numeric(d[fd.COUNT], errors='coerce').to_numpy() - 1   # see field.COUNT
    return meta, Z, bad


def effects(meta, Z, bad):
    """Each well minus the mean of its plate's DMSO wells; a DMSO well minus the mean of the plate's OTHER DMSO wells.

    A value that is missing or non-finite in a treated well is set to its plate's DMSO mean
    (no effect on that feature); e8's feature set has none in DMSO or positive-control wells.
    """
    E = np.zeros_like(Z)
    Zc = np.where(bad, np.nan, Z)
    cells = meta.cells.to_numpy()
    cells_ratio = np.full(len(meta), np.nan)
    for _, g in meta.groupby('plate'):
        i = g.index.to_numpy()
        is_dmso = (g.compound == 'DMSO').to_numpy()
        dm = i[is_dmso]
        total, n = Zc[dm].sum(axis=0), len(dm)
        for k, own in zip(i, is_dmso):
            ref = (total - Zc[k]) / (n - 1) if own else total / n
            E[k] = np.nan_to_num(Zc[k] - ref, nan=0.0, posinf=0.0, neginf=0.0)
        cells_ratio[i] = cells[i] / cells[dm].mean()
    return E, cells_ratio


# ---------------------------------------------------------------- agreement

def unit_rows(E):
    n = np.linalg.norm(E, axis=1, keepdims=True)
    return E / np.where(n == 0, 1, n)


def agreement(meta, E, cells=None):
    """Lab-by-lab mean cosine between single-well effects (pairs on different plates), size and cells."""
    labs = sorted(meta.lab.unique())
    U = unit_rows(E)
    C = U @ U.T
    lab = meta.lab.to_numpy()
    plate = meta.plate.to_numpy()
    other_plate = plate[:, None] != plate[None, :]
    M = pd.DataFrame(np.nan, index=labs, columns=labs)
    pairs = pd.DataFrame(0, index=labs, columns=labs)
    for a in labs:
        for b in labs:
            m = (lab == a)[:, None] & (lab == b)[None, :] & other_plate
            if a == b:
                m = np.triu(m, 1)
            if m.any():
                M.loc[a, b], pairs.loc[a, b] = C[m].mean(), int(m.sum())
    size = np.linalg.norm(E, axis=1)
    by_lab = {}
    for a in labs:
        rows = lab == a
        other = M.loc[a].drop(a)
        by_lab[a] = {'n_wells': int(rows.sum()), 'n_plates': int(meta.plate[rows].nunique()),
                     'own_lab': r3(M.loc[a, a]), 'own_lab_pairs': int(pairs.loc[a, a]),
                     'other_labs': r3(other.mean()) if other.notna().any() else None,
                     'size': round(float(size[rows].mean()), 2),
                     'size_median': round(float(np.median(size[rows])), 2)}
        if cells is not None:
            by_lab[a]['cells_vs_dmso'] = r3(np.nanmean(cells[rows]))
    own = [by_lab[a]['own_lab'] for a in labs if by_lab[a]['own_lab'] is not None]
    gap = [by_lab[a]['own_lab'] - by_lab[a]['other_labs'] for a in labs
           if by_lab[a]['own_lab'] is not None and by_lab[a]['other_labs'] is not None]
    off = M.to_numpy()[np.triu_indices(len(labs), 1)]
    return {'n_wells': int(len(meta)), 'n_plates': int(meta.plate.nunique()), 'n_labs': len(labs),
            'own_lab': r3(np.mean(own)) if own else None,
            'other_labs': r3(np.nanmean(off)) if np.isfinite(off).any() else None,
            'own_minus_other_where_both': r3(np.mean(gap)) if gap else None,
            'labs_with_own_lab': len(own),
            'size': round(float(np.mean([v['size'] for v in by_lab.values()])), 2),
            'by_lab': by_lab,
            'lab_by_lab': {a: {b: r3(M.loc[a, b]) for b in labs} for a in labs},
            'pairs': {a: {b: int(pairs.loc[a, b]) for b in labs} for a in labs}}


def same_position_dmso(meta, E):
    """Cosine between DMSO noise of two wells at the same position on two plates of one lab."""
    U = unit_rows(E)
    out = {}
    for a, g in meta.groupby('lab'):
        cos = []
        for _, h in g.groupby('well'):
            i = h.index.to_numpy()
            if len(i) > 1:
                C = U[i] @ U[i].T
                cos += list(C[np.triu_indices(len(i), 1)])
        out[a] = {'pairs': len(cos), 'mean_cosine': r3(np.mean(cos)) if cos else None}
    vals = [v['mean_cosine'] for v in out.values() if v['mean_cosine'] is not None]
    return {'mean_over_labs': r3(np.mean(vals)) if vals else None, 'by_lab': out}


def per_well(meta, E, cells):
    """One row per well of a perturbation, with its cosine to every other well of that perturbation."""
    U = unit_rows(E)
    C = U @ U.T
    size = np.linalg.norm(E, axis=1)
    rows = []
    for k, (i, r) in enumerate(meta.iterrows()):
        rows.append({'lab': r.lab, 'batch': r.batch, 'plate': r.plate, 'well': r.well,
                     'size': round(float(size[k]), 2), 'cells_vs_dmso': r3(cells[k]),
                     'mean_cosine_own_lab': r3(np.mean([C[k, j] for j in range(len(meta)) if j != k and meta.lab.iloc[j] == r.lab])
                                               if (meta.lab == r.lab).sum() > 1 else np.nan),
                     'mean_cosine_other_labs': r3(np.mean([C[k, j] for j in range(len(meta)) if meta.lab.iloc[j] != r.lab]))})
    return rows, np.round(C, 3).tolist()


def study(meta, E, cells, name, keep=None):
    """Everything for one perturbation: its wells, and the references on its own plates."""
    cols = slice(None) if keep is None else keep
    m = (meta.compound == name).to_numpy()
    on = meta.plate.isin(set(meta.plate[m])).to_numpy()
    sub = lambda mask: (meta[mask].reset_index(drop=True), E[mask][:, cols])
    pm, pE = sub(m)
    res = agreement(pm, pE, cells[m])
    ref = {c: agreement(*sub(on & (meta.compound == c).to_numpy()), cells[on & (meta.compound == c).to_numpy()])
           for c in POSCON.values() if (on & (meta.compound == c).to_numpy()).any()}
    dm, dE = sub(on & (meta.compound == 'DMSO').to_numpy())
    noise = agreement(dm, dE, cells[on & (meta.compound == 'DMSO').to_numpy()])
    noise['same_position_same_lab'] = same_position_dmso(dm, dE)
    return pm, pE, res, ref, noise


def compare(name, res, ref, noise):
    """A perturbation beside the eight controls and the DMSO noise, all measured the same way on the same plates."""
    own_c = [v['own_lab'] for v in ref.values() if v['own_lab'] is not None]
    oth_c = [v['other_labs'] for v in ref.values() if v['other_labs'] is not None]
    return {
        'own_lab': {name: res['own_lab'], 'controls_min': r3(min(own_c)), 'controls_median': r3(np.median(own_c)),
                    'controls_max': r3(max(own_c)), 'dmso_noise': noise['own_lab'],
                    'dmso_same_position': noise['same_position_same_lab']['mean_over_labs']},
        'other_labs': {name: res['other_labs'], 'controls_min': r3(min(oth_c)), 'controls_median': r3(np.median(oth_c)),
                       'controls_max': r3(max(oth_c)), 'dmso_noise': noise['other_labs'],
                       'controls_below': [c for c, v in ref.items() if (v['other_labs'] or 1) < res['other_labs']]},
        'size_by_lab': {lab: {name: v['size'], 'dmso_noise_median': noise['by_lab'][lab]['size_median'],
                              'times_noise': round(v['size'] / noise['by_lab'][lab]['size_median'], 2),
                              'controls_median': round(float(np.median([ref[c]['by_lab'][lab]['size'] for c in ref
                                                                        if lab in ref[c]['by_lab']])), 2),
                              'controls': {c: ref[c]['by_lab'][lab]['size'] for c in ref if lab in ref[c]['by_lab']}}
                        for lab, v in res['by_lab'].items()}}


def dose_of(lab):
    return DOSE_UM.get(lab, DOSE_UM['default'])


def untreated_on_each_plate(meta, Z, bad, E, cells, name, listed):
    """Check, well by well, that each perturbation well was measured against its own plate's DMSO wells.

    Recomputes every effect from the plate's DMSO wells, picked by plate name from the whole table (not by effects()'s
    groupby), and compares it with E; compares the number of DMSO wells used with the number the well metadata lists for
    that plate; and recomputes the share of cells left from the same DMSO wells."""
    Zc = np.where(bad, np.nan, Z)
    rows, worst_effect, worst_cells = [], 0.0, 0.0
    for k in np.flatnonzero((meta.compound == name).to_numpy()):
        r = meta.loc[k]
        dm = np.flatnonzero(((meta.plate == r.plate) & (meta.compound == 'DMSO')).to_numpy())
        again = np.nan_to_num(Zc[k] - Zc[dm].mean(axis=0), nan=0.0, posinf=0.0, neginf=0.0)
        worst_effect = max(worst_effect, float(np.abs(again - E[k]).max()))
        c = meta.cells.to_numpy()
        worst_cells = max(worst_cells, abs(float(c[k] / c[dm].mean()) - float(cells[k])))
        rows.append({'lab': r.lab, 'batch': r.batch, 'plate': r.plate, 'well': r.well, 'dose_um': dose_of(r.lab),
                     'dmso_wells_used': int(len(dm)), 'dmso_wells_in_metadata': int(listed.get(r.plate, 0)),
                     'dmso_wells_all_on_this_plate': bool((meta.plate.to_numpy()[dm] == r.plate).all()),
                     'cells_vs_dmso': r3(cells[k])})
    return {'what': f'each {name} well minus the mean of its own plate\'s DMSO wells; cells left as a share of the same wells',
            'every_well_own_plate_dmso': all(w['dmso_wells_all_on_this_plate'] and w['dmso_wells_used'] > 0 for w in rows),
            'every_listed_dmso_well_used': all(w['dmso_wells_used'] == w['dmso_wells_in_metadata'] for w in rows),
            'max_abs_difference_effect': float(f'{worst_effect:.3g}'), 'max_abs_difference_cells': float(f'{worst_cells:.3g}'),
            'dmso_wells_per_plate_min': min(w['dmso_wells_used'] for w in rows),
            'dmso_wells_per_plate_max': max(w['dmso_wells_used'] for w in rows),
            'wells': rows}


def same_dose(meta, E, cells, name, keep, check, full):
    """One perturbation again, on the wells and plates of the labs that assayed library compounds at 10 uM only.

    Everything is recomputed on those labs: the perturbation, the eight controls on the same plates (5 uM in every lab)
    and the DMSO noise on the same plates, in exactly the way the all-lab result is. A lab at another dose is reported
    beside it (left_out), never mixed in. full is the all-lab report block, read for the lower-dose lab's numbers."""
    m = (meta.compound == name).to_numpy()
    labs = sorted(l for l in set(meta.lab[m]) if dose_of(l) == DOSE_UM['default'])
    left = sorted(set(meta.lab[m]) - set(labs))
    at = meta.lab.isin(labs).to_numpy()
    sm, sE, sc = meta[at].reset_index(drop=True), E[at], cells[at]
    pm, pE, res, ref, noise = study(sm, sE, sc, name)
    _, _, r2, ref2, n2 = study(sm, sE, sc, name, keep=keep)
    # the same two numbers as read off the all-lab matrix: cosines between wells do not depend on which other wells are in
    M = full['result']['lab_by_lab']
    own = [M[l][l] for l in labs if M[l][l] is not None]
    oth = [M[a][b] for a in labs for b in labs if a < b and M[a][b] is not None]
    assert (res['own_lab'], res['other_labs']) == (r3(np.mean(own)), r3(np.mean(oth))), 'same-dose subset disagrees with the all-lab matrix'
    P = res['pairs']
    by_lab = {l: {k: v[k] for k in ('n_wells', 'n_plates', 'own_lab', 'own_lab_pairs', 'other_labs', 'cells_vs_dmso', 'size')}
              for l, v in res['by_lab'].items()}
    ratio = DOSE_UM['default'] / np.array([dose_of(l) for l in left]) if left else []
    full_by = full['result']['by_lab']
    wells = full['result']['wells']
    cells_range = lambda lab: [r3(min(w['cells_vs_dmso'] for w in wells if w['lab'] == lab)),
                               r3(max(w['cells_vs_dmso'] for w in wells if w['lab'] == lab))]
    left_out = {l: {'dose_um': dose_of(l), 'n_wells': full_by[l]['n_wells'], 'n_plates': full_by[l]['n_plates'],
                    'cells_vs_dmso': full_by[l]['cells_vs_dmso'], 'cells_vs_dmso_range_over_wells': cells_range(l),
                    'reason': f'{l} assayed library compounds, {name} among them, at {dose_of(l):g} uM; the other labs used '
                              f'{DOSE_UM["default"]:g} uM, {r:g} times more [7]. Side by side, a difference in dose would look like '
                              f'a difference between labs. Its positive controls were 5 uM, as in every lab.'}
                for l, r in zip(left, ratio)}
    all_labs = sorted(full_by)
    controls_cells = {l: {c: v['by_lab'][l]['cells_vs_dmso'] for c, v in full['controls_on_the_same_plates'].items() if l in v['by_lab']}
                      for l in all_labs}
    at_10 = [full_by[l]['cells_vs_dmso'] for l in labs]
    wells_10 = [w['cells_vs_dmso'] for w in wells if w['lab'] in labs]
    wells_low = [w['cells_vs_dmso'] for w in wells if w['lab'] in left]
    in_every_lab = [c for c in full['controls_on_the_same_plates'] if all(controls_cells[l].get(c) is not None for l in all_labs)]
    strongest = min(in_every_lab, key=lambda c: np.mean([controls_cells[l][c] for l in all_labs]))
    dose_check = {
        'what': f'share of cells left after {name}, against the same plate\'s DMSO wells, beside each lab\'s dose; descriptive only: '
                'one dose per lab, so dose and lab cannot be told apart for the lab at the lower dose',
        'by_lab': {l: {'dose_um': dose_of(l), 'n_wells': full_by[l]['n_wells'], 'cells_vs_dmso': full_by[l]['cells_vs_dmso'],
                       'cells_vs_dmso_range_over_wells': cells_range(l), 'size': full_by[l]['size'],
                       'times_dmso_noise': full['compared']['size_by_lab'][l]['times_noise'],
                       'controls_at_5_um_cells_vs_dmso_median': r3(np.median([v for v in controls_cells[l].values() if v is not None]))}
                   for l in all_labs},
        'at_10_um_cells_vs_dmso_min': r3(min(at_10)), 'at_10_um_cells_vs_dmso_max': r3(max(at_10)),
        'lower_dose_labs': left,
        'lower_dose_left_more_cells': bool(left) and all(full_by[l]['cells_vs_dmso'] > max(at_10) for l in left),
        'every_lower_dose_well_above_every_10_um_well': bool(wells_low) and min(wells_low) > max(wells_10),
        'controls_at_5_um_cells_vs_dmso': controls_cells,
        'strongest_control_at_5_um': {
            'compound': strongest, 'cells_vs_dmso_by_lab': {l: controls_cells[l][strongest] for l in all_labs},
            'how_chosen': 'of the controls on the plates of every lab, the one that left the fewest cells, mean over labs'},
        'controls_note': 'the eight positive controls were 5 uM in every lab, so their cells left are a same-dose reference for each lab\'s cells'}
    return {'labs': labs, 'own_lab': res['own_lab'], 'other_labs': res['other_labs'],
            'note': f'labs at {DOSE_UM["default"]:g} uM only: ' + ', '.join(f'{l} ({dose_of(l):g} uM)' for l in left) + ' left out',
            'dose_um': DOSE_UM['default'], 'n_labs': res['n_labs'], 'n_wells': res['n_wells'], 'n_plates': res['n_plates'],
            'labs_with_own_lab': res['labs_with_own_lab'], 'own_minus_other_where_both': res['own_minus_other_where_both'],
            'n_pairs_own': int(sum(P[l][l] for l in labs)),
            'n_pairs_other': int(sum(P[a][b] for a in labs for b in labs if a < b)),
            'by_lab': by_lab, 'lab_by_lab': res['lab_by_lab'], 'pairs': P,
            'controls_on_the_same_plates': ref,
            'noise_on_the_same_plates': noise,
            'compared': compare(name, res, ref, noise),
            'no_position': {'n_features': int(keep.sum()), 'own_lab': r2['own_lab'], 'other_labs': r2['other_labs'],
                            'controls_on_the_same_plates': {c: {'own_lab': v['own_lab'], 'other_labs': v['other_labs']} for c, v in ref2.items()},
                            'dmso_noise': {'own_lab': n2['own_lab'], 'other_labs': n2['other_labs']}},
            'untreated_on_each_plate': {**{k: v for k, v in check.items() if k != 'wells'},
                                        'every_well_own_plate_dmso': all(w['dmso_wells_all_on_this_plate'] and w['dmso_wells_used'] > 0
                                                                         for w in check['wells'] if w['lab'] in labs),
                                        'every_listed_dmso_well_used': all(w['dmso_wells_used'] == w['dmso_wells_in_metadata']
                                                                           for w in check['wells'] if w['lab'] in labs),
                                        'same_for_left_out_labs': all(w['dmso_wells_all_on_this_plate'] and w['dmso_wells_used'] > 0
                                                                      and w['dmso_wells_used'] == w['dmso_wells_in_metadata']
                                                                      for w in check['wells'] if w['lab'] in left),
                                        'wells': check['wells']},
            'left_out': left_out,
            'dose_check': dose_check}


def read_e8():
    rt = json.load(open('results/e8-redteam.json'))['all_features']['compounds']
    sd = json.load(open('results/e8-same-drug-different-answer.json'))['compounds']
    return {'what': 'plate-level effects (mean of about four wells of each control on a plate), every plate of '
                    'every lab; e8-redteam compares a plate with the mean of its own lab (which includes the plate) '
                    'and with the mean of the other labs; e8-same-drug gives mean cosine between pairs of plates',
            'compounds': {c: {'agreement_with_own_lab': rt[c]['agreement_with_own_lab'],
                              'agreement_with_other_labs': rt[c]['agreement_with_other_labs'],
                              'pairs_of_plates_same_lab': sd[c]['agreement_same_lab'],
                              'pairs_of_plates_different_labs': sd[c]['agreement_across_labs'],
                              'effect_size': rt[c]['effect_size']['mean'],
                              'n_plates': rt[c]['n_plates'], 'n_labs': rt[c]['n_labs']} for c in rt}}


def redteam_style(meta, E, name):
    """e8-redteam's agreement on the plates of one perturbation: a plate's effect against its own
    lab's mean (which includes it) and against the mean of the other labs' means. For a single
    well per plate the plate effect is the well; for the controls it is the plate mean."""
    m = (meta.compound == name).to_numpy()
    on = meta.plate.isin(set(meta.plate[m]))
    out = {}
    for c in [name, *POSCON.values()]:
        g = meta[on & (meta.compound == c)]
        eff = {p: E[h.index].mean(axis=0) for p, h in g.groupby('plate')}
        lab = g.groupby('plate').lab.first()
        lab_eff = {l: np.mean([v for p, v in eff.items() if lab[p] == l], axis=0) for l in lab.unique()}
        u = lambda v: v / np.linalg.norm(v)
        own = [u(v) @ u(lab_eff[lab[p]]) for p, v in eff.items()]
        other = [u(v) @ u(np.mean([e for l, e in lab_eff.items() if l != lab[p]], axis=0)) for p, v in eff.items()]
        out[c] = {'agreement_with_own_lab': r3(np.mean(own)), 'agreement_with_other_labs': r3(np.mean(other)),
                  'effect_size': round(float(np.mean([np.linalg.norm(v) for v in eff.values()])), 2)}
    return out


# ---------------------------------------------------------------- images

def well_rc(w):
    m = re.match(r'^([A-Z]+)(\d+)$', w)
    row = 0
    for ch in m.group(1):
        row = row * 26 + ord(ch) - 64
    return row, int(m.group(2))


def representative(meta_p, E_p):
    """Per lab: the well with the highest mean cosine with the lab's other wells (the only one, if alone)."""
    U = unit_rows(E_p)
    C = U @ U.T
    out = {}
    for lab, g in meta_p.groupby('lab'):
        i = g.index.to_numpy()
        score = [np.mean([C[k, j] for j in i if j != k]) if len(i) > 1 else 1.0 for k in i]
        best = sorted(zip(score, g.plate, i), key=lambda t: (-t[0], t[1]))[0]
        out[lab] = meta_p.loc[best[2]]
    return out


def second_channel(meta_p, E_p, features):
    """The channel, other than DNA, whose features carry the largest share of RSL3's effect, labs weighted equally."""
    ch = np.array([channel_of(f) for f in features])
    share = {c: [] for c in SECOND}
    for _, g in meta_p.groupby('lab'):
        v = E_p[g.index].mean(axis=0) ** 2
        for c in SECOND:
            share[c].append(float(v[ch == c].sum() / v.sum()))
    share = {c: round(float(np.mean(s)), 3) for c, s in share.items()}
    return max(share, key=share.get), share


def tiff(url):
    im = tifffile.imread(io.BytesIO(e15.fetch(e15.BUCKET + urllib.parse.quote(url.replace('s3://cellpainting-gallery/', ''))))).astype(np.float32)
    return im[0] if im.ndim == 3 else im


def typical_crop(im, side):
    """Top-left corner of the side-wide window, on a 5 x 5 grid over the field, whose share of bright (nuclear) pixels is nearest the
    whole field's, ties to the centre: a crop as crowded as its image (lab 11's centre crop held 23 nuclei where its count predicts about 37)."""
    med = np.percentile(im, 50); m = im > med + 0.25 * (im.max() - med); whole = m.mean()
    c = ((im.shape[0] - side) // 2, (im.shape[1] - side) // 2)
    grid = [(int(y), int(x)) for y in np.linspace(0, im.shape[0] - side, 5) for x in np.linspace(0, im.shape[1] - side, 5)]
    return min(grid, key=lambda p: (round(abs(m[p[0]:p[0] + side, p[1]:p[1] + side].mean() - whole), 4), abs(p[0] - c[0]) + abs(p[1] - c[1])))


def tile(im, window, um_per_px, path, at=None):
    lo, hi = window
    side = min(round(TILE_UM / um_per_px), *im.shape)
    y0, x0 = at or ((im.shape[0] - side) // 2, (im.shape[1] - side) // 2)
    x = np.clip((im[y0:y0 + side, x0:x0 + side] - lo) / max(hi - lo, 1), 0, 1)
    Image.fromarray((x * 255).astype(np.uint8)).resize((TILE_PX, TILE_PX), Image.LANCZOS).save(path, optimize=True)
    return {'crop_px': [int(x0), int(y0), int(side), int(side)], 'um': round(side * um_per_px, 1)}


def pull_tiles(rep, meta, channel):
    micro = pd.read_csv('metadata/microscope_config.csv').set_index('Metadata_Source')
    ASSETS.mkdir(parents=True, exist_ok=True)
    out = {}
    for lab, r in rep.items():
        ld = pd.read_csv(io.BytesIO(e15.fetch(e15.LOAD.format(s=lab, b=r.batch, p=r.plate))), dtype=str)
        sites = sorted(ld[ld.Metadata_Well == r.well].Metadata_Site, key=int)
        site = sites[len(sites) // 2]
        rr, rc = well_rc(r.well)
        dmso = meta[(meta.plate == r.plate) & (meta.compound == 'DMSO')]
        dmso = dmso[dmso.well.isin(set(ld[ld.Metadata_Site == site].Metadata_Well))]      # imaged at this site
        typical = dmso.cells.median()             # the untreated well shown is a typical one: its cell count nearest the plate's median,
        near = min(dmso.itertuples(), key=lambda d: (abs(d.cells - typical), np.hypot(well_rc(d.well)[0] - rr, well_rc(d.well)[1] - rc), d.well)).well
        um = float(micro.loc[lab, 'Metadata_Pixel_Size_Microns'])
        row = lambda w: ld[(ld.Metadata_Well == w) & (ld.Metadata_Site == site)].iloc[0]
        tag = lab
        info = {'plate': r.plate, 'batch': r.batch, 'well': r.well, 'site': site, 'n_sites': len(sites),
                'dmso_well': near, 'um_per_px': um, 'tile_um': TILE_UM, 'tile_px': TILE_PX,
                'microscope': micro.loc[lab, 'Metadata_Microscope_Name'], 'channels': {}}
        dna = {w: tiff(row(w)['URL_OrigDNA']) for w in (r.well, near)}
        side = min(round(TILE_UM / um), *dna[r.well].shape)
        at = {w: typical_crop(dna[w], side) for w in dna}            # one crop per well, the same for both of its channels
        for c in ('DNA', channel):
            a, b = tiff(row(r.well)[f'URL_Orig{c}']), tiff(row(near)[f'URL_Orig{c}'])
            window = [float(v) for v in np.percentile(b, WINDOW)]
            suffix = '' if c == 'DNA' else f'-{c}'
            fa, fb = ASSETS / f'e16-rsl3-{tag}{suffix}.png', ASSETS / f'e16-dmso-{tag}{suffix}.png'
            info['channels'][c] = {'rsl3': str(fa), 'dmso': str(fb), 'window_from_dmso': window, 'shape': list(a.shape),
                                   'rsl3_above_window_pct': round(100 * float((a > window[1]).mean()), 2),
                                   **tile(a, window, um, fa, at[r.well])}
            info['channels'][c]['dmso_crop_px'] = tile(b, window, um, fb, at[near])['crop_px']
        out[lab] = info
        print(f'  {lab} {r.plate} {r.well} site {site}, DMSO {near}', flush=True)
    return out


# ---------------------------------------------------------------- main

def main():
    w = wanted_wells()
    print(f'{w.Metadata_Plate.nunique()} plates hold RSL3 or erastin', flush=True)
    pull_plates(w)
    scale = field_scale()
    meta, Z, bad = load(scale)
    feats = np.array(scale['features'])
    dmso_or_poscon = meta.compound.isin(['DMSO', *POSCON.values()]).to_numpy()
    E, cells = effects(meta, Z, bad)

    report = {'question': 'many labs run the same reference perturbation; does it look the same in every lab?',
              'perturbations': {n: {'jcp': j, 'what': WHAT[n]} for j, n in PERTURBATIONS.items()},
              'settings': {'features': 'e8: the columns fd.load_poscon() keeps, z-scored on the field\'s DMSO wells',
                           'n_features': int(len(feats)), 'field_plates': scale['n_plates'],
                           'field_dmso_wells': scale['n_dmso_wells'],
                           'effect': 'one well minus the mean of its own plate\'s DMSO wells',
                           'noise': 'one DMSO well minus the mean of its plate\'s other DMSO wells',
                           'pairs': 'cosine between two single-well effects, never two wells of one plate',
                           'labs_weighted': 'equally: own lab and other labs are means over labs, not over pairs',
                           'non_finite_values': {'dmso_and_controls': int(bad[dmso_or_poscon].sum()),
                                                 'rsl3_and_erastin': int(bad[~dmso_or_poscon].sum()),
                                                 'handling': 'set to the plate\'s DMSO mean (no effect on that feature)'}},
              'e8_field': read_e8()}
    keep = np.array([not POSITION.search(f) for f in feats])
    studied = {}
    for name in PERTURBATIONS.values():
        pm, pE, res, ref, noise = study(meta, E, cells, name)
        studied[name] = (pm, pE)
        wells, C = per_well(pm, pE, cells[(meta.compound == name).to_numpy()])
        res['wells'] = wells
        res['cosine_matrix'] = {'order': [f'{r["lab"]} {r["plate"]} {r["well"]}' for r in wells], 'values': C}
        report[name] = {
            'result': res,
            'controls_on_the_same_plates': ref,
            'noise_on_the_same_plates': noise,
            'compared': compare(name, res, ref, noise),
            'e8_redteam_definition_on_these_plates': redteam_style(meta, E, name)}
        # the same summaries without position, count and bookkeeping features
        _, _, r2, ref2, n2 = study(meta, E, cells, name, keep=keep)
        report.setdefault('no_position', {'n_features': int(keep.sum())})[name] = {
            'own_lab': r2['own_lab'], 'other_labs': r2['other_labs'],
            'by_lab': {l: {k: v[k] for k in ('own_lab', 'other_labs', 'size')} for l, v in r2['by_lab'].items()},
            'controls_on_the_same_plates': {c: {'own_lab': v['own_lab'], 'other_labs': v['other_labs']} for c, v in ref2.items()},
            'dmso_noise': {'own_lab': n2['own_lab'], 'other_labs': n2['other_labs']}}

    # do the two ferroptosis inducers agree with each other?
    (rm, rE), (em, eE) = studied['RSL3'], studied['erastin']
    C = unit_rows(rE) @ unit_rows(eE).T
    same = rm.lab.to_numpy()[:, None] == em.lab.to_numpy()[None, :]
    report['rsl3_vs_erastin'] = {'same_lab_pairs': int(same.sum()), 'same_lab': r3(C[same].mean()) if same.any() else None,
                                 'labs_with_both': sorted(set(rm.lab) & set(em.lab)),
                                 'different_labs': r3(C[~same].mean()), 'different_lab_pairs': int((~same).sum())}

    channel, share = second_channel(rm, rE, feats)
    print(f'second channel: {channel} {share}', flush=True)
    report['images'] = {'second_channel': channel, 'share_of_rsl3_effect_by_channel': share,
                        'window': f'percentiles {WINDOW[0]} and {WINDOW[1]} of the DMSO well\'s image, per lab and channel',
                        'labs': pull_tiles(representative(rm, rE), meta, channel)}
    report['dose_um'] = {lab: dose_of(lab) for lab in sorted(set(meta.lab))}
    listed = w[w.Metadata_JCP2022 == DMSO].groupby('Metadata_Plate').size().to_dict()     # DMSO wells per plate in the well metadata
    check = untreated_on_each_plate(meta, Z, bad, E, cells, 'RSL3', listed)
    report['RSL3']['same_dose_only'] = same_dose(meta, E, cells, 'RSL3', keep, check, report['RSL3'])
    report['caveats'] = [
        'RSL3 is one well on each of 12 plates: 5 in source_7, 4 in source_9, 2 in source_5, 1 in source_11. '
        'Own-lab agreement rests on 10, 6 and 1 pairs of wells, and does not exist for source_11.',
        'Erastin is one well on each of 11 plates in six labs; only source_7 (5) and source_3 (2) have an own-lab value.',
        'In source_5 and source_7 every RSL3 well sits at one plate position on plates of one layout, so own-lab agreement can '
        'include a shared layout effect; the same-position DMSO pairs there are small (about 0.06 to 0.07). source_9 puts its four '
        'RSL3 wells at four positions, and its same-position DMSO pairs agree at about 0.36: position matters more there.',
        'source_7 ran its five RSL3 plates in five consecutive runs of one layout, and source_9 its four on one day: '
        'own-lab agreement there is agreement between repeats, close in time.',
        'source_9 uses 1536-well plates, with fewer cells per well, so its single wells are noisier for every compound.',
        'Single wells are noisier than e8\'s plate means; compare RSL3 with the controls on the same plates, '
        'not with e8\'s field numbers directly.',
        'The dose is JUMP\'s, not chosen for ferroptosis, and it is not the same everywhere: source_7 assayed library compounds at '
        '0.625 uM, every other site at 10 uM, while the positive controls were 5 uM at every site [7]. RSL3 left 75 to 87% of cells on all '
        'five source_7 plates, consistent with the 16-fold lower dose, while source_7\'s positive controls worked; dose and lab cannot be '
        'separated there. Erastin was weak in source_7 and also in source_15 at 10 uM. The per-well metadata does not record the dose.',
        'Specificity: across labs RSL3 is only a little more like RSL3 than like some other compounds (NVS-PAK1-1, erastin); dying cells '
        'look alike. The result is an example of the question, not a ferroptosis fingerprint.',
        'Cell counts are the repository\'s per-image estimate from the mean nuclei object index (field.COUNT), not a direct count.']
    json.dump(report, open('results/e16-same-perturbation.json', 'w'), indent=1)

    for name in PERTURBATIONS.values():
        r, c = report[name]['result'], report[name]['compared']
        print(f'\n{name}: {r["n_wells"]} wells, {r["n_labs"]} labs. own lab {r["own_lab"]}, other labs {r["other_labs"]}')
        for lab, v in r['by_lab'].items():
            s = c['size_by_lab'][lab]
            print(f'  {lab:10} n {v["n_wells"]}  own {v["own_lab"]}  other {v["other_labs"]}  size {v["size"]} '
                  f'({s["times_noise"]}x DMSO noise {s["dmso_noise_median"]}; controls median {s["controls_median"]})  cells {v["cells_vs_dmso"]}')
        print(f'  controls on the same plates: own {c["own_lab"]}, other {c["other_labs"]}')
    sd = report['RSL3']['same_dose_only']
    print(f'\nRSL3 at {sd["dose_um"]:g} uM only: {sd["n_wells"]} wells, {sd["n_plates"]} plates, {sd["labs"]}. '
          f'own lab {sd["own_lab"]} ({sd["n_pairs_own"]} pairs), other labs {sd["other_labs"]} ({sd["n_pairs_other"]} pairs)')
    for lab, v in sd['by_lab'].items():
        print(f'  {lab:10} n {v["n_wells"]}  own {v["own_lab"]}  other {v["other_labs"]}  cells {v["cells_vs_dmso"]}')
    print(f'  controls on the same plates: own {sd["compared"]["own_lab"]}, other {sd["compared"]["other_labs"]}')
    print(f'  left out: {sd["left_out"]}')
    print(f'  own-plate DMSO: {({k: v for k, v in sd["untreated_on_each_plate"].items() if k != "wells"})}')
    print('\nRSL3 vs erastin', report['rsl3_vs_erastin'])


if __name__ == '__main__':
    main()
