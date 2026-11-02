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
