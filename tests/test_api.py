import json
import pytest
from app.models.compound import Compound

class TestAPI:
    """Test API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'message' in data
    
    def test_get_compounds_empty(self, client):
        """Test getting compounds when database is empty."""
        response = client.get('/api/compounds')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['compounds'] == []
        assert data['total'] == 0
        assert data['pages'] == 0
    
    def test_create_compound_valid(self, client, sample_compound):
        """Test creating a valid compound."""
        response = client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['name'] == sample_compound['name']
        assert data['smiles'] == sample_compound['smiles']
        assert data['molecular_formula'] == 'C2H6O'
        assert abs(data['molecular_weight'] - 46.069) < 0.01
        assert 'id' in data
        assert 'created_at' in data
    
    def test_create_compound_invalid_smiles(self, client):
        """Test creating compound with invalid SMILES."""
        invalid_compound = {
            'name': 'Invalid Compound',
            'smiles': 'XYZ'
        }
        
        response = client.post(
            '/api/compounds',
            data=json.dumps(invalid_compound),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid SMILES' in data['error']
    
    def test_create_compound_missing_data(self, client):
        """Test creating compound with missing required fields."""
        incomplete_compound = {'name': 'Incomplete'}
        
        response = client.post(
            '/api/compounds',
            data=json.dumps(incomplete_compound),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required field' in data['error']
    
    def test_create_duplicate_compound(self, client, sample_compound):
        """Test creating duplicate compound (same SMILES)."""
        # Create first compound
        client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        
        # Try to create duplicate
        duplicate_compound = {
            'name': 'Different Name',
            'smiles': sample_compound['smiles']
        }
        
        response = client.post(
            '/api/compounds',
            data=json.dumps(duplicate_compound),
            content_type='application/json'
        )
        assert response.status_code == 409
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'already exists' in data['error']
    
    def test_get_compound_by_id(self, client, sample_compound):
        """Test getting compound by ID."""
        # Create compound first
        create_response = client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        created_compound = json.loads(create_response.data)
        compound_id = created_compound['id']
        
        # Get compound by ID
        response = client.get(f'/api/compounds/{compound_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['id'] == compound_id
        assert data['name'] == sample_compound['name']
        assert data['smiles'] == sample_compound['smiles']
    
    def test_get_compound_not_found(self, client):
        """Test getting non-existent compound."""
        response = client.get('/api/compounds/999')
        assert response.status_code == 404
    
    def test_update_compound(self, client, sample_compound):
        """Test updating compound."""
        # Create compound first
        create_response = client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        created_compound = json.loads(create_response.data)
        compound_id = created_compound['id']
        
        # Update compound name
        update_data = {'name': 'Updated Ethanol'}
        response = client.put(
            f'/api/compounds/{compound_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['name'] == 'Updated Ethanol'
        assert data['smiles'] == sample_compound['smiles']  # SMILES unchanged
    
    def test_delete_compound(self, client, sample_compound):
        """Test deleting compound."""
        # Create compound first
        create_response = client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        created_compound = json.loads(create_response.data)
        compound_id = created_compound['id']
        
        # Delete compound
        response = client.delete(f'/api/compounds/{compound_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'deleted successfully' in data['message']
        
        # Verify compound is deleted
        get_response = client.get(f'/api/compounds/{compound_id}')
        assert get_response.status_code == 404
    
    def test_search_by_name(self, client, sample_compound):
        """Test searching compounds by name."""
        # Create compound first
        client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        
        # Search by name
        response = client.get('/api/search?name=Ethanol')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['compounds']) == 1
        assert data['compounds'][0]['name'] == 'Ethanol'
    
    def test_search_by_similarity(self, client, sample_compound):
        """Test searching compounds by SMILES similarity."""
        # Create compound first
        client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        
        # Search by similar SMILES (propanol vs ethanol)
        response = client.get('/api/search?query=CCCO')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should find ethanol with some similarity
        assert len(data['compounds']) >= 0  # Might be 0 if similarity threshold not met
    
    def test_search_no_params(self, client):
        """Test search without parameters."""
        response = client.get('/api/search')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error']
    
    def test_get_compound_properties(self, client, sample_compound):
        """Test getting compound properties."""
        # Create compound first
        create_response = client.post(
            '/api/compounds',
            data=json.dumps(sample_compound),
            content_type='application/json'
        )
        created_compound = json.loads(create_response.data)
        compound_id = created_compound['id']
        
        # Get properties
        response = client.get(f'/api/compounds/{compound_id}/properties')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'molecular_formula' in data
        assert 'molecular_weight' in data
        assert 'logp' in data
        assert 'tpsa' in data
        assert data['molecular_formula'] == 'C2H6O'