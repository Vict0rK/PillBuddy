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

### Facial Recognition

### Buzzer

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

### Weight Sensor


## Test Experiments and Results
### Text Detection

| Experiment                                      | Subject                                      | Observation                                    |
| ---------------------------------------------- | -------------------------------------------- | --------------------------------------------- |
| Check if lighting affects text detection       | Placing it under a well-lit area            | Text detected 18 out of 20 labels      |
|                                                | Placing it under a shaded area              | Text detected 9 out of 20 labels     |
| Check if image resolution affects accuracy     | `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)` <br> `cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)`  | Text detected 18 out of 20 labels        |
|                                                | `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)` <br> `cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 700)` | Text detected 10 out of 20 labels       |



## Team Responsibilities


