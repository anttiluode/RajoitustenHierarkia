# Gate 3 — blind layer attribution, then the fixed-panel kill

Gate 3 asked whether a bounded observer can infer **which constraint family changed** without being handed the hidden operators.

## 3A — the encouraging result

The synthetic world contains six latent causes:

- no structural change;
- local geometry / transport change;
- directed long-range wiring change;
- propagation-delay change;
- recurrent gain change;
- external-input statistics change.

The observer receives four cheap passive residual statistics. It may then buy scalar reversible experiments of the form

```text
(poke node, read time) -> |observed consequence - remembered baseline consequence|
```

There are 24 nodes x 8 read times = **192** candidate scalar experiments.

The observer is not given `G`, `C`, delay, gain, or a changed transition matrix. A training bank supplies empirical consequence distributions for the six cause labels. At test time an active policy selects each next poke by posterior-weighted expected class separation.

Executed seed 17, 240 training samples and 360 held-out samples:

| paid pokes | passive/active accuracy | random-poke accuracy |
|---:|---:|---:|
| 0 | 42.22% | 42.22% |
| 1 | 66.11% | 58.89% |
| 2 | 81.39% | 67.78% |
| 3 | **100.00%** | **72.78%** |
| 4 | 100.00% | 76.67% |
| 8 | 100.00% | 85.56% |

At three active pokes every cause class is individually 100% correct in this assay.

That looked like a clean active-identification result.

## 3B — the boring attacker wins harder

The perturbation sites in 3A are fixed across samples. Therefore a much stronger attacker is obvious: learn a **fixed diagnostic panel** once and reuse it forever.

The attacker greedily selects fixed poke/read-time pairs to maximize training classification accuracy. This selection is intentionally favorable to the attacker: it uses the same training set that estimated the class likelihoods.

Executed result:

| fixed probes | selected addition | held-out accuracy |
|---:|---|---:|
| 1 | node 4 @ t=7 | **98.33%** |
| 2 | node 5 @ t=5 | **100.00%** |
| 3 | node 0 @ t=1 | 100.00% |

So a single learned fixed probe beats the one-poke active policy by more than 32 percentage points, and two fixed probes equal the three-poke adaptive result.

Classification:

```text
STATIC_PANEL_ATTACKER_COLLAPSES_ACTIVE_NECESSITY_ON_FIXED_SUBSTRATE
```

## What survives

Gate 3A still establishes that the hidden cause families are behaviorally distinguishable from scalar intervention consequences. It does **not** establish that adaptive experiment selection is needed.

The fixed-panel result tells us exactly what must change next:

> **The address of the structural change must move.**

If geometry/wiring/gain changes can occur anywhere, a fixed two-probe panel should no longer be sufficient. The observer must first use cheap evidence to infer *where* the surprise probably lives and then spend its poke budget there.

That is Gate 3C.

## Claim boundary

This entire gate uses one synthetic base topology. Cause labels are supplied in training. The system is learning an empirical diagnostic codebook, not discovering an ontology from scratch.

Gate 3C removes the fixed-address cheat. A later gate must also randomize the underlying substrate itself.

**Negative results are part of the architecture search: if two static probes solve the world, do not build an active observer.**
