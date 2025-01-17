from longport.openapi import TradeContext, Config

config = Config.from_env()

# Init config without ENV
# config = Config(app_key = "YOUR_APP_KEY", app_secret = "YOUR_APP_SECRET", access_token = "YOUR_ACCESS_TOKEN")

ctx = TradeContext(config)

resp = ctx.account_balance()
print(resp)

# 获取股票持仓
# https://open.longportapp.com/docs/trade/asset/stock
from longport.openapi import TradeContext, Config

config = Config.from_env()
ctx = TradeContext(config)
resp = ctx.stock_positions()
print(resp)