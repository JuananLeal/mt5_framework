from data_provider.data_provider import DataProvider
from signal_generator.interfaces.signal_generator_interface import ISignalGenerator
from position_sizer.position_sizer import PositionSizer
from risk_manager.risk_manager import RiskManager
from order_executor.order_executor import OrderExecutor
from notifications.notifications import NotificationService

from events.events import DataEvent, SignalEvent, SizingEvent, OrderEvent, ExecutionEvent, PlacedPendingOrderEvent

from typing import Dict, Callable
import queue
import time
from utils.utils import Utils


class TradingDirector():

    def __init__(self,
                 events_queue: queue.Queue,
                 data_provider: DataProvider, 
                 signal_generator: ISignalGenerator, 
                 position_sizer: PositionSizer, 
                 risk_manager: RiskManager,
                 order_executor: OrderExecutor,
                 notification_service: NotificationService):

        self.events_queue = events_queue

        # References to modules
        self.DATA_PRIVIDER = data_provider
        self.SIGNAL_GENERATOR = signal_generator
        self.POSITION_SIZER = position_sizer
        self.RISK_MANAGER = risk_manager
        self.ORDER_EXECUTOR = order_executor
        self.NOTIFICATIONS = notification_service

        # Trading Controler
        self.continue_trading: bool = True

        # Event handler
        self.event_handler: Dict[str, Callable] = {
            "DATA": self._handle_data_event,
            "SIGNAL": self._handle_signal_event,
            "SIZING": self._handle_sizing_event,
            "ORDER": self._handle_order_event,
            "EXECUTION": self._handle_execution_event,
            "PENDING": self._handle_pending_order_event
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
                    handler = self.event_handler.get(event.event_type, self._handle_unknowk_event)
                    handler(event)
                else:
                    self._handle_none_event(event)
            
            time.sleep(0.01)

    def _handle_data_event(self, event: DataEvent):
        # Manage DataEvent type events
        print(f"{Utils.dateprint()} - Received new DATA EVENT from {event.symbol} - Last close prize: {event.data.close}")
        self.SIGNAL_GENERATOR.generate_signal(event)

    def _handle_signal_event(self,event: SignalEvent):
        #Signal event processing
        print(f"{Utils.dateprint()} - SIGNAL EVENT received {event.signal} for {event.symbol}")
        self.POSITION_SIZER.size_signal(event)

    def _handle_sizing_event(self, event: SizingEvent):
        print(f"{Utils.dateprint()} - SIZING EVENT received {event.signal} with volume {event.volume} for {event.symbol}")
        self.RISK_MANAGER.assess_order(event)

    def _handle_order_event(self, event: OrderEvent):
        print(f"{Utils.dateprint()} - ORDER EVENT received {event.signal} with volume {event.volume} for {event.symbol}")
        self.ORDER_EXECUTOR.execute_order(event)

    def _handle_execution_event(self, event: ExecutionEvent):
        print(f"{Utils.dateprint()} - EXECUTION EVENT received {event.signal} in {event.symbol} and volume {event.volume} with price {event.fill_price}")
        self._process_execution_or_pending_events(event)

    def _handle_pending_order_event(self, event: PlacedPendingOrderEvent):
        print(f"{Utils.dateprint()} - PLACE PENDING ORDER EVENT received {event.signal} {event.target_order} with volume {event.volume} for {event.symbol} with price {event.target_price}")
        self._process_execution_or_pending_events(event)

    def _process_execution_or_pending_events(self, event: ExecutionEvent | PlacedPendingOrderEvent):
        # Code for telegram messages
        if isinstance(event, ExecutionEvent):
            self.NOTIFICATIONS.send_notification(tittle=f"{event.symbol} - MARKET ORDER", message=f"Executed MARKET ORDER {event.signal} in {event.symbol} and volume {event.volume} with price {event.fill_price}")
        elif isinstance(event, PlacedPendingOrderEvent):
            self.NOTIFICATIONS.send_notification(tittle=f"{event.symbol} - PENDING PLACED", message=f"Placed PENDING ORDER {event.signal} {event.target_order} with volume {event.volume} for {event.symbol} with price {event.target_price}")
        else:
            pass

    def _handle_none_event(self, event):
        print(f"{Utils.dateprint()} - Error: NULL event. Stoping framework")
        self.continue_trading = False
    
    def _handle_unknowk_event(self, event):
        print(f"{Utils.dateprint()} - Error: Unknown event. Stoping framework. Event: {event}")
        self.continue_trading = False
