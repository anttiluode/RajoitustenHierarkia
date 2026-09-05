# RajoitustenHierarkia

**Hierarchy of constraints for thinking systems.**

This repository asks a narrower question than “does geometry or connectivity matter more?”

> **Which constraints act first, which act later, and which one actually selects the dynamics that appear?**

The working hypothesis is a hierarchy rather than a winner-take-all substrate story:

```text
physical geometry
    ↓
possible spatial modes
    ↓
connectivity + direction + delay
    ↓
which modes can interact and propagate
    ↓
local nonlinear state / gain / adaptation
    ↓
which dynamics become stable or metastable
    ↓
current input / task / intervention
    ↓
which dynamical object is expressed now
```

This is deliberately compatible with several recent results that otherwise look contradictory. Surface geometry can provide a compact smooth basis for macroscale activity; carefully constructed connectome eigenmodes can perform comparably; and smooth null bases can sometimes perform almost as well on static fMRI reconstruction. That means static reconstruction alone is a weak discriminator of mechanism.

The repository therefore treats **prediction of future dynamics under perturbation** as the primary test.

## Executed gate ladder

| gate | question | result |
|---|---|---|
| **G0 — state-dependent operator** | can a state-conditioned operator be distinguished from a flat geometry+connectivity mixture? | held-out MSE **0.000280** vs flat **0.01165**; on an identical-state counterfactual the flat model predicts zero change while the hierarchy tracks the true change with correlation **>0.999999** |
| **G1 — propagation layers** | can local geometry, nonlocal wiring, and delay be separated by held-out futures rather than static reconstruction? | joint delayed NMSE **0.00127–0.00142** across base/rewire/warp/delay/combined interventions vs strongest instantaneous attacker **0.0286–0.0357**; two calibration episodes recover changed delay `4→7` |

CI reruns all executed gates on every PR.

## Gate 0 — state changes the effective operator

The calibration world is

```text
y = tanh(0.72 Gx + 0.48 q C x_prev + 0.35 u + noise)
```

where `G` is local geometry, `C` is directed nonlocal coupling, and `q` changes how strongly the long-range operator is expressed.

The decisive test holds `x`, `x_prev`, `G`, `C`, and input fixed while changing only `q`. The true future changes with RMS magnitude about `0.286`. A state-blind flat model predicts exactly zero counterfactual change; the state-conditioned model reproduces the change with delta MSE around `1.8e-8`.

See [`GATE0.md`](GATE0.md).

## Gate 1 — static similarity is not dynamic equivalence

Gate 1 adds explicit propagation:

```text
x[t+1] = 0.15 x[t]
       + 0.55 G x[t]
       + 0.25 C x[t-d]
       + 0.90 u[t]
       + noise
```

The model is fitted once on a base world with delay `d=4`. It then faces new geometry, rewired long-range edges, a delay changed to `7`, and all three together.

The joint delayed model recovers the generating coefficients almost exactly and keeps normalized next-state error near `0.0013–0.0014`. Geometry-only, connectivity-only, an instantaneous `G+C` model, and a broad smooth-local null all remain around `0.029–0.046` under the same held-out interventions.

More importantly, the delay is not simply handed back after it changes. Two short calibration episodes recover `4` in the original worlds and `7` after the intervention in every tested condition.

> **A controlled change to one constraint layer can separate models that ordinary smooth-state fitting leaves hard to distinguish.**

See [`GATE1.md`](GATE1.md).

## Why this starts from dynamics, not reconstruction

A 2024/2025 geometry-vs-connectome comparison found only minor differences among geometric eigenmodes, smoothed connectome eigenmodes, a local-neighborhood graph, and a heavily smoothed random null when the task was reconstruction of static fMRI maps. The important methodological warning is therefore:

> A smooth basis can reconstruct a smooth map without identifying the mechanism that generated it.

So this repo asks causal questions instead:

```text
change geometry only      → what changes?
change long-range wiring  → what changes?
change delay only         → what changes?
change gain/adaptation    → what changes?
change input only         → what changes?
```

If two models reconstruct the same map but predict different consequences of those interventions, the perturbation separates them.

See [`LITERATURE.md`](LITERATURE.md) for the immediate literature anchor.

## Connection to the recent repos

`Operaattori` supplied the language **structure compiles an operator**.

`OutoSynapsi` showed that the effective operator itself can sometimes be inferred from sparse scalar consequences.

`AlternativeNeuron` supplied active poking, causal addresses, dynamical-object identity, and the warning that state cannot always be inferred from a frozen frame.

`SpectralIslandsV2` supplied the intuition that several dynamically maintained mode packets can coexist without everything mixing into everything else, but its older literal holographic/ephaptic claims are not assumed here.

The synthesis tested here is:

```text
constraint hierarchy
    ↓ compiles / selects
state-dependent effective operator
    ↓ supports
selectively maintained dynamical objects
    ↓ probed by
bounded active observer
```

## The next attacker

Gate 1 still knows the decomposition into `G` and `C`. That is a major convenience.

The next gate therefore gives a generic lagged state-space / VAR model enough history and parameters to attack the result. If an operator-agnostic history model transfers across held-out rewiring, geometry warp, and delay changes just as well, the “hierarchy” language has not earned itself.

Only after that attack should this repo proceed to nonlinear selectively maintained dynamical islands and an `AlternativeNeuron`-style bounded observer.

## Claim boundary

This is not a claim that the brain is “made of eigenmodes”, that one spectral representation explains cognition, or that geometry dominates connectivity. Geometry, connectivity, delays, local nonlinearities, and input all constrain different parts of the problem.

Both current gates are synthetic and generated from the decompositions they are meant to test. They calibrate the causal assay; they do not establish a biological hierarchy.

**Attackers first, claims second.**
