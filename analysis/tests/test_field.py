"""Checks on the shared geometry, on small synthetic data. Run from the repository root:

    PYTHONPATH=analysis python -m unittest discover analysis/tests
"""
import unittest

import numpy as np
import pandas as pd

import field as fd
import e9_replay as e9
import e10_certificate_predicts_answer as e10


def synthetic(shift_last_batch=0.0, n_features=40, seed=0):
    """Three labs, four dated batches each, three plates per batch, eight wells per plate."""
    rng = np.random.default_rng(seed)
    centre = {'source_1': 0.0, 'source_2': 6.0, 'source_3': -6.0}
    rows, X = [], []
    for lab, c in centre.items():
        for b in range(4):
            for p in range(3):
                for w in range(8):
                    rows.append({'Metadata_Source': lab, 'Metadata_Batch': f'2021060{b + 1}_run{b}',
                                 'Metadata_Plate': f'{lab}-{b}-{p}', 'Metadata_Well': f'A{w:02d}',
                                 fd.COUNT: 100.0, 'Metadata_AllVehicle': False})
                    x = rng.normal(c, 1.0, n_features)
                    if lab == 'source_1' and b == 3:
                        x = x + shift_last_batch
                    X.append(x)
    d = pd.DataFrame(rows)
    return d, pd.DataFrame(np.array(X, 'float32'), columns=[f'Cells_Texture_f{i}' for i in range(n_features)])


class BatchOrder(unittest.TestCase):
    def test_dates_in_every_format_jump_uses(self):
        self.assertEqual(str(fd.batch_date('20210607_Batch_2').date()), '2021-06-07')
        self.assertEqual(str(fd.batch_date('2021_05_31_U2OS_48_hr_run1').date()), '2021-05-31')
        self.assertEqual(str(fd.batch_date('p210824CPU2OS48hw384exp022JUMP').date()), '2021-08-24')
        self.assertEqual(str(fd.batch_date('JUMPCPE-20210623-Run01_20210624_003152').date()), '2021-06-23')
        self.assertEqual(str(fd.batch_date('Batch1_20221004').date()), '2022-10-04')
        self.assertIsNone(fd.batch_date('CP_25_all_Phenix1'))

    def test_order_is_by_date_not_by_name(self):
        order, _ = fd.ordered_batches(['20210808_Batch_4', '20210712_Batch_5', '20210607_Batch_2'])
        self.assertEqual(order, ['20210607_Batch_2', '20210712_Batch_5', '20210808_Batch_4'])

    def test_undated_batches_order_by_run_number(self):
        order, dates = fd.ordered_batches(['CP_36_all_Phenix1', 'CP59', 'CP_25_all_Phenix1', 'Batch10', 'Batch9'])
        self.assertEqual(order, ['Batch9', 'Batch10', 'CP_25_all_Phenix1', 'CP_36_all_Phenix1', 'CP59'])
        self.assertTrue(all(v is None for v in dates.values()))


class Scale(unittest.TestCase):
    def test_the_judged_lab_never_sets_the_scale(self):
        d, X = synthetic()
        before = fd.Field(d, X, 'source_1')
        X2 = X.copy()
        X2.loc[d.Metadata_Source == 'source_1'] += 100.0      # move only the judged lab
        after = fd.Field(d, X2, 'source_1')
        others = before.lab != 'source_1'
        np.testing.assert_allclose(before.cent[others], after.cent[others], atol=1e-5)
        self.assertAlmostEqual(before.spread, after.spread, places=5)

    def test_every_plate_is_one_row(self):
        d, X = synthetic()
        F = fd.Field(d, X, 'source_1')
        self.assertEqual(len(F.plates), d.Metadata_Plate.nunique())
        self.assertTrue((F.n_wells == 8).all())


class Replay(unittest.TestCase):
    def test_a_stable_lab_is_never_flagged(self):
        d, X = synthetic(shift_last_batch=0.0)
        r = e9.replay(fd.Field(d, X, 'source_1'), 'source_1')
        self.assertEqual(e9.verdicts(r), '....')

    def test_a_batch_that_moves_next_to_another_lab_is_flagged(self):
        d, X = synthetic(shift_last_batch=5.0)                 # lab 1's last batch lands near lab 2
        r = e9.replay(fd.Field(d, X, 'source_1'), 'source_1')
        self.assertEqual(e9.verdicts(r), '...O')
        self.assertEqual(r['batches'][-1]['nearest_other'], 'source_2')

    def test_cell_count_verdict_uses_only_the_past(self):
        d, X = synthetic()
        d.loc[d.Metadata_Batch == '20210603_run2', fd.COUNT] = 50.0
        r = e9.replay(fd.Field(d, X, 'source_1'), 'source_1')
        self.assertEqual([b['cell_count_vs_own_history'] for b in r['batches']], [None, None, 'below', 'inside'])


class KnownAnswer(unittest.TestCase):
    def test_a_batch_with_no_effect_is_failed_and_others_are_not(self):
        lab = pd.Series(['a'] * 5)
        agreement = pd.Series([0.8, 0.8, 0.1, 0.8, 0.2])
        size = pd.Series([30.0, 28.0, 3.0, 31.0, 29.0])       # low agreement alone is not failure
        self.assertEqual(list(e10.positive_controls_failed(agreement, size, lab)), [False, False, True, False, False])


if __name__ == '__main__':
    unittest.main()
