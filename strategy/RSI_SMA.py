import backtrader as bt
from strategy import StrategySelfBase
# Create a Stratey
class RSI_SMA(StrategySelfBase):
    params = (
        ('period_sma50', 50),
        ('maperiod', 14),
        ('rsiup', 50),
        ('rsidown', 50),
    )

    def __init__(self, doprint=True):
        super().__init__()

        self.doprint = doprint
        self.listordermsg = []
        # Keep a reference to the "close" line in the datas[0] dataseries
        self.dataclose = self.datas[0].close

        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['firstbaropen'] = d.open[1]
            self.inds[d]['earnmoney'] = 0.0
            self.inds[d]['sma50'] = bt.ind.SMA(d.close, period=self.p.period_sma50)
            self.inds[d]['rsi'] = bt.ind.RSI_SMA(d.close, period=self.p.maperiod)
            # 跟踪订单状态以及买卖价格和佣金
            self.inds[d]['buyprice'] = None
            self.inds[d]['buycomm'] = None
            self.inds[d]['order'] = None


    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name # 获取时间及股票代码
            pos = self.getposition(d).size

            # Check if we are in the market
            # 入场条件
            if not pos:
                if d.close[0] > self.inds[d]['sma50'] and self.inds[d]['rsi'] < self.params.rsidown:
                    self.log('Name %s'% (dn))
                    
                
                    self.inds[d]['order'] = self.buy(data = d)

            else:
                # 设置止盈止损
                if (self.inds[d]['rsi'] > self.params.rsiup or
                     d.open[0] < self.inds[d]['order'].executed.price * 0.95):
                    
                    self.log('Name %s'% (dn))
                    # 卖出
                    self.inds[d]['order'] = self.close(data = d)             
