"""Sanity-check the local environment: Python, PyTorch + CUDA, RDKit, ddss package."""
import sys

import torch
from rdkit import Chem
from rdkit.Chem import Descriptors

import ddss

print(f"Python       : {sys.version.split()[0]}")
print(f"PyTorch      : {torch.__version__}")
print(f"ddss         : {ddss.__version__}")
print(f"CUDA avail.  : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU          : {torch.cuda.get_device_name(0)}")
    props = torch.cuda.get_device_properties(0)
    print(f"VRAM         : {props.total_memory / 1024 ** 3:.1f} GB")
    a = torch.randn(2048, 2048, device="cuda")
    b = a @ a
    torch.cuda.synchronize()
    print(f"GPU matmul   : OK ({b.shape[0]}x{b.shape[1]})")

aspirin =  Chem.MolFromSmiles("CC(=O)OC1=CC=CC=C1C(=O)O")
print(f"RDKit      : aspirin mol weight = {Descriptors.MolWt(aspirin):.2f} (expected 180.16)")