"""G1 paired, held-out echo-reading benchmark with fixed source and seed splits."""
from __future__ import annotations
import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
from .model import Beach, Config

WINDOW = (120, 290)
SOURCES = (0, 1, 2)


def read_features(beach: Beach, h, win=WINDOW):
    # Receiver echoes only; the decoder never observes the hidden material.
    return np.concatenate([beach.read(h, source=s)[win[0]:win[1]] for s in SOURCES])


def make_pairs(beach, seeds, mode='live'):
    xs, hidden, delta = [], [], []
    for seed in seeds:
        pair, maps = [], []
        for order in ((0, 1), (1, 0)):
            h, _ = beach.history(order, seed=int(seed), feedback=(mode != 'fixed'))
            if mode == 'permuted':
                rng = np.random.default_rng(900_000 + int(seed)*17 + len(pair))
                h = h[rng.permutation(len(h))]
            pair.append(read_features(beach, h))
            maps.append(h)
        xs.append(pair)
        hidden.append(maps)
        delta.append(float(np.linalg.norm(maps[0] - maps[1])))
    return np.asarray(xs), np.asarray(hidden), delta


def fit_decide(train, test):
    # Train-only feature normalization; no held-out model fitting or tuning.
    flat = train.reshape(-1, train.shape[-1])
    mu = train.mean((0, 1))
    scale = np.maximum(flat.std(0), .03 * np.max(flat.std(0)))
    cent = ((train - mu) / scale).mean(0)
    direction = cent[0] - cent[1]
    scores = ((test - mu) / scale) @ direction
    return (scores[:, 0] > 0), (scores[:, 1] < 0), scores


def paired_pvalue(scores, observed_correct, permutations=9999):
    """Randomly swap AB/BA labels *within* each paired material seed."""
    rng = np.random.default_rng(88)
    swaps = rng.integers(0, 2, size=(permutations, len(scores)), dtype=np.int8)
    # Predicted 0 (AB) if score >0; predicted 1 (BA) otherwise.
    predicted_ab = (scores[:, 0] > 0).astype(np.int8)
    predicted_ba = (scores[:, 1] > 0).astype(np.int8)
    num_correct = (
        (predicted_ab[None, :] == 1 - swaps).astype(np.int16)
        + (predicted_ba[None, :] == swaps).astype(np.int16)
    ).sum(axis=1)
    return float((1 + np.count_nonzero(num_correct >= observed_correct))
                 / (permutations + 1))


def run_benchmark(cfg=Config(), train_n=14, test_n=32, noise=.04, seed=2026):
    beach = Beach(cfg)
    train_seeds = np.arange(100, 100 + train_n)
    test_seeds = np.arange(40000, 40000 + test_n)
    train, _, _ = make_pairs(beach, train_seeds)
    echo_rms = float(np.sqrt(np.mean(train ** 2)))
    rng = np.random.default_rng(seed)
    report = {
        'setup': asdict(cfg),
        'window': list(WINDOW), 'sources': list(SOURCES),
        'train_seeds': train_seeds.tolist(), 'test_seeds': test_seeds.tolist(),
        'noise_relative_to_train_echo_rms': noise,
        'train_echo_rms': echo_rms,
        'modes': {},
    }
    for mode in ('live', 'fixed', 'permuted'):
        test, maps, dist = make_pairs(beach, test_seeds, mode=mode)
        perturbed = test + rng.normal(0, noise*echo_rms, size=test.shape)
        correct_ab, correct_ba, scores = fit_decide(train, perturbed)
        correct = int(correct_ab.sum() + correct_ba.sum())
        # Fixed/permuted controls use the LIVE-trained classifier intentionally.
        # Permuted is an intervention, not a retrained matched classifier.
        report['modes'][mode] = {
            'balanced_accuracy': float(correct / (2*len(correct_ab))),
            'correct_ab': int(correct_ab.sum()),
            'correct_ba': int(correct_ba.sum()),
            'paired_label_swap_p': paired_pvalue(scores, correct),
            'mean_map_order_distance': float(np.mean(dist)),
            'min_map_order_distance': float(np.min(dist)),
            'max_map_mass_change': float(np.max(np.abs(maps.sum(-1)))),
            'mean_echo_order_distance':
                float(np.linalg.norm(test[:, 0]-test[:, 1], axis=-1).mean()),
        }
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results/g1_confirmatory.json')
    ap.add_argument('--train', type=int, default=14)
    ap.add_argument('--test', type=int, default=32)
    ap.add_argument('--noise', type=float, default=.04)
    args = ap.parse_args()
    result = run_benchmark(train_n=args.train, test_n=args.test, noise=args.noise)
    print(json.dumps(result['modes'], indent=2))
    dest = Path(args.out)
    dest.parent.mkdir(exist_ok=True, parents=True)
    dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
