// Lean compiler output
// Module: FiniteQuerySandbox.Screenability
// Imports: public import Init
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
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___lam__0(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___lam__0___boxed(lean_object*);
static const lean_closure_object lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___lam__0___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___closed__0 = (const lean_object*)&lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___closed__0_value;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___lam__0(lean_object* v___y_1_){
_start:
{
lean_inc(v___y_1_);
return v___y_1_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___lam__0___boxed(lean_object* v___y_2_){
_start:
{
lean_object* v_res_3_; 
v_res_3_ = lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___lam__0(v___y_2_);
lean_dec(v___y_2_);
return v_res_3_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen(lean_object* v_T_5_){
_start:
{
lean_object* v___f_6_; 
v___f_6_ = ((lean_object*)(lp_finiteQuerySandbox_FiniteQuerySandbox_identityScreen___closed__0));
return v___f_6_;
}
}
lean_object* initialize_Init(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_Screenability(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
