# Preregistered G2b — does a teacher wave make the existing sand law descend?

*Frozen 2026-11-02 after exploratory work on seeds 31–33 and before any G2b confirmatory result on seeds 800–815.*

## Testable distinction
G2a showed the discrete Robin derivative is proportional to a local forward × adjoint field product. That mathematical identity **does not imply** the pre-existing thresholded G1 sediment rule will make the correct wall change. The tested writer here is unchanged:
- For each patch, the average **velocity** is measured from the fast field.
- At each neighbouring interface, signed velocity contrast `s_i=v_(i+1)-v_i`.
- Flux `q_i=sign(s_i)*max(|s_i|-theta,0)^1.5`, then `delta_h_i=.06 sum_t(q_(i-1)-q_i)`.
- This conserves total signed material exactly to floating point. No gradients or target data enter its update.

## Favorable idealization, openly declared
- Start from the **unchanged** WallMemoryLaw 96×96 elliptical cavity, K=8 and fraction=.6, the baseline `Beach.initial(seed)`, and frozen Robin coefficients during the entire teaching episode.
- A target is obtained from a different randomly offset hidden material state (Gaussian sigma .21, recentered so total mass matches). The wave is a Gaussian **initial displacement** from `source=seed%3`.
- The teacher is the **computed exact discrete adjoint** field, aligned at each timestep with the forward field. It is not yet produced by a real receiver transducer: the numerical backward recursion computes it. Thus this is a best-case cross-field exposure, not demonstrated physical time reversal or trained hydrodynamics.
- An externally specified gain adjusts teacher **wall RMS** to exactly one times forward wall RMS. The gain and separately the teacher-alone exposure are reported. Gain is not a passive physical process.
- At each time step, evaluate existing signed transport law on (a) forward field only, (b) teacher field only, (c) their sum. Record `delta_interference = delta_(sum) - delta_forward - delta_teacher`. This subtractive counterfactual is for *measurement*, not the actual update algorithm.
- Time horizon 310 samples; there is no dynamically changing wave operator within this episode (more favorable for a true gradient comparison). Stress threshold is specified as the multiple of mean absolute forward-only interface velocity contrast, using all patches/timepoints, and is frozen per case before any target-alignment result.
- Use projected negative dJ/dh as referee (remove its mean because total h is conserved). The gradient is derived from WallMemoryLaw, not ArborVerb's edge gain. Verify the local cross-product algebra independently.

## Frozen parameters and holdouts
- **Primary:** threshold fraction .5, teacher/forward wall RMS ratio 1, phase sign +, normalized material comparison length .025.
- Confirmatory seeds 800–815 (16 independent hidden targets, none used in development). Train on no seeds; no classifier fitted.
- Controls on all 16 seeds: forward-only (teacher off), teacher-only, interference-only (subtraction), reversed teacher phase (-lambda), and zero-amplitude teacher.
- Secondary threshold curve: fractions [0, .25, .5, 1, 2] at teacher ratio 1; report means, medians, number of positive cosines and loss-improving normalized updates, *without* threshold selection.

## Locked primary success rule
Call G2b a *positive learning writer* **only if** on 16 cases, at the primary setting:
1. >= 12 of 16 teacher-on updates have cosine with projected -gradient > 0.
2. mean cosine >= .5, and >= 12/16 equal-length teacher-on updates lower target loss (`loss_ratio < 1`).
3. teacher-on loss ratio beats **forward-only** loss ratio on >= 12/16 paired cases.
4. interference-only material change has mean cosine >= .3 with projected -gradient, and its mean is greater than the phase-reversed interference mean by >= .2.
5. material mass conservation max error <= 1e-10 and independently derived cross-identity rel error <= 1e-10.

If any fails, this **particular signed-velocity flux rule** does not demonstrate G2b. This cannot disprove other physically realistic transport laws or other ways of forming an energy-sensitive photonic/hydrodynamic teacher.

## Calibration and caveats
- The loss is 0.5 mean squared receiver echo difference. All updates are compared at a common Euclidean norm .025 (and record unnormalized norms); this isolates *direction*, not physical actuation energy or speed.
- The raw physical "teacher-on" operation is `delta_(sum)`. "Interference-only" is an analytical control that subtracts independent exposures and is not directly a standalone physical training recipe.
- Prior exploratory work (seeds 31–33, multiple thresholds) found mixed or negative interference alignment, motivating this preregistration but not included in confirmatory averages.
- G2a previously passed finite differences. G1 previously passed echo order in an effective patch model. Neither implies success here.
