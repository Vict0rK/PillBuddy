import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import os
import datetime

BROKER_IP = "192.168.162.29"  # Replace with Raspberry Pi 1's IP
TOPIC = "pillbuddy/sound_buzzer" 

GPIO.setwarnings(False)
BUZZER_PIN = 18  # Passive buzzer

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Set Up Passive Buzzer
pwm = GPIO.PWM(BUZZER_PIN, 1000)

	
# Function to handle incoming MQTT messages
def on_message(client , userdata, msg):
	global mqtt_message, box_open, box_state_changed
	mqtt_message = msg.payload.decode("utf-8")
	print(f"Received MQTT message: {mqtt_message}")

	# Start RFID scanning only when "box open" message is received
	if mqtt_message == "Sound":
		pwm.start(10)
		time.sleep(0.5)
		pwm.stop()
		time.sleep(0.5)



client = mqtt.Client(client_id="Subscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(BROKER_IP, 1883)
client.subscribe(TOPIC)

print("🟢 Waiting for messages...")
client.loop_forever()



