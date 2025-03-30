from flask import Blueprint, request, jsonify
from models.patient import Patient
from models.medication import Medication

patients_bp = Blueprint("patients", __name__)

@patients_bp.route("/patients/<patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    """
    DELETE /api/patients/<patient_id>
    Delete the patient and all related meds.
    """
    try:
        Patient.delete(patient_id)
        Medication.delete_by_patient_id(patient_id)
        return jsonify({"message": "Patient and related medications deleted."}), 200
    except Exception as e:
        return jsonify({"message": "Error deleting patient", "error": str(e)}), 500
