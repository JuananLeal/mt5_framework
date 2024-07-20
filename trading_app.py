from platform_connector.platform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from trading_director.trading_director import TradingDirector
from position_sizer.position_sizer import PositionSizer
from risk_manager.risk_manager import RiskManager
from order_executor.order_executor import OrderExecutor
from signal_generator.signal_generator import SignalGenerator
from signal_generator.properties.signal_generator_properties import MACossoverProps

from position_sizer.properties.position_sizer_properties import MinSizingProps,FixedSizingProps,RiskPctSizingProps
from portfolio.portfolio import Portfolio
from risk_manager.properties.risk_maganer_properties import MaxLeverageFactorRiskProps
from notifications.notifications import NotificationService, TelegramNotificationProperties

from queue import Queue




if __name__ == "__main__":

    #Defining variables needed to trade
    symbols = ['EURUSD']#,'EURUSD', 'EURJPY', 'EURGBP', 'XAUUSD']
    timeframe = '1m'
    magic_number = 12345
    slow_ma_period = 50
    fast_ma_period = 25

    # Main event queue creation
    events_queue = Queue()

    # Main Framework modules creation
    CONNECT = PlatformConnector(symbol_list=symbols)

    DATA_PROVIDER = DataProvider(events_queue=events_queue,symbol_list=symbols,timeframe=timeframe)

    PORTFOLIO = Portfolio(magic_number=magic_number)

    ORDER_EXECUTOR = OrderExecutor(events_queue=events_queue,
                                   portfolio=PORTFOLIO)

    SIGNAL_GENERATOR = SignalGenerator(events_queue=events_queue,
                                       data_provider=DATA_PROVIDER,
                                       portfolio=PORTFOLIO,
                                       order_executor=ORDER_EXECUTOR,
                                       signal_properties=MACossoverProps(timeframe=timeframe, fast_period=fast_ma_period, slow_period=slow_ma_period))
    
    POSITION_SIZER = PositionSizer(events_queue=events_queue,
                                   data_provider=DATA_PROVIDER,
                                   sizing_properties=FixedSizingProps(volume=1))
    
    RISK_MANAGER = RiskManager(events_queue=events_queue,
                               data_provider=DATA_PROVIDER,
                               portfolio=PORTFOLIO,
                               risk_properties=MaxLeverageFactorRiskProps(max_leverage_factor=5))
    
    NOTIFICATIONS = NotificationService(properties=TelegramNotificationProperties(token="",
                                                                                  chat_id=""))

    # Trading Director creation and main method execution
    TRADING_DIRECTOR = TradingDirector(events_queue=events_queue,
                                       data_provider=DATA_PROVIDER,
                                       signal_generator=SIGNAL_GENERATOR, 
                                       position_sizer=POSITION_SIZER,
                                       risk_manager=RISK_MANAGER,
                                       order_executor=ORDER_EXECUTOR,
                                       notification_service=NOTIFICATIONS)

    
    TRADING_DIRECTOR.run()