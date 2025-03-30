import paho.mqtt.client as mqtt
import os

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.162.172")
MQTT_TOPIC_BOX_STATE = "pillbuddy/wrong_medication_alert"

mqtt_client = mqtt.Client(client_id="Publisher", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.connect(MQTT_BROKER, 1883, 60)

mqtt_client.publish(MQTT_TOPIC_BOX_STATE, "Wrong medication Alert")
