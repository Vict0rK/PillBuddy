# PillBuddy Project

## Overview
**PillBuddy** is a project aimed at managing medication adherence and monitoring inventory using a smart medication box. This project involves both frontend and backend components to provide real-time medication tracking, alerts, and data analysis for better medication management.

### Technologies Used:
- **Frontend**: React.js, Tailwind CSS
- **Backend**: Flask, Python
- **Database**: MongoDB
- **Data Visualization**: Chart.js for analytics display
- **Deployment**: Local setup

## Prerequisites
Before setting up the project, you will need the following tools installed on your machine:

- **Node.js** (for the frontend)
- **npm** or **yarn** (package manager for Node.js)
- **Python 3** (for the backend)
- **pip** (Python package installer)
- **MongoDB** (locally or via Atlas for cloud database)
- **Git** (to clone the repository and track changes)

## Setup Instructions

### Step 1: Clone the Repository
Clone the project repository to your local machine:

```bash
git clone https://github.com/Vict0rK/PillBuddy.git
cd PillBuddy
```

### Step 2: Backend Setup

#### 2.1 Install Python Dependencies
1. Create a virtual environment:
```bash
python -m venv venv
```
2. Activate the virtual environment:
- On Windows:
```bash
.\venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```
3. Install the required Python packages:
 ```bash
  pip install -r backend/requirements.txt
```

#### 2.2 MongoDB Setup
1. Install MongoDB locally or use MongoDB Atlas for a cloud setup.
2. Run the backend app:
```bash
cd backend
python app.py
```
This will start the Flask API on http://localhost:5000.


### Step 3: Frontend Setup
#### 3.1 Install Frontend Dependencies
1. Navigate to the frontend folder:
```bash
cd frontend
```
2. Install the required npm packages:
```bash
npm install
```
#### 3.2 Run the Frontend
1. Start the React development server:
```bash
npm start
```
This will run the frontend on http://localhost:3000.


## Project Components Implementation
### Ultrasonic Sensor
- This implementation uses the HC-SR04 ultrasonic sensor to detect the distance between the sensor and the medication box lid, helping determine whether the box is opened or closed.
- We are using RPi.GPIO to control the TRIG and ECHO pins, and calculate distance based on the time taken for an ultrasonic pulse to return.
- When the buzzer alert is triggered, the ultrasonic sensor begins continuous distance measurement to check for box status:
  - If the distance is greater than 10cm, the box is considered opened.
  - If the distance drops below 10cm again, it is considered closed.
- MQTT is used to publish box state updates (Box Opened / Box Closed) to the web dashboard in real time.
- The sensor also plays a role in managing the facial recognition process:
  - Starts face recognition when the box is opened
  - Terminates face recognition once the box is closed again

### Facial Recognition
- The facial recognition module performs real-time facial recognition using a Raspberry Pi and a camera to identify authorized or unknown indivuduals. It integrates with MQTT to send alerts when an unknown person is detected.
- We are using the face_recognition library from python to detect and match faces, and OpenCV to capture and annotate frames from the camera.
- Known face encodings are loaded from a pickle file and compared with detected faces in each frame.
- If an authorized face is recognized, no alerts will be triggered and the user can proceed with using the medication box normally.
- If an unknown face is detected, a buzzer alert is triggered, and a snapshot is taken and sent to the web server, triggering an additional SMS notification.
- The image is encoded in base64 and sent as a JSON payload to an MQTT topic to notify the server.

### Buzzer
- This implementation uses a passive buzzer to alert patients when it is time to take their medication or when an unauthorised user is taking the medication.
- We are using RPi.GPIO's PWM feature to activate the buzzer in periodic pulses (on-off beeping) for better audibility.
- The buzzer is triggered in the following scenarios:
  - When the current time matches a scheduled medication time, it starts beeping until the ultrasonic sensor detects that the box has been opened.
  - When facial recognition detects an unrecognized face, the buzzer immediately beeps as an alert for potential unauthorized access.
- This dual-purpose alerting system improves both medication adherence and physical access security.
- MQTT works alongside this setup to:
  - Monitor whether the alert condition is resolved (i.e., box opened or unauthorised user detected)
  - Help trigger follow-up actions like SMS alerts and logging to the dashboard

### Text Recognition
- This implementation performs real-time text detection using a webcam to identify medication names. The process is integrated with MQTT messaging to communicate with an IoT device, alerting caregivers when incorrect medication is taken.
- We are using OpenCV which captures and processes frames from the webcam. Pytesseract which uses Optical Character Recognition (OCR) to extract text from images.
- When the web cam is turned on, it captures frames using OpenCV and does preprocessing to improve OCR Accuracy:
  - convert to grayscale
  - Blurred using GaussianBlur to reduce noise
  - Thresholding applied to highlight text
- Tesseract will extract text and conver to lower case for comparison
- MQTT is also used to publish/receive any alerts/updates between web server

### RFID 
- This implementation utilizes the MFRC522 RFID sensor to scan for medication tags when the box is opened.
- The sensor communicates with the Raspberry Pi through SPI (Serial Peripheral Interface), which allows efficient communication between the sensor and the Raspberry Pi.
- The sensor continuously scans for RFID tags inside the box, ensuring the correct medication is detected:
  - If the correct RFID tag is not found in the box, the system assumes that the patient has taken the correct medication, confirming proper medication adherence.
  - If an incorrect RFID tag is detected, an alert is triggered, notifying the system and caregivers of potential issues.
 - MQTT protocol is used to communicate the medication status to the web dashboard in real time, ensuring that any discrepancies or issues with medication intake are promptly addressed.

### Weight Sensor
- This system uses the HX711 load cell to measure the weight of the medication inside the box.
- The load cell detects weight changes whenever the box is opened or interacted with, helping to track whether the medication has been taken.
  - The sensor sends data to the Raspberry Pi, which processes the weight difference before and after the box is interacted with.
  - The system then compares the weight change to the expected dosage, ensuring that the correct amount of medication has been removed.
  - If the weight difference deviates significantly from the expected dosage, an alert is generated.
- MQTT is employed to send dosage alerts to the web dashboard,


## Test Experiments and Results

### Ultrasonic Sensor
| Experiment                              | Subject                                      | Observation                               |
| ----------------------------------------| -------------------------------------------- | ------------------------------------------|
| Check distance detection sensitivity    | Object placed at 5cm, 10cm, and 20cm from sensor | Sensor accurately measured distance within ±1 cm |
| Check false triggers                    | No object in front of sensor                 | Sensor remained stable, no false readings  |
| Check box open/close threshold          | Lid opened beyond 10 cm                      | Sensor consistently triggered “Box Opened” event |
| Check effect of smoothing               | Using median filter over 5 readings          | Distance readings were smoother with fewer false values |


### Facial Recognition
| Experiment                                      | Subject                                                                 | Observation                                        |
| ---------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------- |
| Check if lighting affects facial recognition   | Placing face under a well-lit area                                      | Faces correctly detected 19 out of 20 attempts     |
|                                                | Placing face under a dimly lit area                                     | Faces correctly detected 17 out of 20 attempts     |
| Check if frame resizing affects accuracy       | `cv_scaler = 5`                                                         | Faces correctly detected 20 out of 20 attempts. Better FPS and accuracy    |
|                                                | `cv_scaler = 15`                                                        | Faces correctly detected 17 out of 20 attempts. Lower FPS and accuracy   |
|                                                | `cv_scaler = 10`                                                        | Faces correctly detected 20 out of 20 attempts   |
| Check if face distance affects recognition     | Face placed within 1 meter of camera `cv_scaler = 5`                                     | Faces correctly detected 20 out of 20 attempts     |
|                                                | Face placed beyond 2 meters `cv_scaler = 5`                                           | Faces correctly detected 0 out of 20 attempts      |
|                                                | Face placed within 1 meter of camera `cv_scaler = 15`                                           | Faces correctly detected 20 out of 20 attempts      |
|                                                | Face placed beyond 2 meters `cv_scaler = 15`                                           | Faces correctly detected 20 out of 20 attempts      |
|                                                | Face placed within 1 meters of camera `cv_scaler = 10`                                           | Faces detected 20 out of 20 attempts      |
|                                                | Face placed beyond 2 meters `cv_scaler = 10`                                           | Faces correctly detected 16 out of 20 attempts      |
| Check if face angle affects recognition        | Face looking straight at camera                                         | Faces correctly detected 20 out of 20 attempts     |
|                                                | Face tilted ~30° sideways                                               | Faces correctly detected 12 out of 20 attempts     |
| Check MQTT payload sent on unknown detection   | MQTT broker active and reachable                                        | JSON payload with image sent successfully          |
|                                                | MQTT broker offline                                                     | Image not sent, no alert triggered                 |


### Buzzer
| Experiment                              | Subject                                      | Observation                               |
| ----------------------------------------| -------------------------------------------- | ------------------------------------------|
| Check buzzer activation on schedule     | System time matches medication schedule      | Buzzer beeps at correct time               |
| Check buzzer on unauthorized access     | Unknown face shown during facial recognition | Buzzer beeped immediately after detection  |
| Check buzzer duration and audibility    | Let buzzer run for 30s in a quiet room       | Sound was clear and loud at 3–5 meter range |

### Text Detection

| Experiment                                      | Subject                                      | Observation                                    |
| ---------------------------------------------- | -------------------------------------------- | --------------------------------------------- |
| Check if lighting affects text detection       | Placing it under a well-lit area            | Text detected 18 out of 20 labels      |
|                                                | Placing it under a shaded area              | Text detected 9 out of 20 labels     |
| Check if image resolution affects accuracy     | `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)` <br> `cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)`  | Text detected 18 out of 20 labels        |
|                                                | `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)` <br> `cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 700)` | Text detected 10 out of 20 labels       |

### RFID

| Experiment                                       | Subject                                                | Observation                                         |
| ------------------------------------------------ | ------------------------------------------------------ | --------------------------------------------------- |
| Check RFID detection accuracy                    | Scan RFID tags with known and unknown IDs               | Correct RFID tag detected; incorrect or unknown tags not recognized |
| Check RFID tag read time                         | Scan a known RFID tag multiple times in quick succession | RFID tag consistently detected in less than 1 second |
| Check for RFID tag removal                       | Remove RFID tag and wait for 3 cycles                   | Sensor detects missing tag after 3 cycles |
| Check RFID scan sensitivity in varying conditions | Place RFID tag at different angles or distances         | RFID detection still accurate at a range of up to 5 cm |
| Check behavior when no RFID tag is detected      | No RFID tag in the box                                 | Sensor accurately detects absence |

### Weight Sensor

| Experiment                                       | Subject                                               | Observation                                         |
| ------------------------------------------------ | ----------------------------------------------------- | --------------------------------------------------- |
| Check weight measurement accuracy                | Weigh known objects (e.g., 10g, 50g, 100g items)       | Weight measurements matched actual values within ±2g |
| Check weight sensor response time               | Measure weight after placing items in the box          | Response time consistently under 5 second for each measurement |
| Check weight stability during box open/close     | Box opened and closed with known dosage inside         | Weight consistently measured during open and closed states |
| Check tolerance for weight variation             | Compare measured weight with expected dosage (e.g., 50g ± 5g) | Measured weight was within the acceptable tolerance range |
| Check weight sensor accuracy with varying conditions | Place items of different shapes and materials inside the box | Consistent weight measurements regardless of material type (plastic, metal, etc.) |


## Team Responsibilities

| Team Member                              | Responsibility                                      | 
| ----------------------------------------| -------------------------------------------- |
| KONG TENG FOONG VICTOR                  |        |
| LAM JUN XIAN, AARON                     |  - Designed and implemented facial recognition module. - Modularised ultrasonic and buzzer into modules. - Integrated ultrasonic, buzzer, and facial recognition modules to trigger/deactivate functions and publish MQTT messages to other Pis. - Implemented smoothing and calibration of ultrasonic sensor module. - Implemented medication box setup (publishing information to edge pis) from web server. | 
| LOW YI SAN                              |  - Developed and implemented the web dashboard using React (frontend) and Flask (backend).<br> - Integrated MongoDB Atlas for data storage and management.<br>  - Created APIs for medication box setup, logs, weekly adherence graph, and statistics.<br> - Designed and implemented user interface features for caregivers to manage medication schedules and monitor adherence.     |
| MICHELLE MAGDALENE TRISOERANTO          |  - Developed and tested the buzzer notification system <br> - Implemented the ultrasonic sensor for box state detection <br> - Designed and structured the initial alert logic involving Twilio, MQTT messaging, and sensor integration <br> - Assisted in the construction of the physical box prototype <br> - Assisted in refining frontend dashboard and notification features for improved UX                                            |
| NADHIRAH BINTI AYUB KHAN                |        |
