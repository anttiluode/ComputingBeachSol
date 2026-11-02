# G2b — A valid gradient in the wave field does not make a sand-gradient writer

**Frozen study: FAIL.** Preregistered in [PREREG_G2B.md](PREREG_G2B.md) at commit `183db703`, before seeds 800–815 were evaluated. Full source: [beach/teacher.py](beach/teacher.py), runner: [beach/g2b.py](beach/g2b.py), summary with per-seed table: [results/g2b_summary.json](results/g2b_summary.json). This is a model result, **not experimental fluid physics**.

## The distinction being measured

G2a verified the Robin-wall derivative against finite differences. For frozen material and a receiver loss, the discrete adjoint gives

```
dJ/db_i = -[(C*DT)^2*KAPPA/(1+DAMP*DT/2)]
          * SUM_{t,x} counts_i(x) * u_t(x) * lambda_{t+1}(x)
```

That is the local forward–adjoint interference product. It can be reconstructed algebraically from `(u+lambda)^2-u^2-lambda^2`, but it **does not say how a real material changes**.

We exposed the current G1 **target-blind** signed velocity-threshold transport to the *numerically computed ideal adjoint field*, aligned with the forward wave; the teacher wall RMS was externally amplified to equal the forward wave. The nonlinear transport is

```
s_i(t) = v_(i+1)(t) - v_i(t)
q_i(t) = sign(s_i) * max(|s_i|-threshold,0)^1.5
delta_h_i = 0.06 * SUM_t [q_(i-1)-q_i]
```

We then compared `delta_h` with the **projected** negative gradient of receiver loss with respect to h, so the referee respects constant total material. The reader loss is recomputed after a common-norm material step (.025). The gradient never updates the writer; it only judges the direction.

The writer computes material changes for (1) forward-only, (2) teacher-only, (3) superposed forward+teacher waves. The *interference-only diagnostic* subtracts (1) and (2) from (3). It is not itself a standalone writing intervention.

## Locked held-out results

16 unseen target/material seeds 800–815, 310 wave steps, source `seed % 3`, target offset sigma .21, primary interface stress threshold = .5 × mean forward-only absolute interface contrast, teacher wall RMS = forward wall RMS, no parameter tuning on held-outs.

| Measurement | Forward only | Teacher only | Teacher on (sum) | Isolated interference |
|---|---:|---:|---:|---:|
| Mean cosine with projected -gradient | **+0.2069** | +0.1238 | +0.0904 | **−0.2413** |
| Positive alignment, /16 | 12 | 9 | 11 | **4** |
| Equal-length update lowers target loss, /16 | 12 | 10 | 11 | **4** |
| Mean updated/initial loss ratio | 1.0094 | 0.9869 | 1.0130 | **1.0384** |

The teacher-on update beats forward-only in **5/16** cases; there is no consistent benefit. A reversed-phase teacher gives interference mean cosine **+0.0534** and does not establish correctly signed supervision either. Zero-amplitude teacher gives the forward-only result exactly.

**Preregistered gates:** 6 learning criteria failed; the 3 numerical integrity controls passed (conservation, gradient identity, zero teacher). Max signed material-sum error: 2.4e-16. Discrete-gradient cross identity error: at most 1.1e-15. The external teacher amplification needed to match forward wall RMS was large: median **1626×** (a normalization, *not* a feasible passive gain measurement).

## Threshold sweep (secondary, not an optimization search)

| threshold / mean forward stress | teacher-on mean cosine | interference-only mean cosine | teacher on beats off |
| ---: | ---: | ---: | ---: |
| 0.00 | +0.0336 | −0.2266 | 5/16 |
| 0.25 | +0.0668 | −0.2363 | 5/16 |
| 0.50 | +0.0904 | −0.2413 | 5/16 |
| 1.00 | +0.1284 | −0.2406 | 6/16 |
| 2.00 | +0.1765 | −0.1874 | 7/16 |

**No tested threshold rescued the interference-only writer.** Selecting the best-looking threshold after the fact would violate the protocol anyway.

## Interpretation — the missing operator

The wave gradient is a **local product** of forward and adjoint displacement fields, integrated over a patch. The sand rule moves mass using **differences of neighbouring velocity signals**, followed by an additional divergence and a hard nonlinearity. None of those operations preserves the gradient direction in general. Total mass conservation correctly removes the uniform-gradient direction, but that alone does not make signed flux match a useful projected gradient. An automatic Shields-like read/write threshold is **not** automatically a learning law.

In particular, adding an error wave does not imply that the cross term in its intensity becomes the cross term in *transport*. The thresholded, signed nonlinear function is applied **after wave velocities have been differenced**.

This narrows the next question, rather than killing the beach concept:

1. Can a physically justified local **energy-sensitive** sediment flux align with a *metric-aware* negative gradient across targets? If mass moves by local flux divergence, compare its natural preconditioning with the projected gradient, not assume exact equality.
2. Can the backward field be launched from a genuine reciprocal receiver source, with time-reversal indexing and attenuation treated correctly? G2b idealized this instead of demonstrating it.
3. Does teacher-on learning survive fully **online, feedback-coupled writing**, new geometries, and real shear measurements? These remain untested.

**Not shown:** real sand learning, backpropagating sediment, in-situ physical reverse propagation, or G3 fast overtopping computation. G1's earlier synthetic order memory and G2a's exact numerical derivative still stand as *separate* results.

**Reproduction:**

```bash
python -m unittest discover -s tests -v
python -m beach.g2b --out results/g2b_full_reproduction.json
```

CI independently regenerates the full per-seed 16 × 5 threshold sweep, phase-reversed and zero-teacher controls, checks frozen aggregate metrics, and uploads its raw JSON as a workflow artifact.
