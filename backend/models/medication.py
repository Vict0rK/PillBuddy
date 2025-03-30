from database import mongo
from bson import ObjectId

class Medication:
    @staticmethod
    def add_medication(med_data):
        """
        Insert a medication record.
        med_data must include:
          - patient_id
          - name
          - timings (list)
          - dosage
          - unit (g or ml)
          - stock
          - stockUnit (g or ml)
        """
        mongo.db.medications.insert_one(med_data)

    @staticmethod
    def get_by_patient_id(patient_id):
        """Fetch all medications for the given patient_id."""
        meds = mongo.db.medications.find({"patient_id": patient_id})
        return [Medication.serialize(med) for med in meds]

    @staticmethod
    def delete_by_patient_id(patient_id):
        """Delete all medication records for the given patient_id."""
        mongo.db.medications.delete_many({"patient_id": patient_id})

    @staticmethod
    def serialize(doc):
        doc["_id"] = str(doc["_id"])
        return doc
