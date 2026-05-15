import FiniteQuerySandbox.Tools
import FiniteQuerySandbox.InfoTheory
import FiniteQuerySandbox.QuantizedBound
import FiniteQuerySandbox.IdentifiabilityGap
import FiniteQuerySandbox.CMI_Nonneg
import FiniteQuerySandbox.DualCertificate
import CutSetBoundExtract
import FiniteQuerySandbox.TraceRecoverability
import FiniteQuerySandbox.TraceRecoverabilityBridge
import FiniteQuerySandbox.QuotientFactorization
import FiniteQuerySandbox.GeometricTools
import FiniteQuerySandbox.CoveringBound
import FiniteQuerySandbox.PACBounds
import FiniteQuerySandbox.FiniteQueryDecisionImpossibility
import FiniteQuerySandbox.PredictabilityRouteImpossibility
import FiniteQuerySandbox.SeparatedPackingImpossibility

/-!
# FiniteQuerySandbox

Root module for the Lean verification artifact. Importing this file checks the
finite information-theory layer, finite-query impossibility cores, screenability
surrogates, certificate reductions, covering bounds, and PAC algebraic core.
An alternate root name is available via `FiniteQueryAudit`.
-/
