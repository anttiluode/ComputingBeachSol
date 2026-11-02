# ComputingBeachSol — a wave writes a medium, then a ping reads its history


## Live browser experiment — memory drift over 20 exposures

**[Open Memory Drift: live controls and plots](https://anttiluode.github.io/ComputingBeachSol/online.html)** · [Source HTML](online.html) · [Wave-operator JavaScript](online.js) · [Model guide](PAGES_LAB.md).

Claude's ComputingBeachClaude G7 raised the next real difficulty: the remembered normal stress can become stale after several updates, while a rapidly tracking threshold may learn the teacher away. The new separate browser lab recomputes a 48-node **complex wave operator** each epoch and compares seven matched controllers across 20 material updates. It shows receiver loss, gradient alignment, material profiles and an exportable per-epoch JSON ledger. Try **quiet versus loud**, **no versus strong wave loss**, and the baseline-tracking timescale. The page is cross-linked from the original shore animation.

**Claim boundary:** this is a new synthetic browser diagnostic, NOT the main 288-cell beach solver, Claude's 2D sand, the preregistered Python G6-G8 experiments, or real sediment. It uses a reciprocal receiver-launched numerical teaching field and externally matched material steps; a separate teacher-free recalibration control pays an extra forward wave solve. The purpose is to exhibit failure modes, not assert passive beach learning.


## November 2: G8 — replace runaway potential with neighbour-edge memory

**[G8 frozen results](G8_RESULTS.md) · [G8 preregistration](PREREG_G8.md) · [CI reproduction](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41416660126)**

The G7 local Poisson relay carried a numerically divergent **common potential** that never affected material motion. G8 stores oriented neighbour differences `q_i` instead of absolute potential `z_i` and updates them by neighbour-only diffusion. Across **16 fresh held-out K8/K48 cases**, its material updates agree with G7 to **6.96e−13** relative error, remain mass-conserving, and improve receiver loss in **16/16**. The q common mode stays effectively zero. Three preregistered gates pass.

Fixed per-edge caps and leakage were also tested: a tight cap of half the externally calibrated maximum residual causes **54.8%** mean K48 direction error but still improves 8/8 tasks; a 0.01 leak per communication round causes **42.5%** K48 error. These expose latency and finite dynamic range, and the cap's global calibration remains an engineering assumption. As before, the teacher is a **numerical ideal adjoint** and the test is a **single material update**, not genuine autonomous sediment learning or a solution to multi-epoch stale thresholds.

Claude's [independent G6/G7](https://github.com/anttiluode/ComputingBeachClaude) makes the critical complementary point: after multiple updates the learned normal stress becomes stale, the loud-harbour objective largely fails, and damping defeats physical teacher-wave alignment. G8 does not supersede those negative results.


## November 2: G6 and G7 — stress memory and local redistribution

**New, reproducible numerical result:** [G6 frozen test](G6_RESULTS.md) | [G7 frozen test](G7_RESULTS.md) | [G6 protocol](PREREG_G6.md) | [G7 protocol](PREREG_G7.md).

- **G6: 5 of 6 gates passed.** A second slow patch-stress state learned from twelve ordinary exposures makes one idealized teacher-on exposure produce an update aligned with the desired task gradient (mean cosine **0.9971**, **16/16** improved); flipping teacher phase reverses it. The direct nearest-neighbour conservative flux **fails** (**0/16**). The successful G6 step still uses global mean projection and a numerically generated ideal teacher.
- **G7: 5 of 5 gates passed.** A separate local diffusion potential replaces the global projection with strictly neighbour-only communications and conservative pair flux. At K8 it reaches mean relative projection error **0.000234** after 64 local rounds; at K48 it takes **4096 rounds** to reach **4.19e−7**. Receiver loss improves in **8/8** held-out cases at each size. **However, the potential's common mode grows without bound:** physical leak/saturation and real local sensing remain untested.
- Frozen runs in GitHub Actions: [G6](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41414618551) and [G7](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41415181563), each with complete per-seed machine-readable artifacts.

Try `python3.13 -m beach.g6_memory --phase development` and `python3.13 -m beach.g7_local --phase development`. Confirmatory phases reproduce the preregistered test seeds. None of this is literal hydraulic sand, an autonomous physical teacher, or a demonstration of homeostatic learning in living axons.


## Interactive GitHub Pages — the multiscale shore (November 2)

**[Open the standalone HTML wave experiment](index.html)** · [Model guide, exact equations and controls](PAGES_LAB.md).

The new browser page lets you write long (96-cell), medium (48-cell), and short (24-cell) spatial patterns into a single 288-cell material via a **real finite-difference wave update** and a slow thresholded, mass-conserving transport proxy. Its controls include selective resonant-mode versus incident boundary drive, weak frozen frequency readout versus a blank reference, and AB/BA–ABX/BAX order tests with strict fixed-operator/additive controls. The page is mobile-friendly, dependency-free, and does not require the Python experiments to run.

This is an **additional 1D demonstration**, not a port of the 2D held-out G1/G2 numerical experiments. Its ideal mode-shaped excitation and wavelength-dependent stress averaging are explicit assumptions. The local bounded transport can itself create order effects independently of bed-to-wave feedback, and the page shows that confound rather than hiding it. Physical readback is measured from receiver waves, never inferred directly from the material spectrum.

**To enable the site:** Settings → Pages → Deploy from a branch → `main` / `/(root)`. Once published, the expected address is `https://anttiluode.github.io/ComputingBeachSol/`.


**G1: executable, source-pinned, held-out test passed in a deliberately simplified model.** A medium with a thresholded, mass-conserving slow wall changes how later waves propagate. Two exposures A and B have identical counts and nominal energy in either order; only the persistent material carries state between episodes.

The challenge comes from [Evening](https://github.com/anttiluode/Evening) (positive scout-written order discrimination), [2729](https://github.com/anttiluode/2729) (negative held-out phase-pair order task), [WallMemoryLaw](https://github.com/anttiluode/WallMemoryLaw) (causal geometric limits on readable wall interactions), and [Arborverb](https://github.com/anttiluode/Arborverb) (verified adjoint for a *different*, scattering-waveguide model). Claude's independent sister branch: [ComputingBeachClaude](https://github.com/anttiluode/ComputingBeachClaude).

**Important:** The beach is presently a **patch-scale numerical analog**, not a hydrodynamic beach. The effective transport is **not** a calibrated Exner/Shields sand law. Nothing here demonstrates actual sediment backpropagation or a new physical effect.

## November 2 follow-up — resolution, common-tail memory and gradient-matched writing

**[Read the complete Round 3 report](ROUND3_RESULTS.md)** · [Frozen K/G2c protocol](PREREG_ROUND3.md) · [Frozen fair G2d protocol](PREREG_G2D.md) · [Machine-readable results](results/round3_summary.json) · [Fair G2d results](results/g2d_summary.json).

**G1b/c (32 paired held-out seeds per resolution):** ABX versus BAX with an identical strong final wave X is recovered from *late* receiver echoes at **100%, 100%, 100%, 95.3%** for K = **8,16,24,48**, respectively. Early-window ABX accuracy is **95.3%, 100%, 82.8%, 76.6%**. All first arrivals are at step 122; no-signal pre-arrival decoding is an informed tie scored 50%. Fixed-operator writes commute to within 3e-15. **K is not a pure dimensionality intervention:** it also changes patch widths and markedly changes transport activity. Late echoes beating early echoes does not refute the causal scattering-tour limit.

**G2c (16 held-out seeds):** two-phase energy contrast with an *ideal numerical adjoint* matches the projected negative gradient (cosine **0.999992**), and improves echo loss 16/16. The actually local conservative downhill flux **fails** (cosine −0.841; 0/16 improvements). Original E5 comparing conserving contrast against **unconstrained** natural erosion failed 8/16 and remains failed; that control was not equally mass-constrained.

**G2d (16 new held-out seeds, frozen separately):** fair comparison against **mean-projected natural erosion** passes: gradient-matched contrast beats the conserving natural writer **16/16**, and beats conserving single-exposure erosion **16/16**, at equal material step norm. **Still not autonomous physical learning.** The teacher is numerically generated, two energy measurements are subtracted externally, and mass projection is global rather than a local sediment flux. None of the work models calibrated real sand.

Reproduce locally:

```powershell
python3.13 -m beach.g1b_batch --gather --out results/g1b_reproduced.json   # after batch caches are generated
python3.13 -m beach.energy_writer --phase confirm
python3.13 -m beach.g2d
```

The [round3](.github/workflows/confirm-round3.yml) and [G2d](.github/workflows/confirm-g2d.yml) GitHub Actions workflows build/verify the complete frozen held-out ledgers automatically.

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
