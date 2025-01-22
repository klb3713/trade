import backtrader as bt

# Create a Stratey
# 不兼容多股票输入
# 1、标的选择（手动）
# 2、建仓时机-》震荡行情开始，分类问题（暂时手动）
# 3、与上一次买入/卖出相差一个百分数阈值-》卖出/买入
# 4、行情结束-》卖出
class NetTrade(bt.Strategy):

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