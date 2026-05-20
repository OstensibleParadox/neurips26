import Mathlib

open Finset

namespace FiniteQuerySandbox

noncomputable section

/-- A finite directed acyclic graph over natural-number node labels. -/
structure DAG where
  nodes : Finset ℕ
  edges : Finset (ℕ × ℕ)
  edges_subset : ∀ {u v : ℕ}, (u, v) ∈ edges → u ∈ nodes ∧ v ∈ nodes
  acyclic : WellFounded fun u v => (u, v) ∈ edges

namespace DAG

/-- Directed edge predicate. -/
def HasEdge (G : DAG) (u v : ℕ) : Prop :=
  (u, v) ∈ G.edges

/--
Build a DAG from a rank function that strictly increases along every edge.
This is a convenient way to construct examples without proving
well-foundedness directly.
-/
def ofRank (nodes : Finset ℕ) (edges : Finset (ℕ × ℕ)) (rank : ℕ → ℕ)
    (edges_subset : ∀ {u v : ℕ}, (u, v) ∈ edges → u ∈ nodes ∧ v ∈ nodes)
    (rank_increases : ∀ {u v : ℕ}, (u, v) ∈ edges → rank u < rank v) : DAG where
  nodes := nodes
  edges := edges
  edges_subset := edges_subset
  acyclic :=
    (InvImage.wf rank wellFounded_lt).mono fun _ _ h => rank_increases h

/-- A rank is compatible with the DAG if it strictly increases along edges. -/
def RespectsTopologicalRank (G : DAG) (rank : ℕ → ℕ) : Prop :=
  ∀ {u v : ℕ}, G.HasEdge u v → rank u < rank v

end DAG

/-- Directed reachability, including the zero-length path. -/
def Reachable (G : DAG) (u v : ℕ) : Prop :=
  Relation.ReflTransGen (fun a b => G.HasEdge a b) u v

lemma not_transGen_self_of_wellFounded {α : Type} {r : α → α → Prop}
    (h : WellFounded r) (a : α) :
    ¬ Relation.TransGen r a a := by
  induction a using h.induction with
  | h x ih =>
      intro hcycle
      rcases Relation.TransGen.tail'_iff.mp hcycle with ⟨y, hxy, hyx⟩
      rcases Relation.reflTransGen_iff_eq_or_transGen.mp hxy with h_eq | htrans
      · subst y
        exact h.irrefl.irrefl x hyx
      · exact ih y hyx (Relation.TransGen.head hyx htrans)

/-- Incoming neighbors of `v`. -/
def parents (G : DAG) (v : ℕ) : Finset ℕ :=
  (G.edges.filter fun e => e.2 = v).image Prod.fst

/-- Outgoing neighbors of `v`. -/
def children (G : DAG) (v : ℕ) : Finset ℕ :=
  (G.edges.filter fun e => e.1 = v).image Prod.snd

/-- A leaf node is a graph node with no outgoing edges. -/
def IsLeaf (G : DAG) (v : ℕ) : Prop :=
  v ∈ G.nodes ∧ children G v = ∅

/-- Every nonempty finite DAG has at least one leaf node. -/
lemma exists_leaf_of_nonempty (G : DAG) (h_nodes : G.nodes.Nonempty) :
    ∃ v : ℕ, IsLeaf G v := by
  classical
  let Node := {v : ℕ // v ∈ G.nodes}
  letI : Fintype Node := Finset.Subtype.fintype G.nodes
  letI : LE Node := ⟨fun a b => Reachable G a.1 b.1⟩
  letI : IsTrans Node (· ≤ ·) := ⟨by
    intro a b c hab hbc
    exact Relation.ReflTransGen.trans hab hbc⟩
  have h_univ : (Finset.univ : Finset Node).Nonempty := by
    rcases h_nodes with ⟨v, hv⟩
    exact ⟨⟨v, hv⟩, Finset.mem_univ _⟩
  obtain ⟨m, hmax⟩ := (Finset.univ : Finset Node).exists_maximal h_univ
  refine ⟨m.1, m.2, ?_⟩
  apply eq_empty_iff_forall_notMem.mpr
  intro w hw
  rcases Finset.mem_image.mp hw with ⟨e, he_filter, hwe⟩
  have he_edges : e ∈ G.edges := (Finset.mem_filter.mp he_filter).1
  have he_src : e.1 = m.1 := (Finset.mem_filter.mp he_filter).2
  rcases e with ⟨u, z⟩
  simp at he_src hwe
  subst u
  subst w
  have h_edge : G.HasEdge m.1 z := by
    simpa [DAG.HasEdge] using he_edges
  let child : Node := ⟨z, (G.edges_subset h_edge).2⟩
  have h_forward : m ≤ child := Relation.ReflTransGen.single h_edge
  have h_back : child ≤ m := hmax.2 (Finset.mem_univ child) h_forward
  have hcycle : Relation.TransGen (fun a b => G.HasEdge a b) m.1 m.1 :=
    Relation.TransGen.head' h_edge h_back
  exact (not_transGen_self_of_wellFounded G.acyclic m.1) hcycle

/-- Undirected adjacency induced by the directed edge set. -/
def Adjacent (G : DAG) (u v : ℕ) : Prop :=
  G.HasEdge u v ∨ G.HasEdge v u

namespace DAG

lemma ne_of_hasEdge (G : DAG) {u v : ℕ} (h : G.HasEdge u v) : u ≠ v := by
  intro huv
  subst v
  exact (G.acyclic.irrefl.irrefl u) (by simpa [DAG.HasEdge] using h)

lemma not_hasEdge_reverse_of_hasEdge (G : DAG) {u v : ℕ} (h : G.HasEdge u v) :
    ¬ G.HasEdge v u := by
  intro hrev
  have hcycle : Relation.TransGen (fun a b => G.HasEdge a b) u u :=
    Relation.TransGen.head h (Relation.TransGen.single hrev)
  exact (not_transGen_self_of_wellFounded G.acyclic u) hcycle

end DAG

end

end FiniteQuerySandbox
