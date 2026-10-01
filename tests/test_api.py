import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_returns_descriptors():
    response = client.post("/predict", json={"smiles": ASPIRIN})
    assert response.status_code == 200
    body =  response.json()
    assert body["descriptors"]["molecular_weight"] == pytest.approx(180.16, abs=0.01)
    assert body["model"] == "not trained yet"

def test_predict_reject_invalid_smiles():
    response = client.post("/predict", json={"smiles": "not a molecule"})
    assert response.status_code == 422

def test_predict_reject_empty_smiles():
    response = client.post("/predict", json={"smiles": ""})
    assert response.status_code == 422
