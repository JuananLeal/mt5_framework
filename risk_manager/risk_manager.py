from events.events import SizingEvent
from .interfaces.risk_manager_interface import IRiskManager
from .properties.risk_maganer_properties import BaseRiskProps
from .risk_managers.max_leverage_factor_risk_manager import MaxLeverageFactorRiskManager
from data_provider.data_provider import DataProvider
from portfolio.portfolio import Portfolio
from events.events import SizingEvent, OrderEvent
from utils.utils import Utils

from queue import Queue
import MetaTrader5 as mt5

class RiskManager(IRiskManager):

    def __init__(self, events_queue: Queue, data_provider: DataProvider, portfolio: Portfolio, risk_properties: BaseRiskProps):
        self.events_queue = events_queue
        self.DATA_PROVIDER = data_provider
        self.PORTFOLIO = Portfolio

        self.risk_management_method = self._get_risk_management_method(risk_properties)

    def _get_risk_management_method(self, risk_props: BaseRiskProps) -> IRiskManager:

        if isinstance(risk_props, MaxLeverageFactorRiskManager):
            return MaxLeverageFactorRiskManager(risk_props)
        else:
            raise Exception(f"ERROR: Unknown risk manager: {risk_props}")
        
    def _compute_current_value_of_positions_in_account_currency(self) -> float:
        # Get all open positions from our strategy
        current_positions = self.PORTFOLIO.get_strategy_open_positions()

        #Calc our open positions value
        total_value = 0.0
        for position in current_positions:
            total_value += self._compute_value_of_position_in_account_currency()
        return total_value
    
    def _compute_value_of_position_in_account_currency(self, symbol: str, volume: float, position_type: int) -> float:
        symbol_info = mt5.symbol_info(symbol)

        # Traded units in symbol currency
        traded_units = volume * mt5.symbol_info.trade_contract_size

        # Value from traded units in symbol currency
        value_traded_in_profit_currency = traded_units * self.DATA_PROVIDER.get_latest_tick(symbol)['bid']

        # Convert value traded in profit currency into account currency
        value_traded_in_account_currency = Utils.convert_currency_amount_to_another_currency(value_traded_in_profit_currency,
                                                                                             symbol_info.currency_profit,
                                                                                             mt5.account_info().currency)
        if position_type == mt5.ORDER_TYPE_SELL:
            return -value_traded_in_account_currency
        else:
            return value_traded_in_account_currency

    def _create_and_put_order_event(self, sizing_event: SizingEvent, volume: float) -> None:
        # Create Order event using size event and volume
        order_event = OrderEvent(symbol=sizing_event.symbol,
                            signal=sizing_event.signal,
                            target_order= sizing_event.target_order,
                            target_price=sizing_event.target_price,
                            magic_number=sizing_event.magic_number,
                            sl=sizing_event.sl,
                            tp=sizing_event.tp,
                            volume=volume)
        
        # Put order event into events queue
        self.events_queue.put(order_event)
        
    def assess_order(self, sizing_event: SizingEvent) -> None:
        # Get all open positions value from strategy
        current_position_value = self._compute_current_value_of_positions_in_account_currency()

        # Get new value type that new position will have in the account currency
        position_type = mt5.ORDER_TYPE_BUY if sizing_event.signal == "BUY" else mt5.ORDER_TYPE_SELL
        new_position_value = self._compute_value_of_position_in_account_currency(sizing_event.symbol, sizing_event.volume, position_type)

        # Obtain new operation volume, after passing through risk manager
        new_volume = self.risk_management_method.assess_order(sizing_event, current_position_value, new_position_value)

        # Check new volume
        if new_volume > 0.0:
            # Put order into the events queue
            self._create_and_put_order_event(sizing_event, new_volume)