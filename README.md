# ComputingBeachSol — a wave writes a medium, then a ping reads its history

**G1: executable, source-pinned, held-out test passed in a deliberately simplified model.** A medium with a thresholded, mass-conserving slow wall changes how later waves propagate. Two exposures A and B have identical counts and nominal energy in either order; only the persistent material carries state between episodes.

The challenge comes from [Evening](https://github.com/anttiluode/Evening) (positive scout-written order discrimination), [2729](https://github.com/anttiluode/2729) (negative held-out phase-pair order task), [WallMemoryLaw](https://github.com/anttiluode/WallMemoryLaw) (causal geometric limits on readable wall interactions), and [Arborverb](https://github.com/anttiluode/Arborverb) (verified adjoint for a *different*, scattering-waveguide model). Claude's independent sister branch: [ComputingBeachClaude](https://github.com/anttiluode/ComputingBeachClaude).

**Important:** The beach is presently a **patch-scale numerical analog**, not a hydrodynamic beach. The effective transport is **not** a calibrated Exner/Shields sand law. Nothing here demonstrates actual sediment backpropagation or a new physical effect.

## Status: G1 passes, G2a passes, G2b **fails** in the tested signed-transport model

- **G1 (history)**: 62/64 fresh noisy receiver echoes decode AB versus BA; frozen-operator control 50%.
- **G2a (sensitivity)**: exact discrete Robin-wall gradient agrees with finite differences.
- **G2b (teacher wave)**: a phase-aligned, externally amplified numerical adjoint teacher does **not** give reliable gradient-directed sediment motion. The isolated interference-induced change has mean cosine **−0.241** with the projected descent gradient across 16 held-out cases; teacher-on beats forward-only in only **5/16**.
- **G3 (fast nonlinear waves)**: not yet tested.

[Read the G2b negative-result report](G2B_RESULTS.md) · [Frozen protocol](PREREG_G2B.md) · [All metrics, seed table](results/g2b_summary.json). The raw full 16 × 5 sweep can be regenerated with `python -m beach.g2b` and is uploaded by [the G2b replay workflow](.github/workflows/confirm-g2b.yml). None of this is real sediment or a physical in-situ backpropagation demonstration.

## Result — G1, frozen before held-out evaluation

[Pre-registered experiment](PREREG.md) was committed in `586ed5b5` before seeds 40000–40031 were evaluated. Development tuning used other seeds. The configuration, locked train/test split, results and provenance are in [results/g1_confirmatory.json](results/g1_confirmatory.json).

| Condition | AB correct | BA correct | Balanced accuracy | Paired swap p |
| --- | ---: | ---: | ---: | ---: |
| **Live wall feedback** | **31/32** | **31/32** | **96.875%** | **0.0001** (floor) |
| Fixed wave operator for both writes | 32/32 | 0/32 | 50.0% | 1.0 |
| Final wall sectors independently permuted | 11/32 | 25/32 | 56.25% | 0.2118 |

The reader sees **only 3 receiver echoes**, sampled at steps [120,290), with fresh additive Gaussian receiver noise equal to 4% of training-echo RMS. It never sees the material vector. Training uses 14 other paired seeds; tests use 32 paired held-out seeds. A paired-label-swap test is used rather than treating the 64 echoes as independent.

The **fixed-operator control** must be defined carefully. The material still accumulates flux, but **both** writing episodes propagate using the exact same initial wall operator. Hence changes add commutatively; mean map AB/BA difference is `9.8e-16`, versus **0.1351** for the live coupled medium (minimum across new seeds 0.1333). Both orders have the same A and B pulses and the fast field is reset to rest between episodes. This isolates the material→wave→material feedback path. In the fixed control the classifier's 50% is not an achievement: its paired waveforms are mathematically identical.

**G1 decisions:** P1 threshold / P2 order material / P3 noisy read **PASS** under the frozen toy-model rules. P4 spatial permutation **PASS** as an intervention: accuracy drops by 40.625 points (it is not a retrained equal-power control). P5 tour-horizon **PASS** for one selected pair: patches (0,3), predicted shortest tour 278.54 steps; before step 238, the two-patch inclusion–exclusion interaction is at most 1.30e-7 of its full-trace peak. This is *not* an exact-zero result or the whole binary calibration-count law.

For representative written walls, a weak drive .01 gives peak wall-velocity contrast <.0039, below the **proxy threshold .1**, and changes every material coordinate by exactly zero. Strong drive 6 produces nonzero transport. This exact nonwriting property follows from the toy's hard threshold, not a guarantee for physical beaches.

## How it works

```
A or B wave → WML wave propagation with CURRENT Robin wall
          → patch velocity contrasts → thresholded signed flux
          → conservative divergence update of bed profile h
          → next wave sees a DIFFERENT Robin wall
       [wave state reset; h alone persists]
After AB or BA: weak receiver ping → original, frozen WML reader
```

The wall stores 8 signed, conserved-total height components. At patch interface i,
`s_i = v_(i+1) - v_i`, with v the patch-averaged change in wave displacement per timestep:

```
q_i = sign(s_i) * max(abs(s_i) - 0.1, 0)**1.5
h_i <- h_i + 0.06 * (q_(i-1) - q_i)
kappa_i = 0.28 * (0.5 + 0.45 * tanh(h_i/0.45))
```

The telescoping divergence conserves `sum(h)` up to floating error (maximum on held-out maps ~2e-15); the smooth tanh bounds the Robin spring to (0.014,0.266), avoiding unstable negative stiffness. **Signed velocity contrast is a deliberately elementary transport proxy**, not actual tangential bed shear or a full spatial discretization of sand. The model is nonlinear on its **writing** timescale; for a frozen material the **reading** wave solver is linear in excitation.

## Run locally (Windows / Python 3.13)

```powershell
git clone https://github.com/anttiluode/ComputingBeachSol.git
cd ComputingBeachSol
python3.13 -m pip install -r requirements.txt
python3.13 -m unittest discover -s tests -v
python3.13 -m beach.experiment --out results/reproduction.json
python3.13 -m beach.g2b --out results/g2b_reproduction.json
```

On other systems, replace `python3.13` with your Python executable. Only NumPy is required. There are no GPU requirements, model downloads or API keys.

The two intact WallMemoryLaw modules `wml/cavity.py` and `wml/law.py` were copied byte-for-byte from [WallMemoryLaw commit `1135aa6`](https://github.com/anttiluode/WallMemoryLaw/commit/1135aa6262873369e9c89761719db4800d4d9be7). The separate `beach/model.py` uses the same wave-stencil coefficients during writing and is checked against the upstream frozen solver in unit tests. Its own sediment update is additional, not upstream physics.

## Open scientific questions

**G2a — the Robin-wall gradient is now independently checked (numerical referee).** `beach/adjoint.py` differentiates the precise WallMemoryLaw two-level finite-difference stencil, rather than incorrectly reusing ArborVerb's edge-gain gradient. Its adjoint computes

```
dJ/db_i = -(C*DT)^2 * KAPPA / (1 + DAMP*DT/2)
          * sum_t sum_x [ counts_i(x) * u_t(x) * lambda_(t+1)(x) ]
```

For the 8-patch, 190-step finite-difference check, relative L2 error is **2.10e-8**, gradient-direction cosine **0.99999999998**, and the local forward/adjoint cross-product algebra matches to ~2e-16 relative error. Source: [G2a ledger](results/g2a_adjoint.json). Unit tests independently check all three sources and upstream forward parity. Run: `python -m beach.adjoint`.

**G2b — tested, negative for the existing writer.** In 16 held-out tasks the G1 signed-velocity transport fails the preregistered teacher-wave criterion. The teacher's *mathematical* local cross term computes the correct gradient, but the thresholded signed flux and its divergence do not preserve that direction. [See full result and caveats](G2B_RESULTS.md). This test used the **numerically calculated adjoint field** as an ideal exposure; it did **not** demonstrate a physically injected time-reversed teacher. A more faithful energy-sensitive Exner/shallow-water model and physical backward excitation are independent open problems.

**G3 — fast wave-time gating.** A frozen linear wave equation is a state-bearing but linear read operator. To get a fast computer, add a physically motivated overtopping or local nonlinear gate and compare with ordinary linear and matched conventional nonlinear baselines. G2a and the **negative G2b numerical teacher-field test** are implemented; a physically injected teacher wave and G3's fast nonlinear gate are not.

**Critical caveats:** the threshold, rate and source choice were designed on development worlds; one geometry, one deterministic toy fluid, 32 paired confirmatory seeds, and a simple centroid reader do not establish broad generality. Repetition on different geometries and stress laws is required. Never confuse finite-difference memory of the material with proof of a novel physical backpropagation mechanism.

*Do not hype. Do not lie. Just show.*
