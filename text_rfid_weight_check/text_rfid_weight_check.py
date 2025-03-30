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

# MQTT Topics to publish Logs
mqtt_topic_publish_wrong_medication_alert = "pillbuddy/wrong_medication_alert"
mqtt_topic_publish_wrong_dosage_alert = "pillbuddy/wrong_dosage_alert"
mqtt_topic_publish_correct_medication_alert = "pillbuddy/correct_medication_alert"

# MQTT Topics from Edge Devices (Text Detection, Weigh Sensor, RFID)
mqtt_topic_subscribe_wrong_medication_flag = "pillbuddy/wrong_medication_flag"
mqtt_topic_subscribe_wrong_dosage_flag = "pillbuddy/wrong_dosage_flag"
mqtt_topic_subscribe_wrong_rfid_flag = "pillbuddy/wrong_rfid_flag"
mqtt_message = None  # This will store the incoming MQTT message


# MQTT Topics to listen box state (box open or close)
mqtt_topic_subscribe_box_state = "pillbuddy/box_state"


# Flags 
initial_flag = True     # to ensure that the checks only happen after the first MQTT message comes in
wrong_medication_flag = False
wrong_dosage_flag = False
wrong_rfid_flag = False
haveAlerted_flag = False  # this is to show that it has been alerted once and once only

# box state flag (open or close), False by default, indicating close
box_open = False
box_state_changed = False



# Function to handle incoming MQTT messages
def on_message(client, userdata, msg):
    global mqtt_message, wrong_medication_flag, wrong_dosage_flag, wrong_rfid_flag, initial_flag, box_open, box_state_changed
    mqtt_message = msg.payload.decode("utf-8")
    
    if msg.topic == mqtt_topic_subscribe_wrong_medication_flag:
        if mqtt_message == "True":
            print("Wrong Medication Flag is True")
            wrong_medication_flag = True
        else:
            wrong_medication_flag = False
        initial_flag = False

    elif msg.topic == mqtt_topic_subscribe_wrong_dosage_flag:
        if mqtt_message == "True":
            print("Wrong Dosage Flag is True")
            wrong_dosage_flag = True
        else:
            wrong_dosage_flag = False
        #initial_flag = False

    elif msg.topic == mqtt_topic_subscribe_wrong_rfid_flag:
        if mqtt_message == "True":
            print("Wrong RFID Flag is True")
            wrong_rfid_flag = True
        else:
            wrong_rfid_flag = False
        #initial_flag = False
        
    elif msg.topic == mqtt_topic_subscribe_box_state:
        if mqtt_message == "Box Opened":
            print("Box is open. Starting Weight scan.")
            box_open = True
        elif mqtt_message == "Box Closed":
            print("Box is closed. Stopping Weight scan.")
            box_open = False
            box_state_changed = True
            initial_flag = False



def publish_message(client, topic, message):
    """Helper function to ensure the MQTT client is connected before publishing"""
    try:
        if client.is_connected():  # Check if the client is connected
            client.publish(topic, message)
            print(message)
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


# Setup MQTT client and callbacks
client = mqtt.Client()
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port)
client.subscribe(mqtt_topic_subscribe_wrong_medication_flag)
client.subscribe(mqtt_topic_subscribe_wrong_dosage_flag)
client.subscribe(mqtt_topic_subscribe_wrong_rfid_flag)
client.subscribe(mqtt_topic_subscribe_box_state)

# Start the MQTT loop
client.loop_start()

try:
    while True:
        # DEBUG: test for current flags
        print(f"Wrong Medication: {wrong_medication_flag}, Wrong Dosage: {wrong_dosage_flag}, Wrong RFID: {wrong_rfid_flag}, Initial Flag: {initial_flag}, haveAlerted Flag: {haveAlerted_flag}")
        
        if box_open:
            print("Box is open, monitoring scans...")
            

            
            if wrong_medication_flag and not initial_flag and not haveAlerted_flag:
                publish_message(client, mqtt_topic_publish_wrong_medication_alert, "Wrong Medication Taken")
                print("Published Wrong Medication Taken")
                haveAlerted_flag = True
                 

        else:
            # When box is closed
            print("Box is closed, waiting...")
            
            time.sleep(1)

                        
            # Conditions for dosage and rfid
            if not wrong_medication_flag and not wrong_rfid_flag and not haveAlerted_flag and not initial_flag:
                if wrong_dosage_flag:
                    publish_message(client, mqtt_topic_publish_wrong_dosage_alert, "Incorrect Dosage Taken")
                    print("Published Wrong Dosage Alert")
                    haveAlerted_flag = True
                    #wrong_dosage_flag = False
                    #initial_flag = True

                elif not wrong_dosage_flag:
                    publish_message(client, mqtt_topic_publish_correct_medication_alert, "Medication Taken Correctly")
                    print("Published Correct Medication Alert")
                    haveAlerted_flag = True
                    #initial_flag = True

            
            # reset the flags
            haveAlerted_flag = False  # Reset alert flag when the box is opened
            wrong_medication_flag = False
            wrong_dosage_flag = False
            wrong_rfid_flag = False
            initial_flag = True
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping...")
 
finally:
    client.loop_stop()
    client.disconnect()

