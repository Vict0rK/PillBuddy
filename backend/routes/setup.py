from flask import Blueprint, request, jsonify
from models.patient import Patient
from models.medication import Medication
import base64, pickle, numpy as np
#import face_recognition

setup_bp = Blueprint("setup", __name__)

@setup_bp.route("/setup", methods=["GET"])
def get_setup():
    """
    Returns the most recent patient document and that patient's medications.
    If no patient exists, returns an empty JSON with a 404 status.
    """
    patient = Patient.get_latest()
    if not patient:
        return jsonify({}), 404

    meds = Medication.get_by_patient_id(patient["_id"])
    patient["medications"] = meds
    return jsonify(patient), 200

# This API is called for either Adding New Patient Setup, or or Saving Changes to the Patient Setup
@setup_bp.route("/setup", methods=["POST"])
def setup_patient_and_meds():
    """
    POST /api/setup
    Updates an existing patient if `patient_id` is provided; otherwise, creates a new patient.
    """
    try:
        data = request.json # data from request header

        # Check if request header has all the required fields
        if "name" not in data or "face_data" not in data or "medications" not in data:
            return jsonify({"message": "Invalid data format"}), 400

        # Store the request data values to local variables
        patient_id = data.get("patient_id")
        name = data["name"]
        face_data = data["face_data"]
        meds = data["medications"]
        # face_model = data["face_model"]
        # hard coded face model pickle file
        face_model = "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"

        # Check if this is called from "Save Changes" (i.e There is an existing patient setup already)
        if patient_id:
            # Update existing patient
            Patient.update(patient_id, name, face_data, face_model)
            Medication.delete_by_patient_id(patient_id)  # Clear old meds

        # Else, Create new patient
        else:
            # Create a new patient
            patient_id = Patient.add(name, face_data, face_model)

        # Save new medications
        for med in meds:
            Medication.add_medication({
                "patient_id": patient_id,
                "name": med["name"],
                "timings": med["timings"],
                "dosage": med["dosage"],
                "unit": med["unit"],
                "stock": med["stock"],
                "stockUnit": med["stockUnit"]
            })

        return jsonify({"message": "Setup saved successfully!", "patient_id": patient_id}), 201

    except Exception as e:
        return jsonify({"message": "Error saving setup", "error": str(e)}), 500
    

# @setup_bp.route("/trainface", methods=["POST"])
# def train_face():
#     data = request.get_json()
#     face_data_base64 = data.get("face_data")
#     if not face_data_base64:
#         return jsonify({"error": "No face data provided"}), 400

#     # Decode the base64 string into bytes
#     face_bytes = base64.b64decode(face_data_base64)
#     # Convert bytes to a NumPy array and decode it as an image
#     nparr = np.frombuffer(face_bytes, np.uint8)
#     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     # Convert BGR to RGB
#     rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#     # Detect face and compute encoding
#     boxes = face_recognition.face_locations(rgb, model="hog")
#     encodings = face_recognition.face_encodings(rgb, boxes)
#     if len(encodings) == 0:
#         return jsonify({"error": "No face found"}), 400

#     # Use the first encoding (for demonstration)
#     encoding = encodings[0]
#     # Create a model dictionary (you might want to include a name or additional info)
#     model_data = {"encoding": encoding.tolist()}
#     # Serialize the model data to pickle bytes
#     pickle_bytes = pickle.dumps(model_data)
#     # Convert the pickle file to a base64 string
#     base64_pickle = base64.b64encode(pickle_bytes).decode("utf-8")
#     return jsonify({"face_model": base64_pickle})