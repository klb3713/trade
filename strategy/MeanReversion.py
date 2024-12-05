import backtrader as bt
from strategy import StrategySelfBase
# Create a Stratey
class MeanReversion(StrategySelfBase):
    params = (
        ('period_sma10', 10),
        ('period_ema200', 200),
        ('maperiod', 2),
        ('rsiup', 90),
        ('rsidown', 10),
        ('upperband', 90.0),
        ('lowerband', 10.0),
    )

    def __init__(self):
        super().__init__()

        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['sma10'] = bt.ind.SMA(d.close, period=self.p.period_sma10)
            self.inds[d]['ema200'] = bt.ind.EMA(d.close, period=self.p.period_ema200)
            self.inds[d]['rsi'] = bt.ind.RSI(d.close,
                                             period=self.p.maperiod,
                                             lowerband=self.p.lowerband,
                                             upperband=self.p.upperband)
            
            # 跟踪订单状态以及买卖价格和佣金
            self.inds[d]['buyprice'] = None
            self.inds[d]['buycomm'] = None
            self.inds[d]['order'] = None
            self.inds[d]['order_creation_time'] = None

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name # 获取时间及股票代码
            pos = self.getposition(d).size

            # Check if we are in the market
            # 入场条件
            if not pos:
                if (d.close[0] < self.inds[d]['sma10'] and
                    d.close[0] > self.inds[d]['ema200'] and
                    self.inds[d]['rsi'] < self.params.rsidown):
                    
                    self.log('Name %s'% (dn))
                    self.inds[d]['order'] = self.buy(data = d)
                    self.inds[d]['order_creation_time'] = self.datetime.date(0)
            else:
                # 不允许卖空
                if self.inds[d]['order']:
                    if (d.close[0] > self.inds[d]['sma10']):
                        # 卖出
                        self.log('卖出 Name %s'% (dn))

                        self.inds[d]['order'] = self.sell(data = d,size=self.inds[d]['order'].executed.size)
                        self.inds[d]['order'] = None     
                    # 止损
                    elif ((self.datetime.date(0) - self.inds[d]['order_creation_time']).days > 3 ):
                        
                        self.log('止损 Name %s'% (dn))
                        # 卖出
                        self.close(data = d)  
                        self.inds[d]['order'] = None           
