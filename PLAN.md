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
- Deployment: React/Vite → Vercel · FastAPI (Docker) → Render ·
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
| 0 | Skeleton + deployment (repo, env, stub API on Render, stub UI on Vercel, CI) | 🔨 |
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

## Deployment decisions

### API host: Render (changed 2026-10-03)
Originally planned for Hugging Face Spaces. HF now restricts Docker and Gradio Spaces to
PRO ($9/mo); only Static Spaces remain free, and those cannot run Python. Alternatives
checked: Fly.io dropped its free tier, Koyeb now requires a payment method with a $29 hold.

Render free tier chosen: Docker supported, no credit card, 750 instance-hours/month per
workspace, 512 MB RAM / 0.1 CPU, auto-deploys on push to `main`, spins down after 15 min
idle (~1 min cold start). HF Hub is still used for model storage in Phase 9 — only Spaces
became paid.

**Consequence — the 512 MB serving budget.** Phases 0–2 (RDKit, scikit-learn, XGBoost) fit
comfortably. Phase 3's ChemBERTa (~83M params, fp32) plus PyTorch does not. Plan: train in
PyTorch on the local GPU, then **export to ONNX and quantise to int8** for serving (~80 MB,
and PyTorch drops out of the deployed image entirely). The train-heavy / serve-light split
is standard production practice, so the constraint improves the design.

Note: RAAS-DOS shares the same Render workspace, so the 750 free hours are shared. Both
services sleep when idle, so this should stay within budget — worth monitoring.

## Log
- 2026-09-30 — Planning Pass 1 complete; plan approved.
- 2026-10-01 — Task 0.1 done: repo created, `.gitignore`/README/PLAN/LICENSE on `main`.
- 2026-10-01 — Task 0.2 done: `.venv` (Python 3.12), PyTorch 2.11.0+cu128 with CUDA
  verified on the RTX 3060, RDKit, `src/` layout installed as editable package `ddss`,
  pinned requirements, smoke test passing.
- 2026-10-01 — Task 0.3a done: `ddss.features.descriptors` (7 RDKit descriptors,
  `InvalidSmilesError`, canonical SMILES) + FastAPI `/health` and `/predict`; 8 tests pass.
  Local port 8001 (RAAS-DOS owns 8000).
- 2026-10-03 — Task 0.3b done: Dockerfile + .dockerignore; API live at
  https://ddss-api.onrender.com — verified in production: aspirin 180.159, caffeine 194.19,
  invalid/empty SMILES → 422 with user-safe messages, CORS preflight OK, valid TLS.