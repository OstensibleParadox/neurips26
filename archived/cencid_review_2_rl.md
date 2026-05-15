# OpenReview Feedback

## Summary
The paper formalizes the non-identifiability of hidden-state influence in LLM agents from observational traces alone. It introduces two certificates to bound decision-relevant hidden influence: a static certificate that upper-bounds the structurally possible hidden capacity based on deployment topology (min-cut), and a dynamic certificate that lower-bounds the behavioral impact of hidden state on decisions using admissible probes (replay, intervention, proxy). The paper applies this dual-certificate framework to three scenarios relevant to agentic AI and decision making: ReAct-style agents (dormant hidden capacity), diffusion-LMs acting as agents (late-binding influence), and multi-agent systems (where peer-reporting channels can carry near-maximal hidden influence). The results underscore that behaviorally identical agents can have vastly different latent reliance on hidden states.

## Strengths
1. **Relevance to Agentic AI and Control**: The paper addresses a crucial safety and transparency problem in sequential decision-making systems with partial observability (e.g., unlogged scratchpads or communication channels in multi-agent setups).
2. **Rigorous Formalization**: The dual-certificate approach provides a grounded, information-theoretic methodology (bounding $H(S_t \mid \tilde T_t)$ and $I(S_t; A_t \mid \tilde T_t)$). This formulation elegantly links structural network capacity to causal behavioral influence.
3. **Empirical Diversity**: The experiments span multiple agent architectures (ReAct, Diffusion LMs, Multi-Agent systems). The multi-agent experiment is particularly compelling for the RL/Agentic community as it demonstrates how private communication channels act as epistemic edges with high decision relevance.
4. **Formal Verification**: The use of Lean 4 to mechanize the core finite-discrete claims adds a strong layer of mathematical rigor rarely seen in standard empirical RL/Agent papers.

## Weaknesses
1. **Assumption of Fixed Deployment Marginal**: As the authors note, the framework assumes a fixed deployment prompt distribution. In standard RL or control, policies often face distribution shift (e.g., out-of-distribution states, exploration vs. exploitation). The applicability of these certificates under dynamic deployment drift or adversarial red-teaming isn't fully explored.
2. **Probe Misspecification Risk**: The dynamic certificate relies heavily on the admissibility of probes ($X_t \to S_t \to A_t$). If the causal graph is misspecified or the proxy probe is insufficient, the lower bound might significantly underestimate the true decision relevance.
3. **Generalization to Continuous Control**: While the paper mentions continuous action spaces and estimators like InfoNCE/MINE, the formal proofs and most concrete experiments are constrained to discrete action spaces (tokens, tool choices). In traditional RL and control, continuous actions are prevalent, and the tightness/stability of these estimators might degrade.

## Questions
1. How does the static certificate scale to hierarchical RL setups where high-level and low-level controllers might share complex, implicitly unlogged state representations?
2. In the multi-agent experiment, you demonstrated the effect of replacing the worker report. How sensitive is the dynamic certificate to the exact choice of counterfactual (e.g., in continuous or highly stochastic multi-agent environments)?
3. Could you elaborate on how these certificates could be practically integrated into a reinforcement learning training loop (e.g., as regularizers) rather than just being used for post-hoc auditing?

## Rating
8: Accept, Good Paper