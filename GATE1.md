# Gate 1 — geometry, wiring, and delay predict different futures

Gate 0 showed the basic discriminator in a state-dependent toy. Gate 1 adds time explicitly.

The synthetic world is

```text
x[t+1] = 0.15 x[t]
       + 0.55 G x[t]
       + 0.25 C x[t-d]
       + 0.90 u[t]
       + noise
```

where `G` is a local ring-propagation operator, `C` is a directed long-range operator, `d` is a conduction delay, and `u` is a sparse external pulse.

The base training world uses `d=4`. After fitting once, the same coefficients are reused after controlled interventions to geometry, wiring, and delay.

## Models

| model | mechanism available |
|---|---|
| geometry | present state + `Gx` + input |
| connectivity | present state + delayed `Cx` + input |
| flat instantaneous | present state + `Gx + Cx` + input, no propagation delay |
| smooth null | present state + a broad generic local smoother + input |
| joint delayed | present state + `Gx + Cx[t-d]` + input |

The connectivity-only and joint models search delay candidates `0..9` on training data. The joint model must then re-identify a changed delay from only **two calibration episodes** before each held-out evaluation.

## Learned base mechanism

True coefficients:

```text
[0.15, 0.55, 0.25, 0.90]
```

Recovered by the joint delayed model:

```text
[0.149954, 0.550153, 0.249847, 0.900062]
```

Recovered delay:

```text
true = 4
fit  = 4
```

Training MSE is `3.98e-6` for the joint model versus about `8.9e-5` for the flat instantaneous model.

## Held-out interventions

Normalized next-state MSE (lower is better):

| intervention | geometry | connectivity | flat instant | smooth null | joint delayed |
|---|---:|---:|---:|---:|---:|
| base | 0.03244 | 0.03915 | 0.03169 | 0.03870 | **0.001279** |
| rewire long-range `C` | 0.03018 | 0.03869 | 0.02935 | 0.03724 | **0.001270** |
| warp local geometry `G` | 0.03658 | 0.04214 | 0.03565 | 0.04572 | **0.001420** |
| change delay `4 → 7` | 0.02870 | 0.03826 | 0.02861 | 0.03651 | **0.001346** |
| warp + rewire + delay 7 | 0.03145 | 0.04095 | 0.03163 | 0.04186 | **0.001408** |

The two-episode calibration identified the correct delay in every condition:

```text
base      4 → 4
rewire    4 → 4
warp      4 → 4
delay7    7 → 7
combined  7 → 7
```

So, in this assay, a decomposition that preserves local geometry, nonlocal wiring, and temporal delay transfers across interventions roughly **20–30×** better than the strongest state-blind instantaneous attacker.

## What this does and does not mean

The useful result is methodological:

> **When several smooth structural descriptions can explain ordinary states, controlled changes to one constraint layer can make their future predictions diverge.**

But this world was generated from exactly the factorization being tested. The operators `G` and `C` are supplied to the models after an intervention. This is therefore still a calibration of causal factorization, not evidence that this particular hierarchy is a biological law.

The next serious attacker is a generic lagged state-space / VAR model with no semantic decomposition. If a sufficiently strong history model transfers across held-out structural interventions just as well, the words “hierarchy of constraints” are unnecessary.
