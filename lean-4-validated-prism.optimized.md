# Optimized Lean 4 Plan: Finite-Discrete Information-Theory Axiom Reduction

## Prism Analysis

This is a third-pass rewrite grounded in actual Lean file content and paper-file cross-checks (not plan prose). Changes from the previous version are marked with `[CHANGED]` / `[NEW]` / `[FLAGGED]` annotations, with the rationale inline.

---

## 0. Verified Facts From The Codebase

**Four axioms remain** (confirmed by `grep -rn "^axiom"` on all Lean files):

| # | Axiom | File | Line | Role |
|---|-------|------|------|------|
| 1 | `chain_rule` | DualCertificate.lean | 104 | Trace-gap identity for Prop 1 |
| 2 | `cut_set_bound` | DualCertificate.lean | 117 | Universal cut-capacity bound |
| 3 | `condMarkov` | InfoTheory.lean | 119 | Conditional Markov predicate |
| 4 | `cond_dpi` | InfoTheory.lean | 122 | Conditional DPI inequality |

**`IdentifiabilityGap.lean` is axiom-free** (verified). It uses only `entropyOf`, `negMulLog2`, finite-sum algebra, and `ring`. Paper claim stands.

**`Screenability.lean` is axiom-free** (verified). It proves `no_eis_autoregressive` from `DeterministicScreen` structure alone.

**`marginalXYWMass` does NOT exist** (verified by `grep` with zero results). The plan's PR 3 correctly identifies this gap.

---

## [CHANGED] 1. Status-Drift: Verified With Exact Line Numbers

The plan claimed a mismatch `paperd.tex` vs `experiments/7.2_dynamic_certificate/README.md`. This is real, and worse than described:

| Source | Claim | Line | Status |
|--------|-------|------|--------|
| `paper/main.tex` / `archived/paperd.tex` | `delta_act^LB = 0.0163 bits`, `epsilon_state^UB` from 16464 to 0, etc. | lines 40-41 | Presented as completed |
| `experiments/7.2_dynamic_certificate/README.md` | "**In development.**" Pipeline scaffold in place; "full execution on Qwen2.5-7B-Instruct over a WebArena sample is scheduled for the next revision." | lines 11-13 | In development |
| `experiments/7.1_static_certificate/README.md` | "**In development.**" Networkx-based cut enumeration and matplotlib figure rendering "scheduled for the next revision." | lines 13-14 | In development |
| `experiments/7.5_diffusion_certificate/README.md` | Predicts **inverted-U** pattern: "peaks at steps 4-6, decays at step 10" | line 17-19 | Prediction contradicts paper's "late-binding" result (step 10 is max) |

**The 7.2 README also describes a different experiment** than the paper: README uses WebArena (5-class: click, type, search, scroll, stop); the paper uses tool-selection (calculator, search, email, calendar, weather). The README predicts "0.5 to 1.5 nats" on a 1.61 nat ceiling; the paper reports 0.0163 bits on a presumably lower ceiling.

**PR 0 scope must expand** to reconcile all three: (a) status flags, (b) task definitions, (c) predicted vs reported patterns for LLaDA.

---

## [CHANGED] 2. Dependency Graph Validation

Validated against actual Lean definitions, not descriptions:

```
PR 1 (chain_rule)        -- independent: pure ℝ algebra, no other axiom used
  |
PR 2 (cut_set_bound)     -- independent: axiom restructuring only, no entropy proof
  |
PR 3 (condMarkov)        -- independent: definition of a Prop, no proof needed
  |
PR 4 (entropy layer)     -- foundational: needs KL nonneg etc. from Mathlib
  |  \
  |   PR 5 (quantized)   -- depends on PR 4's entropy_le_log_card
  |
PR 6 (cond_dpi)          -- depends on PR 3 (condMarkov defn) AND PR 4 (KL nonneg)
  |
PR 7 (metric covering)   -- orthogonal: geometry, not info theory
```

**Key finding: PR 4 and PR 6 share proof infrastructure.** Both need `kl_nonneg` (or an equivalent log-sum / Jensen inequality for finite PMFs). This means PR 6 cannot start until PR 4 is done. If PR 4 stalls, PR 6 cannot proceed.

**Mitigation in section 8 below**: split PR 4 into (4a) easy entropy lemmas + (4b) KL nonneg. If KL nonneg causes a multi-week stall, the project can still deliver PRs 1-3 and 4a, compressing from 4 axioms to 3 axioms + 1 analytic axiom (the hard inequality).

---

## [CHANGED] 3. PR 1: Verified Proof Shape

**Axiom location**: `DualCertificate.lean:104`
```lean
axiom chain_rule (P : FinitePMF (State × VisibleTrace × MissingTrace)) :
    H_S_cond_Ttilde P = H_S_cond_Tfull P + I_S_M_cond_Ttilde P
```

**Definitions** (verified from code):
- `H_S_cond_Ttilde P` = `entropyOf (stateVisibleMass P) - entropyOf (visibleMass P)`
- `H_S_cond_Tfull P` = `fullTraceEntropy P - entropyOf (visibleMissingMass P)`
- `I_S_M_cond_Ttilde P` = `entropyOf (stateVisibleMass P) + entropyOf (visibleMissingMass P) - entropyOf (visibleMass P) - fullTraceEntropy P`

**Algebra**: RHS = `(C - D) + (A + D - B - C)` = `A - B` = LHS. Pure ℝ linear identity.

**Proof** (will work with `ring` on ℝ):
```lean
theorem chain_rule (P : FinitePMF (State × VisibleTrace × MissingTrace)) :
    H_S_cond_Ttilde P = H_S_cond_Tfull P + I_S_M_cond_Ttilde P := by
  unfold H_S_cond_Ttilde H_S_cond_Tfull I_S_M_cond_Ttilde fullTraceEntropy
  ring
```

`ring` works because after `unfold`, the body is a linear expression in 4 real-valued `entropyOf(...)` terms. `fullTraceEntropy` is a `def` (unfoldable). No proof of any analytic property of entropy is needed.

**Acceptance**: Remove axiom, replace with theorem, delete `trace_gap_identity` wrapper (it becomes identical to `chain_rule`), update `prop1_static_ub` to call the theorem directly.

---

## [CHANGED] 4. PR 2: Why The Current Axiom Is Worse Than Described

**Current axiom** (`DualCertificate.lean:117`):
```lean
axiom cut_set_bound (Cut : Type) (C_cut : Cut -> ℝ) (Cuts_U_to_S : Set Cut) :
    ∀ Ω ∈ Cuts_U_to_S, ∀ P : FinitePMF (State × VisibleTrace × MissingTrace),
    I_S_M_cond_Ttilde P ≤ C_cut Ω
```

**Problem**: The axiom quantifies over ALL `P` for a fixed `C_cut`. If someone sets `C_cut Ω = 0` for all Ω, the axiom claims `I_S_M_cond_Ttilde P ≤ 0` for every P -- which is false for most P. For the axiom to be sound, `C_cut` must be a supremum over the space of all PMFs. The axiom does not encode this; it just asserts the inequality for whatever `C_cut` happens to be given.

**[NEW] Also**: the axiom is not even used correctly downstream. `prop1_static_ub` applies it as:
```lean
have h_cut : I_S_M_cond_Ttilde P ≤ C_cut Ω := cut_set_bound Cut C_cut Cuts_U_to_S Ω hΩ P
```
This picks a single cut Ω and claims the bound holds. But the paper's Proposition 1 uses `min_Ω C_cut(Ω)`, not `C_cut(Ω)` for an arbitrary cut. The theorem is technically sound (if `C_cut(Ω)` is an absolute supremum for that Ω), but the proof structure doesn't match the paper's claim.

**Recommended PR 2 scope**: Replace the universally-quantified axiom with an explicit theorem that consumes cut-capacity premises:

```lean
theorem cut_set_bound_from_capacity
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (hDPI : I_S_M_cond_Ttilde P ≤ I_YZ_W P_cut)
    (hCapacity : I_YZ_W P_cut ≤ C_cut) :
    I_S_M_cond_Ttilde P ≤ C_cut :=
  le_trans hDPI hCapacity
```

This still needs a conditional-DPI-like step (`hDPI`), which PR 6 will eventually provide. For PR 2, the architectural improvement is:

1. Remove the monolithic `cut_set_bound` axiom.
2. Make `prop1_static_ub` take `(h_bound : I_S_M_cond_Ttilde P ≤ C_cut)` as a premise.
3. Add a brief comment explaining that this premise will be discharged by the cut-set bound (network info theory) when the full DPI infrastructure is in place.

This is cleaner because the theorem no longer assumes a universal capacity function, and the user must provide a per-instance capacity proof.

---

## [CHANGED] 5. PR 3: What `marginalXYWMass` Definition To Add

**Verified**: `marginalXYWMass` does not exist in any Lean file (grep returned empty).

**Required definition** (added to `InfoTheory.lean` near the other 4-variable marginals):

```lean
def marginalXYWMass (P : FinitePMF (α × β × γ × δ)) (xyw : α × β × δ) : ℝ :=
  ∑ z : γ, P.pmf (xyw.1, xyw.2.1, z, xyw.2.2)
```

After adding this, the `condMarkov` definition becomes:

```lean
def condMarkov (P : FinitePMF (α × β × γ × δ)) : Prop :=
  ∀ x y z w,
    P.pmf (x, y, z, w) * marginalYWMass P (y, w)
      =
    marginalXYWMass P (x, y, w) * marginalYZWMass P (y, z, w)
```

This replaces `axiom condMarkov ... : Prop` with a concrete definition. The `condMarkov` type changes from `Prop` (axiom-introduced) to `Prop` (definition-introduced). All downstream code that assumes `h : condMarkov P` continues to work without change.

**Risk**: Low for the definition itself. The downstream code (`cond_dpi` axiom and `prop2_dynamic_lb`) works regardless of whether `condMarkov` is an axiom or a definition, because both produce a term of type `Prop`.

---

## [CHANGED] 6. PR 4: The Real Bottleneck

The plan correctly identifies PR 4 as the high-risk item. Based on Mathlib's current API, here is a realistic assessment:

**What Mathlib provides**:
- `Real.log` for ℝ
- `Finset.sum` for finite sums
- `Finset.card` / `Fintype.card` for cardinalities
- No prebuilt `kl_divergence` for finite PMFs
- No prebuilt `entropy_le_log_card` for arbitrary finite types

**What must be built**:

The `kl_nonneg` theorem requires either:
- **(Route A)** Jensen's inequality with `ConvexOn` for `x * log(x/y)`. Mathlib has `ConvexOn` but applying it to finite-sum KL divergence requires showing `f(x) = x * log(x/y)` is convex for `x,y > 0`, then applying Jensen. Feasible but significant.
- **(Route B)** The log-sum inequality: `∑ a_i log(a_i/b_i) ≥ (∑ a_i) log(∑ a_i / ∑ b_i)`. Mathlib does not have this pre-built.
- **(Route C)** Gibbs' inequality: `-∑ p_i log p_i ≤ -∑ p_i log q_i`. This follows from the log-sum inequality or from `log x ≤ x - 1`.

**[NEW] Proposed fallback strategy**:

Structure PR 4 as two sub-PRs:

**PR 4a (Low risk, quick wins)**:
- `pmf_le_one`
- `marginal_nonneg`, `marginal_sum_one`
- `entropy_nonneg`
These require only basic positivity properties and `-p * log p ≥ 0` for `p ∈ [0,1]`.

**PR 4b (High risk, may stall)**:
- `kl_nonneg`
- `entropy_le_log_card`

If PR 4b stalls, the project should fall back to **one well-scoped axiom**:

```lean
-- Temporary: standard analytic inequality, tracked at issue #XXX
axiom kl_nonneg (p q : α → ℝ) (hp_nonneg : ∀ x, 0 ≤ p x) (hq_pos : ∀ x, 0 < q x)
    (hp_sum : ∑ x, p x = 1) (hq_sum : ∑ x, q x = 1) :
    0 ≤ ∑ x, p x * (Real.log (p x / q x))
```

This concentrates the remaining trust into a single, standard, well-understood inequality rather than 3 domain-specific axioms. The paper's Appendix should note this choice and reference the standard textbook proof.

**Acceptance criterion for PR 4b being "done"**: `kl_nonneg` is proved, not axiomatized. If it remains an axiom, the axiom count goes from 4 to 2 (chain_rule removed, cut_set_bound restructured, condMarkov defined), with 1 remaining analytic axiom + cond_dpi.

---

## [NEW] 7. PR 5: Two Issues Not In The Plan

**Issue 1: `Real.log Q` when `Q = 0`**. The plan says "require 0 < Q." This is correct but needs to be baked into the type: use `Fin (Q+1)` or `hQpos : 0 < Q` as a premise. `Real.log 0 = 0` in Mathlib by convention, but `entropy <= d * (log 0 / log 2)` with Q=0 would be mathematically suspect.

**Issue 2: The quantized bound needs `entropy_le_log_card` first**, which needs PR 4. If PR 4 is split, PR 5 can start after PR 4a (entropy_nonneg), but the full proof needs PR 4b (kl_nonneg -> entropy_le_log_card). PR 5 should be explicitly marked as "starts after PR 4b."

---

## [NEW] 8. PR 6: cond_dpi Proof Route Assessment

**Current axiom** (`InfoTheory.lean:122`):
```lean
axiom cond_dpi (P : FinitePMF (α × β × γ × δ)) (h : condMarkov P) :
    I_XZ_W P ≤ I_YZ_W P
```

**Proof sketch** (requires PR 3 + PR 4b):

The standard conditional DPI proof route for finite PMFs:

1. For each `w : δ`, define conditional distributions `P(X,Z | W=w)` and `P(Y,Z | W=w)`.
2. The Markov chain `X → Y → Z | W` implies `P(X,Z | W=w) = ∑_y P(X,Y=y | W=w) * P(Z|Y=y,W=w) / ...` hmm, this gets messy.

A cleaner approach for finite PMFs: use the **log-sum inequality** on the joint PMF factorization. Given `condMarkov P`, the joint PMF factors as:
```
P(x,y,z,w) * P(y,w) = P(x,y,w) * P(y,z,w)
```

From this one can derive `P(x,y,z,w) = (P(x,y,w) * P(y,z,w)) / P(y,w)` (when denominator non-zero). Then:

`I(X;Z|W) = ∑_{x,z,w} P(x,z,w) * log(P(x,z,w) / (P(x,w) * P(z,w) / P(w)))`
`I(Y;Z|W) = ∑_{y,z,w} P(y,z,w) * log(P(y,z,w) / (P(y,w) * P(z,w) / P(w)))`

The DPI `I(X;Z|W) ≤ I(Y;Z|W)` under `X → Y → Z | W` follows from applying KL nonnegativity to the conditional distributions.

**[NEW] Realistic proof cost**: The Lean proof is not trivial. Expect 100-300 lines. The key insight is that both `I_XZ_W` and `I_YZ_W` can be expressed as conditional KL divergences, and the `condMarkov` factorization lets you relate them via the chain rule for KL divergence. The `kl_nonneg` theorem from PR 4b is the essential building block.

---

## [CHANGED] 9. PR 7: Remove From Critical Path

The metric-covering extension (PR 7) is not on the axiom-removal critical path. It adds geometry theorems that do not help remove `cond_dpi` or `kl_nonneg`. The existing `GeometricTools.lean` and `CoveringBound.lean` files already define covers, Lipschitz properties, and good-region bounds -- the plan correctly notes these should be reused.

**Recommendation**: Label PR 7 as a **stretch goal** or **future work**. Do not include it in the axiom-reduction milestone sequence. The existing files are sufficient for the paper's Lean-facing claims.

---

## [NEW] 10. Hidden Typeclass Assumptions In The Lean Code

**`Real` ring properties** (asked in the review): The code uses `Real.log`, `/` division, and `ring`. These all work because `ℝ` is a `StrictOrderedRing` in Mathlib, which provides `CommSemiring` (needed for `ring`), `LinearOrderedField` (needed for `/` and ordered arithmetic). No hidden assumptions.

**`Fintype α` everywhere**: All PMF types must be `Fintype`. This is consistent with the finite-discrete scope. Every theorem signature includes `[Fintype α] [DecidableEq α]`. The `FinitePMF` structure embeds this requirement.

**[NEW] Possible typeclass pain point**: The `condMarkov` definition uses 4 type variables `(α × β × γ × δ)`. In Lean, nested product types can cause typeclass inference issues with `DecidableEq`. The current code avoids this by having separate `DecidableEq` for each variable. This is fine but should be preserved in the new definition.

---

## [CHANGED] 11. Right-Sizing Recommendations

| PR | Current Scope | Assessment | Recommendation |
|----|---------------|------------|----------------|
| PR 0 | Artifact consistency | Correct | Expand to check all 3 experiment READMEs + 7.5 prediction mismatch |
| PR 1 | chain_rule | Correct size | One file, one theorem, ~5 lines. Keep as PR 1. |
| PR 2 | cut_set_bound refactor | Correct size | Restructure axiom into explicit premises. Keep as PR 2. |
| PR 3 | condMarkov defn | Correct size | Add one `marginalXYWMass` def, replace axiom with def. Keep as PR 3. |
| PR 4 | Entropy/KL layer | **Too big** | Split into PR 4a (easy lemmas) and PR 4b (KL nonneg / entropy_le_log_card). Make PR 4b the contingency axiom PR. |
| PR 5 | Quantized bound | Correct size | Depends on 4b. Mark as gated. |
| PR 6 | cond_dpi | Borderline | Could split, but the dependencies (PR 3 + PR 4b) mean it's better to keep as one PR. Add a "if 4b is axiomatized, 6 uses that axiom" note. |
| PR 7 | Metric covering | **Too ambitious** | Remove from critical path. Stretch goal only. |

---

## [CHANGED] 12. Hardened Risk Register

| Risk | Trigger | Mitigation | Owner |
|------|---------|------------|-------|
| PR 4b `kl_nonneg` stalls | No proof after 2 weeks | Admit `kl_nonneg` as a single scoped axiom, document in `lean-verified-boundary.md`, track as issue | Formalization lead |
| PR 6 `cond_dpi` blocks on PR 4b | PR 4b not finished | PR 6 can use the same temporary `kl_nonneg` axiom if admitted | Same as above |
| Reviewer spots experiment-README status drift | Submission review | PR 0 before submission: update READMEs or soften paper claims. Add a `scripts/verify_reproducibility.sh` that validates each paper number against its source script | All authors |
| "Finite is too restrictive" reviewer complaint | Paper review | Do NOT promise continuous info theory in Lean. Add scoped future-work paragraph in Appendix. The `QuantizedVector` bridge theorem (PR 5) shows the discrete-to-analog connection, which satisfies most finite-vs-continuous concerns. | Paper lead |
| LLaDA README predicts inverted-U but paper reports late-binding | Experiment reproduction fails | Fix the README to match the actual finding, or rerun with the described parameters to verify | Experiment lead |
| `cut_set_bound` axiom is too strong for the claimed paper proof | Reviewer checks math | The refactored PR 2 makes capacity bounds explicit. The paper's Proposition 1 proof sketch (cut-set + min-cut) is mathematically correct; the Lean refactoring just makes the assumptions explicit. | Formalization lead |

---

## 13. Optimized Milestones

| # | What | Axiom Impact | Risk | Max Time | Depends On |
|---|------|--------------|------|----------|------------|
| 0 | Reconcile paper + experiments + Lean claims | (none) | Low | 2 days | -- |
| 1 | Prove `chain_rule` as theorem | 4 -> 3 | Low | 1 day | -- |
| 2 | Restructure `cut_set_bound` into explicit-premise theorem | 3 -> 3 (cleaner) | Low-Med | 2 days | -- |
| 3 | Define `condMarkov` as `def`, add `marginalXYWMass` | 3 -> 3 (cleaner) | Low-Med | 1 day | -- |
| 4a | Prove `entropy_nonneg`, `pmf_le_one`, marginal lemmas | 3 -> 3 | Low | 2 days | -- |
| 4b | Prove `kl_nonneg` and `entropy_le_log_card` | 3 -> 2 (or 3 -> 2 with 1 ax) | **High** | 3 weeks | 4a |
| 5 | Prove `quantized_entropy_bound` | 2 -> 2 | Med | 2 days | 4b |
| 6 | Prove `cond_dpi` as theorem | 2 -> 1 (or 3ax -> 2ax with 4b ax) | **High** | 2 weeks | 3, 4b |
| 7 | Metric covering extension | Stretch | Med-High | -- | -- |

**Best case**: 4 axioms -> 1 (just `kl_nonneg` as a standard analytic axiom).
**Contingency (PR 4b stalls)**: 4 axioms -> 2 (chain_rule + cut_set_bound removed, condMarkov defined; `kl_nonneg` + `cond_dpi` remain as axioms).
This is still a meaningful reduction: from 4 domain-specific axioms to at most 2, with the remaining one being a standard textbook inequality.

---

## 14. Highest-Value Immediate Actions

1. **Run PR 0 NOW.** The experiment READMEs are inconsistent with the paper. This is the highest review-surface risk.
2. **Run PR 1 next.** One file, one theorem, `ring`. Validates the axiom-removal workflow.
3. **Run PR 3 before PR 4b.** `condMarkov` as a `def` is trivially correct and removes a `Prop` axiom regardless of the heavy entropy proofs.
4. **Do NOT start PR 7.** Remove from the critical path.
5. **Decide on the PR 4b contingency** before starting it: if `kl_nonneg` is not proved within 2 weeks, axiomatize it with a TODO.

---

## Appendix: Exact Discrepancies Found

### `experiments/7.2_dynamic_certificate/README.md` (lines 11-13)
> "**In development.** The pipeline scaffold (configs, inference hook template, three estimator stubs, aggregation stub) is in place; full execution on Qwen2.5-7B-Instruct over a WebArena sample is scheduled for the next revision."

But the paper presents pipeline results (0.0163 bits, Table 2 with calculator/planning tasks) as completed. The README references WebArena (click/type/search/scroll/stop); the paper uses tool-selection (calculator/search/email/calendar/weather). These are different task distributions.

### `experiments/7.1_static_certificate/README.md` (lines 13-14)
> "**In development.** The pipeline scaffold ... is in place; networkx-based cut enumeration and matplotlib figure rendering are scheduled for the next revision."

But the paper presents a completed static certificate table (16,464 bits stepwise reduction) and two figures (react_dag.pdf, logging_ablation.pdf) as extracted results.

### `experiments/7.5_diffusion_certificate/README.md` (line 17-19)
> "The predicted pattern is an inverted-U: delta_act^LB near zero at step 2 (noise-dominated), peaks at steps 4-6 (semantic commitment), decays at step 10 (token refinement)."

The paper reports a "late-binding" pattern where step 10 is the peak (0.110 bits), not an inverted-U. The README predicts decreasing after 4-6; the paper shows increasing to step 10.

### `LEAN_VERIFICATION.md` vs code
The LEAN_VERIFICATION.md claims 4 axioms. After PR 1 (`chain_rule` proven), this must be updated to 3. The file should reference the current verified axiom count dynamically, or be manually updated after each PR.

### `paper/main.tex` and `archived/paperd.tex` are identical
Both are the same draft. The `archived/paperd.tex` appears to be a backup copy rather than a different version. The paper's Appendix claim "4 explicit information-theoretic axioms" matches the current codebase, but will go stale after PR 1.
