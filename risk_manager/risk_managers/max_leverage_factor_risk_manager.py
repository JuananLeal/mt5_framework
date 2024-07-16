from events.events import SizingEvent
from ..interfaces.risk_manager_interface import IRiskManager
from ..properties.risk_maganer_properties import MaxLeverageFactorRiskProps

import MetaTrader5 as mt5
import sys 


class MaxLeverageFactorRiskManager(IRiskManager):

    def __init__(self, properties:MaxLeverageFactorRiskProps):
        self.max_leverage_factor = properties.max_leverage_factor

    def _compute_leverage_factor(self, account_value_account_currency: float) -> float:
        account_equity = mt5.account_info().equity

        if account_equity <= 0:
            return sys.float_info.max
        else:
            return account_value_account_currency / account_equity
        
    def _check_expected_new_position_is_compliant_with_max_leverage_factor(self, 
                                                                           sizing_event: SizingEvent,
                                                                           current_positions_value_account_currency: float,
                                                                           new_position_value_account_currency: float) -> bool:
        # Calc new expected account value if we execute the new order
        new_account_value = current_positions_value_account_currency + new_position_value_account_currency

        # Calc new leverage factor if we finally execute the new order
        new_leverage_factor = self._compute_leverage_factor(new_account_value)

        # Check if new leverage factor is greater than our max leverage factor
        if abs(new_leverage_factor) <= self.max_leverage_factor:
            return True
        else:
            print(f"RISK MANAGEMENT: New position with volume {sizing_event.volume} with a leverage factor of {abs(new_leverage_factor):.2f}, is greater than {self.max_leverage_factor}")
            return False

    def assess_order(self, sizing_event: SizingEvent, current_positions_value_account_currency: float, new_position_value_account_currency: float) -> float:
    
        # Determine if an order exceeds max leverage or not
        if self._check_expected_new_position_is_compliant_with_max_leverage_factor(sizing_event, current_positions_value_account_currency, new_position_value_account_currency):
            return sizing_event.volume
        else:
            return 0.0