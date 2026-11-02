# G2d pre-registration — equal-mass natural erosion control

Frozen on 2026-11-02 before seeds **1200–1215** were evaluated. Earlier G2c seeds 900–915 already exposed an **unfair comparison**: the tested energy-contrast update was mean-projected to conserve sum(h), while the ordinary erosion baseline -E_forward could change total mass. E5 failed at 8/16, but it could not distinguish target-specific learning from exploiting the uniform material mode.

**Do not rewrite or reinterpret G2c's preregistered E5.** This is a separate confirmatory experiment with unused seeds.

## Fixed comparison
- Same G2c WML elliptical cavity, K8, teacher=exact numerical adjoint, 310 steps, teacher/forward wall RMS ratio 0.02, zero integrated energy threshold.
- Same target-generation recipe: seed-specific Gaussian offsets sigma 0.21, recentered. Same starting material, injection source=seed%3, waveform error, echo loss, input and target in both conditions.
- `contrast = (E_plus-E_minus)/(4*alpha)` with E measuring summed displacement squared over each patch and time. Its signed candidate update is `contrast-mean(contrast)`.
- **Matched null:** forward-only erosion `-E_forward` with the SAME global mean removal `-E_forward - mean(-E_forward)`. Both candidate updates have zero total signed height and are scaled to the same Euclidean height-step norm **0.025**. No hidden gradient is provided to either candidate. The numerical adjoint is available as teacher for the contrast candidate.
- Additional control: one-teacher-exposure erosion `-E_plus` with identical mean subtraction, also normalized to 0.025. It is not an independent learned teacher mechanism.
- Original unconstrained erosion and local conservative-downhill-flux conditions are reported as *diagnostics* but are not fair controls for this isolated constrained comparison.
- Seeds **1200–1215** are disjoint from G2c development and held-out, and G2b.
- Report each direction's gradient cosine and recomputed finite-step loss, not merely relative ranking.

## Locked prediction
D1: energy-contrast beats mean-projected forward-only erosion (lower loss) in at least **12 of 16** new seeds.
D2: energy-contrast beats mean-projected single-exposure `-E_plus` in at least **12 of 16**.
D3: mean cosine energy-contrast vs projected negative gradient >= **0.999**, and loss is reduced in >=14/16.
D4: both comparator updates conserve sum(h) within 1e-10, and same update norm is applied.
If D1-4 pass, conclude **two-phase, externally contrasted numerical teacher exposure improves over matched conserving natural energy erosion in this toy model**. Do **not** claim autonomous physical backpropagation: the teacher and E_plus-E_minus subtraction remain computational, and the global mean subtraction is not a local conservation law.

No adaptive threshold or step-size selection after inspecting new seeds.
