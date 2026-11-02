# G6 — one-exposure stress-memory writer (2 November 2026)

**Frozen protocol:** [PREREG_G6.md](PREREG_G6.md), committed at `38f62ec` before evaluation of held-out seeds `1600–1615`. **Implementation:** [beach/g6_memory.py](beach/g6_memory.py). **Reproducible run:** [GitHub Actions 41414618551](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41414618551), which uploads the complete per-seed JSON as `g6-locked-heldout`. All integrity checks passed. This report records successes *and* failures without changing any preregistered criterion.

## Experiment

A frozen numerical Robin-wall cavity produces a forward displacement `u` and a **numerically computed ideal adjoint** `lambda` for a target receiver echo. The background patch energy `E_i(u)` is learned into a *second state* `theta_i` over 12 teacher-free episodes with `theta <- theta + 0.65*(E-theta)`. The teacher exposure is a **single** `u + boost*lambda` field, externally amplitude-calibrated to 2% of forward RMS. The update input is locally `r_i = E_i(u+boost*lambda)-theta_i`. The material change scored in the successful branch is `r-mean(r)`: **global, software-enforced mass conservation**. The independent nearest-neighbour transport branch uses `local_flux(r)`.

This is a *best-case numerical two-state writer*, **not a real wave-injected teacher**, true Exner transport, or evidence of automatic plasticity in axonal actin rings.

## Held-out results (K8, 310 wave steps, 16 seeds)

| Candidate | Mean gradient cosine | Cases decreasing loss | Mean final / initial echo loss |
|---|---:|---:|---:|
| One teacher exposure + stored baseline + global mass projection | **+0.997104** | **16/16** | **0.877270** |
| Exactly known baseline + projection | +0.997102 | 16/16 | 0.877270 |
| G2d-style external two-exposure subtraction + projection | +0.999979 | 16/16 | 0.877162 |
| One teacher exposure, no baseline + projection | +0.001579 | 8/16 | 0.978885 |
| Wrong-source baseline + projection | +0.112912 | 10/16 | 0.975688 |
| Negative-phase teacher + learned baseline + projection | **−0.997347** | 0/16 | 1.140867 |
| Teacher off + learned baseline + projection | −0.013801 | 8/16 | 0.981293 |
| **Nearest-neighbour conservative flux** (no global projection) | **−0.861727** | **0/16** | **1.122249** |

**Caveat:** The teacher-off branch has a minuscule nonzero residual from incomplete EWMA calibration. Its normalized full-size counterfactual step can lower loss in 8/16 even though that material step would be extremely small if applied at its true unnormalized amplitude. Hence its **norm** matters more than the 8/16 number for that null: the off/on residual norm ratio is **0.0002935**.

Additional numerical checks:

- The single-exposure cross-term identity holds at relative error **4.23e−14**.
- Stored baseline relative RMS error is **3.38e−6** after twelve ordinary exposures.
- Reversing teacher phase reverses the update's direction.
- Mean-calibrated zero-net projected updates have max signed-sum error **5.12e−13**.
- After a material change, four additional baseline episodes reduce the stale baseline error to **0.015006** of its initial error. This is the **fixed-field** adaptation test, not many online episodes with changing material.
- Adaptive single-exposure writing beats the no-baseline matched update in **16/16** held-out cases.
- Internal baseline is marginally worse than perfect external two-exposure algebra: mean echo loss ratio 0.877270 vs 0.877162, as expected from small teacher-square and residual-calibration terms.

## Preregistered gate verdict

- **G6-A PASS** — energy algebra matches the forward–adjoint cross term.
- **G6-B PASS** — internal baseline plus idealized teacher is well aligned and improves all 16.
- **G6-C PASS** — phase reversal flips direction, and teacher-off residual norm is tiny.
- **G6-D PASS** — mathematical zero-sum checks (not real sediment).
- **G6-E FAIL** — the *local conserving flux* opposes the desired gradient and worsens loss in all 16.
- **G6-F PASS** — four passive recalibration episodes repair baseline lag to <5% in this frozen-bed protocol.

## Interpretation / next gate

G6 repairs the **subtraction problem** in a model with an **explicit second slow stress state**, not by asking a single plain sand height variable to magically infer a desired task. It **does not** repair the **transport problem**, which remains the key physical bottleneck. A local flux based on the raw stress *gradient* applies a Laplacian to the desired update and in this model reverses its sign. The global mean projection hides a nonlocal redistribution operation.

A future separately preregistered **local diffusion / conservative-transport** circuit may test whether a second, communicating potential field can implement the required projection through only neighbour exchanges. If it succeeds, the delay and extra memory needed for local communication must be counted; it would remain an engineered model, not natural sediment learning.

**Read/write and G2b failures remain unchanged.** The new gate neither solves fast nonlinear overtopping nor establishes loss-tolerant reverse teacher propagation.
