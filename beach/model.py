"""Thresholded, mass-conserving patch-scale wall model around WallMemoryLaw's solver.

This is an effective *transport proxy*, not Exner sediment hydraulics or Shields
stress. The fast wave stencil and frozen reader are copied exactly from WML.
"""
from dataclasses import dataclass
import numpy as np
from wml.cavity import Cavity, KAPPA, N, DT, C, DAMP, SIGMA


@dataclass(frozen=True)
class Config:
    k: int = 8
    fraction: float = .6
    shape: str = 'ellipse'
    drive: float = 6.0
    threshold: float = .1
    rate: float = .06
    steps: int = 170
    base: float = .5
    noise: float = .015
    read_drive: float = .01
    read_steps: int = 320


class Beach:
    def __init__(self, cfg=Config()):
        self.cfg = cfg
        self.cav = Cavity(K=cfg.k, fraction=cfg.fraction, shape=cfg.shape)
        self.counts = self.cav.counts
        self.weights = self.counts.sum((1, 2))
        self.ins = self.cav.inside.astype(float)
        self.a = 1 + DAMP * DT / 2
        self.b = 1 - DAMP * DT / 2
        self.c2 = (C * DT) ** 2

    def initial(self, seed=0):
        rng = np.random.default_rng(seed)
        v = rng.normal(0, self.cfg.noise, size=self.cfg.k)
        return v - v.mean()

    def kappa_bits(self, h):
        # Bounded passive Robin coefficients, even if signed bed height grows.
        return self.cfg.base + .45 * np.tanh(np.asarray(h) / .45)

    def forcing(self, u, prev):
        velocity = (u - prev) / DT
        patch_v = np.einsum('kij,ij->k', self.counts, velocity, optimize=True) / self.weights
        return np.roll(patch_v, -1) - patch_v

    def transport(self, shear):
        excess = np.maximum(np.abs(shear) - self.cfg.threshold, 0)
        return np.sign(shear) * excess ** 1.5

    def event(self, h, source, drive=None, steps=None, feedback=True,
              write=True, record=False, frozen_kappa=None):
        # Every event resets fast wave state. Material is the ONLY retained state.
        drive = self.cfg.drive if drive is None else float(drive)
        steps = self.cfg.steps if steps is None else int(steps)
        h = np.asarray(h, dtype=float).copy()
        sy, sx = self.cav.sources[source]
        pulse = np.exp(-((self.cav.x-sx)**2 + (self.cav.y-sy)**2)
                       / (2 * SIGMA**2)) * self.ins
        u = drive * pulse
        prev = np.zeros_like(u)
        base_h = h.copy()
        total_flux = 0.0
        active = 0
        peak = 0.0
        out = []

        for _ in range(steps):
            # For fixed material, this is WallMemoryLaw's stencil unchanged.
            bits = self.kappa_bits(h if feedback else
                                   (base_h if frozen_kappa is None else frozen_kappa))
            robin = KAPPA * np.einsum('k,kij->ij', bits, self.counts, optimize=True)
            lap = -(self.cav.neigh + robin) * u
            for ax, s, nb in self.cav._nbr:
                lap += np.roll(u, s, axis=ax) * nb
            nxt = (2 * u - self.b * prev + self.c2 * lap) / self.a
            nxt *= self.ins

            if write:
                shear = self.forcing(nxt, u)
                q = self.transport(shear)
                d = self.cfg.rate * (np.roll(q, 1) - q)
                h += d  # telescopes exactly: signed total material is conserved
                total_flux += float(np.sum(np.abs(q)))
                active += int(np.count_nonzero(q))
                peak = max(peak, float(np.max(np.abs(shear))))

            prev, u = u, nxt
            if record:
                out.append(u[self.cav.receiver])

        return h, {
            'active_interfaces': active,
            'total_transport': total_flux,
            'peak_proxy': peak,
            'trace': np.array(out) if record else None,
        }

    def history(self, sequence, seed=0, feedback=True, write=True):
        h = self.initial(seed)
        hist = []
        for source in sequence:
            h, metrics = self.event(
                h, source, feedback=feedback, write=write,
                # Fixed-operator control must use the SAME original wall in
                # both phases, rather than refreshing the reference each event.
                frozen_kappa=None if feedback else self.initial(seed))
            hist.append(metrics)
        return h, hist

    def read(self, h, source=0, steps=None, drive=None):
        steps = self.cfg.read_steps if steps is None else steps
        drive = self.cfg.read_drive if drive is None else float(drive)
        # A frozen read calls WML's original exact implementation, not ours.
        return self.cav.run(self.kappa_bits(h), source=source, steps=steps)[0, :, 0] * drive
