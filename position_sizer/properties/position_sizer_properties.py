from pydantic import BaseModel

class BaseSizerProps(BaseModel):
    pass

class MinSizingProps(BaseSizerProps):
    pass 

class FixedSizingProps(BaseSizerProps):
    volume: float

class RiskPctSizingProps(BaseSizerProps):
    risk_pct: float