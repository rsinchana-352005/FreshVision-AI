
from flask import Flask, request, jsonify, session, render_template, redirect,send_file, after_this_request
from database import client, db
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from datetime import datetime, timezone, timedelta
from pymongo.errors import DuplicateKeyError
import os

import tempfile
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename
from ai_engine import predict_both
from dotenv import load_dotenv
import uuid
import time
from flask import send_from_directory
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError
from ai_engine import predict_both, prepare_image
from xai_engine import (
    generate_both_gradcams,
    XAI_OUTPUT_DIR
)
from report_generator import (
    generate_individual_report,
    generate_evaluation_report
)
import re
from urllib.parse import urlsplit
from pathlib import Path
from threading import Lock
from lime_engine import generate_both_lime

load_dotenv()

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY"),
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    WTF_CSRF_TIME_LIMIT=3600,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
)

if not app.config["SECRET_KEY"]:
    raise ValueError("FLASK_SECRET_KEY is missing from .env")

csrf = CSRFProtect(app)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

users_collection = db["users"]
feedback_collection = db["feedback"]
# Temporary XAI image ownership registry
xai_ownership = {}
xai_ownership_lock = Lock()

users_collection.create_index("email", unique=True)


@app.route("/")
def home():
    return render_template("index.html")
@app.route("/login")
def login_page():
    if session.get("user_email"):
        return redirect("/dashboard")

    return render_template("login.html")
@app.route("/register")
def register_page():
    if session.get("user_id"):
        return redirect("/dashboard")

    return render_template("register.html")
@app.route("/dashboard")
def dashboard_page():
    if not session.get("user_email"):
        return redirect("/login")

    return render_template("dashboard.html")

    return render_template("dashboard.html")
@app.route("/analysis")
def analysis_page():
    if not session.get("user_email"):
        return redirect("/login")

    return render_template("analysis.html")
@app.route("/comparison")
def comparison_page():
    if not session.get("user_email"):
        return redirect("/login")

    return render_template("comparison.html")
@app.route("/explainability")
def explainability_page():
    if not session.get("user_email"):
        return redirect("/login")
    return render_template("explainability.html")

@app.route("/analytics")
def analytics_page():
    if not session.get("user_email"):
        return redirect("/login")
    return render_template("analytics.html")
@app.route("/profile")
def profile_page():
    if not session.get("user_email"):
        return redirect("/login")
    return render_template("profile.html")
@app.route("/feedback")
def feedback_page():
    if not session.get("user_email"):
        return redirect("/login")
    return render_template("feedback.html")
@app.route("/health")
def health():
    try:
        client.admin.command("ping")

        return jsonify({
            "status": "healthy"
        }), 200

    except Exception:
        app.logger.exception("Health check failed")

        return jsonify({
            "status": "unavailable"
        }), 503

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Please provide valid JSON data."
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    institution = data.get("institution", "")

    if not all(isinstance(v, str) for v in [name, email, password, institution]):
        return jsonify({
            "success": False,
            "message": "Invalid input."
        }), 400

    name = name.strip()
    email = email.strip().lower()
    institution = institution.strip()

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Name, email and password are required."
        }), 400
    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters."
        }), 400

    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    user = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "institution": institution,
        "created_at": datetime.now(timezone.utc)
    }

    try:
        users_collection.insert_one(user)
        return jsonify({
            "success": True,
            "message": "Registration successful."
        }), 201

    except DuplicateKeyError:
        return jsonify({
            "success": False,
            "message": "An account with this email already exists."
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Registration could not be completed."
        }), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    email = email.strip().lower()

    user = users_collection.find_one({"email": email})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    session.clear()
    session.permanent = True
    session["user_email"] = user["email"]

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "institution": user.get("institution", "")
        }
    }), 200


@app.route("/api/me", methods=["GET"])
def current_user():
    email = session.get("user_email")

    if not email:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    user = users_collection.find_one({"email": email})

    if not user:
        session.clear()
        return jsonify({
            "success": False,
            "message": "User account not found."
        }), 404

    return jsonify({
        "success": True,
        "user": {
            "name": user["name"],
            "email": user["email"],
            "institution": user.get("institution", "")
        }
    })
@app.route("/api/csrf-token", methods=["GET"])
def get_csrf_token():
    return jsonify({
        "success": True,
        "csrf_token": generate_csrf()
    })

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logout successful."
    })

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
        
    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json(silent=True) or {}

    category = data.get("category")
    message = data.get("message")

    if not isinstance(category, str) or not isinstance(message, str):
        return jsonify({
            "success": False,
            "message": "Category and message are required."
        }), 400

    category = category.strip()
    message = message.strip()

    allowed_categories = [
    "General Feedback",
    "Technical Issue",
    "AI Prediction",
    "UI/UX Suggestion",
    "Feature Request"
]

    if category not in allowed_categories:
        return jsonify({
            "success": False,
            "message": "Invalid feedback category."
        }), 400

    if not message:
        return jsonify({
            "success": False,
            "message": "Feedback message cannot be empty."
        }), 400

    if len(message) > 2000:
        return jsonify({
            "success": False,
            "message": "Feedback must be under 2000 characters."
        }), 400

    feedback = {
        "category": category,
        "message": message,
        "submitted_at": datetime.now(timezone.utc),
        "user_email": session.get("user_email")
    }

    try:
        feedback_collection.insert_one(feedback)

        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully."
        }), 201

    except Exception:
        return jsonify({
            "success": False,
            "message": "Unable to submit feedback."
        }), 500

def cleanup_old_xai_files():
    current_time = time.time()
    expired_ids = set()

    for filename in os.listdir(XAI_OUTPUT_DIR):
        file_path = os.path.join(XAI_OUTPUT_DIR, filename)

        if (
            os.path.isfile(file_path)
            and current_time - os.path.getmtime(file_path) > 1800
        ):
            os.remove(file_path)

            # Extract the prediction ID from the filename
            unique_id = filename.split("_")[0]
            expired_ids.add(unique_id)

    # Remove expired ownership records
    with xai_ownership_lock:
        for unique_id in expired_ids:
            xai_ownership.pop(unique_id, None)

@app.route("/api/predict", methods=["POST"])
def predict_image():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "Please upload an image."
        }), 400

    file = request.files["image"]

    if not file.filename:
        return jsonify({
            "success": False,
            "message": "No image selected."
        }), 400

    filename = secure_filename(file.filename)
    extension = filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "success": False,
            "message": "Only JPG, JPEG, PNG and WEBP images are allowed."
        }), 400

    temp_path = None

    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(
            suffix="." + extension,
            dir=UPLOAD_FOLDER,
            delete=False
        ) as temp_file:
            temp_path = temp_file.name

        file.save(temp_path)

        # Validate image
        with Image.open(temp_path) as img:
            img.verify()

        # Run both classification models
        results = predict_both(temp_path)

        # Prepare image for Grad-CAM
        image_array = prepare_image(temp_path)
        cleanup_old_xai_files()

        # Generate unique identifier
        unique_id = uuid.uuid4().hex[:12]
        with xai_ownership_lock:
            xai_ownership[unique_id] = session["user_email"]

        # Generate both Grad-CAM explanations
        xai_results = generate_both_gradcams(
            image_array,
            unique_id
        )
        # Generate both LIME explanations
        lime_results = generate_both_lime(
    image_array,
    unique_id
)

        # Return predictions and explanation URLs
        return jsonify({
            "success": True,
            "message": "Prediction and explanations generated successfully.",

            "results": {
                "mobilenet": {
                    "model": results["mobilenet"]["model"],
                    "predicted_class": results["mobilenet"]["predicted_class"],
                    "confidence": round(
                        results["mobilenet"]["confidence"] * 100, 2
                    )
                },

                "efficientnet": {
                    "model": results["efficientnet"]["model"],
                    "predicted_class": results["efficientnet"]["predicted_class"],
                    "confidence": round(
                        results["efficientnet"]["confidence"] * 100, 2
                    )
                },

                "models_agree": results["models_agree"]
            },

            "explanations": {
    "mobilenet_gradcam": {
        "prediction": xai_results["mobilenet_gradcam"]["predicted_class"],
        "confidence": xai_results["mobilenet_gradcam"]["confidence"],
        "image_url": f"/api/xai/{unique_id}_mobilenet_gradcam.png"
    },

    "efficientnet_gradcam": {
        "prediction": xai_results["efficientnet_gradcam"]["predicted_class"],
        "confidence": xai_results["efficientnet_gradcam"]["confidence"],
        "image_url": f"/api/xai/{unique_id}_efficientnet_gradcam.png"
    },

    "mobilenet_lime": {
        "prediction": lime_results["mobilenet_lime"]["predicted_class"],
        "confidence": lime_results["mobilenet_lime"]["confidence"],
        "image_url": f"/api/xai/{unique_id}_mobilenet_lime.png"
    },

    "efficientnet_lime": {
        "prediction": lime_results["efficientnet_lime"]["predicted_class"],
        "confidence": lime_results["efficientnet_lime"]["confidence"],
        "image_url": f"/api/xai/{unique_id}_efficientnet_lime.png"
    }
}
        }), 200

    except (UnidentifiedImageError, OSError):
        return jsonify({
            "success": False,
            "message": "The uploaded file is not a valid image."
        }), 400

    except Exception:
        app.logger.exception("Prediction or Grad-CAM generation failed")

        return jsonify({
            "success": False,
            "message": "Unable to process the image and explanations."
        }), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "message": "Image size must not exceed 8 MB."
    }), 413
@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return jsonify({
        "success": False,
        "message": "CSRF validation failed. Please refresh and try again."
    }), 400
@app.route("/api/xai/<filename>")
def serve_xai_image(filename):

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    # Allow only the four generated explanation image types
    allowed_suffixes = (
        "_mobilenet_gradcam.png",
        "_efficientnet_gradcam.png",
        "_mobilenet_lime.png",
        "_efficientnet_lime.png"
    )

    if not filename.endswith(allowed_suffixes):
        return jsonify({
            "success": False,
            "message": "Invalid explanation filename."
        }), 400

    unique_id = filename.split("_", 1)[0]

    # Validate generated ID format
    if (
        len(unique_id) != 12
        or not all(c in "0123456789abcdef" for c in unique_id)
    ):
        return jsonify({
            "success": False,
            "message": "Invalid explanation filename."
        }), 400

    with xai_ownership_lock:
        owner = xai_ownership.get(unique_id)

    if owner != session["user_email"]:
        return jsonify({
            "success": False,
            "message": "You are not authorized to access this image."
        }), 403

    return send_from_directory(
        XAI_OUTPUT_DIR,
        filename
    )

# --------------------------------------------------
# PDF REPORT DOWNLOADS
# --------------------------------------------------

def send_generated_pdf(generator, download_name):

    output_path = None

    try:
        report_dir = Path("generated_reports")
        report_dir.mkdir(exist_ok=True)

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".pdf",
            prefix="freshvision_",
            dir=str(report_dir),
            delete=False
        )

        output_path = Path(temp_file.name)
        temp_file.close()

        generator(output_path)

        @after_this_request
        def remove_temporary_report(response):
            try:
                if output_path.exists():
                    output_path.unlink()
            except OSError:
                app.logger.exception("Report cleanup failed.")

            return response

        return send_file(
            output_path,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/pdf"
        )

    except Exception:
        if output_path and output_path.exists():
            try:
                output_path.unlink()
            except OSError:
                app.logger.exception("Could not remove failed report.")

        raise


# --------------------------------------------------
# INDIVIDUAL ANALYSIS PDF
# --------------------------------------------------

@app.route("/api/reports/individual", methods=["POST"])
def download_individual_report():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid report data."
        }), 400

    results = data.get("results")
    explanations = data.get("explanations")

    if not isinstance(results, dict) or not isinstance(explanations, dict):
        return jsonify({
            "success": False,
            "message": "Prediction or explanation data is missing."
        }), 400

    required_keys = (
        "mobilenet_gradcam",
        "efficientnet_gradcam",
        "mobilenet_lime",
        "efficientnet_lime"
    )

    report_explanations = {}
    image_ids = set()

    try:
        for key in required_keys:

            explanation = explanations.get(key)

            if not isinstance(explanation, dict):
                raise ValueError("Missing explanation.")

            image_url = explanation.get("image_url")

            if not isinstance(image_url, str):
                raise ValueError("Invalid explanation URL.")

            parsed_path = urlsplit(image_url).path

            if not parsed_path.startswith("/api/xai/"):
                raise ValueError("Invalid explanation URL.")

            filename = Path(parsed_path).name

            match = re.fullmatch(
                r"([0-9a-f]{12})_(mobilenet_gradcam|"
                r"efficientnet_gradcam|mobilenet_lime|"
                r"efficientnet_lime)\.png",
                filename
            )

            if not match:
                raise ValueError("Invalid explanation filename.")

            unique_id = match.group(1)
            image_ids.add(unique_id)

            # Confirm that the image belongs to the logged-in user.
            with xai_ownership_lock:
                owner = xai_ownership.get(unique_id)

            if owner != session["user_email"]:
                return jsonify({
                    "success": False,
                    "message": "You are not authorized to use this explanation."
                }), 403

            image_path = (
                Path(XAI_OUTPUT_DIR) / filename
            ).resolve()

            xai_root = Path(XAI_OUTPUT_DIR).resolve()

            if image_path.parent != xai_root or not image_path.is_file():
                raise ValueError("Explanation image is unavailable.")

            report_explanations[key] = {
                "prediction": explanation.get("prediction"),
                "confidence": explanation.get("confidence"),
                "local_path": str(image_path)
            }

        # All four images must belong to the same prediction.
        if len(image_ids) != 1:
            raise ValueError("Explanation images do not belong to one analysis.")

        report_data = {
            "results": results,
            "models_agree": results.get("models_agree"),
            "explanations": report_explanations
        }

        return send_generated_pdf(
            lambda output_path: generate_individual_report(
                report_data,
                output_path
            ),
            "FreshVision_Individual_Analysis.pdf"
        )

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception:
        app.logger.exception("Individual PDF generation failed.")

        return jsonify({
            "success": False,
            "message": "Unable to generate the individual analysis report."
        }), 500


# --------------------------------------------------
# MODEL EVALUATION PDF
# --------------------------------------------------

@app.route("/api/reports/evaluation", methods=["GET"])
def download_evaluation_report():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first."
        }), 401

    try:
        return send_generated_pdf(
            generate_evaluation_report,
            "FreshVision_Model_Evaluation.pdf"
        )

    except Exception:
        app.logger.exception("Evaluation PDF generation failed.")

        return jsonify({
            "success": False,
            "message": "Unable to generate the evaluation report."
        }), 500

if __name__ == "__main__":
    app.run(debug=False)
