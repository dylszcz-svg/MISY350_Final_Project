import json
from pathlib import Path
 
 
class DataManager:
    def __init__(self, json_path):
        self.json_path = Path(json_path)
 
    def load(self):
        if self.json_path.exists():
            with open(self.json_path, "r") as f:
                return json.load(f)
        return []
 
    def save(self, data):
        with open(self.json_path, "w") as f:
            json.dump(data, f)
 
