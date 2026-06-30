# Dual Certificates: IEEE S&P 2027 Cycle 2 Plan

This repository is the working home for the security-paper version of **Dual
Certificates**. The target is **IEEE Symposium on Security and Privacy 2027,
Cycle 2**.

As of 2026-06-30:

- Abstract registration deadline: 2026-11-10.
- Paper submission deadline: 2026-11-17.
- Remaining time to full paper: 140 days.
- S&P format: IEEE `conference,compsoc`, US letter, 13 pages of text plus up to
  5 pages for references and appendix, 18 pages total.
- Current paper state: IEEE S&P source uses `IEEEtran` plus
  `paper/ieee_sp_2027.sty`; it compiles to 11 pages with no undefined
  references or citations.
- Current readiness: ML-paper ready about 80%; S&P-ready about 45%.

## Core Reframe

The paper is not a generic LLM-agent audit or probing paper. The S&P version
should be a security paper about **latent causal channels** in neural agents:

> Transcript-level audit can pass while a hidden, action-relevant causal channel
> remains unrecoverable. Security auditing therefore needs certificates for both
> latent-state non-recoverability and residual action relevance.

Pearl-style intervention notation is a foil, not the main target. The paper's
claim is:

> Drawing an intervention in an observed causal graph does not certify that the
> deployed neural mechanism has exposed the information needed for a security
> audit.

The title direction is:

> Dual Certificates for Latent Causal Channels in Neural Agents

## S&P Threat Model

The S&P paper must open with a concrete security setting.

- **Defender/auditor:** reviews logs, transcripts, traces, and declared
  instrumentation for a deployed neural agent.
- **Protected assets:** action integrity, audit completeness, and forensic
  accountability.
- **Failure mode:** the visible transcript omits a hidden state variable that
  remains action-relevant.
- **Security risk:** log-only audit can certify the wrong thing. A system may
  appear compliant while routing, delegation, denoising, or scratchpad state
  still controls the action.
- **Adversarial setting:** a deployment or component can hide, compress, or
  route decision-relevant information through latent channels not represented in
  the audit transcript.
- **Non-goal:** the paper does not claim to recover the full internal state of a
  neural model. It certifies lower bounds and maps where unrecoverable
  action-relevant capacity can reside.

This threat model is mandatory. Without it the paper is an ML audit paper and
will look out of scope for S&P.

## Security Punchline

The central punchline for the introduction:

> Pearl's `do` edits an observed causal graph; security auditing of neural
> agents requires certifying whether hidden, action-relevant causal channels are
> recoverable at all.

Operational form:

- The **capacity map** is an attack-surface map: where can hidden capacity reside
  under the logging boundary?
- The **dynamic certificate** is a detection/forensics primitive: which hidden
  sites actually affect the action?
- The **dual certificate** is the security claim: the transcript omitted state
  that is both unrecoverable and action-relevant.

## Current Repository Contents

- `paper/main.tex` - current paper body. It must stay on IEEE
  `conference,compsoc`.
- `paper/ieee_sp_2027.sty` - local S&P helper package. It centralizes package
  dependencies but must not alter margins, spacing, fonts, or IEEE geometry.
- `paper/references.bib` - current bibliography.
- `paper/figures/` - rendered figures used by the paper.
- `paper/tables/` - generated LaTeX tables and macros used by the paper.
- `paper/SUPPLEMENTARY.md` - current reproduction notes; needs S&P artifact
  rewrite and anonymity cleanup.
- `experiments/7.1_static_certificate/` - capacity-map and min-cut pipelines.
- `experiments/7.2_dynamic_certificate/` - proxy/MI estimator pipelines.
- `experiments/7.3_intervention/` - ReAct intervention and replay pipelines.
- `experiments/7.4_synthetic_gt/` - synthetic ground-truth calibration.
- `experiments/7.5_diffusion_certificate/` - LLaDA temporal certificate scripts.
- `experiments/7.6_multi_agent_certificate/` - multi-agent private-report
  certificate scripts.
- `data/processed/` - checked-in processed artifacts for intervention,
  diffusion, boundary replay, and multi-agent results.
- `src/` - shared trace schema and utilities.
- `docker/` - current Dockerfile scaffold.
- `configs/` - shared configuration files.

## Keep / Delete Policy

Keep:

- Paper source, figures, tables, bibliography.
- All scripts needed to regenerate tables, figures, and processed artifacts.
- Processed data used by paper tables and figures.
- Raw intervention rows already checked into `data/processed/intervention/raw/`.
- Architecture JSON files and experiment configs.

Delete or rewrite:

- Venue-specific NeurIPS wording in paper and experiment docs.
- Any reintroduced NeurIPS style file, NeurIPS package import, or NeurIPS
  template language.
- Author-identifying absolute paths, usernames, local machine paths, and
  acknowledgments.
- Stale README claims that frame the repository as only a benchmark/empirical
  paper.
- Any supplement line that references missing artifacts without a regeneration
  command.
- One-off assistant notes, temporary local files, build products, PDFs, caches,
  and model downloads.

Do not delete:

- `paper/ieee_sp_2027.sty`, unless its package list is folded into a cleaner
  IEEE-compatible build file.
- Processed result artifacts, even if their metadata needs path sanitization.
- Diagnostic scripts with old estimator labels, unless their replacement path is
  documented and the paper no longer depends on them.

## Paper Surgery Plan

### Phase 1: Security Skeleton

Deadline: 2026-07-07.

Actions:

- Replace title and abstract with S&P security framing.
- Add `Threat Model and Security Goal` before the technical setup.
- Keep the introduction free of venue-specific NeurIPS wording.
- Define the security object as a latent causal channel, not a generic hidden
  state.
- State the out-of-scope boundary: no full-state recovery, no universal
  interpretability claim.

Deliverable:

- A paper that a security reviewer can summarize as:
  "This paper audits hidden causal channels that bypass transcript-level logs."

### Phase 2: Main-Text Reorder

Deadline: 2026-07-31.

Target order:

1. Introduction and security failure.
2. Threat model and audit abstraction.
3. Dual certificates.
4. Capacity map as latent-channel attack-surface localization.
5. Dynamic certificates as detection/forensics.
6. Security evaluation.
7. Limitations, ethics, and deployment guidance.

Move or compress:

- Closed-form laboratories move to appendix or become a short bridge.
- Network information background stays appendix-only.
- Proxy estimator diagnostics stay appendix-only.
- Synthetic ground truth stays appendix unless used as a main validity check.

### Phase 3: Security Evaluation

Deadline: 2026-08-31.

Reframe the current experiments as security failure modes:

- **ReAct:** logging-policy bypass through an unlogged scratchpad channel.
- **LLaDA:** temporal latent channel at the final action-binding step.
- **Multi-agent:** private-report edge as a latent delegation channel.

Strengthen if time permits:

- Add a minimal adversarial or compromised-worker case.
- Show one log-only audit that passes while the dynamic certificate remains
  positive.
- Report the capacity map first, then the activation/certificate profile.

### Phase 4: Artifact Hardening

Deadline: 2026-08-31.

Required artifact work:

- Add a top-level `Makefile` with at least `make smoke`, `make tables`, and
  `make figures`.
- Add `requirements.txt` or `environment.yml`.
- Add a data manifest with hashes and regeneration commands.
- Sanitize absolute paths in processed artifacts.
- Remove author-identifying local paths from README, supplement, configs, and
  outputs.
- Ensure the anonymous artifact can be frozen before submission; S&P says
  artifact repositories should not be updated after the paper deadline.

### Phase 5: IEEE Template and Page Budget

Deadline: 2026-09-30.

Template migration status: complete. The source now begins with
`\documentclass[conference,compsoc]{IEEEtran}` and loads
`paper/ieee_sp_2027.sty`. The old NeurIPS style file has been removed. Future
agents must not reintroduce `neurips_2026.sty`, `\usepackage{neurips_*}`, or
NeurIPS submission language.

Actions:

- Keep IEEEtran as the only document class:
  `\documentclass[conference,compsoc]{IEEEtran}`.
- Keep the local package wrapper as `\usepackage{ieee_sp_2027}` unless the
  dependency list is moved into another IEEE-compatible build file.
- Keep author block and acknowledgments absent for anonymous review.
- Fit the main claim into 13 text pages.
- Keep references and appendix within the remaining 5 pages.
- Avoid relying on appendix for the core security claim; reviewers are not
  required to read appendices.

### Phase 6: Submission Risk Package

Deadline: 2026-10-20.

Required text:

- Ethics considerations.
- Harm and dual-use discussion.
- Generative AI usage disclosure.
- Environmental footprint rationale.
- Limitations: validity depends on the declared audit abstraction, probe
  admissibility, finite audit resolution, and logging boundary.

## Milestones

- 2026-07-07: S&P title, abstract, introduction, and threat model skeleton.
- 2026-07-31: Security-framed main draft.
- 2026-08-31: Evaluation and artifact manifest complete.
- 2026-09-30: IEEE `conference,compsoc` 13+5 page draft with overfull tables and
  equations fixed.
- 2026-10-20: Cold-review version.
- 2026-11-03: Dry-run abstract registration metadata: title, abstract, authors,
  ORCIDs, COIs.
- 2026-11-10: Abstract registration.
- 2026-11-16: Full paper submitted at least 24 hours before deadline.
- 2026-11-17: Official full-paper deadline.

## Immediate Next Actions

1. Rewrite `paper/main.tex` abstract and first two pages around the threat model.
2. Add a new `Threat Model and Security Goal` section.
3. Search for and remove any reintroduced venue-specific terms: NeurIPS,
   benchmark paper, generic audit diagnostic.
4. Sanitize paths in `data/processed/intervention/*.json` and
   `data/processed/intervention/*.csv`.
5. Rewrite `paper/SUPPLEMENTARY.md` as an anonymous S&P artifact guide.
6. Add dependency and reproduction entry points.
7. Fix IEEE two-column layout issues: wide theorem equations, wide result
   tables, appendix cross-references, and long artifact paths.

## Repository Boundary

This repository carries only the Dual Certificates security paper, experiments,
and artifacts.

- Lean/formal proof artifact: separate repository `CausalQIF`.
- Infinitesimal Shannon/operator theory manuscript: separate repository
  `infinitesimal-shannon`.

Do not merge those projects back into this repository.
