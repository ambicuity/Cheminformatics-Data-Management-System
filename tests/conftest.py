import pytest
from app import create_app, db
from app.models.compound import Compound

@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def sample_compound():
    """Sample compound data for testing."""
    return {
        'name': 'Ethanol',
        'smiles': 'CCO'
    }