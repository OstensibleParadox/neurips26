# Continuous CasualQIF over Linear-Gaussian SCMs

This note preserves the original idea first, then gives an edited version on
top of it. The edited version keeps the claim conservative: finite CasualQIF
gives structural upper bounds; the linear-Gaussian setting is the natural
continuous case where tightness can be answered by water-filling.

## 1. Original Idea

我的想法是：在 Gaussian / linear-Gaussian SCM 上做 continuous CasualQIF。

```text
状态:        N(mu_v, Sigma_v) 在每个 vertex
restriction: 线性 map A_ij + 加性 Gaussian noise (= OU 一步)
cut:         A 的线性 projection 到子空间
capacity:    (1/2) log det(I + Sigma_signal Sigma_noise^{-1})
DPI 静态:    Sigma_target >= A Sigma_source A^T + Sigma_noise  (covariance order)
DPI 动态:    KL contraction along OU semigroup
tightness:   Blahut-Arimoto 在 Gaussian 退化为 water-filling
             water-filling = exp family I-projection 的闭式解

Lean 可做: 用 MeasureTheory.GaussianMeasure + 协方差矩阵代数, 避免 Bochner 积分巨坑
两条几何同时可用: 静态投影 + 动态收缩
与 NeurIPS 现有有限版结构对偶: Finset.sum -> covariance matrix trace; CI graph -> conditional covariance zeros

副线 (conjecture / future work):
exp family 一般情形 -> 投影 DPI
一般 Markov 半群 -> Bakry-Emery 风格 DPI
```

## 2. Edited Version

The continuous extension should not be framed as:

```text
Pearl causality is a special case of sheaf theory.
```

That claim is too broad. A reviewer can reasonably ask why the proposed cut
capacity is tight, and finite Pearl-style d-separation cannot answer that
question by itself. KKT conditions only certify necessary optimality at an
optimizer; they do not by themselves produce the optimizing distribution or
show convergence from arbitrary initialization. The Gaussian channel case has a
better answer: Blahut-Arimoto degenerates to Gaussian water-filling, and
water-filling gives the closed-form optimizer.

The safer claim is:

```text
Finite CasualQIF gives graph-certified information-flow upper bounds.
Linear-Gaussian CasualQIF is a continuous instance where those bounds become
tight under the usual covariance/power constraints, because Gaussian
water-filling solves the capacity problem exactly.
```

## 3. Linear-Gaussian Information Sheaf

Let the base be a finite causal DAG or finite causal poset. Each vertex carries
a Gaussian stalk:

```text
F_v = Gaussian family over R^{d_v}
state at v = N(mu_v, Sigma_v)
```

A causal edge or comparable pair has a noisy linear restriction map:

```text
X_j = A_ij X_i + epsilon_ij
epsilon_ij ~ N(0, Sigma_ij)
```

Equivalently:

```text
rho_ij : N(mu_i, Sigma_i)
      -> N(A_ij mu_i, A_ij Sigma_i A_ij^T + Sigma_ij)
```

This is the continuous analogue of a lossy restriction map. Loss is no longer
counted by finite fibers; it is measured by covariance growth, entropy growth,
mutual-information loss, KL contraction, or Fisher-metric contraction.

## 4. Static DPI Layer

For an exact Gaussian restriction:

```text
Sigma_j = A_ij Sigma_i A_ij^T + Sigma_noise
```

If the target observation has additional unmodeled noise or coarsening, then
the exact equality relaxes to Loewner domination:

```text
Sigma_target >= A Sigma_source A^T + Sigma_noise
```

So the paper should not identify DPI with covariance order directly. The more
precise statement is:

```text
In the Gaussian setting, information monotonicity can be represented by matrix
inequalities over covariance operators.
```

The finite analogue is:

```text
Finset.sum over discrete states
```

while the Gaussian analogue is:

```text
trace / log-det / Loewner order over covariance matrices
```

## 5. Cut Capacity

For a linear Gaussian cut channel:

```text
Y = A X + N
N ~ N(0, Sigma_N)
```

with input covariance `Sigma_X`, the mutual information is:

```text
I(X; Y) = 1/2 log det(I + Sigma_N^{-1/2} A Sigma_X A^T Sigma_N^{-1/2})
```

In the aligned or projected-subspace case this becomes the intended expression:

```text
C = 1/2 log det(I + Sigma_signal Sigma_noise^{-1})
```

subject to a covariance or power constraint on `Sigma_X`.

The important distinction is:

```text
finite CasualQIF:       h_cap : I_cut <= C is an external premise
Gaussian CasualQIF:     C is computed by solving a Gaussian channel capacity problem
```

Thus the reviewer question:

```text
Why is C tight?
```

has the answer:

```text
Because the optimizing Gaussian input covariance is given by water-filling,
which is the Gaussian specialization of Blahut-Arimoto / I-projection.
```

## 6. Dynamic DPI Layer

The same structure has a dynamic version through the Ornstein-Uhlenbeck
semigroup:

```text
dX_t = -B X_t dt + sqrt(2D) dW_t
```

The restriction map is now time evolution:

```text
P_t : law(X_0) -> law(X_t)
```

The DPI statement becomes KL contraction:

```text
D_KL(P_t mu || P_t nu) <= D_KL(mu || nu)
```

and, under stronger curvature or log-Sobolev assumptions, exponential
contraction:

```text
D_KL(P_t mu || pi) <= exp(-2 lambda t) D_KL(mu || pi)
```

For the main paper, this should be a secondary geometry, not the core theorem.
The core theorem should be the static Gaussian channel bound plus tightness via
water-filling.

## 7. Lean Formalization Boundary

The Lean target should avoid full measure-theoretic DPI at first. The tractable
core is matrix algebra for Gaussian channels:

```text
positive definite covariance matrices
linear maps A
Gaussian covariance pushforward
log-det mutual information formula
Loewner-order monotonicity lemmas
conditional covariance zeros for Gaussian CI
```

The formalization should aim for:

```text
linear Gaussian restriction maps compose by matrix multiplication
Gaussian covariance pushforward is functorial
Gaussian CI corresponds to conditional covariance zeros
Gaussian cut capacity has the log-det form
```

The full optimization theorem can initially be isolated:

```text
WaterFilling_optimal:
  under a trace/covariance constraint, the Gaussian channel capacity is attained
  by the water-filling covariance.
```

This keeps the Lean development away from the Bochner-integral layer while
still connecting directly to continuous information theory.

## 8. Relation to the Finite NeurIPS Version

The continuous theory mirrors the finite one:

```text
finite hidden state       -> Gaussian latent vector
finite visible trace      -> linear projection / noisy observation
missing trace             -> orthogonal or conditional subspace
cut capacity              -> Gaussian channel capacity
Finset.sum                -> trace / log-det
CI graph                  -> conditional covariance zeros
d-separation certificate  -> Gaussian conditional-independence certificate
stateLeakage <= capacity  -> mutual information <= Gaussian cut capacity
```

So the right narrative is:

```text
The finite theory proves that graph structure certifies an information-flow
upper bound. The Gaussian theory identifies a continuous setting where that
upper bound is computable and tight.
```

## 9. Future Work

The following should be marked as conjectural or future work:

```text
exponential families:
  projection DPI via I-projection / information geometry

general Markov semigroups:
  entropy contraction via Bakry-Emery or log-Sobolev methods

general measurable kernels:
  full measure-theoretic DPI, replacing sums by integrals
```

The paper should not depend on these generalizations. They are the conceptual
roadmap after the linear-Gaussian case is made precise.

## 10. One-Line Version

Continuous CasualQIF should be developed first for linear-Gaussian SCMs:
Gaussian stalks, noisy linear restriction maps, covariance/log-det capacity,
static DPI as matrix monotonicity, dynamic DPI as OU KL contraction, and
tightness by water-filling rather than by finite Pearl semantics alone.
