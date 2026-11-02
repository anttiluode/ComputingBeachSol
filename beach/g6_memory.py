"""G6: internal per-patch stress memory as a *one-exposure* numerical writer.

The writer receives patch energy from only u + beta*lambda and a stored theta.
Theta was learned from earlier teacher-free drives; no concurrent minus exposure
or gradient enters the update. A *numerical* adjoint still supplies lambda.
Projecting the update to zero net material is GLOBAL SOFTWARE, not sand physics.
The local-flux branch is the independently scored conservative counterexample.
See PREREG_G6.md before interpreting any held-out result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .adjoint import loss_and_gradient, propagate
from .energy_writer import angle, local_flux
from .model import Beach
from .teacher import adjoint_snapshot

ALPHA = 0.65
CALIBRATION_EPISODES = 12
TEACHER_RATIO = 0.02
STEP_NORM = 0.025
STEPS = 310


def patch_energy(beach, field):
    """Time-integrated patch displacement energy; no gradient or target used."""
    return np.einsum("kij,tij->k", beach.counts, field ** 2, optimize=True)


def remember(theta, energy, episodes=1, alpha=ALPHA):
    """A strictly local EWMA of the ordinary (teacher-free) stress."""
    state = np.asarray(theta, dtype=float).copy()
    energy = np.asarray(energy, dtype=float)
    for _ in range(episodes):
        state += alpha * (energy - state)
    return state


def teacher_boost(beach, u, lam, ratio=TEACHER_RATIO):
    # A calibrated external teacher amplitude, identical to G2d's convention.
    pu = np.einsum("kij,tij->tk", beach.counts, u, optimize=True) / beach.weights
    pl = np.einsum("kij,tij->tk", beach.counts, lam, optimize=True) / beach.weights
    return float(ratio * np.sqrt(np.mean(pu ** 2)) /
                 max(np.sqrt(np.mean(pl ** 2)), 1e-30))


def project(v):
    """Nonlocal conservation ORACLE; never describe it as local transport."""
    a = np.asarray(v, dtype=float)
    return a - a.mean()


def score(beach, h, direction, source, target, base_loss, ideal, step_norm=STEP_NORM):
    norm = float(np.linalg.norm(direction))
    if norm <= 1e-20:
        return dict(cosine=None, loss_ratio=1.0, norm=norm, applied=False)
    trial = h + (step_norm / norm) * direction
    out, _ = propagate(beach.cav, beach.kappa_bits(trial),
                       source=source, steps=len(target))
    new_loss = 0.5 * np.mean((out - target) ** 2)
    return dict(cosine=angle(direction, ideal),
                loss_ratio=float(new_loss / max(base_loss, 1e-30)),
                norm=norm, applied=True)


def single_case(beach, seed, steps=STEPS, baseline_episodes=CALIBRATION_EPISODES):
    """One independently seeded material/target; all branch conditions matched."""
    seed = int(seed)
    h = beach.initial(seed)
    rng = np.random.default_rng(seed)
    target_h = h + rng.normal(0, 0.21, size=beach.cfg.k)
    target_h -= target_h.mean() - h.mean()
    source = seed % 3
    target, _ = propagate(beach.cav, beach.kappa_bits(target_h),
                          source=source, steps=steps)
    bits = beach.kappa_bits(h)
    u, lam, _ = adjoint_snapshot(beach.cav, bits, target, source=source)
    loss, gb, _ = loss_and_gradient(beach.cav, bits, target, source=source)
    grad_h = gb / np.cosh(h / 0.45) ** 2
    ideal = project(-grad_h)

    boost = teacher_boost(beach, u, lam)
    e_u = patch_energy(beach, u)
    e_l = patch_energy(beach, lam)
    e_pos = patch_energy(beach, u + boost * lam)
    e_neg = patch_energy(beach, u - boost * lam)
    # No target or gradient is ever used to construct the baseline.
    theta = remember(np.zeros_like(e_u), e_u, baseline_episodes)
    wrong_u, _ = propagate(beach.cav, bits, source=(source + 1) % 3,
                           steps=steps, store_states=True)
    # propagate returns states, with states[0] = the initial wave.
    _, wrong_states = propagate(beach.cav, bits,
                                source=(source + 1) % 3, steps=steps,
                                store_states=True)
    wrong_theta = remember(np.zeros_like(e_u),
                           patch_energy(beach, wrong_states[:-1]),
                           baseline_episodes)

    direct_cross = np.einsum("kij,tij->k", beach.counts, u * lam, optimize=True)
    predicted_exact = 2 * boost * direct_cross + boost ** 2 * e_l
    raw_exact = e_pos - e_u
    identity_error = float(np.max(np.abs(raw_exact - predicted_exact)) /
                           max(1., float(np.linalg.norm(raw_exact))))
    raw = {
        "adaptive": e_pos - theta,
        "exact_theta": raw_exact,
        "no_theta": e_pos,
        "negative_teacher": e_neg - theta,
        "teacher_off": e_u - theta,
        "wrong_source_theta": e_pos - wrong_theta,
        "two_exposure_oracle": (e_pos - e_neg) / (4 * boost),
    }
    results = {name: score(beach, h, project(d), source, target, loss, ideal)
               for name, d in raw.items()}
    results["local_flux"] = score(beach, h, local_flux(raw["adaptive"]),
                                  source, target, loss, ideal)

    adaptive = project(raw["adaptive"])
    off = project(raw["teacher_off"])
    # Numeric material-conservation checks use the *raw* directions.
    max_mass_error = max(float(abs(project(d).sum())) for d in raw.values())
    max_mass_error = max(max_mass_error,
                         float(abs(local_flux(raw["adaptive"]).sum())))
    # On the updated material the old theta may be stale. Teacher field is
    # recomputed as a separately supplied best-case numerical adjoint.
    norm = float(np.linalg.norm(adaptive))
    new_h = h + STEP_NORM * adaptive / norm if norm > 1e-20 else h.copy()
    u2, lam2, _ = adjoint_snapshot(beach.cav, beach.kappa_bits(new_h),
                                   target, source=source)
    e_u2 = patch_energy(beach, u2)
    e_pos2 = patch_energy(beach, u2 + teacher_boost(beach, u2, lam2) * lam2)
    stale_error = float(np.linalg.norm(theta - e_u2))
    drift = {}
    for n in (0, 1, 4):
        theta2 = remember(theta, e_u2, episodes=n)
        drift[str(n)] = dict(
            relative_baseline_error=float(np.linalg.norm(theta2 - e_u2) /
                                          max(stale_error, 1e-30)),
            writer_residual_norm=float(np.linalg.norm(project(e_pos2-theta2))),
        )

    return dict(
        seed=seed, source=source, base_loss=float(loss), boost=boost,
        baseline_relative_error=float(np.linalg.norm(theta-e_u) /
                                      max(np.linalg.norm(e_u), 1e-30)),
        cross_identity_error=identity_error, results=results,
        projected_off_to_on_ratio=float(np.linalg.norm(off) /
                                        max(np.linalg.norm(adaptive), 1e-30)),
        max_mass_error=max_mass_error,
        drift=drift,
    )


def aggregate(rows):
    names = rows[0]["results"].keys()
    scores = {}
    for name in names:
        cases = [row["results"][name] for row in rows]
        cosines = [r["cosine"] for r in cases if r["cosine"] is not None]
        scores[name] = dict(
            mean_cosine=float(np.mean(cosines)) if cosines else None,
            improved=int(sum(r["loss_ratio"] < 1 for r in cases)),
            mean_loss_ratio=float(np.mean([r["loss_ratio"] for r in cases])),
            inactive=int(sum(not r["applied"] for r in cases)),
        )
    wins_without_baseline = sum(
        r["results"]["adaptive"]["loss_ratio"] <
        r["results"]["no_theta"]["loss_ratio"] for r in rows)
    initial_loss = [r["results"]["adaptive"]["loss_ratio"] for r in rows]
    wins_oracle = sum(
        r["results"]["adaptive"]["loss_ratio"] <
        r["results"]["two_exposure_oracle"]["loss_ratio"] for r in rows)
    mean = lambda vals: float(np.mean(vals))
    maxidentity = max(r["cross_identity_error"] for r in rows)
    maxmass = max(r["max_mass_error"] for r in rows)
    offratio = mean([r["projected_off_to_on_ratio"] for r in rows])
    baseline_error = mean([r["baseline_relative_error"] for r in rows])
    recalibration4 = mean([r["drift"]["4"]["relative_baseline_error"] for r in rows])
    passes = {
        "G6_A_energy_algebra": maxidentity < 1e-9,
        "G6_B_internal_baseline":
            scores["adaptive"]["mean_cosine"] >= .98 and
            scores["adaptive"]["improved"] >= 14 and
            wins_without_baseline >= 12,
        "G6_C_signed_teacher":
            scores["negative_teacher"]["mean_cosine"] <= -.90 and
            offratio < .001,
        "G6_D_numerical_conservation": maxmass < 1e-10,
        "G6_E_local_flux": scores["local_flux"]["mean_cosine"] > .50 and
                               scores["local_flux"]["improved"] >= 12,
        "G6_F_drift_recovery": recalibration4 <= .05,
    }
    return dict(scores=scores, wins_vs_no_baseline=int(wins_without_baseline),
                wins_oracle=int(wins_oracle), adaptive_mean_ratio=mean(initial_loss),
                max_algebra_error=maxidentity, max_material_sum_error=maxmass,
                mean_off_to_on_norm_ratio=offratio,
                mean_baseline_relative_error=baseline_error,
                mean_four_episode_relative_error=recalibration4,
                gates=passes)


def run(seeds, steps=STEPS, baseline_episodes=CALIBRATION_EPISODES):
    beach = Beach()
    rows = [single_case(beach, seed, steps, baseline_episodes) for seed in seeds]
    return dict(protocol="PREREG_G6.md", writer="EWMA stress baseline",
                ideal_teacher="numerical adjoint, externally amplitude matched",
                global_projection_is_physical=False,
                seeds=list(seeds), steps=steps, alpha=ALPHA,
                baseline_episodes=baseline_episodes, teacher_ratio=TEACHER_RATIO,
                step_norm=STEP_NORM, summary=aggregate(rows), per_seed=rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=("development", "confirm"), default="development")
    p.add_argument("--out")
    args = p.parse_args()
    seeds = range(41, 45) if args.phase == "development" else range(1600, 1616)
    result = run(seeds)
    out = Path(args.out or ("results/g6_" + args.phase + ".json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("G6", args.phase, json.dumps(result["summary"], indent=2), flush=True)


if __name__ == "__main__":
    main()
