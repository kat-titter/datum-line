"""Slide 02c's image search results: one negative-control field from each published U2OS screen.

The search card shows six "U2OS cells, normal morphology" results, one per paper. Five come from
the Image Data Resource (IDR). The first build (28 Sep 2026) took a field from the middle of
each screen's first plate, so four of the five showed treated cells: an siRNA against ARSG
(Doil 2009), niflumic acid (Gustafsdottir 2013), clemastine (Bray 2017) and a target siRNA
from an antibody-validation pair (Stadler 2012). Only Rohban 2017 was a control well. This
script replaces those four with a well each study itself labels "negative control", on the
same plate as the old tile.

Which well. Doil (8 per plate), Gustafsdottir and Bray (64) have many control wells, so one rule
picks among them: the negative-control wells on the old tile's plate, minus any the study's
quality control removed, minus any in the outer two rows and columns; of those, field 1 of
the sharpest, by a focus score on the DNA channel (mean absolute Laplacian of a sigma-1 px
Gaussian over the brightest quarter of pixels, over their mean brightness, x100). The script
re-ranks the candidates on every run and stops if the top one is not the well fixed below.
Stadler has one scrambled-siRNA well per antibody, so its tile is the old tile's own pair:
same plate, same antibody, same field, scrambled siRNA instead of the target siRNA.

What is checked before anything is drawn:
  - the plate belongs to the study's screen, and the plate's grid puts the image in that
    well and field;
  - the well's row in IDR's bulk annotation table (the study's screenA annotation CSV, as
    IDR serves it) says Control Type "negative control", and the image is annotated U2OS;
  - the licence and the publication come from the screen's own map annotation.

Rendering is IDR's default: render_image with every channel's on/off state, window and
colour read from the image's default rendering settings (webgateway/imgData), as a PNG at
full resolution. Nothing is re-coloured or re-stretched. Each field is scaled to cover
400 x 307 px (the 300:230 aspect of the tiles on the slide) and centre-cropped, then saved
as JPEG at quality 85.

Rohban 2017 keeps its tile. Its provenance is recorded too (image 3191231), with a check
that re-rendering that image the way the first build did (render_birds_eye_view at 600 px,
cover-cropped to 300 x 230) matches the tile in index.html. The sixth tile, JUMP 2023 lab 2,
is from the Cell Painting Gallery, not IDR; it is not touched here.

Usage:  python analysis/pull_search_tiles.py
Needs:  network access to idr.openmicroscopy.org (public, no login), Pillow, numpy, scipy.
        About 100 single-channel renders for the ranking; a minute or two.
Writes: figures/assets/search-doil-2009.jpg, figures/assets/search-gustafsdottir-2013.jpg,
        figures/assets/search-bray-2017.jpg, figures/assets/search-stadler-2012.jpg,
        results/search-tiles.json
"""
import base64
import concurrent.futures as cf
import datetime as dt
import http.cookiejar
import io
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
IDR = 'https://idr.openmicroscopy.org'
TILE_W, TILE_H = 400, 307          # 300:230, the aspect of the tiles on the slide
JPEG_QUALITY = 85
EDGE = 2                           # wells this close to the plate edge are not candidates

# Journal details checked against Crossref on 2026-10-25. Authors, titles and licences are
# read from IDR at run time. pick='sharpest' applies the rule in the docstring; dna = the
# channel number holding the DNA stain.
TILES = [
    dict(key='doil-2009', label='Doil 2009', study='idr0010', screen=1351,
         plate=4503, well='C6', field=1, image=1922265, dna=1, pick='sharpest',
         paper=dict(year=2009, journal='Cell', volume='136(3):435-446', doi='10.1016/j.cell.2008.12.041'),
         replaces=1922333),
    dict(key='gustafsdottir-2013', label='Gustafsdottir 2013', study='idr0036', screen=1952,
         plate=4403, well='N14', field=1, image=1899001, dna=1, pick='sharpest',
         paper=dict(year=2013, journal='PLoS ONE', volume='8(12):e80999', doi='10.1371/journal.pone.0080999'),
         replaces=1895787),
    dict(key='bray-2017', label='Bray 2017', study='idr0016', screen=1251,
         plate=6208, well='C16', field=1, image=3408886, dna=1, pick='sharpest',
         paper=dict(year=2017, journal='GigaScience', volume='6(12):giw014', doi='10.1093/gigascience/giw014'),
         replaces=3407146),
    dict(key='stadler-2012', label='Stadler 2012', study='idr0025', screen=1851,
         plate=6001, well='G1', field=1, image=3260536, dna=1, pick='pair',
         paper=dict(year=2012, journal='Journal of Proteomics', volume='75(7):2236-2251', doi='10.1016/j.jprot.2012.01.030'),
         chosen=('The paired control of the old tile (E1, siRNA s25059 against C20orf26): same plate, same '
                 'antibody (HPA009079; IDR leaves the control well\'s antibody blank, but its Comments give the '
                 'raw image directory "plate 1 E1F1 ab 13 c20orf26", the same as E1 and F1), same field; '
                 'scrambled siRNA instead of the target siRNA. The study did not validate this antibody\'s '
                 'localization (E1: "Validated localizations: none"), so the green channel is not a validated '
                 'protein location.'),
         replaces=3260520),
]
KEPT = dict(key='rohban-2017', label='Rohban 2017', study='idr0033', screen=1751,
            plate=5958, well='A1', field=1, image=3191231, dna=1, pick='kept',
            paper=dict(year=2017, journal='eLife', volume='6:e24060', doi='10.7554/eLife.24060'),
            chosen='Kept from the first build (commit 5df3918, 28 Sep 2026); already a negative-control well.')

_jar = http.cookiejar.CookieJar()
_web = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))


def get(path, raw=False):
    req = urllib.request.Request(IDR + path, headers={'User-Agent': 'datum-line pull_search_tiles.py',
                                                      'Referer': IDR + '/webclient/'})
    body = _web.open(req, timeout=180).read()
    return body if raw else json.loads(body)


def map_annotations(kind, oid):
    """IDR key-value annotations on a screen, well or image, as {key: [values]}."""
    out = {}
    for a in get(f'/webclient/api/annotations/?type=map&{kind}={oid}').get('annotations', []):
        for k, v in a.get('values', []):
            out.setdefault(k, []).append(v)
    return out


def bulk_rows(well_id, query):
    """Rows of IDR's bulk annotation table (the study's screenA annotation CSV) for a query."""
    d = get(f'/webgateway/table/Screen.plateLinks.child.wells/{well_id}/query/?'
            + urllib.parse.urlencode({'query': query, 'limit': 5000}))['data']
    return [dict(zip(d['columns'], r)) for r in d['rows']]


def bulk_row(well_id):
    rows = bulk_rows(well_id, f'Well-{well_id}')
    assert len(rows) == 1, (well_id, len(rows))
    return rows[0]


def plate_grid(plate, field):
    """{well label: grid cell} for one field of a plate, from IDR's plate view."""
    g = get(f'/webgateway/plate/{plate}/{field - 1}/')
    return {f'{g["rowlabels"][i]}{g["collabels"][j]}': c
            for i, row in enumerate(g['grid']) for j, c in enumerate(row) if c}


def check_place(t):
    """The plate is in the screen, and the plate grid puts the image in that well and field."""
    plates = {p['@id']: p['Name'] for p in get(f'/api/v0/m/screens/{t["screen"]}/plates/?limit=1000')['data']}
    assert t['plate'] in plates, (t['key'], 'plate not in screen')
    cell = plate_grid(t['plate'], t['field']).get(t['well'])
    assert cell and cell['id'] == t['image'], (t['key'], 'grid gives', cell and cell['id'])
    return plates[t['plate']], cell['wellId'], cell['name']


def screen_info(t):
    s = map_annotations('screen', t['screen'])
    screen_name = get(f'/api/v0/m/screens/{t["screen"]}/')['data']['Name']
    pubs = list(zip(s.get('Publication Title', []), s.get('Publication Authors', []), s.get('Publication DOI', [])))
    pub = [p for p in pubs if p[2].split()[0] == t['paper']['doi']]
    assert pub, (t['key'], 'paper DOI not among the screen\'s publications')
    title, authors, _ = pub[0]
    name, url = s['License'][0].rsplit(' ', 1)          # e.g. "CC BY 4.0 https://creativecommons.org/licenses/by/4.0/"
    info = dict(screen_name=screen_name, study_title=(s.get('Study Title') or [''])[0],
                licence=dict(name=name, url=url, as_stated=s['License'][0]),
                annotation_file=(s.get('Annotation File') or [''])[0],
                paper=dict(authors=authors, title=title.rstrip('.'), **t['paper']))
    if 'Data DOI' in s:
        info['data_doi'] = s['Data DOI'][0].split()[0]
    return info


def window(ch):
    return f"{ch['window']['start']:g}:{ch['window']['end']:g}"


def default_render_url(image_id, md, fmt='png'):
    """render_image with the image's own default channel settings: on/off, window and colour."""
    c = ','.join(('' if ch['active'] else '-') + f"{k + 1}|{window(ch)}${ch['color']}" for k, ch in enumerate(md['channels']))
    z, t = md['rdefs'].get('defaultZ', 0), md['rdefs'].get('defaultT', 0)
    return f'/webgateway/render_image/{image_id}/{z}/{t}/?' + urllib.parse.urlencode({'c': c, 'm': 'c', 'format': fmt}, safe='|$,:')


def focus(image_id, dna):
    """Focus score of the DNA channel at its default window: mean |LoG| over the brightest quarter / their mean, x100."""
    md = get(f'/webgateway/imgData/{image_id}/')
    ch = md['channels'][dna - 1]
    z, t = md['rdefs'].get('defaultZ', 0), md['rdefs'].get('defaultT', 0)
    url = f'/webgateway/render_image/{image_id}/{z}/{t}/?' + urllib.parse.urlencode(
        {'c': f'{dna}|{window(ch)}$FFFFFF', 'm': 'g', 'format': 'png'}, safe='|$,:')
    a = np.asarray(Image.open(io.BytesIO(get(url, raw=True))).convert('L'), float)
    g = ndimage.gaussian_filter(a, 1)
    bright = g > np.percentile(g, 75)
    return float(np.abs(ndimage.laplace(g))[bright].mean() / max(g[bright].mean(), 1) * 100)


def rank(t, well_id):
    """Every candidate well on the plate under the rule in the docstring, sharpest first."""
    grid = plate_grid(t['plate'], t['field'])
    rows = sorted({re.match(r'[A-Z]+', w).group(0) for w in grid}, key=lambda r: (len(r), r))
    cols = sorted({int(re.search(r'\d+', w).group(0)) for w in grid})
    inner_rows, inner_cols = set(rows[EDGE:-EDGE]), set(cols[EDGE:-EDGE])
    by_id = {c['wellId']: (w, c['id']) for w, c in grid.items()}
    plate = bulk_rows(well_id, f'Plate-{t["plate"]}')
    neg = [r for r in plate if r.get('Control Type') == 'negative control']
    ok = [r for r in neg if not (r.get('Quality Control') or '').strip()]
    inner = [r for r in ok if r['Well'] in by_id
             and re.match(r'[A-Z]+', by_id[r['Well']][0]).group(0) in inner_rows
             and int(re.search(r'\d+', by_id[r['Well']][0]).group(0)) in inner_cols]
    with cf.ThreadPoolExecutor(6) as ex:
        scores = list(ex.map(lambda r: focus(by_id[r['Well']][1], t['dna']), inner))
    ranked = sorted(([by_id[r['Well']][0], by_id[r['Well']][1], round(s, 2)] for r, s in zip(inner, scores)),
                    key=lambda x: -x[2])
    return dict(negative_control_wells=len(neg), has_qc=any('Quality Control' in r for r in plate), after_quality_control=len(ok),
                not_on_edge=len(inner), plate_layout=f'{len(rows)} x {len(cols)}', ranked=ranked)


def cover_crop(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def control_fields(row):
    keep = ('Control Type', 'Control Comments', 'Compound Name', 'Dose', 'siRNA Identifier', 'Original Gene Target',
            'Gene Symbol', 'Quality Control', 'Quality Control Comments', 'Cell Count', 'Comments')
    return {k: row[k] for k in keep if k in row and row[k] not in ('', None)}


def provenance(t):
    plate_name, well_id, image_name = check_place(t)
    md = get(f'/webgateway/imgData/{t["image"]}/')
    assert md['meta']['wellId'] == well_id, (t['key'], 'imgData well differs from grid well')
    row = bulk_row(well_id)
    assert row['Control Type'] == 'negative control', (t['key'], row['Control Type'])
    cell_line = map_annotations('image', t['image']).get('Cell Line', [''])[0]
    assert cell_line == 'U2OS', (t['key'], cell_line)
    info = screen_info(t)
    rec = dict(
        label=t['label'], paper=info.pop('paper'), idr_study=t['study'],
        screen=dict(id=t['screen'], name=info.pop('screen_name')),
        plate=dict(id=t['plate'], name=plate_name), well=dict(label=t['well'], id=well_id),
        field=t['field'], image=dict(id=t['image'], name=image_name,
                                     size_px=[md['size']['width'], md['size']['height']],
                                     webclient=f'{IDR}/webclient/?show=image-{t["image"]}'),
        cell_line=cell_line,
        control=dict(annotation=control_fields(row),
                     source=(f'IDR bulk annotation table for well {well_id} ({IDR}/webgateway/table/Screen.plateLinks.child.wells/'
                             f'{well_id}/query/?query=Well-{well_id}), i.e. {info["annotation_file"].split()[0]}')),
        channels=(row.get('Channels') or '').strip(), **info)
    if t['pick'] == 'sharpest':
        r = rank(t, well_id)
        assert r['ranked'] and r['ranked'][0][1] == t['image'], (t['key'], 'the rule now picks', r['ranked'][:3])
        qc = (f'{r["after_quality_control"]} pass the study\'s quality control (Quality Control blank)' if r['has_qc']
              else 'the study has no quality-control column')
        rec['chosen'] = (f'The rule: the plate has {r["negative_control_wells"]} negative-control wells; {qc}; '
                         f'{r["not_on_edge"]} of those are outside the outer {EDGE} rows and columns of the '
                         f'{r["plate_layout"]} layout. This is the sharpest of them, field {t["field"]}, by the DNA-channel '
                         f'focus score.')
        rec['ranking'] = dict(score='focus: mean |Laplacian of Gaussian, sigma 1 px| over the brightest quarter of '
                                    'DNA-channel pixels / their mean, x100; higher is sharper',
                              top=[dict(well=w, image=i, focus=s) for w, i, s in r['ranked'][:5]],
                              median=round(float(np.median([s for _, _, s in r['ranked']])), 2))
    else:
        rec['chosen'] = t['chosen']
    return md, rec


def what_it_showed(image_id):
    md = get(f'/webgateway/imgData/{image_id}/')
    row = bulk_row(md['meta']['wellId'])
    keep = ('Control Type', 'Control Comments', 'Compound Name', 'Dose', 'siRNA Identifier', 'Original Gene Target',
            'Gene Symbol', 'Antibody Identifier', 'Validated localizations')
    return dict(image=image_id, name=md['meta']['imageName'], well_id=md['meta']['wellId'],
                annotation={k: row[k] for k in keep if k in row and row[k] not in ('', None)})


def check_kept_tile(image_id):
    """Pixel match of the first build's rendering of this image against the tile in index.html."""
    html = (ROOT / 'index.html').read_text()
    m = re.search(r'<img src="data:image/jpeg;base64,([^"]+)" alt="Image search result: U2OS cells, Rohban 2017', html)
    if not m:
        return 'tile not found in index.html'
    deck = np.asarray(Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB'), float)
    first = Image.open(io.BytesIO(get(f'/webgateway/render_birds_eye_view/{image_id}/600/', raw=True))).convert('RGB')
    redo = np.asarray(cover_crop(first, deck.shape[1], deck.shape[0]), float)
    r = float(np.corrcoef(deck.ravel(), redo.ravel())[0, 1])
    return dict(method='render_birds_eye_view at 600 px, cover-cropped to the tile size, as the first build did',
                pearson_r=round(r, 3), mean_abs_diff_8bit=round(float(np.abs(deck - redo).mean()), 2))


def main():
    fetched = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    tiles = []
    for t in TILES:
        md, rec = provenance(t)
        url = default_render_url(t['image'], md)
        im = Image.open(io.BytesIO(get(url, raw=True))).convert('RGB')
        out = ROOT / 'figures' / 'assets' / f'search-{t["key"]}.jpg'
        cover_crop(im, TILE_W, TILE_H).save(out, quality=JPEG_QUALITY)
        rec.update(
            image_url=IDR + url,
            rendering=dict(method='IDR default rendering: webgateway render_image, channel settings from webgateway/imgData',
                           channels=[dict(label=ch['label'], on=ch['active'], window=[ch['window']['start'], ch['window']['end']],
                                          colour=ch['color']) for ch in md['channels']]),
            file=str(out.relative_to(ROOT)), file_px=[TILE_W, TILE_H], jpeg_quality=JPEG_QUALITY,
            crop=f'scaled to cover {TILE_W} x {TILE_H} px, centre-cropped', fetched=fetched,
            replaces=what_it_showed(t['replaces']))
        tiles.append(rec)
        print(f'{t["label"]:20s} {rec["plate"]["name"]} {t["well"]} field {t["field"]} image {t["image"]}: '
              f'{rec["control"]["annotation"]["Control Type"]}, {rec["control"]["annotation"].get("Control Comments", "")}'
              f' | {rec["licence"]["name"]} -> {rec["file"]}')
        if 'ranking' in rec:
            print(f'{"":20s} focus, sharpest first: '
                  + ', '.join(f'{x["well"]} {x["focus"]}' for x in rec['ranking']['top']) + f'; median {rec["ranking"]["median"]}')
    md, kept = provenance(KEPT)
    kept.update(image_url=IDR + default_render_url(KEPT['image'], md), fetched=fetched,
                first_build_url=f'{IDR}/webgateway/render_birds_eye_view/{KEPT["image"]}/600/',
                deck_tile_check=check_kept_tile(KEPT['image']), file='embedded in index.html (not re-written)')
    print(f'{KEPT["label"]:20s} kept; image {KEPT["image"]}: {kept["control"]["annotation"]["Control Comments"]}; '
          f'match to deck tile: {kept["deck_tile_check"]}')
    result = dict(
        question='Slide 02c search results: is each published U2OS image a negative-control well, and where is it from?',
        source='Image Data Resource (idr.openmicroscopy.org), public; licences as each IDR study states them',
        script='analysis/pull_search_tiles.py', fetched=fetched,
        tiles=tiles, kept=[kept],
        not_covered='JUMP 2023 lab 2 tile: from the Cell Painting Gallery (cpg0016), not IDR; unchanged and not fetched here')
    path = ROOT / 'results' / 'search-tiles.json'
    path.write_text(json.dumps(result, indent=1, ensure_ascii=False) + '\n')
    print('wrote', path.relative_to(ROOT))


if __name__ == '__main__':
    main()
