import pytest
from app.utils.chem_utils import ChemUtils

class TestChemUtils:
    """Test chemical utility functions."""
    
    def test_validate_smiles_valid(self):
        """Test SMILES validation with valid molecules."""
        assert ChemUtils.validate_smiles('CCO') == True
        assert ChemUtils.validate_smiles('c1ccccc1') == True
        assert ChemUtils.validate_smiles('CC(=O)OC1=CC=CC=C1C(=O)O') == True
    
    def test_validate_smiles_invalid(self):
        """Test SMILES validation with invalid molecules."""
        assert ChemUtils.validate_smiles('') == False
        assert ChemUtils.validate_smiles('XYZ') == False
        assert ChemUtils.validate_smiles('C(C(C') == False
    
    def test_canonicalize_smiles(self):
        """Test SMILES canonicalization."""
        # Test that benzene variations return the same canonical form
        canonical1 = ChemUtils.canonicalize_smiles('c1ccccc1')
        canonical2 = ChemUtils.canonicalize_smiles('C1=CC=CC=C1')
        
        assert canonical1 is not None
        assert canonical2 is not None
        assert canonical1 == canonical2
    
    def test_canonicalize_smiles_invalid(self):
        """Test canonicalization with invalid SMILES."""
        assert ChemUtils.canonicalize_smiles('XYZ') is None
        assert ChemUtils.canonicalize_smiles('') is None
    
    def test_calculate_properties_ethanol(self):
        """Test property calculation for ethanol (CCO)."""
        properties = ChemUtils.calculate_properties('CCO')
        
        assert properties is not None
        assert properties['molecular_formula'] == 'C2H6O'
        assert abs(properties['molecular_weight'] - 46.069) < 0.01
        assert properties['hbd'] == 1  # One OH group
        assert properties['hba'] == 1  # One oxygen
        assert properties['rotatable_bonds'] == 1  # C-C bond
    
    def test_calculate_properties_benzene(self):
        """Test property calculation for benzene."""
        properties = ChemUtils.calculate_properties('c1ccccc1')
        
        assert properties is not None
        assert properties['molecular_formula'] == 'C6H6'
        assert abs(properties['molecular_weight'] - 78.114) < 0.01
        assert properties['hbd'] == 0  # No hydrogen bond donors
        assert properties['hba'] == 0  # No hydrogen bond acceptors
        assert properties['rotatable_bonds'] == 0  # Rigid ring
    
    def test_calculate_properties_invalid(self):
        """Test property calculation with invalid SMILES."""
        assert ChemUtils.calculate_properties('XYZ') is None
        assert ChemUtils.calculate_properties('') is None
    
    def test_calculate_similarity_identical(self):
        """Test similarity calculation for identical molecules."""
        similarity = ChemUtils.calculate_similarity('CCO', 'CCO')
        assert similarity == 1.0
    
    def test_calculate_similarity_different(self):
        """Test similarity calculation for different molecules."""
        similarity = ChemUtils.calculate_similarity('CCO', 'c1ccccc1')
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.5  # Should be quite different
    
    def test_calculate_similarity_similar(self):
        """Test similarity calculation for similar molecules."""
        similarity = ChemUtils.calculate_similarity('CCO', 'CCCO')  # Ethanol vs Propanol
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should be fairly similar
    
    def test_calculate_similarity_invalid(self):
        """Test similarity calculation with invalid SMILES."""
        assert ChemUtils.calculate_similarity('XYZ', 'CCO') == 0.0
        assert ChemUtils.calculate_similarity('CCO', 'XYZ') == 0.0
        assert ChemUtils.calculate_similarity('XYZ', 'ABC') == 0.0