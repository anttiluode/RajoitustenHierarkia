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

## Gate 0 — can a hierarchy be distinguished from a flat mixture?

We begin with a synthetic system where four layers are separately controllable:

1. **Geometry** sets a spatial Laplacian and therefore the available low-order modes.
2. **Connectivity** adds long-range directed couplings and propagation delays.
3. **Local state** adds nonlinear gain/adaptation that can stabilize only a subset of those modes.
4. **Input** selects which currently admissible mode is driven.

The first gate must compare these models on held-out perturbations:

- geometry only;
- connectivity only;
- geometry + connectivity as a flat additive predictor;
- full hierarchy with state-dependent selection;
- smooth low-frequency null basis;
- oracle simulator.

Metrics:

- next-state prediction error;
- wave direction / arrival latency;
- attractor or metastable-state identity;
- return time after perturbation;
- held-out response to an intervention;
- robustness when one layer is changed while the others are fixed.

**Kill condition:** if the flat mixture predicts held-out interventions as well as the hierarchy, there is no reason to claim a hierarchy.

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

## Claim boundary

This is not a claim that the brain is “made of eigenmodes”, that one spectral representation explains cognition, or that geometry dominates connectivity. Geometry, connectivity, delays, local nonlinearities, and input all constrain different parts of the problem.

The point of the repository is to discover when that ordering is genuinely necessary and when a simpler flat model is enough.

**Attackers first, claims second.**
