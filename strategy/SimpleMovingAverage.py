import backtrader as bt
from strategy import StrategySelfBase

# Create a Stratey
# 不兼容多股票输入
class SimpleMovingAverage(StrategySelfBase):
    params = (
        ('maperiod', 20),
    )
    def __init__(self):
        super().__init__()  # 初始化父类
        for i, d in enumerate(self.datas):
            # 增加移动均线
            self.inds[d]['sma'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.maperiod)
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
                # 大于均线就买
                if d.close[0] > self.inds[d]['sma']:
                    
                    self.log('Name %s'% (dn))
                    self.inds[d]['order'] = self.buy(data = d)
                    self.inds[d]['buyprice'] = d.close[0]
                    self.inds[d]['order_creation_time'] = self.datetime.date(0)
            else:
                # 不允许卖空
                if self.inds[d]['order']:
                     # 小于均线卖卖卖！
                    if d.close[0] < self.inds[d]['sma']:
                        self.log('Sell Name %s'% (dn))
                        # 卖出
                        self.close(data = d)  
                        self.inds[d]['order'] = None      
