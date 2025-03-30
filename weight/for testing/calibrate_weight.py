import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.cleanup() 

GPIO.setmode(GPIO.BCM)  # Set GPIO pin mode to BCM numbering
hx = HX711(dout_pin=5, pd_sck_pin=6)

hx.zero()  # Reset the sensor

input("Place known weight on scale and press Enter...")
reading = hx.get_data_mean(readings=100)
print(f"Raw sensor value: {reading}")

known_weight_grams = float(input("Enter known weight in grams: "))

# Calculate calibration factor
calibration_factor = reading / known_weight_grams
print(f"Calibration Factor: {calibration_factor}")

# Store calibration factor
hx.set_scale_ratio(calibration_factor)

print("\n ^|^e Calibration complete! Use this factor in the next script.\n")
