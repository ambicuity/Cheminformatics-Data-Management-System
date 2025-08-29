# Cheminformatics Data Management System

A scalable backend system for storing, managing, and retrieving large-scale chemical data, integrated with a web-based visualization tool for data interpretation.

## Features

- **Chemical Data Storage**: Store molecular structures in SMILES format with associated properties
- **RESTful API**: Complete CRUD operations for chemical compounds
- **Data Validation**: Molecular structure validation using RDKit
- **Scalable Architecture**: PostgreSQL database with optimized queries
- **Web Visualization**: Interactive web interface for data exploration
- **Containerized Deployment**: Docker support for easy scaling

## Architecture

```
Frontend (Web Interface)
        ↓
Backend API (Flask)
        ↓
Database (PostgreSQL)
```

## Quick Start

### Using Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/ambicuity/Cheminformatics-Data-Management-System.git
cd Cheminformatics-Data-Management-System

# Start the services
docker-compose up -d

# Access the application
# API: http://localhost:5000
# Web Interface: http://localhost:3000
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost/chemdb"
export FLASK_ENV=development

# Initialize the database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run the application
python run.py
```

## API Endpoints

### Compounds
- `GET /api/compounds` - List all compounds
- `POST /api/compounds` - Add a new compound
- `GET /api/compounds/<id>` - Get compound details
- `PUT /api/compounds/<id>` - Update compound
- `DELETE /api/compounds/<id>` - Delete compound

### Search
- `GET /api/search?query=<smiles>` - Search compounds by SMILES similarity
- `GET /api/search?name=<name>` - Search compounds by name

### Properties
- `GET /api/compounds/<id>/properties` - Get computed molecular properties

## Data Model

### Compound
- `id`: Unique identifier
- `name`: Compound name
- `smiles`: SMILES notation
- `molecular_formula`: Chemical formula
- `molecular_weight`: Molecular weight
- `created_at`: Timestamp
- `updated_at`: Timestamp

## Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Cheminformatics**: RDKit
- **Frontend**: HTML/JavaScript/CSS
- **Containerization**: Docker

## Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Apache License 2.0