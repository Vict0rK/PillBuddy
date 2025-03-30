import cv2
import pytesseract
import json
import paho.mqtt.client as mqtt
import base64
import time
import os

################### MQTT ########################### 
mqtt_broker = "192.168.220.172"
mqtt_port = 1883
mqtt_topic_publish_wrong_medication_flag = "pillbuddy/wrong_medication_flag"
mqtt_topic_subscribe_box_state = "pillbuddy/box_state"  # Topic to subscribe 
mqtt_topic_subscribe_setup = "pillbuddy/setup" 
mqtt_message = None  # This will store the incoming MQTT message
box_open = False  # This flag will control when the RFID scanning should start (by default should be false)
box_state_changed = False  # To track when the box state has changed

medicine_prescriptions_column = "medicine_prescriptions"  # edit this according to the name inside the json file
medicine_to_take = "medicine_to_take"  # edit this according to the name inside the json file
path_to_json = "/home/pi/PillBuddy/medication_json_file/patient_data.json"  # edit this based on the path of the json file


# directory to save the json file to for [SETUP]
json_directory = "/home/pi/PillBuddy/medication_json_file"
json_file_path = os.path.join(json_directory, "patient_data.json")

# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    global mqtt_message, box_open, box_state_changed
    mqtt_message = msg.payload.decode("utf-8")
    
    if msg.topic == "pillbuddy/box_state":
        # Start RFID scanning only when "box open" message is received
        if mqtt_message == "Box Opened":
            print("Box is open. Starting Text Detection scan.")
            box_open = True
            box_state_changed = True  # Mark box state as changed
        elif mqtt_message == "Box Closed":
            print("Box is closed. Stopping Text Detection scan.")
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


def publish_message(client, message):
    """Helper function to ensure the MQTT client is connected before publishing"""
    try:
        if client.is_connected():  # Check if the client is connected
            client.publish(mqtt_topic_publish_wrong_medication_flag, message)
            print(f"Published message: {message}")
        else:
            print("MQTT client is not connected, retrying to publish...")
            # Attempt to reconnect if not connected
            client.reconnect()
            time.sleep(1)  # Give it a moment to reconnect
            if client.is_connected():
                client.publish(mqtt_topic_publish_wrong_medication_flag, message)
                print(f"Published message after reconnecting: {message}")
            else:
                print("Failed to reconnect to MQTT broker.")
    except Exception as e:
        print(f"Error while publishing message: {e}")


# Load medicine list from JSON file
def load_medicine_list(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
        return [{"name": med, "not_detected_count": 0} for med in data["medication_list"]]

# Function to load medicine to take from JSON File
def load_medicine_toTake(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
        return [med["name"].lower() for med in data["medications_to_take"]]  # Convert to lowercase


# Setup MQTT client and callbacks
client = mqtt.Client()
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port)  # Connect to the MQTT broker
client.subscribe(mqtt_topic_subscribe_box_state)  # Subscribe to the topic
client.subscribe(mqtt_topic_subscribe_setup)

# Start the MQTT loop to listen for messages
client.loop_start()



# Initialize the webcam
cap = cv2.VideoCapture(0)

# Adjust resolution
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Adjust resolution and frame rate
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduce width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Reduce height
cap.set(cv2.CAP_PROP_FPS, 30)  # Set FPS to 15 for better performance


# Load the list of medicines
medicine_list = load_medicine_list(path_to_json)  # Replace with your JSON file path
medicine_to_take_list = load_medicine_toTake(path_to_json)


# Track if an alert has been sent for each medicine
sent_alerts = {medicine["name"].lower(): False for medicine in medicine_list}


# Preprocess Frame 
def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh


# Function to Extract Text
def extract_text(frame):
    processed_frame = preprocess_frame(frame)
    # custom config to assume a single uniform block of text 
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(processed_frame, config=custom_config)
    return text


# Main loop to wait for the "Box Opened" message before starting the Text Detection
while True:
    if box_open:
        try:
            while box_open:
                # Capture frame from the webcam
                ret, frame = cap.read()
                
                # [DEBUG] print medicine 
                #for x in medicine_to_take_list:
                    #print(f"Correct Medicine is {x}")

                if not ret:
                    print("Failed to capture frame.")
                    break

                # Extracting text from the frame
                #flipped_frame = cv2.flip(frame, -1)  # Flip to correct mirroring issue
                detected_text = extract_text(frame).lower()
                print("Detected Text:", detected_text)

                # Check if detected text contains any medicine names
                for medicine in medicine_list:
                    medicine_name = medicine["name"].lower()
                    print(f"Medicine Name: {medicine['name']}, Count: {medicine['not_detected_count']}") 

                    # If medicine is detected (medicine is still in the box)
                    if medicine_name in detected_text:
                        print(f"?? Alert: {medicine_name} is still in box") 
                        medicine["not_detected_count"] = 0  # Reset counter if detected
                        # Reset the alert flag if the medicine is detected
                        sent_alerts[medicine_name] = False  # Reset the sent alert flag

                    # If medicine is not detected (medicine is taken out)
                    else: 
                        medicine["not_detected_count"] += 1  # add to 1 count if not detected

                        if medicine["not_detected_count"] >= 30:  # Medicine is out of box, add to 1 count if not detected
                            print(f"?? Alert: {medicine_name} is out of the box")

                            # If the alert has not been sent yet, send it now
                            if not sent_alerts[medicine_name]:
                                
                                # [DECISION POINT: If wrong medication is being taken, meaning the one that is taken out is the wrong one]
                                if medicine_name not in medicine_to_take_list:
                                    publish_message(client, "True")
                                    print(f"?? Alert: {medicine_name} is the wrong medicine!")
                                # [DECISION POINT: Correct medication is taken, meaning the correct one is taken out]
                                else:
                                    publish_message(client, "False")
                                    print(f"?? Alert: {medicine_name} is the correct medication to be taken")
                                
                                # Set the flag to True to prevent further alerts for this medicine
                                sent_alerts[medicine_name] = True

                # Display the frame
                cv2.imshow("Webcam Feed", frame)

                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("Process interrupted")
            break
        
    else:
        # Check for "Box Closed" status and send a message if needed
        if box_state_changed and not box_open:
            
            # Reset all medication counter to zero 
            for medicine in medicine_list:
                medicine["not_detected_count"] = 0
            
            box_state_changed = False  # Reset state change to prevent repeated publishing

        # Wait for the "Box Opened" message before starting Text Detection scan
        print("Waiting for 'Box Opened' message to start Text Detection scan...")
        time.sleep(1)

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
