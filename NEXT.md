# NEXT — make the hierarchy internal rather than supplied

Gates 0–3C have reached a sharper boundary.

Known factorization transfers efficiently after structural change (G0–G2). Hidden cause families are behaviorally distinguishable from scalar intervention consequences (G3A). Fixed addresses let a static diagnostic panel destroy the need for adaptivity (G3B). Moving the event across all 24 nodes restores a modest but real value for sequential paid outcomes in **exact localization**, while coarse cause-family classification remains mostly cheap/fixed (G3C).

So the next question is no longer “does address matter?” It is:

> **Does the address survive when the substrate itself changes?**

## Gate 3D — unseen substrates

Randomize the underlying local geometry and long-range directed topology across worlds.

Training sees many worlds. Test uses held-out worlds generated from the same family but with different literal node neighborhoods and different long-range edges.

The crucial rule:

```text
literal node IDs are not a transferable semantic label.
```

The machine may know the baseline behavior of the CURRENT world before a fault/change, but it may not use a global atlas learned on another world to say “node 7 always means this.”

### Two representations to compare

**Coordinate atlas**

Learn cause/address signatures tied directly to node IDs, as in G3C. This should fail when node identities no longer imply the same causal neighborhood.

**Relative causal address**

Describe a candidate location by local behavioral relations measured in the current baseline world, for example:

```text
local return profile after a tiny poke
outgoing consequence latency
neighbor-vs-nonneighbor response ratio
short-horizon controllability fingerprint
coarse residual neighborhood
```

Then characterize the *change* relative to that local baseline fingerprint.

This is the point where the AlternativeNeuron notion of an address as an intervention-conditioned equivalence class can become concrete.

### Attackers

- literal coordinate/codebook classifier;
- generic black-box classifier given the same training worlds;
- full-state system identifier with matched post-change calibration budget;
- random probes;
- coarse-residual-only diagnosis;
- oracle that is given the current world operators;
- relative-causal-address observer.

### Metrics

- cause-family accuracy on unseen substrates;
- exact changed-node localization;
- joint cause+location accuracy;
- paid probes needed;
- degradation from seen to unseen substrates;
- performance after a random relabeling of node coordinates.

The **random relabeling control is mandatory**. If a method claims to use relative causal addresses but collapses when every node label is permuted consistently inside a world, it was still using coordinates.

### Kill conditions

If the relative-address method does not transfer better than a literal codebook or generic classifier at matched evidence budget, then “causal address” is still our explanatory language rather than a useful machine representation.

If merely supplying the current baseline operator makes the task trivial, report that and separate **model access** from **active discovery** rather than hiding it.

## Gate 4 — selectively maintained dynamical islands

Only after substrate-relative addressing should the repository return to `SpectralIslandsV2`.

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
which constraint changed, and where relative to this substrate?
    ↓
update medium model
    ↓
repeat enough times
    ↓
slowly alter routing / structure
```

At that point the repo would no longer merely model a hierarchy of constraints. The machine would use that hierarchy to decide **what to measure, what changed, where it changed, and what deserves structural adaptation**.

**Coordinates are cheap. Relative causal identity is the next test.**
