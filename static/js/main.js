// Main JavaScript file for Cheminformatics Data Management System

// Global configuration
const API_BASE_URL = '/api';

// Utility functions
const utils = {
    // Show loading state
    showLoading: (elementId) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<div class="loading"></div> Loading...';
        }
    },

    // Show error message
    showError: (elementId, message) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        }
    },

    // Show success message
    showSuccess: (elementId, message) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="alert alert-success">${message}</div>`;
        }
    },

    // Format molecular weight
    formatMW: (value) => {
        return value ? parseFloat(value).toFixed(2) : 'N/A';
    },

    // Format LogP
    formatLogP: (value) => {
        return value ? parseFloat(value).toFixed(2) : 'N/A';
    },

    // Validate SMILES format (basic check)
    validateSMILES: (smiles) => {
        if (!smiles || smiles.trim().length === 0) {
            return false;
        }
        // Basic SMILES validation - contains only allowed characters
        const smilesRegex = /^[A-Za-z0-9@+\-\[\]()=#:.\\\/]+$/;
        return smilesRegex.test(smiles.trim());
    },

    // Truncate long strings
    truncate: (str, maxLength = 50) => {
        if (!str) return 'N/A';
        return str.length > maxLength ? str.substring(0, maxLength) + '...' : str;
    }
};

// API functions
const api = {
    // Generic fetch wrapper
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // Get all compounds
    async getCompounds(page = 1, perPage = 10) {
        return await this.request(`/compounds?page=${page}&per_page=${perPage}`);
    },

    // Get single compound
    async getCompound(id) {
        return await this.request(`/compounds/${id}`);
    },

    // Create compound
    async createCompound(data) {
        return await this.request('/compounds', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // Update compound
    async updateCompound(id, data) {
        return await this.request(`/compounds/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // Delete compound
    async deleteCompound(id) {
        return await this.request(`/compounds/${id}`, {
            method: 'DELETE'
        });
    },

    // Search compounds
    async searchCompounds(query) {
        const params = new URLSearchParams(query);
        return await this.request(`/search?${params.toString()}`);
    },

    // Health check
    async healthCheck() {
        return await this.request('/health');
    }
};

// Compound management functions
const compounds = {
    // Render compound list
    renderList: (compounds, containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!compounds || compounds.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No compounds found.</div>';
            return;
        }

        let html = '<div class="row">';
        compounds.forEach(compound => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${compound.name}</h6>
                            <p class="card-text">
                                <strong>SMILES:</strong> <code>${utils.truncate(compound.smiles, 30)}</code><br>
                                <strong>MW:</strong> ${utils.formatMW(compound.molecular_weight)}<br>
                                <strong>LogP:</strong> ${utils.formatLogP(compound.logp)}
                                ${compound.similarity ? `<br><strong>Similarity:</strong> ${(compound.similarity * 100).toFixed(1)}%` : ''}
                            </p>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="compounds.viewDetails(${compound.id})">
                                    View
                                </button>
                                <button class="btn btn-outline-warning" onclick="compounds.edit(${compound.id})">
                                    Edit
                                </button>
                                <button class="btn btn-outline-danger" onclick="compounds.delete(${compound.id})">
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    },

    // View compound details
    async viewDetails(id) {
        try {
            const compound = await api.getCompound(id);
            
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Compound Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <table class="table">
                                <tr><th>Name</th><td>${compound.name}</td></tr>
                                <tr><th>SMILES</th><td><code>${compound.smiles}</code></td></tr>
                                <tr><th>Formula</th><td>${compound.molecular_formula || 'N/A'}</td></tr>
                                <tr><th>Molecular Weight</th><td>${utils.formatMW(compound.molecular_weight)}</td></tr>
                                <tr><th>LogP</th><td>${utils.formatLogP(compound.logp)}</td></tr>
                                <tr><th>TPSA</th><td>${compound.tpsa ? compound.tpsa.toFixed(2) : 'N/A'}</td></tr>
                                <tr><th>HBD</th><td>${compound.hbd || 'N/A'}</td></tr>
                                <tr><th>HBA</th><td>${compound.hba || 'N/A'}</td></tr>
                                <tr><th>Rotatable Bonds</th><td>${compound.rotatable_bonds || 'N/A'}</td></tr>
                                <tr><th>Created</th><td>${compound.created_at ? new Date(compound.created_at).toLocaleString() : 'N/A'}</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            modal.addEventListener('hidden.bs.modal', () => {
                document.body.removeChild(modal);
            });
            
        } catch (error) {
            alert(`Error loading compound details: ${error.message}`);
        }
    },

    // Edit compound (placeholder)
    edit: (id) => {
        alert(`Edit functionality for compound ${id} would be implemented here`);
    },

    // Delete compound
    async delete(id) {
        if (!confirm('Are you sure you want to delete this compound?')) {
            return;
        }

        try {
            await api.deleteCompound(id);
            alert('Compound deleted successfully');
            // Reload the current view
            location.reload();
        } catch (error) {
            alert(`Error deleting compound: ${error.message}`);
        }
    }
};

// Search functionality
const search = {
    // Initialize search handlers
    init: () => {
        // Add event listeners for search forms
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', search.handleSubmit);
        }
    },

    // Handle search form submission
    handleSubmit: async (event) => {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const query = {};
        
        const name = formData.get('name');
        const smiles = formData.get('smiles');
        
        if (name) query.name = name;
        if (smiles) query.query = smiles;
        
        if (Object.keys(query).length === 0) {
            alert('Please enter a search term');
            return;
        }
        
        try {
            utils.showLoading('searchResults');
            const results = await api.searchCompounds(query);
            compounds.renderList(results.compounds, 'searchResults');
        } catch (error) {
            utils.showError('searchResults', `Search failed: ${error.message}`);
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    search.init();
    console.log('Cheminformatics Data Management System initialized');
});

// Export for global access
window.ChemDB = {
    api,
    utils,
    compounds,
    search
};