# Gate 3F — baseline memory under slow drift

Gate 3D made `current - remembered baseline` the useful cross-substrate representation. Gate 3E then found that a learned eight-probe static panel beats two plausible adaptive post-change policies.

Gate 3F attacks the remaining cheat: the remembered healthy baseline had been treated as perfect and free.

## Assay

Thirty held-out substrates each face **12 reversible local incidents** while their healthy transport/wiring substrate drifts slowly. The incident family remains `geometry`, `wiring`, or `gain`, with moving addresses.

Every policy uses the same locked eight-probe panel learned in Gate 3E and pays the same eight post-change scalar calls per incident.

Only healthy-baseline acquisition differs:

| policy | healthy baseline rule |
|---|---|
| `refresh_every` | reacquire all 8 healthy scalars before every incident |
| `frozen` | acquire the panel once and reuse it forever |
| `periodic_4` | acquire once, then refresh every four incidents |
| `sentinel` | spend one healthy sentinel scalar every incident; if it moves by more than 0.008, buy the other seven panel entries |

The healthy substrate changes by a small deterministic drift independent of the fault: about 0.1% common local-transport scale per incident plus a world-specific local redistribution and a smaller long-range change.

## Executed result

Across **360 incidents**:

| policy | joint cause+address accuracy | healthy baseline calls | post-change calls | total calls | calls / incident | calls / correct diagnosis |
|---|---:|---:|---:|---:|---:|---:|
| refresh every | **71.67%** | 2880 | 2880 | **5760** | **16.00** | 22.33 |
| frozen | 52.78% | **240** | 2880 | **3120** | **8.67** | 16.42 |
| periodic every 4 | **70.56%** | 720 | 2880 | **3600** | **10.00** | **14.17** |
| one-sentinel trigger | 57.22% | 698 | 2880 | **3578** | **9.94** | 17.37 |

The periodic policy preserves **98.45% of the refresh-every accuracy** (`70.56 / 71.67`) while using **37.5% fewer total scalar measurements** (`3600` vs `5760`). It also has the best calls-per-correct-diagnosis of the four policies.

Frozen memory is genuinely stale rather than merely noisier. Its joint accuracy by incident falls from **83.33%** at incident 0 to **30.00%, 23.33%, 20.00%, 33.33%** over incidents 8–11.

Periodic refresh resets that decay: its corresponding incidents 8–11 are **53.33%, 83.33%, 73.33%, 63.33%**.

The sentinel attacker is the second important result. It spends almost exactly the same total budget as periodic refresh (`9.94` vs `10.00` calls/incident) but reaches only **57.22%** accuracy. A single local change detector is a poor summary of distributed baseline drift.

## What this earns

For this synthetic workload, medium-timescale memory finally pays rent:

> **Remembered baseline measurements can amortize repeated diagnosis when the substrate changes more slowly than incidents occur.**

This is not because memory contains a rich world model. It stores expected consequences of a small diagnostic panel and avoids reacquiring them every time.

The useful three-clock decomposition is now concrete:

```text
fast      incident consequence
medium    remembered healthy consequence panel
slow      substrate drift
```

The medium state is valuable only because its timescale lies between the other two.

## What it does not earn

The sentinel result kills a stronger active-memory story. One scalar surprise trigger does not discover when the distributed baseline has become stale. A boring fixed refresh schedule is substantially better at essentially the same cost.

So the present conclusion is **not**:

> memory should actively decide when to consolidate.

It is:

> **reuse expectations for several incidents, then refresh them on a schedule matched to substrate drift.**

That sits comfortably inside ordinary caching/calibration/control ideas. No novelty claim is made.

## Remaining cheats

The initial eight-entry baseline panel still arrives fully populated, and the drift timescale is stationary enough that a period-4 schedule works well.

The next attacks should therefore be:

1. **sparse acquisition / cache budget** — ordinary interaction must earn baseline entries rather than receiving all eight at startup;
2. **variable drift regimes** — a fixed refresh period should eventually become wrong, creating a fairer test for whether a richer refresh signal can beat a schedule;
3. **utility-weighted retention** — compare LRU/frequency/value caches before any learned consolidation rule.

Gate 3G should begin with the first item and attack it with simple cache policies.

CI classification:

`PERIODIC_BASELINE_MEMORY_AMORTIZES_REPEATED_DIAGNOSIS_UNDER_SLOW_DRIFT; FROZEN_MEMORY_GOES_STALE; SIMPLE_PERIODIC_REFRESH_BEATS_ONE_SENTINEL_AT_MATCHED_COST`
