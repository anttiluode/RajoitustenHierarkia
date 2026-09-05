"""Gate 3C: move the hidden structural address.

Gate 3A showed that scalar intervention consequences can distinguish six hidden
cause families on one fixed substrate. Gate 3B then killed the architectural
claim: because the perturbations always lived at the same addresses, two
learned fixed diagnostic probes solved the problem.

This gate removes that cheat. Local geometry, wiring, gain, and input changes
may occur at ANY of 24 nodes. Delay and no-change remain global controls.

The observer gets two information channels:

1. a FREE six-bin residual map computed from ordinary commanded background
   activity under the remembered baseline model. The map is deliberately
   coarse: four physical nodes share each bin and only the normalized spatial
   distribution of residual magnitude is retained;
2. PAID experiments of the form
       (poke node, read time) -> one scalar global consequence error.

The observer never receives G, C, delay, gain, or the true changed address.
The known background command is available when forming the residual map -- an
explicit efference-copy assumption. Hidden external drive is not known.

A training bank teaches empirical distributions for 98 latent hypotheses:
24 addresses x {geometry, wiring, gain, input}, plus delay and no-change.
Cause priors are balanced so the many address hypotheses do not swamp the two
global classes.

Attackers:
- random paid pokes;
- a globally learned fixed diagnostic panel;
- a stronger coarse-bin-conditioned fixed panel that may choose a different
  pre-learned probe sequence from the FREE residual map, but cannot adapt that
  sequence to paid outcomes;
- the full intervention panel.

The intended result is deliberately narrower than "active wins everything".
Moving the address should make sequential paid outcomes useful for JOINT
cause+address recovery and localization. Cause-family classification may remain
mostly solvable from the cheap residual and a fixed panel.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

import numpy as np


N = 24
BINS = tuple(np.arange(4 * b, 4 * (b + 1)) for b in range(6))
TIMES = (1, 2, 3, 4, 5, 7, 9)
BASE_DELAY = 3
MAX_HORIZON = max(TIMES)
CLASSES = ("none", "geometry", "wiring", "delay", "gain", "input")
LOCAL_CAUSES = ("geometry", "wiring", "gain", "input")
MEASUREMENT_NOISE = 1e-4


@dataclass
class Stats:
    passive_mean: np.ndarray
    passive_var: np.ndarray
    probe_mean: np.ndarray
    probe_var: np.ndarray


def make_operators(seed: int = 7) -> tuple[np.ndarray, np.ndarray]:
    g = np.zeros((N, N))
    for i in range(N):
        g[i, i] = 0.42
        g[i, (i - 1) % N] = 0.29
        g[i, (i + 1) % N] = 0.29

    rng = np.random.default_rng(seed)
    c = np.zeros((N, N))
    for source in range(N):
        target = (source + int(rng.integers(6, N - 5))) % N
        c[target, source] += float(rng.uniform(0.4, 1.0))
    c /= max(1.0, float(np.linalg.norm(c, 2)))
    return g, c


G0, C0 = make_operators()


def changed_world(kind: str, magnitude: float, address: int | None):
    g, c = make_operators()
    delay = BASE_DELAY
    gain = np.ones(N)
    hidden_shift = np.zeros(N)
    hidden_scale = np.ones(N)

    if kind == "geometry":
        assert address is not None
        delta = 0.14 * magnitude
        g[address, address] -= delta
        g[address, (address + 1) % N] += delta
    elif kind == "wiring":
        assert address is not None
        c = c.copy()
        c[(address + 8) % N, address] += 0.22 * magnitude
    elif kind == "delay":
        delay = 5
    elif kind == "gain":
        assert address is not None
        gain[address] = 1.0 + 0.22 * magnitude
    elif kind == "input":
        assert address is not None
        hidden_shift[address] = 0.05 * magnitude
        hidden_scale[address] = 1.0 + 0.35 * abs(magnitude)
    elif kind != "none":
        raise ValueError(kind)

    return g, c, delay, gain, hidden_shift, hidden_scale


def evolve(g, c, delay: int, gain: np.ndarray, inputs: np.ndarray) -> np.ndarray:
    states = np.zeros((len(inputs) + 1, N))
    zero = np.zeros(N)
    for t in range(len(inputs)):
        delayed = states[t - delay] if t - delay >= 0 else zero
        z = (
            0.16 * states[t]
            + 0.56 * (g @ states[t])
            + 0.22 * (c @ delayed)
            + inputs[t]
        )
        states[t + 1] = np.tanh(gain * z)
    return states


def ordinary_activity(params, seed: int, steps: int = 180):
    """Return state plus the observer's known background motor/command drive."""
    g, c, delay, gain, hidden_shift, hidden_scale = params
    rng = np.random.default_rng(seed)
    command = 0.08 * rng.standard_normal((steps, N))
    hidden = 0.008 * rng.standard_normal((steps, N)) * hidden_scale + hidden_shift
    states = evolve(g, c, delay, gain, command + hidden)
    return states, command


def impulse_response(params, poke: int) -> np.ndarray:
    g, c, delay, gain, _hidden_shift, _hidden_scale = params
    states = np.zeros((MAX_HORIZON + 1, N))
    states[0, poke] = 1.0
    zero = np.zeros(N)
    for t in range(MAX_HORIZON):
        delayed = states[t - delay] if t - delay >= 0 else zero
        z = 0.16 * states[t] + 0.56 * (g @ states[t]) + 0.22 * (c @ delayed)
        states[t + 1] = np.tanh(gain * z)
    return states


def raw_coarse_residual(states: np.ndarray, command: np.ndarray) -> np.ndarray:
    """Six coarse bins; each hides four physical addresses.

    The remembered baseline operator and the known command are used to predict
    each next state. Hidden external input and structural changes both appear as
    residual. We retain only mean absolute residual per four-node bin.
    """
    zero = np.zeros(N)
    rows = []
    for t in range(40, len(states) - 1):
        delayed = states[t - BASE_DELAY] if t - BASE_DELAY >= 0 else zero
        pred = np.tanh(
            0.16 * states[t]
            + 0.56 * (G0 @ states[t])
            + 0.22 * (C0 @ delayed)
            + command[t]
        )
        rows.append(states[t + 1] - pred)
    residual = np.asarray(rows)
    return np.asarray([np.mean(np.abs(residual[:, nodes])) for nodes in BINS])


def make_hypotheses():
    hypotheses: list[tuple[str, int | None]] = [("none", None)]
    for cause in LOCAL_CAUSES:
        for address in range(N):
            hypotheses.append((cause, address))
    hypotheses.append(("delay", None))
    return hypotheses


def logsumexp(a: np.ndarray, axis: int | None = None) -> np.ndarray:
    m = np.max(a, axis=axis, keepdims=True)
    out = np.squeeze(m, axis=axis) + np.log(np.sum(np.exp(a - m), axis=axis))
    return out


def build_baseline(seed: int = 17):
    rng = np.random.default_rng(seed)
    readout = rng.standard_normal(N)
    readout /= np.linalg.norm(readout)
    experiments = [(poke, t) for poke in range(N) for t in TIMES]

    base = changed_world("none", 1.0, None)
    response = {poke: impulse_response(base, poke) for poke in range(N)}
    base_probe = np.asarray(
        [float(readout @ response[poke][t]) for poke, t in experiments]
    )

    residual_bank = []
    for k in range(80):
        states, command = ordinary_activity(base, 3000 + k)
        residual_bank.append(raw_coarse_residual(states, command))
    residual_bank = np.asarray(residual_bank)
    base_raw = np.mean(residual_bank, axis=0)
    base_profile = base_raw / np.sum(base_raw)
    return readout, experiments, base_probe, base_profile


def one_sample(
    cause: str,
    address: int | None,
    magnitude: float,
    seed: int,
    readout: np.ndarray,
    experiments: list[tuple[int, int]],
    base_probe: np.ndarray,
    base_profile: np.ndarray,
):
    params = changed_world(cause, magnitude, address)
    states, command = ordinary_activity(params, seed)
    raw = raw_coarse_residual(states, command)
    profile = raw / np.sum(raw)
    # Preserve spatial shape, deliberately discard total residual amplitude.
    passive = 100.0 * (profile - base_profile)

    cache = {poke: impulse_response(params, poke) for poke in range(N)}
    rrng = np.random.default_rng(seed + 999_999)
    probes = []
    for j, (poke, t) in enumerate(experiments):
        observed = float(readout @ cache[poke][t])
        consequence = abs(observed - base_probe[j])
        consequence += float(rrng.normal(0.0, MEASUREMENT_NOISE))
        probes.append(consequence)
    return passive, np.asarray(probes)


def make_datasets(seed: int = 17):
    readout, experiments, base_probe, base_profile = build_baseline(seed)
    hypotheses = make_hypotheses()
    hyp_index = {h: i for i, h in enumerate(hypotheses)}
    cause_index = {c: i for i, c in enumerate(CLASSES)}

    # Equal samples per cause+address hypothesis for estimating local signatures.
    train_p, train_v, train_h = [], [], []
    rng = np.random.default_rng(100)
    sid = 0
    for hi, (cause, address) in enumerate(hypotheses):
        for _ in range(8):
            magnitude = 1.0 if cause in ("none", "delay") else float(rng.uniform(0.7, 1.3))
            p, v = one_sample(
                cause,
                address,
                magnitude,
                10_000 + sid,
                readout,
                experiments,
                base_probe,
                base_profile,
            )
            train_p.append(p)
            train_v.append(v)
            train_h.append(hi)
            sid += 1

    # Held-out set is balanced by CAUSE, with address resampled each episode.
    test_p, test_v, test_h, test_cause, test_address = [], [], [], [], []
    rng = np.random.default_rng(200)
    sid = 0
    for cause in CLASSES:
        for _ in range(60):
            if cause in LOCAL_CAUSES:
                address = int(rng.integers(0, N))
                magnitude = float(rng.uniform(0.7, 1.3))
            else:
                address = None
                magnitude = 1.0
            p, v = one_sample(
                cause,
                address,
                magnitude,
                200_000 + sid,
                readout,
                experiments,
                base_probe,
                base_profile,
            )
            test_p.append(p)
            test_v.append(v)
            test_h.append(hyp_index[(cause, address)])
            test_cause.append(cause_index[cause])
            test_address.append(-1 if address is None else address)
            sid += 1

    return (
        np.asarray(train_p),
        np.asarray(train_v),
        np.asarray(train_h),
        np.asarray(test_p),
        np.asarray(test_v),
        np.asarray(test_h),
        np.asarray(test_cause),
        np.asarray(test_address),
        hypotheses,
        experiments,
    )


def fit_stats(passive: np.ndarray, probes: np.ndarray, labels: np.ndarray, n_hyp: int) -> Stats:
    pm, pv, vm, vv = [], [], [], []
    for hi in range(n_hyp):
        rows = labels == hi
        pm.append(np.mean(passive[rows], axis=0))
        # Coarse profile is intentionally approximate; keep likelihood broad.
        pv.append(np.var(passive[rows], axis=0) + 0.05)
        vm.append(np.mean(probes[rows], axis=0))
        vv.append(np.var(probes[rows], axis=0) + 2e-7)
    return Stats(np.asarray(pm), np.asarray(pv), np.asarray(vm), np.asarray(vv))


def metadata(hypotheses):
    cause_index = {c: i for i, c in enumerate(CLASSES)}
    h_cause = np.asarray([cause_index[cause] for cause, _ in hypotheses])
    h_address = np.asarray([-1 if address is None else address for _, address in hypotheses])
    counts = np.bincount(h_cause, minlength=len(CLASSES))
    # Equal prior per cause, then equal prior over addresses inside a cause.
    logprior = np.asarray(
        [-np.log(len(CLASSES)) - np.log(counts[ci]) for ci in h_cause]
    )
    return h_cause, h_address, logprior


def initial_logp(passive: np.ndarray, stats: Stats, logprior: np.ndarray) -> np.ndarray:
    return logprior - 0.5 * np.sum(
        np.log(stats.passive_var)
        + (passive[None, :] - stats.passive_mean) ** 2 / stats.passive_var,
        axis=1,
    )


def cause_scores(logp: np.ndarray, h_cause: np.ndarray) -> np.ndarray:
    return np.asarray(
        [logsumexp(logp[h_cause == ci]) for ci in range(len(CLASSES))]
    )


def choose_active_probe(logp: np.ndarray, used: np.ndarray, stats: Stats) -> int:
    posterior = np.exp(logp - logsumexp(logp))
    mean = np.sum(posterior[:, None] * stats.probe_mean, axis=0)
    between = np.sum(
        posterior[:, None] * (stats.probe_mean - mean[None, :]) ** 2,
        axis=0,
    )
    within = np.sum(posterior[:, None] * stats.probe_var, axis=0)
    score = between / (within + 1e-12)
    score = score.copy()
    score[used] = -np.inf
    return int(np.argmax(score))


def add_probe(logp: np.ndarray, observation: float, j: int, stats: Stats) -> np.ndarray:
    return logp - 0.5 * (
        np.log(stats.probe_var[:, j])
        + (observation - stats.probe_mean[:, j]) ** 2 / stats.probe_var[:, j]
    )


def decode(logp: np.ndarray, h_cause: np.ndarray, h_address: np.ndarray):
    cause = int(np.argmax(cause_scores(logp, h_cause)))
    if CLASSES[cause] in LOCAL_CAUSES:
        hs = np.flatnonzero(h_cause == cause)
        best_h = int(hs[np.argmax(logp[hs])])
        address = int(h_address[best_h])
    else:
        address = -1
    return cause, address


def classify_one(
    passive: np.ndarray,
    probes: np.ndarray,
    stats: Stats,
    h_cause: np.ndarray,
    h_address: np.ndarray,
    logprior: np.ndarray,
    budget: int,
    policy: str,
    rng: np.random.Generator | None = None,
    fixed: list[int] | None = None,
):
    logp = initial_logp(passive, stats, logprior)
    used = np.zeros(len(probes), dtype=bool)
    order = []
    for k in range(budget):
        if policy == "active":
            j = choose_active_probe(logp, used, stats)
        elif policy == "random":
            assert rng is not None
            j = int(rng.choice(np.flatnonzero(~used)))
        elif policy == "fixed":
            assert fixed is not None
            j = int(fixed[k])
        else:
            raise ValueError(policy)
        used[j] = True
        order.append(j)
        logp = add_probe(logp, float(probes[j]), j, stats)
    cause, address = decode(logp, h_cause, h_address)
    return cause, address, order


def batch_cause_prediction(logps: np.ndarray, h_cause: np.ndarray) -> np.ndarray:
    scores = []
    for ci in range(len(CLASSES)):
        x = logps[:, h_cause == ci]
        m = np.max(x, axis=1, keepdims=True)
        scores.append(m[:, 0] + np.log(np.sum(np.exp(x - m), axis=1)))
    return np.argmax(np.stack(scores, axis=1), axis=1)


def macro_accuracy(pred: np.ndarray, labels: np.ndarray) -> float:
    return float(
        np.mean(
            [np.mean(pred[labels == ci] == ci) for ci in range(len(CLASSES))]
        )
    )


def learned_global_panel(
    train_logp: np.ndarray,
    train_contrib: np.ndarray,
    train_cause: np.ndarray,
    size: int,
    h_cause: np.ndarray,
):
    selected: list[int] = []
    current = train_logp.copy()
    for _ in range(size):
        best_acc, best_j = -1.0, -1
        for j in range(train_contrib.shape[2]):
            if j in selected:
                continue
            pred = batch_cause_prediction(current + train_contrib[:, :, j], h_cause)
            acc = macro_accuracy(pred, train_cause)
            if acc > best_acc:
                best_acc, best_j = acc, j
        selected.append(best_j)
        current += train_contrib[:, :, best_j]
    return selected


def coarse_bin(passive: np.ndarray) -> int:
    return int(np.argmax(np.abs(passive)))


def learned_bin_panels(
    train_passive: np.ndarray,
    train_logp: np.ndarray,
    train_contrib: np.ndarray,
    train_cause: np.ndarray,
    size: int,
    h_cause: np.ndarray,
):
    panels = {}
    bins = np.asarray([coarse_bin(p) for p in train_passive])
    for b in range(len(BINS)):
        idx = np.flatnonzero(bins == b)
        labels = train_cause[idx]
        present = np.unique(labels)
        current = train_logp[idx].copy()
        selected: list[int] = []
        for _ in range(size):
            best_acc, best_j = -1.0, -1
            for j in range(train_contrib.shape[2]):
                if j in selected:
                    continue
                pred = batch_cause_prediction(
                    current + train_contrib[idx, :, j], h_cause
                )
                acc = float(
                    np.mean(
                        [np.mean(pred[labels == ci] == ci) for ci in present]
                    )
                )
                if acc > best_acc:
                    best_acc, best_j = acc, j
            selected.append(best_j)
            current += train_contrib[idx, :, best_j]
        panels[b] = selected
    return panels


def score_policy(
    passive: np.ndarray,
    probes: np.ndarray,
    causes: np.ndarray,
    addresses: np.ndarray,
    stats: Stats,
    h_cause: np.ndarray,
    h_address: np.ndarray,
    logprior: np.ndarray,
    budget: int,
    policy: str,
    fixed: list[int] | None = None,
    panels: dict[int, list[int]] | None = None,
):
    cause_hits = 0
    joint_hits = 0
    localization_hits = 0
    localization_den = 0
    rng = np.random.default_rng(700 + budget)

    for i in range(len(causes)):
        chosen_fixed = fixed
        chosen_policy = policy
        if policy == "bin_fixed":
            assert panels is not None
            chosen_policy = "fixed"
            chosen_fixed = panels[coarse_bin(passive[i])]

        pred_cause, pred_address, _ = classify_one(
            passive[i],
            probes[i],
            stats,
            h_cause,
            h_address,
            logprior,
            budget,
            chosen_policy,
            rng=rng,
            fixed=chosen_fixed,
        )
        correct_cause = pred_cause == causes[i]
        cause_hits += int(correct_cause)

        if CLASSES[int(causes[i])] in LOCAL_CAUSES:
            if correct_cause:
                localization_den += 1
                localization_hits += int(pred_address == addresses[i])
            joint_hits += int(correct_cause and pred_address == addresses[i])
        else:
            joint_hits += int(correct_cause)

    return {
        "cause_accuracy": cause_hits / len(causes),
        "joint_cause_address_accuracy": joint_hits / len(causes),
        "localization_given_correct_cause": localization_hits / max(1, localization_den),
    }


def run(seed: int = 17) -> dict:
    (
        train_p,
        train_v,
        train_h,
        test_p,
        test_v,
        _test_h,
        test_cause,
        test_address,
        hypotheses,
        experiments,
    ) = make_datasets(seed)
    stats = fit_stats(train_p, train_v, train_h, len(hypotheses))
    h_cause, h_address, logprior = metadata(hypotheses)
    train_cause = h_cause[train_h]

    train_logp = np.asarray(
        [initial_logp(p, stats, logprior) for p in train_p]
    )
    train_contrib = -0.5 * (
        np.log(stats.probe_var)[None, :, :]
        + (train_v[:, None, :] - stats.probe_mean[None, :, :]) ** 2
        / stats.probe_var[None, :, :]
    )

    global_panel = learned_global_panel(
        train_logp, train_contrib, train_cause, 4, h_cause
    )
    bin_panels = learned_bin_panels(
        train_p, train_logp, train_contrib, train_cause, 4, h_cause
    )

    curves = {name: {} for name in ("active", "random", "global_fixed", "bin_fixed")}
    for budget in (0, 1, 2, 3, 4):
        curves["active"][str(budget)] = score_policy(
            test_p, test_v, test_cause, test_address, stats,
            h_cause, h_address, logprior, budget, "active"
        )
        curves["random"][str(budget)] = score_policy(
            test_p, test_v, test_cause, test_address, stats,
            h_cause, h_address, logprior, budget, "random"
        )
        if budget > 0:
            curves["global_fixed"][str(budget)] = score_policy(
                test_p, test_v, test_cause, test_address, stats,
                h_cause, h_address, logprior, budget, "fixed", fixed=global_panel
            )
            curves["bin_fixed"][str(budget)] = score_policy(
                test_p, test_v, test_cause, test_address, stats,
                h_cause, h_address, logprior, budget, "bin_fixed", panels=bin_panels
            )

    # Full-panel ceiling, vectorized.
    test_logp = np.asarray([initial_logp(p, stats, logprior) for p in test_p])
    test_contrib = -0.5 * (
        np.log(stats.probe_var)[None, :, :]
        + (test_v[:, None, :] - stats.probe_mean[None, :, :]) ** 2
        / stats.probe_var[None, :, :]
    )
    full_logp = test_logp + np.sum(test_contrib, axis=2)
    full_cause = batch_cause_prediction(full_logp, h_cause)
    full_cause_hits = 0
    full_joint_hits = 0
    full_loc_hits = 0
    full_loc_den = 0
    for i, pred_cause in enumerate(full_cause):
        ok = pred_cause == test_cause[i]
        full_cause_hits += int(ok)
        if CLASSES[int(test_cause[i])] in LOCAL_CAUSES:
            if ok:
                hs = np.flatnonzero(h_cause == pred_cause)
                best_h = int(hs[np.argmax(full_logp[i, hs])])
                pred_address = int(h_address[best_h])
                full_loc_den += 1
                full_loc_hits += int(pred_address == test_address[i])
                full_joint_hits += int(pred_address == test_address[i])
        else:
            full_joint_hits += int(ok)

    decoded_global = [
        {"poke_node": int(experiments[j][0]), "read_time": int(experiments[j][1])}
        for j in global_panel
    ]
    decoded_bins = {
        str(b): [
            {"poke_node": int(experiments[j][0]), "read_time": int(experiments[j][1])}
            for j in panel
        ]
        for b, panel in bin_panels.items()
    }

    classification = (
        "MOVING_ADDRESS_MAKES_ADAPTIVE_OUTCOMES_USEFUL_FOR_LOCALIZATION_"
        "BUT_CAUSE_CLASSIFICATION_REMAINS_MOSTLY_CHEAP_OR_FIXED"
    )

    return {
        "seed": seed,
        "classification": classification,
        "n": N,
        "coarse_bins": len(BINS),
        "physical_nodes_per_bin": 4,
        "hidden_hypotheses": len(hypotheses),
        "candidate_scalar_interventions": len(experiments),
        "train_samples": int(len(train_h)),
        "test_samples": int(len(test_cause)),
        "curves": curves,
        "learned_global_panel": decoded_global,
        "learned_bin_panels": decoded_bins,
        "full_panel": {
            "cause_accuracy": full_cause_hits / len(test_cause),
            "joint_cause_address_accuracy": full_joint_hits / len(test_cause),
            "localization_given_correct_cause": full_loc_hits / max(1, full_loc_den),
        },
    }


def check(result: dict) -> None:
    active = result["curves"]["active"]
    random = result["curves"]["random"]
    fixed = result["curves"]["global_fixed"]
    bin_fixed = result["curves"]["bin_fixed"]

    # Cheap residual is informative, but does not solve exact cause+address.
    assert 0.65 <= active["0"]["cause_accuracy"] <= 0.80
    assert active["0"]["joint_cause_address_accuracy"] <= 0.45

    # Moving address restores a real value for adaptive paid outcomes -- most
    # clearly in joint attribution/localization, not in cause label alone.
    assert active["3"]["joint_cause_address_accuracy"] >= fixed["3"]["joint_cause_address_accuracy"] + 0.07
    assert active["3"]["joint_cause_address_accuracy"] >= bin_fixed["3"]["joint_cause_address_accuracy"] + 0.05
    assert active["3"]["joint_cause_address_accuracy"] >= random["3"]["joint_cause_address_accuracy"] + 0.12
    assert active["3"]["localization_given_correct_cause"] >= bin_fixed["3"]["localization_given_correct_cause"] + 0.06

    # Do NOT claim a large cause-family win: a strong fixed panel remains close.
    assert abs(active["3"]["cause_accuracy"] - fixed["3"]["cause_accuracy"]) <= 0.03

    assert result["full_panel"]["cause_accuracy"] >= 0.98
    assert result["full_panel"]["joint_cause_address_accuracy"] >= 0.85


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check:
        check(result)
        print("GATE3C PASS (partial result: localization earned, cause-label win did not)")


if __name__ == "__main__":
    main()
