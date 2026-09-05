# NEXT — combine stale memory with changing demand

Gates 0–3G have turned the original “hierarchy of constraints” idea into a much more testable systems problem.

Known factorization helps after structural change (G0–G2). Fixed addresses make adaptivity unnecessary (G3A/G3B). Moving addresses gives sequential measurements some localization value (G3C). Across unseen substrates, a current-world baseline delta removes most substrate variation (G3D). Under a hard evidence budget, a learned static spatial cover beats two active post-change policies (G3E). Under slow drift, periodically reused baseline memory preserves almost all fresh-calibration accuracy at much lower cumulative cost (G3F). When useful expectations exceed memory capacity, LRU is already near a future-use oracle and lifetime-frequency retention over-consolidates the old regime (G3G).

The surviving mechanism is now:

> **remember expected consequences when reuse saves future measurement, but refresh or discard them when either the world or demand changes.**

The next gate should combine the two pressures that 3F and 3G deliberately separated.

## Gate 3H — variable drift + sparse cache

Gate 3F changed the world but kept the useful panel fixed. Gate 3G changed demand but kept the world fixed.

Now run both at once.

Each held-out world has a sparse expectation cache smaller than the total useful measurement set. Diagnostic contexts switch over time, while the healthy substrate follows a nonstationary drift schedule:

```text
stable epoch
    ↓
rapid drift burst
    ↓
new stable epoch
```

A cached expectation can therefore fail in two distinct ways:

```text
still accurate but no longer useful      (demand moved)
recently useful but now numerically wrong (substrate moved)
```

That distinction matters. Pure recency only sees demand. A fixed refresh clock only sees elapsed time. Neither directly measures prediction error.

### Policies to compare

Use the same diagnosis model and static post-change panels. Compare memory-management policies only:

- **no cache / fresh baseline** — expensive reference;
- **LRU + fixed period refresh**;
- **LRU + short fixed period** — attacker tuned for rapid drift;
- **LRU + long fixed period** — attacker tuned for stable epochs;
- **age-only TTL**;
- **distributed residual refresh** — use several cheap healthy cache checks and refresh entries whose expected consequence becomes inconsistent;
- **oracle stale-bit / future-use** ceiling.

Do not use one sentinel again; Gate 3F already showed that a single scalar is a poor summary of distributed drift.

### A fair adaptive trigger

A candidate distributed trigger may sample `k` cached expectations during healthy intervals and compute residuals:

```text
r_i = observed healthy consequence_i - cached expectation_i
```

The trigger must not know the drift phase. It may refresh only when the sampled residual distribution exceeds a threshold learned on training worlds.

The trigger's own scalar checks count toward total evidence cost.

### Metrics

Report:

- joint cause+exact-address accuracy;
- total baseline/cache-check/post-change scalar calls;
- calls per correct diagnosis;
- stale-cache error rate;
- cache hit rate;
- refresh count;
- performance separately in stable / burst / post-burst epochs;
- regret versus the best fixed policy chosen in hindsight;
- regret versus oracle stale/future knowledge.

### Kill conditions

If one fixed refresh period is essentially optimal across the whole schedule, adaptive refresh still has not earned work.

If residual checks cost as much as the saved refreshes, adaptive management has no practical value.

If LRU plus a simple TTL is near oracle, stop there.

A positive result earns only:

> **distributed prediction error can decide when cached expectations have become stale under nonstationary drift, reducing evidence cost relative to any single fixed refresh timescale.**

That would be the first gate where “surprise controls memory maintenance” survives a strong boring attacker.

## Gate 3I — only if 3H survives: utility-weighted cache

If adaptive staleness detection is useful, then combine it with demand value. Each cache entry would have two quantities:

```text
validity:  is this expectation still true?
utility:   is this expectation likely to save future calls?
```

Attack any learned utility rule with LRU, LFU-with-decay, and simple exponential recency-frequency scores first.

Only if those fail should a learned retention policy be introduced.

## Later — compile repeated evidence into slow structure

Do not alter routing yet.

The architecture should earn three distinct clocks before slow structural adaptation is introduced:

```text
fast      current incident / pulse
medium    cached expected consequences + validity
slow      substrate / routing operator
```

If repeated medium-timescale evidence reliably predicts a persistent change in the slow world, then ask whether changing the operator reduces future diagnostic or control cost. That is where `Operaattori`, `OutoSynapsi`, V24 write-timescale work, and the old Geometric Neuron intuition can finally meet without metaphor doing the work.

**First make surprise beat a clock. Then let surprise change structure.**
