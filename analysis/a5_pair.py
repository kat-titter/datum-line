"""a5: two labs, one cell count. Does the image still tell them apart?

Board A5 says a cell count and an image ask one question two ways: the count moves only when
cells die or divide, the image moves when anything changes. This checks the claim on two labs
whose microscopes match (source_5 and source_6: both CV8000, confocal, NA 0.75, the same DNA
filters, 0.65 um pixels), using the untreated field e15_pull_images.py kept for every plate.

For every plate, on the DNA channel (the 8-bit PNG, 512 px on the long side):
  count    nuclei: Otsu threshold, connected components (skimage.measure.label), then
           components under 50 um^2 dropped. Touching nuclei count as one, so the count is a
           floor, and it is a floor the same way for both labs. One field, not a whole well.
  texture  the share of in-nucleus signal finer than 5 um, in percent. The image is split by
           FFT at 0.2 cycles/um; the high band's squared intensity, summed inside the nuclear
           mask, over the image's squared intensity summed there. The cutoff is in microns, so
           each lab's own pixel size sets it in pixels, and the band stops at the coarser lab's
           Nyquist, so both labs are measured over the same frequencies.

Each lab's representative is the plate nearest its own median count and median texture,
distance in units of that lab's interquartile range. Spread is pooled across the two labs as
the interquartile range of every plate's distance from its own lab's median.
  count_close      the representatives' counts differ by less than the pooled count IQR
  texture_differs  their textures differ by more than the pooled texture IQR
The same two checks are repeated on the lab medians, on every cross-lab pair of plates, at
other cutoffs and with the nuclear edge eroded away, so the answer does not rest on one pair
or one threshold. The high band of the background, outside any nucleus, is reported as a
noise floor. Each representative is drawn as a 300 um square of its field, 256 px, at the
field's own nuclear density (see tile()).

Usage:  python analysis/a5_pair.py
Needs:  cache/images/source_5/, cache/images/source_6/ (e15_pull_images.py), metadata/microscope_config.csv
Writes: results/a5-pair.json, figures/assets/a5-lab5.png, figures/assets/a5-lab6.png
"""
import concurrent.futures as cf
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.morphology import binary_dilation, binary_erosion, disk

LABS = {'lab_5': 'source_5', 'lab_6': 'source_6'}
IMAGES = Path('cache/images')
ASSETS = Path('figures/assets')
MIN_AREA_UM2 = 50          # a U2OS nucleus here is about 250 um^2
CUT = 0.2                  # cycles per um: detail finer than 5 um
CUTS = [0.1, 0.15, 0.2, 0.25, 0.3]
TILE_UM, TILE_PX = 300, 256


def png_um_per_px(lab, meta, png_side, micro):
    """Microns per pixel of the stored PNG: the microscope's pixel, scaled by the resize."""
    return float(micro.loc[lab, 'Metadata_Pixel_Size_Microns']) * max(meta['channels']['DNA']['shape']) / png_side


def nuclei(I, um):
    """Otsu, label, drop small components: the label image and which labels are nuclei."""
    lab = label(I > threshold_otsu(I))
    keep = np.bincount(lab.ravel()) >= MIN_AREA_UM2 / um ** 2
    keep[0] = False
    return lab, keep


def measure(plate_dir, micro, top):
    meta = json.loads((plate_dir / 'meta.json').read_text())
    I = np.asarray(Image.open(plate_dir / 'DNA.png'), dtype=np.float64) / 255
    um = png_um_per_px(meta['source'], meta, max(I.shape), micro)
    lab, keep = nuclei(I, um)
    mask = keep[lab]
    # texture: share of squared intensity inside nuclei that sits above the cutoff
    F = np.fft.fft2(I)
    f = np.hypot(*np.meshgrid(np.fft.fftfreq(I.shape[0], um), np.fft.fftfreq(I.shape[1], um), indexing='ij'))
    high = lambda cut: np.real(np.fft.ifft2(F * ((f > cut) & (f <= top))))
    share = lambda H, m: 100 * float((H[m] ** 2).sum() / (I[m] ** 2).sum())
    H = high(CUT)
    inner = binary_erosion(mask, disk(1))
    background = ~binary_dilation(mask, disk(3))
    row = {'lab': meta['source'], 'plate': meta['plate'], 'batch': meta['batch'], 'well': meta['well'], 'site': meta['site'],
           'um_per_px': um, 'count': int(keep.sum()), 'texture': share(H, mask),
           'texture_inner': share(H, inner),
           'noise_floor': 100 * float((H[background] ** 2).mean() / (I[mask] ** 2).mean())}
    row.update({f'texture_{c}': share(high(c), mask) for c in CUTS})
    return row


def iqr(x):
    q1, q3 = np.percentile(x, [25, 75])
    return float(q3 - q1)


def pooled_iqr(d, col):
    """Interquartile range of every plate's distance from its own lab's median, both labs together."""
    return iqr(np.concatenate([g[col].to_numpy() - g[col].median() for _, g in d.groupby('lab')]))


def checks(d, col_count, col_tex):
    """count_close and texture_differs on the medians and on every cross-lab pair of plates."""
    a, b = (d[d.lab == s] for s in LABS.values())
    pc, pt = pooled_iqr(d, col_count), pooled_iqr(d, col_tex)
    dc = np.abs(a[col_count].to_numpy()[:, None] - b[col_count].to_numpy()[None, :])
    dt = b[col_tex].to_numpy()[None, :] - a[col_tex].to_numpy()[:, None]
    return {'pooled_iqr': round(pt, 4),
            'median_lab_5': round(float(a[col_tex].median()), 4), 'median_lab_6': round(float(b[col_tex].median()), 4),
            'medians_count_close': bool(abs(a[col_count].median() - b[col_count].median()) < pc),
            'medians_texture_differ': bool(abs(a[col_tex].median() - b[col_tex].median()) > pt),
            'pairs_count_close': round(float((dc < pc).mean()), 3),
            'pairs_texture_differs': round(float((np.abs(dt) > pt).mean()), 3),
            'pairs_both': round(float(((dc < pc) & (np.abs(dt) > pt)).mean()), 3),
            'pairs_lab_6_higher': round(float((dt > 0).mean()), 3)}


def tile(plate_dir, um, out):
    """A square of the field, TILE_UM across, resized to TILE_PX, at the field's own density.

    Cells are not spread evenly, so the exact centre can look sparse or crowded next to the
    field's count. The tile is the square nearest the centre whose nucleus count is within
    10% of the field's count scaled to its area; the centre itself when it already is.
    """
    im = Image.open(plate_dir / 'DNA.png')
    I = np.asarray(im, dtype=np.float64) / 255
    lab, keep = nuclei(I, um)
    cy, cx = (np.array(c) for c in zip(*[p.centroid for p in regionprops(lab) if keep[p.label]]))
    side = round(TILE_UM / um)
    expected = len(cy) * side * side / I.size
    inside = lambda x0, y0: int(((cx >= x0) & (cx < x0 + side) & (cy >= y0) & (cy < y0 + side)).sum())
    c0 = ((im.width - side) // 2, (im.height - side) // 2)
    grid = [(x0, y0) for x0 in range(0, im.width - side + 1, 4) for y0 in range(0, im.height - side + 1, 4)] + [c0]
    near = lambda p: np.hypot(p[0] - c0[0], p[1] - c0[1])
    ok = [p for p in grid if abs(inside(*p) - expected) <= 0.1 * expected]
    x0, y0 = min(ok, key=near) if ok else min(grid, key=lambda p: (abs(inside(*p) - expected), near(p)))
    im.crop((x0, y0, x0 + side, y0 + side)).resize((TILE_PX, TILE_PX), Image.LANCZOS).save(out, optimize=True)
    return {'crop_png_px': [int(x0), int(y0), side, side], 'nuclei_in_tile': inside(x0, y0),
            'nuclei_expected': round(float(expected), 1), 'nuclei_in_centre_square': inside(*c0)}


def main():
    micro = pd.read_csv('metadata/microscope_config.csv').set_index('Metadata_Source')
    dirs = [p for s in LABS.values() for p in sorted((IMAGES / s).iterdir()) if (p / 'DNA.png').exists() and (p / 'meta.json').exists()]
    # one frequency band for both labs: up to the Nyquist of the coarser PNG pixel
    top = min(0.5 / png_um_per_px(m['source'], m, max(Image.open(p / 'DNA.png').size), micro)
              for p in dirs for m in [json.loads((p / 'meta.json').read_text())])
    with cf.ThreadPoolExecutor(8) as ex:
        d = pd.DataFrame(list(ex.map(lambda p: measure(p, micro, top), dirs)))
    print(f'{len(d)} plates: ' + ', '.join(f'{s} {int((d.lab == s).sum())}' for s in LABS.values()), flush=True)

    out = {'question': 'two labs, one cell count: does the image still tell them apart?',
           'channel': 'DNA', 'texture_unit': 'percent of squared intensity inside nuclei above the cutoff',
           'cutoff_cycles_per_um': CUT, 'band_top_cycles_per_um': round(top, 4), 'min_nucleus_um2': MIN_AREA_UM2}
    rep = {}
    for key, s in LABS.items():
        g = d[d.lab == s]
        cm, ci, tm, ti = float(g['count'].median()), iqr(g['count']), float(g.texture.median()), iqr(g.texture)
        r = g.loc[np.hypot((g['count'] - cm) / ci, (g.texture - tm) / ti).idxmin()]
        rep[key] = r
        m = micro.loc[s]
        out[key] = {'source': s, 'plate': r.plate, 'batch': r.batch, 'well': r.well, 'site': r.site,
                    'count': int(r['count']), 'texture': round(float(r.texture), 4),
                    'count_median': cm, 'count_iqr': ci, 'texture_median': round(tm, 4), 'texture_iqr': round(ti, 4),
                    'n_plates': int(len(g)), 'wells': {k: int(v) for k, v in g.well.value_counts().items()},
                    'microscope': f"{m.Metadata_Microscope_Name}, {m.Metadata_Widefield_vs_Confocal.lower()}, NA {m.Metadata_Objective_NA}",
                    'um_per_px_png': round(float(r.um_per_px), 4),
                    'tile': {'file': f'figures/assets/a5-{key.replace("_", "")}.png', 'um': TILE_UM, 'px': TILE_PX,
                             'um_per_px': round(TILE_UM / TILE_PX, 4),
                             **tile(IMAGES / s / r.plate, float(r.um_per_px), ASSETS / f'a5-{key.replace("_", "")}.png')}}
    a, b = rep['lab_5'], rep['lab_6']
    pc, pt = pooled_iqr(d, 'count'), pooled_iqr(d, 'texture')
    out.update({'count_diff': int(abs(a['count'] - b['count'])), 'count_pooled_iqr': pc,
                'texture_diff': round(float(abs(a.texture - b.texture)), 4), 'texture_pooled_iqr': round(pt, 4),
                'count_close': bool(abs(a['count'] - b['count']) < pc),
                'texture_differs': bool(abs(a.texture - b.texture) > pt)})
    out['robustness'] = {'main': checks(d, 'count', 'texture'),
                         'nuclear_edge_eroded_1px': checks(d, 'count', 'texture_inner'),
                         'cutoffs': {str(c): checks(d, 'count', f'texture_{c}') for c in CUTS}}
    out['noise_floor'] = {'what': 'high band outside nuclei, mean square, over mean square inside nuclei, percent',
                          **{k: round(float(d[d.lab == s].noise_floor.median()), 4) for k, s in LABS.items()}}
    json.dump(out, open('results/a5-pair.json', 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ('count_close', 'texture_differs', 'count_diff', 'count_pooled_iqr', 'texture_diff', 'texture_pooled_iqr')}))
    for k in LABS:
        print(k, {f: out[k][f] for f in ('plate', 'well', 'count', 'texture', 'count_median', 'count_iqr', 'texture_median', 'texture_iqr', 'n_plates')})
    print('cutoffs', {c: (v['medians_texture_differ'], v['pairs_texture_differs'], v['pairs_lab_6_higher']) for c, v in out['robustness']['cutoffs'].items()})


if __name__ == '__main__':
    main()
