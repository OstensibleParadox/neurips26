// Lean compiler output
// Module: FiniteQuerySandbox.DAG.Basic
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
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* lp_mathlib_Multiset_filter___redArg(lean_object*, lean_object*);
lean_object* lp_mathlib_Multiset_map___redArg(lean_object*, lean_object*);
lean_object* lp_mathlib_List_pwFilter___at___00List_dedup___at___00Multiset_dedup___at___00Multiset_toFinset___at___00Multiset_bell_spec__2_spec__4_spec__6_spec__8___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_ofRank___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_ofRank(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_ofRank___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__0(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__0___boxed(lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__1___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_image___at___00FiniteQuerySandbox_parents_spec__0___redArg(lean_object*, lean_object*);
static const lean_closure_object lp_finiteQuerySandbox_FiniteQuerySandbox_parents___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__0___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents___closed__0 = (const lean_object*)&lp_finiteQuerySandbox_FiniteQuerySandbox_parents___closed__0_value;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_image___at___00FiniteQuerySandbox_parents_spec__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__0(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__0___boxed(lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__1___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_finiteQuerySandbox_FiniteQuerySandbox_children___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__0___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children___closed__0 = (const lean_object*)&lp_finiteQuerySandbox_FiniteQuerySandbox_children___closed__0_value;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_ofRank___redArg(lean_object* v_nodes_1_, lean_object* v_edges_2_){
_start:
{
lean_object* v___x_3_; 
v___x_3_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3_, 0, v_nodes_1_);
lean_ctor_set(v___x_3_, 1, v_edges_2_);
return v___x_3_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_ofRank(lean_object* v_nodes_4_, lean_object* v_edges_5_, lean_object* v_rank_6_, lean_object* v_edges__subset_7_, lean_object* v_rank__increases_8_){
_start:
{
lean_object* v___x_9_; 
v___x_9_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_9_, 0, v_nodes_4_);
lean_ctor_set(v___x_9_, 1, v_edges_5_);
return v___x_9_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_ofRank___boxed(lean_object* v_nodes_10_, lean_object* v_edges_11_, lean_object* v_rank_12_, lean_object* v_edges__subset_13_, lean_object* v_rank__increases_14_){
_start:
{
lean_object* v_res_15_; 
v_res_15_ = lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_ofRank(v_nodes_10_, v_edges_11_, v_rank_12_, v_edges__subset_13_, v_rank__increases_14_);
lean_dec_ref(v_rank_12_);
return v_res_15_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__0(lean_object* v_self_16_){
_start:
{
lean_object* v_fst_17_; 
v_fst_17_ = lean_ctor_get(v_self_16_, 0);
lean_inc(v_fst_17_);
return v_fst_17_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__0___boxed(lean_object* v_self_18_){
_start:
{
lean_object* v_res_19_; 
v_res_19_ = lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__0(v_self_18_);
lean_dec_ref(v_self_18_);
return v_res_19_;
}
}
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__1(lean_object* v_v_20_, lean_object* v_a_21_){
_start:
{
lean_object* v_snd_22_; uint8_t v___x_23_; 
v_snd_22_ = lean_ctor_get(v_a_21_, 1);
v___x_23_ = lean_nat_dec_eq(v_snd_22_, v_v_20_);
return v___x_23_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__1___boxed(lean_object* v_v_24_, lean_object* v_a_25_){
_start:
{
uint8_t v_res_26_; lean_object* v_r_27_; 
v_res_26_ = lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__1(v_v_24_, v_a_25_);
lean_dec_ref(v_a_25_);
lean_dec(v_v_24_);
v_r_27_ = lean_box(v_res_26_);
return v_r_27_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_image___at___00FiniteQuerySandbox_parents_spec__0___redArg(lean_object* v_f_28_, lean_object* v_s_29_){
_start:
{
lean_object* v___x_30_; lean_object* v___x_31_; 
v___x_30_ = lp_mathlib_Multiset_map___redArg(v_f_28_, v_s_29_);
v___x_31_ = lp_mathlib_List_pwFilter___at___00List_dedup___at___00Multiset_dedup___at___00Multiset_toFinset___at___00Multiset_bell_spec__2_spec__4_spec__6_spec__8___redArg(v___x_30_);
return v___x_31_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents(lean_object* v_G_33_, lean_object* v_v_34_){
_start:
{
lean_object* v_edges_35_; lean_object* v___f_36_; lean_object* v___f_37_; lean_object* v___x_38_; lean_object* v___x_39_; 
v_edges_35_ = lean_ctor_get(v_G_33_, 1);
lean_inc(v_edges_35_);
lean_dec_ref(v_G_33_);
v___f_36_ = ((lean_object*)(lp_finiteQuerySandbox_FiniteQuerySandbox_parents___closed__0));
v___f_37_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_parents___lam__1___boxed), 2, 1);
lean_closure_set(v___f_37_, 0, v_v_34_);
v___x_38_ = lp_mathlib_Multiset_filter___redArg(v___f_37_, v_edges_35_);
v___x_39_ = lp_finiteQuerySandbox_Finset_image___at___00FiniteQuerySandbox_parents_spec__0___redArg(v___f_36_, v___x_38_);
return v___x_39_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_image___at___00FiniteQuerySandbox_parents_spec__0(lean_object* v_00_u03b1_40_, lean_object* v_f_41_, lean_object* v_s_42_){
_start:
{
lean_object* v___x_43_; 
v___x_43_ = lp_finiteQuerySandbox_Finset_image___at___00FiniteQuerySandbox_parents_spec__0___redArg(v_f_41_, v_s_42_);
return v___x_43_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__0(lean_object* v_self_44_){
_start:
{
lean_object* v_snd_45_; 
v_snd_45_ = lean_ctor_get(v_self_44_, 1);
lean_inc(v_snd_45_);
return v_snd_45_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__0___boxed(lean_object* v_self_46_){
_start:
{
lean_object* v_res_47_; 
v_res_47_ = lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__0(v_self_46_);
lean_dec_ref(v_self_46_);
return v_res_47_;
}
}
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__1(lean_object* v_v_48_, lean_object* v_a_49_){
_start:
{
lean_object* v_fst_50_; uint8_t v___x_51_; 
v_fst_50_ = lean_ctor_get(v_a_49_, 0);
v___x_51_ = lean_nat_dec_eq(v_fst_50_, v_v_48_);
return v___x_51_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__1___boxed(lean_object* v_v_52_, lean_object* v_a_53_){
_start:
{
uint8_t v_res_54_; lean_object* v_r_55_; 
v_res_54_ = lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__1(v_v_52_, v_a_53_);
lean_dec_ref(v_a_53_);
lean_dec(v_v_52_);
v_r_55_ = lean_box(v_res_54_);
return v_r_55_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children(lean_object* v_G_57_, lean_object* v_v_58_){
_start:
{
lean_object* v_edges_59_; lean_object* v___f_60_; lean_object* v___f_61_; lean_object* v___x_62_; lean_object* v___x_63_; 
v_edges_59_ = lean_ctor_get(v_G_57_, 1);
lean_inc(v_edges_59_);
lean_dec_ref(v_G_57_);
v___f_60_ = ((lean_object*)(lp_finiteQuerySandbox_FiniteQuerySandbox_children___closed__0));
v___f_61_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_children___lam__1___boxed), 2, 1);
lean_closure_set(v___f_61_, 0, v_v_58_);
v___x_62_ = lp_mathlib_Multiset_filter___redArg(v___f_61_, v_edges_59_);
v___x_63_ = lp_finiteQuerySandbox_Finset_image___at___00FiniteQuerySandbox_parents_spec__0___redArg(v___f_60_, v___x_62_);
return v___x_63_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Basic(uint8_t builtin) {
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
