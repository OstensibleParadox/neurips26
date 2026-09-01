from __future__ import annotations

import unittest

from tracetwin import (
    analytic_values,
    clamped_joint,
    conditional_mutual_information,
    passive_joint,
    total_variation,
    visible_marginal,
)


class TraceTwinTests(unittest.TestCase):
    def setUp(self) -> None:
        self.p = 0.2
        self.rho = 0.1

    def test_passive_visible_laws_are_identical(self) -> None:
        bypass = visible_marginal(passive_joint("bypass", self.p, self.rho))
        mediated = visible_marginal(passive_joint("mediated", self.p, self.rho))
        self.assertLess(total_variation(bypass, mediated), 1e-14)

    def test_passive_cmi_matches_distinct_analytic_values(self) -> None:
        expected = analytic_values(self.p, self.rho)
        bypass = conditional_mutual_information(passive_joint("bypass", self.p, self.rho))
        mediated = conditional_mutual_information(passive_joint("mediated", self.p, self.rho))
        self.assertAlmostEqual(bypass, expected["passive_bypass_cmi_bits"], places=12)
        self.assertAlmostEqual(mediated, 0.0, places=12)

    def test_clamped_and_passive_estimands_differ_at_interior_p(self) -> None:
        expected = analytic_values(self.p, self.rho)
        bypass = conditional_mutual_information(clamped_joint("bypass", self.p, self.rho))
        mediated = conditional_mutual_information(clamped_joint("mediated", self.p, self.rho))
        self.assertAlmostEqual(bypass, expected["clamped_bypass_cmi_bits"], places=12)
        self.assertAlmostEqual(mediated, 0.0, places=12)
        self.assertNotAlmostEqual(
            bypass, expected["passive_bypass_cmi_bits"], places=6
        )

    def test_estimand_values_can_coincide_at_p_half(self) -> None:
        expected = analytic_values(0.5, self.rho)
        self.assertAlmostEqual(
            expected["passive_bypass_cmi_bits"],
            expected["clamped_bypass_cmi_bits"],
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
