import paho.mqtt.client as mqtt
import os
import datetime

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload

    if topic == "pillbuddy/wrong_medication_alert":
        print(f"⚠️ Text Detection Alert received: {payload}")

    elif topic == "pillbuddy/image":
        print(f"📩 Received unknown face image ({len(message.payload)} bytes)")
        
        # Generate a timestamp-based filename for saving the image
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        folder_path = "UnknownFaces"  # Folder to store images

        # Create the folder if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        image_path = f"{folder_path}/unknown_face_received_{timestamp}.jpg"  # Example: unknown_face_received_20240313_143045.jpg

        with open(image_path, "wb") as image_file:
            image_file.write(message.payload)

    elif topic == "pillbuddy/rfid_alert":
        print(f"⚠️ RFID Alert received: {payload.decode()}")
        
    elif topic == "pillbuddy/wrong_dosage_alert":
        print(f"⚠️ Weight Alert received: {payload.decode()}")
        
    elif topic == "pillbuddy/wrong_medication_alert":
        print(f"⚠️ Text Detection Alert received: {payload.decode()}")
    
        
    elif topic == "pillbuddy/box_state":
        print(f"⚠️ Box state received: {payload.decode()}") 



    else:
        print(f"🔔 Received message on unhandled topic '{topic}': {payload.decode()}")

# Initialize MQTT client
client = mqtt.Client(client_id="Subscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message

# Connect to the MQTT broker
client.connect("192.168.162.172", 1883)

# Subscribe to multiple topics
client.subscribe("pillbuddy/wrong_medication_alert")
client.subscribe("pillbuddy/image")
client.subscribe("pillbuddy/rfid_alert")
client.subscribe("pillbuddy/wrong_dosage_alert")
client.subscribe("pillbuddy/box_state")

# Keep listening for messages
client.loop_forever()
