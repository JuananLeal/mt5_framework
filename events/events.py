from enum import Enum
from pydantic import BaseModel
import pandas as pd

# Define differente event types

class EventType(str, Enum):
    DATA = "DATA"

class BaseEvent(BaseModel):
    event_type: EventType

    class Config:
        arbitrary_types_allowed = True # Pydantic solving pandas type of data verification

class DataEvent(BaseEvent):
    event_type: EventType = EventType.DATA
    symbol: str
    data: pd.Series