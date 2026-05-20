// Lean compiler output
// Module: FiniteQuerySandbox.InfoTheory.Basic
// Imports: public import Init public import Mathlib
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
extern lean_object* lp_mathlib_Real_definition_00___x40_Mathlib_Data_Real_Basic_1850581184____hygCtx___hyg_8_;
extern lean_object* lp_mathlib_Real_instAddCommMonoid;
lean_object* lp_mathlib_Finset_sum___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg___lam__0(lean_object* v_e_1_, lean_object* v_P_2_, lean_object* v_x_3_){
_start:
{
lean_object* v_toFun_4_; lean_object* v___x_5_; lean_object* v___x_6_; 
v_toFun_4_ = lean_ctor_get(v_e_1_, 0);
lean_inc(v_toFun_4_);
lean_dec_ref(v_e_1_);
v___x_5_ = lean_apply_1(v_toFun_4_, v_x_3_);
v___x_6_ = lean_apply_1(v_P_2_, v___x_5_);
return v___x_6_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg(lean_object* v_e_7_, lean_object* v_P_8_){
_start:
{
lean_object* v___f_9_; 
v___f_9_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg___lam__0), 3, 2);
lean_closure_set(v___f_9_, 0, v_e_7_);
lean_closure_set(v___f_9_, 1, v_P_8_);
return v___f_9_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv(lean_object* v_00_u03b7_10_, lean_object* v_00_u03b8_11_, lean_object* v_inst_12_, lean_object* v_inst_13_, lean_object* v_inst_14_, lean_object* v_inst_15_, lean_object* v_e_16_, lean_object* v_P_17_){
_start:
{
lean_object* v___f_18_; 
v___f_18_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg___lam__0), 3, 2);
lean_closure_set(v___f_18_, 0, v_e_16_);
lean_closure_set(v___f_18_, 1, v_P_17_);
return v___f_18_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___boxed(lean_object* v_00_u03b7_19_, lean_object* v_00_u03b8_20_, lean_object* v_inst_21_, lean_object* v_inst_22_, lean_object* v_inst_23_, lean_object* v_inst_24_, lean_object* v_e_25_, lean_object* v_P_26_){
_start:
{
lean_object* v_res_27_; 
v_res_27_ = lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv(v_00_u03b7_19_, v_00_u03b8_20_, v_inst_21_, v_inst_22_, v_inst_23_, v_inst_24_, v_e_25_, v_P_26_);
lean_dec_ref(v_inst_24_);
lean_dec(v_inst_23_);
lean_dec_ref(v_inst_22_);
lean_dec(v_inst_21_);
return v_res_27_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__0(lean_object* v_f_28_, lean_object* v_inst_29_, lean_object* v_y_30_, lean_object* v_P_31_, lean_object* v_x_32_){
_start:
{
lean_object* v___x_33_; lean_object* v___x_34_; uint8_t v___x_35_; 
lean_inc(v_x_32_);
v___x_33_ = lean_apply_1(v_f_28_, v_x_32_);
v___x_34_ = lean_apply_2(v_inst_29_, v___x_33_, v_y_30_);
v___x_35_ = lean_unbox(v___x_34_);
if (v___x_35_ == 0)
{
lean_object* v___x_36_; 
lean_dec(v_x_32_);
lean_dec(v_P_31_);
v___x_36_ = lp_mathlib_Real_definition_00___x40_Mathlib_Data_Real_Basic_1850581184____hygCtx___hyg_8_;
return v___x_36_;
}
else
{
lean_object* v___x_37_; 
v___x_37_ = lean_apply_1(v_P_31_, v_x_32_);
return v___x_37_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__1(lean_object* v_f_38_, lean_object* v_inst_39_, lean_object* v_P_40_, lean_object* v___x_41_, lean_object* v_inst_42_, lean_object* v_y_43_){
_start:
{
lean_object* v___f_44_; lean_object* v___x_45_; 
v___f_44_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__0), 5, 4);
lean_closure_set(v___f_44_, 0, v_f_38_);
lean_closure_set(v___f_44_, 1, v_inst_39_);
lean_closure_set(v___f_44_, 2, v_y_43_);
lean_closure_set(v___f_44_, 3, v_P_40_);
v___x_45_ = lp_mathlib_Finset_sum___redArg(v___x_41_, v_inst_42_, v___f_44_);
return v___x_45_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__1___boxed(lean_object* v_f_46_, lean_object* v_inst_47_, lean_object* v_P_48_, lean_object* v___x_49_, lean_object* v_inst_50_, lean_object* v_y_51_){
_start:
{
lean_object* v_res_52_; 
v_res_52_ = lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__1(v_f_46_, v_inst_47_, v_P_48_, v___x_49_, v_inst_50_, v_y_51_);
lean_dec_ref(v___x_49_);
return v_res_52_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg(lean_object* v_inst_53_, lean_object* v_inst_54_, lean_object* v_P_55_, lean_object* v_f_56_){
_start:
{
lean_object* v___x_57_; lean_object* v___f_58_; 
v___x_57_ = lp_mathlib_Real_instAddCommMonoid;
v___f_58_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg___lam__1___boxed), 6, 5);
lean_closure_set(v___f_58_, 0, v_f_56_);
lean_closure_set(v___f_58_, 1, v_inst_54_);
lean_closure_set(v___f_58_, 2, v_P_55_);
lean_closure_set(v___f_58_, 3, v___x_57_);
lean_closure_set(v___f_58_, 4, v_inst_53_);
return v___f_58_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map(lean_object* v_00_u03b1_59_, lean_object* v_00_u03b2_60_, lean_object* v_inst_61_, lean_object* v_inst_62_, lean_object* v_inst_63_, lean_object* v_inst_64_, lean_object* v_P_65_, lean_object* v_f_66_){
_start:
{
lean_object* v___x_67_; 
v___x_67_ = lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___redArg(v_inst_61_, v_inst_64_, v_P_65_, v_f_66_);
return v___x_67_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map___boxed(lean_object* v_00_u03b1_68_, lean_object* v_00_u03b2_69_, lean_object* v_inst_70_, lean_object* v_inst_71_, lean_object* v_inst_72_, lean_object* v_inst_73_, lean_object* v_P_74_, lean_object* v_f_75_){
_start:
{
lean_object* v_res_76_; 
v_res_76_ = lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_map(v_00_u03b1_68_, v_00_u03b2_69_, v_inst_70_, v_inst_71_, v_inst_72_, v_inst_73_, v_P_74_, v_f_75_);
lean_dec(v_inst_72_);
lean_dec_ref(v_inst_71_);
return v_res_76_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Basic(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
