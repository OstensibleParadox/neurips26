// Lean compiler output
// Module: FiniteQuerySandbox.InfoTheory.MutualInfo
// Imports: public import Init public import FiniteQuerySandbox.InfoTheory.Entropy public import FiniteQuerySandbox.InfoTheory.Marginal public import FiniteQuerySandbox.InfoTheory.KL
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
lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalPairFst___redArg(lean_object*, lean_object*, lean_object*);
lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalPairSnd___redArg(lean_object*, lean_object*, lean_object*);
lean_object* lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_4214226450____hygCtx___hyg_8_(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass___redArg(lean_object* v_inst_1_, lean_object* v_inst_2_, lean_object* v_P_3_, lean_object* v_xy_4_){
_start:
{
lean_object* v_fst_5_; lean_object* v_snd_6_; lean_object* v___x_7_; lean_object* v___x_8_; lean_object* v___f_9_; 
v_fst_5_ = lean_ctor_get(v_xy_4_, 0);
lean_inc(v_fst_5_);
v_snd_6_ = lean_ctor_get(v_xy_4_, 1);
lean_inc(v_snd_6_);
lean_dec_ref(v_xy_4_);
lean_inc(v_P_3_);
v___x_7_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalPairFst___redArg(v_inst_2_, v_P_3_, v_fst_5_);
v___x_8_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalPairSnd___redArg(v_inst_1_, v_P_3_, v_snd_6_);
v___f_9_ = lean_alloc_closure((void*)(lp_mathlib_Real_definition___lam__0_00___x40_Mathlib_Data_Real_Basic_4214226450____hygCtx___hyg_8_), 3, 2);
lean_closure_set(v___f_9_, 0, v___x_7_);
lean_closure_set(v___f_9_, 1, v___x_8_);
return v___f_9_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass(lean_object* v_00_u03b1_10_, lean_object* v_00_u03b2_11_, lean_object* v_inst_12_, lean_object* v_inst_13_, lean_object* v_inst_14_, lean_object* v_inst_15_, lean_object* v_P_16_, lean_object* v_xy_17_){
_start:
{
lean_object* v___x_18_; 
v___x_18_ = lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass___redArg(v_inst_12_, v_inst_13_, v_P_16_, v_xy_17_);
return v___x_18_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass___boxed(lean_object* v_00_u03b1_19_, lean_object* v_00_u03b2_20_, lean_object* v_inst_21_, lean_object* v_inst_22_, lean_object* v_inst_23_, lean_object* v_inst_24_, lean_object* v_P_25_, lean_object* v_xy_26_){
_start:
{
lean_object* v_res_27_; 
v_res_27_ = lp_finiteQuerySandbox_FiniteQuerySandbox_productMarginalMass(v_00_u03b1_19_, v_00_u03b2_20_, v_inst_21_, v_inst_22_, v_inst_23_, v_inst_24_, v_P_25_, v_xy_26_);
lean_dec_ref(v_inst_24_);
lean_dec_ref(v_inst_23_);
return v_res_27_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Entropy(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Marginal(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_KL(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_MutualInfo(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Entropy(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_Marginal(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory_KL(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
