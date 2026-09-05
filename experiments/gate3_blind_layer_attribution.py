"""Gate 3: can a bounded observer infer which constraint family changed?

This is a deliberately narrow discoverability assay.

The observer is *not* given G, C, delay, gain, or the changed operator.  It gets:

1. four cheap passive residual statistics;
2. a menu of reversible addressed scalar interventions;
3. one scalar consequence per paid intervention.

Six latent causes are present:

    none / local geometry / long-range wiring / delay / gain / input statistics

A training bank supplies examples of those cause classes, but not the hidden
operators themselves.  The active observer learns only empirical consequence
statistics for each candidate intervention.  At test time it starts from the
cheap passive evidence, then chooses the next poke by a Fisher-like expected
separation score under its current posterior.

Important boundary: all samples share one underlying substrate topology; only
perturbation magnitude/sign and stochastic drive change.  This gate asks
whether the causal families are distinguishable from bounded consequences at
all.  Generalization across unseen substrates is left for Gate 3B.
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
class ClassStats:
    passive_mean: np.ndarray
    passive_var: np.ndarray
    probe_mean: np.ndarray
    probe_var: np.ndarray


def make_operators(n: int = N, seed: int = 7) -> tuple[np.ndarray, np.ndarray]:
    """Local ring geometry plus sparse directed long-range coupling."""
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


def perturb(kind: str, magnitude: float) -> tuple[np.ndarray, np.ndarray, int, float, float, float]:
    """Return hidden changed world parameters.

    The classifier never receives these arrays/labels directly.
    """
    g, c = make_operators()
    delay = BASE_DELAY
    gain = 1.0
    input_shift = 0.0
    input_scale = 1.0

    if kind == "geometry":
        # Local metric/transport deformation around one neighborhood.
        i = 5
        delta = 0.12 * magnitude
        g[i, i] -= delta
        g[i, (i + 1) % N] += delta
    elif kind == "wiring":
        # Directed nonlocal path modification.
        c = c.copy()
        c[17, 5] += 0.18 * magnitude
    elif kind == "delay":
        delay = 5 if magnitude > 0 else 2
    elif kind == "gain":
        gain = 1.0 + 0.12 * magnitude
    elif kind == "input":
        # Operator unchanged; only external drive statistics move.
        input_shift = 0.08 * magnitude
        input_scale = 1.0 + 0.25 * abs(magnitude)
    elif kind != "none":
        raise ValueError(kind)

    return g, c, delay, gain, input_shift, input_scale


def impulse_response(
    g: np.ndarray,
    c: np.ndarray,
    delay: int,
    gain: float,
    poke: int,
    horizon: int = MAX_HORIZON,
) -> np.ndarray:
    a, b, cc = 0.18, 0.55, 0.22
    states = np.zeros((horizon + 1, N))
    states[0, poke] = 1.0
    for t in range(horizon):
        delayed = states[t - delay] if t - delay >= 0 else np.zeros(N)
        z = a * states[t] + b * (g @ states[t]) + cc * (c @ delayed)
        states[t + 1] = np.tanh(gain * z)
    return states


def spontaneous(
    g: np.ndarray,
    c: np.ndarray,
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


def passive_stats(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    y = states[50:] @ readout
    return np.array(
        [
            float(np.mean(y)),
            float(np.std(y)),
            float(np.mean(y[:-1] * y[1:])),
            float(np.mean(np.abs(y))),
        ]
    )


def gaussian_loglike(x: np.ndarray, mean: np.ndarray, var: np.ndarray) -> float:
    return float(-0.5 * np.sum(np.log(var) + (x - mean) ** 2 / var))


def fit_stats(passive: np.ndarray, probes: np.ndarray, labels: np.ndarray) -> dict[int, ClassStats]:
    out: dict[int, ClassStats] = {}
    for ci in range(len(CLASSES)):
        mask = labels == ci
        out[ci] = ClassStats(
            passive_mean=np.mean(passive[mask], axis=0),
            passive_var=np.var(passive[mask], axis=0) + 1e-3,
            probe_mean=np.mean(probes[mask], axis=0),
            probe_var=np.var(probes[mask], axis=0) + 1e-7,
        )
    return out


def passive_log_posterior(x: np.ndarray, stats: dict[int, ClassStats]) -> np.ndarray:
    return np.asarray(
        [
            gaussian_loglike(x, stats[ci].passive_mean, stats[ci].passive_var)
            for ci in range(len(CLASSES))
        ]
    )


def choose_probe(
    logp: np.ndarray,
    used: set[int],
    stats: dict[int, ClassStats],
) -> int:
    """Choose the scalar experiment with highest posterior-weighted separation."""
    p = np.exp(logp - np.max(logp))
    p /= np.sum(p)

    best_j = -1
    best_score = -np.inf
    width = len(stats[0].probe_mean)
    for j in range(width):
        if j in used:
            continue
        means = np.asarray([stats[ci].probe_mean[j] for ci in range(len(CLASSES))])
        variances = np.asarray([stats[ci].probe_var[j] for ci in range(len(CLASSES))])
        mixture_mean = float(np.sum(p * means))
        between = float(np.sum(p * (means - mixture_mean) ** 2))
        within = float(np.sum(p * variances))
        score = between / (within + 1e-12)
        if score > best_score:
            best_score = score
            best_j = j
    return best_j


def classify(
    passive: np.ndarray,
    probes: np.ndarray,
    stats: dict[int, ClassStats],
    budget: int,
    rng: np.random.Generator | None = None,
    random_policy: bool = False,
) -> tuple[int, list[int]]:
    logp = passive_log_posterior(passive, stats)
    used: set[int] = set()
    order: list[int] = []

    for _ in range(budget):
        candidates = [j for j in range(len(probes)) if j not in used]
        if random_policy:
            if rng is None:
                raise ValueError("random policy needs rng")
            j = int(rng.choice(candidates))
        else:
            j = choose_probe(logp, used, stats)
        used.add(j)
        order.append(j)

        observation = probes[j]
        for ci in range(len(CLASSES)):
            mean = stats[ci].probe_mean[j]
            var = stats[ci].probe_var[j]
            logp[ci] += -0.5 * (np.log(var) + (observation - mean) ** 2 / var)

    return int(np.argmax(logp)), order


def make_dataset(
    per_class: int,
    seed: int,
    sample_offset: int,
    readout: np.ndarray,
    base_passive_mean: np.ndarray,
    base_passive_scale: np.ndarray,
    base_probe: np.ndarray,
    experiments: list[tuple[int, int]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    passive_rows = []
    probe_rows = []
    labels = []
    sid = sample_offset

    for ci, kind in enumerate(CLASSES):
        for _ in range(per_class):
            if kind == "none":
                magnitude = 1.0
            elif kind == "delay":
                magnitude = 1.0 if rng.random() < 0.5 else -1.0
            else:
                magnitude = float(rng.uniform(0.7, 1.3))
                if rng.random() < 0.5:
                    magnitude *= -1.0

            g, c, delay, gain, input_shift, input_scale = perturb(kind, magnitude)
            states = spontaneous(
                g,
                c,
                delay,
                gain,
                input_shift,
                input_scale,
                seed=10_000 + sid,
            )
            p = (passive_stats(states, readout) - base_passive_mean) / base_passive_scale

            # A paid experiment is (poke-address, read-time) -> one scalar global
            # prediction error relative to the remembered baseline response.
            responses = []
            cache: dict[int, np.ndarray] = {}
            for j, (poke, t) in enumerate(experiments):
                if poke not in cache:
                    cache[poke] = impulse_response(g, c, delay, gain, poke)
                y = float(readout @ cache[poke][t])
                error = abs(y - base_probe[j]) + float(rng.normal(0.0, MEASUREMENT_NOISE))
                responses.append(error)

            passive_rows.append(p)
            probe_rows.append(np.asarray(responses))
            labels.append(ci)
            sid += 1

    return np.asarray(passive_rows), np.asarray(probe_rows), np.asarray(labels)


def run(seed: int = 17) -> dict:
    rng = np.random.default_rng(seed)
    readout = rng.standard_normal(N)
    readout /= np.linalg.norm(readout)

    experiments = [(poke, t) for poke in range(N) for t in TIMES]
    g0, c0 = make_operators()

    # Remembered baseline intervention consequences.
    base_probe = []
    for poke in range(N):
        response = impulse_response(g0, c0, BASE_DELAY, 1.0, poke)
        for t in TIMES:
            base_probe.append(float(readout @ response[t]))
    base_probe = np.asarray(base_probe)

    # Cheap passive residual normalization comes from ordinary baseline life,
    # not from any post-change operator label.
    baseline_bank = []
    for k in range(50):
        baseline_bank.append(
            passive_stats(
                spontaneous(g0, c0, BASE_DELAY, 1.0, 0.0, 1.0, seed=2000 + k),
                readout,
            )
        )
    baseline_bank = np.asarray(baseline_bank)
    base_passive_mean = np.mean(baseline_bank, axis=0)
    base_passive_scale = np.std(baseline_bank, axis=0) + 1e-6

    train = make_dataset(
        per_class=60,
        seed=seed + 1,
        sample_offset=0,
        readout=readout,
        base_passive_mean=base_passive_mean,
        base_passive_scale=base_passive_scale,
        base_probe=base_probe,
        experiments=experiments,
    )
    test = make_dataset(
        per_class=80,
        seed=seed + 2,
        sample_offset=100_000,
        readout=readout,
        base_passive_mean=base_passive_mean,
        base_passive_scale=base_passive_scale,
        base_probe=base_probe,
        experiments=experiments,
    )
    p_train, v_train, y_train = train
    p_test, v_test, y_test = test
    stats = fit_stats(p_train, v_train, y_train)

    budgets = (0, 1, 2, 3, 4, 6, 8)
    active_curve = {}
    random_curve = {}
    selected_examples = {}

    for budget in budgets:
        active_correct = 0
        random_correct = 0
        random_rng = np.random.default_rng(9000 + budget)
        first_orders = []
        for i in range(len(y_test)):
            pred, order = classify(p_test[i], v_test[i], stats, budget)
            active_correct += int(pred == y_test[i])
            if i < 6:
                first_orders.append(order)

            pred_random, _ = classify(
                p_test[i],
                v_test[i],
                stats,
                budget,
                rng=random_rng,
                random_policy=True,
            )
            random_correct += int(pred_random == y_test[i])

        active_curve[str(budget)] = active_correct / len(y_test)
        random_curve[str(budget)] = random_correct / len(y_test)
        if budget in (1, 3):
            selected_examples[str(budget)] = first_orders

    # Full empirical intervention panel: an upper bound using all scalar pokes,
    # but still no hidden operator arrays.
    full_correct = 0
    for i in range(len(y_test)):
        pred, _ = classify(p_test[i], v_test[i], stats, len(experiments))
        full_correct += int(pred == y_test[i])
    full_accuracy = full_correct / len(y_test)

    # Per-class accuracy for the three-poke policy makes sure one easy class
    # is not carrying the aggregate result.
    class_hits = {name: [0, 0] for name in CLASSES}
    for i in range(len(y_test)):
        pred, _ = classify(p_test[i], v_test[i], stats, 3)
        name = CLASSES[int(y_test[i])]
        class_hits[name][1] += 1
        class_hits[name][0] += int(pred == y_test[i])
    class_accuracy = {name: hits / total for name, (hits, total) in class_hits.items()}

    decoded_examples = {}
    for budget, rows in selected_examples.items():
        decoded_examples[budget] = [
            [
                {
                    "probe_node": int(experiments[j][0]),
                    "read_time": int(experiments[j][1]),
                }
                for j in order
            ]
            for order in rows
        ]

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
        "three_poke_class_accuracy": {k: float(v) for k, v in class_accuracy.items()},
        "full_panel_accuracy": float(full_accuracy),
        "example_active_queries": decoded_examples,
    }


def check(result: dict) -> None:
    active = result["active_accuracy_by_budget"]
    random = result["random_accuracy_by_budget"]

    # Passive evidence should be useful but insufficient.
    assert 0.35 < result["passive_only_accuracy"] < 0.70

    # Active consequences should make the cause families sharply identifiable
    # with a tiny fraction of the 192 available scalar experiments.
    assert active["3"] >= 0.95
    assert active["3"] >= random["3"] + 0.15
    assert active["1"] >= random["1"] + 0.08
    assert result["full_panel_accuracy"] >= 0.98

    # No class is allowed to be a complete blind spot at the headline budget.
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
