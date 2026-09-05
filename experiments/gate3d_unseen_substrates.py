"""Gate 3D: unseen substrates, and a deliberately boring baseline-delta attacker.

Gate 3C moved the fault address but kept one underlying geometry/connectome.
This gate changes the substrate itself across worlds.

Thirty training worlds and thirty held-out test worlds each have:
- node-specific local transport weights;
- a different sparse directed long-range graph;
- the same *families* of local geometry, wiring, and gain perturbations.

For this representation audit we temporarily use the FULL diagnostic panel:
24 poke nodes x 7 read times = 168 scalar global consequences.  That isolates
representation/invariance from the separate active-budget question.

For each current world the machine is allowed to remember its pre-change
baseline response.  We compare:

1. absolute literal atlas: post-change response templates tied to node IDs;
2. absolute shared: one node-independent template per cause;
3. baseline DELTA literal: per-node templates of after-minus-before response;
4. baseline DELTA shared: node-independent templates of the same difference;
5. baseline-normalized variants.

A final control randomly relabels every node in every held-out episode.

The anticipated boundary is not a glamorous causal-address victory.  If simple
current-world differencing already removes substrate variation, preserve that
negative: the fancy representation has not earned explanatory work yet.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np


N = 24
TIMES = (1, 2, 3, 4, 5, 7, 9)
MAX_HORIZON = max(TIMES)
CAUSES = ("geometry", "wiring", "gain")
MEASUREMENT_NOISE = 0.002


@dataclass
class Gaussian:
    mean: np.ndarray
    var: np.ndarray


def make_world(seed: int):
    """Random local transport plus random directed nonlocal coupling."""
    rng = np.random.default_rng(seed)
    g = np.zeros((N, N))
    for i in range(N):
        left = float(rng.uniform(0.24, 0.32))
        right = float(rng.uniform(0.24, 0.32))
        self_weight = float(rng.uniform(0.34, 0.44))
        g[i, i] = self_weight
        g[i, (i - 1) % N] = left
        g[i, (i + 1) % N] = right
    # Keep the random family stable without erasing local heterogeneity.
    g *= 0.95 / max(0.95, float(np.linalg.norm(g, 2)))

    c = np.zeros((N, N))
    for source in range(N):
        candidates = [
            target
            for target in range(N)
            if min((target - source) % N, (source - target) % N) > 3
        ]
        target = int(rng.choice(candidates))
        c[target, source] = float(rng.uniform(0.25, 0.70))
    c /= max(1.0, float(np.linalg.norm(c, 2)))
    return g, c


def impulse(g: np.ndarray, c: np.ndarray, gain: np.ndarray, poke: int) -> np.ndarray:
    states = np.zeros((MAX_HORIZON + 1, N))
    states[0, poke] = 1.0
    zero = np.zeros(N)
    delay = 3
    for t in range(MAX_HORIZON):
        delayed = states[t - delay] if t - delay >= 0 else zero
        z = 0.15 * states[t] + 0.58 * (g @ states[t]) + 0.22 * (c @ delayed)
        states[t + 1] = np.tanh(gain * z)
    return states


def response_vector(g: np.ndarray, c: np.ndarray, gain: np.ndarray, poke: int) -> np.ndarray:
    """Seven scalar global consequences, invariant to node relabeling."""
    states = impulse(g, c, gain, poke)
    return np.asarray([np.sum(np.abs(states[t])) for t in TIMES])


def perturb(g: np.ndarray, c: np.ndarray, cause: str, address: int, seed: int):
    g = g.copy()
    c = c.copy()
    gain = np.ones(N)
    rng = np.random.default_rng(seed)

    if cause == "geometry":
        delta = 0.13
        g[address, address] -= delta
        g[address, (address + 1) % N] += delta
    elif cause == "wiring":
        candidates = [
            target
            for target in range(N)
            if min((target - address) % N, (address - target) % N) > 3
        ]
        target = int(rng.choice(candidates))
        c[target, address] += 0.18
    elif cause == "gain":
        gain[address] = 1.18
    else:
        raise ValueError(cause)
    return g, c, gain


def event_features(world_seed: int, cause: str, address: int, event_seed: int):
    g, c = make_world(world_seed)
    base_gain = np.ones(N)
    baseline = np.stack([response_vector(g, c, base_gain, poke) for poke in range(N)])

    g2, c2, gain2 = perturb(g, c, cause, address, event_seed)
    post = np.stack([response_vector(g2, c2, gain2, poke) for poke in range(N)])

    # Baseline and post measurements are remembered/observed independently.
    rng = np.random.default_rng(event_seed + 999)
    baseline = baseline + rng.normal(0.0, MEASUREMENT_NOISE, baseline.shape)
    post = post + rng.normal(0.0, MEASUREMENT_NOISE, post.shape)

    delta = post - baseline
    normalized = delta / (np.abs(baseline) + 0.05)
    return baseline, post, delta, normalized


def fit_gaussian(rows: list[np.ndarray], floor: float) -> Gaussian:
    x = np.asarray(rows)
    return Gaussian(np.mean(x, axis=0), np.var(x, axis=0) + floor)


def loglike(x: np.ndarray, model: Gaussian) -> float:
    return float(-0.5 * np.sum(np.log(model.var) + (x - model.mean) ** 2 / model.var))


def make_training_events():
    events = []
    for wi in range(30):
        world_seed = 1000 + wi
        for ci, cause in enumerate(CAUSES):
            for rep in range(4):
                # Deterministic schedule gives every literal node 4-6 training
                # appearances per cause rather than relying on lucky sampling.
                address = int((wi * 7 + rep * 5 + ci * 3) % N)
                seed = 50_000 + wi * 100 + rep + 1000 * ci
                events.append((world_seed, cause, address, *event_features(world_seed, cause, address, seed)))
    return events


def fit_shared(events, feature: str):
    pos = {cause: [] for cause in CAUSES}
    null = []
    idx = {"post": 4, "delta": 5, "normalized": 6}[feature]
    for event in events:
        _world, cause, address = event[:3]
        values = event[idx]
        pos[cause].append(values[address])
        # Same event supplies current-world negative locations.
        for other in ((address + 3) % N, (address + 7) % N, (address + 11) % N, (address + 15) % N):
            null.append(values[other])
    floor = 1e-3 if feature == "post" else 1e-4
    return ({cause: fit_gaussian(rows, floor) for cause, rows in pos.items()}, fit_gaussian(null, floor))


def fit_literal(events, feature: str, likelihood_ratio: bool):
    idx = {"post": 4, "delta": 5, "normalized": 6}[feature]
    positive = {(node, cause): [] for node in range(N) for cause in CAUSES}
    negative = {node: [] for node in range(N)}

    for event in events:
        _world, cause, address = event[:3]
        values = event[idx]
        positive[(address, cause)].append(values[address])
        if likelihood_ratio:
            for other in ((address + 3) % N, (address + 7) % N, (address + 11) % N, (address + 15) % N):
                negative[other].append(values[other])

    floor = 1e-3 if feature == "post" else 1e-4
    positive_model = {key: fit_gaussian(rows, floor) for key, rows in positive.items()}
    negative_model = None
    if likelihood_ratio:
        negative_model = {node: fit_gaussian(rows, floor) for node, rows in negative.items()}
    return positive_model, negative_model


def predict_shared(values: np.ndarray, positive: dict[str, Gaussian], null: Gaussian):
    best = (-np.inf, None, None)
    for node in range(N):
        ll0 = loglike(values[node], null)
        for cause in CAUSES:
            score = loglike(values[node], positive[cause]) - ll0
            if score > best[0]:
                best = (score, cause, node)
    return best[1], int(best[2])


def predict_literal(
    values: np.ndarray,
    positive: dict[tuple[int, str], Gaussian],
    negative: dict[int, Gaussian] | None,
):
    best = (-np.inf, None, None)
    for node in range(N):
        ll0 = 0.0 if negative is None else loglike(values[node], negative[node])
        for cause in CAUSES:
            score = loglike(values[node], positive[(node, cause)]) - ll0
            if score > best[0]:
                best = (score, cause, node)
    return best[1], int(best[2])


def build_models(events):
    abs_shared = fit_shared(events, "post")
    delta_shared = fit_shared(events, "delta")
    norm_shared = fit_shared(events, "normalized")
    abs_literal = fit_literal(events, "post", likelihood_ratio=False)
    delta_literal = fit_literal(events, "delta", likelihood_ratio=True)
    norm_literal = fit_literal(events, "normalized", likelihood_ratio=True)
    return {
        "absolute_literal_atlas": ("literal", "post", abs_literal),
        "absolute_shared": ("shared", "post", abs_shared),
        "delta_literal_atlas": ("literal", "delta", delta_literal),
        "delta_shared": ("shared", "delta", delta_shared),
        "normalized_literal_atlas": ("literal", "normalized", norm_literal),
        "normalized_shared": ("shared", "normalized", norm_shared),
    }


def evaluate(models, permuted: bool):
    counts = {
        name: {"cause": 0, "address": 0, "joint": 0}
        for name in models
    }
    total = 0
    rng = np.random.default_rng(2026 if permuted else 999)

    for wi in range(30, 60):
        world_seed = 1000 + wi
        for ci, cause in enumerate(CAUSES):
            for rep in range(4):
                address = int(rng.integers(N))
                seed = 80_000 + wi * 100 + rep + 1000 * ci
                baseline, post, delta, normalized = event_features(world_seed, cause, address, seed)
                features = {"post": post, "delta": delta, "normalized": normalized}

                if permuted:
                    # new-index -> old-index. Global response scalars are
                    # permutation invariant, so reordering the candidate-node
                    # axis is exactly a consistent relabeling control here.
                    permutation = rng.permutation(N)
                    address = int(np.flatnonzero(permutation == address)[0])
                    features = {name: values[permutation] for name, values in features.items()}

                for name, (kind, feature_name, model) in models.items():
                    values = features[feature_name]
                    if kind == "shared":
                        pred_cause, pred_address = predict_shared(values, *model)
                    else:
                        pred_cause, pred_address = predict_literal(values, *model)
                    counts[name]["cause"] += int(pred_cause == cause)
                    counts[name]["address"] += int(pred_address == address)
                    counts[name]["joint"] += int(pred_cause == cause and pred_address == address)
                total += 1

    return {
        name: {
            "cause_accuracy": score["cause"] / total,
            "address_accuracy": score["address"] / total,
            "joint_accuracy": score["joint"] / total,
        }
        for name, score in counts.items()
    }


def run(seed: int = 17) -> dict:
    # Seed is retained in the receipt/API even though world/event schedules are
    # locked independently for reproducibility of this preregistered audit.
    train = make_training_events()
    models = build_models(train)
    unseen = evaluate(models, permuted=False)
    relabeled = evaluate(models, permuted=True)

    return {
        "seed": seed,
        "classification": (
            "CURRENT_WORLD_BASELINE_DIFFERENCING_ERASES_MOST_SUBSTRATE_VARIATION;_"
            "RELATIVE_CAUSAL_ADDRESS_HAS_NOT_EARNED_MORE_THAN_DIFFERENTIAL_CHANGE_DETECTION"
        ),
        "n": N,
        "causes": list(CAUSES),
        "training_worlds": 30,
        "held_out_worlds": 30,
        "training_events": len(train),
        "held_out_events": 30 * len(CAUSES) * 4,
        "scalar_measurements_per_full_panel": N * len(TIMES),
        "unseen_substrates": unseen,
        "unseen_substrates_random_relabel": relabeled,
    }


def check(result: dict) -> None:
    unseen = result["unseen_substrates"]
    relabeled = result["unseen_substrates_random_relabel"]

    # Absolute response atlases do not transfer across changing substrates.
    assert unseen["absolute_literal_atlas"]["joint_accuracy"] <= 0.10
    assert unseen["absolute_shared"]["joint_accuracy"] <= 0.50

    # The boring current-world before/after difference almost solves this world
    # family, even if templates are still indexed by literal node ID.
    assert unseen["delta_shared"]["joint_accuracy"] >= 0.98
    assert unseen["delta_literal_atlas"]["joint_accuracy"] >= 0.97
    assert abs(
        unseen["delta_shared"]["joint_accuracy"]
        - unseen["delta_literal_atlas"]["joint_accuracy"]
    ) <= 0.02

    # Consistent relabeling barely matters once prediction is expressed as a
    # current-world delta. This kills a premature coordinate-invariance story.
    assert relabeled["delta_shared"]["joint_accuracy"] >= 0.97
    assert relabeled["delta_literal_atlas"]["joint_accuracy"] >= 0.97

    # Extra baseline normalization is not required in this assay.
    assert unseen["delta_shared"]["joint_accuracy"] >= unseen["normalized_shared"]["joint_accuracy"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE3D PASS (negative boundary: baseline differencing is enough here)")


if __name__ == "__main__":
    main()
