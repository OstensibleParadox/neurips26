# OpenReview Feedback

**Paper Title:** Dual Certificates for Agent Audit: Separating Structural Unrecoverability from Decision Relevance
**Secondary Area Focus:** Decision making, reinforcement learning, and control (e.g., hierarchical RL, multi-agent systems, agentic AI)

## Summary
The paper proposes a dual-certificate framework for auditing deployed language-model agents, addressing the challenge of unrecorded or hidden states. It separates the audit into two quantities: a static certificate (an upper bound on residual hidden-state entropy based on deployment topology and network min-cut) and a dynamic certificate (a lower bound on residual decision relevance using probing techniques such as replay, intervention, and proxy). The framework is evaluated across several agentic setups, including a ReAct agent, a diffusion-based language model (LLaDA), and a multi-agent communication edge. From the perspective of decision making and multi-agent systems, the paper offers a principled, information-theoretic approach to analyzing information flow and behavioral dependence in agent architectures.

## Strengths
- **Novel Formalism:** The separation of structural unrecoverability (capacity) and decision relevance (activation) provides a clear, principled framework for agent auditing.
- **Relevance to Agentic AI:** As multi-step decision-making agents are increasingly deployed in complex topologies, bounding the impact of unobserved states is highly pertinent.
- **Diverse Empirical Validation:** The experiments cover a good breadth of agent architectures, including single-agent tool use (ReAct), multi-agent communication edges, and diffusion denoising trajectories.
- **Rigor:** The incorporation of a Lean 4 mechanized artifact for structural reductions adds confidence to the theoretical claims.

## Weaknesses
- **Limited Scope in RL/Control:** While highly relevant to "agentic AI" (specifically LLM-based agents), the paper's connection to traditional reinforcement learning, control theory, or standard POMDP frameworks is somewhat weak. The methodologies are tailored to language model traces and discrete API calls.
- **Conservative Static Bounds:** The static certificate relies on worst-case capacity budgets (e.g., $K \log |\mathcal{V}|$). In practical, complex hierarchical or multi-agent RL systems, this bound might be excessively loose, reducing its diagnostic utility without extensive empirical tightening.
- **Observational Bottlenecks:** As acknowledged by the authors, the proxy-based dynamic certificate can suffer from severe observational bottlenecks, meaning the lower bound could be arbitrarily weak if the chosen predictor class or proxy is inadequate.
- **Multi-Agent Topology Depth:** The multi-agent experiment is relatively simple (a single worker-to-controller report edge). Evaluating the cut-set approach on more complex, decentralized multi-agent interaction topologies would strengthen the paper's applicability to this area.

## Questions
1. How might this framework be adapted or connected to traditional POMDPs or state-abstraction concepts in reinforcement learning literature?
2. In highly complex multi-agent systems with continuous communication channels or decentralized execution, how computationally feasible is it to construct tight per-edge capacity bounds for the static certificate?
3. Could adversarial agent behavior (e.g., steganographic encoding in the visible trace) trivially defeat the proxy or intervention certificates, and how can an auditor choose an admissible probe taxonomy to mitigate this?

## Rating
7: Good paper, accept
