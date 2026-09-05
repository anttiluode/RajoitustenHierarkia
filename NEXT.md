# NEXT — make the hierarchy internal rather than supplied

Gates 0–2 have reached a useful boundary.

A factorized description transfers efficiently after structural intervention **when the changed operators are supplied**. A generic lagged state-space model can represent the same linear dynamics, but needs substantially more post-change data to relearn them.

The next question is therefore no longer whether factorization helps. It is whether a bounded system can **discover the factorization from consequences**.

## Gate 3 — blind constraint-layer attribution

Hide the semantic labels `G`, `C`, `delay`, and `gain` from the observer.

Construct worlds where exactly one layer changes:

```text
A. local geometry changes
B. long-range wiring changes
C. propagation delay changes
D. local gain / adaptation changes
E. external input statistics change
F. nothing structural changes
```

The observer receives:

- ordinary state observations through a bounded readout;
- a cheap residual / prediction-error signal;
- a small budget of reversible addressed pokes;
- a scalar global consequence.

It must choose experiments and infer which latent constraint family changed.

### Attackers

- generic VAR change detector;
- full-state linear system identification;
- random interventions;
- passive observation only;
- oracle with layer labels;
- active factorized observer.

### Metrics

- layer-attribution accuracy;
- number of paid interventions;
- post-change prediction NMSE;
- recovery/calibration samples;
- false structural-change alarms;
- transfer to an unseen combination of two changed layers.

### Kill condition

If a generic change detector or black-box system identifier reaches the same attribution/prediction performance at the same evidence budget, then the hierarchy has not become an architectural advantage.

This gate is where `OutoSynapsi` and `AlternativeNeuron` should re-enter: scalar consequences and active interventions are now used to identify **which operator family changed**, not merely the hidden state inside a known world.

## Gate 4 — selectively maintained dynamical islands

Only after Gate 3 should the repository return to `SpectralIslandsV2`.

Introduce several nonlinear dynamical objects with overlapping spectra. An island earns identity only if it remains recognizable across substrate drift by a multi-coordinate causal fingerprint:

```text
return dynamics
response latency
phase relation
transition probabilities
controllability
held-out poke response
context dependence
```

Frequency-only identity is an explicit attacker.

The interesting question becomes whether the constraint hierarchy creates **dynamical separation**: some perturbations die, some resonate, some switch basins, and some rewrite the slow operator.

## Gate 5 — ordering itself

Test whether constraint ordering has causal content.

Compare histories that end with similar apparent operators but were reached by different sequences:

```text
geometry → wiring adaptation → local gain
```

versus

```text
local gain → wiring adaptation → geometry
```

If only the final effective matrix matters, “hierarchy” is unnecessary language. If order changes reachable attractors, adaptation cost, or intervention response under the same endpoint budget, the ordering has earned explanatory work.

## Gate 6 — bounded thinking system

Finally put the pieces together:

```text
cheap residual
    ↓
active experiment
    ↓
which constraint changed?
    ↓
update medium model
    ↓
repeat enough times
    ↓
slowly alter routing / structure
```

At that point the repo would no longer merely model a hierarchy of constraints. The machine would use that hierarchy to decide **what to measure, what changed, and what deserves structural adaptation**.

**First make the factors discoverable. Then make them useful.**
