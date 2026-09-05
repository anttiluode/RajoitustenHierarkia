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
| **G3E — hard delta budget** | once current-world deltas transfer, do we need adaptive measurement selection? | **not yet**: at 8 post-change scalars greedy static reaches **72.50%** joint cause+address vs active-joint **62.22%**, active-address **53.06%**, random **50.83%**; full 168-panel = **100%** |
| **G3F — stale baseline memory** | does remembered baseline evidence actually save measurements under slow substrate drift? | **yes, narrowly**: refresh-every gives **71.67%** at 16 calls/incident; periodic-4 gives **70.56%** at **10 calls/incident**; frozen decays to **52.78%**; one-sentinel refresh gets only **57.22%** at 9.94 calls/incident |

CI reruns every executed gate/attacker on every PR.

## What survived the attackers

G0–G2 establish a modest, standard structured-inductive-bias result: **known factorization buys compositional transfer and data efficiency after structural change**. A generic history model can represent the dynamics but needs more post-change evidence to relearn them.

G3 asks whether the factors can be discovered rather than handed to the model. G3A initially looked impressive, but G3B supplied the important negative: when each cause always lives at the same address, a tiny learned fixed panel solves the problem. So adaptivity had not earned architectural work.

G3C moves the hidden event. That separates “what happened?” from “where did it happen?” Coarse cause-family diagnosis remains mostly cheap/fixed, but sequential paid outcomes improve exact localization.

G3D changes the substrate across worlds. The coordinate atlas fails, but a much simpler representation wins: remember what the current world normally does and subtract it. Shared `after-before` delta templates reach **99.17%** joint accuracy with the full panel, and random coordinate relabeling barely matters.

G3E restores a severe post-change budget and attacks the active observer. A learned static eight-probe cover beats two plausible adaptive policies. At eight measurements: static **72.50%**, active-joint **62.22%**, active-address **53.06%**, random **50.83%**. The active-joint policy actually identifies the cause family well but under-covers physical space.

> **Before building an adaptive diagnostic policy, learn the best static measurement cover.**

G3F then makes the remembered baseline costly and stale. Thirty held-out substrates undergo 12 reversible incidents while their healthy operator drifts slowly. Reacquiring the eight healthy baseline measurements every incident costs 16 total scalar calls/incident and gives **71.67%** joint diagnosis. Refreshing the stored baseline only every four incidents gives **70.56%** at **10 calls/incident** — **98.45% of the reference accuracy with 37.5% fewer total calls**.

Frozen memory is not enough: it falls to **52.78%** overall and reaches only **20%** accuracy by incident 10. Memory therefore earns a narrow role because its timescale sits between fast incidents and slower substrate drift.

The active-looking sentinel attacker loses too. One healthy sentinel scalar per incident plus triggered full refresh costs **9.94 calls/incident**, almost identical to periodic refresh, but reaches only **57.22%**. Distributed drift is not summarized well by one sentinel.

> **For this assay, memory pays rent; active memory management does not.**

The surviving architecture is becoming simpler:

```text
slow substrate drift
        ↓
medium remembered expected consequences
        ↓
fast incident consequence
        ↓
Δ = current - expected
        ↓
small static measurement cover
        ↓
periodic recalibration when the slow timescale demands it
```

See [`GATE0.md`](GATE0.md), [`GATE1.md`](GATE1.md), [`GATE2.md`](GATE2.md), [`GATE3.md`](GATE3.md), [`GATE3C.md`](GATE3C.md), [`GATE3D.md`](GATE3D.md), [`GATE3E.md`](GATE3E.md), and [`GATE3F.md`](GATE3F.md).

## Connection to the recent repos

`Operaattori` supplied **structure compiles an operator**. `OutoSynapsi` showed that sparse scalar consequences can identify an effective operator family. `AlternativeNeuron` supplied active poking and intervention-conditioned identity. `GeometricNeuronV24` supplied the address-selection and persistent-memory lessons.

The strongest surviving piece from that family is now quite concrete: **medium-timescale expected consequences amortize repeated measurement of a slower-changing substrate**. That is much closer to calibration/cache/system-identification language than to a new neuron theory.

## The next cheat to remove

Gate 3F still begins with the complete eight-entry healthy baseline panel already populated, and the drift timescale is stationary enough that a fixed period-4 refresh works.

Gate 3G should remove the free initial memory. Let ordinary healthy interactions populate a limited cache of expected consequences. Compare simple LRU/frequency/value retention before any learned consolidation rule. A stored expectation earns its slot only when it saves future measurements.

After that, vary the drift regime so a fixed refresh period becomes wrong. Only then is there a fair reason to revisit adaptive refresh.

## Claim boundary

This is not a claim that the brain is “made of eigenmodes”, that geometry dominates connectivity, that active sensing is generally unnecessary, or that periodic refresh is a universal memory law. The gates are synthetic and generated from the decompositions they test. Their value is the causal-testing workflow and the repeated removal of machinery that stronger attackers make unnecessary.

**Attackers first, claims second.**
