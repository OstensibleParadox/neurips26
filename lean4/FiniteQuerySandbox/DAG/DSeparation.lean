import FiniteQuerySandbox.DAG.Moralization
import FiniteQuerySandbox.DAG.BayesBall

open Finset

namespace FiniteQuerySandbox

noncomputable section

/-- Nodes retained after moralization and deletion of the conditioning set. -/
def DAG.dSeparationGraphNodes (G : DAG) (X Y Z : Finset ℕ) : Finset ℕ :=
  G.ancestralSubgraphNodes (X ∪ Y ∪ Z) \ Z

/-- Moralized ancestral graph with the conditioning set `Z` removed. -/
def DAG.dSeparationGraph (G : DAG) (X Y Z : Finset ℕ) : SimpleGraph ℕ where
  Adj u v :=
    u ∈ G.dSeparationGraphNodes X Y Z ∧
      v ∈ G.dSeparationGraphNodes X Y Z ∧
      (G.moralGraph (X ∪ Y ∪ Z)).Adj u v
  symm := by
    intro u v h
    exact ⟨h.2.1, h.1, (G.moralGraph (X ∪ Y ∪ Z)).symm h.2.2⟩
  loopless := by
    constructor
    intro u h
    exact (G.moralGraph (X ∪ Y ∪ Z)).loopless.irrefl u h.2.2

/--
d-separation by the ancestral-subgraph/moralization/deletion criterion:
after moralizing ancestors of `X ∪ Y ∪ Z` and deleting `Z`, no `X` node is
connected to any `Y` node.
-/
def DAG.dSeparated (G : DAG) (X Y Z : Finset ℕ) : Prop :=
  ∀ x, x ∈ X → ∀ y, y ∈ Y → ¬(G.dSeparationGraph X Y Z).Reachable x y

/-- `Z` d-separates node set `X` from node set `Y`. -/
def dSeparates (G : DAG) (X Y Z : Finset ℕ) : Prop :=
  ∀ x, x ∈ X → ∀ y, y ∈ Y → ∀ t : Trail G x y, t.isBlocked Z

/-- Standard domain for a d-separation query: `X`, `Y`, and `Z` are pairwise disjoint. -/
def DSeparationQuery (X Y Z : Finset ℕ) : Prop :=
  Disjoint X Y ∧ Disjoint X Z ∧ Disjoint Y Z

/-- `X`, `Y`, and `Z` are pairwise disjoint.
    This is the standard domain for a d-separation query
    (Oxford Graphical Models §8.3, Theorem 8.1). -/
def DisjointSets (X Y Z : Finset ℕ) : Prop :=
  Disjoint X Y ∧ Disjoint X Z ∧ Disjoint Y Z

/-- `DSeparationQuery` and `DisjointSets` are definitionally equivalent. -/
theorem DSeparationQuery_iff_DisjointSets (X Y Z : Finset ℕ) :
    DSeparationQuery X Y Z ↔ DisjointSets X Y Z :=
  Iff.rfl

namespace DAG

lemma mem_dSeparationGraphNodes_of_ancestor_not_mem
    {G : DAG} {X Y Z : Finset ℕ} {v : ℕ}
    (hvA : v ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z))
    (hvZ : v ∉ Z) :
    v ∈ G.dSeparationGraphNodes X Y Z := by
  exact Finset.mem_sdiff.mpr ⟨hvA, hvZ⟩

lemma mem_dSeparationGraphNodes_of_mem_left
    {G : DAG} {X Y Z : Finset ℕ} {v : ℕ}
    (hvX : v ∈ X) (hvG : v ∈ G.nodes) (hvZ : v ∉ Z) :
    v ∈ G.dSeparationGraphNodes X Y Z := by
  exact mem_dSeparationGraphNodes_of_ancestor_not_mem
    (G := G) (X := X) (Y := Y) (Z := Z)
    (DAG.mem_ancestralSubgraphNodes_of_mem
      (G := G) (S := X ∪ Y ∪ Z) (v := v) (by simp [hvX]) hvG)
    hvZ

lemma mem_dSeparationGraphNodes_of_mem_right
    {G : DAG} {X Y Z : Finset ℕ} {v : ℕ}
    (hvY : v ∈ Y) (hvG : v ∈ G.nodes) (hvZ : v ∉ Z) :
    v ∈ G.dSeparationGraphNodes X Y Z := by
  exact mem_dSeparationGraphNodes_of_ancestor_not_mem
    (G := G) (X := X) (Y := Y) (Z := Z)
    (DAG.mem_ancestralSubgraphNodes_of_mem
      (G := G) (S := X ∪ Y ∪ Z) (v := v) (by simp [hvY]) hvG)
    hvZ

lemma not_mem_right_of_disjoint_left {X Z : Finset ℕ} {v : ℕ}
    (hXZ : Disjoint X Z) (hvX : v ∈ X) :
    v ∉ Z := by
  intro hvZ
  exact (Finset.disjoint_left.mp hXZ) hvX hvZ

lemma mem_ancestralSubgraphNodes_of_mem_dSeparationGraphNodes
    {G : DAG} {X Y Z : Finset ℕ} {v : ℕ}
    (hv : v ∈ G.dSeparationGraphNodes X Y Z) :
    v ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
  exact (Finset.mem_sdiff.mp (by simpa [DAG.dSeparationGraphNodes] using hv)).1

end DAG

lemma collider_mem_ancestralSubgraphNodes_of_active {G : DAG} {X Y Z : Finset ℕ}
    {a b c : ℕ}
    (hactive : ¬ TripleBlocked G Z a b c)
    (hcoll : TripleCollider G a b c) :
    b ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
  classical
  have hnotDis :
      ¬ Disjoint ({b} ∪ descendants G b) Z := by
    intro hdis
    exact hactive (Or.inr ⟨hcoll, hdis⟩)
  rw [Finset.disjoint_left] at hnotDis
  push Not at hnotDis
  rcases hnotDis with ⟨z, hz_left, hzZ⟩
  have hbG : b ∈ G.nodes := (G.edges_subset hcoll.1).2
  have hreach : Reachable G b z := by
    rcases Finset.mem_union.mp hz_left with hz_single | hz_desc
    · simp at hz_single
      subst z
      exact Relation.ReflTransGen.refl
    · exact (Finset.mem_filter.mp hz_desc).2.2
  have hzS : z ∈ X ∪ Y ∪ Z := by
    simp [hzZ]
  exact Finset.mem_biUnion.mpr
    ⟨z, hzS, by simp [DAG.ancestors, hbG, hreach]⟩

lemma first_forward_target_mem_ancestral_of_active
    {G : DAG} {X Y Z : Finset ℕ} {u w v : ℕ}
    (h : G.HasEdge u w) (tail : Trail G w v)
    (h_active : ¬ TrailBlocked G Z (u :: tail.toList))
    (hvA : v ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z)) :
    w ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
  induction tail generalizing u with
  | nil w =>
      simpa [Trail.toList] using hvA
  | forward h₂ tail₂ ih =>
      have htail_active :=
        not_trailBlocked_tail_of_not_trailBlocked_cons
          (by simpa [Trail.toList] using h_active)
      have hcA := ih h₂ htail_active hvA
      exact DAG.mem_ancestralSubgraphNodes_of_hasEdge_left h₂ hcA
  | backward h₂ tail₂ =>
      have hhead :=
        not_tripleBlocked_head_of_not_trailBlocked_trail (t := tail₂)
          (by simpa [Trail.toList] using h_active)
      exact collider_mem_ancestralSubgraphNodes_of_active
        (G := G) (X := X) (Y := Y) (Z := Z) hhead ⟨h, h₂⟩

def bayesBallPathCert_of_active_trail_from_prev
    {G : DAG} {X Y Z : Finset ℕ}
    {prev u v : ℕ} {arrival : TrailDir}
    (hprev : TrailDir.edgeIntoCurrent G prev u arrival)
    (t : Trail G u v)
    (h_active : ¬ TrailBlocked G Z (prev :: t.toList))
    (huA : u ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z))
    (hvD : v ∈ G.dSeparationGraphNodes X Y Z) :
    Σ final_dir, {p : BayesBallPath G Z (u, arrival) (v, final_dir) //
      ∀ {q : ℕ × TrailDir}, BayesBallPath.RequiredState p q →
        q.1 ∈ G.dSeparationGraphNodes X Y Z} := by
  induction t generalizing prev arrival with
  | nil v =>
      refine ⟨arrival, ⟨BayesBallPath.nil (v, arrival), ?_⟩⟩
      intro q hreq
      cases hreq
  | forward h tail ih =>
      rename_i u₀ w₀ v₀
      have hhead : ¬ TripleBlocked G Z prev u₀ w₀ :=
        not_tripleBlocked_head_of_not_trailBlocked_trail (t := tail) h_active
      have hstep :
          BayesBallStep G Z (u₀, arrival) (w₀, TrailDir.into) := by
        exact BayesBallStep.of_active_triple hprev
          (by simpa [TrailDir.edgeIntoCurrent] using h) hhead
      have htail_active : ¬ TrailBlocked G Z (u₀ :: tail.toList) :=
        not_trailBlocked_tail_of_not_trailBlocked_cons h_active
      have hvA : v₀ ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        (Finset.mem_sdiff.mp (by
          simpa [DAG.dSeparationGraphNodes] using hvD)).1
      have hwA : w₀ ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        first_forward_target_mem_ancestral_of_active
          (G := G) (X := X) (Y := Y) (Z := Z)
          h tail htail_active hvA
      rcases ih (prev := u₀) (arrival := TrailDir.into)
          (by simpa [TrailDir.edgeIntoCurrent] using h)
          htail_active hwA hvD with
        ⟨final_dir, ⟨ptail, hreq_tail⟩⟩
      refine ⟨final_dir, ⟨BayesBallPath.cons hstep ptail, ?_⟩⟩
      intro q hreq
      cases ptail with
      | nil s =>
          cases hreq with
          | one _ =>
              simpa using hvD
      | cons step₂ rest =>
          cases hreq with
          | colliderTarget hcoll =>
              exact hreq_tail
                (BayesBallPath.required_first_target_of_outOf step₂ rest hcoll.2)
          | colliderRest hcoll hrest =>
              exact hreq_tail
                (BayesBallPath.required_rest_of_outOf step₂ rest hcoll.2 hrest)
          | noncolliderTarget hnot =>
              cases step₂ with
              | step hEdge hopen =>
                  have hwZ : w₀ ∉ Z :=
                    not_mem_Z_of_active_directional_noncollider hopen hnot
                  exact DAG.mem_dSeparationGraphNodes_of_ancestor_not_mem hwA hwZ
          | noncolliderRest _ htailReq =>
              exact hreq_tail htailReq
  | backward h tail ih =>
      rename_i u₀ w₀ v₀
      have hhead : ¬ TripleBlocked G Z prev u₀ w₀ :=
        not_tripleBlocked_head_of_not_trailBlocked_trail (t := tail) h_active
      have hstep :
          BayesBallStep G Z (u₀, arrival) (w₀, TrailDir.outOf) := by
        exact BayesBallStep.of_active_triple hprev
          (by simpa [TrailDir.edgeIntoCurrent] using h) hhead
      have htail_active : ¬ TrailBlocked G Z (u₀ :: tail.toList) :=
        not_trailBlocked_tail_of_not_trailBlocked_cons h_active
      have hwA : w₀ ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        DAG.mem_ancestralSubgraphNodes_of_hasEdge_left h huA
      rcases ih (prev := u₀) (arrival := TrailDir.outOf)
          (by simpa [TrailDir.edgeIntoCurrent] using h)
          htail_active hwA hvD with
        ⟨final_dir, ⟨ptail, hreq_tail⟩⟩
      refine ⟨final_dir, ⟨BayesBallPath.cons hstep ptail, ?_⟩⟩
      intro q hreq
      cases ptail with
      | nil s =>
          cases hreq with
          | one _ =>
              simpa using hvD
      | cons step₂ rest =>
          cases hreq with
          | colliderTarget hcoll =>
              cases hcoll.1
          | colliderRest hcoll _ =>
              cases hcoll.1
          | noncolliderTarget hnot =>
              cases step₂ with
              | step hEdge hopen =>
                  have hwZ : w₀ ∉ Z :=
                    not_mem_Z_of_active_directional_noncollider hopen hnot
                  exact DAG.mem_dSeparationGraphNodes_of_ancestor_not_mem hwA hwZ
          | noncolliderRest _ htailReq =>
              exact hreq_tail htailReq

def bayesBallPathCert_of_active_trail_outOf
    {G : DAG} {X Y Z : Finset ℕ} {u v : ℕ}
    (t : Trail G u v)
    (h_active : ¬ t.isBlocked Z)
    (huZ : u ∉ Z)
    (huA : u ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z))
    (hvD : v ∈ G.dSeparationGraphNodes X Y Z) :
    Σ final_dir, {p : BayesBallPath G Z (u, TrailDir.outOf) (v, final_dir) //
      ∀ {q : ℕ × TrailDir}, BayesBallPath.RequiredState p q →
        q.1 ∈ G.dSeparationGraphNodes X Y Z} := by
  cases t with
  | nil v =>
      refine ⟨TrailDir.outOf, ⟨BayesBallPath.nil (u, TrailDir.outOf), ?_⟩⟩
      intro q hreq
      cases hreq
  | forward h tail =>
      rename_i w₀
      have hstep :
          BayesBallStep G Z (u, TrailDir.outOf) (w₀, TrailDir.into) :=
        BayesBallStep.step (by simpa [TrailDir.edgeIntoCurrent] using h)
          (by
            simpa [Trail.StartOpen] using
              (Trail.startOpen_outOf_of_not_mem (G := G) (Z := Z)
                (u := u) (v := v)
                (t := Trail.forward h tail) huZ))
      have htail_active : ¬ TrailBlocked G Z (u :: tail.toList) := by
        simpa [Trail.isBlocked, Trail.toList] using h_active
      have hvA : v ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        (Finset.mem_sdiff.mp (by
          simpa [DAG.dSeparationGraphNodes] using hvD)).1
      have hwA : w₀ ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        first_forward_target_mem_ancestral_of_active
          (G := G) (X := X) (Y := Y) (Z := Z)
          h tail htail_active hvA
      rcases bayesBallPathCert_of_active_trail_from_prev
          (G := G) (X := X) (Y := Y) (Z := Z)
          (prev := u) (u := w₀) (v := v) (arrival := TrailDir.into)
          (by simpa [TrailDir.edgeIntoCurrent] using h)
          tail htail_active hwA hvD with
        ⟨final_dir, ⟨ptail, hreq_tail⟩⟩
      refine ⟨final_dir, ⟨BayesBallPath.cons hstep ptail, ?_⟩⟩
      intro q hreq
      cases ptail with
      | nil s =>
          cases hreq with
          | one _ =>
              simpa using hvD
      | cons step₂ rest =>
          cases hreq with
          | colliderTarget hcoll =>
              exact hreq_tail
                (BayesBallPath.required_first_target_of_outOf step₂ rest hcoll.2)
          | colliderRest hcoll hrest =>
              exact hreq_tail
                (BayesBallPath.required_rest_of_outOf step₂ rest hcoll.2 hrest)
          | noncolliderTarget hnot =>
              cases step₂ with
              | step hEdge hopen =>
                  have hwZ : w₀ ∉ Z :=
                    not_mem_Z_of_active_directional_noncollider hopen hnot
                  exact DAG.mem_dSeparationGraphNodes_of_ancestor_not_mem hwA hwZ
          | noncolliderRest _ htailReq =>
              exact hreq_tail htailReq
  | backward h tail =>
      rename_i w₀
      have hstep :
          BayesBallStep G Z (u, TrailDir.outOf) (w₀, TrailDir.outOf) :=
        BayesBallStep.step (by simpa [TrailDir.edgeIntoCurrent] using h)
          (by
            simpa [Trail.StartOpen] using
              (Trail.startOpen_outOf_of_not_mem (G := G) (Z := Z)
                (u := u) (v := v)
                (t := Trail.backward h tail) huZ))
      have htail_active : ¬ TrailBlocked G Z (u :: tail.toList) := by
        simpa [Trail.isBlocked, Trail.toList] using h_active
      have hwA : w₀ ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        DAG.mem_ancestralSubgraphNodes_of_hasEdge_left h huA
      rcases bayesBallPathCert_of_active_trail_from_prev
          (G := G) (X := X) (Y := Y) (Z := Z)
          (prev := u) (u := w₀) (v := v) (arrival := TrailDir.outOf)
          (by simpa [TrailDir.edgeIntoCurrent] using h)
          tail htail_active hwA hvD with
        ⟨final_dir, ⟨ptail, hreq_tail⟩⟩
      refine ⟨final_dir, ⟨BayesBallPath.cons hstep ptail, ?_⟩⟩
      intro q hreq
      cases ptail with
      | nil s =>
          cases hreq with
          | one _ =>
              simpa using hvD
      | cons step₂ rest =>
          cases hreq with
          | colliderTarget hcoll =>
              cases hcoll.1
          | colliderRest hcoll _ =>
              cases hcoll.1
          | noncolliderTarget hnot =>
              cases step₂ with
              | step hEdge hopen =>
                  have hwZ : w₀ ∉ Z :=
                    not_mem_Z_of_active_directional_noncollider hopen hnot
                  exact DAG.mem_dSeparationGraphNodes_of_ancestor_not_mem hwA hwZ
          | noncolliderRest _ htailReq =>
              exact hreq_tail htailReq

/--
Reachability in the moralized ancestral graph, packaged as explicit "large
steps": either a direct underlying DAG edge survives deletion of `Z`, or two
co-parents are connected by the moralization jump.
-/
inductive MAGWalk (G : DAG) (X Y Z : Finset ℕ) : ℕ → ℕ → Prop where
  | refl (u : ℕ) : MAGWalk G X Y Z u u
  | single {u v : ℕ}
      (hEdge : G.HasEdge u v ∨ G.HasEdge v u)
      (hu : u ∈ G.dSeparationGraphNodes X Y Z)
      (hv : v ∈ G.dSeparationGraphNodes X Y Z) :
      MAGWalk G X Y Z u v
  | jump {u v w : ℕ}
      (huw : G.HasEdge u w)
      (hvw : G.HasEdge v w)
      (hne : u ≠ v)
      (hu : u ∈ G.dSeparationGraphNodes X Y Z)
      (hv : v ∈ G.dSeparationGraphNodes X Y Z)
      (hw : w ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z)) :
      MAGWalk G X Y Z u v
  | trans {u v w : ℕ}
      (huv : MAGWalk G X Y Z u v)
      (hvw : MAGWalk G X Y Z v w) :
      MAGWalk G X Y Z u w

lemma dSeparationGraph_adj_of_mag_single {G : DAG} {X Y Z : Finset ℕ} {u v : ℕ}
    (hEdge : G.HasEdge u v ∨ G.HasEdge v u)
    (hu : u ∈ G.dSeparationGraphNodes X Y Z)
    (hv : v ∈ G.dSeparationGraphNodes X Y Z) :
    (G.dSeparationGraph X Y Z).Adj u v := by
  let S := X ∪ (Y ∪ Z)
  have huA : u ∈ G.ancestralSubgraphNodes S := by
    simpa [S] using DAG.mem_ancestralSubgraphNodes_of_mem_dSeparationGraphNodes (G := G) (X := X)
      (Y := Y) (Z := Z) hu
  have hvA : v ∈ G.ancestralSubgraphNodes S := by
    simpa [S] using DAG.mem_ancestralSubgraphNodes_of_mem_dSeparationGraphNodes (G := G) (X := X)
      (Y := Y) (Z := Z) hv
  have hne : u ≠ v := by
    rcases hEdge with huv | hvu
    · exact G.ne_of_hasEdge huv
    · exact Ne.symm (G.ne_of_hasEdge hvu)
  have huA0 : u ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
    simpa [S, Finset.union_assoc] using huA
  have hvA0 : v ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
    simpa [S, Finset.union_assoc] using hvA
  refine ⟨hu, hv, ?_⟩
  dsimp [DAG.moralGraph]
  refine ⟨huA0, hvA0, hne, ?_⟩
  rcases hEdge with huv | hvu
  · left
    exact Finset.mem_filter.mpr ⟨by simpa [DAG.HasEdge] using huv, huA0, hvA0⟩
  · right
    left
    exact Finset.mem_filter.mpr ⟨by simpa [DAG.HasEdge] using hvu, hvA0, huA0⟩

lemma dSeparationGraph_adj_of_mag_jump {G : DAG} {X Y Z : Finset ℕ} {u v w : ℕ}
    (huw : G.HasEdge u w)
    (hvw : G.HasEdge v w)
    (hne : u ≠ v)
    (hu : u ∈ G.dSeparationGraphNodes X Y Z)
    (hv : v ∈ G.dSeparationGraphNodes X Y Z)
    (hw : w ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z)) :
    (G.dSeparationGraph X Y Z).Adj u v := by
  let S := X ∪ (Y ∪ Z)
  have huA : u ∈ G.ancestralSubgraphNodes S := by
    simpa [S] using DAG.mem_ancestralSubgraphNodes_of_mem_dSeparationGraphNodes (G := G) (X := X)
      (Y := Y) (Z := Z) hu
  have hvA : v ∈ G.ancestralSubgraphNodes S := by
    simpa [S] using DAG.mem_ancestralSubgraphNodes_of_mem_dSeparationGraphNodes (G := G) (X := X)
      (Y := Y) (Z := Z) hv
  have hwA : w ∈ G.ancestralSubgraphNodes S := by
    simpa [S] using hw
  have huA0 : u ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
    simpa [S, Finset.union_assoc] using huA
  have hvA0 : v ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
    simpa [S, Finset.union_assoc] using hvA
  have hwA0 : w ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) := by
    simpa [S, Finset.union_assoc] using hwA
  refine ⟨hu, hv, ?_⟩
  dsimp [DAG.moralGraph]
  refine ⟨huA0, hvA0, hne, Or.inr (Or.inr ?_)⟩
  refine ⟨w, ?_, ?_, hne⟩
  · exact Finset.mem_filter.mpr ⟨by simpa [DAG.HasEdge] using huw, huA0, hwA0⟩
  · exact Finset.mem_filter.mpr ⟨by simpa [DAG.HasEdge] using hvw, hvA0, hwA0⟩

theorem MAGWalk.to_dSeparationGraph_reachable {G : DAG} {X Y Z : Finset ℕ} {u v : ℕ}
    (h : MAGWalk G X Y Z u v) :
    (G.dSeparationGraph X Y Z).Reachable u v := by
  induction h with
  | refl u =>
      exact SimpleGraph.Reachable.refl u
  | single hEdge hu hv =>
      exact SimpleGraph.Adj.reachable (dSeparationGraph_adj_of_mag_single hEdge hu hv)
  | jump huw hvw hne hu hv hw =>
      exact SimpleGraph.Adj.reachable (dSeparationGraph_adj_of_mag_jump huw hvw hne hu hv hw)
  | trans _ _ ihuv ihvw =>
      exact SimpleGraph.Reachable.trans ihuv ihvw

lemma mag_single_or_jump_of_dSeparationGraph_adj {G : DAG} {X Y Z : Finset ℕ} {u v : ℕ}
    (h : (G.dSeparationGraph X Y Z).Adj u v) :
    MAGWalk G X Y Z u v := by
  let S := X ∪ (Y ∪ Z)
  rcases h with ⟨hu, hv, hmoral⟩
  dsimp [DAG.moralGraph] at hmoral
  rcases hmoral with ⟨_, _, hne, hdir | hrev | hcop⟩
  · have hmem :
        (u, v) ∈ G.edges.filter (fun e =>
          e.1 ∈ G.ancestralSubgraphNodes S ∧ e.2 ∈ G.ancestralSubgraphNodes S) := by
        simpa [DAG.ancestralSubgraph, DAG.HasEdge, S] using hdir
    exact MAGWalk.single (G := G) (X := X) (Y := Y) (Z := Z)
      (Or.inl (by simpa [DAG.HasEdge] using (Finset.mem_filter.mp hmem).1)) hu hv
  · have hmem :
        (v, u) ∈ G.edges.filter (fun e =>
          e.1 ∈ G.ancestralSubgraphNodes S ∧ e.2 ∈ G.ancestralSubgraphNodes S) := by
        simpa [DAG.ancestralSubgraph, DAG.HasEdge, S] using hrev
    exact MAGWalk.single (G := G) (X := X) (Y := Y) (Z := Z)
      (Or.inr (by simpa [DAG.HasEdge] using (Finset.mem_filter.mp hmem).1)) hu hv
  · rcases hcop with ⟨w, huw', hvw', huw_ne_v⟩
    have huw_mem :
        (u, w) ∈ G.edges.filter (fun e =>
          e.1 ∈ G.ancestralSubgraphNodes S ∧ e.2 ∈ G.ancestralSubgraphNodes S) := by
        simpa [DAG.ancestralSubgraph, DAG.HasEdge, S] using huw'
    have hvw_mem :
        (v, w) ∈ G.edges.filter (fun e =>
          e.1 ∈ G.ancestralSubgraphNodes S ∧ e.2 ∈ G.ancestralSubgraphNodes S) := by
        simpa [DAG.ancestralSubgraph, DAG.HasEdge, S] using hvw'
    exact MAGWalk.jump (G := G) (X := X) (Y := Y) (Z := Z)
      (by simpa [DAG.HasEdge] using (Finset.mem_filter.mp huw_mem).1)
      (by simpa [DAG.HasEdge] using (Finset.mem_filter.mp hvw_mem).1)
      huw_ne_v hu hv (by
        simpa [S] using (Finset.mem_filter.mp huw_mem).2.2)

theorem MAGWalk.of_dSeparationGraph_reachable {G : DAG} {X Y Z : Finset ℕ} {u v : ℕ}
    (h : (G.dSeparationGraph X Y Z).Reachable u v) :
    MAGWalk G X Y Z u v := by
  rcases h with ⟨p⟩
  induction p with
  | nil =>
      exact MAGWalk.refl _
  | cons hAdj _ ih =>
      exact MAGWalk.trans (mag_single_or_jump_of_dSeparationGraph_adj hAdj) ih

theorem magWalk_iff_dSeparationGraph_reachable {G : DAG} {X Y Z : Finset ℕ} {u v : ℕ} :
    MAGWalk G X Y Z u v ↔ (G.dSeparationGraph X Y Z).Reachable u v :=
  ⟨MAGWalk.to_dSeparationGraph_reachable, MAGWalk.of_dSeparationGraph_reachable⟩

lemma MAGWalk.jump_of_active_collider {G : DAG} {X Y Z : Finset ℕ} {u x w : ℕ}
    (hux : G.HasEdge u x)
    (hwx : G.HasEdge w x)
    (hactive : ¬ TripleBlocked G Z u x w)
    (hu : u ∈ G.dSeparationGraphNodes X Y Z)
    (hw : w ∈ G.dSeparationGraphNodes X Y Z) :
    MAGWalk G X Y Z u w := by
  by_cases huw : u = w
  · subst w
    exact MAGWalk.refl u
  · exact MAGWalk.jump hux hwx huw hu hw
      (collider_mem_ancestralSubgraphNodes_of_active hactive ⟨hux, hwx⟩)

lemma MAGWalk.single_of_bayesBallStep {G : DAG} {X Y Z : Finset ℕ}
    {u v : ℕ} {arrival departure : TrailDir}
    (hstep : BayesBallStep G Z (u, arrival) (v, departure))
    (hu : u ∈ G.dSeparationGraphNodes X Y Z)
    (hv : v ∈ G.dSeparationGraphNodes X Y Z) :
    MAGWalk G X Y Z u v := by
  cases hstep with
  | step hEdge _ =>
      cases departure
      · exact MAGWalk.single
          (Or.inl (by simpa [TrailDir.edgeIntoCurrent] using hEdge)) hu hv
      · exact MAGWalk.single
          (Or.inr (by simpa [TrailDir.edgeIntoCurrent] using hEdge)) hu hv

lemma MAGWalk.jump_of_bayesBall_collider {G : DAG} {X Y Z : Finset ℕ}
    {a b c : ℕ} {arrival : TrailDir}
    (hInto : BayesBallStep G Z (a, arrival) (b, TrailDir.into))
    (hOut : BayesBallStep G Z (b, TrailDir.into) (c, TrailDir.outOf))
    (ha : a ∈ G.dSeparationGraphNodes X Y Z)
    (hc : c ∈ G.dSeparationGraphNodes X Y Z) :
    MAGWalk G X Y Z a c := by
  cases hInto with
  | step hIntoEdge _ =>
      cases hOut with
      | step hOutEdge hOutOpen =>
          have hactive : ¬ TripleBlocked G Z a b c := by
            intro hblocked
            exact hOutOpen
              ((directionalTripleBlocked_iff_tripleBlocked hIntoEdge hOutEdge).mpr hblocked)
          have hcoll : TripleCollider G a b c := by
            exact ⟨by simpa [TrailDir.edgeIntoCurrent] using hIntoEdge,
              by simpa [TrailDir.edgeIntoCurrent] using hOutEdge⟩
          have hb : b ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
            collider_mem_ancestralSubgraphNodes_of_active hactive hcoll
          by_cases hac : a = c
          · subst c
            exact MAGWalk.refl a
          · exact MAGWalk.jump
              (by simpa [TrailDir.edgeIntoCurrent] using hIntoEdge)
              (by simpa [TrailDir.edgeIntoCurrent] using hOutEdge)
              hac ha hc hb

lemma MAGWalk.trans_jump_of_bayesBall_collider {G : DAG} {X Y Z : Finset ℕ}
    {r a b c : ℕ} {arrival : TrailDir}
    (hprefix : MAGWalk G X Y Z r a)
    (hInto : BayesBallStep G Z (a, arrival) (b, TrailDir.into))
    (hOut : BayesBallStep G Z (b, TrailDir.into) (c, TrailDir.outOf))
    (ha : a ∈ G.dSeparationGraphNodes X Y Z)
    (hc : c ∈ G.dSeparationGraphNodes X Y Z) :
    MAGWalk G X Y Z r c :=
  MAGWalk.trans hprefix
    (MAGWalk.jump_of_bayesBall_collider hInto hOut ha hc)

namespace BayesBallPath

/--
Compress an explicit Bayes-ball path to a `MAGWalk`, scanning with a two-step
window.  Non-collider windows consume one step as a `MAGWalk.single`; collider
windows of the form `(a, _) → (b, into) → (c, outOf)` consume two steps as one
`MAGWalk.jump`, so the skipped collider `b` need not be present in
`dSeparationGraphNodes`.
-/
def compressWithFuel {G : DAG} {X Y Z : Finset ℕ} :
    (fuel : ℕ) →
    {s t : ℕ × TrailDir} →
    (p : BayesBallPath G Z s t) →
    p.length ≤ fuel →
    s.1 ∈ G.dSeparationGraphNodes X Y Z →
    t.1 ∈ G.dSeparationGraphNodes X Y Z →
    (∀ {q : ℕ × TrailDir}, RequiredState p q →
      q.1 ∈ G.dSeparationGraphNodes X Y Z) →
    MAGWalk G X Y Z s.1 t.1
  | 0, s, _, nil _, _, hs, _, _ =>
      MAGWalk.refl s.1
  | 0, _, _, cons step rest, hfuel, _, _, _ => by
      simp [BayesBallPath.length] at hfuel
  | _ + 1, s, _, nil _, _, hs, _, _ =>
      MAGWalk.refl s.1
  | _ + 1, _, _, cons step (nil _), _, hs, ht, _ =>
      MAGWalk.single_of_bayesBallStep step hs ht
  | fuel + 1, _, _, cons (s := start) (t := mid) step₁
      (cons (s := _) (t := next) step₂ rest), hfuel, hs, ht, hreq => by
      rcases start with ⟨a, arrA⟩
      rcases mid with ⟨b, arrB⟩
      rcases next with ⟨c, arrC⟩
      by_cases hcoll : arrB = TrailDir.into ∧ arrC = TrailDir.outOf
      · have hc : c ∈ G.dSeparationGraphNodes X Y Z :=
          hreq (q := (c, arrC))
            (RequiredState.colliderTarget
              (G := G) (Z := Z) (s := (a, arrA)) (mid := (b, arrB))
              (next := (c, arrC)) (step₁ := step₁) (step₂ := step₂)
              (rest := rest) hcoll)
        rcases hcoll with ⟨harrB, harrC⟩
        subst arrB
        subst arrC
        have hreq_rest :
            ∀ {q : ℕ × TrailDir}, RequiredState rest q →
              q.1 ∈ G.dSeparationGraphNodes X Y Z := by
          intro q hq
          exact hreq (q := q)
            (RequiredState.colliderRest
              (G := G) (Z := Z) (s := (a, arrA))
              (mid := (b, TrailDir.into)) (next := (c, TrailDir.outOf))
              (step₁ := step₁) (step₂ := step₂) (rest := rest)
              ⟨rfl, rfl⟩ hq)
        have hfuel_rest : rest.length ≤ fuel := by
          simp [BayesBallPath.length] at hfuel ⊢
          omega
        exact MAGWalk.trans
          (MAGWalk.jump_of_bayesBall_collider
            (G := G) (X := X) (Y := Y) (Z := Z)
            (a := a) (b := b) (c := c) (arrival := arrA)
            step₁ step₂ hs hc)
          (compressWithFuel fuel rest hfuel_rest hc ht hreq_rest)
      · have hb : b ∈ G.dSeparationGraphNodes X Y Z :=
          hreq (q := (b, arrB))
            (RequiredState.noncolliderTarget
              (G := G) (Z := Z) (s := (a, arrA)) (mid := (b, arrB))
              (next := (c, arrC)) (step₁ := step₁) (step₂ := step₂)
              (rest := rest) hcoll)
        have hreq_tail :
            ∀ {q : ℕ × TrailDir}, RequiredState (cons step₂ rest) q →
              q.1 ∈ G.dSeparationGraphNodes X Y Z := by
          intro q hq
          exact hreq (q := q)
            (RequiredState.noncolliderRest
              (G := G) (Z := Z) (s := (a, arrA)) (mid := (b, arrB))
              (next := (c, arrC)) (step₁ := step₁) (step₂ := step₂)
              (rest := rest) hcoll hq)
        have hfuel_tail : (cons step₂ rest).length ≤ fuel := by
          simp [BayesBallPath.length] at hfuel ⊢
          omega
        exact MAGWalk.trans
          (MAGWalk.single_of_bayesBallStep
            (G := G) (X := X) (Y := Y) (Z := Z)
            (u := a) (v := b) (arrival := arrA) (departure := arrB)
            step₁ hs hb)
          (compressWithFuel fuel (cons step₂ rest) hfuel_tail hb ht hreq_tail)

/-- Fuel-free wrapper for the compressed Bayes-ball path scanner. -/
def compress {G : DAG} {X Y Z : Finset ℕ} {s t : ℕ × TrailDir}
    (p : BayesBallPath G Z s t)
    (hs : s.1 ∈ G.dSeparationGraphNodes X Y Z)
    (ht : t.1 ∈ G.dSeparationGraphNodes X Y Z)
    (hreq : ∀ {q : ℕ × TrailDir}, RequiredState p q →
      q.1 ∈ G.dSeparationGraphNodes X Y Z) :
    MAGWalk G X Y Z s.1 t.1 :=
  compressWithFuel p.length p le_rfl hs ht hreq

end BayesBallPath

lemma magWalk_of_bayesBall_pair {G : DAG} {X Y Z : Finset ℕ}
    {s t : ℕ × TrailDir}
    (h_bb : BayesBallReachable G Z s t)
    (hmem : ∀ {n : ℕ} {d : TrailDir},
      BayesBallReachable G Z s (n, d) →
        n ∈ G.dSeparationGraphNodes X Y Z) :
    MAGWalk G X Y Z s.1 t.1 := by
  induction h_bb with
  | refl =>
      exact MAGWalk.refl s.1
  | tail hreach hstep ih =>
      rename_i current target
      rcases current with ⟨n, arrival⟩
      rcases target with ⟨w, departure⟩
      cases hstep with
      | step hEdge hopen =>
          have hn : n ∈ G.dSeparationGraphNodes X Y Z := hmem hreach
          have hnext :
              BayesBallReachable G Z s (w, departure) :=
            hreach.trans (Relation.ReflTransGen.single
              (BayesBallStep.step (G := G) (Z := Z) hEdge hopen))
          have hw : w ∈ G.dSeparationGraphNodes X Y Z := hmem hnext
          exact MAGWalk.trans ih
            (MAGWalk.single_of_bayesBallStep
              (G := G) (X := X) (Y := Y) (Z := Z)
              (u := n) (v := w) (arrival := arrival) (departure := departure)
              (BayesBallStep.step hEdge hopen) hn hw)

lemma magWalk_of_bayesBall {G : DAG} {X Y Z : Finset ℕ}
    {u v : ℕ} {d₁ d₂ : TrailDir}
    (h_bb : BayesBallReachable G Z (u, d₁) (v, d₂))
    (hmem : ∀ {n : ℕ} {d : TrailDir},
      BayesBallReachable G Z (u, d₁) (n, d) →
        n ∈ G.dSeparationGraphNodes X Y Z) :
    MAGWalk G X Y Z u v :=
  magWalk_of_bayesBall_pair h_bb hmem

theorem dSeparationGraph_reachable_of_active_trail_disjoint
    {G : DAG} {X Y Z : Finset ℕ} {x y : ℕ}
    (hXZ : Disjoint X Z) (hYZ : Disjoint Y Z)
    (hxX : x ∈ X) (hyY : y ∈ Y)
    (t : Trail G x y) (h_active : ¬ t.isBlocked Z) :
    (G.dSeparationGraph X Y Z).Reachable x y := by
  have hxZ : x ∉ Z := DAG.not_mem_right_of_disjoint_left hXZ hxX
  have hyZ : y ∉ Z := DAG.not_mem_right_of_disjoint_left hYZ hyY
  cases t with
  | nil x =>
      exact SimpleGraph.Reachable.refl x
  | forward h tail =>
      rename_i w
      have hxG : x ∈ G.nodes := (G.edges_subset h).1
      have hyG : y ∈ G.nodes :=
        Trail.target_mem_graph_nodes_of_source_mem
          (Trail.forward (G := G) (u := x) (w := w) (v := y) h tail) hxG
      have hxD : x ∈ G.dSeparationGraphNodes X Y Z :=
        DAG.mem_dSeparationGraphNodes_of_mem_left hxX hxG hxZ
      have hyD : y ∈ G.dSeparationGraphNodes X Y Z :=
        DAG.mem_dSeparationGraphNodes_of_mem_right hyY hyG hyZ
      have hxA : x ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        DAG.mem_ancestralSubgraphNodes_of_mem_dSeparationGraphNodes hxD
      rcases bayesBallPathCert_of_active_trail_outOf
          (G := G) (X := X) (Y := Y) (Z := Z)
          (u := x) (v := y)
          (Trail.forward (G := G) (u := x) (w := w) (v := y) h tail)
          h_active hxZ hxA hyD with
        ⟨final_dir, ⟨p, hreq⟩⟩
      exact MAGWalk.to_dSeparationGraph_reachable
        (BayesBallPath.compress
          (G := G) (X := X) (Y := Y) (Z := Z)
          (s := (x, TrailDir.outOf)) (t := (y, final_dir))
          p hxD hyD hreq)
  | backward h tail =>
      rename_i w
      have hxG : x ∈ G.nodes := (G.edges_subset h).2
      have hyG : y ∈ G.nodes :=
        Trail.target_mem_graph_nodes_of_source_mem
          (Trail.backward (G := G) (u := x) (w := w) (v := y) h tail) hxG
      have hxD : x ∈ G.dSeparationGraphNodes X Y Z :=
        DAG.mem_dSeparationGraphNodes_of_mem_left hxX hxG hxZ
      have hyD : y ∈ G.dSeparationGraphNodes X Y Z :=
        DAG.mem_dSeparationGraphNodes_of_mem_right hyY hyG hyZ
      have hxA : x ∈ G.ancestralSubgraphNodes (X ∪ Y ∪ Z) :=
        DAG.mem_ancestralSubgraphNodes_of_mem_dSeparationGraphNodes hxD
      rcases bayesBallPathCert_of_active_trail_outOf
          (G := G) (X := X) (Y := Y) (Z := Z)
          (u := x) (v := y)
          (Trail.backward (G := G) (u := x) (w := w) (v := y) h tail)
          h_active hxZ hxA hyD with
        ⟨final_dir, ⟨p, hreq⟩⟩
      exact MAGWalk.to_dSeparationGraph_reachable
        (BayesBallPath.compress
          (G := G) (X := X) (Y := Y) (Z := Z)
          (s := (x, TrailDir.outOf)) (t := (y, final_dir))
          p hxD hyD hreq)

theorem dsep_complete_of_endpoint_disjoint
    {G : DAG} {X Y Z : Finset ℕ}
    (hXZ : Disjoint X Z) (hYZ : Disjoint Y Z) :
    DAG.dSeparated G X Y Z → dSeparates G X Y Z := by
  intro hdsep x hxX y hyY t
  by_contra h_active
  exact hdsep x hxX y hyY
    (dSeparationGraph_reachable_of_active_trail_disjoint
      (G := G) (X := X) (Y := Y) (Z := Z)
      hXZ hYZ hxX hyY t h_active)

theorem dsep_complete_of_query
    {G : DAG} {X Y Z : Finset ℕ}
    (hquery : DSeparationQuery X Y Z) :
    DAG.dSeparated G X Y Z → dSeparates G X Y Z :=
  dsep_complete_of_endpoint_disjoint hquery.2.1 hquery.2.2

/-- **Soundness of d-separation under pairwise-disjoint domain.**
    If `X`, `Y`, `Z` are pairwise disjoint (`DisjointSets X Y Z`) and the
    moralized ancestral graph separates `X` from `Y` after deleting `Z`
    (`DAG.dSeparated G X Y Z`), then every trail from `X` to `Y` is blocked
    by `Z` (`dSeparates G X Y Z`).
-/
theorem dSeparated_of_dSeparated_disjoint
    {G : DAG} {X Y Z : Finset ℕ}
    (hXYZ : DisjointSets X Y Z)
    (hsep : DAG.dSeparated G X Y Z) : dSeparates G X Y Z := by
  exact dsep_complete_of_endpoint_disjoint hXYZ.2.1 hXYZ.2.2 hsep

/-! ## Small checkable examples -/

namespace DAGExamples

/-- The chain `0 → 1 → 2`. -/
def chain3 : DAG :=
  DAG.ofRank ({0, 1, 2} : Finset ℕ) ({(0, 1), (1, 2)} : Finset (ℕ × ℕ)) id
    (by
      intro u v h
      simp at h
      rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> simp)
    (by
      intro u v h
      simp at h
      rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> simp)

/-- The fork `1 → 0` and `1 → 2`. -/
def fork3 : DAG :=
  DAG.ofRank ({0, 1, 2} : Finset ℕ) ({(1, 0), (1, 2)} : Finset (ℕ × ℕ))
    (fun n => if n = 1 then 0 else 1)
    (by
      intro u v h
      simp at h
      rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> simp)
    (by
      intro u v h
      simp at h
      rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> simp)

/-- The collider `0 → 1 ← 2`. -/
def collider3 : DAG :=
  DAG.ofRank ({0, 1, 2} : Finset ℕ) ({(0, 1), (2, 1)} : Finset (ℕ × ℕ))
    (fun n => if n = 1 then 1 else 0)
    (by
      intro u v h
      simp at h
      rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> simp)
    (by
      intro u v h
      simp at h
      rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> simp)

example : parents chain3 1 = {0} := by
  decide

example : children chain3 1 = {2} := by
  decide

example : (chain3.deleteLeaf 2).nodes = ({0, 1} : Finset ℕ) := by
  decide

example : (chain3.deleteLeaf 2).edges = ({(0, 1)} : Finset (ℕ × ℕ)) := by
  decide

example : (chain3.deleteLeaf 2).nodes.card < chain3.nodes.card :=
  DAG.deleteLeaf_card_lt (G := chain3) (v := 2) (by decide)

def chainTrail02 : Trail chain3 0 2 :=
  Trail.forward (u := 0) (w := 1) (v := 2)
    (by
      change (0, 1) ∈ ({(0, 1), (1, 2)} : Finset (ℕ × ℕ))
      simp)
    (Trail.forward (u := 1) (w := 2) (v := 2)
      (by
        change (1, 2) ∈ ({(0, 1), (1, 2)} : Finset (ℕ × ℕ))
        simp)
      (Trail.nil 2))

example : chainTrail02.isBlocked ({1} : Finset ℕ) := by
  unfold Trail.isBlocked TrailBlocked TripleBlocked TripleCollider HasTriple
  refine ⟨0, 1, 2, ?_, ?_⟩
  · refine ⟨[], [], ?_⟩
    simp [chainTrail02, Trail.toList]
  · left
    constructor
    · change ¬
        ((0, 1) ∈ ({(0, 1), (1, 2)} : Finset (ℕ × ℕ)) ∧
          (2, 1) ∈ ({(0, 1), (1, 2)} : Finset (ℕ × ℕ)))
      simp
    · simp

def colliderTrail02 : Trail collider3 0 2 :=
  Trail.forward (u := 0) (w := 1) (v := 2)
    (by
      change (0, 1) ∈ ({(0, 1), (2, 1)} : Finset (ℕ × ℕ))
      simp)
    (Trail.backward (u := 1) (w := 2) (v := 2)
      (by
        change (2, 1) ∈ ({(0, 1), (2, 1)} : Finset (ℕ × ℕ))
        simp)
      (Trail.nil 2))

example : colliderTrail02.isBlocked (∅ : Finset ℕ) := by
  unfold Trail.isBlocked TrailBlocked TripleBlocked TripleCollider HasTriple
  refine ⟨0, 1, 2, ?_, ?_⟩
  · refine ⟨[], [], ?_⟩
    simp [colliderTrail02, Trail.toList]
  · right
    constructor
    · change
        (0, 1) ∈ ({(0, 1), (2, 1)} : Finset (ℕ × ℕ)) ∧
          (2, 1) ∈ ({(0, 1), (2, 1)} : Finset (ℕ × ℕ))
      simp
    · simp

end DAGExamples

/--
The unrestricted statement `DAG.dSeparated G X Y Z → dSeparates G X Y Z` is
false for the current public definitions.
-/
theorem dsep_complete_endpoint_in_Z_counterexample :
    ∃ (G : DAG) (X Y Z : Finset ℕ),
      DAG.dSeparated G X Y Z ∧ ¬ dSeparates G X Y Z := by
  classical
  refine ⟨DAGExamples.chain3, ({0} : Finset ℕ), ({1} : Finset ℕ), ({0} : Finset ℕ),
    ?_, ?_⟩
  · intro x hx y hy hreach
    simp only [Finset.mem_singleton] at hx hy
    subst x
    subst y
    rcases hreach with ⟨p⟩
    cases p with
    | cons h _ =>
        have h0_not_mem :
            0 ∉ DAGExamples.chain3.dSeparationGraphNodes ({0} : Finset ℕ)
              ({1} : Finset ℕ) ({0} : Finset ℕ) := by
          simp [DAG.dSeparationGraphNodes]
        exact h0_not_mem h.1
  · intro hsep
    have hblocked :
        (Trail.forward (G := DAGExamples.chain3) (u := 0) (w := 1) (v := 1)
          (by
            change (0, 1) ∈ ({(0, 1), (1, 2)} : Finset (ℕ × ℕ))
            simp)
          (Trail.nil 1)).isBlocked ({0} : Finset ℕ) :=
      hsep 0 (by simp) 1 (by simp)
        (Trail.forward (G := DAGExamples.chain3) (u := 0) (w := 1) (v := 1)
          (by
            change (0, 1) ∈ ({(0, 1), (1, 2)} : Finset (ℕ × ℕ))
            simp)
          (Trail.nil 1))
    rcases hblocked with ⟨a, b, c, htriple, _⟩
    rcases htriple with ⟨pre, post, hlist⟩
    have hlen := congrArg List.length hlist
    simp [Trail.toList] at hlen
    omega

theorem not_forall_dsep_complete :
    ¬ ∀ (G : DAG) (X Y Z : Finset ℕ), DAG.dSeparated G X Y Z → dSeparates G X Y Z := by
  intro h
  rcases dsep_complete_endpoint_in_Z_counterexample with ⟨G, X, Y, Z, hdsep, hnot⟩
  exact hnot (h G X Y Z hdsep)

theorem not_forall_dsep_iff :
    ¬ ∀ (G : DAG) (X Y Z : Finset ℕ), dSeparates G X Y Z ↔ DAG.dSeparated G X Y Z := by
  intro h
  rcases dsep_complete_endpoint_in_Z_counterexample with ⟨G, X, Y, Z, hdsep, hnot⟩
  exact hnot ((h G X Y Z).mpr hdsep)

end

end FiniteQuerySandbox
