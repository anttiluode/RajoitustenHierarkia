"""Gate 3H: combine changing demand with nonstationary substrate drift.

Gate 3F showed that cached healthy consequences go stale under slow drift and a
boring periodic refresh beats one sentinel. Gate 3G showed that when demand
moves across a larger useful set, LRU is already near a future-use oracle and
lifetime frequency over-consolidates the old regime.

Those gates separated two failure modes. Here they occur together:

- demand changes which expected consequences are worth retaining;
- the healthy substrate follows stable -> rapid-drift -> stable epochs, so a
  recently useful expectation can still become numerically wrong.

All policies use the same 12-slot LRU capacity and the same rotated eight-scalar
post-change panels. They differ only in how cached healthy baselines are
refreshed. Every healthy check/refresh counts as a scalar measurement.

The deliberately simple attackers are fixed refresh periods (2/4/8 incidents)
and a per-entry TTL. The candidate adaptive rule buys two distributed healthy
checks from currently-needed cached entries, computes their residual against
memory, and refreshes the rest of the current panel only when the residual RMS
crosses a locked threshold.

The result is allowed to be negative. If a fixed period or TTL matches the
residual trigger at lower cost, surprise-driven memory maintenance has not yet
earned architectural work.
"""

from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from dataclasses import dataclass

import numpy as np

from experiments.gate3d_unseen_substrates import (
    CAUSES,
    MEASUREMENT_NOISE,
    N,
    make_world,
)
from experiments.gate3e_active_delta_budget import (
    fit_relative_delta_model,
    training_events,
)
from experiments.gate3f_baseline_memory import perturb_current_world
from experiments.gate3g_expectation_cache import (
    CACHE_CAPACITY,
    CONTEXT_SEQUENCE,
    context_indices,
    predict_from_panel,
    response_table,
)


HELD_OUT_WORLDS = 30
STABLE_RATE = 0.00015
BURST_RATE = 0.0035
BURST_START = 8
BURST_END = 16
DRIFT_RATES = (
    (STABLE_RATE,) * BURST_START
    + (BURST_RATE,) * (BURST_END - BURST_START)
    + (STABLE_RATE,) * (len(CONTEXT_SEQUENCE) - BURST_END)
)
RESIDUAL_CHECKS = 2
RESIDUAL_THRESHOLD = 0.008
TTL = 4
STALE_ERROR_THRESHOLD = 0.012
POLICIES = (
    "fresh",
    "lru_plain",
    "period_2",
    "period_4",
    "period_8",
    "ttl_4",
    "residual_2",
    "phase_oracle",
)
EPOCHS = ("stable_pre", "burst", "stable_post")


@dataclass
class CacheEntry:
    value: float
    stored_step: int


def epoch_name(step: int) -> str:
    if step < BURST_START:
        return "stable_pre"
    if step < BURST_END:
        return "burst"
    return "stable_post"


def cumulative_drift(step: int) -> float:
    return float(sum(DRIFT_RATES[:step]))


def drift_basis(world_seed: int) -> np.ndarray:
    rng = np.random.default_rng(world_seed + 515_151)
    dg = np.zeros((N, N))
    for i in range(N):
        left = float(rng.normal())
        right = float(rng.normal())
        dg[i, i] = -0.5 * (left + right)
        dg[i, (i - 1) % N] = left
        dg[i, (i + 1) % N] = right
    return dg


def variable_drift_world(
    g0: np.ndarray,
    c0: np.ndarray,
    step: int,
    world_seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Healthy world with a locked stable -> burst -> stable drift schedule."""
    amount = cumulative_drift(step)
    dg = drift_basis(world_seed)

    g = (1.0 + amount) * g0 + 0.5 * amount * dg
    c = (1.0 - 0.6 * amount) * c0

    norm = float(np.linalg.norm(g, 2))
    if norm > 1.02:
        g *= 1.02 / norm
    return g, c, np.ones(N)


def baseline_observation(
    healthy_exact: np.ndarray,
    exps: list[tuple[int, int]],
    j: int,
    world_index: int,
    step: int,
) -> float:
    poke, ti = exps[j]
    seed = 410_000 + world_index * 100_000 + step * 1000 + j
    return float(
        healthy_exact[poke, ti]
        + np.random.default_rng(seed).normal(0.0, MEASUREMENT_NOISE)
    )


def post_observation(
    post_exact: np.ndarray,
    exps: list[tuple[int, int]],
    j: int,
    world_index: int,
    step: int,
) -> float:
    poke, ti = exps[j]
    seed = 510_000 + world_index * 100_000 + step * 1000 + j
    return float(
        post_exact[poke, ti]
        + np.random.default_rng(seed).normal(0.0, MEASUREMENT_NOISE)
    )


def touch(cache: OrderedDict[int, CacheEntry], key: int) -> None:
    cache.move_to_end(key)


def insert(
    cache: OrderedDict[int, CacheEntry],
    key: int,
    value: float,
    step: int,
) -> None:
    if key in cache:
        cache[key] = CacheEntry(value, step)
        touch(cache, key)
        return
    if len(cache) >= CACHE_CAPACITY:
        cache.popitem(last=False)
    cache[key] = CacheEntry(value, step)


def classify(
    panel: list[int],
    baselines: list[float],
    post_values: dict[int, float],
    mu: np.ndarray,
    var: np.ndarray,
    hyps: list[tuple[str, int]],
) -> tuple[str, int]:
    deltas = [post_values[j] - b for j, b in zip(panel, baselines)]
    return predict_from_panel(panel, deltas, mu, var, hyps)


def should_periodically_refresh(policy: str, step: int) -> bool:
    if policy == "period_2":
        return step > 0 and step % 2 == 0
    if policy == "period_4":
        return step > 0 and step % 4 == 0
    if policy == "period_8":
        return step > 0 and step % 8 == 0
    return False


def run(seed: int = 17) -> dict:
    mu, var, hyps, exps = fit_relative_delta_model(training_events())
    panels = context_indices(exps)

    stats = {
        name: {
            "correct": 0,
            "baseline_calls": 0,
            "post_calls": 0,
            "refresh_triggers": 0,
            "stale_uses": 0,
            "correct_by_epoch": {epoch: 0 for epoch in EPOCHS},
            "incidents_by_epoch": {epoch: 0 for epoch in EPOCHS},
            "baseline_by_epoch": {epoch: 0 for epoch in EPOCHS},
        }
        for name in POLICIES
    }

    for wi in range(30, 30 + HELD_OUT_WORLDS):
        world_seed = 1000 + wi
        g0, c0 = make_world(world_seed)
        caches: dict[str, OrderedDict[int, CacheEntry]] = {
            name: OrderedDict()
            for name in POLICIES
            if name != "fresh"
        }

        for step, context in enumerate(CONTEXT_SEQUENCE):
            epoch = epoch_name(step)
            panel = panels[context]
            g, c, gain = variable_drift_world(g0, c0, step, world_seed)
            healthy_exact = response_table(g, c, gain)

            cause = CAUSES[(wi + step) % len(CAUSES)]
            address = int((wi * 7 + step * 5) % N)
            event_seed = 620_000 + wi * 100 + step
            g2, c2, gain2 = perturb_current_world(
                g, c, gain, cause, address, event_seed
            )
            post_exact = response_table(g2, c2, gain2)
            post_values = {
                j: post_observation(post_exact, exps, j, wi, step)
                for j in panel
            }

            for name in POLICIES:
                stats[name]["post_calls"] += len(panel)
                stats[name]["incidents_by_epoch"][epoch] += 1

            # Expensive reference: buy the current healthy panel every time.
            fresh_baselines = [
                baseline_observation(healthy_exact, exps, j, wi, step)
                for j in panel
            ]
            stats["fresh"]["baseline_calls"] += len(panel)
            stats["fresh"]["baseline_by_epoch"][epoch] += len(panel)
            pred = classify(panel, fresh_baselines, post_values, mu, var, hyps)
            ok = pred == (cause, address)
            stats["fresh"]["correct"] += int(ok)
            stats["fresh"]["correct_by_epoch"][epoch] += int(ok)

            for name in POLICIES:
                if name == "fresh":
                    continue
                cache = caches[name]
                measured_this_step: dict[int, float] = {}
                old_values: dict[int, float] = {}

                # Residual policy checks the two oldest currently-needed hits.
                checked: list[int] = []
                trigger = False
                if name == "residual_2":
                    hits = [j for j in panel if j in cache]
                    hits.sort(key=lambda j: cache[j].stored_step)
                    checked = hits[:RESIDUAL_CHECKS]
                    residuals = []
                    for j in checked:
                        old_values[j] = cache[j].value
                        value = baseline_observation(healthy_exact, exps, j, wi, step)
                        measured_this_step[j] = value
                        residuals.append(value - cache[j].value)
                        stats[name]["baseline_calls"] += 1
                        stats[name]["baseline_by_epoch"][epoch] += 1
                    if len(residuals) == RESIDUAL_CHECKS:
                        rms = float(np.sqrt(np.mean(np.square(residuals))))
                        trigger = rms > RESIDUAL_THRESHOLD
                        stats[name]["refresh_triggers"] += int(trigger)

                baselines: list[float] = []
                for j in panel:
                    if j in measured_this_step:
                        value = measured_this_step[j]
                        insert(cache, j, value, step)
                        baselines.append(value)
                        continue

                    hit = j in cache
                    refresh = False
                    if hit:
                        if should_periodically_refresh(name, step):
                            refresh = True
                        elif name == "ttl_4" and step - cache[j].stored_step >= TTL:
                            refresh = True
                        elif name == "residual_2" and trigger:
                            refresh = True
                        elif name == "phase_oracle":
                            # Free knowledge of the hidden drift phase is an
                            # intentionally unfair ceiling, not a deployable policy.
                            refresh = BURST_START <= step <= BURST_END

                    if (not hit) or refresh:
                        value = baseline_observation(healthy_exact, exps, j, wi, step)
                        stats[name]["baseline_calls"] += 1
                        stats[name]["baseline_by_epoch"][epoch] += 1
                        insert(cache, j, value, step)
                    else:
                        value = cache[j].value
                        poke, ti = exps[j]
                        if abs(float(healthy_exact[poke, ti]) - value) > STALE_ERROR_THRESHOLD:
                            stats[name]["stale_uses"] += 1
                        touch(cache, j)
                    baselines.append(value)

                pred = classify(panel, baselines, post_values, mu, var, hyps)
                ok = pred == (cause, address)
                stats[name]["correct"] += int(ok)
                stats[name]["correct_by_epoch"][epoch] += int(ok)

    total_incidents = HELD_OUT_WORLDS * len(CONTEXT_SEQUENCE)
    policies = {}
    for name in POLICIES:
        s = stats[name]
        total_calls = s["baseline_calls"] + s["post_calls"]
        correct = int(s["correct"])
        policies[name] = {
            "joint_accuracy": correct / total_incidents,
            "correct": correct,
            "baseline_calls": int(s["baseline_calls"]),
            "post_calls": int(s["post_calls"]),
            "total_scalar_calls": int(total_calls),
            "calls_per_incident": total_calls / total_incidents,
            "calls_per_correct_diagnosis": total_calls / max(1, correct),
            "refresh_triggers": int(s["refresh_triggers"]),
            "stale_uses": int(s["stale_uses"]),
            "accuracy_by_epoch": {
                epoch: s["correct_by_epoch"][epoch]
                / max(1, s["incidents_by_epoch"][epoch])
                for epoch in EPOCHS
            },
            "baseline_calls_by_epoch": {
                epoch: int(s["baseline_by_epoch"][epoch]) for epoch in EPOCHS
            },
        }

    fixed_names = ("period_2", "period_4", "period_8", "ttl_4")
    best_fixed = min(
        fixed_names,
        key=lambda name: policies[name]["calls_per_correct_diagnosis"],
    )
    residual = policies["residual_2"]
    fixed = policies[best_fixed]

    if (
        residual["joint_accuracy"] >= fixed["joint_accuracy"] - 0.03
        and residual["calls_per_correct_diagnosis"]
        <= 0.95 * fixed["calls_per_correct_diagnosis"]
    ):
        classification = (
            "DISTRIBUTED_RESIDUAL_REFRESH_BEATS_THE_BEST_FIXED_CLOCK_AT_SIMILAR_"
            "DIAGNOSIS_QUALITY_UNDER_NONSTATIONARY_DRIFT"
        )
    else:
        classification = (
            "BORING_FIXED_OR_TTL_REFRESH_REMAINS_COMPETITIVE;_SURPRISE_DRIVEN_"
            "MEMORY_MAINTENANCE_NOT_YET_NECESSARY"
        )

    return {
        "seed": seed,
        "classification": classification,
        "held_out_worlds": HELD_OUT_WORLDS,
        "incidents_per_world": len(CONTEXT_SEQUENCE),
        "total_incidents": total_incidents,
        "cache_capacity": CACHE_CAPACITY,
        "context_sequence": list(CONTEXT_SEQUENCE),
        "drift_rates": list(DRIFT_RATES),
        "burst_start": BURST_START,
        "burst_end": BURST_END,
        "residual_checks": RESIDUAL_CHECKS,
        "residual_threshold": RESIDUAL_THRESHOLD,
        "ttl": TTL,
        "best_fixed_by_calls_per_correct": best_fixed,
        "policies": policies,
    }


def check(result: dict) -> None:
    p = result["policies"]
    fresh = p["fresh"]

    assert result["cache_capacity"] < 32
    assert fresh["joint_accuracy"] >= 0.68

    # The variable-drift workload must create a real stale-memory problem.
    assert p["lru_plain"]["stale_uses"] > 0
    assert p["lru_plain"]["accuracy_by_epoch"]["burst"] < fresh["accuracy_by_epoch"]["burst"]

    # At least one bounded-memory policy must save a substantial amount of
    # evidence relative to repurchasing every healthy baseline.
    best_calls = min(
        p[name]["total_scalar_calls"]
        for name in p
        if name != "fresh"
    )
    assert best_calls <= 0.80 * fresh["total_scalar_calls"]

    # The adaptive rule must actually observe and sometimes react; whether it
    # beats the fixed attackers is left to the recorded classification.
    assert p["residual_2"]["baseline_calls"] > 0
    assert p["residual_2"]["refresh_triggers"] > 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE3H PASS (classification determined by locked attacker comparison)")


if __name__ == "__main__":
    main()
