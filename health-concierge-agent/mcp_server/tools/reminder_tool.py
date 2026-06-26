import os
import json
from datetime import datetime
from .audit import log_audit

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
FILE_PATH = os.path.join(DATA_DIR, "reminders.json")

def set_medication_reminder(medication_name: str, time_str: str, frequency: str) -> str:
    """
    Saves a reminder schedule to data/reminders.json.
    """
    log_audit("set_medication_reminder")
    reminders = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            try:
                reminders = json.load(f)
            except json.JSONDecodeError:
                pass
                
    entry = {
        "medication_name": medication_name,
        "time_str": time_str,
        "frequency": frequency,
        "created_at": datetime.now().isoformat()
    }
    
    reminders.append(entry)
    
    with open(FILE_PATH, "w") as f:
        json.dump(reminders, f, indent=2)
        
    return f"Reminder set: {medication_name} at {time_str} ({frequency})."

def get_due_reminders() -> str:
    """
    Returns any reminders due within the next hour.
    (Simplified logic for demonstration purposes)
    """
    log_audit("get_due_reminders")
    if not os.path.exists(FILE_PATH):
        return "No reminders set."
        
    with open(FILE_PATH, "r") as f:
        try:
            reminders = json.load(f)
        except json.JSONDecodeError:
            return "Failed to parse reminders."
            
    # For demo purposes, we just return the full list of reminders as a summary.
    if not reminders:
        return "No active reminders."
        
    return "Current Active Reminders:\n" + json.dumps(reminders, indent=2)
