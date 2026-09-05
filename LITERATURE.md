# Literature anchor — why static reconstruction is not enough

The immediate trigger for this repository is the geometry/connectome reconstruction dispute around cortical eigenmodes.

## Olsen et al. / Pang / Mansour / Zalesky / Behjat / Van De Ville

**On Reconstruction of Cortical Functional Maps Using Subject-Specific Geometric and Connectome Eigenmodes**

bioRxiv 2024 preprint: `10.1101/2024.10.28.620635`.

The paper compares eigenbases derived from:

- cortical surface geometry;
- subject-specific and group structural connectomes;
- a local-neighborhood graph;
- surface-smoothed random noise.

Its key methodological result is awkward in a useful way: at modest smoothing and density, reconstruction of static task and resting-state fMRI maps differs only slightly among several of these bases. Subject-specific connectome eigenmodes do not gain the expected advantage; highly smoothed null bases and a local-neighborhood graph can perform comparably to geometry and smoothed connectomes.

The authors therefore warn that their reconstruction framework favors **spatially smooth eigenmodes**. In their own conclusion, geometry, connectomes, a smoothed null basis, and a local-neighborhood graph show little difference in reconstruction accuracy, motivating alternative methods that isolate contributions of individual eigenmodes or spectral bands.

This repository takes that as a design constraint:

> **Do not infer mechanism from static reconstruction quality when smooth bases are hard to distinguish. Use interventions and future dynamics.**

A model here must predict consequences of controlled changes to geometry, long-range wiring, delay, local state, or input.

## Related older connectome result

Wang, Owen, Mukherjee & Raj (2017), *Brain network eigenmodes provide a robust and compact representation of the structural connectome in health and disease*, PLoS Computational Biology 13(6): e1005550.

That work uses a graph-Laplacian diffusion model on tractography-derived connectivity. Its slow eigenmodes are reproducible across healthy subjects and some parcellations, while the paper explicitly limits the diffusion approximation to slow macroscopic dynamics and notes that higher-frequency behavior requires richer models including cortical processing and axonal conduction delays.

That limitation is useful here: it suggests a hierarchy of operators rather than one universal eigenbasis.

## Working synthesis, not a literature claim

The project hypothesis is:

```text
geometry        constrains available spatial modes
connectivity    constrains nonlocal coupling
signal delay    constrains phase / propagation
local state     changes effective gain and stability
input/task      selects what is expressed now
```

The literature above motivates testing this hierarchy; it does not establish it.
