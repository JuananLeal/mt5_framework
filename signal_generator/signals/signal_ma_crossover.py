from events.events import DataEvent,SignalEvent
from data_provider.data_provider import DataProvider
from ..interfaces.signal_generator_interface import ISignalGenerator

import pandas as pd
from queue import Queue


class SignalMACrossover(ISignalGenerator):

    def __init__(self,events_queue: Queue, data_provider: DataProvider, timeframe:str, fast_period:int, slow_period: int):
        
        self.events_queue = events_queue

        self.DATA_PROVIDER = data_provider

        self.timeframe = timeframe
        self.fast_period = fast_period if fast_period > 1 else 2
        self.slow_period = slow_period if slow_period > 2 else 3

        if self.fast_period >= slow_period:
            raise Exception("ERROR: Fast period ({self.fast_period}) is higher than lower period ({self.slow_period})")


    def _create_and_put_signal_event(self, symbol: str, signal: str, target_order: str, target_price: float, magic_number: int, sl: float, tp: float) -> None:

        #SignalEvent creation
        signal_event = SignalEvent(symbol=symbol,
                                   signal= signal,
                                   target_order=target_order,
                                   target_price=target_price,
                                   magic_number=magic_number,
                                   sl=sl,
                                   tp=tp
                                   )
        
        #Put SignalEvent into events queue
        self.events_queue.put(signal_event)

    def generate_signal(self, data_event: DataEvent) -> None:
        
        #Get symbol from event
        symbol = data_event.symbol

        #Get data needed to generate moving averages
        bars = self.DATA_PROVIDER.get_latest_closed_bars(symbol, self.timeframe,self.slow_period)

        #Indicators value
        fast_ma = bars['close'][-self.fast_period:].mean()
        slow_ma = bars['close'].mean()

        #Check buy signal
        if fast_ma > slow_ma:
            signal = "BUY"
        #Check sell signal
        elif slow_ma > fast_ma:
            signal = "SELL"
        else:
            signal = ""

        #Generate SignalEvent if signal variable is not empty
        if signal != "":
            self._create_and_put_signal_event(symbol=symbol,
                                              signal=signal,
                                              target_order="MARKET",
                                              target_price=0.0, #= because target_order = MARKET
                                              magic_number=1234,
                                              sl=0.0,
                                              tp= 0.0)