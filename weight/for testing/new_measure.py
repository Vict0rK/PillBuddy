import time
import RPi.GPIO as GPIO
from hx711 import HX711

# Initialize HX711 Weight Sensor
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=5, pd_sck_pin=6)
CALIBRATION_FACTOR = 517.8137254901961  # Replace with your actual calibration >
hx.set_scale_ratio(CALIBRATION_FACTOR)

try:
	while True:
		weight = hx.get_weight_mean(readings=10)
		print(f"weight: {weight:.2f} g")
except KeyboardInterrupt:
	print("Exiting...")
	GPIO.cleanup()


