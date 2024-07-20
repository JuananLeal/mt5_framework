from portfolio.portfolio import Portfolio
from events.events import OrderEvent, ExecutionEvent, PlacedPendingOrderEvent, SignalType
from utils.utils import Utils

import time
from datetime import datetime
import pandas as pd
from queue import Queue
import MetaTrader5 as mt5
from utils.utils import Utils


class OrderExecutor():
    
    def __init__(self, events_queue: Queue, portfolio: Portfolio):
      
        self.events_queue = events_queue
        self.PORTFOLIO = portfolio

    def execute_order(self, order_event: OrderEvent) -> None:
      # Check which order type we are going to execute
      if order_event.target_order == "MARKET":
         # Call to method that execute market orders
         self._execute_market_order(order_event)
      else:
         # Call to method that execute pending orders
         self._send_pending_order(order_event)
      
    def _execute_market_order(self, order_event: OrderEvent) -> None:
        # Check if order is type BUY or SELL
        if order_event.signal == "BUY":
           order_type = mt5.ORDER_TYPE_BUY
        elif order_event.signal == "SELL":
           order_type = mt5.ORDER_TYPE_SELL
        else:
           raise Exception(f"{Utils.dateprint()} - ORDER EXECUTOR: Signal {order_event.signal} invalid")
       
        # Market order request creation
        market_order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": order_event.symbol,
            "volume": order_event.volume,
            "sl": order_event.sl,
            "tp": order_event.tp,
            "type": order_type,
            "deviation": 0,
            "magic": order_event.magic_number,
            "comment": "FWK Market Order",
            "type_filling":  mt5.ORDER_FILLING_FOK,
            "price": mt5.symbol_info(order_event.symbol).bid # Just for demo account, ignored in real account
       }

        # Send trade request
        result = mt5.order_send(market_order_request)

        # Check if the order has executed correctly
        if self._check_execution_status(result):
           print(f"{Utils.dateprint()} - Market Order {order_event.signal} for {order_event.symbol} with {order_event.volume} lots, executed correctly")
           # Generate execution event and add it to event queue
           self._create_and_put_execution_event(result)
        else:
           raise Exception(f"{Utils.dateprint()} - Error executing MARKET ORDER {order_event.signal} for {order_event.symbol}: {result.comment}")
        
    def _send_pending_order(self, order_event: OrderEvent) -> None:
        # Check if order is type STOP or LIMIT
        if order_event.target_order == "STOP":
            order_type = mt5.ORDER_TYPE_BUY_STOP if order_event.signal == "BUY" else mt5.ORDER_TYPE_SELL_STOP
        elif order_event.target_order == "LIMIT":
           order_type = mt5.ORDER_TYPE_BUY_LIMIT if order_event.signal == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT
        else:
           raise Exception(f"{Utils.dateprint()} - ORDER EXECUTOR: Pending objective order {order_event.target_order} invalid")
        
        # Create pending order request
        pending_order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": order_event.symbol,
            "volume": order_event.volume,
            "sl": order_event.sl,
            "tp": order_event.tp,
            "type": order_type,
            "price": order_event.target_price,
            "deviation": 0,
            "magic": order_event.magic_number,
            "comment": "FWK Pnding Order",
            "type_filling":  mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_GTC
       }
        
        # Send trade request
        result = mt5.order_send(pending_order_request)

        # Check if the order has executed correctly
        if self._check_execution_status(result):
           print(f"{Utils.dateprint()} - Pending Order {order_event.signal} {order_event.target_order} for {order_event.symbol} with {order_event.volume} lots, on {order_event.target_price}")
           # Execute event for pending orders
           self._create_and_put_placed_pending_order_event(order_event)
        else:
           raise Exception(f"{Utils.dateprint()} - Error executing PENDING ORDER  {order_event.signal} {order_event.target_order} for {order_event.symbol}: {result.comment}")
        
    def cancel_pending_order_by_ticker(self, ticket: int) -> None:
        # Access to pending order we are interested in
        order = mt5.orders_ger(ticket=ticket)[0]

        # Verify if order exists
        if order is None:
           print(f"{Utils.dateprint()} - ORDER EXECUTOR: Pending order with ticket {ticket} does not exist")
           return 
        
        # Create trade request in order to cancel pending order
        cancel_request = {
           'action': mt5.TRADE_ACTION_REMOVE,
           'order': order.ticket,
           'symbol': order.symol
        }

        # Send cancel request
        result = mt5.order_send(cancel_request)

        # Check if the order has been cancelled
        if self._check_execution_status(result):
           print(f"{Utils.dateprint()} - Pending order with ticket {ticket} in {order.symbol} and volume {order.volume_initial} has been cancelled succesfully")
        else:
           raise Exception(f"{Utils.dateprint()} - Error cancelling position with {ticket} in {order.symbol} and volume {order.volume_initial}: {result.comment}")

    def close_position_by_ticket(self, ticket:int) -> None:
        # Access to position by ticket
        position = mt5.positions_get(ticket=ticket)[0]

        if position is None:
           print(f"{Utils.dateprint()} - ORDER EXECUTOR: No position for ticket {ticket}")
           return 
        
        # Trade request creation for that position
        close_request = {
           'action': mt5.TRADE_ACTION_DEAL,
           'position': position.ticket,
           'symbol': position.symbol,
           'volume': position.volume,
           'type': mt5.ORDER_TYPE_BUY if position.type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_SELL,
           'type_filling': mt5.ORDER_FILLING_FOK,
           "price": mt5.symbol_info(position.symbol).bid # Just for demo account, ignored in real account
        }

        # Send close_request
        result = mt5.order_send(close_request)

        # Check if the order has executed correctly
        if self._check_execution_status(result):
           print(f"{Utils.dateprint()} - Position with ticket {ticket} in {position.symbol} and volume {position.volume} has been closed sucessfully")
           # Generate execution event and add it to event queue
           self._create_and_put_execution_event(result)
        else:
           raise Exception(f"{Utils.dateprint()} - Error closing position {ticket} in {position.symbol} and volume {position.volume}: {result.comment}")

    def close_strategy_long_positions_by_symbol(self, symbol: str) -> None:
        # Access all open positions for our strategy
        positions = self.PORTFOLIO.get_strategy_open_positions()

        # Filter positions by symbol and order type
        for position in positions:
           if position.symbol == symbol and position.type == mt5.ORDER_TYPE_BUY:
              self.close_position_by_ticket(position.ticket)

    def close_strategy_short_positions_by_symbol(self, symbol: str) -> None:
        # Access all open positions for our strategy
        positions = self.PORTFOLIO.get_strategy_open_positions()

        #Filter positions by symbol and order type
        for position in positions:
          if position.symbol == symbol and position.type == mt5.ORDER_TYPE_SELL:
             self.close_position_by_ticket(position.ticket)

    def _create_and_put_placed_pending_order_event(self, order_event: OrderEvent) -> None:
        # Create placed pending order event
        placed_pendig_order_event = PlacedPendingOrderEvent(symbol=order_event.symbol,
                                                            signal=order_event.sig,
                                                            target_order=order_event.target_order,
                                                            magic_number=order_event.magic_number,
                                                            sl=order_event.sl,
                                                            tp=order_event.tp,
                                                            volume=order_event.volume)
        
        # Add it to the queue
        self.events_queue.put(placed_pendig_order_event)

    def _create_and_put_execution_event(self, order_result) -> None:
        """
        Creates an execution event based on the order result and puts it into the events queue.
    
        Args:
            order_result (OrderResult): The result of the order execution.
    
        Returns:
            None
        """
        # We obtain the deal information resulting from the execution of the order using the POSITION to which the deal belongs (instead of the deal ticket itself),
        # since in LIVE the result of the deal is usually 0 if we consult it immediately.
        #deal = mt5.history_deals_get(ticket=order_result.deal)[0]
        deal = None
    
        # We simulate a fill_time using the current time
        fill_time = datetime.now()

        # We create a small loop to give the server time to generate the deal, and we define a maximum of 5 attempts.
        for _ in range(5):
            # Wait 0.5 seconds
            time.sleep(0.5)
            try:
                deal = mt5.history_deals_get(position=order_result.order)[0]  # We use position instead of ticket
            except IndexError:
                deal = None

            if not deal:
                # If we don't get the deal, let's save the fill time as “now” to have an approximation -> you can modify it if you consider necessary
                fill_time = datetime.now()
                continue
            else:
                break
            
        # If after the loop we have not obtained the deal, we show an error message
        if not deal:
            print(f"{Utils.dateprint()} - ORD EXEC: The order execution deal could not be obtained. {order_result.order}, although it has probably been executed.")
    
        # Creamos el execution event
        execution_event = ExecutionEvent(symbol=order_result.request.symbol,
                                        signal=SignalType.BUY if order_result.request.type == mt5.DEAL_TYPE_BUY else SignalType.SELL,
                                        fill_price=order_result.price,
                                        fill_time=fill_time if not deal else pd.to_datetime(deal.time_msc, unit='ms'),
                                        volume=order_result.request.volume)

        # Place the execution event to the event queue
        self.events_queue.put(execution_event)

    def _check_execution_status(self, order_result) -> bool:
        if order_result.retcode == mt5.TRADE_RETCODE_DONE:
           return True
        elif order_result.retcode == mt5.TRADE_RETCODE_DONE_PARTIAL:
           return True
        else:
           return False