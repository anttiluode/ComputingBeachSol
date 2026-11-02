"""G8: conservative edge-only stress-memory relay, without G7's z common mode.

Numerical ideal adjoint and external teacher amplitude remain G6/G7 assumptions.
Only the *redistribution* lives in the q edge circuit. Every q update is local
to neighbouring edges and stresses. Externally calibrated clipping capacities
and matched-norm evaluation are deliberately NOT autonomous physical mechanisms.
See PREREG_G8.md (committed before held-out seeds).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from .adjoint import propagate, loss_and_gradient
from .energy_writer import local_flux
from .g6_memory import (remember, patch_energy, teacher_boost, score,
                        project, CALIBRATION_EPISODES, STEP_NORM, STEPS)
from .g7_local import relay, lap, relative_error
from .model import Beach, Config
from .teacher import adjoint_snapshot

RELAX = 0.2
SEEDS = range(2200, 2208)
PAIR = {8: 64, 48: 4096}
CAPS = (0.5, 2., 16., 64.)
LEAKS = (0.001, 0.01)


def divergence(q):
    """Patch height increment from oriented edge fluxes: ∇*q."""
    return q - np.roll(q, 1)


def edge_relay(r, rounds, *, cap=None, leak=0.0, step=RELAX):
    """Iterative neighbour-only q update; no spatial mean or global sum.

    If cap is supplied it is a fixed external engineering parameter. Its
    calibration from global max(|r|) happens only in the *referee*.
    """
    raw = np.asarray(r, dtype=float)
    q = np.zeros_like(raw)
    nclips = 0
    max_unclipped = 0.
    for _ in range(int(rounds)):
        nextq = q + step * ((raw-np.roll(raw,-1)) - lap(q)) - leak*q
        max_unclipped = max(max_unclipped,float(np.max(np.abs(nextq))))
        if cap is not None:
            nclips += int(np.count_nonzero(np.abs(nextq) > cap))
            nextq = np.clip(nextq, -cap, cap)
        q = nextq
    return divergence(q), q, dict(clips=nclips, max_unclipped_edge=max_unclipped)


def get_case(k, seed, steps=STEPS):
    beach = Beach(Config(k=k))
    h = beach.initial(seed)
    rng = np.random.default_rng(seed)
    desired = h+rng.normal(0,.21,size=k)
    desired -= desired.mean()-h.mean()
    source = seed%3
    bits = beach.kappa_bits(h)
    target, _ = propagate(beach.cav, beach.kappa_bits(desired),
                          source=source, steps=steps)
    u, lam, _ = adjoint_snapshot(beach.cav, bits, target, source=source)
    loss, gb, _ = loss_and_gradient(beach.cav, bits, target, source=source)
    grad_h = gb/np.cosh(h/.45)**2
    ideal = project(-grad_h)
    e = patch_energy(beach, u)
    theta = remember(np.zeros_like(e),e,CALIBRATION_EPISODES)
    r = patch_energy(beach,u+teacher_boost(beach,u,lam)*lam)-theta
    return beach,h,source,target,float(loss),ideal,r


def run_case(k, seed, steps=STEPS):
    beach,h,source,target,loss,ideal,r = get_case(k,seed,steps)
    n = PAIR[k]
    z_direction,z = relay(r,n)
    edge_direction,q,edge_diag = edge_relay(r,n)
    oracle = project(r)
    scale = float(np.max(np.abs(r)))
    bound = 1./(2*np.sin(np.pi/k))
    ref_score = score(beach,h,z_direction,source,target,loss,ideal)
    global_score = score(beach,h,oracle,source,target,loss,ideal)
    old_flux_score = score(beach,h,local_flux(r),source,target,loss,ideal)
    caps = {}
    for c in CAPS:
        d, qc, diagnostics = edge_relay(r,n,cap=c*scale)
        caps[str(c)] = dict(
            relative_to_edge=relative_error(d,edge_direction),
            relative_to_global=relative_error(d,oracle),
            normalized_loss=score(beach,h,d,source,target,loss,ideal),
            max_q=float(np.max(np.abs(qc))),cap=float(c*scale),
            **diagnostics
        )
    leakage = {}
    for value in LEAKS:
        d, ql, diag = edge_relay(r,n,leak=value)
        leakage[str(value)] = dict(
            relative_to_edge=relative_error(d,edge_direction),
            relative_to_global=relative_error(d,oracle),
            normalized_loss=score(beach,h,d,source,target,loss,ideal),
            max_q=float(np.max(np.abs(ql))),
            **diag
        )
    return dict(
        k=k,seed=seed,rounds=n,raw_max=scale,raw_norm=float(np.linalg.norm(r)),
        unbounded_q_norm=float(np.linalg.norm(q)),
        spectral_q_over_r_bound=float(bound),
        observed_q_over_r_norm=float(np.linalg.norm(q)/max(np.linalg.norm(r),1e-30)),
        mean_q=float(q.mean()),mean_z=float(z.mean()),
        edge_to_z_relative_error=relative_error(edge_direction,z_direction),
        edge_to_global_relative_error=relative_error(edge_direction,oracle),
        edge_total_mass_error=float(abs(edge_direction.sum())),
        z_total_mass_error=float(abs(z_direction.sum())),
        edge_score=score(beach,h,edge_direction,source,target,loss,ideal),
        z_score=ref_score,global_score=global_score,old_flux_score=old_flux_score,
        clipped=caps,leaky=leakage,
        edge_diagnostics=edge_diag,
    )


def summarize(rows):
    allerr=max(r["edge_to_z_relative_error"] for r in rows)
    allmass=max(max(r["edge_total_mass_error"],r["z_total_mass_error"]) for r in rows)
    spec=max(r["observed_q_over_r_norm"]-r["spectral_q_over_r_bound"] for r in rows)
    maxqmean=max(abs(r["mean_q"]) for r in rows)
    blocks={}
    for k in PAIR:
        cases=[r for r in rows if r["k"]==k]
        cap_out={}
        for c in CAPS:
            rec=[r["clipped"][str(c)] for r in cases]
            cap_out[str(c)]=dict(
                total_clipped_updates=int(sum(x["clips"] for x in rec)),
                mean_relative_to_edge=float(np.mean([x["relative_to_edge"] for x in rec])),
                mean_relative_to_global=float(np.mean([x["relative_to_global"] for x in rec])),
                improved=int(sum(x["normalized_loss"]["loss_ratio"]<1. for x in rec)),
                mean_loss_ratio=float(np.mean([x["normalized_loss"]["loss_ratio"] for x in rec])),
            )
        leak_out={}
        for value in LEAKS:
            rec=[r["leaky"][str(value)] for r in cases]
            leak_out[str(value)] = dict(
                mean_relative_to_edge=float(np.mean([x["relative_to_edge"] for x in rec])),
                mean_relative_to_global=float(np.mean([x["relative_to_global"] for x in rec])),
                improved=int(sum(x["normalized_loss"]["loss_ratio"]<1. for x in rec)),
                mean_loss_ratio=float(np.mean([x["normalized_loss"]["loss_ratio"] for x in rec])),
            )
        blocks[str(k)]=dict(
            edge_mean_cosine=float(np.mean([r["edge_score"]["cosine"] for r in cases])),
            edge_improved=int(sum(r["edge_score"]["loss_ratio"]<1. for r in cases)),
            edge_mean_loss_ratio=float(np.mean([r["edge_score"]["loss_ratio"] for r in cases])),
            z_mean_loss_ratio=float(np.mean([r["z_score"]["loss_ratio"] for r in cases])),
            original_z_mean_abs=float(np.mean([abs(r["mean_z"]) for r in cases])),
            edge_mean_abs_q_mean=float(np.mean([abs(r["mean_q"]) for r in cases])),
            edge_mean_qnorm_over_rnorm=float(np.mean([r["observed_q_over_r_norm"] for r in cases])),
            caps=cap_out,leakage=leak_out,
        )
    gates = {
        "G8_A_edge_equivalence_and_mass":
            allerr<1e-9 and allmass<1e-9,
        "G8_B_no_runaway_gauge":
            spec <=1e-8 and maxqmean<1e-9,
        "G8_C_loose_finite_cap":
            all(r["clipped"]["64.0"]["clips"]==0 and
                r["clipped"]["64.0"]["relative_to_edge"]<1e-8 for r in rows)
            and all(blocks[str(k)]["caps"]["64.0"]["improved"]>=7 for k in PAIR),
    }
    return dict(max_edge_z_relative_error=allerr,
                worst_material_sum_error=allmass,
                largest_spectral_bound_excess=spec,
                worst_abs_mean_edge_state=maxqmean,
                blocks=blocks,gates=gates)


def run(seeds):
    rows=[run_case(k,int(seed)) for k in PAIR for seed in seeds]
    return dict(protocol="PREREG_G8.md",seeds=list(seeds),
                resolutions=list(PAIR),rounds={str(k):v for k,v in PAIR.items()},
                caps=list(CAPS),leaks=list(LEAKS),
                clip_capacity_is_externally_calibrated=True,
                teacher_is_externally_computed=True,
                writer_uses_global_mean=False,
                step_norm_is_external=True,
                summary=summarize(rows),per_case=rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=("development","confirm"),default="development")
    ap.add_argument("--out")
    args=ap.parse_args()
    seeds=range(81,84) if args.phase=="development" else SEEDS
    result=run(seeds)
    p=Path(args.out or "results/g8_"+args.phase+".json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("G8",args.phase,json.dumps(result["summary"],indent=2),flush=True)


if __name__=="__main__":
    main()
