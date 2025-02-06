import backtrader as bt

'''
基于统计套利的配对交易策略是一种市场中性策略，具体的说，
是指从市场上找出历史股价走势相近的股票进行配对，
当配对的股票价格差偏离历史均值时，则做空股价较高的股票同时买进股价较低的股票，
等待他们回归到长期均衡关系，由此赚取两股票价格收敛的报酬。

配对交易策略 的时期分为 形成期（Formation Period）和 交易期（Trading Period）。

在形成期挑选历史走势存在规律的股票对，并制定交易策略；
在交易期模拟开仓平仓交易，而后计算收益。在整个配对交易策略过程中，具体需要考虑如下问题：

（1）如何挑选进行配对的股票？

（2）挑选好股票对以后，如何制定交易策略？开仓点如何设置？

（3）开仓时，两只股票如何进行多空仓配比？
'''


# Create a Stratey
class PairTrade(bt.Strategy):

    def __init__(self, doprint=True):
        self.doprint = doprint

        # Keep a reference to the "close" line in the datas[0] dataseries
        self.dataclose = self.datas[0].close
        # 跟踪订单状态以及买卖价格和佣金
        self.order = None
        self.buycomm = None

        # 获取目标标的，及当前标定仓位
        self.buyprice = None
        self.sellprice = None
        self.last_sellbuy = None
        # 获取上一次标的买入/卖出的价格
        self.holdcash = None

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        if self.doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # 记录当前处理的close值
        self.log('Close, %.2f' % self.dataclose[0])
        print('当前可用资金', self.broker.getcash())
        print('当前总资产', self.broker.getvalue())
        print('当前持仓量', self.broker.getposition(self.data).size)
        print('当前持仓成本', self.broker.getposition(self.data).price)
        # 也可以直接获取持仓
        print('当前持仓量', self.getposition(self.data).size)
        print('当前持仓成本', self.getposition(self.data).price)

        # 订单是否
        if self.order:
            return
        
        # 判断收盘价与上一次买入/卖出价格差值是否超过阈值
        if not self.position:
            # 若未买入，则判断是否买入
            print('position')
            self.order = self.buy()
        else:
            print('buyprice')

            if self.dataclose[0] - self.buyprice > 0.3:
                self.order = self.sell()
            elif self.dataclose[0] - self.buyprice < -0.3:
                self.order = self.buy()
            

    def notify_order(self, order):
        # 订单状态为提交和接受，不做处理
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        # 检查订单是否成交
        # 注意，没有足够现金的话，订单会被拒绝。        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('Buy Executed. Price: %.2f, Cost: %.2f, Comm %.2f' % 
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm)
                )
                self.buyprice = order.executed.price
                self.comm = order.executed.comm
            else:
                self.log('Sell Executed. Price: %.2f, Cost: %.2f, Comm %.2f' % 
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm)
                )  
                self.buyprice = order.executed.price
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('Operation Profit, Gross %.2f, Net %.2f' %
            (trade.pnl, trade.pnlcomm)
        )