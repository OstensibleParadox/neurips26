# neurips26 Working Notes

<!--
FILE-ROLE INDEX.

The canonical POPL27 theory source is `popl27_magwalk_sheaf_bridge.md`.
`epistemic_cut_hierarchy.md` is a roadmap from existing artifacts to future
proof obligations. The former `information_sheaf_pearl.md` note has been
merged into the canonical note and removed to avoid parallel, conflicting
theory sources.
-->

## Theory Notes

- [popl27_magwalk_sheaf_bridge.md](popl27_magwalk_sheaf_bridge.md) is the
  canonical theory note. It states the corrected thesis: Pearl causality
  supplies causal syntax; enriched `MAGWalk` / `SheafMAGWalk` supplies the
  probability-sheaf bridge.
- [epistemic_cut_hierarchy.md](epistemic_cut_hierarchy.md) is a roadmap. It
  connects the existing NeurIPS/Lean finite certificate artifacts to the POPL27
  bridge and maps later continuous proof obligations.
- `information_sheaf_pearl.md` has been removed. Its useful material was merged
  into the canonical MAGWalk note; its old framing was superseded because Pearl
  causality alone does not carry stalks, restriction maps, pushforwards,
  collider gluing, or capacity certificates.

## Lean Artifact

The current Lean `MAGWalk` is a graph-level certificate for large-step walks in
the moralized ancestral graph. Any probability/sheaf-carrying version should be
introduced separately, for example as `SheafMAGWalk`, and should project down to
the checked graph-level `MAGWalk`.
