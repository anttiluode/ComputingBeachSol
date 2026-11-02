# Beach AI lab — model contract and tests (2026-11-02)

This is a **standalone interactive tab/page** inside ComputingBeachSol, not a retrofit of the existing 288-cell shore or the Robin-wall Python benchmark. Its purpose is a visibly calculable demonstration of **fast-weight associative memory**, routing, and attention across four connected writable wave media. The analogy is intentional; performance claims must not imply a physically realized brain, photon chip, or new AI algorithm.

## Mechanism

Each of four beaches contains one fast water state `u(x,t)` with a damped 1D nearest-neighbour wave recurrence, and one persistent material profile `h(x)` with 36 cells. Three incident frequencies (LONG, MID, SHORT) encode one-hot keys. Six orthonormal spatial Fourier profiles (cosine and sine quadratures for three bands) encode a 3x2 associative matrix **inside the material**. The response of a local query is computed by projecting h onto these profiles and multiplying by the query key. This is an **effective readout**, not a measured solution of the fast water PDE; the wave display is an accompanying propagation model, not a hidden trained neural network.

- Strong-wave teaching updates h by `eta * target ⊗ key` in Hebbian mode or `eta * (target - W key) ⊗ key` in Delta mode. Both change the **actual material coefficients** used to read later queries.
- Weak probes do not call material-writing code.
- Neighbour links transmit wave displacement at their boundaries and forward query access; optional **relay teaching** deliberately writes attenuated copies to immediate neighbours. There is no automatic backpropagation, physical adjoint, or claimed spontaneous tutoring.
- A frequency-based, weighted multi-beach read is computed from port reachability and content-dependent resonance strength. Turning off attention uses just reachability-normalized mixing. The attention softmax is explicit external computation; it is not spontaneous physics.
- Finite retention/overwrite, key collisions, and loss of locality are displayed. Frequency is only an address, not a guaranteed unique memory.

## Acceptance checks, before implementation

1. Orthonormality of six band quadratures. A one-hot write to A changes only intended frequency/output coefficient in A when neighbour-teaching is off.
2. Weak query of selected beach does not change any material state, even if network links are on.
3. Network routing from beach A can read a memory in a remote beach when connected; disconnected access cannot.
4. Repeating identical writes shows Hebbian amplification and bounded delta convergence. For same-key conflicting lessons, summed Hebbian writes commute (AB=BA), while delta writes do not (AB≠BA).
5. Optional relay teaching changes adjacent beaches only, at attenuated learning rate.
6. All values and scores displayed in the page come from the running model's state and computations; there are no baked-in result constants or success graphics.
7. GitHub Pages and unit tests run in Actions. The page remains runnable offline with only local HTML+JS.

**Boundary:** This is a transparent software realization of fast weights suggested by the beach; it cannot establish that actual sand, waves, puddles, neuronal dendrites or optical materials implement the delta rule automatically. It is also not a comparison against DeltaNet or Titan model benchmarks.
