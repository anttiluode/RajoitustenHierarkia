# Gate 3G — sparse expectation cache

Gate 3F established a narrow value for medium-timescale memory: reusing healthy baseline consequences can preserve diagnosis while avoiding repeated scalar measurements under slow substrate drift. It still started with the useful baseline panel already populated.

Gate 3G removes that free initialization.

## Question

> If expected consequences must be acquired one scalar at a time and memory capacity is smaller than the set of useful expectations, what retention mechanism actually earns work?

This gate isolates cache replacement from drift. The healthy substrate is fixed during each sequence; Gate 3F already audited staleness. Each world starts with an **empty cache**.

## Workload

The Gate-3E static diagnostic panel has eight scalar experiments. Four rotated contexts require four disjoint versions of that panel, for **32 distinct baseline expectations**. Cache capacity is **12**, so the observer cannot retain everything.

The context schedule changes halfway through the sequence. The first regime emphasizes contexts 0/1; the second emphasizes 2/3. This deliberately attacks retention rules that permanently protect historically frequent entries.

For each required experiment:

```text
if expected consequence is cached:
    buy post-change scalar only
else:
    buy healthy/recovery baseline scalar
    buy post-change scalar
    optionally retain the expectation
```

Diagnosis itself uses the same shared relative-delta likelihood model. Cache policies differ only in which healthy expectations must be repurchased.

## Attackers

- **no cache** — repurchase every baseline scalar;
- **LRU** — retain recent expectations;
- **LFU** — retain lifetime-frequent expectations, with no frequency decay across the regime switch;
- **random eviction** — boring capacity-only baseline;
- **Belady oracle** — future-use ceiling, evicting the cached expectation whose next use lies farthest ahead.

## Metrics

- joint cause+exact-address diagnosis accuracy;
- healthy baseline scalar calls;
- post-change scalar calls;
- total scalar calls per incident;
- total calls per correct diagnosis;
- cache hit rate;
- baseline calls before and after the regime switch.

## Kill conditions

Caching has not earned a role if simple retention materially damages diagnosis relative to repurchasing every baseline.

A learned consolidation mechanism has not earned work if LRU or random eviction is already close to the future-use oracle.

Lifetime-frequency retention is specifically attacked for over-consolidation: after the context distribution changes, its baseline reacquisition cost should rise if old frequent entries remain protected.

## Claim boundary

A positive result would support only the following narrow systems statement:

> **A bounded store of expected consequences can reduce future evidence acquisition, and under changing demand simple recency may be sufficient.**

It would not establish a biological consolidation law, a new cache algorithm, or a need for learned memory management.

The gate is executed by `experiments/gate3g_expectation_cache.py` and is locked into CI before its result is promoted to the README.
