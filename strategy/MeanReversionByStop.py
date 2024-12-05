import backtrader as bt
from strategy import StrategySelfBase
# Create a Stratey
class MeanReversionByStop(StrategySelfBase):
    params = (
        ('period_sma10', 10),
        ('period_ema200', 50),
        ('maperiod', 7),
        ('rsiup', 90),
        ('rsidown', 30),
        ('upperband', 90.0),
        ('lowerband', 30.0),
    )

    def __init__(self):
        super().__init__()

        for i, d in enumerate(self.datas):
            self.inds[d]['sma10'] = bt.ind.SMA(d.close, period=self.p.period_sma10)
            self.inds[d]['ema200'] = bt.ind.EMA(d.close, period=self.p.period_ema200)
            self.inds[d]['rsi'] = bt.ind.RSI(d.close,
                                             period=self.p.maperiod,
                                             lowerband=self.p.lowerband,
                                             upperband=self.p.upperband)
            self.inds[d]['crossover'] = bt.ind.CrossOver(self.inds[d]['sma10'], self.inds[d]['ema200'])
            
            # 跟踪订单状态以及买卖价格和佣金
            self.inds[d]['buyprice'] = None
            self.inds[d]['buycomm'] = None
            self.inds[d]['order'] = None
            self.inds[d]['order_creation_time'] = None
            self.inds[d]['profit'] = None
            self.inds[d]['profitbase'] = 0.05
            self.inds[d]['gettarget'] = False
            

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name # 获取时间及股票代码
            pos = self.getposition(d).size

            # Check if we are in the market
            # 入场条件
            if not pos:
                if (
                    self.inds[d]['crossover']>0):
                    
                    self.log('Name %s'% (dn))
                    self.inds[d]['order'] = self.buy(data = d)
                    self.inds[d]['buyprice'] = d.close[0]
                    self.inds[d]['order_creation_time'] = self.datetime.date(0)
            else:
                # 不允许卖空
                if self.inds[d]['order']:
                    # 持有
                    self.inds[d]['profit'] = (d.close[0]-self.inds[d]['buyprice'])/self.inds[d]['buyprice']
                    if (self.inds[d]['profit'] > self.inds[d]['profitbase'] * 2 and self.inds[d]['gettarget']):
                        self.inds[d]['profitbase'] = self.inds[d]['profit'] * 0.80
                    # 止盈
                    if (self.inds[d]['profit'] > self.inds[d]['profitbase'] and self.inds[d]['gettarget'] == False):
                        self.inds[d]['gettarget'] = True
    
                    if (self.inds[d]['profit'] < self.inds[d]['profitbase'] and  self.inds[d]['gettarget']):
                        
                        # 卖出
                        self.log('卖出 Name %s'% (dn))
                        self.inds[d]['profitbase'] = 0.05
                        self.inds[d]['gettarget'] = False
                        self.inds[d]['order'] = self.sell(data = d,size=self.inds[d]['order'].executed.size)
                        self.inds[d]['order'] = None     
                    # 止损
                    elif ((d.close[0] - self.inds[d]['buyprice'])/self.inds[d]['buyprice'] < -0.05 
                    ):
                        
                        self.log('止损 Name %s'% (dn))
                        # 卖出
                        self.close(data = d)  
                        self.inds[d]['order'] = None      
                        self.inds[d]['gettarget'] = False
                        self.inds[d]['profitbase'] = 0.05

