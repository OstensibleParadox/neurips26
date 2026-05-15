# OpenReview Feedback

**Paper:** Dual Certificates for Agent Audit: Separating Structural Unrecoverability from Decision Relevance
**Reviewer Focus:** Secondary Area - Socio-technical aspects of AI (e.g., fairness, interpretability, privacy, safety, governance)

## Summary
The paper proposes a dual-certificate framework for auditing deployed language-model agents. It formally separates two quantities that are often conflated in black-box evaluations: "structural unrecoverability" (the amount of operative state that escapes the logged trace, measured by a static upper bound $\varepsilon_\text{state}^\text{UB}$) and "decision relevance" (the extent to which that residual hidden state actually drives behavior, measured by a dynamic lower bound $\delta_\text{act}^\text{LB}$). By leveraging topological cut-set bounds for the static certificate and conditional data processing inequalities via probes (replay, intervention, proxy) for the dynamic certificate, the framework equips auditors with a principled way to evaluate AI agents. The authors demonstrate this protocol across three relevant scenarios: a ReAct agent's unlogged scratchpad, a diffusion language model's denoising trajectory, and a multi-agent private communication edge.

## Strengths
* **High Relevance to AI Governance and Safety:** The conceptual separation of dormant unrecoverable state from active, decision-driving hidden capacity is a significant contribution to the socio-technical study of AI. It gives internal alignment teams and external regulators a much more precise language and toolset for compliance auditing than simple "hiddenness" scores.
* **Rigorous Formal Foundation:** The framing of the static certificate as a network-information-theoretic cut-set bound, alongside the mechanization of structural reductions in Lean 4, provides the kind of verifiable guarantees that are highly desirable in formal safety contexts. 
* **Versatility Across Risky Topologies:** The methodology effectively generalizes across diverse paradigms where safety risks typically emerge, such as potential scratchpad steganography, latent decision-making in diffusion processes, and covert collusion in multi-agent communication edges.

## Weaknesses
* **Dependence on White/Gray-Box Access:** The static bound ($\varepsilon_\text{state}^\text{UB}$) requires structural access to the deployment graph and interface budgets, while the most effective dynamic bounds rely on causal interventions or controlled replay. In real-world governance scenarios, third-party auditors or regulatory bodies may only have black-box API access, severely limiting the practical deployment of this framework.
* **Vulnerability to Observational Bottlenecks:** As acknowledged by the authors, read-only proxy estimators for the dynamic certificate can suffer from finite-sample bias and variance, or hit an observational ceiling if baseline predictability is high. This forces reliance on interventional access, which may break deployment constraints.
* **Adversarial Robustness:** The paper does not deeply explore adversarial evasion. A sufficiently capable agent might detect the slight distribution shifts associated with replay or intervention probes and intentionally mask its reliance on hidden states, thereby spoofing the dynamic certificate.

## Questions
1. How does the framework perform in adversarial settings where a highly capable agent might deduce it is under audit (e.g., recognizing the intervention or replay state) and alter its behavior to artificially minimize $\delta_\text{act}^\text{LB}$?
2. In regulatory contexts where only black-box access is granted (e.g., interacting with an API), how loose do the static bounds become if they must be inferred solely from external rate limits and observable token counts rather than the true internal DAG?
3. Could you expand on the practical safety applications of the temporal activation profiles? For instance, how might the late-binding discovery in LLaDA be operationalized to build runtime tripwires or safety monitors in deployment?

## Rating
8: Accept, Good paper