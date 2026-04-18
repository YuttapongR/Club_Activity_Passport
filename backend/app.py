from flask import Flask, redirect, send_from_directory
from flask_cors import CORS
from backend.core.config import SECRET_KEY
import os

app = Flask(__name__, static_folder=None)
app.secret_key = SECRET_KEY
CORS(app, supports_credentials=True)

# --- Register Blueprints ---
from backend.auth.routes import auth_bp
from backend.activities.routes import activities_bp
from backend.clubs.routes import clubs_bp
from backend.members.routes import members_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(activities_bp, url_prefix='/api/activities')
app.register_blueprint(clubs_bp, url_prefix='/api/clubs')
app.register_blueprint(members_bp, url_prefix='/api/members')

# --- Serve Frontend Static Files ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.route('/')
def index():
    return redirect('/frontend/auth/login.html')


@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    frontend_dir = os.path.join(BASE_DIR, 'frontend')
    return send_from_directory(frontend_dir, filename)


@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    return send_from_directory(uploads_dir, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
