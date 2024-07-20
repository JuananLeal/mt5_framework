import MetaTrader5 as mt5
from datetime import datetime
from zoneinfo import ZoneInfo

# Create static method to convert currencies

class Utils():

    def __init__(self):
        pass

    @staticmethod
    def convert_currency_amount_to_another_currency(amount: float, from_currency: str, to_currency: str) -> float:

        # Check if both currencies are the same
        if from_currency == to_currency:
            return amount

        all_fx_symbol = ("AUDCAD", "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD", "CADCHF", "CADJPY", "CHFJPY", "EURAUD", "EURCAD",
                         "EURCHF", "EURGBP", "EURJPY", "EURNZD", "EURUSD", "GBPAUD", "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD",
                         "GBPUSD", "NZDCAD", "NZDCHF", "NZDJPY", "NZDUSD", "USDCAD", "USDCHF", "USDJPY", "USDSEK", "USDNOK")
        
        # Convert currencies to upper
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Search currencies symbol
        fx_symbol = [symbol for symbol in all_fx_symbol if from_currency in symbol and to_currency in symbol][0]
        fx_symbol_base = fx_symbol[:3]

        # Get latest data available for fx_symbol
        try:
            tick = mt5.symbol_info_tick(fx_symbol)
            if tick is None:
                raise Exception(f"Symbol {fx_symbol} not available. Please, check available symbols in your broker/platform")
        
        except Exception as e:
            print(f"ERROR: Cannot get las tick from symbol {fx_symbol}. MT5 error: {mt5.last_error()}, Exception: {e}")
            return 0.0
        
        else:
            # Get last available price from symbol
            last_price = tick.bid

            # Convert from currency into our account currency
            converted_amount = amount / last_price if fx_symbol_base == to_currency else amount * last_price
            return converted_amount

    @staticmethod
    def _dateprint(self) -> str:
        return datetime.now(ZoneInfo("Asia/Nicosia")).strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]