# ComputingBeachSol — GitHub Pages multiscale wave instrument (November 2, 2026)

**Launch from the repository root:** [`index.html`](index.html). This file contains its own CSS, HTML, JavaScript, wave integrator, conservative local material writer, charts, and downloadable state ledger. There are **no external scripts, network requests, dependencies, servers, or model downloads**. It can be opened in an ordinary modern browser.

**Publish on GitHub Pages:** Repository **Settings → Pages → Build and deployment → Deploy from a branch → `main` → `/(root)` → Save**. GitHub will provide the site when deployment finishes. The expected address *after you enable Pages* is [anttiluode.github.io/ComputingBeachSol/](https://anttiluode.github.io/ComputingBeachSol/). We did not change the repository's Pages settings.

## What it actually calculates

The browser steps a **one-dimensional linear wave equation in a material-dependent medium** with 288 grid sites, two reflecting ends, baseline speed 0.78 cells/time unit, step size 0.46 and damping 0.003. The slow variable `h[i]` modifies local squared wave speed during propagation unless feedback is disabled. Every exposure starts with fast field at rest while material stays.

Three driving spatial modes, `m = 6, 12, 24`, correspond to baseline wavelengths approximately `96, 48, 24` cells (`lambda = 2*(N-1)/m`). The mode-drive option applies a **distributed, deliberately frequency/space-matched resonant force**, proportional to `sin(m*pi*x/(N-1))*sin(omega*t)`. The "incident boundary" option drives **only the leftmost boundary**. These should not be conflated: selecting an ideal standing mode is *not proof* that incident waves autonomously self-sort into anatomical compartments. The two ends also make this a global reflecting cavity rather than an infinite open beach; it has **no interior compartments**.

During 2,304 fast steps per write, local wave-displacement gradients produce a squared-stress proxy; every 12 steps the model computes their average. Before thresholding, this proxy is **explicitly spatially averaged** over radii 9, 4, and 0 cells for the long, medium, short mode respectively. This is a model assumption, motivated by scale-dependent mobility—not something derived from fluid equations. Then

```
E_i = averaged squared spatial wave gradient
M_i = max( E_i - 0.00003 * threshold_slider, 0 )
q_(i+1/2) = -0.012*(M_(i+1)-M_i)
h_i <- h_i + q_(i-1/2) - q_(i+1/2)
```

A local per-edge capacity limiter keeps `-0.12 <= h_i <= +0.12`, applying accepted transfers between pairs of sites. Every accepted transfer is exactly mass conserving, with no material added from outside. The first/last few sites are nonmobile near boundary conditions. This is **not** calibrated Shields or Exner sediment transport, and the height variable is signed, abstract effective structure.

**What the visualizations mean:**
- The upper canvas shows the actual evolving wave state and the stored effective height (height display is auto-exaggerated for legibility).
- The **spatial spectrum** is the Fourier power of the *material array itself*, not a claim about an acoustic receiver. Coarse peaks are at lower spatial wavenumber.
- **Weak read** simulates three actual, weak *boundary-driven* harmonic waves in the current frozen bed, then in a blank reference bed, with identical 1,500-step observation lengths. The instrument displays the normalized absolute **difference in receiver output RMS**. A read does **not call the material-update code**, so it is nondestructive by construction. This is a frequency-addressed transfer measurement, **not a trained decoder** or G1's 96.9% AB/BA accuracy.
- **AB vs BA / ABX vs BAX** launch two or three identical-strength exposures in different orders and compare material L2 distances under three variants: wave/material feedback with a bounded writer, **fixed wave operator with the same nonlinear bounded writer**, and **fixed wave operator with an unbounded additive writer**. The middle control can still remember order, because the material's capacity is nonlinear! The final fixed/unbounded control should commute to numerical precision. These are **not** the held-out 2D Robin-wall benchmark; the web page demonstrates mechanisms and pitfalls in an independent simplified model.

## Measured local browser checks (default settings, not pre-registered results)

Tested in headless Chromium using actual button clicks and JavaScript console-error capture, at desktop and 390px mobile width.

- Flat starting bed: zero material mass and no stored spectral peak.
- After one resonant long write: the intended `k=6` is the largest material Fourier component and contains approximately **64.6%** of sampled `k=1..42` Fourier power.
- Long → Medium → Short: 3 material writes, signed mass drift below **2e-15**. The sampled final spectrum contains peaks at `k=12` (~36.9% of tracked power) and `k=24` (~25.3%); older low-frequency content may be overwritten.
- Weak read: new frequency-dependent receiver RMS deviations were measured versus the flat reference, while the material array stayed bitwise unchanged.
- A strict order control on the same default model gave an AB/BA material L2 distance around **2.6e-14** for the *fixed-operator/unbounded writer*. The *fixed-operator/bounded writer* still gave a nonzero distance (~0.87) because of local capacity saturation; this is **not** evidence for wave feedback. The feedback-enabled, bounded case gave a different nonzero distance (~1.93).
- The mobile page has no horizontal overflow; there were no browser JavaScript exceptions in the automated checks.

These figures describe one deterministic demonstration and can change when sliders, drive mode, writing order, or model constants change. They must **not** be presented as held-out scientific validations.

## What we carried from September

[ObjektiYksi](https://github.com/anttiluode/ObjektiYksi) treated frequency and input ports as ways to interrogate **one persistent structure**. Its keep/revert, mass-conserving material learner had no direct adjoint and remains a valuable untested experiment for the beach. The September resonant-cavity/dendrite work motivates looking at *spatial modes rather than isolated individual edits*. This standalone page makes that connection tangible but doesn't implement the old Gates 2–3 optimizer.

The two November numerical lines remain distinct:

- [ComputingBeachSol](https://github.com/anttiluode/ComputingBeachSol): G1 order-memory controls, Robin-wall adjoint, negative natural teacher writer, positive **externally contrasted** energy update with fair baselines.
- [ComputingBeachClaude](https://github.com/anttiluode/ComputingBeachClaude): distributed shallow-water floor, difficult readable echo task, loss-limited physical teacher, and distinct transport tests.

The next physically meaningful questions are whether unshaped incident waves form narrowband gratings robustly, whether multiple gratings can coexist without catastrophic rewriting, and whether a *genuinely local* conserved update can improve a transfer objective using only delayed success/failure (ObjektiYksi's keep/revert idea). **Nothing on this page demonstrates autonomous backpropagation or a neuron.**


## November 2 extension — online memory drift lab (separate numeric instrument)

The standalone [Memory Drift lab](online.html) runs beside the existing shore page, linked from the index navigation and the hero. It loads one local `online.js`, has no remote services or dependencies, and leaves the 288-cell shore experiment unchanged.

### The model, not the metaphor

**Different numerical engine.** The extension uses 48 coupled complex steady-state oscillators, with a tridiagonal wave operator `A(h,ω,γ)`. It solves `A u=F` at each material update using the Thomas tridiagonal solver. Source = node 3; receiver = node 44; the material enters the operator's real diagonal and changes propagation. The dissipation parameter appears as an imaginary diagonal term. This is a frequency-domain toy wave *operator*, not calibrated coastal hydraulics, not the original 288-cell time-stepping page, not Claude's 2D floor, and not the frozen Python Robin-wall G6–G8 benchmark. It has no sand-exchange physics, hydrodynamic overtopping, or calibrated scattering/radiation boundaries.

Receiver loss is `J=0.5*|u_receiver-target|²`. Quiet targets zero complex receiver amplitude. Loud targets double the complex initial receiver amplitude, fixed across training. Each arm gets 20 online updates to the same initial rough material. A numerical teacher is produced by driving the receiver with the current complex error; its spatial field is `tau_i=beta*G_i,receiver*(u_receiver-target)`. That is an actual receiver-source wave-operator solve but is **not** generally the correct physical adjoint in dissipative media.

The local eligibility signal is `r_i=|u_i+tau_i|²-theta_i`, where `theta` is the stored teacher-free baseline from the initial material. The **G8-style edge relay** runs 512 nearest-neighbor rounds to obtain conservative material increments. It neither stores an unbounded common potential nor explicitly calculates a global mean during the writer update. A fixed per-step *maximum change* is imposed externally to compare branches fairly; the material is **not** bounded by a physical sediment-capacity law.

The seven controls, all evaluated on the current bed at every epoch, are:

1. Frozen baseline `theta` (staleness).
2. Teacher-tracking baseline with adjustable T, updated toward the combined forward+teacher energy at the new bed (teacher absorption).
3. Teacher-free recalibration on the new bed, requiring **an extra independent forward solve every epoch**.
4. Plain field-energy reinforcement with the same conservative relay (use-dependent baseline).
5. Exact analytic loss gradient with global mean projection (**oracle, not local/physical**).
6. Teacher off with frozen initial baseline.
7. External two-phase subtraction of `|u+tau|²-|u-tau|²` (software reference).

### What the site plots and stores

The two graphs show relative receiver loss and cosine with the exact gradient over 20 episodes. The epoch slider shows the computed material profiles; the table gives initial gradient alignment, epoch-ten alignment and final task loss for all seven arms. Controls change the numerical run, not just a visualization. Export JSON includes all per-epoch material states and metrics.

**Illustrative default, not a preregistered result:** seed 41, no damping, quiet objective, step 0.0005, teacher coefficient 0.003 and T=3. A Chromium and Node smoke check found a frozen-baseline final loss ratio of about **0.752**, compared with **0.596** after teacher-free recalibration, and **0.593** under exact analytic descent. The frozen baseline's gradient alignment decreases during repeated material modification. At seed 777, strong damping 0.07 and loud target, the first teacher gradient cosine is only about **0.12**, and its frozen-baseline final loss rises above the starting loss. These are **site examples** only; they cannot be compared directly to Claude's held-out 2D model or used to claim autonomous sediment learning.

The site exposes a simple `window.__onlineBeachDiagnostics()` for browser smoke tests and its reproducible pure solver via `window.__onlineBeachModel.run(...)`. [`tests/test_online_page.py`](tests/test_online_page.py) checks syntax, controls, live behavior and conservative height updates with fixed illustrative settings. Node tests are skipped when Node is not installed.

**Research interpretation:** the goal is to make Claude's concern inspectable: repeated updates can make a previously calibrated threshold stale, and aggressive teacher tracking can erase useful novelty. The page does not claim to identify a universal optimal memory timescale. The hard challenge still lies in physically generated, loss-aware teachers and a bounded, local and task-aligned material writer.
