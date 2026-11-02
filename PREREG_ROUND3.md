# PRE-REGISTRATION — G1b resolution and timing, G1c common-tail order, G2c matched energy writer
Date: 2026-11-02. **Committed before confirmatory seeds 41000–41031 and 900–915 were evaluated.**
This is a new gate, separate from G1 (which used seeds 40000–40031), G2a, and negative G2b.

## Scope and parent model
Unchanged `wml/cavity.py` at pinned WallMemoryLaw parent `1135aa6`; unchanged G1 `Beach.event` 96x96 elliptical Robin-wall physics and toy signed-threshold conservative material dynamics. A fresh wave starts at rest for each A, B, or X episode. All material updates occur before measuring echoes. During read, the exact WML solver holds wall coefficients fixed. The same weak read amplitude .01 and noise standard deviation rule are applied at every K.

This is an effective patch material, **not real sediment**. Sweeping K changes parameter count, patch width/size and local velocity averaging simultaneously. Therefore a K effect is not proof that dimensionality alone caused the result.

## G1b/G1c: K and arrival windows
- `K in {8,16,24,48}`, angular fraction 0.6 of each sector; same total writable wall fraction approximately, no changes to pulse amplitudes (6), episode length (170), threshold (.1), transport rate (.06), input source positions, receiver location, cavity and wave damping.
- Two binary histories: AB vs BA from source indices 0 and 1. **Common-final-exposure attack:** ABX vs BAX with X source index 2, same amplitude 6 and duration 170; X starts from zero fast wave state but current material is retained.
- Training material seeds 1100–1115 (16 paired worlds). Held-out seeds 41000–41031 (32 paired worlds); no overlap with prior G1 or development seeds.
- Read each state using all three receiver source traces, exactly 510 time steps. Arrival t_a(s) is the first point where the **unwritten** all-zero material trace from source s crosses 0.1% of its own peak; this measurement cannot inspect labels or held-out material. Offset the windows *independently per source* by the recorded t_a(s).
- Windows: prearrival [t_a-110,t_a-10), early [t_a-10,t_a+170), late [t_a+170,t_a+350), whole [0,510). Early and late are equal length. Prearrival is an explicit absence-of-signal diagnostic.
- Train only the G1 centroid-difference linear classifier on unmodified training echoes for each K/history/window. Normalize each feature with train-only mean/variance and 3%-of-global-max standard-deviation floor. Apply additive independent Gaussian receiver noise to test data at **4% of the training EARLY-echo RMS**, fixed for all windows for a given K and history. Deterministic RNG seeds `2026 + 10*K + window_index + (500 if ABX)`. A zero classifier direction is scored as 50% undecided, not 0%.
- Evaluate fixed-wave-operator open-loop AB/BA and ABX/BAX at K=8 and K=48, with wave coefficients held to initial material during *all* writes. Record transport activity and material-difference norms, not just decoder scores.
- Primary unselected comparisons (no best-window picking): early vs late at each K, AB vs ABX at each K, K8 vs K48 for ABX early. Whole and prearrival are diagnostics. A result is only a cross-K or timing pattern **in this toy model**, not direct confirmation of WallMemoryLaw's binary calibration-count law.

### Locked G1b/c predictions
- R1: K8 AB early decoding >= 0.85; K8 ABX early decoding >= 0.75.
- R2: K48 ABX early falls >= 0.10 versus K8 ABX early.
- R3: K8 and K48 ABX *late* both >= 0.75; common final event does not automatically erase order.
- R4: prearrival accuracy is 0.5 (uninformative) within +/-0.10 at every K/history.
- R5: in fixed-operator controls max AB/BA and ABX/BAX material distance <1e-10.
- No prediction that early always beats late; the development runs suggest late sometimes outperforms early. Report actual arrivals and every window, including failed predictions.

Development seeds were 200–211 (train), 500–505 (test), and **not** reused in confirmation. Threshold/window settings are fixed above before new seeds.

## G2c: matched local quadratic operator, not yet autonomous sand learning
- Keep the same K8 Robin cavity; exact **numerical discrete** teacher field `lambda[t]` computed by `beach.teacher.adjoint_snapshot` from source `seed%3`, and a target made from a random sigma 0.21 offset in material. Forward field `u[t]` uses frozen current wall. Response length 310.
- The energy writer *only* sees two measured patch energies `E_i^+=sum_(t,x in patch_i)(u+alpha lambda)^2` and `E_i^-=sum_(t,x in patch_i)(u-alpha lambda)^2`. External software forms `(E_plus-E_minus)/(4 alpha)`. There is **no gradient input to the writer**; reference gradient from `loss_and_gradient` is used only for evaluation.
- External teacher gain alpha is set by a fixed teacher/forward wall RMS ratio **0.02**. It is a laboratory normalization, not free physical in-situ amplification.
- Threshold applied to each integrated patch energy *before* subtraction: `max(E_plus-theta,0)-max(E_minus-theta,0)`; theta is predetermined fraction in {0,0.25,0.5,0.75} of median forward patch energy for that case. This is a *global integrated energy threshold*, not instantaneous Shields stress.
- Three candidate directions: **unconstrained** local energy contrast, **projected** contrast after subtracting mean (globally adjusted mass constraint, not autonomous local physics), and **conservative downhill flux** (`q_i=contrast_i-contrast_(i+1)`; `delta_h_i=q_(i-1)-q_i`, local divergence). Include natural `-E_forward` and single-exposure `-E_plus` controls.
- Gradient referee is chain rule `dJ/dh=dJ/db*sech²(h/.45)`, projected onto sum(h)=constant. Reports include cosine and echo loss after **equal-norm .025** material update for every candidate. The external mean subtraction and two-phase subtraction are *not* evidence a passive beach learned autonomously.
- Held-out seeds 900–915 (16), separate from development 31–34 and earlier G2b 800–815. No threshold chosen after inspection.

### Locked G2c predictions
- E1: with zero threshold, projected contrast mean cosine with negative projected gradient >=0.999 and loss decreases in >=14/16.
- E2: when cutoff fraction is .75, projected mean cosine decreases from zero-threshold case by >=.03.
- E3: conservative downhill-flux writer has mean cosine <0 at zero threshold and improves loss in <=4/16.
- E4: zero-threshold energy contrast obeys the 4 alpha cross term to numerical precision; material mass of projected and conservative updates changes by <=1e-10.
- E5: the teacher-influenced projected contrast must outperform natural forward-only erosion in >=12/16 on equal-norm loss comparison. If E1 passes but E5 fails, call it mathematically aligned, not useful learning superiority.

**Interpretation boundary:** E1/E4 are largely algebraic sanity checks given a correct adjoint. They do not demonstrate a single-exposure, local, signed physical writer. The conservatively moving sand (E3) is the better physical analog. Do not combine E1 with G1 to claim physical backpropagation.
