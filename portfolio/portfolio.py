import MetaTrader5 as mt5

class Portfolio():

    def __init__(self, magic_number: int):
        self.magic = magic_number

    def get_open_positions(self) -> tuple:
        return mt5.positions_get()
    
    def get_strategy_open_positions(self) -> tuple:

        positions = []
        for position in mt5.positions_get():
            if position.magic == self.magic:
                positions.append(position)
        
        return tuple(positions)
    
    def get_number_of_open_positions_by_symbol(self, symbol: str) -> dict[str, int]:
        longs = 0
        shorts = 0

        for position in mt5.positions_get(symbol=symbol):
            if position.type == mt5.ORDER_TYPE_BUY:
                longs += 1
            else:
                shorts += 1
                
        return {"LONG": longs, "SHORT": shorts, "TOTAL": longs + shorts}

    def get_number_of_strategy_open_positions_by_symbol(self, symbol: str) -> dict[str, int]:
        longs = 0
        shorts = 0

        for position in mt5.positions_get(symbol=symbol):
            if position.magic == self.magic:
                                longs += 1
            else:
                shorts += 1
        
        return {"LONG": longs, "SHORT": shorts, "TOTAL": longs + shorts}