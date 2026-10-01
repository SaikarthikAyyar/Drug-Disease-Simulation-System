"""Request and response shapes for the API."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    smiles: str = Field(..., min_length=1, max_length=500, examples = ["CC(=O)Oc1ccccc1C(=O)O"])

class Descriptors(BaseModel):
    molecular_weight: float
    logp: float
    h_bond_donors: float
    h_bond_acceptors: float
    tpsa: float
    rotatable_bonds: float
    aromatic_rings: float

class PredictResponse(BaseModel):
    smiles: str
    canonical_smiles: str
    descriptors: Descriptors
    model: str = Field(description="Which model produced the prediction.")

class HealthResponse(BaseModel):
    status: str
    version: str