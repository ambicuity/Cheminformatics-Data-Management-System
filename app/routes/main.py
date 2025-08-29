from flask import Blueprint, render_template, jsonify
from app.models.compound import Compound

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page"""
    compound_count = Compound.query.count()
    return render_template('index.html', compound_count=compound_count)

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with statistics"""
    stats = {
        'total_compounds': Compound.query.count(),
        'recent_compounds': Compound.query.order_by(
            Compound.created_at.desc()
        ).limit(5).all()
    }
    return render_template('dashboard.html', **stats)