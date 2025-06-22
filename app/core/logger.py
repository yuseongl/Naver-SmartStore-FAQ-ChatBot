import csv
import datetime
import os
from core import LOG_PATH

def save_log(question: str, context: str, response: str):
    """
    Save the chat log to a CSV file.
    """
    new = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["timestamp", "question", "retrieved_context", "ai_response", "feedback"])
        writer.writerow([
            datetime.datetime.now().isoformat(),
            question,
            context,
            response,
        ])

def get_logs() -> list:
    """
    Retrieve all chat logs from the CSV file.
    
    Returns:
        list: A list of dictionaries containing the chat logs.
    """
    if not os.path.exists(LOG_PATH):
        return []

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows