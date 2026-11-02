# G9 site experiments — stress-memory rest versus an external agent (2 November 2026)

**Source and frozen protocol:** [SITE_G9_PROTOCOL.md](SITE_G9_PROTOCOL.md), committed first at `1b198f4`, with the supplementary fixed eight-seed rest extension committed at `efe2714` before measurement. Both tests use **the independent synthetic 48-node complex tridiagonal wave model**, *not* physical sand, not the 288-cell finite-difference shore, not Claude's 2D floor and not Sol's G6–G8 Robin-wall benchmark.

**Runnable pages:** [Memory Drift / rest audit](online.html) and [Judge the Shore / trial agent](trial.html). The sites compute their own results locally, with no services or model weights. They are exploratory numerical instrument tests; no preregistered pass bars are retroactively introduced.

## A. Eight-seed agent learns under loss by keep/revert

[CI receipt 41420352959](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41420352959) completed successfully and archived the *complete 80 seed×task×shape histories*. Seeds `1001,1009,1013,1019,1021,1031,1033,1039`; both objectives, 200 proposals per seed, max magnitude `0.0025`, damping `0.07`. Each agent candidate is evaluated by a new wave-operator solve. Accept an improving receiver-power change, otherwise restore the entire bed exactly. **No teacher or adjoint is used in the agent arms.**

| Shape | Quiet median receiver power ΔdB (negative good) | Loud median ΔdB (positive good) | Avg accepted: quiet/loud |
|---|---:|---:|---:|
| Smooth noise (4 local averaging passes) | −5.4869 | **+8.4349** | 90.75 / 105.25 |
| Wave-shaped storms (intensity from randomly sourced steady wave) | **−5.8258** | +7.2951 | 92.875 / 102.375 |
| White noise | −5.2668 | +6.6735 | 97 / 100.75 |
| Conserved smooth noise (spatial mean removed) | −5.4900 | +7.9582 | 96.375 / 101.375 |
| Conserved storms | −4.4776 | +4.8914 | 102.5 / 96.5 |

**Interpretation:** All methods improved their own goal, which is guaranteed by the external judge's accept/revert rule. Storms narrowly won quieting while smooth noise won amplification. Conservation weakened storm proposals but scarcely changed the quieting performance of smooth proposals. These modest improvements differ from Claude's −46.9/+11.5 dB smooth-noise results because the models and objectives differ; no cross-model equality was predicted.

**Computation:** 201 receiver solves per seed×shape×task (one initial + 200 trial reads). Storms additionally need 200 source-wave solves to generate their candidate shape. For each eight-seed aggregate, that is 1,608 receiver solves for one shape and task; another 1,600 wave solves for storm generation. An external judge, writable rollback memory and nonconserving proposals are engineering privileges, not environmental properties.

## B. The extra cost of physical-style teacher-free rest

[CI receipt 41420776426](https://github.com/anttiluode/ComputingBeachSol/actions/runs/41420776426) completed successfully and archived all cases. Same eight seeds, 20 epochs, step 0.0005, teacher coefficient 0.003, theta memory timescale T3. Both quiet/loud targets, at loss=0 and loss=0.07.

- **Frozen θ:** θ remains the initial forward-wave energy forever.
- **Teacher-tracking θ:** θ is updated toward the teacher-on energy after each write. Can absorb teaching.
- **Privileged teacher-free reset:** after each write, one extra teacher-free solve sets θ **exactly** to normal stress of the **frozen** new bed. Bed is not allowed to move during the reset. This is a code-assisted upper control.
- **Material-moving rest:** after the teacher write, a forward-only rest wave generates a second local G8 edge-relay material update. θ then relaxes toward the resulting bed's teacher-free energy, with T3. This requires **at least two additional forward-only solves**, an **extra bed update**, and an externally scheduled teacher/rest switch.
- **Exact-gradient control:** numerical oracle with a globally projected sensitivity, not physical writing.

*Median receiver-power ΔdB*, negative good for quiet, positive good for loud:

| Writer | Lossless quiet | Lossless loud | Strong-loss quiet | Strong-loss loud |
|---|---:|---:|---:|---:|
| Frozen θ | −1.1979 | +1.0169 | +0.2532 | −0.2512 |
| Teacher-tracking T3 | −1.1998 | +1.0182 | +0.2997 | −0.2904 |
| Privileged reset, bed frozen during reset | −2.2110 | +1.9954 | −0.1612 | +0.1876 |
| **Moving-material rest** | **−2.6035** | +1.8460 | **+0.6894** | **−0.6365** |
| Exact gradient | −2.2341 | +2.0131 | −1.0052 | +1.0092 |

Under **strong loss**, only **1/8** materials improve receiver power with moving-material rest for each target; **8/8** improve slightly under privileged code-assisted reset. At zero loss, the material-moving rest improves 8/8 for both tasks, but this is **not equal-resource** to other arms because rest adds another material update. These medians are not ratios to Claude's gradient-descent optimum.

**Important target distinction:** The loud online target is *twice the original complex receiver amplitude*. The site's task loss `0.5 |u_receiver − target|²` is **not** the same as directly maximizing receiver power; this report displays receiver-power dB while the page also reports relative *complex-target* loss. The agent page, in contrast, optimizes receiver power directly for both quiet/loud objectives.

## C. Conclusions and claim limits

Claude's warning was justified: an ideal stress-memory reset can be unusually effective because it freezes the bed and installs a perfect new baseline. A more physical rest exposure that is allowed to move material can destroy that benefit under loss. This tested rest is only one possible transport and adaptation law; it does not prove that all naturally habituating substrates fail.

The agent controls provide a different route to learning under damping, by measuring the actual effect of each trial. However they require **external objective evaluation, reversible bed edits and persistent agent state**. Calling this autonomous natural sand learning would be incorrect.

The G9 browser models do **not** solve the physical backward-wave/adjoint problem, calibrated real sediment transport, sparse energy budget, open-boundary radiation, or fast nonlinear wetting/overtopping. The best next gate is a finite, actually local low-cost baseline/habituation scheme that cannot secretly freeze the material during rest—and a fair accounting of how many waves, teacher measurements and material reversions each successful learning step requires.

**Do not hype. Do not lie. Just show.**
