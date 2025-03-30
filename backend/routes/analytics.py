from flask import Blueprint, jsonify, request
from models.analytics import Analytics
from models.medication import Medication
from models.patient import Patient
from datetime import datetime, timedelta

# Create the analytics blueprint
analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/weekly-adherence", methods=["GET"])
def get_weekly_adherence():
    """
    Calculate weekly medication adherence based on logs.
    Adherence is determined by taking correct medication within ±1 hour of scheduled times.
    
    Returns:
        JSON response with weekly adherence percentages
    """
    try:
        from models.log import Log
        from models.medication import Medication
        from models.patient import Patient
        from datetime import datetime, timedelta

        # Get the latest patient
        patient = Patient.get_latest()
        if not patient:
            return jsonify({"error": "No patient found"}), 404

        # Get all medications for the patient
        meds = Medication.get_by_patient_id(patient["_id"])
        
        # Collect all unique medication times across all medications
        all_med_times = []
        for med in meds:
            all_med_times.extend(med.get('timings', []))
        
        # Convert times to datetime format
        expected_times = []
        for time_str in all_med_times:
            hours, minutes = map(int, time_str.split(':'))
            expected_times.append((hours, minutes))

        # Get today's date and calculate the 7-day window
        today = datetime.now()
        start_date = today - timedelta(days=6)  # Last 7 days including today

        # Get all logs for correct medication
        logs = Log.get_all()
        
        # Filter and process logs within the 7-day window
        adherence_logs = []
        for log in logs:
            if log.get('action') == 'Medication Taken Correctly':
                try:
                    log_time = datetime.fromisoformat(log['time'])
                    
                    # Check if log is within the last 7 days
                    if start_date <= log_time <= today:
                        adherence_logs.append(log_time)
                
                except Exception as e:
                    print(f"Error processing log: {e}")

        # Calculate daily adherence
        daily_adherence = {}
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            day_logs = [
                log for log in adherence_logs 
                if log.date() == current_date.date()
            ]
            
            # Check each expected medication time
            day_adherence = 0
            total_expected_doses = len(expected_times)
            
            for expected_hour, expected_minute in expected_times:
                # Check if any log is within ±1 hour of expected time
                dose_taken = any(
                    abs((log.hour * 60 + log.minute) - (expected_hour * 60 + expected_minute)) <= 60 
                    for log in day_logs
                )
                
                if dose_taken:
                    day_adherence += 1
            
            # Calculate percentage for this day
            daily_adherence[current_date.date()] = (day_adherence / total_expected_doses * 100) if total_expected_doses > 0 else 0

        # Format the results for the last 7 days
        adherence_data = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "adherence": round(percentage, 2)
            } 
            for date, percentage in daily_adherence.items()
        ]

        return jsonify(adherence_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@analytics_bp.route("/next-medication", methods=["GET"])
def get_next_medication():
    """
    Determine the next scheduled medication time
    """
    try:
        from models.medication import Medication
        from models.patient import Patient
        from datetime import datetime, timedelta

        # Get the latest patient
        patient = Patient.get_latest()
        if not patient:
            return jsonify({"nextMedicationTime": "N/A"}), 200

        # Get all medications for the patient
        meds = Medication.get_by_patient_id(patient["_id"])
        
        # Get current time
        current_time = datetime.now()
        today = current_time.date()

        # Collect all medication times for today and tomorrow
        upcoming_med_times = []
        for med in meds:
            for time_str in med.get('timings', []):
                # Convert time string to datetime for today and tomorrow
                hours, minutes = map(int, time_str.split(':'))
                today_time = datetime.combine(today, datetime.min.time().replace(hour=hours, minute=minutes))
                
                # Add times that are in the future
                if today_time > current_time:
                    upcoming_med_times.append(today_time)

        # Find the earliest upcoming medication time
        if upcoming_med_times:
            next_medication = min(upcoming_med_times)
            return jsonify({
                "nextMedicationTime": next_medication.strftime("%I:%M %p")
            }), 200
        
        return jsonify({"nextMedicationTime": "N/A"}), 200
    
    except Exception as e:
        print(f"Error in next medication calculation: {e}")
        return jsonify({"nextMedicationTime": "N/A"}), 200
@analytics_bp.route("/missed-doses", methods=["GET"])
def get_missed_doses():
    """
    Calculate missed doses for today based on medication schedule and logs
    """
    try:
        from models.log import Log
        from models.medication import Medication
        from models.patient import Patient
        from datetime import datetime, timedelta

        # Get the latest patient
        patient = Patient.get_latest()
        if not patient:
            return jsonify({"missedDosesToday": 0}), 200

        # Get all medications for the patient
        meds = Medication.get_by_patient_id(patient["_id"])
        
        # Get current time
        current_time = datetime.now()
        today = current_time.date()

        # Collect all medication times for today
        missed_med_times = []
        for med in meds:
            for time_str in med.get('timings', []):
                # Convert time string to datetime for today
                hours, minutes = map(int, time_str.split(':'))
                expected_time = datetime.combine(today, datetime.min.time().replace(hour=hours, minute=minutes))
                
                # If expected time is before current time
                if expected_time < current_time:
                    missed_med_times.append(expected_time)

        # Get all logs for today with 'Medication Taken Correctly' action
        logs = Log.get_all()
        correct_medication_logs = [
            log for log in logs 
            if log.get('action') == 'Medication Taken Correctly' 
            and datetime.fromisoformat(log['time']).date() == today
        ]

        # Count missed doses
        missed_doses = 0
        for expected_time in missed_med_times:
            # Check if there's a log for this time within a 2-hour window
            dose_taken = any(
                abs((datetime.fromisoformat(log['time']) - expected_time).total_seconds()) <= 2 * 3600  # 2 hours window
                for log in correct_medication_logs
            )
            
            # If no log found, increment missed doses
            if not dose_taken:
                missed_doses += 1

        return jsonify({"missedDosesToday": missed_doses}), 200
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error in missed doses calculation: {e}")
        return jsonify({"missedDosesToday": 0}), 200