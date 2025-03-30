import paho.mqtt.client as mqtt
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MQTT Configuration
MQTT_BROKER = "192.168.24.227"

# Initialize MQTT Client but do NOT connect immediately
mqtt_client = mqtt.Client(client_id="Publisher", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)


def connect_mqtt():
    """Connect to the MQTT broker."""
    try:
        mqtt_client.connect(MQTT_BROKER, 1883, 60)
        mqtt_client.loop_start()
        print("Connected to MQTT broker.")
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")

def publish_message(client, topic, message):
    """Publish a message to MQTT."""
    try:
        if client.is_connected():
            client.publish(topic, message)
            print(f"Published message: {message}")
        else:
            print("MQTT client is not connected, attempting to reconnect...")
            client.reconnect()
            time.sleep(1)
            if client.is_connected():
                client.publish(topic, message)
                print(f"Published after reconnecting: {message}")
            else:
                print("Failed to reconnect.")
    except Exception as e:
        print(f"Error publishing: {e}")
