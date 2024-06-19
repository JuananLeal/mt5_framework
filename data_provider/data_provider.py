import MetaTrader5 as mt5
import pandas as pd
from typing import Dict
from datetime import datetime
from events.events import DataEvent
from queue import Queue


class DataProvider():

    def __init__(self, events_queue: Queue, symbol_list: list, timeframe: str):
        
        self.events_queue = events_queue
        
        self.symbols: list = symbol_list
        self.timeframe: str = timeframe

        #Create dictionary to save datetime from last candle
        self.last_bar_datetime: Dict[str, datetime] = {symbol: datetime.min for symbol in self.symbols}

    def _map_timeframes(self, timeframe:str) -> int:
        timeframe_mapping = {
            '1m'  : mt5.TIMEFRAME_M1,
            '2m'  : mt5.TIMEFRAME_M2,
            '3m'  : mt5.TIMEFRAME_M3,
            '4m'  : mt5.TIMEFRAME_M4,
            '5m'  : mt5.TIMEFRAME_M5,
            '6m'  : mt5.TIMEFRAME_M6,
            '10m' : mt5.TIMEFRAME_M10,
            '12m' : mt5.TIMEFRAME_M12,
            '15m' : mt5.TIMEFRAME_M15,
            '20m' : mt5.TIMEFRAME_M20,
            '30m' : mt5.TIMEFRAME_M30,
            '1h'  : mt5.TIMEFRAME_H1,
            '2h'  : mt5.TIMEFRAME_H2,
            '3h'  : mt5.TIMEFRAME_H3,
            '4h'  : mt5.TIMEFRAME_H4,
            '6h'  : mt5.TIMEFRAME_H6,
            '8h'  : mt5.TIMEFRAME_H8,
            '12h' : mt5.TIMEFRAME_H12,
            '1d'  : mt5.TIMEFRAME_D1,
            '1w'  : mt5.TIMEFRAME_W1,
            '1M'  : mt5.TIMEFRAME_MN1,
        }
        try:
            return timeframe_mapping[timeframe]
        except:
            print(f"Timeframe {timeframe} invalid")

    def get_latest_closed_bar(self, symbol:str, timeframe:str):
        
        # Define data parameters
        tf = self._map_timeframes(timeframe)
        from_position = 1
        num_bars = 1

        try:
            #Getting data from the last candle
            bars_np_array = pd.DataFrame(mt5.copy_rates_from_pos(symbol,tf,from_position,num_bars))
            if bars_np_array is None:
                print(f"Symbol {symbol} does not exist")

                # Returns empty Series
                return pd.Series()
            else:
                bars = pd.DataFrame(bars_np_array)

                # Convert time column to datatime and make it index
                bars['time'] = pd.to_datetime(bars['time'], unit='s')
                bars.set_index('time', inplace = True)

                # Change columns names and order
                bars.rename(columns={'tick_volume':'tickvol', 'real_volume':'vol'}, inplace=True)
                bars = bars[['open','high','low','close','tickvol','vol','spread']]
        except Exception as e:
            print(f"Cannot restore data from last candle of {symbol} {timeframe}. MT5 Error: {mt5.last_error}, excpetion: {e}")

        else:
            # If dataframe is empty, return empty serie
            if bars.empty:
                return pd.Series()
            else:
                return bars.iloc[-1]

    def get_latest_closed_bars(self, symbol: str, timeframe: str, num_bars: int = 1) -> pd.DataFrame:
        # Define data parameters
        tf = self._map_timeframes(timeframe)
        from_position = 1
        bars_count = num_bars if num_bars > 0 else 1

        try:
            #Getting data from the last candle
            bars_np_array = pd.DataFrame(mt5.copy_rates_from_pos(symbol,tf,from_position,num_bars))
            if bars_np_array is None:
                print(f"Symbol {symbol} does not exist")

                # Returns empty DataFrame
                return pd.DataFrame()
            else:
                bars = pd.DataFrame(bars_np_array)

                # Convert time column to datatime and make it index
                bars['time'] = pd.to_datetime(bars['time'], unit='s')
                bars.set_index('time', inplace = True)

                # Change columns names and order
                bars.rename(columns={'tick_volume':'tickvol', 'real_volume':'vol'}, inplace=True)
                bars = bars[['open','high','low','close','tickvol','vol','spread']]
        except Exception as e:
            print(f"Cannot restore data from last candle of {symbol} {timeframe}. MT5 Error: {mt5.last_error}, excpetion: {e}")

        else:
            # If ok, return dataframe with num_bars
            return bars
        
    def get_latest_tick(self, symbol: str) -> dict:

        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                print(f"Couldn't get last tick from {symbol}. MT5 error: {mt5.last_error()}, exception: {e}")
                return {}
        except Exception as e:
            print(f"Something went wrong getting last tick from {symbol}. MT5 error: {mt5.last_error()}, exception: {e}")
        else:
            return tick._asdict()
        
    def check_for_new_data(self) -> None:

        # Check if new data is available
        for symbol in self.symbols:
            # Find latest available data
            latest_bar = self.get_latest_closed_bar(symbol,self.timeframe)

            if latest_bar is None:
                continue

            # If there is new data
            if not latest_bar.empty and latest_bar.name > self.last_bar_datetime[symbol]:
                # Update last candle data
                self.last_bar_datetime[symbol] = latest_bar.name

                # Create DataEvent 
                data_event = DataEvent(symbol= symbol, data=latest_bar)

                # Add DataEVent to event queue
                self.events_queue.put(data_event)
