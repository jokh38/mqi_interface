import json
from datetime import datetime
from enum import Enum

class CustomJsonEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that handles special types like Enum and datetime.
    """
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        return super().default(o)
