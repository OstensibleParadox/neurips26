import Lake
open Lake DSL

package finiteQuerySandbox where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

require mathlib from git "https://github.com/leanprover-community/mathlib4.git"

@[default_target]
lean_lib FiniteQuerySandbox

