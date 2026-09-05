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
| **G2 — generic history attacker** | is the hierarchy merely a verbose VAR with memory? | a 6,360-parameter VAR fits the unchanged world near the noise floor, but with only 2 post-change episodes its NMSE is **10.7×–59.2×** worse than the 5-parameter factorized model; by 16–32 episodes the VAR largely catches up |

CI reruns all executed gates on every PR.

## What the first three gates actually establish

Gate 0 calibrates the basic discriminator: when current state changes the effective operator, a state-blind mixture can fit ordinary data yet fail a controlled counterfactual.

Gate 1 adds explicit propagation. The model is fitted once on a base world and then faces rewiring, geometry warp, a changed delay, and all three together. The factorized `G + delayed C` description transfers across those interventions roughly 20–30× better than instantaneous or partial models.

Gate 2 attacks the result with a generic ten-lag VAR. This is the important boundary:

```text
unchanged world:
    generic VAR is excellent

small post-change budget:
    factorized model transfers far better

large post-change budget:
    generic VAR relearns and catches up
```

So the present result is **not** that the hierarchy expresses dynamics a generic history model cannot represent.

It is:

> **Known constraint factorization buys compositional transfer and data efficiency after structural change.**

That is useful, but it is structured-inductive-bias territory rather than a new theorem.

See [`GATE0.md`](GATE0.md), [`GATE1.md`](GATE1.md), and [`GATE2.md`](GATE2.md).

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

The synthesis being tested is:

```text
constraint hierarchy
    ↓ compiles / selects
state-dependent effective operator
    ↓ supports
selectively maintained dynamical objects
    ↓ probed by
bounded active observer
```

## The remaining cheat

The factorized Gate-2 model is handed the changed `G` and `C` after intervention. That is legitimate side information for a mechanistic simulator, but not yet an internal discovery made by a thinking system.

The next gate therefore removes those semantic labels. The observer should see trajectories and sparse intervention consequences and infer whether a surprise is best explained by changed local geometry, long-range wiring, delay, local gain/state, or external input.

If that cannot be done more efficiently than generic black-box relearning, then “hierarchy of constraints” remains our description of the world rather than an architectural advantage for the machine.

## Claim boundary

This is not a claim that the brain is “made of eigenmodes”, that one spectral representation explains cognition, or that geometry dominates connectivity. Geometry, connectivity, delays, local nonlinearities, and input all constrain different parts of the problem.

The current gates are synthetic and generated from the decompositions they test. They demonstrate a causal-testing workflow and a data-efficiency benefit when structural factors are known. They do not establish a biological hierarchy.

**Attackers first, claims second.**
