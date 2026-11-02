"""Geometry-only shortest two-patch tour and frozen-wall interaction test."""
import numpy as np
from wml.cavity import STEP


def pair_tour(cavity, i, j, source=0):
    a, b = cavity.patch_points(i), cavity.patch_points(j)
    src = np.array(cavity.sources[source])
    dst = np.array(cavity.receiver)
    cross = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1)
    ab = (np.linalg.norm(a-src, axis=1)[:, None] + cross
          + np.linalg.norm(b-dst, axis=1)[None, :]).min()
    ba = (np.linalg.norm(b-src, axis=1)[None, :] + cross
          + np.linalg.norm(a-dst, axis=1)[:, None]).min()
    return float(min(ab, ba) / STEP)


def pair_interaction(beach, h, i, j, delta=.1, source=0, steps=330):
    """Four-read inclusion/exclusion, with a fixed existing background wall."""
    h = np.array(h, dtype=float, copy=True)
    base = beach.read(h, source=source, steps=steps)
    a = h.copy(); a[i] += delta
    b = h.copy(); b[j] += delta
    ab = h.copy(); ab[i] += delta; ab[j] += delta
    return (beach.read(ab, source=source, steps=steps)
            - beach.read(a, source=source, steps=steps)
            - beach.read(b, source=source, steps=steps) + base)
