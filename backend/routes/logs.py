from flask import Blueprint, jsonify, request
from models.log import Log, NotificationLog
from datetime import datetime
from twilio.rest import Client
import os


# TWILLIO Credentials for SMS 
# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER")


# Connect to Twillio Client
# Initialize Twilio Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to Send SMS Reminder
def send_sms(message_to_send):
    try:
        print("Sending SMS Reminder...")
        message = twilio_client.messages.create(
            body=message_to_send,
            from_=TWILIO_PHONE_NUMBER,
            to=PATIENT_PHONE_NUMBER
        )
        print(f"SMS Sent! Message SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")



# Create the logs blueprint
logs_bp = Blueprint("logs", __name__)

@logs_bp.route("/logs", methods=["GET"])
def get_logs():
    logs = Log.get_all()  # returns list of dict from Mongo
    # Convert the BSON date to a string
    for log in logs:
        if "time" in log and isinstance(log["time"], datetime):
            log["time"] = log["time"].isoformat()  # e.g. "2023-06-15T01:00:00+00:00"
    return jsonify(logs)



# Add a new log (POST request)
@logs_bp.route("/logs", methods=["POST"])
def add_log():
    try:
        data = request.json  # Get the incoming JSON data
        # Validate the data
        if "user" not in data or "action" not in data or "time" not in data:
            return jsonify({"message": "Missing required fields: 'user', 'action', or 'time'"}), 400
        
        Log.add(data)
        NotificationLog.add(data)
        send_sms(data["action"])

        return jsonify({"message": "Log added successfully!"}), 201
    except Exception as e:
        return jsonify({"message": "Error adding log", "error": str(e)}), 500
    

# Logs for notifications page

@logs_bp.route("/notifications", methods=["GET"])
def get_notifications():
    logs = NotificationLog.get_all()
    for log in logs:
        if "time" in log and isinstance(log["time"], datetime):
            log["time"] = log["time"].isoformat()
    return jsonify(logs)


@logs_bp.route("/notifications", methods=["DELETE"])
def clear_notifications():
    try:
        NotificationLog.clear()
        return jsonify({"message": "Notifications cleared successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Error clearing notifications", "error": str(e)}), 500
