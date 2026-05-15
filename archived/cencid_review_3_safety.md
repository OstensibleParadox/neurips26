# OpenReview Feedback: Output Traces Are Not Safety Certificates

## Secondary Area Focus
Socio-technical aspects of AI (e.g., fairness, interpretability, privacy, safety, governance)

## Summary
The paper addresses the crucial safety and governance challenge of latent-variable non-identifiability in LLM agents. It argues that output traces alone are insufficient to certify the absence of decision-relevant hidden state influence. The authors propose a dual-certificate framework consisting of a static upper bound (derived from the agent's deployment topology via min-cut capacity) and a dynamic lower bound (derived from behavioral probing). The work spans three diverse agent architectures (ReAct, diffusion-LM, and multi-agent systems) to empirically demonstrate how these certificates can bound hidden state uncertainty and decision relevance. Furthermore, the paper provides mechanized proofs for its discrete information-theoretic claims using Lean 4.

## Strengths
- **Rigorous Framing for Safety & Governance:** By distinguishing between structural capacity (what could remain hidden) and active decision relevance (what is actually used), the paper offers a robust operational framework for auditing partially-observable systems.
- **Empirical Breadth:** The evaluation across different architectures—especially the multi-agent private-report intervention—is highly relevant to current socio-technical concerns about unlogged, collusive, or deceptive channels in multi-agent deployments.
- **Formal Verification:** The inclusion of Lean 4 formalized proofs for finite-discrete claims significantly bolsters the paper's reliability and appeals to the safety-critical AI community.

## Weaknesses
- **Probe Misspecification Risks:** The dynamic certificate's validity depends strongly on admissible probe specification (the conditional Markov chain requirement). Misspecification could lead to underestimating the true decision relevance, posing a risk in adversarial settings.
- **Scope Limitations (Fixed Marginal):** The audit framework is explicitly scoped to a fixed deployment marginal. This means it might not capture hidden capacities that are activated only under distribution shifts, such as during adaptive red-teaming or deployment drift.
- **Orthogonality Assumption:** The static min-cut certificate relies on software orthogonality for the per-edge additive decomposition to be tight. In highly entangled neural architectures, this assumption might lead to looser bounds.

## Questions
1. How might the framework be extended to handle adaptive distribution shifts or adversarial red-teaming, where the deployment marginal is no longer fixed?
2. Could you provide a more detailed theoretical error analysis for the InfoNCE/MINE-style continuous-action estimators used in the dynamic certificate?
3. How does the audit strategy adapt if an "Untrusted" component learns to compress state in a way that violates the assumed channel capacities?

## Rating
8: Accept, Good Paper