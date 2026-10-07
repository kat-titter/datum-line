"""e15, part 2: can an off-the-shelf image model place a raw control image on the map?

The map in this deck runs on CellProfiler profiles. The box on slide 01 promises an image.
This asks whether a frozen, general-purpose vision model (DINOv2, ViT-S/14, no training on
cells) gives an embedding from one field of one untreated well that

  names the lab        a logistic regression on the embedding, whole batches held out,
                       balanced accuracy against chance of one in eleven (e1 did this on profiles)
  agrees with the map  the nearest other lab by image is the nearest other lab by profile (e9)
  sees the drift       lab 2's batches, distance from its own first batch by image against
                       the same distance by profile (e9), Spearman

Three inputs are tried: the DNA channel alone, a composite of DNA, AGP and Mito as RGB, and
brightfield where the lab kept one. The judged lab never sets its own scale: embeddings are
z-scored on the other labs before any distance is taken.

Usage:  python analysis/e15_image_model.py
Needs:  cache/images/ (e15_pull_images.py), results/e9-replay.json
Writes: results/e15-image-model.json, results/e15-embeddings-{dna,rgb,brightfield}.parquet
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import timm
import torch
from PIL import Image
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

import field as fd

MODEL = 'vit_small_patch14_dinov2.lvd142m'
INPUTS = {'dna': ['DNA'], 'rgb': ['DNA', 'AGP', 'Mito'], 'brightfield': ['Brightfield']}
SEED = 0


def load_image(folder, channels):
    ims = []
    for c in channels:
        f = folder / f'{c}.png'
        if not f.exists():
            return None
        ims.append(np.asarray(Image.open(f).convert('L').resize((518, 518), Image.BILINEAR), dtype=np.float32) / 255)
    x = np.stack(ims if len(ims) == 3 else ims * 3, axis=0)
    return x


def embed(model, device, folders, channels):
    mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
    sd = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)
    out, keep = [], []
    batch = []
    for k, f in enumerate(folders):
        x = load_image(f, channels)
        if x is None:
            continue
        batch.append(x); keep.append(k)
        if len(batch) == 16 or k == len(folders) - 1:
            with torch.no_grad():
                t = (torch.tensor(np.stack(batch), device=device) - mean) / sd
                out.append(model(t).float().cpu().numpy())
            batch = []
    if batch:
        with torch.no_grad():
            t = (torch.tensor(np.stack(batch), device=device) - mean) / sd
            out.append(model(t).float().cpu().numpy())
    return np.concatenate(out), np.array(keep)


def name_the_lab(E, lab, batch, rng):
    """Whole batches held out; labs with fewer than three batches are dealt round-robin like e1."""
    folds = np.zeros(len(E), int)
    for l in np.unique(lab):
        bs = np.unique(batch[lab == l]); rng.shuffle(bs)
        for i, b in enumerate(bs):
            folds[(lab == l) & (batch == b)] = i % 5
    pred = np.empty(len(E), dtype=object)
    for k in range(5):
        tr, te = folds != k, folds == k
        sc = StandardScaler().fit(E[tr])
        clf = LogisticRegression(max_iter=2000, C=0.5).fit(sc.transform(E[tr]), lab[tr])
        pred[te] = clf.predict(sc.transform(E[te]))
    return balanced_accuracy_score(lab, pred), pred


def nearest_by_image(E, lab, batch, judged):
    """For each batch of the judged lab: nearest other lab, in a space scaled on the other labs."""
    ref = lab != judged
    mu, sd = E[ref].mean(axis=0), E[ref].std(axis=0) + 1e-9
    Z = (E - mu) / sd
    centres = {l: Z[lab == l].mean(axis=0) for l in np.unique(lab[ref])}
    out = {}
    for b in np.unique(batch[lab == judged]):
        c = Z[(lab == judged) & (batch == b)].mean(axis=0)
        out[b] = min(centres, key=lambda l: np.linalg.norm(c - centres[l]))
    return out, Z


def main():
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    model = timm.create_model(MODEL, pretrained=True, num_classes=0).eval().to(device)
    metas = sorted(Path('cache/images').glob('*/*/meta.json'))
    meta = pd.DataFrame([json.load(open(m)) for m in metas])
    folders = [m.parent for m in metas]
    replay = json.load(open('results/e9-replay.json'))['labs']
    rng = np.random.default_rng(SEED)
    out = {'model': MODEL, 'n_plates': int(len(meta)), 'n_labs': int(meta.source.nunique()), 'inputs': {}}
    for name, channels in INPUTS.items():
        E, keep = embed(model, device, folders, channels)
        m = meta.iloc[keep].reset_index(drop=True)
        lab, batch = m.source.to_numpy(), m.batch.to_numpy()
        if len(np.unique(lab)) < 3:
            out['inputs'][name] = {'n_plates': int(len(E)), 'n_labs': int(len(np.unique(lab))), 'note': 'too few labs keep this channel'}
            continue
        acc, pred = name_the_lab(E, lab, batch, rng)
        chance = 1 / len(np.unique(lab))
        # agreement with the profile map on the nearest other lab, batch by batch, for every lab in the replay
        agree, n = 0, 0
        for judged in sorted(set(lab) & set(replay)):
            near, _ = nearest_by_image(E, lab, batch, judged)
            for b in replay[judged]['batches']:
                if b['batch'] in near:
                    n += 1; agree += near[b['batch']] == b['nearest_other']
        # lab 2's drift, by image against by profile
        drift = None
        if 'source_2' in set(lab):
            _, Z = nearest_by_image(E, lab, batch, 'source_2')
            B = replay['source_2']['batches']
            first = Z[(lab == 'source_2') & (batch == B[0]['batch'])].mean(axis=0)
            spread = np.mean([np.linalg.norm(Z[(lab == l)] - Z[lab == l].mean(axis=0), axis=1).mean() for l in np.unique(lab) if l != 'source_2'])
            by_image = [float(np.linalg.norm(Z[(lab == 'source_2') & (batch == b['batch'])].mean(axis=0) - first) / spread) for b in B if (batch == b['batch']).any()]
            by_profile = [b['from_baseline'] for b in B if (batch == b['batch']).any()]
            drift = {'spearman': round(float(spearmanr(by_image, by_profile).statistic), 3), 'n_batches': len(by_image),
                     'by_image': [round(v, 2) for v in by_image], 'by_profile': by_profile}
        out['inputs'][name] = {'n_plates': int(len(E)), 'n_labs': int(len(np.unique(lab))), 'balanced_accuracy': round(float(acc), 4), 'chance': round(chance, 4),
                               'nearest_lab_agrees_with_profiles': f'{agree} of {n}', 'lab_2_drift': drift}
        print(name, json.dumps(out['inputs'][name])[:300], flush=True)
        pd.DataFrame(E, columns=[f'e{i}' for i in range(E.shape[1])]).assign(source=lab, batch=batch, plate=m.plate.to_numpy()).to_parquet(f'results/e15-embeddings-{name}.parquet', index=False)
    json.dump(out, open('results/e15-image-model.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
