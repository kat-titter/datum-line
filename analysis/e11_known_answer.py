"""e11: did the known answer come out? A positive-control check, batch by batch.

A positive control is a compound whose effect is known. For every batch of every lab this
reports, per compound, the size of the measured effect and its agreement with the field's,
and marks a batch FAILED when the compounds the field agrees on show no effect there:
mean agreement below e10.FAIL and mean effect size below a quarter of the lab's own median.
The rule is defined once, in e10.

For a failed batch it then asks where the effect went. Whole plates are downloaded and
every well is compared with the field's effect of the strongest control. If the compound
had been dispensed into other wells than the plate map says, some well would show it.
One plate from a batch that came out is probed the same way, as a check on the method.

Untreated wells cannot see this failure. It is the second half of a certificate.

Usage:  python analysis/e11_known_answer.py [--probe N]     (whole plates per failed batch, default 2)
Needs:  cache/poscon/, results/e10-certificate-predicts-answer.json, metadata/
Writes: results/e11-known-answer.json
"""
import argparse
import io
import json
import urllib.request

import numpy as np
import pandas as pd

import e10_certificate_predicts_answer as e10
import e8_pull_wells as pull
import field as fd

STRONGEST = 'AMG900'
LOOKS_LIKE = 0.6        # cosine with the field's effect
NAMES = {**e10.POSCON, e10.DMSO: 'DMSO'}


def field_effect(eff, judged):
    """The field's effect of each compound: lab means, averaged over every lab but the judged one."""
    out = {}
    for c in e10.POSCON.values():
        labs = {}
        for (s, b, cc), v in eff.items():
            if cc == c and s != judged:
                labs.setdefault(s, []).append(v)
        out[c] = np.mean([np.mean(v, axis=0) for v in labs.values()], axis=0)
    return out


def check(lab, eff, n_plates, fieldv, order, dates, pooled):
    rows = []
    for k, b in enumerate(order):
        per = {c: {'size': float(np.linalg.norm(eff[(lab, b, c)])),
                   'agreement': float(e10.unit(eff[(lab, b, c)]) @ e10.unit(fieldv[c]))}
               for c in e10.POSCON.values() if (lab, b, c) in eff}
        use = [c for c in pooled if c in per]
        rows.append({'batch': b, 'run': k + 1, 'date': str(dates[b].date()) if dates[b] is not None else None,
                     'n_plates': int(max(n_plates[(lab, b, c)] for c in per)) if per else 0,
                     'agreement': round(float(np.mean([per[c]['agreement'] for c in use])), 3) if use else None,
                     'size': round(float(np.mean([per[c]['size'] for c in use])), 2) if use else None,
                     'by_compound': {c: {k2: round(v2, 2) for k2, v2 in v.items()} for c, v in per.items()}})
    median = float(np.median([r['size'] for r in rows if r['size'] is not None]))
    for r in rows:
        r['verdict'] = ('no positive controls' if r['size'] is None else
                        'failed' if r['agreement'] < e10.FAIL and r['size'] < e10.FAIL_SIZE * median else 'came out')
    return rows, median


def probe(lab, batch, plate, verdict, columns, mu, sd, target, plate_map):
    """Every well of one plate against the field's effect of the strongest control."""
    raw = urllib.request.urlopen(pull.URL.format(s=lab, b=batch, p=plate), timeout=180).read()
    d = pd.read_parquet(io.BytesIO(raw))
    W = d[columns].apply(pd.to_numeric, errors='coerce').to_numpy('float32')
    Z = np.nan_to_num(np.clip((W - mu) / sd, -fd.CLIP, fd.CLIP))
    label = d.Metadata_Well.map(plate_map)
    dmso = (label == e10.DMSO).to_numpy()
    E = Z - Z[dmso].mean(axis=0)
    size = np.linalg.norm(E, axis=1)
    cos = (E @ e10.unit(target)) / np.maximum(size, 1e-9)
    floor = float(np.percentile(size[dmso], 99))
    hits = (cos > LOOKS_LIKE) & (size > floor)
    jcp = next(k for k, v in e10.POSCON.items() if v == STRONGEST)
    labelled = (label == jcp).to_numpy()
    return {'lab': lab, 'batch': batch, 'batch_verdict': verdict, 'plate': plate, 'n_wells': int(len(d)),
            'compound': STRONGEST, 'wells_the_map_says_hold_it': sorted(d.Metadata_Well[labelled]),
            'their_agreement_with_the_field': [round(float(v), 2) for v in cos[labelled]],
            'their_size_over_the_dmso_99th_percentile': [round(float(v / floor), 2) for v in size[labelled]],
            'wells_that_look_like_it': sorted(d.Metadata_Well[hits]),
            'what_the_map_says_those_hold': sorted({NAMES.get(x, 'a library compound') for x in label[hits]})}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--probe', type=int, default=2)
    a = ap.parse_args()
    pooled = json.load(open('results/e10-certificate-predicts-answer.json'))['compounds_pooled']
    meta, X, columns = e10.load()
    wells = pd.read_csv('metadata/well.csv.gz', dtype=str)
    out = {'rule': f'failed when mean agreement with the field is below {e10.FAIL} and mean effect size is below a '
                   'quarter of the lab\'s own median, over the compounds the field agrees on',
           'compounds': pooled, 'n_plates': int(meta.Metadata_Plate.nunique()), 'labs': {}, 'failed': [], 'probe': []}

    for lab in sorted(meta.Metadata_Source.unique()):
        eff, n_plates = e10.batch_effects(meta, X, lab)
        fieldv = field_effect(eff, lab)
        order, dates = fd.ordered_batches(meta[meta.Metadata_Source == lab].Metadata_Batch)
        rows, median = check(lab, eff, n_plates, fieldv, order, dates, pooled)
        out['labs'][lab] = {'median_size': round(median, 2), 'batches': rows}
        failed = [r for r in rows if r['verdict'] == 'failed']
        out['failed'] += [{'lab': lab, 'batch': r['batch'], 'run': r['run'], 'n_plates': r['n_plates'],
                           'agreement': r['agreement'], 'size': r['size'], 'lab_median_size': round(median, 2)} for r in failed]
        print(f"{lab:10} " + ''.join('X' if r['verdict'] == 'failed' else '-' if r['size'] is None else '.' for r in rows), flush=True)
        if not failed or not a.probe:
            continue
        mu, sd, ok = e10.scale(meta, X, lab)
        cols = [c for c, k in zip(columns, ok) if k]
        good = next(r for r in rows if r['verdict'] == 'came out')
        for r, n in [(good, 1)] + [(f, a.probe) for f in failed]:
            here = meta[(meta.Metadata_Source == lab) & (meta.Metadata_Batch == r['batch'])]
            for plate in sorted(here.Metadata_Plate.unique())[:n]:
                plate_map = wells[wells.Metadata_Plate == plate].set_index('Metadata_Well').Metadata_JCP2022
                p = probe(lab, r['batch'], plate, r['verdict'], cols, mu[ok], sd[ok], fieldv[STRONGEST], plate_map)
                out['probe'].append(p)
                print(f"   {r['batch']:20} {plate:12} {r['verdict']:9} labelled {p['wells_the_map_says_hold_it']} "
                      f"agree {p['their_agreement_with_the_field']} | look-alikes {p['wells_that_look_like_it'][:10]} "
                      f"{p['what_the_map_says_those_hold']}", flush=True)
    json.dump(out, open('results/e11-known-answer.json', 'w'), indent=1)
    print(len(out['failed']), 'failed batches,', sum(f['n_plates'] for f in out['failed']), 'plates:',
          [(f['lab'], f['batch']) for f in out['failed']])


if __name__ == '__main__':
    main()
