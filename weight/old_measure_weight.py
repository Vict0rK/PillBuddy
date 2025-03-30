import time
import os
import json
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from hx711 import HX711

################### MQTT ###########################
mqtt_broker = "192.168.162.172"
mqtt_port = 1883
mqtt_topic_publish_wrong_dosage_flag = "pillbuddy/wrong_dosage_flag"
mqtt_topic_subscribe_box_state = "pillbuddy/box_state"  # Topic to subscribe to
mqtt_topic_subscribe_setup = "pillbuddy/setup"

mqtt_message = None  # This will store the incoming MQTT message
box_open = False  # This flag will control when the RFID scanning should start (by default should be false)
box_state_changed = False  # To track when the box state has changed from the ultrasonic
correct_dosage_flag = False  # To track if the correct dosage has been taken

medicine_prescriptions_column = "medicine_prescriptions"  # Edit this according to the name inside the JSON file
path_to_json = "/home/aaron/PillBuddy/medication_json_file/patient_data.json"  # Edit this based on the path of the JSON file

# Directory to save the JSON file to for [SETUP]
json_directory = "/home/aaron/PillBuddy/medication_json_file"
json_file_path = os.path.join(json_directory, "patient_data.json")


# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    global mqtt_message, box_open, box_state_changed
    mqtt_message = msg.payload.decode("utf-8")

    if msg.topic == "pillbuddy/box_state":
        # Start RFID scanning only when "box open" message is received
        if mqtt_message == "Box Opened":
            print("Box is open. Starting Weight scan.")
            box_open = True
            box_state_changed = True  # Mark box state as changed
        elif mqtt_message == "Box Closed":
            print("Box is closed. Stopping Weight scan.")
            box_open = False
            box_state_changed = True  # Mark box state as changed

    elif msg.topic == "pillbuddy/setup":
        print(f"Received MQTT message: {mqtt_message}")
        try:
            # Convert string to JSON
            data = json.loads(mqtt_message)

            # Ensure the directory exists
            if not os.path.exists(json_directory):
                os.makedirs(json_directory)

            # Save JSON data to file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"Saved setup data to {json_file_path}")

        except json.JSONDecodeError:
            print("Error: Received message is not a valid JSON format.")


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
                client.publish(mqtt_topic_publish_dosage_alert, message)
                print(f"Published message after reconnecting: {message}")
            else:
                print("Failed to reconnect to MQTT broker.")
    except Exception as e:
        print(f"Error while publishing message: {e}")


# Function to load all the medicine dosages as floats from the JSON file
def load_medicine_dosages(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
        print(f"Loaded JSON data: {data}")  # For debugging purposes

        # Extract dosage from "medications_to_take" and convert to float
        return [float(med["dosage"]) for med in data["medications_to_take"]]


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
CALIBRATION_FACTOR = 938.6527777777778  # Replace with your actual calibration factor
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


medicine_weight = load_medicine_dosages(path_to_json)

# Flags
send_alerts = False
correct_weight_count = 0

# Main loop to wait for the "Box Opened" message before starting Weight Detection
initial_weight = None
final_weight = None
tolerance = 15  # Adjust based on your accuracy needs

while True:
    if box_open:
        if initial_weight is None:
            # Store weight once when box is opened
            initial_weight = get_weight()
            print(f"Initial weight when box opened: {initial_weight} g")

        # Keep printing live weight while box is open
        current_weight = get_weight()
        print(f"Live weight: {current_weight} g")

        # Wait before next read
        time.sleep(1)

        # Keep waiting here until box is closed
        print("Box is open... waiting to close.")
        time.sleep(1)

    else:
        # Box has just been closed
        if box_state_changed:
            print("Box closed")
            final_weight = get_weight()
            print(f"Final weight after box closed: {final_weight} g")

            # Reset state change flag
            box_state_changed = False

            if initial_weight is not None and final_weight is not None:
                weight_difference = round(initial_weight - final_weight, 2)
                expected = medicine_weight[0]

                if weight_difference < 0:
                    weight_difference = -weight_difference

                print(f"Weight difference: {weight_difference} g")
                print(f"Expected: {expected} ± {tolerance} g")

                if expected - tolerance <= weight_difference <= expected + tolerance:
                    print("Dosage is correct.")
                    publish_message(client, mqtt_topic_publish_wrong_dosage_flag, "False")
                    correct_dosage_flag = True
                elif weight_difference < expected - tolerance:
                    print("Dosage was too little.")
                    publish_message(client, mqtt_topic_publish_wrong_dosage_flag, "True")
                elif weight_difference > expected + tolerance:
                    print("Dosage was too much.")
                    publish_message(client, mqtt_topic_publish_wrong_dosage_flag, "True")

            # Reset for the next cycle
            initial_weight = None
            final_weight = None
            correct_dosage_flag = False

        # Wait for the "Box Opened" message before starting Text Detection scan
        print("Waiting for 'Box Opened' message to start Weight Sensor...")
        time.sleep(1)
