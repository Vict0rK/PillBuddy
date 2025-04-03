import time
import os
import RPi.GPIO as GPIO
from hx711 import HX711
import json
import paho.mqtt.client as mqtt
import base64

################### MQTT ########################### 
mqtt_broker = "192.168.220.172"
mqtt_port = 1883
mqtt_topic_publish_dosage_flag = "pillbuddy/wrong_dosage_flag"
mqtt_topic_publish_buzzer = "pillbuddy/sound_buzzer"
mqtt_topic_subscribe_box_state = "pillbuddy/box_state"
mqtt_topic_subscribe_setup = "pillbuddy/setup"
mqtt_topic_publish_updated_weight = "pillbuddy/updated_weight"
mqtt_topic_subscribe_medication_taken = "pillbuddy/medication_taken"
mqtt_message = None
box_open = False
box_state_changed = False
correct_dosage_flag = False
current_medication_taken = None

medicine_prescriptions_column = "medicine_prescriptions"
path_to_json = "/home/aaron/PillBuddy/medication_json_file/patient_data.json"

json_directory = "/home/aaron/PillBuddy/medication_json_file"
json_file_path = os.path.join(json_directory, "patient_data.json")

# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    global mqtt_message, box_open, box_state_changed
    mqtt_message = msg.payload.decode("utf-8")

    if msg.topic == "pillbuddy/box_state":
        if mqtt_message == "Box Opened":
            print("Box is open. Starting Weight scan.")
            box_open = True
            box_state_changed = True
        elif mqtt_message == "Box Closed":
            print("Box is closed. Stopping Weight scan.")
            box_open = False
            box_state_changed = True

    elif msg.topic == "pillbuddy/setup":
        print(f"Received MQTT message: {mqtt_message}")
        try:
            data = json.loads(mqtt_message)
            if not os.path.exists(json_directory):
                os.makedirs(json_directory)
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Saved setup data to {json_file_path}")
        except json.JSONDecodeError:
            print("Error: Received message is not a valid JSON format.")

    elif msg.topic == "pillbuddy/medication_taken":
        current_medication_taken = mqtt_message
        print(f"Medication taken received: {current_medication_taken}")

def publish_message(client, topic, message):
    try:
        if client.is_connected():
            client.publish(topic, message)
            print(f"Published message: {message}")
        else:
            print("MQTT client is not connected, retrying to publish...")
            client.reconnect()
            time.sleep(1)
            if client.is_connected():
                client.publish(topic, message)
                print(f"Published message after reconnecting: {message}")
            else:
                print("Failed to reconnect to MQTT broker.")
    except Exception as e:
        print(f"Error while publishing message: {e}")

def load_medicine_toTake(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
        print(f"Loaded JSON data: {data}")
        return [float(med["dosage"]) for med in data["medications_to_take"]]

client = mqtt.Client()
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port)
client.subscribe(mqtt_topic_subscribe_box_state)
client.subscribe(mqtt_topic_subscribe_setup)
client.subscribe(mqtt_topic_subscribe_medication_taken)
client.loop_start()

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=5, pd_sck_pin=6)
CALIBRATION_FACTOR = 938.6527777777778
hx.set_scale_ratio(CALIBRATION_FACTOR)

def get_weight():
    try:
        weight = hx.get_weight_mean(readings=10)
        return round(weight, 2)
    except Exception as e:
        print(f"Error reading weight: {e}")
        return None

medicine_weight = load_medicine_toTake(path_to_json)

send_alerts = False
correct_weight_count = 0
initial_weight = None
final_weight = None
tolerance = 15

while True:
    if box_open:
        if initial_weight is None:
            initial_weight = get_weight()
            print(f"Initial weight when box opened: {initial_weight} g")

        current_weight = get_weight()
        print(f"Live weight: {current_weight} g")

        time.sleep(1)
        print("Box is open... waiting to close.")
        time.sleep(1)
    else:
        if box_state_changed:
            print("Box closed")
            final_weight = get_weight()
            print(f"Final weight after box closed: {final_weight} g")

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
                    publish_message(client, mqtt_topic_publish_dosage_flag, "False")
                    correct_dosage_flag = True
                elif weight_difference < expected - tolerance:
                    print("Dosage was too little.")
                    publish_message(client, mqtt_topic_publish_dosage_flag, "True")
                    publish_message(client, mqtt_topic_publish_buzzer, "Sound")
                elif weight_difference > expected + tolerance:
                    print("Dosage was too much.")
                    publish_message(client, mqtt_topic_publish_dosage_flag, "True")
                    publish_message(client, mqtt_topic_publish_buzzer, "Sound")

                # Publish updated weight if we have a medication name from text_detection
                if current_medication_taken is not None:
                    payload = json.dumps({
                        "medication": current_medication_taken,
                        "weight": final_weight
                    })
                    publish_message(client, mqtt_topic_publish_updated_weight, payload)
                    current_medication_taken = None


            initial_weight = None
            final_weight = None
            correct_dosage_flag = False

        print("Waiting for 'Box Opened' message to start Weight Sensor...")
        time.sleep(1)
