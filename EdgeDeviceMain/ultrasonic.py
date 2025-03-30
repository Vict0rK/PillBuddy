import RPi.GPIO as GPIO
import time
import statistics

# GPIO Setup
GPIO.setwarnings(False)
ULTRASONIC_TRIG = 23
ULTRASONIC_ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(ULTRASONIC_TRIG, GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO, GPIO.IN)


# Number of samples for averaging
NUM_SAMPLES = 5

def measure_distance():
    """Measures distance using the ultrasonic sensor and smooths the reading."""
    distances = []

    for _ in range(NUM_SAMPLES):
        GPIO.output(ULTRASONIC_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(ULTRASONIC_TRIG, False)

        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(ULTRASONIC_ECHO) == 0:
            start_time = time.time()

        while GPIO.input(ULTRASONIC_ECHO) == 1:
            stop_time = time.time()

        elapsed_time = stop_time - start_time
        distance = (elapsed_time * 34300) / 2
        distances.append(distance)

        time.sleep(0.05)  # Short delay to prevent sensor interference

    # Use median or mean for smoothing
    smoothed_distance = statistics.median(distances)  # More resistant to outliers
    # smoothed_distance = sum(distances) / len(distances)  # Simple average (optional)

    print(f"Smoothed Distance: {smoothed_distance:.2f} cm")  # Debugging print
    return smoothed_distance



# while True:
    # measure_distance()
