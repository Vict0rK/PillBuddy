
import paho.mqtt.client as mqtt
import os
import datetime

BROKER_IP = "192.168.178.227"  # Replace with Raspberry Pi 1's IP
TOPIC = "image/topic"  # This is the topic where the image is sent

def on_message(client, userdata, message):
    print(f"📩 Received unknown face image ({len(message.payload)} bytes)")
    
    # Generate a timestamp-based filename for saving the image
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    
    folder_path = "UnknownFaces"  # Folder to store images

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    image_path = f"{folder_path}/unknown_face_received_{timestamp}.jpg"  # Example: unknown_face_received_20240313_143045.jpg

    # image_path = "unknown_face_received.jpg"

    with open(image_path, "wb") as image_file:
        image_file.write(message.payload)

    # print(f"✅ Unknown face image saved as {image_path}")


client = mqtt.Client(client_id="Subscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(BROKER_IP, 1883)
client.subscribe(TOPIC)

print("🟢 Waiting for messages...")
client.loop_forever()
