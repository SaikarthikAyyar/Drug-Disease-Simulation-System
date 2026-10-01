import pytest

from ddss.features.descriptors import (
    InvalidSMILESError,
    canonical_smiles,
    compute_descriptors,
)

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"

def test_aspirin_descriptors_match_reference_values():
    d = compute_descriptors(ASPIRIN)
    assert d["molecular_weight"] == pytest.approx(180.16, abs=0.01)
    assert d["h_bond_donors"] == 1
    assert d["aromatic_rings"] == 1

def invalid_smiles_raises():
    with pytest.raises(InvalidSMILESError):
        compute_descriptors("not a molecule")

def test_canonical_smiles_is_spelling_independent():
    assert canonical_smiles("CCO") == canonical_smiles("OCC")

def test_invalid_raises_smiles():
    with pytest.raises(InvalidSMILESError):
        compute_descriptors("not a molecule")