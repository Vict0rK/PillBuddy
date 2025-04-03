import time
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from mqtt_setup import mqtt_client, connect_mqtt
from buzzer import reminder_alert 
import base64

# Load environment variables
load_dotenv()

# Setup and Connect to MQTT
connect_mqtt()
time.sleep(2)

# Hardcoded medication reminder times (24-hour format)
REMINDER_TIMES = ["18:27"]
# print(f"Current reminder times: {REMINDER_TIMES}")

authorized_names = []

output_pickle_path = "Face_Recognition/encodings.pickle"


def decode_pickle_to_file(base64_pickle_string, output_pickle_path):
    """
    Decodes a base64-encoded pickle string and saves it as a pickle file.
    
    :param base64_pickle_string: The base64-encoded string representation of the pickle data.
    :param output_pickle_path: Path where the decoded pickle file should be saved.
    """
    # Decode the base64 string back to pickle bytes
    pickle_bytes = base64.b64decode(base64_pickle_string)
    
    # Write the bytes to the output file in binary mode
    with open(output_pickle_path, "wb") as f:
        f.write(pickle_bytes)
    print(f"Pickle file saved to: {output_pickle_path}")


# MQTT callback to update REMINDER_TIMES when new setup is received
def on_reminder_update(client, userdata, message):
    global REMINDER_TIMES
    global authorized_names
    try:
        data = json.loads(message.payload.decode())  # Parse the JSON
        # print("Received data:", data)
        
        authorized_names = [data["name"].lower()]

        # Get the timings array from the first medication
        new_times = data["medications_to_take"][0]["timings"]
        # print("Extracted new reminder times:", new_times)

        # Update the global REMINDER_TIMES with the new timings
        REMINDER_TIMES = new_times
        print(f"Updated REMINDER_TIMES: {REMINDER_TIMES}")

        base64_pickle_string = data["face_model"]    
        decode_pickle_to_file(base64_pickle_string, output_pickle_path)

    except Exception as e:
        print("Error updating settings:", e)


# Subscribe to the configuration topic and add the callback
mqtt_client.subscribe("pillbuddy/setup")
mqtt_client.message_callback_add("pillbuddy/setup", on_reminder_update)


def check_reminders():
    """Continuously checks if the current time matches a scheduled reminder."""
    while True:
        current_time = datetime.now().strftime("%H:%M")  # Get current time as HH:MM

        if current_time in REMINDER_TIMES:
            print(f"🔔 Reminder triggered at {current_time}")

            # Call buzzer alert
            reminder_alert(authorized_names)

            time.sleep(30)  # Prevent multiple triggers in the same minute
        
        time.sleep(1)  # Check every second

if __name__ == "__main__":
    print("🟢 Medication Box Started. Waiting for scheduled times...")
    check_reminders()
