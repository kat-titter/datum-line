"""e8: does a lab's position change the answer it gets from the same drug?

This is the beam the pitch rests on. e1 shows control wells carry lab identity.
e8 asks whether that identity costs you a measurement.

JUMP runs the same eight positive controls in columns 1 and 24 of every compound
plate: AMG900, dexamethasone, FK-866, LY2109761, NVS-PAK1-1, quinidine, TC-S-7004
and aloxistatin (perturbation_control.csv). So for every plate we can compute the
measured effect of a fixed compound, the way any lab would:

    delta_p,c  =  mean(x | plate p, compound c)  -  mean(x | plate p, DMSO)

That is treated minus control, on the same plate, which is exactly what a screen
reports. Then three questions, in order of how much they matter:

  Q1  Does delta agree across labs?
      Cosine similarity between each plate's delta and the field's mean delta for
      that compound, grouped by source. Also the same-lab baseline: cosine between
      two plates within one lab. If within-lab agreement is high and across-lab
      agreement is lower, the same drug reads differently by lab.

  Q2  Does the disagreement track how far the lab's CONTROLS sit from the field?
      For each plate: d_ctrl = || mean(DMSO | plate) - mean(DMSO | field) || in
      units of the field's control spread (the certificate's own distance), and
      d_effect = 1 - cos(delta_p,c, delta_field,c). Correlate the two across plates
      (Spearman, and a per-compound breakdown). A positive correlation is the
      claim: the further your controls sit, the more your answer moves.

  Q3  Is the effect big enough to matter?
      Express the across-lab spread of delta as a fraction of the mean effect size
      || delta ||, per compound. "The same compound, measured X% differently
      depending on the building" is the sentence for the slide.

Guardrails, because this result would carry the pitch:
  - plate-level aggregation only; no well is used twice
  - z-scoring is fit on the FIELD's DMSO wells, never on the plate being judged
  - compounds are analysed separately, then pooled; no averaging over compounds
    with different mechanisms before the per-compound numbers are reported
  - a null: shuffle plate labels within lab and recompute Q2's correlation
  - if Q1 shows no across-lab disagreement, say so on the slide and drop the claim;
    that outcome is publishable too and it is better found now than on stage

Scope, checked against JUMP metadata on 23 Sep 2026:
  1,829 compound plates carry both the eight positive controls and DMSO,
  across 11 sources and 129 batches (source_3 237 plates, source_6 209,
  source_2 208, source_10 205, source_5 197, source_8 195, source_11 167,
  source_15 146, source_7 115, source_9 99, source_1 51). Every compound is
  present on at least 1,730 of them. That is 144,279 wells of profiles: about
  32 poscon and 32 DMSO wells per plate. Pull those wells only.

Usage: python e8_same_drug_different_answer.py PROFILES.parquet METADATA_DIR
       PROFILES.parquet needs well-level profiles for DMSO and poscon wells with
       Metadata_Source, Metadata_Plate, Metadata_Well, Metadata_JCP2022.
Writes: results/e8-same-drug-different-answer.json and results/e8-points.csv
"""
import sys, json, itertools, numpy as np, pandas as pd
from scipy.stats import spearmanr

PROF, META = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'metadata')
DMSO = 'JCP2022_033924'
POSCON = {'JCP2022_037716': 'AMG900', 'JCP2022_025848': 'dexamethasone', 'JCP2022_046054': 'FK-866',
          'JCP2022_035095': 'LY2109761', 'JCP2022_064022': 'NVS-PAK1-1', 'JCP2022_050797': 'quinidine',
          'JCP2022_012818': 'TC-S-7004', 'JCP2022_085227': 'aloxistatin'}

d = pd.read_parquet(PROF)
for c in ('Metadata_Source', 'Metadata_Plate', 'Metadata_JCP2022'):
    d[c] = d[c].astype(str)
feats = [c for c in d.columns if not c.startswith('Metadata_')]
# a few CellProfiler features overflow on some plates; a non-finite or absurd value would
# dominate every cosine, so those columns are dropped for everyone, label-free
X = d[feats].apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan)
keep = X.notna().all() & (X.std() > 0) & (X.abs().max() < 1e6)
X = X.loc[:, keep]; feats = list(X.columns)

def unit(v):
    n = np.linalg.norm(v)
    return v / n if n else v

out = {'n_wells': int(len(d)), 'n_plates': int(d.Metadata_Plate.nunique()),
       'n_sources': int(d.Metadata_Source.nunique()), 'n_features': len(feats), 'compounds': {}}

# field-level scaling: fit on DMSO wells only, so nothing is scaled by the thing being judged
dm = d.Metadata_JCP2022 == DMSO
mu, sd = X[dm].mean(), X[dm].std().replace(0, np.nan)
Z = ((X - mu) / sd).fillna(0.0)
d = d.assign(**{'_i': np.arange(len(d))})

# per-plate DMSO centroid and its distance from the field's DMSO centroid
plate_ctrl, ctrl_dist = {}, {}
field_ctrl = Z[dm.values].mean().values
spread = np.linalg.norm(Z[dm.values].values - field_ctrl, axis=1).mean()
for p, g in d[dm].groupby('Metadata_Plate'):
    v = Z.iloc[g._i.values].mean().values
    plate_ctrl[p] = v
    ctrl_dist[p] = float(np.linalg.norm(v - field_ctrl) / spread)

rows = []
for jcp, name in POSCON.items():
    sel = d.Metadata_JCP2022 == jcp
    deltas, src_of = {}, {}
    for p, g in d[sel].groupby('Metadata_Plate'):
        if p not in plate_ctrl:
            continue
        deltas[p] = Z.iloc[g._i.values].mean().values - plate_ctrl[p]
        src_of[p] = g.Metadata_Source.iloc[0]
    if len(deltas) < 6:
        continue
    field = np.mean(list(deltas.values()), axis=0)
    cos = {p: float(unit(v) @ unit(field)) for p, v in deltas.items()}
    within, across = [], []
    for a, b in itertools.combinations(deltas, 2):
        c = float(unit(deltas[a]) @ unit(deltas[b]))
        (within if src_of[a] == src_of[b] else across).append(c)
    per_src = pd.Series({p: cos[p] for p in cos}).groupby(pd.Series(src_of)).mean().round(3)
    x = [ctrl_dist[p] for p in deltas]; y = [1 - cos[p] for p in deltas]
    rho, pval = spearmanr(x, y)
    mags = [float(np.linalg.norm(v)) for v in deltas.values()]
    out['compounds'][name] = {
        'n_plates': len(deltas), 'n_sources': len(set(src_of.values())),
        'mean_effect_size': round(float(np.mean(mags)), 2),
        'agreement_same_lab': round(float(np.mean(within)), 3) if within else None,
        'agreement_across_labs': round(float(np.mean(across)), 3),
        'cosine_to_field_by_source': per_src.to_dict(),
        'spearman_controls_vs_effect': [round(float(rho), 3), float(pval)],
        'effect_spread_pct_of_effect': round(100 * float(np.std(mags) / np.mean(mags)), 1)}
    rows += [(name, ctrl_dist[p], 1 - cos[p], src_of[p]) for p in deltas]

if rows:
    df = pd.DataFrame(rows, columns=['compound', 'control_distance', 'effect_disagreement', 'source'])
    rho, pval = spearmanr(df.control_distance, df.effect_disagreement)
    rng = np.random.default_rng(0)
    null = []
    for _ in range(200):
        sh = df.groupby('source').control_distance.transform(lambda s: rng.permutation(s.values))
        null.append(spearmanr(sh, df.effect_disagreement).statistic)
    out['pooled'] = {'n_points': len(df), 'spearman': round(float(rho), 3), 'p': float(pval),
                     'null_mean': round(float(np.mean(null)), 3), 'null_95pct': round(float(np.percentile(null, 95)), 3)}
    df.to_csv('results/e8-points.csv', index=False)

json.dump(out, open('results/e8-same-drug-different-answer.json', 'w'), indent=2)
print(json.dumps(out, indent=2)[:3000])
