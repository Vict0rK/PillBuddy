from database import mongo
from bson import ObjectId

class Patient:
    @staticmethod
    def add(name, face_data, face_model):
        """Create new patient, return its ID."""
        result = mongo.db.patients.insert_one({
            "name": name,
            "face_data": face_data,
            "face_model": face_model
        })
        return str(result.inserted_id)

    @staticmethod
    def update(patient_id, name, face_data, face_model):
        """Update existing patient by ID."""

        mongo.db.patients.update_one(
            {"_id": ObjectId(patient_id)},
            {"$set": {"name": name, "face_data": face_data, "face_model": face_model}}
        )

    @staticmethod
    def get_latest():
        doc = mongo.db.patients.find_one({}, sort=[("_id", -1)])
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def delete(patient_id):
        mongo.db.patients.delete_one({"_id": ObjectId(patient_id)})