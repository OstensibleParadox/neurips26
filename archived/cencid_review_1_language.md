# OpenReview Feedback

**Title**: Output Traces Are Not Safety Certificates: Static and Dynamic Certificates for Hidden-State Influence in LLM Agents

**Primary Area**: Language and multimodal language models (e.g., text generation, summarization, VQA)

## Summary
The paper addresses the challenge of identifying hidden-state influence in LLM agents operating under partial observability. It highlights that behavioral output traces cannot reliably certify latent decision relevance without additional structural assumptions. To resolve this, the authors propose a dual-certificate architecture: a static certificate that upper-bounds the residual hidden-state uncertainty based on deployment topology (using min-cut network information theory) and a dynamic certificate that lower-bounds decision-relevant influence through admissible causal behavioral probes (e.g., controlled replay, interventions, proxies). The framework is empirically demonstrated across three diverse setups: ReAct agents (revealing dormant capacity), a diffusion-LM (LLaDA) (showing late-binding active state), and a multi-agent system (near-saturation hidden influence). Furthermore, finite-discrete information-theoretic claims are mechanically verified in Lean 4.

## Strengths
1. **Novel and Rigorous Framework:** The separation of structural capacity (static bounds) and actual behavioral usage (dynamic bounds) is a highly principled way to audit LLM agents. The use of information-theoretic bounds for formalizing partial observability is well executed.
2. **Mechanized Verification:** A significant strength is the formal verification of the finite-discrete claims using Lean 4, which increases the trustworthiness of the theoretical foundations.
3. **Comprehensive Empirical Evaluation:** Testing the framework on a standard autoregressive tool-use agent (ReAct), a continuous intermediate-state agent (diffusion-LM LLaDA), and a multi-agent communication setting provides a convincing demonstration of the method's versatility.

## Weaknesses
1. **Probe Misspecification Risks:** The dynamic certificate's validity depends critically on the conditional Markov assumption ($X_t \to S_t \to A_t \mid \tilde T_t$). If the admissible probe is misspecified or fails to capture the true causal path, the lower bound may severely underestimate actual decision relevance.
2. **Estimation in Continuous Spaces:** While the discrete-action estimators are straightforward (e.g., Jensen-Shannon divergence), continuous-action estimators rely on InfoNCE or MINE, which introduces optimization instabilities and critic-class error. The practical impact of these errors on the lower bounds is not deeply explored.
3. **Software Orthogonality Assumption:** The tightness of the static certificate's additive decomposition relies on software orthogonality. In complex LLM deployments where hidden states are heavily entangled, the bound might become quite loose, reducing its practical utility.

## Questions
1. How does the choice and optimization of the probe architecture in continuous action spaces (InfoNCE/MINE) affect the variance and reliability of the dynamic certificate? Do you have empirical results regarding sample complexity?
2. In cases where software orthogonality fails, how loose does the static certificate become in practical systems compared to the additive decomposition?
3. Can you discuss potential mitigation strategies if an auditor suspects the dynamic certificate is underestimating influence due to probe misspecification?

## Rating
8: Accept, Good paper
