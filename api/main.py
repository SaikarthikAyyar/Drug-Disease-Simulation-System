"""FastAPI application for the Drug-Disease Simulation System."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import ddss
from api.schemas import HealthResponse, PredictRequest, PredictResponse
from ddss.features.descriptors import (
    InvalidSMILESError,
    canonical_smiles,
    compute_descriptors,
)

app = FastAPI(
    title="Drug-Disease Simulation System",
    description="In-silico screening and PK/PD simulation for candidate compounds.",
    version=ddss.__version__
)

# The frontend is served from a different origin (Vercel), so the browser needs
# permission to call this API. Phase 0 allows all origins; Task 0.4 narrows it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveliness check used by the deployment and API"""
    return HealthResponse(status="ok", version=ddss.__version__)


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    """Compute molecular descriptors for a compound.
    
    No model is trained here: this just includes real RDKit Chemistry
    """
    try:
        descriptors = compute_descriptors(request.smiles)
        canonical = canonical_smiles(request.smiles)
    except InvalidSMILESError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PredictResponse(
        smiles=request.smiles,
        canonical_smiles=canonical,
        descriptors=descriptors,
        model="not trained yet",
    )
