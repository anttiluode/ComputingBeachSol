# G8 preregistration — bounded edge-state relay, eliminating G7's runaway common mode

**Frozen 2026-11-02 before held-out evaluation of K8/K48 seeds 2200–2207.** Development seeds (if required) are restricted to 81–83. The algorithm is a *numerical engineered circuit*, not sediment hydrodynamics or living AIS plasticity. It follows [G6](G6_RESULTS.md), [G7](G7_RESULTS.md), and Claude's independent G6 compliance/G7 sliding-threshold findings.

## Hypothesis

The original G7 potential `z_i` accumulates an unbounded spatially uniform component because the Poisson equation on a periodic ring lacks a zero-mode inverse. Height updates depend only on the differences of z, not the common mode. Can we eliminate the *variable* rather than artificially leak away its mean?

Define oriented edge states `q_i = z_i - z_(i+1)`. For the same per-patch residual `r_i = E_i(u+boost*lambda)-theta_i` as G6/G7, update each edge using its adjacent patch residuals and two neighbouring edge states:

```
q_i <- q_i + 0.2 * ((r_i - r_(i+1)) -
                    (2*q_i - q_(i-1) - q_(i+1)))
dh_i = q_i - q_(i-1)
```

Only neighbour differences are used during the relay. It has no absolute `z`, global mean, or zero-mode driving term; total material is conserved because `sum(dh)=0`. With q initially zero it should give the **same finite-time height update as G7's z relay** at every round, up to floating-point error. This is elementary discrete Hodge/Poisson mathematics, not a new theorem. The magnitude of q is bounded in the fixed finite system under fixed finite r (but can still be physically too large, especially at large K).

The wave teacher is still an externally supplied numerical adjoint, calibrated to 2% of the forward patch RMS; baseline EWMA remains twelve forward-only episodes. K changes the effective patch geometry and stress distribution as in earlier tests.

## Experiments

- K = 8 (64 relay rounds), K = 48 (4096 rounds); eight new seeds per K (2200–2207), 310 fast-wave steps, unchanged G6 targets, same echo loss and norm-matched 0.025 material step as G7.
- Three reference writers: existing `z` relay `Lz` at identical rounds, externally projected global `r-mean(r)` (referee only), and old direct local `local_flux(r)`.
- Edge circuits at fixed relay step 0.2: unbounded q (no clip/leak); q clipped after every update at absolute `B = c*max_i|r_i|` with `c=0.5,2,16,64`; and separately leaky q with per-round `leak = 0.001` or `0.01` and no clip. **IMPORTANT:** the clip capacity is *externally calibrated from global max stress*, not obtainable from neighbour-only edges. It is an engineering diagnostic, not an autonomous local material law. The clip itself is applied independently on each edge.
- An exact generic inequality provides a finite-state benchmark for unbounded edge-q after equilibration: `||q||_2/||r||_2 <= 1/(2 sin(pi/K))` for the stable, zero-initialized ring relay. Report q magnitude, common-mode q, original z mean, clipping fraction and echo-loss ratios. The bound is not an engineered fixed hardware range.
- Include a periodic sinusoidal stress probe to separate slow-mode convergence from echo optimization. Test whether larger K requires more rounds to produce the same projected update.
- Do NOT claim physical boundedness merely from bounded q on these inputs; true bounded capacity, hysteresis, noise and local calibration remain separate engineering questions.

## Pre-registered outcomes

**A / exact edge equivalence:** max relative L2 difference between unbounded q-divergence and original z-Laplacian < 1e-9 across all 16 cases, at respective fixed rounds, and both sum to zero within 1e-9.

**B / no runaway gauge mode:** maximum `||q||_2/||r||_2` satisfies the spectral bound + 1e-8, and |mean(q)| < 1e-9. Report z's potentially runaway common mode separately.

**C / finite cap envelope:** with `B=64 max|r|`, no edge clips in any held-out case, mean relative discrepancy from unbounded q < 1e-8, and norm-matched material update improves receiver loss in >=7/8 cases at each K. This deliberately generous bound is not evidence that tight local memory suffices.

**D / finite capacity stress test:** report loss and direction error at `B=0.5,2,16` with no tuning; no pass threshold, because clipping could preferentially remove useful spatial patterns. Any observed failure must remain visible.

**E / state leak tradeoff:** report leakage `0.001`, `0.01` separately, plus task losses and comparative projection errors; no directional claim preregistered. It tests the physical price of forgetting against the exact edge circuit.

The decisive new result, if A–C pass, is only that a **gauge-invariant, neighbour-only, finite-amplitude edge representation** removes the runaway *common* mode. It does not establish an autonomous physical writer or solve the damped-wave teacher problem Claude observed.
