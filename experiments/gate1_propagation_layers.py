"""Gate 1: geometry, long-range wiring, and delay as separable constraints.

The world is a stable linear propagation system on a ring:

    x[t+1] = a x[t] + b G x[t] + c C x[t-d] + e u[t] + noise

G is a local geometric smoothing/propagation operator.
C is a directed long-range operator.
d is a conduction delay.

Models are fitted on a base world, then tested after controlled changes to
geometry, wiring, delay, or all three. The delayed joint model must reuse the
same learned coefficients and is allowed only a tiny two-episode calibration
to re-identify delay after a delay intervention.

This is still a synthetic assay. It tests whether controlled interventions can
separate mechanisms that ordinary smooth-state prediction tends to blur.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np


TRUE_COEFF = np.array([0.15, 0.55, 0.25, 0.90], dtype=float)


@dataclass
class Episode:
    states: np.ndarray  # shape (T+1, N)
    inputs: np.ndarray  # shape (T, N)


def geometry_operator(n: int, warp: float = 0.0, phase: float = 0.0) -> np.ndarray:
    """Local ring propagation. warp changes left/right transport by position."""
    g = np.zeros((n, n), dtype=float)
    for i in range(n):
        asym = warp * np.sin(2.0 * np.pi * i / n + phase)
        left = 0.25 * (1.0 + asym)
        right = 0.25 * (1.0 - asym)
        g[i, i] = 0.50
        g[i, (i - 1) % n] = left
        g[i, (i + 1) % n] = right
    return g


def connectivity_operator(
    n: int, rng: np.random.Generator, degree: int = 2
) -> np.ndarray:
    """Directed non-local wiring; rows receive from distant source columns."""
    c = np.zeros((n, n), dtype=float)
    for i in range(n):
        candidates = [
            j for j in range(n) if min((i - j) % n, (j - i) % n) > 6
        ]
        js = rng.choice(candidates, size=degree, replace=False)
        weights = rng.uniform(0.5, 1.0, size=degree)
        weights /= weights.sum()
        c[i, js] = weights
    return c


def smooth_null_operator(n: int) -> np.ndarray:
    """Generic broad local smoother, not the true geometric operator."""
    s = np.zeros((n, n), dtype=float)
    weights = {0: 0.30, 1: 0.20, -1: 0.20, 2: 0.10, -2: 0.10, 3: 0.05, -3: 0.05}
    for i in range(n):
        for offset, weight in weights.items():
            s[i, (i + offset) % n] = weight
    return s


def simulate_episode(
    g: np.ndarray,
    c: np.ndarray,
    delay: int,
    rng: np.random.Generator,
    steps: int = 70,
    pulse_probability: float = 0.18,
    noise_sd: float = 0.002,
) -> Episode:
    n = g.shape[0]
    states = [np.zeros(n, dtype=float)]
    inputs: list[np.ndarray] = []

    for t in range(steps):
        x = states[t]
        x_delayed = states[t - delay] if t - delay >= 0 else np.zeros(n)

        u = np.zeros(n, dtype=float)
        if rng.random() < pulse_probability:
            idx = int(rng.integers(0, n))
            u[idx] = float(rng.choice([-1, 1])) * float(rng.uniform(0.6, 1.0))

        y = (
            TRUE_COEFF[0] * x
            + TRUE_COEFF[1] * (g @ x)
            + TRUE_COEFF[2] * (c @ x_delayed)
            + TRUE_COEFF[3] * u
        )
        y += rng.normal(scale=noise_sd, size=n)
        states.append(y)
        inputs.append(u)

    return Episode(states=np.asarray(states), inputs=np.asarray(inputs))


def make_episodes(
    g: np.ndarray,
    c: np.ndarray,
    delay: int,
    seed: int,
    count: int,
) -> list[Episode]:
    rng = np.random.default_rng(seed)
    return [simulate_episode(g, c, delay, rng) for _ in range(count)]


def design(
    episodes: list[Episode],
    g: np.ndarray,
    c: np.ndarray,
    delay: int,
    kind: str,
    smooth_null: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n = g.shape[0]
    mats: list[np.ndarray] = []
    ys: list[np.ndarray] = []

    for ep in episodes:
        for t, u in enumerate(ep.inputs):
            x = ep.states[t]
            y = ep.states[t + 1]
            x_delayed = ep.states[t - delay] if t - delay >= 0 else np.zeros(n)
            one = np.ones(n)

            if kind == "geometry":
                m = np.c_[x, g @ x, u, one]
            elif kind == "connectivity":
                m = np.c_[x, c @ x_delayed, u, one]
            elif kind == "flat_instant":
                m = np.c_[x, g @ x, c @ x, u, one]
            elif kind == "joint_delayed":
                m = np.c_[x, g @ x, c @ x_delayed, u, one]
            elif kind == "smooth_null":
                m = np.c_[x, smooth_null @ x, u, one]
            else:
                raise ValueError(kind)

            mats.append(m)
            ys.append(y)

    return np.vstack(mats), np.asarray(ys)


def fit_model(
    episodes: list[Episode],
    g: np.ndarray,
    c: np.ndarray,
    kind: str,
    smooth_null: np.ndarray,
    delay_candidates: tuple[int, ...],
) -> dict:
    best: dict | None = None
    for delay in delay_candidates:
        x, y = design(episodes, g, c, delay, kind, smooth_null)
        beta, *_ = np.linalg.lstsq(x, y.reshape(-1), rcond=None)
        pred = (x @ beta).reshape(y.shape)
        mse = float(np.mean((pred - y) ** 2))
        candidate = {"delay": delay, "beta": beta, "train_mse": mse}
        if best is None or mse < best["train_mse"]:
            best = candidate
    assert best is not None
    return best


def infer_delay(
    calibration: list[Episode],
    g: np.ndarray,
    c: np.ndarray,
    model: dict,
    smooth_null: np.ndarray,
    max_delay: int = 9,
) -> tuple[int, list[float]]:
    beta = model["beta"]
    scores: list[float] = []
    for delay in range(max_delay + 1):
        x, y = design(calibration, g, c, delay, "joint_delayed", smooth_null)
        pred = (x @ beta).reshape(y.shape)
        scores.append(float(np.mean((pred - y) ** 2)))
    return int(np.argmin(scores)), scores


def evaluate(
    episodes: list[Episode],
    g: np.ndarray,
    c: np.ndarray,
    true_delay: int,
    kind: str,
    model: dict,
    smooth_null: np.ndarray,
    supplied_delay: int | None = None,
) -> dict:
    if kind in ("joint_delayed", "connectivity"):
        delay = true_delay if supplied_delay is None else supplied_delay
    else:
        delay = 0

    x, y = design(episodes, g, c, delay, kind, smooth_null)
    pred = (x @ model["beta"]).reshape(y.shape)
    mse = float(np.mean((pred - y) ** 2))
    energy = float(np.mean(y**2)) + 1e-12
    return {"mse": mse, "nmse": mse / energy}


def run(seed: int = 42) -> dict:
    n = 48
    g0 = geometry_operator(n)
    c0 = connectivity_operator(n, np.random.default_rng(seed))
    smooth = smooth_null_operator(n)

    train = make_episodes(g0, c0, delay=4, seed=seed + 1, count=40)

    models = {
        "geometry": fit_model(train, g0, c0, "geometry", smooth, (0,)),
        "connectivity": fit_model(
            train, g0, c0, "connectivity", smooth, tuple(range(10))
        ),
        "flat_instant": fit_model(train, g0, c0, "flat_instant", smooth, (0,)),
        "joint_delayed": fit_model(
            train, g0, c0, "joint_delayed", smooth, tuple(range(10))
        ),
        "smooth_null": fit_model(train, g0, c0, "smooth_null", smooth, (0,)),
    }

    g_warp = geometry_operator(n, warp=0.40, phase=0.70)
    c_rewired = connectivity_operator(n, np.random.default_rng(99))
    variants = {
        "base": (g0, c0, 4, 1001),
        "rewire": (g0, c_rewired, 4, 1002),
        "warp": (g_warp, c0, 4, 1003),
        "delay7": (g0, c0, 7, 1004),
        "combined": (g_warp, c_rewired, 7, 1005),
    }

    results: dict[str, dict] = {}
    delay_calibration: dict[str, dict] = {}

    for name, (g, c, delay, test_seed) in variants.items():
        calibration = make_episodes(g, c, delay, seed=test_seed, count=2)
        inferred, scores = infer_delay(
            calibration, g, c, models["joint_delayed"], smooth, max_delay=9
        )
        test = make_episodes(g, c, delay, seed=test_seed + 100, count=12)

        row = {}
        for kind, model in models.items():
            if kind == "joint_delayed":
                row[kind] = evaluate(
                    test,
                    g,
                    c,
                    delay,
                    kind,
                    model,
                    smooth,
                    supplied_delay=inferred,
                )
            else:
                row[kind] = evaluate(test, g, c, delay, kind, model, smooth)
        results[name] = row
        delay_calibration[name] = {
            "true": delay,
            "inferred": inferred,
            "candidate_mse": scores,
        }

    return {
        "seed": seed,
        "n": n,
        "true_coefficients": TRUE_COEFF.tolist(),
        "fit": {
            name: {
                "delay": int(model["delay"]),
                "train_mse": float(model["train_mse"]),
                "coefficients": [float(x) for x in model["beta"]],
            }
            for name, model in models.items()
        },
        "delay_calibration": delay_calibration,
        "test": results,
    }


def check(result: dict) -> None:
    fit = result["fit"]
    assert fit["joint_delayed"]["delay"] == 4
    assert fit["connectivity"]["delay"] == 4

    for name, delay_info in result["delay_calibration"].items():
        assert delay_info["inferred"] == delay_info["true"], name

    for name, row in result["test"].items():
        joint = row["joint_delayed"]["nmse"]
        flat = row["flat_instant"]["nmse"]
        geom = row["geometry"]["nmse"]
        null = row["smooth_null"]["nmse"]
        assert joint < 0.003, (name, joint)
        assert flat > 10.0 * joint, (name, flat, joint)
        assert geom > 10.0 * joint, (name, geom, joint)
        assert null > 10.0 * joint, (name, null, joint)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE1 PASS")


if __name__ == "__main__":
    main()
