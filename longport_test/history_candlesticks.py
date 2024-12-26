import datetime
from longport.openapi import QuoteContext, Config, SubType, PushQuote, Period, AdjustType

config = Config.from_env()
ctx = QuoteContext(config)

# get candlesticks by offset
print("get candlesticks by offset")
print("====================")
# candlesticks = ctx.history_candlesticks_by_offset("700.HK", Period.Day, AdjustType.NoAdjust, False, datetime.datetime(2024, 12, 8), 10)
# for candlestick in candlesticks:
#     print(candlestick)

# get candlesticks by date
print("get candlesticks by date")
print("====================")
candlesticks = ctx.history_candlesticks_by_date("700.HK", Period.Day, AdjustType.NoAdjust, datetime.date(2024, 12, 5), datetime.date(2024, 12, 23))
for candlestick in candlesticks:
    print(candlestick)