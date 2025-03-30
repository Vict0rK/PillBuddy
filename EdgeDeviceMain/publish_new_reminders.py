import json
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.24.227"  # Replace with your broker's IP
TOPIC = "pillbuddy/reminder_times"

# New reminder times you want to send (24-hour format)
reminder_times = ["18:35", "19:04", "19:06"]

client = mqtt.Client(client_id="PublisherTest",  callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

payload = json.dumps(reminder_times)
client.publish(TOPIC, payload)
print("Published reminder times:", payload)

# Allow some time to ensure the message is sent before shutting down
time.sleep(1)
client.loop_stop()
client.disconnect()
