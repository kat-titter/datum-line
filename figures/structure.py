"""RSL3's chemical structure, drawn from the SMILES that JUMP recorded for it.

Slide 05 shows what RSL3 does to cells in four labs; this draws the molecule itself, so the biology
and the chemistry sit side by side. The SMILES is read from JUMP's compound table under RSL3's JUMP
id, never typed, so the drawing is exactly what JUMP recorded. Formula, average molecular weight and
InChIKey are computed by RDKit from that SMILES, and the InChIKey is checked against JUMP's own.

JUMP's record has no stereochemistry: its InChIKey carries the standard 'no stereo' block, and RDKit
finds its stereocentres unspecified. The drawing, like the record, shows no wedges.

The warhead is the chloroacetamide: the C(=O)CH2Cl group on the ring nitrogen, the group that binds
GPX4. It is found by a substructure pattern, not by atom number, and must match exactly once.

Two drawings, one geometry: rsl3-warhead.svg has a soft neutral halo behind the warhead, and
rsl3-structure.svg is the same drawing with the halo removed, so the two line up exactly and one can
fade into the other. Layout is RDKit's CoordGen, which is deterministic: a rerun writes byte-identical
files. Bonds and labels are one ink (#14171a), bonds 2 px at the drawing's own width (about 260 px),
labels 15 px in Archivo with sans-serif fallbacks, transparent background, no title. Inline the SVG in
the page to get Archivo; as an <img> it falls back to Helvetica or Arial. Set it on a light card.

Usage:  python figures/structure.py
Needs:  metadata/compound.csv.gz, rdkit (requirements.txt)
Writes: figures/assets/rsl3-structure.svg, figures/assets/rsl3-warhead.svg, results/rsl3-structure.json
"""
import json
import re
from pathlib import Path

import pandas as pd
from rdkit import Chem, rdBase
from rdkit.Chem import Descriptors, rdDepictor, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

ROOT = Path(__file__).resolve().parent.parent
JCP = 'JCP2022_087365'
NAME = 'RSL3'
WARHEAD = '[N;R]C(=O)[CH2]Cl'           # ring nitrogen, then the chloroacetyl group on it; the group is every atom after the N
INK, HALO = '#14171a', '#e3e6e7'
FONT = 'Archivo,Helvetica Neue,Helvetica,Arial,sans-serif'
PX_PER_BOND = 26                        # sets the drawing's own size: about 260 px wide
FONT_PX, BOND_PX = 15, 2
HALO_RADIUS = 0.40                      # halo circle radius, in bond lengths
HALO_BAND = 21                          # halo band across a bond, px: the circles' diameter, so the halo reads as one shape
PADDING = 0.02
OUT_PLAIN = ROOT / 'figures/assets/rsl3-structure.svg'
OUT_HALO = ROOT / 'figures/assets/rsl3-warhead.svg'
OUT_JSON = ROOT / 'results/rsl3-structure.json'


def rgb(hex_colour):
    return tuple(int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))


def record():
    c = pd.read_csv(ROOT / 'metadata/compound.csv.gz', dtype=str)
    row = c[c.Metadata_JCP2022 == JCP]
    if len(row) != 1:
        raise SystemExit(f'{JCP}: {len(row)} rows in metadata/compound.csv.gz, expected 1')
    return row.iloc[0]


def warhead(mol):
    hits = mol.GetSubstructMatches(Chem.MolFromSmarts(WARHEAD))
    if len(hits) != 1:
        raise SystemExit(f'warhead pattern {WARHEAD} matched {len(hits)} times, expected once')
    ring_n, *group = hits[0]
    bonds = sorted(b.GetIdx() for b in mol.GetBonds() if b.GetBeginAtomIdx() in group and b.GetEndAtomIdx() in group)
    return ring_n, list(group), bonds


def draw(mol, atoms, bonds):
    """The halo drawing. CoordGen layout; flexicanvas, so the canvas fits the molecule and its halo."""
    rdDepictor.SetPreferCoordGen(True)
    rdDepictor.Compute2DCoords(mol)
    d = rdMolDraw2D.MolDraw2DSVG(-1, -1, -1, -1, True)        # True: labels as <text>, so the page's Archivo applies
    o = d.drawOptions()
    o.scalingFactor = PX_PER_BOND
    o.fixedFontSize = FONT_PX
    o.bondLineWidth = BOND_PX
    o.clearBackground = False                                  # transparent
    o.padding = PADDING
    o.setAtomPalette({-1: rgb(INK), **{z: rgb(INK) for z in range(119)}})
    o.fillHighlights = True
    o.highlightRadius = HALO_RADIUS
    o.highlightBondWidthMultiplier = HALO_BAND
    d.DrawMolecule(mol, highlightAtoms=atoms, highlightBonds=bonds,
                   highlightAtomColors={i: rgb(HALO) for i in atoms}, highlightBondColors={i: rgb(HALO) for i in bonds})
    d.FinishDrawing()
    return d.GetDrawingText()


def tidy(svg, label):
    svg = re.sub(r"^<\?xml[^>]*\?>\s*", '', svg)               # so the file can be inlined in a page as it is
    svg = svg.replace('<!-- END OF HEADER -->\n', '')
    svg = svg.replace('font-family:sans-serif', f'font-family:{FONT}')
    svg = svg.replace(INK.upper(), INK).replace(HALO.upper(), HALO)
    svg = svg.replace("<svg version='1.1'", f"<svg role='img' aria-label='{label}' version='1.1'", 1)
    assert '<rect' not in svg, 'background rectangle drawn'
    assert set(re.findall(r'#[0-9a-fA-F]{6}', svg)) <= {INK, HALO}, 'a colour other than ink and halo'
    return svg


def main():
    r = record()
    mol = Chem.MolFromSmiles(r.Metadata_SMILES)
    if mol is None:
        raise SystemExit(f'RDKit could not read the SMILES recorded for {JCP}')
    ring_n, atoms, bonds = warhead(mol)
    centres = Chem.FindMolChiralCenters(mol, includeUnassigned=True, useLegacyImplementation=False)

    label = f'{NAME}, chemical structure'
    halo = tidy(draw(mol, atoms, bonds), f'{label}, the group that binds GPX4 shaded')
    halo_elements = re.findall(rf"<(?:path|ellipse)[^>]*{HALO}[^>]*/>\n?", halo)
    plain = halo.replace(f"aria-label='{label}, the group that binds GPX4 shaded'", f"aria-label='{label}'", 1)
    for e in halo_elements:
        plain = plain.replace(e, '', 1)
    assert len(halo_elements) == len(atoms) + len(bonds) and HALO not in plain, 'halo not removed cleanly'
    OUT_PLAIN.parent.mkdir(parents=True, exist_ok=True)
    OUT_PLAIN.write_text(plain)
    OUT_HALO.write_text(halo)

    inchikey = Chem.MolToInchiKey(mol)
    view = [float(v) for v in re.search(r"viewBox='([^']+)'", halo).group(1).split()]
    out = {'name': NAME, 'jcp': JCP, 'source': 'metadata/compound.csv.gz',
           'smiles_as_recorded': r.Metadata_SMILES,
           'formula': rdMolDescriptors.CalcMolFormula(mol),
           'average_mw': round(Descriptors.MolWt(mol), 2),
           'inchikey_computed': inchikey, 'inchikey_as_recorded': r.Metadata_InChIKey,
           'inchikey_matches_jump': inchikey == r.Metadata_InChIKey,
           'inchi_matches_jump': Chem.MolToInchi(mol) == r.Metadata_InChI,
           'stereocentres': len(centres),
           'stereocentres_specified': sum(label != '?' for _, label in centres),
           'any_stereo_specified': any(label != '?' for _, label in centres),
           'stereocentre_atoms': [int(i) for i, _ in centres],
           'warhead': {'what': 'chloroacetamide: the C(=O)CH2Cl group on the ring nitrogen; the group that binds GPX4',
                       'pattern': WARHEAD, 'atoms': atoms, 'bonds': bonds, 'ring_nitrogen': int(ring_n),
                       'atom_symbols': [mol.GetAtomWithIdx(i).GetSymbol() for i in atoms]},
           'atom_indices': 'RDKit atom order of the SMILES as recorded',
           'drawing': {'layout': 'RDKit CoordGen', 'rdkit': rdBase.rdkitVersion,
                       'plain': str(OUT_PLAIN.relative_to(ROOT)), 'warhead': str(OUT_HALO.relative_to(ROOT)),
                       'same_geometry': 'the plain drawing is the warhead drawing with its halo removed',
                       'viewbox': view, 'px_per_bond': PX_PER_BOND, 'bond_px': BOND_PX, 'font_px': FONT_PX,
                       'font': FONT, 'ink': INK, 'halo': HALO, 'background': 'transparent'}}
    OUT_JSON.write_text(json.dumps(out, indent=1) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'drawing'}, indent=1))
    print(f'wrote {OUT_PLAIN.relative_to(ROOT)}, {OUT_HALO.relative_to(ROOT)} ({view[2]:g} x {view[3]:g}), {OUT_JSON.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
