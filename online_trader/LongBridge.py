
import datetime
from longport.openapi import QuoteContext, Config, SubType, PushQuote, Period, AdjustType,TradeContext
import pandas as pd

class LongPortData():
    '''
    从longport读取香港股票数据日线
    '''

    def __init__(self):
        super().__init__()
        config = Config.from_env()
        self.ctx = TradeContext(config)
        # 账户信息
        self.account_balance = self.ctx.account_balance()
        # 持仓信息
        self.stock_positions = self.ctx.stock_positions()
        print( self.account_balance)
        print(self.stock_positions)

if __name__ == '__main__':
    data = LongPortData()