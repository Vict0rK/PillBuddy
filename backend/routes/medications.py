from flask import Blueprint, request, jsonify
from models.medication import Medication

medication_bp = Blueprint("medication", __name__)

@medication_bp.route("/medications/<patient_id>", methods=["GET"])
def get_medications_by_patient(patient_id):
    """
    GET /api/medications/<patient_id>
    Returns all medications for a given patient_id.
    """
    try:
        meds = Medication.get_by_patient_id(patient_id)
        return jsonify(meds), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medication_bp.route("/medications/<patient_id>", methods=["PUT"])
def update_medication_weight(patient_id):
    """
    PUT /api/medications/<patient_id>
    Expects JSON data: { "medication": "<med_name>", "weight": <new_weight> }
    Updates the weight/stock for the specified medication.
    """
    data = request.get_json()
    try:
        updated_med = Medication.update_weight(patient_id, data["medication"], data["weight"])
        return jsonify(updated_med), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
