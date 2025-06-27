import csv
import datetime
import os


class Logger:
    def __init__(self, log_path: str):
        self.log_path = log_path

    def save_log(self, question: str, context: str, response: str):
        """
        Save the chat log to a CSV file.
        """
        new = not os.path.exists(self.log_path)
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new:
                writer.writerow(
                    [
                        "timestamp",
                        "question",
                        "retrieved_context",
                        "ai_response",
                        "feedback",
                    ]
                )
            writer.writerow(
                [
                    datetime.datetime.now().isoformat(),
                    question,
                    context,
                    response,
                ]
            )

    def get_logs(self) -> list:
        """
        Retrieve all chat logs from the CSV file.

        Returns:
            list: A list of dictionaries containing the chat logs.
        """
        if not os.path.exists(self.log_path):
            return []

        with open(self.log_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        return rows
