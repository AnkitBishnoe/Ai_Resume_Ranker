import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def save_screening(data: dict):
    """Saves a screening result to history.json."""
    history = load_history()
    
    # Add timestamp
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    history.append(data)
    
    # Keep only the last 20 records to avoid huge files
    if len(history) > 20:
        history = history[-20:]
        
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Error saving history: {e}")

def load_history() -> list:
    """Loads screening history from history.json."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def clear_history():
    """Clears screening history by removing or emptying the history.json."""
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
    except Exception as e:
        print(f"Error clearing history: {e}")

