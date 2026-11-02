# Browser G9 protocol: the price of rest and the external judge

**Frozen 2026-11-02 before implementing/running the eight-seed browser suite.** This is an explicitly *illustrative* experiment on the independent `online.js` 48-site complex tridiagonal wave model, **not** the 2D ComputingBeachClaude G8 or a calibrated physical beach. No success bar is claimed beforehand.

## Questions prompted by ComputingBeachClaude G8

1. Our earlier blue **teacher-free recalibration** updated the slow threshold from a fresh forward-only field but did **not** move bed material. That is an external privilege. How does it compare with a **rest exposure that can move material** while the baseline adapts?
2. Can a separate **trial, measure, keep-or-revert agent** improve a quiet or loud receiver with loss, even when the reciprocal receiver teacher is incorrectly phased?
3. Do white, smooth, wave/storm-shaped, and mass-conserving proposals differ strongly? Note that proposal shape and conserved-total-material are independent factors.

## Frozen numerical rules

Wave network, `N=48`, source node 3, receiver node 44, real material-dependent tridiagonal operator, existing exact complex direct solver. Use loss settings `0`, `0.01`, `0.07` exposed on the page. Teacher-on branch uses the existing `0.003` coefficient, G8 edge-only conservative relay, and max-step `0.0005` over 20 updates. **Rest arm** follows each teacher-on update with one extra teacher-free field measurement. The difference between its forward energy and remembered `theta` moves the bed via the same G8 edge relay, with at most one additional `0.0005` material update, then measures the forward field again and relaxes `theta` toward that measured energy with `T=3`. This is an *externally scheduled teacher/rest gate*, not autonomous physiology. We keep the old privileged recalibration arm as an explicit upper control.

For trial learning fix eight *new* seeds `[1001,1009,1013,1019,1021,1031,1033,1039]` (distinct from the site demos, G6/G7/G8 numerical seeds and Claude's 600–607 beds). At each loss setting run both **quiet** (`minimize |u_receiver|²`) and **loud** (`maximize |u_receiver|²`) objectives for 200 proposals per seed and shape, starting from identical bed per shape. Candidate maximum absolute material step is `0.0025`. Keep only if the new receiver-power objective improves; otherwise restore exactly. No teacher or adjoint is provided to those trial arms.

Proposal families (all use the same per-arm deterministic seeded pseudorandom generator):
- **White:** independent centred noise at each site.
- **Smooth:** 4 passes of local 3-site averaging of white noise (no forced mass conservation).
- **Conservative smooth:** the same smooth proposal with spatial mean removed, pre-normalization.
- **Wave-shaped storm:** intensity of a steady forward field from a random source site, with random sign; **no** external score-gradient.
- **Conservative storm:** same wave-shaped exposure but its spatial mean removed.

Site shows both the median receiver-power change in dB over eight seeds *and* acceptance counts, per-arm losses and receiver eval counts. Negative dB is success for quiet; positive dB is success for loud. Do **not** compare these directly against Claude's measured numbers: different model, effective wave frequency and targets. Smooth noise may beat storms.

## Integrity checks

- Eight seeds are fixed and enumerated; no selecting best seeds after running.
- For the *agent*, the objective score must never worsen after an accepted proposal; rejected proposal leaves bed bitwise unchanged.
- Trial arms use no `grad`, `theta`, `teacher`, or global oracle: the only global decision is keep/revert after receiver evaluation. Conserving proposals use external per-vector mean removal (this is an intervention, not natural sand).
- Material-read counts are reported separately from storm-proposal wave solves. 200 candidates means 201 receiver-read solves per seed/shape plus additional storm generation.
- The active physical-rest arm (if shown) must count additional forward-only wave solves, extra material movement, and an externally supplied teacher/rest gate.
- Everything is synthetic and browser-local. No physical teacher propagation, true Exner sediment dynamics, actual open/radiating boundary, or demonstrated agent-free task optimization.
