from events.events import DataEvent
from interfaces.signal_generator_interface import ISignalGenerator
from properties.signal_generator_properties import BaseSignalProps, MACossoverProps
from .signals.signal_ma_crossover import SignalMACrossover
from data_provider.data_provider import DataProvider
from portfolio.portfolio import Portfolio
from order_executor.order_executor import OrderExecutor

from queue import Queue

class SignalGenerator(ISignalGenerator):
    
    def __init__(self, events_queue: Queue, data_provider: DataProvider, portfolio: Portfolio, order_executor: OrderExecutor, signal_properties: BaseSignalProps):
        self.events_queue = events_queue
        self.DATA_PROVIDER = data_provider
        self.PORTFOLIO = portfolio
        self.ORDER_EXECUTOR = order_executor

        self.signal_generator_method = self._get_signal_generator_method(signal_properties)

    def _get_signal_generator_method(self, signal_props: BaseSignalProps) -> ISignalGenerator:
        if isinstance(signal_props, MACossoverProps):
            return SignalMACrossover(properties=signal_props)
        else:
            raise Exception(f"ERROR: Signal method not recognized: {signal_props}")
        
    def generate_signal(self, data_event: DataEvent) -> None:
        # Recover SignalEvent 
        signal_event = self.signal_generator_method.generate_signal(data_event, self.DATA_PROVIDER, self.PORTFOLIO, self.ORDER_EXECUTOR)

        # Check SignalEvent is not None and add it to queue
        if signal_event is not None:
            self.events_queue.put(signal_event)