"""e18: one strong positive control, seen in every lab. The median cell before and after AMG900.

Slide 05 asks how shared data separates a drug's real effect from each lab's noise. AMG900 (JCP2022_037716, an Aurora
kinase inhibitor) is JUMP's strongest positive control (e11); cells that cannot divide grow large nuclei. For every lab:

  wells    one compound plate from each of up to three batches whose known answer came out (e11), in batch order, from
           the plates e15 imaged: one AMG900 well and the DMSO well e15 used; site 1; DNA (Hoechst) and AGP (actin, Golgi,
           plasma membrane), the 16-bit originals
  nuclei   Gaussian blur (1 px), Otsu threshold, connected components; kept if 20 to 1,500 square microns and clear of
           the field's edge; pixel size from metadata/microscope_config.csv
  cells    each nucleus seeds its cell: the AGP foreground (smoothed, above halfway from background to Otsu) is split
           among the nuclei by a watershed, so each cell body is the foreground nearest its nucleus
  median   the lab's median cell: the whole cell, clear of the field's edge and smaller than the window, whose nuclear
           area is closest to the lab's median for that condition; cropped at 90 x 90 microns around the cell's centre,
           resampled to 192 x 192 (0.47 microns a pixel), everything outside that one cell set to black. (A pixel-wise
           median of all crops was tried first: the cell bodies blur into an even wash.)
  display  one scale for every lab and both conditions: after each field's 1st-percentile background is taken off, DNA is
           divided by 1.8 times the lab's median nuclear DNA intensity and AGP by 2.5 times its median cytoplasm AGP
           intensity, both measured on its DMSO cells, then drawn as the cell body in green with the nucleus laid over it
           in pink (the deck's colours: pink a point, green the field around it)
  size     median nuclear area per lab and condition, and its ratio, AMG900 over DMSO

Raw size differs from lab to lab (microscope, stain, cell density): noise. The ratio, each lab against its own DMSO, is
the drug's shared change: the signal.

Usage:  python analysis/e18_median_cell.py      resumable; about 600 MB of downloads into cache/e18
Needs:  metadata/well.csv.gz, metadata/plate.csv.gz, metadata/microscope_config.csv, cache/images/*/*/meta.json (e15),
        results/e11-known-answer.json
Writes: results/e18-median-cell.json, figures/assets/median-cell/{source}-{dmso,amg900}.png
"""
import concurrent.futures as cf
import io
import json
import sys
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
from PIL import Image
from scipy import ndimage
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.segmentation import watershed

sys.path.insert(0, str(Path(__file__).parent))
from e15_pull_images import BUCKET, LOAD, fetch  # noqa: E402

AMG900, DMSO = 'JCP2022_037716', 'JCP2022_033924'
CACHE, ASSETS = Path('cache/e18'), Path('figures/assets/median-cell')
PLATES, WIN_UM, SIDE = 3, 90.0, 192      # 192 px: crisp at 02b's size, downscaled elsewhere
PINK, GREEN = np.array([239, 116, 173]) / 255, np.array([63, 224, 160]) / 255      # the deck's dark-slide pink and green


def plates():
    """Per lab, one plate e15 imaged (holding an AMG900 well) from each of the first PLATES batches whose known answer came out."""
    w = pd.read_csv('metadata/well.csv.gz', dtype=str)
    amg = w[w.Metadata_JCP2022 == AMG900].groupby('Metadata_Plate')['Metadata_Well'].apply(sorted).to_dict()
    e11 = json.load(open('results/e11-known-answer.json'))['labs']
    good = {(s, b['batch']) for s, v in e11.items() for b in v['batches'] if b['verdict'] == 'came out'}
    out = []
    for meta in sorted(Path('cache/images').glob('*/*/meta.json')):
        m = json.loads(meta.read_text())
        if m['plate'] in amg and (m['source'], m['batch']) in good:
            out.append(dict(m, amg900=amg[m['plate']][0]))
    df = pd.DataFrame(out).sort_values(['source', 'batch', 'plate']).groupby(['source', 'batch']).head(1)
    return df.groupby('source').head(PLATES)


def field(row, well, channel='DNA'):
    """One channel of one well, site 1 (or its first site), cached as the original TIFF."""
    path = CACHE / row.source / (f'{row.plate}-{well}.tif' if channel == 'DNA' else f'{row.plate}-{well}-{channel}.tif')
    if not path.exists():
        ld = pd.read_csv(io.BytesIO(fetch(LOAD.format(s=row.source, b=row.batch, p=row.plate))), dtype=str)
        here = ld[ld.Metadata_Well == well]
        r = here.sort_values('Metadata_Site', key=lambda s: s.astype(int)).iloc[0]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(fetch(BUCKET + urllib.parse.quote(r[f'URL_Orig{channel}'].replace('s3://cellpainting-gallery/', ''))))
    im = tifffile.imread(path).astype(np.float32)
    return im[0] if im.ndim == 3 else im


def cells(dna, agp, um):
    """Every nucleus's area (for the numbers), and each whole cell clear of the field's edge (for the picture): its crop in both
    channels, background taken off, with masks of the cell and its nucleus, and its nuclear DNA and cytoplasm AGP intensity."""
    sd = ndimage.gaussian_filter(dna, 1)
    nuc = label(sd > threshold_otsu(sd))
    sa = ndimage.gaussian_filter(agp, 2)
    bd, ba = np.percentile(dna, 1), np.percentile(agp, 1)
    fg = (sa > ba + 0.5 * (threshold_otsu(sa) - ba)) | (nuc > 0)
    cell = watershed(np.zeros_like(sa), markers=nuc, mask=fg)
    H, W = dna.shape
    half = WIN_UM / 2 / um
    areas, recs = [], []
    for p in regionprops(nuc):
        a = p.area * um * um
        y, x = p.centroid
        if not 20 <= a <= 1500 or y < half or x < half or y > H - half or x > W - half:
            continue
        areas.append(a)
        mine = cell == p.label
        ys, xs = np.nonzero(mine)
        if ys.min() == 0 or xs.min() == 0 or ys.max() == H - 1 or xs.max() == W - 1:
            continue
        if (ys.max() - ys.min()) * um > WIN_UM or (xs.max() - xs.min()) * um > WIN_UM:
            continue
        cy, cx = ys.mean(), xs.mean()
        if not (half <= cy <= H - half and half <= cx <= W - half):
            continue
        n = nuc == p.label
        cyto = mine & ~n
        sl = (slice(int(cy - half), int(cy + half)), slice(int(cx - half), int(cx + half)))
        recs.append({'area': a, 'nuc': float((dna[n] - bd).mean()), 'cyto': float((agp[cyto] - ba).mean()) if cyto.any() else 0.0,
                     'crop': (dna[sl] - bd, agp[sl] - ba, mine[sl])})
    return areas, recs


def draw(rec, nuc_s, cyt_s):
    """One cell alone, on black: cell body green, nucleus pink laid over it, at the lab's one scale."""
    d, a, m = rec['crop']
    size = lambda x, how: np.asarray(Image.fromarray(x).resize((SIDE, SIDE), how))
    d, a = size(d.astype(np.float32), Image.BILINEAR), size(a.astype(np.float32), Image.BILINEAR)
    m = size(m.astype(np.uint8) * 255, Image.NEAREST) > 127
    dna = np.clip(d / (1.8 * nuc_s), 0, 1) * m
    body = np.clip(a / (2.5 * cyt_s), 0, 1) ** 0.8 * m
    rgb = body[..., None] * GREEN * (1 - dna[..., None]) + dna[..., None] * PINK
    return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))


def main():
    px = (pd.read_csv('metadata/microscope_config.csv').drop_duplicates('Metadata_Source')
          .set_index('Metadata_Source').Metadata_Pixel_Size_Microns.to_dict())
    rows = list(plates().itertuples())
    print(f'{len(rows)} plates, {len({r.source for r in rows})} labs, {2 * len(rows)} fields', flush=True)
    with cf.ThreadPoolExecutor(8) as ex:      # downloads first, in parallel
        jobs = [ex.submit(field, r, w, c) for r in rows for w in (r.well, r.amg900) for c in ('DNA', 'AGP')]
        for k, j in enumerate(cf.as_completed(jobs), 1):
            j.result()
            if k % 10 == 0:
                print(f'  {k}/{len(jobs)} fields', flush=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    out = {'compound': 'AMG900', 'jcp': AMG900, 'dose_um': 5, 'window_um': WIN_UM, 'side_px': SIDE, 'labs': {}}      # 5 uM: JUMP [7], JUMP-Target's recommended dose
    for src in sorted({r.source for r in rows}, key=lambda s: int(s.split('_')[1])):
        mine = [r for r in rows if r.source == src]
        um = float(px[src])
        got = {'dmso': [cells(field(r, r.well), field(r, r.well, 'AGP'), um) for r in mine],
               'amg900': [cells(field(r, r.amg900), field(r, r.amg900, 'AGP'), um) for r in mine]}
        areas = {c: [x for a_s, _ in v for x in a_s] for c, v in got.items()}
        recs = {c: [x for _, rs in v for x in rs] for c, v in got.items()}
        if min(len(recs['dmso']), len(recs['amg900'])) < 5:
            print(f'{src}: too few whole cells, skipped', flush=True)
            continue
        nuc_s, cyt_s = float(np.median([r['nuc'] for r in recs['dmso']])), float(np.median([r['cyto'] for r in recs['dmso']]))
        shown = {}
        for c in recs:
            med = float(np.median(areas[c]))
            best = min(recs[c], key=lambda r: abs(r['area'] - med))          # the median cell, by nuclear area
            draw(best, nuc_s, cyt_s).save(ASSETS / f'{src}-{c}.png', optimize=True)
            shown[c] = round(best['area'], 1)
        a0, a1 = float(np.median(areas['dmso'])), float(np.median(areas['amg900']))
        out['labs'][src] = {'plates': [r.plate for r in mine], 'batches': [r.batch for r in mine], 'wells': {'dmso': [r.well for r in mine], 'amg900': [r.amg900 for r in mine]},
                            'pixel_um': um, 'n_nuclei': {c: len(v) for c, v in areas.items()}, 'n_whole_cells': {c: len(v) for c, v in recs.items()},
                            'shown_nuclear_area_um2': shown,
                            'median_area_um2': {'dmso': round(a0, 1), 'amg900': round(a1, 1)}, 'ratio': round(a1 / a0, 2)}
        print(f'{src}: {len(areas["dmso"])} / {len(areas["amg900"])} nuclei, {a0:.0f} -> {a1:.0f} um2, x{a1 / a0:.2f}', flush=True)
    r = [v['ratio'] for v in out['labs'].values()]; d = [v['median_area_um2']['dmso'] for v in out['labs'].values()]
    out['summary'] = {'n_labs': len(r), 'ratio_mean': float(np.mean(r)), 'ratio_median': float(np.median(r)), 'ratio_range': [min(r), max(r)],
                      'dmso_area_range_um2': [min(d), max(d)],
                      'cv_dmso_area': float(np.std(d) / np.mean(d)), 'cv_ratio': float(np.std(r) / np.mean(r))}
    Path('results/e18-median-cell.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out['summary']), flush=True)


if __name__ == '__main__':
    main()
