from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import RiskPctSizingProps
from utils.utils import Utils
import MetaTrader5 as mt5


class RiskPercentagePositionSizer(IPositionSizer):

    def __init__(self, properties: RiskPctSizingProps):
        self.risk_pct = properties.risk_pct
    
    def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:

        # Check if risk is > 0
        if self.risk_pct <= 0.0:
            print(f"ERROR: (RiskPercentagePositionSizer): Risk percentage invalid for {signal_event.symbol}")
            return 0.0
        
        #Check if Stop Loss != 0
        if signal_event.sl <= 0.0:
            print(f"ERROR: (RiskPercentagePositionSizer): Stop Loss value invalid for {signal_event.symbol}")
            return 0.0
        
        # Access account infor (account currency)
        account_info = mt5.account_info()

        # Access account info symbol in order to calculate risk
        symbol_info = mt5.symbol_info(signal_event.symbol)

        #Get estimated price from order
        #If its market order
        if signal_event.target_order == "MARKET":
            #Get latest available price
            last_tick = data_provider.get_latest_tick(signal_event.symbol)
            entry_price = last_tick['ask'] if signal_event.signal == "BUY" else last_tick["bid"]

        else: #Pending order
            #Get price from signal event
            entry_price = signal_event.target_price

        # Get last values we need to calculate stop loss
        equity = account_info.equity
        volume_step = symbol_info.volume_step                   # Min volume change
        tick_size = symbol_info.trade_tick_size                 # Min price change
        account_currency = account_info.currency                # Account currency
        symbol_profit_currency = symbol_info.currency_profit    # Profic currency symbol
        contract_size = symbol_info.trade_contract_size         # Contract size 

        # Aux calc
        tick_value_profit_currency = contract_size * tick_size  # Win / Lose quantity per tick

        # Convert profit currency tick value from the symbol into account currency
        tick_value_account_currency = Utils.convert_currency_amount_to_another_currency(tick_value_profit_currency, symbol_profit_currency, account_currency)

        #Position size calc
        try:
            price_distance_in_integer_ticksizes = int(abs(entry_price - signal_event.sl) / tick_size)
            monetary_risk = equity * self.risk_pct
            volume = monetary_risk  / (price_distance_in_integer_ticksizes * tick_value_account_currency)
            volume = round(volume / volume_step) * volume_step
        
        except Exception as e:
            print(f"ERROR: Position size calculation error. Exception: {e}")
            return 0.0

        return volume
