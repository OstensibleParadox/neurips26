<!--
ROADMAP NOTE, NOT CANONICAL THEORY.

This file is a dependency map from the existing NeurIPS / Lean artifacts to the
POPL27 probability-sheaf bridge and later continuous proof obligations. The
canonical theory note is `popl27_magwalk_sheaf_bridge.md`.

Do not use this file as an independent source for the MAGWalk/sheaf claim. Use
it to locate which existing artifact supplies which premise, and where the next
proof obligations should attach.
-->

# Epistemic Cut Hierarchy

This roadmap summarizes the progression from existing finite artifacts to the
POPL27 probability-sheaf bridge and later continuous epistemic-cut proofs. It
has two jobs:

```text
1. connect the current NeurIPS / Lean results to the revised MAGWalk story
2. map the later continuous proof path without making those claims canonical
```

For the canonical POPL27 statement, use `popl27_magwalk_sheaf_bridge.md`.

## 0. Core Question

The underlying problem is the other-minds problem in mathematical form:

```text
internal state / cause
        ↓ observation map, cut, channel, or sigma-algebra
external trace / behavior
```

The recurring claim is not mystical unknowability. It is observational
non-invertibility:

```text
observation factors the internal state through a quotient;
anything lost before the cut cannot be reconstructed downstream.
```

The finite form asks whether the state can be recovered. The stronger form asks
how much can be recovered, at what rate, and through which certified witness.

## 1. Classical Starting Points

### 1.1 Shannon's Gaussian Move

Shannon did not solve the Gaussian channel by taking finite discrete channels
to a limit term by term. The decisive structure was:

```text
variance constraint + maximum differential entropy = Gaussian
```

This gives the closed capacity formula:

```text
C = (1/2) log(1 + SNR)
```

The lesson is methodological: for a continuous problem, do not merely replace
finite sums by integrals. Find the continuous structure whose extremizer closes
the theorem.

### 1.2 Data Processing

The finite theorem says that Markov factorization cannot increase information:

```text
X -> Y -> Z
I(X; Z) <= I(X; Y)
```

In the existing Lean artifacts, this appears as finite conditional DPI over
`FinitePMF`, finite KL, finite entropy, and `Finset.sum`.

This is correct but structurally limited: it proves monotonicity after the
probability model is already discrete.

### 1.3 de Bruijn / Entropy Dissipation

For continuous heat-like flows, entropy changes according to Fisher information:

```text
d/dt Entropy(rho_t) = FisherInformation(rho_t)
```

or, in relative/invariant-measure form:

```text
d/dt Ent_mu(P_t f) = - I_mu(P_t f)
```

This is the first continuous replacement for finite CMI algebra: information
loss becomes an energy dissipation identity.

### 1.4 Bakry-Emery / Gamma Calculus

For a diffusion generator `L`, the carre-du-champ calculus defines:

```text
Gamma(f) = 1/2 (L(f^2) - 2 f L f)
```

and curvature conditions such as:

```text
Gamma_2 >= rho Gamma
```

yield contraction or exponential decay:

```text
information distance decays at rate controlled by rho.
```

This is the local-curvature version of the continuous DPI intuition.

### 1.5 KLS / Isoperimetric Bottleneck

KLS enters as the global-bottleneck analogue:

```text
not pointwise curvature,
but global isoperimetry / spectral gap / Cheeger bottleneck.
```

For the present project, this is closer to the intended `lambda_cut` than pure
Ricci curvature. It says that information decay can be controlled by a
bottleneck constant even when no simple local curvature lower bound is
available.

## 2. The Proposed Continuous Interface

The intended continuous object is not generic measure-theoretic DPI. It is a
specific information-geometric cut theorem.

### 2.1 State and Auditor Distributions

```text
p_{S_t} = true state distribution
q_{S_t} = auditor-reconstructible state distribution
```

The epistemic gap is measured not by exact state recovery but by a geometric
distance between distributions.

### 2.2 Fisher-Rao Geometry

Use Fisher-Rao geometry, or the equivalent local Hellinger/Fisher information
structure, to measure distinguishability:

```text
g_FR(p_{S_t}, q_{S_t})
```

For Gaussian families, Fisher-Rao has a closed form involving mean and covariance:

```text
ds^2 = dm^T Sigma^{-1} dm
     + (1/2) tr(Sigma^{-1} dSigma Sigma^{-1} dSigma)
```

### 2.3 Fokker-Planck Flow

State distributions evolve under a diffusion:

```text
partial_t rho_t = L^* rho_t
```

The information flow is no longer a static graph property alone. It is a
dynamical contraction/dissipation phenomenon.

### 2.4 Cut Fisher Bottleneck

The cut has an information operator. Its bottleneck is represented by:

```text
lambda_cut
```

Interpreted precisely, `lambda_cut` should be a spectral/isoperimetric or
generalized-eigenvalue bottleneck of the cut Fisher operator relative to the
state Fisher metric.

Small `lambda_cut` means weak reconstruction through the cut. `lambda_cut = 0`
is the continuous analogue of a non-injective observation map.

### 2.5 Linear-Gaussian Diffusion as Extremal Model

The proposed extremal structure is:

```text
Linear-Gaussian diffusion
```

It plays the role that Gaussian distributions play in Shannon capacity:

```text
dS_t = A_t S_t dt + B_t dW_t
p_t, q_t remain Gaussian
Fisher-Rao distance has closed form
cut bottleneck becomes spectral
```

The expected theorem shape:

```text
d/dt g_FR(p_t, q_t)^2
  <= - 2 lambda_cut(t) g_FR(p_t, q_t)^2
     + hidden source term
```

Without an extra hidden source:

```text
g_FR(p_t, q_t)
  <= exp(- int_0^t lambda_cut(s) ds) g_FR(p_0, q_0)
```

This is the continuous, graded form of Mealy non-injectivity.

## 3. Relation to Existing Formalizations

### 3.1 Mealy Machine

Finite toy model:

```text
state q --lambda--> output o
```

If `lambda` is non-injective, no decoder can recover `q` from `o`.

What it proves:

```text
observational quotient exists
```

What it cannot prove:

```text
how much information crosses,
which witness certifies it,
how reconstruction degrades dynamically.
```

### 3.2 NeurIPS Lean Artifact

Finite information-theoretic certificate:

```text
hidden state S
visible trace T_tilde
missing trace M
cut variable Y
```

Main chain:

```text
condMarkov
-> finite conditional DPI
-> I(S; M | T_tilde) <= I(Y; M | T_tilde)
-> stateLeakage_le, given h_cap
```

Load-bearing gap:

```text
h_cap : I(Y; M | T_tilde) <= C
```

This is the capacity-closure gap. The current artifact can consume a capacity
witness; it does not yet derive the natural continuous capacity structure.

### 3.3 POPL d-Separation Artifact

Graph-theoretic / witness-extraction core:

```text
trail blocking
<-> moralized ancestral graph separation
```

under explicit disjointness conditions.

Its conceptual advance:

```text
Reachable : Prop
-> StaticRoute / OpenTrace / ActiveRoute : Sigma-type witness
```

What it closes:

```text
what graph evidence licenses as a causal path.
```

What it does not close by itself:

```text
probability semantics,
entropy,
capacity,
continuous information flow.
```

### 3.4 CasualQIF Combined Artifact

Finite end-to-end QIF chain:

```text
d-separation
-> FactorizesOverDAG
-> condMarkov
-> conditional DPI
-> stateLeakage <= cutCapacity
-> optional dual KL witness
```

This is the cleanest finite closure.

Its boundary:

```text
FinitePMF
Fintype
Finset.sum
finite KL / finite CMI
```

It is not a continuous theory. Its future is either to remain an honest finite
artifact or to be replaced by a new continuous layer rather than mechanically
lifted term by term.

### 3.5 POPL27 Revised Bridge

The POPL27 story should not say that Pearl causality already carries
sheaf/probability semantics.  It does not.  Pearl causality supplies causal
syntax:

```text
nodes
edges
trails
colliders
conditioning sets
d-separation
```

The bridge object is an enriched MAGWalk / SheafMAGWalk:

```text
causal path syntax
+ typed collider/non-collider witnesses
+ stalks
+ restriction maps
+ pushforward distributions
+ collider fiber-merge / gluing data
```

Then the proof pipeline is:

```text
Trail
-> BayesBallPath / typed base path
-> explicit collider witnesses
-> graph-level MAGWalk
-> enriched SheafMAGWalk
-> conditional Markov interface
-> conditional DPI
-> Shannon/KKT cut certificate
-> stateLeakage <= cutCapacity
```

This is the precise way that Shannon cut-set bounds, conditional DPI, and KKT
capacity certificates pass through causal inference into QIF.  The causal layer
makes the use of DPI type-correct; it does not itself provide the information
semantics or capacity tightness.

## 4. Gap Sizes

From the continuous epistemic-cut perspective:

```text
largest gap:
  CasualQIF finite-only probability foundation

middle gap:
  NeurIPS capacity closure h_cap

smallest gap:
  POPL probability-semantics bridge
```

The POPL gap is an interface/integration gap. The NeurIPS gap is the main
capacity-theory gap. The CasualQIF gap is a foundation-change gap.

## 5. The Current Interface

The current proposed interface is:

```text
Finite causal cut syntax
    identifies where information may cross.

Continuous Markov/Fokker-Planck semantics
    describes how state laws evolve.

Fisher-Rao geometry
    measures auditor-vs-truth distinguishability.

lambda_cut
    measures the weakest Fisher/isoperimetric direction through the cut.

Linear-Gaussian diffusion
    supplies the extremal closed-form model.
```

Canonical theorem target:

```text
Epistemic Cut Theorem, continuous version:

For a state law p_t and auditor law q_t evolving under a Markov/Fokker-Planck
semantics with cut Fisher bottleneck lambda_cut, the Fisher-Rao distance between
truth and reconstruction contracts at a rate controlled by lambda_cut, up to
hidden source terms.
```

Linear-Gaussian diffusion is the first model where this should close cleanly.

## 6. Conversation Progression

1. The initial Lean future-work question identified that the current formal
   artifact is zero-sorry but still has explicit structural premises.

2. The Shannon analogy reframed the problem: do not lift finite DPI by replacing
   sums with integrals; find the continuous structure that closes the theorem.

3. The candidate structure became Fisher information, Fokker-Planck flow,
   entropy dissipation, and cut energy.

4. The three artifacts were then classified by their failure points:
   NeurIPS lacks capacity closure, POPL lacks probability semantics, and
   CasualQIF is finite-only.

5. The Mealy machine was reinterpreted as the minimal model of observational
   non-invertibility, not the final theorem.

6. The common theorem was named as an epistemic cut theorem: all observation
   factors through a cut or quotient, and reconstruction is bounded by what
   crosses that cut.

7. The continuous version was sharpened: the extremal structure is not generic
   information geometry but Linear-Gaussian diffusion with Fisher-Rao distance
   and a cut Fisher bottleneck.

8. KLS entered as a guide for replacing pointwise curvature by global
   isoperimetric or spectral bottlenecks. This suggests that `lambda_cut` should
   be treated as a bottleneck constant, not merely a curvature scalar.

## 7. One-Line Summary

The project is moving from:

```text
non-injective output maps prevent exact reconstruction
```

to:

```text
continuous information flow across a causal cut has a Fisher/geometric
capacity, and Linear-Gaussian diffusion is the extremal structure where the
other-minds problem becomes a closed contraction theorem.
```
