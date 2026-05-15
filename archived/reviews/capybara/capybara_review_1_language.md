# OpenReview Style Feedback

## Summary
The paper introduces a dual-certificate protocol for auditing deployed language-model agents, aiming to separate structural unrecoverability of hidden states from their behavioral decision relevance. The static certificate upper-bounds residual hidden-state entropy based on the deployment topology via a min-cut on untraced channels. The dynamic certificate lower-bounds the residual decision relevance through probes like replay, intervention, and proxy under conditional data processing. Experiments across ReAct, a diffusion LM (LLaDA), and a multi-agent setting show how these tools can identify where hidden capacity is behaviorally used. A Lean 4 formalization of some structural reductions is also provided.

## Strengths
1. **Conceptual Clarity:** The distinction between structural unrecoverability ($\varepsilon_\text{state}^\text{UB}$) and residual decision relevance ($\delta_\text{act}^\text{LB}$) is a valuable contribution. It addresses the limitation of output-only auditing by decoupling the potential for hidden state from its actual causal effect on behavior.
2. **Methodological Rigor:** The use of information-theoretic bounds and causal interventions provides a principled framework. The application of the cut-set bound to time-unrolled DAGs of agents is a novel and rigorous approach to establishing the static certificate.
3. **Diverse Empirical Evaluation:** The framework is applied across three distinct architectures (ReAct scratchpad, LLaDA diffusion steps, multi-agent private reports), demonstrating its versatility and ability to generate insightful activation profiles over different coordinates (module, time step, communication edge).
4. **Formal Verification:** Including a Lean 4 artifact to machine-check structural reductions adds a layer of confidence to the theoretical claims, which is increasingly appreciated in safety and alignment research.

## Weaknesses
1. **Conservative Static Bounds:** The static certificate relies on worst-case capacities (e.g., $K \log |\mathcal{V}|$), which can lead to excessively loose upper bounds in practice. While Appendix G mentions empirical tightening, the main text's reliance on loose structural bounds might limit the practical utility of $\varepsilon_\text{state}^\text{UB}$ as a diagnostic tool.
2. **Proxy Estimator Limitations:** The proxy certificate's utility is heavily constrained by observational bottlenecks and estimator variance. As shown in Appendix C, the cross-entropy difference estimator often yields very small bits and confidence intervals straddling zero, making it less reliable than the causal intervention methods.
3. **Scalability to Complex Architectures:** Extracting the time-unrolled DAG and precisely defining unlogged edge capacities for highly complex, proprietary agents might be challenging. The paper assumes significant structural access, which may not be feasible for all third-party auditors.
4. **Limited Discussion on Continuous Actions:** While the paper mentions using InfoNCE/MINE for continuous action spaces, the empirical evaluation focuses entirely on discrete tool choices or categorical labels. Demonstrating the dynamic certificate on a continuous generation task would strengthen the claims.

## Questions
1. How does the framework scale to agents with highly dynamic control flow where the time-unrolled DAG cannot be statically determined before execution?
2. Can you provide more concrete examples of how an auditor would defensibly calculate empirical conditional budgets ($c_e^\star$) to tighten the static certificate in a real-world scenario without full internal access?
3. For the LLaDA experiment, the late-binding effect at step 10 is clear. However, does this imply that steps 1-9 are largely irrelevant for the final decision, or simply that their influence is fully mediated by the visible trace? Could a different choice of visible trace alter this temporal profile?
4. The Lean 4 formalization relies on external axioms (e.g., conditional DPI). What are the main challenges in deriving these axioms fully within Lean's measure-theoretic foundations, and how much risk does leaving them as axioms pose to the overall formal guarantee?

## Rating
7: Good paper, accept.
