# Datum Line · Control is an illusion

**Confidence without control.** A pitch deck for the AI × Bio pitch contest, AWS Builder Loft, San Francisco, 29 September 2026.

**View it:** https://kat-titter.github.io/datum-line/ · **PDF:** [`datum-line-deck.pdf`](datum-line-deck.pdf)

---

## 1. The idea

Every result in biology is a difference from a control, and nobody checks the control. A plate can pass every local QC rule while its untreated wells look like a different institution's. Normal is a comparison you cannot make alone.

Datum Line places your control wells against every lab running the same line, from images you already take, and returns a certificate: in distribution or not, and which features moved.

## 2. How to read the deck

- **Scroll**, or use **↑ ↓ / Space / Page Up·Down**. **Home / End** jump to either end.
- Slides **04** and **05** are interactive: **click** (or press **→**) to step through three states.
- Animations play as each slide scrolls into view.
- Slides 01–08 are the four-minute talk. The **appendix** (A0–A10) holds method and evidence for questions; A0 is an index from question to slide.

## 3. The evidence

All data shown is public: the **JUMP Cell Painting** consortium dataset (cpg0016), CC0. Untreated (DMSO) wells from seven institutions; a classifier names the institution from control wells alone at 96.2% balanced accuracy against 14.3% chance, held out by plate. Per-batch whitening, the standard correction, drops it to 12%: below chance, deleting the coordinate a certificate needs.

The shown work is fluorescence (Cell Painting). The product bets on label-free brightfield; that test is labelled pending in the appendix (A10).

## 4. References cited in the deck

1. Ewald JD, Titterton KL, et al. Cell Painting for cytotoxicity and mode-of-action analysis in primary human hepatocytes. *Cell Systems*, 2026.
2. Seal S, Dee W, … Titterton K, … Carpenter AE. Counting cells can accurately predict small-molecule bioactivity benchmarks. *Nature Communications*, 2026.
3. Wu JW, Titterton K, et al. A neuronal tau aggregation assay for tau-related drug discovery. *J Biol Chem*, 2025.
4. Chandrasekaran SN, et al. JUMP Cell Painting dataset. *bioRxiv*, 2023.
5. Bray MA, et al. Cell Painting. *Nature Protocols* 11:1757, 2016.
6. Freedman LP, Cockburn IM, Simcoe TS. The economics of reproducibility in preclinical research. *PLoS Biology* 13(6):e1002165, 2015.

## 5. Files

| file | what |
|---|---|
| `index.html` | the deck: one self-contained page, images inlined, fonts from Google Fonts |
| `datum-line-deck.pdf` | static vector PDF, 23 pages; click states of 04 and 05 become three pages each |
| `preview.png` | link-preview image |

## 6. Colophon

Archivo, IBM Plex Mono, Source Serif 4. Pink `#be1e74` is yours; green `#0f8f6c` is the field (a green–magenta pair, chosen to survive red–green colour blindness). Every figure is generated from data, never hand-drawn; every number traces to a results file or a numbered reference.

Kat Titterton · San Francisco
