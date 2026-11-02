# G8 — edge-only relay removes the runaway gauge mode (2 November 2026)

**Preregistered before held-out evaluation:** [PREREG_G8.md](PREREG_G8.md), commit `52891a6c`. **Code:** [beach/g8_edge.py](beach/g8_edge.py), [unit tests](tests/test_g8.py). **Independent held-out reproduction:** [GitHub Actions run 41416660126](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41416660126), passing CI with complete per-seed artifact `g8-frozen-heldout`.

## Scientific question

G7 represented the local stress-memory writer with an auxiliary Poisson potential `z_i`. The spatial mean of z grew every local round, because the periodic Laplacian cannot resolve a constant stress offset. Yet `delta_h=Lz` depends only on **differences** of z. That suggests a gauge redundancy rather than a necessary physical reservoir.

Define oriented edge flux `q_i=z_i-z_(i+1)`. The equivalent local rule is

```
q_i <- q_i + 0.2 * [(r_i-r_(i+1)) - (2*q_i-q_(i-1)-q_(i+1))]
delta_h_i = q_i-q_(i-1)
```

All update operations involve neighbouring stresses and neighbouring edges. `sum(delta_h)=0` by telescoping. No global mean, stored absolute z, or global projector exists inside the edge writer. **This is an elementary discrete differential identity, not an unprecedented learning law.**

## Frozen comparison

Both K8 and K48 use eight fresh seeds, 2200–2207, 310 fast steps, a trained per-patch stress baseline, a 2%-RMS externally supplied ideal numerical adjoint teacher, and a matched 0.025-norm evaluation material step. K8 uses 64 neighbour exchanges; K48 uses 4096. The existing original potential relay and external global projection are *referee controls*, not edge computation.

| Measurement | Result |
|---|---:|
| Largest relative difference, edge writer vs G7 z writer (16 cases) | **6.96e−13** |
| Worst total-material sum error | **2.13e−14** |
| Largest absolute mean q state | **4.26e−15** |
| K8 original z mean magnitude at 64 rounds | **42.62** |
| K48 original z mean magnitude at 4096 rounds | **635.06** |
| K8 gradient cosine of edge writer | **0.999293** |
| K48 gradient cosine of edge writer | **0.999481** |
| Loss-improving cases | **8/8 K8 + 8/8 K48** |
| K8 mean final/initial receiver loss | **0.890794** |
| K48 mean final/initial receiver loss | **0.893021** |

The stable edge-state norm relative to patch-stress residual norm is bounded by the periodic-graph spectral gap:
`||q||/||r|| <= 1 / [2 sin(pi/K)]`.
Observed mean ratios were **0.677 (K8)** and **3.037 (K48)**; every held-out case remained below the derived bound.

## Explicit capacity limitation

Clipping each individual edge update is local, but the hard cap `B=c max_i |r_i|` is **externally calibrated from a global maximum**. This is an engineering envelope test, *not* a fully local capacity-selection mechanism.

| Cap | K8 relative edge-direction error | K8 mean loss ratio | K48 relative edge-direction error | K48 mean loss ratio |
|---:|---:|---:|---:|---:|
| 0.5 max|r| | 0.13861 | 0.891621 | 0.54797 | 0.913669 |
| 2 max|r| | 0 | 0.890794 | 0.13329 | 0.894560 |
| 16 max|r| | 0 | 0.890794 | 0 | 0.893021 |
| 64 max|r| | 0 | 0.890794 | 0 | 0.893021 |

All 8/8 cases improved at each K for each capacity, but the strong clipping at K48 clearly degrades update quality. A large K costs both latency *and* more dynamic range.

Leaking the edge state each round has its own cost:

| Leak/round | K8 error | K48 error | K8 mean loss ratio | K48 mean loss ratio |
|---:|---:|---:|---:|---:|
| 0.001 | 0.00595 | 0.11238 | 0.890795 | 0.893264 |
| 0.01 | 0.05561 | 0.42515 | 0.890834 | 0.901525 |

All tested leaks still improve receiver loss; their increased directional error is a quantitative physical-memory tradeoff. These relative errors compare with the nonleaky edge relay, not with the ideal gradient.

## Frozen gates: A/B/C pass

- **A PASS:** edge and potential updates agree within 1e-9 and conserve material.
- **B PASS:** the edge-state common mode stays absent and its norm is below the spectral bound.
- **C PASS:** generous fixed-in-run envelope `64 max|r|` never clips and still improves at least 7/8 per K.
- **D/E diagnostic only:** tight caps and leaks measured at the preset values, not tuned to pass.

## What this does NOT establish

The teacher remains a **computed ideal adjoint**. The baseline remembers a stationary forward field, and this benchmark makes **one** material update. It does not address the multi-epoch staleness Claude observed in ComputingBeachClaude's G7, the teacher phase error under damping, fast nonlinear overtopping, or any true sediment mobility law. The norm-matched 0.025 trial step and cap calibration are externally imposed.

The finite edge-state architecture removes one unnecessary nonphysical common-mode divergence. It does **not** establish that real sand, neurons, or passive cavities could realize the entire controller.

## Next useful falsification

Carry over Claude's quiet/loud comparison as an **online, multi-epoch** study with the new edge relay and an explicit slowly adapting stress baseline. Count baseline recalibrations, time needed for edge diffusion and storage capacity; compare matched plain scour, teacher-off, and true-gradient controls. Separately investigate a physically launched teacher through an **open radiating boundary**. Radiation remains energy loss from the computational region; do not assume open means perfectly time reversible.
