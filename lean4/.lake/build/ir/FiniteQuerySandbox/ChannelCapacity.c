// Lean compiler output
// Module: FiniteQuerySandbox.ChannelCapacity
// Imports: public import Init public import Mathlib public import FiniteQuerySandbox.InfoTheory
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
lean_object* lp_mathlib_Finset_sum___redArg(lean_object*, lean_object*, lean_object*);
extern lean_object* lp_mathlib_Real_instAddCommMonoid;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__2(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__0(lean_object* v_z_1_, lean_object* v_y_2_, lean_object* v_x_3_, lean_object* v_P_4_, lean_object* v_w_5_){
_start:
{
lean_object* v___x_6_; lean_object* v___x_7_; lean_object* v___x_8_; lean_object* v___x_9_; 
v___x_6_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_6_, 0, v_z_1_);
lean_ctor_set(v___x_6_, 1, v_w_5_);
v___x_7_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_7_, 0, v_y_2_);
lean_ctor_set(v___x_7_, 1, v___x_6_);
v___x_8_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_8_, 0, v_x_3_);
lean_ctor_set(v___x_8_, 1, v___x_7_);
v___x_9_ = lean_apply_1(v_P_4_, v___x_8_);
return v___x_9_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__1(lean_object* v_y_10_, lean_object* v_x_11_, lean_object* v_P_12_, lean_object* v___x_13_, lean_object* v_inst_14_, lean_object* v_z_15_){
_start:
{
lean_object* v___f_16_; lean_object* v___x_17_; 
v___f_16_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__0), 5, 4);
lean_closure_set(v___f_16_, 0, v_z_15_);
lean_closure_set(v___f_16_, 1, v_y_10_);
lean_closure_set(v___f_16_, 2, v_x_11_);
lean_closure_set(v___f_16_, 3, v_P_12_);
v___x_17_ = lp_mathlib_Finset_sum___redArg(v___x_13_, v_inst_14_, v___f_16_);
return v___x_17_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__1___boxed(lean_object* v_y_18_, lean_object* v_x_19_, lean_object* v_P_20_, lean_object* v___x_21_, lean_object* v_inst_22_, lean_object* v_z_23_){
_start:
{
lean_object* v_res_24_; 
v_res_24_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__1(v_y_18_, v_x_19_, v_P_20_, v___x_21_, v_inst_22_, v_z_23_);
lean_dec_ref(v___x_21_);
return v_res_24_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__2(lean_object* v_y_25_, lean_object* v_P_26_, lean_object* v___x_27_, lean_object* v_inst_28_, lean_object* v_inst_29_, lean_object* v_x_30_){
_start:
{
lean_object* v___f_31_; lean_object* v___x_32_; 
lean_inc_ref(v___x_27_);
v___f_31_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__1___boxed), 6, 5);
lean_closure_set(v___f_31_, 0, v_y_25_);
lean_closure_set(v___f_31_, 1, v_x_30_);
lean_closure_set(v___f_31_, 2, v_P_26_);
lean_closure_set(v___f_31_, 3, v___x_27_);
lean_closure_set(v___f_31_, 4, v_inst_28_);
v___x_32_ = lp_mathlib_Finset_sum___redArg(v___x_27_, v_inst_29_, v___f_31_);
lean_dec_ref(v___x_27_);
return v___x_32_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg(lean_object* v_inst_33_, lean_object* v_inst_34_, lean_object* v_inst_35_, lean_object* v_P_36_, lean_object* v_y_37_){
_start:
{
lean_object* v___x_38_; lean_object* v___f_39_; lean_object* v___x_40_; 
v___x_38_ = lp_mathlib_Real_instAddCommMonoid;
v___f_39_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg___lam__2), 6, 5);
lean_closure_set(v___f_39_, 0, v_y_37_);
lean_closure_set(v___f_39_, 1, v_P_36_);
lean_closure_set(v___f_39_, 2, v___x_38_);
lean_closure_set(v___f_39_, 3, v_inst_35_);
lean_closure_set(v___f_39_, 4, v_inst_34_);
v___x_40_ = lp_mathlib_Finset_sum___redArg(v___x_38_, v_inst_33_, v___f_39_);
return v___x_40_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass(lean_object* v_00_u03b1_41_, lean_object* v_00_u03b2_42_, lean_object* v_00_u03b3_43_, lean_object* v_00_u03b4_44_, lean_object* v_inst_45_, lean_object* v_inst_46_, lean_object* v_inst_47_, lean_object* v_inst_48_, lean_object* v_inst_49_, lean_object* v_inst_50_, lean_object* v_inst_51_, lean_object* v_inst_52_, lean_object* v_P_53_, lean_object* v_y_54_){
_start:
{
lean_object* v___x_55_; 
v___x_55_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___redArg(v_inst_45_, v_inst_47_, v_inst_48_, v_P_53_, v_y_54_);
return v___x_55_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass___boxed(lean_object* v_00_u03b1_56_, lean_object* v_00_u03b2_57_, lean_object* v_00_u03b3_58_, lean_object* v_00_u03b4_59_, lean_object* v_inst_60_, lean_object* v_inst_61_, lean_object* v_inst_62_, lean_object* v_inst_63_, lean_object* v_inst_64_, lean_object* v_inst_65_, lean_object* v_inst_66_, lean_object* v_inst_67_, lean_object* v_P_68_, lean_object* v_y_69_){
_start:
{
lean_object* v_res_70_; 
v_res_70_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYMass(v_00_u03b1_56_, v_00_u03b2_57_, v_00_u03b3_58_, v_00_u03b4_59_, v_inst_60_, v_inst_61_, v_inst_62_, v_inst_63_, v_inst_64_, v_inst_65_, v_inst_66_, v_inst_67_, v_P_68_, v_y_69_);
lean_dec_ref(v_inst_67_);
lean_dec_ref(v_inst_66_);
lean_dec_ref(v_inst_65_);
lean_dec_ref(v_inst_64_);
lean_dec(v_inst_61_);
return v_res_70_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_ChannelCapacity(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
