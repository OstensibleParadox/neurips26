import FiniteQuerySandbox.DAG.Trail

open Finset

namespace FiniteQuerySandbox

noncomputable section

/--
Bayes-ball step relation over `(node, arrival-direction)` states.  A step is
available when the edge to the next node has the recorded orientation and the
local direction-only triple at the current node is not blocked by `Z`.
-/
inductive BayesBallStep (G : DAG) (Z : Finset ℕ) :
    ℕ × TrailDir → ℕ × TrailDir → Prop where
  | step {v w : ℕ} {arrival departure : TrailDir}
      (hEdge : TrailDir.edgeIntoCurrent G v w departure)
      (hopen : ¬ DirectionalTripleBlocked G Z v arrival departure) :
      BayesBallStep G Z (v, arrival) (w, departure)

/-- Reachability in the Bayes-ball state graph. -/
def BayesBallReachable (G : DAG) (Z : Finset ℕ)
    (s t : ℕ × TrailDir) : Prop :=
  Relation.ReflTransGen (BayesBallStep G Z) s t

/-- Explicit Bayes-ball paths, used when proofs need a two-step scan window. -/
inductive BayesBallPath (G : DAG) (Z : Finset ℕ) :
    ℕ × TrailDir → ℕ × TrailDir → Type where
  | nil (s : ℕ × TrailDir) : BayesBallPath G Z s s
  | cons {s t u : ℕ × TrailDir}
      (step : BayesBallStep G Z s t)
      (rest : BayesBallPath G Z t u) :
      BayesBallPath G Z s u

namespace BayesBallPath

/-- Number of Bayes-ball steps in an explicit path. -/
def length {G : DAG} {Z : Finset ℕ} :
    {s t : ℕ × TrailDir} → BayesBallPath G Z s t → ℕ
  | _, _, nil _ => 0
  | _, _, cons _ rest => rest.length + 1

/-- Forget an explicit Bayes-ball path to reflexive-transitive reachability. -/
def toReachable {G : DAG} {Z : Finset ℕ} :
    {s t : ℕ × TrailDir} → BayesBallPath G Z s t → BayesBallReachable G Z s t
  | _, _, nil _ => Relation.ReflTransGen.refl
  | _, _, cons step rest => (Relation.ReflTransGen.single step).trans rest.toReachable

/-- Append a final Bayes-ball step to an explicit path. -/
def snoc {G : DAG} {Z : Finset ℕ} {s t u : ℕ × TrailDir}
    (p : BayesBallPath G Z s t) (step : BayesBallStep G Z t u) :
    BayesBallPath G Z s u :=
  match p with
  | nil _ => cons step (nil u)
  | cons head rest => cons head (rest.snoc step)

/--
States whose node-membership proof is required by the compressed path scanner.
For a collider window `(a, _) → (b, into) → (c, outOf)`, the scanner jumps
directly from `a` to `c`, so `b` is deliberately not required here.
-/
inductive RequiredState {G : DAG} {Z : Finset ℕ} :
    {s t : ℕ × TrailDir} → BayesBallPath G Z s t → ℕ × TrailDir → Prop where
  | one {s mid : ℕ × TrailDir} (step : BayesBallStep G Z s mid) :
      RequiredState (BayesBallPath.cons step (BayesBallPath.nil mid)) mid
  | colliderTarget {s mid next finish : ℕ × TrailDir}
      {step₁ : BayesBallStep G Z s mid}
      {step₂ : BayesBallStep G Z mid next}
      {rest : BayesBallPath G Z next finish}
      (hcoll : mid.2 = TrailDir.into ∧ next.2 = TrailDir.outOf) :
      RequiredState (BayesBallPath.cons step₁ (BayesBallPath.cons step₂ rest)) next
  | colliderRest {s mid next finish : ℕ × TrailDir}
      {step₁ : BayesBallStep G Z s mid}
      {step₂ : BayesBallStep G Z mid next}
      {rest : BayesBallPath G Z next finish}
      {q : ℕ × TrailDir}
      (hcoll : mid.2 = TrailDir.into ∧ next.2 = TrailDir.outOf)
      (hreq : RequiredState rest q) :
      RequiredState (BayesBallPath.cons step₁ (BayesBallPath.cons step₂ rest)) q
  | noncolliderTarget {s mid next finish : ℕ × TrailDir}
      {step₁ : BayesBallStep G Z s mid}
      {step₂ : BayesBallStep G Z mid next}
      {rest : BayesBallPath G Z next finish}
      (hnot : ¬ (mid.2 = TrailDir.into ∧ next.2 = TrailDir.outOf)) :
      RequiredState (BayesBallPath.cons step₁ (BayesBallPath.cons step₂ rest)) mid
  | noncolliderRest {s mid next finish : ℕ × TrailDir}
      {step₁ : BayesBallStep G Z s mid}
      {step₂ : BayesBallStep G Z mid next}
      {rest : BayesBallPath G Z next finish}
      {q : ℕ × TrailDir}
      (hnot : ¬ (mid.2 = TrailDir.into ∧ next.2 = TrailDir.outOf))
      (hreq : RequiredState (BayesBallPath.cons step₂ rest) q) :
      RequiredState (BayesBallPath.cons step₁ (BayesBallPath.cons step₂ rest)) q

/-- A first target reached with `outOf` arrival is never a collider target. -/
lemma required_first_target_of_outOf {G : DAG} {Z : Finset ℕ}
    {s mid finish : ℕ × TrailDir}
    (step : BayesBallStep G Z s mid)
    (rest : BayesBallPath G Z mid finish)
    (hmid : mid.2 = TrailDir.outOf) :
    RequiredState (BayesBallPath.cons step rest) mid := by
  cases rest with
  | nil _ =>
      exact RequiredState.one step
  | cons step₂ rest₂ =>
      exact RequiredState.noncolliderTarget (by
        intro hcoll
        rw [hmid] at hcoll
        cases hcoll.1)

/-- Required states of a suffix remain required after an `outOf` first target. -/
lemma required_rest_of_outOf {G : DAG} {Z : Finset ℕ}
    {s mid finish : ℕ × TrailDir}
    (step : BayesBallStep G Z s mid)
    (rest : BayesBallPath G Z mid finish)
    (hmid : mid.2 = TrailDir.outOf)
    {q : ℕ × TrailDir}
    (hreq : RequiredState rest q) :
    RequiredState (BayesBallPath.cons step rest) q := by
  cases rest with
  | nil _ =>
      cases hreq
  | cons step₂ rest₂ =>
      exact RequiredState.noncolliderRest (by
        intro hcoll
        rw [hmid] at hcoll
        cases hcoll.1) hreq

end BayesBallPath

lemma BayesBallStep.of_active_triple {G : DAG} {Z : Finset ℕ}
    {a b c : ℕ} {arrival departure : TrailDir}
    (hab : TrailDir.edgeIntoCurrent G a b arrival)
    (hbc : TrailDir.edgeIntoCurrent G b c departure)
    (hactive : ¬ TripleBlocked G Z a b c) :
    BayesBallStep G Z (b, arrival) (c, departure) :=
  BayesBallStep.step hbc
    (by
      rwa [directionalTripleBlocked_iff_tripleBlocked hab hbc])

theorem bayesBallReachable_of_active_trail_from_prev {G : DAG} {Z : Finset ℕ}
    {prev u v : ℕ} {arrival : TrailDir}
    (hprev : TrailDir.edgeIntoCurrent G prev u arrival)
    (t : Trail G u v)
    (h_active : ¬ TrailBlocked G Z (prev :: t.toList)) :
    ∃ final_dir, BayesBallReachable G Z (u, arrival) (v, final_dir) := by
  induction t generalizing prev arrival with
  | nil v =>
      exact ⟨arrival, Relation.ReflTransGen.refl⟩
  | forward h tail ih =>
      rename_i u0 w0 v0
      have hhead : ¬ TripleBlocked G Z prev u0 w0 :=
        not_tripleBlocked_head_of_not_trailBlocked_trail (t := tail) h_active
      have hstep :
          BayesBallStep G Z (u0, arrival) (w0, TrailDir.into) := by
        exact BayesBallStep.of_active_triple hprev
          (by simpa [TrailDir.edgeIntoCurrent] using h) hhead
      have htail_active : ¬ TrailBlocked G Z (u0 :: tail.toList) :=
        not_trailBlocked_tail_of_not_trailBlocked_cons h_active
      rcases ih (prev := u0) (arrival := TrailDir.into)
          (by simpa [TrailDir.edgeIntoCurrent] using h) htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, (Relation.ReflTransGen.single hstep).trans htail⟩
  | backward h tail ih =>
      rename_i u0 w0 v0
      have hhead : ¬ TripleBlocked G Z prev u0 w0 :=
        not_tripleBlocked_head_of_not_trailBlocked_trail (t := tail) h_active
      have hstep :
          BayesBallStep G Z (u0, arrival) (w0, TrailDir.outOf) := by
        exact BayesBallStep.of_active_triple hprev
          (by simpa [TrailDir.edgeIntoCurrent] using h) hhead
      have htail_active : ¬ TrailBlocked G Z (u0 :: tail.toList) :=
        not_trailBlocked_tail_of_not_trailBlocked_cons h_active
      rcases ih (prev := u0) (arrival := TrailDir.outOf)
          (by simpa [TrailDir.edgeIntoCurrent] using h) htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, (Relation.ReflTransGen.single hstep).trans htail⟩

def bayesBallPath_of_active_trail_from_prev {G : DAG} {Z : Finset ℕ}
    {prev u v : ℕ} {arrival : TrailDir}
    (hprev : TrailDir.edgeIntoCurrent G prev u arrival)
    (t : Trail G u v)
    (h_active : ¬ TrailBlocked G Z (prev :: t.toList)) :
    Σ final_dir, BayesBallPath G Z (u, arrival) (v, final_dir) := by
  induction t generalizing prev arrival with
  | nil v =>
      exact ⟨arrival, BayesBallPath.nil (v, arrival)⟩
  | forward h tail ih =>
      rename_i u0 w0 v0
      have hhead : ¬ TripleBlocked G Z prev u0 w0 :=
        not_tripleBlocked_head_of_not_trailBlocked_trail (t := tail) h_active
      have hstep :
          BayesBallStep G Z (u0, arrival) (w0, TrailDir.into) := by
        exact BayesBallStep.of_active_triple hprev
          (by simpa [TrailDir.edgeIntoCurrent] using h) hhead
      have htail_active : ¬ TrailBlocked G Z (u0 :: tail.toList) :=
        not_trailBlocked_tail_of_not_trailBlocked_cons h_active
      rcases ih (prev := u0) (arrival := TrailDir.into)
          (by simpa [TrailDir.edgeIntoCurrent] using h) htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, BayesBallPath.cons hstep htail⟩
  | backward h tail ih =>
      rename_i u0 w0 v0
      have hhead : ¬ TripleBlocked G Z prev u0 w0 :=
        not_tripleBlocked_head_of_not_trailBlocked_trail (t := tail) h_active
      have hstep :
          BayesBallStep G Z (u0, arrival) (w0, TrailDir.outOf) := by
        exact BayesBallStep.of_active_triple hprev
          (by simpa [TrailDir.edgeIntoCurrent] using h) hhead
      have htail_active : ¬ TrailBlocked G Z (u0 :: tail.toList) :=
        not_trailBlocked_tail_of_not_trailBlocked_cons h_active
      rcases ih (prev := u0) (arrival := TrailDir.outOf)
          (by simpa [TrailDir.edgeIntoCurrent] using h) htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, BayesBallPath.cons hstep htail⟩

theorem bayesBallReachable_of_active_trail {G : DAG} {Z : Finset ℕ} {u v : ℕ}
    (t : Trail G u v)
    (h_active : ¬ t.isBlocked Z)
    (init_dir : TrailDir)
    (h_start : t.StartOpen Z init_dir) :
    ∃ final_dir, BayesBallReachable G Z (u, init_dir) (v, final_dir) := by
  cases t with
  | nil v =>
      exact ⟨init_dir, Relation.ReflTransGen.refl⟩
  | forward h tail =>
      rename_i w0
      have hstep :
          BayesBallStep G Z (u, init_dir) (w0, TrailDir.into) :=
        BayesBallStep.step (by simpa [TrailDir.edgeIntoCurrent] using h)
          (by simpa [Trail.StartOpen] using h_start)
      have htail_active : ¬ TrailBlocked G Z (u :: tail.toList) := by
        simpa [Trail.isBlocked, Trail.toList] using h_active
      rcases bayesBallReachable_of_active_trail_from_prev
          (G := G) (Z := Z) (prev := u) (u := w0) (v := v)
          (arrival := TrailDir.into)
          (by simpa [TrailDir.edgeIntoCurrent] using h) tail htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, (Relation.ReflTransGen.single hstep).trans htail⟩
  | backward h tail =>
      rename_i w0
      have hstep :
          BayesBallStep G Z (u, init_dir) (w0, TrailDir.outOf) :=
        BayesBallStep.step (by simpa [TrailDir.edgeIntoCurrent] using h)
          (by simpa [Trail.StartOpen] using h_start)
      have htail_active : ¬ TrailBlocked G Z (u :: tail.toList) := by
        simpa [Trail.isBlocked, Trail.toList] using h_active
      rcases bayesBallReachable_of_active_trail_from_prev
          (G := G) (Z := Z) (prev := u) (u := w0) (v := v)
          (arrival := TrailDir.outOf)
          (by simpa [TrailDir.edgeIntoCurrent] using h) tail htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, (Relation.ReflTransGen.single hstep).trans htail⟩

def bayesBallPath_of_active_trail {G : DAG} {Z : Finset ℕ} {u v : ℕ}
    (t : Trail G u v)
    (h_active : ¬ t.isBlocked Z)
    (init_dir : TrailDir)
    (h_start : t.StartOpen Z init_dir) :
    Σ final_dir, BayesBallPath G Z (u, init_dir) (v, final_dir) := by
  cases t with
  | nil v =>
      exact ⟨init_dir, BayesBallPath.nil (u, init_dir)⟩
  | forward h tail =>
      rename_i w0
      have hstep :
          BayesBallStep G Z (u, init_dir) (w0, TrailDir.into) :=
        BayesBallStep.step (by simpa [TrailDir.edgeIntoCurrent] using h)
          (by simpa [Trail.StartOpen] using h_start)
      have htail_active : ¬ TrailBlocked G Z (u :: tail.toList) := by
        simpa [Trail.isBlocked, Trail.toList] using h_active
      rcases bayesBallPath_of_active_trail_from_prev
          (G := G) (Z := Z) (prev := u) (u := w0) (v := v)
          (arrival := TrailDir.into)
          (by simpa [TrailDir.edgeIntoCurrent] using h) tail htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, BayesBallPath.cons hstep htail⟩
  | backward h tail =>
      rename_i w0
      have hstep :
          BayesBallStep G Z (u, init_dir) (w0, TrailDir.outOf) :=
        BayesBallStep.step (by simpa [TrailDir.edgeIntoCurrent] using h)
          (by simpa [Trail.StartOpen] using h_start)
      have htail_active : ¬ TrailBlocked G Z (u :: tail.toList) := by
        simpa [Trail.isBlocked, Trail.toList] using h_active
      rcases bayesBallPath_of_active_trail_from_prev
          (G := G) (Z := Z) (prev := u) (u := w0) (v := v)
          (arrival := TrailDir.outOf)
          (by simpa [TrailDir.edgeIntoCurrent] using h) tail htail_active with
        ⟨final_dir, htail⟩
      exact ⟨final_dir, BayesBallPath.cons hstep htail⟩

lemma Trail.startOpen_outOf_of_not_mem {G : DAG} {Z : Finset ℕ} {u v : ℕ}
    {t : Trail G u v} (huZ : u ∉ Z) :
    t.StartOpen Z TrailDir.outOf := by
  cases t <;>
    simp [Trail.StartOpen, DirectionalTripleBlocked, TrailDir.colliderAtCurrent, huZ]

theorem bayesBallReachable_of_active_trail_outOf {G : DAG} {Z : Finset ℕ}
    {u v : ℕ} (t : Trail G u v)
    (h_active : ¬ t.isBlocked Z) (huZ : u ∉ Z) :
    ∃ final_dir, BayesBallReachable G Z (u, TrailDir.outOf) (v, final_dir) :=
  bayesBallReachable_of_active_trail t h_active TrailDir.outOf
    (Trail.startOpen_outOf_of_not_mem huZ)

def bayesBallPath_of_active_trail_outOf {G : DAG} {Z : Finset ℕ}
    {u v : ℕ} (t : Trail G u v)
    (h_active : ¬ t.isBlocked Z) (huZ : u ∉ Z) :
    Σ final_dir, BayesBallPath G Z (u, TrailDir.outOf) (v, final_dir) :=
  bayesBallPath_of_active_trail t h_active TrailDir.outOf
    (Trail.startOpen_outOf_of_not_mem huZ)

lemma not_mem_Z_of_active_noncollider {G : DAG} {Z : Finset ℕ} {a b c : ℕ}
    (hactive : ¬ TripleBlocked G Z a b c)
    (hncoll : ¬ TripleCollider G a b c) :
    b ∉ Z := by
  intro hbZ
  exact hactive (Or.inl ⟨hncoll, hbZ⟩)

lemma not_mem_Z_of_active_directional_noncollider {G : DAG} {Z : Finset ℕ}
    {b : ℕ} {arrival departure : TrailDir}
    (hopen : ¬ DirectionalTripleBlocked G Z b arrival departure)
    (hnot : ¬ (arrival = TrailDir.into ∧ departure = TrailDir.outOf)) :
    b ∉ Z := by
  intro hbZ
  exact hopen (Or.inl ⟨by simpa [TrailDir.colliderAtCurrent] using hnot, hbZ⟩)

end

end FiniteQuerySandbox
