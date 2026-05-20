// Lean compiler output
// Module: FiniteQuerySandbox.DSepCMIBridge
// Imports: public import Init public import FiniteQuerySandbox.MarkovGenerator
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
extern lean_object* lp_mathlib_Real_instAddCommMonoid;
lean_object* lp_mathlib_Finset_sum___redArg(lean_object*, lean_object*, lean_object*);
lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_equivACB___lam__0(lean_object*);
static const lean_closure_object lp_finiteQuerySandbox_InfoTheory_equivACB___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_finiteQuerySandbox_InfoTheory_equivACB___lam__0, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_finiteQuerySandbox_InfoTheory_equivACB___closed__0 = (const lean_object*)&lp_finiteQuerySandbox_InfoTheory_equivACB___closed__0_value;
static const lean_ctor_object lp_finiteQuerySandbox_InfoTheory_equivACB___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)&lp_finiteQuerySandbox_InfoTheory_equivACB___closed__0_value),((lean_object*)&lp_finiteQuerySandbox_InfoTheory_equivACB___closed__0_value)}};
static const lean_object* lp_finiteQuerySandbox_InfoTheory_equivACB___closed__1 = (const lean_object*)&lp_finiteQuerySandbox_InfoTheory_equivACB___closed__1_value;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_equivACB(lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg___closed__0;
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_pmfACB(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_pmfACB___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__0(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_equivACB___lam__0(lean_object* v_x_1_){
_start:
{
lean_object* v_snd_2_; lean_object* v_fst_3_; lean_object* v___x_5_; uint8_t v_isShared_6_; uint8_t v_isSharedCheck_19_; 
v_snd_2_ = lean_ctor_get(v_x_1_, 1);
v_fst_3_ = lean_ctor_get(v_x_1_, 0);
v_isSharedCheck_19_ = !lean_is_exclusive(v_x_1_);
if (v_isSharedCheck_19_ == 0)
{
v___x_5_ = v_x_1_;
v_isShared_6_ = v_isSharedCheck_19_;
goto v_resetjp_4_;
}
else
{
lean_inc(v_snd_2_);
lean_inc(v_fst_3_);
lean_dec(v_x_1_);
v___x_5_ = lean_box(0);
v_isShared_6_ = v_isSharedCheck_19_;
goto v_resetjp_4_;
}
v_resetjp_4_:
{
lean_object* v_fst_7_; lean_object* v_snd_8_; lean_object* v___x_10_; uint8_t v_isShared_11_; uint8_t v_isSharedCheck_18_; 
v_fst_7_ = lean_ctor_get(v_snd_2_, 0);
v_snd_8_ = lean_ctor_get(v_snd_2_, 1);
v_isSharedCheck_18_ = !lean_is_exclusive(v_snd_2_);
if (v_isSharedCheck_18_ == 0)
{
v___x_10_ = v_snd_2_;
v_isShared_11_ = v_isSharedCheck_18_;
goto v_resetjp_9_;
}
else
{
lean_inc(v_snd_8_);
lean_inc(v_fst_7_);
lean_dec(v_snd_2_);
v___x_10_ = lean_box(0);
v_isShared_11_ = v_isSharedCheck_18_;
goto v_resetjp_9_;
}
v_resetjp_9_:
{
lean_object* v___x_13_; 
if (v_isShared_11_ == 0)
{
lean_ctor_set(v___x_10_, 1, v_fst_7_);
lean_ctor_set(v___x_10_, 0, v_snd_8_);
v___x_13_ = v___x_10_;
goto v_reusejp_12_;
}
else
{
lean_object* v_reuseFailAlloc_17_; 
v_reuseFailAlloc_17_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_17_, 0, v_snd_8_);
lean_ctor_set(v_reuseFailAlloc_17_, 1, v_fst_7_);
v___x_13_ = v_reuseFailAlloc_17_;
goto v_reusejp_12_;
}
v_reusejp_12_:
{
lean_object* v___x_15_; 
if (v_isShared_6_ == 0)
{
lean_ctor_set(v___x_5_, 1, v___x_13_);
v___x_15_ = v___x_5_;
goto v_reusejp_14_;
}
else
{
lean_object* v_reuseFailAlloc_16_; 
v_reuseFailAlloc_16_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_16_, 0, v_fst_3_);
lean_ctor_set(v_reuseFailAlloc_16_, 1, v___x_13_);
v___x_15_ = v_reuseFailAlloc_16_;
goto v_reusejp_14_;
}
v_reusejp_14_:
{
return v___x_15_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_equivACB(lean_object* v_00_u03b1_23_, lean_object* v_00_u03b2_24_, lean_object* v_00_u03b3_25_){
_start:
{
lean_object* v___x_26_; 
v___x_26_ = ((lean_object*)(lp_finiteQuerySandbox_InfoTheory_equivACB___closed__1));
return v___x_26_;
}
}
static lean_object* _init_lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg___closed__0(void){
_start:
{
lean_object* v___x_27_; 
v___x_27_ = lp_finiteQuerySandbox_InfoTheory_equivACB(lean_box(0), lean_box(0), lean_box(0));
return v___x_27_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg(lean_object* v_P_28_){
_start:
{
lean_object* v___x_29_; lean_object* v___f_30_; 
v___x_29_ = lean_obj_once(&lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg___closed__0, &lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg___closed__0_once, _init_lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg___closed__0);
v___f_30_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_FinitePMF_comapEquiv___redArg___lam__0), 3, 2);
lean_closure_set(v___f_30_, 0, v___x_29_);
lean_closure_set(v___f_30_, 1, v_P_28_);
return v___f_30_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_pmfACB(lean_object* v_00_u03b1_31_, lean_object* v_00_u03b2_32_, lean_object* v_00_u03b3_33_, lean_object* v_inst_34_, lean_object* v_inst_35_, lean_object* v_inst_36_, lean_object* v_inst_37_, lean_object* v_inst_38_, lean_object* v_inst_39_, lean_object* v_P_40_){
_start:
{
lean_object* v___x_41_; 
v___x_41_ = lp_finiteQuerySandbox_InfoTheory_pmfACB___redArg(v_P_40_);
return v___x_41_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_pmfACB___boxed(lean_object* v_00_u03b1_42_, lean_object* v_00_u03b2_43_, lean_object* v_00_u03b3_44_, lean_object* v_inst_45_, lean_object* v_inst_46_, lean_object* v_inst_47_, lean_object* v_inst_48_, lean_object* v_inst_49_, lean_object* v_inst_50_, lean_object* v_P_51_){
_start:
{
lean_object* v_res_52_; 
v_res_52_ = lp_finiteQuerySandbox_InfoTheory_pmfACB(v_00_u03b1_42_, v_00_u03b2_43_, v_00_u03b3_44_, v_inst_45_, v_inst_46_, v_inst_47_, v_inst_48_, v_inst_49_, v_inst_50_, v_P_51_);
lean_dec_ref(v_inst_50_);
lean_dec_ref(v_inst_49_);
lean_dec_ref(v_inst_48_);
lean_dec(v_inst_47_);
lean_dec(v_inst_46_);
lean_dec(v_inst_45_);
return v_res_52_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__0(lean_object* v_b_53_, lean_object* v_a_54_, lean_object* v_P_55_, lean_object* v_c_56_){
_start:
{
lean_object* v___x_57_; lean_object* v___x_58_; lean_object* v___x_59_; 
v___x_57_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_57_, 0, v_b_53_);
lean_ctor_set(v___x_57_, 1, v_c_56_);
v___x_58_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_58_, 0, v_a_54_);
lean_ctor_set(v___x_58_, 1, v___x_57_);
v___x_59_ = lean_apply_1(v_P_55_, v___x_58_);
return v___x_59_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__1(lean_object* v_b_60_, lean_object* v_P_61_, lean_object* v___x_62_, lean_object* v_inst_63_, lean_object* v_a_64_){
_start:
{
lean_object* v___f_65_; lean_object* v___x_66_; 
v___f_65_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__0), 4, 3);
lean_closure_set(v___f_65_, 0, v_b_60_);
lean_closure_set(v___f_65_, 1, v_a_64_);
lean_closure_set(v___f_65_, 2, v_P_61_);
v___x_66_ = lp_mathlib_Finset_sum___redArg(v___x_62_, v_inst_63_, v___f_65_);
return v___x_66_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__1___boxed(lean_object* v_b_67_, lean_object* v_P_68_, lean_object* v___x_69_, lean_object* v_inst_70_, lean_object* v_a_71_){
_start:
{
lean_object* v_res_72_; 
v_res_72_ = lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__1(v_b_67_, v_P_68_, v___x_69_, v_inst_70_, v_a_71_);
lean_dec_ref(v___x_69_);
return v_res_72_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___redArg(lean_object* v_inst_73_, lean_object* v_inst_74_, lean_object* v_P_75_, lean_object* v_b_76_){
_start:
{
lean_object* v___x_77_; lean_object* v___f_78_; lean_object* v___x_79_; 
v___x_77_ = lp_mathlib_Real_instAddCommMonoid;
v___f_78_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_InfoTheory_marginalB___redArg___lam__1___boxed), 5, 4);
lean_closure_set(v___f_78_, 0, v_b_76_);
lean_closure_set(v___f_78_, 1, v_P_75_);
lean_closure_set(v___f_78_, 2, v___x_77_);
lean_closure_set(v___f_78_, 3, v_inst_74_);
v___x_79_ = lp_mathlib_Finset_sum___redArg(v___x_77_, v_inst_73_, v___f_78_);
return v___x_79_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB(lean_object* v_00_u03b1_80_, lean_object* v_00_u03b2_81_, lean_object* v_00_u03b3_82_, lean_object* v_inst_83_, lean_object* v_inst_84_, lean_object* v_inst_85_, lean_object* v_inst_86_, lean_object* v_inst_87_, lean_object* v_inst_88_, lean_object* v_P_89_, lean_object* v_b_90_){
_start:
{
lean_object* v___x_91_; 
v___x_91_ = lp_finiteQuerySandbox_InfoTheory_marginalB___redArg(v_inst_83_, v_inst_85_, v_P_89_, v_b_90_);
return v___x_91_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalB___boxed(lean_object* v_00_u03b1_92_, lean_object* v_00_u03b2_93_, lean_object* v_00_u03b3_94_, lean_object* v_inst_95_, lean_object* v_inst_96_, lean_object* v_inst_97_, lean_object* v_inst_98_, lean_object* v_inst_99_, lean_object* v_inst_100_, lean_object* v_P_101_, lean_object* v_b_102_){
_start:
{
lean_object* v_res_103_; 
v_res_103_ = lp_finiteQuerySandbox_InfoTheory_marginalB(v_00_u03b1_92_, v_00_u03b2_93_, v_00_u03b3_94_, v_inst_95_, v_inst_96_, v_inst_97_, v_inst_98_, v_inst_99_, v_inst_100_, v_P_101_, v_b_102_);
lean_dec_ref(v_inst_100_);
lean_dec_ref(v_inst_99_);
lean_dec_ref(v_inst_98_);
lean_dec(v_inst_96_);
return v_res_103_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB___redArg___lam__0(lean_object* v_ab_104_, lean_object* v_P_105_, lean_object* v_c_106_){
_start:
{
lean_object* v_fst_107_; lean_object* v_snd_108_; lean_object* v___x_110_; uint8_t v_isShared_111_; uint8_t v_isSharedCheck_117_; 
v_fst_107_ = lean_ctor_get(v_ab_104_, 0);
v_snd_108_ = lean_ctor_get(v_ab_104_, 1);
v_isSharedCheck_117_ = !lean_is_exclusive(v_ab_104_);
if (v_isSharedCheck_117_ == 0)
{
v___x_110_ = v_ab_104_;
v_isShared_111_ = v_isSharedCheck_117_;
goto v_resetjp_109_;
}
else
{
lean_inc(v_snd_108_);
lean_inc(v_fst_107_);
lean_dec(v_ab_104_);
v___x_110_ = lean_box(0);
v_isShared_111_ = v_isSharedCheck_117_;
goto v_resetjp_109_;
}
v_resetjp_109_:
{
lean_object* v___x_113_; 
if (v_isShared_111_ == 0)
{
lean_ctor_set(v___x_110_, 1, v_c_106_);
lean_ctor_set(v___x_110_, 0, v_snd_108_);
v___x_113_ = v___x_110_;
goto v_reusejp_112_;
}
else
{
lean_object* v_reuseFailAlloc_116_; 
v_reuseFailAlloc_116_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_116_, 0, v_snd_108_);
lean_ctor_set(v_reuseFailAlloc_116_, 1, v_c_106_);
v___x_113_ = v_reuseFailAlloc_116_;
goto v_reusejp_112_;
}
v_reusejp_112_:
{
lean_object* v___x_114_; lean_object* v___x_115_; 
v___x_114_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_114_, 0, v_fst_107_);
lean_ctor_set(v___x_114_, 1, v___x_113_);
v___x_115_ = lean_apply_1(v_P_105_, v___x_114_);
return v___x_115_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB___redArg(lean_object* v_inst_118_, lean_object* v_P_119_, lean_object* v_ab_120_){
_start:
{
lean_object* v___f_121_; lean_object* v___x_122_; lean_object* v___x_123_; 
v___f_121_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_InfoTheory_marginalAB___redArg___lam__0), 3, 2);
lean_closure_set(v___f_121_, 0, v_ab_120_);
lean_closure_set(v___f_121_, 1, v_P_119_);
v___x_122_ = lp_mathlib_Real_instAddCommMonoid;
v___x_123_ = lp_mathlib_Finset_sum___redArg(v___x_122_, v_inst_118_, v___f_121_);
return v___x_123_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB(lean_object* v_00_u03b1_124_, lean_object* v_00_u03b2_125_, lean_object* v_00_u03b3_126_, lean_object* v_inst_127_, lean_object* v_inst_128_, lean_object* v_inst_129_, lean_object* v_inst_130_, lean_object* v_inst_131_, lean_object* v_inst_132_, lean_object* v_P_133_, lean_object* v_ab_134_){
_start:
{
lean_object* v___x_135_; 
v___x_135_ = lp_finiteQuerySandbox_InfoTheory_marginalAB___redArg(v_inst_129_, v_P_133_, v_ab_134_);
return v___x_135_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalAB___boxed(lean_object* v_00_u03b1_136_, lean_object* v_00_u03b2_137_, lean_object* v_00_u03b3_138_, lean_object* v_inst_139_, lean_object* v_inst_140_, lean_object* v_inst_141_, lean_object* v_inst_142_, lean_object* v_inst_143_, lean_object* v_inst_144_, lean_object* v_P_145_, lean_object* v_ab_146_){
_start:
{
lean_object* v_res_147_; 
v_res_147_ = lp_finiteQuerySandbox_InfoTheory_marginalAB(v_00_u03b1_136_, v_00_u03b2_137_, v_00_u03b3_138_, v_inst_139_, v_inst_140_, v_inst_141_, v_inst_142_, v_inst_143_, v_inst_144_, v_P_145_, v_ab_146_);
lean_dec_ref(v_inst_144_);
lean_dec_ref(v_inst_143_);
lean_dec_ref(v_inst_142_);
lean_dec(v_inst_140_);
lean_dec(v_inst_139_);
return v_res_147_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC___redArg___lam__0(lean_object* v_bc_148_, lean_object* v_P_149_, lean_object* v_a_150_){
_start:
{
lean_object* v_fst_151_; lean_object* v_snd_152_; lean_object* v___x_154_; uint8_t v_isShared_155_; uint8_t v_isSharedCheck_161_; 
v_fst_151_ = lean_ctor_get(v_bc_148_, 0);
v_snd_152_ = lean_ctor_get(v_bc_148_, 1);
v_isSharedCheck_161_ = !lean_is_exclusive(v_bc_148_);
if (v_isSharedCheck_161_ == 0)
{
v___x_154_ = v_bc_148_;
v_isShared_155_ = v_isSharedCheck_161_;
goto v_resetjp_153_;
}
else
{
lean_inc(v_snd_152_);
lean_inc(v_fst_151_);
lean_dec(v_bc_148_);
v___x_154_ = lean_box(0);
v_isShared_155_ = v_isSharedCheck_161_;
goto v_resetjp_153_;
}
v_resetjp_153_:
{
lean_object* v___x_157_; 
if (v_isShared_155_ == 0)
{
v___x_157_ = v___x_154_;
goto v_reusejp_156_;
}
else
{
lean_object* v_reuseFailAlloc_160_; 
v_reuseFailAlloc_160_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_160_, 0, v_fst_151_);
lean_ctor_set(v_reuseFailAlloc_160_, 1, v_snd_152_);
v___x_157_ = v_reuseFailAlloc_160_;
goto v_reusejp_156_;
}
v_reusejp_156_:
{
lean_object* v___x_158_; lean_object* v___x_159_; 
v___x_158_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_158_, 0, v_a_150_);
lean_ctor_set(v___x_158_, 1, v___x_157_);
v___x_159_ = lean_apply_1(v_P_149_, v___x_158_);
return v___x_159_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC___redArg(lean_object* v_inst_162_, lean_object* v_P_163_, lean_object* v_bc_164_){
_start:
{
lean_object* v___f_165_; lean_object* v___x_166_; lean_object* v___x_167_; 
v___f_165_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_InfoTheory_marginalBC___redArg___lam__0), 3, 2);
lean_closure_set(v___f_165_, 0, v_bc_164_);
lean_closure_set(v___f_165_, 1, v_P_163_);
v___x_166_ = lp_mathlib_Real_instAddCommMonoid;
v___x_167_ = lp_mathlib_Finset_sum___redArg(v___x_166_, v_inst_162_, v___f_165_);
return v___x_167_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC(lean_object* v_00_u03b1_168_, lean_object* v_00_u03b2_169_, lean_object* v_00_u03b3_170_, lean_object* v_inst_171_, lean_object* v_inst_172_, lean_object* v_inst_173_, lean_object* v_inst_174_, lean_object* v_inst_175_, lean_object* v_inst_176_, lean_object* v_P_177_, lean_object* v_bc_178_){
_start:
{
lean_object* v___x_179_; 
v___x_179_ = lp_finiteQuerySandbox_InfoTheory_marginalBC___redArg(v_inst_171_, v_P_177_, v_bc_178_);
return v___x_179_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_InfoTheory_marginalBC___boxed(lean_object* v_00_u03b1_180_, lean_object* v_00_u03b2_181_, lean_object* v_00_u03b3_182_, lean_object* v_inst_183_, lean_object* v_inst_184_, lean_object* v_inst_185_, lean_object* v_inst_186_, lean_object* v_inst_187_, lean_object* v_inst_188_, lean_object* v_P_189_, lean_object* v_bc_190_){
_start:
{
lean_object* v_res_191_; 
v_res_191_ = lp_finiteQuerySandbox_InfoTheory_marginalBC(v_00_u03b1_180_, v_00_u03b2_181_, v_00_u03b3_182_, v_inst_183_, v_inst_184_, v_inst_185_, v_inst_186_, v_inst_187_, v_inst_188_, v_P_189_, v_bc_190_);
lean_dec_ref(v_inst_188_);
lean_dec_ref(v_inst_187_);
lean_dec_ref(v_inst_186_);
lean_dec(v_inst_185_);
lean_dec(v_inst_184_);
return v_res_191_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_MarkovGenerator(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DSepCMIBridge(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_MarkovGenerator(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
