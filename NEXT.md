# NEXT — stop tuning the toy cache

Gates 0–3H have now removed enough machinery that another synthetic memory-policy gate would mostly optimize this particular generated world.

The sequence has earned a narrower systems mechanism:

```text
known structure helps transfer
        ↓
current-world baseline subtraction removes substrate nuisance
        ↓
a small static measurement cover often beats adaptive probing
        ↓
remembered healthy consequences can amortize repeated diagnosis
        ↓
LRU is already near a future-use cache oracle when demand shifts
        ↓
when the world itself drifts, age/TTL remains a strong attacker
        ↓
distributed residual checks improve accuracy, but not enough to
beat TTL on the preregistered calls-per-correct criterion
```

Gate 3H is the stopping boundary for synthetic cache invention.

## What Gate 3H actually left us

The workload combined a 12-slot cache, four shifting diagnostic contexts, and a hidden stable → rapid-drift → stable substrate schedule.

Plain LRU went stale: **164 stale uses**, with burst accuracy falling to **60.83%** while fresh calibration stayed at **73.75%**.

The residual-2 policy remeasured two distributed expectations, triggered 69 refreshes, reduced stale uses to **3**, and reached **72.92%** overall at **12.23 calls/incident**. It nearly matched the phase-knowing oracle (**73.75%**, 12.67 calls/incident) and dominated the aggressive period-2 clock.

But TTL-4 still had the best boring calls-per-correct result: **16.35** versus residual-2 **16.78**. Residual bought 3.61 percentage points more diagnosis for 7.94% more total calls, so it failed the locked necessity criterion.

That is enough information. Do not invent Gate 3I just to rescue surprise.

## Gate 4 — real repeated regression diagnosis

Move the surviving mechanism into `LentoOrava` / PulseTriage.

PulseTriage already has the right external shape:

```text
candidate reversible changes
        ↓
choose grouped rollback experiment
        ↓
run expensive validation
        ↓
one scalar KPI
        ↓
localize harmful changes
```

The new question is not whether cache policies work on another generated ring. It is:

> **Across a sequence of real-ish software/ML regressions, can remembered healthy rollback outcomes reduce repeated validation calls without materially reducing recovered KPI?**

### Workload

Start from the executed PulseTriage digits/preprocessing benchmark rather than making a new synthetic simulator.

Run a sequence of incidents against the same evolving validation system. Between incidents allow modest benign drift — changed data slice, preprocessing calibration, or model seed/config — while fault sets also change.

For each coded rollback experiment, the system may cache its healthy scalar validation consequence.

On a later incident:

```text
cached healthy consequence exists and is fresh enough:
    buy post-change validation only
    use Δ KPI

otherwise:
    buy/reconstruct healthy reference
    then buy post-change validation
```

### Attackers

Compare the smallest useful set:

- ordinary PulseTriage with no cross-incident cache;
- exact-key LRU;
- LRU + TTL;
- residual-checked cache only if there is enough drift to justify it;
- exhaustive individual rollback ceiling.

Do **not** add a learned cache controller unless LRU+TTL leaves meaningful measured headroom.

### Metrics

The product-facing metrics are now:

- recovered lost KPI;
- actual fault recall;
- total validation calls over the whole incident sequence;
- validation calls per recovered KPI point;
- cache hit rate;
- false attribution from stale cached calibration;
- degradation after benign distribution/model drift.

The useful number is cumulative validation work saved, not internal prediction accuracy.

### Kill condition

If cached calibration does not reduce total validation calls after accounting for refresh/reconstruction, remove the memory layer from the practical story.

If LRU+TTL saves calls but worsens recovered KPI enough that ordinary PulseTriage is preferable, keep ordinary PulseTriage.

A positive result earns only:

> **reusing healthy black-box intervention outcomes can amortize repeated regression diagnosis.**

That is a deployable feature-shaped claim.

## Only after a real workload survives

If repeated-regression caching works outside the ring model, then revisit the deeper three-timescale synthesis:

```text
fast      incident / current scalar consequence
medium    reusable expected consequences
slow      changing system / operator
```

Only then ask whether repeated medium evidence should alter the slow operator itself. That is where `Operaattori`, `OutoSynapsi`, V24 write-timescale work, and the old Geometric Neuron intuition can reconnect without being protected by a synthetic benchmark.

A visualizer can come after the mechanism is stable. It should make the evidence economy visible: which scalar outcomes were bought, reused, invalidated, and which regression was repaired.

**The next gate is usefulness, not another cache policy.**
