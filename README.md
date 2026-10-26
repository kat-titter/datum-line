# Datum Line

**Do my cells look normal? Confidence with controls.** Datum Line is a shared repository of raw cell images from every lab, on one map, which makes cell data from any lab comparable with any other lab's. Labs put their cells on the map for free; companies that buy cell data pay for the certificate.

**View it:** https://kat-titter.github.io/datum-line/&emsp;**PDF:** [`datum-line-deck.pdf`](datum-line-deck.pdf)&emsp;**Documents:** [`docs/`](https://kat-titter.github.io/datum-line/docs/)

---

## 1. The idea

Every result in biology is a difference from a control, and nobody checks the control against anyone else's. A plate can pass every local QC rule while its DMSO wells look like a different lab's. Normal is a comparison you cannot make alone.

Datum Line places a lab's control wells on a map of every lab running the same line, from images it already takes, and says where its cells sit, how far they have moved and which features moved. It starts as a map; it grows into a certificate, then subscriptions to the repository: raw images any lab, agent or company can trust.

## 2. How to read the deck

- **Scroll**, or use **↑ ↓ / Space / Page Up / Page Down**. **Home / End** jump to either end.
- Slides **02** to **05** step through states: **click** (or press **→**). Three on 02 and 04, two on 03.
- Animations play as each slide scrolls into view.
- Slides 01–10 are the talk: the title; who is asking, the question asked at every bench, and how each lab answers it today, alone (search, ask, guess); one lab or eleven; eleven labs, eleven normals, a new batch placed on the same map with its certificate, and controls alone flag the batches that go wrong; the product, the data every lab checks against; why it compounds as labs join; the market and why now; who else; what the money buys; and where it goes, with the ask. Each talk slide's foot line says where its key numbers come from (a results file, a board or a numbered reference); press **D** for the full figure legends. The **appendix** is twelve slides: A0, an index from question to board, and the eleven boards a judge is most likely to ask for (A3, A9, A10, A14, A15, A18, A19, A20, A21, A22, A24). All 25 boards, with the same codes, are in the [archive](https://kat-titter.github.io/datum-line/archive.html).

## 3. The evidence

All data shown is public: the **JUMP Cell Painting** consortium dataset (cpg0016), CC0.

- **Labs are recognisable.** On 93,228 DMSO control wells from 1,872 plates in eleven labs, a classifier names the lab from control wells alone at 99.9% balanced accuracy against 9.1% chance, on plates it never saw.
- **A lab can move without seeing it.** Replayed batch by batch, one lab's last three batches sit further from its own June baseline than from another lab, while their cell counts stay inside the lab's own range. Across the field 6 of 129 batches do this.
- **The move predicts the answer.** Inside labs, the further a batch has drifted, the less its measured effect of the same positive controls agrees with the lab's own first batch: Spearman -0.71 over 118 batches.
- **Same drug, same dose, different picture.** RSL3 at 10 µM in the three labs that ran it at that dose leaves 14–22% of cells in each, yet its wells agree 0.90 inside a lab and 0.49 across labs; the eight positive controls on the same plates split the same way (`results/e16`, seven wells: an example, not proof). JUMP ran a fourth lab at 0.625 µM; it is left out.
- **A known answer can fail silently.** In four consecutive batches of one lab, 65 plates, the wells the public plate map labels as positive controls show no effect.

Every number is produced by a script in [`analysis/`](analysis/) and stored in [`results/`](results/). [`results/SUMMARY.md`](results/SUMMARY.md) is the full table, and [`analysis/README.md`](analysis/README.md) says how to reproduce it, what did not reproduce from earlier versions of this deck, how each claim was red-teamed, and its limits.

The evidence shown is fluorescence (Cell Painting). The product bets on label-free brightfield: a frozen vision model already names the lab from one brightfield image at 99.5% across 8 labs (median of 20 splits), at least as well as the six-dye profile of the same wells (98.8%, its frame-size columns removed) on 19 of 20 splits, with the same labs, wells and held-out batches for both (`results/e17`); placing a raw image on the map is next (A10, A19).

## 4. Business model

Proposed, not yet validated. Labs and cores put their cells on the map for free; they are the map. Companies that buy cell data they did not make pay for the certificate: per certificate on a dataset they bought, or per line per quarter (~$5–15k) for groups that screen continuously. The map, the box and the code stay open. One way it grows: subscriptions to the repository of certified, comparable raw images, where the lab that made a dataset keeps a share of every subscription. Why now: data sells, and cell data does not convert between sites [10]–[13]. Details on boards A15, A21 to A24.

## 5. References cited in the deck

1. Ewald JD, Titterton KL, et al. Cell Painting for cytotoxicity and mode-of-action analysis in primary human hepatocytes. *Cell Systems*, 2026.
2. Seal S, Dee W, … Titterton K, … Carpenter AE. Counting cells can accurately predict small-molecule bioactivity benchmarks. *Nature Communications*, 2026.
3. Wu JW, Titterton K, et al. A neuronal tau aggregation assay for tau-related drug discovery. *J Biol Chem*, 2025.
4. Kang J, … Titterton K, … Boyden ES. Multiplexed expansion revealing for imaging multiprotein nanostructures in healthy and diseased brain. *Nature Communications*, 2024.
5. Wu B, Jayakar SS, … Titterton K, … Bruzik KS. Inhibitable photolabeling by a neurosteroid diazirine analog in the β3 subunit of GABA-A receptors. *Eur J Med Chem*, 2019.
6. Freedman LP, Cockburn IM, Simcoe TS. The economics of reproducibility in preclinical research. *PLoS Biology* 13(6):e1002165, 2015.
7. Chandrasekaran SN, et al. JUMP Cell Painting dataset. *bioRxiv*, 2023.
8. Bray MA, et al. Cell Painting. *Nature Protocols* 11:1757, 2016.
9. U.S. Food and Drug Administration. FDA announces plan to phase out animal testing requirement for monoclonal antibodies and other drugs. Press release, 10 April 2025. fda.gov/news-events/press-announcements/fda-announces-plan-phase-out-animal-testing-requirement-monoclonal-antibodies-and-other-drugs
10. TechCrunch. Mercor quintuples valuation to $10B with $350M Series C. 27 October 2025.
11. Recursion. Recursion reports third quarter 2025 financial results and provides business update. Press release, 5 November 2025; SEC Form 8-K, exhibit 99.1 (sec.gov/Archives/edgar/data/1601830/000160183025000164/exhibit991-q0325.htm): a second $30 million milestone from Roche and Genentech for a whole-genome phenomap of microglial cells, achieved October 2025. Checked 26 October 2026.
12. Jungco K. Google, Meta join $1.8B push to build AI “virtual cells”: here’s what we know. eWeek, 9 October 2026.
13. Wolff C, …, Schmied C. Morphological profiling data resource enables prediction of chemical compound properties. *iScience* 28(5):112445, 2025.
14. ATCC. Cell line authentication test recommendations. Technical document. atcc.org/resources/technical-documents/cell-line-authentication-test-recommendations
15. Springer Nature. Image integrity and standards. Nature Portfolio editorial policies (unprocessed gel and blot images required; raw microscopy files encouraged, not required). nature.com/nature-portfolio/editorial-policies/image-integrity, accessed 15 October 2026.
16. NCBI PubMed. Record count for the search "RSL3" (all fields): about 1,200 (1,211 on 15 October 2026; the count grows daily). pubmed.ncbi.nlm.nih.gov/?term=RSL3
17. Weisbart E, Kumar A, Arevalo J, Carpenter AE, Cimini BA, Singh S. Cell Painting Gallery: an open resource for image-based profiling. *Nature Methods* 21(10):1775–1777, 2024 (preprint abstract, arXiv 2402.02203: 656 TB of image and numerical data as of January 2024; CC0 and free to read per its AWS Registry of Open Data entry); and the Gallery's dataset table (github.com/broadinstitute/cellpainting-gallery, 14 October 2026): U2OS in 11 of 28 datasets, A549 in 4.
18. Arevalo J, Su E, Ewald JD, van Dijk R, Carpenter AE, Singh S. Evaluating batch correction methods for image-based cell profiling. *Nature Communications* 15:6516, 2024.
19. Yang WS, SriRamaratnam R, Welsch ME, et al. Regulation of ferroptotic cancer cell death by GPX4. *Cell* 156(1–2):317–331, 2014. (GPX4 as RSL3's target; only the (1S,3R) isomer is active; the chloroacetamide is essential.)
20. Dixon SJ, Lemberg KM, Lamprecht MR, et al. Ferroptosis: an iron-dependent form of nonapoptotic cell death. *Cell* 149(5):1060–1072, 2012.
21. Eaton JK, Furst L, Ruberto RA, et al. Selective covalent targeting of GPX4 using masked nitrile-oxide electrophiles. *Nature Chemical Biology* 16:497–506, 2020. (RSL3 binds GPX4 covalently.)
22. Cheff DM, Huang C, Scholzen KC, et al. The ferroptosis inducing compounds RSL3 and ML162 are not direct inhibitors of GPX4 but of TXNRD1. *Redox Biology* 62:102703, 2023.
23. PubChem. (1S,3R)-RSL3, CID 1750826. JUMP records RSL3 as JCP2022_087365 (InChIKey TXJZRSRTYPUYRW-UHFFFAOYSA-N, no stereochemistry); board A9 draws that record (`results/rsl3-structure.json`, `figures/structure.py`).
24. JUMP-Target compound annotations, targets of the eight positive controls from the Drug Repurposing Hub (clue.io/repurposing). github.com/jump-cellpainting/JUMP-Target
25. Broad Institute. JUMP Hub, Dataset overview: cell counts in cpg0016 (1,810,840,525 in all: 1,533,879,336 compound, 91,186,488 ORF, 185,774,701 CRISPR; counts include source_7 and exclude source_15 and the pilot datasets; the page's status heading reads 2024/12, and the 2023 preprint [7] planned about 1.6 billion cells once complete). broadinstitute.github.io/jump_hub/explanations/data_description.html, accessed 25 October 2026, re-checked 26 October 2026, unchanged.
26. Pontén J, Saksela E. Two established in vitro cell lines from human mesenchymal tumours. *International Journal of Cancer* 2(5):434–447, 1967. doi:10.1002/ijc.2910020505. (U-2 OS, first called 2T: an osteosarcoma (bone cancer) line from the tibia of a 15-year-old girl, a cancer cell line, per Cellosaurus CVCL_0042 with ATCC HTB-96 and DSMZ ACC-785, checked 25 October 2026.)
27. Cimini BA, Chandrasekaran SN, Kost-Alimova M, et al. Optimizing the Cell Painting assay for image-based profiling. *Nature Protocols* 18(7):1981–2013, 2023. doi:10.1038/s41596-023-00840-9. (U2OS and A549 performed about equally; JUMP chose U2OS for its full dataset by a slim margin, because more public U2OS data existed. Checked against Crossref and the full text, PMC10536784.)
28. The author's experience in industry cell-imaging screens: a screening run cost about $50k and ran three times a week; one cell line checked late ran 17 weeks, about $2.6M (docs/whitepaper.html, Who pays). Months to wait for an answer by asking or re-running is the author's estimate, not a measurement.

The papers on slide 02, with the four that are not cited above (Kat Titterton's author position in brackets):

- Ollitrault G, … Titterton K, Ewald JD. Cell Painting and machine learning for mechanistic profiling of hepatotoxic botanicals and their constituents. *bioRxiv*, 12 October 2026. doi:10.64898/2026.10.05.756246 [6th of 7]
- Yanamandra K, … Titterton K, …. Conformation-specific anti-pathological tau antibody raised against AD brain-derived seed-competent tau reduces tau pathology in transgenic mice. *Molecular Neurodegeneration Advances* 2:43, 2026. doi:10.1186/s44477-026-00049-6 [15th of 20]
- Sebastian RM, … Titterton K, …. SynCAR platform for capturing neuronal synaptic proteopathic seeds. *iScience* 29(7):116362, 2026. PMID 42325569 [13th of 18]
- Manos JD, … Titterton K, …. Uncovering specificity of endogenous TAU aggregation in a human iPSC-neuron TAU seeding model. *iScience* 25(1):103658, 2022. PMID 35072001 [11th of 13]

Slide 02's record tiles: 8 peer-reviewed papers (references 1–5 and the Yanamandra, Sebastian and Manos papers above; two in *Nature Communications*, [2] and [4]); 2 patent applications on image-based bioactivity detection, filed at Axiom Bio and not yet published (count from the author, 25 October 2026); 100,000+ compounds imaged in two Cell Painting datasets whose assay development, QC and data generation the author oversaw at Axiom Bio (CV, macrofluidic.me/resume).

## 6. Documents

Designed companions to the deck, same type and colour, each a web page with a PDF beside it.

| document | web | PDF |
|---|---|---|
| Scientific background and industry position | [`docs/whitepaper.html`](docs/whitepaper.html) | [`docs/whitepaper.pdf`](docs/whitepaper.pdf) |
| Product vision | [`docs/product-vision.html`](docs/product-vision.html) | [`docs/product-vision.pdf`](docs/product-vision.pdf) |
| Roadmap | [`docs/roadmap.html`](docs/roadmap.html) | [`docs/roadmap.pdf`](docs/roadmap.pdf) |
| Competitive and collaborative landscape | [`docs/landscape.html`](docs/landscape.html) | [`docs/landscape.pdf`](docs/landscape.pdf) |
| Brand and design style | [`docs/brand.html`](docs/brand.html) | [`docs/brand.pdf`](docs/brand.pdf) |

## 7. Files

| file | what |
|---|---|
| `index.html` | the deck: one self-contained page, every slide written by the builders in `figures/` from `results/`, images inlined, fonts from Google Fonts |
| `datum-line-deck.pdf` | static vector PDF, 27 pages, printed from `index.html` by `figures/build_deck_pdf.py`; the click states of 02, 03, 04 and 05 become separate pages |
| `preview.png` | link-preview image: the title slide |
| `docs/` | the documents above, with an index page |
| `analysis/` | the scripts behind every number, with a reproduction guide |
| `results/` | what those scripts wrote: JSON, CSV and a generated summary |
| `figures/` | builders that write the slides and documents from `results/` |

## 8. Colophon

Archivo, IBM Plex Mono, Source Serif 4. Pink `#be1e74` is yours; green `#0f8f6c` is the field (a green–magenta pair, chosen to survive red–green colour blindness). Every figure is generated from data, never hand-drawn; every number traces to a results file or a numbered reference. This repository is the source of truth: the builders in `figures/` write the deck and the documents from `results/`.

Kat Titterton, San Francisco

## License

Code in this repository (`analysis/`, `figures/` builders and scripts) is MIT licensed; see [`LICENSE`](LICENSE). The deck, documents, text and figure designs are © 2026 Katherine Titterton, all rights reserved. Data shown comes from the public JUMP Cell Painting dataset (cpg0016), CC0.
