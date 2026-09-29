# Datum Line · Control is an illusion

**Confidence without control.** Every plate you image, placed in the field. A pitch for the AI × Bio pitch contest, AWS Builder Loft, San Francisco, 29 September 2026.

**View it:** https://kat-titter.github.io/datum-line/ · **PDF:** [`datum-line-deck.pdf`](datum-line-deck.pdf) · **Documents:** [`docs/`](https://kat-titter.github.io/datum-line/docs/)

---

## 1. The idea

Every result in biology is a difference from a control, and nobody checks the control against anyone else's. A plate can pass every local QC rule while its untreated wells look like a different institution's. Normal is a comparison you cannot make alone.

Datum Line places your control wells against every lab running the same line, from images you already take, and returns a certificate: in distribution or not, and which features moved. The vision: every plate you image, placed in the field, with nobody lifting a finger.

## 2. How to read the deck

- **Scroll**, or use **↑ ↓ / Space / Page Up·Down**. **Home / End** jump to either end.
- Slides **04** and **05** are interactive: **click** (or press **→**) to step through their states, three on 04 and four on 05.
- Animations play as each slide scrolls into view.
- Slides 01–10 are the four-minute talk: the question, the founder, the cost, the evidence (04, 05), the product, identity versus behaviour (07), who buys (08), the dataset built to break (09), and the vision and the ask (10). The **appendix** (A0–A12) holds method and evidence for questions; A0 is an index from question to slide.

## 3. The evidence

All data shown is public: the **JUMP Cell Painting** consortium dataset (cpg0016), CC0.

- **Labs are recognisable.** On 93,228 untreated (DMSO) wells from 1,872 plates in eleven labs, a classifier names the lab from control wells alone at 99.9% balanced accuracy against 9.1% chance, on plates it never saw.
- **A lab can move without seeing it.** Replayed batch by batch, one lab's last three batches sit further from its own June baseline than from another lab, while their cell counts stay inside the lab's own range. Across the field 6 of 129 batches do this.
- **The move predicts the answer.** Inside labs, the further a batch has drifted, the less its measured effect of the same positive controls agrees with the lab's own first batch: Spearman -0.71 over 118 batches.
- **A known answer can fail silently.** In four consecutive batches of one lab, 65 plates, the wells the public plate map labels as positive controls show no effect.

Every number is produced by a script in [`analysis/`](analysis/) and stored in [`results/`](results/). [`results/SUMMARY.md`](results/SUMMARY.md) is the full table, and [`analysis/README.md`](analysis/README.md) says how to reproduce it, what did not reproduce from earlier versions of this deck, how each claim was red-teamed, and its limits.

The shown work is fluorescence (Cell Painting). The product bets on label-free brightfield; that test is labelled pending in the appendix (A10).

## 4. Business model

Proposed, not yet validated. Academic labs and cores: free when they contribute control images, which build the reference. Pharma and CRO screening: a subscription per cell line per quarter (~$5–15k), against a ~$2.6M screen run on unchecked cells. Cell banks and vendors: a fee per certified lot. Bad-lot alerts across the network come later. Details in [`docs/roadmap.html`](docs/roadmap.html).

## 5. References cited in the deck

1. Ewald JD, Titterton KL, et al. Cell Painting for cytotoxicity and mode-of-action analysis in primary human hepatocytes. *Cell Systems*, 2026.
2. Seal S, Dee W, … Titterton K, … Carpenter AE. Counting cells can accurately predict small-molecule bioactivity benchmarks. *Nature Communications*, 2026.
3. Wu JW, Titterton K, et al. A neuronal tau aggregation assay for tau-related drug discovery. *J Biol Chem*, 2025.
4. Kang J, … Titterton K, … Boyden ES. Multiplexed expansion revealing for imaging multiprotein nanostructures in healthy and diseased brain. *Nature Communications*, 2024.
5. Wu B, Jayakar SS, … Titterton K, … Bruzik KS. Inhibitable photolabeling by a neurosteroid diazirine analog in the β3 subunit of GABA-A receptors. *Eur J Med Chem*, 2019.
6. Freedman LP, Cockburn IM, Simcoe TS. The economics of reproducibility in preclinical research. *PLoS Biology* 13(6):e1002165, 2015.
7. Chandrasekaran SN, et al. JUMP Cell Painting dataset. *bioRxiv*, 2023.
8. Bray MA, et al. Cell Painting. *Nature Protocols* 11:1757, 2016.

## 6. Documents

Designed companions to the deck, same type and colour, each a web page with a PDF beside it.

| document | web | PDF |
|---|---|---|
| Scientific background and industry position | [`docs/whitepaper.html`](docs/whitepaper.html) | [`docs/whitepaper.pdf`](docs/whitepaper.pdf) |
| Product vision | [`docs/product-vision.html`](docs/product-vision.html) | [`docs/product-vision.pdf`](docs/product-vision.pdf) |
| Roadmap | [`docs/roadmap.html`](docs/roadmap.html) | [`docs/roadmap.pdf`](docs/roadmap.pdf) |
| Competitive and collaborative landscape | [`docs/landscape.html`](docs/landscape.html) | [`docs/landscape.pdf`](docs/landscape.pdf) |
| Judge Q&A | [`docs/judge-qa.html`](docs/judge-qa.html) | [`docs/judge-qa.pdf`](docs/judge-qa.pdf) |
| Speaker script | [`docs/speaker-script.html`](docs/speaker-script.html) | [`docs/speaker-script.pdf`](docs/speaker-script.pdf) |
| Brand and design style | [`docs/brand.html`](docs/brand.html) | [`docs/brand.pdf`](docs/brand.pdf) |

## 7. Files

| file | what |
|---|---|
| `index.html` | the deck: one self-contained page built from the design canvas, images inlined, fonts from Google Fonts |
| `datum-line-deck.pdf` | static vector PDF, 28 pages, printed from `index.html` by `figures/build_deck_pdf.py`; the click states of 04 and 05 become three and four pages |
| `preview.png` | link-preview image |
| `docs/` | the documents above, with an index page |
| `analysis/` | the scripts behind every number, with a reproduction guide |
| `results/` | what those scripts wrote: JSON, CSV and a generated summary |
| `figures/` | builders that write the evidence slides, documents and script from `results/` |

## 8. Colophon

Archivo, IBM Plex Mono, Source Serif 4. Pink `#be1e74` is yours; green `#0f8f6c` is the field (a green–magenta pair, chosen to survive red–green colour blindness). Every figure is generated from data, never hand-drawn; every number traces to a results file or a numbered reference. The design canvas is the source of truth; everything here is built from it.

Kat Titterton · San Francisco
