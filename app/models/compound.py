from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Compound(db.Model):
    __tablename__ = 'compounds'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    smiles = db.Column(db.Text, nullable=False, unique=True)
    molecular_formula = db.Column(db.String(100))
    molecular_weight = db.Column(db.Float)
    logp = db.Column(db.Float)  # Lipophilicity
    tpsa = db.Column(db.Float)  # Topological Polar Surface Area
    hbd = db.Column(db.Integer)  # Hydrogen Bond Donors
    hba = db.Column(db.Integer)  # Hydrogen Bond Acceptors
    rotatable_bonds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'smiles': self.smiles,
            'molecular_formula': self.molecular_formula,
            'molecular_weight': self.molecular_weight,
            'logp': self.logp,
            'tpsa': self.tpsa,
            'hbd': self.hbd,
            'hba': self.hba,
            'rotatable_bonds': self.rotatable_bonds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Compound {self.name}: {self.smiles}>'