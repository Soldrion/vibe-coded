import json
import os
from typing import List
from tracker_model import TrackedItem

STORAGE_FILE = "tracked_items.json"


def save_items(items: List[TrackedItem]):
    with open(STORAGE_FILE, "w") as f:
        json.dump([item.to_dict() for item in items], f, indent=2)


def load_items() -> List[TrackedItem]:
    if not os.path.exists(STORAGE_FILE):
        return []
    with open(STORAGE_FILE, "r") as f:
        data = json.load(f)
        return [TrackedItem.from_dict(item) for item in data]
