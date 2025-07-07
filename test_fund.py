# Example OHLC daily data for Google Inc.
from backtesting.test import GOOG

import pandas as pd

from backtesting import Strategy
from backtesting.lib import crossover
from backtesting import Backtest
from dataloader import AkshareData
import pandas_ta as ta

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()


def DrawDown(values):
    dd = ta.drawdown(pd.Series(values))
    return pd.Series(dd.DD_PCT)


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 5
    n2 = 20

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        self.drawdown = self.I(DrawDown, self.data.Close)
        self.max_drawdown = 0.0

    def next(self):
        print('position.size:', self.position.size)
        print('equity:', self.equity/10000.0)
        cur_drawdown = self.drawdown[-1]
        if cur_drawdown > self.max_drawdown:
            self.max_drawdown = cur_drawdown

        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if not self.position.is_long:
            #if crossover(self.sma1, self.sma2) and cur_drawdown > self.max_drawdown * 0.5:
            if cur_drawdown > 0.15 or crossover(self.sma1, self.sma2):
                self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset

        #if self.trades and self.trades[0].pl_pct > 0.2 and cur_drawdown < 0.1:
        if self.trades:
            if self.trades[0].pl_pct > 0.2 or crossover(self.sma2, self.sma1):
                self.position.close()


df = AkshareData.get_fund_data("017847", '1_year')
# print(df.head())
# print(ta.max_drawdown(pd.Series(df.Close)))

bt = Backtest(df, SmaCross, cash=10000, commission=.002)
stats = bt.run()
print(stats)

bt.plot()