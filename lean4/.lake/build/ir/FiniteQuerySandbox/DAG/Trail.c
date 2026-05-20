// Lean compiler output
// Module: FiniteQuerySandbox.DAG.Trail
// Imports: public import Init public import FiniteQuerySandbox.DAG.Ancestry
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
lean_object* lp_mathlib_List_pwFilter___at___00List_dedup___at___00Multiset_dedup___at___00Multiset_toFinset___at___00List_toFinset___at___00Finset_equivBitIndices_spec__0_spec__0_spec__1_spec__4_spec__5___redArg(lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nil_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nil_elim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nil_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_forward_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_forward_elim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_forward_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_backward_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_backward_elim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_backward_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx(uint8_t);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_toCtorIdx(uint8_t);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_toCtorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim(lean_object*, lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ofNat(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ofNat___boxed(lean_object*);
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_instDecidableEqTrailDir(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_instDecidableEqTrailDir___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter___redArg(uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter___redArg___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_Trail_toList_match__1_splitter___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_Trail_toList_match__1_splitter(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_Trail_toList_match__1_splitter___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___redArg(lean_object* v_x_1_){
_start:
{
switch(lean_obj_tag(v_x_1_))
{
case 0:
{
lean_object* v___x_2_; 
v___x_2_ = lean_unsigned_to_nat(0u);
return v___x_2_;
}
case 1:
{
lean_object* v___x_3_; 
v___x_3_ = lean_unsigned_to_nat(1u);
return v___x_3_;
}
default: 
{
lean_object* v___x_4_; 
v___x_4_ = lean_unsigned_to_nat(2u);
return v___x_4_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___redArg___boxed(lean_object* v_x_5_){
_start:
{
lean_object* v_res_6_; 
v_res_6_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___redArg(v_x_5_);
lean_dec_ref(v_x_5_);
return v_res_6_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx(lean_object* v_G_7_, lean_object* v_a_8_, lean_object* v_a_9_, lean_object* v_x_10_){
_start:
{
lean_object* v___x_11_; 
v___x_11_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___redArg(v_x_10_);
return v___x_11_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx___boxed(lean_object* v_G_12_, lean_object* v_a_13_, lean_object* v_a_14_, lean_object* v_x_15_){
_start:
{
lean_object* v_res_16_; 
v_res_16_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorIdx(v_G_12_, v_a_13_, v_a_14_, v_x_15_);
lean_dec_ref(v_x_15_);
lean_dec(v_a_14_);
lean_dec(v_a_13_);
lean_dec_ref(v_G_12_);
return v_res_16_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(lean_object* v_t_17_, lean_object* v_k_18_){
_start:
{
if (lean_obj_tag(v_t_17_) == 0)
{
lean_object* v_v_19_; lean_object* v___x_20_; 
v_v_19_ = lean_ctor_get(v_t_17_, 0);
lean_inc(v_v_19_);
lean_dec_ref(v_t_17_);
v___x_20_ = lean_apply_1(v_k_18_, v_v_19_);
return v___x_20_;
}
else
{
lean_object* v_u_21_; lean_object* v_w_22_; lean_object* v_v_23_; lean_object* v_tail_24_; lean_object* v___x_25_; 
v_u_21_ = lean_ctor_get(v_t_17_, 0);
lean_inc(v_u_21_);
v_w_22_ = lean_ctor_get(v_t_17_, 1);
lean_inc(v_w_22_);
v_v_23_ = lean_ctor_get(v_t_17_, 2);
lean_inc(v_v_23_);
v_tail_24_ = lean_ctor_get(v_t_17_, 3);
lean_inc_ref(v_tail_24_);
lean_dec_ref(v_t_17_);
v___x_25_ = lean_apply_5(v_k_18_, v_u_21_, v_w_22_, v_v_23_, lean_box(0), v_tail_24_);
return v___x_25_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim(lean_object* v_G_26_, lean_object* v_motive_27_, lean_object* v_ctorIdx_28_, lean_object* v_a_29_, lean_object* v_a_30_, lean_object* v_t_31_, lean_object* v_h_32_, lean_object* v_k_33_){
_start:
{
lean_object* v___x_34_; 
v___x_34_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(v_t_31_, v_k_33_);
return v___x_34_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___boxed(lean_object* v_G_35_, lean_object* v_motive_36_, lean_object* v_ctorIdx_37_, lean_object* v_a_38_, lean_object* v_a_39_, lean_object* v_t_40_, lean_object* v_h_41_, lean_object* v_k_42_){
_start:
{
lean_object* v_res_43_; 
v_res_43_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim(v_G_35_, v_motive_36_, v_ctorIdx_37_, v_a_38_, v_a_39_, v_t_40_, v_h_41_, v_k_42_);
lean_dec(v_a_39_);
lean_dec(v_a_38_);
lean_dec(v_ctorIdx_37_);
lean_dec_ref(v_G_35_);
return v_res_43_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nil_elim___redArg(lean_object* v_t_44_, lean_object* v_nil_45_){
_start:
{
lean_object* v___x_46_; 
v___x_46_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(v_t_44_, v_nil_45_);
return v___x_46_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nil_elim(lean_object* v_G_47_, lean_object* v_motive_48_, lean_object* v_a_49_, lean_object* v_a_50_, lean_object* v_t_51_, lean_object* v_h_52_, lean_object* v_nil_53_){
_start:
{
lean_object* v___x_54_; 
v___x_54_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(v_t_51_, v_nil_53_);
return v___x_54_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nil_elim___boxed(lean_object* v_G_55_, lean_object* v_motive_56_, lean_object* v_a_57_, lean_object* v_a_58_, lean_object* v_t_59_, lean_object* v_h_60_, lean_object* v_nil_61_){
_start:
{
lean_object* v_res_62_; 
v_res_62_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nil_elim(v_G_55_, v_motive_56_, v_a_57_, v_a_58_, v_t_59_, v_h_60_, v_nil_61_);
lean_dec(v_a_58_);
lean_dec(v_a_57_);
lean_dec_ref(v_G_55_);
return v_res_62_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_forward_elim___redArg(lean_object* v_t_63_, lean_object* v_forward_64_){
_start:
{
lean_object* v___x_65_; 
v___x_65_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(v_t_63_, v_forward_64_);
return v___x_65_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_forward_elim(lean_object* v_G_66_, lean_object* v_motive_67_, lean_object* v_a_68_, lean_object* v_a_69_, lean_object* v_t_70_, lean_object* v_h_71_, lean_object* v_forward_72_){
_start:
{
lean_object* v___x_73_; 
v___x_73_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(v_t_70_, v_forward_72_);
return v___x_73_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_forward_elim___boxed(lean_object* v_G_74_, lean_object* v_motive_75_, lean_object* v_a_76_, lean_object* v_a_77_, lean_object* v_t_78_, lean_object* v_h_79_, lean_object* v_forward_80_){
_start:
{
lean_object* v_res_81_; 
v_res_81_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_forward_elim(v_G_74_, v_motive_75_, v_a_76_, v_a_77_, v_t_78_, v_h_79_, v_forward_80_);
lean_dec(v_a_77_);
lean_dec(v_a_76_);
lean_dec_ref(v_G_74_);
return v_res_81_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_backward_elim___redArg(lean_object* v_t_82_, lean_object* v_backward_83_){
_start:
{
lean_object* v___x_84_; 
v___x_84_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(v_t_82_, v_backward_83_);
return v___x_84_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_backward_elim(lean_object* v_G_85_, lean_object* v_motive_86_, lean_object* v_a_87_, lean_object* v_a_88_, lean_object* v_t_89_, lean_object* v_h_90_, lean_object* v_backward_91_){
_start:
{
lean_object* v___x_92_; 
v___x_92_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_ctorElim___redArg(v_t_89_, v_backward_91_);
return v___x_92_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_backward_elim___boxed(lean_object* v_G_93_, lean_object* v_motive_94_, lean_object* v_a_95_, lean_object* v_a_96_, lean_object* v_t_97_, lean_object* v_h_98_, lean_object* v_backward_99_){
_start:
{
lean_object* v_res_100_; 
v_res_100_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_backward_elim(v_G_93_, v_motive_94_, v_a_95_, v_a_96_, v_t_97_, v_h_98_, v_backward_99_);
lean_dec(v_a_96_);
lean_dec(v_a_95_);
lean_dec_ref(v_G_93_);
return v_res_100_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList___redArg(lean_object* v_x_101_, lean_object* v_x_102_){
_start:
{
if (lean_obj_tag(v_x_102_) == 0)
{
lean_object* v___x_103_; lean_object* v___x_104_; 
lean_dec_ref(v_x_102_);
v___x_103_ = lean_box(0);
v___x_104_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_104_, 0, v_x_101_);
lean_ctor_set(v___x_104_, 1, v___x_103_);
return v___x_104_;
}
else
{
lean_object* v_w_105_; lean_object* v_tail_106_; lean_object* v___x_107_; lean_object* v___x_108_; 
v_w_105_ = lean_ctor_get(v_x_102_, 1);
lean_inc(v_w_105_);
v_tail_106_ = lean_ctor_get(v_x_102_, 3);
lean_inc_ref(v_tail_106_);
lean_dec_ref(v_x_102_);
v___x_107_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList___redArg(v_w_105_, v_tail_106_);
v___x_108_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_108_, 0, v_x_101_);
lean_ctor_set(v___x_108_, 1, v___x_107_);
return v___x_108_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList(lean_object* v_G_109_, lean_object* v_x_110_, lean_object* v_x_111_, lean_object* v_x_112_){
_start:
{
lean_object* v___x_113_; 
v___x_113_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList___redArg(v_x_110_, v_x_112_);
return v___x_113_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList___boxed(lean_object* v_G_114_, lean_object* v_x_115_, lean_object* v_x_116_, lean_object* v_x_117_){
_start:
{
lean_object* v_res_118_; 
v_res_118_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList(v_G_114_, v_x_115_, v_x_116_, v_x_117_);
lean_dec(v_x_116_);
lean_dec_ref(v_G_114_);
return v_res_118_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes___redArg(lean_object* v_u_119_, lean_object* v_t_120_){
_start:
{
lean_object* v___x_121_; lean_object* v___x_122_; 
v___x_121_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_toList___redArg(v_u_119_, v_t_120_);
v___x_122_ = lp_mathlib_List_pwFilter___at___00List_dedup___at___00Multiset_dedup___at___00Multiset_toFinset___at___00List_toFinset___at___00Finset_equivBitIndices_spec__0_spec__0_spec__1_spec__4_spec__5___redArg(v___x_121_);
return v___x_122_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes(lean_object* v_G_123_, lean_object* v_u_124_, lean_object* v_v_125_, lean_object* v_t_126_){
_start:
{
lean_object* v___x_127_; 
v___x_127_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes___redArg(v_u_124_, v_t_126_);
return v___x_127_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes___boxed(lean_object* v_G_128_, lean_object* v_u_129_, lean_object* v_v_130_, lean_object* v_t_131_){
_start:
{
lean_object* v_res_132_; 
v_res_132_ = lp_finiteQuerySandbox_FiniteQuerySandbox_Trail_nodes(v_G_128_, v_u_129_, v_v_130_, v_t_131_);
lean_dec(v_v_130_);
lean_dec_ref(v_G_128_);
return v_res_132_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx(uint8_t v_x_133_){
_start:
{
if (v_x_133_ == 0)
{
lean_object* v___x_134_; 
v___x_134_ = lean_unsigned_to_nat(0u);
return v___x_134_;
}
else
{
lean_object* v___x_135_; 
v___x_135_ = lean_unsigned_to_nat(1u);
return v___x_135_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx___boxed(lean_object* v_x_136_){
_start:
{
uint8_t v_x_boxed_137_; lean_object* v_res_138_; 
v_x_boxed_137_ = lean_unbox(v_x_136_);
v_res_138_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx(v_x_boxed_137_);
return v_res_138_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_toCtorIdx(uint8_t v_x_139_){
_start:
{
lean_object* v___x_140_; 
v___x_140_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx(v_x_139_);
return v___x_140_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_toCtorIdx___boxed(lean_object* v_x_141_){
_start:
{
uint8_t v_x_4__boxed_142_; lean_object* v_res_143_; 
v_x_4__boxed_142_ = lean_unbox(v_x_141_);
v_res_143_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_toCtorIdx(v_x_4__boxed_142_);
return v_res_143_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim___redArg(lean_object* v_k_144_){
_start:
{
lean_inc(v_k_144_);
return v_k_144_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim___redArg___boxed(lean_object* v_k_145_){
_start:
{
lean_object* v_res_146_; 
v_res_146_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim___redArg(v_k_145_);
lean_dec(v_k_145_);
return v_res_146_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim(lean_object* v_motive_147_, lean_object* v_ctorIdx_148_, uint8_t v_t_149_, lean_object* v_h_150_, lean_object* v_k_151_){
_start:
{
lean_inc(v_k_151_);
return v_k_151_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim___boxed(lean_object* v_motive_152_, lean_object* v_ctorIdx_153_, lean_object* v_t_154_, lean_object* v_h_155_, lean_object* v_k_156_){
_start:
{
uint8_t v_t_boxed_157_; lean_object* v_res_158_; 
v_t_boxed_157_ = lean_unbox(v_t_154_);
v_res_158_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorElim(v_motive_152_, v_ctorIdx_153_, v_t_boxed_157_, v_h_155_, v_k_156_);
lean_dec(v_k_156_);
lean_dec(v_ctorIdx_153_);
return v_res_158_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim___redArg(lean_object* v_into_159_){
_start:
{
lean_inc(v_into_159_);
return v_into_159_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim___redArg___boxed(lean_object* v_into_160_){
_start:
{
lean_object* v_res_161_; 
v_res_161_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim___redArg(v_into_160_);
lean_dec(v_into_160_);
return v_res_161_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim(lean_object* v_motive_162_, uint8_t v_t_163_, lean_object* v_h_164_, lean_object* v_into_165_){
_start:
{
lean_inc(v_into_165_);
return v_into_165_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim___boxed(lean_object* v_motive_166_, lean_object* v_t_167_, lean_object* v_h_168_, lean_object* v_into_169_){
_start:
{
uint8_t v_t_boxed_170_; lean_object* v_res_171_; 
v_t_boxed_170_ = lean_unbox(v_t_167_);
v_res_171_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_into_elim(v_motive_166_, v_t_boxed_170_, v_h_168_, v_into_169_);
lean_dec(v_into_169_);
return v_res_171_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim___redArg(lean_object* v_outOf_172_){
_start:
{
lean_inc(v_outOf_172_);
return v_outOf_172_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim___redArg___boxed(lean_object* v_outOf_173_){
_start:
{
lean_object* v_res_174_; 
v_res_174_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim___redArg(v_outOf_173_);
lean_dec(v_outOf_173_);
return v_res_174_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim(lean_object* v_motive_175_, uint8_t v_t_176_, lean_object* v_h_177_, lean_object* v_outOf_178_){
_start:
{
lean_inc(v_outOf_178_);
return v_outOf_178_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim___boxed(lean_object* v_motive_179_, lean_object* v_t_180_, lean_object* v_h_181_, lean_object* v_outOf_182_){
_start:
{
uint8_t v_t_boxed_183_; lean_object* v_res_184_; 
v_t_boxed_183_ = lean_unbox(v_t_180_);
v_res_184_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_outOf_elim(v_motive_179_, v_t_boxed_183_, v_h_181_, v_outOf_182_);
lean_dec(v_outOf_182_);
return v_res_184_;
}
}
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ofNat(lean_object* v_n_185_){
_start:
{
lean_object* v___x_186_; uint8_t v___x_187_; 
v___x_186_ = lean_unsigned_to_nat(0u);
v___x_187_ = lean_nat_dec_le(v_n_185_, v___x_186_);
if (v___x_187_ == 0)
{
uint8_t v___x_188_; 
v___x_188_ = 1;
return v___x_188_;
}
else
{
uint8_t v___x_189_; 
v___x_189_ = 0;
return v___x_189_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ofNat___boxed(lean_object* v_n_190_){
_start:
{
uint8_t v_res_191_; lean_object* v_r_192_; 
v_res_191_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ofNat(v_n_190_);
lean_dec(v_n_190_);
v_r_192_ = lean_box(v_res_191_);
return v_r_192_;
}
}
LEAN_EXPORT uint8_t lp_finiteQuerySandbox_FiniteQuerySandbox_instDecidableEqTrailDir(uint8_t v_x_193_, uint8_t v_y_194_){
_start:
{
lean_object* v___x_195_; lean_object* v___x_196_; uint8_t v___x_197_; 
v___x_195_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx(v_x_193_);
v___x_196_ = lp_finiteQuerySandbox_FiniteQuerySandbox_TrailDir_ctorIdx(v_y_194_);
v___x_197_ = lean_nat_dec_eq(v___x_195_, v___x_196_);
lean_dec(v___x_196_);
lean_dec(v___x_195_);
return v___x_197_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_instDecidableEqTrailDir___boxed(lean_object* v_x_198_, lean_object* v_y_199_){
_start:
{
uint8_t v_x_13__boxed_200_; uint8_t v_y_14__boxed_201_; uint8_t v_res_202_; lean_object* v_r_203_; 
v_x_13__boxed_200_ = lean_unbox(v_x_198_);
v_y_14__boxed_201_ = lean_unbox(v_y_199_);
v_res_202_ = lp_finiteQuerySandbox_FiniteQuerySandbox_instDecidableEqTrailDir(v_x_13__boxed_200_, v_y_14__boxed_201_);
v_r_203_ = lean_box(v_res_202_);
return v_r_203_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter___redArg(uint8_t v_x_204_, lean_object* v_h__1_205_, lean_object* v_h__2_206_){
_start:
{
if (v_x_204_ == 0)
{
lean_object* v___x_207_; lean_object* v___x_208_; 
lean_dec(v_h__2_206_);
v___x_207_ = lean_box(0);
v___x_208_ = lean_apply_1(v_h__1_205_, v___x_207_);
return v___x_208_;
}
else
{
lean_object* v___x_209_; lean_object* v___x_210_; 
lean_dec(v_h__1_205_);
v___x_209_ = lean_box(0);
v___x_210_ = lean_apply_1(v_h__2_206_, v___x_209_);
return v___x_210_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter___redArg___boxed(lean_object* v_x_211_, lean_object* v_h__1_212_, lean_object* v_h__2_213_){
_start:
{
uint8_t v_x_26__boxed_214_; lean_object* v_res_215_; 
v_x_26__boxed_214_ = lean_unbox(v_x_211_);
v_res_215_ = lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter___redArg(v_x_26__boxed_214_, v_h__1_212_, v_h__2_213_);
return v_res_215_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter(lean_object* v_motive_216_, uint8_t v_x_217_, lean_object* v_h__1_218_, lean_object* v_h__2_219_){
_start:
{
if (v_x_217_ == 0)
{
lean_object* v___x_220_; lean_object* v___x_221_; 
lean_dec(v_h__2_219_);
v___x_220_ = lean_box(0);
v___x_221_ = lean_apply_1(v_h__1_218_, v___x_220_);
return v___x_221_;
}
else
{
lean_object* v___x_222_; lean_object* v___x_223_; 
lean_dec(v_h__1_218_);
v___x_222_ = lean_box(0);
v___x_223_ = lean_apply_1(v_h__2_219_, v___x_222_);
return v___x_223_;
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter___boxed(lean_object* v_motive_224_, lean_object* v_x_225_, lean_object* v_h__1_226_, lean_object* v_h__2_227_){
_start:
{
uint8_t v_x_37__boxed_228_; lean_object* v_res_229_; 
v_x_37__boxed_228_ = lean_unbox(v_x_225_);
v_res_229_ = lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_TrailDir_edgeIntoCurrent_match__1_splitter(v_motive_224_, v_x_37__boxed_228_, v_h__1_226_, v_h__2_227_);
return v_res_229_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_Trail_toList_match__1_splitter___redArg(lean_object* v_x_230_, lean_object* v_x_231_, lean_object* v_x_232_, lean_object* v_h__1_233_, lean_object* v_h__2_234_, lean_object* v_h__3_235_){
_start:
{
switch(lean_obj_tag(v_x_232_))
{
case 0:
{
lean_object* v___x_236_; 
lean_dec_ref(v_x_232_);
lean_dec(v_h__3_235_);
lean_dec(v_h__2_234_);
lean_dec(v_x_231_);
v___x_236_ = lean_apply_1(v_h__1_233_, v_x_230_);
return v___x_236_;
}
case 1:
{
lean_object* v_w_237_; lean_object* v_tail_238_; lean_object* v___x_239_; 
lean_dec(v_h__3_235_);
lean_dec(v_h__1_233_);
v_w_237_ = lean_ctor_get(v_x_232_, 1);
lean_inc(v_w_237_);
v_tail_238_ = lean_ctor_get(v_x_232_, 3);
lean_inc_ref(v_tail_238_);
lean_dec_ref(v_x_232_);
v___x_239_ = lean_apply_5(v_h__2_234_, v_x_230_, v_x_231_, v_w_237_, lean_box(0), v_tail_238_);
return v___x_239_;
}
default: 
{
lean_object* v_w_240_; lean_object* v_tail_241_; lean_object* v___x_242_; 
lean_dec(v_h__2_234_);
lean_dec(v_h__1_233_);
v_w_240_ = lean_ctor_get(v_x_232_, 1);
lean_inc(v_w_240_);
v_tail_241_ = lean_ctor_get(v_x_232_, 3);
lean_inc_ref(v_tail_241_);
lean_dec_ref(v_x_232_);
v___x_242_ = lean_apply_5(v_h__3_235_, v_x_230_, v_x_231_, v_w_240_, lean_box(0), v_tail_241_);
return v___x_242_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_Trail_toList_match__1_splitter(lean_object* v_G_243_, lean_object* v_motive_244_, lean_object* v_x_245_, lean_object* v_x_246_, lean_object* v_x_247_, lean_object* v_h__1_248_, lean_object* v_h__2_249_, lean_object* v_h__3_250_){
_start:
{
switch(lean_obj_tag(v_x_247_))
{
case 0:
{
lean_object* v___x_251_; 
lean_dec_ref(v_x_247_);
lean_dec(v_h__3_250_);
lean_dec(v_h__2_249_);
lean_dec(v_x_246_);
v___x_251_ = lean_apply_1(v_h__1_248_, v_x_245_);
return v___x_251_;
}
case 1:
{
lean_object* v_w_252_; lean_object* v_tail_253_; lean_object* v___x_254_; 
lean_dec(v_h__3_250_);
lean_dec(v_h__1_248_);
v_w_252_ = lean_ctor_get(v_x_247_, 1);
lean_inc(v_w_252_);
v_tail_253_ = lean_ctor_get(v_x_247_, 3);
lean_inc_ref(v_tail_253_);
lean_dec_ref(v_x_247_);
v___x_254_ = lean_apply_5(v_h__2_249_, v_x_245_, v_x_246_, v_w_252_, lean_box(0), v_tail_253_);
return v___x_254_;
}
default: 
{
lean_object* v_w_255_; lean_object* v_tail_256_; lean_object* v___x_257_; 
lean_dec(v_h__2_249_);
lean_dec(v_h__1_248_);
v_w_255_ = lean_ctor_get(v_x_247_, 1);
lean_inc(v_w_255_);
v_tail_256_ = lean_ctor_get(v_x_247_, 3);
lean_inc_ref(v_tail_256_);
lean_dec_ref(v_x_247_);
v___x_257_ = lean_apply_5(v_h__3_250_, v_x_245_, v_x_246_, v_w_255_, lean_box(0), v_tail_256_);
return v___x_257_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_Trail_toList_match__1_splitter___boxed(lean_object* v_G_258_, lean_object* v_motive_259_, lean_object* v_x_260_, lean_object* v_x_261_, lean_object* v_x_262_, lean_object* v_h__1_263_, lean_object* v_h__2_264_, lean_object* v_h__3_265_){
_start:
{
lean_object* v_res_266_; 
v_res_266_ = lp_finiteQuerySandbox___private_FiniteQuerySandbox_DAG_Trail_0__FiniteQuerySandbox_Trail_toList_match__1_splitter(v_G_258_, v_motive_259_, v_x_260_, v_x_261_, v_x_262_, v_h__1_263_, v_h__2_264_, v_h__3_265_);
lean_dec_ref(v_G_258_);
return v_res_266_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Ancestry(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Trail(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_DAG_Ancestry(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
