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

# @medication_bp.route("/medications", methods=["GET"])
# def get_all_meds():
#     try:
#         meds = Medication.get_all()
#         return jsonify(meds), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
