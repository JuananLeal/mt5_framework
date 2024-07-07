from data_provider.data_provider import DataProvider
from events.events import SignalEvent, SizingEvent
from .interfaces.position_sizer_interface import IPositionSizer
from .properties.position_sizer_properties import MinSizingProps,FixedSizingProps,RiskPctSizingProps,BaseSizerProps
from .position_sizers.min_size_position_sizer import MinSizePositionSizer
from .position_sizers.fix_size_position_sizer import FixSizePositionSizer
from .position_sizers.risk_percentage_position_sizer import RiskPercentagePositionSizer
import MetaTrader5 as mt5
from queue import Queue

class PositionSizer(IPositionSizer):
    
    def __init__(self, events_queue: Queue, data_provider: DataProvider, sizing_properties: BaseSizerProps):
        self.events_queue = events_queue
        self.DATA_PROVIDER = data_provider
        self.position_sizing_method = self._get_position_sizing_method(sizing_properties)

    def _get_position_sizing_method(self, sizing_props: BaseSizerProps) -> IPositionSizer:
        """
        Return a position sizer instance depending on the object propertie receibed
        """
        if isinstance(sizing_props, MinSizingProps):
            return MinSizePositionSizer()
        
        elif isinstance(sizing_props, FixedSizingProps):
            return FixSizePositionSizer(properties=sizing_props)
        
        elif isinstance(sizing_props, RiskPctSizingProps):
            return RiskPercentagePositionSizer(properties=sizing_props)
        
        else:
            raise Exception(f"ERROR: Unknown sizing method: {sizing_props}")

    def _create_and_put_sizing_event(self, signal_event: SignalEvent, volume: float) -> None:

        # Create sizing event using signal event and volume
        sizing_event = SizingEvent(symbol=signal_event.symbol,
                                    signal=signal_event.signal,
                                    target_order= signal_event.target_order,
                                    target_price=signal_event.target_price,
                                    magic_number=signal_event.magic_number,
                                    sl=signal_event.sl,
                                    tp=signal_event.tp,
                                    volume=volume)
        
        # Add sizing event into event queue
        self.events_queue.put(sizing_event)

    def size_signal(self, signal_event: SignalEvent) -> None:
        
        # Get volume from sizing method 
        volume = self.position_sizing_method.size_signal(signal_event, self.DATA_PROVIDER)

        # Volume validation
        if volume < mt5.symbol_info(signal_event.symbol).volume_min:
            print(f"ERROR: Volume {volume} es lower than the lowest valid value for symbol {signal_event.symbol}")
            return 

        # Create event and add it to queue
        self._create_and_put_sizing_event(signal_event=signal_event,volume=volume)