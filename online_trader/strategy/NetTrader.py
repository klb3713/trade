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


class NetTrader(TraderStrategy):
    """A base class for trader strategies."""

    def __init__(self, stock_id: str, config) -> None:
        super().__init__(stock_id=stock_id, cfg=config)
        self.first_amount = config["strategy"]["first_amount"]
        self.amount = config["strategy"]["amount"]
        self.delta_price = config["strategy"]["delta_price"]

        global data
        global order_book
        global last_order
        # 初始化数据类
        data = LongPortData(config)
        order_book = OrderBook(stock_id, config)
        last_order = ""
        # 历史交易记录
        self.last_trader_price = data.get_last_trade_price(
            datetime.today(), self.stock_id
        )

    def Run(self) -> None:
        # 查看仓位 空仓则下单
        if not data.check_stock_positions(self.stock_id):
            logger.info("not have stock position create order")
            current_price = data.get_current_price([self.stock_id])
            self.last_trader_price = current_price
            return current_price, self.amount, OrderSide.Buy

        # 开始网格交易
        logger.info("Start NetTrade")
        logger.info(f"last_trader_price: {self.last_trader_price}")

        # 历史交易记录
        self.last_trader_price = data.get_last_trade_price(
            datetime.today(), self.stock_id
        )

        current_price = data.get_current_price([self.stock_id])
        current_delta = current_price - self.last_trader_price

        logger.info(f"current_price: {current_price}")
        logger.info(f"current_delta: {current_delta}")

        if current_delta > self.delta_price:
            return current_price, self.amount, OrderSide.Buy

        elif current_delta < -self.delta_price:
            return current_price, self.amount, OrderSide.Sell

        return current_price, self.amount, None
