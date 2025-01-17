import backtrader as bt

# Create a Stratey
# 不兼容多股票输入
class NetTrade(bt.Strategy):
    params = (
        ('period_sma10', 10),
        ('period_sma30', 30)
    )

    def __init__(self, doprint=True):
        self.doprint = doprint

        # Keep a reference to the "close" line in the datas[0] dataseries
        self.dataclose = self.datas[0].close
        # 跟踪订单状态以及买卖价格和佣金
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.

        # # 增加移动均线
        # self.sma10 = bt.indicators.SimpleMovingAverage(
        #     self.datas[0], period=self.params.period_sma10)
        # # 增加移动均线
        # self.sma30 = bt.indicators.SimpleMovingAverage(
        #     self.datas[0], period=self.params.period_sma30)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        if self.doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # 记录当前处理的close值
        self.log('Close, %.2f' % self.dataclose[0])

        # 订单是否
        if self.order:
            return
        
        # Check if we are in the market
        if not self.position:
            # 当今天的10日均线大于30日均线并且昨天的10日均线小于30日均线，则进入市场（买）
            if self.sma10[0] > self.sma30[0] and self.sma10[-1] < self.sma30[-1]:
                #若上一个订单处理完成，可继续执行买入操作
                self.order = self.buy()

        else:
            if self.sma10[0] < self.sma30[0] and self.sma10[-1] > self.sma30[-1]:
        	    # 卖出
                self.order = self.close()

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