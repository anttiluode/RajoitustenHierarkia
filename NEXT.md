# NEXT — make memory earn every slot

Gates 0–3F have pruned the original story aggressively.

Known factorization helps after structural change (G0–G2). Fixed addresses make adaptivity unnecessary (G3A/G3B). Moving addresses gives sequential measurements some localization value (G3C). Across unseen substrates, a simple current-world baseline delta is enough to remove most substrate variation (G3D). Under a hard evidence budget, a static spatial cover beats two active post-change policies (G3E). Under slow healthy drift, periodically reused baseline memory preserves almost all fresh-calibration accuracy at far lower cumulative measurement cost (G3F), while a one-sentinel trigger loses to the boring schedule.

So the surviving mechanism is now:

> **cache expected consequences long enough to amortize measurement, but not so long that substrate drift makes them wrong.**

The next gate should attack the fact that the cache currently begins full.

## Gate 3G — sparse expectation cache

Remove the free initial eight-entry baseline panel.

The world begins with an empty expectation cache and a fixed memory capacity smaller than the candidate measurement set. Healthy ordinary interaction occasionally exposes `(poke node, read time) -> scalar consequence`. The machine can store some of those expectations for future incidents.

When an incident occurs, a diagnostic panel entry has two possible costs:

```text
cached expectation:
    pay 1 post-change scalar
    delta = post - cached baseline

not cached:
    pay 1 healthy/recovery baseline scalar
    + 1 post-change scalar
```

Repeated use should therefore make some baseline entries worth retaining.

### Workload

Use several diagnostic contexts rather than one permanently fixed panel. For example, draw incident families from a small set of static panels or task regimes so some measurements are frequent, some rare, and the useful set changes over time.

The cache capacity must be too small to hold every potentially useful baseline.

Healthy substrate drift remains slow; cached values also carry an age and are periodically invalidated/refreshed using the Gate-3F schedule.

### Attackers

Before any learned consolidation rule, compare:

- **no cache** — reacquire every needed baseline;
- **LRU** — evict least recently used expectation;
- **LFU/frequency** — retain most frequently reused entries;
- **value cache** — retain entries with highest measured saved-call utility;
- **random eviction**;
- **oracle future-use cache** as a ceiling.

Do not call the value cache “learning” unless it actually estimates future utility beyond simple counts.

### Metrics

- joint diagnosis accuracy;
- total scalar measurement calls;
- baseline calls avoided by cache hits;
- cache hit rate;
- calls per correct diagnosis;
- stale-cache error rate;
- regret versus oracle cache;
- adaptation after the task-regime frequencies switch.

### Kill conditions

If LRU or LFU is essentially oracle, there is no reason for a learned consolidation mechanism.

If cache hits do not reduce total measurements because stale refresh costs cancel the savings, persistent expectation memory loses its practical role.

If a cache only helps because the workload repeats an exactly fixed panel, the workload is too easy; the useful measurement distribution must shift at least once.

A positive result earns only:

> **retaining frequently reusable expected consequences can reduce future diagnostic measurement cost under a fixed memory budget.**

That is caching, not a new theory of memory.

## Gate 3H — variable drift, only if 3G survives

Gate 3F's period-4 refresh wins partly because the drift timescale is stationary.

After sparse caching works, vary the slow timescale itself:

```text
long stable epoch
→ rapid drift episode
→ new stable epoch
```

Now compare fixed-period refresh against multi-sentinel residual statistics or distributed cache-consistency signals.

Only here does an adaptive refresh policy get a fair workload. A single sentinel already failed in G3F; any richer trigger must beat the best fixed schedule at matched cumulative cost.

## Later — slow structural adaptation

Do not alter the substrate yet.

Only after the system can cheaply maintain useful expectations should repeated diagnostic consequences be allowed to change the slow operator itself. Then the three timescales would have earned separate engineering roles:

```text
fast      current incident / pulse
medium    expectation cache / calibration memory
slow      routing or structural operator
```

At that point the question becomes whether repeated medium-timescale evidence should be compiled into slower structure. Until then, structure learning is premature.

**Memory is now a cache. Make the cache beat no-cache before asking it to become a brain.**
