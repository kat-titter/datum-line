# Datum Line

**Do my cells look normal? Confidence with controls.** Datum Line makes cell data from any lab comparable with any other lab's. Labs put their cells on the map for free; companies that buy cell data pay for the certificate.

**View it:** https://kat-titter.github.io/datum-line/ · **PDF:** [`datum-line-deck.pdf`](datum-line-deck.pdf) · **Documents:** [`docs/`](https://kat-titter.github.io/datum-line/docs/)

---

## 1. The idea

Every result in biology is a difference from a control, and nobody checks the control against anyone else's. A plate can pass every local QC rule while its untreated wells look like a different lab's. Normal is a comparison you cannot make alone.

Datum Line places a lab's control wells on a map of every lab running the same line, from images it already takes, and says where its cells sit, how far they have moved and which features moved. It starts as a map; it can grow into a certificate, then an exchange for cell data any lab can trust.

## 2. How to read the deck

- **Scroll**, or use **↑ ↓ / Space / Page Up·Down**. **Home / End** jump to either end.
- Slides **02**, **05**, **06** and **07** step through states: **click** (or press **→**). Three on 02 and 07, two on 05 and 06.
- Animations play as each slide scrolls into view.
- Slides 01–10 are the talk: the question, one lab or six, how labs answer it today, the founder, the map, the data economy and why the map compounds, the product (the box, the game, the exchange), who else, what the money buys, and where it goes with the ask. The **appendix** (A1–A24) holds method and evidence for questions; A0 is an index from question to board.

## 3. The evidence

All data shown is public: the **JUMP Cell Painting** consortium dataset (cpg0016), CC0.

- **Labs are recognisable.** On 93,228 untreated (DMSO) wells from 1,872 plates in eleven labs, a classifier names the lab from control wells alone at 99.9% balanced accuracy against 9.1% chance, on plates it never saw.
- **A lab can move without seeing it.** Replayed batch by batch, one lab's last three batches sit further from its own June baseline than from another lab, while their cell counts stay inside the lab's own range. Across the field 6 of 129 batches do this.
- **The move predicts the answer.** Inside labs, the further a batch has drifted, the less its measured effect of the same positive controls agrees with the lab's own first batch: Spearman -0.71 over 118 batches.
- **A known answer can fail silently.** In four consecutive batches of one lab, 65 plates, the wells the public plate map labels as positive controls show no effect.

Every number is produced by a script in [`analysis/`](analysis/) and stored in [`results/`](results/). [`results/SUMMARY.md`](results/SUMMARY.md) is the full table, and [`analysis/README.md`](analysis/README.md) says how to reproduce it, what did not reproduce from earlier versions of this deck, how each claim was red-teamed, and its limits.

The evidence shown is fluorescence (Cell Painting). The product bets on label-free brightfield: a frozen vision model already names the lab from one brightfield image at 99.6% across 8 labs (`results/e15`); placing a raw image on the map is next (A10, A19).

## 4. Business model

Proposed, not yet validated. Labs and cores put their cells on the map for free; they are the map. Companies that buy cell data they did not make pay for the certificate: per certificate on a dataset they bought, or per line per quarter (~$5–15k) for groups that screen continuously. The map, the box and the code stay open. One way it grows: an exchange for certified, comparable cell data, where the lab that made a dataset keeps a share of every sale. Why now: data sells, and cell data does not convert between sites [10]–[13]. Details on boards A15, A21 to A24.

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
11. Recursion. Recursion reports third quarter 2025 financial results and provides business update. Press release, 5 November 2025.
12. Jungco K. Google, Meta join $1.8B push to build AI “virtual cells”: here’s what we know. eWeek, 9 October 2026.
13. Wolff C, …, Schmied C. Morphological profiling data resource enables prediction of chemical compound properties. *iScience* 28(5):112445, 2025.

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
| `datum-line-deck.pdf` | static vector PDF, 41 pages, printed from `index.html` by `figures/build_deck_pdf.py`; the click states of 02, 05, 06 and 07 become separate pages |
| `preview.png` | link-preview image: the title slide |
| `docs/` | the documents above, with an index page |
| `analysis/` | the scripts behind every number, with a reproduction guide |
| `results/` | what those scripts wrote: JSON, CSV and a generated summary |
| `figures/` | builders that write the slides and documents from `results/` |

## 8. Colophon

Archivo, IBM Plex Mono, Source Serif 4. Pink `#be1e74` is yours; green `#0f8f6c` is the field (a green–magenta pair, chosen to survive red–green colour blindness). Every figure is generated from data, never hand-drawn; every number traces to a results file or a numbered reference. This repository is the source of truth: the builders in `figures/` write the deck and the documents from `results/`.

Kat Titterton · San Francisco

## License

Code in this repository (`analysis/`, `figures/` builders and scripts) is MIT licensed; see [`LICENSE`](LICENSE). The deck, documents, text and figure designs are © 2026 Katherine Titterton, all rights reserved. Data shown comes from the public JUMP Cell Painting dataset (cpg0016), CC0.
