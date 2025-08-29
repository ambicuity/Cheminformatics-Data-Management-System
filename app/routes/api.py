from flask import Blueprint, jsonify, request
from app import db
from app.models.compound import Compound
from app.utils.chem_utils import ChemUtils
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

@api_bp.route('/compounds', methods=['GET'])
def get_compounds():
    """Get all compounds with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    compounds = Compound.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'compounds': [compound.to_dict() for compound in compounds.items],
        'total': compounds.total,
        'pages': compounds.pages,
        'current_page': page
    })

@api_bp.route('/compounds', methods=['POST'])
def create_compound():
    """Create a new compound"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'smiles']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate SMILES
    smiles = data['smiles']
    if not ChemUtils.validate_smiles(smiles):
        return jsonify({'error': 'Invalid SMILES string'}), 400
    
    # Canonicalize SMILES
    canonical_smiles = ChemUtils.canonicalize_smiles(smiles)
    if not canonical_smiles:
        return jsonify({'error': 'Could not process SMILES string'}), 400
    
    # Check if compound already exists
    existing = Compound.query.filter_by(smiles=canonical_smiles).first()
    if existing:
        return jsonify({'error': 'Compound with this SMILES already exists'}), 409
    
    # Calculate molecular properties
    properties = ChemUtils.calculate_properties(canonical_smiles)
    if not properties:
        return jsonify({'error': 'Could not calculate molecular properties'}), 400
    
    try:
        compound = Compound(
            name=data['name'],
            smiles=canonical_smiles,
            molecular_formula=properties['molecular_formula'],
            molecular_weight=properties['molecular_weight'],
            logp=properties['logp'],
            tpsa=properties['tpsa'],
            hbd=properties['hbd'],
            hba=properties['hba'],
            rotatable_bonds=properties['rotatable_bonds']
        )
        
        db.session.add(compound)
        db.session.commit()
        
        logger.info(f"Created compound: {compound.name}")
        return jsonify(compound.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating compound: {e}")
        return jsonify({'error': 'Failed to create compound'}), 500

@api_bp.route('/compounds/<int:compound_id>', methods=['GET'])
def get_compound(compound_id):
    """Get a specific compound"""
    compound = Compound.query.get_or_404(compound_id)
    return jsonify(compound.to_dict())

@api_bp.route('/compounds/<int:compound_id>', methods=['PUT'])
def update_compound(compound_id):
    """Update a compound"""
    compound = Compound.query.get_or_404(compound_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update name if provided
    if 'name' in data:
        compound.name = data['name']
    
    # Update SMILES if provided (recalculate properties)
    if 'smiles' in data:
        smiles = data['smiles']
        if not ChemUtils.validate_smiles(smiles):
            return jsonify({'error': 'Invalid SMILES string'}), 400
        
        canonical_smiles = ChemUtils.canonicalize_smiles(smiles)
        if not canonical_smiles:
            return jsonify({'error': 'Could not process SMILES string'}), 400
        
        # Check if new SMILES conflicts with existing compound
        existing = Compound.query.filter(
            Compound.smiles == canonical_smiles,
            Compound.id != compound_id
        ).first()
        if existing:
            return jsonify({'error': 'Another compound with this SMILES already exists'}), 409
        
        properties = ChemUtils.calculate_properties(canonical_smiles)
        if not properties:
            return jsonify({'error': 'Could not calculate molecular properties'}), 400
        
        compound.smiles = canonical_smiles
        compound.molecular_formula = properties['molecular_formula']
        compound.molecular_weight = properties['molecular_weight']
        compound.logp = properties['logp']
        compound.tpsa = properties['tpsa']
        compound.hbd = properties['hbd']
        compound.hba = properties['hba']
        compound.rotatable_bonds = properties['rotatable_bonds']
    
    try:
        db.session.commit()
        logger.info(f"Updated compound: {compound.name}")
        return jsonify(compound.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating compound: {e}")
        return jsonify({'error': 'Failed to update compound'}), 500

@api_bp.route('/compounds/<int:compound_id>', methods=['DELETE'])
def delete_compound(compound_id):
    """Delete a compound"""
    compound = Compound.query.get_or_404(compound_id)
    
    try:
        db.session.delete(compound)
        db.session.commit()
        
        logger.info(f"Deleted compound: {compound.name}")
        return jsonify({'message': 'Compound deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting compound: {e}")
        return jsonify({'error': 'Failed to delete compound'}), 500

@api_bp.route('/search', methods=['GET'])
def search_compounds():
    """Search compounds by name or SMILES similarity"""
    query = request.args.get('query')
    name = request.args.get('name')
    similarity_threshold = request.args.get('similarity', 0.7, type=float)
    
    if not query and not name:
        return jsonify({'error': 'Query or name parameter required'}), 400
    
    compounds = []
    
    if name:
        # Search by name (case-insensitive partial match)
        compounds = Compound.query.filter(
            Compound.name.ilike(f'%{name}%')
        ).all()
    
    elif query:
        # Search by SMILES similarity
        if ChemUtils.validate_smiles(query):
            all_compounds = Compound.query.all()
            for compound in all_compounds:
                similarity = ChemUtils.calculate_similarity(query, compound.smiles)
                if similarity >= similarity_threshold:
                    compound_dict = compound.to_dict()
                    compound_dict['similarity'] = similarity
                    compounds.append(compound_dict)
            
            # Sort by similarity (highest first)
            compounds.sort(key=lambda x: x['similarity'], reverse=True)
            return jsonify({'compounds': compounds})
        else:
            return jsonify({'error': 'Invalid SMILES string for similarity search'}), 400
    
    return jsonify({
        'compounds': [compound.to_dict() for compound in compounds]
    })

@api_bp.route('/compounds/<int:compound_id>/properties', methods=['GET'])
def get_compound_properties(compound_id):
    """Get computed molecular properties for a compound"""
    compound = Compound.query.get_or_404(compound_id)
    
    properties = {
        'molecular_formula': compound.molecular_formula,
        'molecular_weight': compound.molecular_weight,
        'logp': compound.logp,
        'tpsa': compound.tpsa,
        'hbd': compound.hbd,
        'hba': compound.hba,
        'rotatable_bonds': compound.rotatable_bonds
    }
    
    return jsonify(properties)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Cheminformatics Data Management System API is running'
    })