# Drug-Disease Simulation System

> 🚧 **Work in progress** — being rebuilt from scratch. See [PLAN.md](PLAN.md) for the roadmap.

An in-silico screening tool that helps drug scientists prioritise new compounds before
lab synthesis. Given a candidate molecule and a disease target, it estimates drug-likeness,
novelty, target potency (with uncertainty), ADMET properties, and runs a PK/PD
virtual-patient simulation — with atom-level insights into which parts of the molecule
help or hurt.

**Validation-first:** the tool is verified on approved drugs for treatable diseases before
being applied to novel compounds for incurable ones (see the verification ladder in PLAN.md).

## Status
| Phase | State |
|---|---|
| 0 · Skeleton + deployment | 🔨 in progress |

## Background
v1 was a university group project in which I built the Python ML backend. v2 is a solo
rebuild that replaces v1's formula-generated labels with real bioactivity data, adds
scaffold-split evaluation, uncertainty estimation, and a full deployment pipeline.

## Disclaimer
Research and educational tool. Simulations are model-based estimates, not medical advice
or a substitute for experimental validation.