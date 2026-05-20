// Lean compiler output
// Module: FiniteQuerySandbox.Impossibility
// Imports: public import Init public import FiniteQuerySandbox.Tools
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
lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_freshIndex(lean_object*, lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_closedOracle(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_closedOracle___boxed(lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_openOracle(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_openOracle___boxed(lean_object*, lean_object*);
static const lean_ctor_object lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0___closed__0 = (const lean_object*)&lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0___closed__0_value;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0___boxed(lean_object*);
static const lean_closure_object lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___closed__0 = (const lean_object*)&lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___closed__0_value;
LEAN_EXPORT const lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier = (const lean_object*)&lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___closed__0_value;
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_closedOracle(lean_object* v_x_1_){
_start:
{
uint8_t v___x_2_; 
v___x_2_ = 0;
return v___x_2_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_closedOracle___boxed(lean_object* v_x_3_){
_start:
{
uint8_t v_res_4_; lean_object* v_r_5_; 
v_res_4_ = lp_finiteQuerySandbox_FiniteQuerySandbox_closedOracle(v_x_3_);
lean_dec(v_x_3_);
v_r_5_ = lean_box(v_res_4_);
return v_r_5_;
}
}
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_openOracle(lean_object* v_support_6_, lean_object* v_n_7_){
_start:
{
lean_object* v___x_8_; lean_object* v___x_9_; uint8_t v___x_10_; 
v___x_8_ = lean_unsigned_to_nat(0u);
v___x_9_ = lp_finiteQuerySandbox_FiniteQuerySandbox_freshIndex(v_support_6_, v___x_8_);
v___x_10_ = lean_nat_dec_eq(v_n_7_, v___x_9_);
lean_dec(v___x_9_);
return v___x_10_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_openOracle___boxed(lean_object* v_support_11_, lean_object* v_n_12_){
_start:
{
uint8_t v_res_13_; lean_object* v_r_14_; 
v_res_13_ = lp_finiteQuerySandbox_FiniteQuerySandbox_openOracle(v_support_11_, v_n_12_);
lean_dec(v_n_12_);
lean_dec(v_support_11_);
v_r_14_ = lean_box(v_res_13_);
return v_r_14_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0(lean_object* v_x_19_){
_start:
{
lean_object* v___x_20_; 
v___x_20_ = ((lean_object*)(lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0___closed__0));
return v___x_20_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0___boxed(lean_object* v_x_21_){
_start:
{
lean_object* v_res_22_; 
v_res_22_ = lp_finiteQuerySandbox_FiniteQuerySandbox_rejectAllCertifier___lam__0(v_x_21_);
lean_dec_ref(v_x_21_);
return v_res_22_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_Tools(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_Impossibility(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_Tools(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
