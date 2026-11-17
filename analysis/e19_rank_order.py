"""e19: do labs rank the same drugs in the same order by nuclear area?

Kat, 17 Nov 2026: "rank order of drugs that increase nuclei area as therapeutic/bioactive phenotype would be different w/o
shared data repo". A claim to test. The eight JUMP positive controls sit on every compound plate of every lab at one dose
(5 uM, JUMP methods [7]), four wells each beside the plate's DMSO wells, so every lab ranks the same drugs.

Effect     per plate: log2( mean nuclear area of a compound's wells / mean nuclear area of the plate's DMSO wells ),
           from each lab's own released CellProfiler profile (Nuclei_AreaShape_Area, pixels); per lab: median over plates
Raw        the same without the control: log2 of the compound wells' mean nuclear area in pixels
Same set   only compounds every lab ran; every lab, every plate that holds DMSO and the compound
Q1         each lab ranks the drugs; Spearman between every pair of labs (within a lab the order is the same raw or as a
           ratio: dividing by one plate's DMSO moves every drug on it alike)
Ceiling    the same lab against itself: its plates dealt into two halves, Spearman between the halves' orders
Chance     drug labels shuffled inside each lab: the median pair Spearman that luck gives
Q2         the pooled list, as a shared repository or a model meets it: each drug measured in a different lab, one list.
           Spearman of that list against the order the other labs give (the measuring lab left out), for
             raw pixels | ratio to own DMSO | shared frame: the ratio rescaled by how strongly that lab answers the
             other shared drugs, against the other labs (gain through the origin, the ranked drug left out)
Usage:  python analysis/e19_rank_order.py        Needs: cache/poscon/ (e8_pull_wells.py)
"""
import glob
import itertools
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

DMSO = 'JCP2022_033924'
POSCON = {'JCP2022_037716': 'AMG900', 'JCP2022_025848': 'dexamethasone', 'JCP2022_046054': 'FK-866',
          'JCP2022_035095': 'LY2109761', 'JCP2022_064022': 'NVS-PAK1-1', 'JCP2022_050797': 'quinidine',
          'JCP2022_012818': 'TC-S-7004', 'JCP2022_085227': 'aloxistatin'}      # the mapping e8 asserts against JUMP's compound table
AREA = 'Nuclei_AreaShape_Area'
COLS = ['Metadata_Source', 'Metadata_Plate', 'Metadata_JCP2022', AREA]
rng = np.random.default_rng(19)
rho = lambda a, b: float(spearmanr(a, b).statistic)

d = pd.concat([pd.read_parquet(f, columns=COLS) for f in sorted(glob.glob('cache/poscon/*/*.parquet'))], ignore_index=True)
d = d[np.isfinite(d[AREA]) & (d[AREA] > 0)]
d['Metadata_Plate'] = d.Metadata_Plate.astype(str)
plate = d.groupby(['Metadata_Source', 'Metadata_Plate', 'Metadata_JCP2022'])[AREA].mean().unstack()
plate = plate[plate[DMSO].notna()]
fc = np.log2(plate[list(POSCON)].div(plate[DMSO], axis=0)).rename(columns=POSCON)        # plate x drug, log2 ratio to own DMSO
raw = np.log2(plate[list(POSCON)]).rename(columns=POSCON)                                # plate x drug, log2 pixels
labs = sorted(fc.index.get_level_values(0).unique(), key=lambda s: int(s.split('_')[1]))
lab_fc = fc.groupby(level=0).median().loc[labs]
lab_raw = raw.groupby(level=0).median().loc[labs]
n_plates = fc.notna().groupby(level=0).sum().loc[labs]
drugs = [c for c in lab_fc.columns if lab_fc[c].notna().all() and (n_plates[c] >= 3).all()]      # same drugs for every lab
F, R = lab_fc[drugs].to_numpy(), lab_raw[drugs].to_numpy()
L, C = F.shape

# Q1: lab against lab
pairs = list(itertools.combinations(range(L), 2))
pair_rho = np.array([rho(F[i], F[j]) for i, j in pairs])
null = np.array([np.median([rho(P[i], P[j]) for i, j in pairs])
                 for P in (np.array([rng.permutation(row) for row in F]) for _ in range(2000))])
order = lambda v: [drugs[k] for k in np.argsort(-v)]
top = [order(F[i])[0] for i in range(L)]
rest = [k for k, c in enumerate(drugs) if c != 'AMG900']
pair_rho_rest = np.array([rho(F[i][rest], F[j][rest]) for i, j in pairs])

# ceiling: a lab against itself, plates dealt into halves
half = []
for lab in labs:
    X = fc.loc[lab][drugs].dropna().to_numpy()
    r = []
    for _ in range(200):
        idx = rng.permutation(len(X)); a, b = X[idx[:len(X) // 2]], X[idx[len(X) // 2:]]
        r.append((rho(np.median(a, 0), np.median(b, 0)), rho(np.median(a, 0)[rest], np.median(b, 0)[rest])))
    half.append(np.median(r, axis=0))
half = np.array(half)

# Q2: one list, each drug from a different lab
def pooled(n=5000):
    out = {'raw pixels': [], 'ratio to own DMSO': [], 'shared frame': []}
    for _ in range(n):
        who = rng.choice(L, size=C, replace=False)
        ref = np.array([np.median(np.delete(F[:, k], who[k])) for k in range(C)])       # the order the other labs give
        cal = []
        for k in range(C):
            others = [j for j in range(C) if j != k]
            m = np.median(np.delete(F[:, others], who[k], axis=0), axis=0)               # the field's answer to the other shared drugs
            g = float(F[who[k], others] @ m / (m @ m))                                    # how strongly this lab answers them
            cal.append(F[who[k], k] / g)
        out['raw pixels'].append(rho(R[who, range(C)], ref))
        out['ratio to own DMSO'].append(rho(F[who, range(C)], ref))
        out['shared frame'].append(rho(np.array(cal), ref))
    return {k: {'median': round(float(np.median(v)), 3), 'p05': round(float(np.percentile(v, 5)), 3), 'p95': round(float(np.percentile(v, 95)), 3),
                'share_top_drug_right': round(float(np.mean(v)), 3) if False else None} for k, v in out.items()}, out

q2, q2_all = pooled()
for k in q2: q2[k].pop('share_top_drug_right')
gain = [float(F[i] @ np.median(np.delete(F, i, 0), 0) / (np.median(np.delete(F, i, 0), 0) @ np.median(np.delete(F, i, 0), 0))) for i in range(L)]

# the same wells the deck shows (results/e18: one analysis of every lab's images, median nucleus) against each lab's own released profile
e18 = json.load(open('results/e18-median-cell.json'))['labs']
wells = pd.concat([pd.read_parquet(f, columns=COLS + ['Metadata_Well']) for f in sorted(glob.glob('cache/poscon/*/*.parquet'))], ignore_index=True)
wells['Metadata_Plate'] = wells.Metadata_Plate.astype(str)
wells = wells.set_index(['Metadata_Source', 'Metadata_Plate', 'Metadata_Well'])
same = {}
for lab in labs:
    v = e18[lab]; r = []
    for p_, wd, wa in zip(v['plates'], v['wells']['dmso'], v['wells']['amg900']):
        a, b = wells.loc[(lab, p_, wa)], wells.loc[(lab, p_, wd)]
        assert a.Metadata_JCP2022 == 'JCP2022_037716' and b.Metadata_JCP2022 == DMSO, (lab, p_)
        r.append(float(a[AREA] / b[AREA]))
    same[lab] = {'images_one_analysis': v['ratio'], 'released_profile': round(float(np.mean(r)), 2)}

res = {
    'question': 'do labs rank the same drugs in the same order by nuclear area, and does a shared frame change that?',
    'settings': {'feature': AREA, 'dose_um': 5, 'drugs': drugs, 'left_out': sorted(set(POSCON.values()) - set(drugs)), 'n_labs': L,
                 'n_plates': int(len(fc)), 'n_wells': int(len(d)), 'effect': 'per plate log2(compound / own DMSO), per lab the median over plates',
                 'chance': 'drug labels shuffled inside each lab, 2,000 draws', 'seed': 19},
    'fold_change_by_lab': {lab: {c: round(float(2 ** lab_fc.loc[lab, c]), 3) for c in drugs} for lab in labs},
    'plates_by_lab': {lab: int(n_plates.loc[lab, drugs].min()) for lab in labs},
    'order_by_lab': {lab: order(F[i]) for i, lab in enumerate(labs)},
    'q1_lab_against_lab': {'n_pairs': len(pairs), 'spearman_median': round(float(np.median(pair_rho)), 3), 'spearman_min': round(float(pair_rho.min()), 3),
                           'spearman_max': round(float(pair_rho.max()), 3), 'chance_median': round(float(np.median(null)), 3),
                           'chance_95pct': round(float(np.percentile(null, 95)), 3), 'labs_with_AMG900_first': int(sum(t == 'AMG900' for t in top)),
                           'without_AMG900': {'spearman_median': round(float(np.median(pair_rho_rest)), 3), 'spearman_min': round(float(pair_rho_rest.min()), 3),
                                              'spearman_max': round(float(pair_rho_rest.max()), 3)}},
    'ceiling_same_lab_split_half': {'spearman_median_over_labs': round(float(np.median(half[:, 0])), 3), 'spearman_min_over_labs': round(float(half[:, 0].min()), 3),
                                    'without_AMG900_median_over_labs': round(float(np.median(half[:, 1])), 3)},
    'amg900': {'fold_change_min': round(float(2 ** lab_fc['AMG900'].min()), 2), 'fold_change_max': round(float(2 ** lab_fc['AMG900'].max()), 2),
               'fold_change_median': round(float(2 ** lab_fc['AMG900'].median()), 2)},
    'q2_one_list_each_drug_from_a_different_lab': {'n_lists': 5000, 'reference': 'the order the other labs give, the measuring lab left out', **q2,
                                                   'shared_beats_ratio_share': round(float(np.mean(np.array(q2_all['shared frame']) > np.array(q2_all['ratio to own DMSO']))), 3),
                                                   'ratio_beats_shared_share': round(float(np.mean(np.array(q2_all['shared frame']) < np.array(q2_all['ratio to own DMSO']))), 3)},
    'same_wells_as_e18': {'what': 'AMG900 over DMSO, nuclear area, on the three plates and wells per lab that slide 05 shows', 'labs': same},
    'lab_gain_against_the_field': {lab: round(g, 3) for lab, g in zip(labs, gain)},
}
json.dump(res, open('results/e19-rank-order.json', 'w'), indent=1)
show = pd.DataFrame(res['fold_change_by_lab']).T
print(show.round(2).to_string()); print()
for k in ('same_wells_as_e18', 'q1_lab_against_lab', 'ceiling_same_lab_split_half', 'amg900', 'q2_one_list_each_drug_from_a_different_lab', 'lab_gain_against_the_field', 'plates_by_lab'):
    print(k, json.dumps(res[k]))
print('left out:', res['settings']['left_out'], '| plates', res['settings']['n_plates'], 'wells', res['settings']['n_wells'])
