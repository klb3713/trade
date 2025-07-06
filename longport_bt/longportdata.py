import datetime
import threading
from decimal import Decimal

import backtrader as bt
from backtrader.feed import DataBase
from backtrader.utils.py3 import queue, with_metaclass

from longport.openapi import Period, SubType, PushQuote, PushCandlestick, TradeSessions
from longport_bt import longportstore


def on_candlestick(symbol: str, event: PushCandlestick):
    #print("on_candlestick:", symbol, event)
    #if not event.is_confirmed:
    #    return
    candle = event.candlestick
    bar = dict(
        datetime=candle.timestamp,
        open=float(candle.open),
        high=float(candle.high),
        low=float(candle.low),
        close=float(candle.close),
        volume=int(candle.volume),
        openinterest=0,  # LongPort行情无持仓量，设为0
    )
    candlestick_queue.put(bar)

class MetaLongPortData(DataBase.__class__):
    def __init__(cls, name, bases, dct):
        '''Class has already been created ... register'''
        # Initialize the class
        super(MetaLongPortData, cls).__init__(name, bases, dct)

        # Register with the store
        longportstore.LongPortStore.DataCls = cls

class LongPortData(with_metaclass(MetaLongPortData, DataBase)):
    params = (
        ('symbol', "700.HK"),  # 股票代码，如"700.HK"
        ('period', Period.Min_1),  # 默认1分钟K线
        ('trade_sessions', TradeSessions.Intraday),
    )

    _store = longportstore.LongPortStore
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lp = self._store(**kwargs)
        global candlestick_queue
        candlestick_queue = queue.Queue()
        self._queue = candlestick_queue
        self._stopping = False
        self._ctx = self.lp.quote_ctx

    def islive(self):
        '''Returns ``True`` to notify ``Cerebro`` that preloading and runonce
        should be deactivated'''
        return True
    
    def start(self):
        super().start()
        self._stopping = False
        self._ctx.set_on_candlestick(on_candlestick)
        self._ctx.subscribe_candlesticks(self.p.symbol, self.p.period, self.p.trade_sessions)

    def stop(self):
        self._stopping = True
        if self._ctx:
            self._ctx.unsubscribe_candlesticks(self.p.symbol, self.p.period)
        super().stop()

    def _load(self):
        # backtrader主循环会调用此方法获取新bar
        try:
            bar = self._queue.get(block=True)
        except Exception:
            return False
        self.lines.datetime[0] = bt.date2num(bar['datetime'])
        self.lines.open[0] = bar['open']
        self.lines.high[0] = bar['high']
        self.lines.low[0] = bar['low']
        self.lines.close[0] = bar['close']
        self.lines.volume[0] = bar['volume']
        self.lines.openinterest[0] = bar['openinterest']
        return True 