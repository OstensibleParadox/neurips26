"""Regression tests for the repaired synthetic ground-truth calculation."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from unittest import mock
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).with_name("run_synthetic.py")
SPEC = importlib.util.spec_from_file_location("synthetic_ground_truth_runner", MODULE_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - importlib invariant
    raise RuntimeError(f"cannot load {MODULE_PATH}")
SYNTHETIC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNTHETIC
SPEC.loader.exec_module(SYNTHETIC)


def manual_softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=-1, keepdims=True)
    values = np.exp(shifted)
    return values / values.sum(axis=-1, keepdims=True)


def manual_balanced_js_nats(q0: np.ndarray, q1: np.ndarray) -> float:
    midpoint = 0.5 * (q0 + q1)
    kl0 = np.sum(q0 * np.log(q0 / midpoint), axis=1)
    kl1 = np.sum(q1 * np.log(q1 / midpoint), axis=1)
    return float(np.mean(0.5 * kl0 + 0.5 * kl1))


class SyntheticGroundTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.T = SYNTHETIC.generate_contexts(n=192, d_tilde=8, seed=7)
        cls.W = SYNTHETIC.generate_mechanism_weights(
            d_tilde=8,
            n_classes=5,
            seed=19,
        )

    def test_beta_zero_is_exactly_zero_for_any_nonnegative_noise(self) -> None:
        for noise_std in (0.0, 0.1, 1.0, 5.0):
            with self.subTest(noise_std=noise_std):
                value = SYNTHETIC.true_conditional_mi(
                    self.T,
                    self.W,
                    0.0,
                    noise_std=noise_std,
                    gt_inner_samples=16,
                    gt_seed=3,
                    gt_batch_size=11,
                )
                self.assertEqual(value, 0.0)

    def test_zero_noise_matches_direct_distribution_sum(self) -> None:
        beta_h = 1.25
        base = np.einsum(
            "nd,dk->nk",
            self.T.astype(np.float64),
            self.W.astype(np.float64),
            optimize=True,
        )
        shifted = base.copy()
        shifted[:, 0] += beta_h
        expected = manual_balanced_js_nats(
            manual_softmax(base),
            manual_softmax(shifted),
        )
        actual = SYNTHETIC.true_conditional_mi(
            self.T,
            self.W,
            beta_h,
            noise_std=0.0,
            gt_inner_samples=1,
            gt_seed=999,
            gt_batch_size=13,
        )
        self.assertAlmostEqual(actual, expected, places=13)

    def test_true_mi_does_not_depend_on_sampled_actions(self) -> None:
        common = dict(
            n=192,
            d_tilde=8,
            n_classes=5,
            beta_h=2.0,
            seed=23,
            mechanism_seed=29,
            noise_std=0.1,
            gt_inner_samples=64,
            gt_seed=31,
            gt_batch_size=17,
        )
        T1, H1, A1, probs1, mi1 = SYNTHETIC.generate_data(
            **common,
            action_seed=101,
        )
        T2, H2, A2, probs2, mi2 = SYNTHETIC.generate_data(
            **common,
            action_seed=202,
        )
        np.testing.assert_array_equal(T1, T2)
        np.testing.assert_array_equal(H1, H2)
        np.testing.assert_array_equal(probs1, probs2)
        self.assertTrue(np.any(A1 != A2), "test action seeds unexpectedly agreed")
        self.assertEqual(mi1, mi2)

    def test_true_mi_is_monotone_in_hidden_shift(self) -> None:
        values = [
            SYNTHETIC.true_conditional_mi(
                self.T,
                self.W,
                beta_h,
                noise_std=0.0,
                gt_inner_samples=1,
                gt_seed=41,
                gt_batch_size=19,
            )
            for beta_h in (0.0, 0.5, 1.0, 2.0, 4.0)
        ]
        self.assertTrue(
            all(right >= left for left, right in zip(values, values[1:])),
            values,
        )
        self.assertGreater(values[-1], values[1])

    def test_ground_truth_batching_does_not_change_result(self) -> None:
        kwargs = dict(
            noise_std=0.3,
            gt_inner_samples=96,
            gt_seed=43,
        )
        one_at_a_time = SYNTHETIC.true_conditional_mi(
            self.T,
            self.W,
            1.5,
            gt_batch_size=1,
            **kwargs,
        )
        full_batch = SYNTHETIC.true_conditional_mi(
            self.T,
            self.W,
            1.5,
            gt_batch_size=len(self.T),
            **kwargs,
        )
        self.assertAlmostEqual(one_at_a_time, full_batch, places=14)

    def test_mechanism_weights_are_independent_of_sample_count(self) -> None:
        original = SYNTHETIC.generate_mechanism_weights
        observed = []

        def capture(d_tilde: int, n_classes: int, seed: int) -> np.ndarray:
            weights = original(d_tilde, n_classes, seed)
            observed.append(weights.copy())
            return weights

        with mock.patch.object(
            SYNTHETIC,
            "generate_mechanism_weights",
            side_effect=capture,
        ):
            SYNTHETIC.generate_data(
                n=7,
                mechanism_seed=47,
                beta_h=0.0,
                gt_inner_samples=1,
            )
            SYNTHETIC.generate_data(
                n=103,
                mechanism_seed=47,
                beta_h=0.0,
                gt_inner_samples=1,
            )

        self.assertEqual(len(observed), 2)
        np.testing.assert_array_equal(observed[0], observed[1])


if __name__ == "__main__":
    unittest.main()
