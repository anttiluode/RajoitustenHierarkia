# RajoitustenHierarkia

**Hierarchy of constraints for thinking systems.**

This repository asks a narrower question than “does geometry or connectivity matter more?”

> **Which constraints act first, which act later, and which one actually selects the dynamics that appear?**

Working hierarchy:

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

Static reconstruction is treated as a weak mechanistic test. The primary assay is **prediction and diagnosis under intervention**.

## Executed gate ladder

| gate | question | result |
|---|---|---|
| **G0 — state-dependent operator** | can a state-conditioned operator be distinguished from a flat geometry+connectivity mixture? | held-out MSE **0.000280** vs flat **0.01165**; identical-state counterfactual correlation **>0.999999** for the hierarchy while the flat model predicts zero change |
| **G1 — propagation layers** | can local geometry, nonlocal wiring, and delay be separated by held-out futures? | joint delayed NMSE **0.00127–0.00142** vs strongest instantaneous attacker **0.0286–0.0357**; two calibration episodes recover changed delay `4→7` |
| **G2 — generic history attacker** | is the hierarchy merely a verbose VAR with memory? | a 6,360-parameter VAR catches up with enough data, but at two post-change episodes its NMSE is **10.7×–59.2×** worse than the 5-parameter factorized model |
| **G3A — blind attribution** | can hidden constraint families be inferred from bounded scalar consequences? | passive **42.22%**; 3 adaptive pokes **100%** vs random **72.78%** |
| **G3B — fixed-panel attacker** | does G3A establish a need for adaptivity? | **no**: one learned fixed poke gives **98.33%**, two give **100%**; fixed event addresses made G3A too easy |
| **G3C — moving address** | what if local changes can occur at any of 24 nodes? | at 3 pokes, cause label active=fixed **83.61%**, but joint cause+exact-address is active **66.39%** vs coarse-bin fixed **59.44%**, global fixed **57.22%**, random **49.17%** |
| **G3D — unseen substrates** | does an invariant “causal address” survive different transport/wiring worlds? | with the full 168-measurement panel, absolute literal atlas collapses to **5.00%** joint accuracy, but simple current-world `after-before` delta reaches **99.17%** with a shared template and **98.33%** after random coordinate relabeling |

CI reruns every executed gate/attacker on every PR.

## What survived the attackers

G0–G2 establish a modest, standard structured-inductive-bias result: **known factorization buys compositional transfer and data efficiency after structural change**. A generic history model can represent the dynamics but needs more post-change evidence to relearn them.

G3 asks whether the factors can be discovered rather than handed to the model. G3A initially looked impressive, but G3B supplied the important negative: when each cause always lives at the same address, a tiny learned fixed panel solves the problem. So adaptivity had not earned architectural work.

G3C moves the hidden event. That separates “what happened?” from “where did it happen?” Coarse cause-family diagnosis remains mostly cheap/fixed, but sequential paid outcomes improve exact localization.

G3D then changes the entire substrate across worlds. The coordinate atlas fails exactly as it should, but the anticipated fancy replacement also loses its claim to necessity. Remembering the current world's baseline and subtracting it almost solves the full-panel task:

```text
what this world normally does
        ↓
what it does now
        ↓
Δ consequence = now - baseline
        ↓
shared change signature
```

On 30 unseen substrates / 360 events, shared delta templates reach **99.17%** joint cause+address accuracy. Consistent random node relabeling barely matters (**98.33%**). Extra normalization is slightly worse.

> **For this assay, the invariant address is not a new ontology. It is a change relative to the current world's remembered behavior.**

That is differential change detection, not a new theorem. It is still a useful architectural clue because it says what medium memory should store: not a universal atlas, but local expectations for the current substrate.

See [`GATE0.md`](GATE0.md), [`GATE1.md`](GATE1.md), [`GATE2.md`](GATE2.md), [`GATE3.md`](GATE3.md), [`GATE3C.md`](GATE3C.md), and [`GATE3D.md`](GATE3D.md).

## Connection to the recent repos

`Operaattori` supplied **structure compiles an operator**. `OutoSynapsi` showed that sparse scalar consequences can identify an effective operator family. `AlternativeNeuron` supplied active poking and intervention-conditioned identity. `GeometricNeuronV24` supplied the address-selection lesson. G3D narrows all of that: before inventing a rich “causal address”, subtract the remembered baseline of the current world and see what remains.

The synthesis currently under test is:

```text
slow substrate / operator
        ↓
remembered expected consequences
        ↓
cheap residual
        ↓
where is uncertainty still high?
        ↓
paid intervention
        ↓
update belief / memory
```

## The next cheat to remove

G3D uses **all 168 post-change scalar measurements**. That is not a bounded observer.

The next gate should keep the cross-substrate current-world delta representation but restore a severe measurement budget. Compare adaptive selection against strong fixed, coarse-routed, and random delta panels on unseen substrates.

If a tiny static delta panel solves the task, active diagnosis loses again. If adaptive selection wins only for exact localization, preserve that narrower boundary rather than inflating it into a general intelligence claim.

## Claim boundary

This is not a claim that the brain is “made of eigenmodes”, that geometry dominates connectivity, or that a new universal causal-address mathematics has been discovered. The gates are synthetic and generated from the decompositions they test. Their value is the causal-testing workflow and the repeated removal of unnecessary machinery.

**Attackers first, claims second.**
