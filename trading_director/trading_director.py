from data_provider.data_provider import DataProvider
from signal_generator.interfaces.signal_generator_interface import ISignalGenerator
from position_sizer.position_sizer import PositionSizer
from risk_manager.risk_manager import RiskManager

from events.events import DataEvent, SignalEvent, SizingEvent, OrderEvent

from typing import Dict, Callable
import queue
import time
from datetime import datetime


class TradingDirector():

    def __init__(self,
                 events_queue: queue.Queue,
                 data_provider: DataProvider, 
                 signal_generator: ISignalGenerator, 
                 position_sizer: PositionSizer, 
                 risk_manager: RiskManager):

        self.events_queue = events_queue

        # References to modules
        self.DATA_PRIVIDER = data_provider
        self.SIGNAL_GENERATOR = signal_generator
        self.POSITION_SIZER = position_sizer
        self.RISK_MANAGER = risk_manager

        # Trading Controler
        self.continue_trading: bool = True

        # Event handler
        self.event_handler: Dict[str, Callable] = {
            "DATA": self._handle_data_event,
            "SIGNAL": self._handle_signal_event,
            "SIZING": self._handle_sizing_event,
            "ORDER": self._handle_order_event
        }

    def run(self) -> None:

        # Main loop definition
        while self.continue_trading:
            try:
                event = self.events_queue.get(block=False) # FIFO
            except queue.Empty:
                self.DATA_PRIVIDER.check_for_new_data()

            else:
                if event is not None:
                    handler = self.event_handler.get(event.event_type)
                    handler(event)
                else:
                    self.continue_trading = False
                    print(f"Error: NULL event. Stoping framework")
            
            time.sleep(0.01)

    def _handle_data_event(self, event: DataEvent):
        # Manage DataEvent type events
        print(f"{self._dateprint()} - Received new DATA EVENT from {event.symbol} - Last close prize: {event.data.close}")
        self.SIGNAL_GENERATOR.generate_signal(event)

    def _dateprint(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

    def _handle_signal_event(self,event: SignalEvent):
        #Signal event processing
        print(f"{self._dateprint()} - SIGNAL EVENT received {event.signal} for {event.symbol}")
        self.POSITION_SIZER.size_signal(event)

    def _handle_sizing_event(self, event: SizingEvent):
        print(f"{self._dateprint()} - SIZING EVENT received {event.signal} with volume {event.volume} for {event.symbol}")
        self.RISK_MANAGER.assess_order(event)

    def _handle_order_event(self, event: OrderEvent):
        print(f"{self._dateprint()} - ORDER EVENT received {event.signal} with volume {event.volume} for {event.symbol}")

        