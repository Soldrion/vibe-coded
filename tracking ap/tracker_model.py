from dataclasses import dataclass, asdict, field
from typing import List, Dict
from datetime import date

@dataclass
class TrackedItem:
    name: str
    tags: List[str]
    due_date: str  # YYYY-MM-DD
    start_time: str  # HH:mm
    end_time: str    # HH:mm
    completed: bool
    priority: str  # Low, Medium, High
    fields: Dict[str, str]
    start_date: str = field(default_factory=lambda: "")  
    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        if "start_date" not in data:
            data["start_date"] = ""
        return TrackedItem(**data)
