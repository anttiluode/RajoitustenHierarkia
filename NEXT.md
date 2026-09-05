# NEXT — make memory pay rent

Gates 0–3E now leave a simpler architecture than we started with.

Known factorization transfers efficiently after structural change (G0–G2). Fixed event addresses make adaptivity unnecessary (G3A/G3B). Moving the event gives sequential pokes some value for exact localization (G3C). Changing the substrate kills literal atlases, but current-world baseline differencing transfers almost perfectly with a full panel (G3D). Restoring a hard post-change budget then lets a learned static spatial cover beat two plausible active policies (G3E).

So the current strongest primitive is no longer “active causal address.” It is:

> **remember what this world normally does, then measure change relative to that expectation.**

The next gate must make that memory pay for itself.

## Gate 3F — stale baseline / amortized sensing

The current cheat is large: the observer owns a perfect healthy baseline consequence for every candidate experiment at zero cost.

Replace that with repeated reversible incidents in the same slowly drifting substrate.

At each incident there is a known healthy interval before the fault/change. A diagnostic policy can either spend measurements rebuilding its baseline or reuse remembered expectations from earlier healthy periods.

Compare:

```text
A. REFRESH EVERY INCIDENT
   measure the diagnostic baseline panel again
   then measure post-change panel

B. FROZEN MEMORY
   measure baseline once at the beginning
   reuse forever

C. PERIODIC REFRESH
   reuse memory for R incidents
   then refresh the panel

D. SENTINEL-TRIGGERED REFRESH
   spend one cheap healthy sentinel measurement
   refresh the whole panel only when baseline prediction error is large
```

Use the strong **G3E greedy static panel** as the diagnostic measurement set. There is no reason to reintroduce adaptive post-change poking until memory itself survives.

### Slow substrate drift

Between incidents, change the healthy transport/wiring substrate slightly without changing the event class. Drift should be large enough that a permanently frozen baseline eventually becomes wrong, but small enough that refreshing every incident is wasteful.

The fault itself remains reversible and local (`geometry`, `wiring`, or `gain`).

This creates the three clocks in a concrete form:

```text
fast:   incident consequence
medium: remembered healthy baseline
slow:   substrate drift
```

### Metrics

For a sequence of repeated incidents report:

- joint cause+address accuracy;
- total healthy-baseline scalar calls;
- total post-change scalar calls;
- total scalar calls per correct diagnosis;
- false diagnoses caused by stale memory;
- refresh count;
- accuracy as drift accumulates.

The useful comparison is **accuracy at matched cumulative measurement cost**, not accuracy alone.

### Kill conditions

If frozen memory stays perfect despite substantial drift, the drift model is too easy and the gate fails.

If refreshing every incident is required to preserve diagnosis, medium-timescale memory has not amortized anything.

If a simple periodic schedule beats a surprise-triggered refresh at the same cost, do not claim active memory management.

A positive result only earns the narrow statement:

> **remembered baseline measurements can amortize repeated diagnosis when the substrate changes more slowly than incidents occur.**

That is a systems result, not a claim about biological memory.

## Gate 3G — sparse baseline acquisition

Only if 3F survives, remove another cheat: the first baseline itself should not begin as a complete table.

Let ordinary interaction gradually populate expected consequences. Repeatedly useful measurements should be retained; rarely useful ones may decay or be evicted under a fixed memory budget.

Attack with a simple frequency/LRU cache before inventing learned consolidation.

This is the first place where V24's old statement **“remembering changes future sensing”** could become an engineering result rather than a metaphor: a stored consequence is valuable only if it saves future measurement calls.

## Gate 4 — postpone dynamical islands

Do not return to `SpectralIslandsV2` yet. First determine whether medium-timescale expectation memory actually lowers evidence cost under realistic drift.

If it does, the later architecture becomes:

```text
slow structure
    ↓
expected local consequences
    ↓
current residual
    ↓
static coverage / selective measurement
    ↓
update medium memory
    ↓ repeated consequence
possibly alter slow structure
```

If it does not, prune the memory layer too.

**Before asking memory to think, make it save measurements.**
