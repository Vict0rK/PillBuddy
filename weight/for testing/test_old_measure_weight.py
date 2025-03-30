import time
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.cleanup() 

# Initialize HX711 Weight Sensor
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=5, pd_sck_pin=6)
CALIBRATION_FACTOR = -1197.7205882352941  # Replace with your actual calibration factor
hx.set_scale_ratio(CALIBRATION_FACTOR)

def get_weight():
 """Measures and returns the current weight."""
 try:
	 weight = hx.get_weight_mean(readings=100)
	 return round(weight, 2)
 except Exception as e:
	 print(f"Error reading weight: {e}")
	 return None

def monitor_weight():
 """Continuously monitors weight and prints/logs detected values."""
 print("\nWeight Measurement Started...\n")

 try:
	 while True:
		 weight = get_weight()
		 if weight is not None:
			 print(f"Current Weight: {weight:.2f} g")
		 else:
			 print("Error: Could not read weight.")
		 time.sleep(2)  # Adjust polling interval

 except KeyboardInterrupt:
	 print("\nExiting weight sensor...")
	 GPIO.cleanup()

if __name__ == "__main__":
 monitor_weight()  # If run as a standalone script, it will monitor weight continuously.
