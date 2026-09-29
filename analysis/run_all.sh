#!/bin/sh
# Every analysis, in order, from the repository root. About three hours the first time,
# almost all of it download; the pulls resume if interrupted.
set -e
export PYTHONPATH=analysis
python -m unittest discover analysis/tests
python analysis/e1_pull_wells.py
python analysis/e8_pull_wells.py
python analysis/e1_lab_classifier.py --perms 1
python analysis/e1_vote.py 1053600681
python analysis/e1_redteam.py
python analysis/e2_plate_position.py 1053600681
python analysis/e2_lab_timeline.py source_2
python analysis/e1b_drift.py source_2
python analysis/plate_cell_count.py 1053600681
python analysis/e9_replay.py
python analysis/e9_replay.py source_2 --redteam
python analysis/e6_what_moved.py source_2
python analysis/e10_certificate_predicts_answer.py
python analysis/e11_known_answer.py
python analysis/e8_redteam.py
python analysis/summarise_results.py
