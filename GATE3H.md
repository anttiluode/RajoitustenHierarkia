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

The healthy substrate now follows a locked nonstationary drift schedule:

```text
incidents 0–7:   stable / very slow drift
incidents 8–15:  rapid drift burst
incidents 16–23: new stable epoch
```

The observer is not told the drift phase.

Every incident still uses an eight-scalar post-change diagnostic panel. All healthy checks and refreshes are charged as scalar measurements.

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

## Metrics

- joint cause+exact-address diagnosis accuracy;
- total baseline/check/post-change scalar calls;
- calls per incident;
- calls per correct diagnosis;
- stale cache uses;
- refresh-trigger count;
- accuracy separately in stable-pre / burst / stable-post epochs;
- baseline calls by epoch;
- best fixed/TTL attacker chosen by calls per correct diagnosis.

## Decision rule

The result is explicitly allowed to be negative.

The residual policy earns the narrow positive classification only if it stays within three accuracy points of the best fixed/TTL attacker **and** improves calls-per-correct-diagnosis by at least 5%.

Otherwise the gate records that a boring fixed clock or TTL remains competitive.

## Kill conditions

If plain LRU never becomes stale, the drift burst is too weak.

If no bounded-memory policy saves at least 20% of total evidence versus fresh calibration, the cache has stopped paying rent.

If residual checks never trigger, the adaptive assay is ineffective.

## Claim boundary

Even a positive result would support only:

> **distributed prediction error can sometimes decide when reusable black-box expectations need recalibration under a changing slow world.**

It would not establish active inference, biological surprise consolidation, or a general adaptive-memory theorem.

The gate is implemented in `experiments/gate3h_variable_drift_cache.py` and is locked into CI before its result is promoted.
