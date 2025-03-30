import paho.mqtt.client as mqtt

# MQTT settings
mqtt_broker = "192.168.162.29"  # Replace with your MQTT broker address
mqtt_port = 1883  # Typically 1883, change if needed
mqtt_topic_subscribe = "pillbuddy/box_closed"  # Topic to subscribe to

# Function to handle incoming MQTT messages
def on_message(client, userdata, message):
    print(f"received Message'{message.payload.decode()}' on topic '{message.topic}")

# Setup MQTT client and callbacks
client = mqtt.Client(client_id="Subscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port)  # Connect to the MQTT broker
client.subscribe(mqtt_topic_subscribe)  # Subscribe to the topic


# Start the MQTT loop in a separate thread
client.loop_forever()

print("MQTT subscriber started...")

