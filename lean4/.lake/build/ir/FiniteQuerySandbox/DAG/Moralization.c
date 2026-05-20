// Lean compiler output
// Module: FiniteQuerySandbox.DAG.Moralization
// Imports: public import Init public import FiniteQuerySandbox.DAG.Ancestry
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
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_moralGraph(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_moralGraph___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_moralGraph(lean_object* v_G_1_, lean_object* v_S_2_){
_start:
{
lean_object* v___x_3_; 
v___x_3_ = lean_box(0);
return v___x_3_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_moralGraph___boxed(lean_object* v_G_4_, lean_object* v_S_5_){
_start:
{
lean_object* v_res_6_; 
v_res_6_ = lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_moralGraph(v_G_4_, v_S_5_);
lean_dec(v_S_5_);
lean_dec_ref(v_G_4_);
return v_res_6_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Ancestry(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Moralization(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Ancestry(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
