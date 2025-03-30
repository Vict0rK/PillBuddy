import time
import RPi.GPIO as GPIO
from hx711 import HX711
import cv2
import pytesseract
import json
import paho.mqtt.client as mqtt
import base64

################### MQTT ########################### 
mqtt_broker = "192.168.162.172"
mqtt_port = 1883
mqtt_topic_publish_dosage_alert = "pillbuddy/wrong_dosage_alert"
mqtt_topic_publish_buzzer = "pillbuddy/sound_buzzer"
mqtt_topic_subscribe_box_state = "pillbuddy/box_state"  # Topic to subscribe to
mqtt_message = None  # This will store the incoming MQTT message
box_open = False  # This flag will control when the RFID scanning should start (by default should be false)
box_state_changed = False  # To track when the box state has changed from the ultrasonic
correct_dosage_flag = False # To track if the correct dosage has been taken

medicine_prescriptions_column = "medicine_prescriptions"  # edit this according to the name inside the json file
medicine_to_take = "medicine_to_take"  # edit this according to the name inside the json file
path_to_json = "/home/pi/PillBuddy/medication_json_file/patientA_data.json"  # edit this based on the path of the json file

# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
		global mqtt_message, box_open, box_state_changed
		mqtt_message = msg.payload.decode("utf-8")
		print(f"Received MQTT message: {mqtt_message}")
		
		# Start RFID scanning only when "box open" message is received
		if mqtt_message == "Box Opened":
			print("Box is open. Starting Weight scan.")
			box_open = True
			box_state_changed = True  # Mark box state as changed
		elif mqtt_message == "Box Closed":
			print("Box is closed. Stopping Weight scan.")
			box_open = False
			box_state_changed = True  # Mark box state as changed

def publish_message(client, topic, message):
    """Helper function to ensure the MQTT client is connected before publishing"""
    try:
        if client.is_connected():  # Check if the client is connected
            client.publish(topic, message)
            print(f"Published message: {message}")
        else:
            print("MQTT client is not connected, retrying to publish...")
            # Attempt to reconnect if not connected
            client.reconnect()
            time.sleep(1)  # Give it a moment to reconnect
            if client.is_connected():
                client.publish(mqtt_topic_publish, message)
                print(f"Published message after reconnecting: {message}")
            else:
                print("Failed to reconnect to MQTT broker.")
    except Exception as e:
        print(f"Error while publishing message: {e}")

# Function to load all the medicine weights from the JSON file
def load_medicine_toTake(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
        print(f"Loaded JSON data: {data}")  # For debugging purposes
        
        # Convert all values to floats and store them in a list
        return [float(value) for value in data["medicine_to_take"].values()]
        

# Setup MQTT client and callbacks
client = mqtt.Client()
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port)  # Connect to the MQTT broker
client.subscribe(mqtt_topic_subscribe_box_state)  # Subscribe to the topic

# Start the MQTT loop to listen for messages
client.loop_start()

# Set the GPIO pin numbering mode (either GPIO.BOARD or GPIO.BCM)
GPIO.setmode(GPIO.BCM)  # Use GPIO.BOARD if you prefer physical pin numbers

# Initialize HX711 Weight Sensor
hx = HX711(dout_pin=5, pd_sck_pin=6)
CALIBRATION_FACTOR = 517.8137254901961  # Replace with your actual calibration factor
hx.set_scale_ratio(CALIBRATION_FACTOR)

def get_weight():
    """Measures and returns the current weight."""
    try:
        weight = hx.get_weight_mean(readings=10)
        return round(weight, 2)
    except Exception as e:
        print(f"Error reading weight: {e}")
        return None

def monitor_weight():
    """Continuously monitors weight and prints/logs detected values."""
    print("\nWeight Measurement Started...\n")

    try:
        while True:
            weight = get_weight()
            if weight is not None:
                print(f"Current Weight: {weight:.2f} g")
            else:
                print("Error: Could not read weight.")
            time.sleep(2)  # Adjust polling interval
    except KeyboardInterrupt:
        print("\nExiting weight sensor...")
        GPIO.cleanup()

medicine_weight = load_medicine_toTake(path_to_json)

# Flag to ensure that it does not send the alert again in a while
send_alerts = False

# Flag to count how many times correct weight is detected
correct_weight_count = 0

# Main loop to wait for the "Box Opened" message before starting the Text Detection
while True:
    if box_open:
        try:
            while box_open:
                # Obtain the weight 
                weight = get_weight()

                # Compare the weights (you can also choose to round or adjust tolerance)
                if medicine_weight[0]+2 >= weight >= medicine_weight[0]-2:
                    correct_weight_count += 1
                else:
                    print(f"Weight mismatch: JSON = {medicine_weight}, Detected = {weight}")
                    correct_weight_count = 0

                if correct_weight_count > 10:
                    print(f"Weight matches: {weight}")
                    publish_message(client, mqtt_topic_publish_dosage_alert, "Dosage is correct!")
                    publish_message(client, mqtt_topic_publish_buzzer, "Sound")
                    correct_dosage_flag = True

        except KeyboardInterrupt:
            print("Process interrupted")
            break

    else:
        # Check for "Box Closed" status and send a message if needed
        if box_state_changed and not box_open:
            print("Box closed")
            box_state_changed = False  # Reset state change to prevent repeated publishing
            if correct_dosage_flag is False:
                print("Dosage was not correct")  # Correct indentation here
                publish_message(client, mqtt_topic_publish_dosage_alert, "Dosage was not correct")
            else:
                correct_dosage_flag = False  # Correct indentation here

        # Wait for the "Box Opened" message before starting Text Detection scan
        print("Waiting for 'Box Opened' message to start Weight Sensor...")
        time.sleep(1)
