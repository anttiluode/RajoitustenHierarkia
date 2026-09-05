# Gate 3H — variable drift + sparse expectation cache

Gates 3F and 3G isolated two different reasons a stored expected consequence can stop being useful:

```text
G3F: the world changed, so memory became wrong
G3G: demand changed, so memory became unused
```

Gate 3H combines them.

## Question

> Can distributed prediction error decide when cached expected consequences have become stale under a nonstationary slow world, or does a boring fixed refresh schedule still win?

## Workload

Thirty held-out substrates each run the same 24-incident context sequence used in Gate 3G. The observer has a **12-slot LRU cache** serving **32 possible useful expectations**.

The healthy substrate follows a locked nonstationary drift schedule:

```text
incidents 0–7:   stable / very slow drift
incidents 8–15:  rapid drift burst
incidents 16–23: new stable epoch
```

The observer is not told the drift phase. Every incident still uses an eight-scalar post-change diagnostic panel. All healthy checks and refreshes are charged as scalar measurements.

## Policies

- **fresh** — buy all eight current healthy baselines every incident; expensive reference;
- **LRU plain** — refresh only on cache miss;
- **period 2 / 4 / 8** — LRU cache plus fixed current-panel refresh clocks;
- **TTL 4** — refresh a requested entry when its stored age reaches four incidents;
- **residual-2** — among currently needed cache hits, remeasure the two oldest expectations, compute the RMS residual, and refresh the rest of the current panel only when the residual crosses a locked threshold;
- **phase oracle** — unfair ceiling that knows when the hidden rapid-drift phase occurs.

The residual rule uses exactly two distributed healthy checks when two cached hits are available. Those checks count toward evidence cost and also update the checked entries.

## Locked adaptive rule

```text
r_i = healthy_now(i) - cached_expectation(i)

R = RMS(r_1, r_2)

if R > 0.008:
    refresh the remaining current-panel cache hits
else:
    keep them
```

A single sentinel is intentionally not retried; Gate 3F already showed it was a weak summary of distributed drift.

## Executed result

Locked CI covers **30 held-out worlds × 24 incidents = 720 incidents**.

| policy | joint accuracy | calls / incident | calls / correct | stale uses |
|---|---:|---:|---:|---:|
| fresh | **73.61%** | 16.00 | 21.74 | 0 |
| LRU plain | 64.86% | **10.67** | 16.45 | 164 |
| period 2 | 72.36% | 13.33 | 18.43 | 0 |
| period 4 | 68.89% | 12.00 | 17.42 | 20 |
| period 8 | 69.03% | 11.33 | 16.42 | 20 |
| TTL 4 | 69.31% | **11.33** | **16.35** | 20 |
| residual-2 | **72.92%** | 12.23 | 16.78 | **3** |
| phase oracle | 73.75% | 12.67 | 17.18 | 0 |

The variable-drift attack is real. Plain LRU is perfect relative to fresh in the first stable epoch (**72.92%** each), then falls to **60.83%** in the burst while fresh remains **73.75%**. It records 164 stale cache uses.

The distributed residual rule reacts: it triggers **69 refreshes**, cuts stale uses from 164 to **3**, and reaches **70.00%** burst accuracy. Across the whole run it reaches **72.92%**, only **0.83 percentage points** below the phase-knowing oracle, while actually using fewer calls per incident (**12.23 vs 12.67**).

So the adaptive mechanism is not useless. It creates a strong Pareto point and dominates the fast period-2 clock on both accuracy (**72.92% vs 72.36%**) and cost (**12.23 vs 13.33 calls/incident**).

But it does **not** satisfy the preregistered necessity criterion. The best boring attacker by calls per correct diagnosis is TTL-4: **16.35** calls/correct versus residual-2 **16.78**. Residual buys an extra **3.61 percentage points** of joint accuracy over TTL-4, but costs **7.94%** more total scalar calls. It therefore fails the required 5% efficiency win.

The locked classification is:

> **BORING FIXED OR TTL REFRESH REMAINS COMPETITIVE; SURPRISE-DRIVEN MEMORY MAINTENANCE NOT YET NECESSARY.**

## What survived

Two narrower statements survived:

1. **Recency alone is insufficient when the world can change faster than demand.** LRU had learned the right *useful* entries but some of those entries were wrong.
2. **Distributed residual checks are a competent staleness detector.** They almost recover the hidden-phase oracle and remove nearly all stale uses.

What did not survive is the stronger claim that surprise-driven refresh is required. A four-incident TTL remains cheaper per correct diagnosis on this locked workload.

That distinction matters. Gate 3H did not kill residual-based maintenance; it demoted it from "architecture" to an optional point on the cost/accuracy frontier.

## Claim boundary

This result supports a systems observation about reusable black-box calibration under nonstationary drift. It does not establish active inference, biological surprise consolidation, a new cache algorithm, or a general adaptive-memory theorem.

The gate is implemented in `experiments/gate3h_variable_drift_cache.py` and rerun in CI on every PR.
