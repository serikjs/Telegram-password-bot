import json
import os

class DatabaseManager:
    def __init__(self, db_directory="database/db"):
        self.db_directory = db_directory
        if not os.path.exists(self.db_directory):
            os.makedirs(self.db_directory)

    def get_user_file_path(self, user_id: str) -> str:
        return os.path.join(self.db_directory, f"{user_id}.json")

    def user_exists(self, user_id: str) -> bool:
        return os.path.exists(self.get_user_file_path(user_id))

    def load_user_data(self, user_id: str) -> dict:
        file_path = self.get_user_file_path(user_id)
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_user_data(self, user_id: str, data: dict):
        file_path = self.get_user_file_path(user_id)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
