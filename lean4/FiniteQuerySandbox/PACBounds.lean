import Mathlib.Data.Fin.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith

namespace FiniteQuerySandbox

/-!
# PAC Packing Lower-Bound Core

This file does **not** formalize the full Gaussian KL / Fano theorem. Instead it
formalizes the algebraic and decision-theoretic core used by the paper's PAC
packing lower bound:

1. the spike reward family is separated in `L1(Px)` by `alpha * tau`;
2. if a learner is within `epsilon < sep / 4` of the true reward in a separated
   family, nearest-neighbor decoding recovers the hidden cell index;
3. if an external statistical argument supplies a Fano lower bound and a
   missed-cell lower bound for that index-recovery problem, the combined lower
   bound is their maximum.

The probability-theoretic step deriving those two lower bounds from Gaussian
observations remains a paper proof sketch, not a Lean theorem.
-/

def PairwiseSeparated {ι : Type} (dist : ι → ι → ℝ) (sep : ℝ) : Prop :=
  ∀ i j : ι, i ≠ j → sep ≤ dist i j

def SpikeIndex (K : Nat) := Option (Fin K)

def spikeL1Distance {K : Nat} (alpha tau : ℝ) :
    SpikeIndex K → SpikeIndex K → ℝ
  | none, none => 0
  | none, some _ => alpha * tau
  | some _, none => alpha * tau
  | some i, some j => if i = j then 0 else 2 * alpha * tau

/--
For the spike reward family

* `R0(e) = 0`,
* `Rj(e) = tau * 1_{e ∈ Cj}`,

with disjoint cells of equal mass `alpha`, the pairwise `L1(Px)` distances are
`alpha * tau` from `R0` to each spike and `2 * alpha * tau` between distinct
spikes. Hence the family is separated at scale `alpha * tau`.
-/
theorem spike_family_separated {K : Nat} {alpha tau : ℝ}
    (h_nonneg : 0 ≤ alpha * tau) :
    PairwiseSeparated (spikeL1Distance (K := K) alpha tau) (alpha * tau) := by
  intro i j hne
  cases i with
  | none =>
      cases j with
      | none => exact False.elim (hne rfl)
      | some j => simp [spikeL1Distance]
  | some i =>
      cases j with
      | none => simp [spikeL1Distance]
      | some j =>
          have hij : i ≠ j := by
            intro hij
            exact hne (by simp [hij])
          simp [spikeL1Distance, hij]
          linarith

/--
Metric triangle interface used for nearest-neighbor decoding. `loss out i`
is the `L1(Px)` distance between the learner output and hypothesis `i`.
-/
def TriangleAgainstFamily {ι Out : Type}
    (dist : ι → ι → ℝ) (loss : Out → ι → ℝ) : Prop :=
  ∀ (out : Out) (true hyp : ι), dist true hyp ≤ loss out true + loss out hyp

/--
If the learner output is within `epsilon < sep / 4` of the true member of a
`sep`-separated family, then every wrong hypothesis is farther away than the
true one. This is Step 2 of the paper proof.
-/
theorem separated_success_makes_true_unique_nearest
    {ι Out : Type} {dist : ι → ι → ℝ} {loss : Out → ι → ℝ}
    {sep epsilon : ℝ} {out : Out} {true hyp : ι}
    (hsep : sep ≤ dist true hyp)
    (htriangle : dist true hyp ≤ loss out true + loss out hyp)
    (hloss_true_nonneg : 0 ≤ loss out true)
    (hsuccess : loss out true ≤ epsilon)
    (heps : epsilon < sep / 4) :
    loss out true < loss out hyp := by
  by_contra hnot
  have hle_hyp : loss out hyp ≤ loss out true := le_of_not_gt hnot
  have hsum : sep ≤ loss out true + loss out hyp := le_trans hsep htriangle
  have heps4 : 4 * epsilon < sep := by linarith
  have heps_nonneg : 0 ≤ epsilon := le_trans hloss_true_nonneg hsuccess
  nlinarith

/--
If `hat` is a nearest-neighbor decoder for the learner output and the learner
is within `epsilon < sep / 4` of the true reward, then `hat = true`.
-/
theorem pac_success_identifies_index
    {ι Out : Type} {dist : ι → ι → ℝ} {loss : Out → ι → ℝ}
    {sep epsilon : ℝ} {out : Out} {true hat : ι}
    (hsep : PairwiseSeparated dist sep)
    (htriangle : TriangleAgainstFamily dist loss)
    (hloss_nonneg : ∀ hyp : ι, 0 ≤ loss out hyp)
    (hsuccess : loss out true ≤ epsilon)
    (heps : epsilon < sep / 4)
    (hhat : ∀ hyp : ι, loss out hat ≤ loss out hyp) :
    hat = true := by
  by_contra hne
  have htrue_ne_hat : true ≠ hat := by
    intro h
    exact hne h.symm
  have hsep_hat : sep ≤ dist true hat := hsep true hat htrue_ne_hat
  have htri_hat : dist true hat ≤ loss out true + loss out hat :=
    htriangle out true hat
  have hlt : loss out true < loss out hat :=
    separated_success_makes_true_unique_nearest hsep_hat htri_hat (hloss_nonneg true) hsuccess heps
  have hle : loss out hat ≤ loss out true := hhat true
  linarith

/--
Once the PAC learner induces an index identifier, any lower bounds for the
resulting index-recovery problem apply to the learner. If the Fano term and
missed-cell term are both lower bounds on the sample size, their maximum is
also a lower bound.
-/
theorem combine_fano_and_missed_cell_bounds
    {m fanoTerm missedCellTerm : ℝ}
    (hfano : fanoTerm ≤ m)
    (hmissed : missedCellTerm ≤ m) :
    max fanoTerm missedCellTerm ≤ m :=
  max_le hfano hmissed

/-!
### Explicit Assumption Wrappers

To make the boundary between Lean-checked algebra and paper-proved statistics
completely rigorous, we wrap the external Fano and missed-cell lower bounds
in explicit assumption structures. The probabilistic derivations (Gaussian KL
and independent missed-cell probabilities) remain external to the Lean formalization.
-/

/--
External Fano/KL premise: proved via standard information-theoretic
arguments in the paper, not checked in Lean.
-/
structure AssumesFanoBound (m fanoTerm : ℝ) : Prop where
  bound : fanoTerm ≤ m

/--
External missed-cell premise: proved via independent sampling arguments
in the paper, not checked in Lean.
-/
structure AssumesMissedCellBound (m missedCellTerm : ℝ) : Prop where
  bound : missedCellTerm ≤ m

/--
The combined external statistical premise for the PAC lower bound.
-/
structure PACStatisticalPremises (m fanoTerm missedCellTerm : ℝ) : Prop where
  fano : AssumesFanoBound m fanoTerm
  missed : AssumesMissedCellBound m missedCellTerm

/-!
### Paper-Facing Conditional Theorems
-/

/--
Conditional PAC Lower Bound Wrapper.
This theorem explicitly takes the external statistical assumptions as inputs,
yielding the combined sample complexity lower bound.
-/
theorem pac_lower_bound_conditional
    {m fanoTerm missedCellTerm : ℝ}
    (h_ext : PACStatisticalPremises m fanoTerm missedCellTerm) :
    max fanoTerm missedCellTerm ≤ m :=
  combine_fano_and_missed_cell_bounds h_ext.fano.bound h_ext.missed.bound

/--
Alias matching the paper's Theorem 3 narrative for the combined result.
-/
theorem theorem3_pac_lower_bound
    {m fanoTerm missedCellTerm : ℝ}
    (h_ext : PACStatisticalPremises m fanoTerm missedCellTerm) :
    max fanoTerm missedCellTerm ≤ m :=
  pac_lower_bound_conditional h_ext

end FiniteQuerySandbox
