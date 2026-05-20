// Lean compiler output
// Module: FiniteQuerySandbox.DualCertificate
// Imports: public import Init public import FiniteQuerySandbox.InfoTheory
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
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__0(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__0(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___redArg___lam__0(lean_object* v_st_1_, lean_object* v_P_2_, lean_object* v_m_3_){
_start:
{
lean_object* v_fst_4_; lean_object* v_snd_5_; lean_object* v___x_7_; uint8_t v_isShared_8_; uint8_t v_isSharedCheck_14_; 
v_fst_4_ = lean_ctor_get(v_st_1_, 0);
v_snd_5_ = lean_ctor_get(v_st_1_, 1);
v_isSharedCheck_14_ = !lean_is_exclusive(v_st_1_);
if (v_isSharedCheck_14_ == 0)
{
v___x_7_ = v_st_1_;
v_isShared_8_ = v_isSharedCheck_14_;
goto v_resetjp_6_;
}
else
{
lean_inc(v_snd_5_);
lean_inc(v_fst_4_);
lean_dec(v_st_1_);
v___x_7_ = lean_box(0);
v_isShared_8_ = v_isSharedCheck_14_;
goto v_resetjp_6_;
}
v_resetjp_6_:
{
lean_object* v___x_10_; 
if (v_isShared_8_ == 0)
{
lean_ctor_set(v___x_7_, 1, v_m_3_);
lean_ctor_set(v___x_7_, 0, v_snd_5_);
v___x_10_ = v___x_7_;
goto v_reusejp_9_;
}
else
{
lean_object* v_reuseFailAlloc_13_; 
v_reuseFailAlloc_13_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_13_, 0, v_snd_5_);
lean_ctor_set(v_reuseFailAlloc_13_, 1, v_m_3_);
v___x_10_ = v_reuseFailAlloc_13_;
goto v_reusejp_9_;
}
v_reusejp_9_:
{
lean_object* v___x_11_; lean_object* v___x_12_; 
v___x_11_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_11_, 0, v_fst_4_);
lean_ctor_set(v___x_11_, 1, v___x_10_);
v___x_12_ = lean_apply_1(v_P_2_, v___x_11_);
return v___x_12_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___redArg(lean_object* v_inst_15_, lean_object* v_P_16_, lean_object* v_st_17_){
_start:
{
lean_object* v___f_18_; lean_object* v___x_19_; lean_object* v___x_20_; 
v___f_18_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___redArg___lam__0), 3, 2);
lean_closure_set(v___f_18_, 0, v_st_17_);
lean_closure_set(v___f_18_, 1, v_P_16_);
v___x_19_ = lp_mathlib_Real_instAddCommMonoid;
v___x_20_ = lp_mathlib_Finset_sum___redArg(v___x_19_, v_inst_15_, v___f_18_);
return v___x_20_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass(lean_object* v_State_21_, lean_object* v_VisibleTrace_22_, lean_object* v_MissingTrace_23_, lean_object* v_inst_24_, lean_object* v_inst_25_, lean_object* v_inst_26_, lean_object* v_inst_27_, lean_object* v_inst_28_, lean_object* v_inst_29_, lean_object* v_P_30_, lean_object* v_st_31_){
_start:
{
lean_object* v___x_32_; 
v___x_32_ = lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___redArg(v_inst_26_, v_P_30_, v_st_31_);
return v___x_32_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass___boxed(lean_object* v_State_33_, lean_object* v_VisibleTrace_34_, lean_object* v_MissingTrace_35_, lean_object* v_inst_36_, lean_object* v_inst_37_, lean_object* v_inst_38_, lean_object* v_inst_39_, lean_object* v_inst_40_, lean_object* v_inst_41_, lean_object* v_P_42_, lean_object* v_st_43_){
_start:
{
lean_object* v_res_44_; 
v_res_44_ = lp_finiteQuerySandbox_FiniteQuerySandbox_stateVisibleMass(v_State_33_, v_VisibleTrace_34_, v_MissingTrace_35_, v_inst_36_, v_inst_37_, v_inst_38_, v_inst_39_, v_inst_40_, v_inst_41_, v_P_42_, v_st_43_);
lean_dec_ref(v_inst_41_);
lean_dec_ref(v_inst_40_);
lean_dec_ref(v_inst_39_);
lean_dec(v_inst_37_);
lean_dec(v_inst_36_);
return v_res_44_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__0(lean_object* v_t_45_, lean_object* v_s_46_, lean_object* v_P_47_, lean_object* v_m_48_){
_start:
{
lean_object* v___x_49_; lean_object* v___x_50_; lean_object* v___x_51_; 
v___x_49_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_49_, 0, v_t_45_);
lean_ctor_set(v___x_49_, 1, v_m_48_);
v___x_50_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_50_, 0, v_s_46_);
lean_ctor_set(v___x_50_, 1, v___x_49_);
v___x_51_ = lean_apply_1(v_P_47_, v___x_50_);
return v___x_51_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__1(lean_object* v_t_52_, lean_object* v_P_53_, lean_object* v___x_54_, lean_object* v_inst_55_, lean_object* v_s_56_){
_start:
{
lean_object* v___f_57_; lean_object* v___x_58_; 
v___f_57_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__0), 4, 3);
lean_closure_set(v___f_57_, 0, v_t_52_);
lean_closure_set(v___f_57_, 1, v_s_56_);
lean_closure_set(v___f_57_, 2, v_P_53_);
v___x_58_ = lp_mathlib_Finset_sum___redArg(v___x_54_, v_inst_55_, v___f_57_);
return v___x_58_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__1___boxed(lean_object* v_t_59_, lean_object* v_P_60_, lean_object* v___x_61_, lean_object* v_inst_62_, lean_object* v_s_63_){
_start:
{
lean_object* v_res_64_; 
v_res_64_ = lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__1(v_t_59_, v_P_60_, v___x_61_, v_inst_62_, v_s_63_);
lean_dec_ref(v___x_61_);
return v_res_64_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg(lean_object* v_inst_65_, lean_object* v_inst_66_, lean_object* v_P_67_, lean_object* v_t_68_){
_start:
{
lean_object* v___x_69_; lean_object* v___f_70_; lean_object* v___x_71_; 
v___x_69_ = lp_mathlib_Real_instAddCommMonoid;
v___f_70_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg___lam__1___boxed), 5, 4);
lean_closure_set(v___f_70_, 0, v_t_68_);
lean_closure_set(v___f_70_, 1, v_P_67_);
lean_closure_set(v___f_70_, 2, v___x_69_);
lean_closure_set(v___f_70_, 3, v_inst_66_);
v___x_71_ = lp_mathlib_Finset_sum___redArg(v___x_69_, v_inst_65_, v___f_70_);
return v___x_71_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass(lean_object* v_State_72_, lean_object* v_VisibleTrace_73_, lean_object* v_MissingTrace_74_, lean_object* v_inst_75_, lean_object* v_inst_76_, lean_object* v_inst_77_, lean_object* v_inst_78_, lean_object* v_inst_79_, lean_object* v_inst_80_, lean_object* v_P_81_, lean_object* v_t_82_){
_start:
{
lean_object* v___x_83_; 
v___x_83_ = lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___redArg(v_inst_75_, v_inst_77_, v_P_81_, v_t_82_);
return v___x_83_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass___boxed(lean_object* v_State_84_, lean_object* v_VisibleTrace_85_, lean_object* v_MissingTrace_86_, lean_object* v_inst_87_, lean_object* v_inst_88_, lean_object* v_inst_89_, lean_object* v_inst_90_, lean_object* v_inst_91_, lean_object* v_inst_92_, lean_object* v_P_93_, lean_object* v_t_94_){
_start:
{
lean_object* v_res_95_; 
v_res_95_ = lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMass(v_State_84_, v_VisibleTrace_85_, v_MissingTrace_86_, v_inst_87_, v_inst_88_, v_inst_89_, v_inst_90_, v_inst_91_, v_inst_92_, v_P_93_, v_t_94_);
lean_dec_ref(v_inst_92_);
lean_dec_ref(v_inst_91_);
lean_dec_ref(v_inst_90_);
lean_dec(v_inst_88_);
return v_res_95_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___redArg___lam__0(lean_object* v_tm_96_, lean_object* v_P_97_, lean_object* v_s_98_){
_start:
{
lean_object* v_fst_99_; lean_object* v_snd_100_; lean_object* v___x_102_; uint8_t v_isShared_103_; uint8_t v_isSharedCheck_109_; 
v_fst_99_ = lean_ctor_get(v_tm_96_, 0);
v_snd_100_ = lean_ctor_get(v_tm_96_, 1);
v_isSharedCheck_109_ = !lean_is_exclusive(v_tm_96_);
if (v_isSharedCheck_109_ == 0)
{
v___x_102_ = v_tm_96_;
v_isShared_103_ = v_isSharedCheck_109_;
goto v_resetjp_101_;
}
else
{
lean_inc(v_snd_100_);
lean_inc(v_fst_99_);
lean_dec(v_tm_96_);
v___x_102_ = lean_box(0);
v_isShared_103_ = v_isSharedCheck_109_;
goto v_resetjp_101_;
}
v_resetjp_101_:
{
lean_object* v___x_105_; 
if (v_isShared_103_ == 0)
{
v___x_105_ = v___x_102_;
goto v_reusejp_104_;
}
else
{
lean_object* v_reuseFailAlloc_108_; 
v_reuseFailAlloc_108_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_108_, 0, v_fst_99_);
lean_ctor_set(v_reuseFailAlloc_108_, 1, v_snd_100_);
v___x_105_ = v_reuseFailAlloc_108_;
goto v_reusejp_104_;
}
v_reusejp_104_:
{
lean_object* v___x_106_; lean_object* v___x_107_; 
v___x_106_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_106_, 0, v_s_98_);
lean_ctor_set(v___x_106_, 1, v___x_105_);
v___x_107_ = lean_apply_1(v_P_97_, v___x_106_);
return v___x_107_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___redArg(lean_object* v_inst_110_, lean_object* v_P_111_, lean_object* v_tm_112_){
_start:
{
lean_object* v___f_113_; lean_object* v___x_114_; lean_object* v___x_115_; 
v___f_113_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___redArg___lam__0), 3, 2);
lean_closure_set(v___f_113_, 0, v_tm_112_);
lean_closure_set(v___f_113_, 1, v_P_111_);
v___x_114_ = lp_mathlib_Real_instAddCommMonoid;
v___x_115_ = lp_mathlib_Finset_sum___redArg(v___x_114_, v_inst_110_, v___f_113_);
return v___x_115_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass(lean_object* v_State_116_, lean_object* v_VisibleTrace_117_, lean_object* v_MissingTrace_118_, lean_object* v_inst_119_, lean_object* v_inst_120_, lean_object* v_inst_121_, lean_object* v_inst_122_, lean_object* v_inst_123_, lean_object* v_inst_124_, lean_object* v_P_125_, lean_object* v_tm_126_){
_start:
{
lean_object* v___x_127_; 
v___x_127_ = lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___redArg(v_inst_119_, v_P_125_, v_tm_126_);
return v___x_127_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass___boxed(lean_object* v_State_128_, lean_object* v_VisibleTrace_129_, lean_object* v_MissingTrace_130_, lean_object* v_inst_131_, lean_object* v_inst_132_, lean_object* v_inst_133_, lean_object* v_inst_134_, lean_object* v_inst_135_, lean_object* v_inst_136_, lean_object* v_P_137_, lean_object* v_tm_138_){
_start:
{
lean_object* v_res_139_; 
v_res_139_ = lp_finiteQuerySandbox_FiniteQuerySandbox_visibleMissingMass(v_State_128_, v_VisibleTrace_129_, v_MissingTrace_130_, v_inst_131_, v_inst_132_, v_inst_133_, v_inst_134_, v_inst_135_, v_inst_136_, v_P_137_, v_tm_138_);
lean_dec_ref(v_inst_136_);
lean_dec_ref(v_inst_135_);
lean_dec_ref(v_inst_134_);
lean_dec(v_inst_133_);
lean_dec(v_inst_132_);
return v_res_139_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__0(lean_object* v_m_140_, lean_object* v_s_141_, lean_object* v_P_142_, lean_object* v_t_143_){
_start:
{
lean_object* v___x_144_; lean_object* v___x_145_; lean_object* v___x_146_; 
v___x_144_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_144_, 0, v_t_143_);
lean_ctor_set(v___x_144_, 1, v_m_140_);
v___x_145_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_145_, 0, v_s_141_);
lean_ctor_set(v___x_145_, 1, v___x_144_);
v___x_146_ = lean_apply_1(v_P_142_, v___x_145_);
return v___x_146_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__1(lean_object* v_m_147_, lean_object* v_P_148_, lean_object* v___x_149_, lean_object* v_inst_150_, lean_object* v_s_151_){
_start:
{
lean_object* v___f_152_; lean_object* v___x_153_; 
v___f_152_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__0), 4, 3);
lean_closure_set(v___f_152_, 0, v_m_147_);
lean_closure_set(v___f_152_, 1, v_s_151_);
lean_closure_set(v___f_152_, 2, v_P_148_);
v___x_153_ = lp_mathlib_Finset_sum___redArg(v___x_149_, v_inst_150_, v___f_152_);
return v___x_153_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__1___boxed(lean_object* v_m_154_, lean_object* v_P_155_, lean_object* v___x_156_, lean_object* v_inst_157_, lean_object* v_s_158_){
_start:
{
lean_object* v_res_159_; 
v_res_159_ = lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__1(v_m_154_, v_P_155_, v___x_156_, v_inst_157_, v_s_158_);
lean_dec_ref(v___x_156_);
return v_res_159_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg(lean_object* v_inst_160_, lean_object* v_inst_161_, lean_object* v_P_162_, lean_object* v_m_163_){
_start:
{
lean_object* v___x_164_; lean_object* v___f_165_; lean_object* v___x_166_; 
v___x_164_ = lp_mathlib_Real_instAddCommMonoid;
v___f_165_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg___lam__1___boxed), 5, 4);
lean_closure_set(v___f_165_, 0, v_m_163_);
lean_closure_set(v___f_165_, 1, v_P_162_);
lean_closure_set(v___f_165_, 2, v___x_164_);
lean_closure_set(v___f_165_, 3, v_inst_161_);
v___x_166_ = lp_mathlib_Finset_sum___redArg(v___x_164_, v_inst_160_, v___f_165_);
return v___x_166_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass(lean_object* v_State_167_, lean_object* v_VisibleTrace_168_, lean_object* v_MissingTrace_169_, lean_object* v_inst_170_, lean_object* v_inst_171_, lean_object* v_inst_172_, lean_object* v_inst_173_, lean_object* v_inst_174_, lean_object* v_inst_175_, lean_object* v_P_176_, lean_object* v_m_177_){
_start:
{
lean_object* v___x_178_; 
v___x_178_ = lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___redArg(v_inst_170_, v_inst_171_, v_P_176_, v_m_177_);
return v___x_178_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass___boxed(lean_object* v_State_179_, lean_object* v_VisibleTrace_180_, lean_object* v_MissingTrace_181_, lean_object* v_inst_182_, lean_object* v_inst_183_, lean_object* v_inst_184_, lean_object* v_inst_185_, lean_object* v_inst_186_, lean_object* v_inst_187_, lean_object* v_P_188_, lean_object* v_m_189_){
_start:
{
lean_object* v_res_190_; 
v_res_190_ = lp_finiteQuerySandbox_FiniteQuerySandbox_missingMass(v_State_179_, v_VisibleTrace_180_, v_MissingTrace_181_, v_inst_182_, v_inst_183_, v_inst_184_, v_inst_185_, v_inst_186_, v_inst_187_, v_P_188_, v_m_189_);
lean_dec_ref(v_inst_187_);
lean_dec_ref(v_inst_186_);
lean_dec_ref(v_inst_185_);
lean_dec(v_inst_184_);
return v_res_190_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_DualCertificate(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
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
