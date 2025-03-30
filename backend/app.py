from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.medications import medication_bp
from routes.logs import logs_bp
from routes.analytics import analytics_bp
from routes.setup import setup_bp
from routes.patients import patients_bp

app = Flask(__name__)
CORS(app)

# Initialize the database
init_db(app)

# Register blueprints for modular routes
app.register_blueprint(medication_bp, url_prefix="/api")
app.register_blueprint(logs_bp, url_prefix="/api")
app.register_blueprint(analytics_bp, url_prefix="/api")
app.register_blueprint(setup_bp, url_prefix="/api")
app.register_blueprint(patients_bp, url_prefix="/api")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

