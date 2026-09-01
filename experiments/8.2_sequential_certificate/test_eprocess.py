from __future__ import annotations

import math
import unittest

import numpy as np

from eprocess import EvidenceProcess, OnlineActionDecoder


class EProcessTests(unittest.TestCase):
    def test_one_step_null_conditional_mean_is_one(self) -> None:
        design = np.asarray([0.3, 0.7])
        decoder = np.asarray([0.8, 0.2])
        factors = decoder / design
        self.assertAlmostEqual(float(np.sum(design * factors)), 1.0, places=12)

    def test_ville_threshold_uses_running_maximum(self) -> None:
        process = EvidenceProcess(alpha=0.05)
        process.update(0, [0.99, 0.01], [0.5, 0.5])
        first_p = process.anytime_p_value
        process.update(1, [0.99, 0.01], [0.5, 0.5])
        self.assertEqual(process.anytime_p_value, first_p)

    def test_decoder_prediction_precedes_fit(self) -> None:
        decoder = OnlineActionDecoder(prior=0.5)
        before = decoder.predict("approve")
        decoder.fit_observation("approve", 1)
        after = decoder.predict("approve")
        self.assertTrue(np.allclose(before, [0.5, 0.5]))
        self.assertGreater(after[1], after[0])

    def test_design_requires_full_support(self) -> None:
        process = EvidenceProcess()
        with self.assertRaises(ValueError):
            process.update(0, [0.5, 0.5], [1.0, 0.0])

    def test_threshold_equivalence(self) -> None:
        process = EvidenceProcess(alpha=0.05)
        self.assertAlmostEqual(math.log(1 / process.alpha), math.log(20.0))


if __name__ == "__main__":
    unittest.main()
