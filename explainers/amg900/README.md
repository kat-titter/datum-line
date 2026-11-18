# Why AMG 900 enlarges nuclei

One self-contained page behind slide 07, where AMG 900's nuclear growth is read against each lab's own DMSO wells.
Live at https://kat-titter.github.io/datum-line/explainers/amg900/

`index.html` carries every style, figure and reference inline; nothing loads but the Google Fonts stylesheet the
deck itself uses. Colours are the deck's own, value for value from `figures/parts.py` (PINK, GREEN, INK, INK2, MUTE, GRID,
PANEL and their dark twins), and the cell drawings wear the deck's own channels, the same pair as its slide 07
crops: DNA and nuclei pink, cell body green. In the measured plot the vehicle is grey and AMG 900 pink; the
machinery - chromosomes, kinase, spindle, nucleosome - stays neutral.

The masthead puts the molecule and the one-glance mechanism above the fold: the structure, and a vehicle cell
beside a treated one with their nuclei drawn to the measured scale (15.0 against 18.1 um equivalent diameter).

Figure 4 is measured, not drawn: 1,092 nuclei from wells G09, N07 (DMSO) and N09 (AMG 900, 10 uM) of plate
BR00116991 of the JUMP Cell Painting pilot, the same public CC0 source as the deck's own AMG 900 crops. Medians:
nuclear area 176 to 258 um2 (1.47x), integrated Hoechst per nucleus 1.63x, 20.2% of treated nuclei above twice the
vehicle median against 0.7% under vehicle.

Figure 3 carries the test on the plot: Mann-Whitney on nuclei, two-sided, with Cliff's delta as the effect
size (area p = 3e-32, delta +0.50; DNA p = 1e-20, delta +0.39). The caption says plainly that the unit of
replication is the well and there is one treated well, and gives the honest replicate test over fields: three
treated against six vehicle, exact permutation p = 0.012 one-sided.

Sixteen references, each verified at its DOI through Crossref.

`assets/icons/` holds the three open icons used in the figures, with their sources and licences in `SOURCE.txt`:
a Servier Medical Art chromosome (CC BY 3.0) and two CC0 Bioicons. They are inlined into `index.html`; the files
are kept here as the licence record.

## Rebuilding

The build lives outside this repo, at `~/moa-explainers/amg900`, and follows the `moa-explainer` skill:

```bash
cd ~/moa-explainers/amg900
python3 scripts/structure.py && python3 scripts/icons.py > assets/symbols.svg
python3 scripts/assay_fig.py > assets/fig-assay.svg && python3 scripts/build.py
cp standalone.html <this repo>/explainers/amg900/index.html
```

`build.py` writes two files: `index.html` for the Claude Artifact, which supplies its own document skeleton, and
`standalone.html` with the skeleton added, which is the one served here.
