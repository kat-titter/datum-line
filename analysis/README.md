# Analysis: how every number in the deck is produced

Every number on the deck's evidence slides is read from a file in [`results/`](../results/),
and every file in `results/` is written by a script in this folder, run on public data.
[`results/SUMMARY.md`](../results/SUMMARY.md) is the full table, generated from the JSON files.

Data: JUMP Cell Painting, `cpg0016-jump`, CC0, from the Cell Painting Gallery. No credentials.
"Untreated" means DMSO wells. "Lab" means a JUMP source. The JUMP metadata is pinned to the
commit in [`metadata/COMMIT`](../metadata/COMMIT).

## Reproduce

Python 3.9, about 10 GB of disk, about two hours of download.

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
git clone https://github.com/jump-cellpainting/datasets jump && git -C jump checkout 016e865 && ln -s jump/metadata metadata
```

Pull the untreated wells of every compound plate, 1,872 plates, resumable:

```bash
python analysis/e1_pull_wells.py
```

```bash
python analysis/e1_lab_classifier.py --perms 1
python analysis/e1_vote.py 1053600681
python analysis/e2_plate_position.py 1053600681
python analysis/e2_lab_timeline.py source_2
python analysis/e1b_drift.py source_2
python analysis/plate_cell_count.py 1053600681
python analysis/e1_redteam.py
python analysis/e8_pull_wells.py metadata results/e8_profiles.parquet --per-source 25
python analysis/e8_same_drug_different_answer.py results/e8_profiles.parquet metadata
python analysis/e8_redteam.py results/e8_profiles.parquet
python analysis/summarise_results.py
```

Run the scripts from the repository root with `analysis/` on the Python path
(`PYTHONPATH=analysis`), since several import `e1_lab_classifier`.

## What each script does

| script | question | writes |
|---|---|---|
| `e1_pull_wells.py` | fetch the untreated wells of every compound plate | `cache/wells/` |
| `e1_lab_classifier.py` | can a classifier name the lab from untreated wells, on plates it never saw? | `e1.json`, `e1-predictions.csv` |
| `e1_vote.py` | how does that classifier vote on one plate? | `e1-vote-PLATE.json` |
| `e1_redteam.py` | does e1 survive held-out batches, one microscope model, one feature family, plate centring? | `e1-redteam.json` |
| `e2_plate_position.py` | where does one plate sit relative to every lab? Which plates sit nearer another lab? | `e2-plate-position-PLATE.json`, `e2-embedding.csv`, `e2-displaced-plates.csv` |
| `e2_lab_timeline.py` | batch by batch, does a lab's cell count move, and does its position? | `e2-timeline-LAB.json` |
| `e1b_drift.py` | how far apart are two plates of one lab, by time between them? | `e1b-drift-LAB.json` |
| `plate_cell_count.py` | is a plate's cell count normal for its lab? | `cell-count-PLATE.json` |
| `e8_pull_wells.py` | fetch untreated and positive-control wells | `e8_profiles.parquet` |
| `e8_same_drug_different_answer.py` | do labs agree on what a fixed compound does? | `e8-same-drug-different-answer.json` |
| `e8_redteam.py` | does e8 survive leaving the plate's own lab out of the field, and is the effect inside labs or between them? | `e8-redteam.json` |
| `summarise_results.py` | one table of every headline number | `SUMMARY.md` |
| `e5`, `e6`, `e7`, `pull_game_tiles.py` | written, not yet run on the full data | |

The deck's evidence slides are rebuilt from these files by
[`figures/build_slide05.py`](../figures/build_slide05.py) and
[`figures/build_slides_04_06.py`](../figures/build_slides_04_06.py).

## What did not reproduce

Earlier versions of the deck carried numbers whose code and results were never on disk.
On 28 and 29 September 2026 the analysis was rebuilt to the written specification and run
on the complete data. Three claims changed.

| earlier claim | what the data says |
|---|---|
| 96.2% balanced accuracy on 12,046 wells, 7 labs | 99.9% on 93,228 wells, 11 labs. The earlier well set is unknown. |
| All 384 wells of plate 1053600681 classify as another lab | All 384 are named as its own lab. The plate is typical of lab 2. |
| Drift between runs rises to about three times the same-day distance, then plateaus | It keeps rising in lab 2: about five times at 6 to 13 weeks and seven times beyond. No plateau. |

What replaced the plate story is in `e2-timeline-source_2.json`: lab 2's cell counts stay
inside their range from June to October 2021, while its October plates sit further from the
lab's own June baseline than from another lab's centre.

## Red team

Each test changes one thing about e1. Numbers are in `results/e1-redteam.json` and
`results/e8-redteam.json`.

| objection | test | outcome |
|---|---|---|
| The model memorised the labels | training labels shuffled | falls to chance |
| Plates from one imaging run leak across the split | whole batches held out | holds |
| It recognises the microscope model | four labs on one model only | holds |
| All-vehicle plates were handled differently | all-vehicle plates removed | holds |
| Position and count features carry it | those features removed | holds |
| One kind of feature carries it | one feature family at a time | every family names the lab |
| A trivial feature carries it | best single features alone | image area in pixels names about half the wells: part of the signature is camera format |
| Plate normalisation would remove it | each plate centred on its own controls | falls to about a quarter, above chance |
| e8 compares a plate with a field that includes its own lab | field is every other lab | holds |
| e8's link is between labs, not inside them | lab means removed, plates shuffled inside labs | holds inside labs; between eleven labs, same sign, not established |
| The October plates are outliers in a few features | z-scores clipped, features removed, 50 principal components | holds in every variant |

## How to read the results, and their limits

- **The classifier recognises a lab, not only its cells.** Every feature family names the lab
  on its own, including image-quality features that describe acquisition, not biology. The
  signature is the whole pipeline: instrument, staining, handling and cells together.
- **It is not the microscope model alone.** Four labs on the same model are separated as well
  as all eleven.
- **Distances are measured in the full feature space.** The scatter on the slides is a PCA of
  a subsample, for the eye only.
- **e8 is strongest inside labs.** Plates whose controls sit further from the field disagree
  more about a compound, inside every lab. Across eleven labs the trend has the same sign,
  and eleven points cannot establish it.
- **Why lab 2 moved is not known.** The data shows that it moved and when. Reagent lot,
  instrument service, protocol change and cell state are not distinguishable from profiles.
- **Fluorescence only.** All of this is Cell Painting. Label-free brightfield is untested.
