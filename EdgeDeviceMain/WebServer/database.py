import RPi.GPIO as GPIO
import time
import cv2
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import subprocess

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["pillbuddy"]
medications_collection = db["medications"]

# List to store medication times
medication_times = []

# Function to Fetch Medication Times from MongoDB
def get_medication_time():
    global medication_times
    record = medications_collection.find_one({"patient_id": "67d14eee54cdeabd985cf424"})  # Example patient ID

    if record and "timings" in record:
        medication_times = record["timings"]
    else:
        medication_times = []

    print(f"Medication Schedule Updated: {medication_times}")
    
    
# Load Initial Medication Times
get_medication_time()
