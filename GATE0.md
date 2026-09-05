# Gate 0 — state-dependent operator

The first question is deliberately smaller than “which substrate explains the brain?”

> **Can a system whose effective operator depends on current state be distinguished from a flat geometry+connectivity mixture by held-out interventions?**

## World

For a 24-node ring with a local geometric operator `G`, a random directed long-range operator `C`, local state `q`, previous state `x_prev`, current state `x`, and localized input `u`, the synthetic world is

```text
y = tanh(0.72 Gx + 0.48 q C x_prev + 0.35 u + noise)
```

The interaction `q*C` is the point. Connectivity exists physically in every condition, but its effective contribution changes with state.

Training states:

```text
q = 0.5, 0.8, 1.1, 1.4
```

Test states:

```text
q = 0.65, 0.95, 1.25, 1.7
```

Thus `q=1.7` is a held-out operator state beyond the training range.

## Attackers

All models know the `tanh` response law and receive the same observations available to their hypothesis class.

| model | terms available |
|---|---|
| geometry | `Gx`, input |
| connectivity | `C x_prev`, input |
| flat | `Gx + C x_prev`, input; fixed coefficients across state |
| hierarchy | `Gx + q C x_prev`, input |

The hierarchy does not receive the true coefficients. Every model fits its best coefficients from training data.

## Deterministic seed-7 result

The expected executed result is approximately:

| model | held-out next-state MSE |
|---|---:|
| geometry | 0.1093 |
| connectivity | 0.2607 |
| flat geometry+connectivity | 0.01165 |
| state-conditioned hierarchy | **0.000280** |

On the hardest unseen state `q=1.7`:

```text
flat       ~0.02994 MSE
hierarchy  ~0.000241 MSE
```

The important assay is a paired counterfactual. The physical `x`, `x_prev`, `G`, `C`, and input are held exactly fixed while only `q` changes from `0.5` to `1.7`.

The true future changes with RMS magnitude about `0.286`.

The flat model predicts **zero change**, because its effective operator is frozen.

The hierarchy predicts the counterfactual change with correlation `> 0.999999` and delta MSE around `1.8e-8`.

## What this means

This does **not** show that the brain implements this hierarchy. The world was generated with a state-dependent operator, so the positive result is a calibration test for the research machinery.

It does establish the discriminator we need for later gates:

> Two descriptions can fit ordinary states similarly while making different predictions about a controlled change to one constraint layer.

That is the escape hatch from the static-eigenmode reconstruction problem.

## Kill condition for later gates

Once the simulator is no longer generated directly from the hierarchy hypothesis, kill the hierarchy claim if a state-blind flat model predicts held-out interventions, delays, wave directions, return times, and transitions just as well.
