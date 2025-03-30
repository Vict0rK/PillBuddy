import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import paho.mqtt.client as mqtt

# MQTT settings
mqtt_broker = "192.168.220.172"  # Replace with your MQTT broker address
mqtt_port = 1883  # Typically 1883, change if needed
mqtt_topic_subscribe = "pillbuddy/box_state"  # Topic to subscribe to
mqtt_topic_publish_wrong_rfid_flag = "pillbuddy/wrong_rfid_flag"  # Topic for incorrect medicine removal alert
mqtt_topic_publish_medicine_taken = "pillbuddy/medicine_taken"  # Topic for correct medicine taken
mqtt_message = None  # Store incoming MQTT message
box_open = False  # Control when the RFID scanning starts (False by default)
box_state_changed = False  # Track when the box state has changed
medication_taken = False  # Boolean flag for whether the correct medicine was taken

# Correct medicine RFID ID
CORRECT_MEDICINE_ID = 1050891322463

# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    global mqtt_message, box_open, box_state_changed
    mqtt_message = msg.payload.decode("utf-8")
    print(f"Received MQTT message: {mqtt_message}")

    if mqtt_message == "Box Opened":
        print("Box is open. Starting RFID scan.")
        box_open = True
        box_state_changed = True
    elif mqtt_message == "Box Closed":
        print("Box is closed. Stopping RFID scan.")
        box_open = False
        box_state_changed = True

# Setup MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port)
client.subscribe(mqtt_topic_subscribe)
client.loop_start()

print("RFID monitoring and MQTT subscriber started...")

# Initialize RFID reader
reader = SimpleMFRC522()

# Track last detected RFID tag
last_detected = None
no_tag_counter = 0  # Track how many cycles no tag has been detected

def publish_message(client, topic, message):
    """Helper function to ensure the MQTT client is connected before publishing"""
    try:
        if client.is_connected():
            client.publish(topic, message)
            print(f"Published to {topic}: {message}")
        else:
            print("MQTT client not connected, retrying...")
            client.reconnect()
            time.sleep(1)
            if client.is_connected():
                client.publish(topic, message)
                print(f"Published after reconnecting: {message}")
            else:
                print("Failed to reconnect to MQTT broker.")
    except Exception as e:
        print(f"Error while publishing message: {e}")

# Main loop to wait for "Box Opened" before scanning RFID
while True:
    if box_open:
        try:
            while box_open:
                # Scan for RFID tag
                rfid_id, text = reader.read_no_block()

                if rfid_id:
                    if last_detected is None:
                        print(f"Medication Detected: {text.strip()} (ID: {rfid_id})")
                    elif rfid_id != last_detected:
                        print(f"Medication Changed: {text.strip()} (ID: {rfid_id})")

                    last_detected = rfid_id
                    no_tag_counter = 0  # Reset counter since a tag was detected

                else:
                    # No tag detected
                    if last_detected is not None:
                        no_tag_counter += 1

                        # If the RFID tag disappears for 3 consecutive cycles, consider it removed
                        if no_tag_counter >= 3:
                            print(f"Medication Removed! Last detected ID: {last_detected}")

                            if last_detected == CORRECT_MEDICINE_ID:
                                print("✅ Correct medicine taken.")
                                publish_message(client, mqtt_topic_publish_wrong_rfid_flag, "False")
                                medication_taken = True
                            else:
                                print("❌ Incorrect medicine taken!")

                            last_detected = None
                            no_tag_counter = 0  # Reset counter

                time.sleep(1)  # Adjust polling interval as needed

        except KeyboardInterrupt:
            print("Process interrupted")
            break
        finally:
            GPIO.cleanup()
    else:
        # If box is closed but medication is not taken, send a message
        if box_state_changed and not box_open and not medication_taken:
            publish_message(client, mqtt_topic_publish_wrong_rfid_flag, "True") # If medication was not taken out at all, it means the wrong medication was taken.
            box_state_changed = False  # Reset flag

        print("Waiting for 'Box Opened' message to start RFID scan...")
        time.sleep(1)
