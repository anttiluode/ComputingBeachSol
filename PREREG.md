# ComputingBeachSol — G1 protocol frozen 2026-11-02

**Status:** exploratory simulator built and tested on development seeds; no confirmatory result from seeds 40000–40031 existed when this protocol was committed. The predictions below are frozen before those seeds are evaluated. This protocol documents a deliberately minimal model, not calibrated sediment physics.

## Frozen model
- Reader and wave stencil: exact unchanged WallMemoryLaw `wml/cavity.py`, 96×96 ellipse, C=.65, DT=.5, DAMP=.006, Robin scale KAPPA=.28, 8 patches of 60% angular-sector width. Reference parent commit `1135aa6262873369e9c89761719db4800d4d9be7`.
- The bed: signed patch heights `h_i` start as centered Gaussian noise (sigma .015). They are not literal sand elevations. Discrete interface flux uses the signed contrast of patch-averaged wave-time derivatives `s_i=v_{i+1}-v_i`. `q_i=sign(s_i) max(|s_i|-.1,0)^1.5`; `h_i <- h_i + .06(q_{i-1}-q_i)`. Thus sum(h) is conserved; there is an exact no-transport threshold in this **proxy**, but no derived Shields law, Exner hydrodynamics, or physical shear calibration.
- The wave changes the wall: `kappa_i = .28 * (.5 + .45*tanh(h_i/.45))`, remaining passive. With material frozen, the cavity solver is the unmodified WallMemoryLaw stencil; writing updates Robin coefficients each step.
- A and B are Gaussian excitations from parent sources 0 and 1, both drive amplitude 6 and 170 steps. AB and BA receive exactly one of each with matched nominal amplitude and length. **The transient wave is reset to rest at each event boundary**, so any difference must persist in material. No event-order labels enter the writer.
- A read is 3 fixed Robin-cavity echo traces from sources 0,1,2 using 320 steps; the observed time window is [120,290). Materials are frozen during the official read. Separate dynamic tests attempt to write with weak amplitude .01 for 320 steps.
- Training: 14 paired seeds 100–113, centroid-difference classifier standardized only with training echoes. Held-out: **32 paired seeds 40000–40031**. Gaussian noise is injected into receiver features with std 4% of training-echo RMS, RNG seed 2026, independently across trials. P-value from 9999 paired-seed label swaps (plus observed, p-floor .0001).
- Controls: **fixed operator** during both writes at the *original* h0, while h accumulates; commutative sum is required. **Permuted wall** shuffles the final patches independently per observation before reading, using deterministic distinct seeds. Both controls are evaluated by the live-trained decoder, so permutation is an intervention, not a retrained comparative model.
- Independent geometry check: two-patch inclusion–exclusion interaction from four frozen continuous walls. Compare early relative amplitude with shortest 2-patch tour minus WallMemoryLaw's *empirical 40-step margin*. This does not automatically inherit the binary-state calibration counts.

## G1 predictions
P1: exact h equality under weak read pulses on fresh and written walls, no active threshold interfaces, and strictly positive transport under strong writes.
P2: `||h_AB-h_BA|| > .01` on >=30/32 held-out pairs; fixed-operator AB and BA distances <1e-10 in 32/32; per-history sum(h) conserved to 1e-10.
P3: held-out balanced order accuracy >=.80, paired label-swap p<.01, using only echo features under fresh 4% relative noise.
P4: shuffling the spatial arrangement drops accuracy >=.15, a diagnostic (not required for G1 core success).
P5: the two-patch interaction is negligible (early max <=1e-3 of peak) before the computed shortest tour minus 40 steps in the selected test geometry.
Only P1+P2+P3 warrant calling this a **toy-model readable order memory**. Even a pass does not demonstrate real sand, brain-like memory, physics-based gradient learning, or fast-time nonlinear computation.

## G2, G3 remain separate
G2 should compare a teacher-wave-induced **actual** sediment state update with the independently verified gradient w.r.t. wall coefficients, sweeping threshold/forcing. `|u+lambda|^2 - |u|^2 - |lambda|^2 = 2 u lambda` is an interference identity, not a proof sediment transport implements a gradient. The proper damped/discrete adjoint, reciprocal port boundary conditions, and directional flux must be accounted for.
G3 asks whether fast overtopping/threshold wave dynamics add a capability over frozen linear propagation, not just nonlinear writing.

## Design-data disclosure
Threshold, rate and read window were chosen in exploratory work using seeds 0–11, 100–107 and 10000–10011. No confirmatory results from seeds 40000–40031 were inspected before this commit.
