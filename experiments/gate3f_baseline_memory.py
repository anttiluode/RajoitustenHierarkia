"""Gate 3F: does remembered baseline evidence amortize repeated diagnosis?

Gate 3D made current-world before/after differencing the useful invariant.
Gate 3E then showed that a learned STATIC eight-probe spatial cover beats two
plausible adaptive post-change acquisition heuristics on the synthetic task.

That leaves an obvious cheat: the healthy baseline table has been treated as
perfect and free.

This gate keeps the strong G3E static panel and studies repeated reversible
incidents while the healthy substrate drifts slowly.  Four baseline policies
are compared:

1. REFRESH_EVERY: reacquire all eight healthy baseline scalars before every
   incident (reference accuracy, expensive).
2. FROZEN: acquire the panel once and reuse it forever.
3. PERIODIC_4: acquire once, then refresh every four incidents.
4. SENTINEL: acquire once; before each incident spend one healthy sentinel
   measurement and refresh the other seven panel entries only when the
   sentinel deviates by more than a fixed threshold.

Every policy spends the same eight post-change measurements per incident.
The substrate drift is deterministic, small, and independent of the local
fault.  A useful result requires BOTH:
- frozen memory eventually becomes stale;
- some reuse policy preserves near-reference diagnosis at lower cumulative
  measurement cost.

A sentinel trigger is included as an attacker against the temptation to call
selective refresh 'active memory'. If a simple periodic schedule wins at
matched cost, preserve that negative.
"""

from __future__ import annotations

import argparse
import json

import numpy as np

from experiments.gate3d_unseen_substrates import (
    CAUSES,
    MEASUREMENT_NOISE,
    N,
    TIMES,
    make_world,
    response_vector,
)
from experiments.gate3e_active_delta_budget import (
    Event,
    classify_sequence,
    fit_relative_delta_model,
    training_events,
)


INCIDENTS = 12
HELD_OUT_WORLDS = 30
DRIFT_RATE = 0.001
PERIOD = 4
SENTINEL_THRESHOLD = 0.008

# Locked eight-probe panel learned in Gate 3E on the 30 training substrates.
# Tuples are (poke node, actual read time).
PANEL_PAIRS = (
    (22, 4),
    (15, 7),
    (11, 4),
    (19, 7),
    (6, 4),
    (1, 4),
    (13, 5),
    (4, 5),
)

POLICIES = ("refresh_every", "frozen", "periodic_4", "sentinel")


def response_table(g: np.ndarray, c: np.ndarray, gain: np.ndarray) -> np.ndarray:
    return np.stack([response_vector(g, c, gain, poke) for poke in range(N)])


def measure(exact: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return exact + rng.normal(0.0, MEASUREMENT_NOISE, exact.shape)


def drift_world(
    g0: np.ndarray,
    c0: np.ndarray,
    step: int,
    world_seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Small healthy substrate drift, independent of the incident.

    There is a mild common change in local-vs-long-range transport plus a
    world-specific redistribution among each node's local self/left/right
    coefficients.  The total drift over 12 incidents is only about one percent
    in the common scale, but it is enough to make a permanently frozen
    consequence table measurably stale.
    """
    rng = np.random.default_rng(world_seed + 424_242)
    dg = np.zeros_like(g0)
    for i in range(N):
        left = float(rng.normal())
        right = float(rng.normal())
        dg[i, i] = -0.5 * (left + right)
        dg[i, (i - 1) % N] = left
        dg[i, (i + 1) % N] = right
    dg *= DRIFT_RATE * 0.5

    g = (1.0 + DRIFT_RATE * step) * g0 + step * dg
    c = (1.0 - 0.6 * DRIFT_RATE * step) * c0

    # Keep the family comfortably stable without erasing the accumulated drift.
    norm = float(np.linalg.norm(g, 2))
    if norm > 1.02:
        g *= 1.02 / norm
    return g, c, np.ones(N)


def perturb_current_world(
    g: np.ndarray,
    c: np.ndarray,
    gain: np.ndarray,
    cause: str,
    address: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Apply the same local event family as Gates 3D/3E to the drifted world."""
    g2 = g.copy()
    c2 = c.copy()
    gain2 = gain.copy()
    rng = np.random.default_rng(seed)

    if cause == "geometry":
        delta = 0.13
        g2[address, address] -= delta
        g2[address, (address + 1) % N] += delta
    elif cause == "wiring":
        candidates = [
            target
            for target in range(N)
            if min((target - address) % N, (address - target) % N) > 3
        ]
        target = int(rng.choice(candidates))
        c2[target, address] += 0.18
    elif cause == "gain":
        gain2[address] *= 1.18
    else:
        raise ValueError(cause)
    return g2, c2, gain2


def panel_indices(exps: list[tuple[int, int]]) -> list[int]:
    time_index = {t: i for i, t in enumerate(TIMES)}
    return [exps.index((poke, time_index[t])) for poke, t in PANEL_PAIRS]


def classify_from_memory(
    post: np.ndarray,
    memory: np.ndarray,
    cause: str,
    address: int,
    panel: list[int],
    mu: np.ndarray,
    var: np.ndarray,
    hyps: list[tuple[str, int]],
    exps: list[tuple[int, int]],
) -> bool:
    event = Event(cause, address, post - memory)
    prediction = classify_sequence(event, panel, mu, var, hyps, exps)
    return prediction == (cause, address)


def run(seed: int = 17) -> dict:
    # Reuse the Gate-3E transferable delta likelihood model.  Only the baseline
    # acquisition policy changes in this gate.
    mu, var, hyps, exps = fit_relative_delta_model(training_events())
    panel = panel_indices(exps)
    sentinel_j = panel[0]
    sentinel_poke, sentinel_ti = exps[sentinel_j]

    stats = {
        name: {
            "correct": 0,
            "healthy_baseline_calls": 0,
            "post_change_calls": 0,
            "full_panel_refreshes": 0,
            "accuracy_by_incident_hits": np.zeros(INCIDENTS, dtype=int),
        }
        for name in POLICIES
    }

    for wi in range(30, 30 + HELD_OUT_WORLDS):
        world_seed = 1000 + wi
        g0, c0 = make_world(world_seed)

        # Medium memory starts with one healthy panel acquisition.  The arrays
        # retain all entries for convenience, but the accounting charges only
        # the eight panel scalars that each policy is allowed to remember.
        g, c, gain = drift_world(g0, c0, 0, world_seed)
        healthy0 = response_table(g, c, gain)
        initial_memory = measure(healthy0, 100_000 + world_seed)
        memory = {
            "frozen": initial_memory.copy(),
            "periodic_4": initial_memory.copy(),
            "sentinel": initial_memory.copy(),
        }
        for name in ("frozen", "periodic_4", "sentinel"):
            stats[name]["healthy_baseline_calls"] += len(panel)
            stats[name]["full_panel_refreshes"] += 1

        for step in range(INCIDENTS):
            g, c, gain = drift_world(g0, c0, step, world_seed)
            healthy_exact = response_table(g, c, gain)

            # Locked deterministic incident schedule with all three causes and
            # moving addresses in every held-out substrate.
            cause = CAUSES[(wi + step) % len(CAUSES)]
            address = int((wi * 7 + step * 5) % N)
            event_seed = 200_000 + wi * 100 + step
            g2, c2, gain2 = perturb_current_world(
                g, c, gain, cause, address, event_seed
            )
            post_exact = response_table(g2, c2, gain2)
            post = measure(post_exact, 300_000 + event_seed)

            # Every policy pays the same eight post-change scalar calls.
            for name in POLICIES:
                stats[name]["post_change_calls"] += len(panel)

            # Reference: current healthy baseline on every incident.
            fresh = measure(healthy_exact, 400_000 + event_seed)
            stats["refresh_every"]["healthy_baseline_calls"] += len(panel)
            stats["refresh_every"]["full_panel_refreshes"] += 1
            ok = classify_from_memory(
                post, fresh, cause, address, panel, mu, var, hyps, exps
            )
            stats["refresh_every"]["correct"] += int(ok)
            stats["refresh_every"]["accuracy_by_incident_hits"][step] += int(ok)

            # Frozen memory: cheapest, but allowed to go stale.
            ok = classify_from_memory(
                post,
                memory["frozen"],
                cause,
                address,
                panel,
                mu,
                var,
                hyps,
                exps,
            )
            stats["frozen"]["correct"] += int(ok)
            stats["frozen"]["accuracy_by_incident_hits"][step] += int(ok)

            # Boring periodic refresh every four incidents.
            if step > 0 and step % PERIOD == 0:
                memory["periodic_4"] = measure(
                    healthy_exact, 500_000 + event_seed
                )
                stats["periodic_4"]["healthy_baseline_calls"] += len(panel)
                stats["periodic_4"]["full_panel_refreshes"] += 1
            ok = classify_from_memory(
                post,
                memory["periodic_4"],
                cause,
                address,
                panel,
                mu,
                var,
                hyps,
                exps,
            )
            stats["periodic_4"]["correct"] += int(ok)
            stats["periodic_4"]["accuracy_by_incident_hits"][step] += int(ok)

            # One-scalar change detector.  The sentinel itself costs one healthy
            # measurement each incident.  A trigger then buys the other seven
            # panel entries, so a refresh still costs eight healthy scalars in
            # total for that incident.
            sentinel = float(
                healthy_exact[sentinel_poke, sentinel_ti]
                + np.random.default_rng(600_000 + event_seed).normal(
                    0.0, MEASUREMENT_NOISE
                )
            )
            stats["sentinel"]["healthy_baseline_calls"] += 1
            remembered_sentinel = float(
                memory["sentinel"][sentinel_poke, sentinel_ti]
            )
            if abs(sentinel - remembered_sentinel) > SENTINEL_THRESHOLD:
                refreshed = measure(healthy_exact, 700_000 + event_seed)
                refreshed[sentinel_poke, sentinel_ti] = sentinel
                memory["sentinel"] = refreshed
                stats["sentinel"]["healthy_baseline_calls"] += len(panel) - 1
                stats["sentinel"]["full_panel_refreshes"] += 1

            ok = classify_from_memory(
                post,
                memory["sentinel"],
                cause,
                address,
                panel,
                mu,
                var,
                hyps,
                exps,
            )
            stats["sentinel"]["correct"] += int(ok)
            stats["sentinel"]["accuracy_by_incident_hits"][step] += int(ok)

    total_incidents = HELD_OUT_WORLDS * INCIDENTS
    out = {}
    for name in POLICIES:
        s = stats[name]
        total_calls = s["healthy_baseline_calls"] + s["post_change_calls"]
        correct = int(s["correct"])
        out[name] = {
            "joint_accuracy": correct / total_incidents,
            "correct": correct,
            "healthy_baseline_calls": int(s["healthy_baseline_calls"]),
            "post_change_calls": int(s["post_change_calls"]),
            "total_scalar_calls": int(total_calls),
            "calls_per_incident": total_calls / total_incidents,
            "calls_per_correct_diagnosis": total_calls / max(1, correct),
            "full_panel_refreshes": int(s["full_panel_refreshes"]),
            "accuracy_by_incident": (
                s["accuracy_by_incident_hits"] / HELD_OUT_WORLDS
            ).tolist(),
        }

    return {
        "seed": seed,
        "classification": (
            "PERIODIC_BASELINE_MEMORY_AMORTIZES_REPEATED_DIAGNOSIS_UNDER_SLOW_DRIFT;_"
            "FROZEN_MEMORY_GOES_STALE;_SIMPLE_PERIODIC_REFRESH_BEATS_ONE_SENTINEL_"
            "AT_MATCHED_COST"
        ),
        "held_out_worlds": HELD_OUT_WORLDS,
        "incidents_per_world": INCIDENTS,
        "total_incidents": total_incidents,
        "drift_rate_per_incident": DRIFT_RATE,
        "panel_size": len(panel),
        "panel": [
            {"poke_node": int(poke), "read_time": int(t)}
            for poke, t in PANEL_PAIRS
        ],
        "period": PERIOD,
        "sentinel_threshold": SENTINEL_THRESHOLD,
        "policies": out,
    }


def check(result: dict) -> None:
    p = result["policies"]
    fresh = p["refresh_every"]
    frozen = p["frozen"]
    periodic = p["periodic_4"]
    sentinel = p["sentinel"]

    # The reference eight-delta panel remains useful on the drifting worlds.
    assert fresh["joint_accuracy"] >= 0.68

    # Permanent memory must genuinely become stale; otherwise the drift audit is
    # too easy and there is nothing for refresh policy to solve.
    assert frozen["joint_accuracy"] <= fresh["joint_accuracy"] - 0.15
    assert frozen["accuracy_by_incident"][10] <= 0.35

    # Reusing a baseline for four incidents preserves nearly all reference
    # accuracy while spending substantially fewer cumulative scalar calls.
    assert periodic["joint_accuracy"] >= fresh["joint_accuracy"] - 0.03
    assert periodic["total_scalar_calls"] <= 0.65 * fresh["total_scalar_calls"]

    # The one-sentinel active-looking scheme is not special here.  At nearly the
    # same cost, a boring periodic schedule is materially more accurate.
    assert abs(
        periodic["calls_per_incident"] - sentinel["calls_per_incident"]
    ) <= 0.25
    assert periodic["joint_accuracy"] >= sentinel["joint_accuracy"] + 0.10


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print(
            "GATE3F PASS (memory amortizes; frozen goes stale; periodic beats sentinel)"
        )


if __name__ == "__main__":
    main()
