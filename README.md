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
git clone https://github.com/lowyisan/PillBuddy.git
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

