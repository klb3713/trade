
from datetime import datetime
from longport.openapi import QuoteContext, Config, SubType, PushQuote, Period, AdjustType,TradeContext,OrderType, OrderSide, TimeInForceType,OpenApiException
import pandas as pd
from decimal import Decimal

import time
 


'''
1、获取账户持仓以及资金储备
2、获取目标标的上一次买入/卖出价格
3、获取目标标的当前价格
4、判断是否买入/卖出
'''
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

        # 市场时间
        self.market_time= {
            "US": {
                "Pre": {
                    "begin": "17:00:00",
                    "end": "22:30:00",
                },
                "Normal": {
                    "begin": "17:00:00",
                    "end": "22:30:00",
                },
                "Post": {
                    "begin": "17:00:00",
                    "end": "22:30:00",
                },
            }
        }
        print(self.account_balance)
        print(self.stock_positions)

    def get_last_trade_price(self, start_date, stock_id):
        resp = self.trade_ctx.history_executions(
            # symbol = "700.HK",
            symbol = stock_id,
            # start_at = datetime(2022, 5, 9),
            start_at = start_date,
            end_at = datetime.today(),
        )
        if resp:
            self.last_trader_price = resp[0].trades[0].price
        print(resp)

    def get_current_price(self, stock_id):
        # resp = ctx.quote(["700.HK", "AAPL.US", "TSLA.US", "NFLX.US"])
        resp = self.quote_ctx.quote(stock_id)
        print(resp)

        return resp[0].last_done
    
    def buy(self,stock_id, price, amount, order_id = None):
        if order_id:
            try:
                resp = self.trade_ctx.replace_order(
                    order_id = order_id,
                    quantity = Decimal(amount),
                    price = Decimal(price),
                )
            except OpenApiException as e:
                print("replace buy order error")
                print(e.code)             
                print(e.message)             
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
                print("submit buy order error")
                print(e.code)
                print(e.message)

        return order_id
    

    def sell(self,stock_id, price, amount, order_id = None):
        if order_id:
            try:
                resp = self.trade_ctx.replace_order(
                    order_id = order_id,
                    quantity = Decimal(amount),
                    price = Decimal(price),
                )
            except OpenApiException as e:
                print("replace sell order error")
                print(e.code)             
                print(e.message)             
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
                print("submit sell order error")
                print(e.code)
                print(e.message)

        return order_id
    
    def check_order_status(self, order_id):
        resp = self.trade_ctx.order_detail(
            order_id = order_id,
        )
        print(resp)
        return resp.status
    
    def check_stock_positions(self, stock_id):
        self.stock_positions = self.trade_ctx.stock_positions()

        # print(resp)
        # return resp.status

    '''
    下单购买逻辑：
    1、查询当前价格
    2、下单购买
    3、一分钟后，追踪订单成交状态
    4、若订单未成交，撤销订单。重新下单，重复1-4
    5、若订单成交，记录成交价格
    '''


if __name__ == '__main__':
    stock_id = "01810.HK"
    stock_id = "MSTX.US"
    data = LongPortData()
    data.get_last_trade_price(datetime(2023, 12, 1), stock_id)


    order_id = None
    while True:
        # 查看当前市场

        # 第一次运行，若无上一次交易记录
        if data.last_trader_price == 0.0:
            status = "WaitToNew"
            order_id = None
            while status  != "Filled":
                current_price = data.get_current_price([stock_id])
                order_id = data.buy(stock_id=stock_id, price=current_price, amount=200, order_id=order_id)
                print(order_id)

                # 暂停程序执行10秒
                time.sleep(10)

                status = data.check_order_status(order_id)

            
            data.last_trader_price = current_price

        # # 开始网格交易
        # current_price = data.get_current_price(["01810.HK"])
        # if current_price - data.last_trader_price > 0.5:
        #     order_id = data.sell(stock_id="01810.HK", price=0.1, amount=200, order_id=order_id)
        #     # 如果是卖空
        #     if not order_id:
        #         data.last_trader_price = 0.0
        # elif current_price - data.last_trader_price < -0.5:
        #     order_id = data.buy(stock_id="01810.HK", price=0.1, amount=200, order_id=order_id)