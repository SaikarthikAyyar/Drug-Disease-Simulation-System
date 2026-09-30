# Drug-Disease Simulation System — Plan

Cumulative plan: append decisions and phase notes; never overwrite history.

## Objective
Help drug scientists design new compounds for currently incurable diseases by simulating
how a novel compound (not an existing drug) affects a diseased patient, and explaining how
its chemical structure drives that effect — to prioritise which compounds are worth
synthesising, reducing experimental cost.

Framing: decision support for early-stage virtual screening. It prioritises; it does not
replace lab experiments.

## Key decisions (2026-09-30)
- Framework: PyTorch (native CUDA on Windows; TF dropped native-Windows GPU after 2.10).
- Hardware: local RTX 3060 Laptop 6 GB for training; Kaggle/Colab as fallback.
- Labels come from real measured data (ChEMBL, MoleculeNet), never formulas (v1's flaw).
- Evaluation uses scaffold splits; approved drugs + close analogues are held out of training.
- Every prediction carries uncertainty and an applicability-domain flag.
- Walking skeleton: deployed end-to-end in Phase 0; each phase upgrades the live app.
- Deployment: React/Vite → Vercel · FastAPI (Docker) → Hugging Face Spaces ·
  Supabase (Phase 8) · DagsHub MLflow + HF Hub registry (Phase 9) · GitHub Actions CI.
- Batch screening (CSV → ranked shortlist) is in core scope.

## Pipeline
1. Validity & drug-likeness — Lipinski, QED, synthetic accessibility
2. Novelty — nearest approved drug + Tanimoto similarity
3. Target potency — predicted pIC50 + uncertainty + applicability domain
4. ADMET — solubility, blood-brain-barrier penetration, toxicity (Tox21)
5. Virtual patient — PK (concentration vs time) → PD (Emax on predicted potency) →
   disease progression vs untreated; toxicity caps dose
6. Insights — atom-attribution maps, reference-drug comparison, batch ranking

## Disease tiers (target IDs to be confirmed in Phase 1)
| Tier | Disease → target | Positive controls |
|---|---|---|
| Verification | Inflammation → COX-2 | celecoxib, etoricoxib |
| Verification | Type 2 diabetes → DPP-4 | sitagliptin, linagliptin |
| Verification | Lung cancer → EGFR | gefitinib, erlotinib, osimertinib |
| Bridge | HIV → reverse transcriptase | efavirenz, nevirapine |
| Novelty | Alzheimer's → BACE1 | none approved (verubecestat etc. failed trials) |

## Verification ladder
1. Known drugs — held-out approved drugs get correct potency/toxicity + simulated recovery
2. Actives vs decoys — enrichment factor, ROC-AUC
3. Unseen scaffolds — graceful accuracy drop; uncertainty rises
4. Novel compounds — useful ranking with honest out-of-domain warnings
A rung counts only once the rung below passes.

## Phases
| # | Phase | Status |
|---|---|---|
| 0 | Skeleton + deployment (repo, env, stub API on HF Spaces, stub UI on Vercel, CI) | 🔨 |
| 1 | Data — ChEMBL + MoleculeNet, standardisation, scaffold split, approved-drug holdout, decoys, DVC | ⏳ |
| 2 | Baselines + drug-likeness + novelty — fingerprints/descriptors → RF/XGBoost, MLflow | ⏳ |
| 3 | PyTorch models — MLP (port of v1), ChemBERTa fine-tune, uncertainty, applicability domain | ⏳ |
| 4 | Simulation — PK/PD virtual patient, calibrated on rung 1 | ⏳ |
| 5 | API — single + batch endpoints, validation, tests | ⏳ |
| 6 | Insights — attributions, reference comparison, ranking | ⏳ |
| 7 | Frontend — full UI incl. Validation page | ⏳ |
| 8 | Database — Supabase: saved runs, prediction logs | ⏳ |
| 9 | MLOps — DagsHub MLflow, HF Hub registry, drift monitoring | ⏳ |
| 10 | Polish — README, architecture diagram, demo video, resume bullets | ⏳ |
| ⭐ | Stretch — docking for data-poor targets; analogue generation | — |

## Working method
Planning / Implementation / Validation passes. Each phase ends with a validation pass,
including a push and a live-deployment check.

## Log
- 2026-09-30 — Planning Pass 1 complete; plan approved.