"""RDKit molecular descriptors computed from a SMILES string."""

from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors


class InvalidSMILESError(ValueError):
    """Raised when a SMILES string cannot be parsed into a molecule."""

def parse_smiles(smiles: str) -> Chem.Mol:
    """Parse a SMILES string, raising InvalidSmilesError if it is not valid."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise InvalidSMILESError(f"Could not parse SMILES string: {smiles!r}")
    return mol

def compute_descriptors(smiles: str) -> dict:
    """Compute the seven core molecular descriptors used throughout the project."""
    mol = parse_smiles(smiles)
    return {
        "molecular_weight": Descriptors.MolWt(mol),
        "logp": Crippen.MolLogP(mol),
        "h_bond_donors": float(Lipinski.NumHDonors(mol)),
        "h_bond_acceptors": float(Lipinski.NumHAcceptors(mol)),
        "tpsa": rdMolDescriptors.CalcTPSA(mol),
        "rotatable_bonds": float(rdMolDescriptors.CalcNumRotatableBonds(mol)),
        "aromatic_rings": float(Descriptors.NumAromaticRings(mol)),
    }

def canonical_smiles(smiles: str) -> str:
    """Return RDKit's canonical form, so the same molecule always has one spelling."""
    return Chem.MolToSmiles(parse_smiles(smiles))