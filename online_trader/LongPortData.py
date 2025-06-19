from datetime import datetime, timedelta
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
import pandas as pd
from decimal import Decimal
import time
from log import logger
from typing import Dict


class Borg:
    _shared_state = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


class LongPortData(Borg):
    def __init__(self, config) -> None:
        if self._shared_state:
            # 如果已经有实例存在，则直接返回
            super().__init__()
            print(
                '"LongPortData" instance already exists, returning existing instance.'
            )
        else:
            # 如果没有实例存在，则初始化
            print("initiate the first instance with default state.")
            super().__init__()
            cfg = Config(
                app_key=config["longport"]["app_key"],
                app_secret=config["longport"]["app_secret"],
                access_token=config["longport"]["access_token"],
                enable_overnight=True,
            )
            self.trade_ctx = TradeContext(cfg)
            self.quote_ctx = QuoteContext(cfg)

            # 账户信息
            self.account_balance = self.trade_ctx.account_balance()
            # 持仓信息
            self.stock_positions = self.trade_ctx.stock_positions()
            # 历史交易记录
            self.last_trader_price = 0.0

            # 市场
            self.market = None
            self.market_during_time = None

            # 市场时间
            self.market_time = {
                "US": {
                    "pre_market_quote": {
                        "begin": "16:00:00",
                        "end": "21:30:00",
                    },
                    "on_market": {
                        "begin": "22:30:00",
                        "end": "05:00:00",
                    },
                    "post_market_quote": {
                        "begin": "05:00:00",
                        "end": "09:30:00",
                    },
                },
                "HK": {
                    "on": {
                        "begin": "09:30:00",
                        "end": "16:00:00",
                    }
                },
            }

            self.symbol_name = None
            # 当前价格
            self.current_price = 0.0
            # 上一时刻价格
            self.last_price = 0.0

            logger.info(self.account_balance)
            logger.info(self.stock_positions)

    def get_last_trade_price(self, start_date, stock_id):
        # 先找当日成交记录
        resp = self.trade_ctx.today_executions(symbol=stock_id)
        if resp:
            self.last_trader_price = resp[len(resp) - 1].price
            return

        # 再找历史成交记录
        resp = self.trade_ctx.history_executions(
            # symbol = "700.HK",
            symbol=stock_id,
            # start_at = datetime(2022, 5, 9),
            start_at=start_date,
            end_at=datetime.today(),
        )
        if resp:
            self.last_trader_price = resp[len(resp) - 1].price
        logger.info(resp)

    def get_current_price(self, stock_id):
        # resp = ctx.quote(["700.HK", "AAPL.US", "TSLA.US", "NFLX.US"])
        resp = self.quote_ctx.quote(stock_id)

        logger.info(resp)

        if self.market_during_time == "on":
            return resp[0].last_done
        elif self.market_during_time == "on_market":
            return resp[0].last_done
        elif self.market_during_time == "pre_market_quote":
            return resp[0].pre_market_quote.last_done
        elif self.market_during_time == "post_market_quote":
            return resp[0].post_market_quote.last_done

    def check_stock_positions(self, stock_id):
        self.stock_positions = self.trade_ctx.stock_positions()

        logger.info(self.stock_positions)
        # 有坑，symbol 前面是不带0的
        for stock_position in self.stock_positions.channels[0].positions:
            if (
                stock_position.symbol_name == self.symbol_name
                or stock_position.symbol == stock_id
            ):
                if stock_position.quantity > 0:
                    return True

        return False

    def check_market(self, stock_id):
        # 补充 symbol_name
        resp = self.quote_ctx.static_info([stock_id])
        self.symbol_name = resp[0].name_en
        logger.info(f"symbol_name {self.symbol_name}")

        # 获取股票所在市场
        market = stock_id.split(".")[1]
        logger.info(f"market: {market}")

        self.market = market
        # 获取当前时间
        currentDateAndTime = datetime.now()

        logger.info(f"The current date and time is {currentDateAndTime}")

        # Output: The current date and time is 2022-03-19 10:05:39.482383

        currentTime = (currentDateAndTime + timedelta(hours=8)).strftime("%H:%M:%S")
        logger.info(f"currentTime {currentTime}")

        # 判断当前时间是否在交易时间内
        is_market_time = False
        for index, during_time in enumerate(self.market_time[self.market]):
            logger.info(f"during_time {during_time}")
            logger.info(
                f"during_time begin {self.market_time[market][during_time]['begin']}"
            )
            logger.info(
                f"during_time end {self.market_time[market][during_time]['end']}"
            )

            if during_time == "on_market":
                if (
                    self.market_time[market][during_time]["begin"] < currentTime
                    and currentTime < "24:00:00"
                ):
                    logger.info("Market is in %s", during_time)
                    is_market_time = True
                    break

                elif (
                    "00:00:00" < currentTime
                    and currentTime < self.market_time[market][during_time]["end"]
                ):
                    logger.info("Market is in %s", during_time)
                    is_market_time = True
                    break

            if (
                self.market_time[market][during_time]["begin"] <= currentTime
                and currentTime <= self.market_time[market][during_time]["end"]
            ):
                logger.info(f"Market is in {during_time}")

                is_market_time = True
                break

        if not is_market_time:
            self.market_during_time = None
            logger.info(f"Market is not in {during_time}")
            return False
        else:
            self.market_during_time = during_time
            return True

    # 查看当前账户信息
    def get_account_balance(self):
        self.account_balance = self.trade_ctx.account_balance()
        logger.info(self.account_balance)
        return self.account_balance

    # 更新信息
    def update_info(self, stock_id):
        # 价格、成交量
        price = self.get_current_price(stock_id)
        if price is not self.current_price:
            self.last_price = self.current_price
            self.current_price = price
            logger.info(f"Current price for {stock_id}: {self.current_price}")
        else:
            logger.info(f"No change current price for {stock_id}")

        # 账户信息
        self.account_balance = self.trade_ctx.account_balance()
        logger.info(f"Account balance: {self.account_balance}")
        # 持仓信息
        self.stock_positions = self.trade_ctx.stock_positions()
        logger.info(f"Stock positions: {self.stock_positions}")
        # # 历史交易记录
        # self.get_last_trade_price(datetime.today(), stock_id)
        # logger.info(f"Last trader price: {self.last_trader_price}")
        # 市场信息
        # self.check_market(stock_id)
        # logger.info(f"Market: {self.market}")
        # logger.info(f"Market during time: {self.market_during_time}")
