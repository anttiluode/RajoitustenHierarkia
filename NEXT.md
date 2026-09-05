# NEXT — make the hierarchy internal rather than supplied

Gates 0–3B have reached the next useful boundary.

Known factorization transfers efficiently after structural change (G0–G2). Hidden constraint families are behaviorally distinguishable from scalar intervention consequences (G3A). But on a fixed substrate with fixed perturbation sites, a learned static diagnostic panel solves the attribution problem even more cheaply than the adaptive observer (G3B).

So the next question is not “can we classify the causes?” It is:

> **Does active addressing become useful when the cause can move?**

## Gate 3C — moving-address layer attribution

Randomize the address of local geometry, wiring, and gain changes on every episode.

Keep global delay/input/no-change causes as controls.

The observer receives:

- a cheap coarse residual map with far fewer bins than physical nodes;
- the remembered baseline consequence model;
- a small budget of addressed scalar pokes;
- no direct access to `G`, `C`, delay, gain, or the true changed address.

The hidden hypothesis should now include both **cause family** and **where the event lives**.

The active policy should use cheap evidence to narrow location, then choose a poke/read-time pair that best separates the remaining cause hypotheses.

### Attackers

- passive coarse residual only;
- random addressed pokes;
- the Gate-3B learned fixed diagnostic panel;
- a stronger greedy fixed panel trained across all possible event locations;
- full 192-poke panel;
- active cause+location observer.

### Headline metrics

- cause-family accuracy at 1/2/3/4 paid pokes;
- localization accuracy for local causes;
- fixed-panel vs active accuracy at equal poke budget;
- false structural-change alarms;
- full-panel ceiling.

### Kill condition

If a small fixed panel remains as good as the active observer once event address is randomized, active addressing has still not earned architectural work.

If active wins only because the cheap residual directly reveals the exact changed node, the gate also fails: the coarse readout must leave genuine address ambiguity.

## Gate 3D — unseen substrates

Only after moving-address attribution works, randomize the underlying geometry/connectivity topology across worlds.

Training should see many substrates; test should use held-out substrates. A useful representation should transfer **relative causal signatures** rather than memorizing literal node IDs.

Attackers include a generic black-box classifier trained on the same worlds and a full-state system identifier with a matched calibration budget.

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
which constraint changed, and where?
    ↓
update medium model
    ↓
repeat enough times
    ↓
slowly alter routing / structure
```

At that point the repo would no longer merely model a hierarchy of constraints. The machine would use that hierarchy to decide **what to measure, what changed, where it changed, and what deserves structural adaptation**.

**First make the factors discoverable. Then make their addresses move.**
