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

## Scope and epistemic limits (settled 2026-10-14)

What this tool does: **ranks candidate compounds against targets that have measured
bioactivity data, quantifies how much to trust each prediction, and shows the evidence
behind every claim.** It is triage for early virtual screening.

What it does NOT do, and will never claim to: predict what a novel compound does in a
human patient. Evidence that this is unsolved, not merely hard:
- 7.9% of programmes entering Phase I reach market (BIO/QLS/Informa 2011–2020, n=12,728);
  Citeline 2014–2023 puts it at 6.7%. Phase II (efficacy) is the bottleneck at ~28%.
- QSAR predictions outside the applicability domain are unreliable by construction, and
  a novel compound is out-of-domain by definition.
- FEP, the gold standard for binding affinity, achieves ~1 kcal/mol RMSE at best — a
  5-fold error in affinity — and needs a 3D complex structure.
- PBPK: only 28% of models in EMA submissions (2022–23) were considered qualified; the
  FDA treats predictions without clinical data as exploratory where disease
  pathophysiology is poorly understood. 82% of FDA / 69% of EMA uses are DDI, not efficacy.

Full citations live in `references.yaml` and render on the Methods page.

### Design rule: visual fidelity tracks evidence strength
Molecular scale (real PDB structure + computed pose) renders in 3D. Body/PK scale renders
as flat schematic compartments. Disease trajectory renders deliberately abstract and
flagged illustrative. A persuasive animation of a drug moving through a photorealistic
body is forbidden — it would assert what the science cannot support.

### Evidence classes (enforced in code)
Every output field carries a provenance tag; a value with no tag cannot reach the UI.
| Tag | Source | May claim | May not claim |
|---|---|---|---|
| MEASURED | ChEMBL / Tox21 lookup | Fact, with assay + reference | — |
| PREDICTED | model + uncertainty | Ranked estimate, σ, AD flag | Truth for out-of-domain input |
| ANALOGY | fingerprint neighbours | Known mechanism of similar measured actives, similarity stated | That similarity implies equal potency (activity cliffs) |
| STRUCTURAL | docking into known PDB | Residue-level contacts, pocket occupancy | Reliable affinity |
| RULE | Lipinski, QED, PAINS | Literature-derived flag, cited | Anything beyond the rule's scope |

## Disease tiers — VERIFIED against ChEMBL + RCSB (2026-10-14)

| Tier | Disease → target | ChEMBL ID | IC50 | All act. | Approved drugs | X-ray+ligand <2.5 Å |
|---|---|---|---|---|---|---|
| Verification | Inflammation → COX-2 | `CHEMBL230` | 8,504 | 15,314 | 11 | 5 (human) |
| Verification | Type 2 diabetes → DPP-4 | `CHEMBL284` | 5,818 | 8,397 | 13 | 63 |
| Verification | Lung cancer → EGFR | `CHEMBL203` | 26,600 | 58,847 | 16 | 151 |
| Bridge | HIV → reverse transcriptase | `CHEMBL247` | 10,993 | 19,411 | 19 | see caveat |
| Novelty | Alzheimer's → BACE1 | `CHEMBL4822` | 13,777 | 27,804 | **0** | 354 |

Positive controls (max_phase 4, from ChEMBL `/mechanism`):
- COX-2: celecoxib, etoricoxib, rofecoxib, valdecoxib, parecoxib, lumiracoxib, meloxicam,
  etodolac, nabumetone, carprofen
- DPP-4: sitagliptin, linagliptin, vildagliptin, saxagliptin, alogliptin, teneligliptin,
  anagliptin, evogliptin, gosogliptin, omarigliptin, trelagliptin
- EGFR: osimertinib, erlotinib, afatinib, dacomitinib, lapatinib, neratinib, brigatinib,
  lazertinib, olmutinib (+ antibodies: cetuximab, panitumumab, necitumumab, amivantamab —
  exclude, not small molecules)
- HIV-1 RT: efavirenz, nevirapine, rilpivirine, etravirine, doravirine, delavirdine,
  lamivudine, abacavir, emtricitabine, tenofovir (+ prodrug salts), stavudine, didanosine
- BACE1: **none** — see finding below

### Finding: data scarcity is NOT the constraint for incurable disease
BACE1 has 13,777 IC50 values and 354 crystal structures — more structural data than COX-2,
which has 11 marketed drugs. It has zero approved drugs anyway. Verubecestat,
lanabecestat and atabecestat were potent, selective, brain-penetrant BACE1 inhibitors that
engaged the target, lowered amyloid, and still failed in Phase III.

Consequence for scope: a model trained on this data will predict BACE1 potency well and
say nothing about whether a patient improves — because potency is not what failed. The
novelty tier therefore claims: *ranks BACE1 binders; makes no claim about Alzheimer's
outcome.* The clinical failure record goes on the Methods page as the justification.

### Open data caveats (resolve in Phase 1)
1. **HIV-RT structure count is wrong.** The query used UniProt `P03366`, the HIV-1 Pol
   polyprotein, which covers protease + RT + integrase in one accession. Top hit `2HS1` is
   an HIV-1 *protease* structure. The 214 count is inflated — re-query by polymer entity
   or RT-specific structures.
2. **The canonical celecoxib structure `3LN1` (2.4 Å) is MURINE COX-2, not human.** Using
   it is standard practice (conserved binding site) but is a cross-species assumption and
   must be declared in `references.yaml`, not glossed over. Human COX-2 has only 5
   structures <2.5 Å with a ligand, so this choice matters.

## Verification ladder
1. Known drugs — held-out approved drugs get correct potency/toxicity + simulated recovery
2. Actives vs decoys — enrichment factor, ROC-AUC
3. Unseen scaffolds — graceful accuracy drop; uncertainty rises
4. Novel compounds — useful ranking with honest out-of-domain warnings
A rung counts only once the rung below passes.

## Phases — vertical slices (restructured 2026-10-14)

Every phase ships capability → API endpoint → **deployed UI panel** → citations, live at
the end of the phase. There is no terminal "build the frontend" phase: the app grows a
visible, scrutinisable layer each time, so mistakes surface immediately and the project is
demonstrable at any moment. Costs ~20% more effort than back-loading the UI; worth it.

| # | Phase | Deployed panel | Sources rendered | Status |
|---|---|---|---|---|
| 0 | Skeleton + deployment | SMILES → descriptors | — | ✅ |
| 1 | Data foundation | Dataset explorer: counts, activity distributions, scaffold-split composition, held-out approved drugs | ChEMBL, MoleculeNet, Bemis–Murcko | 🔨 |
| 2 | Rules + novelty | Compound card: 2D depiction, Lipinski/QED/SA badges, nearest known drug + similarity | Lipinski 1997, QED, SA score, ECFP | ⏳ |
| 3 | Baselines + uncertainty | Prediction with error bar, AD flag, model card with scaffold-split metrics | AD literature | ⏳ |
| 4 | Deep models | Honest comparison: does the GNN/ChemBERTa beat Random Forest? | ChemBERTa, GNN refs | ⏳ |
| 5 | **Docking + 3D viewer** | **Pose overlay — candidate translucent beside reference drug's crystal pose** | Vina/GNINA, PDB entries, COX docking benchmark | ⏳ |
| 6 | Attribution | 2D structure, fragments coloured by contribution | Substructure masking, Integrated Gradients, DrugXAI | ⏳ |
| 7 | PK/PD simulation | Schematic compartments + concentration curves, parameters user-editable, flagged illustrative | PK/PD texts, PBPK limits | ⏳ |
| 8 | **Verification ladder** ⭐ | Live validation page: all 4 rungs, pass/fail, re-run on every deploy | own measured results | ⏳ |
| 9 | Batch screening | CSV upload → ranked shortlist | — | ⏳ |
| 10 | Database | Saved runs, prediction logging (Supabase) | — | ⏳ |
| 11 | MLOps | MLflow, model registry, drift monitoring | — | ⏳ |
| 12 | Polish | Methods page, architecture diagram, demo video | full bibliography | ⏳ |
| ⭐ | Stretch | analogue generation; docking for data-poor targets | — | — |

Docking moved from Phase 7 → 5 so poses are visible during development, not at the end.
The verification ladder became its own public page: the project states in public how well
it works and where it fails.

### references.yaml — sourcing as a data structure
Every method carries its citation as data. The API returns a citation key with each
computed field; the UI renders it beside the number. **A claim that cannot name its source
cannot reach the screen** — enforced in code, not by discipline. Each entry records: the
reference, the method's stated accuracy limit, and what it may not claim. The Methods page
is generated from this file and grows every phase.

### Signature view
Candidate's docked pose superimposed on the approved drug's **crystal** pose in the same
pocket — measured solid, computed translucent. Answers the chemist's real question (does
it sit where the known inhibitor sits, does it touch the key residue) and encodes both
confidence levels in the rendering. Doubles as validation: if the pipeline reproduces
celecoxib's own crystal pose, the method works.

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
- 2026-10-07 — Task 0.4 done: React + Vite frontend (SMILES input, descriptor table,
  user-safe errors) live at https://drug-disease-simulation-system.vercel.app —
  verified in-browser against the live API; `VITE_API_URL` confirmed baked into the
  production bundle. Vercel project name is `drug-disease-simulation-system`
  (`ddss` was taken); Root Directory set to `frontend`.

- 2026-10-08 — Task 0.5 done: GitHub Actions CI (ruff + pytest; npm ci + build) green.
  **Phase 0 complete** — walking skeleton live end to end.
- 2026-10-14 — Planning Pass 2: feasibility assessment (see Scope and epistemic limits);
  scope reframed from "predict patient outcome" to validated prioritisation with explicit
  uncertainty. Phases restructured into vertical slices. Targets verified against ChEMBL
  and RCSB. BACE1 finding recorded. Two data caveats open.
