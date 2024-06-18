import MetaTrader5 as mt5
import os
from dotenv import load_dotenv, find_dotenv

class PlatformConnector():


    def __init__(self, symbol_list: list):
        # Search .env file and load values
        load_dotenv(find_dotenv())

        # Platform Inizialization
        self._initialize_platform()

        # Check account type
        self._live_account_warning()

        # Print account information
        self._print_account_info()

        #Check if algorithmic trading is enabled
        self._check_algo_trading_enabled()

        # Add symbols to MarketWatch
        self._add_symbols_to_marketwatch(symbol_list)

# Establishing connection to metatrader5
    def _initialize_platform(self) -> None:
        """
        Initializes MT5 platform

        Raises: 
            Exception: If there is an error when initializing the platform
        Returns:
            None
        """
        if mt5.initialize(
            path=os.getenv("MT5_PATH"), 
            login=int(os.getenv("MT5_LOGIN")),
            password=os.getenv("MT5_PASSWORD"), 
            server=os.getenv("MT5_SERVER"),
            timeout=int(os.getenv("MT5_TIMEOUT")),
            portable=eval(os.getenv("MT5_PORTABLE"))
        ):
            print("Conected")
        else:
            raise Exception("initialize() failed, error code =", mt5.last_error())
        
    def _live_account_warning(self) -> None:
        """
        Checks account type

        Raises: 
            Exception: If refuse to connect with a real account
        Returns:
            None
        """
        account_info = mt5.account_info()

        # Check if account is live or demo
        if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
            print("DEMO ACCOUNT")
        elif account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_REAL:
            if not input("WARNING! Real Account detected. ¿Do you want to continue? (y/n)").lower() == "y":
                mt5.shutdown()
                raise Exception("User has decided to stop the program.")
        else:
            print("CONTEST ACCOUNT")

    def _check_algo_trading_enabled(self) -> None:
        """
        Checks if algorithmic trading is allowed

        Raises:
            Exception: If is not allowed
        Returns:
            None
        """
        # Check algorithmic tradig is enabled
        if not mt5.terminal_info().trade_allowed:
            raise Exception("Algorithmic trading is disabled. Please, enable it manually")
        

    def _add_symbols_to_marketwatch(self, symbols: list) -> None:
        """
        Adding symbols that are not added yet in the MarketWatch

        Raises:
            None
        Returns:
            None
        """
        
        # Check if the symbol is visible in the marketwatch, if its not we add it.
        for symbol in symbols:
            if mt5.symbol_info(symbol) is None:
                print(f"Can not add symbol {symbol} to MarketWatch: {mt5.last_error()}")
                continue
            if not mt5.symbol_info(symbol).visible:
                if not mt5.symbol_select(symbol,True):
                    print(f"Error trying to add symbol {symbol} to MarketWatch: {mt5.last_error()}")
                else:
                    print(f"Symbol {symbol} has been added succesfully to MarketWatch")
            else:
                print(f"Symbol {symbol} its already in MarketWatch")


    def _print_account_info(self) -> None:
        """
        Printing general information from trading account

        Raises:
            None
        Returns:
            None
        """
        # Get an object AccountInfo
        account_info = mt5.account_info()._asdict()

        print(f"+--------------------Informacion de la cuenta--------------------+")
        print(f"| - Account ID: {account_info['login']}")
        print(f"| - Trader Name: {account_info['name']}")
        print(f"| - Broker: {account_info['company']}")
        print(f"| - Server: {account_info['server']}")
        print(f"| - Leverage: {account_info['leverage']}")
        print(f"| - Currency: {account_info['currency']}")
        print(f"| - Balance: {account_info['balance']}")
        print(f"+----------------------------------------------------------------+")