from datetime import datetime, timedelta
from longport.openapi import QuoteContext, Config, SubType, PushQuote, Period, AdjustType,TradeContext,OrderType, OrderSide, TimeInForceType,OpenApiException,OrderStatus,Market
import pandas as pd
from decimal import Decimal
import time
import logging

# 初始化log
logger = logging.getLogger(__name__)

class LongPortData():
    '''
    从longport读取香港股票数据日线
    '''

    def __init__(self):
        super().__init__()
        config = Config(
            app_key="fddd1f64ad477d0aea79928c749cc581",
            app_secret="d7873d6e17dbff6c0f1bb6ccf3f5a638f044ee9b6ba7f87e92399c8e8164357e",
            access_token="m_eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb25nYnJpZGdlIiwic3ViIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzQyOTk4MzQ3LCJpYXQiOjE3MzUyMjIzNDMsImFrIjoiZmRkZDFmNjRhZDQ3N2QwYWVhNzk5MjhjNzQ5Y2M1ODEiLCJhYWlkIjoyMDUxMzYxNywiYWMiOiJsYl9wYXBlcnRyYWRpbmciLCJtaWQiOjEzNzY5MjY3LCJzaWQiOiJ1N1Fxak51RWd2ZzEydzhMNkR2WmF3PT0iLCJibCI6MywidWwiOjAsImlrIjoibGJfcGFwZXJ0cmFkaW5nXzIwNTEzNjE3In0.X3C9g7KJ8F_gjyRT5EOtC1q-b6pmTGHe9_vFHz8KwKuZSIPSC7elUdyprOlWNNfKLOS5_xFhIwDCDo62WHq0KRyTqUOELfPphSMiqkk5H9nICGNJ7Oi7vzuqppuj-kZNjTerY-h1G45l68GV6Uv0VpIuukRRQ9tziteG42GweV5UKp4qGJkQYK682ORptSlXNyhnMAOry-heuubpwtmrlh-J2U-NnbiKyuvEM_U9S2NkemF_AmirZ_hGPmJSjMRhrcoAavWrO4zMIKDSFE4zKn7R4h8ow32yWpaRQVIJU_NDto-lwAshytGq0TiE5EgEU_iizzvClaASfhgSUWht6sNhj5A4UHkIcB2-S5uMHLgkaIE-Zuvy1iglN-WpEFgTllR4HqEG2G_Vt9JqLGkCRNwYoOkyYIbQkbGIbx8dVivp12N0S5GOkCcedokKL-0SbuJ2HTD-How-mPRhUGeeSwJWQyXYHTOGy4X2j60J7R8koUMGATCLxWRnU94wbVDUe3yRfYqEYmWEmM8gQkOyZC2ozWcu0zysyjLVp4stCApl1c9XiDODdQFhBgUo_MFvKMG82X826EFfYkudW4zsgRsrHj5IIz5qWj0qzkiY1BOtDfMRwkyPi_gsagUaTsSk0RrKBEvOtZXKZvWHfDO5HXsC-NQ63wVb4nTBNH-mMmk",
            enable_overnight=True)
        self.trade_ctx = TradeContext(config)
        self.quote_ctx = QuoteContext(config)
        
        # 账户信息
        self.account_balance = self.trade_ctx.account_balance()
        # 持仓信息
        self.stock_positions = self.trade_ctx.stock_positions()
        # 历史交易记录
        self.last_trader_price = 0.0

        # 市场
        self.market = None
        self.market_during_time= None

        # 市场时间
        self.market_time= {
            "US": {
                "pre_market_quote": {
                    "begin": "17:00:00",
                    "end": "22:30:00",
                },
                0: {
                    "begin": "22:30:00",
                    "end": "05:00:00",
                },
                "post_market_quote": {
                    "begin": "05:00:00",
                    "end": "09:30:00",
                },
            },
            "HK": {
                0: {
                    "begin": "09:30:00",
                    "end": "16:00:00",
                }
            }
        }

        self.symbol_name = None

        logger.info(self.account_balance)
        logger.info(self.stock_positions)

    def get_last_trade_price(self, start_date, stock_id):
        # 先找当日成交记录
        resp = self.trade_ctx.today_executions(symbol = stock_id)
        if resp:
            self.last_trader_price = resp[len(resp)-1].price
            return
        
        # 再找历史成交记录
        resp = self.trade_ctx.history_executions(
            # symbol = "700.HK",
            symbol = stock_id,
            # start_at = datetime(2022, 5, 9),
            start_at = start_date,
            end_at = datetime.today(),
        )
        if resp:
            self.last_trader_price = resp[len(resp)-1].price
        logger.info(resp)

    def get_current_price(self, stock_id):
        # resp = ctx.quote(["700.HK", "AAPL.US", "TSLA.US", "NFLX.US"])
        resp = self.quote_ctx.quote(stock_id)

        logger.info(resp)

        if self.market_during_time == 0:
            return resp[0].last_done
        elif self.market_during_time == 'pre_market_quote':
            return resp[0].pre_market_quote.last_done
        elif self.market_during_time == 'post_market_quote':
            return resp[0].post_market_quote.last_done
    
    def buy(self,stock_id, price, amount, order_id = None):
        if order_id:
            try:
                resp = self.trade_ctx.replace_order(
                    order_id = order_id,
                    quantity = Decimal(amount),
                    price = Decimal(price),
                )
            except OpenApiException as e:
                logger.info("replace buy order error")
                logger.info(e)           
        else:
            try:
                resp = self.trade_ctx.submit_order(
                    stock_id,
                    OrderType.LO,
                    OrderSide.Buy,
                    Decimal(amount),
                    TimeInForceType.Day,
                    submitted_price=Decimal(price),
                    remark="Hello from Python SDK",
                )
                order_id = resp.order_id
            except OpenApiException as e:
                logger.info("submit buy order error")
                logger.info(e)

        return order_id
    

    def sell(self,stock_id, price, amount, order_id = None):
        if order_id != None and self.check_order_status(order_id) != OrderStatus.Filled:
            try:
                resp = self.trade_ctx.replace_order(
                    order_id = order_id,
                    quantity = Decimal(amount),
                    price = Decimal(price),
                )
            except OpenApiException as e:
                logger.info("replace sell order error")
                logger.info(e)           
        else:
            try:
                resp = self.trade_ctx.submit_order(
                    stock_id,
                    OrderType.LO,
                    OrderSide.Sell,
                    Decimal(amount),
                    TimeInForceType.Day,
                    submitted_price=Decimal(price),
                    remark="Hello from Python SDK",
                )
                order_id = resp.order_id
            except OpenApiException as e:
                logger.info("submit sell order error")
                logger.info(e)

        return order_id
    
    def check_order_status(self, order_id):
        if not order_id:
            return OrderStatus.Unknown

        resp = self.trade_ctx.order_detail(
            order_id = order_id,
        )
        return resp.status
    
    def check_stock_positions(self, stock_id):
        self.stock_positions = self.trade_ctx.stock_positions()

        logger.info(self.stock_positions)
        # 有坑，symbol 前面是不带0的
        for stock_position in self.stock_positions.channels[0].positions:
            if stock_position.symbol_name == self.symbol_name or stock_position.symbol == stock_id:
                if stock_position.quantity > 0:
                    return True
              
        return False

    def check_market(self, stock_id):
        # 补充 symbol_name
        resp = self.quote_ctx.static_info([stock_id])
        self.symbol_name = resp[0].name_en
        logger.info("symbol_name %s", self.symbol_name)

        # 获取股票所在市场
        market = stock_id.split('.')[1]
        self.market = market
        # 获取当前时间
        currentDateAndTime = datetime.now()

        logger.info("The current date and time is %s", currentDateAndTime)
        # Output: The current date and time is 2022-03-19 10:05:39.482383

        currentTime = currentDateAndTime.strftime("%H:%M:%S")
        # 判断当前时间是否在交易时间内
        is_market_time = False
        for index,during_time in enumerate(self.market_time[self.market]):
            if self.market_time[market][during_time]["begin"] <= currentTime and currentTime <= self.market_time[market][during_time]["end"]:
                logger.info("Market is in %s", during_time)
                is_market_time = True
                break
 
        if not is_market_time:
            self.market_during_time = None
            logger.info("Market is not in %s", during_time)
            return False
        else:
            self.market_during_time = during_time
            return True
        
    def delete_today_order(self, stock_id):
        resp = self.trade_ctx.today_orders(
            symbol = stock_id,
        )
        for order in resp:
            if order.status !=OrderStatus.Filled and order.status != OrderStatus.Canceled and order.status != OrderStatus.Rejected:
                logger.info("Cancel Order %d",order.order_id)
                self.trade_ctx.cancel_order(order.order_id)
