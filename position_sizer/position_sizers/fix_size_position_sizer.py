from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import FixedSizingProps


class FixSizePositionSizer(IPositionSizer):

    def __init__(self, properties: FixedSizingProps):
        
        self.fixed_volume = properties.volume
    
    def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
        
        if self.fixed_volume >= 0.0:
            # Return fixed position size
            return self.fixed_volume
        else:
            return 0.0