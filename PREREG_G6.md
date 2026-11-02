# G6 preregistration — one teaching exposure with a learned stress baseline

**Frozen on 2026-11-02 before evaluating G6 held-out seeds 1600–1615.** This is a numerical WallMemoryLaw Robin-wall experiment, not actual sand, measured AIS plasticity, or an autonomous physical teacher. This protocol builds on [G2b failure](G2B_RESULTS.md) and [G2d contrast success](ROUND3_RESULTS.md).

## Motivation and model

For a fixed material and forward displacement field `u`, define the patch energy `E_i(u)=sum_{t,x in patch i} u(t,x)^2`. G2d's numerical adjoint field `lambda` is externally computed from a desired receiver echo. Calibrate a **stored stress baseline** `theta_i` by exposing unchanged material to `u` without changing bed height:

`theta <- theta + alpha*(E(u)-theta)`, with theta initially zero, alpha = 0.65, and 12 forward-only episodes. Freeze theta during a **single** simultaneous teacher exposure `u + boost*lambda`, where boost gives a teacher RMS of 2% of forward wall RMS as in G2d. The effective local writer is `r_i = E_i(u+boost*lambda)-theta_i`. It uses **one teacher exposure** plus a stored state; it does not calculate `E_plus-E_minus` at write time.

For exactly calibrated theta, the identity is `r_i=2*boost*sum(u*lambda)_i + boost^2*E_i(lambda)`. Hence a small but nonzero teacher-squared bias remains. The *orientation* of its intended update is compared with the exact **finite-difference-verified** projected negative echo-loss gradient. This is a two-state numerical memory device, not ordinary Exner sediment.

## Fixed evaluation

- Synthetic materials: `Beach()`, same K=8, same target construction and exact adjoint as G2d (`target_h=h+Normal(0,.21)`, target mean corrected; source=`seed%3`; wave length 310), and previously unused held-out seeds `1600..1615`.
- Same material-step norm `0.025` for every nonzero tested update.
- Primary branches: learned baseline with one teacher exposure (`adaptive`); exact ideal baseline `E(u)` (`exact_theta` upper control); no baseline (`no_theta`); opposite teacher phase (`negative_teacher`); no teacher (`teacher_off`); baseline calibrated on a different source (`wrong_source_theta`); software two-exposure projected contrast (`two_exposure_oracle`).
- Writer's material-update direction: `r - mean(r)` (**global mean projection**, nonlocal and explicitly labeled), plus independently assessed local **nearest-neighbour conservative flux** `local_flux(r)` as a physically restricted negative control. A local conserved update must not be described as working if only the mean projection passes.
- Additional baseline drift test: after the first projected update, reuse the stale theta, compare a refreshed exact baseline, and let theta receive `0, 1, 4` new forward-only calibration episodes at the new material before its next teaching exposure.
- Scores: gradient-direction cosine, new/old task loss, number of improving held-out seeds, relative theta calibration error, and total material change. Zero-norm branches are no-ops, never normalized to full step. No threshold is inserted into the teacher energy law; that is a separate future gate.

## Frozen decision rules

G6-A algebra passes if `max|r_exact - (2b<u,lambda>+b²<lambda,lambda>)| / max(1,||r_exact||) < 1e-9`.
G6-B baseline-calibrated teacher passes if mean cosine >= 0.98, echo loss decreases on >= 14/16 held-out materials, and it beats no-baseline echo loss on >= 12/16 matched cases.
G6-C signed response passes if flipping teacher sign produces mean cosine <= -0.90, and the teacher-off mean projected material change is less than 0.1% of the teacher-on mean before unit normalization.
G6-D conservation passes if projected material sum and local flux sum both have absolute error < 1e-10. This is numerical conservation only.
G6-E **local material-learning gate** passes only if nearest-neighbor flux gives mean cosine > 0.50 and improves echo loss in >= 12/16 seeds. Failure here means a **local physical writer is not established**, even if G6-B passes.
G6-F baseline drift recovery passes if four recalibration episodes reduce the mean relative theta error (against the forward energy of the *updated* bed) to <= 5% of stale-theta error. A single write changing the bed is the confound under examination.

Do not change these bars after looking at the held-out results. Report all failed gates, including low-normalization or phase-sign surprises; G2b and G2c negative results remain intact. Do not imply a physically launched reciprocal teacher: the numerical adjoint is still handed to the writer as a best-case signal.

## Reason to test

Claude identified that a baseline `theta` tracking ordinary stress might provide the internal subtraction missing in G2b/G5, reminiscent of homeostatic thresholds. This is a **hypothesis**, not evidence that AIS actin rings or stress-aged gravel implement this specific mathematical rule. Its decisive gap is whether ordinary local transport and finite-memory lag preserve the orientation of the intended update.
