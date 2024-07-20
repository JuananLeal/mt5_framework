from typing import Protocol
from events.events import DataEvent, SignalEvent
from data_provider.data_provider import DataProvider
from portfolio.portfolio import Portfolio
from order_executor.order_executor import OrderExecutor


# Interface creation
class ISignalGenerator(Protocol):
    
    def generate_signal(self, data_event: DataEvent, data_provider: DataProvider, portfolio: Portfolio, order_executor: OrderExecutor) -> SignalEvent | None:
        ...
