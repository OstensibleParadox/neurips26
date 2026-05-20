import FiniteQuerySandbox.DAG.Ancestry

open Finset

namespace FiniteQuerySandbox

noncomputable section

/-- Consecutive entries in a list satisfy a relation. -/
def Consecutive (R : ℕ → ℕ → Prop) : List ℕ → Prop
  | [] => True
  | [_] => True
  | a :: b :: rest => R a b ∧ Consecutive R (b :: rest)

/-- A list contains the consecutive triple `a, b, c`. -/
def HasTriple (xs : List ℕ) (a b c : ℕ) : Prop :=
  ∃ pre post : List ℕ, xs = pre ++ a :: b :: c :: post

/-- A trail is a finite undirected walk in the underlying graph. -/
inductive Trail (G : DAG) : ℕ → ℕ → Type where
  | nil (v : ℕ) : Trail G v v
  | forward {u w v : ℕ} (h : G.HasEdge u w) (tail : Trail G w v) : Trail G u v
  | backward {u w v : ℕ} (h : G.HasEdge w u) (tail : Trail G w v) : Trail G u v

namespace Trail

/-- Vertices visited by a trail, in order. -/
def toList {G : DAG} : {u v : ℕ} → Trail G u v → List ℕ
  | _, _, nil v => [v]
  | u, _, forward (u := _) (w := _) (v := _) _ tail => u :: toList tail
  | u, _, backward (u := _) (w := _) (v := _) _ tail => u :: toList tail

/-- Vertices visited by a trail as a finite set. -/
def nodes {G : DAG} {u v : ℕ} (t : Trail G u v) : Finset ℕ :=
  t.toList.toFinset

@[simp]
lemma mem_nodes {G : DAG} {u v a : ℕ} {t : Trail G u v} :
    a ∈ t.nodes ↔ a ∈ t.toList := by
  simp [nodes]

/-- If the start of a trail is a graph node, then so is its endpoint. -/
lemma target_mem_graph_nodes_of_source_mem {G : DAG} {u v : ℕ}
    (t : Trail G u v) (hu : u ∈ G.nodes) :
    v ∈ G.nodes := by
  induction t with
  | nil _ =>
      exact hu
  | forward h tail ih =>
      exact ih (G.edges_subset h).2
  | backward h tail ih =>
      exact ih (G.edges_subset h).1

end Trail

/-- A middle vertex is a collider on the local triple `a-b-c`. -/
def TripleCollider (G : DAG) (a b c : ℕ) : Prop :=
  G.HasEdge a b ∧ G.HasEdge c b

/--
The local triple is blocked by the conditioning set.  Non-colliders are blocked
when conditioned on directly; colliders are blocked unless the collider or one
of its descendants is conditioned on.
-/
def TripleBlocked (G : DAG) (Z : Finset ℕ) (a b c : ℕ) : Prop :=
  (¬ TripleCollider G a b c ∧ b ∈ Z) ∨
    (TripleCollider G a b c ∧ Disjoint ({b} ∪ descendants G b) Z)

/--
Direction of an edge as seen from the vertex being entered.  `into` means the
edge arrow points into the current vertex; `outOf` means the arrow points out of
the current vertex toward the previous one.
-/
inductive TrailDir where
  | into
  | outOf
  deriving DecidableEq

namespace TrailDir

/-- The directed edge orientation by which a trail enters `curr` from `prev`. -/
def edgeIntoCurrent (G : DAG) (prev curr : ℕ) : TrailDir → Prop
  | into => G.HasEdge prev curr
  | outOf => G.HasEdge curr prev

/--
The local triple is a collider exactly when the trail enters the middle vertex
along an incoming arrow and leaves along another arrow into the middle vertex.
-/
def colliderAtCurrent (arrival departure : TrailDir) : Prop :=
  arrival = into ∧ departure = outOf

end TrailDir

/-- Direction-only version of `TripleBlocked`, used by the Bayes-ball scaffold. -/
def DirectionalTripleBlocked (G : DAG) (Z : Finset ℕ) (b : ℕ)
    (arrival departure : TrailDir) : Prop :=
  (¬ TrailDir.colliderAtCurrent arrival departure ∧ b ∈ Z) ∨
    (TrailDir.colliderAtCurrent arrival departure ∧
      Disjoint ({b} ∪ descendants G b) Z)

lemma directionalTripleBlocked_iff_tripleBlocked {G : DAG} {Z : Finset ℕ}
    {a b c : ℕ} {arrival departure : TrailDir}
    (hab : TrailDir.edgeIntoCurrent G a b arrival)
    (hbc : TrailDir.edgeIntoCurrent G b c departure) :
    DirectionalTripleBlocked G Z b arrival departure ↔ TripleBlocked G Z a b c := by
  cases arrival <;> cases departure
  · simp [TrailDir.edgeIntoCurrent] at hab hbc
    have hnot_cb : ¬ G.HasEdge c b := by
      intro hrev
      have hcycle : Relation.TransGen (fun u v => G.HasEdge u v) b b :=
        Relation.TransGen.head hbc (Relation.TransGen.single hrev)
      exact (not_transGen_self_of_wellFounded G.acyclic b) hcycle
    have hnot : ¬ TripleCollider G a b c := fun hcoll => hnot_cb hcoll.2
    simp [DirectionalTripleBlocked, TrailDir.colliderAtCurrent, TripleBlocked, hnot]
  · simp [TrailDir.edgeIntoCurrent] at hab hbc
    have hcoll : TripleCollider G a b c := ⟨hab, hbc⟩
    simp [DirectionalTripleBlocked, TrailDir.colliderAtCurrent, TripleBlocked, hcoll]
  · simp [TrailDir.edgeIntoCurrent] at hab hbc
    have hnot_ab : ¬ G.HasEdge a b := by
      intro hrev
      have hcycle : Relation.TransGen (fun u v => G.HasEdge u v) b b :=
        Relation.TransGen.head hab (Relation.TransGen.single hrev)
      exact (not_transGen_self_of_wellFounded G.acyclic b) hcycle
    have hnot : ¬ TripleCollider G a b c := fun hcoll => hnot_ab hcoll.1
    simp [DirectionalTripleBlocked, TrailDir.colliderAtCurrent, TripleBlocked, hnot]
  · simp [TrailDir.edgeIntoCurrent] at hab hbc
    have hnot_ab : ¬ G.HasEdge a b := by
      intro hrev
      have hcycle : Relation.TransGen (fun u v => G.HasEdge u v) b b :=
        Relation.TransGen.head hab (Relation.TransGen.single hrev)
      exact (not_transGen_self_of_wellFounded G.acyclic b) hcycle
    have hnot : ¬ TripleCollider G a b c := fun hcoll => hnot_ab hcoll.1
    simp [DirectionalTripleBlocked, TrailDir.colliderAtCurrent, TripleBlocked, hnot]

/-- A trail is blocked if at least one internal triple on it is blocked. -/
def TrailBlocked (G : DAG) (Z : Finset ℕ) (xs : List ℕ) : Prop :=
  ∃ a b c : ℕ, HasTriple xs a b c ∧ TripleBlocked G Z a b c

/-- A trail object is blocked by `Z`. -/
def Trail.isBlocked {G : DAG} {u v : ℕ} (Z : Finset ℕ) (t : Trail G u v) : Prop :=
  TrailBlocked G Z t.toList

/--
Opening condition for the first step of a Bayes-ball run generated from a
trail.  Trail blocking only looks at internal triples, so the first vertex must
be handled separately.
-/
def Trail.StartOpen {G : DAG} {u v : ℕ} (Z : Finset ℕ) (init_dir : TrailDir)
    (t : Trail G u v) : Prop :=
  match t with
  | Trail.nil _ => True
  | Trail.forward (u := u) _ _ =>
      ¬ DirectionalTripleBlocked G Z u init_dir TrailDir.into
  | Trail.backward (u := u) _ _ =>
      ¬ DirectionalTripleBlocked G Z u init_dir TrailDir.outOf

lemma HasTriple.cons {xs : List ℕ} {a b c x : ℕ}
    (h : HasTriple xs a b c) :
    HasTriple (x :: xs) a b c := by
  rcases h with ⟨pre, post, hxs⟩
  exact ⟨x :: pre, post, by simp [hxs, List.cons_append]⟩

lemma TrailBlocked.cons {G : DAG} {Z : Finset ℕ} {xs : List ℕ} {x : ℕ}
    (h : TrailBlocked G Z xs) :
    TrailBlocked G Z (x :: xs) := by
  rcases h with ⟨a, b, c, htriple, hblocked⟩
  exact ⟨a, b, c, HasTriple.cons htriple, hblocked⟩

lemma not_trailBlocked_tail_of_not_trailBlocked_cons {G : DAG} {Z : Finset ℕ}
    {xs : List ℕ} {x : ℕ}
    (h : ¬ TrailBlocked G Z (x :: xs)) :
    ¬ TrailBlocked G Z xs := by
  intro htail
  exact h (TrailBlocked.cons htail)

lemma trailBlocked_of_head_tripleBlocked {G : DAG} {Z : Finset ℕ}
    {a b c : ℕ} {xs : List ℕ}
    (h : TripleBlocked G Z a b c) :
    TrailBlocked G Z (a :: b :: c :: xs) := by
  exact ⟨a, b, c, ⟨[], xs, rfl⟩, h⟩

lemma not_tripleBlocked_head_of_not_trailBlocked {G : DAG} {Z : Finset ℕ}
    {a b c : ℕ} {xs : List ℕ}
    (h : ¬ TrailBlocked G Z (a :: b :: c :: xs)) :
    ¬ TripleBlocked G Z a b c := by
  intro htriple
  exact h (trailBlocked_of_head_tripleBlocked htriple)

lemma HasTriple.head_of_trail {G : DAG} {a b c v : ℕ} (t : Trail G c v) :
    HasTriple (a :: b :: t.toList) a b c := by
  cases t with
  | nil v =>
      exact ⟨[], [], by simp [Trail.toList]⟩
  | forward h tail =>
      exact ⟨[], tail.toList, by simp [Trail.toList]⟩
  | backward h tail =>
      exact ⟨[], tail.toList, by simp [Trail.toList]⟩

lemma trailBlocked_of_head_tripleBlocked_trail {G : DAG} {Z : Finset ℕ}
    {a b c v : ℕ} (t : Trail G c v)
    (h : TripleBlocked G Z a b c) :
    TrailBlocked G Z (a :: b :: t.toList) :=
  ⟨a, b, c, HasTriple.head_of_trail t, h⟩

lemma not_tripleBlocked_head_of_not_trailBlocked_trail {G : DAG} {Z : Finset ℕ}
    {a b c v : ℕ} {t : Trail G c v}
    (h : ¬ TrailBlocked G Z (a :: b :: t.toList)) :
    ¬ TripleBlocked G Z a b c := by
  intro htriple
  exact h (trailBlocked_of_head_tripleBlocked_trail t htriple)

end

end FiniteQuerySandbox
