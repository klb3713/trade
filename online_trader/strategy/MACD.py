from datetime import datetime
from longport.openapi import OrderStatus
import time
from LongPortData import LongPortData
from .TraderStrategy import TraderStrategy
from log import logger
from orderbook.OrderBook import OrderBook
from longport.openapi import (
    QuoteContext,
    Config,
    SubType,
    PushQuote,
    Period,
    AdjustType,
    TradeContext,
    OrderType,
    OrderSide,
    TimeInForceType,
    OpenApiException,
    OrderStatus,
    Market,
)


class MACD(TraderStrategy):
    """A base class for trader strategies."""

    def __init__(self, stock_id: str, config) -> None:
        super().__init__(stock_id=stock_id, cfg=config)
        self.period_1 = config["strategy"]["period_1"]
        self.period_2 = config["strategy"]["period_2"]
        self.amount = config["strategy"]["amount"]

        global data
        global order_book
        global last_order
        # 初始化数据类
        data = LongPortData(config)
        order_book = OrderBook(stock_id, config)
        last_order = ""
        self.candlesticks = data.get_history_candlesticks(stock_id)
        self.current_price = data.get_current_price([self.stock_id])

    def Run(self) -> None:
        # 暂停程序执行一天
        time.sleep(86400)

        logger.info("Start macd strategy")
        # 更新数据
        data.update_info()

        # 计算MACD指标
        # 计算所有30日均线和50日均线
        closes = [candle.close for candle in self.candlesticks]

        ma_30_list = []
        ma_50_list = []
        if len(closes) >= self.period_2:
            for i in range(self.period_2 - 1, len(closes)):
                ma_30 = sum(closes[i - self.period_1 + 1 : i + 1]) / self.period_1
                ma_50 = sum(closes[i - self.period_2 + 1 : i + 1]) / self.period_2
                ma_30_list.append(ma_30)
                ma_50_list.append(ma_50)
        else:
            ma_30_list = []
            ma_50_list = []

        # 判断金叉（短期均线上穿长期均线）和死叉（短期均线下穿长期均线）
        golden_cross = False
        death_cross = False
        if len(ma_30_list) >= 2 and len(ma_50_list) >= 2:
            # 前一时刻短期均线在下，当前时刻上穿
            if ma_30_list[-2] < ma_50_list[-2] and ma_30_list[-1] > ma_50_list[-1]:
                golden_cross = True
            # 前一时刻短期均线在上，当前时刻下穿
            elif ma_30_list[-2] > ma_50_list[-2] and ma_30_list[-1] < ma_50_list[-1]:
                death_cross = True

        self.current_price = data.get_current_price([self.stock_id])
        logger.info(f"Current price: {self.current_price}")
        # 金叉
        if golden_cross:
            logger.info("Golden cross detected, placing buy order")
            return self.current_price, self.amount, OrderSide.Buy

        # 死叉
        elif death_cross:
            logger.info("Death cross detected, placing sell order")
            return self.current_price, self.amount, OrderSide.Sell

        logger.info("Nothing to do, waiting for next cycle")
        return self.current_price, self.amount, None
