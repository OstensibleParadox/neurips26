// Lean compiler output
// Module: FiniteQuerySandbox.GeometricTools
// Imports: public import Init public import Mathlib.Analysis.SpecialFunctions.Log.Basic public import Mathlib.Data.Real.Basic
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
lean_object* lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_2451848184____hygCtx___hyg_8_(lean_object*, lean_object*);
lean_object* lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_1138242547____hygCtx___hyg_8_(lean_object*, lean_object*, lean_object*);
lean_object* lp_mathlib_abs___at___00EReal_abs_spec__0(lean_object*);
extern lean_object* lp_mathlib_Real_definition_00___x40_Mathlib_Data_Real_Basic_1279875089____hygCtx___hyg_8_;
lean_object* lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_4214226450____hygCtx___hyg_8_(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_ReprSim___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_ReprSim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FCG___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FCG(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_ReprSim___redArg(lean_object* v_hB_1_, lean_object* v_d__repr_2_, lean_object* v_e1_3_, lean_object* v_e2_4_){
_start:
{
lean_object* v___x_5_; lean_object* v___x_6_; lean_object* v___x_7_; lean_object* v___x_8_; lean_object* v___f_9_; lean_object* v___f_10_; 
v___x_5_ = lp_mathlib_Real_definition_00___x40_Mathlib_Data_Real_Basic_1279875089____hygCtx___hyg_8_;
lean_inc(v_hB_1_);
v___x_6_ = lean_apply_1(v_hB_1_, v_e1_3_);
v___x_7_ = lean_apply_1(v_hB_1_, v_e2_4_);
v___x_8_ = lean_apply_2(v_d__repr_2_, v___x_6_, v___x_7_);
v___f_9_ = lean_alloc_closure((void*)(lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_2451848184____hygCtx___hyg_8_), 2, 1);
lean_closure_set(v___f_9_, 0, v___x_8_);
v___f_10_ = lean_alloc_closure((void*)(lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_1138242547____hygCtx___hyg_8_), 3, 2);
lean_closure_set(v___f_10_, 0, v___x_5_);
lean_closure_set(v___f_10_, 1, v___f_9_);
return v___f_10_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_ReprSim(lean_object* v_E_11_, lean_object* v_H_12_, lean_object* v_hB_13_, lean_object* v_d__repr_14_, lean_object* v_e1_15_, lean_object* v_e2_16_){
_start:
{
lean_object* v___x_17_; 
v___x_17_ = lp_finiteQuerySandbox_FiniteQuerySandbox_ReprSim___redArg(v_hB_13_, v_d__repr_14_, v_e1_15_, v_e2_16_);
return v___x_17_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FCG___redArg(lean_object* v_R_18_, lean_object* v_hB_19_, lean_object* v_d__repr_20_, lean_object* v_e1_21_, lean_object* v_e2_22_){
_start:
{
lean_object* v___x_23_; lean_object* v___x_24_; lean_object* v___f_25_; lean_object* v___f_26_; lean_object* v___x_27_; lean_object* v___x_28_; lean_object* v___f_29_; 
lean_inc(v_R_18_);
lean_inc(v_e1_21_);
v___x_23_ = lean_apply_1(v_R_18_, v_e1_21_);
lean_inc(v_e2_22_);
v___x_24_ = lean_apply_1(v_R_18_, v_e2_22_);
v___f_25_ = lean_alloc_closure((void*)(lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_2451848184____hygCtx___hyg_8_), 2, 1);
lean_closure_set(v___f_25_, 0, v___x_24_);
v___f_26_ = lean_alloc_closure((void*)(lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_1138242547____hygCtx___hyg_8_), 3, 2);
lean_closure_set(v___f_26_, 0, v___x_23_);
lean_closure_set(v___f_26_, 1, v___f_25_);
v___x_27_ = lp_mathlib_abs___at___00EReal_abs_spec__0(v___f_26_);
v___x_28_ = lp_finiteQuerySandbox_FiniteQuerySandbox_ReprSim___redArg(v_hB_19_, v_d__repr_20_, v_e1_21_, v_e2_22_);
v___f_29_ = lean_alloc_closure((void*)(lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_4214226450____hygCtx___hyg_8_), 3, 2);
lean_closure_set(v___f_29_, 0, v___x_27_);
lean_closure_set(v___f_29_, 1, v___x_28_);
return v___f_29_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FCG(lean_object* v_E_30_, lean_object* v_H_31_, lean_object* v_R_32_, lean_object* v_hB_33_, lean_object* v_d__repr_34_, lean_object* v_e1_35_, lean_object* v_e2_36_){
_start:
{
lean_object* v___x_37_; 
v___x_37_ = lp_finiteQuerySandbox_FiniteQuerySandbox_FCG___redArg(v_R_32_, v_hB_33_, v_d__repr_34_, v_e1_35_, v_e2_36_);
return v___x_37_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Analysis_SpecialFunctions_Log_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Real_Basic(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_GeometricTools(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Analysis_SpecialFunctions_Log_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Data_Real_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
