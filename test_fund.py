# Example OHLC daily data for Google Inc.
from backtesting.test import GOOG

import pandas as pd

from backtesting import Strategy
from backtesting.lib import crossover
from backtesting import Backtest
import akshare as ak
import pandas_ta as ta

df = ak.fund_open_fund_info_em(symbol="018124", indicator="累计净值走势")

df["trade_date"] = pd.to_datetime(df["净值日期"])
df.set_index("trade_date", inplace=True)
df.index.name = "Datetime"
df.sort_index(inplace=True)
df['Open'] = df['High'] = df['Low'] = df['Close'] = df['累计净值']
# 设置今日的开盘价为昨日的收盘价
df.Open = df.Close.shift(1, fill_value=1.0)

for idx, data in df.iterrows():
    df.loc[idx, 'High'] = max(data.Open, data.Close)
    df.loc[idx, 'Low'] = min(data.Open, data.Close)

# 保留近一年的数据用来回测
df = df.tail(250)

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


bt = Backtest(df, SmaCross, cash=10000, commission=.002)
stats = bt.run()
print(stats)

bt.plot()