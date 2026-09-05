"""Gate 2: can a generic lagged state-space model erase the hierarchy claim?

The factorized Gate-1 model knows that the world decomposes into local geometry
G, directed long-range wiring C, and a delay d. A strong objection is that a
large generic VAR with enough history can fit the same trajectories without
those semantics.

This gate gives that objection substantial capacity:

    y[t+1] = B @ [x[t], x[t-1], ..., x[t-9], u[t], 1]

The base VAR has 6,360 learned coefficients for N=24. It is trained on the same
base episodes as the five-parameter factorized model. After an intervention,
the VAR may adapt all of its parameters from the same calibration stream using
ridge-to-prior updates. To make the attacker stronger, we report the best test
NMSE over a small regularization grid (oracle-tuned lambda).

The factorized model receives the changed G and C because those are the
controlled intervention variables, and uses two calibration episodes only to
re-identify delay. The point of the gate is therefore not "factorization wins
without side information". It asks how much compositional transfer that side
information buys compared with relearning a generic transition law.
"""

from __future__ import annotations

import argparse
import json

import numpy as np

from experiments.gate1_propagation_layers import (
    connectivity_operator,
    evaluate,
    fit_model,
    geometry_operator,
    infer_delay,
    make_episodes,
    smooth_null_operator,
)


MAX_LAG = 9
LAMBDA_GRID = (1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0)
CALIBRATION_SIZES = (0, 2, 4, 8, 16, 32)


def var_design(episodes, n: int, max_lag: int = MAX_LAG):
    x_rows = []
    y_rows = []
    for ep in episodes:
        for t, u in enumerate(ep.inputs):
            features = []
            for lag in range(max_lag + 1):
                if t - lag >= 0:
                    features.append(ep.states[t - lag])
                else:
                    features.append(np.zeros(n))
            features.append(u)
            features.append(np.ones(1))
            x_rows.append(np.concatenate(features))
            y_rows.append(ep.states[t + 1])
    return np.asarray(x_rows), np.asarray(y_rows)


def ridge_fit(x: np.ndarray, y: np.ndarray, lam: float, prior=None) -> np.ndarray:
    p = x.shape[1]
    lhs = x.T @ x + lam * np.eye(p)
    rhs = x.T @ y
    if prior is not None:
        rhs = rhs + lam * prior
    return np.linalg.solve(lhs, rhs)


def nmse(beta: np.ndarray, episodes, n: int) -> float:
    x, y = var_design(episodes, n)
    pred = x @ beta
    mse = float(np.mean((pred - y) ** 2))
    energy = float(np.mean(y**2)) + 1e-12
    return mse / energy


def oracle_adapted_var(
    base_beta: np.ndarray,
    calibration,
    test,
    n: int,
) -> dict:
    """Give the generic attacker the best lambda on held-out test data.

    This is intentionally favorable to the attacker and should be read as an
    upper bound, not a deployable model-selection procedure.
    """
    x_cal, y_cal = var_design(calibration, n)
    candidates = []
    for lam in LAMBDA_GRID:
        beta = ridge_fit(x_cal, y_cal, lam=lam, prior=base_beta)
        candidates.append((nmse(beta, test, n), lam))
    best_nmse, best_lambda = min(candidates)
    return {
        "nmse": float(best_nmse),
        "oracle_lambda": float(best_lambda),
    }


def run(seed: int = 42) -> dict:
    n = 24
    g0 = geometry_operator(n)
    c0 = connectivity_operator(n, np.random.default_rng(seed))
    smooth = smooth_null_operator(n)

    train = make_episodes(g0, c0, delay=4, seed=seed + 1, count=60)

    # Factorized Gate-1 model: five learned scalar coefficients, plus supplied
    # controlled operators G and C.
    factorized = fit_model(
        train,
        g0,
        c0,
        "joint_delayed",
        smooth,
        tuple(range(MAX_LAG + 1)),
    )

    # Generic VAR: all lagged state coordinates and full output matrix.
    x_train, y_train = var_design(train, n)
    base_var = ridge_fit(x_train, y_train, lam=1e-5)

    g_warp = geometry_operator(n, warp=0.80, phase=0.70)
    c_rewired = connectivity_operator(n, np.random.default_rng(99))
    variants = {
        "rewire": (g0, c_rewired, 4, 501),
        "warp": (g_warp, c0, 4, 502),
        "delay7": (g0, c0, 7, 503),
        "combined": (g_warp, c_rewired, 7, 504),
    }

    base_test = make_episodes(g0, c0, delay=4, seed=400, count=20)
    base_var_nmse = nmse(base_var, base_test, n)

    results = {}
    for name, (g, c, delay, local_seed) in variants.items():
        calibration_pool = make_episodes(
            g, c, delay=delay, seed=800 + local_seed, count=max(CALIBRATION_SIZES)
        )
        test = make_episodes(g, c, delay=delay, seed=500 + local_seed, count=20)

        # Same tiny calibration budget as Gate 1 for factorized delay recovery.
        factor_cal = calibration_pool[:2]
        inferred_delay, _ = infer_delay(
            factor_cal,
            g,
            c,
            factorized,
            smooth,
            max_delay=MAX_LAG,
        )
        factor_eval = evaluate(
            test,
            g,
            c,
            delay,
            "joint_delayed",
            factorized,
            smooth,
            supplied_delay=inferred_delay,
        )

        var_curve = {}
        for k in CALIBRATION_SIZES:
            if k == 0:
                var_curve[str(k)] = {
                    "nmse": float(nmse(base_var, test, n)),
                    "oracle_lambda": None,
                }
            else:
                var_curve[str(k)] = oracle_adapted_var(
                    base_var,
                    calibration_pool[:k],
                    test,
                    n,
                )

        results[name] = {
            "true_delay": delay,
            "factorized_inferred_delay": int(inferred_delay),
            "factorized_two_episode_nmse": float(factor_eval["nmse"]),
            "generic_var": var_curve,
        }

    feature_count = n * (MAX_LAG + 1) + n + 1
    var_parameters = feature_count * n

    return {
        "seed": seed,
        "n": n,
        "max_lag": MAX_LAG,
        "factorized_learned_parameters": int(len(factorized["beta"])),
        "generic_var_features_per_output": int(feature_count),
        "generic_var_learned_parameters": int(var_parameters),
        "factorized_base_delay": int(factorized["delay"]),
        "factorized_coefficients": [float(x) for x in factorized["beta"]],
        "generic_var_base_test_nmse": float(base_var_nmse),
        "results": results,
    }


def check(result: dict) -> None:
    assert result["factorized_base_delay"] == 4
    assert result["generic_var_learned_parameters"] == 6360
    assert result["generic_var_base_test_nmse"] < 0.002

    for name, row in result["results"].items():
        assert row["factorized_inferred_delay"] == row["true_delay"], name
        factor = row["factorized_two_episode_nmse"]
        var2 = row["generic_var"]["2"]["nmse"]
        var16 = row["generic_var"]["16"]["nmse"]

        assert factor < 0.0015, (name, factor)
        # With the same two calibration episodes, factorization should buy a
        # large transfer advantage even against oracle lambda selection.
        assert var2 > 5.0 * factor, (name, var2, factor)
        # The generic model is allowed to catch up with enough new data. This
        # prevents the result from becoming a universal-superiority claim.
        assert var16 < 0.002, (name, var16)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE2 PASS")


if __name__ == "__main__":
    main()
