import RPi.GPIO as GPIO
import time
import subprocess
from mqtt_setup import mqtt_client
from ultrasonic import measure_distance
import json

TOPIC_BOX_STATE = "pillbuddy/box_state"  # Keep only the topic

GPIO.setwarnings(False)
BUZZER_PIN = 18  # Passive buzzer

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Set Up Passive Buzzer
pwm = GPIO.PWM(BUZZER_PIN, 1000)

# Box closed distance
BOX_CLOSED_DISTANCE = 15


def reminder_alert(authorized_names):
    """Function to start the buzzer alert and wait for box to be opened."""
    print("🚨 Medication Alert! Buzzer Activated.")
    
    # Start buzzing until the box is opened
    while measure_distance() <= BOX_CLOSED_DISTANCE:  # While the box is **closed**
        pwm.start(50)
        time.sleep(0.5)
        pwm.stop()
        time.sleep(0.5)

    print("✅ Box opened! Stopping buzzer...")
    pwm.stop()
    
    # Publish "Box Opened" message using existing MQTT client
    # publish_message(mqtt_client, TOPIC_BOX_STATE, "Box Opened")
    mqtt_client.publish(TOPIC_BOX_STATE, "Box Opened")

    # Start face recognition
    face_rec_process = detect_face(authorized_names)

    # Start monitoring if box is closed again
    check_box_closure(face_rec_process)

def detect_face(authorized_names):
    """Executes the face detection script."""
    face_rec_venv_path = "/home/victor/face_rec/bin/python3"
    script_path = "/home/victor/Desktop/EdgeDeviceMain/Face_Recognition/facial_recognition_hardware.py"
    working_directory = "/home/victor/Desktop/EdgeDeviceMain/Face_Recognition" 
    
    serialized_names = json.dumps(authorized_names)

    print("🟢 Starting face recognition...")

    # Run the face recognition script inside the virtual environment
    # face_rec_process = subprocess.Popen([face_rec_venv_path, script_path], cwd=working_directory)
    face_rec_process = subprocess.Popen([face_rec_venv_path, script_path, serialized_names], cwd=working_directory)
    
    return face_rec_process  # Return the process so we can stop it later

def check_box_closure(face_rec_process):
    """Checks if the box is closed again after opening."""
    print("⌛ Waiting for box to be closed...")

    while True:
        if measure_distance() < BOX_CLOSED_DISTANCE:  # If box is closed
            print("❌ Box closed. Stopping face recognition.")
            face_rec_process.terminate()  # Stop face recognition
            mqtt_client.publish(TOPIC_BOX_STATE, "Box Closed")  # Fixed indentation
            break
        time.sleep(1)
