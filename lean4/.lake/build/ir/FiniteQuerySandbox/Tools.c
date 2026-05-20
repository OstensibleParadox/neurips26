// Lean compiler output
// Module: FiniteQuerySandbox.Tools
// Imports: public import Init public import Init.Data.List.Basic public import Init.Data.List.Lemmas
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
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_supportBound(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_supportBound___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_Tools_0__FiniteQuerySandbox_supportBound_match__1_splitter___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_Tools_0__FiniteQuerySandbox_supportBound_match__1_splitter(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_freshIndex(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_freshIndex___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_supportBound(lean_object* v_x_1_){
_start:
{
if (lean_obj_tag(v_x_1_) == 0)
{
lean_object* v___x_2_; 
v___x_2_ = lean_unsigned_to_nat(0u);
return v___x_2_;
}
else
{
lean_object* v_head_3_; lean_object* v_tail_4_; lean_object* v___x_5_; uint8_t v___x_6_; 
v_head_3_ = lean_ctor_get(v_x_1_, 0);
v_tail_4_ = lean_ctor_get(v_x_1_, 1);
v___x_5_ = lp_finiteQuerySandbox_FiniteQuerySandbox_supportBound(v_tail_4_);
v___x_6_ = lean_nat_dec_le(v_head_3_, v___x_5_);
if (v___x_6_ == 0)
{
lean_dec(v___x_5_);
lean_inc(v_head_3_);
return v_head_3_;
}
else
{
return v___x_5_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_supportBound___boxed(lean_object* v_x_7_){
_start:
{
lean_object* v_res_8_; 
v_res_8_ = lp_finiteQuerySandbox_FiniteQuerySandbox_supportBound(v_x_7_);
lean_dec(v_x_7_);
return v_res_8_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_Tools_0__FiniteQuerySandbox_supportBound_match__1_splitter___redArg(lean_object* v_x_9_, lean_object* v_h__1_10_, lean_object* v_h__2_11_){
_start:
{
if (lean_obj_tag(v_x_9_) == 0)
{
lean_object* v___x_12_; lean_object* v___x_13_; 
lean_dec(v_h__2_11_);
v___x_12_ = lean_box(0);
v___x_13_ = lean_apply_1(v_h__1_10_, v___x_12_);
return v___x_13_;
}
else
{
lean_object* v_head_14_; lean_object* v_tail_15_; lean_object* v___x_16_; 
lean_dec(v_h__1_10_);
v_head_14_ = lean_ctor_get(v_x_9_, 0);
lean_inc(v_head_14_);
v_tail_15_ = lean_ctor_get(v_x_9_, 1);
lean_inc(v_tail_15_);
lean_dec_ref(v_x_9_);
v___x_16_ = lean_apply_2(v_h__2_11_, v_head_14_, v_tail_15_);
return v___x_16_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_Tools_0__FiniteQuerySandbox_supportBound_match__1_splitter(lean_object* v_motive_17_, lean_object* v_x_18_, lean_object* v_h__1_19_, lean_object* v_h__2_20_){
_start:
{
if (lean_obj_tag(v_x_18_) == 0)
{
lean_object* v___x_21_; lean_object* v___x_22_; 
lean_dec(v_h__2_20_);
v___x_21_ = lean_box(0);
v___x_22_ = lean_apply_1(v_h__1_19_, v___x_21_);
return v___x_22_;
}
else
{
lean_object* v_head_23_; lean_object* v_tail_24_; lean_object* v___x_25_; 
lean_dec(v_h__1_19_);
v_head_23_ = lean_ctor_get(v_x_18_, 0);
lean_inc(v_head_23_);
v_tail_24_ = lean_ctor_get(v_x_18_, 1);
lean_inc(v_tail_24_);
lean_dec_ref(v_x_18_);
v___x_25_ = lean_apply_2(v_h__2_20_, v_head_23_, v_tail_24_);
return v___x_25_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_freshIndex(lean_object* v_support_26_, lean_object* v_k_27_){
_start:
{
lean_object* v___x_28_; lean_object* v___x_29_; lean_object* v___x_30_; lean_object* v___x_31_; 
v___x_28_ = lp_finiteQuerySandbox_FiniteQuerySandbox_supportBound(v_support_26_);
v___x_29_ = lean_nat_add(v_k_27_, v___x_28_);
lean_dec(v___x_28_);
v___x_30_ = lean_unsigned_to_nat(1u);
v___x_31_ = lean_nat_add(v___x_29_, v___x_30_);
lean_dec(v___x_29_);
return v___x_31_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_freshIndex___boxed(lean_object* v_support_32_, lean_object* v_k_33_){
_start:
{
lean_object* v_res_34_; 
v_res_34_ = lp_finiteQuerySandbox_FiniteQuerySandbox_freshIndex(v_support_32_, v_k_33_);
lean_dec(v_k_33_);
lean_dec(v_support_32_);
return v_res_34_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init_Data_List_Basic(uint8_t builtin);
lean_object* initialize_Init_Data_List_Lemmas(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_Tools(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init_Data_List_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init_Data_List_Lemmas(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
