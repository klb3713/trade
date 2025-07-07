from time import sleep
from longport.openapi import QuoteContext, Config, PushCandlestick, TradeSessions, Period
config = Config.from_env()
ctx = QuoteContext(config)

def on_candlestick(symbol: str, event: PushCandlestick):
    print(symbol, event)

ctx.set_on_candlestick(on_candlestick)
ctx.subscribe_candlesticks("700.HK", Period.Min_1, TradeSessions.Intraday)
sleep(300)