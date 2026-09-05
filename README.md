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
| **G3E — hard delta budget** | once current-world deltas transfer, do we need adaptive measurement selection? | **not yet**: at 8 post-change scalars greedy static reaches **72.50%** joint cause+address vs active-joint **62.50%**, active-address **54.44%**, random **50.83%**; full 168-panel = **100%** |
| **G3F — stale baseline memory** | does remembered baseline evidence actually save measurements under slow substrate drift? | **yes, narrowly**: refresh-every gives **71.67%** at 16 calls/incident; periodic-4 gives **70.56%** at **10 calls/incident**; frozen decays to **52.78%**; one-sentinel refresh gets only **57.22%** at 9.94 calls/incident |
| **G3G — sparse expectation cache** | if the useful baseline set is larger than memory, does sophisticated consolidation help? | LRU preserves **73.06%** joint accuracy vs no-cache **74.44%** while reducing calls **16.00→10.67/incident**; future-use oracle = **10.17**; random = **11.05**; lifetime-frequency over-consolidates after a regime switch |
| **G3H — variable drift + sparse cache** | when both demand and the world change, does surprise-driven refresh beat a clock? | **not by the preregistered efficiency criterion**: residual-2 reaches **72.92%** at 12.23 calls/incident and only 3 stale uses, but TTL-4 has the best boring calls/correct (**16.35** vs residual **16.78**); residual nearly matches the hidden-phase oracle (**73.75%**) |

CI reruns every executed gate/attacker on every PR.

## What survived the attackers

G0–G2 establish a modest, standard structured-inductive-bias result: **known factorization buys compositional transfer and data efficiency after structural change**. A generic history model can represent the dynamics but needs more post-change evidence to relearn them.

G3 asks whether the factors can be discovered rather than handed to the model. G3A initially looked impressive, but G3B supplied the important negative: when each cause always lives at the same address, a tiny learned fixed panel solves the problem. So adaptivity had not earned architectural work.

G3C moves the hidden event. That separates “what happened?” from “where did it happen?” Coarse cause-family diagnosis remains mostly cheap/fixed, but sequential paid outcomes improve exact localization.

G3D changes the substrate across worlds. The coordinate atlas fails, but a much simpler representation wins: remember what the current world normally does and subtract it. Shared `after-before` delta templates reach **99.17%** joint accuracy with the full panel, and random coordinate relabeling barely matters.

G3E restores a severe post-change budget and attacks the active observer. A learned static eight-probe cover beats two plausible adaptive policies. At eight measurements the current locked CI result is static **72.50%**, active-joint **62.50%**, active-address **54.44%**, random **50.83%**. The active-joint policy still identifies the cause family well but under-covers physical space.

> **Before building an adaptive diagnostic policy, learn the best static measurement cover.**

G3F makes the remembered baseline costly and stale. Thirty held-out substrates undergo 12 reversible incidents while their healthy operator drifts slowly. Reacquiring the eight healthy baseline measurements every incident costs 16 total scalar calls/incident and gives **71.67%** joint diagnosis. Refreshing the stored baseline only every four incidents gives **70.56%** at **10 calls/incident** — **98.45% of the reference accuracy with 37.5% fewer total calls**.

Frozen memory is not enough: it falls to **52.78%** overall and reaches only **20%** accuracy by incident 10. Memory therefore earns a narrow role because its timescale sits between fast incidents and slower substrate drift. The one-sentinel adaptive-looking attacker loses too: **57.22%** at essentially the same budget as periodic refresh.

> **For this assay, memory pays rent; active memory management does not.**

G3G removes the free initial memory and gives the observer an **empty 12-slot cache** facing **32 useful expectations** across four diagnostic contexts. No cache buys 16 scalar measurements per incident and gets **74.44%** joint accuracy. LRU gets **73.06%** at **10.67 calls/incident**, while the future-use oracle only improves that to **10.17**. Random eviction is also strong at **11.05**.

Lifetime-frequency retention exposes over-consolidation: its healthy-baseline misses rise **1,680→2,400** after the regime switch, while LRU stays **960→960**.

> **Before teaching memory what is important, attack it with recency and random eviction.**

G3H combines changing demand with a hidden stable → rapid-drift → stable substrate. This finally breaks plain LRU: it records **164 stale uses** and drops from **72.92%** in the first stable epoch to **60.83%** during the drift burst.

Two distributed residual checks repair most of that. Residual-2 triggers 69 refreshes, leaves only **3 stale uses**, reaches **70.00%** during the burst and **72.92%** overall. That is only **0.83 points** below an unfair policy that knows the hidden drift phase, and residual-2 even uses fewer calls (**12.23 vs 12.67/incident**).

But the stronger architectural claim still fails. TTL-4 gets **69.31%** at **11.33 calls/incident** and the best boring efficiency, **16.35 calls per correct diagnosis**, versus residual-2 **16.78**. Residual buys **3.61 points** more accuracy for **7.94%** more total calls. It is a useful Pareto option, not a demonstrated necessity.

> **Prediction error can detect stale memory; it has not yet beaten a cheap age rule strongly enough to deserve architectural privilege.**

The surviving mechanism is now concrete:

```text
slow substrate / task regime
        ↓
medium cache of expected consequences
        ↓
fast current consequence
        ↓
Δ = current - expected
        ↓
small static measurement cover
        ↓
diagnosis
```

The cache needs two boring bookkeeping quantities before anything fancier: **reuse** and **age**. Residual surprise is useful when accuracy matters enough to pay for checking validity.

See [`GATE0.md`](GATE0.md), [`GATE1.md`](GATE1.md), [`GATE2.md`](GATE2.md), [`GATE3.md`](GATE3.md), [`GATE3C.md`](GATE3C.md), [`GATE3D.md`](GATE3D.md), [`GATE3E.md`](GATE3E.md), [`GATE3F.md`](GATE3F.md), [`GATE3G.md`](GATE3G.md), and [`GATE3H.md`](GATE3H.md).

## Connection to the recent repos

`Operaattori` supplied **structure compiles an operator**. `OutoSynapsi` showed that sparse scalar consequences can identify an effective operator family. `AlternativeNeuron` supplied active poking and intervention-conditioned identity. `GeometricNeuronV24` supplied the address-selection and persistent-memory lessons.

The strongest surviving piece from that family is now much less exotic: **expected consequences are reusable measurements**. Medium-timescale state is useful when storing a consequence now avoids buying the same evidence later. That is closer to calibration, caching, and black-box diagnosis than to a new neuron theory.

## Next: leave the toy world

G3H is a good stopping boundary for synthetic cache-policy invention. We have already attacked static vs active measurement, free vs stale baseline memory, cache capacity, demand shift, and variable drift. Another synthetic retention heuristic would mostly tune this world.

The next useful test should move the mechanism into a real black-box diagnostic workload:

```text
real system / validation workload
        ↓
small reversible intervention panel
        ↓
cache expected healthy scalar outcomes
        ↓
incident / model / data change
        ↓
measure only what must be repurchased
        ↓
localize or repair the regression
```

`LentoOrava` / PulseTriage is the obvious bridge because it already turns addressed reversible rollbacks plus one expensive scalar KPI into sparse fault localization. The question is now practical: **can cached calibration outcomes cut repeated PulseTriage validation calls across successive regressions without materially reducing recovered KPI?**

If the answer is no, stop carrying the memory layer into the product. If yes, we have an actual feature rather than another neuron metaphor.

## Claim boundary

This is not a claim that the brain is “made of eigenmodes”, that geometry dominates connectivity, that active sensing is generally unnecessary, that recency is a universal memory law, or that a new theory of consolidation has been discovered. The gates are synthetic and generated from the decompositions they test. Their value is the causal-testing workflow and the repeated removal of machinery that stronger attackers make unnecessary.

**Attackers first, claims second.**
