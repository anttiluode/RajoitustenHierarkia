# Gate 3E — hard-budget delta diagnosis

Gate 3D found a deliberately boring invariant: on unseen substrates, subtracting the remembered response of the current world from the post-change response almost solves cause+address identification when all 168 scalar measurements are available.

Gate 3E restores the evidence budget and attacks the remaining active-sensing story.

## Assay

Training and test substrates are disjoint: 30 training worlds and 30 held-out worlds, with different node-specific local transport weights and different sparse directed long-range graphs.

The hidden event is one of three local causes at one of 24 nodes:

```text
geometry / wiring / gain
```

so there are 72 `cause × address` hypotheses.

The machine is allowed to remember the current world's baseline consequence table. A paid post-change experiment returns one scalar delta:

```text
(poke node, read time)
        ↓
current scalar consequence
        ↓ subtract remembered baseline
Δ consequence
```

There are 168 candidate scalar measurements (`24 nodes × 7 read times`). The transferable likelihood model is shared across literal node IDs and indexed only by cause family, directed ring offset from a candidate changed node to the poke node, and read time.

## Attackers

Four acquisition strategies receive the same likelihood model and the same post-change budget:

- **active joint** — posterior-weighted separation over all cause+address hypotheses;
- **active address** — a second heuristic explicitly targeting address uncertainty;
- **greedy static** — one fixed probe panel learned only on the 30 training substrates, each added probe chosen to maximize training joint accuracy;
- **random** — random probe/time pairs.

The full 168-probe panel is the ceiling.

## Executed result

Joint cause+exact-address accuracy on 360 events from 30 unseen substrates:

| paid post-change scalars | active joint | active address | greedy static | random |
|---:|---:|---:|---:|---:|
| 1 | 8.61% | 11.67% | 8.61% | 10.28% |
| 2 | 19.17% | 20.28% | 16.67% | 18.06% |
| 3 | 27.78% | 28.89% | 23.61% | 25.28% |
| 4 | 34.17% | 33.33% | **35.00%** | **35.83%** |
| 6 | 51.67% | 44.72% | **52.22%** | 40.56% |
| 8 | 62.22% | 53.06% | **72.50%** | 50.83% |

The full 168-probe panel reaches **100%** joint accuracy.

At eight probes the split is especially informative:

| policy | cause accuracy | address accuracy | joint |
|---|---:|---:|---:|
| active joint | **94.17%** | 62.22% | 62.22% |
| active address | 70.56% | 60.00% | 53.06% |
| greedy static | 90.28% | **73.89%** | **72.50%** |
| random | 76.94% | 53.06% | 50.83% |

The active-joint heuristic actually learns the **cause family** slightly better than the static panel, but it covers space less effectively. Exact diagnosis requires both. The boring static panel distributes its probes across the substrate and therefore wins the joint task.

The learned eight-probe static panel is:

```text
(22, t=4)
(15, t=7)
(11, t=4)
(19, t=7)
( 6, t=4)
( 1, t=4)
(13, t=5)
( 4, t=5)
```

Its joint accuracy rises from 8.61% at one probe to 35.00% at four, 52.22% at six, and 72.50% at eight on unseen worlds.

## Interpretation

Gate 3E does **not** establish that active sensing is useless. It establishes a narrower negative:

> **Once current-world delta memory is available, these two plausible adaptive information-gain heuristics do not beat a learned static spatial coverage panel on this synthetic exact-localization task.**

That matters because the active loop was in danger of becoming architectural ceremony. The current evidence says the stronger primitive is the remembered baseline, not the adaptive poke policy.

A useful failure mode is visible in the numbers. Maximizing generic hypothesis separation can spend measurements learning **what kind of change occurred** while neglecting coverage needed to discover **where it occurred**. A static panel can win by simply covering space better.

This suggests an engineering rule:

```text
before building an adaptive diagnostic policy,
learn the best static measurement cover.
```

Adaptivity only earns work when the situation changes which measurements are useful.

## Remaining cheat

The baseline memory is still perfect and free. The machine is assumed to possess the current healthy world's baseline consequence for every candidate measurement.

That is now the obvious thing to attack.

Gate 3F should make baseline memory costly, sparse, noisy, and stale under slow substrate drift. The relevant comparison is no longer primarily active-vs-static post-change probing. It is:

```text
remeasure baseline every incident
        versus
remember baseline and refresh selectively
```

If memory cannot preserve near-reference diagnosis while using fewer total scalar measurements across repeated incidents, then the medium-timescale memory story also loses.

CI classification:

`CURRENT_WORLD_DELTA_TRANSFERS_BUT_A_GREEDY_STATIC_COVERAGE_PANEL_BEATS_TWO_ACTIVE_HEURISTICS_AT_HIGH_SMALL_BUDGET; ACTIVE_DIAGNOSIS_NOT_YET_NECESSARY`
