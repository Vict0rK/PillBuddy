import RPi.GPIO as GPIO
import time
import cv2
import paho.mqtt.client as mqtt
from twilio.rest import Client
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER")

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.162.29")
MQTT_TOPIC_ALERT = "pillbuddy/alert"
MQTT_TOPIC_MEDICATION_TAKEN = "pillbuddy/medication_taken"
MQTT_TOPIC_UPDATE_SCHEDULE = "pillbuddy/update_schedule"
MQTT_TOPIC_BOX_STATE = "pillbuddy/box_state"

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["pillbuddy"]
medications_collection = db["medications"]

# GPIO Setup
GPIO.setwarnings(False)
BUZZER_PIN = 18  # Passive buzzer
ULTRASONIC_TRIG = 23
ULTRASONIC_ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(ULTRASONIC_TRIG, GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO, GPIO.IN)

# Set Up Passive Buzzer
pwm = GPIO.PWM(BUZZER_PIN, 1000)

# Initialize MQTT Client
# mqtt_client = mqtt.Client(client_id="Pi3-Alert", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
mqtt_client = mqtt.Client(client_id="Publisher", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.connect(MQTT_BROKER, 1883, 60)

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Global Variables
medication_times = []  # Stores medication times

medication_times = ["17:32"] # HEWRE HEHRIHNDiojasndjhoahdsoujansdoujhajsoidaoisdjhoiasjdoiasjdoiajsdojaoisdjoiasjdoiajsdoijda
# Function to Fetch Medication Times from MongoDB
# def get_medication_time():
    # global medication_times
    # record = medications_collection.find_one({"patient_id": "67d14eee54cdeabd985cf424"})  # Example patient ID

    # if record and "timings" in record:
        # medication_times = record["timings"]
    # else:
        # medication_times = []

    # print(f"Medication Schedule Updated: {medication_times}")


# Function to Send SMS Reminder
def send_sms():
    print("Sending SMS Reminder...")
    message = client.messages.create(
        body="Reminder: It's time to take your medication!",
        from_=TWILIO_PHONE_NUMBER,
        to=PATIENT_PHONE_NUMBER
    )
    print(f"SMS Sent! Message SID: {message.sid}")


# Function to Measure Distance (Ultrasonic Sensor)
def measure_distance():
    GPIO.output(ULTRASONIC_TRIG, True)
    time.sleep(0.00001)
    GPIO.output(ULTRASONIC_TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ULTRASONIC_ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ULTRASONIC_ECHO) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2

    print(f"Measured Distance: {distance:.2f} cm")  # Debugging print
    return distance


def detect_face():
	face_rec_venv_path = "/home/victor/face_rec/bin/python3" # path to virtual environment

	script_path = "/home/victor/Desktop/Face_Recognition/facial_recognition_hardware.py"

	print("Starting face recognition...")

	# Run the face rec script inside the virtual environment
	face_rec_process = subprocess.Popen([face_rec_venv_path, script_path])
	# subprocess.run([face_rec_venv_path, script_path])
	
	return face_rec_process  # Return the process so we can stop it later
	
	
def check_box_closure(face_rec_process):
    print("Waiting for box to be closed...")

    while True:
        distance = measure_distance()  # Your function to check box status
        if distance < 10:  # Box is considered "closed"
            print("Box closed. Stopping face recognition.")
            face_rec_process.terminate()  # Stop the face_rec script         
            mqtt_client.publish(MQTT_TOPIC_BOX_STATE, "Box Closed") # Publish "Box Closed" message
            break
        time.sleep(1)


# Function to Trigger Alert
def alert():
    print("Medication Alert! Buzzer Activated.")
    
    # Beep continuously at intervals until the box is opened
    while True:
        pwm.start(50)
        time.sleep(0.5)
        pwm.stop()
        time.sleep(0.5)

        distance = measure_distance()
        if distance > 10:  # Box is considered "opened"
            print("Box opened! Executing Face Recognition...")
            
            # Publish "Box Open" message
            mqtt_client.publish(MQTT_TOPIC_BOX_STATE, "Box Opened")
            
            # Start face recognition script
            face_rec_process = detect_face()
            
            # Start checking if box is closed
            check_box_closure(face_rec_process)

            break


# MQTT Callback to Update Medication Schedule
def on_message(client, userdata, message):
    if message.topic == MQTT_TOPIC_UPDATE_SCHEDULE:
        print("Received update for medication schedule!")
        # get_medication_time()


# MQTT Subscription
mqtt_client.subscribe(MQTT_TOPIC_UPDATE_SCHEDULE)
mqtt_client.on_message = on_message
mqtt_client.loop_start()

# Load Initial Medication Times
# get_medication_time()

# Main Loop
try:
    while True:
        current_time = time.strftime("%H:%M")
        
        if current_time in medication_times:
            print(f"Medication Time Matched: {current_time}! Triggering Alert.")
            alert()
            time.sleep(60)  # Avoid triggering multiple times in the same minute

        time.sleep(1)  # Check every second for precise timing

except KeyboardInterrupt:
    print("Exiting...")
    pwm.stop()
    GPIO.cleanup()
