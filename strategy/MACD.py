import backtrader as bt
from strategy import StrategySelfBase
# Create a Stratey
class MACD(StrategySelfBase):
    params = (
        ('period_sma5', 5),
        ('period_sma20', 20),

    )

    def __init__(self):
        super().__init__()

        for i, d in enumerate(self.datas):
            self.inds[d]['sma5'] = bt.ind.SMA(d.close, period=self.p.period_sma5)
            self.inds[d]['sma20'] = bt.ind.SMA(d.close, period=self.p.period_sma20)
            self.inds[d]['crossover'] = bt.ind.CrossOver(self.inds[d]['sma5'], self.inds[d]['sma20'])
            
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
                # 金叉
                if self.inds[d]['crossover'] > 0:
                    self.log('Name %s'% (dn))
                    self.inds[d]['order'] = self.buy(data = d)

            else:
                # 死叉
                if (self.inds[d]['crossover'] < 0 or
                     d.open[0] < self.inds[d]['order'].executed.price * 0.90):
                    
                    self.log('Name %s'% (dn))
                    # 卖出
                    self.inds[d]['order'] = self.close(data = d)             
