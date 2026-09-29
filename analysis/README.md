# Analysis: how every number in the deck is produced

Every number on the deck's evidence slides is read from a file in [`results/`](../results/),
and every file in `results/` is written by a script in this folder, run on public data.
[`results/SUMMARY.md`](../results/SUMMARY.md) is the full table, generated from the JSON files.

Data: JUMP Cell Painting, `cpg0016-jump`, CC0, from the Cell Painting Gallery. No credentials.
"Untreated" means DMSO wells. "Lab" means a JUMP source. The JUMP metadata is pinned to the
commit in [`metadata/COMMIT`](../metadata/COMMIT).

## Reproduce

Python 3.9, about 20 GB of disk, about three hours of download the first time.

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
git clone https://github.com/jump-cellpainting/datasets jump && git -C jump checkout 016e865 && cp jump/metadata/*.csv* metadata/
```

```bash
PATH=.venv/bin:$PATH sh analysis/run_all.sh
```

[`run_all.sh`](run_all.sh) runs the tests, the two downloads and every analysis in order.
The downloads cache one file per plate and resume if interrupted. To run one script, put
`analysis/` on the Python path: `PYTHONPATH=analysis python analysis/e9_replay.py`.

Then write the slides, the documents and the PDF from the results:

```bash
PYTHONPATH=figures python figures/build_evidence.py && python figures/build_docs.py && python figures/build_script.py
```

## What each script does

| script | question | writes |
|---|---|---|
| `e1_pull_wells.py` | fetch the untreated wells of every compound plate | `cache/wells/` |
| `e8_pull_wells.py` | fetch untreated and positive-control wells of every compound plate | `cache/poscon/` |
| `field.py` | shared loading and geometry; the judged lab never sets its own scale | |
| `e1_lab_classifier.py` | can a classifier name the lab from untreated wells, on plates it never saw? | `e1.json`, `e1-predictions.csv` |
| `e1_vote.py` | how does that classifier vote on one plate? | `e1-vote-PLATE.json` |
| `e1_redteam.py` | does e1 survive held-out batches, one microscope model, one feature family, plate centring? | `e1-redteam.json` |
| `e2_plate_position.py` | where does one plate sit relative to every lab? | `e2-plate-position-PLATE.json`, `e2-embedding.csv` |
| `e1b_drift.py` | how far apart are two plates of one lab, by time between them? | `e1b-drift-LAB.json` |
| `plate_cell_count.py` | is a plate's cell count normal for its lab? | `cell-count-PLATE.json` |
| `e9_replay.py` | what would each batch of each lab have been told, judged with only its own past? | `e9-replay.json`, `e9-replay-redteam.json` |
| `e6_what_moved.py` | which features moved, by channel and measurement? | `e6-what-moved-LAB.json` |
| `e10_certificate_predicts_answer.py` | does the certificate's drift predict how far a drug's answer has moved? | `e10-certificate-predicts-answer.json` |
| `e11_known_answer.py` | did the positive controls come out, batch by batch, and if not, where did the effect go? | `e11-known-answer.json` |
| `e8_same_drug_different_answer.py`, `e8_redteam.py` | do labs agree on what a fixed compound does? | `e8-*.json` |
| `summarise_results.py` | one table of every headline number | `SUMMARY.md` |
| `tests/test_field.py` | batch order, scaling, the replay and the failure rule, on synthetic data | |
| `e5`, `e7`, `pull_game_tiles.py` | written, not yet run on the full data | |

The builders in [`figures/`](../figures/) write whole slides from these files and can be run
again at any time: `build_evidence.py` (slides 05, 06, 10 and boards A8, A9, A11, A12),
`build_docs.py` (six documents, from the originals kept as text in `figures/assets/docs-original/`),
`build_script.py` (every spoken line, the clock and the run of show; it fails if the pitch runs over five minutes) and `build_deck_pdf.py`.
`figures/history/` holds the one-off builders that first carried the verified numbers into
slide 04 and boards A2, A3, A6 and A10.

## What did not reproduce

Earlier versions of the deck carried numbers whose code and results were never on disk.
On 28 and 29 September 2026 the analysis was rebuilt to the written specification and run
on the complete data. Three claims changed.

| earlier claim | what the data says |
|---|---|
| 96.2% balanced accuracy on 12,046 wells, 7 labs | 99.9% on 93,228 wells, 11 labs. The earlier well set is unknown. |
| All 384 wells of plate 1053600681 classify as another lab | All 384 are named as its own lab. The plate is typical of lab 2. |
| Drift between runs rises to about three times the same-day distance, then plateaus | It keeps rising in lab 2: about five times at 6 to 13 weeks and seven times beyond. No plateau. |

What replaced the plate story is the replay in `e9-replay.json`: lab 2's last three batches,
from 30 August 2021, sit further from the lab's own June baseline than from another lab,
while their cell counts are inside the lab's own range.

## Red team

Each test changes one thing. Numbers are in `e1-redteam.json`, `e9-replay-redteam.json`,
`e10-certificate-predicts-answer.json` and `e8-redteam.json`.

| claim | objection | test | outcome |
|---|---|---|---|
| labs are recognisable | the model memorised the labels | training labels shuffled | falls to chance |
| | plates from one run leak across the split | whole batches held out | holds |
| | it recognises the microscope model | labs on one model only | holds |
| | one kind of feature carries it | one feature family at a time | every family names the lab |
| | a trivial feature carries it | best single features alone | image area in pixels names about half the wells: part of the signature is camera format |
| | plate normalisation would remove it | each plate centred on its own controls | falls to about a quarter, above chance |
| lab 2 moved | the baseline was chosen to make it so | first two, or first three, batches as baseline | holds; with three, which takes in the June batch whose cell count fell, three more batches flag |
| | a few extreme features carry it | no clipping; cell-level only; image-level only | holds |
| | all-vehicle plates were handled differently | all-vehicle plates removed | holds |
| | it depends on which lab happens to be nearest | the nearest labs removed from the field | holds |
| | the flag fires all the time | every lab replayed | 6 of 129 batches, in 3 of 11 labs |
| drift predicts the answer | drift and effect share the same control wells | drift from one half of the DMSO wells, effect against the other | holds |
| | one lab carries it | each lab with a flagged batch removed, then all of them | holds |
| | batches whose positive controls failed carry it | those batches removed | holds |
| same drug, different answer | a plate is compared with a field that includes its own lab | field is every other lab | holds |
| | the link is between labs, not inside them | lab means removed, plates shuffled inside labs | holds inside labs; between eleven labs, same sign, not established |

## How to read the results, and their limits

- **The classifier recognises a lab, not only its cells.** Every feature family names the lab
  on its own, including image-quality features that describe acquisition, not biology. The
  signature is the whole pipeline: instrument, staining, handling and cells together.
- **It is not the microscope model alone.** Labs on the same model are separated as well as
  all eleven.
- **The replay is hindsight.** Each batch is judged with only its own lab's past, but against
  the field as published in 2023. It shows what a lab uploading that batch today would be told.
- **The flagged batches are small.** Lab 2's hold 5, 6 and 14 plates. Every one of those 25
  plates is outside, and 2 of the other 194 are.
- **Flag and calendar are confounded inside lab 2.** Its flagged batches are its last three.
  The test of whether drift predicts the answer uses every lab, and holds without lab 2.
- **What moved is where to look, not why.** Stain intensity rose in two channels. Profiles
  cannot tell a stain lot or an exposure setting from biology.
- **The failed positive controls are unexplained.** In four batches of one lab the wells the
  public plate map labels as positive controls show no effect, and no other well on the probed
  plates does. The data cannot say whether compounds were left out or the map is wrong.
- **Distances are measured in the full feature space.** The scatter on the slides is a PCA of
  a subsample, for the eye only.
- **One plate is left out.** A lab 11 profile names its plate `EC000157real`, which the
  metadata does not know, so it cannot be placed in run order.
- **Fluorescence only.** All of this is Cell Painting. Label-free brightfield is untested.
