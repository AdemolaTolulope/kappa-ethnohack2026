"""RDKit validation and deterministic molecular feature generation."""
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors, AllChem, rdFingerprintGenerator
import numpy as np

FPGEN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=512)

def molecule(smiles):
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None: return None
    return Chem.RemoveHs(mol)

def descriptors(smiles):
    mol = molecule(smiles)
    if mol is None: return None
    return {
        'canonical_smiles': Chem.MolToSmiles(mol, canonical=True),
        'formula': rdMolDescriptors.CalcMolFormula(mol),
        'mw': round(Descriptors.MolWt(mol), 3),
        'logp': round(Crippen.MolLogP(mol), 3),
        'tpsa': round(rdMolDescriptors.CalcTPSA(mol), 3),
        'hbd': int(Lipinski.NumHDonors(mol)), 'hba': int(Lipinski.NumHAcceptors(mol)),
        'rotatable_bonds': int(Lipinski.NumRotatableBonds(mol)),
        'fraction_csp3': round(rdMolDescriptors.CalcFractionCSP3(mol), 3),
    }

def fingerprint(smiles):
    mol=molecule(smiles)
    if mol is None: return None
    return np.asarray(FPGEN.GetFingerprintAsNumPy(mol), dtype=np.uint8)

def feature_vector(smiles):
    d=descriptors(smiles)
    if d is None: return None
    fp=fingerprint(smiles)
    vals=[d[k] for k in ('mw','logp','tpsa','hbd','hba','rotatable_bonds','fraction_csp3')]
    return np.concatenate((np.asarray(vals,dtype=float),fp.astype(float)))

def scaffold(smiles):
    from rdkit.Chem.Scaffolds import MurckoScaffold
    mol=molecule(smiles)
    if mol is None:return ''
    return MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False) or '__acyclic__'
