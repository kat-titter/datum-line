"""e1 vote: how the held-out e1 classifier votes on one plate's DMSO wells.

Reads results/e1-predictions.csv (out-of-fold, from e1_lab_classifier.py). Refits nothing.
For the target plate and two comparison sets at the same lab:
  - the other all-vehicle plates at that lab (every well DMSO)
  - the DMSO wells of ordinary compound plates in the target plate's batch
reports predicted-lab counts, unanimity, the top two, mean p(own lab) and the mean margin
between the top prediction and the own lab.

Usage:  python analysis/e1_vote.py [PLATE]          (default 1053600681)
Writes: results/e1-vote-PLATE.json, results/e1-vote-PLATE.csv
"""
import sys, json
import numpy as np, pandas as pd


def vote(w, own):
    """Vote summary for a set of wells."""
    pcols = [c for c in w.columns if c.startswith('p_')]
    counts = w['predicted'].value_counts()
    top = counts.index[0]
    shares = [{'lab': k, 'wells': int(v), 'share': round(v / len(w), 4)} for k, v in counts.items()]
    p_top = w[pcols].max(axis=1)
    return {'n_wells': int(len(w)),
            'votes': shares,
            'unanimous': bool(len(counts) == 1),
            'top_two': shares[:2],
            'majority': top,
            'majority_is_own_lab': bool(top == own),
            'wells_named_own_lab': int((w['predicted'] == own).sum()),
            'mean_p_own_lab': round(float(w[f'p_{own}'].mean()), 4),
            'mean_margin_top_minus_own': round(float((p_top - w[f'p_{own}']).mean()), 4)}


def per_plate(w, own):
    rows = []
    for plate, g in w.groupby('Metadata_Plate'):
        v = vote(g, own)
        rows.append({'plate': plate, 'batch': g['Metadata_Batch'].iloc[0], 'n_wells': v['n_wells'],
                     'majority': v['majority'], 'majority_share': v['votes'][0]['share'],
                     'unanimous': v['unanimous'], 'wells_named_own_lab': v['wells_named_own_lab'],
                     'mean_p_own_lab': v['mean_p_own_lab']})
    return sorted(rows, key=lambda r: r['plate'])


def main():
    plate = sys.argv[1] if len(sys.argv) > 1 else '1053600681'
    d = pd.read_csv('results/e1-predictions.csv', dtype={'Metadata_Plate': str})
    e1 = json.load(open('results/e1.json'))
    target = d[d.Metadata_Plate == plate]
    assert len(target), f'plate {plate} not in the e1 predictions'
    own, batch = target.Metadata_Source.iloc[0], target.Metadata_Batch.iloc[0]
    lab = d[d.Metadata_Source == own]

    # Held out: GroupKFold puts each plate in exactly one test fold, and trains that fold on
    # every other fold, so one fold per plate means the plate never trained its own model.
    folds_per_plate = d.groupby('Metadata_Plate')['fold'].nunique()
    assert (folds_per_plate == 1).all(), 'a plate was split across folds'

    vehicle = lab[lab.Metadata_AllVehicle & (lab.Metadata_Plate != plate)]
    ordinary = lab[~lab.Metadata_AllVehicle & (lab.Metadata_Batch == batch)]
    lab_plates = per_plate(lab, own)
    out = {
        'plate': plate, 'lab': own, 'batch': batch,
        'source': 'results/e1-predictions.csv (out-of-fold); settings in results/e1.json',
        'held_out': {'fold': int(target['fold'].iloc[0]), 'plate_in_one_fold_only': True,
                     'note': 'GroupKFold by plate: the model that scored these wells never saw this plate'},
        'target': vote(target, own),
        'other_all_vehicle_plates_same_lab': {'pooled': vote(vehicle, own) if len(vehicle) else None,
                                              'per_plate': per_plate(vehicle, own)},
        'ordinary_compound_plates_same_batch_dmso': {'pooled': vote(ordinary, own) if len(ordinary) else None,
                                                     'per_plate': per_plate(ordinary, own)},
        'lab_plates_in_e1': {'n_plates': len(lab_plates),
                             'majority_other_lab': sum(not r['majority'] == own for r in lab_plates),
                             'plates_majority_other_lab': [r for r in lab_plates if r['majority'] != own]},
        'model_per_class_recall': e1['all_sources']['per_class_recall'],
        'model_predicted_share': e1['all_sources']['predicted_share'],
        'model_true_share': e1['all_sources']['true_share'],
    }
    json.dump(out, open(f'results/e1-vote-{plate}.json', 'w'), indent=2)
    target.drop(columns=['Metadata_AllVehicle']).to_csv(f'results/e1-vote-{plate}.csv', index=False)
    t = out['target']
    print(f"{plate}: {t['n_wells']} wells; " + ', '.join(f"{v['lab']} {v['wells']}" for v in t['votes']))


if __name__ == '__main__':
    main()
