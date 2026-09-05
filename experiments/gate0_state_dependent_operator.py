"""Gate 0: can a state-dependent operator be distinguished from a flat mixture?

Synthetic assay for RajoitustenHierarkia.

The world has:
  * a local geometric operator G (ring diffusion / smoothing),
  * a directed long-range operator C,
  * a scalar local state q that changes how strongly C is expressed,
  * a localized external input u.

The observed next state is

    y = tanh(0.72 Gx + 0.48 q Cx_prev + 0.35 u + noise)

The flat attacker knows G, C, x, x_prev and u, but not the interaction q*C.
The hierarchy model gets the state-conditioned operator term q*C.

This is intentionally a minimal identifiability assay, not a brain model.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np


@dataclass
class Sample:
    geom: np.ndarray
    conn: np.ndarray
    inp: np.ndarray
    q: float


def ring_operator(n: int, self_w: float = 0.45, near_w: float = 0.275) -> np.ndarray:
    g = np.zeros((n, n), dtype=float)
    for i in range(n):
        g[i, i] = self_w
        g[i, (i - 1) % n] = near_w
        g[i, (i + 1) % n] = near_w
    return g


def directed_operator(n: int, rng: np.random.Generator, degree: int = 2) -> np.ndarray:
    c = np.zeros((n, n), dtype=float)
    for i in range(n):
        choices = [
            j
            for j in range(n)
            if j != i and min((i - j) % n, (j - i) % n) > 1
        ]
        js = rng.choice(choices, size=degree, replace=False)
        ws = rng.uniform(0.3, 1.0, size=degree)
        ws /= ws.sum()
        for j, w in zip(js, ws):
            c[i, j] = w
    return c


def smooth_state(g: np.ndarray, rng: np.random.Generator, steps: int = 3) -> np.ndarray:
    x = rng.normal(size=g.shape[0])
    for _ in range(steps):
        x = g @ x
    return x / (np.std(x) + 1e-9)


def make_samples(
    g: np.ndarray,
    c: np.ndarray,
    rng: np.random.Generator,
    count: int,
    q_values: tuple[float, ...],
    noise_sd: float,
) -> tuple[list[Sample], np.ndarray]:
    n = g.shape[0]
    rows: list[Sample] = []
    ys: list[np.ndarray] = []

    for _ in range(count):
        x_prev = smooth_state(g, rng, 3)
        x = 0.75 * (g @ x_prev) + 0.25 * smooth_state(g, rng, 2)
        x /= np.std(x) + 1e-9

        u = np.zeros(n, dtype=float)
        idx = int(rng.integers(0, n))
        u[idx] = float(rng.choice([-1, 1])) * float(rng.uniform(0.4, 1.0))

        q = float(rng.choice(q_values))
        fg = g @ x
        fc = c @ x_prev
        z = 0.72 * fg + 0.48 * q * fc + 0.35 * u
        z += rng.normal(scale=noise_sd, size=n)

        rows.append(Sample(geom=fg, conn=fc, inp=u, q=q))
        ys.append(np.tanh(z))

    return rows, np.asarray(ys)


def design(rows: list[Sample], kind: str) -> np.ndarray:
    mats: list[np.ndarray] = []
    for row in rows:
        n = row.geom.size
        one = np.ones(n)
        if kind == "geometry":
            m = np.c_[row.geom, row.inp, one]
        elif kind == "connectivity":
            m = np.c_[row.conn, row.inp, one]
        elif kind == "flat":
            m = np.c_[row.geom, row.conn, row.inp, one]
        elif kind == "hierarchy":
            m = np.c_[row.geom, row.q * row.conn, row.inp, one]
        else:
            raise ValueError(kind)
        mats.append(m)
    return np.vstack(mats)


def fit(rows: list[Sample], y: np.ndarray, kind: str) -> np.ndarray:
    x = design(rows, kind)
    # The response law is known to all attackers. Inverting tanh lets each model
    # fit the best linear preactivation compatible with its own feature set.
    z = np.arctanh(np.clip(y.reshape(-1), -0.999999, 0.999999))
    beta, *_ = np.linalg.lstsq(x, z, rcond=None)
    return beta


def predict(rows: list[Sample], kind: str, beta: np.ndarray, n: int) -> np.ndarray:
    return np.tanh(design(rows, kind) @ beta).reshape(len(rows), n)


def counterfactual_pairs(
    g: np.ndarray,
    c: np.ndarray,
    seed: int,
    count: int = 200,
    q_low: float = 0.5,
    q_high: float = 1.7,
) -> tuple[list[Sample], list[Sample], np.ndarray, np.ndarray]:
    """Same instantaneous physical variables, different local operator state."""
    rng = np.random.default_rng(seed)
    n = g.shape[0]
    low_rows: list[Sample] = []
    high_rows: list[Sample] = []
    low_y: list[np.ndarray] = []
    high_y: list[np.ndarray] = []

    for _ in range(count):
        x_prev = smooth_state(g, rng, 3)
        x = 0.75 * (g @ x_prev) + 0.25 * smooth_state(g, rng, 2)
        x /= np.std(x) + 1e-9
        u = np.zeros(n)
        idx = int(rng.integers(0, n))
        u[idx] = float(rng.choice([-1, 1])) * float(rng.uniform(0.4, 1.0))
        fg = g @ x
        fc = c @ x_prev

        for q, rows, ys in (
            (q_low, low_rows, low_y),
            (q_high, high_rows, high_y),
        ):
            z = 0.72 * fg + 0.48 * q * fc + 0.35 * u
            rows.append(Sample(geom=fg, conn=fc, inp=u, q=q))
            ys.append(np.tanh(z))

    return low_rows, high_rows, np.asarray(low_y), np.asarray(high_y)


def run(seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    n = 24
    g = ring_operator(n)
    c = directed_operator(n, rng)

    train_rows, y_train = make_samples(
        g, c, rng, count=600, q_values=(0.5, 0.8, 1.1, 1.4), noise_sd=0.025
    )
    test_rows, y_test = make_samples(
        g, c, rng, count=240, q_values=(0.65, 0.95, 1.25, 1.7), noise_sd=0.025
    )

    kinds = ("geometry", "connectivity", "flat", "hierarchy")
    betas = {kind: fit(train_rows, y_train, kind) for kind in kinds}
    mse = {}
    for kind in kinds:
        p = predict(test_rows, kind, betas[kind], n)
        mse[kind] = float(np.mean((p - y_test) ** 2))

    # Harder held-out state: q=1.7 lies beyond the largest training state (1.4).
    hi = [i for i, row in enumerate(test_rows) if row.q == 1.7]
    high_q_mse = {}
    for kind in ("flat", "hierarchy"):
        rows = [test_rows[i] for i in hi]
        p = predict(rows, kind, betas[kind], n)
        high_q_mse[kind] = float(np.mean((p - y_test[hi]) ** 2))

    lo_rows, hi_rows, y_lo, y_hi = counterfactual_pairs(g, c, seed=99)
    true_delta = y_hi - y_lo
    cf = {
        "true_delta_rms": float(np.sqrt(np.mean(true_delta**2))),
    }
    for kind in ("flat", "hierarchy"):
        p_lo = predict(lo_rows, kind, betas[kind], n)
        p_hi = predict(hi_rows, kind, betas[kind], n)
        delta = p_hi - p_lo
        cf[f"{kind}_delta_rms"] = float(np.sqrt(np.mean(delta**2)))
        cf[f"{kind}_delta_mse"] = float(np.mean((delta - true_delta) ** 2))
        if float(np.std(delta)) > 0:
            cf[f"{kind}_delta_corr"] = float(
                np.corrcoef(delta.reshape(-1), true_delta.reshape(-1))[0, 1]
            )
        else:
            cf[f"{kind}_delta_corr"] = None

    return {
        "seed": seed,
        "n": n,
        "train_samples": len(train_rows),
        "test_samples": len(test_rows),
        "test_mse": mse,
        "held_out_q_1_7_mse": high_q_mse,
        "counterfactual": cf,
        "fit_coefficients": {
            kind: [float(x) for x in betas[kind]] for kind in kinds
        },
    }


def check(result: dict) -> None:
    mse = result["test_mse"]
    high = result["held_out_q_1_7_mse"]
    cf = result["counterfactual"]

    assert mse["hierarchy"] < 0.001
    assert mse["flat"] > 20 * mse["hierarchy"]
    assert high["flat"] > 50 * high["hierarchy"]
    assert cf["flat_delta_rms"] < 1e-12
    assert cf["hierarchy_delta_corr"] is not None
    assert cf["hierarchy_delta_corr"] > 0.999
    assert cf["hierarchy_delta_mse"] < 1e-6


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE0 PASS")


if __name__ == "__main__":
    main()
