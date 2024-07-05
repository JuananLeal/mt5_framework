from typing import Protocol
from events.events import DataEvent

# Interface creation
class ISignalGenerator(Protocol):
    
    def generate_signal(self, data_event:DataEvent) -> None:
        ...
