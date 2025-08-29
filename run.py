from app import create_app, db
import os

# Create application instance
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database tables created!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)