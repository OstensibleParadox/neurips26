// Lean compiler output
// Module: FiniteQuerySandbox.MarkovGenerator
// Imports: public import Init public import FiniteQuerySandbox.DAGParser public import FiniteQuerySandbox.InfoTheory
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
uint8_t l_List_elem___at___00Lean_Meta_Grind_Arith_Cutsat_checkElimEqs_spec__0(lean_object*, lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
lean_object* lp_mathlib___private_Init_Data_List_Impl_0__List_eraseTR_go___at___00Multiset_erase___at___00Finset_erase___at___00Multiset_bell_spec__3_spec__6_spec__9(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_parents(lean_object*, lean_object*);
lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_children(lean_object*, lean_object*);
lean_object* lean_array_mk(lean_object*);
lean_object* lean_array_get_size(lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
size_t lean_usize_of_nat(lean_object*);
uint8_t lean_usize_dec_eq(size_t, size_t);
size_t lean_usize_sub(size_t, size_t);
lean_object* lean_array_uget_borrowed(lean_object*, size_t);
lean_object* lp_mathlib_Multiset_bind___redArg(lean_object*, lean_object*);
lean_object* lp_mathlib_List_pwFilter___at___00List_dedup___at___00Multiset_dedup___at___00Multiset_toFinset___at___00Multiset_bell_spec__2_spec__4_spec__6_spec__8___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_spouses___lam__0(lean_object*, lean_object*);
static const lean_array_object lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_array_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 246}, .m_size = 0, .m_capacity = 0, .m_data = {}};
static const lean_object* lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1___closed__0 = (const lean_object*)&lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1___closed__0_value;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0___redArg___lam__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_spouses(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_Init_Data_Array_Basic_0__Array_foldrMUnsafe_fold___at___00List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0_spec__1(lean_object*, size_t, size_t, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_Init_Data_Array_Basic_0__Array_foldrMUnsafe_fold___at___00List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_computeMarkovBlanket(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_spouses___lam__0(lean_object* v_G_1_, lean_object* v_c_2_){
_start:
{
lean_object* v___x_3_; 
v___x_3_ = lp_finiteQuerySandbox_FiniteQuerySandbox_parents(v_G_1_, v_c_2_);
return v___x_3_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1(lean_object* v_x_6_, lean_object* v_x_7_){
_start:
{
if (lean_obj_tag(v_x_7_) == 0)
{
return v_x_6_;
}
else
{
lean_object* v_head_8_; lean_object* v_tail_9_; uint8_t v___x_10_; 
v_head_8_ = lean_ctor_get(v_x_7_, 0);
v_tail_9_ = lean_ctor_get(v_x_7_, 1);
v___x_10_ = l_List_elem___at___00Lean_Meta_Grind_Arith_Cutsat_checkElimEqs_spec__0(v_head_8_, v_x_6_);
if (v___x_10_ == 0)
{
v_x_7_ = v_tail_9_;
goto _start;
}
else
{
lean_object* v___x_12_; lean_object* v___x_13_; 
v___x_12_ = ((lean_object*)(lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1___closed__0));
lean_inc(v_x_6_);
v___x_13_ = lp_mathlib___private_Init_Data_List_Impl_0__List_eraseTR_go___at___00Multiset_erase___at___00Finset_erase___at___00Multiset_bell_spec__3_spec__6_spec__9(v_x_6_, v_head_8_, v_x_6_, v___x_12_);
lean_dec(v_x_6_);
v_x_6_ = v___x_13_;
v_x_7_ = v_tail_9_;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1___boxed(lean_object* v_x_15_, lean_object* v_x_16_){
_start:
{
lean_object* v_res_17_; 
v_res_17_ = lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1(v_x_15_, v_x_16_);
lean_dec(v_x_16_);
return v_res_17_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1(lean_object* v_s_18_, lean_object* v_t_19_){
_start:
{
lean_object* v___x_20_; 
v___x_20_ = lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1(v_s_18_, v_t_19_);
return v___x_20_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1___boxed(lean_object* v_s_21_, lean_object* v_t_22_){
_start:
{
lean_object* v_res_23_; 
v_res_23_ = lp_finiteQuerySandbox_Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1(v_s_21_, v_t_22_);
lean_dec(v_t_22_);
return v_res_23_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0___redArg___lam__0(lean_object* v_t_24_, lean_object* v_a_25_){
_start:
{
lean_object* v___x_26_; 
v___x_26_ = lean_apply_1(v_t_24_, v_a_25_);
return v___x_26_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0___redArg(lean_object* v_s_27_, lean_object* v_t_28_){
_start:
{
lean_object* v___f_29_; lean_object* v___x_30_; lean_object* v___x_31_; 
v___f_29_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0___redArg___lam__0), 2, 1);
lean_closure_set(v___f_29_, 0, v_t_28_);
v___x_30_ = lp_mathlib_Multiset_bind___redArg(v_s_27_, v___f_29_);
v___x_31_ = lp_mathlib_List_pwFilter___at___00List_dedup___at___00Multiset_dedup___at___00Multiset_toFinset___at___00Multiset_bell_spec__2_spec__4_spec__6_spec__8___redArg(v___x_30_);
return v___x_31_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_spouses(lean_object* v_G_32_, lean_object* v_v_33_){
_start:
{
lean_object* v___f_34_; lean_object* v___x_35_; lean_object* v___x_36_; lean_object* v___x_37_; lean_object* v___x_38_; lean_object* v___x_39_; 
lean_inc_ref(v_G_32_);
v___f_34_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_spouses___lam__0), 2, 1);
lean_closure_set(v___f_34_, 0, v_G_32_);
lean_inc(v_v_33_);
v___x_35_ = lp_finiteQuerySandbox_FiniteQuerySandbox_children(v_G_32_, v_v_33_);
v___x_36_ = lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0___redArg(v___x_35_, v___f_34_);
v___x_37_ = lean_box(0);
v___x_38_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_38_, 0, v_v_33_);
lean_ctor_set(v___x_38_, 1, v___x_37_);
v___x_39_ = lp_finiteQuerySandbox_List_diff___at___00Multiset_sub___at___00FiniteQuerySandbox_spouses_spec__1_spec__1(v___x_36_, v___x_38_);
lean_dec_ref(v___x_38_);
return v___x_39_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0(lean_object* v_00_u03b1_40_, lean_object* v_s_41_, lean_object* v_t_42_){
_start:
{
lean_object* v___x_43_; 
v___x_43_ = lp_finiteQuerySandbox_Finset_biUnion___at___00FiniteQuerySandbox_spouses_spec__0___redArg(v_s_41_, v_t_42_);
return v___x_43_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_Init_Data_Array_Basic_0__Array_foldrMUnsafe_fold___at___00List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0_spec__1(lean_object* v_as_44_, size_t v_i_45_, size_t v_stop_46_, lean_object* v_b_47_){
_start:
{
uint8_t v___x_48_; 
v___x_48_ = lean_usize_dec_eq(v_i_45_, v_stop_46_);
if (v___x_48_ == 0)
{
size_t v___x_49_; size_t v___x_50_; lean_object* v___x_51_; uint8_t v___x_52_; 
v___x_49_ = ((size_t)1ULL);
v___x_50_ = lean_usize_sub(v_i_45_, v___x_49_);
v___x_51_ = lean_array_uget_borrowed(v_as_44_, v___x_50_);
v___x_52_ = l_List_elem___at___00Lean_Meta_Grind_Arith_Cutsat_checkElimEqs_spec__0(v___x_51_, v_b_47_);
if (v___x_52_ == 0)
{
lean_object* v___x_53_; 
lean_inc(v___x_51_);
v___x_53_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_53_, 0, v___x_51_);
lean_ctor_set(v___x_53_, 1, v_b_47_);
v_i_45_ = v___x_50_;
v_b_47_ = v___x_53_;
goto _start;
}
else
{
v_i_45_ = v___x_50_;
goto _start;
}
}
else
{
return v_b_47_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_Init_Data_Array_Basic_0__Array_foldrMUnsafe_fold___at___00List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0_spec__1___boxed(lean_object* v_as_56_, lean_object* v_i_57_, lean_object* v_stop_58_, lean_object* v_b_59_){
_start:
{
size_t v_i_boxed_60_; size_t v_stop_boxed_61_; lean_object* v_res_62_; 
v_i_boxed_60_ = lean_unbox_usize(v_i_57_);
lean_dec(v_i_57_);
v_stop_boxed_61_ = lean_unbox_usize(v_stop_58_);
lean_dec(v_stop_58_);
v_res_62_ = lp_finiteQuerySandbox___private_Init_Data_Array_Basic_0__Array_foldrMUnsafe_fold___at___00List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0_spec__1(v_as_56_, v_i_boxed_60_, v_stop_boxed_61_, v_b_59_);
lean_dec_ref(v_as_56_);
return v_res_62_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0(lean_object* v_init_63_, lean_object* v_l_64_){
_start:
{
lean_object* v___x_65_; lean_object* v___x_66_; lean_object* v___x_67_; uint8_t v___x_68_; 
v___x_65_ = lean_array_mk(v_l_64_);
v___x_66_ = lean_array_get_size(v___x_65_);
v___x_67_ = lean_unsigned_to_nat(0u);
v___x_68_ = lean_nat_dec_lt(v___x_67_, v___x_66_);
if (v___x_68_ == 0)
{
lean_dec_ref(v___x_65_);
return v_init_63_;
}
else
{
size_t v___x_69_; size_t v___x_70_; lean_object* v___x_71_; 
v___x_69_ = lean_usize_of_nat(v___x_66_);
v___x_70_ = ((size_t)0ULL);
v___x_71_ = lp_finiteQuerySandbox___private_Init_Data_Array_Basic_0__Array_foldrMUnsafe_fold___at___00List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0_spec__1(v___x_65_, v___x_69_, v___x_70_, v_init_63_);
lean_dec_ref(v___x_65_);
return v___x_71_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0(lean_object* v_s_72_, lean_object* v_t_73_){
_start:
{
lean_object* v___x_74_; 
v___x_74_ = lp_finiteQuerySandbox_List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0(v_t_73_, v_s_72_);
return v___x_74_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_computeMarkovBlanket(lean_object* v_G_75_, lean_object* v_v_76_){
_start:
{
lean_object* v___x_77_; lean_object* v___x_78_; lean_object* v___x_79_; lean_object* v___x_80_; lean_object* v___x_81_; 
lean_inc_n(v_v_76_, 2);
lean_inc_ref_n(v_G_75_, 2);
v___x_77_ = lp_finiteQuerySandbox_FiniteQuerySandbox_parents(v_G_75_, v_v_76_);
v___x_78_ = lp_finiteQuerySandbox_FiniteQuerySandbox_children(v_G_75_, v_v_76_);
v___x_79_ = lp_finiteQuerySandbox_List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0(v___x_78_, v___x_77_);
v___x_80_ = lp_finiteQuerySandbox_FiniteQuerySandbox_spouses(v_G_75_, v_v_76_);
v___x_81_ = lp_finiteQuerySandbox_List_foldrTR___at___00Multiset_ndunion___at___00FiniteQuerySandbox_computeMarkovBlanket_spec__0_spec__0(v___x_80_, v___x_79_);
return v___x_81_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAGParser(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_MarkovGenerator(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_DAGParser(builtin);
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
