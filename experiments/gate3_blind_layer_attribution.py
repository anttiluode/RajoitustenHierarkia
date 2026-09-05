"""Gate 3: infer which hidden constraint family changed from bounded consequences.

The observer is NOT handed geometry G, wiring C, delay, gain, or a changed
operator.  It gets four cheap passive residual statistics plus a menu of
reversible addressed experiments.  Each paid experiment is simply

    (poke node, read time) -> one scalar prediction error.

Six hidden causes are used:

    none / local geometry / long-range wiring / delay / gain / input statistics

A labelled training bank teaches empirical consequence distributions, not the
hidden operators.  At test time the active observer chooses each next scalar
experiment by posterior-weighted class separation.  Random pokes and the full
192-poke panel are attackers.

Boundary: every sample uses the same underlying substrate topology.  This is a
discoverability/calibration assay.  Cross-topology transfer is Gate 3B.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np


CLASSES = ("none", "geometry", "wiring", "delay", "gain", "input")
TIMES = (1, 2, 3, 4, 5, 7, 9, 12)
N = 24
BASE_DELAY = 3
MAX_HORIZON = max(TIMES)
MEASUREMENT_NOISE = 2e-4


@dataclass
class Stats:
    passive_mean: np.ndarray   # classes x passive_features
    passive_var: np.ndarray
    probe_mean: np.ndarray     # classes x candidate_experiments
    probe_var: np.ndarray


def make_operators(n: int = N, seed: int = 7) -> tuple[np.ndarray, np.ndarray]:
    """A local ring operator plus sparse directed long-range coupling."""
    g = np.zeros((n, n))
    for i in range(n):
        g[i, i] = 0.40
        g[i, (i - 1) % n] = 0.30
        g[i, (i + 1) % n] = 0.30

    rng = np.random.default_rng(seed)
    c = np.zeros((n, n))
    for source in range(n):
        target = (source + int(rng.integers(5, n - 4))) % n
        c[target, source] += float(rng.uniform(0.4, 1.0))
    c /= max(1.0, float(np.linalg.norm(c, 2)))
    return g, c


def perturb(kind: str, magnitude: float):
    """Build a hidden changed world.  These parameters never reach classifier."""
    g, c = make_operators()
    delay = BASE_DELAY
    gain = 1.0
    input_shift = 0.0
    input_scale = 1.0

    if kind == "geometry":
        # Local transport deformation. Total outgoing local weight is preserved.
        i = 5
        delta = 0.12 * magnitude
        g[i, i] -= delta
        g[i, (i + 1) % N] += delta
    elif kind == "wiring":
        # Directed nonlocal path change.
        c = c.copy()
        c[17, 5] += 0.18 * magnitude
    elif kind == "delay":
        delay = 5 if magnitude > 0 else 2
    elif kind == "gain":
        gain = 1.0 + 0.12 * magnitude
    elif kind == "input":
        # Dynamics unchanged; external drive statistics move.
        input_shift = 0.08 * magnitude
        input_scale = 1.0 + 0.25 * abs(magnitude)
    elif kind != "none":
        raise ValueError(kind)

    return g, c, delay, gain, input_shift, input_scale


def impulse_response(g, c, delay: int, gain: float, poke: int) -> np.ndarray:
    a, b, cc = 0.18, 0.55, 0.22
    states = np.zeros((MAX_HORIZON + 1, N))
    states[0, poke] = 1.0
    for t in range(MAX_HORIZON):
        delayed = states[t - delay] if t - delay >= 0 else np.zeros(N)
        z = a * states[t] + b * (g @ states[t]) + cc * (c @ delayed)
        states[t + 1] = np.tanh(gain * z)
    return states


def spontaneous(
    g,
    c,
    delay: int,
    gain: float,
    input_shift: float,
    input_scale: float,
    seed: int,
    steps: int = 300,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a, b, cc = 0.18, 0.55, 0.22
    states = np.zeros((steps + 1, N))
    for t in range(steps):
        delayed = states[t - delay] if t - delay >= 0 else np.zeros(N)
        u = np.zeros(N)
        u[0] = 0.06 * float(rng.standard_normal()) * input_scale + input_shift
        u[8] = 0.03 * float(rng.standard_normal())
        z = a * states[t] + b * (g @ states[t]) + cc * (c @ delayed) + u
        states[t + 1] = np.tanh(gain * z)
    return states


def passive_features(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    y = states[50:] @ readout
    return np.array(
        [
            float(np.mean(y)),
            float(np.std(y)),
            float(np.mean(y[:-1] * y[1:])),
            float(np.mean(np.abs(y))),
        ]
    )


def build_baseline(readout: np.ndarray, experiments: list[tuple[int, int]]):
    g0, c0 = make_operators()

    responses = {}
    for poke in range(N):
        responses[poke] = impulse_response(g0, c0, BASE_DELAY, 1.0, poke)
    base_probe = np.asarray(
        [float(readout @ responses[poke][t]) for poke, t in experiments]
    )

    bank = np.asarray(
        [
            passive_features(
                spontaneous(g0, c0, BASE_DELAY, 1.0, 0.0, 1.0, seed=2000 + k),
                readout,
            )
            for k in range(50)
        ]
    )
    return base_probe, np.mean(bank, axis=0), np.std(bank, axis=0) + 1e-6


def make_dataset(
    per_class: int,
    seed: int,
    sample_offset: int,
    readout: np.ndarray,
    experiments: list[tuple[int, int]],
    base_probe: np.ndarray,
    base_passive_mean: np.ndarray,
    base_passive_scale: np.ndarray,
):
    rng = np.random.default_rng(seed)
    passive_rows, probe_rows, labels = [], [], []
    sid = sample_offset

    for ci, kind in enumerate(CLASSES):
        for _ in range(per_class):
            if kind == "none":
                magnitude = 1.0
            elif kind == "delay":
                magnitude = 1.0 if rng.random() < 0.5 else -1.0
            else:
                magnitude = float(rng.uniform(0.7, 1.3))
                magnitude *= 1.0 if rng.random() < 0.5 else -1.0

            g, c, delay, gain, input_shift, input_scale = perturb(kind, magnitude)
            state = spontaneous(
                g, c, delay, gain, input_shift, input_scale, seed=10_000 + sid
            )
            passive = (
                passive_features(state, readout) - base_passive_mean
            ) / base_passive_scale

            cache = {
                poke: impulse_response(g, c, delay, gain, poke) for poke in range(N)
            }
            probe = []
            for j, (poke, t) in enumerate(experiments):
                observed = float(readout @ cache[poke][t])
                # Consequence is the magnitude of violation of the remembered
                # baseline prediction, plus scalar measurement noise.
                consequence = abs(observed - base_probe[j])
                consequence += float(rng.normal(0.0, MEASUREMENT_NOISE))
                probe.append(consequence)

            passive_rows.append(passive)
            probe_rows.append(np.asarray(probe))
            labels.append(ci)
            sid += 1

    return np.asarray(passive_rows), np.asarray(probe_rows), np.asarray(labels)


def fit_stats(passive: np.ndarray, probes: np.ndarray, labels: np.ndarray) -> Stats:
    pm, pv, vm, vv = [], [], [], []
    for ci in range(len(CLASSES)):
        rows = labels == ci
        pm.append(np.mean(passive[rows], axis=0))
        pv.append(np.var(passive[rows], axis=0) + 1e-3)
        vm.append(np.mean(probes[rows], axis=0))
        vv.append(np.var(probes[rows], axis=0) + 1e-7)
    return Stats(np.asarray(pm), np.asarray(pv), np.asarray(vm), np.asarray(vv))


def passive_logp(x: np.ndarray, stats: Stats) -> np.ndarray:
    return -0.5 * np.sum(
        np.log(stats.passive_var)
        + (x[None, :] - stats.passive_mean) ** 2 / stats.passive_var,
        axis=1,
    )


def choose_probe(logp: np.ndarray, used: np.ndarray, stats: Stats) -> int:
    """Posterior-weighted Fisher separation, vectorized over all experiments."""
    p = np.exp(logp - np.max(logp))
    p /= np.sum(p)
    mixture_mean = np.sum(p[:, None] * stats.probe_mean, axis=0)
    between = np.sum(
        p[:, None] * (stats.probe_mean - mixture_mean[None, :]) ** 2, axis=0
    )
    within = np.sum(p[:, None] * stats.probe_var, axis=0)
    score = between / (within + 1e-12)
    score = score.copy()
    score[used] = -np.inf
    return int(np.argmax(score))


def add_probe_loglike(logp: np.ndarray, observation: float, j: int, stats: Stats):
    return logp - 0.5 * (
        np.log(stats.probe_var[:, j])
        + (observation - stats.probe_mean[:, j]) ** 2 / stats.probe_var[:, j]
    )


def classify(
    passive: np.ndarray,
    probes: np.ndarray,
    stats: Stats,
    budget: int,
    rng: np.random.Generator | None = None,
    random_policy: bool = False,
):
    logp = passive_logp(passive, stats)
    used = np.zeros(len(probes), dtype=bool)
    order = []
    for _ in range(budget):
        if random_policy:
            if rng is None:
                raise ValueError("random policy needs rng")
            available = np.flatnonzero(~used)
            j = int(rng.choice(available))
        else:
            j = choose_probe(logp, used, stats)
        used[j] = True
        order.append(j)
        logp = add_probe_loglike(logp, float(probes[j]), j, stats)
    return int(np.argmax(logp)), order


def full_panel_classify(passive: np.ndarray, probes: np.ndarray, stats: Stats) -> int:
    """Use all interventions directly; no pointless adaptive ordering overhead."""
    logp = passive_logp(passive, stats)
    logp += -0.5 * np.sum(
        np.log(stats.probe_var)
        + (probes[None, :] - stats.probe_mean) ** 2 / stats.probe_var,
        axis=1,
    )
    return int(np.argmax(logp))


def run(seed: int = 17) -> dict:
    rng = np.random.default_rng(seed)
    readout = rng.standard_normal(N)
    readout /= np.linalg.norm(readout)
    experiments = [(poke, t) for poke in range(N) for t in TIMES]

    base_probe, base_passive_mean, base_passive_scale = build_baseline(
        readout, experiments
    )
    p_train, v_train, y_train = make_dataset(
        40,
        seed + 1,
        0,
        readout,
        experiments,
        base_probe,
        base_passive_mean,
        base_passive_scale,
    )
    p_test, v_test, y_test = make_dataset(
        60,
        seed + 2,
        100_000,
        readout,
        experiments,
        base_probe,
        base_passive_mean,
        base_passive_scale,
    )
    stats = fit_stats(p_train, v_train, y_train)

    budgets = (0, 1, 2, 3, 4, 6, 8)
    active_curve, random_curve = {}, {}
    sample_orders = {}
    for budget in budgets:
        active_hits = 0
        random_hits = 0
        rrng = np.random.default_rng(9000 + budget)
        orders = []
        for i in range(len(y_test)):
            pred, order = classify(p_test[i], v_test[i], stats, budget)
            active_hits += int(pred == y_test[i])
            if i < 6 and budget in (1, 3):
                orders.append(order)
            pred_r, _ = classify(
                p_test[i], v_test[i], stats, budget, rng=rrng, random_policy=True
            )
            random_hits += int(pred_r == y_test[i])
        active_curve[str(budget)] = active_hits / len(y_test)
        random_curve[str(budget)] = random_hits / len(y_test)
        if orders:
            sample_orders[str(budget)] = orders

    full_accuracy = float(
        np.mean(
            [
                full_panel_classify(p_test[i], v_test[i], stats) == y_test[i]
                for i in range(len(y_test))
            ]
        )
    )

    class_hits = {name: [0, 0] for name in CLASSES}
    for i in range(len(y_test)):
        pred, _ = classify(p_test[i], v_test[i], stats, 3)
        name = CLASSES[int(y_test[i])]
        class_hits[name][0] += int(pred == y_test[i])
        class_hits[name][1] += 1
    class_accuracy = {
        name: float(hits / total) for name, (hits, total) in class_hits.items()
    }

    decoded_orders = {
        budget: [
            [
                {"probe_node": int(experiments[j][0]), "read_time": int(experiments[j][1])}
                for j in order
            ]
            for order in orders
        ]
        for budget, orders in sample_orders.items()
    }

    return {
        "seed": seed,
        "classes": list(CLASSES),
        "n": N,
        "candidate_scalar_interventions": len(experiments),
        "train_samples": int(len(y_train)),
        "test_samples": int(len(y_test)),
        "passive_only_accuracy": float(active_curve["0"]),
        "active_accuracy_by_budget": {k: float(v) for k, v in active_curve.items()},
        "random_accuracy_by_budget": {k: float(v) for k, v in random_curve.items()},
        "three_poke_class_accuracy": class_accuracy,
        "full_panel_accuracy": full_accuracy,
        "example_active_queries": decoded_orders,
    }


def check(result: dict) -> None:
    active = result["active_accuracy_by_budget"]
    random = result["random_accuracy_by_budget"]

    assert 0.35 < result["passive_only_accuracy"] < 0.70
    assert active["3"] >= 0.95
    assert active["3"] >= random["3"] + 0.15
    assert active["1"] >= random["1"] + 0.08
    assert result["full_panel_accuracy"] >= 0.98
    for name, accuracy in result["three_poke_class_accuracy"].items():
        assert accuracy >= 0.85, (name, accuracy)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE3 PASS")


if __name__ == "__main__":
    main()
