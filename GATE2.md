# Gate 2 — the generic history attacker catches up, but needs more data

Gate 1 could be dismissed as a semantic convenience: perhaps `geometry + wiring + delay` is just a verbose way to write a sufficiently large autoregressive state-space model.

So Gate 2 gives that objection a serious attacker.

## Attacker

For `N=24`, the generic VAR sees ten full state lags plus the current input:

```text
[x[t], x[t-1], ..., x[t-9], u[t], 1]
```

That is `265` features per output and **6,360 learned coefficients** overall.

It is not told which parameters correspond to geometry, long-range wiring, or delay.

On the unchanged base world it is strong: held-out normalized MSE is **0.000752**, already near the noise floor.

The factorized model has only **5 learned scalar coefficients**, but it receives the controlled operators `G` and `C` as side information. It uses two short post-change calibration episodes only to infer delay.

After each intervention the VAR may adapt all 6,360 parameters from the same calibration stream. To strengthen the attacker further, every reported VAR number uses the **best held-out score over a small ridge-regularization grid**. That is oracle-tuned regularization and therefore an intentionally favorable upper bound for the generic attacker.

## Two-episode transfer

| intervention | factorized, 2 episodes | generic VAR, 2 episodes | ratio |
|---|---:|---:|---:|
| rewire | **0.000658** | 0.026124 | 39.7× |
| warp geometry | **0.000682** | 0.007280 | 10.7× |
| delay `4→7` | **0.000637** | 0.021645 | 34.0× |
| combined | **0.000687** | 0.040708 | 59.2× |

The factorized model also identifies the correct post-change delay in every condition.

## The negative result is just as important

The VAR catches up when given enough new data.

At 16 calibration episodes its normalized MSE is:

```text
rewire    0.000884
warp      0.000958
delay7    0.000855
combined  0.000928
```

At 32 episodes it is around `0.00073–0.00078`.

So this gate does **not** say that the hierarchy can express dynamics unavailable to a generic history model. In this linear world, it cannot.

The result is narrower:

> **When the changed structural operators are known, factorization buys compositional transfer and large data efficiency. A generic history model can relearn the same dynamics, but must spend substantially more post-change data to do it.**

That is standard structured-inductive-bias territory, not a new theorem.

## The remaining cheat

The factorized model is told what `G` and `C` are after intervention.

That is useful for a mechanistic simulator, but it is not yet a thinking system discovering its own hierarchy of constraints.

The next gate therefore removes the labels. The observer should see consequences and interventions and have to infer whether a surprise came from:

```text
local geometry
long-range wiring
delay
local gain/state
input/world
```

If it cannot discover those factors from evidence more efficiently than a generic black-box model, the hierarchy remains a description supplied by us rather than an internal computational advantage.
