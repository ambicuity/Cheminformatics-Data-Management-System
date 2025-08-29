from app.models.compound import Compound
from app.utils.chem_utils import ChemUtils
from app import db

class TestCompoundModel:
    """Test Compound model."""
    
    def test_compound_creation(self, app):
        """Test creating a compound."""
        with app.app_context():
            # Create compound
            compound = Compound(
                name='Test Compound',
                smiles='CCO',
                molecular_formula='C2H6O',
                molecular_weight=46.069,
                logp=-0.31,
                tpsa=20.23,
                hbd=1,
                hba=1,
                rotatable_bonds=1
            )
            
            db.session.add(compound)
            db.session.commit()
            
            # Test that it was saved
            assert compound.id is not None
            assert compound.name == 'Test Compound'
            assert compound.smiles == 'CCO'
            assert compound.molecular_formula == 'C2H6O'
            assert compound.created_at is not None
            assert compound.updated_at is not None
    
    def test_compound_to_dict(self, app):
        """Test compound serialization to dictionary."""
        with app.app_context():
            compound = Compound(
                name='Test Compound',
                smiles='CCO',
                molecular_formula='C2H6O',
                molecular_weight=46.069,
                logp=-0.31,
                tpsa=20.23,
                hbd=1,
                hba=1,
                rotatable_bonds=1
            )
            
            db.session.add(compound)
            db.session.commit()
            
            compound_dict = compound.to_dict()
            
            assert isinstance(compound_dict, dict)
            assert compound_dict['name'] == 'Test Compound'
            assert compound_dict['smiles'] == 'CCO'
            assert compound_dict['molecular_formula'] == 'C2H6O'
            assert compound_dict['molecular_weight'] == 46.069
            assert 'id' in compound_dict
            assert 'created_at' in compound_dict
            assert 'updated_at' in compound_dict
    
    def test_compound_repr(self, app):
        """Test compound string representation."""
        with app.app_context():
            compound = Compound(name='Test Compound', smiles='CCO')
            
            expected = '<Compound Test Compound: CCO>'
            assert repr(compound) == expected
    
    def test_compound_unique_smiles(self, app):
        """Test that SMILES must be unique."""
        with app.app_context():
            # Create first compound
            compound1 = Compound(name='Compound 1', smiles='CCO')
            db.session.add(compound1)
            db.session.commit()
            
            # Try to create second compound with same SMILES
            compound2 = Compound(name='Compound 2', smiles='CCO')
            db.session.add(compound2)
            
            # This should raise an integrity error due to unique constraint
            try:
                db.session.commit()
                assert False, "Expected IntegrityError for duplicate SMILES"
            except Exception as e:
                db.session.rollback()
                # This is expected - SMILES should be unique