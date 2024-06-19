import queue
from typing import Dict, Callable
from data_provider.data_provider import DataProvider
from events.events import DataEvent
import time


class TradingDirector():

    def __init__(self,events_queue: queue.Queue, data_provider: DataProvider):

        self.events_queue = events_queue

        # References to modules
        self.DATA_PRIVIDER = data_provider

        # Trading Controler
        self.continue_trading: bool = True

        # Event handler
        self.event_handler: Dict[str, Callable] = {
            "DATA" : self._handle_data_event,
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
        print(f"{event.data.name} - Receibed new data from {event.symbol} - Last close prize: {event.data.close}")