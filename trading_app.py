from platform_connector.platform_connector import PlatformConnector

if __name__ == "__main__":

    #Defining variables needed to trade
    symbols = ['EURUSD', 'USDJPY', 'JSHDGKJS']

    CONNECT = PlatformConnector(symbol_list=symbols)