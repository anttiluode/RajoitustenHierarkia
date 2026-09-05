# Gate 3C — move the hidden address

Gate 3B found the embarrassing shortcut: when every cause always changes the same physical address, a learned fixed diagnostic panel can beat the adaptive observer. Two static probes were enough.

Gate 3C moves the event.

## World

There are 24 physical nodes. Four local cause families can occur at **any** node:

- local geometry / transport deformation;
- directed long-range wiring change;
- local recurrent-gain change;
- hidden external-input change.

Delay change and no-change remain global controls.

The resulting latent diagnostic space has

```text
24 x 4 local causes + delay + none = 98 hypotheses.
```

## Free evidence

Ordinary activity contains a known random background command plus hidden external drive. The observer owns a remembered baseline operator and knows the command it issued (an explicit efference-copy assumption).

It computes one-step baseline residuals and pools them into only six spatial bins, four physical nodes per bin. Only the **normalized spatial distribution of residual magnitude** is retained, so total residual amplitude cannot directly identify the cause.

This is a cheap coarse address, not the answer.

## Paid evidence

A paid experiment is

```text
(poke node, read time) -> one scalar global consequence error
```

with 24 poke addresses x 7 read times = **168 candidate scalar interventions**.

The observer is never handed `G`, `C`, delay, gain, or the true changed node.

A training bank estimates empirical response distributions for the 98 hypotheses. Cause priors are balanced so the 24 address variants do not swamp the global classes.

## Attackers

The strongest useful attacker is no longer merely a global fixed panel.

`bin_fixed` may inspect the free coarse residual map, choose one of six pre-learned diagnostic panels, and then execute that whole panel without adapting to paid outcomes. In other words it gets **one-shot conditional routing** for free; only the active policy may change later questions after seeing earlier answers.

## Executed result

Seed 17; 784 training examples and 360 held-out examples.

### Cause family alone

| paid pokes | active | global fixed | coarse-bin fixed | random |
|---:|---:|---:|---:|---:|
| 0 | 73.33% | — | — | 73.33% |
| 1 | 79.72% | 80.00% | 80.00% | 77.78% |
| 2 | 81.39% | 80.56% | 80.56% | 78.33% |
| 3 | **83.61%** | **83.61%** | 81.11% | 78.61% |
| 4 | **85.28%** | 84.17% | 81.94% | 81.94% |

This is **not** a meaningful adaptive win. The cheap coarse residual plus fixed probes already carries most of the cause-family information.

### Joint cause + exact physical address

For local causes, both the cause and the exact node must be correct. Global delay/no-change require only the correct cause.

| paid pokes | active | global fixed | coarse-bin fixed | random |
|---:|---:|---:|---:|---:|
| 0 | 34.72% | — | — | 34.72% |
| 1 | **51.11%** | 45.83% | 46.94% | 43.89% |
| 2 | **61.67%** | 50.00% | 54.72% | 45.83% |
| 3 | **66.39%** | 57.22% | 59.44% | 49.17% |
| 4 | **69.72%** | 62.22% | 61.11% | 54.72% |

At three paid pokes, adaptive questioning gains:

- +9.17 percentage points over the globally fixed learned panel;
- +6.94 points over the stronger coarse-bin-conditioned panel;
- +17.22 points over random pokes.

### Localization, conditional on already getting the cause right

At three pokes:

```text
active            70.33%
coarse-bin fixed  61.76%
global fixed      54.55%
random             46.19%
```

The full 168-probe panel reaches 100% cause accuracy, 88.06% joint cause+address accuracy, and 82.08% localization given a correct cause. So the residual error is partly model/statistical ambiguity, not merely a missing probe budget.

## Classification

```text
MOVING_ADDRESS_MAKES_ADAPTIVE_OUTCOMES_USEFUL_FOR_LOCALIZATION
BUT_CAUSE_CLASSIFICATION_REMAINS_MOSTLY_CHEAP_OR_FIXED
```

This is a partial result, and that is the useful boundary.

Gate 3C does **not** justify the claim that a thinking system needs adaptive interventions just to decide whether a geometry/wiring/gain/input/delay change occurred. In this synthetic world a coarse residual plus a static conditional panel already does nearly as well.

What adaptivity earns is the harder relational question:

> **Which kind of change happened, and where in the current substrate did it happen?**

The paid outcome changes the next address.

That is the first gate in this repo where `address` is not merely metadata attached by the experimenter; it affects the evidence budget.

## Important assumption: efference copy

The cheap residual map subtracts the observer's known background command using the remembered baseline operator. Without knowing what command it issued, ordinary self-generated activity and unexpected world/operator change would be harder to separate.

That assumption is explicit rather than hidden because it connects directly to the self/world ambiguity encountered in `AlternativeNeuron`: intervention consequences become much more interpretable when the machine keeps a privileged record of its own action.

## What remains unearned

All 360 held-out episodes still share the same underlying base geometry and long-range graph. The model may therefore learn node-specific causal fingerprints.

The next gate must randomize the substrate itself.

If an address such as “node 7” stops meaning the same structural position across worlds, successful transfer must use **relative/local dynamical fingerprints**, not a memorized diagnostic atlas.
