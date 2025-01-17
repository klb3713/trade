# 获取标的 k 线
# https://open.longportapp.com/docs/quote/pull/candlestick
# 运行前请访问“开发者中心”确保账户有正确的行情权限。
# 如没有开通行情权限，可以通过“LongPort”手机客户端，并进入“我的 - 我的行情 - 行情商城”购买开通行情权限。
from longport.openapi import QuoteContext, Config, Period, AdjustType

config = Config.from_env()
ctx = QuoteContext(config)

resp = ctx.candlesticks("700.HK", Period.Day, 10, AdjustType.NoAdjust)
print(resp)