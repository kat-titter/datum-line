"""Shared loading and geometry for the analyses that place a lab's plates in the field.

The rule that matters, stated once: the lab being judged never sets its own scale.
Features are z-scored on the wells of every OTHER lab, clipped, and distances are
expressed in units of the field's mean within-plate spread.
"""
import re

import numpy as np
import pandas as pd

import e1_lab_classifier as e1

CLIP = 5.0
COUNT = 'Nuclei_Number_Object_Number'   # mean object index per image: (n + 1) / 2 for n nuclei
_DATE = re.compile(r'(20\d{2})[_-]?(\d{2})[_-]?(\d{2})')
_SHORT_DATE = re.compile(r'^p(\d{2})(\d{2})(\d{2})')


def load():
    """Untreated wells of every cached plate, sorted so each plate's wells are contiguous."""
    d = e1.load_wells()
    # one source_11 profile names its plate 'EC000157real', which the metadata does not know;
    # a plate without a batch cannot be placed in run order, so it is left out
    unplaced = d.Metadata_Batch.isna()
    if unplaced.any():
        print(f'left out {d[unplaced].Metadata_Plate.nunique()} plate(s) with no batch in the metadata: '
              f'{sorted(d[unplaced].Metadata_Plate.unique())}', flush=True)
        d = d[~unplaced]
    d = d.sort_values(['Metadata_Source', 'Metadata_Plate', 'Metadata_Well']).reset_index(drop=True)
    X = e1.feature_matrix(d)
    X = X.loc[:, np.isfinite(X.to_numpy()).all(axis=0)]
    return d, X


def batch_date(name):
    """The date a batch name carries, or None."""
    m = _SHORT_DATE.search(name)
    if m:
        return pd.Timestamp(f'20{m.group(1)}-{m.group(2)}-{m.group(3)}')
    m = _DATE.search(name)
    try:
        return pd.Timestamp(f'{m.group(1)}-{m.group(2)}-{m.group(3)}') if m else None
    except ValueError:
        return None


def ordered_batches(names):
    """Batches in run order: by date when every name carries one, else by run number."""
    names = sorted(set(names))
    dates = {n: batch_date(n) for n in names}
    if all(v is not None for v in dates.values()):
        return sorted(names, key=lambda n: (dates[n], n)), dates
    # the first number in the name is the run: CP_25_all_Phenix1 is run 25, not run 1
    number = lambda n: int(re.findall(r'\d+', n)[0]) if re.findall(r'\d+', n) else 0
    return sorted(names, key=lambda n: (number(n), n)), {n: None for n in names}


class Field:
    """Plate centroids in a space scaled on the reference labs only."""

    def __init__(self, d, X, judged_lab, clip=CLIP, drop_labs=(), keep=None):
        lab = d.Metadata_Source.to_numpy()
        cols = np.ones(X.shape[1], bool) if keep is None else np.asarray(keep)
        Xv = X.to_numpy()[:, cols] if keep is not None else X.to_numpy()
        ref = (lab != judged_lab) & ~np.isin(lab, list(drop_labs))
        mu, sd = Xv[ref].mean(axis=0), Xv[ref].std(axis=0)
        ok = sd > 0
        Z = (Xv[:, ok] - mu[ok]) / sd[ok]
        if clip:
            np.clip(Z, -clip, clip, out=Z)

        plate = d.Metadata_Plate.to_numpy()
        starts = np.flatnonzero(np.r_[True, plate[1:] != plate[:-1]])
        counts = np.diff(np.r_[starts, len(plate)])
        self.plates = plate[starts]
        self.cent = np.add.reduceat(Z, starts, axis=0) / counts[:, None]
        self.lab = lab[starts]
        self.batch = d.Metadata_Batch.to_numpy()[starts]
        self.n_wells = counts
        self.n_features = int(ok.sum())
        self.features = np.array(X.columns)[cols][ok]
        self.dropped = set(drop_labs)
        self.judged = judged_lab
        in_ref = ref[starts]
        spread = [np.linalg.norm(Z[s:s + n] - self.cent[k], axis=1).mean()
                  for k, (s, n) in enumerate(zip(starts, counts)) if in_ref[k]]
        self.spread = float(np.mean(spread))
        cells = 2 * pd.to_numeric(d[COUNT], errors='coerce').to_numpy() - 1
        self.cells = np.add.reduceat(np.nan_to_num(cells), starts) / counts
        self.ref_labs = sorted(set(self.lab[in_ref]))
        self.lab_centre = {l: self.cent[self.lab == l].mean(axis=0) for l in self.ref_labs}

    def of(self, lab, batch=None):
        m = self.lab == lab
        return np.flatnonzero(m if batch is None else m & (self.batch == batch))

    def distance(self, rows, point):
        return np.linalg.norm(self.cent[rows] - point, axis=1) / self.spread

    def to_nearest_lab(self, rows, exclude=()):
        labs = [l for l in self.ref_labs if l not in exclude]
        D = np.stack([self.distance(rows, self.lab_centre[l]) for l in labs], axis=1)
        return D.min(axis=1), np.array(labs)[D.argmin(axis=1)]
