"""G7: local diffusion/Poisson relay for mass-conserving stress-memory writing.

The teacher and patch energy are the same idealized numerical inputs as G6.
Only the *redistribution* circuit is local. A potential z diffuses between
neighbouring patches, driven by a locally measured energy residual r; local
flux divergence changes bed height, preserving total mass without an explicit
mean or all-to-all operation in the writer. Finite-time cost is measured.
See PREREG_G7.md for locked tests and honest physical claim limits.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from .adjoint import propagate, loss_and_gradient
from .energy_writer import local_flux, angle
from .g6_memory import (patch_energy, remember, teacher_boost, project,
                        score, CALIBRATION_EPISODES, ALPHA, STEP_NORM, STEPS)
from .model import Beach, Config
from .teacher import adjoint_snapshot

ROUNDS = (0, 4, 16, 64, 256, 1024, 4096)
RESOLUTIONS = (8, 48)
RELAY_ALPHA = .2


def lap(z):
    """Positive periodic graph Laplacian L=2I-S-S^-1."""
    return 2 * z - np.roll(z, 1) - np.roll(z, -1)


def relay(raw, num_rounds, alpha=RELAY_ALPHA):
    """Local potential communication; no mean/subtraction of global material.

    The *only* communicated state is each patch's two neighbours' z.
    The final height update is the divergence of a pairwise edge flux.
    """
    r = np.asarray(raw, dtype=float)
    z = np.zeros_like(r)
    for _ in range(num_rounds):
        z += alpha * (r - lap(z))
    return lap(z), z


def relative_error(x, ideal):
    return float(np.linalg.norm(x - ideal) / max(np.linalg.norm(ideal), 1e-30))


def harmonic_probe(k, rounds=64):
    x = np.sin(2*np.pi*np.arange(k)/k)
    d, z = relay(x, rounds)
    return dict(fraction_of_ideal=float(np.dot(d, x) / np.dot(x, x)),
                relative_error=relative_error(d, x),
                material_sum_error=float(abs(d.sum())))


def run_case(k, seed, steps=STEPS):
    beach = Beach(Config(k=k))
    seed = int(seed)
    h = beach.initial(seed)
    rng = np.random.default_rng(seed)
    target_h = h + rng.normal(0, .21, size=k)
    target_h -= target_h.mean() - h.mean()
    source = seed % 3
    bits = beach.kappa_bits(h)
    target, _ = propagate(beach.cav, beach.kappa_bits(target_h),
                          source=source, steps=steps)
    u, lam, _ = adjoint_snapshot(beach.cav, bits, target, source=source)
    loss, gb, _ = loss_and_gradient(beach.cav, bits, target, source=source)
    ideal = project(-gb / np.cosh(h/.45)**2)
    base_energy = patch_energy(beach, u)
    theta = remember(np.zeros_like(base_energy), base_energy,
                     CALIBRATION_EPISODES)
    plus = patch_energy(beach, u + teacher_boost(beach, u, lam) * lam)
    raw = plus - theta
    oracle = project(raw)
    oracle_score = score(beach, h, oracle, source, target, loss, ideal)
    old_flux = score(beach, h, local_flux(raw), source, target, loss, ideal)
    stats = {}
    max_mass = 0.
    for n in ROUNDS:
        d, z = relay(raw, n)
        max_mass = max(max_mass, float(abs(d.sum())))
        s = score(beach, h, d, source, target, loss, ideal)
        stats[str(n)] = dict(relative_projection_error=relative_error(d, oracle),
                             projected_fraction=float(np.dot(d, oracle) /
                                                      max(np.dot(oracle,oracle),1e-30)),
                             potential_common_mode=float(z.mean()),
                             direction_norm=float(np.linalg.norm(d)),
                             **s)
    return dict(seed=seed, k=k, source=source, initial_loss=float(loss),
                raw_norm=float(np.linalg.norm(raw)),
                oracle=oracle_score, old_flux=old_flux,
                max_conservation_error=max_mass, stages=stats)


def summary(rows):
    out = {}
    for k in RESOLUTIONS:
        subset = [r for r in rows if r["k"] == k]
        stages = {}
        for n in ROUNDS:
            observations = [r["stages"][str(n)] for r in subset]
            stages[str(n)] = {
                "mean_relative_projection_error": float(np.mean([
                    s["relative_projection_error"] for s in observations])),
                "mean_gradient_cosine": float(np.mean([
                    s["cosine"] for s in observations if s["cosine"] is not None]))
                    if n else None,
                "improved": sum(s["loss_ratio"] < 1 for s in observations),
                "mean_loss_ratio": float(np.mean([
                    s["loss_ratio"] for s in observations])),
                "mean_projected_fraction": float(np.mean([
                    s["projected_fraction"] for s in observations])),
                "mean_absolute_common_potential": float(np.mean([
                    abs(s["potential_common_mode"]) for s in observations])),
            }
        out[str(k)] = {
            "oracle_mean_loss_ratio": float(np.mean([r["oracle"]["loss_ratio"] for r in subset])),
            "oracle_improved": sum(r["oracle"]["loss_ratio"] < 1 for r in subset),
            "old_flux_mean_loss_ratio": float(np.mean([r["old_flux"]["loss_ratio"] for r in subset])),
            "stages": stages,
        }
    sine8 = harmonic_probe(8, 64)
    sine48 = harmonic_probe(48, 64)
    mass_error = max(r["max_conservation_error"] for r in rows)
    k8 = out["8"]["stages"]
    k48 = out["48"]["stages"]
    g = {
        "G7_A_local_conservation_and_zero_rounds":
            mass_error < 1e-9 and
            all(r["stages"]["0"]["applied"] is False for r in rows),
        "G7_B_K8_at_64":
            k8["64"]["mean_relative_projection_error"] <= .05 and
            k8["64"]["improved"] >= 7,
        "G7_C_spatial_latency":
            sine8["fraction_of_ideal"] > .99 and
            sine48["fraction_of_ideal"] < .30,
        "G7_D_K48_at_4096":
            k48["4096"]["mean_relative_projection_error"] <= .01 and
            k48["4096"]["improved"] >= 7,
        "G7_E_matched_loss_vs_global_oracle":
            all(out[str(k)]["stages"]["4096"]["mean_loss_ratio"] <=
                out[str(k)]["oracle_mean_loss_ratio"] + .01
                for k in RESOLUTIONS),
    }
    return dict(per_k=out, sine_probe={"8":sine8,"48":sine48},
                worst_material_conservation_error=mass_error, gates=g)


def run(seeds):
    rows = [run_case(k, seed) for k in RESOLUTIONS for seed in seeds]
    return dict(protocol="PREREG_G7.md",
                ideal_teacher="numerical adjoint, not physical backward wave",
                neighbor_only_redistribution=True, normalization_is_external=True,
                seeds=list(seeds), K=list(RESOLUTIONS), rounds=list(ROUNDS),
                relay_alpha=RELAY_ALPHA, summary=summary(rows), per_seed=rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=("development","confirm"), default="development")
    p.add_argument("--out")
    args = p.parse_args()
    ids = range(71,74) if args.phase == "development" else range(1900,1908)
    result = run(ids)
    out = Path(args.out or "results/g7_"+args.phase+".json")
    out.parent.mkdir(exist_ok=True, parents=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("G7",args.phase,json.dumps(result["summary"],indent=2),flush=True)


if __name__ == "__main__":
    main()
