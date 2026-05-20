// Lean compiler output
// Module: FiniteQuerySandbox.CaseStudy
// Imports: public import Init public import Mathlib public import FiniteQuerySandbox.InfoTheory public import FiniteQuerySandbox.ChannelCapacity public import FiniteQuerySandbox.MarkovGenerator public import FiniteQuerySandbox.CutSetBoundExtract
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
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__0(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__1(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__0(lean_object* v_z_1_, lean_object* v_x_2_, lean_object* v_P4_3_, lean_object* v_y_4_){
_start:
{
lean_object* v___x_5_; lean_object* v___x_6_; lean_object* v___x_7_; lean_object* v___x_8_; lean_object* v___x_9_; 
v___x_5_ = lean_box(0);
v___x_6_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_6_, 0, v_z_1_);
lean_ctor_set(v___x_6_, 1, v___x_5_);
v___x_7_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_7_, 0, v_y_4_);
lean_ctor_set(v___x_7_, 1, v___x_6_);
v___x_8_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_8_, 0, v_x_2_);
lean_ctor_set(v___x_8_, 1, v___x_7_);
v___x_9_ = lean_apply_1(v_P4_3_, v___x_8_);
return v___x_9_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__1(lean_object* v_z_10_, lean_object* v_P4_11_, lean_object* v___x_12_, lean_object* v_inst_13_, lean_object* v_x_14_){
_start:
{
lean_object* v___f_15_; lean_object* v___x_16_; 
v___f_15_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__0), 4, 3);
lean_closure_set(v___f_15_, 0, v_z_10_);
lean_closure_set(v___f_15_, 1, v_x_14_);
lean_closure_set(v___f_15_, 2, v_P4_11_);
v___x_16_ = lp_mathlib_Finset_sum___redArg(v___x_12_, v_inst_13_, v___f_15_);
return v___x_16_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__1___boxed(lean_object* v_z_17_, lean_object* v_P4_18_, lean_object* v___x_19_, lean_object* v_inst_20_, lean_object* v_x_21_){
_start:
{
lean_object* v_res_22_; 
v_res_22_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__1(v_z_17_, v_P4_18_, v___x_19_, v_inst_20_, v_x_21_);
lean_dec_ref(v___x_19_);
return v_res_22_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg(lean_object* v_inst_23_, lean_object* v_inst_24_, lean_object* v_P4_25_, lean_object* v_z_26_){
_start:
{
lean_object* v___x_27_; lean_object* v___f_28_; lean_object* v___x_29_; 
v___x_27_ = lp_mathlib_Real_instAddCommMonoid;
v___f_28_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg___lam__1___boxed), 5, 4);
lean_closure_set(v___f_28_, 0, v_z_26_);
lean_closure_set(v___f_28_, 1, v_P4_25_);
lean_closure_set(v___f_28_, 2, v___x_27_);
lean_closure_set(v___f_28_, 3, v_inst_24_);
v___x_29_ = lp_mathlib_Finset_sum___redArg(v___x_27_, v_inst_23_, v___f_28_);
return v___x_29_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit(lean_object* v_00_u03b1_30_, lean_object* v_00_u03b2_31_, lean_object* v_00_u03b3_32_, lean_object* v_inst_33_, lean_object* v_inst_34_, lean_object* v_inst_35_, lean_object* v_inst_36_, lean_object* v_inst_37_, lean_object* v_inst_38_, lean_object* v_P4_39_, lean_object* v_z_40_){
_start:
{
lean_object* v___x_41_; 
v___x_41_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___redArg(v_inst_33_, v_inst_34_, v_P4_39_, v_z_40_);
return v___x_41_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit___boxed(lean_object* v_00_u03b1_42_, lean_object* v_00_u03b2_43_, lean_object* v_00_u03b3_44_, lean_object* v_inst_45_, lean_object* v_inst_46_, lean_object* v_inst_47_, lean_object* v_inst_48_, lean_object* v_inst_49_, lean_object* v_inst_50_, lean_object* v_P4_51_, lean_object* v_z_52_){
_start:
{
lean_object* v_res_53_; 
v_res_53_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalZMass__unit(v_00_u03b1_42_, v_00_u03b2_43_, v_00_u03b3_44_, v_inst_45_, v_inst_46_, v_inst_47_, v_inst_48_, v_inst_49_, v_inst_50_, v_P4_51_, v_z_52_);
lean_dec_ref(v_inst_50_);
lean_dec_ref(v_inst_49_);
lean_dec_ref(v_inst_48_);
lean_dec(v_inst_47_);
return v_res_53_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__0(lean_object* v_yz_54_, lean_object* v_P4_55_, lean_object* v_x_56_){
_start:
{
lean_object* v_fst_57_; lean_object* v_snd_58_; lean_object* v___x_60_; uint8_t v_isShared_61_; uint8_t v_isSharedCheck_69_; 
v_fst_57_ = lean_ctor_get(v_yz_54_, 0);
v_snd_58_ = lean_ctor_get(v_yz_54_, 1);
v_isSharedCheck_69_ = !lean_is_exclusive(v_yz_54_);
if (v_isSharedCheck_69_ == 0)
{
v___x_60_ = v_yz_54_;
v_isShared_61_ = v_isSharedCheck_69_;
goto v_resetjp_59_;
}
else
{
lean_inc(v_snd_58_);
lean_inc(v_fst_57_);
lean_dec(v_yz_54_);
v___x_60_ = lean_box(0);
v_isShared_61_ = v_isSharedCheck_69_;
goto v_resetjp_59_;
}
v_resetjp_59_:
{
lean_object* v___x_62_; lean_object* v___x_64_; 
v___x_62_ = lean_box(0);
if (v_isShared_61_ == 0)
{
lean_ctor_set(v___x_60_, 1, v___x_62_);
lean_ctor_set(v___x_60_, 0, v_snd_58_);
v___x_64_ = v___x_60_;
goto v_reusejp_63_;
}
else
{
lean_object* v_reuseFailAlloc_68_; 
v_reuseFailAlloc_68_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_68_, 0, v_snd_58_);
lean_ctor_set(v_reuseFailAlloc_68_, 1, v___x_62_);
v___x_64_ = v_reuseFailAlloc_68_;
goto v_reusejp_63_;
}
v_reusejp_63_:
{
lean_object* v___x_65_; lean_object* v___x_66_; lean_object* v___x_67_; 
v___x_65_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_65_, 0, v_fst_57_);
lean_ctor_set(v___x_65_, 1, v___x_64_);
v___x_66_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_66_, 0, v_x_56_);
lean_ctor_set(v___x_66_, 1, v___x_65_);
v___x_67_ = lean_apply_1(v_P4_55_, v___x_66_);
return v___x_67_;
}
}
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__1(lean_object* v_P4_70_, lean_object* v___x_71_, lean_object* v_inst_72_, lean_object* v_yz_73_){
_start:
{
lean_object* v___f_74_; lean_object* v___x_75_; 
v___f_74_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__0), 3, 2);
lean_closure_set(v___f_74_, 0, v_yz_73_);
lean_closure_set(v___f_74_, 1, v_P4_70_);
v___x_75_ = lp_mathlib_Finset_sum___redArg(v___x_71_, v_inst_72_, v___f_74_);
return v___x_75_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__1___boxed(lean_object* v_P4_76_, lean_object* v___x_77_, lean_object* v_inst_78_, lean_object* v_yz_79_){
_start:
{
lean_object* v_res_80_; 
v_res_80_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__1(v_P4_76_, v___x_77_, v_inst_78_, v_yz_79_);
lean_dec_ref(v___x_77_);
return v_res_80_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg(lean_object* v_inst_81_, lean_object* v_P4_82_){
_start:
{
lean_object* v___x_83_; lean_object* v___f_84_; 
v___x_83_ = lp_mathlib_Real_instAddCommMonoid;
v___f_84_ = lean_alloc_closure((void*)(lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg___lam__1___boxed), 4, 3);
lean_closure_set(v___f_84_, 0, v_P4_82_);
lean_closure_set(v___f_84_, 1, v___x_83_);
lean_closure_set(v___f_84_, 2, v_inst_81_);
return v___f_84_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit(lean_object* v_00_u03b1_85_, lean_object* v_00_u03b2_86_, lean_object* v_00_u03b3_87_, lean_object* v_inst_88_, lean_object* v_inst_89_, lean_object* v_inst_90_, lean_object* v_inst_91_, lean_object* v_inst_92_, lean_object* v_inst_93_, lean_object* v_P4_94_){
_start:
{
lean_object* v___x_95_; 
v___x_95_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___redArg(v_inst_88_, v_P4_94_);
return v___x_95_;
}
}
LEAN_EXPORT lean_object* lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit___boxed(lean_object* v_00_u03b1_96_, lean_object* v_00_u03b2_97_, lean_object* v_00_u03b3_98_, lean_object* v_inst_99_, lean_object* v_inst_100_, lean_object* v_inst_101_, lean_object* v_inst_102_, lean_object* v_inst_103_, lean_object* v_inst_104_, lean_object* v_P4_105_){
_start:
{
lean_object* v_res_106_; 
v_res_106_ = lp_finiteQuerySandbox_FiniteQuerySandbox_marginalYZPMF__of__unit(v_00_u03b1_96_, v_00_u03b2_97_, v_00_u03b3_98_, v_inst_99_, v_inst_100_, v_inst_101_, v_inst_102_, v_inst_103_, v_inst_104_, v_P4_105_);
lean_dec_ref(v_inst_104_);
lean_dec_ref(v_inst_103_);
lean_dec_ref(v_inst_102_);
lean_dec(v_inst_101_);
lean_dec(v_inst_100_);
return v_res_106_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_InfoTheory(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_ChannelCapacity(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_MarkovGenerator(uint8_t builtin);
lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_CutSetBoundExtract(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_finiteQuerySandbox_FiniteQuerySandbox_CaseStudy(uint8_t builtin) {
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
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_ChannelCapacity(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_MarkovGenerator(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_finiteQuerySandbox_FiniteQuerySandbox_CutSetBoundExtract(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
