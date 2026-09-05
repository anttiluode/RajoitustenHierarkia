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

## Executed result

Locked CI evaluation covers **30 held-out worlds × 24 incidents = 720 incidents**.

| policy | joint accuracy | baseline calls | calls / incident | cache hit rate |
|---|---:|---:|---:|---:|
| no cache | **74.44%** | 5,760 | 16.00 | 0.00% |
| LRU | 73.06% | **1,920** | **10.67** | 66.67% |
| LFU | 75.14% | 4,080 | 13.67 | 29.17% |
| random | 74.72% | 2,195 | 11.05 | 61.89% |
| future-use oracle | 73.61% | **1,560** | **10.17** | 72.92% |

LRU preserves **98.13% of no-cache diagnosis accuracy** while cutting healthy-baseline acquisition by **66.67%** and total scalar calls by **33.33%**.

The oracle only improves baseline acquisition from 1,920 to 1,560 calls. LRU therefore uses **23.08% more baseline calls than a future-knowing cache**, but only **4.92% more total calls** (10.67 vs 10.17 per incident). That is small headroom for a learned replacement policy on this workload.

Random eviction is also unexpectedly strong: **74.72%** diagnosis at 11.05 calls/incident. It uses only **14.32% more baseline calls than LRU**.

The deliberate over-consolidation attacker behaves as intended. LFU baseline misses rise from **1,680** before the regime switch to **2,400** after it, a **42.86% increase**. LRU is exactly flat at **960 / 960**. Lifetime frequency protects the old regime too strongly once demand changes.

Diagnosis accuracy differences between cache policies are small and partly reflect which noisy healthy baseline sample is retained. The primary result is evidence cost, not an accuracy win.

## What survived

The useful statement became narrower again:

> **A bounded cache of expected consequences can substantially amortize future diagnostic evidence, but simple recency already captures most of the available value under changing demand.**

The result also supplies a concrete failure mode for overly slow consolidation: an expectation can remain internally valid while becoming externally useless because the task distribution moved elsewhere.

## What did not survive

A learned consolidation mechanism has not earned architectural work here. LRU is close to the future-use ceiling and random eviction is surprisingly competitive. LFU-style permanent importance is actively worse after the regime shift.

This does **not** show that recency is a universal memory law. The workload has a small context alphabet, exact cache keys, no recombination between contexts, and no simultaneous substrate drift.

## Next cheat

Recombine the two pressures separated by Gates 3F and 3G:

```text
expectations can become useless because demand changed
                    +
expectations can become wrong because the world drifted
```

Gate 3H should vary the slow drift rate itself so neither a fixed refresh period nor pure LRU is automatically correct. Only then does distributed surprise / adaptive refresh get a fair workload.

The gate is executed by `experiments/gate3g_expectation_cache.py` and rerun in CI on every PR.
