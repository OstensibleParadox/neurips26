# Dual Certificates: Research Reset

**Working direction:** finite-sample, probe-relative certificates of transcript
insufficiency in neural agents.

**Status:** go/no-go research plan, not a statement of completed results.

The current paper should not be extended by adding more mutual-information
estimators, activation perturbations, or interface-width min-cuts. The only
direction worth pursuing is a clean reformulation around one operational
question:

> Given a declared family of admissible interventions, is the public transcript
> sufficient to simulate every safety-relevant action distribution of the
> deployed agent?

The object of certification is not an arbitrarily chosen latent state. It is the
failure, or verified adequacy, of a transcript-only action simulator under an
explicit audit contract.

## Candidate Titles

Primary:

> **Dual Certificates of Transcript Insufficiency in Neural Agents**

Alternatives:

- **When Is a Trace Enough? Primal--Dual Audits of Hidden Action Channels**
- **Transcript Simulation Deficiency in Neural-Agent Audits**
- **Residual Causal Capacity Beyond Agent Transcripts**

## Revised Central Claim

A trace-level graph is a localization hypothesis, not a certificate of the
deployed mechanism. A valid audit claim must be relative to:

- a deployment distribution;
- an audit-access model;
- a declared family of admissible probes or interventions;
- a logging boundary; and
- a safety-relevant action boundary.

Within that contract, the auditor should produce one of two mathematically
linked objects:

1. an **insufficiency witness** showing that an admissible randomized probe
   changes actions in a way not mediated by the transcript; or
2. a **sufficiency certificate** showing that one transcript-only simulator
   uniformly approximates the action laws induced by all admissible probes.

If neither side is established, the correct audit result is **inconclusive**.

This replaces the stronger and generally indefensible claim that an auditor can
unconditionally certify the full deployed mechanism.

## Why the Previous Formulation Is Not Enough

The previous certificate pair was based on

\[
H(S\mid T)
\qquad\text{and}\qquad
I(S;A\mid T),
\]

where \(S\) is a selected latent state, \(T\) the visible transcript, and \(A\)
the action. This formulation has four problems.

1. **Latent entropy is non-canonical.** Appending independent noise to \(S\)
   can increase \(H(S\mid T)\) arbitrarily without changing the deployed
   mechanism or its security properties.
2. **The main implication is conditional data processing.** Once the desired
   Markov chains are assumed, the current lower-bound theorem is too close to a
   direct DPI application to carry the paper.
3. **Raw interface capacity is too loose.** Converting an embedding width into
   thousands of nominal bits gives an attack-surface envelope, not evidence of
   an operative hidden channel.
4. **Sensitivity is not audit insufficiency.** Activation noise, direct report
   replacement, or a changed next-token distribution does not by itself show
   that an action effect bypassed the declared transcript.

Markov equivalence should therefore be a motivating impossibility observation,
not the main technical object. For a white-box neural agent, the computational
graph may already be known; the unresolved questions are mediation,
intervention coverage, and access-relative identifiability.

## Formal Audit Setup

Let:

- \(Z\) be an auditor-randomized admissible probe;
- \(T\) be the public audit transcript;
- \(A\) be a safety-relevant deployed action; and
- \(\pi(z)\) be the auditor's probe-design distribution.

For a fixed mechanism \(M\), define the stable intervention law

\[
P_z^M(t,a)
:=
P_M(T=t,A=a\mid \operatorname{do}(Z=z)).
\]

The audit design mixes these laws according to

\[
P_M^\pi(z,t,a)
:=
\pi(z)P_z^M(t,a).
\]

The intervention kernels \(P_z^M\) are properties of the mechanism and do not
depend on the mixing design \(\pi\).

For an adaptive audit, the design policy is written

\[
\pi_i(z\mid H_{i-1}),
\]

where \(H_{i-1}\) is the information available before round \(i\). The
conditional law induced after observing the transcript is a different object:

\[
q_\pi(z\mid t)
:=
P_M^\pi(Z=z\mid T=t)
=
\frac{\pi(z)P_z^M(t)}
{\sum_{z'}\pi(z')P_{z'}^M(t)},
\]

whenever the denominator is positive.

These symbols must not be conflated. If the probe changes the transcript, then
generally \(q_\pi(Z\mid T)\ne\pi(Z)\).

The preferred protocol is **transcript preserving**: the probe is randomized at
a declared hidden boundary while the relevant public trace is fixed by replay,
clamping, or exact matched construction. Formally, \(P_z^M(T)\) is the same for
every admissible \(z\). In this case \(Z\perp T\) under every design \(\pi\), and
consequently

\[
q_\pi(z\mid t)=\pi(z),
\]

which makes exact trace clamping a particularly clean special case rather than
an implicit notational assumption.

The causal interpretation additionally requires an admissibility contract. The
probe must be randomized exogenously, intervene only at the declared boundary,
and preserve the task and action semantics outside that boundary. Arbitrary
zeroing, Gaussian activation noise, and off-support text replacement do not
satisfy this requirement.

## Core Quantity: Transcript Simulation Deficiency

For a mechanism \(M\) and randomized probe design \(\pi\), define

\[
\Delta_\pi(M)
:=
\inf_{R(a\mid t)}
D_{\mathrm{KL}}
\!\left(
P_M^\pi(z,t,a)
\,\middle\|\,
P_M^\pi(z,t)R(a\mid t)
\right).
\]

For every candidate transcript-only simulator \(R(A\mid T)\), the following
decomposition is exact:

\[
D_{\mathrm{KL}}
\!\left(
P^\pi_{ZTA}
\,\middle\|\,
P^\pi_{ZT}R_{A\mid T}
\right)
=
I_\pi(Z;A\mid T)
+
\mathbb E_{T\sim P_T^\pi}
D_{\mathrm{KL}}
\!\left(
P^\pi(A\mid T)
\,\middle\|\,
R(A\mid T)
\right).
\]

It follows immediately that

\[
\boxed{
\Delta_\pi(M)=I_\pi(Z;A\mid T),
\qquad
R_\pi^\star(A\mid T)=P^\pi(A\mid T).
}
\]

The decoder representation is also exact:

\[
\boxed{
I_\pi(Z;A\mid T)
=
\sup_{g(z\mid t,a)}
\mathbb E
\log
\frac{g(Z\mid T,A)}{q_\pi(Z\mid T)}.
}
\]

For every normalized decoder \(g\), its gap to the optimum is

\[
I_\pi(Z;A\mid T)
-
\mathbb E
\log
\frac{g(Z\mid T,A)}{q_\pi(Z\mid T)}
=
\mathbb E_{T,A}
D_{\mathrm{KL}}
\!\left(
P^\pi(Z\mid T,A)
\,\middle\|\,
g(Z\mid T,A)
\right).
\]

Under an exact transcript clamp, the denominator reduces to the known design
law \(\pi(Z)\). Outside that special case, implementing the decoder certificate
requires the induced law \(q_\pi(Z\mid T)\). If it is not known exactly,
uncertainty in this denominator must be propagated through a separate robust
bound; a plug-in estimate is not automatically a valid certificate.

This gives the intended primal--dual interpretation:

- **Simulator side:** \(R(A\mid T)\) attempts to explain every action using
  only the transcript.
- **Witness side:** \(g(Z\mid T,A)\) attempts to decode the randomized probe
  from the action after observing the transcript.
- A successful witness gives a lower certificate of transcript insufficiency.
- A uniformly valid simulator gives an upper certificate of residual channel
  capacity.

The identity itself is classical. It becomes a paper contribution only when it
is combined with a nontrivial admissible-probe model, finite-sample validity,
sequential agents, and matching auditability limits.

## Residual Causal Capacity

For a declared probe family \(\mathcal Z\), define

\[
C_{\mathcal Z}(M)
:=
\sup_{\pi\in\Delta(\mathcal Z)} I_\pi(Z;A\mid T).
\]

Under conditions that justify minimax exchange, the target conditional
information-radius identity is

\[
\boxed{
C_{\mathcal Z}(M)
=
\inf_{R(A\mid T)}
\sup_{z\in\mathcal Z}
\mathbb E_{T\sim P_z}
D_{\mathrm{KL}}
\!\left(
P_z(A\mid T)\,\middle\|\,R(A\mid T)
\right).
}
\]

The theorem statement must give its minimax conditions explicitly. A clean
first version can assume finite \(\mathcal Z\), \(\mathcal T\), and
\(\mathcal A\), with common support. A more general version requires the
appropriate compactness or tightness, convexity of the simulator class, and
lower-semicontinuity/integrability assumptions. Under an exact trace clamp,
all \(P_z(T)\) coincide and the expression simplifies further.

The information-radius identity is classical. The audit contribution is that
the center is constrained to be a transcript-mediated kernel \(R(A\mid T)\):

- the left side asks how much non-transcript action information the strongest
  randomized admissible probe can expose;
- the right side asks how far the best transcript-only simulator remains from
  the complete intervention family.

Operationally:

- any admissible probe distribution gives a lower bound on
  \(C_{\mathcal Z}\);
- a single simulator whose worst-case divergence is small gives an upper bound;
- the auditor reports a confidence interval
  \(\underline C_{\mathcal Z}\le C_{\mathcal Z}\le
  \overline C_{\mathcal Z}\), not only a point estimate.

A positive lower bound is a definite audit failure. A sufficiently small upper
bound is a positive sufficiency result relative to \(\mathcal Z\). A wide gap is
an abstention that should trigger additional probes or instrumentation.

## A Direct Finite-Sample TV Certificate

For a binary randomized audit variable \(Z\in\{0,1\}\), define

\[
\Delta_A
=
\operatorname{TV}\!\left(P(A\mid Z=0),P(A\mid Z=1)\right),
\]

\[
\Delta_T
=
\operatorname{TV}\!\left(P(T\mid Z=0),P(T\mid Z=1)\right).
\]

For a transcript-only kernel \(K\), let

\[
\eta_K
=
\max_{z\in\{0,1\}}
\operatorname{TV}
\!\left(P(A\mid z),K P(T\mid z)\right).
\]

Contraction and the triangle inequality give

\[
\boxed{
\inf_K\eta_K
\ge
\frac{(\Delta_A-\Delta_T)_+}{2}.
}
\]

Indeed, writing

\[
e_z
:=
\operatorname{TV}\!\left(P(A\mid z),K P(T\mid z)\right),
\]

one line suffices:

\[
\Delta_A
\le
e_0+\Delta_T+e_1
\le
2\max(e_0,e_1)+\Delta_T.
\]

The interpretation is direct: the part of the action separation that exceeds
the transcript separation cannot be explained by any transcript-mediated
mechanism.

This is the cleanest operational failure certificate:

- construct a lower confidence bound \(L_A\) on action distinguishability;
- construct an upper confidence bound \(U_T\) on transcript leakage;
- if \(L_A>U_T\), reject every transcript-mediated mechanism in the declared
  audit class and lower-bound its distance from the observations.

With exact trace clamping, \(\Delta_T=0\) by construction. Any certified action
difference is then evidence of a non-transcript action channel.

There is no distribution-free finite-sample upper bound on arbitrary leakage
through a high-dimensional transcript. A sound paper must therefore use at
least one of:

- exact byte- or schema-level trace equality by construction;
- a finite transcript alphabet;
- a computable likelihood ratio or divergence;
- or an explicitly restricted monitor/critic class with a complexity bound.

The paper must never translate failure of a trained decoder into the statement
that no decoder can recover \(Z\).

## Sequential and Adaptive Audit Certificate

Neural agents generate actions sequentially, and useful auditors adapt their
next probes to previous outcomes. This should be part of the theorem, not an
implementation detail.

Let \(\mathcal F_{i-1}=\sigma(H_{i-1})\) denote the pre-round history and

\[
\pi_i(z\mid H_{i-1})
\]

be a full-support probe policy measurable with respect to
\(\mathcal F_{i-1}\). The primary implementable theorem assumes an exact
conditional trace clamp:

\[
Z_i\perp T_i\mid\mathcal F_{i-1},
\qquad
P(Z_i=z\mid T_i,H_{i-1})
=
\pi_i(z\mid H_{i-1}).
\]

The entire normalized decoder rule

\[
g_i(\,\cdot\mid t,a;H_{i-1})
\]

must also be \(\mathcal F_{i-1}\)-measurable as a map from \((t,a)\) to
\(\Delta(\mathcal Z)\), and must be absolutely continuous with respect to
\(\pi_i(\cdot\mid H_{i-1})\). It may be evaluated at the current
\((T_i,A_i)\), but it may not be fitted to the current labeled observation
after \(Z_i\) is revealed. Define

\[
E_n
=
\prod_{i=1}^n
\frac{g_i(Z_i\mid T_i,A_i;H_{i-1})}
{\pi_i(Z_i\mid H_{i-1})}.
\]

Under the null

\[
Z_i\perp A_i\mid T_i,\mathcal F_{i-1},
\]

the one-step factor has conditional mean one:

\[
\mathbb E_0
\!\left[
\frac{g_i(Z_i\mid T_i,A_i;H_{i-1})}
{\pi_i(Z_i\mid H_{i-1})}
\,\middle|\,
\mathcal F_{i-1},T_i,A_i
\right]
=1.
\]

Taking a further conditional expectation with respect to
\(\mathcal F_{i-1}\) shows that \((E_n)\), adapted to

\[
\mathcal F_i
:=
\sigma(\mathcal F_{i-1},Z_i,T_i,A_i),
\]

is a nonnegative martingale, hence an e-process. Ville's inequality gives

\[
\Pr_0\!\left(\sup_n E_n\ge \alpha^{-1}\right)\le\alpha.
\]

Thus the insufficiency witness remains valid under adaptive probes and optional
stopping. The optimal decoder is

\[
g_i^\star
=
P_\pi(Z_i\mid T_i,A_i,H_{i-1}),
\]

and its expected one-step log growth is

\[
I_\pi(Z_i;A_i\mid T_i,H_{i-1}).
\]

For an i.i.d. fixed design, this reduces to \(I_\pi(Z;A\mid T)\). Under an exact
trace clamp, the denominator is known directly from the audit randomization.

Without exact clamping, the same algebra gives an **oracle identity** after
replacing \(\pi_i\) by the true induced conditional law

\[
q_{\pi,i}(z\mid t,h)
=
P_\pi(Z_i=z\mid T_i=t,H_{i-1}=h).
\]

It does not automatically give an implementable e-process for a composite
null: this law can vary with the unknown null mechanism. A deployable general
theorem must assume one known denominator valid for every null mechanism, or
derive a robust e-factor for an uncertainty set. Directly plugging in an
estimated \(q_{\pi,i}\) does not preserve the exact Ville guarantee.

> **Conditional mutual information is not merely a score. It is the optimal
> evidence-growth rate against transcript sufficiency.**

The e-process construction alone is not the novelty. The target contribution is
its combination with transcript causal sufficiency, sequential localization,
and a minimax converse.

## Required Theorem Package

The rewritten paper is viable only if it contains all or most of the following.
The structural priority is:

1. TraceTwin establishes why passive \(\sigma(T,A)\)-measurable auditing is
   insufficient and why randomized-probe access adds identifying information.
2. The sequential e-process supplies the main technical audit primitive.
3. Coverage and no-free-lunch theorems delimit what nondetection can mean.
4. A real deployment experiment connects the statistical theory to agent
   safety.

The simulator/decoder identities support this spine; they are not sufficient
contributions on their own.

### 1. Passive-Audit Impossibility

Construct two mechanisms that induce the same passive distribution \(P(T,A)\)
and the same trace-compatible graph, while an admissible randomized probe yields

\[
\Delta_\pi(M_0)=0,
\qquad
\Delta_\pi(M_1)>0.
\]

This formally establishes that passive traces and observational graph
compatibility cannot certify the deployed mediation mechanism.

### 2. Simulation--Witness Strong Duality

Give the KL representation above and a finite-alphabet TV or bounded-loss
version with an explicit dual class. State exactly when lower and upper
certificates are statistically computable.

### 3. Soundness and Relative Completeness

Prove that a positive certificate implies a non-transcript action path under the
declared causal admissibility assumptions. Prove that a zero upper certificate
excludes bypasses only within an intervention-complete declared family.

### 4. Probe Coverage and No-Free-Lunch

The paper must answer what, if anything, a finite probe suite says about an
unobserved intervention.

For a metric intervention family \((\mathcal Z,d)\), one possible positive
result assumes a continuity condition such as

\[
\operatorname{TV}\!\left(P_z(A,T),P_{z'}(A,T)\right)
\le
L d(z,z').
\]

If \(\mathcal Z_\varepsilon\) is an \(\varepsilon\)-net, the target TV theorem
should extend a certificate on \(\mathcal Z_\varepsilon\) to the full family
with an explicit \(O(L\varepsilon)\) slack. KL analogues require stronger
support, bounded-likelihood-ratio, or smooth parametric assumptions.

The matching negative result is essential: without continuity, finite
alphabet, bounded rank, enumerability, or another coverage structure, every
finite \(F\subsetneq\mathcal Z\) admits mechanisms \(M_0,M_1\) that agree on
all probes in \(F\) but differ arbitrarily at some
\(z^\star\notin F\). Therefore finite probing cannot certify global transcript
sufficiency without structural assumptions.

### 5. Sequential Composition and Localization

For a multi-turn agent, decompose or bound the global audit gap by deficiencies
at action-binding steps. The localization profile must follow from a
composition theorem rather than being presented only as a heuristic heat map.

### 6. Minimax Auditability Frontier

The ambitious target is

\[
C_{\mathrm{static}}^*
=
\sup_{\pi\in\Pi}
\inf_{M\in\mathcal M_1}
I_{M,\pi}(Z;A\mid T).
\]

This static quantity does **not** by itself imply a sequential detection-time
bound. A full theorem must define an adaptive policy class, a universal
predictable decoder or test, a type-II or expected-stopping-time criterion, and
the minimax exchanges needed to pass from mechanism-wise information growth to
a uniform procedure.

Subject to those additional results, the desired theory should characterize:

- mechanism classes for which the relevant adaptive audit value is zero;
- classes for which that value is positive;
- an optimal or approximately optimal probe law;
- and a detection complexity of order
  \(\log(1/\alpha)/C^*\), together with a matching least-favourable converse,
  for a precisely defined adaptive value \(C^*\).

This complexity statement is a research target. It is not established in the
repository and does not follow from the information-radius identity alone.

## Exact Laboratory: TraceTwin

The first model organism should make passive non-identifiability exact rather
than approximate.

Assume

\[
0<p\le\frac12,
\qquad
0\le\rho<\frac12,
\]

and take all noise variables below to be independent of \(Z\) and of one
another within their respective mechanisms.

Let

\[
Z\sim\operatorname{Bernoulli}(1/2),
\qquad
T=Z\oplus N_T,
\qquad
N_T\sim\operatorname{Bernoulli}(p).
\]

Define a latent-bypass mechanism

\[
M_{\mathrm{bypass}}:
\qquad
A=Z\oplus N_A,
\qquad
N_A\sim\operatorname{Bernoulli}(\rho),
\]

and its transcript-mediated twin

\[
M_{\mathrm{med}}:
\qquad
A=T\oplus N_V,
\qquad
N_V\sim\operatorname{Bernoulli}(r),
\]

where

\[
r=p+\rho-2p\rho.
\]

The two mechanisms have exactly the same passive \(P(T,A)\). Consequently, no
method measurable with respect to \(\sigma(T,A)\) can distinguish them: every
passive audit statistic has the same law under the two mechanisms. The visible
trace graph can also be held fixed. Once the randomized label \(Z\) is made
available to the audit, however,

\[
I_{M_{\mathrm{bypass}}}(Z;A\mid T)
=h_2(r)-h_2(\rho)>0,
\qquad
I_{M_{\mathrm{med}}}(Z;A\mid T)=0.
\]

Thus the construction proves that passive \(\sigma(T,A)\)-measurable access is
insufficient; it does not by itself prove that intervention is the only possible
source of additional identifying information.

> No passive audit measurable with respect to \(\sigma(T,A)\) can distinguish
> transcript mediation from latent bypass in the TraceTwin construction.

The exact-clamp audit is a second, explicitly controlled regime. Randomize
\(Z\sim\operatorname{Bernoulli}(1/2)\) and impose both
\(\operatorname{do}(Z=z)\) and \(\operatorname{do}(T=t)\). Then the visible
trace is identical across arms, and

\[
I_{M_{\mathrm{bypass}}}(Z;A\mid T=t)
=1-h_2(\rho),
\qquad
I_{M_{\mathrm{med}}}(Z;A\mid T=t)=0.
\]

This controlled-clamp quantity is deliberately different from the passive-twin
conditional information \(h_2(r)-h_2(\rho)\). The paper must not conflate the
two regimes.

TraceTwin should test:

- false-positive control under \(M_{\mathrm{med}}\);
- power and confidence coverage under \(M_{\mathrm{bypass}}\);
- monotonicity under mixtures of the two mechanisms;
- agreement with the analytic values in both the passive-label and controlled-
  clamp regimes;
- adaptive-probe validity;
- and the failure of all passive trace-only baselines.

The point of TraceTwin is not synthetic performance. It is an exact
identifiability and calibration laboratory for the claimed certificate.

## Real-System Experiment

The preferred realistic benchmark is an agent with private tool results,
private memory, or policy state that is hidden or redacted at the logging
boundary. [AgentDojo](https://arxiv.org/abs/2406.13352)-style workspace,
banking, email, and travel tasks are natural candidates because they expose
real tool actions and explicit security properties.

### Intervention Protocol

1. Select a consequential action boundary: transfer, recipient selection,
   approval, deletion, message send, or privileged API call.
2. Construct natural paired private records that differ in one security-relevant
   field, such as authorization, recipient ownership, policy status, or an
   indirect prompt injection.
3. Match pairs on the public task and structured transcript class.
4. Checkpoint or replay the agent at the action-binding boundary.
5. Interchange only the declared private state using on-support values from the
   matched pair.
6. Hold the public transcript, model, prompt, and all unrelated state fixed.
7. Measure the distribution of the real deployed action, not only token logits.

The execution sink should be a structured action such as

\[
A\in
\left\{
\text{recipient},
\text{amount},
\text{approve/deny},
\text{tool endpoint},
\text{write target}
\right\}.
\]

The strongest experimental statement has the form

\[
T^{(0)}=T^{(1)},
\qquad
P(A\mid Z=0)\ne P(A\mid Z=1),
\]

and therefore:

> Over the declared intervention family, the visible transcript is
> statistically insufficient to simulate deployed action behavior.

Only exact or predeclared trace-equivalent pairs enter the primary certificate.
Off-manifold zero, blank, Gaussian, and arbitrary-text ablations are retained
only as cautionary baselines.

### Required Controls

- active hidden channel;
- transcript-mediated visible twin;
- dormant private state;
- disconnected channel;
- same-class nuisance swap;
- full-logging oracle;
- off-manifold blank/noise ablation;
- transcript-only classifier or monitor;
- marginal action-rate comparison.

### Primary Metrics

- action-level TV, JS, or bounded decision advantage;
- anytime-valid evidence against transcript sufficiency;
- lower and upper confidence certificates;
- exact structured-trace equivalence rate;
- false-positive rate and power;
- probe budget versus certified residual capacity;
- fixed versus adaptive auditor performance;
- abstention rate when the two certificates do not meet.

For a balanced binary probe, conditional JS is the mutual information between
the probe and action. It should be estimated on discrete, safety-relevant action
outcomes with task-block bootstrap or randomization inference, not through a
fragile neural MI estimator.

## Two-Week Go/No-Go Gate

Do not rewrite the full paper before this gate is passed.

### Week 1: TraceTwin

- implement hidden and visible twins;
- verify numerical equality of passive \(P(T,A)\);
- calibrate the finite-sample certificate;
- test optional stopping and adaptive probes;
- compare against passive transcript-only classifiers.

### Week 2: One Real Action Boundary

- build 50--100 paired private-state cases;
- run at least two open-weight tool-use models or two task suites;
- use 8--16 stochastic repetitions per intervention arm where feasible;
- evaluate actual tool actions and all negative controls.

### Go Criteria

- null false-positive rate at or below the nominal 5% level;
- at least 80% power for a prespecified meaningful action effect;
- passive TraceTwin classifier AUC at or below 0.55;
- structured-trace equivalence rate at least 95%, preferably exact by design;
- a positive action-effect lower certificate in the realistic active condition;
- null results for dormant, disconnected, same-class, and visible-twin controls;
- replication across at least two models or two suites.

### No-Go Criteria

- effects appear only under zero, blank, Gaussian, or arbitrary-text ablations;
- natural on-support private-state swaps do not change real actions;
- the transcript reliably reveals the randomized probe arm;
- the result requires access to logits or an unstable neural MI estimator;
- passive methods distinguish the supposedly observationally identical twins;
- no useful upper certificate can be obtained beyond raw embedding-width
  capacity; or
- the empirical result reduces to a controller following a private report that
  explicitly contains the action label.

If the no-go conditions hold, stop the project rather than returning to the
previous capacity-map narrative.

## What to Keep From the Current Repository

Keep and repurpose:

- the replay and intervention infrastructure in `experiments/7.3_intervention/`;
- the shared trace schema and utilities in `src/`;
- processed artifacts needed to reproduce existing pilot results;
- discrete action-distribution evaluation code;
- the current paper source as a record of the abandoned formulation.

Demote to supporting or appendix material:

- `experiments/7.1_static_certificate/` and the raw min-cut capacity map;
- proxy and neural-MI diagnostics in `experiments/7.2_dynamic_certificate/`;
- LLaDA Gaussian perturbations in `experiments/7.5_diffusion_certificate/`;
- the current direct private-report swap in
  `experiments/7.6_multi_agent_certificate/`.

Before reusing `experiments/7.4_synthetic_gt/`, repair the existing mismatch
between the data generator's logit noise and the reported analytic “true MI.” A
ground-truth experiment cannot serve as certificate validation while its target
omits noise present in the generator.

## Literature Boundary

The paper must not claim novelty for conditional mutual information, generic
activation patching, or counterfactual action sensitivity alone.

- Faithfulness has already been formulated as mediated information flow with
  prompt-to-answer shortcuts that bypass visible CoT; see
  [Jia, Benton, and Easley (2026)](https://arxiv.org/abs/2605.24286).
- CoT monitorability and conditional-information limitations are already
  developed in [Anwar et al. (2026)](https://arxiv.org/abs/2602.18297).
- Activation monitoring, counterfactual action influence, and matched replay for
  latent multi-agent communication are directly approached by
  [VLA (2026)](https://arxiv.org/abs/2608.19161).
- Hidden-objective auditing with behavioral and activation-based methods is
  studied by [Marks et al. (2025)](https://arxiv.org/abs/2503.10965).
- Steganographic collusion and paraphrase defenses are studied by
  [Mathew et al. (2024)](https://arxiv.org/abs/2410.03768).
- Two-run noninterference is a classical hyperproperty; see
  [Clarkson and Schneider (2010)](https://journals.sagepub.com/doi/10.3233/JCS-2009-0393).
- Cryptographic constructions rule out unrestricted absence certification, even
  under strong access models; see
  [Kalavasis et al. (2024)](https://arxiv.org/abs/2406.05660) and
  [Draguns et al. (2024)](https://arxiv.org/abs/2406.02619).
- Anytime-valid confidence sequences for adaptive interventions are not by
  themselves new; see
  [Certified Interventional Fidelity](https://proceedings.mlr.press/v337/asiaee26d.html).
- AgentDojo already supplies dynamic tool-use environments spanning realistic
  security tasks and prompt-injection attacks; see
  [Debenedetti et al. (2024)](https://arxiv.org/abs/2406.13352). Follow-on work
  demonstrates private-data leakage during agent task execution; see
  [Wu et al. (2025)](https://arxiv.org/abs/2506.01055).
- The classical information-radius and redundancy-capacity backbone is surveyed
  by
  [Csiszár and Shields](https://www.renyi.hu/~csiszar/Publications/Information_Theory_and_Statistics:_A_Tutorial.pdf).

The intended novelty is the combination of:

1. transcript simulation deficiency as the audit object;
2. mathematically dual simulator and witness certificates;
3. transcript-preserving, on-support randomized interventions;
4. sequential anytime-valid evidence for an agent audit;
5. a minimax auditability frontier and matching converse; and
6. experiments on consequential actions with exact passive twins and strict
   negative controls.

The differentiation from crowded CoT-faithfulness work should be stated
directly:

> We do not attempt to identify which latent computation constitutes the
> model's “true reasoning.” We ask whether the public transcript is sufficient
> to simulate safety-relevant actions, and we give intervention-relative,
> sequentially valid procedures to reject or certify that claim.

In short:

- CMI and Blackwell deficiency provide the mathematical skeleton, not the
  novelty.
- TraceTwin establishes the insufficiency of passive \(\sigma(T,A)\)-measurable
  auditing and the value of randomized-probe access.
- Simulator/witness duality supplies the audit object.
- The e-process supplies anytime validity.
- Coverage and no-free-lunch results enforce scope discipline.
- A real tool-action benchmark supplies deployment meaning.

Together these components aim at an **active audit calculus for transcript
insufficiency**.

## Claim Discipline

The paper may claim:

> Relative to the declared distribution, access model, logging boundary, and
> admissible probe family, the observed action law cannot be simulated from the
> transcript within the certified error.

It may claim transcript sufficiency only when a uniform upper certificate over
the declared probe family has actually been established.

It must not claim:

- recovery of the full latent state;
- absence of every possible hidden channel;
- universal transcript faithfulness;
- mechanism identification from a Markov-equivalence class;
- or decoder-independent non-recoverability from failure of a finite monitor.

## Immediate Decision

The project should proceed only if the TraceTwin calibration, sequential
certificate, and one real trace-clamped action experiment pass the two-week
gate. If they do, the paper should be rewritten around transcript simulation
deficiency from the first page. If they do not, the current Dual Certificates
paper should be shelved rather than incrementally expanded.
