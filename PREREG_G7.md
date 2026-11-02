# G7 preregistration — the price of local conservation

**Frozen on 2026-11-02 before running G7 held-out seeds 1900–1907.** G6 found that a two-state internal stress baseline enables task-aligned numerical learning only with a **nonlocal mean projection**, while the naive nearest-neighbour `local_flux(r)` fails. G7 asks whether a *different, explicitly modelled local communication state* can approximate the projection while changing height through only conservative neighbour transfers.

## Method / no hidden mean operation in the writer

Given the one-teacher-exposure residual `r = E(u+boost*lambda) - theta` with the same G6 idealized adjoint, twelve EWMA calibration episodes, beta=0.02 RMS and K in `{8, 48}`, introduce an auxiliary patch potential `z`. The **local-only** iteration is

`z_i <- z_i + alpha * [r_i - (2*z_i - z_(i-1) - z_(i+1))]`, `alpha=0.2`.

The periodic discrete positive Laplacian is `L z_i = 2*z_i - z_(i-1) - z_(i+1)`. The final **conservative physical-style height direction** is `dh_i = L z_i`: it arises as a divergence of nearest-neighbour flux, with `sum(dh)=0` at every iteration. No `mean(r)`, global all-to-all message, numerical adjoint or optimizer is invoked **inside the potential update**. (The ideal adjoint is still externally supplied to generate the teacher field; `mean(r)` is computed only by the referee.) Because the zero Fourier mode of L is absent, in the infinite-time limit the *nonzero modes* satisfy `L z = r-mean(r)`. This is standard local diffusion/Poisson relaxation, not a new mathematical discovery.

`z`'s common mode may grow under constant forcing; we will report it, not artificially delete it inside the model. The actual local height direction is insensitive to that common mode. The referee alone norm-matches every nonzero direction to the G6 0.025 step for fair loss comparison. This norm matching is **not part of the autonomous local writer**.

## Fixed tests

- Numeric material seeds 1900..1907 at K=8 and K=48, exact G6 target generation, `steps=310`. Newly held out relative to G2d and G6.
- Local communication rounds N = `0, 4, 16, 64, 256, 1024, 4096`.
- Compare every `L z` with `r-mean(r)` for cosine, unnormalized relative L2 error and task loss after a matched 0.025 step. Score N=0 as an inactive no-op, never normalize a zero direction.
- Explicit spatial stress probe: use `r_i=sin(2*pi*i/K)` at K8 and K48. Compare fraction of ideal projected amplitude captured by N=64; shows the diffusion-time dependence on geometry independently of the trained teacher and readout.
- Negative control: the old direct `local_flux(r)` and a standard teacher-off residual are not optimizers. Do not interpret external `r` computation or global norm-matching as a naturally learned sediment mechanism.
- Retain original G6 outcomes unchanged. No realistic viscosity, in-situ backward teacher, fast overtopping, or calibrated Exner/Shields transport has been added.

## Locked decision rules

G7-A: local height output sums within 1e-9 at all N,K; and N=0 yields an inactive update.
G7-B: at K8,N=64, mean relative projection error <= 0.05 across 8 seeds, and >=7/8 echo losses decrease.
G7-C: on the pure low-frequency sine probe, K8 at N64 captures >99% of projected amplitude, while K48 at N64 captures <30%. This is a geometry/latency test, not a result selected from teacher gradients.
G7-D: for K48,N4096, mean relative projection error <= 0.01 and >=7/8 losses decrease, compared against G6's exact global projection control.
G7-E: for both K8 and K48, the late local update's mean loss ratio must be no worse than the G6 global-projection oracle by more than 0.01, with equal norm. Report raw direction norms and common-mode potential growth.

Failure is an informative bound. A pass would demonstrate a **local, communicating numerical circuit** that enforces conservation; it would not establish spontaneous or passive sand learning. Externally computed numerical teacher, learned θ, and idealized stress writer remain significant engineered assumptions.
