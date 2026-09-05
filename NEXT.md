# NEXT — make the hierarchy useful under a hard evidence budget

Gates 0–3D now leave a much cleaner boundary.

Known factorization transfers efficiently after structural change (G0–G2). Hidden causes can be inferred from consequences, but fixed addresses make adaptivity unnecessary (G3A/G3B). Moving the event restores a modest value for sequential pokes in exact localization (G3C). Changing the entire substrate kills literal coordinate atlases, but a much simpler representation wins: **current-world before/after differencing** (G3D).

So the next question is not “what is a causal address?” It is:

> **Given a remembered baseline of this world, which few differences are worth measuring?**

## Gate 3E — active delta diagnosis on unseen substrates

Keep the G3D world family: training and test use different local transport weights and different directed long-range graphs.

The machine may remember baseline consequences collected during ordinary life before the change. After the change it gets only a tiny paid budget.

A candidate paid experiment is:

```text
(poke address, read time)
        ↓
post-change scalar consequence
        ↓ subtract remembered baseline for same experiment
Δ consequence
```

The observer should update a posterior over `cause × changed address` and choose the next experiment by expected separation / information gain.

### Attackers

- random delta probes;
- one globally learned fixed delta panel;
- a coarse-residual-routed fixed delta panel;
- greedy static panel trained across all worlds;
- active sequential delta observer;
- full 168-probe delta panel ceiling.

The fixed panels must be learned only on training substrates. Test worlds are unseen.

### Metrics

- joint cause+exact-address accuracy at 1/2/3/4/6 probes;
- cause-family accuracy separately;
- exact localization given correct cause;
- degradation after consistent random node relabeling;
- full-panel ceiling;
- number of post-change scalar measurements.

### Kill condition

If a tiny static delta panel performs as well as adaptive selection on unseen substrates, active measurement has not earned work. Keep the simpler static diagnostic.

If active wins only for localization but not cause-family classification, preserve that narrower result.

If all methods collapse once the full 168-panel is removed, then G3D showed representational invariance but not useful bounded diagnosis.

## Gate 3F — forget the perfect baseline

Only if 3E survives, attack the assumption that the machine has a clean full baseline table.

Make baseline memory sparse, noisy, stale, or locally maintained. Then ask whether medium-timescale memory can reconstruct enough expectation to support cheap diagnosis.

This is where the three-timescale architecture can finally earn work:

```text
fast:   current pulse / consequence
medium: remembered local expectation
slow:   substrate / routing parameters
```

A strong attacker is a model that simply spends more baseline measurements up front. Memory is only interesting if it amortizes repeated future diagnosis.

## Gate 4 — dynamical objects only after diagnosis survives

Do not return to `SpectralIslandsV2` yet. First establish that bounded diagnosis works across unseen substrates with a realistic memory/evidence budget.

Only then introduce multiple nonlinear dynamical objects and ask whether their identity survives substrate drift by causal fingerprint rather than frequency label.

## Later: ordering and structural adaptation

If repeated diagnoses identify recurring changes, then test whether medium memory should eventually alter the slow operator. That is where `Operaattori`, `OutoSynapsi`, V24 memory, and the old Geometric Neuron intuition can genuinely converge:

```text
surprise
   ↓
cheap residual
   ↓
selective experiment
   ↓
what changed + where?
   ↓
remember
   ↓ repeated often enough
slowly alter routing / structure
```

But that step should not be built until the evidence-budget gate survives.

**Before inventing a new representation, subtract the baseline. Before inventing an active observer, attack it with a fixed panel.**
