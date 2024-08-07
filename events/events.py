from enum import Enum
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

# Define differente event types

class EventType(str, Enum):
    DATA = "DATA"
    SIGNAL = "SIGNAL"
    SIZING = "SIZING"
    ORDER = "ORDER"
    EXECUTION = "EXECUTION"
    PENDING = "PENDING"

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    
class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class BaseEvent(BaseModel):
    event_type: EventType

    class Config:
        arbitrary_types_allowed = True # Pydantic solving pandas type of data verification

class DataEvent(BaseEvent):
    event_type: EventType = EventType.DATA
    symbol: str
    data: pd.Series

class SignalEvent(BaseEvent):
    event_type: EventType = EventType.SIGNAL
    symbol: str
    signal: SignalType 
    target_order: OrderType
    target_price: float
    magic_number: int
    sl : float
    tp: float

class SizingEvent(BaseEvent):
    event_type : EventType = EventType.SIZING
    symbol: str
    signal: SignalType 
    target_order: OrderType
    target_price: float
    magic_number: int
    sl : float
    tp: float
    volume: float

class OrderEvent(BaseEvent):
    event_type: EventType = EventType.ORDER
    symbol: str
    signal: SignalType 
    target_order: OrderType
    target_price: float
    magic_number: int
    sl : float
    tp: float
    volume: float

class ExecutionEvent(BaseEvent):
    event_type: EventType = EventType.EXECUTION
    symbol: str
    signal: SignalType
    fill_price: float
    fill_time: datetime
    volume : float

class PlacedPendingOrderEvent(BaseEvent):
    event_type: EventType = EventType.PENDING
    symbol: str
    signal: SignalType 
    target_order: OrderType
    target_price: float
    magic_number: int
    sl : float
    tp: float
    volume: float