from pydantic import BaseModel

class BaseSignalProps(BaseModel):
    pass

class MACossoverProps(BaseSignalProps):
    timeframe: str
    fast_period: int
    slow_period: int