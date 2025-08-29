# Deployment Guide

## Production Deployment

### Using Docker (Recommended)

1. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - API: http://localhost:5000
   - Web Interface: http://localhost:5000
   - Database Admin: http://localhost:8080 (Adminer)

3. **Initialize with sample data:**
   ```bash
   curl -X POST http://localhost:5000/api/compounds \
     -H "Content-Type: application/json" \
     -d '{"name": "Ethanol", "smiles": "CCO"}'
   ```

### Manual Deployment

1. **Install RDKit (Production Setup):**
   ```bash
   # Using conda (recommended for RDKit)
   conda install -c conda-forge rdkit
   
   # Or using pip (may require additional system packages)
   pip install rdkit-pypi
   ```

2. **Install other dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database:**
   ```bash
   # Install PostgreSQL
   sudo apt-get install postgresql postgresql-contrib
   
   # Create database and user
   sudo -u postgres psql
   CREATE DATABASE chemdb;
   CREATE USER chemdb_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE chemdb TO chemdb_user;
   \q
   ```

4. **Configure environment variables:**
   ```bash
   export DATABASE_URL="postgresql://chemdb_user:your_password@localhost/chemdb"
   export SECRET_KEY="your-secret-key"
   export FLASK_ENV="production"
   ```

5. **Initialize database:**
   ```bash
   python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
   ```

6. **Run with Gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
   ```

## Scaling Considerations

### Database Optimization

1. **Add indexes for better query performance:**
   ```sql
   CREATE INDEX idx_compounds_smiles ON compounds(smiles);
   CREATE INDEX idx_compounds_name ON compounds(name);
   CREATE INDEX idx_compounds_created_at ON compounds(created_at);
   ```

2. **Consider partitioning for large datasets:**
   ```sql
   -- Example: Partition by creation date
   CREATE TABLE compounds_2023 PARTITION OF compounds 
   FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
   ```

### Application Scaling

1. **Use Redis for caching:**
   ```python
   # Add to requirements.txt
   redis==4.5.4
   flask-caching==2.0.2
   
   # Configure caching in config.py
   CACHE_TYPE = "redis"
   CACHE_REDIS_URL = "redis://localhost:6379"
   ```

2. **Implement connection pooling:**
   ```python
   # In config.py
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 20,
       'pool_recycle': 3600,
       'pool_pre_ping': True
   }
   ```

3. **Use a reverse proxy (Nginx):**
   ```nginx
   upstream chemdb_app {
       server 127.0.0.1:5000;
       server 127.0.0.1:5001;
       server 127.0.0.1:5002;
       server 127.0.0.1:5003;
   }
   
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://chemdb_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Security Considerations

1. **Add authentication:**
   ```python
   # Consider using Flask-JWT-Extended
   from flask_jwt_extended import JWTManager, create_access_token, jwt_required
   ```

2. **Input validation:**
   ```python
   # Use marshmallow for request validation
   from marshmallow import Schema, fields, validate
   ```

3. **Rate limiting:**
   ```python
   # Use Flask-Limiter
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address
   
   limiter = Limiter(
       app,
       key_func=get_remote_address,
       default_limits=["200 per day", "50 per hour"]
   )
   ```

## Monitoring

### Health Checks

The application includes a health endpoint at `/api/health` for monitoring.

### Logging

Configure logging in production:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/chemdb.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Performance Monitoring

Consider using tools like:
- **New Relic** or **DataDog** for APM
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for log analysis

## Backup Strategy

1. **Database backups:**
   ```bash
   # Daily backup script
   pg_dump -h localhost -U chemdb_user chemdb > backup_$(date +%Y%m%d).sql
   ```

2. **Application backups:**
   ```bash
   # Backup application files
   tar -czf chemdb_app_$(date +%Y%m%d).tar.gz /path/to/application
   ```

## Environment Variables

Create a `.env` file with:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/chemdb

# Flask
SECRET_KEY=your-super-secret-key
FLASK_ENV=production

# Optional: External services
REDIS_URL=redis://localhost:6379
SENTRY_DSN=your-sentry-dsn
```