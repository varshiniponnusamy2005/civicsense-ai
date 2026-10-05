from flask import Flask
from flask_cors import CORS

from database import db
from routes.auth_routes import auth_bp
from routes.complaint_routes import complaint_bp
from routes.department_routes import department_bp
from routes.status_routes import status_bp
from routes.department_complaint_routes import department_complaint_bp
from routes.tracking_routes import tracking_bp
from routes.notification_routes import notification_bp


app = Flask(__name__)
CORS(app)

# Register API routes
app.register_blueprint(auth_bp)
app.register_blueprint(complaint_bp)
app.register_blueprint(department_bp)
app.register_blueprint(status_bp)
app.register_blueprint(department_complaint_bp)
app.register_blueprint(tracking_bp)
app.register_blueprint(notification_bp)


@app.route("/")
def home():
    return {
        "message": "CiviSense AI Backend is running!"
    }


@app.route("/api/health")
def health():
    return {
        "status": "success",
        "database": "MongoDB connected"
    }


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )