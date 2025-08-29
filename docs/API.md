# API Documentation

## Overview

The Cheminformatics Data Management System provides a RESTful API for managing chemical compounds and their properties. All endpoints return JSON responses.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required. In production, consider implementing API keys or OAuth.

## Endpoints

### Health Check

**GET** `/health`

Returns the API status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Cheminformatics Data Management System API is running"
}
```

### Compounds

#### Get All Compounds

**GET** `/compounds`

**Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 10)

**Response:**
```json
{
  "compounds": [...],
  "total": 10,
  "pages": 1,
  "current_page": 1
}
```

#### Create Compound

**POST** `/compounds`

**Request Body:**
```json
{
  "name": "Ethanol",
  "smiles": "CCO"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Ethanol",
  "smiles": "CCO",
  "molecular_formula": "C2H6O",
  "molecular_weight": 46.069,
  "logp": -0.31,
  "tpsa": 20.23,
  "hbd": 1,
  "hba": 1,
  "rotatable_bonds": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

#### Get Compound

**GET** `/compounds/{id}`

**Response:**
```json
{
  "id": 1,
  "name": "Ethanol",
  "smiles": "CCO",
  // ... other properties
}
```

#### Update Compound

**PUT** `/compounds/{id}`

**Request Body:**
```json
{
  "name": "Updated Name",
  "smiles": "new_smiles_optional"
}
```

#### Delete Compound

**DELETE** `/compounds/{id}`

**Response:**
```json
{
  "message": "Compound deleted successfully"
}
```

### Search

#### Search Compounds

**GET** `/search`

**Parameters:**
- `name` (string): Search by compound name (partial match)
- `query` (string): Search by SMILES similarity
- `similarity` (float, optional): Minimum similarity threshold (default: 0.7)

**Response:**
```json
{
  "compounds": [
    {
      "id": 1,
      "name": "Ethanol",
      "smiles": "CCO",
      "similarity": 0.95,
      // ... other properties
    }
  ]
}
```

### Properties

#### Get Compound Properties

**GET** `/compounds/{id}/properties`

**Response:**
```json
{
  "molecular_formula": "C2H6O",
  "molecular_weight": 46.069,
  "logp": -0.31,
  "tpsa": 20.23,
  "hbd": 1,
  "hba": 1,
  "rotatable_bonds": 1
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

## Examples

### Add a new compound using cURL:

```bash
curl -X POST http://localhost:5000/api/compounds \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin",
    "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
  }'
```

### Search for compounds similar to caffeine:

```bash
curl "http://localhost:5000/api/search?query=CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
```

### Get all compounds with pagination:

```bash
curl "http://localhost:5000/api/compounds?page=1&per_page=5"
```