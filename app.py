import os
from pathlib import Path

from dotenv import load_dotenv

# Load env before ai_service (which builds OpenAI client at import time).
_backend_dir = Path(__file__).resolve().parent
load_dotenv(_backend_dir.parent / ".env")
load_dotenv(_backend_dir / ".env")

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from extensions import db
from pdf_processor import extract_text_from_pdf
from ai_service import generate_study_plan, generate_quiz
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///databsde.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
from models import History, User  # noqa: E402 - register models after db.init_app

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#authentication
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email = data.get("email")).first()
    if not user or not check_password_hash(user.password, data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401
    login_user(user)
    return jsonify({"message": "Login successful"}), 200

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if User.query.filter_by(email = email).first():
        return jsonify({"error": "Email already exists"}), 400
    user = User(
        email = email,
        password = generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registration successful"}), 201
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200






@app.route("/plan", methods =["POST"])
@login_required
def plan():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400
    try:
        text = extract_text_from_pdf(file)
        result = generate_study_plan(text)
        history = History(
            user_id=current_user.id,
            filename=file.filename,
            type="plan",
            result=str(result)
        )
        db.session.add(history)
        db.session.commit()
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/quiz", methods=["POST"])
@login_required
def quiz():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400
    num_q = int(request.form.get("num_questions", 10))
    try:
        text = extract_text_from_pdf(file)
        result = generate_quiz(text, num_questions=num_q)
        history = History(
            user_id=current_user.id,
            filename=file.filename,
            type="quiz",
            result=str(result)
        )
        db.session.add(history)
        db.session.commit()
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
@login_required
def history():
    items = History.query.filter_by(user_id=current_user.id).order_by(History.created_at.desc()).all()
    return jsonify([{
        "id": item.id,
        "filename": item.filename,
        "type": item.type,
        "created_at": item.created_at.strftime("%Y-%m-%d %H:%M")
    } for item in items])
if __name__ == "__main__":
    app.run(debug=True,port=5000)