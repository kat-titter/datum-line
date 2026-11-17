# Why AMG 900 enlarges nuclei

One self-contained page behind slide 07, where AMG 900's nuclear growth is read against each lab's own DMSO wells.
Live at https://kat-titter.github.io/datum-line/explainers/amg900/

`index.html` carries every style, figure and reference inline; nothing loads but the Google Fonts stylesheet the
deck itself uses. Colours are the deck's own, value for value from `figures/parts.py` (PINK, GREEN, INK, INK2,
MUTE, GRID, PANEL and their dark twins), and they mean the same thing: pink is the one thing singled out, which
here is AMG 900; green is the reference it is read against, the DMSO vehicle; the machinery is neutral.

Figure 4 is measured, not drawn: 1,092 nuclei from wells G09, N07 (DMSO) and N09 (AMG 900, 10 uM) of plate
BR00116991 of the JUMP Cell Painting pilot, the same public CC0 source as the deck's own AMG 900 crops. Medians:
nuclear area 176 to 258 um2 (1.47x), integrated Hoechst per nucleus 1.63x, 20.2% of treated nuclei above twice the
vehicle median against 0.7% under vehicle.

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
