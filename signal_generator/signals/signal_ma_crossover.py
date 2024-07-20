from events.events import DataEvent,SignalEvent
from data_provider.data_provider import DataProvider
from ..interfaces.signal_generator_interface import ISignalGenerator
from portfolio.portfolio import Portfolio
from order_executor.order_executor import OrderExecutor
from ..properties.signal_generator_properties import MACossoverProps


class SignalMACrossover(ISignalGenerator):

    def __init__(self, properties: MACossoverProps):

        self.timeframe = properties.timeframe
        self.fast_period = properties.fast_period if properties.fast_period > 1 else 2
        self.slow_period = properties.slow_period if properties.slow_period > 2 else 3

        if self.fast_period >= self.slow_period:
            raise Exception("ERROR: Fast period ({self.fast_period}) is higher than lower period ({self.slow_period})")


    def generate_signal(self, data_event: DataEvent, data_provider: DataProvider, portfolio: Portfolio, order_executor: OrderExecutor) -> SignalEvent:
        
        #Get symbol from event
        symbol = data_event.symbol

        #Get data needed to generate moving averages
        bars = data_provider.get_latest_closed_bars(symbol, self.timeframe,self.slow_period)

        # We recover the positions opened by this strategy in the symbol where we have had the Data Event.
        open_positions = portfolio.get_number_of_strategy_open_positions_by_symbol(symbol)


        #Indicators value
        fast_ma = bars['close'][-self.fast_period:].mean()
        slow_ma = bars['close'].mean()

        #Check buy signal
        if open_positions['LONG'] == 0 and fast_ma > slow_ma:
            if open_positions['SHORT'] > 0:
                # If we have a long order but there is an sell position opened. We have to close it before open a buy position
                order_executor.close_strategy_short_positions_by_symbol(symbol)
            signal = "BUY"
        #Check sell signal
        elif open_positions['SHORT'] == 0 and slow_ma > fast_ma:
            if open_positions['LONG'] > 0:
                # If we have a short order but there is an buy position opened. We have to close it before open a sell position
                order_executor.close_strategy_long_positions_by_symbol(symbol)
            signal = "SELL"
        else:
            signal = ""

        #Generate SignalEvent if signal variable is not empty
        if signal != "":

            signal_event = SignalEvent(symbol=symbol,
                           signal= signal,
                           target_order="MARKET",
                           target_price=0.0,
                           magic_number=portfolio.magic,
                           sl=0.0,
                           tp=0.0
                           )
            
            return signal_event