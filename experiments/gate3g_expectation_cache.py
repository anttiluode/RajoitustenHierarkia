"""Gate 3G: make baseline memory earn every cache slot.

Gate 3F established a narrow value for medium-timescale memory: periodically
reusing an eight-entry healthy consequence panel preserved almost all fresh
calibration accuracy while saving scalar measurements under slow drift.

This gate removes the free initial panel.  Each world begins with an EMPTY
baseline cache of capacity 12.  Four diagnostic contexts require four rotated
versions of the Gate-3E eight-probe panel: 32 distinct baseline entries total,
so the cache cannot hold them all.

When a required expectation is cached, an incident costs only the post-change
scalar.  On a miss, the system also buys the matching healthy/recovery baseline
scalar and may retain it.

To isolate cache replacement from staleness, the healthy substrate is fixed
within this gate.  Gate 3F already audited drift/refresh.  Gate 3H can recombine
the two if sparse caching survives.

The context distribution switches halfway through each sequence.  This is an
attacker against over-consolidation: entries useful in the first regime become
less useful in the second.

Replacement policies:
- no cache;
- LRU (recency);
- LFU (lifetime frequency, deliberately sticky across the regime switch);
- random eviction;
- Belady/future-use oracle ceiling.

If simple recency or even random eviction is already close to the oracle, a
learned consolidation mechanism has not earned architectural work.
"""

from __future__ import annotations

import argparse
import json
from collections import OrderedDict, defaultdict

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
    fit_relative_delta_model,
    training_events,
)
from experiments.gate3f_baseline_memory import PANEL_PAIRS, perturb_current_world


CACHE_CAPACITY = 12
CONTEXT_SHIFTS = (0, 6, 12, 18)
CONTEXT_SEQUENCE = (
    (0,) * 6
    + (1,) * 3
    + (2,) * 2
    + (3,)
    + (2,) * 6
    + (3,) * 3
    + (0,) * 2
    + (1,)
)
HELD_OUT_WORLDS = 30
POLICIES = ("no_cache", "lru", "lfu", "random", "oracle")


def response_table(g: np.ndarray, c: np.ndarray, gain: np.ndarray) -> np.ndarray:
    return np.stack([response_vector(g, c, gain, poke) for poke in range(N)])


def context_pairs() -> list[list[tuple[int, int]]]:
    """Four disjoint rotated copies of the Gate-3E panel."""
    return [
        [((poke + shift) % N, t) for poke, t in PANEL_PAIRS]
        for shift in CONTEXT_SHIFTS
    ]


def context_indices(exps: list[tuple[int, int]]) -> list[list[int]]:
    time_index = {t: i for i, t in enumerate(TIMES)}
    return [
        [exps.index((poke, time_index[t])) for poke, t in panel]
        for panel in context_pairs()
    ]


def predict_from_panel(
    panel: list[int],
    deltas: list[float],
    mu: np.ndarray,
    var: np.ndarray,
    hyps: list[tuple[str, int]],
) -> tuple[str, int]:
    logp = np.zeros(len(hyps))
    for j, x in zip(panel, deltas):
        logp += -0.5 * (np.log(var[j]) + (x - mu[j]) ** 2 / var[j])
    return hyps[int(np.argmax(logp))]


def next_use(flat_refs: list[int], key: int, position: int) -> int:
    try:
        return flat_refs.index(key, position + 1)
    except ValueError:
        return 10**9


def run(seed: int = 17) -> dict:
    mu, var, hyps, exps = fit_relative_delta_model(training_events())
    panels = context_indices(exps)
    flat_refs = [j for context in CONTEXT_SEQUENCE for j in panels[context]]

    unique_pages = len(set(flat_refs))
    assert unique_pages == 32

    stats = {
        name: {
            "correct": 0,
            "baseline_calls": 0,
            "post_calls": 0,
            "hits": 0,
            "misses": 0,
            "baseline_calls_first_half": 0,
            "baseline_calls_second_half": 0,
        }
        for name in POLICIES
    }

    for wi in range(30, 30 + HELD_OUT_WORLDS):
        world_seed = 1000 + wi
        g, c = make_world(world_seed)
        gain = np.ones(N)
        baseline_exact = response_table(g, c, gain)

        lru: OrderedDict[int, float] = OrderedDict()
        lfu_data: dict[int, float] = {}
        lfu_count: defaultdict[int, int] = defaultdict(int)
        lfu_last: dict[int, int] = {}
        random_data: dict[int, float] = {}
        oracle_data: dict[int, float] = {}
        random_rng = np.random.default_rng(900_000 + wi)

        ref_position = 0
        for step, context in enumerate(CONTEXT_SEQUENCE):
            panel = panels[context]
            cause = CAUSES[(wi + step) % len(CAUSES)]
            address = int((wi * 7 + step * 5) % N)
            event_seed = 200_000 + wi * 100 + step

            g2, c2, gain2 = perturb_current_world(
                g, c, gain, cause, address, event_seed
            )
            post_exact = response_table(g2, c2, gain2)

            # One matched post-change measurement realization is shared by all
            # cache policies; only their baseline acquisition differs.
            post_values: dict[int, float] = {}
            for j in panel:
                poke, ti = exps[j]
                post_values[j] = float(
                    post_exact[poke, ti]
                    + np.random.default_rng(300_000 + event_seed + j).normal(
                        0.0, MEASUREMENT_NOISE
                    )
                )

            for name in POLICIES:
                deltas: list[float] = []
                for local_position, j in enumerate(panel):
                    poke, ti = exps[j]
                    half_key = (
                        "baseline_calls_first_half"
                        if step < len(CONTEXT_SEQUENCE) // 2
                        else "baseline_calls_second_half"
                    )

                    if name == "no_cache":
                        baseline = float(
                            baseline_exact[poke, ti]
                            + np.random.default_rng(
                                400_000 + wi * 10_000 + step * 100 + j
                            ).normal(0.0, MEASUREMENT_NOISE)
                        )
                        stats[name]["baseline_calls"] += 1
                        stats[name][half_key] += 1
                        stats[name]["misses"] += 1

                    elif name == "lru":
                        if j in lru:
                            baseline = lru[j]
                            lru.move_to_end(j)
                            stats[name]["hits"] += 1
                        else:
                            baseline = float(
                                baseline_exact[poke, ti]
                                + np.random.default_rng(
                                    500_000 + wi * 10_000 + step * 100 + j
                                ).normal(0.0, MEASUREMENT_NOISE)
                            )
                            stats[name]["baseline_calls"] += 1
                            stats[name][half_key] += 1
                            stats[name]["misses"] += 1
                            if len(lru) >= CACHE_CAPACITY:
                                lru.popitem(last=False)
                            lru[j] = baseline

                    elif name == "lfu":
                        # Lifetime counts deliberately do NOT decay after the
                        # regime switch.  This makes LFU a consolidation-like
                        # attacker that can overprotect old frequent entries.
                        lfu_count[j] += 1
                        if j in lfu_data:
                            baseline = lfu_data[j]
                            stats[name]["hits"] += 1
                        else:
                            baseline = float(
                                baseline_exact[poke, ti]
                                + np.random.default_rng(
                                    600_000 + wi * 10_000 + step * 100 + j
                                ).normal(0.0, MEASUREMENT_NOISE)
                            )
                            stats[name]["baseline_calls"] += 1
                            stats[name][half_key] += 1
                            stats[name]["misses"] += 1
                            if len(lfu_data) >= CACHE_CAPACITY:
                                victim = min(
                                    lfu_data,
                                    key=lambda key: (
                                        lfu_count[key], lfu_last.get(key, -1)
                                    ),
                                )
                                del lfu_data[victim]
                            lfu_data[j] = baseline
                        lfu_last[j] = ref_position + local_position

                    elif name == "random":
                        if j in random_data:
                            baseline = random_data[j]
                            stats[name]["hits"] += 1
                        else:
                            baseline = float(
                                baseline_exact[poke, ti]
                                + np.random.default_rng(
                                    700_000 + wi * 10_000 + step * 100 + j
                                ).normal(0.0, MEASUREMENT_NOISE)
                            )
                            stats[name]["baseline_calls"] += 1
                            stats[name][half_key] += 1
                            stats[name]["misses"] += 1
                            if len(random_data) >= CACHE_CAPACITY:
                                keys = list(random_data)
                                victim = keys[int(random_rng.integers(len(keys)))]
                                del random_data[victim]
                            random_data[j] = baseline

                    else:  # Belady oracle: evict the page used farthest ahead.
                        if j in oracle_data:
                            baseline = oracle_data[j]
                            stats[name]["hits"] += 1
                        else:
                            baseline = float(
                                baseline_exact[poke, ti]
                                + np.random.default_rng(
                                    800_000 + wi * 10_000 + step * 100 + j
                                ).normal(0.0, MEASUREMENT_NOISE)
                            )
                            stats[name]["baseline_calls"] += 1
                            stats[name][half_key] += 1
                            stats[name]["misses"] += 1
                            if len(oracle_data) >= CACHE_CAPACITY:
                                current = ref_position + local_position
                                victim = max(
                                    oracle_data,
                                    key=lambda key: next_use(
                                        flat_refs, key, current
                                    ),
                                )
                                del oracle_data[victim]
                            oracle_data[j] = baseline

                    deltas.append(post_values[j] - baseline)
                    stats[name]["post_calls"] += 1

                prediction = predict_from_panel(panel, deltas, mu, var, hyps)
                stats[name]["correct"] += int(prediction == (cause, address))

            ref_position += len(panel)

    incidents = HELD_OUT_WORLDS * len(CONTEXT_SEQUENCE)
    out = {}
    for name in POLICIES:
        s = stats[name]
        total_calls = s["baseline_calls"] + s["post_calls"]
        accesses = s["hits"] + s["misses"]
        out[name] = {
            "joint_accuracy": s["correct"] / incidents,
            "correct": int(s["correct"]),
            "baseline_calls": int(s["baseline_calls"]),
            "post_calls": int(s["post_calls"]),
            "total_scalar_calls": int(total_calls),
            "calls_per_incident": total_calls / incidents,
            "calls_per_correct_diagnosis": total_calls / max(1, s["correct"]),
            "cache_hits": int(s["hits"]),
            "cache_misses": int(s["misses"]),
            "cache_hit_rate": 0.0 if accesses == 0 else s["hits"] / accesses,
            "baseline_calls_first_half": int(s["baseline_calls_first_half"]),
            "baseline_calls_second_half": int(s["baseline_calls_second_half"]),
        }

    return {
        "seed": seed,
        "classification": (
            "SPARSE_EXPECTATION_CACHE_SAVES_MEASUREMENTS;_SIMPLE_RECENCY_IS_NEAR_"
            "ORACLE_AND_LIFETIME_FREQUENCY_OVERCONSOLIDATES_OLD_REGIME;_"
            "LEARNED_CONSOLIDATION_NOT_YET_NECESSARY"
        ),
        "held_out_worlds": HELD_OUT_WORLDS,
        "incidents_per_world": len(CONTEXT_SEQUENCE),
        "total_incidents": incidents,
        "cache_capacity": CACHE_CAPACITY,
        "distinct_required_expectations": unique_pages,
        "context_shifts": list(CONTEXT_SHIFTS),
        "context_sequence": list(CONTEXT_SEQUENCE),
        "regime_switch_incident": len(CONTEXT_SEQUENCE) // 2,
        "policies": out,
    }


def check(result: dict) -> None:
    p = result["policies"]
    no_cache = p["no_cache"]
    lru = p["lru"]
    lfu = p["lfu"]
    random = p["random"]
    oracle = p["oracle"]

    assert result["distinct_required_expectations"] > result["cache_capacity"]

    # Caching should not materially damage the actual diagnosis task.
    assert lru["joint_accuracy"] >= no_cache["joint_accuracy"] - 0.04

    # Recency cuts baseline reacquisition by about two thirds and total scalar
    # calls by about one third relative to no memory.
    assert lru["baseline_calls"] <= 0.35 * no_cache["baseline_calls"]
    assert lru["total_scalar_calls"] <= 0.70 * no_cache["total_scalar_calls"]

    # LRU is close enough to the future-use oracle that a learned cache policy
    # has not earned much headroom on this locked workload.
    assert lru["baseline_calls"] <= 1.25 * oracle["baseline_calls"]

    # Lifetime frequency over-consolidates the first regime and becomes worse
    # after the task distribution switches.  LRU does not accumulate that debt.
    assert lfu["baseline_calls_second_half"] >= 1.30 * lfu["baseline_calls_first_half"]
    assert lru["baseline_calls_second_half"] <= 1.10 * lru["baseline_calls_first_half"]

    # Even random eviction is a strong boring attacker here.
    assert random["baseline_calls"] <= 1.20 * lru["baseline_calls"]


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
            "GATE3G PASS (cache helps; LRU near oracle; lifetime frequency overconsolidates)"
        )


if __name__ == "__main__":
    main()
