// Lean compiler output
// Module: FiniteQuerySandbox.InfoTheory.all
// Imports: public import Init public import FiniteQuerySandbox.InfoTheory.Basic public import FiniteQuerySandbox.InfoTheory.KL public import FiniteQuerySandbox.InfoTheory.Entropy public import FiniteQuerySandbox.InfoTheory.Marginal public import FiniteQuerySandbox.InfoTheory.MutualInfo public import FiniteQuerySandbox.InfoTheory.Conditional public import FiniteQuerySandbox.InfoTheory.DPI
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
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Basic(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_KL(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Entropy(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Marginal(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_MutualInfo(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Conditional(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_DPI(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_all(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_KL(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Entropy(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Marginal(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_MutualInfo(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Conditional(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_DPI(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
