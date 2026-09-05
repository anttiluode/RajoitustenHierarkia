"""Gate 3B: does active selection survive a learned fixed-probe attacker?

Gate 3A compared adaptive addressed pokes against random pokes on one fixed
substrate.  That is not enough: if the perturbation families always leave their
signatures in the same places, a boring diagnostic panel can be learned once
and reused forever.

This attacker greedily selects a fixed set of scalar experiments using training
accuracy.  It is intentionally strong and even selects on the same training set
used to estimate class likelihoods.  If one or two fixed probes solve the test
set, then Gate 3A did NOT establish a need for adaptive poking.
"""

from __future__ import annotations

import argparse
import json

import numpy as np

from experiments.gate3_blind_layer_attribution import (
    CLASSES,
    N,
    TIMES,
    build_baseline,
    classify,
    fit_stats,
    make_dataset,
    passive_logp,
)


def likelihood_tensors(passive: np.ndarray, probes: np.ndarray, stats):
    base = np.asarray([passive_logp(row, stats) for row in passive])
    # sample x class x candidate experiment
    contribution = -0.5 * (
        np.log(stats.probe_var)[None, :, :]
        + (probes[:, None, :] - stats.probe_mean[None, :, :]) ** 2
        / stats.probe_var[None, :, :]
    )
    return base, contribution


def greedy_fixed_panel(
    train_logp: np.ndarray,
    train_contrib: np.ndarray,
    train_labels: np.ndarray,
    test_logp: np.ndarray,
    test_contrib: np.ndarray,
    test_labels: np.ndarray,
    experiments: list[tuple[int, int]],
    size: int = 3,
):
    selected: list[int] = []
    train_current = train_logp.copy()
    test_current = test_logp.copy()
    curve = {}

    for step in range(1, size + 1):
        best_j = None
        best_train_accuracy = -1.0
        for j in range(train_contrib.shape[2]):
            if j in selected:
                continue
            prediction = np.argmax(train_current + train_contrib[:, :, j], axis=1)
            accuracy = float(np.mean(prediction == train_labels))
            if accuracy > best_train_accuracy:
                best_train_accuracy = accuracy
                best_j = j

        assert best_j is not None
        selected.append(best_j)
        train_current += train_contrib[:, :, best_j]
        test_current += test_contrib[:, :, best_j]
        test_accuracy = float(np.mean(np.argmax(test_current, axis=1) == test_labels))
        curve[str(step)] = {
            "train_accuracy": best_train_accuracy,
            "test_accuracy": test_accuracy,
            "added_probe": {
                "node": int(experiments[best_j][0]),
                "read_time": int(experiments[best_j][1]),
            },
        }

    return selected, curve


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

    train_logp, train_contrib = likelihood_tensors(p_train, v_train, stats)
    test_logp, test_contrib = likelihood_tensors(p_test, v_test, stats)
    selected, fixed_curve = greedy_fixed_panel(
        train_logp,
        train_contrib,
        y_train,
        test_logp,
        test_contrib,
        y_test,
        experiments,
        size=3,
    )

    active_curve = {}
    random_curve = {}
    for budget in (0, 1, 2, 3):
        active_hits = 0
        random_hits = 0
        rrng = np.random.default_rng(7000 + budget)
        for i in range(len(y_test)):
            pred, _ = classify(p_test[i], v_test[i], stats, budget)
            active_hits += int(pred == y_test[i])
            pred_r, _ = classify(
                p_test[i],
                v_test[i],
                stats,
                budget,
                rng=rrng,
                random_policy=True,
            )
            random_hits += int(pred_r == y_test[i])
        active_curve[str(budget)] = active_hits / len(y_test)
        random_curve[str(budget)] = random_hits / len(y_test)

    return {
        "seed": seed,
        "classification": "STATIC_PANEL_ATTACKER_COLLAPSES_ACTIVE_NECESSITY_ON_FIXED_SUBSTRATE",
        "classes": list(CLASSES),
        "candidate_scalar_interventions": len(experiments),
        "active_accuracy": {k: float(v) for k, v in active_curve.items()},
        "random_accuracy": {k: float(v) for k, v in random_curve.items()},
        "fixed_panel_curve": fixed_curve,
        "fixed_panel": [
            {
                "node": int(experiments[j][0]),
                "read_time": int(experiments[j][1]),
            }
            for j in selected
        ],
    }


def check(result: dict) -> None:
    fixed1 = result["fixed_panel_curve"]["1"]["test_accuracy"]
    fixed2 = result["fixed_panel_curve"]["2"]["test_accuracy"]
    active1 = result["active_accuracy"]["1"]
    active3 = result["active_accuracy"]["3"]

    # The negative result is the gate: on this fixed substrate a static learned
    # panel is already enough, so adaptivity has not earned architectural work.
    assert fixed1 >= 0.90
    assert fixed1 >= active1 + 0.20
    assert fixed2 >= 0.98
    assert fixed2 >= active3 - 0.02


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE3B PASS (negative result preserved)")


if __name__ == "__main__":
    main()
