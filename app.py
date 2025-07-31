from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# 🔐 Load Firebase credentials
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# 🔗 Connect to Firestore
db = firestore.client()
collection = db.collection("students")

# 🚀 Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"message": "✅ Flask backend is running."}), 200

@app.route("/students", methods=["GET"])
def get_students():
    try:
        docs = collection.stream()
        students = [{
            "name": doc.to_dict().get("name", ""),
            "rollNo": doc.to_dict().get("rollNo", ""),
            "degree": doc.to_dict().get("degree", ""),
            "email": doc.to_dict().get("email", ""),
            "department": doc.to_dict().get("department", ""),
            "id": doc.id
        } for doc in docs]
        return jsonify(students), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/students", methods=["POST"])
def add_student():
    try:
        data = request.get_json()
        required = ["name", "rollNo", "degree", "email", "department"]
        if not all(data.get(field) for field in required):
            return jsonify({"error": "Missing required fields"}), 400

        doc_ref = collection.document()
        doc_ref.set(data)
        return jsonify({"id": doc_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/students/<id>", methods=["PUT"])
def update_student(id):
    try:
        data = request.get_json()
        doc_ref = collection.document(id)
        if not doc_ref.get().exists:
            return jsonify({"error": "Student not found"}), 404

        doc_ref.update(data)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/students/<id>", methods=["DELETE"])
def delete_student(id):
    try:
        doc_ref = collection.document(id)
        if not doc_ref.get().exists:
            return jsonify({"error": "Student not found"}), 404

        doc_ref.delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Running Flask server on http://localhost:5000")
    app.run(debug=True)
