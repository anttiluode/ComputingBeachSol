# Round 3 — What the beach can read, and what a teacher wave can actually write

**2 November 2026. Source:** [ComputingBeachSol](https://github.com/anttiluode/ComputingBeachSol). The three experiments are pinned by the protocols [PREREG_ROUND3.md](PREREG_ROUND3.md) and [PREREG_G2D.md](PREREG_G2D.md). All numerical results below refer to a synthetic, discretized WallMemoryLaw Robin-wall material, **not literal sand or an experimentally verified fluid writer**.

## 1. K-resolution and listening-time sweep — G1b

The original G1 held-out test was limited to **K=8** and the fixed time interval [120,290). The question here is whether the same model still reads the order of two writes with K=16,24,48, and whether a listening window after arrival is more useful than a late window.

A fresh wave starts from rest for each event. **Material alone persists** between A and B. We additionally test ABX vs BAX, in which the final strong wave X is identical in both histories. At each K, sixteen training seeds (1100–1115) and thirty-two new held-out seeds (41000–41031) are used; each seed creates both history labels. The reader has access to three point-receiver waveforms and uses only the training-set centroid-difference classifier. Gaussian test noise is 4% of the training *early-window* echo RMS.

Arrival was measured from a **label-free flat wall** at step **122** for all three sources. Our four windows are:
- Pre-arrival [12,112) (no detectable signal),
- Early [112,292),
- Late [292,472),
- Whole [0,510).

No window was selected by maximizing test accuracy. Early and late windows have the same length. The listening-window rule in WallMemoryLaw is a *causal support and calibration-complexity ceiling*, not an assertion that early time must maximize classification accuracy.

| K | AB early | AB late | ABX early | ABX late | ABX whole |
|---:|---:|---:|---:|---:|---:|
| 8 | 93.75% | 100% | 95.31% | 100% | 100% |
| 16 | 100% | 100% | 100% | 100% | 100% |
| 24 | 92.19% | 100% | 82.81% | 100% | 100% |
| 48 | 73.44% | 100% | 76.56% | 95.31% | 92.19% |

All pre-arrival conditions report 50%, because the waveform has zero class-discriminating direction and the classifier uses an explicit *uninformative tie* policy. This is not a stochastic discovery of exactly chance accuracy.

**What survives.** The common final X wave does **not** automatically erase which of A/B came first: ABX vs BAX remains decodable even at K48, where the late-window accuracy is 61/64 = **95.31%**. At K8/16/24, late ABX is 64/64.

**What fails as a generalization.** Early windows do *not* always read better; late windows often read far better. A later echo can contain more phase-separated or repeated interactions, even though it also contains higher scattering order. That result is compatible with WallMemoryLaw's causality, but contradicts any simplistic "shorter always means easier" reading of it.

**Feedback control.** Freeze the wave operator to the original material for all writes but allow signed material updates to accumulate. AB/BA and ABX/BAX then produce final states identical up to **3×10⁻¹⁵** at both K8 and K48. The order distinction depends on material feeding back into propagation, not mere additive exposure.

**Critical confound:** K varies the physical patch dimensions and averaging as well as the number of parameters. Mean total transport per write rises from ~95 (K8, AB) to ~1275 (K48, AB); these are proxy quantities, not calibrated sediment mass. The model therefore **does not isolate parameter count** as the cause of changing early accuracy. A future strictly matched-transport K sweep would need to hold integrated stress/transport constant, rather than interpret this row as pure dimension scaling.

The pre-registered R1–R5 outcome is PASS in this toy protocol; each actual accuracy and proxy-transport measurement is in [round3_summary.json](results/round3_summary.json).

## 2. G2c — the quadratic field product is correct, but conservation remains difficult

The G2b failure used an odd signed velocity-contrast transport law. G2c replaces the candidate writer by a contrast between two **integrated patch energies** measured under a numerically calculated ideal adjoint teacher:

```
E_plus(i)  = SUM[t,x in patch i] (u + alpha*lambda)^2
E_minus(i) = SUM[t,x in patch i] (u - alpha*lambda)^2
contrast(i) = (E_plus(i) - E_minus(i)) / (4*alpha)
```

This is the exact patch integral of `u*lambda` in the no-threshold regime, the quantity appearing in the verified discrete Robin gradient. **The subtraction is performed externally by the experiment.** An ordinary beach under two separate exposures does not subtract their effects by itself.

Sixteen unused held-out seeds (900–915), K8, and a 2%-of-forward-wall-RMS teacher field produce:

| Candidate direction | Mean cosine against negative projected gradient | Reduces echo loss |
|---|---:|---:|
| Two-phase contrast, mean-projected | **+0.999992** | **16/16** |
| Local conservative downhill contrast-flux | **−0.840988** | **0/16** |
| Forward-only natural erosion (unconstrained) | +0.1043 vs projected gradient | 11/16 |

The mean-projected contrast follows the gradient and reduces echo loss. The physically more sand-like *local* flux `delta_h = Lap(contrast)` moves in the opposite direction. Threshold cutoffs of 0.25, 0.5 and 0.75 of median forward integrated patch energy eventually degrade the match; at cutoff 0.75 mean cosine is **0.7842**. The preregistered E1–E4 diagnostics pass.

**Important G2c failure and correction:** E5 required contrast to beat *unconstrained* forward-only erosion in at least 12/16 seeds. It beat it in only **8/16**, and E5 stays FAIL in the ledger. This was a flawed direct comparison: the contrast was constrained to zero net material change, while natural erosion was free to lower *all* wall heights together. A simple cosine against the projected gradient does not capture this unconstrained uniform component. The original result is not retrospectively reclassified.

## 3. G2d — correctly matched conservation control, independently pre-registered

Before G2d seeds **1200–1215** were evaluated, we committed [PREREG_G2D.md](PREREG_G2D.md) to specify new equal-mass and equal-update-length controls. Both contrastive and natural erosion candidates now subtract their own means, conserving total material, and both use the same 0.025-norm height update. The two-phase teacher is still numerical and its contrast still computed externally.

| Held-out G2d | Two-phase teacher contrast | Mean-projected forward-only erosion | Mean-projected single-exposure erosion |
|---|---:|---:|---:|
| Gradient cosine | **0.999986** | 0.5060 | 0.4926 |
| Loss decreases | **16/16** | 14/16 | 14/16 |
| Mean final / original loss | **0.8877** | 0.9438 | 0.9458 |
| Paired comparison | — | Teacher beats in **16/16** | Teacher beats in **16/16** |

All four new preregistered D1–D4 tests pass. The local **conservative downhill flux** remains a separate failed candidate, mean cosine −0.856 and no loss decreases.

**Interpretation:** This establishes a genuine improvement of the **two-exposure, externally processed, mean-projected numerical teacher update** over two fair, equally material-conserving null updates, in this specific toy task. It **does not** establish an autonomous physical material learning mechanism: a numerical adjoint was used to generate the teacher; software subtracted the two measured energies; and a global mean projection imposed conservation rather than a local physical sediment flux.

## 4. What to build next

The research bottleneck has become unusually precise: find an implementable *local*, conservative physical rule that preserves enough of the measured `u*lambda` direction **without relying on external two-exposure subtraction and global redistribution**. Lossy receiver-injected adjoints, realistic sediment shear, and wave-time overtopping are all separate physical challenges. The two GitHub projects should not merge away their negative results.

The strongest scientific result currently is narrower but robust: **in a wave cavity, material-to-wave feedback stores event order; an appropriately observed late echo can recover it after an additional shared write. A mathematically matched interference signal can guide a constrained update when external contrast and redistribution operations are allowed.**

## Reproduction

```powershell
cd D:\anttiluode\ComputingBeachSol
git pull
python3.13 -m pip install -r requirements.txt
python3.13 -m unittest discover -s tests -v
python3.13 -m beach.energy_writer --phase confirm
```

For G1b all K cases, use the deterministic `beach.g1b_batch` runner in the repository, or run the [GitHub Actions full reproduction](.github/workflows/confirm-round3.yml), which writes the original unrounded per-seed echo score ledger as a downloadable workflow artifact.

**Ledger discipline:** PREREG_ROUND3 was committed before the first K/G2c held-out observations; PREREG_G2D was committed before the new equal-mass control seeds were evaluated. Earlier G2b and G2c failures are preserved, not overwritten.

*Do not hype. Do not lie. Just show.*
