// Lean compiler output
// Module: FiniteQuerySandbox.DAG.Ancestry
// Imports: public import Init public import FiniteQuerySandbox.DAG.Basic
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
lean_object* lp_mathlib_Multiset_erase___at___00Finset_erase___at___00Multiset_bell_spec__3_spec__6(lean_object*, lean_object*);
lean_object* lp_mathlib_Multiset_filter___redArg(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf___lam__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf___lam__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf___lam__0(lean_object* v_v_1_, lean_object* v_a_2_){
_start:
{
lean_object* v_fst_3_; lean_object* v_snd_4_; uint8_t v___x_5_; 
v_fst_3_ = lean_ctor_get(v_a_2_, 0);
v_snd_4_ = lean_ctor_get(v_a_2_, 1);
v___x_5_ = lean_nat_dec_eq(v_fst_3_, v_v_1_);
if (v___x_5_ == 0)
{
uint8_t v___x_6_; 
v___x_6_ = lean_nat_dec_eq(v_snd_4_, v_v_1_);
if (v___x_6_ == 0)
{
uint8_t v___x_7_; 
v___x_7_ = 1;
return v___x_7_;
}
else
{
return v___x_5_;
}
}
else
{
uint8_t v___x_8_; 
v___x_8_ = 0;
return v___x_8_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf___lam__0___boxed(lean_object* v_v_9_, lean_object* v_a_10_){
_start:
{
uint8_t v_res_11_; lean_object* v_r_12_; 
v_res_11_ = lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf___lam__0(v_v_9_, v_a_10_);
lean_dec_ref(v_a_10_);
lean_dec(v_v_9_);
v_r_12_ = lean_box(v_res_11_);
return v_r_12_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf(lean_object* v_G_13_, lean_object* v_v_14_){
_start:
{
lean_object* v_nodes_15_; lean_object* v_edges_16_; lean_object* v___x_18_; uint8_t v_isShared_19_; uint8_t v_isSharedCheck_26_; 
v_nodes_15_ = lean_ctor_get(v_G_13_, 0);
v_edges_16_ = lean_ctor_get(v_G_13_, 1);
v_isSharedCheck_26_ = !lean_is_exclusive(v_G_13_);
if (v_isSharedCheck_26_ == 0)
{
v___x_18_ = v_G_13_;
v_isShared_19_ = v_isSharedCheck_26_;
goto v_resetjp_17_;
}
else
{
lean_inc(v_edges_16_);
lean_inc(v_nodes_15_);
lean_dec(v_G_13_);
v___x_18_ = lean_box(0);
v_isShared_19_ = v_isSharedCheck_26_;
goto v_resetjp_17_;
}
v_resetjp_17_:
{
lean_object* v___f_20_; lean_object* v___x_21_; lean_object* v___x_22_; lean_object* v___x_24_; 
lean_inc(v_v_14_);
v___f_20_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_DAG_deleteLeaf___lam__0___boxed), 2, 1);
lean_closure_set(v___f_20_, 0, v_v_14_);
v___x_21_ = lp_mathlib_Multiset_erase___at___00Finset_erase___at___00Multiset_bell_spec__3_spec__6(v_nodes_15_, v_v_14_);
lean_dec(v_v_14_);
v___x_22_ = lp_mathlib_Multiset_filter___redArg(v___f_20_, v_edges_16_);
if (v_isShared_19_ == 0)
{
lean_ctor_set(v___x_18_, 1, v___x_22_);
lean_ctor_set(v___x_18_, 0, v___x_21_);
v___x_24_ = v___x_18_;
goto v_reusejp_23_;
}
else
{
lean_object* v_reuseFailAlloc_25_; 
v_reuseFailAlloc_25_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_25_, 0, v___x_21_);
lean_ctor_set(v_reuseFailAlloc_25_, 1, v___x_22_);
v___x_24_ = v_reuseFailAlloc_25_;
goto v_reusejp_23_;
}
v_reusejp_23_:
{
return v___x_24_;
}
}
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Basic(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Ancestry(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
