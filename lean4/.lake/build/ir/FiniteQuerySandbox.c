// Lean compiler output
// Module: FiniteQuerySandbox
// Imports: public import Init public import FiniteQuerySandbox.Tools public import FiniteQuerySandbox.InfoTheory public import FiniteQuerySandbox.QuantizedBound public import FiniteQuerySandbox.IdentifiabilityGap public import FiniteQuerySandbox.CMI_Nonneg public import FiniteQuerySandbox.DualCertificate public import FiniteQuerySandbox.ChannelCapacity public import FiniteQuerySandbox.CaseStudy public import FiniteQuerySandbox.CutSetBoundExtract public import FiniteQuerySandbox.TraceRecoverability public import FiniteQuerySandbox.TraceRecoverabilityBridge public import FiniteQuerySandbox.QuotientFactorization public import FiniteQuerySandbox.GeometricTools public import FiniteQuerySandbox.CoveringBound public import FiniteQuerySandbox.PACBounds public import FiniteQuerySandbox.FiniteQueryDecisionImpossibility public import FiniteQuerySandbox.PredictabilityRouteImpossibility public import FiniteQuerySandbox.SeparatedPackingImpossibility public import FiniteQuerySandbox.DAGParser public import FiniteQuerySandbox.MarkovGenerator public import FiniteQuerySandbox.DSepCMIBridge
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_Tools(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_QuantizedBound(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_IdentifiabilityGap(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_CMI__Nonneg(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DualCertificate(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_ChannelCapacity(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_CaseStudy(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_CutSetBoundExtract(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_TraceRecoverability(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_TraceRecoverabilityBridge(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_QuotientFactorization(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_GeometricTools(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_CoveringBound(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_PACBounds(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_FiniteQueryDecisionImpossibility(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_PredictabilityRouteImpossibility(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_SeparatedPackingImpossibility(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAGParser(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_MarkovGenerator(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DSepCMIBridge(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_Tools(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_QuantizedBound(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_IdentifiabilityGap(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_CMI__Nonneg(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_DualCertificate(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_ChannelCapacity(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_CaseStudy(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_CutSetBoundExtract(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_TraceRecoverability(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_TraceRecoverabilityBridge(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_QuotientFactorization(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_GeometricTools(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_CoveringBound(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_PACBounds(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_FiniteQueryDecisionImpossibility(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_PredictabilityRouteImpossibility(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_SeparatedPackingImpossibility(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_DAGParser(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_MarkovGenerator(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_DSepCMIBridge(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
