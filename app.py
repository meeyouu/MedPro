import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///medlab.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Add custom template filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    import json
    if value:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}

# Context processor to make session data available in all templates
@app.context_processor
def inject_session_data():
    from flask import session
    from translations import get_all_translations
    current_language = session.get('language', 'en')
    return {
        'current_language': current_language,
        'session': session,
        'translations': get_all_translations(current_language)
    }

with app.app_context():
    # Import models to create tables
    import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created")
    
    # Initialize sample data
    try:
        from routes import create_sample_data
        create_sample_data()
        logging.info("Sample data initialized")
    except Exception as e:
        logging.warning(f"Could not initialize sample data: {e}")
