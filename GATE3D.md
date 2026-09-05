# Gate 3D — unseen substrates

Gate 3C moved the hidden event address but kept one underlying substrate. Gate 3D changes the substrate itself across worlds.

## Assay

Thirty training worlds and thirty held-out worlds each receive different node-specific local transport weights and a different sparse directed long-range graph. The hidden causes are local geometry, wiring, or gain changes at arbitrary nodes.

This first audit intentionally uses the **full 168-measurement panel** (`24 nodes × 7 read times`). The purpose is to isolate representation transfer before reintroducing a paid-probe budget.

For every current world the observer is allowed to remember the pre-change response. We compare:

- absolute post-change templates tied to literal node IDs;
- absolute node-shared templates;
- current-world `after - before` deltas tied to literal node IDs;
- node-shared delta templates;
- baseline-normalized variants;
- a mandatory consistent random node relabeling control.

## Executed result

On 360 held-out events from 30 unseen substrates:

| representation | cause | address | joint |
|---|---:|---:|---:|
| absolute literal atlas | 37.22% | 6.11% | **5.00%** |
| absolute shared | 55.28% | 37.50% | **35.28%** |
| delta literal atlas | 98.89% | 98.89% | **98.89%** |
| delta shared | 99.17% | 99.17% | **99.17%** |
| normalized literal | 97.78% | 97.78% | **97.78%** |
| normalized shared | 96.94% | 96.94% | **96.94%** |

After independently and consistently relabeling every held-out world's node coordinates, joint accuracy remains **98.33%** for both the literal-delta and shared-delta variants. The absolute literal atlas falls to **3.33%** joint accuracy.

CI classification:

`CURRENT_WORLD_BASELINE_DIFFERENCING_ERASES_MOST_SUBSTRATE_VARIATION; RELATIVE_CAUSAL_ADDRESS_HAS_NOT_EARNED_MORE_THAN_DIFFERENTIAL_CHANGE_DETECTION`

## Interpretation

The coordinate-atlas story really does fail across unseen substrates. But the replacement does **not** need a sophisticated learned causal-address representation in this assay.

A boring current-world residual is enough:

```text
baseline response in this world
        ↓
post-change response
        ↓
after - before
        ↓
shared change template
```

That almost completely removes substrate-specific variation. Extra normalization does not help.

So the present result is not:

> we discovered a substrate-invariant causal address language.

It is:

> **for this world family, differential change detection relative to the current substrate is already the invariant representation.**

This is a useful negative boundary. The system needs memory of what *this world normally does* more than it needs an abstract coordinate ontology.

## Remaining cheat

The result spends all 168 scalar measurements after the change. That is far outside the bounded-observer regime.

The next test should therefore keep the current-world baseline memory but restore a strict paid-measurement budget. The question is no longer whether deltas transfer; they do. The question is whether **sequentially choosing which delta to measure** buys anything over a small fixed or random panel on unseen substrates.

If a tiny static delta panel wins, active diagnosis loses again.
