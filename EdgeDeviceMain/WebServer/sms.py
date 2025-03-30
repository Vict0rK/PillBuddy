import paho.mqtt.client as mqtt
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER")

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to Send SMS Reminder
def send_sms():
    print("Sending SMS Reminder...")
    message = client.messages.create(
        body="Reminder: It's time to take your medication!",
        from_=TWILIO_PHONE_NUMBER,
        to=PATIENT_PHONE_NUMBER
    )
    print(f"SMS Sent! Message SID: {message.sid}")
