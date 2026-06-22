import FiniteQuerySandbox.InfoTheory

namespace FiniteQuerySandbox

noncomputable section

open scoped Real

/-- Entropy of an `N`-point quantized random variable is bounded by `log₂ N`. -/
theorem quantized_entropy_bound {N : ℕ} (_hN : 0 < N) (P : FinitePMF (Fin N)) :
    entropy P ≤ Real.log (N : ℝ) / Real.log 2 := by
  simpa using (entropy_le_log_card P)

/-- Entropy of a `d`-dimensional `Q`-ary quantized vector is at most `d log₂ Q`. -/
theorem quantized_vector_entropy_bound {d Q : ℕ} (_hd : 0 < d) (hQ : 0 < Q)
    (P : FinitePMF (Fin (Q ^ d))) :
    entropy P ≤ (d : ℝ) * Real.log (Q : ℝ) / Real.log 2 := by
  have hN : 0 < Q ^ d := pow_pos hQ d
  have h := quantized_entropy_bound hN P
  rw [show Real.log ((Q ^ d : ℕ) : ℝ) = (d : ℝ) * Real.log (Q : ℝ) by
    rw [Nat.cast_pow, Real.log_pow]] at h
  exact h

end

end FiniteQuerySandbox
