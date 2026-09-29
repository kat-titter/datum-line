"""Pull six real JUMP control-well tiles for the "which lab?" game (slide 04).

Three sites from plate 1053600681 (source_2) and three from an all-vehicle plate at a
second source (default: the first source_5 plate in data/jump_all_vehicle_plates.csv).
DNA channel only, one centre crop per site, contrast matched across all six by shared
percentiles, and placed in a FIXED order so the reveal board's labels are already right:

    positions 1, 4, 5  = source_2 (pink on the reveal)
    positions 2, 3, 6  = the other source (green on the reveal)

Needs: awscli (aws s3 cp --no-sign-request), numpy, pandas, tifffile, scikit-image.
Usage: python pull_game_tiles.py [other_plate] [other_source]
Writes: game/tile-1.png ... game/tile-6.png and game/key.json
"""
import sys, os, json, subprocess, io, random
import numpy as np, pandas as pd, tifffile
from skimage.transform import resize
from skimage.io import imsave

BUCKET = 's3://cellpainting-gallery/cpg0016-jump'
A = ('source_2', '20210614_Batch_1', '1053600681')
other = pd.read_csv('data/jump_all_vehicle_plates.csv')
o = other[other.Metadata_Source == (sys.argv[2] if len(sys.argv) > 2 else 'source_5')].iloc[0]
B = (o.Metadata_Source, o.Metadata_Batch, str(sys.argv[1] if len(sys.argv) > 1 else o.Metadata_Plate))

def s3(path, dst):
    subprocess.run(['aws', 's3', 'cp', '--no-sign-request', path, dst], check=True, capture_output=True)

def load_data(src, batch, plate):
    dst = f'game/{plate}_load_data.csv.gz'
    s3(f'{BUCKET}/{src}/workspace/load_data_csv/{batch}/{plate}/load_data.csv.gz', dst)
    return pd.read_csv(dst)

def dna_sites(src, batch, plate, n=3, seed=7):
    ld = load_data(src, batch, plate)
    # interior wells only, so no edge effects are in the game
    ld = ld[ld.Metadata_Well.str.match(r'^[C-N](0[4-9]|1[0-9]|2[01])$')]
    rows = ld.sample(n=n, random_state=seed)
    imgs = []
    for _, r in rows.iterrows():
        p = r['PathName_OrigDNA'].replace('s3://cellpainting-gallery/', 's3://cellpainting-gallery/') .rstrip('/') + '/' + r['FileName_OrigDNA']
        dst = f'game/{plate}_{r.Metadata_Well}_{r.Metadata_Site}.tiff'
        s3(p, dst)
        im = tifffile.imread(dst).astype(np.float32)
        h, w = im.shape[:2]; c = min(h, w) // 2; cy, cx = h // 2, w // 2
        imgs.append(im[cy - c // 2: cy + c // 2, cx - c // 2: cx + c // 2])
    return imgs

os.makedirs('game', exist_ok=True)
a = dna_sites(*A); b = dna_sites(*B)
allpix = np.concatenate([x.ravel() for x in a + b])
lo, hi = np.percentile(allpix, [1, 99.7])          # one contrast window for all six
def tile(im):
    x = np.clip((im - lo) / (hi - lo), 0, 1)
    return (resize(x, (512, 512), anti_aliasing=True) * 255).astype(np.uint8)
order = {1: ('A', 0), 4: ('A', 1), 5: ('A', 2), 2: ('B', 0), 3: ('B', 1), 6: ('B', 2)}
key = {}
for pos, (which, i) in order.items():
    im = (a if which == 'A' else b)[i]
    imsave(f'game/tile-{pos}.png', tile(im))
    key[pos] = A[0] if which == 'A' else B[0]
json.dump({'positions': key, 'plates': {'A': A, 'B': B}, 'contrast_window': [float(lo), float(hi)]}, open('game/key.json', 'w'), indent=2)
print(json.dumps(key, indent=2))
