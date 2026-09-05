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

This is deliberately compatible with several recent results that otherwise look contradictory. Surface geometry can provide a compact smooth basis for macroscale activity; carefully constructed connectome eigenmodes can perform comparably; and smooth null bases can sometimes perform almost as well on static fMRI reconstruction. Static reconstruction alone is therefore a weak discriminator of mechanism.

The repository treats **prediction of future dynamics under perturbation** as the primary test.

## Executed gate ladder

| gate | question | result |
|---|---|---|
| **G0 — state-dependent operator** | can a state-conditioned operator be distinguished from a flat geometry+connectivity mixture? | held-out MSE **0.000280** vs flat **0.01165**; on an identical-state counterfactual the flat model predicts zero change while the hierarchy tracks the true change with correlation **>0.999999** |
| **G1 — propagation layers** | can local geometry, nonlocal wiring, and delay be separated by held-out futures rather than static reconstruction? | joint delayed NMSE **0.00127–0.00142** across base/rewire/warp/delay/combined interventions vs strongest instantaneous attacker **0.0286–0.0357**; two calibration episodes recover changed delay `4→7` |
| **G2 — generic history attacker** | is the hierarchy merely a verbose VAR with memory? | a 6,360-parameter VAR fits the unchanged world near the noise floor, but with only 2 post-change episodes its NMSE is **10.7×–59.2×** worse than the 5-parameter factorized model; by 16–32 episodes the VAR largely catches up |
| **G3A — blind layer attribution** | can constraint families be inferred from bounded scalar consequences without seeing the hidden operators? | passive evidence **42.22%**; 3 active pokes **100%** vs random-poke **72.78%** across six causes |
| **G3B — fixed-panel attacker** | does that establish a need for adaptive poking? | **no**: one learned fixed poke gives **98.33%**, two fixed pokes **100%**. Fixed perturbation addresses made G3A too easy |

CI reruns every executed gate/attacker on every PR.

## What the gates establish

Gate 0 calibrates the basic discriminator: when current state changes the effective operator, a state-blind mixture can fit ordinary data yet fail a controlled counterfactual.

Gate 1 adds explicit propagation. The model is fitted once on a base world and then faces rewiring, geometry warp, a changed delay, and all three together. The factorized `G + delayed C` description transfers across those interventions roughly 20–30× better than instantaneous or partial models.

Gate 2 attacks the result with a generic ten-lag VAR:

```text
unchanged world:
    generic VAR is excellent

small post-change budget:
    factorized model transfers far better

large post-change budget:
    generic VAR relearns and catches up
```

So the result is not that the hierarchy represents dynamics that generic history models cannot. It is:

> **Known constraint factorization buys compositional transfer and data efficiency after structural change.**

Gate 3 then removes direct access to those operators. A bounded observer sees four cheap passive residual summaries and may buy scalar addressed experiments. Six hidden causes are used: none, local geometry, long-range wiring, delay, gain, and external-input statistics.

Three adaptively chosen pokes classify all six causes perfectly in the fixed-substrate assay, while three random pokes reach only 72.78%. But that is **not the headline**. A stronger boring attacker learns a fixed diagnostic panel from the training set. One fixed probe reaches 98.33%; two reach 100%.

So G3A does establish that the cause families have distinct behavioral fingerprints, but G3B kills the claim that adaptive measurement is necessary when structural changes always occur at the same addresses.

> **If two static probes solve the world, do not build an active observer. Move the world.**

See [`GATE0.md`](GATE0.md), [`GATE1.md`](GATE1.md), [`GATE2.md`](GATE2.md), and [`GATE3.md`](GATE3.md).

## Why this starts from dynamics, not reconstruction

A 2024/2025 geometry-vs-connectome comparison found only minor differences among geometric eigenmodes, smoothed connectome eigenmodes, a local-neighborhood graph, and a heavily smoothed random null when the task was reconstruction of static fMRI maps. The methodological warning is:

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

`GeometricNeuronV24` supplied the address-selection lesson that an informative measurement may depend on **where** the hidden event lives.

`SpectralIslandsV2` supplied the intuition that several dynamically maintained mode packets can coexist without everything mixing into everything else, but its older literal holographic/ephaptic claims are not assumed here.

The synthesis under test is:

```text
constraint hierarchy
    ↓ compiles / selects
state-dependent effective operator
    ↓ supports
selectively maintained dynamical objects
    ↓ diagnosed by
bounded observer + interventions
```

## The next cheat to remove

G3A/G3B still use a fixed base substrate and fixed perturbation addresses. That is why a static diagnostic panel can win.

The next gate randomizes the **address** of local geometry/wiring/gain changes. The observer must use cheap residual evidence to infer where the surprise probably lives and then decide where/when to poke. The fixed panel attacker stays.

If active addressing does not beat a strong learned static panel once the hidden cause can move, then active measurement still has not earned architectural work.

After that, the underlying substrate itself should change across worlds.

## Claim boundary

This is not a claim that the brain is “made of eigenmodes”, that one spectral representation explains cognition, or that geometry dominates connectivity. Geometry, connectivity, delays, local nonlinearities, and input constrain different parts of the problem.

The current gates are synthetic and generated from the decompositions they test. They demonstrate a causal-testing workflow, compositional transfer from known factorization, and a clear negative result showing when adaptive diagnosis is unnecessary. They do not establish a biological hierarchy.

**Attackers first, claims second.**
