# G7 — neighbor-only redistribution, latency, and conservation (2 Nov 2026)

**Pre-registered first:** [PREREG_G7.md](PREREG_G7.md), commit `1609eff` before held-out seeds 1900–1907. **Code:** [beach/g7_local.py](beach/g7_local.py). **Independent CI run:** [GitHub Actions 41415181563](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41415181563) (success, 16 held-out seed/K cases, complete per-seed JSON attached as `g7-locked-per-seed`).

## Why G7 exists

[G6](G6_RESULTS.md) made the single-exposure numerical teacher effective by letting each patch subtract its own **previously learned ordinary stress**. However the resulting material update was projected to constant net material with a global `r-mean(r)`. The direct local conservative flux `local_flux(r)` was anti-aligned with the task gradient and failed 0/16. G7 tests a more sophisticated **explicit local relay**; it is a proposed engineered auxiliary circuit, not a discovered natural sand transport rule.

For patch residual `r`, a nearest-neighbour scalar potential evolves by

```
z_i <- z_i + 0.2 * (r_i - [2*z_i - z_(i-1) - z_(i+1)])
delta_h_i = 2*z_i - z_(i-1) - z_(i+1)
```

Only nearest neighbours are accessed inside this redistribution; `delta_h` is a divergence of local edge fluxes and sums to zero each step. The globally projected desired update `r-mean(r)` is **used by the referee only**. The `0.025` equal-length step used to compare task loss is **also external evaluation normalization**, not part of a physical controller.

## Frozen K=8 and K=48 results

Eight fresh seeds for each K, 310-step frozen Robin-wall wave calculations, G6 baseline trained for 12 teacher-free episodes, ideal numerically generated teacher boosted to 2% of the forward wall RMS.

| Neighbour communication rounds | K8 mean relative direction error | K48 mean relative direction error | K8 improvements | K48 improvements |
|---:|---:|---:|---:|---:|
| 0 | 1.000 | 1.000 | 0/8 (no update) | 0/8 (no update) |
| 4 | 0.4221 | 0.7806 | 8/8 | 8/8 |
| 16 | 0.09284 | 0.6648 | 8/8 | 8/8 |
| 64 | **0.0002345** | 0.4783 | 8/8 | 8/8 |
| 256 | 1.5e-14 | 0.2191 | 8/8 | 8/8 |
| 1024 | 2.8e-14 | 0.01569 | 8/8 | 8/8 |
| 4096 | 9.9e-14 | **4.19e-7** | **8/8** | **8/8** |

At N4096:

- K8 local mean final/initial loss **0.884867081379162**, global oracle **0.884867081379164**.
- K48 local mean loss ratio **0.889534771827988**, global oracle **0.889534772446647**.
- Worst total-material conservation error **5.68e-14**.
- Naive `local_flux(r)` remains a negative control, mean loss ratio **1.10625** at K8 and **1.05365** at K48.

An independent sinusoidal low-frequency probe, pre-specified without fitting to teacher responses, recovered **99.9656%** of its amplitude at K8 in 64 rounds but only **19.6989%** at K48. This matches standard Fourier-mode diffusion relaxation and makes the locality/latency cost explicit.

## All five preregistered gates pass

- **A PASS:** zero-sum flux and N0 no-op.
- **B PASS:** K8 N64 highly accurate direction and 8/8 task improvements.
- **C PASS:** large-K slow-mode latency contrast matches analytic prediction.
- **D PASS:** K48 N4096 reaches near-exact projection, 8/8 improvements.
- **E PASS:** task loss after the late local relay matches the global projected oracle.

## Critical limitation — the common mode is unbounded

The neighbor-only Poisson relay solves the zero-mean component, but `z`'s spatial average grows linearly as long as the mean stress drive remains nonzero. This is **not physically benign** if z represents a finite chemical concentration, pressure, or internal state.

Measured mean absolute common-mode magnitude (K48): **9.93** at 64 rounds, **158.87** at 1024 and **635.49** at 4096. At K8 it reaches **2261.61** by N4096. Differences between neighbouring z values still converge numerically, but a physically bounded implementation would need leak, saturation, a balancing reservoir, or explicit homeostasis. All can distort the useful gradient and must be measured rather than assumed safe.

This experiment uses an ideal software-provided reverse adjoint and energy-square stress writer, not real hydraulic stress or an autonomous natural transport law. It neither solves damping-induced teacher phase errors nor fast overtopping.

## Honest conclusion

**A two-memory-state numerical writer can use one teacher-on exposure, and an explicitly communicating neighbour-only auxiliary field can redistribute its locally measured update while conserving total material.** The second field replaces the software global redistribution at the price of latency and an unbounded common mode. This is a constructive numerical architecture, not evidence that actual sand does this spontaneously.

Next falsification: impose realistic bounded/leaky z and no externally supplied ideal teacher. See whether local learning survives under fixed time and finite dynamic range.
