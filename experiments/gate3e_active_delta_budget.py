"""Gate 3E: restore a hard post-change evidence budget after Gate 3D.

Gate 3D showed that current-world before/after differencing almost completely
removes substrate variation when the observer is allowed the FULL 168-scalar
panel.  This gate asks whether active acquisition is actually needed once that
simple invariant representation is available.

Training and test substrates are disjoint.  The observer is allowed to remember
the current world's baseline consequence for every candidate experiment.  A
paid post-change measurement therefore returns one scalar delta:

    delta = consequence_now(poke, time) - remembered_baseline(poke, time)

The learned likelihood model is shared across node IDs.  It is indexed only by
cause family, directed ring offset from candidate changed node to poke node,
and read time.  This grants the stable local ring relation shared by the world
family; the gate is about evidence budget, not another coordinate-invariance
claim.

Attackers:
- random post-change delta probes;
- active Fisher-like separation over all cause x address hypotheses;
- active address-focused separation;
- a greedy STATIC panel learned on training worlds;
- the full 168-probe panel ceiling.

Important boundary: a static panel winning does not prove active sensing is
useless in general.  It says adaptivity has not earned architectural work in
this synthetic workload once current-world delta memory is available.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np

from experiments.gate3d_unseen_substrates import (
    CAUSES,
    N,
    TIMES,
    event_features,
    make_training_events,
)


VAR_FLOOR = 1e-6
BUDGETS = (0, 1, 2, 3, 4, 6, 8)


@dataclass
class Event:
    cause: str
    address: int
    delta: np.ndarray  # shape [N, len(TIMES)]


def hypotheses() -> list[tuple[str, int]]:
    return [(cause, address) for cause in CAUSES for address in range(N)]


def experiments() -> list[tuple[int, int]]:
    """(poke node, time-index)."""
    return [(poke, ti) for poke in range(N) for ti in range(len(TIMES))]


def training_events() -> list[Event]:
    out: list[Event] = []
    for row in make_training_events():
        _world_seed, cause, address, _baseline, _post, delta, _normalized = row
        out.append(Event(cause, int(address), np.asarray(delta)))
    return out


def held_out_events(address_seed: int = 999) -> list[Event]:
    """Thirty unseen substrates, 360 events total."""
    rng = np.random.default_rng(address_seed)
    out: list[Event] = []
    for wi in range(30, 60):
        world_seed = 1000 + wi
        for ci, cause in enumerate(CAUSES):
            for rep in range(4):
                address = int(rng.integers(N))
                seed = 80_000 + wi * 100 + rep + 1000 * ci
                _baseline, _post, delta, _normalized = event_features(
                    world_seed, cause, address, seed
                )
                out.append(Event(cause, address, np.asarray(delta)))
    return out


def fit_relative_delta_model(
    events: list[Event],
) -> tuple[np.ndarray, np.ndarray, list[tuple[str, int]], list[tuple[int, int]]]:
    """Return mean/variance arrays shaped [experiment, hypothesis].

    The transferable relation is directed offset, not literal node ID:

        offset = (poke - candidate_address) mod N

    Each scalar likelihood is learned across all training worlds and addresses.
    """
    hyps = hypotheses()
    exps = experiments()

    buckets: dict[tuple[str, int, int], list[float]] = {
        (cause, offset, ti): []
        for cause in CAUSES
        for offset in range(N)
        for ti in range(len(TIMES))
    }

    for event in events:
        for poke in range(N):
            offset = (poke - event.address) % N
            for ti in range(len(TIMES)):
                buckets[(event.cause, offset, ti)].append(float(event.delta[poke, ti]))

    means: dict[tuple[str, int, int], float] = {}
    variances: dict[tuple[str, int, int], float] = {}
    for key, values in buckets.items():
        x = np.asarray(values)
        means[key] = float(np.mean(x))
        variances[key] = float(np.var(x) + VAR_FLOOR)

    mu = np.empty((len(exps), len(hyps)))
    var = np.empty_like(mu)
    for j, (poke, ti) in enumerate(exps):
        for hi, (cause, address) in enumerate(hyps):
            key = (cause, (poke - address) % N, ti)
            mu[j, hi] = means[key]
            var[j, hi] = variances[key]
    return mu, var, hyps, exps


def observation_matrix(events: list[Event], exps: list[tuple[int, int]]) -> np.ndarray:
    return np.asarray(
        [[event.delta[poke, ti] for poke, ti in exps] for event in events]
    )


def loglike_vector(x: float, mu: np.ndarray, var: np.ndarray) -> np.ndarray:
    return -0.5 * (np.log(var) + (x - mu) ** 2 / var)


def posterior(logp: np.ndarray) -> np.ndarray:
    p = np.exp(logp - np.max(logp))
    return p / np.sum(p)


def choose_active_joint(
    logp: np.ndarray,
    used: set[int],
    mu: np.ndarray,
    var: np.ndarray,
) -> int:
    """Posterior-weighted between-hypothesis separation / within variance."""
    p = posterior(logp)
    mixture_mean = mu @ p
    between = ((mu - mixture_mean[:, None]) ** 2) @ p
    within = var @ p
    score = between / (within + 1e-12)
    if used:
        score[list(used)] = -np.inf
    return int(np.argmax(score))


def choose_active_address(
    logp: np.ndarray,
    used: set[int],
    mu: np.ndarray,
    var: np.ndarray,
    hyps: list[tuple[str, int]],
) -> int:
    """A second active attacker that explicitly targets address uncertainty."""
    p = posterior(logp)
    p_addr = np.zeros(N)
    mean_addr = np.zeros((len(mu), N))
    var_addr = np.zeros((len(mu), N))

    for address in range(N):
        idx = [hi for hi, (_cause, a) in enumerate(hyps) if a == address]
        weight = p[idx]
        mass = float(np.sum(weight))
        p_addr[address] = mass
        if mass <= 0.0:
            continue
        conditional = weight / mass
        local_mu = mu[:, idx]
        local_var = var[:, idx]
        m = local_mu @ conditional
        mean_addr[:, address] = m
        var_addr[:, address] = (local_var + (local_mu - m[:, None]) ** 2) @ conditional

    overall = mean_addr @ p_addr
    between = ((mean_addr - overall[:, None]) ** 2) @ p_addr
    within = var_addr @ p_addr
    score = between / (within + 1e-12)
    if used:
        score[list(used)] = -np.inf
    return int(np.argmax(score))


def classify_sequence(
    event: Event,
    sequence: list[int],
    mu: np.ndarray,
    var: np.ndarray,
    hyps: list[tuple[str, int]],
    exps: list[tuple[int, int]],
) -> tuple[str, int]:
    logp = np.zeros(len(hyps))
    for j in sequence:
        poke, ti = exps[j]
        x = float(event.delta[poke, ti])
        logp += loglike_vector(x, mu[j], var[j])
    return hyps[int(np.argmax(logp))]


def active_sequence(
    event: Event,
    budget: int,
    mode: str,
    mu: np.ndarray,
    var: np.ndarray,
    hyps: list[tuple[str, int]],
    exps: list[tuple[int, int]],
) -> list[int]:
    logp = np.zeros(len(hyps))
    used: set[int] = set()
    sequence: list[int] = []

    for _ in range(budget):
        if mode == "joint":
            j = choose_active_joint(logp, used, mu, var)
        elif mode == "address":
            j = choose_active_address(logp, used, mu, var, hyps)
        else:
            raise ValueError(mode)
        used.add(j)
        sequence.append(j)
        poke, ti = exps[j]
        x = float(event.delta[poke, ti])
        logp += loglike_vector(x, mu[j], var[j])
    return sequence


def greedy_static_panel(
    train: list[Event],
    mu: np.ndarray,
    var: np.ndarray,
    hyps: list[tuple[str, int]],
    exps: list[tuple[int, int]],
    max_budget: int,
) -> tuple[list[int], list[float]]:
    """Strong boring attacker: choose a single fixed panel on training worlds.

    Each added probe is the candidate that maximizes TRAINING joint
    cause+address accuracy when appended to the already selected panel.
    Test worlds remain entirely unseen.
    """
    observations = observation_matrix(train, exps)
    truth_index = np.asarray(
        [hyps.index((event.cause, event.address)) for event in train], dtype=int
    )

    # [experiment, training_event, hypothesis]
    ll = np.empty((len(exps), len(train), len(hyps)), dtype=np.float32)
    for j in range(len(exps)):
        x = observations[:, j][:, None]
        ll[j] = (
            -0.5
            * (
                np.log(var[j])[None, :]
                + (x - mu[j][None, :]) ** 2 / var[j][None, :]
            )
        ).astype(np.float32)

    current = np.zeros((len(train), len(hyps)), dtype=np.float32)
    available = set(range(len(exps)))
    panel: list[int] = []
    training_curve: list[float] = []

    for _ in range(max_budget):
        best_j = -1
        best_accuracy = -1.0
        for j in available:
            prediction = np.argmax(current + ll[j], axis=1)
            accuracy = float(np.mean(prediction == truth_index))
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_j = j
        panel.append(best_j)
        available.remove(best_j)
        current += ll[best_j]
        training_curve.append(best_accuracy)

    return panel, training_curve


def score_prediction(pred: tuple[str, int], event: Event) -> tuple[int, int, int]:
    cause, address = pred
    return (
        int(cause == event.cause),
        int(address == event.address),
        int(cause == event.cause and address == event.address),
    )


def evaluate(
    train: list[Event],
    test: list[Event],
    seed: int,
) -> dict:
    mu, var, hyps, exps = fit_relative_delta_model(train)
    max_budget = max(BUDGETS)
    fixed_panel, fixed_training_curve = greedy_static_panel(
        train, mu, var, hyps, exps, max_budget
    )

    curves: dict[str, dict[str, dict[str, float]]] = {
        "active_joint": {},
        "active_address": {},
        "greedy_static": {},
        "random": {},
    }

    for budget in BUDGETS:
        accum = {
            name: np.zeros(3, dtype=float)
            for name in curves
        }
        random_rng = np.random.default_rng(12_000 + seed + budget)

        for event in test:
            if budget == 0:
                sequences = {name: [] for name in curves}
            else:
                sequences = {
                    "active_joint": active_sequence(
                        event, budget, "joint", mu, var, hyps, exps
                    ),
                    "active_address": active_sequence(
                        event, budget, "address", mu, var, hyps, exps
                    ),
                    "greedy_static": fixed_panel[:budget],
                    "random": list(
                        random_rng.choice(len(exps), size=budget, replace=False)
                    ),
                }

            for name, sequence in sequences.items():
                pred = classify_sequence(event, sequence, mu, var, hyps, exps)
                accum[name] += np.asarray(score_prediction(pred, event))

        for name in curves:
            cause, address, joint = accum[name] / len(test)
            curves[name][str(budget)] = {
                "cause_accuracy": float(cause),
                "address_accuracy": float(address),
                "joint_accuracy": float(joint),
            }

    full = np.zeros(3, dtype=float)
    full_sequence = list(range(len(exps)))
    for event in test:
        pred = classify_sequence(event, full_sequence, mu, var, hyps, exps)
        full += np.asarray(score_prediction(pred, event))
    full /= len(test)

    return {
        "seed": seed,
        "classification": (
            "CURRENT_WORLD_DELTA_TRANSFERS_BUT_A_GREEDY_STATIC_COVERAGE_PANEL_"
            "BEATS_TWO_ACTIVE_HEURISTICS_AT_HIGH_SMALL_BUDGET;_"
            "ACTIVE_DIAGNOSIS_NOT_YET_NECESSARY"
        ),
        "training_worlds": 30,
        "held_out_worlds": 30,
        "training_events": len(train),
        "held_out_events": len(test),
        "hypotheses": len(hyps),
        "candidate_scalar_measurements": len(exps),
        "budgets": list(BUDGETS),
        "greedy_static_panel": [
            {"poke_node": int(exps[j][0]), "read_time": int(TIMES[exps[j][1]])}
            for j in fixed_panel
        ],
        "greedy_static_training_joint_accuracy": fixed_training_curve,
        "curves": curves,
        "full_panel": {
            "cause_accuracy": float(full[0]),
            "address_accuracy": float(full[1]),
            "joint_accuracy": float(full[2]),
        },
    }


def run(seed: int = 17) -> dict:
    train = training_events()
    test = held_out_events(address_seed=999)
    return evaluate(train, test, seed)


def check(result: dict) -> None:
    curves = result["curves"]
    active = curves["active_joint"]
    address_active = curves["active_address"]
    fixed = curves["greedy_static"]
    random = curves["random"]

    assert result["full_panel"]["joint_accuracy"] >= 0.99

    # A handful of deltas is informative, but this is not a miracle search.
    assert fixed["4"]["joint_accuracy"] >= 0.30
    assert fixed["8"]["joint_accuracy"] >= 0.65

    # Strong static coverage is at least as good as both plausible active
    # acquisition heuristics by eight probes on the locked unseen-world audit.
    assert fixed["8"]["joint_accuracy"] >= active["8"]["joint_accuracy"] + 0.05
    assert fixed["8"]["joint_accuracy"] >= address_active["8"]["joint_accuracy"] + 0.10

    # The learned panel must also beat random coverage substantially.
    assert fixed["8"]["joint_accuracy"] >= random["8"]["joint_accuracy"] + 0.10


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE3E PASS (negative boundary: static delta coverage beats active acquisition here)")


if __name__ == "__main__":
    main()
