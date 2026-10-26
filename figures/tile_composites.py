"""03's tiles as two-channel composites (26 Oct, Kat: "dont show only nuclei in images: two channels one pink one green").
For each lab, the DMSO field e15 imaged on the lab's first plate (cache/images, as coherence.eleven_tiles picks it): DNA
(Hoechst) as pink nuclei laid over AGP (phalloidin, WGA) as a green cell body, each channel as e15 windowed it, on black;
320 x 320 JPEG. The field's width in microns goes beside it, so the 100-micron bars stay true. Run once; the assets are tracked.

Usage:  python figures/tile_composites.py
Writes: figures/assets/tile-composite/{source}.jpg, figures/assets/tile-composite/fields.json
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

PINK, GREEN = np.array([239, 116, 173]) / 255, np.array([63, 224, 160]) / 255
OUT = Path('figures/assets/tile-composite')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    px = pd.read_csv('metadata/microscope_config.csv').drop_duplicates('Metadata_Source').set_index('Metadata_Source').Metadata_Pixel_Size_Microns
    fields = {}
    for lab in sorted(os.listdir('cache/images'), key=lambda s: int(s.split('_')[1])):
        plate = sorted(p for p in os.listdir(f'cache/images/{lab}') if os.path.exists(f'cache/images/{lab}/{p}/DNA.png'))[0]
        d = Path(f'cache/images/{lab}/{plate}')
        dna = np.asarray(Image.open(d / 'DNA.png').convert('L').resize((320, 320), Image.LANCZOS), dtype=np.float32) / 255
        agp = np.asarray(Image.open(d / 'AGP.png').convert('L').resize((320, 320), Image.LANCZOS), dtype=np.float32) / 255
        rgb = (agp ** 0.8)[..., None] * GREEN * (1 - dna[..., None]) + dna[..., None] * PINK
        Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(OUT / f'{lab}.jpg', quality=88)
        meta = json.loads((d / 'meta.json').read_text())
        fields[lab] = {'plate': plate, 'well': meta['well'], 'field_um': round(meta['channels']['DNA']['shape'][1] * float(px[lab]), 1)}
    (OUT / 'fields.json').write_text(json.dumps(fields, indent=1))
    print(json.dumps(fields))


if __name__ == '__main__':
    main()
